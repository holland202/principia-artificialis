# HyDE retrieval for PA research evidence — separate exploratory opportunity

**Status:** SPECULATIVE / EXPLORATORY PROPOSAL / NOT REGISTERED / NOT RUN. **No retrieval benchmark or LLM-generation run has been authorized or performed.** This file does not amend the results or preregistration of Note #061.
**Origin:** Owner-supplied screenshots of two public LinkedIn discussions (AI documentation reliability; RAG versus HyDE), used as prompts for questions, **not** scientific evidence. The posts are paraphrased here without reproducing or attributing unverifiable passages. External academic reference: Luyu Gao, Xueguang Ma, Jimmy Lin and Jamie Callan, *Precise Zero-Shot Dense Retrieval without Relevance Labels*, ACL 2023, https://aclanthology.org/2023.acl-long.99/ . Full paper and LinkedIn material have not been archived into this repo; citation is prior-art direction, not independent reproduction or methodological adoption.
**Authoring/provenance:** Owner Chad Holland directed preservation of the opportunity. ChatGPT (OpenAI GPT-6) formulated this proposal after source-reading existing PA Note #061; human review: direction only; no human technical validation established.

## Why the question belongs here

[Research Note #061](../research_notes/note061_toc_retrieval_signal.md) already tested flat TF-IDF and table-of-contents narrowing on a pinned 83-file corpus, **with refutations retained**. Its best-looking post-hoc narrowing width is exploratory, not a confirmed improvement. It also leaves paraphrased queries unrun. This proposal asks a different question: whether constructing a *hypothetical answer-shaped search query* helps recover the correct PA research records when the original query is a natural-language question rather than copied text.

The cited HyDE method generates a hypothetical document from a query, embeds that synthetic document, and uses the embedding to find real source documents. Generated text is **query material**, never a quote, evidence, experiment result, or authority. Embeddings do not guarantee removal of hallucinated details.

## Proposed comparison — design only

Under a **new, separate W2 registration**, use a frozen, source-identified **public-only** document corpus and independently constructed human information needs (not copied source sentences). Compare under a predefined shared query budget:

1. Existing flat lexical TF-IDF baseline (comparable to Note #061's FLAT arm, without recycling its old results).
2. Direct semantic embedding retrieval (same encoder and index budget as the HyDE arm).
3. HyDE-generated hypothetical-document embedding retrieval, with the generating model/version/prompts pinned.
4. Optional lexical+dense hybrid, preregistered before results if studied.

Register a primary metric (for example Recall@1 or Recall@k), relevance-label creation independent from the retrieving model, exclusion counts, prompts, token/cost/latency budget, exact estimator, uncertainty bounds and stopping rule. Use a holdout set of fresh questions; handle shared queries with paired comparison methods. Pre-register negative controls including a deliberately irrelevant hypothetical document and an answer/source mismatch. Preserve cases where HyDE confidently retrieves irrelevant evidence. **Do not** use generated answers as ground truth.

**Potential falsifier:** At equal evidence corpus and matched budgets, HyDE does not outperform direct embedding retrieval under the registered uncertainty criterion, or its additional unsupported-context errors exceed a preregistered bound. These are proposed decision directions, not frozen thresholds or registered predictions.

## SWAY gates before research execution

This is a W9 documentation record, **not** W2 registration. Before any study, apply [METHOD.md](../METHOD.md) M1–M18, [WORKFLOW.md](../WORKFLOW.md) W1–W9, and the full [CONTROLS.md](../CONTROLS.md) trigger table. Likely triggers include C-FEAS (query/corpus eligibility counts), C-STAT, C-NOISE (generated-document variability), C-EXT (paper and outside sources), C-BUILD (scoring gates), C-EXPLORE (any prompt/pipeline tuning), and C-INDEP **if** independence or replication is claimed. Reassess C-DEVICE, C-EVID and C-METHCOMP according to their precise triggers at registration rather than assuming all apply.

**Unrun next test:** Can HyDE outperform direct semantic search on a held-out set of independently drafted PA questions under a matched budget while leaving source attribution and error rates intact? This remains a research door, not a deployment recommendation. No code, indexes, dashboards, permissions, or live AI research assistant is changed by this proposal.
