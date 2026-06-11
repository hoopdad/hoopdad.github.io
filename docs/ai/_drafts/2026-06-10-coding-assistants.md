---
layout: post
title: "Coding Assistants - Part 1 - Decisions, Capabilities, and Expertise"
---

The technology world has turned to AI coding assistants. It's here, it's not "going" to happen because it already has. Enterprise leaders need to make decisions about who, what, how, and why. You know, the usual suspects of any major decision. This is timely because one of the leading AI model companies recently announced that 80% of its code - critical corporate assets, its very lifeblood in that industry! - is written by AI.

In this post, part 1 of 3, I'm sharing capabilities, limitations, and perspective on effective management and usage of these tools. Subsequent posts will show the 3 patterns I worked out and what wrangling an AI assistance looks like in practice.

## Teeing up with Individual Capabilities

Let's lay out some of the speciic capabilities the tools have, then in the next section implications for putting them all together. This section is level set with those who haven't worked much or at all with these tools.

First, you'll see that I am using AI Coding Assistant and various AI agents interchangeably in this conversation. Most of the time here, the capabilities I describe go beyond "an assistant" into  specialized agency - software doing things with knowledge and intention.

AI coding assistants can write code, sure. No sweat. Code is just language after all, and these assistants are backed by some serious large language models (LLMs). The perspective I'm sharing is that we define far more than web pages with code: back-end API's, cloud infrastructure, security policy, network configurations, and even other agents. In other words, any thing in your technical environment that is expressed in a formatted file, or connected to with an API or tool, is fair game.

So let's bulid on that, because these are first class agents. They run tools. Tools exist for just about all of the functions of modern platorms: clouds, databases, issue tracking systems, quality testing. And some tools are smart enough to work from screens where tools don't exist. Coding agents can be permitted to run these. 

With enough of a clue for input, ai coding assistants can even design end-to-end flows. Based on established patterns written about by dopes like me sharing all their knowledge for free, an LLM can figure out all the system components needed, the roles for each component, and how they wire up together. 

I'll tack on "follow instructions" as a capability, though this is where it can get a little wild. These tools are built to start up and look for instructions files as their guide. Instructions can steer the flow of events, that code must be tested before going to the next step, to log all decisions to a file, to always keep a regression test when a bug is found. Compliance depends on how well aligned the instructions as written are to the tasks the assistant encounters. Well-written isntructions will fire when the same thing happens in different contexts. For example, always write a regression test when a bug is fixed, but do you mean bugs that you find or the assistant finds or both?

## Putting Capabilities Together

You probably have already connected the dots, so I'll sum this up. 

1. Give the ai coding assistant rules and procedures.
2. In a standard way, tell your ideas to AI as flows of interactions between a user and the system.
3. AI does the technical design and parcels out work between code repositories, one per layer.
4. A Red Team agent iterates with AI to identify cyber security risks and fix them.
4. AI builds and tests based on the specs.
5. A critic agent validates that the coding agent actually did what it was supposed to.
6. A deployment agent deploys each repo: cloud, api, web, etc.
7. AI assesses log files for positive and negative feedback.

Shout out to some keywords that have big meaning:

- Red Team: this is from cybersecurity, and means a team that finds cybersecurity issues and resolutions or mitigations to them. Having an iterative loop with a Red Team Agent and a Designer Agent hardens a design to reduce cybersecurity risks. 
- TDD: Test Drive Development. This little buzzword makes your coding agent design the test before it writes the code. In real life, this was to keep us from skipping over automated testing and had the amazing benefit of speeding along delivery because the target and ambiguities were better understood.
- Critic: A Critic agent evaluates what something should be versus what it is, and provides that candid, direct feedback like it wants a podcast.
- Infrastructure as Code (IaC): instead of issuing ad hoc commands, using IaC lets LLM's use language to define cloud resources, and then use basic tool execution patterns to deploy your stuff.

## Examples of Things I Built

Over the last couple of months I have been zealously figuring out how best to work with these tools as if I were writing Enterprise or commercial software. But I didn't write any code, not a line. That was the test: can GitHub Copilot write code that maintained high quality, adhered to standards, took actions that were traceable and auditable, and follow a logical workflow? Yes. Not to understate, but yes! It takes a good manager, but yes. It was exhausting with 15 minute follow-ups rather than the dailiy standups a people manager would have, but yes. 

My role in this was to set up coding assistants to do the work. What I did:

- Communicated the flow from the user perspective
- Wrote system requirements and made the assistant refer to them
- Setup tasks with no tools like log in to Apple and Google developer sites
- When there was a problem and AI couldn't fix it quickly, reviewed code and log files, then steered AI

The outcomes varied from fully functional to almost-there but break-fix loops til I stepped back to look at my approach.

- An application that translates natural language into math formulas, then runs it and tunes for efficiency (web firewall, website, agent, tools)
- An application that analyzes a resume against a job description, rewrites it in the language of the target employer (web firewall, website, android app, api, database, agent)
- An application that remembers what TV shows I was streaming (web firewall, website, android app, alexa integration, iOS app, database)

## Abstractions

More than any software development lifecycle I've done, this lends itself to end-to-end automated workflows. It pushes back to the left and out to the right. 

I created 4 reusable frameworks for different scenarios I found. I kept iterating and they kept getting better. They are rough and at a minimum I will share concepts but not likely reusable in their current state.

1. For a small app, with a single repository, maybe this would be a script. Define the sprint in `.github/copilot-instructions.md` and tell it to follow `OPERATOR_RUNBOOK.md`. Prompt it with some boilerplate with sprint goals and acceptance criteria, as if you were an Agile scrum master.
2. For an app with multiple repositories, one per layer, what I called the Enterprise Copilot Fleet Controller. One agent coordinates and designs and has only access to design and work items. Many specialist agents write code and deployment procedures. Critics everywhere like in real life keep them in check.
3. An alternative for an app with multiple repositories, one per layer: a parent repository tracks the layers' respositories as git submodules and has access to read all of them. Keeping scope limited for token count reasons was challenging. I found that the coordinator agent tended to micromanage, doing work itself instead of delegating. Costs to this are to quality and effort - with that much scope the coordinator would get overhwhelmed. (Any managers in the room right now, feeling that?) But it churned through many sprints successfully before falling down.
4. Custom workflows. This is not really working yet. I had AI design and write it with workflows that I delivered, but implementing all the details in this will take more time. Not there yet but offers deterministic gates that give temporary control to indeterministic agents.

## Human Expertise

Projecting what I found in my experimentation into the real world uncovers roles and skills that become even more important. With these skills, ideas will take off very quickly, like you wouldn't believe. Those without these skills will be spinning in circles and wasting tokens.

- Vision casting: this kicks off the whole process. The clearer it is, the faster it comes to life
- Written communication: concise language and removing ambiguity are step 1. Understanding how AI will receive that communication and what it does with that is key here. And understanding that AI can read structured formats easier than prose.
- Software tooling: run code, format it, test it, deploy it, check for vulnerabilities. How to trigger these at the write time without having your AI design it from scratch each time saves a kingdom of tokens.
- Gathering feedback systematically from users and the system itself, to feed improvements and fixes.
- Managing scope: start with a clear definition and checking back to make sure we're still on that. Making sure we limit scope of our agents' memories and processing abilities systematically, in ways very similar to how we do the same for our human developers.
- Software integrations: understanding how components wire together is key to making sure the system is thinking about flows correctly, and being the real big brain when it finds  bug it can't troubleshoot. Enabling self-diagnostics comes from this skill, too.

## Where to Put Your Money Right Now

This is what I see the tech doing very well, and I boil it down to language skills.

- Writing code. Putting the "language" back in programming language. A natural for python, HTML, but also Terraform.
- Gap analysis or critical analysis. Believe it or not, it's pretty good. Try it with your personal AI assistant and ask what you're doing wrong. Based on the data you've given it, it'll let you know.
- Technical flow design. How data flows from a screen to an api to a database with different names and structures is handled well, as long as you instruct it to be systematic.

The skills I highlighted above aren't necessarily part of any single current job description. There are more soft skills, imagination, and abstract thinking, needed now. But also the fundamentals of software engineering are more important than ever. Someone will invent a new way to get from idea to deployment, in a new shape that doesn't exist yet, but, we're not there quite yet.
