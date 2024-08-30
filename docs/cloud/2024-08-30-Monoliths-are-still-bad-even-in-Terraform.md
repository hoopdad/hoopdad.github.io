---
layout: post
title:  "Monoliths are still bad, even in Terraform"
---

## Reusability in Infrastructure as Code

I want to dive into what makes good reusable Terraform, To do that, I'm reflecting on the benefits and pitfalls of designing reusable code of any kind. What is commonly true about C++ code, microservices, and Terraform? And how can we apply to Terraform all the learning from well-developed coding practices of the past?

Regardless of the language, certain attributes of the resulting reusable assets are critical. Reusabilty is the clear intent of this post. With it we need to consider maintainability and code stability. Maintainability is how we make sure that others understand what we did, and that we did it consistently. Stability means that when we want to use code, there is a version of it that is known to be well-tested and functioning.

## Too much of a Good Thing

It is tempting to add that next new thing into the existing thing. You already have a code repository, a pipeline to deploy it, procedures to support it. Those aspects are the counterbalance to separating code into modules. It seems like a judgement call but we can put some guidelines around how much is too much in a Terraform module.

You will find an inverse correlation between the numbers of kinds of resources created in a module and reusability. If your module builds too many things, the likelihood that someone else needs that code to build all of those same things goes down. They might not need them or they might want those same things but build them in a different order.

An example would be a module for a database. That database needs storage, and it can't live without storage. In Azure it probably needs a managed identity to communicate with storage. So here are two scenarios - one that builds the monolith, an opinionated construct of all the things I need for a database, versus independent components.

### The Monolith

Here's all the things we need for the database, so let's roll them together. Then, when someone else needs a database, they can reuse it? We'll see! Let's leave out the network considerations as we can illustrate the point without adding in that volume of items.

- the managed service of the MS SQL database, tuned to my organization's security policies
- storage for the database, tuned to my organization's security policies
- the managed identity (i.e. what Azure calls a service principal)  assigned to the database
- the multiple privileges for that managed identity to manage storage for the database
- the diagnostic settings for the database (In Azure these can be discretely tuned as separate Terraform objects)
- the diagnostic settings for storage

### Re-use of the Monolith

Our monolith is a thorough and complete solution for an MS SQL database that requires this particular kind of storage, a single managed identity, and a single way to set up diagnostics.

If those assumptions are all true for the next project, we'll get reuse out of the monolith. But very likely there are other outcomes like the following that mean you can't use that monolith.

- The next project uses PostgreSQL instead of MSSQL, so you can't reuse the storage, identity or settings.
- Another project requires re-use of an existing storage object and managed identity. That same storage is to be accessed directly by another service and the identity is also created and configured to that other service first.
- Another project needs advanced features on the database which are more expensive than the other projects', and require an exception to run in your company's environment.

Before we leave the monolith, let's recognize that the way we have constructed and glued together the listed objects is actually potentially reusable by a limited set of other projects. So we can actually call that an opinionated deployment pattern. You might actually get some re-use, and for those, wow, it has exactly what they need with no changes. This is one way to build deployment patterns.

Hold that thought and let's come back to deployment patterns.

### The Atomic Components

Now let's take that same list and break it into logical components that are more atomic in nature, meaning they are more likely to be reused but there might be more wiring required to use them.

- Module 1 - the database
  - the managed service of the database, tuned to my organization's security policies
  - the diagnostic settings for the database
- Module 2 - storage
  - storage
  - the diagnostic settings for storage, tuned to my organization's security policies
- Not in modules - applications use these definitions as glue which can vary wildly from one project to the next
  - the managed identity (i.e. what Azure calls a service principal)  assigned to the database
  - the multiple privileges for that managed identity to manage storage for the database


#### Re-use of the Atomic Components

Because we built the modules to include fewer resources, we can compose them differently in an application.

- Project needs PostgreSQL instead of MSSQL - create a new database module for PG, and re-use the rest
- Project needs to re-use storage and identity - well, just re-use it. The application provided the glue, so it can re-glue in any way it needs.
- Advanced features on teh MSSQL database - you can create a new database module or provide variables to drive those more expensive features. Judgement call.

What you didn't have to do was vigorously re-test the modules that didn't change. Those are in a known, good state.




These are questions that I've worked to answer in microservices, web services, web sites, and object-oriented programming. They all rally around one value judgement - monoliths are bad! And, it's the role of architecture to answer them.

## Impediments to Reuse

If you're building a module, you probably are taking a little extra time in separating your code and maybe putting it in a different repo. Those are obvious requirements. But then, what makes it more likely to be reused?



### About Monoliths

A monolith is an attempt to lump your code into one "thing". The first pass through, this is usually very fast and gets a prototype up very quickly. It means a single deployment and everything goes at once. But ...

The result of building monoliths is that the whole system experiences risks of change whenever even the smallest requirement is implemented. It could introduce a bug at an area you're not thinking about, so testing cycles need to cover more ground and are more likely to miss that bug. 

The code becomes spaghetti or a "house of cards" and it breaks a lot, because when you fix "thing a" you wouldn't logically think to test "thing z" because they are so far apart. But your monolith connected them.

It means deployments are massive events with "all hands on deck" instead of a seamless addition of the new requirement.

Monoliths are not reusable.

A monolithic Terraform build would put all the configurations for the whole system together. It would meet requirements on day 1. The more you refactor it, the more risks of breaking dependency graphs and lengthy build times. And you aren't re-using it on your next project, no matter how many variables you use, unless you consider copy and paste as reuse.

## Designing for Reuse

Certain relative elements of design influence how often your code can be re-used. Balance is key as you have deadlines to meet, and can potentially refactor later. Until you've missed the window where refactoring is "easy" or not.

### Breadth of the scope of work

For example, in a given module
- 

- how opinionated is the design?
- 

## Get Philosophical

One of the enjoyable aspects of system design is the abstract thinking in classification of your system's objects. 

Understanding the "role" an object plays in 



Assume you have parameters - count up what you think each object needs to be fully dynamic. You'll find that table stakes is a large list of parameters that each implementor has to understand, find, and likely code in their locals.