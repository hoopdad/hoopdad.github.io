---
layout: post
title:  "Token Efficiency: Which Loops are you Engineering? - Part 1"
---

Optimizing your token use comes down to a disciplined approach. It is easy
to start off with the right configurations and, by way of reacting to
how things are turning out, take a wrong turn down Overly Chatty Street, 
costing you a fortune in tokens.

This article is kind of a "Prequel" to the trilogy of articles I wrote
about Token Efficiency. After writing those and trying some more examples,
I have even more to share. Key takeaway: scope and clarity are royalty in 
the land of LLM context.

This article covers

- What is Loop Engineering
- What I Built
- Warnings

## What is Loop Engineering?

I'm co-opting the phrase Loop Engineering from what I've been reading on socials
lately. It's a good phrase for what I did here, which is different than 
prompt engineering or context engineering or even agentic workflows. I'm using it
to describe a semi-deterministic workflow with multiple different agents having
different scopes, skills, and jobs, working towards a common goal.

When I started this quest to make agents do big things, that phrase 
didn't exist. It's only in June of 2026 that it's becoming a phrase,
from one of the Anthropic or OpenClaw guys I think. I didn't do loop 
engineering the way Anthropic markets it though. And I took on a really 
ambitious goal that really stretch the limits of what agents can do.

![Diagram of a complex system of multiple agents with different jobs](/assets/2026/loop-engineering/loops-within-loops-v13-final-16x9.png)

The Product Owner and Technical Architect (AKA the people) collaborate on respective inputs: user flows,
personas, cloud requirements, security requirements, etc. They feed this into the agentic
flow and examine the final outputs. Ideally, steering, clarifying, and redirecting are
minimized. This saves clock time and tokens. 

> That graphic was a clean-up done by Microsoft Scout using a critic loop. It's 1,000,000 times better than my artwork, but taking the moment to call out another Loop use case.

### Feedback Loops: Good for People and Agents

I'm putting it up front here because understanding feedback loops with
agents is the number one lesson. A loop in the AI agent world can refer 
to many things, but is generally rooted in the concept of feedback loops: 
do something, get feedback from another perspective, incorporate feedback, 
get more feedback, and so on, until a goal is met.

### Other Kinds of Loops

I'm not talking about Ralph Loops, suffice it to say for now. There are some
understandings of the many ways that concept is wasteful. There may be valid
use cases. Just leaving that open for another day.

"Loop Engineering" as shared on socials the past couple of weeks usually 
refers to a specific "/loop" mode of Claude Code that will put your prompt 
into a feedback loop. The good idea out of this is to make these feedback 
loops more accessible to anyone. What I incorporated was a series of loops
that mimic the roles that specialist humans play in an Agile team: designer,
developer, tester, end-to-end architect, product owner.

A quick shout-out to "eval loops" as a good use of tokens in the right use cases.
These are the feedback loops used to automate changes to agents, fine-tuned models, 
and many other scenarios where it is beneficial to have an automated evaluation 
of impact of changes.

With this understanding of Loop Engineering under my belt, and soon
with your knowledge of it as well, we can all decide upon good and
practical uses of Agents to do work. Let's face it - we are responsible for 
both the cost of the tools and their outcome.

### A Warning About What You Produce

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

Another story I heard was about a person who wanted to enable access to their
functionality to the public internet but did not include rate limiters. That design
flaw, born of a good idea but incomplete information, left that developer open to
unlimited expenses if bad actors decided to mess with them and call that API over and over.
Or even well-intentioned people whose agents ran the work for them. Not inconceivable.

## What I Built

I built apps. Whole apps, deployed, securely in the cloud. Some of my tests
were mobile apps (iOS and Android), and one was an Alexa skill. All involved
complex authentication flows, with self-registration and profile setups. 
Most involved use of an agent as part of the runtime. Because they came with 
real costs and there wasn't a business plan to profit from any of them, I
took them down as quickly as they went up and were tested.

The apps I list below were among the many written between early April and mid June in my free 
time. About your free time, here's another warning: we should have a side conversation 
about the **dopamine effects and stress** that goes with managing agents. That compounds 
with the lack of sleep that comes with the urgency of keeping up with a rapidly evolving
technology landscape. Writing this is my knowledge consolidation and then I am taking 
a much needed summer break!

My approach was to write one or more requirements documents and queue up 
GitHub Copilot CLI with a specific prompt. As I learned more, I learned to use
more custom MCP tools, more Skills, more Agents with Agents running in parallel, 
and startup instructions. As an architect I was looking for repeatable patterns
so I could take what I built, i.e. a team of Agents, and bring that to another
project. I introduced a patterns repo with common requirements docs for these.

And one of the key learnings out of all of that is to ask Copilot to run a retrospective.
Specifically, ask Copilot to review this session or the past day's sessions or all 
the sessions for this repo, extracting learnings specifically to improve token 
efficiency and number of turns. What it tells you may be things that you never thought of.

For example, through this process Copilot generated tools as python programs plus `.copilot/mcp.json`, 
skills as `skills.md` in multiple skills folders, agents as `agents.md`, and 
instructions in `.github/copilot-instructions.md` so that 
they could be picked up automatically. 

I tried Squad, a multi-agent tool. I tried instructions sets for single orchestrator 
agent that managed all of it. I played around with `/fleet` mode but actually landed on a novel
mcp tool to launch agents. I tried queueing instructions with a standard prompt that made
it look like a sprint. I tried queuing instructions with boilerplate that reminded
the agents of their core instructions to follow. 

In almost every case, solutions for **saving tokens meant self-disciplined work** 
that I should do. The concepts of giving an agent optimal scope and real boundaries came up
time and again. This is where it looks like what human Agile teams go through: a focused
scope for a sprint gets a good result. But there's less teamwork after, so less Agile: 
agent team members had to stay focused on their work deliver the best outcome. Agents that
can wander through multiple repos for example will end up working in those repo in an ad hoc way.

### Word Game - Multi User Game

> **Multi-Repo** - **Agentic Workflow** - **Reminder Prompt** 

Here's a multi-user Guessing Game that I had the team build. It mostly worked. I did this one
as a "capstone" to this learning more than any serious effort, but used my best agents and skills.
And then I saw them need to improve even more throughout the course of the build.

![architecture diagram including Web Application Firewall -- React UI -- Python API with Cosmos DB   -- Python Agent with a Foundry-hosted Model](/assets/2026/loop-engineering/azure-container-apps-agent-architecture-32x9-v1.png)

![Word Game Screenshot](/assets/2026/loop-engineering/word-game.png)

### Team Brain - Knowledge Sharing

> **Multi-Repo** - **Fleet Mode** - **Sprint Prompt**

This was a concept to enable people to share information they gained, ask questions of others
who had that knowledge, using Cosmos as a graph database to connect ideas and an LLM to match 
synonyms.

![architecture diagram including Web Application Firewall -- React UI -- Python API with Cosmos DB including Graph/Gremlin API   -- Python Agent with a Foundry-hosted Model](/assets/2026/loop-engineering/azure-container-apps-agent-architecture-graph-gremlin-32x9-v1.png)

![Team Brain](/assets/2026/loop-engineering/team-brain.png)

### Marginalia

> **Single-Repo** - **Squad** - **Conversational Prompting**

I let AI name this one. Bad move. This was a concept that took a Copilot-like AI Assistant chat
and added annotations. "Margin" in "Marginalia" is where annotations could pop down to. It came
together remarkably fast.

![architecture diagram including Web Application Firewall -- React UI -- Python API with Cosmos DB   -- Python Agent with a Foundry-hosted Model](/assets/2026/loop-engineering/azure-container-apps-agent-architecture-32x9-v1.png)

![Marginalia](/assets/2026/loop-engineering/marginalia.png)

## My Hypothesis

Token efficiency is parts actual token usage and parts completion to goal.
My key hypothesis for all of this: a very complex initial prompt will either
succeed quickly, with the agents taking the ball and running with it to the 
goal line. Or it will lead to many wasteful interactions, steering back 
to the goal, clarifying, correcting. The latter, highly interactive model
will waste tokens.

I found measuring tokens to be very hard to do in interactive mode, and so 
honestly focused on my hypothesis rather than actually measuring
tokens. I could see my overall token usage, which included my day job and my hobby merged together. 
As my time went on, similar efforts and outcomes saw reduced 
overall token usage. But there were many factors including that day job thing. 
How similar were the efforts and outcomes would really be the key but is 
quite hard to measure without redoing the same project multiple times and 
very controlled usage.

## Next Up

I'll go deeper into each of these with examples of prompts I used,
agents, skills, and MCP tools. I want to share how important
solid software engineering remains with all of this, and that
you can do awesome things with the right expertise. Relying on 
AI alone for your business or livelihood is perilous.

## Token Efficiency Series

- [Token Efficiency - Part 1 - An Architectural Constraint]({% post_url /ai/2026-05-27-token-efficiency-part1 %})
- [Token Efficiency - Part 2 - Design Patterns]({% post_url /ai/2026-05-27-token-efficiency-part2 %})
- [Token Efficiency - Part 3 - An Operational Playbook]({% post_url /ai/2026-05-27-token-efficiency-part3 %})
