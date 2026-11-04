---
layout: post
title: "Token Efficiency - Part 1 - An Architectural Constraint"
---

This is the first post in a three-part series on token efficiency. It is aimed at engineering leaders and architects deciding whether token usage is a budgeting nuisance, an implementation detail, or something more structural.

My view: token usage has crossed into architecture. This means there is a need tools, frameworks, and principles to maximize the asset. If you design AI-heavy systems as though tokens are effectively free, you will make avoidable mistakes in cost, speed, system shape, and operational trust.

![Token Efficiency as Architectural Constraint](/assets/2026/token-efficiency/token-efficiency-architectural-constraint-32x9-v2.png)

## The Forcing Function: Usage-Based Billing

Usage-based billing makes this real in a practical sense, not just theoretical. The old model hid a lot: a quick question, a long autonomous coding run, and a messy prompt that re-sent half a repository could feel roughly equivalent because the billing abstraction blurred the difference.

That abstraction is going away. Usage now maps more directly to token consumption: input, output, and cached tokens. Ars Technica quoted the rationale clearly: "Today, a quick chat question and a multi-hour autonomous coding session can cost the user the same amount... [lumping them together] is no longer sustainable."

That line matters more than the packaging around it. It says the platform has matured to the point where resource usage must be measured like other engineering resources.

Once tokens map directly to money, behavior changes. Model choice matters. Context size matters. Retry patterns matter. Whether an agent keeps rediscovering the same repository facts matters. Prompt design stops being an aesthetic preference and starts looking like workload engineering.

This does not mean every team needs microscopic token accounting. It does mean leaders should stop treating token use as an invisible byproduct of "AI magic" and start treating it as a measurable systems concern.

![The behavioral shift](/assets/2026/token-efficiency/token-efficiency-behavioral-shift-32x9-v2.png)

## The Behavioral Shift

The most interesting change is how we adapt our behaviors to make sure we can keep realizing this value.

I found myself changing how I work. I spent time understanding how tokens flow through these systems, where they get burned, which tasks justify the spend, and how interaction patterns affect quality and cost. Then I started restructuring my own habits on purpose.

That pattern is familiar. Whenever a resource becomes scarce - memory, bandwidth, compute, or now tokens - teams relearn that optional discipline eventually becomes necessary design.

In practice, the shift looks like this:

**Reduce prompt overhead before asking for intelligence.** If a task can be framed with a tight scope, a short contract, and a few durable artifacts, I do that first. A smaller, better-bounded request is often cheaper, faster, and more reliable than a sprawling one.

**Separate orchestration from execution.** Instead of throwing one giant context window at a complex problem, I increasingly use an orchestrator-and-specialists model. The orchestrator owns the plan, handoffs, and constraints. Specialists work inside smaller scopes. This is not just cheaper; it is easier to reason about and audit.

**Invest in reusable artifacts.** If an architecture decision, API contract, migration rule, or workflow matters more than once, it should live in a file, not in repeated prompt prose. A checked-in artifact is durable memory. It shortens future prompts and gives humans something reviewable when the model gets creative in the wrong direction.

**Prefer trustable controls over clever prompts.** Prompting alone is a soft control plane. For predictable behavior, I would rather route the model through deterministic tools, templates, guards, and role-scoped access. Critical behavior belongs in enforceable mechanisms, not convention.

That is the novel signal: not the billing change by itself, but engineers adapting their design and operating behavior around tokens as a real constraint.

![A philosophy for token-efficient AI work](/assets/2026/token-efficiency/token-efficiency-philosophy-32x9-v2.png)

## A Philosophy for Token-efficient AI Work

The answer is not to squeeze every prompt until it squeaks. Over-optimization can make systems brittle and unpleasant. But teams do need a working philosophy.

**Optimize for lower overhead and faster iteration.** The first payoff of token efficiency is speed. Smaller prompts are faster to prepare, faster to run, and easier to debug. When something goes wrong, a focused request is much easier to diagnose than a heroic paragraph that bundles task definition, architecture notes, caveats, and half a design review.

**Use LLMs for the work they are good at.** LLMs are valuable for synthesis, code generation, translation across representations, tool selection, and selective reuse of existing artifacts. They are less valuable as a substitute for durable memory, deterministic validation, or automation that should already exist in scripts and pipelines.

If your model spends tokens rediscovering stable facts every few turns, you have an architecture problem, not just a prompting problem.

**Manage context by managing scope.** Large context windows are useful, but they can hide poor boundaries the way a larger server can hide an inefficient query. Better patterns often involve smaller repository boundaries, clearer ownership, and orchestration that sends specialists only what they need.

**Write things down.** As the elementary school principal for one of my kids used to tell the students, "if it's important, write it down." Store the things that matter as files: interface contracts, workflow notes, migration rules, design decisions, operating constraints, and acceptance criteria. Use them as handoff documents for humans and models alike. AI did not replace runbooks, ADRs, contracts, and interface definitions. If anything, it made them more valuable.

**Favor deterministic, auditable controls for trust.** If a workflow must be safe, compliant, or reviewable, put as much behavior as possible in deterministic controls. Use explicit tools, templates, policy layers, scoped access, and sequential migrations when the change surface is sensitive.

Token efficiency and trust reinforce each other. A deterministic control is often cheaper than a long prompt trying to persuade a model to behave. It is also easier to audit when something goes wrong.

## What's Next

In Part 2, I will move from principle to design patterns: concrete ways to shape repositories, agents, artifacts, and workflows so token-efficient behavior happens by default instead of by constant human vigilance.

For now, the main point is simple: usage-based billing did not create token efficiency as a concern; it revealed it as one. It is a reflection of the underlying cost of using the technology. Once engineers change how they think, structure work, and build controls around a resource, that resource is no longer just a line item. It is part of the architecture.

## References

- GitHub Blog, [GitHub Copilot is moving to usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/){:target="_blank" rel="noopener noreferrer"}
- Ars Technica, [GitHub will start charging Copilot users based on their actual AI usage](https://arstechnica.com/ai/2026/04/github-will-start-charging-copilot-users-based-on-their-actual-ai-usage/){:target="_blank" rel="noopener noreferrer"}

## Continue the Series

- [Part 2: Design Patterns]({% post_url /ai/2026-05-27-token-efficiency-part2 %})
- [Part 3: An Operational Playbook]({% post_url /ai/2026-05-27-token-efficiency-part3 %})
