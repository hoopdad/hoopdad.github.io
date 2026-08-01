---
layout: post
title:  "Energy Comparison: CPU, GPU+ML, GPU+LLM"
---

Use the right tool for the job. With computing resources, the cost difference alone can be
dramatic.

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

| Approach | Throughput | Power | Energy/item | Per 1M items | vs CPU |
|---|---|---|---|---|---|
| CPU rules (VADER, 1 core) — measured | 25,239 items/s | 6 W | 0.24 mJ | 0.066 Wh | 1× |
| GPU+ML (DistilBERT, T4) | ~1,581 items/s | 70 W | 44 mJ | 12.3 Wh | ~186× |
| GPU+ML (DistilBERT, A100) | ~11,963 items/s | 400 W | 33 mJ | 9.3 Wh | ~141× |
| GPU+LLM (self-hosted ~8B, batched) | — | — | ~112 J | ~31 kWh | ~470,000× |
| GPU+LLM (frontier API query) | — | — | 1,080–3,600 J | 300–1,000 kWh | ~4.5M–15M× |

## Take-away

The results show the hyperbolic escalation in power consumption. With the world energy crisis, 
increasing pushback against data center projects, and the fact that you pay for electricity,
picking the right path is critical for sustainability of the earth as well as your business.

See the full repo for this at [github.com/hoopdad/energy-comparison-experiment]](https://github.com/hoopdad/energy-comparison-experiment){:target="_blank"}
