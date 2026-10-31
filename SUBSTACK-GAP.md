# Blog → Substack: what to import

Updated 2026-10-31. Blog: `hoopdad.github.io`.
Substack: [The Agent Operating Model](https://mikeolivieri.substack.com/) (27 posts live).

**Theme being matched against** (from your About page): *"Running AI coding agents in
the enterprise: decisions, governance, and the engineering to back them up."* Audience:
engineering leaders, architects, builders. Every issue should give "a decision framework,
a template, or a working artifact."

---

## Where to import (corrected)

There is **no "Import from URL" in the Substack editor** — I had that wrong. The importer
lives in publication settings:

1. **Settings** → **Import/Export** in the left nav
2. **Import posts**
3. Paste the feed URL
4. Select **Import**
5. Confirm ownership and agree to the terms → **Next**

Two things from Substack's own docs that change the plan:

- **Imported posts publish.** Substack says "your posts will appear in your Home and
  Archive." They do not land as drafts. Only import what you want live.
- **There is an "Update existing posts" checkbox** on re-import. That removes the
  duplicate risk I warned about earlier — a second import updates rather than duplicates.

Substack's documented fallback, if an import misbehaves: paste the post into the editor
by hand, publish, then change the publication date in that post's settings to match the
original.

---

## What's queued for import

`docs/substack-gap-import.xml` now holds **3 posts** — not the original 7.

| # | Post | Date | Fit | Status |
|---|------|------|-----|--------|
| 1 | AI Platform Hardening - Part 1 - Azure ML Workspace | 2026-10-31 | **9/10** | Newly staged, needs your read |
| 2 | AI Platform Hardening - Part 2 - Foundry Deployments | 2026-10-31 | **9/10** | Newly staged, needs your read |
| 3 | Energy Comparison: CPU, GPU+ML, GPU+LLM | 2026-07-31 | **9/10** | **Already drafted in Substack** (post 222944429) |

The 6 older gap posts (Jenkins, Your Vision Matters, Private Network Access, both ASE
posts, Event Hubs Kafka) are **deliberately left out** — they exist as drafts in your
Substack dashboard and you judged them off-theme. Nothing further needed; leave them
unpublished or delete them there.

---

## Substack has no tables

Confirmed by inspecting the editor's **More** menu on 2026-10-31: it offers Code block,
Divider, Financial chart, Footnote, LaTeX, Poetry, Poll, Prediction market and Recipe —
**no table**. A pasted or imported `<table>` collapses into a single run-on paragraph with
every cell jammed together, like this:

```
ApproachThroughputPower (GPU + CPU)Energy/itemPer 1M itemsvs CPUCPU rules (VADER, 1 core)25,156 items/s0 + 9.5 W0.374 mJ0.104 Wh1×GPU+ML (DistilBERT…
```

This matters more than it sounds, because all three queued posts have tables, and in the
two hardening posts the table **is** the deliverable — 31 and 21 rows of control-level
reference.

**The feed therefore never emits a table.** `table_as_list()` in the generator turns each
row into a bullet, with the first column as the label. It picks a layout by cell length:

- **Short cells** (the energy results) get a lead-in naming the columns, then bare values:
  `**CPU rules (VADER, 1 core)** — 25,156 items/s · 0 + 9.5 W · 0.374 mJ · 0.104 Wh · 1×`
- **Long cells** (the hardening checklists, whose values are sentences) carry their own
  column name: `**Workspace managed identity** — Setting Applied: System-assigned or
  user-assigned, enabled at creation · Security Principle: No static credentials · …`

No data is dropped either way, and both read correctly on a phone and in email, which a
six-column table never would.

**The blog keeps its real tables.** This transform is feed-only; the Markdown sources are
untouched and Jekyll still renders proper `<table>` markup.

If you would rather have monospace columns than bullets, the editor's Code block preserves
alignment — but it scrolls sideways on a phone, which is where most of your readers are.

---

## The two hardening posts (revived)

These had been sitting in `docs/cloud/_drafts/` unpublished on both the blog and Substack.
They were the strongest unused material in the repo: control-level checklists written as
"a practical blueprint," which is exactly the About page's promise of something a reader
could take into Monday's meeting.

**What I changed, mechanically:**

- `git mv`'d both from `docs/cloud/_drafts/` to `docs/ai/_posts/`, dated `2026-10-31`.
  I put them in `ai/` rather than `cloud/` because the subject is securing AI platforms,
  which tracks the newsletter theme and sits beside your existing Foundry post. Easy to
  reverse — it only affects the URL path, and neither has a published URL yet.
- Added Jekyll front matter. Without it they render with no layout and a filename-derived
  title, so they would not have shown up correctly as posts.
- Stripped the `# Post 1:` / `# Post 2:` H1s, since the post layout renders `title` as the
  H1 and you would have had two.
- Retitled to match your series convention (`Safe AI - Part 1`, `Token Efficiency - Part 1 - …`):
  **AI Platform Hardening - Part 1 / Part 2**.
- Added a one-line series cross-link between them using `post_url`, matching how the ASE
  pair links to each other.
- Wrapped the 12 bare Microsoft Learn reference URLs in angle brackets so they render as
  links. As bare text kramdown leaves them unclickable, so this fixes the blog too.
- Gave Part 2 a 13:00 UTC timestamp against Part 1's 12:00. Your three Token Efficiency
  posts all share 2026-05-27 and Substack shows them out of order (2, 3, 1) — distinct
  timestamps stop that happening to this pair.

**Subtitles already in the feed:**

```
The specific controls, why each one matters, and how to verify it. Part 1 of two.
```

```
Identity, model access control, runtime safety, and the governance that keeps them from drifting. Part 2 of two.
```

### Two things to decide before you publish these

**1. The "we" voice.** Both posts say "the controls *we* implemented" and "*our* Foundry
deployments," where everything else you write is first-person "I." For a newsletter whose
pitch is "I write from what I've tried," the team voice reads differently — and it implies
an employer or engagement speaking. Your blog carries the "Opinions are my own" disclaimer,
but that disclaimer does less work when the text says "we." Worth a pass to decide whether
these are your posts or a team's.

**2. Content review.** I checked both for leakage and they are clean — no subscription IDs,
tenant IDs, GUIDs, resource names, or customer identifiers, and each table header already
states that identifiers are excluded. Every control maps to public Microsoft Learn
guidance. But I did not write these and you have not looked at them in months, so read them
before they go live. You know the engagement they came from; I don't.

**Also:** `docs/cloud/_drafts/azure-ml-foundry-security-checklist-blog.md` is just a stub
pointing at these two ("If you want, this index can also be used as the parent landing
page"). I left it in `_drafts`. Delete it, or make it a real series landing page.

---

## Energy Comparison — already drafted

The purest expression of your stated mission in the archive: a decision framework ("don't
reach for an LLM by default"), measured first-party data, working repo, cost governance
argued from evidence rather than opinion.

**This one is done.** Drafted into Substack on 2026-10-31 as post `222944429`, by copying
the rendered blog post and cleaning it up in the editor:

- Title and the subtitle below are set
- Blog chrome removed: site header, duplicate H1, date, the "Find this post on Substack"
  cross-promo, the feedback block, the site footer
- Headings, inline code (`pynvml`, `typeperf`), italics and the repo link all survived
- The results table was rebuilt by hand as a bulleted list, every figure checked against
  the source

Verified at the time: Drafts went 9 → 10 and Published stayed at 27, so nothing was
published or emailed.

**Subtitle used:**

```
Five orders of magnitude separate the cheapest option from the most expensive one, for the same job on the same machine.
```

**Alternate** if you want the leadership angle over the shock number:

```
I measured CPU, a small fine-tuned model, and an LLM on the same task. The default choice was the most expensive one available.
```

The feed still carries this post, so a re-import would overwrite the hand-cleaned draft
with the generated version. The generated one is fine, but the wording of the list lead-in
differs slightly — if you have edited the draft, tick "Update existing posts" only when you
mean to replace it.

---

## If you later change your mind on the 6

Suggested retitles and framing, kept for reference:

| Post | Suggested Substack title | Why it needs it |
|---|---|---|
| Jenkins DevOps data (8/10) | Getting Build Data to an Agent: The Jenkins Side | Agent payoff is buried under a plugin tutorial |
| Private Network Access (6/10) | Running Azure ML When Public Access Is Off | Current title reads as a networking footnote |
| Your Vision Matters (6/10) | The Agent Can Get You to B. You Still Have to Supply C. | Reads as a keynote recap; your own argument is buried mid-post |
| Event Hubs Kafka (5/10) | — | Needs a paragraph tying managed identity to *agent* identity |
| ASE ×2 (3/10) | — | Pre-agent; leave on the blog |

---

## Regenerating the feed

`substack-gap-feed.py` (repo root) builds the file. Edit the `SELECTIONS` list at the
bottom — `(path_under_docs, subtitle[, hour_utc])` — and run:

```bash
python substack-gap-feed.py docs docs/substack-gap-import.xml
```

It converts Markdown the way your original import did: kramdown-style heading ids,
language-tagged `<pre><code>`, absolute `hoopdad.github.io` URLs, `post_url` resolved to
permalinks, `---` to `<hr />`, `<url>` autolinks, `{:target="_blank"}` stripped, and tables
flattened to bulleted lists as described above. Keeping this in the repo is what stops the
gap reopening — the July drift happened because that feed was a one-off with no way to
regenerate it.

---

## Verification

Feed checked for: well-formed XML, zero `<table>` elements, zero relative `src`/`href`,
zero unresolved Liquid tags or `post_url` references, zero leftover attribute lists, no
stray `<p>---</p>`, no bare-URL list items, no stray `|` characters or empty bullets left
by the table transform, valid UTF-8 (`·`, `—`, `×` preserved — 120, 79 and 7 occurrences),
and no `]]>` sequences that would break CDATA. The three tables become 5, 31 and 21
bullets with no cell dropped.

**Not verified:** the blog has not been rebuilt, so the two new posts have not been
rendered by Jekyll. Ruby is installed at `C:\Ruby33-x64` but has no `bin` directory, so
`bundle` does not run and I could not build the site. Their front matter matches your other
posts exactly and both `post_url` targets resolve to real filenames, but that is inference,
not a green build — worth one `bundle exec jekyll build` once Ruby works.

Also not verified: how Substack's importer renders this feed. The energy post was drafted
through the editor, not imported, so the import path itself is still untested end to end.

**Not verified:** the blog has not been rebuilt, so the two new posts have not been
rendered by Jekyll. Ruby is installed at `C:\Ruby33-x64` but has no `bin` directory, so
`bundle` does not run and I could not build the site. Their front matter matches your other
posts exactly, but the `post_url` cross-links are the kind of thing that fails the build if
a path is wrong — worth one `bundle exec jekyll build` once Ruby works.
