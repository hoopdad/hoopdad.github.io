---
layout: post
title:  "A More Secure PaaS Environment in Azure - ASE Configuration Options"
---

## What is an Application Service Environment?

In Microsoft Azure, an Application Service Environment (ASE) is an enhanced PaaS platform for web and serverless applications. It bundles many features including load balancing, TLS certificates, DNS management. This article focuses on the choice of "dedicated hosts" or "zone redundancy". Think of these as options put forward as "secure" and "more secure" configurations.

Note that when I discuss virtual machines, these are not VM's that you have any direct control over. This is simply getting into the internals of how ASE's work. It is very nicely wrapped as a PaaS product which simplifies management, deployment, and operations of these kinds of workloads.

Disclaimer - the below diagram is for a generalized understanding only. While it demonstrates likelihood and difficulty of cyber attacks, it is conceptual so that you can see the primary difference between the two ASE modes. Typical deployment and deployment configurations are included to help illustrate more of the stack.

Here is a visualization that illustrates the differences in "attack surface" (which is the exposed points that a cyber attacker might try to exploit) along with "attack vectors" (the specific ways in which a cyber attacker is trying to get into your system.) The higher up items can be thought of as more common and easier to accomplish; the lower items are far less common and very hard to do.

![Successful Imports](/assets/2024-11-01-ase-layers.png)

## Dedicated Hosts ASE

This section talks about the "more secure" (versus just "secure") option mentioned above. An ASE that is configured as a "dedicated hosts" ASE provides isolation down to the hardware level. This is not a typical cloud-level security measure, which some refer to as "bare metal." You specify the number of VM's to run in a data center for resiliency purposes, and they will run on the hardware used by other customers.

It is rare to be able to request physical hardware in a cloud environment, because that goes against the virtualization methods that cloud providers use to scale up to many customers. Due to the fact that Azure can't take advantage of availability probabilities that occur when one app is randomly active and another is not, this option costs more.

This configuration is allocating hardware that may sit idle instead of sharing those CPU cycles with other workloads. Since your virtual compute is not sharing resources with other customers at the physical layer, which is how 99.999% of cloud offerings securely work, you eliminate at least one attack vector. This is the "cross VM" attack, an extremely rare type of attack that I have not heard occurrences at any major cloud provider. This is where the attacker breaks through its own VM into the parent hypervisor layer, finds VM's on the same hardware, and then breaks into those VM's. Many challenges exist for an attack of this kind and it would be highly complex. It is not impossible of course, and your level of risk tolerance is your guide on whether to mitigate that or not.

## Zone Redundant ASE

An ASE that is "zone redundant' replicates your underlying VM's to 3 data centers in the same Azure region. This is a great defense against a single data center's potential failures such as a power outage (and generators fail), redundant networking somehow gets taken out, or some other single point of failure ... fails. This does not replicate to other regions for a DR solution but solves more on the availability spectrum.

From a security perspective, your VM's might end up on a physical server that hosts other customers' VM's. As discussed above, the "cross VM" becomes an attack vector, however likely or unlikely. But it maintains all the other security features of an ASE. You have to weigh the risks, your risk posture, and other factors such as cost. The trade-off between the two can be summed up by isolation versus resiliency.

## Potential Use Cases

If you have highly sensitive data, the "Dedicated Hosts" option is eliminating an attack vector and therefore may be attractive to you. Since there are so many layers and so many attack vectors, you have to make the judgement call if this is one you want or need. Weigh the trade-off of automated zonal redundancy versus isolation and differing costs. There are definitely use cases for Dedicated Hosts, but general guidance is that other options are going to provide a secure operating environment.
