from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import re
import json
import hashlib
import asyncio
import time
import traceback
from pathlib import Path
import yaml

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from tools.rag_core import (
    load_investor_documents,
    split_investor_documents,
    load_decision_rules,
    load_vectorstore,
    create_vectorstore,
    query_vectorstore,
    ensemble_reasoning,
    build_committee_prompt,
    run_ensemble_committee,
    TieredEnsembleResponse,
    PrimaryAllocation,
    EnsembleResponse,
    EnsembleRequest,
    CitationItem,
    ExpertOpinion,
    EnsembleAdjustment,
    AllocationBuckets,
)

from tools.llm_bridge import LLMBridge, LLMBridgeError, extract_json_block
from tools.reasoning_core import get_master_personality, EnsembleAdjudicator, ExpertOpinion as AdjudicatorOpinion

app = FastAPI(title="Investment Masters RAG API")

# 全局向量库实例
vectorstore = None
vectorstore_init_task: Optional[asyncio.Task] = None
VECTORSTORE_STATUS: Dict[str, Any] = {
    "state": "idle",  # idle | loading | ready | failed
    "attempts": 0,
    "last_attempt_ts": None,
    "last_success_ts": None,
    "last_error": None,
    "next_retry_in_s": None,
}
PERSIST_DIR = str(PROJECT_ROOT / "vectorstore")
WEB_OUT_DIR = PROJECT_ROOT / "web" / "out"
INDEX_PATH = PROJECT_ROOT / "config" / "investor_index.yaml"
POLICY_PATH = PROJECT_ROOT / "config" / "policy_gate.yaml"
SCENARIOS_PATH = PROJECT_ROOT / "config" / "scenarios.yaml"
AUDIT_DIR = PROJECT_ROOT / "logs"
AUDIT_PATH = AUDIT_DIR / "policy_gate_audit.jsonl"

_index_cache: Optional[Dict[str, Any]] = None


def _require_bearer_token(authorization: Optional[str]) -> str:
    """
    nofx-style API protection:
    - Expect: Authorization: Bearer <token>
    - Token source: IMH_API_TOKEN (env) OR the token itself is an LLM Key (starts with sk-)
    Returns the token string if valid.
    """
    auth = (authorization or "").strip()
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized: Authorization header missing")

    parts = auth.split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format (Expected Bearer <token>)")

    token = parts[1].strip()
    
    # 1. Check if it's the specific access token for this IMH instance
    expected = (os.getenv("IMH_API_TOKEN") or "").strip()
    if expected and token == expected:
        return token

    # 2. Check if it looks like an LLM API Key (nofx mode)
    # Most keys start with 'sk-' (OpenAI, OpenRouter, Anthropic, etc.)
    if token.startswith("sk-") or token.startswith("or-"):
        return token

    # 3. If IMH_API_TOKEN is not set, we might be in "open access" mode or "only LLM key" mode
    if not expected:
        # If no expected token, we only allow LLM keys
        raise HTTPException(status_code=401, detail="Unauthorized: IMH_API_TOKEN not set and token is not an LLM key")

    raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")


def _get_vectorstore_doc_count(vs: Any) -> Optional[int]:
    """
    Best-effort: Chroma exposes _collection.count(). Keep it defensive.
    """
    if vs is None:
        return None
    try:
        col = getattr(vs, "_collection", None)
        if col is not None and hasattr(col, "count"):
            return int(col.count())
    except Exception:
        return None
    return None


def _load_index() -> Dict[str, Any]:
    global _index_cache
    if _index_cache is not None:
        return _index_cache
    if not INDEX_PATH.exists():
        _index_cache = {}
        return _index_cache
    data = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8")) or {}
    _index_cache = data
    return data


_policy_cache: Optional[Dict[str, Any]] = None
_policy_cache_hash: Optional[str] = None


def _load_policy() -> Dict[str, Any]:
    global _policy_cache, _policy_cache_hash
    if not POLICY_PATH.exists():
        _policy_cache = {}
        _policy_cache_hash = None
        return {}

    raw = POLICY_PATH.read_text(encoding="utf-8")
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if _policy_cache is not None and _policy_cache_hash == h:
        return _policy_cache

    data = yaml.safe_load(raw) or {}
    _policy_cache = data
    _policy_cache_hash = h
    return data


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _cmp(op: str, a: float, b: float) -> bool:
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == "==":
        return a == b
    return False


def _cmp_expectation(op: str, actual: float, expected: float, tol: Optional[float] = None) -> bool:
    """
    Compare actual vs expected for scenario expectations (supports "~" / approx).
    Keep deterministic and minimal; do NOT affect core Policy Gate scoring logic.
    """
    if op in ("~", "≈", "approx"):
        t = float(tol) if tol is not None else 0.05
        return abs(actual - expected) <= t
    if op == "!=":
        return actual != expected
    return _cmp(op, actual, expected)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _hash_input(obj: Any) -> str:
    try:
        s = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    except Exception:
        s = str(obj)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _match_scenarios(text: str) -> List[str]:
    t = (text or "").strip()
    t_low = t.lower()

    scenario_keywords = {
        "市场恐慌": ["恐慌", "暴跌", "崩盘", "踩踏", "流动性危机", "挤兑", "panic", "crash", "selloff", "limit down", "跌停"],
        "市场狂热": ["狂热", "fomo", "all in", "追高", "过热", "疯涨", "逼空", "挤空", "meme", "热钱"],
        "经济衰退": ["衰退", "萧条", "失业", "经济下行", "recession", "hard landing", "soft landing"],
        "利率转向": ["降息", "加息", "利率", "yield", "rates", "转向", "拐点", "会议纪要", "点阵图"],
        "流动性收紧": ["缩表", "收紧", "紧缩", "流动性", "tga", "rrp", "qt", "qe", "融资", "保证金"],
        "估值泡沫": ["估值", "泡沫", "过高", "市盈率", "pe", "ps", "pb", "ev/ebitda", "估值扩张"],
        "创业与产品化": ["创业", "合伙人", "产品化", "股权", "特定知识", "不可替代", "MVP", "startup"],
        "杠杆与财富": ["杠杆", "代码", "媒体", "劳动力", "财富积累", "所有权", "leverage", "equity"],
        "幸福哲学": ["幸福", "宁静", "欲望", "习惯", "冥想", "身心系统", "happiness"],
        "政策与法案": ["政策", "法案", "立法", "补贴", "加税", "披露", "对冲", "policy", "bill", "legislation", "disclosure"],
        "地产与交易": ["地产", "谈判", "筹码艺术", "地段", "再融资", "地标", "real estate", "negotiation", "deal"],
        "财商与现金流": ["财商", "现金流", "资产负债", "被动收入", "老鼠赛跑", "esbi", "cash flow", "rich dad"],
        "叙事与风投": ["叙事", "趋势", "科技风口", "反身性", "非对称", "舆论杠杆", "vc", "narrative", "chamath"],
        "硬资产": ["黄金", "白银", "比特币", "抗通胀", "印钞", "gold", "silver", "bitcoin", "btc", "inflation"],
    }

    matched: List[str] = []
    for scen, keys in scenario_keywords.items():
        if any(k.lower() in t_low for k in keys):
            matched.append(scen)
    return matched


def _route_investors(text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Very simple local-first router:
    - scenario keyword match -> consult_order boosts
    - per-investor keyword match from tags_zh / key_concepts / style / best_for / fund boosts
    Returns ranked investors with reasons.
    """
    idx = _load_index()
    investors = idx.get("investors", []) or []
    scenario_routing = idx.get("scenario_routing", {}) or {}

    t = (text or "").strip()
    t_low = t.lower()

    quick_lookup = (idx.get("quick_lookup", {}) or {}).get("by_question", {}) or {}

    # Scenario keyword heuristics (Chinese + English-ish)
    matched_scenarios = _match_scenarios(t)

    # Decision intent keywords -> investor boosts (very novice-friendly)
    intent_keywords = {
        "买入/追高": (["买", "买入", "开仓", "追", "追吗", "chase", "enter"], ["warren_buffett", "peter_lynch", "charlie_munger"]),
        "卖出/止盈": (["卖", "卖出", "止盈", "take profit", "exit"], ["howard_marks", "stanley_druckenmiller", "george_soros"]),
        "止损/风控": (["止损", "风控", "回撤", "仓位", "max drawdown", "risk", "position sizing"], ["george_soros", "stanley_druckenmiller", "seth_klarman", "naval_ravikant"]),
        "宏观/政策": (["宏观", "利率", "通胀", "就业", "美元", "政策", "fed", "cpi", "ppi", "法案", "立法", "国会"], ["ray_dalio", "stanley_druckenmiller", "george_soros", "nancy_pelosi"]),
        "周期/情绪": (["周期", "情绪", "极端", "恐慌", "狂热", "sentiment", "cycle"], ["howard_marks", "ray_dalio", "charlie_munger", "donald_trump"]),
        # Valuation (novice-friendly)
        "估值/安全边际": (
            [
                "估值",
                "高估",
                "低估",
                "贵不贵",
                "便不便宜",
                "值不值",
                "合理吗",
                "溢价",
                "折价",
                "安全边际",
                "内在价值",
                "价值陷阱",
                "pe",
                "pb",
                "ps",
                "ev/ebitda",
                "intrinsic value",
                "undervalued",
                "overvalued",
                "cheap",
                "expensive",
            ],
            ["warren_buffett", "seth_klarman", "howard_marks", "charlie_munger"],
        ),
        "成长/PEG": (["成长", "peg", "营收增长", "增速", "tenbagger"], ["peter_lynch", "warren_buffett"]),
        "量化/因子": (["量化", "因子", "模型", "回测", "因子投资", "factor"], ["james_simons", "ed_thorp", "cliff_asness"]),
        "事件/激进": (["并购", "分拆", "回购", "重组", "股东行动", "proxy fight", "activist"], ["carl_icahn", "seth_klarman"]),
        "创业/杠杆": (["创业", "产品化", "杠杆", "特定知识", "股权", "所有权", "天使投资", "自由", "wealth"], ["naval_ravikant", "charlie_munger"]),
        "地产/谈判": (["地产", "房子", "写字楼", "谈判", "筹码", "品牌溢价", "再融资", "杠杆经营", "real estate"], ["donald_trump"]),
        "期权/披露": (["期权", "看涨", "看跌", "披露", "国会交易", "内幕", "跟单", "options", "leaps"], ["nancy_pelosi", "ed_thorp"]),
        "财商/通胀": (["财商", "现金流", "硬资产", "通胀", "黄金", "比特币", "资产负债", "被动收入"], ["robert_kiyosaki", "ray_dalio"]),
        "叙事/科技": (["叙事", "风口", "科技趋势", "反身性", "非对称", "跨周期"], ["chamath_palihapitiya", "naval_ravikant"]),
    }

    # Base score table
    scores: Dict[str, float] = {}
    reasons: Dict[str, List[str]] = {}

    def add(iid: str, delta: float, why: str):
        scores[iid] = scores.get(iid, 0.0) + delta
        reasons.setdefault(iid, []).append(why)

    # Quick lookup exact phrases (from YAML)
    for q, ids in quick_lookup.items():
        if q and q in t:
            for iid in (ids or []):
                add(iid, 3.5, f"匹配快速问题「{q}」")

    # Scenario match boosts consult_order
    for scen in matched_scenarios:
        route = scenario_routing.get(scen, {}) or {}
        consult = route.get("consult_order", []) or []
        for rank, iid in enumerate(consult):
            add(iid, 3.0 - min(rank, 3) * 0.5, f"匹配情境「{scen}」")

    # Intent boosts (buy/sell/stoploss/macro etc.)
    for intent, (keys, ids) in intent_keywords.items():
        if any(k.lower() in t_low for k in keys):
            for iid in ids:
                add(iid, 1.8, f"匹配意图「{intent}」")

    # Explicit over/under valuation routing (stronger signal)
    underval_keys = ["低估", "便宜", "折价", "underpriced", "undervalued", "cheap"]
    overval_keys = ["高估", "太贵", "贵", "溢价", "overpriced", "overvalued", "expensive"]
    if any(k.lower() in t_low for k in underval_keys):
        for iid in ["seth_klarman", "warren_buffett", "howard_marks"]:
            add(iid, 2.6, "判断是否低估/有安全边际")
    if any(k.lower() in t_low for k in overval_keys):
        for iid in ["charlie_munger", "michael_burry", "howard_marks", "george_soros"]:
            add(iid, 2.6, "判断是否高估/泡沫与风险")

    # Ticker hints (AAPL/TSLA/NVDA etc.) -> treat as stock selection
    if re.search(r"\b[A-Z]{1,5}\b", text or ""):
        for iid in ["warren_buffett", "peter_lynch", "charlie_munger"]:
            add(iid, 1.2, "识别到代码/股票缩写，偏向选股视角")

    # Per-investor keyword match
    for inv in investors:
        iid = inv.get("id")
        if not iid:
            continue

        # Name direct match
        cn = (inv.get("chinese_name") or "").strip()
        en = (inv.get("full_name") or "").strip()
        if cn and cn in t:
            add(iid, 5.0, "文本中直接提到该大师姓名")
        if en and en.lower() in t_low:
            add(iid, 5.0, "文本中直接提到该大师英文名")

        # Field matchers
        fields: List[str] = []
        for k in ("tags_zh", "style", "best_for"):
            vals = inv.get(k) or []
            if isinstance(vals, list):
                fields.extend([str(x) for x in vals if x])

        # key_concepts items may contain "moat (护城河)" -> both tokens
        key_concepts = inv.get("key_concepts") or []
        if isinstance(key_concepts, list):
            for x in key_concepts:
                s = str(x)
                fields.append(s)
                m = re.search(r"\(([^)]+)\)", s)
                if m:
                    fields.append(m.group(1))

        # fund/company
        fund = inv.get("fund")
        if fund:
            fields.append(str(fund))

        # score if any field token appears in text
        matched = []
        for token in set(fields):
            if not token:
                continue
            token_low = token.lower()
            if (len(token) >= 2 and token in t) or (len(token_low) >= 3 and token_low in t_low):
                matched.append(token)
        if matched:
            add(iid, min(3.0, 0.6 * len(matched)), f"匹配关键词：{', '.join(matched[:6])}" + ("…" if len(matched) > 6 else ""))

    # Build output
    by_id = {inv.get("id"): inv for inv in investors if inv.get("id")}
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    out: List[Dict[str, Any]] = []
    for iid, sc in ranked[: max(1, min(int(top_k or 5), 10))]:
        inv = by_id.get(iid) or {}
        out.append(
            {
                "investor_id": iid,
                "chinese_name": inv.get("chinese_name") or iid,
                "full_name": inv.get("full_name") or iid,
                "nationality": inv.get("nationality"),
                "fund": inv.get("fund"),
                "intro_zh": inv.get("intro_zh"),
                "score": round(sc, 3),
                "reasons": reasons.get(iid, [])[:5],
                "matched_scenarios": matched_scenarios,
            }
        )

    # Ensure we always return enough candidates for novices (fill with sensible defaults).
    target_n = max(1, min(int(top_k or 5), 10))
    defaults = ["warren_buffett", "charlie_munger", "howard_marks", "ray_dalio", "seth_klarman"]
    existing = {x.get("investor_id") for x in out}
    if len(out) < target_n:
        for iid in defaults:
            if len(out) >= target_n:
                break
            if iid in existing:
                continue
            inv = by_id.get(iid) or {}
            out.append(
                {
                    "investor_id": iid,
                    "chinese_name": inv.get("chinese_name") or iid,
                    "full_name": inv.get("full_name") or iid,
                    "nationality": inv.get("nationality"),
                    "fund": inv.get("fund"),
                    "intro_zh": inv.get("intro_zh"),
                    "score": 0.0,
                    "reasons": ["信息不足/关键词不明显，补齐通用组合（价值/周期/宏观/风控）"],
                    "matched_scenarios": matched_scenarios,
                }
            )
    return out

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    investor_id: Optional[str] = None
    source_type: Optional[str] = None
    kind: Optional[str] = None

class QueryResponse(BaseModel):
    content: str
    metadata: Dict[str, Any]
    similarity_estimate: float


class RouteRequest(BaseModel):
    text: str
    top_k: int = 5


class RouteResponse(BaseModel):
    investor_id: str
    chinese_name: str
    full_name: str
    nationality: Optional[str] = None
    fund: Optional[str] = None
    intro_zh: Optional[str] = None
    score: float
    reasons: List[str]
    matched_scenarios: List[str] = []


class SaveScenariosRequest(BaseModel):
    scenarios: List[Dict[str, Any]]


class ValidationItem(BaseModel):
    scenario_id: str
    label: str
    passed: bool
    details: List[str]
    results: Optional[Dict[str, Any]] = None


class ValidationReport(BaseModel):
    total: int
    passed_count: int
    failed_count: int
    items: List[ValidationItem]


# ---------------- Policy Gate (Fund Stack) ----------------
class PolicyGateRequest(BaseModel):
    # Natural language market observations / thesis / news summary
    text: str
    # Structured features (VIX, rates, spreads, inflation, breadth, etc.)
    features: Dict[str, float] = {}
    # Portfolio live state (leverage, cash, drawdown, turnover, corr, concentration)
    portfolio_state: Dict[str, float] = {}
    # Hard constraints / limits (optional)
    constraints: Dict[str, float] = {}
    top_k_router: int = 5
    top_k_rule_hits: int = 8


class RiskOverlay(BaseModel):
    multipliers: Dict[str, float]
    absolute: Dict[str, float]


class EvidenceItem(BaseModel):
    content: str
    metadata: Dict[str, Any]
    similarity_estimate: float


class PolicyGateResponse(BaseModel):
    regime: Dict[str, Any]
    scenario: Dict[str, Any]
    router: List[RouteResponse]
    rule_hits: List[EvidenceItem]
    risk_overlay: RiskOverlay
    explanation: Dict[str, Any]
    audit: Dict[str, Any]



@app.post("/api/rag/ensemble", response_model=TieredEnsembleResponse)
async def rag_ensemble(req: EnsembleRequest, authorization: Optional[str] = Header(None)):
    token = _require_bearer_token(authorization)
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query is required")
    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vectorstore not ready")

    # Step 1: Initialize bridge with potential token override
    bridge = LLMBridge()
    if token.startswith("sk-") or token.startswith("or-"):
        bridge.set_api_key(token)

    try:
        # Step 2: call shared ensemble committee logic
        # We wrap this in to_thread because it involves synchronous network calls (LLM) 
        # and vectorstore queries.
        from tools.rag_core import run_ensemble_committee
        result = await asyncio.to_thread(
            run_ensemble_committee,
            vectorstore,
            req.query.strip(),
            bridge,
            req.top_n_rules,
            req.top_k_experts
        )
        return TieredEnsembleResponse(**result)
        
    except LLMBridgeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        print(f"Ensemble error: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"ensemble llm error: {e}")
@app.on_event("startup")
async def startup_event():
    global vectorstore, vectorstore_init_task
    # IMPORTANT: do not block app startup on vectorstore init.
    # We start the server quickly (so the web UI is visible), then init vectorstore in background.
    print(f"正在初始化 RAG 服务（后台加载向量库），持久化目录: {PERSIST_DIR}")

    async def _init_vectorstore_bg():
        global vectorstore, VECTORSTORE_STATUS

        def _sync_init():
            vs = None
            if os.path.exists(PERSIST_DIR):
                print("发现已持久化的向量库，正在加载...")
                try:
                    vs = load_vectorstore(PERSIST_DIR)
                    print("向量库加载成功!")
                    return vs
                except Exception as e:
                    print(f"加载失败: {e}，将重新构建...")
                    vs = None

            print("正在构建新的向量库（这可能需要一些时间）...")
            investor_docs = load_investor_documents()
            investor_docs = split_investor_documents(investor_docs)
            rule_docs = load_decision_rules()
            all_docs = investor_docs + rule_docs
            vs = create_vectorstore(all_docs, PERSIST_DIR)
            print("向量库构建并保存成功!")
            return vs

        delay = 1.0
        while True:
            VECTORSTORE_STATUS["state"] = "loading"
            VECTORSTORE_STATUS["attempts"] = int(VECTORSTORE_STATUS.get("attempts") or 0) + 1
            VECTORSTORE_STATUS["last_attempt_ts"] = time.time()
            VECTORSTORE_STATUS["next_retry_in_s"] = None
            try:
                vectorstore = await asyncio.to_thread(_sync_init)
                VECTORSTORE_STATUS["state"] = "ready"
                VECTORSTORE_STATUS["last_success_ts"] = time.time()
                VECTORSTORE_STATUS["last_error"] = None
                VECTORSTORE_STATUS["next_retry_in_s"] = None
                print(f"向量库就绪：doc_count={_get_vectorstore_doc_count(vectorstore)}")
                return
            except Exception as e:
                # keep service up, but mark vectorstore as unavailable
                vectorstore = None
                VECTORSTORE_STATUS["state"] = "failed"
                VECTORSTORE_STATUS["last_error"] = f"{type(e).__name__}: {e}"
                VECTORSTORE_STATUS["next_retry_in_s"] = delay
                print(f"向量库初始化失败（将重试，服务仍可用）：{type(e).__name__}: {e}")
                print(traceback.format_exc())
                await asyncio.sleep(delay)
                delay = min(delay * 2.0, 60.0)

    if vectorstore_init_task is None or vectorstore_init_task.done():
        vectorstore_init_task = asyncio.create_task(_init_vectorstore_bg())

@app.get("/health")
async def health():
    # persistent dir stats (best-effort)
    persist_exists = os.path.exists(PERSIST_DIR)
    file_count = 0
    total_bytes = 0
    if persist_exists:
        try:
            for root, _dirs, files in os.walk(PERSIST_DIR):
                for fn in files:
                    file_count += 1
                    try:
                        total_bytes += os.path.getsize(os.path.join(root, fn))
                    except Exception:
                        pass
        except Exception:
            pass

    doc_count = _get_vectorstore_doc_count(vectorstore)
    return {
        "status": "ok",
        "vectorstore_ready": vectorstore is not None,
        "vectorstore_doc_count": doc_count,
        "vectorstore_status": VECTORSTORE_STATUS,
        "persist_dir": PERSIST_DIR,
        "persist_dir_exists": persist_exists,
        "persist_dir_file_count": file_count,
        "persist_dir_total_bytes": total_bytes,
    }


# Backwards/interop alias (some clients probe /api/health)
@app.get("/api/health", include_in_schema=False)
@app.get("/api/health/", include_in_schema=False)
async def health_alias():
    return await health()


@app.get("/api/policy/scenarios")
async def get_scenarios():
    if not SCENARIOS_PATH.exists():
        return {"scenarios": []}
    try:
        data = yaml.safe_load(SCENARIOS_PATH.read_text(encoding="utf-8")) or {}
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policy/scenarios")
async def save_scenarios(req: SaveScenariosRequest):
    try:
        data = {"scenarios": req.scenarios}
        SCENARIOS_PATH.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return {"status": "success", "count": len(req.scenarios)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/policy/validate_all", response_model=ValidationReport)
async def validate_all_scenarios():
    if not SCENARIOS_PATH.exists():
        return ValidationReport(total=0, passed_count=0, failed_count=0, items=[])
    
    try:
        scen_data = yaml.safe_load(SCENARIOS_PATH.read_text(encoding="utf-8")) or {}
        scenarios = scen_data.get("scenarios", []) or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load scenarios: {e}")

    items = []
    passed_count = 0
    
    for s in scenarios:
        sid = s.get("id", "unknown")
        label = s.get("label", sid)
        expectations = s.get("expectations", {}) or {}
        
        # Prepare request
        gate_req = PolicyGateRequest(
            text=s.get("description") or s.get("label") or "",
            features=s.get("features", {}),
            portfolio_state=s.get("portfolio_state", {}),
            constraints={},
            top_k_router=5,
            top_k_rule_hits=5
        )
        
        try:
            # We call the existing endpoint logic internally
            res = await policy_gate(gate_req)
            
            details = []
            passed = True
            
            # Helper to check expectations
            for key, exp in expectations.items():
                op = str(exp.get("op") or "").strip()
                val = _safe_float(exp.get("value"))
                tol = _safe_float(exp.get("tol"))
                scope = str(exp.get("scope") or "").strip().lower()  # multipliers | absolute | ""
                if not op or val is None:
                    continue

                # Default: risk_multiplier is a multiplier; other guardrail keys are absolute.
                if scope == "multipliers":
                    actual = _safe_float(res.risk_overlay.multipliers.get(key))
                elif scope == "absolute":
                    actual = _safe_float(res.risk_overlay.absolute.get(key))
                else:
                    if key == "risk_multiplier":
                        actual = _safe_float(res.risk_overlay.multipliers.get(key))
                    else:
                        actual = _safe_float(res.risk_overlay.absolute.get(key))
                        if actual is None:
                            actual = _safe_float(res.risk_overlay.multipliers.get(key))

                if actual is None:
                    details.append(f"❌ {key}: 预期 {op} {val}, 但输出中未找到该指标")
                    passed = False
                    continue

                if _cmp_expectation(op, actual, val, tol=tol):
                    if op in ("~", "≈", "approx"):
                        details.append(f"✅ {key}: 预期 {op} {val} ± {tol if tol is not None else 0.05}, 实际 {actual}")
                    else:
                        details.append(f"✅ {key}: 预期 {op} {val}, 实际 {actual}")
                else:
                    if op in ("~", "≈", "approx"):
                        details.append(f"❌ {key}: 预期 {op} {val} ± {tol if tol is not None else 0.05}, 实际 {actual}")
                    else:
                        details.append(f"❌ {key}: 预期 {op} {val}, 实际 {actual}")
                    passed = False
            
            if passed:
                passed_count += 1
                
            items.append(ValidationItem(
                scenario_id=sid,
                label=label,
                passed=passed,
                details=details,
                results={
                    "regime": res.regime,
                    "risk_overlay": res.risk_overlay.model_dump()
                }
            ))
            
        except Exception as e:
            items.append(ValidationItem(
                scenario_id=sid,
                label=label,
                passed=False,
                details=[f"🔥 系统错误: {e}"]
            ))

    return ValidationReport(
        total=len(scenarios),
        passed_count=passed_count,
        failed_count=len(scenarios) - passed_count,
        items=items
    )


@app.post("/api/route", response_model=List[RouteResponse])
async def route(req: RouteRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        ranked = _route_investors(req.text, top_k=req.top_k)
        return [RouteResponse(**x) for x in ranked]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=List[QueryResponse])
async def query(req: QueryRequest):
    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vectorstore not ready")

    # 构建过滤器 (Chroma 语法)
    filters = []
    if req.investor_id:
        filters.append({"investor_id": req.investor_id})
    if req.source_type:
        filters.append({"source_type": req.source_type})
    if req.kind:
        filters.append({"kind": req.kind})

    filter_dict = None
    if len(filters) == 1:
        filter_dict = filters[0]
    elif len(filters) > 1:
        filter_dict = {"$and": filters}

    try:
        results = query_vectorstore(vectorstore, req.query, k=req.top_k, filter_dict=filter_dict)
        
        responses = []
        for doc, score in results:
            responses.append(QueryResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                similarity_estimate=round(1 - score, 4)
            ))
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Compatibility: keep the web frontend calling /api/rag/query
@app.post("/api/rag/query", response_model=List[QueryResponse])
async def query_alias(req: QueryRequest, authorization: Optional[str] = Header(None)):
    # Optional token for regular query as well (NOFX style)
    if os.getenv("IMH_API_TOKEN") or (authorization and "Bearer" in authorization):
        _require_bearer_token(authorization)

    return await query(req)


def _score_regimes(policy: Dict[str, Any], features: Dict[str, float]) -> Dict[str, Any]:
    regimes = policy.get("regimes", []) or []
    scores: Dict[str, float] = {}
    reasons: Dict[str, List[str]] = {}

    for r in regimes:
        rid = r.get("id")
        if not rid:
            continue
        total = 0.0
        rs: List[str] = []
        for rule in (r.get("rules", []) or []):
            feat = rule.get("feature")
            op = rule.get("op")
            val = _safe_float(rule.get("value"))
            w = _safe_float(rule.get("weight")) or 0.0
            if not feat or not op or val is None:
                continue
            fv = _safe_float(features.get(str(feat)))
            if fv is None:
                continue
            if _cmp(str(op), fv, val):
                total += w
                rs.append(f"{feat} {op} {val} (got {fv})")
        if total > 0:
            scores[rid] = total
            reasons[rid] = rs

    if not scores:
        return {"id": "neutral", "label": "中性 / Neutral", "score": 0.0, "confidence": 0.0, "reasons": []}

    best_id, best_score = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[0]
    # confidence: normalized by sum
    ssum = sum(scores.values())
    conf = (best_score / ssum) if ssum > 0 else 0.0
    label = best_id
    for r in regimes:
        if r.get("id") == best_id and r.get("label"):
            label = r.get("label")
            break

    return {"id": best_id, "label": label, "score": round(best_score, 4), "confidence": round(conf, 4), "reasons": reasons.get(best_id, [])}


def _compute_overlay(policy: Dict[str, Any], regime_id: str, scenarios: List[str], portfolio_state: Dict[str, float], constraints: Dict[str, float]) -> Dict[str, Any]:
    base = (policy.get("base_guardrails", {}) or {}).copy()
    clamps = policy.get("clamps", {}) or {}

    regime_overlays = policy.get("regime_overlays", {}) or {}
    overlay = (regime_overlays.get(regime_id) or regime_overlays.get("neutral") or {}).copy()

    # Start multipliers
    multipliers: Dict[str, float] = {}
    for k in ["risk_multiplier", "max_leverage", "min_cash", "max_invest", "max_turnover", "max_corr"]:
        multipliers[k] = float(_safe_float(overlay.get(k)) or 1.0)

    # Scenario tweaks
    scen_over = policy.get("scenario_overlays", {}) or {}
    for s in scenarios:
        m = scen_over.get(s) or {}
        for k in ["max_leverage", "min_cash", "max_invest", "max_turnover", "max_corr"]:
            if k in m:
                multipliers[k] *= float(_safe_float(m.get(k)) or 1.0)

    # Portfolio pressure tweaks
    port_rules = policy.get("portfolio_overlays", {}) or {}
    for feat, rules in port_rules.items():
        pv = _safe_float(portfolio_state.get(str(feat)))
        if pv is None:
            continue
        for rule in (rules or []):
            op = str(rule.get("op") or "")
            val = _safe_float(rule.get("value"))
            if not op or val is None:
                continue
            if _cmp(op, pv, val):
                for k in ["max_leverage", "min_cash", "max_invest", "max_turnover", "max_corr"]:
                    if k in rule:
                        multipliers[k] *= float(_safe_float(rule.get(k)) or 1.0)

    # Build absolute guardrails
    absolute: Dict[str, float] = {}
    for k in ["max_leverage", "min_cash", "max_invest", "max_turnover", "max_corr"]:
        b = float(_safe_float(base.get(k)) or 0.0)
        abs_val = b * float(multipliers.get(k, 1.0))

        c = clamps.get(k) or {}
        lo = float(_safe_float(c.get("min")) or 0.0)
        hi = float(_safe_float(c.get("max")) or 1e9)
        abs_val = _clamp(abs_val, lo, hi)

        # Apply user constraints if present
        # Convention:
        # - min_* means lower bound; max_* means upper bound
        if k.startswith("min_"):
            user_min = _safe_float(constraints.get(k))
            if user_min is not None:
                abs_val = max(abs_val, user_min)
        else:
            user_max = _safe_float(constraints.get(k))
            if user_max is not None:
                abs_val = min(abs_val, user_max)

        absolute[k] = round(abs_val, 6)

    multipliers = {k: round(v, 6) for k, v in multipliers.items()}
    return {"multipliers": multipliers, "absolute": absolute}


@app.post("/api/policy/gate", response_model=PolicyGateResponse)
async def policy_gate(req: PolicyGateRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    if vectorstore is None:
        raise HTTPException(status_code=503, detail="Vectorstore not ready")

    policy = _load_policy()
    regime = _score_regimes(policy, req.features or {})

    scenarios = _match_scenarios(req.text)
    scenario_info = {
        "matched": scenarios,
        "primary": (scenarios[0] if scenarios else None),
        "count": len(scenarios),
    }

    router_raw = _route_investors(req.text, top_k=req.top_k_router)
    router = [RouteResponse(**x) for x in router_raw]

    overlay = _compute_overlay(policy, regime.get("id") or "neutral", scenarios, req.portfolio_state or {}, req.constraints or {})

    # RAG rule hits (source_type=rule)
    query_text = req.text
    # augment query with compact feature + portfolio summary (keeps it explainable)
    try:
        f_summary = ", ".join([f"{k}={v}" for k, v in (req.features or {}).items()][:12])
        p_summary = ", ".join([f"{k}={v}" for k, v in (req.portfolio_state or {}).items()][:12])
        if f_summary:
            query_text += f"\nFEATURES: {f_summary}"
        if p_summary:
            query_text += f"\nPORTFOLIO: {p_summary}"
    except Exception:
        pass

    try:
        results = query_vectorstore(vectorstore, query_text, k=req.top_k_rule_hits, filter_dict={"source_type": "rule"})
        rule_hits: List[EvidenceItem] = []
        for doc, score in results:
            rule_hits.append(
                EvidenceItem(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    similarity_estimate=round(1 - score, 4),
                )
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"policy gate rag error: {e}")

    # Human-friendly narrative
    md_lines = []
    md_lines.append("## Policy Gate 输出")
    md_lines.append(f"- Regime: **{regime.get('id')}** ({regime.get('label')})  conf={regime.get('confidence')}")
    if scenarios:
        md_lines.append(f"- Scenario: {', '.join(scenarios)}")
    else:
        md_lines.append("- Scenario: (none)")
    md_lines.append("\n## Risk Overlay（不改方向，只改你敢下多少）")
    md_lines.append("### Multipliers")
    for k, v in overlay["multipliers"].items():
        md_lines.append(f"- {k}: {v}")
    md_lines.append("### Absolute Guardrails")
    for k, v in overlay["absolute"].items():
        md_lines.append(f"- {k}: {v}")
    md_lines.append("\n## Router（建议先问谁）")
    for r in router[: min(len(router), 5)]:
        md_lines.append(f"- {r.chinese_name} ({r.investor_id}): {', '.join(r.reasons[:2])}")
    md_lines.append("\n## Evidence（规则命中）")
    for i, hit in enumerate(rule_hits[: min(len(rule_hits), 6)]):
        meta = hit.metadata or {}
        md_lines.append(f"- [{i+1}] {meta.get('investor_id','?')} {meta.get('rule_id','')} {meta.get('kind','')}: {meta.get('title_hint') or meta.get('source')}")

    explanation = {
        "markdown": "\n".join(md_lines),
        "json": {
            "regime": regime,
            "scenario": scenario_info,
            "overlay": overlay,
            "router_top": [r.model_dump() for r in router[: min(len(router), 5)]],
        },
    }

    audit = {
        "ts": int(__import__("time").time()),
        "policy_hash": _policy_cache_hash,
        "input_hash": _hash_input({
            "text": req.text,
            "features": req.features,
            "portfolio_state": req.portfolio_state,
            "constraints": req.constraints,
        }),
        "regime": regime,
        "scenario": scenario_info,
    }

    # Minimal audit log (JSONL): safe, local, append-only
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            **audit,
            "overlay": overlay,
            "router": [r.model_dump() for r in router[: min(len(router), 10)]],
            "rule_hits_meta": [
                {
                    "investor_id": (h.metadata or {}).get("investor_id"),
                    "rule_id": (h.metadata or {}).get("rule_id"),
                    "kind": (h.metadata or {}).get("kind"),
                    "source": (h.metadata or {}).get("source"),
                    "title_hint": (h.metadata or {}).get("title_hint"),
                    "similarity_estimate": h.similarity_estimate,
                }
                for h in rule_hits[: min(len(rule_hits), 20)]
            ],
        }
        with AUDIT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Never fail trading/analytics because logging failed
        pass

    return PolicyGateResponse(
        regime=regime,
        scenario=scenario_info,
        router=router,
        rule_hits=rule_hits,
        risk_overlay=RiskOverlay(**overlay),
        explanation=explanation,
        audit=audit,
    )


@app.get("/")
async def web_index():
    """
    Serve the exported static web app.
    """
    index_file = WEB_OUT_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Web UI not built. Run: cd web && npm install && npm run build",
        )
    return FileResponse(index_file)


# Mount static after API routes so /query stays functional.
if WEB_OUT_DIR.exists():
    # Support both hosting styles:
    # - root:   http://host:port/
    # - /imh:   http://host:port/imh/  (when integrated into another app or basePath is used)
    #
    # IMPORTANT: mount /imh BEFORE /, otherwise / will swallow /imh and cause 404 for /imh/* assets.
    app.mount("/imh", StaticFiles(directory=str(WEB_OUT_DIR), html=True), name="web_imh")
    app.mount("/", StaticFiles(directory=str(WEB_OUT_DIR), html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
