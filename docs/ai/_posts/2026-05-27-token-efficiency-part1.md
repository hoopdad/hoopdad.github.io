---
layout: post
title: "Token Efficiency - Part 1 - An Architectural Constraint"
---

This post is the first in a three-part series on token efficiency. It is aimed at engineering leaders and architects who are trying to decide whether token usage is a budgeting nuisance, an implementation detail, or something more structural. My view is that it has crossed the line into architecture. If you design AI-heavy systems and teams as though tokens are effectively free, you will make avoidable mistakes in cost, speed, system shape, and operational trust.

## The Forcing Function: Usage-Based Billing

The first major AI tool moving to usage-based billing in June 2026 is the forcing function that makes this discussion practical instead of theoretical. The old model hid a lot. A quick question, a long autonomous coding run, and a messy prompt that re-sent half a repository could all feel roughly equivalent from the user side because the billing abstraction blurred the difference.

The new pricing model removes that abstraction: usage now consumes AI Credits based on token consumption, including input, output, and cached tokens. Ars Technica quoted the rationale cleanly: “Today, a quick chat question and a multi-hour autonomous coding session can cost the user the same amount... [lumping them together] is no longer sustainable.” That is the important line, more than the product packaging around it. It tells us the platform has matured to the point where resource usage must be measured the way other engineering resources are measured.

Once token use maps directly to money, behavior changes. It always does. If API rates span from roughly $4.50 per million tokens for lower-cost models to $30 per million for higher-end ones, prompt design stops being an aesthetic preference and starts looking a lot like workload engineering. The model choice matters. Context size matters. Retry patterns matter. Whether your agent keeps rediscovering the same repository facts matters.

This does not mean every engineering team needs to become obsessed with microscopic token accounting. But it does mean leaders should stop treating token use as an invisible byproduct of “AI magic” and start treating it as a measurable systems concern.

## The Behavioral Shift

This is the part I think matters most.

The real change is not that billing got more granular. The real change is that I found myself changing how I work. I spent a good number of hours understanding how tokens actually flow through these systems, where they get burned, what kinds of tasks justify that spend, and how interaction patterns affect both quality and cost. Then I started restructuring my own habits to be more efficient on purpose.

That is new.

When engineers begin studying the internal mechanics of a resource and then deliberately adapting their design and operating behavior around it, the resource has become architecturally relevant. That is what happened with memory allocation. It happened with database query plans. It happened with chatty service calls over slow networks. Token usage is now entering the same category.

In practical terms, the behavioral shift looks like this:

### I reduce prompt overhead before I ask for intelligence

If a task can be framed with a tight scope, a short contract, and a few durable artifacts, I do that first. Sending a model a loose, sprawling prompt and hoping it sorts things out is often expensive, slower than it should be, and oddly fragile. A smaller, better-bounded request usually performs better anyway.

### I separate orchestration from execution

Instead of throwing one giant context window at a complex problem, I increasingly think in terms of an orchestrator and specialists. The orchestrator owns the plan, the handoffs, and the constraints. Specialists work within a smaller scope, often against a smaller repository boundary or a narrower artifact set. This is not just cheaper. It is easier to reason about and easier to audit.

### I invest in reusable artifacts

If an architecture decision, API contract, migration rule, or workflow matters more than once, it should live in a file, not in repeated prompt prose. A checked-in artifact is durable memory. It shortens future prompts, improves handoffs, and gives humans something reviewable when the model gets creative in the wrong direction. Models are fast. Files are patient.

### I prefer trustable controls over clever prompts

Prompting alone is a soft control plane. Sometimes that is fine. Often it is not. If I need predictable behavior, I would rather route the model through deterministic tools, templates, guards, and role-scoped access. It is the same instinct we learned in other eras: move critical behavior out of convention and into enforceable mechanisms.

That, to me, is the novel signal. Not the invoice. The adaptation.

## Historical Parallels: When Resources Become Scarce

![Resources that became architectural constraints — from memory to network to databases to cloud to tokens](/assets/2026/token-efficiency/resource-timeline.png)

None of this is unprecedented. The pattern is old, even if the resource is new.

### Memory management before invisibility won

In the 80s and 90s, memory was not an abstract concern for most developers. It was a daily one. You learned where copying hurt, where fragmentation hurt, and why a seemingly simple feature could fail under real constraints. Garbage collection and cheaper hardware changed the ergonomics, but they did not make memory irrelevant. They made careless use temporarily survivable.

Tokens feel similar right now. Many teams are still in the “hardware will save us” phase of thinking. Sometimes it will. Sometimes the bill or the latency graph will have other ideas.

### Network efficiency in the dial-up and early web eras

Anyone who built distributed systems when bandwidth was dear learned quickly that chatty protocols were not elegant; they were painful. You compressed responses, reduced round trips, batched work, and paid close attention to what crossed the wire. Later, faster networks made some of that discipline less visible, though never truly obsolete. Then microservices reintroduced the lesson in a more expensive suit.

AI systems have their own version of chattiness. Re-sending bulky context, repeating instructions that should have been durable artifacts, or asking one agent to do work that should have been decomposed is the new form of unnecessary network traffic. Different medium. Same smell.

### Database optimization when cost and time were obvious

Database people learned long ago that logical correctness is not the same thing as operational fitness. A query can be right and still be irresponsible. Once storage, memory, and compute costs became visible enough, query planning stopped being a niche concern and became part of competent software engineering.

The same thing is happening with prompts and context. A prompt can be valid and still be wasteful.

### Cloud cost optimization after fixed infrastructure

Cloud billing made engineers care about things they had happily ignored in fixed-capacity environments: idle resources, scaling behavior, noisy retries, and hidden multipliers across services. FinOps emerged because the architecture and the bill were now coupled in a way people could not ignore.

Usage-based AI is pushing us toward the same place. Token efficiency begins as cost awareness. It matures into design discipline.

## A Philosophy for Token-Efficient AI Work

I do not think the answer is to squeeze every prompt until it squeaks. Over-optimization is real, and it can make systems brittle or unpleasant to use. But I do think teams need a working philosophy. Here is the one I keep coming back to.

### Optimize for lower overhead and faster iteration

The first payoff of token efficiency is not even cost. It is iteration speed.

Smaller prompts are usually faster to prepare, faster to run, and easier to debug. When an interaction goes wrong, it is much easier to diagnose a focused request than a sprawling one that bundled task definition, architecture notes, temporary caveats, and half a design review into one heroic paragraph. Those prompts tend to age like milk.

### Use LLMs for the work they are good at

LLMs are valuable for synthesis, code generation, translation across representations, tool selection, and selective reuse of existing artifacts. They are less valuable as an expensive substitute for durable memory, deterministic validation, or basic automation that should already exist in scripts and pipelines.

If your model is spending tokens to rediscover stable facts about your system every few turns, you have an architecture problem, not merely a prompting problem.

### Manage context by managing scope

Large context windows are useful, but they are also a trap. A bigger window can hide poor boundaries the same way a larger server can hide an inefficient query. It works until scale, cost, or reliability makes the shortcut visible.

A better pattern is often smaller repository boundaries, clearer ownership, and an orchestration model that sends specialists only what they need. Fleet-style execution becomes more attractive under usage-based billing because it aligns cost with focused work. It also aligns failure domains, which architects should appreciate on principle.

### Write things down in file-based artifacts

This is one of the most useful practices in AI-assisted engineering.

Store the things that matter as files: interface contracts, workflow notes, migration rules, design decisions, operating constraints, acceptance criteria. Use them as handoff documents for humans and models alike. A good artifact reduces repeated explanation, shortens prompts, and gives future runs a stable point of reference.

We have seen this pattern before in service contracts, deployment runbooks, ADRs, and interface definitions. AI did not replace the need for those things. If anything, it increased it.

### Favor deterministic, auditable controls for trust

If a workflow must be safe, compliant, or simply reviewable, place as much behavior as possible in deterministic controls. Use explicit tools. Use templates. Use policy layers. Use sequential migrations instead of free-form improvisation when the change surface is sensitive. Keep access scoped.

Token efficiency and trust reinforce each other here. A deterministic control is often cheaper than a long prompt trying to persuade a model to behave. It is also easier to audit when something goes wrong at 2:17 in the morning, which is still when many architectural truths reveal themselves.

## What's Next

In Part 2, I will move from principle to design patterns: concrete ways to shape repositories, agents, artifacts, and workflows so token-efficient behavior happens by default instead of by constant human vigilance. That is where this becomes less philosophical and more operational.

For now, the main point is simple. Usage-based billing did not create token efficiency as a concern; it revealed it as one. Once engineers start changing how they think, structure work, and build controls around a resource, that resource is no longer just a line item. It is part of the architecture.

And architecture gets interesting when the scarce thing is no longer memory, bandwidth, or storage, but attention translated into tokens.

## References

- GitHub Blog, [GitHub Copilot is moving to usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)
- Ars Technica, [GitHub will start charging Copilot users based on their actual AI usage](https://arstechnica.com/ai/2026/04/github-will-start-charging-copilot-users-based-on-their-actual-ai-usage/)
