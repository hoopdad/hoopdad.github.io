---
layout: post
title:  "Token Efficiency"
---

## The Importance of Token Efficiency
UBB
Environment
hyperscalder data center capacity

## Philosophy
Token optimization as a practical driver: Lower prompt overhead and faster iteration.
Use LLMs for their strengths: AI-generated code, smart tool use, and selective artifact reuse.
Manage context by managing scope: Smaller repo boundaries with orchestrator + specialists in fleet mode.
Write things down in file-based artifacts: Durable memory and handoff docs for flows, contracts, and decisions.
Use token-efficient languages pragmatically: Prefer concise, performant stacks where they fit; use Python when ecosystem depth is needed.
Codify operations, not ad hoc commands: Prefer reusable scripts and IaC over one-off terminal sequences.
Favor deterministic, auditable controls for trust: Template-first paths, guarded LLM fallback, sequential migrations, explicit governance layers, and role-scoped tools.
Use keywords to reduce prompt turns when helpful: TDD mindset, red-team thinking, and instruction-following.

## Tops for Use

### Keep infra codified

Use Terraform or Bicep for Azure deployments, but go one step further. Use Azure Verified Modules as opinionated TF/Bicep modules to minimize the amount of requirements tokens to use.

### Bias to reusable artifacts

Encode recurring workflows in contracts, requirements, and decision logs for faster future turns. Deployments are via scripts that you have AI write and store, preferably executed by MCP tools.


### Remind the agent
If you see it not following your workflow, tell it to follow its instructions.