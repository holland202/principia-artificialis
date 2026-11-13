# MEM-DECAY-001 S1: SML as an external arm (registration, W2)

**Status:** REGISTERED, NOT RUN. Committed before any case was scored. Running SML as an arm was authorized by Chad
Holland on 2026-11-13. SML is used through its public API at the pinned commit
[`6262dbe`](https://github.com/holland202/sovereign-memory-layer/tree/6262dbe362c77e2cf8ecf9c326517c494dc125e8). It is
not modified, and nothing is written to its repository.

**Question.** In MEM-DECAY-001, pure rank decay buried old critical records while pinning protected them. SML has a
`protected` flag. Do its decaying retrieval methods (`recency`, `importance`, `protected`) still bury an old protected
record? And what does SML's key lookup, `recall(key)`, report for such a record?

## Design ([`sml_arm.py`](sml_arm.py))

- **Cases.** 50 cases, seed 20261116. Each case is a fresh `MemoryStore(create=True)` with a fixed clock, holding:
  - 1 protected critical record (weight 1.0, 220–365 days old, embedding very close to the query);
  - 6 newer competitors (0–30 days old, related, different keys);
  - 20 random filler records.

  The embeddings are 384-dimensional synthetic vectors (SML's `DIM`), with the same geometry as MEM-DECAY-001.
- **Calls.** For each of SML's four methods: `retrieve("critical", method=m, top_k=5, embedding=q)` and
  `recall("critical", method=m, top_k=5, embedding=q)`.
- **Parameters.** SML's own defaults: `half_life` 30 days, `threshold` 0.15.
- **Pin check.** The script refuses to run (exit 2) unless the SML checkout is at the pinned commit.
- **Before registering, only a construction smoke check was run.** It built one store and read its records back
  (27 records, critical protected, 300 days old). Nothing was retrieved or recalled.

**Analytic expectation, written before running.** Under `recency`, `importance` and `protected`, SML multiplies
similarity by exp(−ln 2 · age / 30 days). At 220 days that factor is 2^(−7.33) ≈ 0.006. A record scoring about
0.97 × 0.006 falls below the default threshold of 0.15, so it is not returned at all. A competitor 0–30 days old keeps
a factor of 0.5 or more.

## Registered predictions

| ID | Prediction |
|---|---|
| S1a | `retrieve`, method `similarity`, finds the old protected critical record in ≥ 0.95 of cases |
| S1b | `retrieve`, method `protected`, finds it in ≤ 0.05 of cases. **SML's decay undoes the protection at retrieval** |
| S1c | `recall(key, method="protected")` answers KNOWN in ≤ 0.05 of cases. **The record is stored and protected, but recall reports UNKNOWN (`insufficient_evidence`)** |
| S1d | `recall(key)` with SML's default method (`similarity`) answers KNOWN in ≥ 0.95 of cases |

`recency` and `importance` are reported without a prediction.

## Controls (each must HOLD; any FAILED makes the run exit 1)

| Control | Setup | Holds when |
|---|---|---|
| A | Critical record 0–1 days old | `retrieve/protected` finds it in ≥ 0.95 of cases. Shows the method can find a protected record at all |
| B | `half_life` = 10¹⁵ s, so there is no effective decay | `retrieve/protected` finds it in ≥ 0.95 of cases. Shows that decay, not something else, does the burying |

## What this can and cannot show (C-DESIGN, C-INDEP)

- **What it can show:** how SML 6262dbe's public API behaves on these synthetic inputs, at its default parameters.
- **What it is not:** a defect claim. Decay methods are a caller's choice; the default `similarity` method has no
  decay. Whether `protected` should exempt a record from retrieval decay is a design decision for the owner.
- **SELF-TESTED.** Claude co-built SML and wrote this arm, so this is not independent of either.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| C-FEAS | 50 cases, fixed |
| C-NOISE | Deterministic. Seeded, fixed clock, digest recorded |
| C-STAT | Exact counts, fixed thresholds |
| C-EVID | Yes: protection and withdrawal semantics |
| C-INDEP | Self-tested, see above |
| C-EXT | SML is the owner's own public repo, pinned |
| C-DEVICE | Versions printed |
| C-BUILD | Exit 2 if SML is not at the pin; exit 1 on a failed control or a digest mismatch |
| C-EXPLORE | The construction smoke check only |
| C-METHCOMP | Four SML methods on the same cases |
| C-PRIVATE | No: synthetic |
| C-DESIGN | See above |
| C-HOLDOUT | Nothing tuned; SML defaults used as shipped |
| C-SYNTH | Same generator geometry as MEM-DECAY-001, which was already inspected |

## Provenance (M13)

Claude (Anthropic, Opus 5.5) registered this at Chad Holland's direction on 2026-11-13 (direction only). Human
validation: not performed. Human responsibility: Chad Holland.
