# CCC-001 accept-shift decomposition: does the instruction move probability toward *accept*, or toward a letter or a slot? (registration)

**Status:** REGISTERED, NOT RUN. Development-only post-hoc reanalysis of measurements already on disk (C-EXPLORE).
Self-tested. No model is loaded and no new forward pass is made.
**Date:** 2026-11-22. **Parents:** QORDER (registered `88614da`, run `d0761d7`, pinned `9053557`,
[QORDER_RESULTS.md](QORDER_RESULTS.md)) and LONGCTX REF (scope `633ed1e`, pinned `80c7fc1`,
[LONGCTX_RESULTS.md](LONGCTX_RESULTS.md)).
**Agreed in the relay (PR #172):** Claude read the instruction's sign pattern as a letter or position interaction
(`ccc-relay/claude/023`). ChatGPT proposed the rival, a semantic shift toward accepting claims, and the
letter-versus-slot dissociation (`ccc-relay/chatgpt/024`). Claude proposed this computation on existing QORDER
and LONGCTX data (`ccc-relay/claude/025`). ChatGPT set the reporting rules, the three-meaning decomposition and the
negative control (`ccc-relay/chatgpt/026`). No CCC-001 registration is frozen by this file. **No earlier verdict
changes, whatever happens here** (M12).

## Question (W1)

When the explicit instruction is added (arm E against arm D), does the probability of the letter that means
*accept* rise in every letter × slot cell? A semantic accept shift predicts yes everywhere. A letter or slot account
predicts that the sign follows the printed letter or the list position.

## What is already public, so this is not blind (C-EXPLORE)

- QORDER published arm-D and arm-E cell means of p(not-enough letter) by its letter and slot, per-condition means,
  and G gains grouped by the not-enough cell. The Δ_ne table below is therefore partly derivable from published
  numbers. Δ_acc and Δ_rej by their own cells have **not** been computed by anyone so far as the record shows.
- LONGCTX REF published per-π gains in G and, post-hoc, G gains averaged over π by correct answer: accept `0.2887`,
  reject `-0.0576`, not-enough `-0.0741` (`ccc-relay/claude/023`). Those are accept-item-only numbers. P3 below
  is partly informed by them.
- In `ccc-relay/claude/025` Claude opened one record of `longctx_ref.json` to confirm the `p` field. Nothing was
  computed. The counts in Feasibility were computed from metadata (letters, order, row counts) only.

## Instrument and stand-ins (M4)

Inputs, read only: `results/ccc_001/qorder.json` (36 conditions × 24 items × arms D and E; float32 letter logits
`z` over A, B, C) and `results/ccc_001/longctx_ref.json` (cells D0–D2 and E0–E2; letter probabilities `p` rounded
to 6 dp). Model: Qwen2.5-1.5B-Instruct, as measured then. Items: the 24 development items of `probes.py`; their
content is not discussed (RELAY.md rule 4).

The harness `experiments/ccc_001/accbias.py` will be pure Python (no torch). It imports `probes.ITEMS` and
`probes.OPTIONS`. It reads `KEY_MEANING` and `PI` from `qdiag.py` with `ast.literal_eval`, without importing it
(that would need torch). It asserts that every stored key equals the letter of the item's meaning under that
condition's mapping. QORDER probabilities are a float64 softmax of the stored logits with the maximum subtracted.
P0 checks this softmax against `qorder.probs`'s published outputs.

**Definitions.** A pair is one (condition, item) with an arm-D and an arm-E reading. For meaning M, `ℓ(M)` is its
letter in that condition, and `s(M)` is its display slot (QORDER: 1–3 from `order`; LONGCTX: the option line is
always A, B, C, so slot equals letter). Δ_M(pair) = p_E(ℓ(M)) − p_D(ℓ(M)). For each pair,
Δ_acc + Δ_rej + Δ_ne = 0.

**Cells.** QORDER: for each meaning M, 9 cells (ℓ(M), s(M)). Each cell holds 4 conditions × 24 items = 96 pairs.
Cell value = mean over items of the item's mean over its pairs in the cell (equal item weights; with balanced cells
it equals the pair mean). Letter mean = mean of a letter's 3 cells; slot mean = mean of a slot's 3 cells.
LONGCTX: one cell per π (π0 accept A, π1 accept B, π2 accept C, read from the stored keys), 24 pairs each.

## Predictions (M2, M5)

- **P0 (reproduction gate; nothing else is read if it fails).** (a) The 9 QORDER arm-D cell means of
  p(not-enough letter) match `qorder_run.txt`'s `REPORT letter L: j=…` values within 1e-6. (b) The 9 arm-E
  gains (mean G(E) − G(D)) and E>D counts per not-enough cell match the `REPORT` secondary lines: gains within
  5e-5, counts exactly. (c) LONGCTX per-π gains, rounded to 4 dp, equal `[-0.0294, 0.2321, -0.0457]` from
  `longctx_ref_run.txt`. (d) Bookkeeping: |Δ_acc + Δ_rej + Δ_ne| ≤ 1e-12 per QORDER pair and ≤ 5e-6 per LONGCTX
  pair. (e) Identity check: with E replaced by D, every one of the 27 QORDER and 9 LONGCTX cell values is exactly 0.
- **P1 (Claude, against the semantic rival).** At least one of the 9 QORDER accept cells has Δ_acc ≤ 0. The rival
  (ChatGPT, 024) predicts all 9 > 0, which would REFUTE P1.
- **P2 (Claude: the letter matters more than the slot).** For Δ_acc in QORDER, the range of the 3 letter means
  (max − min) is greater than the range of the 3 slot means.
- **P3 (Claude, LONGCTX REF).** Δ_acc > 0 in each of π0, π1 and π2. Partly informed by the published accept-item
  gains (above).

**Reported, never gated:**
- all three 3 × 3 tables (Δ_acc, Δ_rej, Δ_ne, each by its own meaning's letter and slot);
- within each accept cell, the mean Δ_rej and Δ_ne, showing where accept's gain comes from;
- for each cell, items moving up and down (per-item means, of 24) and pairs moving up, down or zero (of 96);
- the smallest cell mean with its letter and slot, and min |cell| (flagged NEAR ZERO below 1e-4);
- LONGCTX per π: Δ_acc, Δ_rej, Δ_ne and up/down item counts. LONGCTX stays separate from the QORDER table.

**Negative control (registered computation, reported).** There are 2,000 shuffles, from `random.Random(20261122)`,
drawn in a fixed order: shuffle 0..1999, then conditions in `qorder.json` order, then items 0..23. Each pair gets
one draw `randrange(3)`, which picks a pseudo-accept letter. The **same** draw is used for both members of the
pair. The pair goes to cell (pseudo letter, that letter's slot in the condition). The cell value uses equal item
weights over the items present. Reported:
- the observed minimum cell mean;
- the 5th, 50th and 95th percentiles of the shuffled minimum;
- the fraction of shuffles whose minimum is ≥ the observed minimum;
- the fraction of shuffles with all 9 cells > 0.

**Anti-vacuity (M3).** `--sabotage` replaces each arm-E reading with its arm-D reading before analysis. Every cell
is then 0, so P1 holds and P2 and P3 are REFUTED. The digest changes and the exit code is 1. P0(e) also exercises
this path in-process.

**Verdict line:** `VERDICT n of 4 as registered`, plus a `DIGEST`: the SHA-256 of all cell values, LONGCTX values
and per-item Δ rounded to 6 dp. The exit code is 0 only on the outcome pinned after the run. If P0 fails, P1–P3
print `NOT READ` and count as not held.

## What each outcome means (this model, these 24 items, these layouts only)

| Outcome | Reading |
|---|---|
| P1 REFUTED (all 9 > 0), shuffled "all 9 > 0" fraction small | Sign-level support for a semantic accept shift at short context. Letter or slot effects can still coexist; read the table |
| P1 HELD, P2 HELD | The accept shift is not uniform and varies more by letter than by slot |
| P1 HELD, P2 REFUTED | The shift is not uniform and varies at least as much by slot as by letter |
| P3 HELD | LONGCTX REF shows a positive accept shift under every π; mapping and slot are confounded there |
| P3 REFUTED | At REF, at least one π shows no accept shift |
| P0 refuted | Readout or bookkeeping defect; report it before anything else |

## Feasibility (C-FEAS)

Computed from metadata only (letters, order and row counts, no logits or probabilities):

```
accept [(('A', 1), 4), (('A', 2), 4), (('A', 3), 4), (('B', 1), 4), (('B', 2), 4), (('B', 3), 4), (('C', 1), 4), (('C', 2), 4), (('C', 3), 4)]
reject [(('A', 1), 4), (('A', 2), 4), (('A', 3), 4), (('B', 1), 4), (('B', 2), 4), (('B', 3), 4), (('C', 1), 4), (('C', 2), 4), (('C', 3), 4)]
notenough [(('A', 1), 4), (('A', 2), 4), (('A', 3), 4), (('B', 1), 4), (('B', 2), 4), (('B', 3), 4), (('C', 1), 4), (('C', 2), 4), (('C', 3), 4)]
pairs 864 True
longctx pairs {'0': 24, '1': 24, '2': 24}
```

The run is arithmetic on 864 + 72 pairs and 2,000 shuffles. It takes seconds (NOT RUN estimate).

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Above |
| Noise | No new measurement. Same-input noise was measured by QORDER P0 (0.000001) and LONGCTX G2 (0.000000) |
| Statistics | No population claim. Signs and ranges of cell means on 24 fixed items. The shuffle is a descriptive null, not a test with error control |
| Evidence | Numbers come from the harness output, pasted verbatim |
| Independence | No. Claude writes and runs it. ChatGPT's rules are design input, not review. SELF-TESTED |
| External | Qwen2.5 weights (Apache-2.0), as measured earlier |
| Device | Linux container CPU, pure Python. S25 NOT VALIDATED |
| Verdict code | Fail-closed. P0 gates reading. Sabotage must exit 1 |
| Exploration | Yes. Post-hoc on published aggregates; what was already seen is listed above |
| Held-out | None. Development items only; nothing here can confirm CCC-001 |
| Generated inputs | None new. QORDER prompts were printed and read before that run |
| People's data | None |
| Design | Instrument diagnostic on one model's answer format; no claim about conversations |

## Limits

- One small model, which is not qualified, with 24 items and one instruction wording.
- A sign rule passes on a tiny positive value, so sizes and counts are printed.
- In LONGCTX, π, letter and slot are one factor.
- The shuffle control asks whether the pattern belongs to *accept* rather than to an arbitrary letter. It does not
  separate token identity from alphabetical rank.

## Open door (M15)

Not run: the same decomposition on the GPU7B run's stage Q and LONGCTX outputs (amendment `5b4807c`), once their
returned JSON reproduces the recorded digests. Also not run: a fresh letter × slot crossing at REF length, which
QORDER never covered.

## Provenance (M13)

Question origin for CCC-001: Federico Talens-Alesson, credited as the question's originator only; no endorsement
or validation by him is implied. Rival and reporting rules: ChatGPT (OpenAI), in the relay. Registration written by
Claude (Anthropic, Opus 5.5) in a fresh scheduled session, under Chad Holland's standing direction of 2026-11-21.
Human validation: not performed. Human editing/curation: direction only. Human responsibility: Chad Holland.
