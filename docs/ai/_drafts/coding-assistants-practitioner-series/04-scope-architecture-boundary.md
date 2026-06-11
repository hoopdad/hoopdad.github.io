# Scope Is the New Architecture Boundary

AI coding assistants make scope visible in a way that feels familiar to anyone who has managed software delivery.

Give too little context and the assistant guesses. Give too much and it may wander, micromanage, or churn through tokens doing work it should have delegated. That makes scope a practical architecture concern.

## Four workflow shapes I tried

I created 4 frameworks for different scenarios I found. I kept iterating and they kept getting better. They are still rough and if you want to use them you will have to make them work in your environment. (Pro tip: use an AI coding assistant to help!)

1. For a small app, with a single repository, maybe this would be a script. Define the sprint in `.github/copilot-instructions.md` and tell it to follow `OPERATOR_RUNBOOK.md`. Prompt it with some boilerplate with sprint goals and acceptance criteria, as if you were an Agile scrum master. See [Lightweight Sprint](https://github.com/hoopdad/agentic-harness/tree/main/lightweight-sprint)
2. For an app with multiple repositories, one per layer, what I called the Enterprise Copilot Fleet Controller. One agent coordinates and designs and has only access to design and work items. Many specialist agents write code and deployment procedures. Critics everywhere like in real life keep them in check. [Enterprise Copilot Fleet Controller](https://github.com/hoopdad/enterprise-copilot-fleet-controller)
3. An alternative for an app with multiple repositories, one per layer: a parent repository tracks the layers' respositories as git submodules and has access to read all of them. Keeping scope limited for token count reasons was challenging. I found that the coordinator agent tended to micromanage, doing work itself instead of delegating. Costs to this are to quality and effort - with that much scope the coordinator would get overhwhelmed. (Any managers in the room right now, feeling that?) But it churned through many sprints successfully before falling down. See [Multi Repo](https://github.com/hoopdad/agentic-harness/tree/main/multi-repo)
4. Custom workflows. This is not really working yet. I had AI design and write it with workflows that I delivered, but implementing all the details in this will take more time. Not there yet but offers deterministic gates that give temporary control to indeterministic agents. Link to follow!

The pattern underneath those examples is simple: the bigger the system, the more deliberate the boundaries have to be.

## Why executives should care about scope

Scope is not just a developer convenience. It affects cost, quality, accountability, and delivery risk.

Projecting what I found in my experimentation into the real world uncovers roles and skills that become even more important. With these skills, ideas will take off very quickly, like you wouldn't believe. Those without these skills will be spinning in circles and wasting tokens.

- Vision casting: this kicks off the whole process. The clearer it is, the faster it comes to life
- Written communication: concise language and removing ambiguity are step 1. Understanding how AI will receive that communication and what it does with that is key here. And understanding that AI can read structured formats easier than prose.
- Software tooling: run code, format it, test it, deploy it, check for vulnerabilities. How to trigger these at the write time without having your AI design it from scratch each time saves a kingdom of tokens.
- Gathering feedback systematically from users and the system itself, to feed improvements and fixes.
- Managing scope: start with a clear definition and checking back to make sure we're still on that. Making sure we limit scope of our agents' memories and processing abilities systematically, in ways very similar to how we do the same for our human developers.
- Software integrations: understanding how components wire together is key to making sure the system is thinking about flows correctly, and being the real big brain when it finds  bug it can't troubleshoot. Enabling self-diagnostics comes from this skill, too.

That list is not exotic. It is the work of making software delivery coherent.

AI just raises the stakes because it can move through the wrong scope quickly.

## The decision-maker takeaway

If you are adopting AI coding assistants in an enterprise environment, do not treat scope as an afterthought.

Decide what the assistant can see. Decide what it can change. Decide when it should delegate. Decide when a critic reviews the work. Decide what evidence counts as done.

The boundary is part of the design.
