# Desktop scheduling contract

## What this change does

This repository contains the method, topic queue and execution prompt. It does
not install, enable or run a schedule. The author will configure a desktop
agent to invoke the prompt every three days.

One job is sufficient: evidence preparation, writing and visual production
are stages of the same bounded topic task. No cloud Automation, automation
group, GitHub Actions schedule or additional paid service is provisioned.

## Desktop setup

| Setting | Intended value |
|---|---|
| Working directory | Dedicated checkout of `hoopdad/hoopdad.github.io` |
| Task | Read and execute `.github/prompts/think-fast-post.prompt.md` |
| Cadence | Every three days; one topic attempted per invocation |
| Anchor | Author chooses the first run's date, time and time zone in the desktop scheduler |
| Overlap | One active invocation; do not launch a catch-up run while it is active |
| Output | A new or resumed topic draft PR, never publication |
| Runtime/model | Author's chosen desktop agent; no model is prescribed here |

Use the scheduler's native three-day interval if available. A day-of-month
cron such as `0 9 */3 * *` resets at month boundaries and is not an exact
three-day interval. Decide whether the desktop product means 72 elapsed hours
or every third local calendar day, especially across daylight-saving changes.
Do not invent a cron expression if the product cannot express the chosen
interval. Record the actual configured anchor and interval in the desktop
task, not as guessed dates in the topic queue.

If a scheduled time is missed while the machine is asleep or offline, use
at most one catch-up invocation, then resume the configured cadence. Do not
backfill multiple articles. These are required operating policies; verify
that the chosen desktop product supports them rather than assuming it does.

## Paste into the scheduled desktop task

Set the task's working directory to the dedicated blog checkout, then use:

```text
In this checkout of hoopdad/hoopdad.github.io, read and execute
.github/prompts/think-fast-post.prompt.md.

Use editorial/think-fast/method.md and editorial/think-fast/queue.yml as
the durable method and topic scope. Resume or produce exactly one topic,
save its evidence, page and visuals, and create/update its draft PR.
Do not publish, merge, start paid model runs or change infrastructure.
If blocked or no work is eligible, report that honestly and stop.
```

Keep the wrapper short. Update the reviewed repository prompt/method rather
than maintaining a second, diverging copy in the desktop scheduler.

## Required capabilities and access

- Read the designated blog checkout and its remote branches/PRs, create a
  branch, commit/push scoped changes and create/update a draft PR. The agent
  must be able to inspect complete PR history for work identity.
- Read the repository prompt from a trusted checkout. Start with the merged
  method PR, not files fetched from an arbitrary contributor's branch. Before
  each invocation reconcile the designated checkout with the default branch
  without discarding in-progress topic work; inspect existing topic branches
  before updating them. Do not blindly pull into a dirty worktree.
- Run the existing Ruby/Bundler and Node/Playwright tooling, and operate a
  local browser for desktop/mobile draft previews.
- If implementation detail needs it, read an author-designated
  `hoopdad/think-fast-tests` checkout or explicitly authorized remote source.
  A `think-fast-web` checkout is optional for its retained-capture recipe.
  Keep machine paths and authentication in desktop configuration, not Git.
- For actual application captures, use an author-supplied, already-running
  local application/backend and an authorized existing retained run bound
  to the topic. No cloud endpoints, secrets, tunnel setup or accepted-record
  fabrication are supplied or authorized by this repository.

Check these capabilities during the first authorized invocation. If browser,
source or runtime access is missing, produce a precise blocker and retain
safe partial work; do not enable broad permissions as a workaround.

The desktop environment may be shared. Use only its designated checkouts and
owned temporary directories/processes. Do not scan unrelated home directories,
reuse unknown listeners, terminate processes by name or alter global settings.

## Progress, recovery and author review

The queue order is not a promise of publication dates. Every invocation
attempts one eligible topic; evidence or access blockers may prevent a complete
draft. An open review-ready PR does not block the next topic. There are only
seven enabled topics; once all are delivered, held or blocked, the job is idle.
Pause the desktop schedule when the queue is exhausted or review load is too
high. It never invents additional topics to keep itself busy.

The PR's identity/state markers and the branch's evidence brief are the
checkpoint. The scheduler need not remember the previous conversation.
Topic queue changes, retry-attempt increments and visual waivers require
explicit author approval; the agent must not grant them to itself.

After an interruption, inspect the exact remote branch/PR before resuming.
An uncertain push or PR response is not permission to create another branch
or duplicate PR. Preserve local-only work until it can be safely reconciled.
If remote state cannot be established, stop with the known references.

Merging a topic draft PR preserves its `_drafts` article and supporting files
but does not publish the article. All committed files are public regardless
of whether Jekyll publishes them. Publication requires a separate author-approved
change; the scheduler may not move the page into `_posts` or merge that change.

Optional feedback is described in the method. Begin with author corrections;
no separate assessor, self-improving job or additional schedule is enabled.
