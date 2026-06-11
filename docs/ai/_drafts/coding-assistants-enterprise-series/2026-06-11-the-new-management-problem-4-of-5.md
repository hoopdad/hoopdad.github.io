# The New Management Problem

![A visionary enterprise manager setting direction and guardrails without micromanaging](/assets/2026/coding-assistants-enterprise/visionary-manager-leader.svg)

AI coding assistants do not remove management from software delivery. They move management into new places.

The work becomes more about setting direction, defining scope, writing clear requirements, checking outputs, and designing feedback loops. That may sound familiar because it is.

## The human role changes

Over the last couple of months I have been zealously figuring out how best to work with these tools as if I were writing Enterprise or commercial software. I needed some example applications and wanted to be at least a little ambitious. But I didn't write any code, not a line. That was the test: can GitHub Copilot write code that maintained high quality, adhered to standards, took actions that were traceable and auditable, and follow a gated workflow? Yes. Not to understate, but yes! It takes a good manager, but yes. It was sometimes exhausting having 15 minute follow-ups with a team of agents, rather than the dailiy standups a people manager would have, but yes.

That is the management problem in one paragraph. The assistant can do meaningful work, but someone still has to manage the shape of that work.

## What managing the assistant looked like

My role in this was to set up coding assistants to do the work. What I did:

- Communicated the flow from the user perspective
- Wrote implementation patterns and system requirements and made the assistant refer to them
- Manual setup tasks with no tools like log in to Apple and Google developer sites
- Reviewing outcomes, Spot checking code (fine for my POC stuff but you might consider more rigor)
- When there was a problem and AI couldn't fix it quickly, reviewed code and log files, then steered AI

Those are not fringe activities. They are the practical work of keeping delivery pointed at the right outcome.

## Skills that become more important

Projecting what I found in my experimentation into the real world uncovers roles and skills that become even more important. With these skills, ideas will take off very quickly, like you wouldn't believe. Those without these skills will be spinning in circles and wasting tokens.

- Vision casting: this kicks off the whole process. The clearer it is, the faster it comes to life
- Written communication: concise language and removing ambiguity are step 1. Understanding how AI will receive that communication and what it does with that is key here. And understanding that AI can read structured formats easier than prose.
- Software tooling: run code, format it, test it, deploy it, check for vulnerabilities. How to trigger these at the write time without having your AI design it from scratch each time saves a kingdom of tokens.
- Gathering feedback systematically from users and the system itself, to feed improvements and fixes.
- Managing scope: start with a clear definition and checking back to make sure we're still on that. Making sure we limit scope of our agents' memories and processing abilities systematically, in ways very similar to how we do the same for our human developers.
- Software integrations: understanding how components wire together is key to making sure the system is thinking about flows correctly, and being the real big brain when it finds  bug it can't troubleshoot. Enabling self-diagnostics comes from this skill, too.

That is a useful list for leaders because it does not pretend the future is only about model capability. It points to the human and organizational skills that decide whether the capability turns into results.

## Where to invest attention

This is what I see the tech doing very well, and I boil it down to language skills.

- Writing code. Putting the "language" back in programming language. A natural for python, HTML, but also Terraform.
- Gap analysis or critical analysis. Believe it or not, it's pretty good. Try it with your personal AI assistant and ask what you're doing wrong. Based on the data you've given it, it'll let you know.
- Technical flow design. How data flows from a screen to an api to a database with different names and structures is handled well, as long as you instruct it to be systematic.
- Having AI build tools to take the pressure off AI. Query copilot to tell you what MCP tools would benefit the scenarios you face. Local tools for a single project are quick to build, can evolve with the project, and save tokens.

The skills I highlighted above aren't necessarily part of any single current job description. There are more soft skills, imagination, and abstract thinking, needed now. But also the fundamentals of software engineering are more important than ever. Someone will invent a new way to get from idea to deployment, in a new shape that doesn't exist yet, but, we're not there quite yet.

The decision-maker takeaway is direct: do not only buy tools. Build the management muscle around them.
