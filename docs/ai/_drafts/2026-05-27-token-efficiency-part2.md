---
layout: post
title: "Token Efficiency - Part 2 - Design Patterns"
---

This is the second post in a three-part series on token efficiency. In Part 1, I framed tokens as an engineering budget: latency, cost, accuracy, and team flow all degrade when we waste context. This post is the architectural follow-through for leaders and architects who want AI systems that stay useful after the demo and the bill arrives.

## Manage Context by Managing Scope

The most practical way to reduce token use is not clever prompting. It is reducing how much irrelevant material the model needs to see in the first place.

That sounds obvious, but teams still point AI tooling at monorepos with six languages, three generations of build systems, and abandoned platform experiments. The model pays attention to all of it because, from its point of view, all of it might matter.

This is the old microservices lesson in new clothing: scope is a design decision. In the SOA and microservices years, we learned that service boundaries were not just organizational niceties. They controlled blast radius, deployment independence, and failure modes. AI adds one more reason to care. Boundaries now also control context load.

If a repository contains only one bounded capability, the AI starts with less noise. Fewer irrelevant files. Fewer adjacent concerns. Less ambiguity between similarly named handlers, DTOs, or test fixtures. The model has a better chance of staying on task because the system has already done some filtering.

That does not mean every team should carve a monolith into fifty tiny repos because an LLM prefers a clean room. We already made that mistake once for other reasons. The point is narrower: when you create boundaries, include AI context efficiency in the tradeoff analysis along with deployability, ownership, and runtime coupling.

### The Orchestrator and Specialist Pattern

A pattern I like here is one orchestrator agent paired with specialist agents that each work inside a narrow scope. Think fleet mode, but with architecture behind it.

The orchestrator owns the goal: "implement this API change," "audit the migration plan," or "trace the regression." It delegates to specialists with constrained views of the world: one agent for the payment service, one for the deployment templates, one for the test harness, one for the ADRs. Each specialist gets a smaller slice of the repo and a more specific instruction set.

That is very close to service decomposition thinking from the SOA era. A coordinator handles workflow. Specialized services own clearly bounded responsibilities. We used to do this to reduce coupling and let systems evolve independently. Now we also do it so the AI does not drag half the company into its prompt.

A concrete example might look like this:

```yaml
agents:
  - name: orchestrator
    scope:
      - docs/architecture
      - plans
    responsibilities:
      - break work into subproblems
      - gather specialist outputs
      - produce final implementation plan
  - name: billing-specialist
    scope:
      - services/billing
      - contracts/billing.openapi.yaml
    responsibilities:
      - update billing API and tests
  - name: infra-specialist
    scope:
      - infra/terraform
      - .github/workflows
    responsibilities:
      - update deployment and policy checks
```

The file is simple on purpose. It is auditable, easy to reason about, and captures the operating model: each agent sees only what it needs.

That changes repository design in a subtle way. We used to ask, "How should humans organize this code?" Now we should also ask, "What does an AI need to see to solve a bounded problem well?" Those are not identical questions.

## File-Based Artifacts as Durable Memory

LLMs are stateless across sessions in any meaningful engineering sense. Tools may retain chat history for a while, but the reliable unit of persistence is still the file.

The principal from one of my children's schools would say, "if it's important, write it down." So write things down. Or splurge a little and have AI translate your natural language to YML.

I mean the boring, durable things: architecture decision records, interface contracts, migration plans, requirements, known constraints, and handoff notes. Write it once because re-explaining the same system from scratch burns tokens and introduces drift.

This pattern has deep roots. Configuration management, infrastructure as code, and docs-as-code all came from the same realization: if a fact matters operationally, it should exist as a durable artifact rather than tribal memory. AI work benefits from the same discipline.

A lightweight ADR is often enough:

```md
# ADR-021: Customer IDs remain immutable

## Context
Billing events, support tooling, and data warehouse pipelines all key on `customer_id`.

## Decision
`customer_id` is immutable after creation. Merges create a new canonical mapping record.

## Consequences
- API handlers must reject update attempts with HTTP 409.
- ETL jobs must resolve canonical mappings.
- Support tooling needs a merge workflow, not an edit workflow.
```

That ADR saves tokens every time an agent touches billing, support, or ETL code. Instead of re-teaching the constraint in lengthy, ambiguous prose, you point to `docs/adr/021-customer-id-immutable.md`.

Contracts matter just as much. When interface definitions are explicit, the model spends less effort inferring them from scattered implementations.

```yaml
paths:
  /customers/{customerId}:
    patch:
      operationId: updateCustomer
      responses:
        '409':
          description: customer_id is immutable
```

There is a workflow shift here that I think matters: move from "explain it every time" to "point to the file." Teams that internalize that shift get faster handoffs between people, between sessions, and between humans and AI agents.

In practice, that usually means:

- decision logs for rules that are easy to violate
- contracts for APIs, events, and schema boundaries
- short handoff documents for multi-session work
- runbooks for operational steps you do not want improvised

None of this is glamorous, and it reduces your chances to have a snarky argument with AI about what you meant. But it is still the right move.

## Token-Efficient Language Choices (Pragmatically)

Language choice affects token efficiency more than many teams expect. Some languages simply require more syntax, ceremony, or framework scaffolding to express the same unit of behavior. That extra structure is not always bad; sometimes it buys safety or clarity. But it does increase context noise.

To illustrate, here is an example of the same basic, tiniest microservice endpoint with two different stacks.

```go
package main

import (
    "encoding/json"
    "net/http"
)

type Status struct {
    Service string `json:"service"`
    OK      bool   `json:"ok"`
}

func statusHandler(w http.ResponseWriter, _ *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    _ = json.NewEncoder(w).Encode(Status{Service: "billing", OK: true})
}
```

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/status")
def status() -> dict[str, object]:
    return {"service": "billing", "ok": True}
```

The Python version is shorter. Often much shorter. For fast iteration, data work, or library-heavy AI integration, that is an advantage. The Go version is also concise by industry standards and in a larger service can create less framework sprawl than some dynamic stacks. It depends.

I would not make language decisions on token count alone any more than I would choose a database solely by benchmark charts. The better rule is to be intentional. If a service benefits from a concise, performant stack, say so and use it. If the problem lives or dies on library depth, notebooks, or model SDK support, Python is often the practical answer.

If you can use Rust, it's even more concise and easier for AI to manage. I found that libraries I wanted to use weren't available yet in Rust, so for now I am sticking with Python.

This is the same polyglot architecture lesson many of us learned over the last twenty years: right tool for the job beats ideological purity. AI adds one more input to the decision matrix. The language is not just for the runtime and the developers anymore. It is also part of the model's working set.

I think this is where engineering leaders need to stay disciplined. "Use Python for AI" is too blunt. "Never use Python because it gets messy" is too blunt too. Pick the stack that reduces total system friction, including what the humans maintain and what the model must absorb.

## Use LLMs for Their Strengths

LLMs are good at synthesis, code generation, translation between formats, and making reasonable local guesses when the problem is underspecified. They are not especially good at being your source of record, your deployment engine, or your final authority on whether a critical change is safe.

So let the model generate. Let scripts execute.

This is just separation of concerns applied to AI systems. We learned long ago not to let presentation logic own database integrity. We learned not to let distributed retries rewrite business rules. The same restraint applies here.

A good pattern is template-first with guarded fallback. Try the deterministic path first. If that path cannot cover the case, let the LLM fill the gap inside clear constraints.

```python
from pathlib import Path

TEMPLATES = {
    "http-api": "templates/http_api_service/",
    "worker": "templates/queue_worker/",
}


def scaffold_service(kind: str, destination: Path) -> None:
    template = TEMPLATES.get(kind)
    if template:
        copy_tree(template, destination)
        return

    generated = llm_generate_service(kind=kind)
    validate_generated_files(generated)
    write_generated_files(destination, generated)
```

The interesting part is not the fallback. It is the order of operations. Known good artifacts first. Generation second. Validation always.

Selective artifact reuse fits the same model. If your team has already generated a clean Terraform module, an OpenAPI policy, a database migration skeleton, or a reliable GitHub Actions workflow, save it and reuse it. Stop paying tokens to rediscover the same answer every Tuesday morning.

Mature teams get better results from AI by not asking the model to be endlessly creative in routine paths. They let it help where novelty exists and standardize the rest.

## Deterministic Controls Where Trust Matters

Where trust matters, bias toward deterministic and auditable controls.

I am not saying every AI-assisted workflow must feel like launching a spacecraft. That would be exhausting. But if the action touches security, compliance, production infrastructure, data movement, or irreversible change, you want explicit governance layers around the model.

This has strong precedent in defensive programming and distributed systems. Circuit breakers, retries with limits, idempotency keys, feature flags, and approval gates all exist because complex systems fail in creative ways. AI gives us one more source of creativity. Not always the good kind.

A practical control stack might include:

- template-first paths for common changes
- guarded LLM fallback when the template does not fit
- sequential migrations instead of free-form mutation
- policy checks before merge or deploy
- role-scoped tools so agents can inspect more than they can change

Sequential migrations are a good example. An agent should not invent the entire state transition model in one free-form leap if a migration framework already exists.

```bash
#!/usr/bin/env bash
set -euo pipefail

for file in migrations/*.sql; do
  echo "Applying ${file}"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$file"
done
```

Is that script glamorous? No. Is it more trustworthy than asking an LLM to improvise schema surgery against production? Very much so.

The broader pattern is the same as a circuit breaker: prefer bounded behavior under uncertainty. Let the model propose, translate, draft, classify, or fill in well-defined gaps. Do not let it quietly become the policy engine.

Role-scoped tools matter here too. Give one agent read access to production logs. Give another access to generate deployment manifests in a branch. Do not casually hand broad mutation rights to every helpful-looking assistant. We spent years learning least privilege for humans and services. That lesson did not expire when the interface became conversational.

## The Thread That Connects These Patterns

These patterns are not separate tricks. They reinforce each other.

Smaller scope reduces context load. Durable artifacts preserve context across sessions. Intentional language choices reduce incidental noise. LLM-first-for-generation and deterministic-first-for-control keeps the model where it is strong and the system where it is trustworthy. Put together, they create AI systems that are cheaper to operate, easier to reason about, and less likely to wander off into expensive nonsense.

I have seen this movie before, just with different props. Distributed systems forced us to care about coupling, failure domains, contracts, and operational discipline. AI systems force the same habits back onto the table, with tokens now standing in for bandwidth and memory.

That is why I think token efficiency is not a prompt-engineering hobby. It is architecture. If you treat it that way, the decisions become clearer.

## What's Next

Part 3 will move from patterns to operations: how to turn these ideas into a practical playbook for teams and delivery pipelines. That is where the tradeoffs get less theoretical. The interesting question is whether teams will treat token efficiency as temporary tuning or as a permanent architectural constraint.
