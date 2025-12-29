"""
Build static backtest runs index for the exported web UI.

We scan: investment-masters-handbook/web/public/backtests/<run_id>/
and write: investment-masters-handbook/web/public/backtests/index.json

This enables a **pure static** backtest history viewer (no /api/backtest/* required).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


PROJECT_ROOT = Path(__file__).parent.parent
STATIC_ROOT = PROJECT_ROOT / "web" / "public" / "backtests"
INDEX_PATH = STATIC_ROOT / "index.json"


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _iso_from_mtime(ts: float) -> str:
    # localtime ISO without timezone suffix (matches existing API style)
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ts or 0.0))


def _list_runs(static_root: Path) -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []
    if not static_root.exists():
        return runs

    for child in sorted(static_root.iterdir()):
        if not child.is_dir():
            continue
        run_id = child.name
        if run_id.startswith("."):
            continue

        metrics_a = _read_json(child / "metrics_A.json")
        metrics_b = _read_json(child / "metrics_B.json")

        modes: List[str] = []
        metrics: Dict[str, Any] = {}
        if metrics_a is not None:
            modes.append("A")
            metrics["A"] = metrics_a
        if metrics_b is not None:
            modes.append("B")
            metrics["B"] = metrics_b

        # only list folders that look like a run
        has_any = any(
            (child / fn).exists()
            for fn in (
                "metrics_A.json",
                "metrics_B.json",
                "equity_curve_A.csv",
                "equity_curve_B.csv",
                "history_A.csv",
                "history_B.csv",
                "comparison.md",
                "run_config.json",
            )
        )
        if not has_any:
            continue

        try:
            st = child.stat()
            mtime = float(st.st_mtime)
        except Exception:
            mtime = 0.0

        runs.append(
            {
                "run_id": run_id,
                "root": "static",
                "last_modified_ts": mtime,
                "last_modified_iso": _iso_from_mtime(mtime),
                "modes": modes,
                "metrics": metrics,
            }
        )

    runs.sort(key=lambda r: float(r.get("last_modified_ts") or 0.0), reverse=True)
    return runs


def main() -> int:
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
    runs = _list_runs(STATIC_ROOT)
    payload = {"root": "static", "runs": runs}
    INDEX_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {INDEX_PATH} (runs={len(runs)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


