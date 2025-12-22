"""
Validate docs/tasks task documents contain required sections.

This is intentionally lightweight: it enforces "minimal necessary context"
so multi-agent collaboration doesn't stall on missing DoD/Scope/Constraints/etc.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "docs" / "tasks"

# Required patterns (case-insensitive). Accept CN/EN headings used in repo.
REQUIRED_PATTERNS = {
    "goal": re.compile(r"^##\s*\d+\.\s*目标\b|^##\s*目标\b|^##\s*\d+\.\s*Goal\b|^##\s*Goal\b", re.IGNORECASE | re.MULTILINE),
    "scope": re.compile(r"^##\s*\d+\.\s*范围\b|^##\s*范围\b|^##\s*\d+\.\s*Scope\b|^##\s*Scope\b", re.IGNORECASE | re.MULTILINE),
    "spec": re.compile(r"^##\s*\d+\.\s*详细规格\b|^##\s*详细规格\b|^##\s*\d+\.\s*Spec\b|^##\s*Spec\b", re.IGNORECASE | re.MULTILINE),
    "dod": re.compile(r"^##\s*\d+\.\s*验收标准\b|^##\s*验收标准\b|^##\s*\d+\.\s*DoD\b|^##\s*DoD\b", re.IGNORECASE | re.MULTILINE),
    "constraints": re.compile(r"^##\s*\d+\.\s*限制\b|^##\s*限制\b|^##\s*\d+\.\s*Constraints\b|^##\s*Constraints\b|^##\s*\d+\.\s*限制与不变量\b|^##\s*限制与不变量\b", re.IGNORECASE | re.MULTILINE),
    "test_plan": re.compile(r"^##\s*\d+\.\s*(运行/验证方式|Test Plan)\b|^##\s*(运行/验证方式|Test Plan)\b", re.IGNORECASE | re.MULTILINE),
}


def _is_task_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() != ".md":
        return False
    if path.name.upper().startswith("IMH-TASK-") and path.name.upper() != "IMH-TASK-README.MD":
        return True
    return False


def validate_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    missing = []
    for key, pat in REQUIRED_PATTERNS.items():
        if not pat.search(text):
            missing.append(key)
    return missing


def main() -> int:
    if not TASKS_DIR.exists():
        print(f"[validate_tasks] tasks dir not found: {TASKS_DIR}")
        return 0

    task_files = sorted([p for p in TASKS_DIR.iterdir() if _is_task_file(p)])
    if not task_files:
        print("[validate_tasks] no task files found; ok")
        return 0

    failed = False
    for f in task_files:
        missing = validate_file(f)
        if missing:
            failed = True
            print(f"[validate_tasks] FAIL {f.relative_to(REPO_ROOT)} missing sections: {', '.join(missing)}")
        else:
            print(f"[validate_tasks] ok   {f.relative_to(REPO_ROOT)}")

    if failed:
        print("\n[validate_tasks] Required sections: goal, scope, spec, dod, constraints, test_plan")
        print("[validate_tasks] Tip: copy docs/tasks/TEMPLATE.md")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


