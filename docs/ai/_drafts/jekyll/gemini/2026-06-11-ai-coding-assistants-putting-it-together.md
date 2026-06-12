---
layout: post
title: "Coding Assistants - Part 2: Putting Capabilities Together"
date: 2026-06-11 10:00:00 -0400
categories: [AI, Architecture]
tags: [workflows, TDD, automation, case-study]
excerpt: "How do individual AI capabilities combine into powerful multi-agent systems? We explore complex workflows and real-world examples."
---

![Putting it Together](assets/post2.png)

In part 1, we explored the individual capabilities of AI coding assistants. Now, let's look at what happens when you combine those capabilities into automated software development lifecycles.

## Putting Capabilities Together

You've probably already connected the dots, but here is a summary of how a coordinated AI development flow works:

1. **Provide Rules**: Give the AI coding assistant clear rules and procedures.
2. **Standardize Input**: Tell your ideas to the AI as flows of interactions between a user and the system.
3. **Delegation**: The AI does the technical design and parcels out work between code repositories (e.g., one per architectural layer).
4. **Security Iteration**: A Red Team agent iterates with the AI to identify cyber security risks and fix them proactively.
5. **Implementation**: The AI builds and tests based on the agreed-upon specs.
6. **Validation**: A Critic agent validates that the coding agent actually did what it was supposed to do.
7. **Deployment**: A deployment agent deploys each repository (cloud infrastructure, API, web frontend, etc.).
8. **Feedback**: The AI assesses log files for positive and negative feedback to refine the system.

### Key Concepts
- **Red Team**: A cybersecurity term for a team that identifies and mitigates security issues. An iterative loop between a Red Team Agent and a Designer Agent hardens systems automatically.
- **TDD (Test-Driven Development)**: This ensures your coding agent designs the test *before* writing the code. It speeds delivery because the target and ambiguities are understood up front.
- **Critic**: Evaluates what something should be versus what it actually is, providing candid feedback.
- **Infrastructure as Code (IaC)**: Lets LLMs use language to define cloud resources, rather than issuing ad hoc commands, enabling seamless automated deployment.

## Real-World Examples

Over the last few months, I have been actively exploring how best to work with these tools as if I were writing commercial enterprise software. *But I didn't write a single line of code.* 

That was the test: Could GitHub Copilot write code that maintained high quality, adhered to standards, was traceable, and followed a logical workflow? The answer is a resounding yes. It takes a good manager, and 15-minute follow-ups rather than daily standups, but it works.

My role was to set up the assistants to do the work:
- Communicated the flow from the user's perspective.
- Wrote system requirements and made the assistant refer to them.
- Handled tasks with no programmatic tools, like logging into developer portals.
- Reviewed code and log files when the AI got stuck, and steered it back on track.

Here are a few things I built:
- **Math Formula Translator**: An app that translates natural language into math formulas, runs them, and tunes for efficiency (involving a web firewall, website, agent, and tools).
- **Resume Analyzer**: An application that analyzes a resume against a job description and rewrites it in the target employer's language (involving a web firewall, website, Android app, API, database, and agent).
- **Media Tracker**: An app that remembers what TV shows I was streaming across various platforms (involving a web firewall, website, Android app, Alexa integration, iOS app, and database).

The outcomes varied from fully functional systems to break-fix loops that required me to rethink my approach, but the potential is enormous.