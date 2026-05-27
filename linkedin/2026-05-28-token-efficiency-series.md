# LinkedIn Posts — Token Efficiency Series

## Post 1 — Wednesday May 28 (Series Introduction)

Usage-based billing for AI tools changed something I didn't expect: not my budget, but my behavior.

When news came out about AI tools starting to move to token-based pricing, I started studying how tokens actually flow. Where they get burned. What patterns waste them. How interaction design affects both quality and cost.

Then I noticed: I was doing the same thing engineers did when memory was expensive, when bandwidth was scarce, when database queries had visible cost: studying the resource, adapt to the constraints, and build discipline where there used to be indifference.

Token efficiency is becoming an architectural constraint, not just a prompting trick or cost optimization exercise. Take it as a design principle, the kind that reshapes how systems get built.

I wrote a three-part series on this. Part 1 is live now and covers the shift from "tokens are invisible" to "tokens are architecture."

🔗 [link to Part 1]

---

## Post 2 — Friday May 30 (Design Patterns)

Part 2 of the token efficiency series is up.

This one is about design patterns: the structural decisions that make AI systems cheaper and better at the same time.

The one that surprised me most: repository boundaries are now a context management decision. We already learned from microservices that scope controls blast radius, deployment independence, and failure modes. Turns out scope also controls how much noise an AI has to wade through before it gets to useful work.

Other patterns in the post: file-based artifacts as durable memory, orchestrator-specialist decomposition, and why deterministic controls still beat clever prompts where trust matters.

Most of these have precedent in distributed systems thinking from the last two decades. The props are new. The engineering lessons are not.

Part 2 of 3: 🔗 [link to Part 2]

---

## Post 3 — Sunday June 1 (Operational Playbook)

Part 3 of the token efficiency series — the operational one.

The idea that stuck with me while writing this: every ad hoc command typed into a prompt is a token expense that doesn't compound, but every saved script is a token expense paid once.

That's the whole post in one line, really. But the details matter — Azure Verified Modules as requirement compression, MCP tools invoking stored scripts instead of rediscovering steps, prompt keywords that carry implied behavior, and knowing when to remind an agent versus when to fix the environment.

None of it is magic. It's engineering hygiene applied to a new kind of resource. The teams that do well here won't necessarily have the best models. They'll be the ones that stop paying rent on knowledge they could have written down.

Final post in the series: 🔗 [link to Part 3]
