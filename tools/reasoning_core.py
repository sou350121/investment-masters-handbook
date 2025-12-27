import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import yaml

@dataclass
class ExpertOpinion:
    investor_id: str
    impact: float  # -1.0 to 1.0 (Risk down to Risk up)
    confidence: float
    reason: str


class ExpertPersonality:
    """
    nofx-style personalities (used to bias the committee discussion like a debate).
    """

    BULL = "bull"
    BEAR = "bear"
    ANALYST = "analyst"
    CONTRARIAN = "contrarian"
    RISK_MANAGER = "risk_manager"


PERSONALITY_DESCRIPTIONS: Dict[str, str] = {
    ExpertPersonality.BULL: "Aggressive Bull: optimistic, looks for long opportunities, trend continuation.",
    ExpertPersonality.BEAR: "Cautious Bear: skeptical, focuses on risks, highlights downside and liquidity stress.",
    ExpertPersonality.ANALYST: "Data Analyst: neutral and data-driven, weighs evidence and uncertainty explicitly.",
    ExpertPersonality.CONTRARIAN: "Contrarian: challenges consensus, searches for overlooked risks/opportunities.",
    ExpertPersonality.RISK_MANAGER: "Risk Manager: capital preservation first, position sizing, stop losses, guardrails.",
}


# Default mapping: align major masters to debate roles (can be refined later).
MASTER_PERSONALITIES: Dict[str, str] = {
    # Macro
    "ray_dalio": ExpertPersonality.RISK_MANAGER,
    "george_soros": ExpertPersonality.CONTRARIAN,
    "stanley_druckenmiller": ExpertPersonality.ANALYST,
    # Value
    "warren_buffett": ExpertPersonality.BULL,
    "charlie_munger": ExpertPersonality.CONTRARIAN,
    # Distressed / cycle
    "seth_klarman": ExpertPersonality.BEAR,
    "howard_marks": ExpertPersonality.RISK_MANAGER,
    "michael_burry": ExpertPersonality.BEAR,
    # Growth / quant
    "peter_lynch": ExpertPersonality.BULL,
    "james_simons": ExpertPersonality.ANALYST,
    "ed_thorp": ExpertPersonality.ANALYST,
    "cliff_asness": ExpertPersonality.CONTRARIAN,
}

PROJECT_ROOT = Path(__file__).parent.parent
REASONING_CONFIG_PATH = PROJECT_ROOT / "config" / "reasoning_config.yaml"


def _load_reasoning_config() -> Dict[str, Any]:
    if not REASONING_CONFIG_PATH.exists():
        return {}
    try:
        data = yaml.safe_load(REASONING_CONFIG_PATH.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


_CFG: Dict[str, Any] = _load_reasoning_config()

if isinstance(_CFG.get("personality_descriptions"), dict):
    PERSONALITY_DESCRIPTIONS = {**PERSONALITY_DESCRIPTIONS, **_CFG["personality_descriptions"]}

if isinstance(_CFG.get("master_personalities"), dict):
    MASTER_PERSONALITIES = {**MASTER_PERSONALITIES, **_CFG["master_personalities"]}


def get_master_personality(investor_id: str) -> str:
    return MASTER_PERSONALITIES.get(str(investor_id or "").strip(), ExpertPersonality.ANALYST)


def get_personality_description(personality: str) -> str:
    return PERSONALITY_DESCRIPTIONS.get(personality, PERSONALITY_DESCRIPTIONS[ExpertPersonality.ANALYST])


class EnsembleAdjudicator:
    """
    Investment Committee Adjudicator.
    Synthesizes multiple expert opinions into a quantitative risk adjustment.
    """
    
    # Regime-to-Expert-Category Weight Matrix
    # Categories: macro, value, growth, quant, cycle, distressed
    REGIME_WEIGHTS = {
        "crisis": {
            "macro": 0.9,
            "distressed": 0.8,
            "cycle": 0.7,
            "value": 0.4,
            "growth": 0.2
        },
        "stagflation": {
            "macro": 0.8,
            "cycle": 0.8,
            "value": 0.6,
            "growth": 0.2
        },
        "bull": {
            "growth": 0.9,
            "value": 0.7,
            "quant": 0.7,
            "macro": 0.4
        },
        "neutral": {
            "value": 0.8,
            "growth": 0.6,
            "quant": 0.6,
            "cycle": 0.5
        }
    }

    # Expert ID to Category Mapping
    EXPERT_CATEGORIES = {
        "ray_dalio": "macro",
        "george_soros": "macro",
        "stanley_druckenmiller": "macro",
        "warren_buffett": "value",
        "charlie_munger": "value",
        "seth_klarman": "distressed",
        "howard_marks": "cycle",
        "michael_burry": "cycle",
        "peter_lynch": "growth",
        "james_simons": "quant",
        "ed_thorp": "quant",
        "cliff_asness": "quant"
    }

    # Allow overriding via config file (if present)
    if isinstance(_CFG.get("regime_weights"), dict):
        REGIME_WEIGHTS = {**REGIME_WEIGHTS, **_CFG["regime_weights"]}
    if isinstance(_CFG.get("expert_categories"), dict):
        EXPERT_CATEGORIES = {**EXPERT_CATEGORIES, **_CFG["expert_categories"]}

    @classmethod
    def adjudicate(cls, regime_id: str, opinions: List[ExpertOpinion]) -> Dict[str, Any]:
        """
        Adjudicate multiple expert opinions based on the current regime.
        Returns a dictionary with quantitative adjustments and reasoning.
        """
        if not opinions:
            return {
                "final_multiplier_offset": 0.0,
                "primary_expert": None,
                "conflict_detected": False,
                "resolution": "No expert opinions to adjudicate."
            }

        regime_weights = cls.REGIME_WEIGHTS.get(regime_id, cls.REGIME_WEIGHTS["neutral"])
        
        weighted_sum = 0.0
        total_weight = 0.0
        expert_contributions = []
        
        # Track conflicts (opposite signs)
        pos_impacts = []
        neg_impacts = []

        for op in opinions:
            category = cls.EXPERT_CATEGORIES.get(op.investor_id, "value")
            weight = regime_weights.get(category, 0.5) * op.confidence
            
            impact_value = op.impact * weight
            weighted_sum += impact_value
            total_weight += weight
            
            expert_contributions.append({
                "investor_id": op.investor_id,
                "weight": round(weight, 2),
                "impact": op.impact,
                "contribution": round(impact_value, 3)
            })

            if op.impact > 0.1:
                pos_impacts.append(op.investor_id)
            elif op.impact < -0.1:
                neg_impacts.append(op.investor_id)

        final_offset = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # Determine conflict
        conflict_detected = len(pos_impacts) > 0 and len(neg_impacts) > 0
        
        # Sort contributions to find primary expert
        expert_contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        primary_expert = expert_contributions[0]["investor_id"] if expert_contributions else None

        resolution_msg = f"Weighted average of {len(opinions)} experts in {regime_id} regime."
        if conflict_detected:
            resolution_msg = f"Resolved conflict between {', '.join(pos_impacts)} and {', '.join(neg_impacts)} based on {regime_id} priority."

        return {
            "final_multiplier_offset": round(final_offset, 3),
            "primary_expert": primary_expert,
            "conflict_detected": conflict_detected,
            "resolution": resolution_msg,
            "contributions": expert_contributions
        }

