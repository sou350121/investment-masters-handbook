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


def extract_from_investor_md(path: Path) -> List[Dict[str, Any]]:
    text = read_text(path)
    fm = parse_front_matter(text)
    investor_id = path.stem
    body = text
    if fm:
        investor_id = str(fm.data.get("investor_id") or investor_id)
        body = fm.body

    # Locate the DECISION_RULES section
    lines = body.splitlines()
    start_idx = -1
    for i, line in enumerate(lines):
        if "decision_rules" in line.lower():
            start_idx = i
            break
    
    if start_idx == -1:
        return []

    relevant_lines = lines[start_idx:]
    extracted = []
    per_kind_counter = {}
    current_header = ""
    
    in_code_block = False
    current_block_lines = []

    for line in relevant_lines:
        trimmed = line.strip()
        
        # Header detection
        if not in_code_block and trimmed.startswith("#"):
            current_header = trimmed.lower()
            continue
            
        # Code block detection
        if trimmed.startswith("```"):
            if not in_code_block:
                in_code_block = True
                current_block_lines = []
            else:
                # End of code block
                in_code_block = False
                code_content = "\n".join(current_block_lines)
                
                # Determine kind
                kind = "other"
                if any(x in current_header for x in ["买入", "buy", "entry"]):
                    kind = "entry"
                elif any(x in current_header for x in ["卖出", "sell", "exit"]):
                    kind = "exit"
                elif any(x in current_header for x in ["不买", "avoid", "风险", "risk", "flags", "止损"]):
                    kind = "risk_management"
                
                if kind == "other":
                    lower_code = code_content.lower()
                    if any(x in lower_code for x in ["买入", "buy", "entry"]):
                        kind = "entry"
                    elif any(x in lower_code for x in ["卖出", "sell", "exit"]):
                        kind = "exit"
                    elif any(x in lower_code for x in ["不买", "avoid", "风险", "risk", "flags", "止损"]):
                        kind = "risk_management"

                triples = _parse_rule_block(code_content)
                if triples:
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
            continue
            
        if in_code_block:
            current_block_lines.append(line)

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
                # If we have duplicate IDs, it means the extraction or stability logic failed
                print(f"[rules] duplicate rule_id: {rid} in {md}", file=sys.stderr)
                # We'll just append a suffix for now to avoid crashing, but this shouldn't happen
                count = 1
                new_rid = f"{rid}_{count}"
                while new_rid in seen_ids:
                    count += 1
                    new_rid = f"{rid}_{count}"
                rid = new_rid
                r["rule_id"] = rid
                
            seen_ids.add(rid)
            out.append(r)

    return out


if __name__ == "__main__":
    rules = extract_all()
    print("[rules] extracted: {}".format(len(rules)))
