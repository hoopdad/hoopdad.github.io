---
layout: post
date: 2026-11-17
title: "A Cheaper Router Was Only the Beginning: What Five Rounds of Agent Testing Changed"
topic: tokenomics
description: "Decision-1 made routing cheaper. Policy-servicing tests showed why useful agent outcomes also depend on explicit tasks, evidence handoffs and evaluators worth inspecting."
---

I started with a fairly simple question: why pay a high-quality generative model to decide which agent runs next? If the choices are already defined, a decision model seems like a better fit.

The first results were encouraging. Across 19 matched policy-servicing prompt pairs, Microsoft Decision-1 reduced estimated workflow inference cost by **14.01%**. But elapsed time increased slightly, and a refund example used for screenshots was both costlier and slower with Decision-1.

Then there was the evaluation problem. In an early follow-up, GPT accepted 23 of 24 completed answers. Decision-1 accepted none of them. They had received the same task, evidence and candidate answer.

That deserved more attention than a savings headline.

This is the third article in my decision-model series. The [first explored claims evidence and coverage](/tokenomics/2026/11/03/maximize-ai-insurance-workflow1.html); the [second examined underwriting intake and evidence handoffs](/tokenomics/2026/11/16/think-fast-insurance-underwriting-intake.html). Here, five rounds of policy-servicing follow-up work took the investigation beyond routing economics: defining the work, testing the whole workflow, and learning from evaluators without treating them as authorities.

By the final round, the refined Decision-1 workflows were **18.32% cheaper and 9.59% faster than the corresponding GPT-routed workflows**. That is a completed-workflow observation on one refund task, not proof that the tuning caused those savings. Understanding that distinction turned out to be as useful as the result.

## What the service representative actually needs

Policy servicing includes endorsements, refunds, renewals, billing questions and document requests. These sound routine until a request, a quote and a completed transaction get treated as the same thing.

Take the synthetic refund case used throughout the follow-up work. The supplied quote illustrates **40 units**. Cancellation has not been approved or posted, and the complete supplied ledger contains no refund payment. The requested output is an explanation and draft correspondence for human review.

The useful answer separates four states: quoted, approved, posted and paid. It explains what the supplied evidence establishes and what would have to happen before calling the refund completed. It does not pay anything.

There is an important scope distinction here. Explaining this supplied snapshot does not necessarily require investigating the policy's live status today. An actual request to verify today's position would. Asking for an operational date simply because a generic checklist mentions dates can make an otherwise answerable task look blocked.

That distinction became one of the main things the tests exposed.

![An existing Think Fast refund comparison shows advisory draft correspondence and a final review that distinguish a 40-unit quote from approval, posting and payment.](/assets/2026/tokenomics/policy-servicing-04-review-packet.jpeg)

*The original November 13 application capture, run `78df101a594a41ff8b3a336103301389`. Notice the separate refund states and the human-review boundary. Also notice the date-related caveats: later experiments examined when those caveats were relevant. This is not a screenshot of the refined agents.*

## Give the models different jobs

Think Fast runs the same request through two Microsoft Agent Framework workflows. GPT-5.6 Sol does the specialist work in both. The comparison changes the routing model: GPT selects the next action in one lane; Decision-1 scores a fixed set of choices in the other.

The servicing workflow has five available specialists:

| Specialist | Responsibility |
|---|---|
| Intake | Separate the requested service from recorded facts and identify required work. |
| Policy terms | Interpret supplied terms, dates and approval conditions when needed. |
| Billing reconciliation | Reconcile ledger evidence without inventing fees or executing payments. |
| Correspondence | Prepare an unsent draft from the required current specialist results. |
| Review | Assemble the evidence-linked packet and unresolved items for a person. |

The simple refund case uses intake, billing, correspondence and review. Other servicing requests need policy-terms work too. The router sees the five worker IDs plus `complete` and `error`; application code enforces prerequisites, freshness and visit budgets.

This is a sensible division of responsibility. Generation helps interpret evidence and explain it. A decision model can choose among bounded actions. Code performs defined calculations and checks whether a proposed transition is legal. A person retains authority over consequential servicing actions.

It is not proof that five specialists are better than one agent. That would need a separate comparison.

### A completed graph is not a correct answer

Here is a small part of the [existing downloadable guard implementation](/assets/2026/tokenomics/think-fast-policy-servicing/src/think_fast_tests/workflows/guards.py). This is a verbatim excerpt of `State.complete_ready`, not a standalone program:

```python
    def complete_ready(self):
        return set(self.definition.required) <= self.current.keys() and all(
            self.current[r].accepted and self.current[r].dependencies == tuple(
                self.current[d].visit_id for d in self.definition.dependencies(r)
            ) for r in self.definition.required
        )
```

`definition.required` identifies the selected task's workers. Each current result records which dependency visits it used. The check requires accepted results from every required worker, using the current upstream visits rather than superseded ones.

If billing changes, an old draft cannot quietly remain current. That is useful protection. But this check cannot establish that the draft gives a clear, accurate explanation. Structural completion and answer quality need different checks.

The [source snapshot manifest](/assets/2026/tokenomics/think-fast-policy-servicing/bundle-manifest.json) records revision `a26fd2a6` and the snapshot's limits. It includes later observation hooks and is not the exact installed source for every October run or the later experimental clones.

## The original cost result still matters

The October servicing benchmark contains 25 prompt pairs: five request types at five complexity levels. Nineteen pairs have matched recorded settings and native completion, rather than completion established by later revalidation. Those are the primary historical comparison; matching execution settings does not establish equivalent answer quality.

| October matched cohort, 19 pairs | GPT routing | Decision-1 routing |
|---|---:|---:|
| Total workflow inference estimate | $9.19 | $7.91 |
| Mean inference estimate per workflow | $0.48 | $0.42 |
| Mean workflow elapsed time | 122.94 s | 124.51 s |

Using unrounded totals, Decision-1 reduced inference cost by **14.01%** while elapsed time increased **1.28%**. Including all 25 pairs, six of which mix recorded versions, gives 17.33% lower cost and 2.64% less elapsed time. That broader result is a sensitivity check, not a reason to discard the matched cohort.

![The original 19-pair benchmark separates routing and worker inference estimates: total cost falls from $9.19 to $7.91, while mean workflow elapsed time increases from 122.94 to 124.51 seconds.](/assets/2026/tokenomics/policy-servicing-05-cost-breakdown.svg)

*Saved October evidence, not an application screenshot. Routing inference cost fell 98.64%, but worker inference cost increased by $0.46 across the matched runs. Components are rounded independently. Hosting and evaluation are excluded.*

Routing calls saved 123.60 seconds of summed physical call time, yet total workflow elapsed time increased by 29.84 seconds. Those are different timing measures, but the contrast tells us where to look: a faster component did not produce a faster overall workflow.

The screenshot example went further in the unfavorable direction:

![The original Think Fast comparison reports estimated inference cost of about $0.38 and 105.13 seconds for GPT routing, versus $0.41 and 122.92 seconds for Decision-1 routing.](/assets/2026/tokenomics/policy-servicing-01-comparison.jpeg)

*The same November illustrative refund run, separate from the October cohort. The Decision-1 lane made an extra correspondence-repair visit. The UI shows its original unrounded estimates and operator-supplied prices; processed tokens are reported, but Decision-1's full cache split is unavailable.*

It would be easy to blame the extra repair. But the saved October version of this refund prompt also favored GPT on total cost and time, with the same four accepted worker visits and no repairs in either lane. Worker generation, tool rounds, caching and platform timing all deserved inspection. A plausible explanation is something to test, not something to put in the results column.

These are inference estimates under the study's recorded prices, not an Azure bill or total operating cost. They include internal model calls and repairs within the selected workflows, but exclude hosting, networking, storage, human work and separate evaluation spending.

## Five rounds, and a changing understanding of the problem

The follow-up work narrowed the investigation to `l1-refund`, rather than repeating the whole 25-prompt benchmark. It compared guidance based on best practices for agent coding, Systems Thinking, and both together, using both routers.

The best-practice guidance emphasized people defining concepts, explicit acceptance criteria, current evidence and token-resource management. Systems Thinking emphasized the whole deliverable, dependency-aware progress and bounded corrective feedback. These were specific instruction bundles, not tests of whether one engineering philosophy is universally better.

Here is the progression:

| Follow-up round | What changed or was investigated | What it revealed |
|---|---|---|
| 1. Routing guidance | Three guidance designs, both routers, five attempts per condition: 30 allocated workflows. | 24 completed; 23 split the judges and one was rejected by both. Six routing calls failed with native 401 errors. |
| 2. Final-review guidance | Fresh original/refined controls, with guidance handed to the review agent through a common engine. | All 60 completed. GPT accepted 55; Decision-1 accepted seven. There were 48 disagreements. |
| 3. Upstream guidance | A new common all-role handoff, comparing original and third-set instructions. | 58 of 60 business outputs completed. Of 57 fully judged outputs, 54 split the judges. Some unnecessary limitations decreased, but disagreement persisted. |
| 4. Explicit evaluation | Keep the third-round business instruction conditions; introduce six named evaluation checks and a separate overall judgment. | All 60 completed and were fully judged. Nine disagreements remained; instruction groups differed under the same new evaluator. |
| 5. Explicit role contracts | Keep the evaluator fixed; change the workers' rules for task scope, supplied references and evidence freshness. | Both judges accepted all 57 fully judged outputs, including every available control. Clearer contracts did not demonstrate an additional acceptance gain on this task. |

Each later controlled round allocated five attempts per condition, with smoke runs kept outside measurement. Original answers, votes and unknowns were retained. A diagnostic-only refinement version also encountered lifecycle problems before business measurement; it is not an extra completed 60-run cohort.

These rounds changed different layers. They are a learning sequence, not five comparable points on an improvement curve.

![A four-step whiteboard loop connects defining the task, running a frozen cohort, evaluating the answer, and inspecting evidence before revising the responsible layer. Original answers and judgments are preserved.](/assets/2026/tokenomics/think-fast-policy-servicing/policy-servicing-learning-loop.svg)

*The engineering process around the experiment, not a trace of an agent run. Each revision needs a new, identified comparison; changing the question does not change the answer already recorded.*

### First, check whether the router has a decision to improve

In the first follow-up's 126 recorded routing requests, the legal choices contained exactly **one non-error action**. Every completed run followed intake, billing, correspondence, review and completion.

That is a fairly important limit on an experiment about better routing instructions. There was no alternative productive branch for the guidance to select.

Decision-1 still performed the bounded selection cheaply. But adding more sophisticated routing advice could not demonstrate better branch selection in this case. If the production process is equally constrained, ordinary deterministic orchestration deserves a baseline too. The experiment did not run that comparison.

### Then, follow a bad assumption through the handoffs

The second-round diagnosis found date/currentness caveats originating upstream. Intake introduced a missing-date limitation; billing added another; correspondence and review carried them forward.

The result contract required inherited unresolved limitations to remain verbatim. Telling the final reviewer to be concise could not safely remove them. That would hide evidence rather than fix the assumption that created it.

The third instruction set therefore addressed scope earlier: distinguish an explanation of the supplied synthetic snapshot from a request to verify a live system. Mark a requirement not applicable only when it really does not apply. Preserve genuine missing facts, conflicting evidence and approval boundaries.

The mechanism changed. Across 29 saved measured answers in each instruction group, formal limitation sections contained 118 lines for controls and 51 for the third set. That is a descriptive count, not a clarity score. Some controls were already concise, and some refined answers still contained unnecessary caveats.

More importantly, the judges still disagreed on 54 of 57 fully judged outputs. Better-looking prose had not resolved the measurement problem.

## The evaluator needs a defined job too

It is tempting to treat evaluation as the easy part. Give another model the answer and ask whether it passes.

But "acceptable" can conceal several questions. Did the answer fulfill the selected task? Were its facts right? Did it invent a prerequisite? Was it cautious about an actual uncertainty, or did it refuse to answer a question the evidence already settled?

The fourth round made those questions explicit:

| Check | What the evaluator must assess |
|---|---|
| Task fulfillment | The exact requested deliverables, without adding unrequested work. |
| Quality | Material facts, arithmetic and applicable rules against supplied evidence. |
| Clarity | A clear answer, basis and relevant limitations, without material contradiction. |
| Scenario fidelity | The selected variant and explicit premises, including evidence declared complete or current. |
| No invented prerequisites | No irrelevant investigation or currentness requirement blocking the bounded answer. |
| Grounding and authority | Supported claims, no fabricated execution, and preserved human approval boundaries. |

Both evaluators received the same blinded task, criteria, evidence and candidate output. Each check used positive Yes/No wording. Application code computed cumulative Pass only when all six were Yes; missing or invalid judgments remained unknown.

A separate seventh question asked for an overall Pass/Fail judgment of the original packet. It did not receive the six sibling answers. Both providers answered the questions in one native request per evaluator, not six separate calls.

This is **explicit acceptance criteria**, one of the best practices for agent coding, applied to the evaluator itself. It also makes the limits of an evaluator visible.

Decision-1's overall judgment passed all 60 answers, while its six-check cumulative result failed eight. GPT's overall and cumulative judgments matched on all 60. That does not reveal either model's reasoning, but it does show that asking one broad question and applying a conjunction of specific checks can produce different decisions.

The changed evaluator was not independently calibrated against human correctness labels. Its greater specificity made the judgments more inspectable; the experiment did not establish that it was more accurate.

### What the fresh controls showed

Within round four, both instruction groups used that same new evaluator. Original instructions produced 19 shared acceptances, four shared rejections and seven disagreements from 30 outputs. Third-set instructions produced 28 shared acceptances and two disagreements from 30.

That is a useful within-round observation. The fall in disagreement from earlier rounds is a different matter: the evaluator changed, and the business answers were fresh. We cannot assign that difference entirely to better agent answers or entirely to better judging.

![Round four makes evaluation criteria explicit: 19 versus 28 shared acceptances from 30 allocated workflows per instruction group. Round five changes worker scope and reference contracts while keeping the evaluator fixed: controls and refined roles have 28 and 29 shared acceptances, with two and one unknown judgment pairs respectively. Every available control also passes.](/assets/2026/tokenomics/think-fast-policy-servicing/policy-servicing-evaluator-checks.svg)

*Round four clarifies what the judges must check; round five puts the task boundaries into the workers' own instructions. Those are different interventions. Fresh controls prevent us from crediting the last change for a result the controls also achieved. Green means both models accepted, not independently established correctness; unknown judgment pairs remain visible.*

Round five addressed the agents' definition of the job, not just the wording of their answers. A more specific evaluator cannot repair a worker instruction that sends the workflow looking for evidence the task does not require.

The cloned intake, billing, correspondence and review roles therefore received explicit scope and reference rules. Use the references actually supplied, rather than inventing aliases from another servicing variant. Distinguish evidence with unknown freshness from evidence known to be stale. Require a date when the requested determination depends on it, not simply because a general checklist mentions dates. The policy-terms role was unchanged.

**The worker and evaluator need the same definition of the task.** Otherwise one agent can manufacture an unnecessary prerequisite, the handoff contract can faithfully preserve it, and another model can penalize the answer for carrying it. That is a workflow-design problem, not something a cheaper router will solve.

But making the contracts clearer did **not** demonstrate an additional acceptance gain here. Both judges accepted all 28 fully judged control outputs and all 29 fully judged refined outputs. The unchanged evaluator and fresh controls kept that result honest.

The fixed allocation was still 60. There were 59 collected outcomes, 58 complete business outputs and 57 complete judgment pairs. One Hosted result was unavailable, another workflow retained a worker error with unknown outcome, and one completed answer lacked a known Decision-1 judgment. Missing observations are neither rejections nor successes.

One separately authorized follow-up under the missing Hosted result's condition completed and passed both judges. **We ran one new follow-up; we did not replace the missing observation.** It stays outside the primary table, and the original outcome and its cost remain unknown.

There is no reason to rescue a positive treatment claim here. The fresh controls are part of the finding.

## Was Decision-1 faster and cheaper by the end?

**Yes, in the final refined cohort.** Across its 15 completed workflows per router, Decision-1 averaged **$0.28 and 78.22 seconds**, versus **$0.34 and 86.52 seconds** for GPT routing. Using unrounded means, that is **18.32% lower workflow inference cost and 9.59% less elapsed time**.

Here is the first-to-last accounting. "Round 1" means the first follow-up on this refund task, not the broader October benchmark. These are whole business workflows, including their internal model calls and repairs, not router-only prices or summed call durations.

| Round 1 | GPT | Decision-1 |
|---|---:|---:|
| Complete / allocated | 12 / 15 | 12 / 15 |
| Mean inference | $0.35 | $0.28 |
| Mean elapsed | 86.09 s | 77.26 s |

| Round 5: fresh control | GPT | Decision-1 |
|---|---:|---:|
| Complete / allocated | 14 / 15 | 14 / 15 |
| Mean inference | $0.36 | $0.32 |
| Mean elapsed | 96.72 s | 95.89 s |

| Round 5: refined roles | GPT | Decision-1 |
|---|---:|---:|
| Complete / allocated | 15 / 15 | 15 / 15 |
| Mean inference | $0.34 | $0.28 |
| Mean elapsed | 86.52 s | 78.22 s |

*Means are weighted by completed business workflows across the three guidance designs, using the same fixed study price assumptions in both rounds. Separate evaluation, smoke and supplemental spending is excluded. Failed or unavailable business outcomes are excluded from these conditional means, not counted as free or fast completions. Full first-round and final-control spending remains unknown.*

Decision-1 was already cheaper and faster among round one's completions: **19.76% lower cost and 10.26% less elapsed time** than GPT routing. Its final refined mean was actually a little costlier and slower than its first-round mean. The tuning did not demonstrate that it widened Decision-1's economic advantage.

That before-and-after comparison also has limits. Round one's completed guidance groups were uneven after six native failures; the final refined groups completed all five attempts per condition. Worker instructions, engines and evaluation changed between rounds. This is not a controlled estimate of the tuning's effect, and round one had no answers accepted by both judges.

The final refined cohort's business costs and timings are complete, even though one of its Decision-1 evaluations remains unknown. Of its 30 completed business outputs, 29 had complete judge pairs and all 29 passed both judges. That supports the narrower end-state observation: **Decision-1 finished cheaper and faster on this task under the refined instructions, alongside strong observed model acceptance.** It does not turn model acceptance into a human correctness finding or establish quality-preserved savings in production.

## What this changes about building the solution

The decision-model result remains useful: routing was much cheaper under the recorded rates, and the final refined Decision-1 workflows also finished cheaper and faster overall. The follow-up work explains why economics is only one part of qualifying an agent workflow.

**Define the requested determination.** A quote is not a paid refund. An explanation of complete supplied evidence is not a live-system verification. Both the worker and its evaluator need those distinctions.

**Fix assumptions where they enter.** If intake creates an irrelevant limitation and the contract correctly preserves it downstream, polishing final review is the wrong intervention. Trace the dependency and correct the upstream instruction without deleting genuine uncertainty.

**Measure the whole deliverable.** Router savings, worker output, tool rounds, repairs and waiting affect different parts of cost and time. A local improvement can be outweighed elsewhere.

**Keep the experiment capable of saying no.** Freeze each cohort, retain unfavorable outcomes and compare against fresh controls. Better instructions might help both routers, neither router, or only a particular task. Unanimous model acceptance can also expose a ceiling in the test rather than prove the solution finished.

These follow-ups used one synthetic refund task, with five allocated attempts per condition. They do not establish reliability across endorsements, renewals or production servicing. Model agreement is not a human audit, and the changed evaluator prevents a single quality-preserved savings claim across all rounds.

For a service-team pilot, I would next measure whether a person can use the packet correctly, how much rework it creates, and whether it reduces handling time or repeat contacts. Those would connect the technical result to business value. This experiment did not measure them.

I would still test a decision model for a bounded routing job. I would also spend at least as much care defining what a useful answer means, and checking whether the test is measuring it.

## Evidence and implementation

The historical [paired CSV](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/workflow-pairs.csv), [per-run CSV](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/workflows.csv) and [dashboard](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/index.html) contain the October measurements. Filter on `insurance-policy-servicing`. The [existing source and synthetic-fixture manifest](/assets/2026/tokenomics/think-fast-policy-servicing/bundle-manifest.json) describes the downloadable implementation snapshot.

The follow-up protocols and closeouts are in the access-restricted [study repository](https://github.com/hoopdad/think-fast-tests/tree/41ca588e674993810c0a1782de555014b2b98c75): `docs/deployment/OrchestratorStudyHosted-20261116.md`, `OrchestratorRefinement-20261116.md` and `OrchestratorScopeReference-20261117.md`. They retain the version boundaries, fixed allocations, separate smoke and evaluation spending, and unresolved costs. They are not a public download of private runtime records.
