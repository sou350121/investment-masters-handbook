from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import re
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
    query_vectorstore
)

app = FastAPI(title="Investment Masters RAG API")

# 全局向量库实例
vectorstore = None
PERSIST_DIR = str(PROJECT_ROOT / "vectorstore")
WEB_OUT_DIR = PROJECT_ROOT / "web" / "out"
INDEX_PATH = PROJECT_ROOT / "config" / "investor_index.yaml"

_index_cache: Optional[Dict[str, Any]] = None


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
    scenario_keywords = {
        "市场恐慌": ["恐慌", "暴跌", "崩盘", "踩踏", "流动性危机", "挤兑", "panic", "crash", "selloff", "limit down", "跌停"],
        "市场狂热": ["狂热", "fomo", "all in", "追高", "过热", "疯涨", "逼空", "挤空", "meme", "热钱"],
        "经济衰退": ["衰退", "萧条", "失业", "经济下行", "recession", "hard landing", "soft landing"],
        "利率转向": ["降息", "加息", "利率", "yield", "rates", "转向", "拐点", "会议纪要", "点阵图"],
        "流动性收紧": ["缩表", "收紧", "紧缩", "流动性", "tga", "rrp", "qt", "qe", "融资", "保证金"],
        "估值泡沫": ["估值", "泡沫", "过高", "市盈率", "pe", "ps", "pb", "ev/ebitda", "估值扩张"],
    }

    # Decision intent keywords -> investor boosts (very novice-friendly)
    intent_keywords = {
        "买入/追高": (["买", "买入", "开仓", "追", "追吗", "chase", "enter"], ["warren_buffett", "peter_lynch", "charlie_munger"]),
        "卖出/止盈": (["卖", "卖出", "止盈", "take profit", "exit"], ["howard_marks", "stanley_druckenmiller", "george_soros"]),
        "止损/风控": (["止损", "风控", "回撤", "仓位", "max drawdown", "risk", "position sizing"], ["george_soros", "stanley_druckenmiller", "seth_klarman"]),
        "宏观/政策": (["宏观", "利率", "通胀", "就业", "美元", "政策", "fed", "cpi", "ppi"], ["ray_dalio", "stanley_druckenmiller", "george_soros"]),
        "周期/情绪": (["周期", "情绪", "极端", "恐慌", "狂热", "sentiment", "cycle"], ["howard_marks", "ray_dalio", "charlie_munger"]),
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
    matched_scenarios: List[str] = []
    for scen, keys in scenario_keywords.items():
        if any(k.lower() in t_low for k in keys):
            matched_scenarios.append(scen)
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

@app.on_event("startup")
async def startup_event():
    global vectorstore
    print(f"正在初始化 RAG 服务，持久化目录: {PERSIST_DIR}")
    
    if os.path.exists(PERSIST_DIR):
        print("发现已持久化的向量库，正在加载...")
        try:
            vectorstore = load_vectorstore(PERSIST_DIR)
            print("向量库加载成功!")
        except Exception as e:
            print(f"加载失败: {e}，将重新构建...")
            vectorstore = None

    if vectorstore is None:
        print("正在构建新的向量库（这可能需要一些时间）...")
        investor_docs = load_investor_documents()
        investor_docs = split_investor_documents(investor_docs)
        rule_docs = load_decision_rules()
        all_docs = investor_docs + rule_docs
        vectorstore = create_vectorstore(all_docs, PERSIST_DIR)
        print("向量库构建并保存成功!")

@app.get("/health")
async def health():
    return {"status": "ok", "vectorstore_ready": vectorstore is not None}


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

    # 构建过滤器
    filter_dict = {}
    if req.investor_id:
        filter_dict["investor_id"] = req.investor_id
    if req.source_type:
        filter_dict["source_type"] = req.source_type
    if req.kind:
        filter_dict["kind"] = req.kind
    
    if not filter_dict:
        filter_dict = None

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
async def query_alias(req: QueryRequest):
    return await query(req)


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
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
