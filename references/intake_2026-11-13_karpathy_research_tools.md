# November 13, 2026 — public scan and Karpathy research references

**Disposition:** No new candidate met the public scan's research-intake threshold. The Karpathy material came from a separately supplied LinkedIn post and is recorded here as established tooling, teaching material and methodological prior art. This is a documentation record (W9 / C-EXT). Evidence level: primary-source reading. Experimental execution and independent reproduction: none.

## Public scan disposition

The [scan as supplied](../docs/external/chatgpt_research_scan_2026-11-13.txt) is preserved verbatim as UTF-8 without a terminal newline. SHA-256: `d2d0beca8ed310b0049ca43d4e69a8cdcd05fe3e9c9d5cc6716b612c723a3dd0`.

| Item | What the follow-up checked | Disposition |
| --- | --- | --- |
| AgentSafety-Papers | Two commits dated November 13 update the literature index and paper data. The tracker changes alone establish that entries were added or refreshed. [First commit](https://github.com/NY1024/AgentSafety-Papers/commit/d10f08f1eb04471e22299ef1ffd3d2cc5aa04c14) · [Second commit](https://github.com/NY1024/AgentSafety-Papers/commit/800ce99645952bcd0f179237023d731a5a05b6f9) | Index update. |
| IBM agent consistency | IBM's September 15 post distinguishes average success across repeated attempts from the fraction of tasks that succeed on every attempt. The article supplies its own reported results. [IBM Research](https://huggingface.co/blog/ibm-research/altk-evolve-consistency) | Earlier methodological reference. |
| MLCommons AILuminate Safety 1.2.1 | The cited official English (US) results were published October 29. The documented scope is single-turn, English-language text-to-text requests. [MLCommons](https://mlcommons.org/ailuminate/safety/results/) | Earlier benchmark reference. |

ToyBlocks, Cosmos 3, AIPOCH, Ethan Cao's interpretability study, Silent Instrument Errors, OpenRE-Bench, SWE-Time, and earlier MLCommons releases remain duplicate exclusions as reported in the original scan. The scan reports blocked Codeberg access and incomplete coverage of arXiv, peer-reviewed venues and newly published artifacts. The follow-up checked the three named references and did not repeat the search.

## Karpathy source extraction

Source lead: a LinkedIn post attributed in the supplied screenshots to Sushil Pershad. The post's star counts, platform graphics, and promotional descriptions carry no evidentiary weight here. GitHub commit links pin the material that was read.

| Reference | What the primary source documents | Principia Artificialis fit |
| --- | --- | --- |
| **autoresearch** | An agent edits the training file and iterates under a five-minute training budget on one NVIDIA GPU. A fixed validation split supplies the selection score, validation bits per byte (`val_bpb`). The instructions log kept, discarded and crashed attempts in a local TSV that is left untracked. A discarded change can disappear from the active branch while its TSV row remains. [README](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/README.md) · [Experiment instructions](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md) · [Data and evaluator](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/prepare.py) | Closest methodological comparator. The repeatedly consulted validation split guides selection. A separate held-out evaluation and an independently inspected attempt record would be needed for stronger claims. |
| **nanoGPT** | Readable transformer and training loop with a small character-model example. The pinned README marks the project deprecated and points to nanochat as its successor. [README](https://github.com/karpathy/nanoGPT/blob/3adf61e154c3fe3fca428ad6bc3818b27a3b8291/README.md) | Historical teaching reference. |
| **nanochat** | A compact pipeline from tokenization through evaluation and inference. Its advertised budget is an author estimate tied to a GPT-2 CORE benchmark target, runtime and rental rate for an eight-H100 node. The smaller CPU/MPS example uses a different model scale. [README](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/README.md) · [Speedrun script](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/runs/speedrun.sh) | Reference for hardware, metric and cost scoping. There is no PA or Android performance measurement here. |
| **LLM Wiki** | A design note for separating a curated read-only source collection, model-maintained Markdown and a schema for updates. The note describes ingest, query and lint operations. [Gist revision](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f/ac46de1ad27f92b28ac95459c782c07f6b8c964a) | A possible pattern for a derived reference index. Keep source evidence and generated summaries separately traceable. |
| **llm.c** | A C/CUDA pretraining reference with an earlier C CPU implementation and a parallel PyTorch reference. [README](https://github.com/karpathy/llm.c/blob/f1e2ace651495b74ae22d45d1723443fd00ecd3a/README.md) | Useful reading for training internals and comparison against a reference implementation. |
| **micrograd** | A small reverse-mode autodiff engine over scalar operations and a neural-network teaching library. [README](https://github.com/karpathy/micrograd/blob/7bc720e951fe422b8f8814aa5aa1b64121d26b4c/README.md) | Smallest teaching example. A transparent gradient check is a tractable local exercise. |

The useful comparison for [SWAY](../METHOD.md) is whether a fixed-budget search loop still improves an independently scored holdout when every attempt is retained. A future design could compare an adaptive loop with a simple fixed search under matched compute, freeze the evaluator and deciding data, and use a separate holdout for final judgment (C-HOLDOUT). Preserve crashes, ties, reversions and the denominator. This is a candidate question only.

## Provenance

ChatGPT (OpenAI, GPT-6 family, exact variant unavailable) checked public sources, hashed the supplied materials and drafted this note. The scan was supplied by Chad Holland as an earlier ChatGPT research-scan summary. Human validation: not performed. Human editing and curation: Chad Holland provided the sources and direction. Human responsibility: Chad Holland. Review level: direction only.

| Supplied screenshot | SHA-256 of the attachment bytes |
| --- | --- |
| `1000149150.png` | `6485cb88750274e9db9c98f1fb4868d9e0fea2ad8a1bc72d2332916d6e242006` |
| `1000149152.png` | `4f935768bf5c53925323adeb31c542edd6b0339cfeccc23741ce8c1632581acc` |
| `1000149154.png` | `401b2ddf4098e85cd6ba3c91a0db612cc05443661d34600d2e819c4723113719` |
