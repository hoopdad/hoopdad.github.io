# Coding Assistants — Proposed Blog Series

A three-part Jekyll-ready series adapted from `../blog.txt`, expanding the author's
original "Part 1 of 3" notes into a complete, structured arc. The voice and phrasing
of the source notes are preserved; structure, section headers, transitions, and
cross-links were added to improve flow and fill the gaps the original notes pointed at.

## Intended Sequence

| # | Post | File | Publish date |
|---|------|------|--------------|
| 1 | **Decisions, Capabilities, and Expertise** — what AI coding assistants can actually do, and the human skills that make or break results | [`2026-06-10-coding-assistants-part-1-decisions-capabilities-expertise.md`](2026-06-10-coding-assistants-part-1-decisions-capabilities-expertise.md) | 2026-06-10 |
| 2 | **Orchestrating the Fleet** — the end-to-end pipeline and the four reusable multi-agent frameworks | [`2026-06-17-coding-assistants-part-2-orchestrating-the-fleet.md`](2026-06-17-coding-assistants-part-2-orchestrating-the-fleet.md) | 2026-06-17 |
| 3 | **Wrangling AI in Practice** — a field report: three apps shipped with zero hand-written code, and the lessons from the break-fix loops | [`2026-06-24-coding-assistants-part-3-wrangling-in-practice.md`](2026-06-24-coding-assistants-part-3-wrangling-in-practice.md) | 2026-06-24 |

The posts are designed to be read in order. Each ends with an "Up Next" link to the
following part (using Jekyll's `post_url` tag), and Part 3 links back to Part 1.

## How the Source Was Mapped

The original `blog.txt` was a single "Part 1 of 3" draft that promised follow-up posts
on "the patterns I worked out" and "wrangling an AI assistant in practice." That promise
defined the split:

- **Part 1** ← intro, *Teeing up with Individual Capabilities*, *Human Expertise*, *Where to Put Your Money*.
- **Part 2** ← *Putting Capabilities Together*, the keyword glossary (Red Team / TDD / Critic / IaC), and *Abstractions* (the four frameworks).
- **Part 3** ← *Examples of Things I Built*, the author's role, and the outcomes / lessons.

## Assets

Each post references at least one PNG (1200×630, open-graph friendly) stored in
[`assets/`](assets/) and linked with a relative path:

- `assets/part1-capabilities.png` — concept card of the four core capabilities
- `assets/part2-fleet-pipeline.png` — diagram of the multi-agent orchestration pipeline
- `assets/part3-lessons.png` — quote/lessons card

Graphics are generated reproducibly by [`assets/make_images.py`](assets/make_images.py)
(requires Python + Pillow). Re-run with:

```bash
cd assets && python3 make_images.py
```

## Front Matter Convention

Every post includes Jekyll front matter with `layout`, `title`, `date`, `categories`,
`tags`, `excerpt`, and a social `image`. Filenames follow Jekyll's
`YYYY-MM-DD-title.md` convention so they drop straight into a `_posts/` directory.

> **Note:** the `image:` front-matter paths use a site-absolute form
> (`/jekyll/assets/...`) as a placeholder; adjust to your site's baseurl when the
> posts move into a real Jekyll `_posts/` folder. The inline `![](assets/...)` image
> links are relative to this folder.
