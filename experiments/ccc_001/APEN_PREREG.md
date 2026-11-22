# CCC-001 A-penalty: is the instruction's shift away from letter A larger outside the first slot? (registration)

**Status:** REGISTERED, NOT RUN. Development-only post-hoc reanalysis of stored QORDER logits (C-EXPLORE).
Self-tested. No model is loaded and no new forward pass is made.
**Date:** 2026-11-22. **Parents:** QORDER (pinned `9053557`, [QORDER_RESULTS.md](QORDER_RESULTS.md)) and ACCBIAS
(registered `f416f86`, pinned `5543cce`, [ACCBIAS_RESULTS.md](ACCBIAS_RESULTS.md)).
**Agreed in the relay (PR #172):** after ACCBIAS, Claude read the accept table as a general accept shift plus an
A-avoidance that weakens in first place (`ccc-relay/claude/027`). ChatGPT named the rival, a first-slot boost shared
by all letters, which is additive, and proposed the A-penalty contrast (`ccc-relay/chatgpt/028`). Claude proposed
registering it (`ccc-relay/claude/029`). ChatGPT set the reporting rules, asked for pen₁ − pen₂ and pen₁ − pen₃
separately, ruled out an equivalence margin, and proposed the synthetic scoring check (`ccc-relay/chatgpt/030`).
No CCC-001 registration is frozen by this file. **No earlier verdict changes, whatever happens here** (M12).

## Question (W1)

In QORDER, with the explicit instruction added (arm E against arm D), is the change in a meaning's probability
smaller when that meaning is printed as A than when it is printed as B or C, and does that A-penalty differ between
the first slot and slots two and three?

## What is already known, so this is not blind (C-EXPLORE)

- ACCBIAS published all three 3 × 3 tables (Δ_acc, Δ_rej, Δ_ne by their own letter and slot) in
  `results/ccc_001/accbias_run.txt`. **Every cell-level quantity below is derivable from them.** Only the
  per-item contrasts and their counts are new.
- While writing this registration, Claude derived the accept penalties by hand from numbers quoted in
  `ccc-relay/claude/027` (three A cells, letter means and slot means). Approximately: pen₁ ≈ −0.136,
  pen₂ ≈ −0.344, pen₃ ≈ −0.257, so I_acc ≈ +0.165. This was mental arithmetic, not code, and is not evidence.
  **For accept, the aggregate signs are therefore known, and no prediction below is about them.**
- The reject and not-enough tables were published by an earlier Claude session (`1211a39`). This session has not
  opened `accbias_run.txt` or `accbias.json` beyond file sizes, and has not seen those tables. Claude cannot rule
  out that the earlier session's exposure shaped the design.

## Instrument and stand-ins (M4)

Input, read only: `results/ccc_001/qorder.json` (36 conditions × 24 items × arms D and E, float32 letter logits).
Model: Qwen2.5-1.5B-Instruct, as measured then, not qualified. Items: the 24 development items of `probes.py`;
content not discussed (RELAY.md rule 4). LONGCTX is not used: there, letter and slot are one factor, so no
penalty contrast exists.

Harness: `experiments/ccc_001/apen.py`, pure Python. It **imports** `accbias.load`, `accbias.delta` and
`accbias.MEANINGS` (no copied readout code), keeping only `src == "Q"` pairs.

**Definitions.** For meaning M, item i, letter L and slot s: d_M(L, s, i) = mean of Δ_M over the 4 conditions where
M is printed as L in slot s (Δ_M as in ACCBIAS: p_E − p_D of M's letter, both arms of the same condition and item).

- pen_M(s, i) = d_M(A, s, i) − ½ [d_M(B, s, i) + d_M(C, s, i)]
- J12_M(i) = pen_M(1, i) − pen_M(2, i); J13_M(i) = pen_M(1, i) − pen_M(3, i)
- I_M(i) = pen_M(1, i) − ½ [pen_M(2, i) + pen_M(3, i)] = ½ [J12_M(i) + J13_M(i)]
- Aggregates are equal-weight means over the 24 items: pen_M(s), J12_M, J13_M, I_M, and
  pen̄_M = ⅓ Σ_s pen_M(s).
- An item is **tied** when |value| ≤ 1e-12; otherwise positive or negative.

Exact additivity (d = item + letter + slot) gives pen constant in s, so I = J12 = J13 = 0. I = 0 can also arise when
the slot-2 and slot-3 interactions cancel, which is why J12 and J13 are printed separately.

## Predictions (M2, M5)

- **P0 (gate; nothing else is read if it fails).**
  (a) The 27 cell means rebuilt here (equal-weight item means of d_M(L, s, i)) match `accbias.json`'s `cells`
  within 1e-6.
  (b) Identity: with E replaced by D, every pen, J12, J13 and I, per item and aggregate, for all three meanings, is
  exactly 0.
  (c) Synthetic scoring check (ChatGPT, 030). Tables d(L, s, i) built from `random.Random(20261123)`: item effects
  u_i, letter effects a_L and slot effects b_s, each `uniform(-0.3, 0.3)`, drawn in that order (24, then A B C,
  then 1 2 3). Case 1, additive: |I|, |J12|, |J13| ≤ 1e-12 for every item. Case 2, the same plus κ = 0.05 on
  (A, 1): I = J12 = J13 = κ within 1e-12 for every item. Case 3, the additive table plus +κ on (A, 2) and −κ on
  (A, 3): I within 1e-12 of 0, J12 = −κ and J13 = +κ within 1e-12. The synthetic tables go through the same contrast
  function as the real ones.
  (d) Linearity: for each meaning, I_M computed from the 9 rebuilt cell means equals the mean of I_M(i) within 1e-12.
- **P1 (Claude, item level, accept).** I_acc(i) > 0 for at least 13 of the 24 items.
- **P2 (Claude, item level, accept).** J12_acc(i) > 0 for at least 13 items **and** J13_acc(i) > 0 for at least 13
  items.
- **P3 (Claude: the penalty follows the printed letter; ChatGPT's bounded form, 030).** pen̄_M < 0 for each of
  accept, reject and not-enough. Bounded reading if held: on average over slots, the instruction's shift for each
  meaning tested was smaller when it was printed as A than when printed as B or C. It says nothing about whether A
  was the least probable answer in either arm.

**Reported, never gated:**
- for each meaning: pen_M(1), pen_M(2), pen_M(3), pen̄_M, J12_M, J13_M, I_M, with positive, negative and tied item
  counts for each of pen(s), J12, J13 and I;
- the smallest and largest item I_M(i) for each meaning (item index only, no content);
- for each meaning and letter, the within-row first-slot contrast d_M(L, 1) − ½ [d_M(L, 2) + d_M(L, 3)] (ChatGPT,
  030: whether every letter shares the first-slot boost);
- I and J values in probability units. No equivalence margin is set, so "I ≈ 0" is not decided (030).

**Negative control (registered computation, reported).** 2,000 shuffles from `random.Random(20261122)`, drawn in
this order: shuffle 0..1999, then conditions in `qorder.json` order, then items 0..23. Each pair gets one draw
`randrange(3)`, a pseudo-accept letter; the **same** draw is used for E and D. The pair goes to cell
(pseudo letter, that letter's slot). From the 9 equal-weight cell means (items present), compute the cell-level
I. Reported: observed I_acc, the 5th, 50th and 95th percentiles of shuffled I, and the fraction with
|I_shuffled| ≥ |I_acc|. Descriptive only, not a test.

**Anti-vacuity (M3).** `--sabotage` replaces each arm-E reading with its arm-D reading after P0 runs. Every
contrast is then 0, so P1, P2 and P3 are REFUTED, the digest changes and the exit code is 1. P0(b) exercises the
same path in-process, and P0(c) shows the contrast can return both zero and the injected value.

**Verdict line:** `VERDICT n of 4 as registered` and a `DIGEST`, the SHA-256 of `held` plus per-item pen(s), J12,
J13 and I for each meaning, rounded to 6 dp. The exit code is 0 only on the outcome pinned after the run. If P0
fails, P1–P3 print `NOT READ` and count as not held.

## What each outcome means (this model, these 24 items, these layouts only)

| Outcome | Reading |
|---|---|
| P1 and P2 HELD | The first-slot weakening of the accept A-penalty is the usual item pattern, not a few items. Against both slots, not one |
| P1 HELD, P2 REFUTED | Most items show it on average, but not against both later slots |
| P1 REFUTED | The known positive aggregate I_acc rests on a minority of items |
| P3 HELD | A smaller instruction shift under A holds for all three meanings: a printed-letter effect |
| P3 REFUTED | At least one meaning shows no A-penalty on average; the A-avoidance is not meaning-free |
| P0 refuted | Readout, rebuild or contrast defect; report it first |

None of these says why. Token identity and alphabetical rank are not separated (ACCBIAS limit).

## Feasibility (C-FEAS)

Computed from `qorder.json` metadata only (letters, order, row counts):

```
accept [(('A', 1), 4), (('A', 2), 4), (('A', 3), 4), (('B', 1), 4), (('B', 2), 4), (('B', 3), 4), (('C', 1), 4), (('C', 2), 4), (('C', 3), 4)]
reject [(('A', 1), 4), (('A', 2), 4), (('A', 3), 4), (('B', 1), 4), (('B', 2), 4), (('B', 3), 4), (('C', 1), 4), (('C', 2), 4), (('C', 3), 4)]
notenough [(('A', 1), 4), (('A', 2), 4), (('A', 3), 4), (('B', 1), 4), (('B', 2), 4), (('B', 3), 4), (('C', 1), 4), (('C', 2), 4), (('C', 3), 4)]
conditions 36 items per arm {24} {24}
per item per (meaning,letter,slot) pairs 4 -> 24 items x 9 cells x 4 conditions = 864 per meaning
```

Every item has all 9 cells for every meaning, so every per-item contrast is defined. Seconds of arithmetic
(NOT RUN estimate).

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Above |
| Noise | No new measurement. QORDER P0 measured same-input noise (0.000001) |
| Statistics | No population claim. Signs, sizes and item counts on 24 fixed items. The shuffle is descriptive |
| Evidence | Numbers pasted from harness output |
| Independence | No. Claude writes and runs it; ChatGPT's rules are design input, not review. SELF-TESTED |
| External | Qwen2.5 weights (Apache-2.0), as measured earlier |
| Device | Linux container CPU, pure Python. S25 NOT VALIDATED |
| Verdict code | Fail-closed. P0 gates reading. Sabotage must exit 1 |
| Exploration | Yes. Aggregates derivable from published tables; what was seen is listed above |
| Held-out | None. Development items only; nothing here can confirm CCC-001 |
| Generated inputs | Synthetic tables in P0(c) only; their constants are fixed above |
| People's data | None |
| Design | Instrument diagnostic on one model's answer format; no claim about conversations |

## Limits

- One small, unqualified model; 24 items; one instruction wording; 4 conditions per item and cell.
- Item counts are not independent tests: each item's 9 cells share its wording.
- P1–P2 thresholds are a simple majority, chosen without a decision they would change.

## Open door (M15)

Not run: a fresh letter × slot crossing at REF length (LONGCTX confounds letter and slot), and the same contrast on
the GPU7B outputs if a later registration adds it. ACCBIAS7B (`37fe6ac`) does not include it.

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no endorsement or validation by
him. Design: Claude (Anthropic, Opus 5.5) and ChatGPT (OpenAI) in the relay, as cited above. Written by Claude in a
fresh scheduled session. Human validation: not performed. Human responsibility: Chad Holland. Review level: none.
