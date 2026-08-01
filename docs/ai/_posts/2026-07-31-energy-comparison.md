---
layout: post
title:  "Energy Comparison: CPU, GPU+ML, GPU+LLM"
---

Scaling up automations that will run many times requires looking at total costs.
Here's a way that may save you a fortune in computing costs: don't use AI for everything. Just because 
it can do so much doesn't mean you should be using it for everything. There are limitations of other
computing types, which is why AI exists, but the fallback option to use AI for everything is widespread,
and wasteful.

From my own observations I know that AI and large language models are very energy hungry. We reach for
specialized hardware to run them not because a CPU can't do the job. It can, and Ollama does it every
day. But because a CPU is an order of magnitude too slow at it, we deem it not practical. What I wasn't sure about
was how much more power a large language model actually used.

I discovered that there's a library, `pynvml`, from NVIDIA that would help me measure energy consumption from 
my laptop's GPU, a "value" product a few years ago, GeForce RTX 2050 with 4GB of VRAM. The CPU side turned
out to be measurable too, and more easily than I expected. Intel's chips carry RAPL energy counters, and
Windows exposes them through the built-in `typeperf` utility as an "Energy Meter" performance counter.
There was no kernel driver, no admin rights, and nothing to install.

To have real data to illustrate the concept is extremely valuable. We might run it a 100 times and 
get different answers — and we do. Two identical runs of the language model at temperature zero gave me 98.3%
and 97.0% accuracy, and two identical CPU runs measured 10.6 W and 9.7 W. But a few hundred runs are probably 
directionally correct enough to draw attention to the importance of this decision.

With all of this in mind I asked a powerful language model to build me a test to compare all three.
And I would note for the wise guys like me, generating 3 similar programs for purposes of experimentation
is not a task that a CPU or even regular machine learning would be able to do for me. Definitely not in the 30 
seconds that Fable produced it in!

The task was to analyze text to identify the sentiment of the text. This is a classic machine learning and AI 
play, because the variation in terminology that people can use to express the same sentiment is wide. But 
bear with me, this was just a test that was designed to be able to run in three modes. The real point is, 
there are many use cases that fall in this category.

## CPU-only (VADER rules)

A hand-built lexicon scores each word for sentiment polarity, then heuristic rules adjust for negation, intensifiers, punctuation, and capitalization to produce a compound score. 

## GPU+ML (DistilBERT)

A transformer pre-trained on general text and fine-tuned on SST-2 sentiment data encodes each review into contextual embeddings, then a classification head reads out positive/negative. Batches of 128 sequences run through the GPU as dense matrix math.

## GPU+LLM (prompted model)

Each review gets wrapped in a natural-language instruction ("Classify this as POSITIVE or NEGATIVE") and fed to a general-purpose language model. I ran Ollama locally for this one.

## Counting the CPU in the GPU tests

This is where measuring both sides paid off. A "GPU" workload is never only a GPU workload — something has to
tokenize the text, drive the driver, and in the language model's case run an HTTP client and the server's
scheduling and sampling loops. My first pass reported GPU board power alone, and it undercounted badly.

For DistilBERT the CPU turned out to be 31% of the total power draw. For the language model it was 73% — the
CPU pulled 22 W against the GPU's 8 W. The reason is specific and worth knowing: a 3B model quantized to
Q4_K_M needs about 2.9 GB, and on a 4 GB card that doesn't leave enough room, so Ollama split it 20% CPU /
80% GPU. A fifth of the model was running on the processor the whole time. On a card with enough VRAM to hold
the model outright, this row would look considerably better.

So every number below counts both processors. Each figure is power *attributable* to the run. I sampled an
idle baseline first and subtracted it from both the CPU package and the GPU board, so the machine's resting
draw isn't billed to whichever workload happened to be running. As a sanity check, the CPU-only run measures
-0.1 W attributable on the GPU, which is what a correct subtraction should look like.

## Results

Measured on one laptop, same seeded corpus, on 2026-07-31. Power is sampled throughout every run — NVML at
5 Hz for the GPU, RAPL at 1 Hz for the CPU. Nothing here is modeled, estimated, or cited.

| Approach | Throughput | Power (GPU + CPU) | Energy/item | Per 1M items | vs CPU |
|---|---|---|---|---|---|
| CPU rules (VADER, 1 core) | 25,156 items/s | 0 + 9.5 W | 0.374 mJ | 0.104 Wh | 1× |
| GPU+ML (DistilBERT, batch 128) | 3,555 items/s | 27.0 + 11.9 W | 10.96 mJ | 3.04 Wh | 29× |
| GPU+LLM (llama3.2:3b, sequential) | 2.23 items/s | 8.1 + 22.0 W | 13.46 J | 3.74 kWh | ~36,000× |
| GPU+LLM (llama3.2:3b, concurrency 4) | 6.65 items/s | 19.7 + 43.4 W | 9.49 J | 2.64 kWh | ~25,000× |

Accuracy on an identical 300-review sample: VADER 88.0%, DistilBERT 92.7%, llama3.2:3b 97.0%.

One honest caveat about the accounting. Subtracting idle is an approximation.
If you instead take raw package-plus-board draw with idle included, the CPU row rises to 1.29 mJ and the
sequential language model to 22.7 J, and the ratio between them drops to about 17,700×.
Neither includes PSU losses, RAM, storage, or the screen, so both still understate what a wall
meter would tell you.

And this is one laptop. An RTX 2050 is not a datacenter GPU and a 3B quantized model is not a frontier model.

## Take-away

Four to five orders of magnitude separate the cheapest option from the most expensive one, for the same job on
the same machine. If you take one thing from this, take reaching for a language model by default as a
real decision comes with a real bill attached.

But the more useful finding sits in the middle of the table. DistilBERT is a 67-million-parameter model
fine-tuned for exactly this task, and it landed within about four accuracy points of a 3-billion-parameter LLM
while using more than 1,200 times less energy per review. So the choice isn't really rules versus AI. It's
whether you need a general model that can do anything, or a small specialized one that does your one thing
nearly as well for a rounding error of the cost.

For one of the tests, sending requests one at a time left both
processors idling between them. Running four in parallel cut energy per review by 30% and then stopped
helping. If you self-host and haven't looked at batching,
part of what looks like model cost is really serving cost.

I'd stop short of drawing universal conclusions from one laptop. What my numbers do support is narrower and
more immediate. You pay for electricity, for latency, and for hardware, and on this task the default choice
(use an LLM) was the most expensive one available by roughly four orders of magnitude. Taking time to measure and decide
accordingly could save a scaled-up project a lot of electricity and money in the long run.

See the full repo for this at [github.com/hoopdad/energy-comparison-experiment](https://github.com/hoopdad/energy-comparison-experiment){:target="_blank"}
