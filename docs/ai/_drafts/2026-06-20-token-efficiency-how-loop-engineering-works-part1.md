---
layout: post
title:  "Token Efficiency: Which Loops are you Engineering - Part 1"
---

To understand where agents are given "too much" is to understand how 
to optimize communication with an LLM. This is 100% connected to the 
token efficiency articles I've written, and was the basis for a lot 
of the learning I gained in writing those. In this
prequel series, I'm going to share 
how I got different versions of "Loop Engineering" work
with GitHub Copilot CLI, 
efficiency of different loops 
I am seeing and hearing about and whixh
are wasteful, plus lessons I gained from it.

This article covers

- What is Loop Engineering
- What I Built
- Warnings

## What is Loop Engineering?

When I started this quest to make agents do big things, that phrase 
didn't exist. It's only in June of 2026 that it's becoming a phrase,
from one of the Anthropic or OpenClaw guys I think. I didn't do loop engineering
the way Anthropic markets it though. And I took on a really ambitious
goal that really stretch the limits of what agents can do.

A loop in the AI agent world can refer to many things, but
is generally rooted in the concept of feedack loops: 
do something, get feedback from another perspectice,
incorporate feedback, get more feedback, and so on.
Earlier this year "Ralph Loops" were a big idea, but for most uses 
(not all) seem to
waste tokens as compared to letting a human put some 
upfront thought into it. I mean, their bumbling namesake Ralph Wiggum of The Simpsons
isn't exactly known for his thinking. Maybe Lisa (Simpson) Loops 
would offer potential if it exists.

Loop Engineering as shared on socials usually refers to a dpecific "/loop" mode
of Claude Code that will put your prompt into a feedback loop.
The good idea out of this is to make these feedback loops more accessible to anyone.

With this understanding of Loop Engineering under my belt, and soon
with your knowledge of it as well, we can all decide upon good and
practical uses of Agents to do work. Let's face it - we still own the
outcome. 

### A Warning about What You Produce

If you put out code written by an agent, you own it, are
liable for its malfunction, how it complies with laws like GDPR, and
cost of the deployment. Buyer beware - make sure you understand what
you are building and how to operate it. 

I'll give an almost comical
example about one "dangerous" thing I kept seeing: I had a strict rule,
repeated many times, to only use private networking, only use private IP
addresses, don't expose to the public Internet. I'm running it in a 
secured private cloud like an Enterprise would, for containment,
cybersecurity, and risk reasons. Yet, many times as I sent my agent
off on its way to troubleshoot, I would see, "I see the problem! Public
Networking is disabled. I will enable it now." Exactly violating one of my
key rules. Putting a critic agent, a red team agent, and an infrastructure
expert agent weren't enough when the coordinator agent was queueing up a plan.

![Enable Public Network Argument](/assets/2026/loop-engineering/enable-public-net.png)

## What I Built and About My Approach

I built apps. Whole apps, deployed, securely in the cloud. Some of my tests
were mobile apps (iOS and Android), and one was an Alexa skill. All involved
complex authentication flows, with self-registration and profile setups. 
Most involved use of an agent as part of the runtime.

The apps I list below were written between early April and mid June in my free 
time. Another warning: we should have a side conversation about the 
**dopamine affects and stress** that goes with managing agents. Writing this 
is my knowledge consolidation and then I am taking a much needed summer break!

My approach was to write one or more requirements documents and queue up 
GitHub Copilot CLI with a specific prompt. As I learned more, I learned to use
more cutom MCP tools, more Skills, more Agents with Agents running in parallel, 
and startup instructions. As an architect I was looking for repeatable patterns
so I could take what I built, i.e. a team of Agents, and bring that to another
project. I intorduced a patterns repo with common requirements docs for these.

And the key learning out of all of that is to ask Copilot to review
this session or the past day's sessions or all the sessions for this repo, and
extract learnigns specifically to improve token efficiency and number of turns.
It generated tools as python programs plus `.copilot/mcp.json`, 
skills as `skills.md` in multiple skills folders, 
agents as `agents.md`, 
and instructions in `.github/copilot-instructions.md` so that they could be picked up
automatically. I played around with `/fleet` mode but actually landed on a novel
mcp tool to launch agents. I'll explain why in a later article.

In almost every case, solutions for **saving tokens meant self-discplined work** 
that I should do.

### Word Game - Multi User Game

> [!NOTE]
> **multi repo**
> **multi agent**

Here's a multi-user Guessing Game that I had the team build. It mostly works.

![architecture diagram including Web Application Firewall -- React UI -- Python API with Cosmos DB   -- Python Agent with a Foundry-hosted Model](/assets/2026/loop-engineering/azure-container-apps-agent-architecture-32x9-v1.png)

![Word Game Screenshot](/assets/2026/loop-engineering/word-game.png)

### Team Brain - Knowledge Sharing

![architecture diagram including Web Application Firewall -- React UI -- Python API with Cosmos DB including Graph/Gremlin API   -- Python Agent with a Foundry-hosted Model](/assets/2026/loop-engineering/azure-container-apps-agent-architecture-graph-gremlin-32x9-v1.png)

![Team Brain](/assets/2026/loop-engineering/team-brain.png)

### Score That Job - Resume Scoring and Editing

![architecture diagram including Web Application Firewall -- React UI -- Python API with Cosmos DB   -- Python Agent with a Foundry-hosted Model](/assets/2026/loop-engineering/azure-container-apps-agent-architecture-32x9-v1.png)

![Score That Job](/assets/2026/loop-engineering/score-that-job.png)

### Marginalia

I let AI name this one. Bad move.

![architecture diagram including Web Application Firewall -- React UI -- Python API with Cosmos DB   -- Python Agent with a Foundry-hosted Model](/assets/2026/loop-engineering/azure-container-apps-agent-architecture-32x9-v1.png)

![Marginalia](/assets/2026/loop-engineering/marginalia.png)
