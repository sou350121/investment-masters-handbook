# -*- coding: utf-8 -*-
"""Fetch investor avatars from Wikipedia REST summary.

Downloads small thumbnails (usually 200-400px wide) into:
  web/public/avatars/

This script is best-effort:
- If a page has no thumbnail, it will be skipped.
- Some investors may not have a Wikipedia page; they will be skipped.

Usage:
  python tools/fetch_avatars_wikipedia.py

"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "web" / "public" / "avatars"

# id -> wikipedia title (en)
WIKI_TITLE_BY_ID: dict[str, str] = {
    "warren_buffett": "Warren Buffett",
    "charlie_munger": "Charlie Munger",
    "peter_lynch": "Peter Lynch",
    "seth_klarman": "Seth Klarman",
    "ray_dalio": "Ray Dalio",
    "stanley_druckenmiller": "Stanley Druckenmiller",
    "george_soros": "George Soros",
    "howard_marks": "Howard Marks (investor)",
    "michael_burry": "Michael Burry",
    "carl_icahn": "Carl Icahn",
    "james_simons": "James Simons",
    "ed_thorp": "Edward O. Thorp",
    "cliff_asness": "Cliff Asness",
    "duan_yongping": "Duan Yongping",
    "greg_abel": "Greg Abel",
}

# Optional: try Chinese Wikipedia for CN investors (or when en has no images).
ZH_WIKI_TITLE_BY_ID: dict[str, str] = {
    "duan_yongping": "段永平",
    "qiu_guolu": "邱国鹭",
    "feng_liu": "冯柳",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "imh-avatar-fetcher/1.0 (local script)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8", errors="replace")
    return json.loads(data)


def fetch_thumb_via_action_api(title: str) -> str | None:
    """Fallback to MediaWiki action API pageimages."""
    encoded_title = urllib.parse.quote(title.replace(" ", "_"), safe="")
    api = (
        "https://en.wikipedia.org/w/api.php"
        f"?action=query&titles={encoded_title}"
        "&prop=pageimages&format=json&pithumbsize=400"
    )

    data = fetch_json(api)
    pages = ((data.get("query") or {}).get("pages") or {})
    for _page_id, page in pages.items():
        thumb = (page.get("thumbnail") or {}).get("source")
        if thumb:
            return thumb
    return None


def fetch_thumb_from_rest_summary(lang: str, title: str) -> str | None:
    encoded = urllib.parse.quote(title.replace(" ", "_"), safe="")
    api = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    data = fetch_json(api)
    return (data.get("thumbnail") or {}).get("source")


def wikidata_best_image(name: str, language: str = "en") -> str | None:
    """Try to find a P18 image via Wikidata search."""
    q = urllib.parse.quote(name, safe="")
    search_url = (
        "https://www.wikidata.org/w/api.php"
        f"?action=wbsearchentities&search={q}&language={language}&format=json&limit=1"
    )
    data = fetch_json(search_url)
    results = data.get("search") or []
    if not results:
        return None
    qid = results[0].get("id")
    if not qid:
        return None

    entity_url = (
        "https://www.wikidata.org/w/api.php"
        f"?action=wbgetentities&ids={qid}&props=claims&format=json"
    )
    ent = fetch_json(entity_url)
    entities = ent.get("entities") or {}
    e = entities.get(qid) or {}
    claims = e.get("claims") or {}
    p18 = claims.get("P18") or []
    if not p18:
        return None
    mainsnak = p18[0].get("mainsnak") or {}
    datavalue = mainsnak.get("datavalue") or {}
    value = datavalue.get("value")
    if not value or not isinstance(value, str):
        return None

    # value is a Commons filename like "Example.jpg"
    encoded_file = urllib.parse.quote(value.replace(" ", "_"), safe="")
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded_file}?width=256"

def download(url: str, out_path: Path) -> None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "imh-avatar-fetcher/1.0 (local script)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        content = resp.read()
    out_path.write_bytes(content)


def safe_ext_from_url(url: str) -> str:
    # Try to keep the original extension (jpg/png/webp).
    path = urllib.parse.urlparse(url).path
    m = re.search(r"\.(jpg|jpeg|png|webp)$", path, re.IGNORECASE)
    if not m:
        return ".jpg"
    ext = m.group(1).lower()
    if ext == "jpeg":
        ext = "jpg"
    return f".{ext}"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = 0
    skipped = 0

    for investor_id, title in WIKI_TITLE_BY_ID.items():
        try:
            thumb = fetch_thumb_from_rest_summary("en", title)
            data = {}
        except Exception as e:
            thumb = None
            data = {"_error": str(e)}

        if not thumb:
            try:
                thumb = fetch_thumb_via_action_api(title)
            except Exception:
                thumb = None

        # Fallback: Chinese Wikipedia for certain ids
        if not thumb and investor_id in ZH_WIKI_TITLE_BY_ID:
            zh_title = ZH_WIKI_TITLE_BY_ID[investor_id]
            try:
                thumb = fetch_thumb_from_rest_summary("zh", zh_title)
            except Exception:
                thumb = None

        # Fallback: Wikidata P18 (sometimes available even when Wikipedia pages have no thumbnails)
        if not thumb:
            try:
                thumb = wikidata_best_image(title, language="en")
            except Exception:
                thumb = None

        if not thumb:
            if "_error" in data:
                print(f"[skip] {investor_id}: fetch failed and no thumbnail")
            else:
                print(f"[skip] {investor_id}: no thumbnail")
            skipped += 1
            continue

        ext = safe_ext_from_url(thumb)
        out_path = OUT_DIR / f"{investor_id}{ext}"

        try:
            download(thumb, out_path)
        except Exception as e:
            print(f"[skip] {investor_id}: download failed: {e}")
            skipped += 1
            continue

        print(f"[ok]   {investor_id} -> {out_path.name}")
        ok += 1

    print("\nDone")
    print(f"- downloaded: {ok}")
    print(f"- skipped:    {skipped}")


if __name__ == "__main__":
    main()
