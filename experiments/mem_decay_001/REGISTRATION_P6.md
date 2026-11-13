# MEM-DECAY-001 P6: registration (W2)

**Status:** REGISTERED, NOT RUN. Committed before any metric was computed on the P6 split. This is the door left open
in [REGISTRATION.md](REGISTRATION.md) (P6) and in [RESULTS.md](RESULTS.md). The original registration and results
are not edited.

**Question.** In the first run, T = h came out at about 49 days. That was set by the many young
competitor/distractor records, not by the background store. With T taken from background ages and 4× the filler,
two things are open:

- Does pure rank decay still lose old critical records?
- Does it still suppress stale values worse than TTL?

At what half-life does decay start keeping critical records?

## What changes, and what does not ([`memdecay_p6.py`](memdecay_p6.py))

**Unchanged.** `memdecay.py`, imported as is:

- the generator;
- the six categories and their success rules;
- the arms A0–A4;
- the guard (G0/G1);
- top-5;
- the Wilson intervals.

The registered test run still reproduces its digest `b94971e4…d53d`.

**Changed:**

| | First run | P6 |
|---|---|---|
| Split | seed 20261114, 2,000 filler | seed 20261115, 200 queries per category, **8,000 filler** |
| Records | 6,200 | 12,200 |
| T = h | Median age of the whole store | **Median age of filler records only:** 182.1826 days (the whole-store median is 134.7245) |
| N (LRU) | Half the store | **As many records as TTL keeps:** 7,211, so deletion stays matched. Half the store would no longer match TTL here |
| Sweep | — | A3 alone at h = T × {1, 2, 4, 8, 16, 32}, guard G1: critical, stale and current recall |

**Seal:** `c2a17dc734a1b3b42be80468682d79c23efe32f7ce7564348798d4524c81e583`. It was computed with `seal`, which
prints the store size and T and scores nothing.

## What was looked at before registering

- The seal output: sizes and T.
- A check that LRU now keeps exactly as many records as TTL (7,211 each), and that the records it keeps are the most
  recently accessed.
- **An analytic estimate, written down before running.** A critical record (cosine ≈ 0.97, age a) only outscores a
  typical competitor (cosine ≈ 0.91, age ≈ 15 days) when h > (a − 15) / log₂(0.97/0.91). That is about 2,225 days at
  a = 220, 3,007 at a = 292 and 3,799 at a = 365. T × 4 ≈ 729 and T × 32 ≈ 5,830.

No arm was scored on the P6 split.

## Registered predictions (guard G1)

| ID | Prediction | Why |
|---|---|---|
| P6a | A3 critical ≤ 0.05 at h = T | Even at a background half-life (~182 days), decay should still bury 220–365-day-old critical records under 6 fresh related records. If refuted, the first run's P3 was an artifact of the short T |
| P6b | A3 stale ≥ A1 stale − 0.05 | At a half-life ~4× longer, new values (0–60 days) keep most of their score, so P2's failure should not recur. If refuted, decay's stale cost is not just a short-h effect |
| P6c | A3 current < A0 current − 0.05 | Decay still costs recall of old ordinary facts against young background noise |
| P6d | A3 critical ≤ 0.05 for every h ≤ 4T, **and** ≥ 0.95 at h = 32T | From the analytic estimate. It is partly true by construction, so it checks the instrument and the arithmetic, not a finding about memory. 8T and 16T are reported without a prediction |

**Control:** NC2. h = ∞ must give A3 rankings identical to A0's on every query, otherwise the run exits 1. The NC1
from the first run is not reused, because it was mis-specified (see RESULTS.md); a corrected version needs its own
registration.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility (C-FEAS) | Yes: counts fixed by construction |
| Noise (C-NOISE) | Yes: deterministic. The seal and digest are recorded, and a rerun must match |
| Statistics (C-STAT) | Yes: exact counts and Wilson intervals, fixed thresholds |
| Evidence (C-EVID) | Yes: freshness and withdrawal handling |
| Independence (C-INDEP) | Yes: SELF-TESTED. Claude wrote everything |
| External (C-EXT) | No new outside material |
| Device (C-DEVICE) | Yes: versions printed |
| Verdict code (C-BUILD) | Yes: exit 2 on a gate failure or a seal mismatch; exit 1 on a failed NC2 or a digest mismatch |
| Exploration (C-EXPLORE) | Yes: disclosed above. This design follows a completed, published run, so the predictions are informed by it |
| Method comparison (C-METHCOMP) | Yes: the same five arms at an equal top-5 |
| People's data (C-PRIVATE) | No: synthetic only |
| Design (C-DESIGN) | Yes: synthetic benchmark; claims are limited to this generator |
| Held-out (C-HOLDOUT) | Yes: a new seed, nothing tuned |
| Generated inputs (C-SYNTH) | Yes: same generator as before, which was already inspected; only the filler count and seed change |

## Pre-mortem

1. **P6a and P6d rest on 6 fresh competitors per critical record.** With fewer competitors, a critical record could
   survive at shorter h. Competitor count is a door.
2. **Matched deletion now uses a different N rule from the first run**, so A2 is not directly comparable across the
   two runs.
3. **With 8,000 random filler, some filler lands close to queries by chance.** That lowers the current-fact
   baseline for every arm equally.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) designed and registered this at Chad Holland's direction on 2026-11-13 (direction only).
Human validation: not performed. Human responsibility: Chad Holland.
