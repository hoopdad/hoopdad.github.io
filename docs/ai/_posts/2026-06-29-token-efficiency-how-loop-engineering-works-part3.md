---
layout: post
title:  "Token Efficiency Lessons From Loop Engineering Part 3"
---
This is a deep-dive with plenty of screenshots. I'm writing to consolidate
my knowledge on this topic and share with you what I am learning so we can collectively 
understand the technology better from every perspective.

I'll start with the analogy to human teams, and jump into a loop of loops I used to
get high quality results in my experimentation, and then show what it created. I will 
wrap up with some takeaways.

And while my goal remains a single prompt to build and deploy an application, this was 
not the Holy Grail you were looking for. It came close but ran into a couple of blockers
along the way. These required my specific knowledge of my own environment and the recognition
that it is very hard to write a single spec with every conceivable parameter defined.

![graphic of different specialties focused on one problem](/assets/2026/loop-engineering/teammates-shared-goal_16x9_web596.png)

## The Power of Agentic Teams And Fleet Mode

An Agentic Team, a team of agents, is not a team of the generalist, do-it-all agent. This
concept is to steer a particular session with a point of view. Each subagent gets its own session
in Fleet Mode, so your context does not get biased with predecessor work instructions. It is
examining the output and comparing it to the instructions. Because it does not share instructions,
it is basically getting a fresh set of eyes on the project.

### Using Human Teams as a Model

We know this works when people come together, assuming civil behavior of course. "This will
work well" and "this won't work" are statements made when people have the benefit of experience
in a specific context. A given situation, whatever it is, looks like something that some or all
team members have experienced. When people in this situation remain focused on the goal and less 
on ego, the alternative thoughts encourage people to think differently.

Likewise, an agent can be a specialist or a generalist. The specialist can be instructed to 
prioritize best practices from Cyber Security for example. When reviewing work done by a
Cloud specialist whose priority is optimal cost and function of a way to run code, Cyber best
practices can reveal ways that the solution would fail. And both perspectives are needed
for success. The specialist critic doesn't distinguish between another agent's work and what
another agent or human did. It is just judging the work against the required criteria.

Starting with my requirements, each specialist builder agent comes with its own best practices. 
I enlist specific kinds of evaluations to make sure that various perspectives are considered
in the final result.

- Designer Agent focuses on what the product looks like and how a user flows through it. The architect and developer agents get feedback on this.
- Red Team Agent focuses on cybersecurity. I don't just want a system design, I want a secure system design, and the Red Team does, too.
- Critic Agent provides critical thinking to the requirements, and if the rest of the team can answer all those probing questions.

### Agile Workflows Enable Diverse Thinking for Best Results

I'm taking a position on that. I've seen it. A human team with diverse skillsets and diverse
backgrounds brings more comprehensive thinking to problem-solving. And an Agile product team,
composed of individuals who bring best practices and novel ideas of their own, challenges the
others towards a solution that stretches each person. A great web designer will challenge
a web developer to stop using a certain library because it limits accessibility, even though
it checks all the requirement boxes in the developer's primary focus. An API engineer will
have to work with a UX designer to get the best user flow, not the easiest API code to manage.

### The Loop of Loops

![Diagram of a Release Loop with all the incumbent inner loops](/assets/2026/loop-engineering/release-loop-serpentine-v2.drawio.png)

This is a workflow that many Agile teams in Enterprise technology might use. Every stage has a
gate, and a party without a conflict of interest can fairly judge the work using the required
criteria. Getting that encoded in YML was a lot of typing up front, but I type fast, thanks 
to Mrs. Schlessinger's 9th grade typing class.

I created this as a human-readable YML file. Realizing that this would go in with every request
made by the top level agent in the harness, I wanted it to be more concise, so I worked with
GitHub Copilot CLI to make it smaller. I edit [`loop.yml`](https://github.com/hoopdad/thought-connections/blob/main/loops.yml){:target="_blank"} , then run [a script](https://github.com/hoopdad/thought-connections/blob/main/compact.sh){:target="_blank"}, and it produces
[`docs/requirements/compact-loop.yml`](https://github.com/hoopdad/thought-connections/blob/main/docs/runbooks/compact-loop.yml){:target="_blank"} . It saves about 20% of the text, so a direct 20% token
savings. I created a simple YML DSL for this purpose, but it's typical for what you would
put into a workflow.

### Instructions to Copilot

My instructions to GitHub Copilot CLI had to be concise and not contradict anything in the other file.

```yml
 Before repo work, read this file and `docs/runbooks/OPERATOR_RUNBOOK.md`.

- Begin by understanding workflows, entities, and roles in `docs/runbooks/compact-loop.yml`
- Immediately next, begin work with workflow [ReleaseLoop] in `docs/runbooks/compact-loop.yml`
- When in Fleet Mode, use subagents as defined in `docs/runbooks/compact-loop.yml`
- Optimize subagent scope without wasting tokens while getting highest quality work
- Launch subagents with exactly the amount of context they need, no more and no less
- Monitor all parallel work and restart if hung or stopped unexpectedly
- Follow the runbook for the detailed workflow and quality gates
```

That's it. Copilot thinks it's too short, but it ends up working. Then the runbook. 
Here's the link to that: [Operator Runbook](https://github.com/hoopdad/thought-connections/blob/main/docs/runbooks/OPERATOR_RUNBOOK.md){:target="_blank"}
It's not very long, but too much to paste here. It gives a "Critical Operating Mode"
and "Sub-agent workflow" that defer to the Loop YML file.

It followed the instructions remarkably well. Here's the caveat: if it does stop in the 
middle of a flow due to some insurmountable problem, it won't automatically pick up
after that blocker is removed. You have to coach it, steer it back on track. 

### The Prompt

Here's how I kick it off. 

> /fleet You are now in fleet mode. Follow .github/copilot-instructions.md and deliver the MVP of this product. Assess current status and begin or continue. Then per docs/runbooks/OPERATOR_RUNBOOK.MD iterate loops until all sprints are completed and all features, functions, and requirements are complete. Fan out and bring this product to life!

`/Fleet` triggers GitHub Copilot Fleet Mode, which is designed to launch subagents
in separate execution threads for parallelism and separate LLM sessions to optimize
context. I am reminding it to follow instructions - that seems necessary based on past experience.
And the entry point being a "Release Loop" is a key to starting it off in the right place.

That's it. Copilot thinks it's too short, but it ends up working. Then the runbook. 
Here's the link to that: [Operator Runbook](https://github.com/hoopdad/thought-connections/blob/main/docs/runbooks/OPERATOR_RUNBOOK.md){:target="_blank"}
It's not very long, but too much to paste here. It gives a "Critical Operating Mode"
and "Sub-agent workflow" that defer to the Loop YML file.

## What I Built

I spent some time on requirements. And that's the point of all this right? Our expertise and
vision guides AI to meet our goals. It's not thinking or dreaming for us. The difference between 
frustrating hours of turns of deployment fixes and a smooth one-shot send-up is an hour of
defining requirements.

I identified [user flows and system requirements](https://github.com/hoopdad/thought-connections/blob/main/docs/requirements/system-def.md){:target="_blank"} to be able to deploy it in my controlled 
Azure cloud environment. If you look in [tier-specific requirements](https://github.com/hoopdad/thought-connections/blob/main/docs/requirements/https://github.com/hoopdad/thought-connections/tree/main/docs/requirements){:target="_blank"} you will see more requirements
that were intentionally parcelled out in smaller chunks for context management reasons.

I created a script for a non-interactive run of GitHub Copilot CLI, [`go.sh`](https://github.com/hoopdad/thought-connections/blob/main/go.sh){:target="_blank"}

Everything else in that repo was generated as a result of these files!


## What It Created

This was a fairly complex application with many moving parts: a graph database, a NoSQL database,
an LLM, an agent, an api layer, a web layer and a Web Application Firewall (WAF) to sit in front
of all of it.

### The App

![screenshot of graph](/assets/2026/loop-engineering/graph.png)

This is the centerpiece. Using AI to match similar concepts, then connect them in a Graph Database,
then present that visually to a user. It gives the user the ability to move around the nodes to 
find insights.

![screenshot of dashboard](/assets/2026/loop-engineering/dashboard.png)

This hypothetical use case is about knowledge sharing. You have a call on a topic and share details
about it with a customer, then log it here. The next time someone has a question about a related topic
they can reference your notes.

### The Architecture

![System Architecture](/assets/2026/loop-engineering/thought-connections-architecture-v8.drawio.png)

The Azure environment I work in has strict security policies, so this architecture required 
intentional configuration.

- A Web Application Firewall (WAF) as a security layer to minimize impact of a breach.
- Azure Container Apps with ingress from other containers only for most, but from the VNet for the WAF as the single entry point, using a Private Endpoint.
- A Cosmos DB for NoSQL, with a Private Endpoint.
- A Cosmos DB with Gremlin API for graph database capabilities, with a a Private Endpoint.
- A spoke vnet that attaches to the existing Hub for routing over a VPN.
- Entra ID authentication required for the application.
- Managed identities and RBAC assignments for all the above components to use for authorization to communicate with each other.

## Conclusions about Token Efficiency

### Methods for Conserving Tokens

I used **compact files for core instructions**. I wrote out the YML for my workflow, 
and saw that it was quite verbose, out of necessity for clarity's sake and maintenance. 
But I also know that an LLM can translate things and use abbreviations to save on tokens. So I 
created the verbose one, and had GitHub Copilot write a script to translate it 
to a form that kept to the spirit and letter
of what I intended but took 20% less space. Basically, it used acronyms with a glossary. 
That reduced repetition by putting my parenthetical blabbering into that glossary. 
The net impact is that the compounding 
of the instruction set started at that 20%, which yields far more than 20% in the end.

By providing **written requirements**, and then having a phase where the agentic team wrote 
and validated deeper requirements as **persistent files**, we use more cached input tokens 
than if we were prompting with natural language at every turn. Cached input tokens are much
cheaper. And, we have the added value of making per-agent instructions, so they only get
the exact amount of requirements docs (fewer tokens again) that they need for the task. 
For example, the infrastructure agent doesn't need the color scheme on the web design, so 
that can stay out of its context. And, there theoretically are fewer turns due to more
accurate requirements with findings up front in the design stage.

### ROI and Value

This method led me to the fewest interactions of experimentation I've done to date.
I spent less time standing at my computer waiting to answer the next prompt.
I typically have been running experiments most days of the week for the past few months, so while it's 
experiential and not totally scientific, it is a reasonable conclusion to say, this method 
produced results that are really good. In
my earlier iterations with this before landing on the yml loop method, I saw some
really lousy screens and flows that didn't make sense before I added the loops.

**This is where the ROI conversation has to happen.** It used a lot of tokens, yes, but it also produced
the highest-quality product in terms of user experience and infrastructure deployment. Budgets are real,
and delivering value to our customers is also real.

A judgement call or a framework for scaling purposes could help with that. 
If I tie back to Agile, I would say that, just like Agile itself, Token 
Efficiency is focused on delivering optimal customer value. Optimum does not 
always mean maximum, so it leaves the door open for those judgement calls. 
Is it worth spending a higher amount of tokens for a little utility I'm writing for myself? 
Is it worth spending a higher amount of tokens for faster GTM and a better overall look?
I think you can tell a loaded question or two when you see it.

More to come - please let me know if this is helpful, if you want to steer me away 
from some conclusion above or you have ideas to share!
