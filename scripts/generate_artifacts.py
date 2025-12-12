import sys
from pathlib import Path
from typing import Any, Dict, List

from _utils import dump_json, load_yaml, repo_root, write_text
from extract_decision_rules import extract_all


def _render_investor_table(idx):
    investors = idx.get("investors") or []
    rows = []
    for it in investors:
        if not isinstance(it, dict):
            continue
        inv_id = it.get("id", "")
        cn = it.get("chinese_name", "")
        en = it.get("full_name", "")
        fund = it.get("fund", "")
        style = it.get("style", [])
        best_for = it.get("best_for", [])
        related_doc = it.get("related_doc", "")
        style_s = ", ".join(style) if isinstance(style, list) else str(style)
        best_s = ", ".join(best_for) if isinstance(best_for, list) else str(best_for)
        link = f"../investors/{related_doc}" if related_doc else ""
        if link:
            name_cell = "[{}]({})".format(en, link)
        else:
            name_cell = en
        rows.append((inv_id, cn, name_cell, fund, style_s, best_s))

    header = (
        "# 投资人索引（自动生成）\n\n"
        "> 本文件由 `scripts/generate_artifacts.py` 从 `config/investor_index.yaml` 生成，请勿手工编辑。\n\n"
        "| id | 中文名 | 投资人 | 基金/机构 | 风格标签 | best_for |\n"
        "|---|---|---|---|---|---|\n"
    )
    body = "\n".join([f"| `{a}` | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in rows])
    return header + body + "\n"


def main() -> int:
    root = repo_root()
    idx_path = root / "config" / "investor_index.yaml"
    idx = load_yaml(idx_path) or {}

    # 1) generate investor table
    table_md = _render_investor_table(idx)
    write_text(root / "docs" / "INVESTORS.generated.md", table_md)

    # 2) extract machine-readable decision rules
    rules = extract_all()
    dump_json(root / "config" / "decision_rules.generated.json", {"version": "1.0", "rules": rules})

    print("[generate] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


