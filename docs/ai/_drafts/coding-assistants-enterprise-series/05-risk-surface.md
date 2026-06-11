# The Risk Surface

![People communicating in a corporate setting around risk signals and controls](/assets/2026/coding-assistants-enterprise/corporate-communication-risk-surface.svg)

Every useful technology creates a new risk surface. AI coding assistants are no different.

The practical risks are not only science-fiction concerns. They are ordinary delivery risks moving faster: unclear instructions, excessive scope, stale documentation, repeated failed attempts, and the assistant confidently doing the wrong thing.

## Instructions can drift in practice

Sometimes, your coding assistant just won't follow instructions. "ALWAYS call the mcp server to query Azure." Why is it trying to use some other tool? Somehow, the instructions can get muddled even when the context is simple.  Somehow, your very unambiguous statement gets remapped to ambiguous. "NEVER enable public IP addresses," is another battle I fought. You would watch the problem solving and it would suddenly conclude, "This is because public IP are disabled. I will enable public IP." Vigilance is the main watchword; policy as code can minimize harm. Your best bet here is to work to use MCP tools. Ask AI how you can be more clear and more specific and in what coniguration files should you be making exactly what statement to have the behavior happen.

For an enterprise leader, that is the reason controls matter. A clear policy in a document is helpful. A policy expressed in code, guardrails, tests, and repeatable tooling is stronger.

## Context can get stale or too large

Long sessions, where rebuilding the context seems like an arduous task to you, the operator, invariably break down. A friend reminded me of this. Give it a vacation, a holiday. And then come back fresh.

That sounds small until you scale it. Long-running context, unclear ownership, and accumulated assumptions are already familiar enterprise failure modes. AI assistants do not remove them. They can amplify them.

## Old platforms need extra care

Working with old libraries, like Jenkins in one project I had, can confuse things. There is so much documentation and commentary that it can mix and match obsolete with the latest-and-greatest. That doesn't work. You need to figure that part out and be speciic.

This is especially relevant in enterprise environments, where old and new systems often sit side by side. The assistant needs specific guidance about which version, pattern, and operational reality actually applies.

## Repeated failure is a signal

If it fails twice at something, you need to adapt. It won't. You will burn countless tokens along with your midnight oil, and you will feel like you got yourself in a jam. Step back, restate the problem. Coach it and let it coach you to get prerequisites set up.

Redoing the same task over and over. It won't automatically look for ways to re-run your terraform locally. If you watch, you will see it try to search for all the `*.tf` files even though you know it knows where it put them, before running `terraform validate`. Have it write scripts, instruct it to look for scripts, and watch carefully for satements like `Search (glob)` which means it doesn't think it knows where something is. If you can get it to use scripts, templates, and MCP servers, a lot of the repetitive, wasteful churning goes away.

This is one of the clearest management rules: when the loop is no longer improving, change the system around the assistant.

## The enterprise posture

The right posture is disciplined adoption.

Use clear instructions. Limit scope. Prefer repeatable tools. Put policy into enforceable forms. Add independent review. Watch for loops. Treat failures as signals about the workflow, not just the model.

AI coding assistants can be powerful participants in enterprise delivery.

They still need an operating model that assumes reality will be messy.
