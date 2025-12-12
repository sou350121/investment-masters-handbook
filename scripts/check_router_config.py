import sys
from collections import defaultdict
from pathlib import Path

from _utils import is_probably_regex_token, load_yaml, repo_root


def main() -> int:
    root = repo_root()
    investor_index_path = root / "config" / "investor_index.yaml"
    router_config_path = root / "config" / "router_config.yaml"

    idx = load_yaml(investor_index_path) or {}
    router = load_yaml(router_config_path) or {}

    investors = idx.get("investors") or []
    investor_ids = {i.get("id") for i in investors if isinstance(i, dict) and i.get("id")}

    prompt_roles = router.get("prompt_roles") or {}
    prompt_ids = set(prompt_roles.keys())

    failed = False

    # 1) referenced investors/prompts exist
    patterns = (router.get("keyword_patterns") or {}) if isinstance(router, dict) else {}
    for key, spec in patterns.items():
        if not isinstance(spec, dict):
            continue
        invs = spec.get("investors") or []
        prps = spec.get("prompts") or []

        for inv in invs:
            if isinstance(inv, str) and inv.startswith("prompts/"):
                print(
                    f"[router] keyword_patterns.{key}.investors contains path-like value: {inv} "
                    f"(use prompts:[...] + investor ids)",
                    file=sys.stderr,
                )
                failed = True
                continue
            if inv not in investor_ids:
                print(f"[router] keyword_patterns.{key}: unknown investor id: {inv}", file=sys.stderr)
                failed = True

        for pid in prps:
            if pid not in prompt_ids:
                print(f"[router] keyword_patterns.{key}: unknown prompt id: {pid}", file=sys.stderr)
                failed = True

    # 2) lightweight overlap detection: plain tokens duplicated across multiple high-weight patterns
    token_to_patterns = defaultdict(list)
    for key, spec in patterns.items():
        if not isinstance(spec, dict):
            continue
        weight = float(spec.get("weight") or 0)
        if weight < 0.85:
            continue
        pat = spec.get("pattern") or ""
        if not isinstance(pat, str):
            continue
        for tok in [t.strip() for t in pat.split("|")]:
            if not tok or is_probably_regex_token(tok):
                continue
            token_to_patterns[tok].append(key)

    overlaps = {tok: keys for tok, keys in token_to_patterns.items() if len(set(keys)) >= 2}
    if overlaps:
        # don't fail by default; print report for maintainers
        print("[router] warning: potential keyword overlap (plain tokens) among high-weight patterns:")
        for tok, keys in sorted(overlaps.items(), key=lambda x: (len(x[1]), x[0]), reverse=True)[:50]:
            uniq = ", ".join(sorted(set(keys)))
            print(f"  - token={tok} patterns={uniq}")

    if failed:
        return 1

    print("[router] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


