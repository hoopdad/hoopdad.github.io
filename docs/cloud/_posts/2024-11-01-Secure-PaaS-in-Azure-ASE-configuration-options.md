---
layout: post
title:  "A More Secure PaaS Environment in Azure - ASE Configuration Options"
---

## What is an Application Service Environment?

In Microsoft Azure, an Application Service Environment (ASE) is an enhanced PaaS platform for web and serverless applications. It bundles many features including load balancing, TLS certificates, DNS management. This article focuses on the choice of “dedicated hosts” or “zone redundancy”. Think of these as options put forward as “secure” and “more secure” configurations.

Note that when I discuss virtual machines (VM's), these are not VM’s that you have any direct control over. ASE’s are an abstraction running on top of the VM’s in question. ASE is very nicely wrapped as a PaaS product which simplifies management, deployment, and operations of these kinds of workloads.

Disclaimer - the below diagram is for a generalized understanding only. While it demonstrates the likelihood and difficulty of cyber attacks, it is conceptual so that you can see the primary difference between the two ASE modes. Typical deployment and deployment configurations are included to help illustrate more of the stack.

Here is a visualization that illustrates the differences between the two ASE options in terms of “attack surface” (the exposed points that a cyber attacker might try to exploit) as well as “attack vectors” (the specific ways in which a cyber attacker is trying to get into your system). The higher-up items can be thought of as more common and easier to accomplish; the lower items are far less common and very hard to do.

![Successful Imports](/assets/2024-11-01-ase-layers.png)

## Dedicated Hosts ASE

As mentioned above, Dedicated Hosts ASE is the “more secure” option. An ASE that is configured as a "dedicated hosts" ASE provides isolation down to the hardware level, which some refer to as “bare metal.” This is not a typical cloud-level security measure; typically you choose the cloud services you wish to consume, and they will run on hardware shared with other customers.

It is rare to be able to request physical hardware in a cloud environment, because that goes against the virtualization methods that cloud providers use to scale up to many customers. Due to the fact that Azure can't take advantage of the unused capacity on reserved bare metal servers that occur when one app is active and another is not, the Dedicated Hosts option costs more.

This configuration is allocating hardware that may sit idle instead of sharing those CPU cycles with other workloads. Since your virtual compute is not sharing resources with other customers at the physical layer, which is how 99.999% of cloud offerings securely work, you eliminate at least one attack vector. The "cross VM" attack is where the attacker breaks through its own VM into the parent hypervisor layer, finds VM's on the same hardware, and then breaks into those VM's. This type of attack is extremely rare, and I am not aware of any previous documented occurrences at any major cloud provider. This kind of attack presents many challenges and would be highly complex. It is not impossible of course, and your level of risk tolerance should be your guide on whether to mitigate cross-VM attacks or not.

## Zone Redundant ASE

An ASE that is "zone redundant" replicates the VM's underlying your ASE to 3 data centers in the same Azure region. This is a great defense against a single data center's potential failures such as a power outage, or redundant networking failures. This solution does not address regional failures since it does not replicate to other regions, so while it provides enhanced availability as compared to the Dedicated Hosts model, it is not a full disaster recovery solution.

From a security perspective, your VM's might end up on a physical server that hosts other customers' VM's. As discussed above, this does create the potential to exploit the "cross VM" attack vector, however likely or unlikely. But it maintains all the other security features of an ASE. You have to weigh the risks, your risk posture, and other factors such as cost. The trade-off between the two ASE options can be summed up as isolation versus availability.

## Potential Use Cases

If you have highly sensitive data, the "Dedicated Hosts" option is eliminating an attack vector and therefore may be attractive to you. Since there are so many layers and so many attack vectors, you have to make the judgement call if this is one you want or need. Weigh the trade-off of automated zonal redundancy versus isolation and generally higher costs. There are definitely use cases for Dedicated Hosts, but unless you have some very specific security requirements to meet general guidance is that other options (such as Zone Redundant ADE) already provide a sufficiently secure operating environment for your PaaS services.
