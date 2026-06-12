---
layout: post
title:  "Agentic Workflow with Copilot CLI - Single Repo"
---

Ready for an end-to-end agentic workflow that takes you from idea to deployment? I start with a single repository in this post, and, in future posts, will introduce ways to do the same thing with more complex repository layouts.

## What's the Point?

Think of an idea for an application. Then, open your browser or phone and that idea is already running. Well, you'll do a little more than just think of an idea, but we'll get close to that. A little bit of brain-to-typing is involved.

To do this reliably a few things must be true.

**Each stage has to have gates, and every stage writes files.** 

A gate is an approval, and can be as simple as a check for a file to be formatted correctly to passing batteries of tests. We are using agents to be gate keepers in this scenario, and you could put instructions in to make that be humans. That would slow things down while waiting, but it offers more control. For purpsoes of this article, risk is very low so I'm not even worried a little bit about agents being able to adequately gate.

Every stage writes files as a way to handoff to the next. Using simple YML files seems best, with minimal text overhead like quotes and curlies with JSON. Hierarchy in YML represents meaningful relationship between elements. Files stay small, easy to write for an agent, and easy to read for a different agent.

We also need to **manage context and minimize agent micromanaging**. 

Context in this case literally means all the files in the repository, and if too large can lead to wrong decisions or confusion. Confusion on the part of the agent or us, you ask? Yes. Both. 

And by micromanaging, I have seen where agents will take over the job of others because it seems easy, but then they skip around gates. If that sounds like that one job you had (or have!) I feel for you. Been there, done that. And agents can mimic human tendencies for "efficiency" sake. 

## Write Down Your Technical Requirements

As a Microsoft employee, I'm going to be biased for Microsoft tools but believe it or not, Copilot is not. So we have to steer Copilot, and then use our network/security/system knowledge. I write these kinds of things in simple files, usually just a markdown file. In later iterations you'll see me re-use YML files across projects, but let's get started more easily.

I'm going to tell the system that it has to behave in a certain way. It will include the kinds of things listed below. We'll reinforce it with instructions later.

- Deploy to my cloud tenant and subscription in Azure, in the Central US region.
- Expose the minimum public IP surface to the Internet.
- Use a Web Application Firewall that filters the Top 10 OWASP risks, from the latest available list. The WAF is the only surface that gets a public IP address.
- Data can flow from user to the WAF, to a Web server or API server, then to a database. It can't skip layers.
- Manage services to prevent CORS errors.
- Deploy layers as Azure Container Applications.
- Store data in a Cosmos DB.

Since I actual have used this, [here's one](https://github.com/hoopdad/standards/blob/main/external-user-pattern.md) I evolved a little bit. You might want to boil it down and make it your own. And throw in the [Non Functional Requirements](https://github.com/hoopdad/standards/blob/main/nfr.yml) that I used to make it complete. 

That should get us started in a somewhat secure way. If you aren't familiar with setting up user authentication with Entra External ID or Google OAuth 2.0 Clients, you'll want to learn enough about that to get your agent to set that up for you, especially if any user activity writes data into your system.

## Set up Your Runbook

This is where you define the steps of a procedure you want the agent to follow. And make sure to instruct the agent to always follow these. 

The procedure you're defining will take the system through a series of important steps, and I like them to have files written after each step so I can review how it goes. This would be important for audit reasons as well.

1. Take user input in natural language.
2. Determine which data flows and contracts are impacted by the request.
3. Write requests in a place for each layer.
4. "Red Team" the request. This is a wonderful risk mitigator - try it out! It is a strong key word that triggers lots of agent harnesses including Copilot to evaluate risks in designs or code, and provide feedback to the agent responsible for fixing it. Look for those "red team" loops and you'll be seeing security tighten up.
5. Write code for the layer. Suggest Test Drive Development and you'll see quality go up - just like with human developers. Amazing.
6. Test. You're getting the idea now. And you'll see an actual runbook in a minute.
7. Validate and build, then deploy. We do this in a structured way to take load off the agent by having it write scripts once, and then get them to automatically run when we commit code to a repository.

Hopefully by now you are getting the idea. Take that awkward skit that your manager made you do where you had to pretend to be a certain role. You take a document from someone, scribble on it, then hand it to the next person. A process. If you are visual and like flowcharts, draw one, and then you could probably have AI do a one-time flowchart-to-runbook exercise.

[Here's one that works.](https://github.com/hoopdad/agentic-harness/blob/main/lightweight-sprint/OPERATOR_RUNBOOK.md)

## Login to Your Tools

For this example, I've got a number of tools installed. [This script](https://gist.github.com/hoopdad/e9a0d324cc82eae99a363fc3c5e6f41e) should install most of what I needed. The main pre-requisite is to have an Azure account. If you are new to Azure you can currently create an account with a startup credit and access to many of the services at zero or low cost. Your first month could conceivably be free.

If you don't have tools installed,  you do have the option of letting Copilot do that. You can tell it to identify additional tools it needs.

I log into Azure with `az login` which either gives a link to open or opens a browser window for you depending on system settings. Once you're logged in, the command line tool asks you which subscription you want to work in. Pick one and that's about it.

I also use GitHub and GitHub Actions for running a lot of this. I recommend it, but if you don't have that set up, it's beyond what I can write in this blog. Working locally to learn this or develop a proof of concept is likely fine.

## Tell Copilot to Use Your Runbook

Here's what's really important. **You did all this setup, now make sure Copilot uses it.**

You define these things, which reinforce your runbook, in a file called [.github/copilot-instructions.md](https://github.com/hoopdad/agentic-harness/blob/main/lightweight-sprint/copilot-instructions.md) It's very important that the file is in that place, where copilot CLI currently looks for instructions automatically. If not, you will get super annoyed at writing "Use my instructions in .github/copilot-instructions.md." I may or may not know that annouance from experience: the reader must decide if I learn things the hard way or read the instruction manual.

You are logged in, your agent is prepped, your idea is freah and certainly doesn't involve a multi-player tic-tac-toe game. Now you are ready to build!

## Start with a Clear Prompt

Here's what I'm running. I have a virtual team meeting next week and am going to propose a Virtual Heads Up session. That's the game where everybody except one person (the guesser) sees a word. The guesser only knows a category. The beauty of the natural language prompt is that you should be able to understand the game if my prompt is good, just like the agent should. 

One trick - I'm going to use "Fleet" mode to let it run things in parallel. It'll create subagents to focus on certain tasks and orchestrate the whole symphony.

```txt
/Fleet Outcome is a multiplayer, distributed game. Anyone loading the website before a game starts can participate. Only one game is active at a time in the entire system. 

- If a user joins after the game begins, the user will see "Game in progress. Please wait." and their screen will poll the system until they are eligible to play.
- When a user first joins they will not see the dashboard. They must set a name. If others in the system have chosen the same name, tell them "that name is taken. and they must choose another. Once they choose a unique name, they will see the dashboard.
- The names of all active users are displayed on the main dashboard.
- The count of all games ever played is shown on the dashboard.
- The top 10 highest scoring players of all time and the top 3 of today are shown on the dashboard.
- A button to start a game is shown. If any user clicks that button, the game begins and all users are included. 
- The game begins with a screen that says "gathering categories". That shows as long as the Category agent is working.
- The category agent, a Foundry agent with access to the internet, will in parallel connect to all the websites lsited in its configuration table. (That configuraiton table is configurable via a link on the dashbaord that says "configure categories").
- The category agent will read the contents of the web pages and determine 1 or more categories of words or 2-3 word phrases specific to that category. For example, going to "" will find words like {"","","","","","","",""} which can be gruoped into "". The agent should only include non general words; articles, prepositions, etc might be part of a phrase but not a single word. "A" is not valid but "A Long Winter's Night" might go with a category "Christmas".
- The game begins with an overview of the categories that will be used. There will be one category per user. A button the category view starts the first round.
- At the begining of every round, users are assigned roles randomly. Exactly one user will be named as the guesser. The other players will be named as clue-givers. Users are shown their role, then a countdown from 10 seconds to 0 is shown to all. 
- The game works in rounds. A round is a group of one or more guesses that occur during a 2 minute period. A guess is when the clue-givers are shown the word and the guesser has to guess it. When the gueser is correct, as judged by any clue-giver, the guesser sees the word on their screen for 3 seconds, and gets 10 points for the word. After a correct guess but beffore the 3 seconds, another word is shown to clue-givers and the guesser's screen shows no word. If time expires before the guess is correct, 0 points are awarded and the round will end.
- At the end of the round, the score is saved to the database. The system will randomly pick a user who has not yet been a guesser. If all the users have been guessers in this session, the game ends.
- At the end of the game, the winner or winners are shown on the screen. The winner is the user with the most points during that game. If any of the daily or all-time high scores are beaten, then the all time and today's top scores should be updated accordingly.
- After the end of the game, the dashboard resets to pre-game mode with the cards and buttons as defined earlier. A status bar will celebrate the winner(s) of the last game.
```

A very specific prompt but all natural language. It can be read by us and by AI to identify user roles, flows, state change conditions, and data elements. The agentic system described above can turn this into an app!

## Iterate

## It's Alive!

