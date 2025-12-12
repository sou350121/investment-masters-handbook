import re
import sys
from pathlib import Path

from _utils import iter_text_files, repo_root


EMAIL_RE = re.compile(r"(?i)(?<![\\w.])[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}(?![\\w.])")
AWS_KEY_RE = re.compile(r"AKIA[0-9A-Z]{16}")
GITHUB_TOKEN_RE = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PRIVATE) KEY-----")

# allowlist emails that are typically non-sensitive placeholders
ALLOW_EMAIL = {
    "sou350121@users.noreply.github.com",
    "example@example.com",
    "kitwa.sou@example.com",
}


def main() -> int:
    root = repo_root()
    exts = {".md", ".yaml", ".yml", ".py", ".txt"}
    failed = False

    for p in iter_text_files(root, exts):
        # Skip git internals if any
        if ".git" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")

        for m in EMAIL_RE.finditer(text):
            email = m.group(0)
            if email in ALLOW_EMAIL:
                continue
            # common false positives in docs are still privacy-relevant; fail hard
            print(f"[sensitive] {p}: email found: {email}", file=sys.stderr)
            failed = True

        if AWS_KEY_RE.search(text):
            print(f"[sensitive] {p}: AWS access key pattern found", file=sys.stderr)
            failed = True

        if GITHUB_TOKEN_RE.search(text):
            print(f"[sensitive] {p}: GitHub token pattern found", file=sys.stderr)
            failed = True

        if PRIVATE_KEY_RE.search(text):
            print(f"[sensitive] {p}: private key block found", file=sys.stderr)
            failed = True

    if failed:
        return 1
    print("[sensitive] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


