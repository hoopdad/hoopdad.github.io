# When the Assistant Gets Stuck, Stop Prompting and Start Managing

The fastest way to waste time with an AI coding assistant is to keep repeating the same instruction after it has already misunderstood the work.

At some point, the answer is not a better pep talk. It is a better operating environment.

## Where the tools are strong

This is what I see the tech doing very well, and I boil it down to language skills.

- Writing code. Putting the "language" back in programming language. A natural for python, HTML, but also Terraform.
- Gap analysis or critical analysis. Believe it or not, it's pretty good. Try it with your personal AI assistant and ask what you're doing wrong. Based on the data you've given it, it'll let you know.
- Technical flow design. How data flows from a screen to an api to a database with different names and structures is handled well, as long as you instruct it to be systematic.
- Having AI build tools to take the pressure off AI. Query copilot to tell you what MCP tools would benefit the scenarios you face. Local tools for a single project are quick to build, can evolve with the project, and save tokens.

The skills I highlighted above aren't necessarily part of any single current job description. There are more soft skills, imagination, and abstract thinking, needed now. But also the fundamentals of software engineering are more important than ever. Someone will invent a new way to get from idea to deployment, in a new shape that doesn't exist yet, but, we're not there quite yet.

That is the optimistic side. Now the practical side.

## Where it can fall down

Sometimes, your coding assistant just won't follow instructions. "ALWAYS call the mcp server to query Azure." Why is it trying to use some other tool? Somehow, the instructions can get muddled even when the context is simple.  Somehow, your very unambiguous statement gets remapped to ambiguous. "NEVER enable public IP addresses," is another battle I fought. You would watch the problem solving and it would suddenly conclude, "This is because public IP are disabled. I will enable public IP." Vigilance is the main watchword; policy as code can minimize harm. Your best bet here is to work to use MCP tools. Ask AI how you can be more clear and more specific and in what coniguration files should you be making exactly what statement to have the behavior happen.

Long sessions, where rebuilding the context seems like an arduous task to you, the operator, invariably break down. A friend reminded me of this. Give it a vacation, a holiday. And then come back fresh.

Working with old libraries, like Jenkins in one project I had, can confuse things. There is so much documentation and commentary that it can mix and match obsolete with the latest-and-greatest. That doesn't work. You need to figure that part out and be speciic.

## When to intervene

If it fails twice at something, you need to adapt. It won't. You will burn countless tokens with that midnight oil, and you will feel like you got yourself in a jam. Step back, restate the problem. Coach it and let it coach you to get prerequisites set up.

Redoing the same task over and over. It won't automatically look for ways to re-run your terraform locally. If you watch, you will see it try to search for all the `*.tf` files even though you know it knows where it put them, before running `terraform validate`. Have it write scripts, instruct it to look for scripts, and watch carefully for satements like `Search (glob)` which means it doesn't think it knows where something is. If you can get it to use scripts, templates, and MCP servers, a lot of the repetitive, wasteful churning goes away.

## The management lesson

For executives and technology leaders, this is the part to remember: AI assistants do not remove the need for management. They change what management looks like.

The work becomes less about assigning every task by hand and more about creating the conditions where the assistant can succeed: clear instructions, good tools, explicit boundaries, repeatable scripts, and a human who knows when the loop is no longer productive.

When the assistant gets stuck, stop prompting harder.

Start managing the system.
