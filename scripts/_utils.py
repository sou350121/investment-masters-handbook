import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Set

import yaml


RE_FENCE = re.compile(r"^```")


def repo_root() -> Path:
    # scripts/ -> investment-masters/
    return Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def iter_text_files(root: Path, exts: Set[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() in exts:
            yield p


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_newlines(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


class FrontMatter(object):
    def __init__(self, data: Dict[str, Any], body: str) -> None:
        self.data = data
        self.body = body


def parse_front_matter(md_text: str) -> Optional[FrontMatter]:
    md_text = normalize_newlines(md_text)
    if not md_text.startswith("---\n"):
        return None
    parts = md_text.split("\n---\n", 1)
    if len(parts) != 2:
        return None
    raw_yaml = parts[0][4:]  # strip leading '---\n'
    body = parts[1]
    data = yaml.safe_load(raw_yaml) or {}
    if not isinstance(data, dict):
        return None
    return FrontMatter(data=data, body=body)


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9_\\-]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def is_probably_regex_token(tok: str) -> bool:
    # Heuristic: treat tokens containing regex meta as regex-y and skip in overlap checks
    meta = set(["[", "]", "(", ")", ".", "?", "*", "+", "^", "$", "\\"])
    for ch in tok:
        if ch in meta:
            return True
    return False



