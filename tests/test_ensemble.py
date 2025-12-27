import json

import pytest
from fastapi.testclient import TestClient


class DummyDoc:
    def __init__(self, content: str, metadata: dict):
        self.page_content = content
        self.metadata = metadata


class DummyVectorStore:
    def __init__(self, hits):
        self._hits = hits

    def similarity_search_with_score(self, query, k=5, filter=None):
        # ignore query/filter in unit test
        return self._hits[:k]


def test_expert_selection_and_rule_hits_shape():
    from tools.rag_core import ensemble_reasoning

    hits = [
        (DummyDoc("IF A THEN B", {"investor_id": "ray_dalio", "rule_id": "R-1", "kind": "risk_management", "source": "decision_rules.generated.json"}), 0.05),
        (DummyDoc("IF C THEN D", {"investor_id": "ray_dalio", "rule_id": "R-2", "kind": "entry", "source": "decision_rules.generated.json"}), 0.10),
        (DummyDoc("IF E THEN F", {"investor_id": "warren_buffett", "rule_id": "R-3", "kind": "entry", "source": "decision_rules.generated.json"}), 0.20),
    ]
    vs = DummyVectorStore(hits)
    out = ensemble_reasoning(vs, "test", top_n_rules=3, top_k_experts=2)

    assert out["experts"][0] == "ray_dalio"
    assert set(out["experts"]) == {"ray_dalio", "warren_buffett"}
    assert len(out["rule_hits"]) == 3
    assert out["rule_hits"][0]["metadata"]["rule_id"] == "R-1"


def test_ensemble_endpoint_returns_quant_adjustment(monkeypatch):
    import services.rag_service as rs

    # Patch global vectorstore
    hits = [
        (DummyDoc("IF inflation high THEN reduce risk", {"investor_id": "ray_dalio", "rule_id": "R-10", "kind": "risk_management", "source": "decision_rules.generated.json"}), 0.05),
        (DummyDoc("IF moat strong THEN buy", {"investor_id": "warren_buffett", "rule_id": "R-20", "kind": "entry", "source": "decision_rules.generated.json"}), 0.10),
    ]
    rs.vectorstore = DummyVectorStore(hits)
    monkeypatch.setenv("IMH_API_TOKEN", "test-token")

    # Mock LLM call to return strict JSON with required fields
    def _fake_call_chat(self, messages):
        payload = {
            "primary": {
                "target_allocation": {"stocks": 45, "bonds": 35, "gold": 10, "cash": 10},
                "one_liner": "降低股票暴露，提高债券与现金以防守。",
                "confidence": 0.72,
            },
            "secondary": {
                "experts": ["ray_dalio", "warren_buffett"],
                "expert_opinions": [
                    {"expert": "ray_dalio", "summary": "更偏宏观防守。", "impact": -0.4, "confidence": 0.9, "citations": [1]},
                    {"expert": "warren_buffett", "summary": "关注护城河与估值。", "impact": 0.1, "confidence": 0.6, "citations": [2]},
                ],
                "consensus": "降低仓位，优先防守。",
                "conflicts": "是否应在下跌中逐步加仓优质公司。",
                "synthesis": "以宏观防守为主，择机小仓位价值分批。",
                "citations": [{"id": 1}, {"id": 2}],
                "ensemble_adjustment": {
                    "final_multiplier_offset": -0.15,
                    "primary_expert": "ray_dalio",
                    "conflict_detected": True,
                    "resolution": "Crisis regime prioritizes defensive macro over selective value.",
                },
            },
        }
        # nofx-style: return reasoning tag + json tag
        return (
            "<reasoning>Dalio focuses on macro risk; Buffett focuses on moat/value. Resolve with risk-first.</reasoning>\n"
            + "<json>"
            + json.dumps(payload, ensure_ascii=False)
            + "</json>"
        )

    monkeypatch.setattr(rs.LLMBridge, "call_chat", _fake_call_chat, raising=True)

    client = TestClient(rs.app)
    resp = client.post(
        "/api/rag/ensemble",
        json={"query": "现在该怎么配置？"},
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert "primary" in data and isinstance(data["primary"], dict)
    assert "secondary" in data and isinstance(data["secondary"], dict)

    # primary allocation shape
    alloc = data["primary"]["target_allocation"]
    assert set(alloc.keys()) == {"stocks", "bonds", "gold", "cash"}
    assert sum(int(alloc[k]) for k in alloc) == 100
    assert isinstance(data["primary"]["one_liner"], str) and data["primary"]["one_liner"]
    assert isinstance(data["primary"]["confidence"], (int, float))

    assert "ensemble_adjustment" in data["secondary"]
    adj = data["secondary"]["ensemble_adjustment"]
    # hybrid adjudication overrides LLM's direct offset with deterministic output
    assert isinstance(adj["final_multiplier_offset"], (int, float))
    assert adj["primary_expert"] in ("ray_dalio", "warren_buffett")
    assert isinstance(adj["conflict_detected"], bool)
    assert "resolution" in adj and adj["resolution"]
    assert "contributions" in adj and isinstance(adj["contributions"], list)

    # citations normalized by backend (ids 1..N with metadata)
    assert isinstance(data["secondary"]["citations"], list)
    assert data["secondary"]["citations"][0]["id"] == 1
    assert data["secondary"]["citations"][0]["rule_id"] == "R-10"
    assert "metadata" in data["secondary"]
    assert data["secondary"]["metadata"]["experts_personality"]["ray_dalio"] in ("risk_manager", "analyst", "bear", "bull", "contrarian")


