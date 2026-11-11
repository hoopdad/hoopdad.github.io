---
layout: post
title:  "Stop Paying an LLM to Route Every Request: Decision Models for Policy Servicing"
description: "How I built a policy-servicing workflow with Decision-1 routing, what it saved, and the Agent Design Best Practices behind it."
---

I started this experiment with a fairly simple idea. Agents make a lot of decisions about what to do next, and we often pay a high-quality LLM to make every one of them. What happens if a decision model does that part?

This is the second part of my series on decision models in agentic workflows. The [first post](/tokenomics/2026/11/03/maximize-ai-insurance-workflow1.html) was about preparing a claims evidence and coverage pack. This one is about **policy servicing: endorsements, refunds, renewals and billing**.

I kept GPT-5.6 Sol doing the specialist work and compared it with Microsoft Decision-1 for orchestration. I'll walk through the design first, including four Agent Design Best Practices I've been testing, then get into the results.

Keeping it real: the matched policy-servicing runs cost **14.01% less in inference**, while taking **1.28% more elapsed time** with Decision-1 routing. I expected both to improve. That difference is worth looking at.

## About the Workflow

### Start with the prompts

My test set is **25 prompts**, with five kinds of servicing request at five levels of complexity. For each prompt, I compare a saved completed run with GPT routing and one with Decision-1 routing.

Here's an example. A customer asks about a refund. The supplied cancellation quote says 40 units, approval and posting are still outstanding, and the ledger has no refund payment. The agent needs to explain each of those steps and what needs to happen next. You can read the exact [prompt](/assets/2026/tokenomics/think-fast-policy-servicing/assets/corpus/artifacts/insurance-policy-servicing/l1-refund.input.json) and [evidence](/assets/2026/tokenomics/think-fast-policy-servicing/assets/corpus/artifacts/insurance-policy-servicing/l1-refund.evidence.json). 

| Prompt topic | What the agents need to understand |
|---|---|
| Instalments and billing | Of three 100-unit instalments, 100 is paid and 200 scheduled. Explain the balance using the supplied ledger. |
| Endorsement | Adding a storage location requires underwriter approval under clause E2. Prepare the checklist and acknowledgement with that approval outstanding. |
| Refund | Explain the 40-unit quote and the approval, posting and payment steps still needed. |
| Renewal | The offer expires on 30 June. An acknowledgement is recorded; explicit acceptance and payment remain outstanding. |
| Documents | Check the V3 draft certificate and the authorized signature needed before issue. |

Complexity grows from a straightforward explanation to missing dates, conflicting screenshots, a same-day response deadline, and finally an unavailable core system with stale data and a request for backdating. The outcome is a service packet and draft correspondence for a person to review.

This is where **human-agent collaboration** comes into the design. The principle is **Concepts Defined by People**: I need to explain what paid, scheduled, approved and issued mean before asking agents to work with them. In my separate Azure support-triage test, writing a complete brief as the prompt made the difference betweeen being able to deliver a result and not. The study refers to this as a gate-pass and it moved from **0% to 92%** on the moderately specified task. On the underspecified task, the vaguer control was slightly cheaper. My takeaway: spend time defining the work, and measure how much that helps on your own prompts.

<!-- SCREENSHOT 1 PLAN: Think Fast application, verified policy-servicing selection and a completed l1-instalment comparison. Frame the exact synthetic request and both routing lanes; keep the same run for screenshots 3-5. Proposed asset: policy-servicing-01-two-lanes.png. Do not reuse the currently open failed customer-support demo or imply that it is policy servicing. No Run/Retry or deployment changes during screenshot planning. -->
> **Screenshot 1 placeholder - One servicing request, two routers.** Think Fast showing the selected policy-servicing request and both observed worker sequences.

### Give each agent a job

The [workflow module](/assets/2026/tokenomics/think-fast-policy-servicing/src/think-fast-insurance-policy-servicing/workflow.py) constructs five Microsoft Agent Framework agents:

| Agent | Assigned job |
|---|---|
| [`service-intake`](/assets/2026/tokenomics/think-fast-policy-servicing/src/think-fast-insurance-policy-servicing/service_intake.py) | Separate the requested change from recorded status and identify the required work. |
| [`policy-terms`](/assets/2026/tokenomics/think-fast-policy-servicing/src/think-fast-insurance-policy-servicing/policy_terms.py) | Check supplied versions, dates, terms and approval prerequisites. |
| [`billing-reconciliation`](/assets/2026/tokenomics/think-fast-policy-servicing/src/think-fast-insurance-policy-servicing/billing_reconciliation.py) | Reconcile ledger facts without inventing fees, collecting money or paying refunds. |
| [`correspondence-draft`](/assets/2026/tokenomics/think-fast-policy-servicing/src/think-fast-insurance-policy-servicing/correspondence_draft.py) | Prepare factual, conditional text from the current required specialist results. Never send it. |
| [`service-review`](/assets/2026/tokenomics/think-fast-policy-servicing/src/think-fast-insurance-policy-servicing/service_review.py) | Assemble the evidence-linked packet, unresolved limitations and next steps for human review. |

A level-1 refund uses intake, billing reconciliation, correspondence and review. More complex prompts add policy and billing work as needed. The draft waits for the required reconciliation, and final review uses all the required current results. The [source SOP](/assets/2026/tokenomics/think-fast-policy-servicing/assets/corpus/artifacts/insurance-policy-servicing/sop.json) has the details.

Five available agents gives me five responsibilities to work with. I still want the shortest useful path through them. I'd also compare a single-agent baseline before choosing this architecture for production; this experiment tests the router choice inside an existing specialist workflow.

### What the router decides

Both routers receive the same seven choices: the five worker IDs, `complete` and `error`. They see the current state, required workers and prerequisites. GPT selects a route; Decision-1 scores the fixed options. Application code checks that the choice is permitted.

That's the job I'm right-sizing: choosing the next permitted step. A person retains authority over refunds, endorsements and other consequential actions.

## Microsoft Agent Framework Workflows with GPT and Decision Models

### Keep the workers; change the routing client

Here's how the servicing module constructs the agents:

```python
MODULES = (
    service_intake, policy_terms, billing_reconciliation,
    correspondence_draft, service_review,
)


def create_agents(client_factory, tools_factory):
    agents = {}
    for module in MODULES:
        client = client_factory(module.ROLE_ID)
        agents[module.ROLE_ID] = module.create_agent(
            client, tools_factory(module.ROLE_ID, client))
    return agents
```

In the [shared execution service](/assets/2026/tokenomics/think-fast-policy-servicing/src/think_fast_tests/agent_workflows/execution.py), worker clients use `model=gpt`. The routing client selects its model by arm:

```python
router = DomainAccountedClient(
    **options, model=gpt if selected.arm == "gpt" else decision, purpose="routing")
```

In that service, `options` carries accounting, provenance and the workflow definition. The [native runtime adapter](/assets/2026/tokenomics/think-fast-policy-servicing/src/think_fast_tests/agent_workflows/native_runtime.py) connects it to live providers; the base service supports offline testing.

This applies **Token Resources Management**, the principle behind the **cost** objective. In my separate Azure test, a right-sized, steered GPT-5.4-mini cost **73% less** than GPT-5.4 on the hard support tasks, with both meeting the objective 100% of the time. That's a different model comparison, but it's why I keep challenging the default model choice. Qualify the smaller model for the job and measure what changes.

Each worker has its own instructions, structured result and authorized tools. Billing reconciliation uses the registered balance calculation for the [three 100-unit instalments](/assets/2026/tokenomics/think-fast-policy-servicing/assets/corpus/artifacts/insurance-policy-servicing/l1-instalment.fixture.json). Correspondence prepares an unsent draft. Those boundaries let me use generation where it adds value and code for arithmetic.

<!-- SCREENSHOT 2 PLAN: Foundry, exact think-fast-tests-insurance-policy-servicing-gpt and think-fast-tests-insurance-policy-servicing-decision-1 Hosted definitions/version details, if available. Show names and version/provenance needed to identify the two wrappers. The five business workers are constructed inside the service; do not imply five separately deployed Foundry workers. Crop account, tenant, subscription, resource identifiers and endpoint details. Configuration evidence only, not a screenshot of benchmark performance. No start, redeploy, permission change or inference. Proposed asset: policy-servicing-02-foundry-definitions.png. -->
> **Screenshot 2 placeholder - The Foundry deployment boundary.** The exact policy-servicing Hosted agent definitions and versions, with identifying infrastructure details excluded.

### The model proposes; the application checks

After obtaining a routing response, the loop uses this sequence:

```python
choice = route_choice(reply.text.encode(), definition.choices, arm=selected.arm)
state.legal(choice)
```

The [routing guards](/assets/2026/tokenomics/think-fast-policy-servicing/src/think_fast_tests/workflows/guards.py) check the normalized response, Decision-1's scores and the selected option. Then the application checks prerequisites and budgets.

That's **Acceptance Criteria**, one of the principles for managing a **quality** objective. My separate coding-agent test, using Claude Haiku 4.5, compared a deterministic contract checker with model reasoning. At 120 endpoints, the checker-assisted approach passed **25/25 runs versus 7/25** for reasoning alone, while consuming more tokens. On smaller tasks, reasoning was cheaper and similarly reliable. I take that as a reason to choose checks deliberately and account for the quality they buy. For servicing, the [rubric](/assets/2026/tokenomics/think-fast-policy-servicing/assets/corpus/artifacts/insurance-policy-servicing/rubric.json) defines the required findings; independent evaluation still checks the business answer.

I also cap the loop: **seven worker visits, including two repairs, and eight routing occurrences**, with a terminal route reserved. A four-worker path plus `complete` uses five routing calls and four worker calls, before internal tool round trips or retries. That gives the workflow room to repair a result and a clear point to stop.

<!-- SCREENSHOT 3 PLAN: Think Fast Selected evidence on a Decision-1 routing step from the same verified policy-servicing run as screenshot 1. Show all seven option scores, selected route and available prerequisite/state evidence. Do not invent a confidence threshold or describe scores as final-answer accuracy. If the current UI does not expose a field, omit it from the eventual caption. Proposed asset: policy-servicing-03-routing-evidence.png. -->
> **Screenshot 3 placeholder - A bounded routing decision.** Think Fast's selected-step evidence showing the actual Decision-1 choice and option scores.

### Keep the evidence current through the handoffs

The **governance** objective shows up in **File-Based Inputs, Evidence and Outputs**. Each result carries source references and dependency visit IDs. If an upstream result changes, downstream work using the old version needs to be revisited.

Why fuss over freshness? In my separate Azure test, a stale saved index passed the freshness check **0/25 times**, while retrieving current information passed **18/25**. The fresh-index scenarios had real cost savings, but the stale index failed freshness in every run. That matters for the [conflicting refund screenshot](/assets/2026/tokenomics/think-fast-policy-servicing/assets/corpus/artifacts/insurance-policy-servicing/l3-refund.input.json) and the [stale-cache endorsement request](/assets/2026/tokenomics/think-fast-policy-servicing/assets/corpus/artifacts/insurance-policy-servicing/l5-endorsement.input.json). I want the packet to say exactly what the supplied evidence supports and what needs checking next.

A completed packet can still contain an unresolved date or missing approval. The person reviewing it decides how to proceed. The tools in this exercise can prepare the work; actual payment, policy changes and delivery require a separately authorized production integration.

<!-- SCREENSHOT 4 PLAN: Think Fast service-review output and correspondence from the same verified servicing run. Show the selected scenario's exact distinction and unsent/advisory limitation; for l1-instalment, 100 paid versus 200 scheduled and no invented fee. Use actual exposed output rather than a reconstructed success packet. If using a refund instead, switch the whole screenshot sequence consistently and disclose its actual outcome. Proposed asset: policy-servicing-04-review-packet.png. -->
> **Screenshot 4 placeholder - A useful answer with a hard boundary.** The final review packet and unsent correspondence, showing what is known, what remains conditional and what has not been executed.

Those are four Agent Design Best Practices applied to the work itself. The Azure support tests used GPT-5.4-mini (compared it with GPT-5.4); the coding test used Claude Haiku 4.5. Their results help me choose what to try here. The [Azure test notes](https://github.com/hoopdad/turingteamengineering/blob/7dd1cb07b0b8c448489b68fb5521563c3ba0f945/analysis/agent-operations/EVIDENCE-STATE.md) and [coding test results](https://github.com/hoopdad/turingteamengineering/blob/7dd1cb07b0b8c448489b68fb5521563c3ba0f945/resources/token-efficiency-tests/RESULTS.md#t07-deterministic-tool--deterministic-verification-tool-vs-llm-reasoning) cover those separate experiments.

The [source bundle manifest](/assets/2026/tokenomics/think-fast-policy-servicing/bundle-manifest.json) records the downloadable servicing code and synthetic fixtures. These are current local snapshots, including later observation hooks, rather than an installable package or the exact code behind every historical run. The benchmark results below come from the preserved October export.

## Stats from my Tests

### Cost and time

The larger study for this series covers nine workflows and 225 prompt pairs. For policy servicing, **19 of the 25 pairs have matched recorded settings and native completion**. Meaning, 19 out of 25 times both evals agreed on the outcome (essentially, both were "pass" or both were "fail"). The other six mix recorded versions, so I'm leading with the 19.

| Matched policy-servicing runs, 19 pairs | GPT router | Decision-1 router |
|---|---:|---:|
| Mean workflow inference cost per run | $0.48 | $0.42 |
| Total workflow inference cost | $9.19 | $7.91 |
| Mean workflow elapsed time | 122.94 s | 124.51 s |

That's **14.01% less inference spend** and **1.28% more elapsed time**, using the unrounded totals. Decision-1 was cheaper on 16 of the 19 prompts and both cheaper and faster on 10.

I expected the faster router to make the workflow faster too. Looking closer, Decision-1 saved **123.60 seconds of physical routing-call time** across the matched runs, yet the workflows took **29.84 seconds longer** overall. The work outside routing outweighed that gain.

My suspicion is variation in worker execution: different paths or repairs, generated response lengths, and waiting around the model calls could all contribute. Worker inference spend was also **$0.46 higher** with Decision-1 across these matched pairs, which is a reason to inspect those calls. It doesn't establish the cause of the timing difference. I'd follow up by tracing visits and waits, repeating the same prompts with fixed versions, and alternating which router runs first.

The mean time difference was only 1.57 seconds per run, with a 95% bootstrap interval from -11.02 to +13.16 seconds. There's enough variation here to be cautious about the speed result. Including all 25 pairs changes it to **17.33% lower spend and 2.64% less elapsed time**.

The routing component itself was much cheaper: **98.64% lower inference spend** and **80.35% less physical call time** in the matched cohort. The GPT workers still account for most of the workflow cost.

<!-- SCREENSHOT 5 PLAN: Think Fast final observed comparison and expanded inference-cost breakdown for the same verified servicing pair. Include the run-original price revision and complete/partial status. Caption the actual run's values and label it a single demonstration, not the 19- or 25-pair aggregate. Never use the currently failed run's known subtotals as complete costs. Proposed asset: policy-servicing-05-cost-breakdown.png. -->
> **Screenshot 5 placeholder - Where the money went.** One verified servicing comparison, with router/worker cost attribution and the applied price assumptions visible.

### How did the answers hold up?

With all the tests in this series, I also wanted to try out the decision model as an evaluator. Why not? It just needs to come up with a simple yes/no or pass/fail answer. Both models independently evaluated each saved answer. Here are their original single-pass acceptance judgments for all 25 prompt pairs:

| Evaluator | GPT-routed answers | Decision-1-routed answers |
|---|---:|---:|
| GPT-5.6 Sol | 84% (21/25) | 88% (22/25) |
| Decision-1 | 92% (23/25) | 80% (20/25) |

They agreed on 40 of the 50 answers. To be clear, agreement tells me about consistency; I still need independent labels and a defined quality bar to establish whether the two routing approaches produce equivalent quality. The separate post-hoc repeat study is in the [evaluation report](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/evaluation.html).

### What the saving could mean

At **100,000 eligible requests a year**, the matched-run means would imply **$48,386.87 versus $41,606.85 in inference**, a difference of **$6,780.02**. Your mileage may vary, of course, but at scale that's worth looking into.

These are model-inference estimates, including internal calls and repairs in the selected completed runs. Hosted compute, networking, storage, tools, evaluation and replaced historical attempts are outside those totals. The dollar amounts came from prices that were in effect as of the day of testing, and might change when you get your hands on it.

The bigger business opportunity is the service representative's time and the quality of the response. I'd measure handling time, rework and repeat contacts alongside operating cost in a pilot. This experiment gives me a reason to try that, learning from where this experiment may have gone wrong with prompting perhaps.

The [results dashboard](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/index.html), [paired CSV](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/workflow-pairs.csv), [per-run CSV](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/workflows.csv) and [summary JSON](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/summary.json) have the details. Filter on `insurance-policy-servicing`.

## What's next

Seven workflows remain in this series: 
- commercial submission intake and triage
- product, rate and rule change testing
- core-system incident triage
- legacy policy and claims data-migration validation
- reinsurance and catastrophe risk research
- treaty and bordereaux reconciliation
- customer support routing.

I'll keep connecting the results to Agent Design Best Practices as I go. For this one, right-sizing the router reduced the cost. Now I want to understand the rest of the elapsed time and what a service team would gain from the finished packet.