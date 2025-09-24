---
layout: post
title:  "Data Engineering of DevOps Data - Jenkins"
---

The first step in any AI or data project is to identify the sources of data and triggers that cause change. This article is about one way to gather data from Jenkins so that it can trigger other activities such as running logs or code through AI agents.

The source code for a demonstration of this plugin is here: [https://github.com/hoopdad/jenkins-plugin-reference)[https://github.com/hoopdad/jenkins-plugin-reference]

## The Solution

![Jenkins Event Flow](/assets/2025/jenkins/simple-agentic-ai-flow-triggered-by-jenkins.png)

Leverage Jenkins event architecture to run custom code at certain times like when a Job ends. Gather data from the Jenkins runtime environment using exposed Java objects. Send the data to a REST endpoint to trigger an agent. The agent analyzes the output log file and emails the support team with a summarized action plan.

## The Platform

Jenkins is the leading CI/CD platform, a mature open source tool. It is coded in Java, runs pipelines that use Groovy, and can run commands for any language. CloudBees is a vendor that supports a licensed version.

In our scenario, the DevOps team wants to analyze output from Jenkins logs after a job completes. Any number of insights can be gleaned from these logs including failure analysis, resources touched during the job, or reasons for errors or warnings.

Jenkins is built on a plugin architecture. Not only do plugins enable extending functions of the platform, but the platform itself uses plugins to execute a lot of its tasks. Tapping into that plugin architecture is not for the faint of heart due to a rare problem: too much documentation. Due to the long lifespan of Jenkins, many articles published a decade ago are obsolete but still turn up in search results.

## Events

Event-driven architectures give the advantage of potential near real-time follow-up actions without the overhead of polling. Enterprise systems with hooks like Jenkins events give us a way to tap into the flow of the system at certain points in time.

Our plugin watches for certain key events:

- classic pipeline start and complete
- pipeline life cycle events of Created, Running, Resumed, and Completed

To handle this we create one Java class, tag it as @Extension so Jenkins will know it is a plugin, and then implement two interfaces.

- [hudson.model.listeners.RunListener](https://javadoc.jenkins.io/hudson/model/listeners/RunListener.html)
- [org.jenkinsci.plugins.workflow.flow.FlowExecutionListener](https://javadoc.jenkins.io/plugin/workflow-api/org/jenkinsci/plugins/workflow/flow/FlowExecutionListener.html)

With these event handler methods implemented, you'll be able to inspect the runtime environment. In the example, we are only logging this to a log file. Once that data is culled from Java objects, however, it can be sent anywhere: calling a REST API, enterprise event publishers, or simply logged to a database.

## Versions

With Jenkins, using the "latest and greatest" did not work in a test environment. In fact the minor version behind the version of the system in use worked but nothing later. As long as Jenkins continues to provide backwards compatibility this works. Plugins have to run in that environment that can only look at its current or previous versions, but not versions after its current version. 2.504 can run 2.504 or 2.479 for example but not 2.6 because that didn't exist at the time of 2.504's build.

For Java, the version was pinned at 17 because versions after that would not work with this Jenkins stack. Make sure you have downloaded that version, set its install directory as JAVA_HOME and added JAVA_HOME/bin to your path environment variables to make this work. See the setup.md in the repo for more details.