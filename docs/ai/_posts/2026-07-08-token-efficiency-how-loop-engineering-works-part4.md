---
layout: post
title:  "Token Efficiency Lessons From Loop Engineering Part 4"
---

![relationship between agents, skills, tools, instructions, and github copilot cli](/assets/2026/loop-engineering/github-copilot-cli-ecosystem-wide-32x9-v3-final-preview.jpg)

## Learning about AI from AI

This is a deep-dive with plenty of screenshots, code examples, and links to repos.
I'm writing to consolidate my knowledge on this topic and share with you what 
I am learning so we can collectively understand the technology better from every
perspective.

Efficiency comes from expertise with a tool. AI tools come built in with
ways to answer your hardest, most thought-provoking questions. Ask AI how
to use it more efficiently and it will not only teach you, it will build the
tools you need to use. And install them. I used more loop engineering in this
experiment. But the real story is about using AI to learn about AI to be 
more efficient (and save tokens).

**End of series bonus:** check out a self-teaching trick I've started doing that I 
share somewhere mysteriously in this post. Possibly the end, but I wouldn't leap 
to conclusions.

## Customizing Agents, Skills, and Tools for Token Efficiency

GitHub Copilot CLI has great support for Agents, Skills, and Tools. It has a 
built-in mechanism for core instructions. These are critical for efficiency
and I'll explain why.

Let me lead with kinds of problems that inefficient use leads to.

### Shelling Out

![when copilot shells out](/assets/2026/loop-engineering/shelling-out.png)

Above you can see repeated calls labeled with the prefix `Shell`. The newest version
actually makes it more obvious with caps: `[SHELL]`. It's
all caps - gets your attention, right? This means the agent harness, Copilot,
had to not only figure out what command to run, but then execute it, wait for
and interpret results. Ok, big deal, right? Well, when you repeat the same
things over and over, it is. It doesn't remember. Each one of those stages 
costs tokens. Ouch.

### Weak DevOps Practices

![repeated painful errors](/assets/2026/loop-engineering/repeated-errors.png)

Here's a more complex use case. You don't know by looking, but I watched it
many, many times create a container with errors, then wait while it takes
ages to delete. It will start to pause itself: `"Waiting up to 180 seconds
for shell output"`. That's 3 minutes of idle time. Then 3 more and 3 more,
because this particular deletion process just takes a long time. There are
multiple options to minimize these chances, such as working with a local
Docker image, more tests, more lint. And we can build that DevOps expertise
into our process.

## Agentic Engineering

We have to use the hooks that GitHub Copilot provides to get efficient. We
have to engineer the way to get to the solution. Otherwise it's just vibe coding.
I knew about these but in my night-time, after-hours work, I didn't feel I 
had the time to write out Agents, Skills, and Tools. By the end of it, 
I wished I had. But I did come up with a solution that taught me more about AI
and Agents, and ended up lessening these repetitive, wasteful issues.

### Skills

Here's a snippet of a Skill that I used. I'll tell you how I used AI to create
it and how I used AI to orchestrate setting up and installing these in the right
places.

```md
---
name: container-app-troubleshoot
description: Diagnose and fix Azure Container Apps deployment failures — activation failures, image pull errors, crash loops, health probe failures, and ingress misconfigurations. Use when container apps show "Activation failed", replicas won't start, or deployments aren't healthy.
---
# Container App Troubleshoot Skill

## Purpose

Use this skill to systematically diagnose and remediate Azure Container Apps
deployment failures. It uses the `container-app-diagnostics` MCP tools to gather
evidence, then applies a structured triage process to identify root causes.

## Invoke When

Use this skill when the user mentions any of:

- "Activation failed" on a container app
- Container app not starting / not healthy
- Deployment failed / deploy not working
```

The full skill is in a repo I made public, 
[enterprise fleet controller repo](https://github.com/hoopdad/enterprise-copilot-fleet-controller/blob/main/skills/container-app-troubleshoot/SKILL.md){:target="_blank"}

It might work in your environment. But likely you will need to do what I did,
at least at first, and almost manually adjust for each project.

Open a session in Copilot CLI. And prompt it something like this:

> Examine the skill in https://github.com/hoopdad/enterprise-copilot-fleet-controller/blob/main/skills/container-app-troubleshoot/SKILL.md
> Examine what it does to understand its intent. Adapt it for my specific 
> environment and requirements. Then install it in this repo in the 
> standard place where GitHub Copilot CLI will be able to find it and load
> it when needed. Examine my session history to understand how to make it
> most efficient for me.

I can just about guarantee you that it will make substantial edits, because
it is fairly finely tuned to a specific set of environmental requirements and constraints
that aren't the same as yours.

Here's the take-away: given an intent, it can figure out how to write code.
Given an intent to make your environment more efficient, along with the 
understanding of how you have been prompting and interacting with it, it will
write code that will save you tokens.

### Agents

Let's dial in to the work product of your agent. It's a generalist and can do
anything, 999 different ways. But, you as the visionary architect want it to
work a certain way. And you know things that you haven't been able to put on
paper because there are so many things! But use an Agent to dial that in, and 
get the core instructions down on paper.

Here's an example snippet from a companion Agent used 
in the same project as that skill. But I can't share the definition with 
you because it was dynamically generated by another agent. More on that 
later.

```md
---
name: word-game-api-specialist
description: "Backend specialist that implements and validates FastAPI + Azure SDK changes in word-game-api under contract and guardrail constraints."
tools: ["scaffold-generator", "lint-local", "contract-compliance", "security-scanner", "usage-tracker"]
---

You are the backend specialist for word-game-api (../word-game-api).
...
## Your Scope
- Repository: ../word-game-api
- Stack: Python 3 / FastAPI (src-layout package `word_game_api`) with Azure SDK; managed via pyproject.toml, linted with ruff, tested with pytest
- Validation: `ruff check . && pytest`
```

This puts constraints on the agent so it names a number of things.

- For API, use Python with the FastAPI package. What it won't do is invent its own library or use an obscure language that doesn't have the libraries you want, so later re-do all the work in a language that does have the libraries you want.
- Tells it how to validate the code.
- Implies that it needs to be writing tests.
- Tells it where its working directory is, and confines its scope to that. Don't let your agents wander throughout all your repos because they will change things to make their own work easier.

It's a back-end specialist. This steers the model to prioritize
skills and best practices of a back-end specialist, not a general linguist.

### MCP Tools

The agent definition above mentions tools. These are MCP Tools, and by including
them in your instructions you infer specific ways to do tasks that reduce token usage.
These are general tools, and the agent needs to figure out what the values 
of the parameters are, but it doesn't have to figure the whole thing out. And it
will do this thing consistently.

Here's an example of a set of tools. The first one is for comparing work that an 
agent implemented to what the orchestrator agent designed for it to do. If it 
doesn't match, the specialist agent didn't do its job, and has to go back to fix 
it. But it's a basic comparison that doesn't require an LLM and tokens to figure 
out. There are some about figuring out what's wrong with a resource in the cloud.
It's not a task that needs the power or tokens of an LLM. 

```md
    "contract-compliance": {
      "description": "Compare implemented routes to .contracts/*.yml endpoint definitions.",
    "scaffold-generator": {
      "description": "Generate non-overwriting FastAPI/TypeScript stubs from contracts.",
    "azure-inspector": {
      "description": "Read Container Apps, Cosmos DB, and ACR state via Azure CLI.",
    "container-app-diagnostics": {
      "description": "Deep troubleshooting for Container Apps \u2014 diagnose activation failures, pull logs, inspect revisions/replicas, verify image pulls, compare app configs.",
    "azure-resource-status": {
      "description": "Inventory Azure resources and inspect status/error events for troubleshooting.",

```
These are available in that same repo: [Enterprise Copilot Fleet Controller Tools](https://github.com/hoopdad/enterprise-copilot-fleet-controller/tree/main/tools){:target="_blank"}

## Agentic Engineering Patterns

### Prompting for More Efficient Ways

Ok, so I had to take it one step further. I built Agents, Skills, and Tools 
by prompting copilot to build them for me. Something like:

> Examine the past session of building this application. There are many 
> inefficiencies in this approach. Look through all the calls to SHELL,
> the repeated effort, the steering and corrections that I made through
> prompting. Identify Agents, Skills, and MCP Tools that can make my efforts
> more efficient in this project. Build those and save them to the places
> where copilot will find them. Make the MCP tools run on local python servers.

And so it went off and cranked through and built me a project's set of
efficiencies. And then I had to prompt again because it needed core instructions,
like `.github/copilot-instructions.md` to follow the Agile workflow that I 
wanted it to use. (And later, loops.)

Great. One project done. But I had to build that project to be able to find
out how to more efficiently build that project. See the catch-22 there? Tokens: spent. Lessons: learned.

### Make a generic framework for building Agents, Tools and Skills

Then I got the idea that, if copilot knew the stack I wanted to use, and
common problems I would face, it could actually proactively build those
instructions, Agents, Tools, and Skills. And there could be some re-use
across similar projects.

I defined a stack which I cleverly named
[Azure Full Stack](https://github.com/hoopdad/enterprise-copilot-fleet-controller/tree/main/patterns/azure-fullstack/pattern.yml){:target="_blank"}

Basically the pattern describes the tiers to use, and the tech stack in each tier.

With that pattern, a simple program - not a full LLM prompt - can start to dish out
new directories and repos, and start to do some configuration. Though, it was
only when I was able to use a non-interactive prompt inside a shell script
that I could scaffold a repo. I could have used templates. Maybe I got lazy.
But this generated code is using elements of the full stack, so that
later in the shell script, another non-interactive prompt could custom
build the agents and pull in Skills and Tools specific to that repo.

It's a very lengthy script, but [init-core.sh](https://github.com/hoopdad/enterprise-copilot-fleet-controller/blob/main/scripts/init-core.sh){:target="_blank"}
does all of this. The end of the init story is below.

```sh
═══ Phase 6: Running initial Copilot prompt ═══
  → Installed child MCP config into word-game-waf/.github/mcp.json
  → Installed child MCP config into word-game-web/.github/mcp.json
  → Installed child MCP config into word-game-api/.github/mcp.json
  → Installed child MCP config into word-game-agent/.github/mcp.json
  → Installed child MCP config into word-game-infra/.github/mcp.json
  → Installed child-scoped MCP config into 5 child repo(s)
  → Running orchestration preflight checks...
  → Preflight debug: shell_cwd=/home/mike/source/word-game/word-game-harness
  → Preflight debug: target_dir=/home/mike/source/word-game/word-game-harness
  → Preflight debug: mcp_enabled=true mcp_config=/home/mike/source/word-game/word-game-harness/.github/mcp.json
  → Preflight debug: mcp_servers repo-index=yes child-agent-runner=yes usage-tracker=yes
Installed skills into:
  /home/mike/source/word-game/word-game-harness/.github/skills

Installed selection:
  hub-skill

Source repository:
  hoopdad/infra-skills@main

Next steps:
  1. Confirm the skills under /home/mike/source/word-game/word-game-harness/.github/skills
  2. Open Copilot Chat in the target repo
  3. Invoke the installed skill by name
```

This will run for any project now, though a new pattern might need to be defined for
new stacks. And, more skills and tools might come along and be useful.

Now I have a more efficient way (saving more tokens) to scaffold not only the code
of my projects but skills, agents, tools, and instructions.  Try this out 
and let me know if you have luck with it. Feel free to fork and PR for updates! 

Repo: [Enterprise Copilot Fleet Controller](https://github.com/hoopdad/enterprise-copilot-fleet-controller/tree/main){:target="_blank"}

## The Project to Prove It Out

Well, this capstone was a beast. I ended up refining [the requirements](https://github.com/hoopdad/word-game/blob/main/system-requirements.md){:target="_blank"} many, many
times as I designed complex user flows in a multi-user collaborative environment.
Not trivial. I had AI rewrite them, only to then not understand what it did, and I
tried to back out, so it's a little ugly. The longer the requirements, the
greater the chances for ambiguity and even conflicting requirements. As this
run is wrapping up, literally as I type this, I am telling Copilot yet again,
"No public IP addresses are allowed. Why did you give the WAF a public IP?"
So I can adjust the requirement and see where I was not clear or gave conflicting
requirements. (Some WAF patterns are intentionally public, filtering traffic to
protected servers, so I see the confusion.)

Eventually it built. I shared the screenshot on the first post, and it was mostly
working. Now I'm re-doing it, applying new learnings to see if it goes better. 
The jury is still deliberating and the agents are still looping. I will update here
when it is finally done. I am eager to wrap this up and think the main points
have been taken.

The learnings about efficient use of AI are real.

## Bonus Learning

This was about using AI to learn about AI. As I continue to learn how best
to use AI to support my business—a.k.a. my real job—I came across a useful concept.
With a maturity matrix, and deep understanding of how I use AI, AI itself
can judge me and tell me where I fall on that maturity curve. 

Here's the learning for you. Open the harness you use most often: Scout, 
GitHub Copilot, Claude Code, Codex, whatever. I run this analysis based on 
the maturity curve written by [Every](https://every.to/){:target="_blank"} . 

> Based on everything you know about me, including memories, tools and skills installed, and past session history, what level would you say I’m at on this guide to AI adoption levels? https://every.to/guides/the-eight-levels-of-ai-adoption

It will judge you. Breathe. You might not like the answer, but 
you can handle this. It may understand that you are asking so that you can
improve and start to give you suggestions. If it doesn't, follow up.

> What would take me to [the next level up]? How can I use you more effectively? What opportunities did I miss?

This is about taking your use of AI to the next level. It may or may not cost
you more tokens, but you will definitely learn how to squeeze more value out of
AI.