import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import json
import re

from tools.reasoning_core import get_master_personality, get_personality_description
from tools.llm_bridge import LLMBridge, extract_json_block
from pydantic import BaseModel

# ---------------- Master Reasoning Board (Ensemble) Schemas ----------------
class CitationItem(BaseModel):
    id: int
    expert: Optional[str] = None
    source: Optional[str] = None
    rule_id: Optional[str] = None
    kind: Optional[str] = None
    title_hint: Optional[str] = None


class ExpertOpinion(BaseModel):
    expert: str
    summary: str
    impact: Optional[float] = None
    confidence: Optional[float] = None
    citations: List[int] = []


class EnsembleAdjustment(BaseModel):
    final_multiplier_offset: float
    primary_expert: str
    conflict_detected: bool
    resolution: str
    contributions: Optional[List[Dict[str, Any]]] = None


class EnsembleResponse(BaseModel):
    experts: List[str]
    expert_opinions: List[ExpertOpinion]
    consensus: str
    conflicts: str
    synthesis: str
    citations: List[CitationItem]
    ensemble_adjustment: EnsembleAdjustment
    metadata: Dict[str, Any] = {}


class AllocationBuckets(BaseModel):
    stocks: int
    bonds: int
    gold: int
    cash: int


class PrimaryAllocation(BaseModel):
    target_allocation: AllocationBuckets
    one_liner: str
    confidence: float


class TieredEnsembleResponse(BaseModel):
    primary: PrimaryAllocation
    secondary: EnsembleResponse


def _normalize_target_allocation(raw: Any) -> Dict[str, int]:
    """
    Ensure we always return a valid allocation:
    - keys: stocks/bonds/gold/cash
    - each 0..100 integer
    - sum == 100 (best-effort rebalance)
    """
    base = {"stocks": 60, "bonds": 20, "gold": 10, "cash": 10}

    if not isinstance(raw, dict):
        return base

    out: Dict[str, int] = {}
    for k in ("stocks", "bonds", "gold", "cash"):
        v = raw.get(k, base[k])
        try:
            iv = int(round(float(v)))
        except Exception:
            iv = int(base[k])
        iv = max(0, min(100, iv))
        out[k] = iv

    s = sum(out.values())
    if s == 100:
        return out
    if s <= 0:
        return base

    # Proportional normalization to 100 with integer rounding.
    scaled = {k: int(round(out[k] * 100.0 / s)) for k in out}
    # Fix rounding drift by adjusting the largest bucket.
    drift = 100 - sum(scaled.values())
    if drift != 0:
        kmax = max(scaled.keys(), key=lambda k: scaled[k])
        scaled[kmax] = max(0, min(100, scaled[kmax] + drift))
    # As a final guard, if still off due to clipping, fall back to base.
    if sum(scaled.values()) != 100:
        return base
    return scaled


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def _top_experts_from_hits(hits: List[tuple], top_n_docs: int = 20, top_k_experts: int = 3) -> List[str]:
    """
    Select experts from vectorstore hits: (Document, score).
    We approximate relevance by counting frequency and similarity among top_n_docs.
    """
    # score in langchain similarity_search_with_score is often distance (lower is better)
    weights: Dict[str, float] = {}
    for i, (doc, score) in enumerate((hits or [])[: max(1, int(top_n_docs or 20))]):
        meta = getattr(doc, "metadata", {}) or {}
        iid = str(meta.get("investor_id") or "").strip()
        if not iid:
            continue
        try:
            dist = float(score)
        except Exception:
            dist = 0.5
        sim = max(0.0, min(1.0, 1.0 - dist))
        # stronger weight for earlier hits
        rank_boost = 1.0 - min(i, 10) * 0.03
        w = (0.6 + 0.4 * sim) * rank_boost
        weights[iid] = weights.get(iid, 0.0) + w

    ranked = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
    return [iid for iid, _ in ranked[: max(1, min(int(top_k_experts or 3), 5))]]


def _tokenize_light(text: str) -> List[str]:
    """
    Lightweight tokenizer (no deps):
    - english-ish tokens: [a-z0-9_]{2,}
    - chinese tokens: 2-char shingles from continuous CJK sequences
    """
    t = (text or "").lower()
    out: List[str] = []

    out.extend(re.findall(r"[a-z0-9_]{2,}", t))

    cjk_runs = re.findall(r"[\u4e00-\u9fff]{2,}", text or "")
    for run in cjk_runs:
        if len(run) <= 6:
            out.append(run)
        for i in range(0, max(0, len(run) - 1)):
            out.append(run[i : i + 2])

    return out


def rerank_hits(hits: List[tuple], query: str) -> List[tuple]:
    """
    Rerank vector hits using a tiny lexical overlap signal to reduce noisy rules.
    Keeps it deterministic + fast.
    """
    if not hits:
        return hits

    q_tokens = set(_tokenize_light(query))
    if not q_tokens:
        return hits

    scored = []
    for rank, (doc, dist) in enumerate(hits):
        try:
            d = float(dist)
        except Exception:
            d = 0.5
        sim = max(0.0, min(1.0, 1.0 - d))  # vector similarity

        text = getattr(doc, "page_content", "") or ""
        meta = getattr(doc, "metadata", {}) or {}
        meta_text = " ".join([str(meta.get("rule_id") or ""), str(meta.get("kind") or ""), str(meta.get("investor_id") or "")])

        d_tokens = set(_tokenize_light(text + "\n" + meta_text))
        overlap = len(q_tokens.intersection(d_tokens))
        overlap_score = min(1.0, overlap / max(6, len(q_tokens)))

        # Combine: prefer strong semantic similarity, but boost lexical overlap.
        # Also keep a small rank prior (earlier hits slightly favored).
        rank_boost = 1.0 - min(rank, 12) * 0.01
        final = (0.82 * sim + 0.18 * overlap_score) * rank_boost
        scored.append((final, doc, dist))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [(doc, dist) for _, doc, dist in scored]


def build_committee_prompt(
    query: str,
    experts: List[str],
    evidence: List[Dict[str, Any]],
    require_quant: bool = True,
) -> List[Dict[str, str]]:
    """
    Build messages for committee reasoning. We require:
    - consensus / conflicts / synthesis
    - citations to evidence items
    - quantitative ensemble_adjustment output
    """
    experts = [e for e in (experts or []) if e]
    ev_lines = []
    for i, item in enumerate(evidence or []):
        meta = item.get("metadata") or {}
        ev_lines.append(
            f"[{i+1}] investor_id={meta.get('investor_id','?')} rule_id={meta.get('rule_id','')} kind={meta.get('kind','')} "
            f"source={meta.get('source','')}\n{item.get('content','')}"
        )

    # nofx-inspired debate framing: give each expert a role/personality so the committee
    # naturally produces conflict + consensus rather than a bland summary.
    expert_roles = []
    for e in experts:
        p = get_master_personality(e)
        expert_roles.append(f"- {e}: personality={p} ({get_personality_description(p)})")

    system = (
        "你是“大师决策委员会 (Master Reasoning Board)”的调停人（Moderator）。\n"
        "你必须严格基于提供的证据片段（IF-THEN 规则/原文片段）推理，不要编造不存在的规则。\n"
        "你要像 nofx 的多 AI 辩论系统一样：先呈现分歧，再达成可执行的一致结论。\n"
        "你需要输出结构化结果，便于前端展示与溯源。"
    )

    schema = (
        "{\n"
        '  "primary": {\n'
        '    "target_allocation": {"stocks": 60, "bonds": 20, "gold": 10, "cash": 10},\n'
        '    "one_liner": "一句话：本次应如何调整四类资产比例（可执行）。",\n'
        '    "confidence": 0.75\n'
        "  },\n"
        '  "secondary": {\n'
        '    "experts": ["..."],\n'
        '    "expert_opinions": [\n'
        '      {\n'
        '        "expert": "warren_buffett",\n'
        '        "summary": "markdown...",\n'
        '        "impact": -0.25,\n'
        '        "confidence": 0.75,\n'
        '        "citations": [1,2]\n'
        "      }\n"
        "    ],\n"
        '    "consensus": "markdown...",\n'
        '    "conflicts": "markdown...",\n'
        '    "synthesis": "markdown...",\n'
        '    "citations": [\n'
        '      {"id": 1, "expert": "ray_dalio", "source": "decision_rules.generated.json", "rule_id": "R-xxx", "title_hint": ""}\n'
        "    ],\n"
        '    "ensemble_adjustment": {\n'
        '      "final_multiplier_offset": -0.15,\n'
        '      "primary_expert": "ray_dalio",\n'
        '      "conflict_detected": true,\n'
        '      "resolution": "Crisis regime prioritizes defensive macro over selective value."\n'
        "    }\n"
        "  }\n"
        "}"
    )

    user = (
        f"用户问题：{query}\n\n"
        f"委员会成员（候选）：{', '.join(experts) if experts else '(auto)'}\n\n"
        "角色设定（每位专家必须遵守自己的 personality 立场，但不得无视证据）：\n"
        + ("\n".join(expert_roles) if expert_roles else "(auto)\n")
        + "\n\n"
        "证据片段（编号可用于 citation 引用）：\n"
        + "\n\n".join(ev_lines)
        + "\n\n"
        "输出要求（nofx 风格）：\n"
        "1) 先输出 <reasoning> ... </reasoning>（自然语言分析，可包含 markdown，但不要出现 JSON）。\n"
        "2) 再输出 <json> ... </json>，其中必须是一个**严格 JSON 对象**（不要 markdown code fence）。\n"
        "要求：\n"
        "- 你必须输出两级结构：primary + secondary。\n"
        "- 注意：primary.target_allocation 会由服务端根据 secondary.expert_opinions.impact/confidence 与裁决引擎重新计算（Sharpe 优先、抗抖动）。你仍需输出 primary 结构，但不必为整数配比耗费大量 token。\n"
        "- primary 是面向交易执行的“一级输出”，必须包含：\n"
        "  - target_allocation: stocks/bonds/gold/cash 四个整数，范围 0..100，且四者之和必须等于 100。\n"
        "  - one_liner: 一句话可执行建议（例如：提高现金与债、降低股票暴露）。\n"
        "  - confidence: 0.0..1.0，表示你对这个配比建议的信心。\n"
        "- secondary 是面向溯源的“二级输出”，必须包含：experts / expert_opinions / consensus / conflicts / synthesis / citations / ensemble_adjustment。\n"
        "- 所有二级结论必须引用证据编号（在 secondary.expert_opinions.citations / secondary.citations.id 中体现）。\n"
        "- secondary.consensus/conflicts/synthesis 用 markdown 字符串。\n"
        "- secondary.expert_opinions.impact 为 -1.0 到 +1.0 的浮点数（负数=更保守/降风险；正数=更激进/加风险）。\n"
        "- secondary.expert_opinions.confidence 为 0.0 到 1.0 的浮点数。\n"
        "- secondary.ensemble_adjustment.final_multiplier_offset 为 -0.50 到 +0.50 的浮点数（表示对 risk_multiplier 的增量调整）。\n"
        "- secondary.ensemble_adjustment.primary_expert 必须是 experts 中之一。\n"
        "- secondary.ensemble_adjustment.conflict_detected 表示是否存在明显分歧。\n"
        "- secondary.ensemble_adjustment.resolution 用一句话解释为什么得到该 offset（可英文或中文）。\n\n"
        f"JSON Schema 示例：\n{schema}"
    )

    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def ensemble_reasoning(
    vectorstore: Any,
    query: str,
    top_n_rules: int = 20,
    top_k_experts: int = 3,
) -> Dict[str, Any]:
    """
    Pure data prep:
    - query top_n_rules rule hits
    - select top_k_experts experts
    Returns: {experts, rule_hits}
    """
    if vectorstore is None:
        raise ValueError("vectorstore is None")

    from tools.rag_core import query_vectorstore  # Ensure available
    hits = query_vectorstore(vectorstore, query, k=int(top_n_rules or 20), filter_dict={"source_type": "rule"})
    hits = rerank_hits(hits, query=query)

    experts = _top_experts_from_hits(hits, top_n_docs=int(top_n_rules or 20), top_k_experts=int(top_k_experts or 3))

    rule_hits: List[Dict[str, Any]] = []
    for doc, score in hits:
        rule_hits.append(
            {
                "content": getattr(doc, "page_content", ""),
                "metadata": getattr(doc, "metadata", {}) or {},
                "similarity_estimate": round(1 - float(score), 4) if isinstance(score, (int, float)) else 0.0,
            }
        )

    return {"experts": experts, "rule_hits": rule_hits}


def run_ensemble_committee(
    vectorstore: Any,
    query: str,
    bridge: Optional[LLMBridge] = None,
    top_n_rules: int = 20,
    top_k_experts: int = 3,
) -> Dict[str, Any]:
    """
    Complete ensemble flow: retrieval -> LLM synthesis -> adjudication.
    Returns the tiered response as a dict.
    """
    from tools.llm_bridge import LLMBridge, extract_json_block
    from tools.reasoning_core import (
        get_master_personality,
        EnsembleAdjudicator,
        ExpertOpinion as AdjudicatorOpinion,
        SharpePrimaryAllocator,
    )
    
    if bridge is None:
        bridge = LLMBridge()

    # Step 1: retrieve rule hits + select experts
    prep = ensemble_reasoning(
        vectorstore=vectorstore,
        query=query,
        top_n_rules=top_n_rules,
        top_k_experts=top_k_experts,
    )
    experts = prep.get("experts") or []
    rule_hits = prep.get("rule_hits") or []
    experts_personality = {eid: get_master_personality(eid) for eid in experts}

    # Step 2: call LLM to synthesize structured JSON
    messages = build_committee_prompt(
        query=query,
        experts=experts,
        evidence=rule_hits,
        require_quant=True,
    )
    raw = bridge.call_chat(messages)

    parsed, rest = extract_json_block(raw)
    if parsed is None:
        raise ValueError("ensemble output is not valid JSON")

    # New tiered format: { primary, secondary }. If LLM returns legacy shape, treat it as secondary.
    if isinstance(parsed, dict) and "secondary" in parsed and isinstance(parsed.get("secondary"), dict):
        primary_in = parsed.get("primary") if isinstance(parsed.get("primary"), dict) else {}
        secondary = parsed.get("secondary") or {}
    else:
        primary_in = {}
        secondary = parsed if isinstance(parsed, dict) else {}

    # Step 2.5: hybrid adjudication (deterministic overlay)
    def _match_scenarios_local(text: str) -> List[str]:
        # Light copy of _match_scenarios from rag_service
        t_low = (text or "").lower()
        scenario_keywords = {
            "市场恐慌": ["恐慌", "暴跌", "崩盘", "流动性危机", "panic", "crash", "selloff"],
            "市场狂热": ["狂热", "fomo", "overheated", "追高"],
            "经济衰退": ["衰退", "萧条", "recession"],
            "流动性收紧": ["紧缩", "qt", "tightening"],
        }
        matched = []
        for scen, keys in scenario_keywords.items():
            if any(k in t_low for k in keys):
                matched.append(scen)
        return matched

    def _infer_regime_id(text: str) -> str:
        scen = _match_scenarios_local(text)
        if any(s in scen for s in ("市场恐慌", "经济衰退", "流动性收紧")):
            return "crisis"
        if any(s in scen for s in ("市场狂热", "估值泡沫")):
            return "bull"
        return "neutral"

    regime_id = _infer_regime_id(query)
    secondary.setdefault("metadata", {})
    secondary["metadata"]["regime_id_inferred"] = regime_id

    opinions_in = secondary.get("expert_opinions") or []
    adjudicator_ops: List[AdjudicatorOpinion] = []
    if isinstance(opinions_in, list):
        for op in opinions_in:
            if not isinstance(op, dict):
                continue
            expert_id = str(op.get("expert") or "").strip()
            if not expert_id:
                continue
            
            def _safe_f(v):
                try: return float(v)
                except: return None

            imp = _safe_f(op.get("impact"))
            conf = _safe_f(op.get("confidence"))
            adjudicator_ops.append(
                AdjudicatorOpinion(
                    investor_id=expert_id, 
                    impact=max(-1.0, min(1.0, float(imp or 0.0))), 
                    confidence=max(0.0, min(1.0, float(conf or 0.6))), 
                    reason=str(op.get("summary") or "")
                )
            )

    adjudicated = EnsembleAdjudicator.adjudicate(regime_id, adjudicator_ops)
    secondary["ensemble_adjustment"] = {
        "final_multiplier_offset": float(adjudicated.get("final_multiplier_offset") or 0.0),
        "primary_expert": str(adjudicated.get("primary_expert") or (experts[0] if experts else "")),
        "conflict_detected": bool(adjudicated.get("conflict_detected") or False),
        "resolution": str(adjudicated.get("resolution") or ""),
        "contributions": adjudicated.get("contributions") or [],
    }

    # Step 3: normalize citations
    citations_out = []
    for i, hit in enumerate(rule_hits):
        meta = hit.get("metadata") or {}
        citations_out.append({
            "id": i + 1,
            "expert": meta.get("investor_id"),
            "source": meta.get("source"),
            "rule_id": meta.get("rule_id"),
            "kind": meta.get("kind"),
            "title_hint": meta.get("title_hint"),
        })

    secondary["citations"] = citations_out
    secondary.setdefault("experts", experts)
    secondary["metadata"].update({
        "top_n_rules": int(top_n_rules),
        "top_k_experts": int(top_k_experts),
        "llm_provider": bridge.cfg.provider,
        "llm_model": bridge.cfg.model,
        "experts_personality": experts_personality
    })
    if rest:
        secondary["metadata"]["reasoning_preview"] = rest[:2000]

    # Step 4: build primary allocation deterministically (Sharpe-first).
    # We still accept LLM's primary fields for interop, but the allocation is generated
    # from adjudicator output to reduce numeric noise and improve stability.
    adj = secondary.get("ensemble_adjustment") if isinstance(secondary, dict) else {}
    try:
        final_offset = float((adj or {}).get("final_multiplier_offset") or 0.0)
    except Exception:
        final_offset = 0.0
    conflict = bool((adj or {}).get("conflict_detected") or False)

    alloc_det = SharpePrimaryAllocator.allocate(regime_id, final_offset, conflict_detected=conflict)
    target_alloc = _normalize_target_allocation(alloc_det)

    secondary.setdefault("metadata", {})
    secondary["metadata"]["primary_generated_by"] = "allocator_sharpe_v1"
    secondary["metadata"]["primary_allocator_inputs"] = {
        "objective": "sharpe",
        "regime_id": regime_id,
        "final_multiplier_offset": round(final_offset, 3),
        "conflict_detected": conflict,
    }

    def _safe_f(v):
        try:
            return float(v)
        except Exception:
            return None

    # Confidence: prefer impact-weighted expert confidence; fall back to LLM primary.
    conf_llm = _safe_f((primary_in or {}).get("confidence"))
    conf_det: Optional[float] = None
    try:
        weights = []
        for op in (opinions_in or []):
            if not isinstance(op, dict):
                continue
            c = _safe_f(op.get("confidence"))
            imp = _safe_f(op.get("impact")) or 0.0
            w = abs(float(imp))
            if c is None:
                continue
            weights.append((float(c), float(w)))
        if weights:
            denom = sum(w for _, w in weights)
            if denom > 0:
                conf_det = sum(c * w for c, w in weights) / denom
            else:
                conf_det = sum(c for c, _ in weights) / float(len(weights))
    except Exception:
        conf_det = None

    conf = conf_det if conf_det is not None else (conf_llm if conf_llm is not None else 0.6)
    if conflict:
        conf *= 0.85
    conf = max(0.0, min(1.0, float(conf)))

    # One-liner: keep LLM summary if present, but ensure it includes the computed allocation.
    alloc_str = f"股{target_alloc['stocks']}/债{target_alloc['bonds']}/金{target_alloc['gold']}/现{target_alloc['cash']}"
    llm_liner = str((primary_in or {}).get("one_liner") or "").strip()
    if llm_liner:
        one_liner = llm_liner
        if alloc_str not in one_liner:
            one_liner = f"{one_liner} 目标配比：{alloc_str}。"
    else:
        one_liner = f"Sharpe 优先：目标配比 {alloc_str}。"

    primary = {"target_allocation": target_alloc, "one_liner": one_liner, "confidence": conf}

    return {"primary": primary, "secondary": secondary}

def load_investor_documents():
    """加载投资者文档为 LangChain Document 格式"""
    try:
        # langchain<1.0
        from langchain.schema import Document  # type: ignore
    except Exception:
        # langchain>=1.0
        from langchain_core.documents import Document  # type: ignore
    
    documents = []
    investors_dir = PROJECT_ROOT / "investors"
    
    # 加载投资者索引获取元数据
    index_file = PROJECT_ROOT / "config" / "investor_index.yaml"
    investor_meta = {}
    
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = yaml.safe_load(f)
            for inv in index_data.get("investors", []):
                investor_meta[inv["id"]] = inv
    
    # 加载每个投资者的 Markdown 文件
    for md_file in investors_dir.glob("*.md"):
        investor_id = md_file.stem
        
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 获取元数据
        meta = investor_meta.get(investor_id, {})
        
        doc = Document(
            page_content=content,
            metadata={
                "source": str(md_file.relative_to(PROJECT_ROOT)),
                "investor_id": investor_id,
                "investor_name": meta.get("full_name", investor_id),
                "chinese_name": meta.get("chinese_name", ""),
                "style": ", ".join(meta.get("style", [])),
                "best_for": ", ".join(meta.get("best_for", [])),
            }
        )
        documents.append(doc)
    
    return documents

def split_investor_documents(documents, chunk_size: int = 900, chunk_overlap: int = 200):
    """将投资者长文档分块，并记录 start_index 用于精确溯源"""
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    except Exception:
        from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " "],
        add_start_index=True,
    )

    split_docs = []

    for parent in documents:
        investor_id = parent.metadata.get("investor_id", "unknown")
        chunks = splitter.split_documents([parent])

        for idx, doc in enumerate(chunks):
            # 标题提示：取 chunk 内第一个 markdown 标题
            m = re.search(r"(?m)^(#{1,4})\s+(.+?)\s*$", doc.page_content)
            title_hint = m.group(2) if m else ""

            doc.metadata["source_type"] = "investor_doc"
            doc.metadata["chunk_index"] = idx
            doc.metadata["chunk_id"] = f"{investor_id}#{idx}"
            if title_hint:
                doc.metadata["title_hint"] = title_hint

        split_docs.extend(chunks)

    return split_docs

def load_decision_rules():
    """加载决策规则为 Document 格式"""
    try:
        from langchain.schema import Document  # type: ignore
    except Exception:
        from langchain_core.documents import Document  # type: ignore
    
    rules_file = PROJECT_ROOT / "config" / "decision_rules.generated.json"
    if not rules_file.exists():
        return []
    
    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    kind_labels = {
        "entry": "入场规则 (Entry)",
        "exit": "出场规则 (Exit)",
        "risk_management": "风险管理 (Risk Management)",
        "other": "其他 (Other)"
    }
    
    documents = []
    for rule in data.get("rules", []):
        kind = rule.get('kind', 'other')
        kind_label = kind_labels.get(kind, kind)
        
        # 将规则转为自然语言
        content = f"""
投资者: {rule.get('investor_id', 'unknown')}
规则类型: {kind_label}

IF {rule.get('when', 'N/A')}
THEN {rule.get('then', 'N/A')}
BECAUSE {rule.get('because', 'N/A')}
        """.strip()
        
        doc = Document(
            page_content=content,
            metadata={
                "source": "decision_rules.generated.json",
                "investor_id": rule.get("investor_id", "unknown"),
                "rule_id": rule.get("rule_id", ""),
                "kind": kind,
                "source_type": "rule",
            }
        )
        documents.append(doc)
    
    return documents

def get_embeddings():
    """获取 Embedding 模型配置"""
    from langchain_community.embeddings import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

def create_vectorstore(documents, persist_dir=None):
    """创建并可选持久化向量存储"""
    from langchain_community.vectorstores import Chroma
    embeddings = get_embeddings()
    
    if persist_dir:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        # Since Chroma 0.4.x, persist() is often automatic or handled via persistent client
        # vectorstore.persist()
    else:
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings
        )
    return vectorstore

def load_vectorstore(persist_dir: str):
    """从持久化目录加载向量存储"""
    from langchain_community.vectorstores import Chroma
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=get_embeddings(),
    )

def query_vectorstore(vectorstore, query: str, k: int = 5, filter_dict: dict = None):
    """查询向量存储，支持元数据过滤"""
    return vectorstore.similarity_search_with_score(
        query, 
        k=k,
        filter=filter_dict
    )
