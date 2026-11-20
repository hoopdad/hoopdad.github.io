---
name: substack-draft
description: Copy posts from the hoopdad.github.io blog into Substack (The Agent Operating Model) as drafts for review. Use when asked to sync the blog to Substack, find posts missing from Substack, or draft/copy a blog post into Substack. Handles gap detection against both published posts and existing drafts, then creates a draft per missing post with formatting, images and tables intact.
---

# Blog → Substack, as drafts

Copies posts from `hoopdad.github.io` into **The Agent Operating Model**
(`mikeolivieri.substack.com`) as drafts. Never publishes.

## Scope rule

**Create drafts only. Never publish, never send email.** Substack's *importer*
(Settings → Import/Export) publishes straight to Home and Archive — that is why
this skill does not use it. Verify after every run that the published count is
unchanged.

## What you need

A browser tab signed in to the Substack dashboard. The built-in browser pane
keeps its sign-in between sessions; check with
`fetch('/api/v1/post_management/counts?query=')`. If the pane is signed out,
ask the user to sign in there — never type credentials.

Claude in Chrome also works when connected, but it is per-device: it may be
running on a machine that is not this one, and `list_connected_browsers`
returning `[]` means that Chrome is unreachable, not that the task is blocked.

## Process

### 1. Find the gaps

```bash
# in the Substack dashboard tab, run scripts/substack_inventory.js,
# save its JSON, then:
python .claude/skills/substack-draft/scripts/gap.py docs inventory.json
```

`gap.py` matches on normalised titles, not URLs or dates. Both move: the blog
has been restructured before (`ai/` → `tokenomics/` and `data/`), which changed
every permalink while titles stayed put, and post dates have been edited after
publication. It also reports posts covered only by an unpublished draft, which
are queued rather than live.

Always diff against **published *and* drafts**. Re-drafting something already
sitting in drafts creates a duplicate.

### 2. Create the draft shell

Navigate to `https://mikeolivieri.substack.com/publish/post?type=newsletter`.
This creates an empty draft and redirects to `/publish/post/<id>` — note the id.

Set the title, **then screenshot, then** set the subtitle. The subtitle field
moves down the page as the title wraps to more lines, so a subtitle click based
on the pre-title layout lands back in the title and injects the subtitle
mid-word. Read the subtitle's position from a fresh screenshot every time.

Subtitle text: use the post's front-matter `description` when it has one — the
site theme renders it as the deck, so it is already written to be a standfirst.
Otherwise write one sentence that gives the post's finding, not its topic.

### 3. Paste the body

Click once in the editor body, then run `scripts/paste_post.js` with
`__POST_URL__` replaced by the post's URL.

It fetches the article, takes `.prose` (body only — no site header, "ON THIS
PAGE" box, related posts or footer, so there is nothing to clean up
afterwards), absolutises URLs, converts tables to lists, and dispatches a
`paste` event into the editor.

### 4. Verify

Run `scripts/verify_draft.js`. Require: `tablesLeft` 0, `brokenImages` 0,
`imageHosts` showing `substackcdn.com`, and headings/words matching the source.

Then confirm the **published count has not changed** and the draft count rose
by exactly the number of posts created.

## Things that do not work

Learned the hard way; do not retry them.

- **The clipboard is unavailable in the browser pane.** Synthetic Ctrl+C never
  writes, `document.execCommand('copy')` returns `false`, and
  `navigator.clipboard.write` fails with "Write permission denied" (and
  "Document is not focused" until the page is clicked). Tab-to-tab copy/paste
  does nothing. `paste_post.js` avoids the clipboard entirely.
- **Typing markdown does nothing.** Substack's markdown shortcuts fire on real
  keystrokes, so injected `## Heading` and `**bold**` stay literal. This holds
  whether the marker is typed with the text or on its own.
- **Substack has no tables.** The More menu offers Code block, Divider,
  Footnote, LaTeX, Poll — no table. A pasted `<table>` collapses into one
  run-on paragraph. Convert before pasting; `paste_post.js` does.
- **Screenshots of the editor go stale.** The body can hold thousands of
  characters while the pane still renders "Start writing...". Trust
  `verify_draft.js`, not the picture.
- **The management API 400s without `order_by`.** `?offset=0&limit=50` alone
  fails; it needs `order_by` and `order_direction`, and pages at 25 whatever
  limit is asked for.
- **`title` is null on drafts.** Their heading lives in `draft_title`.

## Known content quirks

- **HTML comments are authoring notes.** Posts carry `<!-- SCREENSHOT 3: ... -->`
  markers. They do not render, so `.prose` never contains them — but any
  markdown-level converter must strip them, and must not let them swallow the
  image that follows on the next line.
- **Long posts warn about email truncation.** Expected past roughly 3,000 words
  with images. Web readers are unaffected; mention it, do not act on it.
- **Do not silently fix typos.** Flag them and fix at the blog source, so the
  two copies do not diverge. `TEXT_FIXES` in `paste_post.js` exists for when
  the source fix is not yet live.
