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

# Deterministic allocation policy (used to generate primary.target_allocation).
# Goal: improve risk-adjusted returns (Sharpe) by reducing LLM numeric noise and
# dampening aggressive shifts under expert conflicts.
ALLOCATION_POLICY: Dict[str, Any] = {
    "objective": "sharpe",
    # Map final_multiplier_offset (-0.50..+0.50) to a stocks delta in percentage points.
    # Smaller amplitude => smoother allocations (typically improves Sharpe).
    "amplitude": 8,  # +/- 8% stocks swing at max offset
    # When experts conflict, dampen the effective offset to avoid whipsaw.
    "conflict_damping": 0.7,
    # Mapping (non-linear + asymmetric): risk-on slower, risk-off faster.
    # This usually improves downside risk metrics (Sortino) by reducing whipsaw
    # while cutting risk more quickly under stress.
    "mapping_mode": "asymmetric_power",
    "exp_up": 1.35,     # >1 => slower risk-on
    "exp_down": 0.85,   # <1 => faster risk-off
    "scale_up": 0.90,
    "scale_down": 1.10,
    # Soft bounds
    "min_cash": 5,
    "max_cash": 30,
    # Regime base allocations (must sum to 100; will be normalized defensively).
    "regime_bases": {
        "neutral": {"stocks": 60, "bonds": 20, "gold": 10, "cash": 10},
        "bull": {"stocks": 70, "bonds": 15, "gold": 5, "cash": 10},
        "crisis": {"stocks": 40, "bonds": 30, "gold": 15, "cash": 15},
        "stagflation": {"stocks": 50, "bonds": 20, "gold": 20, "cash": 10},
    },
}

if isinstance(_CFG.get("allocation_policy"), dict):
    ap = _CFG.get("allocation_policy") or {}
    if isinstance(ap.get("regime_bases"), dict):
        ALLOCATION_POLICY["regime_bases"] = {**ALLOCATION_POLICY["regime_bases"], **ap.get("regime_bases")}
    for k in (
        "objective",
        "amplitude",
        "conflict_damping",
        "mapping_mode",
        "exp_up",
        "exp_down",
        "scale_up",
        "scale_down",
        "min_cash",
        "max_cash",
    ):
        if k in ap:
            ALLOCATION_POLICY[k] = ap.get(k)


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
        abs_sum = 0.0
        expert_contributions = []
        
        # Track conflicts (opposite signs)
        pos_impacts = []
        neg_impacts = []

        for op in opinions:
            category = cls.EXPERT_CATEGORIES.get(op.investor_id, "value")
            weight = regime_weights.get(category, 0.5) * op.confidence
            
            impact_value = op.impact * weight
            weighted_sum += impact_value
            abs_sum += abs(impact_value)
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

        # Continuous disagreement score in [0..1]:
        # - 0 => aligned (all contributions in same direction)
        # - 1 => strong cancellation (experts heavily disagree)
        disagreement_score = 0.0
        try:
            if abs_sum > 0:
                disagreement_score = 1.0 - min(1.0, abs(weighted_sum) / abs_sum)
                disagreement_score = max(0.0, min(1.0, float(disagreement_score)))
        except Exception:
            disagreement_score = 0.0
        
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
            "disagreement_score": round(float(disagreement_score), 3),
            "resolution": resolution_msg,
            "contributions": expert_contributions
        }


class SharpePrimaryAllocator:
    """
    Deterministic allocator for primary.target_allocation.

    Inputs:
    - regime_id: inferred/known market regime (bull/neutral/crisis/stagflation)
    - final_multiplier_offset: [-0.50..+0.50] risk adjustment from EnsembleAdjudicator
    - conflict_detected: whether committee opinions materially disagree

    Output:
    - allocation dict with keys stocks/bonds/gold/cash, integer percentages, sum=100.
    """

    @staticmethod
    def _clamp(v: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, v))

    @classmethod
    def _normalize_int_alloc(cls, raw: Dict[str, Any]) -> Dict[str, int]:
        base = {"stocks": 60, "bonds": 20, "gold": 10, "cash": 10}
        out: Dict[str, int] = {}
        for k in ("stocks", "bonds", "gold", "cash"):
            v = raw.get(k, base[k])
            try:
                iv = int(round(float(v)))
            except Exception:
                iv = int(base[k])
            out[k] = max(0, min(100, iv))

        s = sum(out.values())
        if s == 100:
            return out
        if s <= 0:
            return base

        # proportional scale to 100 with drift fix
        scaled = {k: int(round(out[k] * 100.0 / s)) for k in out}
        drift = 100 - sum(scaled.values())
        if drift != 0:
            kmax = max(scaled.keys(), key=lambda kk: scaled[kk])
            scaled[kmax] = max(0, min(100, scaled[kmax] + drift))
        if sum(scaled.values()) != 100:
            return base
        return scaled

    @classmethod
    def allocate(
        cls,
        regime_id: str,
        final_multiplier_offset: float,
        conflict_detected: bool = False,
        disagreement_score: Optional[float] = None,
    ) -> Dict[str, int]:
        ap = ALLOCATION_POLICY or {}

        # Regime base
        bases = ap.get("regime_bases") if isinstance(ap.get("regime_bases"), dict) else {}
        base_raw = (bases or {}).get(regime_id) or (bases or {}).get("neutral") or {}
        base = cls._normalize_int_alloc(base_raw)

        # Effective offset
        try:
            off = float(final_multiplier_offset)
        except Exception:
            off = 0.0
        off = cls._clamp(off, -0.5, 0.5)

        # Continuous damping for stability (Sortino/Sharpe):
        # - if disagreement_score provided: interpolate between 1.0 and conflict_damping
        # - else fall back to boolean conflict_detected
        try:
            damp_min = float(ap.get("conflict_damping") or 0.7)
        except Exception:
            damp_min = 0.7
        damp_min = cls._clamp(damp_min, 0.0, 1.0)

        if disagreement_score is not None:
            try:
                ds = float(disagreement_score)
            except Exception:
                ds = 0.0
            ds = cls._clamp(ds, 0.0, 1.0)
            damp = 1.0 - ds * (1.0 - damp_min)  # ds=0 => 1.0; ds=1 => damp_min
            off *= damp
        elif conflict_detected:
            off *= damp_min

        # Map offset to stocks delta
        try:
            amp = float(ap.get("amplitude") or 8.0)
        except Exception:
            amp = 8.0
        amp = cls._clamp(amp, 0.0, 25.0)

        risk_score = off / 0.5 if 0.5 != 0 else 0.0  # [-1..1]
        risk_score = cls._clamp(risk_score, -1.0, 1.0)

        # Non-linear + asymmetric mapping to reduce whipsaw:
        # - risk-on (positive) moves slower
        # - risk-off (negative) moves faster
        mode = str(ap.get("mapping_mode") or "asymmetric_power").strip()
        eff = risk_score
        if mode == "asymmetric_power":
            try:
                exp_up = float(ap.get("exp_up") or 1.35)
            except Exception:
                exp_up = 1.35
            try:
                exp_down = float(ap.get("exp_down") or 0.85)
            except Exception:
                exp_down = 0.85
            try:
                scale_up = float(ap.get("scale_up") or 0.9)
            except Exception:
                scale_up = 0.9
            try:
                scale_down = float(ap.get("scale_down") or 1.1)
            except Exception:
                scale_down = 1.1

            exp_up = cls._clamp(exp_up, 0.2, 3.0)
            exp_down = cls._clamp(exp_down, 0.2, 3.0)
            scale_up = cls._clamp(scale_up, 0.0, 2.0)
            scale_down = cls._clamp(scale_down, 0.0, 2.0)

            if risk_score >= 0:
                eff = (risk_score ** exp_up) * scale_up
            else:
                eff = -((abs(risk_score) ** exp_down) * scale_down)

        eff = cls._clamp(float(eff), -1.0, 1.0)
        delta = int(round(amp * eff))

        # Distribute delta across safe buckets proportionally to base weights (smoother).
        safe_total = 100 - base["stocks"]
        if safe_total <= 0:
            out = {"stocks": 100, "bonds": 0, "gold": 0, "cash": 0}
        else:
            out_f: Dict[str, float] = {"stocks": float(base["stocks"] + delta)}
            for k in ("bonds", "gold", "cash"):
                out_f[k] = float(base[k]) - float(delta) * (float(base[k]) / float(safe_total))
            out = {k: int(round(out_f[k])) for k in ("stocks", "bonds", "gold", "cash")}

        out = {k: max(0, min(100, int(out.get(k, 0)))) for k in ("stocks", "bonds", "gold", "cash")}

        # Soft cash bounds (improve execution + reduce extreme allocations)
        try:
            min_cash = int(round(float(ap.get("min_cash") or 5)))
        except Exception:
            min_cash = 5
        try:
            max_cash = int(round(float(ap.get("max_cash") or 30)))
        except Exception:
            max_cash = 30
        min_cash = max(0, min(100, min_cash))
        max_cash = max(0, min(100, max_cash))
        if max_cash < min_cash:
            max_cash = min_cash

        if out["cash"] < min_cash:
            need = min_cash - out["cash"]
            out["cash"] += need
            for src in ("bonds", "gold", "stocks"):
                take = min(need, out[src])
                out[src] -= take
                need -= take
                if need <= 0:
                    break

        if out["cash"] > max_cash:
            excess = out["cash"] - max_cash
            out["cash"] -= excess
            # Prefer bonds for Sharpe stability; then gold; then stocks.
            for dst in ("bonds", "gold", "stocks"):
                out[dst] += excess
                break

        # Final normalize
        return cls._normalize_int_alloc(out)

