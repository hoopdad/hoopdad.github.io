---
layout: post
title:  "Running a Private LLM"
---

This article describes the benefits of running a private Large Language Model (LLM) in a Kubernetes cluster, and provides some Infrastructure as Code to demonstrate how to do this.

## Why Use a Private LLM

There are two primary reasons why one might run their own LLM: Privacy and Cost. 

For some, privacy concerns can be abated by insuring that network connectivity to and from a running LLM is tightly restricted. This is a safeguard for data and Intellectual Property (IP) leakage. If users of a commercial LLM are not careful, the operators of that LLM or bad actors with illegal access may potentially mine chats for IP. For example, someone may paste a large document into a chat to ask a question about it. And if that document contained trade secrets, there is some potential, however small, that someone who should not have access can now see those trade secrets. This has caused many to avoid using an LLM altogether, but a Private LLM may be a viable solution.

The other reason is cost. Rather than paying a managed service for their technical (and human) resources to manage a system, some may find economies of scale in hosting their own. If someone is already running an appropriate environment, it may be less costly to run their own. Using an open source LLM such as DeepSeek or Lllama further reduces cost.

## Components of a Self-hosted LLM Solution

For the example I'm providing to you today, the components that brought this together for me include:

- A container image that runs Ollama
- A Dockerfile to build the container image
- An AWS Elastic Kubernetes Service (EKS) cluster
- EKS Node Groups with GPU access
- An instance of AWS Elastic Container Registry (ECR) for making that image accessible by EKS
- A Helm chart to deploy the image
- Either a user with access to run kubectl from their analytical workstation (example included) or a Helm chart to create an ingress to the service (not part of this example, to keep network security even tighter)
- Terraform to build the EKS cluster, ECR, and Node Groups
- Code to interface with the container image

There's a lot here so let's dive in.

## Container Image and its Dockerfile

We're creating an image based on Ollama. 

```Dockerfile

```