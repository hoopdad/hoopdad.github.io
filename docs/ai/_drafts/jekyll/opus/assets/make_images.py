#!/usr/bin/env python3
"""Generate clean, professional PNG graphics for the Coding Assistants blog series.

Run:  python3 make_images.py
Output: PNG files in the same directory (assets/).
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Palette (calm, professional engineering-blog look) -------------------
BG = (15, 23, 42)          # slate-900
PANEL = (30, 41, 59)       # slate-800
ACCENT = (56, 189, 248)    # sky-400
ACCENT2 = (167, 139, 250)  # violet-400
ACCENT3 = (52, 211, 153)   # emerald-400
TEXT = (226, 232, 240)     # slate-200
MUTED = (148, 163, 184)    # slate-400
LINE = (71, 85, 105)       # slate-600

W, H = 1200, 630  # standard social/open-graph size


# ---- Font loading ---------------------------------------------------------
def _find_font(candidates):
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


BOLD_PATH = _find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
])
REG_PATH = _find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
])
MONO_PATH = _find_font([
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
])


def font(bold=False, size=40, mono=False):
    path = MONO_PATH if mono else (BOLD_PATH if bold else REG_PATH)
    if path:
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def new_canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # subtle top accent bar
    d.rectangle([0, 0, W, 10], fill=ACCENT)
    return img, d


def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def wrap(d, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(d, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rounded(d, box, radius, **kw):
    d.rounded_rectangle(box, radius=radius, **kw)


def kicker(d, label, color=ACCENT):
    f = font(bold=True, size=24)
    d.text((70, 48), label.upper(), font=f, fill=color)


def footer(d, text="bloggr.dev  ·  Coding Assistants series"):
    f = font(size=22)
    d.text((70, H - 56), text, font=f, fill=MUTED)


# ---------------------------------------------------------------------------
# Post 1 — Concept card: Capabilities of an AI coding assistant
# ---------------------------------------------------------------------------
def post1():
    img, d = new_canvas()
    kicker(d, "Part 1  ·  Capabilities & Expertise")

    title = "What an AI Coding Assistant Can Actually Do"
    tf = font(bold=True, size=52)
    y = 96
    for line in wrap(d, title, tf, W - 140):
        d.text((70, y), line, font=tf, fill=TEXT)
        y += 62

    caps = [
        ("Write code", "Any formatted file is fair game"),
        ("Run tools", "Clouds, DBs, trackers, test suites"),
        ("Design flows", "End-to-end system architecture"),
        ("Follow instructions", "Steered by instruction files"),
    ]
    colors = [ACCENT, ACCENT3, ACCENT2, ACCENT]
    cw, ch, gap = 510, 110, 30
    x0, y0 = 70, y + 18
    for i, (head, sub) in enumerate(caps):
        col, row = i % 2, i // 2
        bx = x0 + col * (cw + gap)
        by = y0 + row * (ch + gap)
        rounded(d, [bx, by, bx + cw, by + ch], 16, fill=PANEL)
        d.rectangle([bx, by + 18, bx + 8, by + ch - 18], fill=colors[i])
        d.text((bx + 30, by + 22), head, font=font(bold=True, size=32), fill=TEXT)
        d.text((bx + 30, by + 64), sub, font=font(size=24), fill=MUTED)

    footer(d)
    img.save(os.path.join(HERE, "part1-capabilities.png"))


# ---------------------------------------------------------------------------
# Post 2 — Diagram: the multi-agent orchestration pipeline
# ---------------------------------------------------------------------------
def post2():
    img, d = new_canvas()
    kicker(d, "Part 2  ·  Patterns for the Fleet", ACCENT2)

    title = "Orchestrating a Fleet of Specialist Agents"
    tf = font(bold=True, size=50)
    y = 96
    for line in wrap(d, title, tf, W - 140):
        d.text((70, y), line, font=tf, fill=TEXT)
        y += 58

    stages = [
        ("Coordinator", "Designs & delegates", ACCENT),
        ("Red Team", "Hardens security", ACCENT2),
        ("Builder", "TDD, writes code", ACCENT3),
        ("Critic", "Validates output", ACCENT),
        ("Deploy", "IaC to cloud", ACCENT2),
    ]
    n = len(stages)
    bw, bh = 196, 120
    gap = (W - 140 - bw * n) // (n - 1)
    by = y + 70
    cx = []
    for i, (head, sub, col) in enumerate(stages):
        bx = 70 + i * (bw + gap)
        cx.append((bx, bx + bw))
        rounded(d, [bx, by, bx + bw, by + bh], 14, fill=PANEL, outline=col, width=2)
        ht = font(bold=True, size=26)
        d.text((bx + (bw - text_w(d, head, ht)) // 2, by + 24), head, font=ht, fill=col)
        st = font(size=19)
        for j, sl in enumerate(wrap(d, sub, st, bw - 24)):
            d.text((bx + (bw - text_w(d, sl, st)) // 2, by + 60 + j * 24), sl, font=st, fill=MUTED)
    # arrows
    ay = by + bh // 2
    for i in range(n - 1):
        x1 = cx[i][1] + 6
        x2 = cx[i + 1][0] - 6
        d.line([x1, ay, x2, ay], fill=LINE, width=3)
        d.polygon([(x2, ay), (x2 - 10, ay - 6), (x2 - 10, ay + 6)], fill=LINE)

    # feedback loop label
    fb = "Logs feed back  →  assess  →  iterate"
    ff = font(size=24, mono=True)
    d.text(((W - text_w(d, fb, ff)) // 2, by + bh + 46), fb, font=ff, fill=ACCENT3)

    footer(d)
    img.save(os.path.join(HERE, "part2-fleet-pipeline.png"))


# ---------------------------------------------------------------------------
# Post 3 — Quote / lessons card: wrangling AI in practice
# ---------------------------------------------------------------------------
def post3():
    img, d = new_canvas()
    kicker(d, "Part 3  ·  Wrangling in Practice", ACCENT3)

    quote = "\u201CI didn\u2019t write a line of code. The test was whether I could manage the work \u2014 and the answer was yes.\u201D"
    qf = font(bold=True, size=46)
    y = 120
    for line in wrap(d, quote, qf, W - 160):
        d.text((70, y), line, font=qf, fill=TEXT)
        y += 60

    d.text((70, y + 10), "Three apps shipped, zero lines hand-written:", font=font(size=26), fill=ACCENT3)
    apps = [
        "Natural language \u2192 math formulas, tuned for efficiency",
        "Resume rewriter aligned to a target employer\u2019s language",
        "TV-show memory assistant with Alexa + iOS integration",
    ]
    yy = y + 56
    for a in apps:
        d.ellipse([72, yy + 9, 86, yy + 23], fill=ACCENT2)
        for j, sl in enumerate(wrap(d, a, font(size=26), W - 200)):
            d.text((104, yy + j * 32), sl, font=font(size=26), fill=MUTED)
        yy += 32 * (len(wrap(d, a, font(size=26), W - 200))) + 16

    footer(d)
    img.save(os.path.join(HERE, "part3-lessons.png"))


if __name__ == "__main__":
    post1()
    post2()
    post3()
    print("Generated:")
    for f in sorted(os.listdir(HERE)):
        if f.endswith(".png"):
            print(" -", f)
