---
layout: post
title:  "Energy Comparison: CPU, GPU+ML, GPU+LLM"
---

Here's a way that may save you a fortunate in computing costs: don't use AI for everything. Just because 
it can do so much doesn't mean you should be using it for everything. There are limitations of other
computing types, which is why AI exists, but the fallback option to use AI for everything is widespread,
and wasteful.

From my own observations I know that AI and large language models are very energy hungry. 
We need specialized computer resources to run them because the usual CPU resources aren't powerful 
enough. But I wasn't sure how much more power that a large language model used.

I discovered that there's a library, `pynvml`, from NVIDIA that would help me measure energy consumption from 
my laptop's GPU, a "value" product a few years ago, GeForce RTX 2050 with 4GB of VRAM. 
To have real data to illustrate the concept is extremely valuable. We might run it a 100 times and 
get different answers. But with just a few runs, or a few hundred runs in this case, are probably 
directionally correct enough to draw attention to the importance of this decision.

With all of this in mind I asked a powerful language model to build me a test to compare all three.
And I would note for the wise guys like me, generating 3 similar programs for purposes of experimentation
is not a task that a CPU or even regular machine learning would be able to do for me. Definitely not in the 30 
seconds that Fable produced it in!

The task was to analyze text to identify the sentiment of the text. This is a classic machine learning and AI 
play, because the variation in terminology that people can use to express the same sentiment is wide. But 
bear with me, this was just a test that was designed to be able to run in three modes. The point is, there are 
many use cases that fall in this category.

## CPU-only (VADER rules)

A hand-built lexicon scores each word for sentiment polarity, then heuristic rules adjust for negation, intensifiers, punctuation, and capitalization to produce a compound score. 

## GPU+ML (DistilBERT)

A transformer pre-trained on general text and fine-tuned on SST-2 sentiment data encodes each review into contextual embeddings, then a classification head reads out positive/negative. Batches of 128 sequences run through the GPU as dense matrix math.

## GPU+LLM (prompted model)

Each review gets wrapped in a natural-language instruction ("Classify this as POSITIVE or NEGATIVE") and fed to a general-purpose language model. I ran Ollama locally for this one.

## Results

All four rows below were measured on the same laptop, same seeded corpus, on
2026-07-31. Power is sampled throughout each run — NVML at 5 Hz for the GPU,
Intel RAPL at 1 Hz for the CPU. Nothing here is modeled or cited.

| Approach | Throughput | Power | Energy/item | Per 1M items | vs CPU |
|---|---|---|---|---|---|
| CPU rules (VADER, 1 core) | 25,260 items/s | 9.7 W | 0.384 mJ | 0.107 Wh | 1× |
| GPU+ML (DistilBERT, batch 128) | 3,573 items/s | 35.9 W | 10.03 mJ | 2.79 Wh | 26× |
| GPU+LLM (llama3.2:3b, sequential) | 2.22 items/s | 11.9 W | 5.348 J | 1.486 kWh | 13,913× |
| GPU+LLM (llama3.2:3b, concurrency 4) | 6.60 items/s | 25.0 W | 3.786 J | 1.052 kWh | 9,849× |

Accuracy on an identical 300-review sample: VADER 88.0%, DistilBERT 92.7%,
llama3.2:3b 97.0%.

Two caveats worth stating out loud. The CPU figure is power *attributable* to
the work (package draw minus idle baseline); the GPU figures are total board
power including idle. Using the CPU's un-subtracted package power instead
would put the sequential LLM at 4,806× rather than 13,913× — a 2.9× swing from
accounting choice alone. And this is one laptop: an RTX 2050 is not a
datacenter GPU and a 3B quantized model is not a frontier model. The shape of
the result travels; the magnitudes do not.

## Take-away

Four orders of magnitude separate the cheapest option from the most expensive one, for the
same job on the same machine. If you take one thing from this, take that: reaching for a
language model by default is a real decision with a real bill attached.

But the more useful finding sits in the middle of the table. DistilBERT is a 67-million-parameter
model fine-tuned for exactly this task, and it landed within about four accuracy points of a
3-billion-parameter LLM while using 533 times less energy per review. So the choice isn't really
rules versus AI. It's whether you need a general model that can do anything, or a small
specialized one that does your one thing nearly as well for a rounding error of the cost.

Some of that gap was my own doing, and it's worth admitting. Sending requests one at a time left
the GPU idling between them. Running four in parallel cut energy per review by 29% and then
stopped helping, because Ollama defaults to four parallel requests. If you self-host and haven't
looked at batching, part of what looks like model cost is really serving cost.

I'd stop short of drawing planetary conclusions from one laptop. This was a 3B model on a
value-tier GPU running a small synthetic task; a frontier model in a datacenter is a different
animal, and the published studies linked in the repo are better evidence for that argument than
my numbers are. What my numbers do support is narrower and more immediate: you pay for
electricity, for latency, and for hardware, and on this task the default choice was the most
expensive one available by a factor of roughly ten thousand.

See the full repo for this at [github.com/hoopdad/energy-comparison-experiment](https://github.com/hoopdad/energy-comparison-experiment){:target="_blank"}
