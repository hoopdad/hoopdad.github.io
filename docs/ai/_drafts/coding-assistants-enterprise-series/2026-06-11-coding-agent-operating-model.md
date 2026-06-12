# The Operating Model: Rules, Agents, Critics, and Deployment

![Managing AI Coding Agents in the Enterprise](/assets/2026/coding-agents-enterprise/managing-ai-coding-agents-i    n-the-enterprise.png)

Once AI coding agents can work across code, infrastructure, tools, and requirements, the enterprise question becomes operational.

How should the work flow? Who checks it? Where do security and quality enter? What evidence shows that the agent did the right thing?

## A practical delivery flow

You probably have already connected the dots, so I'll sum this up.

1. Give the AI coding agent rules and procedures.
2. In a standard way, tell your ideas to AI as flows of interactions between a user and the system.
3. AI does the technical design and parcels out work between code repositories, one per layer.
4. A Red Team agent iterates with AI to identify cyber security risks and fix them.
4. AI builds and tests based on the specs.
5. A critic agent validates that the coding agent actually did what it was supposed to.
6. A deployment agent deploys each repo: cloud, api, web, etc.
7. AI assesses log files for positive and negative feedback.

This is the shape of an operating model, not just a productivity workflow. It describes inputs, design, security review, implementation, validation, deployment, and feedback.

That is the right level of conversation for enterprise leaders.

## The controls are familiar

Shout out to some keywords that have big meaning for AI. Using these keywords is a cheat-code to unlocking key features.

- Red Team: this is from cybersecurity, and means a team that finds cybersecurity issues and resolutions or mitigations to them. Having an iterative loop with a Red Team Agent and a Designer Agent hardens a design to reduce cybersecurity risks.
- TDD: Test Drive Development. This little buzzword makes your coding agent design the test before it writes the code. In real life, this was to keep us from skipping over automated testing and had the amazing benefit of speeding along delivery because the target and ambiguities were better understood.
- Critic: A Critic agent evaluates what something should be versus what it is, and provides that candid, direct feedback like it wants a podcast.
- Infrastructure as Code (IaC): instead of issuing ad hoc commands, using IaC lets LLM's use language to define cloud resources, and then use basic tool execution patterns to deploy your stuff.

None of those ideas are exotic. They are familiar enterprise concerns: security, quality, independent review, repeatable deployment, and measurable feedback.

The new part is that agents can participate in each stage.

## Automated does not mean unchecked

More than any software development lifecycle I've done, this tooling lends itself to end-to-end automated workflows. It pushes back to the left and out to the right. Every stage has an evaluation by a separate agent, checking to make sure it makes sense. And that is a feedback loop. So, designs, coding, testing all get checked by expert agents.

That is the opportunity, and the caution. The better enterprise pattern is not one agent with broad authority and no review. It is a workflow where authority is scoped, outputs are checked, and feedback is built into the system.

The agent can move quickly. The operating model decides whether quickly is useful.
