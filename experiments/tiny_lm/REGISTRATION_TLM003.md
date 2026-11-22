# TLM-003 registration: does size help at the same data budget? 3.2M vs 1M parameters

**Status:** REGISTERED, NOT RUN on seed 31. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-21). Design and code: Claude (Anthropic, Opus 5.5). Human review level:
direction only.

## Why

In TLM-002 ([RESULTS_TLM002.md](RESULTS_TLM002.md)) the 1,018,624-parameter model beat the refit byte 8-gram
(1.1422 / 1.1242 bits per byte vs 1.1736), and its loss had nearly flattened. **Question:** at the same data budget
(51,200,000 bytes, same schedule), does a 3,215,872-parameter model do better? If yes, capacity was the limit.

## What changes (and only this)

- **Model size:** `train.py SEED 6250 OUT 256 4 4` — width 256, 4 layers, 4 heads; 3,215,872 parameters (printed
  by code in `exploration/x903_3m.json`). Everything else is unchanged from TLM-002: data slice, steps, batch,
  learning rate, schedule, evaluation windows, rival, checks.
- **One seed (31), not two.** A 3.2M run takes about 2.5 hours on 2 threads, and two in parallel would take about
  5 hours. With one seed this is a single-run comparison; TLM-002's two seeds differed by 0.0180 bpb, so P1 needs a
  margin larger than that (below).

## Exploration (C-EXPLORE)

Seed 903, a 250-step schedule (it decays to zero at 250): valid bpb 2.7770 after 357 s. This confirms the model
trains at this learning rate; it says nothing about the 6,250-step result.

## Registered predictions (seed 31)

| ID | Prediction | Basis |
|---|---|---|
| P1 | **Size helps:** valid bpb < 1.1062, i.e. more than 0.0180 (TLM-002's seed-to-seed gap) below the better 1M seed (1.1242) | TLM-002 1M loss had nearly flattened |
| P2 | Beats the refit rival: valid bpb < 1.1736 | TLM-002 |
| P3 | Known-word rate ≥ 0.90 (`gencheck.py`, run with `256 4 4`) | TLM-002: 0.9960 / 0.9948 |
| P4 | Copied-span rate ≤ 0.20 | TLM-002: 0.0281 / 0.0451 |
| P5 | Shuffled-valid bpb ≥ 4.0 (`shufcheck.py`, adapted only to build the 256/4/4 model) | TLM-002: 10.57 / 10.56 |

- **If P1 fails**, size at this data budget is not the limit, and the next step is more data per run or a
  word-piece tokenizer, not a bigger model.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes: about 2.5 h for one run, plus checks. |
| Noise | One seed; P1's margin is set above TLM-002's seed-to-seed gap (0.0180). Not a variance estimate. |
| Statistics | No population claim. |
| Evidence | Numbers from the scripts' printed output, pasted verbatim. |
| Independence | No: SELF-TESTED. |
| External | TinyStories data (CDLA-Sharing-1.0). |
| Device | Linux container CPU only. S25 NOT VALIDATED. |
| Verdict code | Thresholds applied by hand to printed numbers. |
| Exploration | Yes: seed 903, disclosed. |
| Held-out | Yes: valid file never trained on; seed 31 fresh. |
| Generated inputs | Same data as TLM-001/002. |
| People's data | No. |
| Design | One-seed size comparison at a fixed data budget; supports "at most this much from size, at this budget". |

## Unrun door

- A second 3.2M seed; a word-piece tokenizer; publishing the models.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, coded and wrote this → human validation: not performed →
human editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level:
direction only.*
