---
layout: post
title: "When Two AI Judges Agree, What Have We Actually Measured?"
topic: tokenomics
description: "GPT and Decision-1 judged the same 450 saved answers. Their costs, timing and repeated disagreements show what consensus can screen, and what it alone cannot prove."
---

My experiment was to find out if a decision model can evaluate results
cheaper and faster with the same quality of results. I used a GPT model and
Microsoft Decision-1 to judge the same 450 answers. They agreed on **360, or 80%**.
Decision-1's estimated evaluation inference cost was much lower on the fully
priced comparison, and a separate repeat study found it more consistent.

That makes it useful to look at what the judges agreed about, where they
differed, and what it cost to get those judgments. Agreement alone does not
tell us which judge was right, but, lacking the time to personally review
450 results, consistency may be a good enough answer depending on the situation.

This is the fourth article in the Think Fast sequence, following [claims evidence](/tokenomics/2026/11/03/maximize-ai-insurance-workflow1.html), [underwriting intake](/tokenomics/2026/11/16/think-fast-insurance-underwriting-intake.html) and [policy servicing](/tokenomics/2026/11/17/stop-paying-an-llm-to-route-every-request.html). Here, the models have a different job: evaluating an existing work product rather than deciding which specialist runs next.

## What is the evaluation supposed to help us decide?

Can a fixed-choice decision model replace a generative model for evals?

The earlier articles compared models as routers. Here, they are the evaluators: each reads a completed answer with its task, evidence and criteria, then decides whether the answer is acceptable. This is useful when the output needs more than an exact-text comparison.

For example, a good underwriting response might request a missing document rather than declare the submission complete. The eval needs to recognize whether that response meets the selected task. Comparing the judges' votes shows where they make the same distinction and where a closer look is needed.

## One answer, two judgments

Each answer gets two votes, one from GPT and one from Decision-1. If one passes it and the other fails it, that is a disagreement about the *same answer*, not a difference between the two workflows' outputs.

The October r6 experiment collected 450 answers from 225 paired workflow comparisons across nine use cases. Running both judges on each answer produced **900 logical evaluations**.

![Design diagram showing a frozen task, criteria, evidence and candidate answer supplied separately to GPT and Decision-1, with binary validation before human review.](/assets/2026/tokenomics/think-fast-evaluator-methodology/01-evaluation-pipeline.svg)

*Source-derived evaluation design, not an execution trace. Both judges receive the same packet in separate states, without router identity or previous votes. Different provider protocols carry that shared content.*

Both judges receive the task, selected scenario criteria, supplied evidence and exact candidate answer. Neither sees which router produced it or the other judge's vote. The instructions used here are versioned as `scenario-acceptability-v2`.

The judge evaluates the answer, not whether the application was deployed correctly or every workflow step ran. Those execution checks are separate from deciding whether the answer meets the request.

## The shared question needs two different clients

The instructions define what a pass means. In the [published evaluator source](/assets/2026/tokenomics/think-fast-tests/src/think_fast_tests/agent_workflows/scenario_evaluation.py), `CLARITY_INSTRUCTIONS` includes this direction:

> Accuracy and material completeness are primary: reject incorrect facts, arithmetic or rule application, missing requested deliverables, unsupported conclusions and violations of human-authority boundaries.

It also limits which requirements the judge should apply:

> Apply ONLY the selected variant and level. Broader SOP descriptions and other variant examples do not add requirements to this request.

These are verbatim excerpts, not the entire instruction set. They help distinguish an appropriate missing-information request from an answer that simply leaves out a required calculation. The task, scenario criteria, evidence and answer arrive separately in the packet; neither model is being asked for a general impression of the writing.

`compile_native` sends those instructions and the packet through each provider's API. Before the excerpt below, it validates the packet and model configuration and selects the versioned instructions.

This is a verbatim excerpt with indentation removed, not a standalone client:

```python
if model.deployment == "decision-1":
    body = {
        "model": "decision-1", "state": encoded(packet).decode("utf-8"),
        "questions": {"quality": {
            "type": "choice", "instructions": instructions, "criteria": CHOICES}},
    }
    url = DECISION_URL
else:
    body = {
        "model": "gpt-5.6-sol", "max_completion_tokens": cap,
        "messages": [
            {"role": "system", "content": instructions + " " + encoded(CHOICES).decode()},
            {"role": "user", "content": encoded(packet).decode("utf-8")}],
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "ScenarioAcceptability", "strict": True, "schema": {
                "type": "object", "properties": {
                    "choice": {"type": "string", "enum": ["Pass", "Fail"]}},
                "required": ["choice"], "additionalProperties": False}}},
    }
    url = GPT_URL
```

Decision-1 scores the named choices through its `state` and `questions` contract. GPT receives system and user messages and a strict JSON schema. The same serialized `packet` appears in both; that is the content comparison we want to preserve.

This is not a claim that the APIs or generation settings are identical. The retained model identities name GPT `gpt-5.6-sol`, expected version `2026-07-09`, and Microsoft-Decision-1, expected version `1`. Those are recorded expected versions, not a fresh verification of today's deployments.

The configuration records `max_output_tokens` settings of 8192 for GPT and 2048 for Decision-1. Notice that Decision's fixed-choice body does not send GPT's `max_completion_tokens` parameter. That recorded setting is not a claim about Decision-1's input context window. Neither judge is asked to generate a long rationale, although the recorded token accounting still differs.

After provider parsing and binary validation, `binary_result` preserves the returned choice:

```python
return {
    "decision": {"Pass": "Accept", "Fail": "Do not accept"}[value["choice"]],
    "native": value, "confidence": value.get("confidence"),
    "tie": probabilities is not None and probabilities["Pass"] == probabilities["Fail"],
    "rationale": None,
}
```

`probabilities` has already been read from the validated result. A reported tie remains diagnostic; the mapping does not replace the provider's actual choice with a preferred vote. Confidence, when returned, is retained but is not an acceptance threshold in this binary experiment.

The last line is important. No rationale was returned. A later analyst can inspect an answer and suggest why the models might disagree, but that is not recovered model reasoning.

Transport failures, incomplete responses and invalid binary output remain technical statuses, not rejections. An existing evaluation identity is lookup-only: an unresolved result is not permission to send it again. The historical collection includes separately approved recovery; this article does not turn that into a general retry recipe.

## What did judging cost?

Evaluation is additional work after answer generation. Its cost should not be hidden inside a router-savings percentage.

For **378 answers with complete cost records for both judges**, the summed estimated inference cost was **$10.48 for GPT and $0.11 for Decision-1**. The unrounded ratio of sums gives a **98.93% lower recorded cost** for Decision-1 on that subset. The other 72 pairs remain incompletely priced; they are excluded from both sides, not charged at zero.

![Separate comparisons show GPT evaluation cost of 10.48 dollars versus Decision-1 at 0.11 dollars on 378 fully priced pairs, and mean recorded elapsed of 46.26 versus 22.69 seconds on 450 timed pairs.](/assets/2026/tokenomics/think-fast-evaluator-methodology/02-evaluator-cost-and-time.svg)

*Rendering of saved October r6 evidence, not a new experiment. Cost and timing have different coverage. Elapsed sums physical attempts, including controller admission and rate pacing; it is neither pure inference latency nor concurrent experiment duration.*

The rates are fixed study assumptions per million tokens: GPT input $4.00, cached input $0.40 and output $20.00; Decision input and cached input $0.042, with output priced at $0. These are not invoices or current vendor quotes. Hosting, networking and human checking are outside the comparison.

The complete attempt ledger tells a less tidy, but more useful, story:

| Evaluator | Completed judgments | Physical attempts | Failed attempts | Known cost subtotal | Unknown-cost attempts |
|---|---:|---:|---:|---:|---:|
| GPT | 450 | 519 | 69 | $12.60 | 69 |
| Decision-1 | 450 | 459 | 9 | $0.14 | 9 |

These known subtotals include recorded spending outside the paired-cost subset. They are lower bounds, not complete experiment totals. Two specifically approved timeout replacements remain linked to their original ambiguous attempts; possible duplicate provider execution and original unknown costs were not resolved merely by collecting a final vote.

All 450 pairs have recorded evaluation timing. Mean elapsed was **46.26 seconds for GPT and 22.69 seconds for Decision-1**. Much of that was admission wait: the recorded totals include about 16,234.84 seconds for GPT and 9,276.92 seconds for Decision-1. Removing that recorded wait would still leave transport and other overhead, so it would not give us pure model latency.

The original evaluation interleaved models; later repeat passes used parallel per-model controllers. Adding call durations does not tell us how long a person waited for the whole experiment. These measurements describe this collection, not a controlled production speedup.

## What can we understand from 80% of judgments being in agreement?

Of the 450 answers, both judges accepted 353 and both rejected seven. The remaining 90 split in two directions: GPT rejected 63 that Decision-1 accepted, and accepted 27 that Decision-1 rejected.

![The original same-answer vote matrix shows 353 shared acceptances, seven shared rejections, 27 GPT-only acceptances and 63 Decision-1-only acceptances.](/assets/2026/tokenomics/think-fast-evaluator-methodology/03-original-judge-agreement.svg)

*All 450 original same-answer pairs. The diagonal is 360 agreements, not 360 acceptable answers and certainly not 360 independently verified correct answers.*

The aggregate also hides substantial variation. Underwriting has 49 agreements out of 50 answers; claims has 19 out of 50. That difference makes a single all-case agreement percentage a poor substitute for looking at the work being judged.

For a concrete record, take the Decision-routed servicing answer for `l3-endorsement`, answer ID beginning `10c1f899fe37`. GPT-5.6 Sol returned Do not accept; Decision-1 returned Accept. In the [retained report's original votes table](/assets/2026/tokenomics/think-fast-tests/assets/runs/analysis-h2-r6-wus3-20261029-v2/evaluation.html#inspect), find that answer ID and read across the two judge columns. The routing arm identifies how the answer was produced, not which judge cast either vote. The paired CSV preserves the same record.

That row gives us an item to inspect. It does not tell us which criterion caused the disagreement, or which judge was correct. Neither original binary vote supplies an explanation.

Agreement can still be useful for screening. Shared rejection identifies work that both models flag. Disagreement identifies work needing a closer look. Shared acceptance may help prioritize a review queue, but skipping human review on that basis would require evidence about false accepts that this study does not supply.

Two different models also need not have independent errors. They receive the same supplied evidence and criteria. If those omit an important obligation, both can consistently miss it.

## Would more votes settle it?

A separate retained study revisited all **90 original disagreements**. Each evaluator ultimately had three votes on the same saved answer and packet, using fresh evaluation states. The original answers and votes remained unchanged.

Decision-1 was unanimous across its three votes on **87 of 90 answers**. GPT was unanimous on **54 of 90**. That is a clear consistency difference on this selected subset.

![On the 90 original disagreements, Decision-1 has 87 unanimous triples and GPT has 54; both remain unanimously opposed on 51 answers and their model majorities match on only 16.](/assets/2026/tokenomics/think-fast-evaluator-methodology/04-repeatability-not-correctness.svg)

*Separate three-pass repeatability evidence, not a replacement for the original 80% agreement result. The sample was selected because the judges initially disagreed; it cannot estimate agreement across all answers.*

The more interesting finding is the **51 answers where both models were unanimous, but opposed**. Repeating the vote did not make those judgments converge. Taking each model's own majority left 74 opposing majority decisions and only 16 matching ones.

A stable judge can be consistently wrong. A less stable judge can sometimes be right. Without independent adjudication, this experiment cannot distinguish those possibilities.

The policy-servicing article also describes later changes to task instructions and evaluation policies. Those are different cohorts. They should not be pooled with this October experiment to produce a more flattering agreement number.

## Where this leaves an engineering team

A testing process using an eval follows a fairly simple sequence: **run the application, gather its outputs, run the evals, and summarize the results**. Start with a defined set of inputs and acceptance criteria. Save each output with the task and evidence needed to judge it, then have the evaluator check that collection. Summarize passes, failures, disagreements, cost and elapsed time by test case, rather than only reporting one overall score.

The next step is to inspect the failed or disputed answers and decide what needs to change in the application or the eval instructions. Run the same tests after the change, keeping track of which inputs, criteria and versions were used. In my experiment, the answers were frozen before judging so both models evaluated the same work.

Decision-1 is worth trying for that judging step. It had substantially lower estimated evaluation cost on the fully priced subset and more consistent votes in the repeat study. A sample of accepted and rejected answers still needs an independent check: matching votes tell us that the judges agree, not that the answers are correct.

