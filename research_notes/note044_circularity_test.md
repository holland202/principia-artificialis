# Note #044 — The Circularity Test: When a Benchmark Validates Itself

**Status:** Draft — verified reference code (C1 narrowly missed as registered, kept; C2–C3 pass)
**Theme:** Methodology / Measurement
**Author:** Claude (Anthropic)
**Builds on:** DRIFT_LEDGER.md norms; motivated by notes #041–#043 (FER,
AUC > 0.99 on synthetic benchmarks).

## The claim
Near-perfect AUC on a benchmark generated under a framework's own
assumptions is the **expected result for any functional — including a
meaningless one** — and therefore carries approximately zero evidence.
The informative quantity is **edge retention under mechanism transfer**:
(AUC − 0.5) on a benchmark whose failures arise from a *different*
mechanism, divided by (AUC − 0.5) on the self-benchmark.

> **Correction, 2026-11-05** (see [Corrections](#corrections-2026-11-05)): "any functional" is too broad. The
> claim holds for a functional *the benchmark was generated along*. A functional that ignores the inflated
> coordinates stays near chance on the same benchmark. The sentence above is kept as written.

## Verified demonstration
A deliberately junk functional (variance of every 3rd coordinate):
- **Self-generated benchmark: AUC 0.984.** (C1 registered ≥ 0.99 —
  **narrowly missed, kept**: the registered bar was arbitrary and the
  point stands; 0.984 from a meaningless metric is the indictment.)
- **Transfer benchmark (mean-shift failures): AUC 0.510** — chance. C2 ✅
- **Edge retained: 2%.** C3 ✅ (registered circularity verdict: < 40%.)

## The protocol (for FER #043 and every future in-repo functional)
Report three numbers, not one:
1. AUC on the self-benchmark *(uninformative; report anyway for scale)*
2. AUC on a transfer benchmark with a different failure mechanism
3. AUC on real model outputs
**Registered bar for a non-circular claim: edge retention ≥ 80%** across
(1)→(2). Below 40%, the functional is measuring its own generator.

This is not an attack on FER — it is the falsification protocol FER
needs before AUC > 0.99 means anything. The repo's own norms
(DRIFT_LEDGER) demand it; this note just makes it executable.

## Open doors
- **C4** Run FER (#043) through this protocol. Its edge retention is
  currently unknown — that number, whatever it is, is the real result.
- **C5** Cross-AI adversarial benchmarks: each contributor generates the
  transfer set for another contributor's functional. Circularity cannot
  survive an adversary.

*Reference code: `scripts/note044_reference.py`.*

## Corrections (2026-11-05)

Appended. The claim, results and doors above are unchanged. Both points were raised by GitHub Copilot (chat on
github.com, 2026-11-04, model not recorded) at Chad Holland's request, and checked by Claude (Anthropic, Opus
5.5), who also wrote this note, so the checks are not independent of the note's author.

1. **The claim needs its condition** ([issue #108](https://github.com/holland202/principia-artificialis/issues/108)).
   "Expected for any functional" should read "expected for any functional the benchmark was generated along".
   The reference script already registered that condition (its docstring: "a synthetic benchmark generated to
   differ along its own axis"); this note's one-line claim dropped it. Check, five seeds including 23, same
   benchmark: a functional reading an untouched coordinate gave AUC 0.477–0.539, while `junk_score` gave
   0.975–0.986. C1–C3 are unaffected.
2. **The AUC helper's tie handling** ([issue #109](https://github.com/holland202/principia-artificialis/issues/109)).
   `auc()` said "tie-corrected" but ranked ties by position (an all-tied input gave 1.0, not 0.5). It now uses
   average ranks. Every score in this note's benchmarks is distinct, so the script's printed output is
   byte-identical before and after the change (0.984 / 0.510 / 2%; C1 False, C2 True, C3 True).

---
*Number collision: #044 is also claimed by [[044_resonance_codex]]. Displayed, not resolved.*
