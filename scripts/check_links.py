import re
import sys
from pathlib import Path

from _utils import repo_root


# Markdown inline link: [text](target)
RE_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def is_external(href: str) -> bool:
    href = href.strip()
    return (
        href.startswith("http://")
        or href.startswith("https://")
        or href.startswith("mailto:")
        or href.startswith("#")
    )


def strip_fragment(href: str) -> str:
    return href.split("#", 1)[0]


def main() -> int:
    root = repo_root()
    failed = False

    md_files = sorted(root.rglob("*.md"))
    for md in md_files:
        text = md.read_text(encoding="utf-8", errors="replace")
        for m in RE_LINK.finditer(text):
            href = m.group(1).strip()
            if is_external(href):
                continue
            href = strip_fragment(href)
            if not href:
                continue

            # Ignore angle-bracket style <...> links inside ()
            href = href.strip("<>").strip()

            # Only validate relative paths within repo
            if href.startswith("/"):
                target = root / href.lstrip("/")
            else:
                target = (md.parent / href).resolve()

            # Keep inside repo root
            try:
                target.relative_to(root)
            except ValueError:
                print(f"[links] {md}: link escapes repo: {href}", file=sys.stderr)
                failed = True
                continue

            if not target.exists():
                print(f"[links] {md}: missing target: {href}", file=sys.stderr)
                failed = True

    if failed:
        return 1
    print("[links] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


