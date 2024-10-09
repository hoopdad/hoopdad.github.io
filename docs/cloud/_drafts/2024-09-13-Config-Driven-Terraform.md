---
layout: post
title:  "Config-Driven Terraform"
---
Attribution: this post is a collaboration with Caleb Cohen, GitHub ID .

The concept of config-driven Terraform goes hand-in-hand with deployment patterns. A Terraform Module that is of type Deployment Pattern can be written in a way to achieve additional goals: ease of use and flexibility. Additionally, implementations that use modules and resources define parameters that adapt the infrastructure as the supported application evolves.

There is a balance between very simple input variables and complex module code that must be managed. The module could become too complex to maintain if it has to make a lot of assumptions. It could become too opinionated in design and so less reusable. Key principles in this post provide design guidance intended to keep that balance reasonable.

## The Balance: Simplicity in Use versus Complexity of Development

The most obvious beneficiary of a config-driven design is the implementor, and, closely connect, the maintainer.  The implementor is the person putting together Terraform code that reuses modules and manages pipelines to deploy the underlying resources. The maintainer is the person who is responsible for changes to that code and pipeline on Day 2. They are both focus on responding to business needs quickly, so giving them a nice interface to the module makes their job (and business results) better.

The balances comes in when a very simple configuration is really complex in the back-end module. Deep hierarchical input objects with many default values requires sophisticated programming to write and even more sophisticated troubleshooting skills. There's a song in software development that it is harder to debug complex code than it is to write it. To make an extreme point of it: let's say you had a day when you had salient flashes of brilliance and wrote complex code. On a day later when you are stressed and sleep-deprived, lacking coffee, you won't be able to debug your own code.

For now, we leave this measure of simplicity versus complexity as a judgement call for the code designer, but offer these principles as guardrails.

## Terraform Input Design Principles

- Inputs match the implementor's understanding of resources.
- Input values aren't duplicated.
- Use simple hierarchies.
- Favor referencing other hierarchies simply over deep nesting
- Restrict use of data lookups to when the implementor isn't like to have an object ID

### Inputs match the implementor's understanding of resources

The "Facade" patterns from Object-Oriented Design (OOD) give us a construct for this concept. You create as much complexity as you need, but hide it behind a nice, simple, succinct front-end. This encourages re-use because you aren't requiring the implementor to understand arcane object relationships or constructs. You could theoretically change you create the intended resources completely without changing the parameters. This is equivalent to "design by contract" in Service Oriented Architecture or late binding in OOD. As implementor you know what you want the thing to do but you don't care how it gets the job done.,

### Input values aren't duplicated


### Use Simple Hierarchies

Use simple hierarchies for nesting attributes under objects whose count is more than one and not known at the time of module development.

### Favor referencing other hierarchies simply over deep nesting



### Restrict use of data lookups to when the implementor isn't like to have an object ID
