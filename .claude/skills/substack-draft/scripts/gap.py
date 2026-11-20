#!/usr/bin/env python3
"""Find blog posts that have no Substack post or draft yet.

Usage:
    python gap.py <docs_dir> <substack_inventory.json> [--json]

The inventory JSON is what scripts/substack_inventory.js returns when run in
the signed-in Substack tab: {"published": [...], "drafts": [...]}, each entry
having a `title`. Drafts report their title in `draft_title`, so the collector
normalises both into `title` before writing the file.

Matching is on a normalised title, not the URL: the blog has been restructured
before (ai/ -> tokenomics/), which changes every permalink while the titles
stay put. Dates move too, so they are not part of the key either.
"""
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

SITE = "https://hoopdad.github.io"


def normalise(title):
    """Fold a title to a comparison key: case, punctuation and spacing differ
    between the blog source and what Substack stores (curly quotes, mainly)."""
    t = unicodedata.normalize("NFKD", title or "")
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("—", "-").replace("–", "-")
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return t.strip()


def read_post(path):
    """Return (title, date, permalink) for a Jekyll post."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    title = None
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.S)
    if m:
        fm = re.search(r"^title:\s*(.+?)\s*$", m.group(1), re.M)
        if fm:
            title = fm.group(1).strip().strip('"').strip("'")
    if not title:
        # posts without front matter carry their title as a leading H1
        h1 = re.search(r"^#\s+(.+?)\s*$", raw, re.M)
        title = h1.group(1).strip() if h1 else path.stem

    collection = path.parts[-3]
    y, mo, d, slug = path.stem.split("-", 3)
    return title, "%s-%s-%s" % (y, mo, d), "%s/%s/%s/%s/%s/%s.html" % (
        SITE, collection, y, mo, d, slug)


def collect_posts(docs):
    posts = []
    for path in sorted(docs.glob("*/_posts/*.md")):
        title, date, url = read_post(path)
        posts.append({
            "title": title,
            "date": date,
            "url": url,
            "path": str(path.relative_to(docs)).replace("\\", "/"),
        })
    return posts


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if len(args) < 2:
        print(__doc__)
        return 2

    docs = Path(args[0])
    inv = json.loads(Path(args[1]).read_text(encoding="utf-8"))

    covered = {}
    for kind in ("published", "drafts"):
        for row in inv.get(kind, []):
            t = row.get("title") or row.get("draft_title") or ""
            if t.strip():
                covered.setdefault(normalise(t), kind)

    posts = collect_posts(docs)
    gaps = [p for p in posts if normalise(p["title"]) not in covered]

    if as_json:
        print(json.dumps(gaps, indent=2))
        return 0

    print("blog posts      : %d" % len(posts))
    print("substack posts  : %d published, %d drafts (%d with titles)"
          % (len(inv.get("published", [])), len(inv.get("drafts", [])), len(covered)))
    print("missing          : %d" % len(gaps))
    if gaps:
        print()
        for g in sorted(gaps, key=lambda g: g["date"], reverse=True):
            print("  %s  %s" % (g["date"], g["title"]))
            print("  %s  %s" % (" " * 10, g["url"]))
    # a post covered only by a draft is worth knowing about: it is queued, not live
    draft_only = [p for p in posts if covered.get(normalise(p["title"])) == "drafts"]
    if draft_only:
        print("\ncovered by an unpublished draft (%d):" % len(draft_only))
        for p in sorted(draft_only, key=lambda p: p["date"], reverse=True):
            print("  %s  %s" % (p["date"], p["title"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
