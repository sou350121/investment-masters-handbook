import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from _utils import parse_front_matter, read_text, repo_root


def _make_rule(rule_id, investor_id, kind, when, then, because, source_file):
    return {
        "rule_id": rule_id,
        "investor_id": investor_id,
        "kind": kind,
        "when": when,
        "then": then,
        "because": because,
        "source_file": source_file,
    }


RE_IF = re.compile(r"^IF\s+(.*)$", re.IGNORECASE)
RE_THEN = re.compile(r"^THEN\s+(.*)$", re.IGNORECASE)
RE_BECAUSE = re.compile(r"^BECAUSE\s+(.*)$", re.IGNORECASE)


def _stable_rule_id(investor_id: str, kind: str, idx: int) -> str:
    return f"{investor_id}:{kind}:{idx:03d}"


def _extract_blocks_under_decision_rules(body):
    """
    Heuristic extractor:
    - Find the first heading containing 'DECISION_RULES'
    - Collect fenced code blocks (``` ... ```) after that point.
    """
    body = body.replace("\\r\\n", "\\n").replace("\\r", "\\n")
    pos = body.lower().find("decision_rules")
    if pos < 0:
        return []
    tail = body[pos:]

    blocks = []
    parts = tail.split("```")
    # odd indices are fenced content
    for i in range(1, len(parts), 2):
        blocks.append(parts[i])
    return blocks


def _parse_rule_block(block):
    """
    Parse a code fence body that contains multiple IF/THEN/BECAUSE sequences.
    Return list of (when, then, because)
    """
    lines = [ln.strip() for ln in block.splitlines()]
    rules = []

    cur_when = []
    cur_then = []
    cur_because = []
    state = None

    def flush():
        nonlocal cur_when, cur_then, cur_because, state
        if cur_when and cur_then:
            because = " ".join(cur_because).strip() if cur_because else None
            rules.append((" ".join(cur_when).strip(), " ".join(cur_then).strip(), because))
        cur_when, cur_then, cur_because, state = [], [], [], None

    for ln in lines + [""]:  # sentinel empty line
        if not ln:
            flush()
            continue

        m_if = RE_IF.match(ln)
        m_then = RE_THEN.match(ln)
        m_because = RE_BECAUSE.match(ln)

        if m_if:
            # start new rule
            if cur_when and cur_then:
                flush()
            state = "when"
            cur_when.append(m_if.group(1).strip())
            continue
        if m_then:
            state = "then"
            cur_then.append(m_then.group(1).strip())
            continue
        if m_because:
            state = "because"
            cur_because.append(m_because.group(1).strip())
            continue

        # continuation line
        if state == "when":
            cur_when.append(ln)
        elif state == "then":
            cur_then.append(ln)
        elif state == "because":
            cur_because.append(ln)
        else:
            # ignore stray lines (e.g., titles) to avoid noise
            continue

    return rules


def extract_from_investor_md(path):
    text = read_text(path)
    fm = parse_front_matter(text)
    investor_id = path.stem
    body = text
    if fm:
        investor_id = str(fm.data.get("investor_id") or investor_id)
        body = fm.body

    blocks = _extract_blocks_under_decision_rules(body)
    if not blocks:
        return []

    extracted = []
    per_kind_counter = {}

    for block in blocks:
        lower = block.lower()
        if "买入" in block or "buy" in lower:
            kind = "buy"
        elif "卖出" in block or "sell" in lower:
            kind = "sell"
        elif "不买" in block or "avoid" in lower:
            kind = "avoid"
        else:
            kind = "other"

        triples = _parse_rule_block(block)
        if not triples:
            continue

        per_kind_counter.setdefault(kind, 0)
        for when, then, because in triples:
            per_kind_counter[kind] += 1
            rid = _stable_rule_id(investor_id, kind, per_kind_counter[kind])
            extracted.append(
                _make_rule(
                    rule_id=rid,
                    investor_id=investor_id,
                    kind=kind,
                    when=when,
                    then=then,
                    because=because,
                    source_file=str(path.relative_to(repo_root())),
                )
            )

    return extracted


def extract_all():
    root = repo_root()
    out = []
    seen_ids = set()

    for md in sorted((root / "investors").glob("*.md")):
        rules = extract_from_investor_md(md)
        for r in rules:
            rid = r.get("rule_id")
            if rid in seen_ids:
                print("[rules] duplicate rule_id: {} ({})".format(rid, md), file=sys.stderr)
                raise SystemExit(2)
            seen_ids.add(rid)
            out.append(r)

    return out


if __name__ == "__main__":
    rules = extract_all()
    print("[rules] extracted: {}".format(len(rules)))


