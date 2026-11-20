# TINY-ENGINE-004 registration: position coupling, with its hint isolated

**Status:** REGISTERED, NOT RUN on seeds 21–26. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-20). Design and code: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## Why

Version 3 ([RESULTS_003.md](RESULTS_003.md)) still fails heavy repeats. With an 8-symbol alphabet, no 63-token copy
the model wrote alone was exactly right (0.00 in every seed), and 127-token copies scored 0.5680–0.7018 per token.

Position coupling (Cho et al., "Position Coupling: Improving Length Generalization of Arithmetic Transformers Using
Task Structure", arXiv 2405.20671, appendix B.7) reports near-perfect length generalisation on copying 10-symbol
strings. It gives each answer token the same position id as the source token it copies.

## A fair comparison (the design rule this run follows)

Coupling changes two things at once: (1) matched position ids, and (2) the model being told which tokens are the
answer. A win could come from either. So there are three arms, all on the same seeds and cases:

| Arm | Config | What it adds over the arm above |
|---|---|---|
| A | `CFG3` (version 3) | — |
| B | `CFG4B` | a learned label on every token after SEP ("this is the answer"); 256 parameters |
| C | `CFG4C` | the same label, plus coupled position ids in the rotary layer 0; no further parameters |

- **C vs B isolates coupling.** Same parameters, same label, same initial weights; only the position ids differ.
- **B vs A isolates the label.**
- **Coupled ids** (`engine.answer_layout`) are computed from the input tokens alone, never from targets: in a row
  containing SEP at position s, SEP gets id 0 and the token at s + j gets id j, so answer token i shares source token
  i's id. Rows without SEP (the pattern and look-up tasks) keep ordinary ids.
- **Old configs unchanged:** `CFG`, `CFG2` and `CFG3` trained 30 steps with the old and new `engine.py` give identical
  weights. The new embedding is created last, so A, B and C start with identical shared weights for a seed.

**Limit of the method, stated now:** coupling needs the input to say where the answer starts (SEP). It is a hint
about task structure, not a general ability. It does nothing for inputs without SEP.

## Exploration (C-EXPLORE: seen before registering)

One seed, 903, shared by all three arms; case seeds offset by 20000. Predictions were written beforehand in
`results/tiny_engine/004/exploration/PREMORTEM.md`.

| Score | A | B | C |
|---|---|---|---|
| Teacher-forced copy, 8 symbols, 127 tokens | 0.5203 | 0.2648 | **0.9970** |
| Teacher-forced copy, 8 symbols, 63 tokens | 0.7058 | 0.3878 | **0.9998** |
| Free-running whole copy, 8 symbols, 63 tokens | 0.0000 | 0.0000 | **1.0000** |
| Free-running whole copy, 32 symbols, 63 tokens | 0.1400 | 0.0000 | **1.0000** |
| Free-running whole copy, distinct, 127 tokens | 0.8600 | 0.0000 | 0.8600 |
| Held-out periods, 1,024 tokens | 0.9945 | 0.9519 | 0.9900 |
| Recall, 1,024 tokens | 0.9995 | 0.9364 | 1.0000 |

- **My prediction X2 was refuted.** I expected the label alone (B) to stay within 0.05 of A on 127-token 8-symbol
  copies. It fell to 0.2648, and B got worse on every test. One seed, so this may be an unlucky run.
- **X1, X3 and X4 held** (X4 only just: held-out periods at 1,024 were exactly 0.9900 against a 0.99 bar).
- **Coupling did not help free-running distinct 127-token copies** (0.86 in both A and C).

## Registered predictions (seeds 21–26; each holds if true in ≥ 5 of 6 seeds)

| ID | Prediction | Exploration |
|---|---|---|
| P1 | **Coupling, isolated:** C beats B on teacher-forced 8-symbol copies at 127 tokens | 0.9970 vs 0.2648 |
| P2 | C scores ≥ 0.95 on that test | 0.9970 |
| P3 | C writes whole 8-symbol 63-token copies exactly right in ≥ 50% of 100 tries | 1.00 |
| P4 | C meets the full version 2 bar (Q1–Q3 ≥ 0.95 at 128/256/512; Q4 ≥ 0.90 at 1,024) | met |
| P5 | **The label alone hurts:** B scores below A on teacher-forced 8-symbol copies at 127 tokens | 0.2648 vs 0.5203 |
| P6 | **C depends on the coupled ids:** the same trained C model, with coupling switched off at test time (label kept), scores < 0.50 on that test | not measured |
| P7 | Anti-vacuity: untrained models score < 0.05 (checked for `CFG3` by `test_eval3.py`) | — |

- **P6 has not been looked at.** It checks that C's gain comes from the coupled ids rather than from something else
  the C training happened to produce.
- **Verdict code:** `score4.py` through `guard.py`; exactly seeds 21–26 per arm with that arm's config, else exit 2.
  `test_eval4.py` (5 tests) checks the coupled ids, that coupling changes outputs only when SEP is present, and that
  the scorer can return both HELD and FAILED. Three mutants (ids not coupled, coupling never applied, flipped P1
  comparison) each fail a test. With `test_eval3.py` and `test_guard.py`: 21 tests, all passing.

## Cases and counts (C-FEAS)

- 18 training runs (3 arms × 6 seeds), about 10 minutes each on one CPU thread.
- Evaluation as in 003 (`eval3.evaluate3`), with every case seed offset by 30000: not used by 003's confirmation
  (offset 0) or by this exploration (offset 20000).

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes: counts above. |
| Noise | Yes: training was byte-identical on retraining in version 2 (`results/002/determinism.txt`); greedy deterministic evaluation. Not re-measured. |
| Statistics | No population claim: seed counts against a pre-set 5-of-6 rule, no p-values. |
| Evidence | Yes: fail-closed loader. |
| Independence | No: Claude designed, ran and grades this. SELF-TESTED. |
| External | Position coupling is Cho et al.'s method; their results are context, not evidence here. |
| Device | Linux container CPU only. S25 NOT VALIDATED. |
| Verdict code | Yes: `score4.py`, three mutants. |
| Exploration | Yes: seed 903, disclosed above, not reused. |
| Held-out | Yes: fresh training seeds and case seeds. |
| Generated inputs | Yes: `test_eval3.py` checks each family's layout and repeats. AI inspection only. |
| People's data | No. |
| Design | Three-arm paired training intervention; C vs B isolates coupling. Supports "coupling raises these scores on these cases", not a mechanism beyond P6. |

## Unrun door

- Coupling for tasks without an explicit separator (the model would have to infer the alignment itself).
- Phone measurement on the S25.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, coded and wrote this → human validation: not performed →
human editing/curation: direction by Chad Holland, 2026-11-20 → human responsibility: Chad Holland. Review level:
direction only.*
