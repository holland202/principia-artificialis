# MEM-DECAY-001 S1: SML as an external arm (results, run 2026-11-13)

**Status:** run as registered at `9446808` ([REGISTRATION_S1.md](REGISTRATION_S1.md)), against SML at `6262dbe`
through its public API, with SML unchanged. SELF-TESTED: Claude co-built SML and wrote this arm. **4 of 4 predictions
held, and both controls held.**

- **Determinism:** a second run gave byte-identical output, digest
  `e267ab3429d2927ac232ada3dcbebb5ed3e5d7043227a08ffe958f16de4f0067`.
- **Raw output:** [`results/mem_decay_001/s1.txt`](../../results/mem_decay_001/s1.txt).

## What is weaker than it looks (M8)

- **S1b and S1c were close to certain before running.** At SML's default 30-day half-life, a record 220 days old
  keeps about 0.006 of its score, below the 0.15 threshold. The analytic expectation was written into the
  registration. The run confirms the behaviour of the real code; it does not discover a subtle effect.
- **This is not a defect claim.** SML's default retrieval method, `similarity`, has no decay. The decaying methods are
  a caller's choice.

## Results (50 cases; SML defaults: half_life 30 days, threshold 0.15; top_k 5)

| Call | Old protected critical (220–365 days) | Control A: critical 0–1 days old | Control B: half_life 10¹⁵ s |
|---|---|---|---|
| `retrieve`, `similarity` | 50/50 | 50/50 | 50/50 |
| `retrieve`, `recency` | **0/50** | 50/50 | 50/50 |
| `retrieve`, `importance` | **0/50** | 50/50 | 50/50 |
| `retrieve`, `protected` | **0/50** | 50/50 | 50/50 |
| `recall(key)`, `similarity`: KNOWN | 50/50 | 50/50 | 50/50 |
| `recall(key)`, `recency`: KNOWN | **0/50** | 50/50 | 50/50 |
| `recall(key)`, `importance`: KNOWN | **0/50** | 50/50 | 50/50 |
| `recall(key)`, `protected`: KNOWN | **0/50** | 50/50 | 50/50 |

- **S1a held.** `retrieve` with `similarity` found the old protected record in 50/50 cases.
- **S1b held.** `retrieve` with `protected` found it in 0/50. **SML's retrieval decay undoes its `protected` flag.**
  The `recency` and `importance` methods (no prediction registered) did the same: 0/50.
- **S1c held.** `recall("critical", method="protected")` answered KNOWN in 0/50 cases.

  An unregistered one-case check of the response read
  `{'status': 'UNKNOWN', 'reason': 'insufficient_evidence', 'evidence_ids': []}`, while the record was still stored
  as `current` and `protected`. **The store holds a protected fact and reports that it has no evidence for it.**
- **S1d held.** `recall(key)` with the default method answered KNOWN in 50/50 cases.
- **Controls A and B held.** The protected record is found when it is recent, and when decay is switched off. The
  burying comes from decay, not from anything else.

## What it means for SML (for the owner; SML is not changed)

`protected` currently means "never removed by `compact()`". It does not mean "always retrievable". Under the three
decaying methods, protection and decay pull in opposite directions, and decay wins: an old protected record drops
below the threshold and disappears from both `retrieve` and `recall`. With `recall`, the answer then reads as
"insufficient evidence" rather than "stored but decayed".

**Options, as a decision for the owner, not a recommendation from evidence:**

1. **Exempt protected records from the decay factor** in `_retrieve_from`. That is the pinned-TTL result from
   MEM-DECAY-001 and P6, applied to SML.
2. **Keep the behaviour and document it** in SML's README next to `protected`.
3. **Have `recall` report a distinct reason** when current records for the key exist but fall below the threshold,
   so a decayed fact is not reported as absent evidence.

Any of these would be an SML change with its own registration and tests in the SML repo.

## Doors (M15), unrun

- How many days old a protected record must be before each method loses it at SML's defaults. The threshold alone predicts
  about 81 days for a record at cosine 0.97 (30 · log₂(0.97/0.15)); that is unmeasured.
- The same test against SML's Rust and TypeScript ports, which share the file format.
- An outside person running `sml_arm.py` against the pinned SML commit. CI does not rerun S1: it takes about
  3.7 minutes and needs an SML checkout.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) registered, ran and wrote this on 2026-11-13, at Chad Holland's direction, which
authorized SML as an arm (direction only). Human validation: not performed. Human responsibility: Chad Holland.
