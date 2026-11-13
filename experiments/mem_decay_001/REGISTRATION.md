# MEM-DECAY-001: registration (W2)

**Status:** REGISTERED, NOT RUN. This file and the code it names were committed before any metric was computed on
either split. Results go in a separate `RESULTS.md`. This file is not edited after the run; any change is a dated
amendment appended at the end (M12).

**Question.** On one frozen synthetic store, does *reversible rank decay* suppress stale records as well as
destructive TTL/LRU deletion? Does it keep critical constraints retrievable? Or does a simpler rival, TTL with
critical records pinned, explain any advantage?

**Source:** the proposal [`docs/proposals/MEM-DECAY-001_PROPOSAL_2026-11-13.md`](../../docs/proposals/MEM-DECAY-001_PROPOSAL_2026-11-13.md)
and the intake note [`references/intake_2026-11-13_ai_memory_growth_decay.md`](../../references/intake_2026-11-13_ai_memory_growth_decay.md).

## Design as implemented ([`memdecay.py`](memdecay.py))

### Store

Every record has:

- a unit vector (d = 32);
- an age and an access age, in days;
- a critical flag;
- a status: current, superseded or revoked.

The vectors are synthetic. No embedding model is called.

| Category | Built as | Success counted when |
|---|---|---|
| current | One record near the key | It is in the top-5 |
| stale | An old value (200–365 days) placed very close to the query, plus a new value (0–60 days). Even items: the old value is linked as superseded. Odd items: no link | The new value is in the top-5, and the old one is absent or ranked below it |
| contradictory | Two current values, no link, ages 0–365 | Both are in the top-5 |
| critical | One critical record, 220–365 days old, never accessed since it was written, very close to the query. Plus 6 newer related records (0–30 days) with different keys | The critical record is in the top-5 |
| revoked | A revoked record (30–365 days) very close to the query, plus a newer replacement | Leak: the revoked record is in the top-5. **Lower is better** |
| adversarial | A target (150–365 days) very close to the query, plus 6 newer distractors (0–30 days) with different keys | The target is in the top-5 |

Plus unrelated filler records with random vectors.

| Split | Seed | Queries per category | Filler | Records |
|---|---|---|---|---|
| dev | 20261113 | 50 | 500 | 1,550 |
| test | 20261114 | 200 | 2,000 | 6,200 |

### Arms

All arms use the same budget: top-k = 5.

| Arm | Rule |
|---|---|
| A0 | No decay: cosine similarity over everything |
| A1 | TTL: delete age > T, rank by similarity |
| A2 | LRU: keep the N = ⌊store/2⌋ most recently accessed, delete the rest |
| A3 | Reversible rank decay: score = sim · exp(−ln 2 · age / h). Nothing is deleted |
| A4 | Pinned TTL (simplest rival, M14): A1, but critical records are never deleted |

**Guard:**

- G0: status is ignored at retrieval, so soft revocation is not enforced.
- G1: only `current` records can be returned.

**Rules, not tuned values:** T = median record age of the split, h = T, N = half the store. A1 and A2 therefore
delete the same half. Nothing is tuned on dev. Dev is a smoke run only.

### Seals

These were computed with `memdecay.py seal`, which builds the split and prints its size and T. It scores nothing.

| Split | T = h | SHA-256 |
|---|---|---|
| dev | 46.7883 days | `e75ebc4f8328e95b2049b3330905e5d01da1ec0ce8fe5e44378d00668f85189f` |
| test | 48.9186 days | `7753da049bef7f4514d0737b203f91ca16850634f5e22ba83a6f579be9b1d338` |

The registered run must reproduce the test seal. If it does not, it exits 2 when given `--expect-seal`.

## What was looked at before registering (C-EXPLORE, C-SYNTH)

- **Property tests.** Twelve spec-derived property tests were run, with no answer key and no registered metric.
  Mutants M1–M7 were each caught. M8 (the Wilson end fix reverted) was an equivalent mutant, because a second clamp
  gives the same result. M8b, with both clamps removed, was caught.
- **A bug found and fixed before registration.** The Wilson lower bound came out about 5.6e-17 instead of 0 at k = 0.
- **Generated dev inputs were inspected:**
  - Ages and cosine similarities by role.
  - Stale, critical, revoked and adversarial records sit at cosine ≈ 0.97 to their query. Normal targets sit at ≈ 0.73.
  - Critical competitors sit at ≈ 0.91.
  - Filler ranges from −0.60 to 0.62.
- **T is set by the store's composition.** The 600 young competitors and distractors (dev) pull the median age to
  about 47 days. As a result, A1 deletes about half of ordinary targets and 87% of filler.
- **That is a property of this generator, not of real stores.** T = background-only median is left as a door (P6).
- **No arm was scored on either split.**

## Registered predictions (test split, G1 unless stated)

The exact expressions are in `predictions()` in `memdecay.py`.

| ID | Prediction | Why it is informative |
|---|---|---|
| P1 | A1 critical ≤ 0.05 **and** A4 critical ≥ 0.95 | Instrument check: TTL must lose old critical records and the pin must keep them. Partly true by construction |
| P2 | A3 stale ≥ A1 stale − 0.05 | Non-inferiority: keeping everything and only down-ranking suppresses stale values at least about as well as deleting them |
| P3 | A3 critical < A4 critical − 0.05 | **The discriminating one.** Pure decay loses old critical records once newer related records compete, and pinning does not. If this is refuted, decay alone keeps critical constraints |
| P4 | Under G0, the A0 and A3 revoked-leak rates are > 0.5. Under G1, the leak rate is 0 for every arm | Small-scale echo of arXiv:2609.08258: soft revocation leaks unless retrieval filters it |
| P5 | A0 adversarial ≥ 0.95 **and** A3 adversarial < A0 − 0.05 | The cost of decay: old, correct targets lose to newer look-alikes |

**Measured, with no prediction:** current-fact recall, contradictory both-surfaced, and the fraction of the store
kept.

## Negative controls (each must HOLD; any FAILED makes the run exit 1)

| ID | Control | Holds when |
|---|---|---|
| NC1 | Ages and access ages shuffled across records | \|A3 − A0\| on stale is ≤ 0.05. Any decay advantage must come from age |
| NC2 | h = ∞ | A3 top-5 lists are identical to A0's on every query |
| NC3 | A guard that passes everything | The revoked leaks equal G0's exactly, for every arm |
| NC4 | Critical records made recent (0–30 days) | A1 critical ≥ 0.95 |

**Sabotage (`--sabotage`).** G1 is replaced by G0. P4 must be REFUTED, NC3 must report FAILED, and the run must exit 1.

## Door (M15), left unrun

**P6.** Rerun with T taken from filler (background) ages only, and with filler ×4 (store growth). Does P3 still hold
when T is longer than the age gap between critical records and their competitors?

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility (C-FEAS) | Yes: synthetic, so counts are set by construction (200 per category on test) |
| Noise (C-NOISE) | Yes: deterministic. The seed is fixed, there is no sampling at scoring time, and the seal and digest are recorded. A same-input rerun must give an identical digest |
| Statistics (C-STAT) | Yes: exact counts with Wilson 95% intervals. Thresholds are fixed above. Fixed sample, no stopping rule |
| Evidence (C-EVID) | Yes: freshness (stale) and withdrawal (revoked) handling are the subject |
| Independence (C-INDEP) | Yes: Claude wrote the generator, the arms, the scorer and the predictions. Results are SELF-TESTED. Independent reproduction means someone else running the sealed test |
| External (C-EXT) | Yes: the design comes from the intake note's sources. The arms re-implement generic rules, not any vendor system |
| Device (C-DEVICE) | Yes: Python and numpy versions are printed. An S25 rerun would be reported separately |
| Verdict code (C-BUILD) | Yes: exit 2 on an integrity-gate failure or a seal mismatch; exit 1 on a failed control or a digest mismatch |
| Exploration (C-EXPLORE) | Yes: disclosed above. No arm was scored before this commit |
| Method comparison (C-METHCOMP) | Yes: five retrieval policies at an equal top-k budget, with the simplest rival (A4) included |
| People's data (C-PRIVATE) | No: synthetic records only |
| Design (C-DESIGN) | Yes: a synthetic benchmark. The strongest claim it can carry is "for this generator and these vectors". It says nothing about real embeddings, real stores or users |
| Held-out (C-HOLDOUT) | Yes: nothing is tuned. Dev is a smoke run; the sealed test split is scored once |
| Generated inputs (C-SYNTH) | Yes: inspected above. The integrity gate checks counts, unit vectors, the revoked count, and that every critical record is older than T |

## Pre-mortem

How could this be wrong in a way the controls would miss?

1. **P3 may be decided by my choice of 6 competitors and h = T ≈ 49 days.** At 220+ days, decay multiplies a critical
   record's score by at most 2^(−220/49) ≈ 0.04. The result is about this setting, which is why P6 exists.
2. **The stale-success rule rewards deleting the old value.** A1 and A3 can both score well for different reasons.
3. **Synthetic cosine geometry is not real embedding geometry.** Nothing here transfers to a real model without a rerun.

## Deviations from the proposal

- **Synthetic vectors, not a pinned embedding model.** Nothing to download, fully deterministic, but narrower in what
  it can claim.
- **No parameters are tuned on dev.** T, N and h are rules.
- **Competitors and distractors added** to the critical and adversarial categories, plus P5.
- **Outcomes are defined in code.**

## Provenance (M13)

Claude (Anthropic, Opus 5.5) designed the build and wrote `memdecay.py`, the tests and this registration, after Chad
Holland's direction on 2026-11-13 to take the growth-and-decay line forward and to choose the scope. Human
validation: not performed. Human editing and curation: direction only. Human responsibility: Chad Holland.
