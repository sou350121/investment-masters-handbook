import sys
from pathlib import Path

from _utils import parse_front_matter, repo_root


REQUIRED_FIELDS = [
    "investor_id",
    "full_name",
    "chinese_name",
    "fund",
    "style",
    "applicable_scenarios",
    "decision_weight",
    "tags",
]


def main() -> int:
    root = repo_root()
    investors_dir = root / "investors"
    if not investors_dir.exists():
        print(f"[front_matter] missing dir: {investors_dir}", file=sys.stderr)
        return 2

    failed = False

    for md in sorted(investors_dir.glob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        fm = parse_front_matter(text)
        if fm is None:
            print(f"[front_matter] {md.name}: missing/invalid YAML front matter", file=sys.stderr)
            failed = True
            continue

        data = fm.data
        for k in REQUIRED_FIELDS:
            if k not in data or data[k] in (None, "", []):
                print(f"[front_matter] {md.name}: missing required field: {k}", file=sys.stderr)
                failed = True

        investor_id = data.get("investor_id")
        if investor_id and md.stem != str(investor_id):
            print(
                f"[front_matter] {md.name}: filename stem != investor_id "
                f"({md.stem} != {investor_id})",
                file=sys.stderr,
            )
            failed = True

    if failed:
        return 1

    print("[front_matter] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


