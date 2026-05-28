---
layout: post
title: "Token Efficiency - Part 3 - An Operational Playbook"
---

![Token Efficiency - Part 3 - An Operational Playbook](/assets/2026/token-efficiency/token-efficiency-operational-playbook-32x9-v1.png)

This is the practical post in the series. In Parts 1 and 2 I argued that token efficiency is not just about shaving prompt length, but about designing engineering systems so the model spends tokens on useful work instead of rediscovering your environment every turn. This final post is the playbook.

Here's a key hypothesis for you: some languages are easier and faster for an LLM to read and write. And another one: it is easier for an LLM to read a file you already wrote than for you to explain the whole thing again.

If you lead teams or shape architecture, this is where the idea becomes policy. Just enough to stop explaining the same thing for the fiftieth time.

## Keep Infrastructure Codified

The first move is simple: stop carrying infrastructure requirements around in prompts.

Most teams already know they should use Terraform or Bicep. The more interesting move is to encode as much of the organization’s non-functional posture as possible in reusable modules: networking rules, private endpoints, monitoring defaults, naming patterns, diagnostics, RBAC assignments, and the compliance details nobody remembers until release review.

Why does this matter for tokens? Because every time an engineer asks an AI to stand up or modify infrastructure, the prompt has to either restate those requirements or rely on the model to guess them. Both are expensive.

When the requirements are already encoded, the prompt gets shorter:

```txt
Use our standard app service module.
Add one staging slot.
Keep the existing private endpoint and diagnostics configuration.
```

That is a much cheaper interaction than this:

```txt
Create an Azure App Service. It needs private networking, diagnostic settings to Log Analytics,
managed identity enabled, naming aligned to our convention, tags for cost center and owner,
TLS locked down, and make sure it follows our standard RBAC pattern.
```

Same intent. Very different token bill.

### Azure Verified Modules as Token Savers

Azure Verified Modules are a good concrete example. They are opinionated, pre-validated, community-maintained Terraform and Bicep modules for common Azure resources. They are built to meet requirements of Microsoft's Well Architected Framework. I like them because they narrow the gap between “we know what good looks like” and “the AI can reliably produce it.”

A module becomes a compression format for requirements.

Here is a Terraform-flavored sketch:

```hcl
module "web_app" {
  source  = "Azure/avm-res-web-site/azurerm"
  version = "x.y.z"

  name                = "app-prod-eastus"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  service_plan_resource_id = module.app_service_plan.resource_id

  https_only = true
  managed_identities = {
    system_assigned = true
  }

  diagnostic_settings = {
    send_to_law = {
      workspace_resource_id = azurerm_log_analytics_workspace.main.id
    }
  }

  tags = local.standard_tags
}
```

The exact module name will vary, and AVM will not encode every organizational quirk. That is fine. The important part is the principle: encode the recurring non-functional requirements once, then point the model at the artifact instead of narrating them again.

This is not new. We did similar things years ago with golden AMIs, platform templates, base Helm charts, and internal service scaffolds.

![Bias to Reusable Artifacts](/assets/2026/token-efficiency/bias-to-reusable-artifacts-32x9-v1.png)

## Bias to Reusable Artifacts

The second habit is to prefer artifacts over fresh reasoning.

A lot of teams use AI as if it were a smart intern with a clean notebook every morning. But if the workflow happens more than once, the goal should change from “have the model figure it out” to “have the model use the thing it already wrote.”

That means saving recurring outputs in durable form: deployment scripts, interface contracts, environment requirements, decision logs, and canonical command sequences. Not every conversation deserves a permanent artifact. Recurring workflows do.

### MCP Tools and Stored Scripts

One of the cleaner patterns is to have the AI generate a script once, store it, and then call it through an MCP tool or a trusted wrapper. The first interaction is expensive because you are discovering the steps. The next ten are cheap because you are invoking a known path. I have had success even telling Copilot to generate the MCP as a local tool and it created a stdio python script that worked.

#### Prompt to Generate an MCP Server with 3 Tools

This is the exact prompt I used in a project that builds and deploys a system.

```txt
/fleet Write an mcp tool that looks for the status of every azure 
resource that you have deployed. Do this by maintaining a local-only
list of resources, which you generate by an mcp tool. With that 
list of resources, another tool will loop through it and use the
resource-specific method of getting a status. A third tool will
look at log files from the resource or azure monitor or log
analytics (you decide) to examine the last 100 entries and find
errors in context. That's 3 tools in total: 
list_azure_resources - gets the resource IDs as a local file
get_azure_status - gets the status for one or more or all of those resources
find_error - gets the errors from logs in context from one or more or all resources
Deploy this locally, make sure it gets into the current
working git branch and push those files exactly including .gitignore
so that we don't add any IDs into the repo. Make sure you have good
descriptions with those tools so that you will know when to use them. 
Develop tests that can be used now and in the future so we can be sure
these run properly.
```

#### Prompt to Generate a Script

For example, instead of repeatedly prompting:

```txt
Deploy the app to Azure Container Apps, build the image, tag it with the commit SHA,
update the revision label, and run the smoke test against the health endpoint.
```

You move to this:

```bash
./scripts/deploy-container-app.sh --env prod --sha 4f2c9d1
```

And the AI prompt becomes:

```txt
Run the standard container app deployment for prod with commit 4f2c9d1.
```

That is the shift. The model starts orchestrating a known artifact.

A simple script like this often pays for itself quickly. It is not glamorous but that is part of its charm. It is operational knowledge turned into a reusable asset, much like runbooks were for humans before we asked language models to sit in the operator chair.

![Codify Operations, Not Ad Hoc Commands](/assets/2026/token-efficiency/codify-operations-not-ad-hoc-commands-32x9-v1.png)

## Codify Operations, Not Ad Hoc Commands

This deserves its own section because teams underestimate the cost of improvisation.

Every ad hoc command sequence typed into a prompt is a token expense that does not compound. It solves one moment. Then it evaporates.

Every saved script, Make target, IaC module, or checked-in workflow is a token expense paid once and reused many times. That compounds.

If I see a team repeatedly asking an assistant to do some variation of this:

```txt
Run these six commands, but in this order, and skip step four in staging, and use this alternate flag in prod.
```

I do not think, “great use of AI.” I think, “you found a script trying to escape.”

The old operations lesson still holds: codified knowledge beats organizational knowledge.

A decent standard looks something like this:

- If the action will happen again, script it.
- If the resource shape will repeat, module it.
- If the decision matters later, log it.
- If the workflow is sensitive, expose it through a controlled tool.

There is some upfront cost. But I would rather pay once to create a durable path than keep paying a token tax for cleverness.

## Keywords as Token Shortcuts

Learn the keywords that map to behavior in your AI tooling.

Well-configured assistants often respond to compact cues that carry a lot of implied instruction. “TDD” can trigger test-first behavior. “Red-team” can trigger adversarial analysis. “Use the standard deployment path” can point it at an existing script or module rather than improvising.

Compare these two prompts:

```txt
Use TDD. Start by writing a failing test for the token validation edge case,
then implement the minimal code change, then rerun the relevant tests.
```

and:

```txt
Please first think about how to test the requirement before changing code.
Write the test in the existing framework, make sure it fails, then implement
only enough logic to pass it, and finally rerun the targeted tests.
```

The second is fine. The first is cheaper and, in a healthy environment, just as clear.

This is shared vocabulary. Over time, teams develop prompt shorthand the same way operations teams developed shared language for incident response.

There is one caveat. Keywords only work when the assistant has been configured to map those terms to real behavior. If the shorthand does not stick, do not pretend it does.

### Pro Tip - Red Team

For security risk analysis and remediation, I am having good luck telling the LLM to "Red Team" a design.

```txt
/fleet I need a new user flow that does xxxxx. Design it using our best 
practices. Red Team it. Build it, test it, and follow our devops procedure to 
ship it.
```

## Remind the Agent

Even with good system prompts, stored artifacts, and useful shorthand, agents drift. They skip a step. They get enthusiastic. They decide one file is “probably enough.”

When that happens, I prefer the cheapest correction first: remind the agent to follow its instructions.

Something as short as this is often enough:

```txt
Follow your instructions and use the repo workflow.
```

Or:

```txt
Use TDD and the checked-in deployment script. Do not improvise commands.
```

That is usually better than re-briefing the task. It costs a few tokens and often snaps the interaction back onto the rails.

I think of this the same way I think about working with experienced humans: a brief “hey, we talked about this” is often sufficient.

That said, reminders are not a cure-all. If the agent misses the same behavior repeatedly, the problem is probably structural: the instructions are buried, the artifacts are hard to discover, or the workflow is not encoded tightly enough. At that point, fix the environment.

My rule is simple:

- Use a reminder for occasional drift.
- Restructure instructions or tooling for repeated drift.

That distinction matters.

## Closing: The Compound Effect

![Token Efficiency Flywheel](/assets/2026/token-efficiency/token-efficiency-flywheel.png)

Token efficiency compounds in the same way operational discipline compounds. A shorter prompt is nice. A better system is better.

Codified infrastructure means fewer requirements to restate. Reusable artifacts mean fewer workflows to rediscover. Scripts and modules beat clever one-off command sequences. Shorthand vocabulary reduces prompt chatter. Brief reminders handle normal drift without starting over.

None of this is magical. It is just engineering hygiene applied to AI-assisted work.

We spent years learning that reliable systems come from turning intent into artifacts and artifacts into repeatable paths. AI does not change that lesson. If anything, it makes it harder to ignore. The teams that do well here may not be the ones with the fanciest models, but the ones that stop paying rent on knowledge they could have written down.

## References

- Azure Verified Modules: https://azure.github.io/Azure-Verified-Modules/
