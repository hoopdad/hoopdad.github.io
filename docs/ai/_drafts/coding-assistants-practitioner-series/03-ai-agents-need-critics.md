# AI Agents Need Critics

One of the most useful shifts in working with AI coding assistants is to stop thinking about a single assistant doing a single task.

The more interesting pattern is a system of agents with checks around them. A designer. A builder. A Red Team. A critic. A deployment agent. Not because the labels are exciting, but because separation of responsibility still matters.

## Putting capabilities together

You probably have already connected the dots, so I'll sum this up.

1. Give the ai coding assistant rules and procedures.
2. In a standard way, tell your ideas to AI as flows of interactions between a user and the system.
3. AI does the technical design and parcels out work between code repositories, one per layer.
4. A Red Team agent iterates with AI to identify cyber security risks and fix them.
4. AI builds and tests based on the specs.
5. A critic agent validates that the coding agent actually did what it was supposed to.
6. A deployment agent deploys each repo: cloud, api, web, etc.
7. AI assesses log files for positive and negative feedback.

For enterprise use, this is the more useful mental model. The question is not "Can an AI write code?" The question is "Can the workflow produce work that survives review, testing, security scrutiny, deployment, and feedback?"

## The words that matter

Shout out to some keywords that have big meaning:

- Red Team: this is from cybersecurity, and means a team that finds cybersecurity issues and resolutions or mitigations to them. Having an iterative loop with a Red Team Agent and a Designer Agent hardens a design to reduce cybersecurity risks.
- TDD: Test Drive Development. This little buzzword makes your coding agent design the test before it writes the code. In real life, this was to keep us from skipping over automated testing and had the amazing benefit of speeding along delivery because the target and ambiguities were better understood.
- Critic: A Critic agent evaluates what something should be versus what it is, and provides that candid, direct feedback like it wants a podcast.
- Infrastructure as Code (IaC): instead of issuing ad hoc commands, using IaC lets LLM's use language to define cloud resources, and then use basic tool execution patterns to deploy your stuff.

The point is not to invent a new ceremony. The point is to use the same engineering instincts that already work: separate duties, test before build, review independently, deploy repeatably, and inspect what happened afterward.

## Feedback loops are the architecture

More than any software development lifecycle I've done, this tooling lends itself to end-to-end automated workflows. It pushes back to the left and out to the right. Every stage has an evaluation by a separate agent, checking to make sure it makes sense. And that is a feedback loop. So, designs, coding, testing all get checked by expert agents.

That is where this becomes interesting for enterprise decision makers. The assistant is not just a productivity tool sitting inside an IDE. It can become part of a delivery system.

But only if the checks are designed in.

## The practical recommendation

Do not evaluate AI coding assistants only by how quickly they produce code. Evaluate whether they can work inside a controlled loop:

- requirements that are clear enough to build from
- tests that define success before implementation
- security review before deployment
- critic review after delivery
- log analysis after the system runs

Speed is useful.

Independent evaluation is what makes speed usable.
