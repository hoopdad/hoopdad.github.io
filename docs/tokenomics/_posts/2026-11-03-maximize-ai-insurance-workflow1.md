---
layout: post
title:  "Maximizing AI in Insurance Workflows, Responsibly: Decision Models for Cost and Time Savings"
---

My testing shows potential for massive value add with agentic AI workflows. I ran 225 tests of agentic workflows to compare the quality, time and cost of the new Microsoft Decision-1 decision model versus a high-quality LLM. This post shows the engineering and design that goes into a workflow, what it consumes, and the value it produces. The focus is on a workflow modeled for insurance industry savants: "Claims evidence & coverage pack."

Here's the question that started it. We use GPT-style models for almost everything in an agent. But agents make a lot of narrow decisions: which specialist goes next, whether the work is done, whether a person needs to look. Those decisions may not need a generative model at all.

<!-- SCREENSHOT 1: Think Fast side by side on a workflow. GPT routing on the left, Microsoft Decision-1 on the right, the same request on both. -->
![Think Fast running a workflow with a GPT orchestrator on the left and a Microsoft Decision-1 orchestrator on the right](/assets/2026/tokenomics/claims-01-side-by-side.png)

This is the first post in a series. I tested 9 insurance and reinsurance industry common workflows.
I'll post about them all and my best-practices Tokenomics design principles behind them.

## About the Workflow

### The use case

A new claim shows up with a stack of evidence: the first notice of loss, the policy, photos, repair estimates, invoices, correspondence, maybe a police report. Before an adjuster can make a call, someone has to answer four questions. What happened? Is it covered? Does the evidence hold together? Is there money to recover from someone else?

That prep work is where adjusters lose hours. It's also where leakage creeps in: a missed exclusion, a duplicated invoice, a subrogation opportunity nobody spotted. The claims evidence & coverage pack does the prep. The adjuster makes the decision.

### The agents

Five specialist agents, each with a narrow job:

1. `claim-intake` pulls the loss facts out of the first notice and the documents: who, what, when, where and how much, plus anything missing.
2. `evidence-reconciliation` lines the documents up against each other and flags conflicts: dates that don't match, amounts that don't add up, descriptions that disagree.
3. `coverage-review` checks those facts against the policy wording, including coverages, limits, deductibles, exclusions and conditions, and cites the clause behind each finding.
4. `recovery-review` looks for subrogation, salvage and other recovery opportunities, and flags anything that deserves a second look.
5. `adjuster-review` assembles the pack for a human: the coverage position, the evidence gaps, the recovery flags and the open questions.

A person makes the coverage decision. Always! The agents gather, prepare and support but the adjuster decides.

### What the orchestrator does

The orchestrator doesn't write any of the analysis. It routes. After every step it looks at the workflow state (the claim, which agents have finished, what they produced) and picks what happens next: the next specialist, a repeat of a step when new evidence calls for it, finish, or stop on an unusable file.

That's a decision. It's not the business decision, but it's an impactful decision to the cost, elapsed
runtime, and ultimately the value of this workflow. In one version of the workflow, a GPT-5.6 Sol orchestrator reads the state and answers with its choice. In the other, the same state goes to Decision-1 with a fixed list of options, and Decision-1 returns a probability for every one of them. The five worker agents are identical in both versions. Only the orchestrator changes.

Those are the literal routing IDs; the Python modules use underscores. Required workers and prerequisites depend on the scenario. Five available specialists doesn't mean every claim visits all five. The simplest water-loss scenario, `l1-water`, requires intake, evidence reconciliation, coverage review and adjuster review, but not recovery review.

Because each orchestrator chooses as it goes, the two versions don't always take the same path through the agents. In the 25 claims pairs, 12 took identical ordered paths, counting repeats and the terminal choice.

<!-- SCREENSHOT 2: The route view for one claims test, both orchestrators: the orchestrator and five agent cards in the observed sequence, with the point where the two paths diverge visible. -->


## Stats from my Tests

### How I tested

I built nine workflows: eight insurance/reinsurance cases and customer support. Each has five complexity levels and five scenarios at each level. That's 25 scenario pairs per workflow and 225 pairs in all, with 450 selected completed runs. Every scenario has both a GPT-routed answer and a Decision-1-routed answer.

The intended comparison holds the GPT-5.6 Sol workers, prompts, evidence, tools and completion rules fixed while changing the router. The saved collection includes recovered runs and different recorded versions/settings; it is not one pristine campaign. The dashboard's matched native cohort contains 156 pairs, excluding mixed-version and offline-revalidated pairs. Claims has 25 pairs, of which 19 have matched recorded settings and six do not.

The claims evidence & coverage pack ranges from level 1 (simplest) to level 5 (hardest). Each saved answer was independently evaluated by GPT-5.6 Sol and Decision-1 using [`scenario-acceptability-v2`](/assets/2026/tokenomics/think-fast-tests/src/think_fast_tests/agent_workflows/scenario_evaluation.py){:target="_blank"}. The rubric prioritizes accuracy and material completeness, requires enough clarity for human review, and checks the selected scenario's evidence, deliverables, arithmetic and human-authority boundary. It requests a binary accept/reject judgment, not a rationale or confidence score.

Repeatability was a separate, post-hoc study: the 90 originally disagreeing answers across all workflows were evaluated twice more, with the original answers and votes preserved. That tests evaluator consistency; it is not pre-validation of accuracy.

### The results

| Claims evidence & coverage pack, 25 tests | GPT-5.6 Sol orchestrator | Decision-1 orchestrator |
|---|---:|---:|
| Median run time | 149.84 s | 140.98 s |
| Median model inference cost per run | $0.5297 | $0.4489 |
| Orchestrator's share of summed inference cost | 17.29% | 0.29% |
| Median tokens per run, input / output | 122,359 / 11,471 | 118,838 / 12,058 |
| Quality: GPT-5.6 Sol evaluator acceptance, post-hoc majority | 44% (11/25) | 52% (13/25) |
| Quality: Decision-1 evaluator acceptance, post-hoc majority | 96% (24/25) | 88% (22/25) |
| Tests where both chose the same path | 12 of 25 | |

Across the 25 claims pairs, Decision-1's median run was 140.98 seconds and $0.4489 in inference, versus 149.84 seconds and $0.5297 for GPT routing. Summing all selected claims runs gives 17.75% lower inference cost and 7.79% less elapsed time; those percentages are ratios of sums, not differences between medians.

The quality rows show each evaluator separately. Originally agreeing answers retain their initial votes. For originally disagreeing answers, each evaluator's result is its own majority across the original vote and two post-hoc repeats. This does not mean every answer was evaluated three times. In claims, 31 of the 50 saved answers received repeats; the other 19 retain their original agreeing votes.

Under that aggregation, evaluator agreement across all nine workflows is **376/450 (83.56%)**, supporting the observation that overall agreement exceeded 80% after repeated evaluation. The claims-only figure is **22/50 (44%)**. Those agreement percentages include shared accepts and shared rejects; they are not the acceptance rates in the table, an accuracy measure or proof that either router preserved or reduced answer quality. The [three-pass record](/assets/2026/tokenomics/think-fast-tests/assets/analysis/evaluator-repeatability/h2-repeatability-20261031-r2/three-pass-pairs.csv){:target="_blank"} retains the original and repeated votes.

On the 19 matched-settings claims pairs, the reductions are 13.32% in inference cost and 3.65% in elapsed time. The dashboard reports uncertainty separately; these are observations from selected synthetic runs, not guaranteed production savings.

Inference cost includes all recorded internal model calls and repairs in each selected complete run. It excludes historical attempts replaced during recovery, evaluation spending and non-inference Azure services. Token medians cover workers and routing; the router percentages divide summed router cost by summed whole-workflow inference cost.

The fixed study rate card uses USD per million tokens: GPT input $4.00, cached input $0.40 and output $20.00; Decision-1 input and cached input $0.042, output $0. Cached tokens are already included in the input count. These are recorded operator assumptions, not independently verified current Azure prices.

Every test, with its run time, tokens, cost and saved votes, is in the [results report](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/index.html){:target="_blank"} and its [workflow CSV](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/workflows.csv){:target="_blank"}. The report opens directly here, with its evaluation page and linked downloads hosted alongside it.

These are static source and evidence snapshots. The [bundle manifest](/assets/2026/tokenomics/think-fast-tests/bundle-manifest.json){:target="_blank"} records original and hosted file hashes. Three report links to an unavailable private runtime page now point to the saved evaluation CSV; those HTML-only adaptations are recorded separately from the original exports' manifests. No private runtime journals or authentication state are included.

<!-- SCREENSHOT 3: Cost versus run time for all 25 claims scenarios, one point per orchestrator run: 50 points in 25 pairs. -->
![Cost and run time for each of the 25 claims tests, by orchestrator](/assets/2026/tokenomics/claims-03-cost-vs-time.png)

<!-- SCREENSHOT 4: Both evaluators' post-hoc majority acceptance rates and median inference cost by complexity level (1 to 5), for each orchestrator. -->
![Both evaluators' post-hoc majority acceptance rates and median inference cost by complexity level for each orchestrator](/assets/2026/tokenomics/claims-04-by-complexity.png)

Each complexity bar summarizes five answers per router. With only five scenarios, one changed judgment moves an acceptance rate by 20 percentage points. This figure uses the same explicitly labeled repeat aggregation as the table; it does not average the two evaluators into a single quality score.

This started with a customer-support demo. The comparisons here come from the saved 225-pair experiment, not a selected demo run. One run isn't a benchmark.

### The value added

Here's where the claims workflow earns its keep. These are estimates, not measured savings, so I'll show my math.

- Time. If the pack saves an adjuster 30 minutes on a document-heavy claim, that's worth about $36. The [U.S. Bureau of Labor Statistics](https://www.bls.gov/ooh/business-and-financial/claims-adjusters-appraisers-examiners-and-investigators.htm){:target="_blank"} reports a $76,790 median annual wage for claims adjusters, examiners and investigators in May 2024. Assume a 1.7x benefits/overhead multiplier and 1,800 productive hours: $76,790 x 1.7 / 1,800 = $72.52 per hour, or $36.26 for half an hour. The multiplier, productive hours and time saved are assumptions, not test measurements.
- Leakage. [EY's P&C claims assessment discussion](https://www.ey.com/content/dam/ey-unified-site/ey-com/en-us/insights/insurance/documents/ey-property-and-casualty-insurers-tackle-indemnity-in-litigated-claims-v1.pdf){:target="_blank"} places leakage at approximately 7-14% of carriers' total spend in its assessment context; it does not measure this workflow's effect. For an illustrative carrier, assume the workflow prevents leakage equal to 0.25% of $5.6 billion in annual claims spend and touches 480,000 eligible claims. That's $14 million / 480,000 = $29.17 per eligible claim. Both the reduction and the eligible-claim count are scenario assumptions.
- Together, that's about $65 per eligible claim ($36.26 + $29.17), if both assumptions hold without overlap. Capacity released is not automatically cash saved.

Now the cost side. The measured Decision-1-routed claims median is $0.4489 in inference per run; the mean is $0.4419. Document extraction, hosting, storage and tracing were not costed by this benchmark. The median inference estimate alone exceeds $0.30, so these results do not support an all-in Azure estimate below 30 cents.

At 100,000 eligible claims a year, assuming the same workload mix, the observed mean implies roughly $44,190 of inference, plus those unmeasured services. The illustrative $65-per-claim benefit would be about $6.5 million of capacity and avoided leakage, not measured savings or a validated production ROI.

The lesson I keep relearning: the workflow you pick decides the value. How you build it decides the cost.

<!-- SCREENSHOT 5: The results panel for one claims run: elapsed time and estimated inference cost for each route, with the token price settings visible. -->
![Elapsed time and estimated inference cost for one claims run, GPT versus Decision-1](/assets/2026/tokenomics/claims-05-run-results.png)

This panel is reconstructed from one fresh `l1-water` comparison captured for routing evidence, not included in the 25-pair benchmark. GPT took 110.58 seconds and $0.4282 in estimated inference; Decision-1 took 117.58 seconds and $0.3451. Both followed intake, evidence reconciliation, coverage review, adjuster review, then `complete`. No evaluators were called for this capture. Screenshots 3, 4, 5 and 7 are labeled saved-evidence renderings, not screenshots of the live application's UI.

## Microsoft Agent Framework Workflows with GPT and Decision Models

I built both versions with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework){:target="_blank"} and Foundry. The workflow wires an orchestrator to the five agents. The only thing that changes between versions is which model answers "what's next?"

The [claims workflow module](/assets/2026/tokenomics/think-fast-tests/src/think-fast-insurance-claims-evidence/workflow.py){:target="_blank"} constructs the five actual framework agents. This is its wiring, not an invented `router.choose` API:

```python
from . import (
    adjuster_review, claim_intake, coverage_review,
    evidence_reconciliation, recovery_review,
)

MODULES = (
    claim_intake, evidence_reconciliation, coverage_review,
    recovery_review, adjuster_review,
)


def create_agents(client_factory, tools_factory):
    agents = {}
    for module in MODULES:
        client = client_factory(module.ROLE_ID)
        agents[module.ROLE_ID] = module.create_agent(
            client, tools_factory(module.ROLE_ID, client))
    return agents
```

The [shared execution service](/assets/2026/tokenomics/think-fast-tests/src/think_fast_tests/agent_workflows/execution.py){:target="_blank"} gives every worker a GPT `DomainAccountedClient`. It changes only the routing client's model:

```python
router = DomainAccountedClient(
    **options,
    model=gpt if selected.arm == "gpt" else decision,
    purpose="routing",
)
```

That is an excerpt inside the service, where `options` binds the provider/accounting context and `gpt` and `decision` are its model identities. The loop computes legal choices, validates each selected route, attaches evidence tools to the authorized visit and calls the selected agent's `run`. The [native runtime adapter](/assets/2026/tokenomics/think-fast-tests/src/think_fast_tests/agent_workflows/native_runtime.py){:target="_blank"} supplies live providers; the base service's synthetic-only adapter is not itself a live model test.

The GPT router asks the model to pick the next step and parses its answer. The Decision-1 router asks a structured question instead.

### Asking Decision-1 a question

A decision model doesn't take a chat-message list on this endpoint. It takes the state (the evidence), the instructions (what's being decided) and the criteria (the allowed choices and what each one means). The [native compiler](/assets/2026/tokenomics/think-fast-tests/src/think-fast-usecase-one/native.py){:target="_blank"} builds those from the case and current workflow state. These are the exact compiled claims criteria and instructions from the captured `l1-water` request:

```python
import json

criteria = {
    "claim-intake": (
        "Required worker claim-intake is pending or has a reported repairable "
        "defect, and its prerequisites are satisfied. Run this worker to "
        "produce its own required advisory deliverable. "
        "Normalize the synthetic notice and identify missing source fields."
    ),
    "evidence-reconciliation": (
        "Required worker evidence-reconciliation is pending or has a reported "
        "repairable defect, and its prerequisites are satisfied. Run this "
        "worker to produce its own required advisory deliverable. "
        "Check supplied dates, invoices and duplicate documents; never infer "
        "unseen evidence."
    ),
    "coverage-review": (
        "Required worker coverage-review is pending or has a reported "
        "repairable defect, and its prerequisites are satisfied. Run this "
        "worker to produce its own required advisory deliverable. "
        "Apply only supplied policy clauses; flag ambiguity for a qualified adjuster."
    ),
    "recovery-review": (
        "Required worker recovery-review is pending or has a reported "
        "repairable defect, and its prerequisites are satisfied. Run this "
        "worker to produce its own required advisory deliverable. "
        "Describe potential third-party recovery evidence without determining liability."
    ),
    "adjuster-review": (
        "Required worker adjuster-review is pending or has a reported "
        "repairable defect, and its prerequisites are satisfied. Run this "
        "worker to produce its own required advisory deliverable. "
        "Produce an evidence-linked advisory packet and mandatory human-review boundary."
    ),
    "complete": (
        "All case-specific required_workers, including adjuster-review, "
        "have accepted current outputs and completion_ready is true. "
        "Review must use all required current results."
    ),
    "error": (
        "An unrecoverable execution failure prevents every remaining "
        "permitted worker, repair and terminal completion within the budgets."
    ),
}
instructions = (
    "Select the next permitted workflow action. "
    "Choose only from legal_choices. Accepted current prerequisites "
    "must precede dependent work. Pending required workers or "
    "repairable defects do not by themselves justify error. "
    "Use the case-specific required_workers and prerequisites; "
    "completion_ready describes structural readiness, not independent quality. "
    "Choose a legal choice using executable graph progress. Pending "
    "required workers and unresolved business facts are not terminal "
    "execution failures. Run ready workers, repairing rejected visits "
    "only within remaining budgets. Preserve unknown facts and advisory "
    "limitations rather than inventing verification. Final review must "
    "use every current required result. Complete only when "
    "completion_ready is true; independent quality judging is separate. "
    "Error is appropriate when no permitted work can proceed within "
    "the remaining budgets, not merely because work is unfinished."
)
state = json.dumps({
    key: value for key, value in context.items()
    if key not in {
        "messages", "instructions", "tools", "response_format", "tool_choice",
        "max_output_tokens", "token_budget",
    }
})
question = {"type": "choice", "instructions": instructions, "criteria": criteria}
payload = {"model": "decision-1", "state": state, "questions": {"next": question}}
```

Here `context` is the execution service's actual routing context, not a fabricated claim summary. It includes the selected prompt, current worker outputs/status, required workers, prerequisites, legal choices, repair defects, remaining visit budgets and `completion_ready`. In the captured first step, the legal choices were `claim-intake` and `error`; all seven catalog options still received scores.

Give it the actual workflow state, not just the original claim. The question is "what happens next," not "what is this claim about." Structural readiness to complete is separate from independent answer quality.

### Calling it

Decision-1 isn't chat completions or the Responses API. It has its own route on your Foundry resource, and `state` travels as a JSON-encoded string inside the request body.

```python
import os

import httpx
from azure.identity import ManagedIdentityCredential


def call_decision(payload: dict) -> dict:
    # https://<account>.services.ai.azure.com/providers/microsoft/v1/systemone
    endpoint = os.environ["DECISION_ENDPOINT"]
    with ManagedIdentityCredential(client_id=os.getenv("AZURE_CLIENT_ID")) as credential:
        token = credential.get_token("https://cognitiveservices.azure.com/.default").token
        with httpx.Client(timeout=60) as client:
            response = client.post(
                endpoint,
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
            )
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "not supplied")
        raise RuntimeError(
            f"Decision API throttled; Retry-After={retry_after}; no automatic retry"
        )
    if response.status_code != 200:
        raise RuntimeError(f"Decision API HTTP {response.status_code}; no retry")
    return response.json()
```

This is a single-call managed-identity example, not the benchmark's full transport/accounting implementation. It never automatically retries. A retrying caller must honor `Retry-After` and preserve the outcome of the original attempt. The native harness records a Decision-1 allowance of at most 17 requests per 60 seconds for this deployment; that observed allowance is not a universal model limit.

<!-- SCREENSHOT 6: Foundry portal with Microsoft Decision-1 selected in the model catalog, or its deployment details page. -->
![Microsoft Decision-1 in the Foundry model catalog](/assets/2026/tokenomics/claims-06-foundry-decision-1.png)

### Turning probabilities into a route

Decision-1 returns a probability for every option. The benchmark's policy validates all scores, checks that the reported choice is a maximum, applies catalog-order tie breaking and enforces deterministic legal-route gates. It does not use a 0.5 confidence threshold:

```python
import math


def choose_next(answer: dict, choices: tuple[str, ...], legal_choices: list[str]) -> str:
    scores = answer["probabilities"]
    if set(scores) != set(choices):
        raise ValueError("Expected exactly the allowed choices")
    values = [answer["confidence"], *scores.values()]
    if any(
        type(value) not in (int, float)
        or not math.isfinite(value)
        or not 0 <= value <= 1
        for value in values
    ):
        raise ValueError("Invalid probability or confidence")
    if abs(math.fsum(scores.values()) - 1) > 1e-6:
        raise ValueError("Probabilities must sum to 1")
    best = max(choices, key=scores.__getitem__)
    if scores.get(answer["choice"]) != scores[best]:
        raise ValueError("Reported choice is not a maximum")
    if best not in legal_choices:
        raise ValueError("Selected route violates workflow prerequisites")
    return best


answer = call_decision(payload)["answers"]["next"]
next_step = choose_next(answer, tuple(criteria), context["legal_choices"])
```

This is a compact illustration of the tested guards; the repository also validates the provider envelope and duplicate JSON keys. A threshold-based human escalation policy could be added, but it wasn't tested here. Such an escalation would pause for a person, not send work to `adjuster-review` before its prerequisites are satisfied.

In the fresh claims capture, the first Decision-1 routing step assigned **99.7604% to `claim-intake`**, spreading approximately 0.2396% across the other six options. Its reported confidence was a separate field (0.9972048), not a measure of the final answer's quality. The selected route and all seven probabilities were checked against the original provider request/response hashes.

<!-- SCREENSHOT 7: The Selected evidence panel from a claims run: Decision-1's option and probability table for one routing step, with the selected option highlighted. -->
![Decision-1 option probabilities for one routing step in a claims run](/assets/2026/tokenomics/claims-07-probabilities.png)

The linked implementation files are downloadable source snapshots, not a standalone installation of think-fast-tests. For more prompt and agent examples, see my [decision-maker repo](https://github.com/hoopdad/decision-maker){:target="_blank"}, and Bart Czernicki's [System One Decisions Console](https://github.com/bartczernicki/SystemOneDecisionsConsole){:target="_blank"} for a wide range of decision use cases. Microsoft's [introduction to Decision-1](https://commandline.microsoft.com/microsoft-decision-1-model-foundry/){:target="_blank"} and the [Foundry model pricing page](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/microsoft/){:target="_blank"} fill in the rest.

## Why Would this be "Responsible"?

AI's appetite for electricity is real. The IEA projects that electricity demand from data centres will more than double by 2030, to around 945 TWh, slightly more than all of Japan uses today, with AI as the biggest driver ([IEA](https://www.iea.org/news/ai-is-set-to-drive-surging-electricity-demand-from-data-centres-while-offering-the-potential-to-transform-how-the-energy-sector-works){:target="_blank"}).

The per-request picture keeps improving at the same time. Google measured its median Gemini text prompt at 0.24 watt-hours, 0.03 grams of CO2-equivalent and 0.26 milliliters of water, and reported a 33x drop in energy per prompt over one year ([Google Cloud](https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference){:target="_blank"}). MIT Technology Review pointed out that reasoning models likely sit above that median, because they take more steps before they answer ([MIT Technology Review](https://www.technologyreview.com/2025/08/21/1122288/google.gemini.ai.energy/){:target="_blank"}).

Now look at an agent workflow. The orchestrator makes a decision before each worker visit and at termination. Across the 25 claims runs per arm, there were 132 GPT routing decisions and 135 Decision-1 routing decisions: averages of 5.28 and 5.40 per claim, including repeats and terminal choices. If that case mix scaled unchanged to an illustrative 800,000 claims a year, it would mean about 4.22 million or 4.32 million routing calls. That extrapolation is not a production measurement, and five available agents do not impose a six-route minimum.

A decision model scores a fixed set of options instead of generating a prose answer. In this study's rate card, Decision-1 input costs $0.042 per million tokens and output costs $0. Its usage records still report an output token per routing call; zero output pricing is not zero reported output tokens.

Across all 225 selected pairs, whole-workflow inference totals were $127.9392 with GPT routing and $106.7662 with Decision-1: 16.55% lower cost. Summed workflow elapsed time was 3.79% lower. In the stricter 156-pair matched native cohort, the corresponding reductions were 16.21% and 3.79%. These are ratios of summed costs/times, not median-run reductions.

Router-only measurements tell a different story from whole-workflow measurements: across all 225 pairs, summed routing inference cost was 98.61% lower and summed physical routing-call time was 83.97% lower with Decision-1. The GPT workers still dominate overall workflow cost, so those routing percentages must not be presented as whole-workflow savings.

I didn't measure energy, power, carbon or water for either router. Lower prices and elapsed time do not establish proportional reductions in energy: hardware, utilization, caching, scheduling and pricing also matter. The experiment supports a narrower claim about inference cost and timing, and motivates measuring the environmental effect rather than assuming it.

"Responsible" has a second meaning here too. The routing policy and prerequisite gates can be written down and audited, while a human escalation policy could be evaluated separately. The adjuster still makes every coverage decision. Use the smallest model suited to the routing task, validate the work product separately, and keep a human on the decisions that matter. That's what I mean by responsible.

## What's next

This is the first of nine. Next up, one post per workflow for the insurance and reinsurance industries:

- Commercial submission intake and triage
- Policy servicing: endorsements, refunds, renewals and billing
- Product, rate and rule change testing
- Core-system incident triage and mitigation
- Legacy policy and claims data-migration validation
- Reinsurance and catastrophe risk research
- Reinsurance treaty and bordereaux reconciliation
- Customer support routing, where this whole experiment started

After that, I'll walk through the 10 principles that shaped how these workflows were designed and tested, and I would consider best practices for Tokenomics-aware design.

1. Concepts Defined by People
2. Architecture
3. File-Based Inputs, Evidence and Outputs
4. Acceptance Criteria
5. Skills for People
6. Token Resources Management
7. Human Review Gates
8. Agent-Friendly Languages
9. Loops
10. Retrospectives

If you're new here, my [Token Efficiency series](https://hoopdad.github.io/tokenomics/2026/05/27/token-efficiency-part1.html){:target="_blank"} is where this line of thinking started.
