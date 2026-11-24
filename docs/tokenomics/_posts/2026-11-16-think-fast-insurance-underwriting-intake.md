---
layout: post
title: "A Complete Submission Is Not an Underwriting Decision"
topic: tokenomics
description: "How an evidence-linked underwriting referral keeps missing documents, conflicting activities and stale rules visible, with measured routing trade-offs."
---

A commercial submission can contain every field on the form and still leave an underwriter with the important question unanswered. Does the supporting evidence establish what the submission says? And which rule applies if the documents disagree?

That is useful work for an agent workflow. Gather the supplied facts, connect them to the relevant manual excerpt, identify the missing or conflicting evidence, and prepare a referral someone can review. The useful deliverable is a better starting point for the underwriter, not an automated decision to accept the risk.

Think Fast compares two ways of routing that work. One uses GPT-5.6 Sol to select the next specialist; the other uses Microsoft Decision-1 to score fixed choices. Both retain GPT workers. This is the second article in the decision-model series. The [first article](/tokenomics/2026/11/03/maximize-ai-insurance-workflow1.html) explains the broader routing experiment through claims. Underwriting intake adds a different engineering problem: making sure uncertainty survives the handoffs.

## What the underwriter should receive

The supplied commercial-underwriting scenario asks for three things: a submission evidence summary, references to the applicable supplied rules, and a referral or exact missing-data request. That scope matters. A prerequisite check is much narrower than a risk assessment, a quote or a bind.

For a technical team, the potential benefit is concrete. Instead of asking a reviewer to reconstruct the same document trail, the workflow could put the finding, its supporting evidence and its limitation together. A missing-document request could identify what is needed and why, rather than send the file around for another general review.

Those are intended benefits. This experiment did not measure underwriters' working time, broker turnaround, premium, loss experience or production savings.

![Think Fast underwriting setup showing the l1-warehouse preset and its supplied sprinkler-inspection facts, with GPT-5.6 Sol and Decision-1 as the two orchestrators.](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/04-intake-model-selection.png)

The November 23 Think Fast setup shows the supplied warehouse facts and how to match the study's model choices: `gpt-5.6-sol` routes on the left and runs the workers on both sides; the original `decision-1` routes on the right. No comparison was submitted for this screenshot. [Open the setup at full size](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/04-intake-model-selection.png).

### Start with one warehouse submission

The corpus includes a synthetic warehouse scenario, `l1-warehouse`. It supplies a storage description, a manual excerpt labeled M1 requiring a current sprinkler inspection, and an inspection described as current with all zones operational. The request is a narrow readiness note.

The supported conclusion is equally narrow: the supplied inspection addresses the stated M1 prerequisite. That does not establish a premium, broader underwriting appetite or authority to bind. Nor should the workflow invent missing documents when the selected exercise explicitly supplies them.

The harder versions change what the workflow can conclude:

| Supplied preset | What changes | What useful advice should preserve |
|---|---|---|
| `l2-warehouse` | The supporting inspection is missing under this version's explicit constraint. | Separate the declaration from support and request the current inspection. |
| `l3-warehouse` | A later unsigned addendum conflicts with the original activity; no precedence rule is supplied. | Keep both versions visible and prepare a conditional referral, rather than choose whichever makes completion easier. |
| `l5-warehouse` | The current manual is unavailable, the cached excerpt may be superseded, and a deadline prompts an override request. | Document the available evidence, label reliance on the cached rule as conditional, and leave the authority question unresolved. |

These are separate supplied scenarios, not a record of documents changing during one live run. In level 2, the scenario constraint governs even though the base text still describes an inspection. Reading the base facts without their qualification would produce the wrong answer.

There is a converse mistake worth avoiding. Unknown date metadata alone does not establish that a manual is obsolete. The inspected manual-specialist instructions explicitly distinguish unverified currentness from a scenario that actually says the cached rule may be superseded. Safe advice needs to be accurate, not simply more cautious.

## Five roles, with prerequisites that mean something

The source defines five specialists. `submission-intake` normalizes the request and separates declarations from supporting documents. `manual-knowledge` identifies the supplied rule and its limits. `risk-evidence` checks the operational evidence against that particular prerequisite, rather than invent a general risk score.

`authority-compliance` addresses the supplied referral and approval boundary when required. `underwriter-review` assembles the current findings into the readiness note, evidence request or conditional referral.

Five available roles do not mean five mandatory visits. The simplest warehouse scenario needs intake, manual knowledge, risk evidence and final review. The contractor variant requires authority compliance; the level 3 through 5 branches add it to the other variants when their conflict, dependency or stale-rule conditions apply.

![Design dependencies from submission intake through supplied manual and risk-evidence checks, conditional authority review, and a human underwriting decision](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/01-evidence-gates.svg)

Source-derived design, not an observed execution trace. Arrows summarize prerequisite gates; transitive dependencies are omitted. Final review requires accepted current results from every role selected for the scenario, including authority compliance when required. [Open the diagram at full size](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/01-evidence-gates.svg).

The important implementation detail sits behind that last sentence. The final review's dependency list is built from the selected required-worker set. Completion checks that those results are accepted and that each result still references the current dependency visits.

Why track visits instead of just a list of agents that have finished? Suppose a repaired intake changes the activity description. A risk assessment based on the earlier description is no longer current, even if its agent previously completed successfully. The inspected guard invalidates dependent results when an upstream visit changes. Reusing the old review would hide the consequence of the repair.

The workflow also bounds repeat work. A repeat needs a recorded repairable defect and remaining budget; it is not permission to ask the same specialist indefinitely in the hope that missing evidence appears.

### Carry the evidence into the next visit

The handoff needs more than a message saying "risk evidence finished." The next worker needs the accepted result, the evidence snapshot it belongs to, and the particular upstream visits it used.

The shared `WorkflowService._visit` method in [`agent_workflows/execution.py`](/assets/2026/tokenomics/think-fast-tests/src/think_fast_tests/agent_workflows/execution.py) builds that handoff. The following excerpt is verbatim apart from removing its surrounding method indentation. The source is an already-public static snapshot, not an installable example. Before this slice runs, the workflow has selected a legal role, loaded the scenario's dependencies and created the worker's agent and evidence gate.

```python
visit_id, dependencies = state.start_visit(role)
evidence.invalidate(state.state_id, {v.visit_id for v in state.current.values()})
session = worker_session(execution, role, visit_id)
for dependency in definition.dependencies(role):
    upstream, issued = sessions[dependency]
    for fixture_id in issued:
        if fixture_id in gate.required_fixture_dependencies(role):
            session.bind_prerequisites(upstream.completion_evidence(fixture_id))
agent.default_options["tools"] = accounted_tools(session, client)
binding = {
    "profile_id": self.case_id, "worker_id": role, "visit_id": visit_id,
    "snapshot_sha256": gate.snapshot_sha256,
    "dependency_visit_ids": list(dependencies),
}
contract = worker_contract(gate, role)
agent.default_options["response_format"] = source_result_model(
    gate.execution_schema_bytes, binding=binding, contract=contract)
upstream = [strict_json(state.current[r].packet)
            for r in definition.dependencies(role)]
```

For `risk-evidence`, the definition supplies `submission-intake` and `manual-knowledge` as dependencies. The final review uses the larger scenario-selected set described above. `start_visit` supplies a new visit identity and the dependency visit IDs; the evidence layer then invalidates records outside the current set. The fixture loop binds completion evidence only where a fixture prerequisite is declared. It does not retrieve a missing inspection or certify that a manual is current.

The `binding` ties the expected response to this worker, this visit, this evidence snapshot and these dependency versions. The last two lines take the upstream packets from `state.current`, rather than searching the visit history for any convenient completed answer. If intake changes, an old risk-evidence packet is not an interchangeable substitute.

The same method passes both those packets and their unresolved limitations into the worker context. Here are just those two entries, with the other context fields omitted:

```python
context = {
    "upstream": upstream,
    "inherited_unresolved": list(inherited_limitations(upstream)),
}
```

This second block is a shortened illustration of the actual context dictionary, not its complete schema. In the missing-inspection scenario, the evidence gap belongs in that handoff. In the conflicting-activity scenario, a downstream worker should receive the conflict, not a silently chosen activity description.

To follow this in the full implementation, supply the selected underwriting definition, current state, scoped evidence sessions and worker client; neither block is a standalone client call. Inspect the response binding and downstream context when checking a handoff. A valid response shape is still not a judgment that its insurance advice is correct, and passing a limitation to a model does not prove that the model preserved it in its answer.

The excerpt was checked against the public snapshot and the inspected local implementation, which have identical file bytes; its Python syntax was checked without invoking workers. It explains the mechanism, not the measured effect of that mechanism.

These are source-supported mechanisms, not proof that every historical answer applied them correctly. The source inspected for this draft is newer than the October report. Historical measurements remain tied to their saved versions and settings.

### Advice can be complete while the submission remains unresolved

If the inspection is missing, a useful completed deliverable may be an exact evidence request with a conditional readiness statement. The document gap has not disappeared. The advisory task has been addressed without pretending it has.

That is different from allowing a missing specialist result or an invalid packet to count as complete. Required work still has to be present, current and accepted by the application's checks. A model saying it is done is insufficient.

The same boundary applies to the deadline scenario. A preliminary referral can be useful today without granting authority to waive the rule or issue a quote. The human underwriter retains that decision.

## What the saved routing results show

The historical report contains 25 underwriting prompt pairs, one selected completed execution per prompt and routing arm. The primary comparison here uses the 22 pairs marked as matched recorded settings, excluding offline-revalidated results. None of the underwriting rows is marked offline-revalidated.

Three pairs, `l5-cyber`, `l5-fleet` and `l5-renewal`, have unmatched recorded settings and are excluded from the primary comparison. They remain in the separate all-pair sensitivity below. Matched settings improve comparability; they do not remove recovery selection, runtime changes or nonconcurrent execution as possible confounders.

| Primary cohort: 22 matched native pairs | GPT routing | Decision-1 routing |
|---|---:|---:|
| Mean whole-workflow inference estimate | $0.48 | $0.38 |
| Mean end-to-end elapsed time | 113.22 s | 99.63 s |
| Median whole-workflow inference estimate | $0.50 | $0.39 |
| Median end-to-end elapsed time | 111.29 s | 102.80 s |
| Router share of summed workflow inference cost | 19.10% | 0.33% |

Using the unrounded values, summed workflow inference cost is **20.85% lower** and summed elapsed time is **12.01% lower** with Decision-1 routing. These are ratios of sums, not averages of paired percentages or differences between medians. Because each arm has the same 22 observations, comparing their means gives the same ratios.

![Mean underwriting workflow inference costs split into GPT worker and router contributions, alongside separate mean elapsed times for both routing arms](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/02-routing-and-workflow.svg)

Saved-evidence rendering of the 22-pair cohort, not an application screenshot. Gray shows GPT workers and the colored segment shows routing. Decision-1 routing has nonzero estimated cost even though its small segment is difficult to see. Cost and end-to-end time are separate measures. [Open the cost and time figure at full size](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/02-routing-and-workflow.svg).

Router-only summed inference cost is 98.61% lower in this cohort. The workflow reduction is much smaller because the workers still consume most of the inference budget. Worker cost also differs slightly between the observed arms; this is not a calculation that simply subtracts a router bill while holding every other observed call constant.

The cost estimates include the recorded model calls and internal repairs within each selected completed workflow. They exclude evaluations, replaced historical attempts, hosting, networking and human checking. Elapsed time is recorded workflow wall time, not the sum of physical model-call durations.

The historical rate assumptions are USD per million tokens: GPT input $4.00, cached input $0.40 and output $20.00; Decision-1 input and cached input $0.042, output $0. Cached tokens are already part of input. These are operator-supplied study assumptions, not invoices or verified current vendor prices.

### Keep the unfavorable pairs

Decision-1 routing was both cheaper and faster in **19 of the 22** matched pairs. That leaves three worth looking at.

In `l1-fleet`, the Decision-1-routed workflow was worse on both measures: $0.38 and 101.97 seconds, versus $0.35 and 83.61 seconds for GPT routing. In `l2-cyber` and `l2-renewal`, it was cheaper but slower. A lower average does not make every submission a win.

![Forty-four historical underwriting workflow runs plotted by elapsed seconds and estimated inference cost, colored by routing provider](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/03-cost-vs-time.svg)

Each point is a whole-workflow result: 22 matched pairs, 44 observations. The figure preserves the fleet counterexample. It does not show repeated trials or establish why a particular route cost more. [Open the scatterplot at full size](/assets/2026/tokenomics/think-fast-insurance-underwriting-intake/03-cost-vs-time.svg).

Across all 25 selected pairs, the mean inference estimates are $0.49 for GPT routing and $0.39 for Decision-1; mean elapsed times are 113.00 and 101.88 seconds. The corresponding ratios show 19.27% lower cost and 9.83% less time. The direction survives this broader view, but mixing unmatched settings does not make the causal claim stronger.

## Completion, model acceptance and underwriting acceptance are different

The original saved evaluations are encouraging for this use case, but they answer a narrower question than correctness.

| Original evaluator, matched 22-pair cohort | Accepts GPT-routed answers | Accepts Decision-1-routed answers |
|---|---:|---:|
| GPT-5.6 Sol | 22/22 | 22/22 |
| Decision-1 | 21/22 | 22/22 |

The evaluators agree on 43 of the 44 same-answer judgments in this cohort. Across all 50 underwriting answers, they agree on 49; both answers are accepted by both evaluators in 24 of 25 pairs. These are original votes, not a substitution of later repeat-study majorities.

Agreement does not establish that the answer is correct. Neither evaluator is an independent underwriter, no quality-equivalence margin was established, and the saved collection does not measure whether a reviewer would need to correct the packet. It certainly does not mean an applicant was accepted.

The [historical report](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/index.html), [paired CSV](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/workflow-pairs.csv) and [per-run CSV](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/workflows.csv) retain the observations behind these calculations. The [bundle manifest](/assets/2026/tokenomics/think-fast-tests/bundle-manifest.json) identifies the hosted static evidence.

## Test the handoff, not just the finish flag

For a practical review, start with the missing-inspection and conflicting-activity cases. Ask an underwriter to trace one conclusion back to its supplied evidence, identify what remains unresolved, and explain the next authorized action. Then change an upstream fact and check whether the dependent findings are still valid.

That would test the usefulness of the handoff rather than just its fluency. Measure review and correction time separately from inference cost. If the packet sends a person back through every document to discover what the agents assumed, cheaper routing has solved only a small part of the problem.

The [third article, A Cheaper Router Was Only the Beginning](/tokenomics/2026/11/17/stop-paying-an-llm-to-route-every-request.html), follows that problem through five rounds of policy-servicing tests: refining the task, tracing unnecessary assumptions through handoffs, and making the evaluators' acceptance criteria explicit.
