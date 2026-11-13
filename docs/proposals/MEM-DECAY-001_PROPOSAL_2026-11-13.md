# MEM-DECAY-001: Does reversible memory decay improve retrieval without losing critical information?

> **PROPOSED / NOT REGISTERED / NOT RUN.** This is a design for owner review. It is not a W2 registration, it has
> no code, and it has no results. Nothing in it may be cited as a finding. Running it needs separate authorization.
>
> **Source:** the intake note for "Growth and Decay in AI Memory"
> ([`intake_2026-11-13_ai_memory_growth_decay.md` at `e580a63`](https://github.com/holland202/principia-artificialis/blob/e580a6371a4ab862f2b3bb42df0ceadb4ec0c9d9/references/intake_2026-11-13_ai_memory_growth_decay.md),
> draft PR #138).

## Why this question

The synthesis recommends that agent memory stores implement decay as "reversible rank demotion" rather than
"destructive TTL/LRU deletion". None of the sources it cites tests that comparison:

- FadeMem's baselines are FIFO windows, LangChain memory, Mem0 and MemGPT.
- DMF has no decay ablation.

The closest prior work found, MaRS/FiFA (arXiv:2512.12856), compares Priority Decay with LRU and FIFO on narrative
coherence. It also argues that LRU is near-optimal when usefulness decays exponentially with age. Vendor guidance
(Mem0) already recommends a "salience floor" so important facts cannot be pruned on time alone.

So the open question is narrow:

- whether keeping everything and decaying only the ranking beats deletion on stale-fact suppression and on keeping
  critical constraints;
- whether it beats the cheaper fix of pinning critical items and deleting the rest.

This is a question to answer, not a new architecture.

## Arms (equal retrieval budget)

All arms share:

- the same frozen store and frozen query set;
- the same embedding vectors (precomputed, hashed);
- the same similarity function, the same top-k and the same score threshold.

| Arm | Rule | Deletes records? |
|---|---|---|
| A0 no decay | Rank by similarity only | No |
| A1 TTL | Delete records older than T, then rank by similarity | Yes |
| A2 LRU | Keep the N most recently accessed records (from a frozen access trace), delete the rest, rank by similarity | Yes |
| A3 reversible rank decay | Score = similarity × exp(−ln 2 · age / h). Nothing is deleted | No |
| A4 pinned TTL (simplest rival, M14) | A1, except records marked critical are never deleted | Yes, except pinned |

- **Matched deletion.** T and N are set so that A1 and A2 delete the same fraction of the store. Storage kept is
  reported as a secondary outcome. A3 keeps everything; that is its cost.
- **Arm A4 was added by Claude**, not by the owner's request. A3 might beat A1 and A2 only because critical items
  survive. If so, pinning gets the same result without keeping everything, and A4 is the test of that.
- **Revocation guard, crossed with every arm:** G0 off, or G1 on. G1 drops records marked revoked or superseded at
  retrieval time. That makes 10 configurations.

## Frozen dataset (synthetic; C-SYNTH)

The dataset comes from a seeded generator and is written once. Each category has an equal count, fixed after the
feasibility step (C-FEAS):

| Category | Construction | Correct retrieval |
|---|---|---|
| Current facts (control) | One current value per key | Value in top-k |
| Stale | Older value plus a newer replacement. Half have a supersession link, half do not | Current value ranked above the stale one, or stale absent |
| Contradictory | Two current values with no link | Both surfaced, or flagged; neither silently chosen |
| Critical constraints | Old, rarely accessed, marked important (for example "allergic to X", "never deploy on Fridays"). Queried late in the trace | Constraint in top-k |
| Revoked | Soft-revoked record plus a replacement | Revoked record not returned |
| Adversarial | Distractors sharing vocabulary with the target; paraphrased queries with no word overlap; a forged future timestamp; near-duplicate keys (NFC/NFD) | Target in top-k, ranked above the distractor |

**Generated inputs are looked at before sealing (C-SYNTH).** A sample of every category is printed and read. A
checker-free integrity gate runs: counts per category, no key collisions across categories, and every critical
item older than T, so A1 can lose it. Then the test split is hashed.

**Embeddings.** SML's `hash_embedding` is lexical, so it cannot test paraphrase or neighbourhood effects. Vectors
come from one pinned small embedding model, computed once and stored with their hash. The model and its version are
recorded (C-DEVICE).

## Decide on one split, judge on another (C-HOLDOUT)

- **Dev split:** chooses T, N, h, the threshold and top-k. It can be inspected freely.
- **Test split:** generated with a different seed and sealed by SHA-256 before any arm sees it. It is scored once.
  No parameter changes after unsealing; any change is a new registration.

## Outcomes

- **Primary**, each an exact count on the test split, with a Wilson 95% interval:
  - **CR (critical retention):** the share of critical-constraint queries whose constraint is in top-k.
  - **SS (stale suppression):** the share of stale queries where the current value outranks the stale one.
  - **RL (revocation leak):** the share of revoked-target queries that return the revoked record.
- **Secondary:** precision@k on current facts; adversarial pass rate; storage kept; contradiction handling.

## Candidate predictions (illustrative; to be fixed with δ and n at registration)

| ID | Prediction | Note |
|---|---|---|
| P1 | A3 CR = 1.0 on test; A1 CR < 1.0 | Partly true by construction, because critical items are older than T. It confirms that the instrument works; it is not a finding |
| P2 | A3 SS is no worse than A1 SS by more than δ (non-inferiority) | The real cost question for keeping everything |
| P3 | A4 matches A3 on CR and SS within δ | **The discriminating prediction.** If it holds, reversible decay adds nothing beyond pinning |
| P4 | Under G0, RL > 0 in every arm that keeps revoked records; under G1, RL = 0 in every arm | Small-scale replication of arXiv:2609.08258's store-level filter result |
| P5 (door, M15) | How CR and SS change when the store grows 10× with the same queries | Left unrun |

## Negative controls (each must be able to flip a verdict)

1. **Shuffled ages.** Randomise timestamps across records. A3's stale-suppression advantage over A0 should vanish.
   If it persists, the advantage was not coming from age.
2. **h → ∞.** A3 must produce byte-identical rankings to A0. This shows the comparison can return "no difference"
   (M3).
3. **Sabotaged guard.** A G1 that passes everything must give the same RL as G0. Otherwise the RL metric is not
   reading the guard.
4. **Recent critical items.** Make critical items recent and frequently accessed. A1 and A2 CR should rise to 1.0.
   That shows their losses came from age and access, not from a bug.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility (C-FEAS) | Yes: the per-category count is fixed from a dry count on dev before registration |
| Noise (C-NOISE) | Yes: same-input reruns must give byte-identical scores; embeddings are precomputed, so no model is called at scoring time |
| Statistics (C-STAT) | Yes: exact counts, Wilson intervals, δ and n registered in advance, fixed sample, no optional stopping |
| Evidence (C-EVID) | Yes: the stale and revoked categories test whether a store handles freshness and withdrawal |
| Independence (C-INDEP) | Yes: Claude would write the arms, so its own results are SELF-TESTED. Independent reproduction needs someone else to rerun the sealed test |
| External (C-EXT) | Yes: the design draws on the intake note and the papers it cites; the decay arms re-implement published formulas, they are not copies of those systems |
| Device (C-DEVICE) | Yes: the embedding model and version, Python version and platform are recorded; S25 runs reported separately |
| Verdict code (C-BUILD) | Yes: the scorer exits 2 (COULD NOT SCORE) on a missing split, a hash mismatch or an empty category |
| Exploration (C-EXPLORE) | Yes: any dev-split exploration is disclosed; nothing runs on test before sealing |
| Method comparison (C-METHCOMP) | Yes: five retrieval policies compared at equal retrieval budget, with the simplest rival (A4) as an arm |
| People's data (C-PRIVATE) | No: synthetic records only, no real user memories |
| Design (C-DESIGN) | Yes: a synthetic benchmark comparison. The strongest claim it can carry is "on this generated set, with these embeddings". It says nothing about production stores or users |
| Held-out (C-HOLDOUT) | Yes: dev chooses, sealed test judges |
| Generated inputs (C-SYNTH) | Yes: samples read and an integrity gate run before sealing |

## Possible later use (not authorized)

SML's public API already has the parts needed to run it as an extra arm without changing it:

- a retrieval-time status filter;
- `recency` and `importance` methods with exponential score decay;
- destructive `compact()` that never removes protected chains.

Running SML in this study, or changing it, needs the owner's separate authorization.

## Provenance (M13)

The question and arms A0–A3 came from Chad Holland's request. Claude (Anthropic, Opus 5.5) drafted the design, added arm A4 and the
negative controls, and chose the outcome definitions. No code was written and nothing was run. Human validation:
not performed. Human editing and curation: direction by Chad Holland. Human responsibility: Chad Holland. Review
level: direction only.
