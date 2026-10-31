#!/usr/bin/env python3
"""Convert selected Jekyll posts into a Substack-importable RSS feed.

Mirrors the HTML conventions of the existing docs/substack-import.xml:
kramdown-style auto heading ids, language-tagged <pre><code>, absolute
image/link URLs under https://hoopdad.github.io.
"""
import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://hoopdad.github.io"
DOCS = Path(__file__).resolve().parent  # overridden by --docs


def slugify(text):
    """kramdown-ish auto id: lowercase, strip non-word, spaces -> hyphen."""
    t = re.sub(r"<[^>]+>", "", text)
    t = html.unescape(t).lower()
    t = re.sub(r"[^\w\s-]", "", t)
    t = re.sub(r"[\s_]+", "-", t.strip())
    return re.sub(r"-+", "-", t).strip("-")


def esc(text):
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def absolutize(url):
    if url.startswith("/"):
        return SITE + url
    return url


def inline(text):
    """Inline markdown -> HTML. Code spans are protected from other rules."""
    spans = []

    def stash_code(m):
        spans.append("<code>" + esc(m.group(1)) + "</code>")
        return "\x00%d\x00" % (len(spans) - 1)

    text = re.sub(r"`([^`]+)`", stash_code, text)
    text = esc(text)

    # <https://...> autolink; kramdown renders these, a bare URL it leaves as text
    text = re.sub(
        r"&lt;(https?://[^\s&]+)&gt;",
        lambda m: '<a href="%s">%s</a>' % (m.group(1).replace("&", "&amp;"), m.group(1)),
        text,
    )

    # images before links (both use the bracket form)
    def img(m):
        alt, src = m.group(1), absolutize(m.group(2))
        return '<img alt="%s" src="%s" />' % (alt, src)

    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, text)

    # {% post_url /cloud/2024-11-01-Name %} -> permalink
    def post_url(m):
        raw = m.group(1).strip().lstrip("/")
        coll, name = raw.split("/", 1)
        y, mo, d, slug = name.split("-", 3)
        return "%s/%s/%s/%s/%s/%s.html" % (SITE, coll, y, mo, d, slug)

    text = re.sub(r"\{%\s*post_url\s+([^%]+?)\s*%\}", post_url, text)

    def link(m):
        label, href = m.group(1), absolutize(m.group(2))
        return '<a href="%s">%s</a>' % (href.replace("&", "&amp;"), label)

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)

    # attribute lists: {:target="_blank"} -> fold onto the preceding <a>
    def attrlist(m):
        attrs = m.group(1).strip()
        return " " + attrs if attrs else ""

    text = re.sub(r"</a>\{:\s*([^}]*?)\s*\}", lambda m: "</a>", text)

    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)

    for i, s in enumerate(spans):
        text = text.replace("\x00%d\x00" % i, s)
    return text


def table_as_list(head, body):
    """Render a Markdown table as a bulleted list.

    Substack's editor has no table support: a pasted/imported <table> collapses
    into one run-on paragraph with every cell jammed together. So the feed never
    emits a table. Each row becomes a bullet: the first column is the label, the
    rest follow it. Short cells are joined bare under a lead-in naming the
    columns; long ones carry their own column name, which reads better when the
    values are sentences. The blog keeps its real tables — this is feed-only.
    """
    rest = [c for row in body for c in row[1:]]
    longhand = bool(rest) and (sum(len(c) for c in rest) / len(rest)) > 40

    items = []
    for row in body:
        label = inline(row[0])
        tail = []
        for j, cell in enumerate(row[1:], start=1):
            if not cell:
                continue
            name = head[j] if j < len(head) else ""
            tail.append(
                "%s: %s" % (inline(name), inline(cell)) if longhand else inline(cell)
            )
        items.append("  <li><strong>%s</strong> — %s</li>" % (label, " · ".join(tail)))

    parts = []
    if not longhand:
        lead = ", ".join(h for h in head[1:] if h)
        parts.append("<p>%s, in order:</p>" % inline(lead))
    parts.append("<ul>\n%s\n</ul>" % "\n".join(items))
    return "\n".join(parts)


def convert(md):
    """Block-level markdown -> HTML."""
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # fenced code
        m = re.match(r"^\s*```+\s*(\S*)\s*$", line)
        if m:
            lang = m.group(1)
            i += 1
            body = []
            while i < n and not re.match(r"^\s*```+\s*$", lines[i]):
                body.append(lines[i])
                i += 1
            i += 1
            # strip the common leading indent some posts use inside fences
            nonblank = [b for b in body if b.strip()]
            if nonblank:
                pad = min(len(b) - len(b.lstrip()) for b in nonblank)
                body = [b[pad:] if b.strip() else "" for b in body]
            cls = ' class="language-%s"' % lang if lang else ""
            out.append(
                "<pre><code%s>%s\n</code></pre>"
                % (cls, esc("\n".join(body).rstrip("\n")))
            )
            continue

        # blank
        if not stripped:
            i += 1
            continue

        # horizontal rule (these posts use --- between every section)
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            out.append("<hr />")
            i += 1
            continue

        # heading
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            lvl, text = len(m.group(1)), inline(m.group(2))
            out.append('<h%d id="%s">%s</h%d>' % (lvl, slugify(m.group(2)), text, lvl))
            i += 1
            continue

        # table
        if stripped.startswith("|") and i + 1 < n and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            def cells(row):
                return [c.strip() for c in row.strip().strip("|").split("|")]

            head = cells(lines[i])
            i += 2
            body = []
            while i < n and lines[i].strip().startswith("|"):
                body.append(cells(lines[i]))
                i += 1
            out.append(table_as_list(head, body))
            continue

        # blockquote
        if stripped.startswith(">"):
            body = []
            while i < n and lines[i].strip().startswith(">"):
                body.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append(
                "<blockquote>\n<p>%s</p>\n</blockquote>"
                % inline(" ".join(b.strip() for b in body if b.strip()))
            )
            continue

        # lists (ul / ol), one level of nesting
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", line)
        if m:
            ordered = bool(re.match(r"^\d+\.$", m.group(2)))
            tag = "ol" if ordered else "ul"
            items, base = [], len(m.group(1))
            while i < n:
                mm = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
                if mm and len(mm.group(1)) <= base:
                    items.append([mm.group(3)])
                    i += 1
                    continue
                if mm and len(mm.group(1)) > base and items:
                    # nested item: keep it as a nested list on the parent
                    sub, indent = [], len(mm.group(1))
                    sub_ordered = bool(re.match(r"^\d+\.$", mm.group(2)))
                    while i < n:
                        m3 = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
                        if m3 and len(m3.group(1)) >= indent:
                            sub.append(m3.group(3))
                            i += 1
                        else:
                            break
                    st = "ol" if sub_ordered else "ul"
                    items[-1].append(
                        "<%s>\n%s\n</%s>"
                        % (st, "\n".join("  <li>%s</li>" % inline(s) for s in sub), st)
                    )
                    continue
                if lines[i].strip() and not mm and items and lines[i].startswith((" ", "\t")):
                    items[-1][0] += " " + lines[i].strip()  # lazy continuation
                    i += 1
                    continue
                break
            parts = []
            for it in items:
                inner = inline(it[0])
                if len(it) > 1:
                    inner += "\n" + "\n".join(it[1:])
                parts.append("  <li>%s</li>" % inner)
            out.append("<%s>\n%s\n</%s>" % (tag, "\n".join(parts), tag))
            continue

        # raw html block
        if stripped.startswith("<") and not stripped.startswith("<http"):
            block = []
            while i < n and lines[i].strip():
                block.append(lines[i])
                i += 1
            out.append("\n".join(block))
            continue

        # paragraph
        para = []
        while i < n and lines[i].strip():
            if re.match(r"^\s*(#{1,6}\s|```|>|\||[-*+]\s|\d+\.\s)", lines[i]):
                break
            if re.match(r"^(-{3,}|\*{3,}|_{3,})$", lines[i].strip()):
                break
            para.append(lines[i].strip())
            i += 1
        if para:
            text = inline("\n".join(para))
            # standalone image -> its own paragraph, matching the existing feed
            out.append("<p>%s</p>" % text)

    return "\n".join(out)


def read_post(path):
    raw = path.read_text(encoding="utf-8")
    fm, body = {}, raw
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if m:
        for ln in m.group(1).split("\n"):
            if ":" in ln:
                k, v = ln.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
        body = m.group(2)
    else:
        # no front matter: first "# Title" line supplies the title
        m2 = re.match(r"^\s*#\s+(.*?)\s*$", body.split("\n")[0])
        if m2:
            fm["title"] = m2.group(1)
            body = "\n".join(body.split("\n")[1:])
    return fm, body


def permalink(path):
    coll = path.parts[-3]
    y, mo, d, slug = path.stem.split("-", 3)
    return "%s/%s/%s/%s/%s/%s.html" % (SITE, coll, y, mo, d, slug)


def rfc822(path, hour=12):
    """Post date at `hour` UTC. Same-day series posts need distinct hours:
    Substack's ordering is unreliable when timestamps tie."""
    y, mo, d, _ = path.stem.split("-", 3)
    dt = datetime(int(y), int(mo), int(d), hour, 0, 0, tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def build(docs, selections, out_path, channel_title, channel_desc):
    items = []
    for sel in selections:
        rel, subtitle = sel[0], sel[1]
        hour = sel[2] if len(sel) > 2 else 12
        path = docs / rel
        fm, body = read_post(path)
        title = fm.get("title") or path.stem
        content = convert(body)
        link = permalink(path)
        items.append(
            "\n".join(
                [
                    "  <item>",
                    "    <title>%s</title>" % esc(title),
                    "    <link>%s</link>" % link,
                    '    <guid isPermaLink="true">%s</guid>' % link,
                    "    <pubDate>%s</pubDate>" % rfc822(path, hour),
                    "    <description>%s</description>" % esc(subtitle),
                    "    <content:encoded><![CDATA[%s]]></content:encoded>" % content,
                    "  </item>",
                ]
            )
        )
    xml = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">',
            "<channel>",
            "  <title>%s</title>" % esc(channel_title),
            "  <link>%s</link>" % SITE,
            "  <description>%s</description>" % esc(channel_desc),
            "\n".join(items),
            "</channel>",
            "</rss>",
        ]
    )
    out_path.write_text(xml, encoding="utf-8")
    return len(items), out_path


# (rel_path_under_docs, substack_subtitle[, hour_utc])
# Curated 2026-10-31: the 6 older gap posts live as drafts in Substack and were
# deliberately left out as off-theme. These three are what should go up.
SELECTIONS = [
    (
        "ai/_posts/2026-10-31-ai-platform-hardening-part1-azure-ml-workspace.md",
        "The specific controls, why each one matters, and how to verify it. "
        "Part 1 of two.",
        12,
    ),
    (
        "ai/_posts/2026-10-31-ai-platform-hardening-part2-foundry-deployments.md",
        "Identity, model access control, runtime safety, and the governance that "
        "keeps them from drifting. Part 2 of two.",
        13,
    ),
    (
        "ai/_posts/2026-07-31-energy-comparison.md",
        "Five orders of magnitude separate the cheapest option from the most "
        "expensive one, for the same job on the same machine.",
    ),
]

if __name__ == "__main__":
    docs = Path(sys.argv[1]) if len(sys.argv) > 1 else DOCS
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else docs / "substack-gap-import.xml"
    count, p = build(
        docs,
        SELECTIONS,
        out,
        "hoopdad dunks - for Substack import",
        "Curated feed: blog posts selected for import into The Agent Operating Model.",
    )
    print("wrote %d items -> %s" % (count, p))
