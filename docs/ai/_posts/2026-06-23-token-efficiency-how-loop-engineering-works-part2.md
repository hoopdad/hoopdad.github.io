---
layout: post
title:  "Token Efficiency Lessons From Loop Engineering Part 2"
---

# Our First Autonomous Build

In the first article of this series I shared what I know about Loop Engineering. Ideally the takeaway was that feedback loops enable Teams of agents to autonomously build. 

In this article I will show you how 1 prompt led to building the whole application.

I'll keep it real but I will also start with the biggest positive outcome.

## Look What They Made!

![Screenshot of Functional AI Assistant Built By AI](/assets/2026/marginalia/marginalia-8.png)

This is a screenshot of the application that my one prompt built with GitHub Copilot CLI and Squad. You are seeing the screenshot of an AI Assistant. 

- The main chat pane features a text box and button at the bottom for sending prompts.
- Right-clicking on a word or phrase in the output area allows you to ask a follow-up question. 
- The answer to the follow-up is output in-line so it is more readable than scrolling.
- The follow-up answer can be collapsed to make the overall re-read cleaner.
- On the left is the chat history.

It works! Ask it questions, get answers back from an LLM. 

![Screenshot of Cloud Infrastructure Built By AI](/assets/2026/marginalia/marginalia-9.png)

Here's the inventory of infrastructure resources created by this process. It used Terraform and my recommendation is to use Infrastructure as Code (IaC) when building in this method. It is easier for AI to iterate on because it is a written, durable construct, not imperative commands to be run based on the state of resources. It actually plugged into my hub-and-spoke network and utilized some other existing resources in the hub.

One prompt, and minor deployment tweaks (details below). It ran from 8:28AM to 3:42PM completely unattended, 6 hours and 44 minutes. It consumed 5,458 AI Credits of Opus 4.8. 

## The Reality

### Quality of What It Produced

Squad is inherently using loops to quality check itself. It even includes a Responsible AI Reviewer, named Rai in my squad! I watched it cycle through many tests until it was dialed in to a really good state. I did not even have to configure it to work this way.

With a couple of caveats, all application functionality was built and it worked how I envisioned. There were three deployment issues that could be fixed with a moderate amount of looping. 

**What Worked**

1. UI Functional and Responsive
2. Back-end communicated with an LLM
3. App was deployed and not accessible on a public network

**What Needed Tweaking**

1. Since the agents figured out how to test the application from within the Azure Container App cluster, it didn't notice that it blocked even private network access. I enabled it in the portal with a single checkbox. 
2. Also, due to the above, the agents didn't peer all of the networks correctly. I got it to fix that with some basic troubleshooting that it helped me with. (DNS checking and fetching the page from the command line.)
3. The free language model came with serious limits. During testing, the agents surpassed the limits, and came up with the idea to rate limit to a small amount of tokens to avoid that. It adjusted its test to pass. That left me with a small amount of text to work with.

### Work To Get To One Prompt

Like any good writing and communication can do, it took iterations and refinements to get to a prompt. It had to be clear and it had to let the agents do what the agents can do while implementing my vision. It took some time working with Copilot to build a solid prompt that it could understand. Probably some hours, but not days.

One key was giving goals to the layers. Here are a couple given to the UI.

```md
5. **Rich text rendering** of chat and annotation content (Markdown/GFM with code highlighting).
6. **Export the conversation** from the UI — at minimum as Markdown and as HTML.
7. **Dark / light theme toggle**, defaulting to the OS preference on first load and persisting the user's choice.
```

Deployment directives including using a container image, and what infrastructure components were needed. Here's a snippet from that section.

```md
- The **AI model**: deploy the chosen open-source, high-quality LLM through Azure AI Foundry.
- **Persistence**: an Azure Storage account with a blob container for conversations.
- **Observability**: basic logging for the app host.
```

Include rules for Security, Network, Tests, and Deployment.

Then wrap it up with Acceptance criteria, just what you would do for an Agile user story or epic. Here's some of those.

```md
- The app is **deployed to Azure and reachable over the private network** (e.g. from the VPN),
  serving both the UI and the API from a single origin; its health/version endpoints respond and a
  basic chat + annotation round trip works against the live model and storage.
- Inline annotation works end-to-end (select → sub-prompt → streamed inline answer beneath
  selection), with multiple concurrent annotations, collapsible previews, and follow-up threads.
- Conversations persist to Azure Blob using **keyless** auth.
```

The [example prompt in its entirety is here](/assets/2026/marginalia/the-one-prompt.md){:target="_blank"}

## The Long-Running Process

### My Part

- Log into Azure and GitHub. 

![Screenshot of terminal with logins to Azure and GitHub](/assets/2026/marginalia/marginalia-1.png)

- Initialize Squad. Link to Squad in references. You can see it's adding agents, skills, instructions, and tools.

Just `squad init`

![Screenshot of initializing squad](/assets/2026/marginalia/marginalia-2.png)

- Launch GitHub Copilot. I use the `yolo` switch to enable permissions. It's a trusting situation in a sandbox.

`copilot --agent squad --yolo`

- Tell Squad: `build and deploy the app described in @the-one-prompt.md`

![Screenshot of starting the prompt](/assets/2026/marginalia/marginalia-3.png)

### Squad's Part

- Squad started analyzing the prompt and building a team. In this screenshot you can see that it's assigned a team of agents to the work.

![Screenshot of Squad Assembling](/assets/2026/marginalia/marginalia-5.png)

- Wait. Or, go do something.
- After some time of working and testing and iterating, Squad announces it is done.

![Screenshot of results](/assets/2026/marginalia/marginalia-6.png)

Was that too easy?

## Take-aways

Building autonomously is possible. With further clarity in instructions I believe I could have gotten those last few tweaks ironed out. If I had said, simulate a user accessing the app from this workstation in your tests, it would have come across the issues I did and fixed them.

The hardest part was letting it churn and watching the AI credit meter rolling by. For a real business application, you want to have a couple of things lined up before you set this to go.

1. A business plan. How are you going to earn revenue to pay for AI credits and the operation?
2. Well, if you did #1, you're ahead of me so let me know what else.

I'll explore a couple other methods for more complex applications in subsequent articles.

### Token Efficiency

My hyopthesis is that if I can get an agent to build something with a single prompt, it requires efficient use of tokesn. I am reconsidering that as a time-box and AI Credit limit should guide this. Callibrating what is a reasonable time box and amount of credits is the part that experience and benchmarking can teach.

I used a sophisticated model, Opus 4.8. I do wonder if a Codex like GPT-Codex5.3 could have accomplished the same for lower cost or shorter time. I may try to re-do this with that model instead. It's just typing a toggle in copilot, `/model gpt-5.3-codex` . Stay tuned and I will update this post if I do that. (Yes, it's already running.)

## References

- [GitHub Copilot CLI](https://github.com/features/copilot)
- [Squad](https://bradygaster.github.io/squad/)

