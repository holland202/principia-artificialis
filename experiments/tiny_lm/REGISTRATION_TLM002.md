# TLM-002 registration: the same 1M model, trained 2.5× longer, against a stronger rival

**Status:** REGISTERED, NOT RUN on seeds 21–22. Self-tested.
**Authors:** Direction: Chad Holland (2026-11-21, agreed to "train the 1M model longer" first). Design and code:
Claude (Anthropic, Opus 5.5). Human review level: direction only.

## Why

In TLM-001 ([RESULTS_TLM001.md](RESULTS_TLM001.md)) the 1,018,624-parameter byte-level model lost to the best byte
n-gram: 1.3633 and 1.3698 bits per byte (bpb) against 1.2075. Its validation loss was still falling when the
learning rate reached zero. **Question:** with 2.5× the training (51,200,000 bytes seen), does it beat a byte
n-gram given at least as much text?

## What changes (and only this)

- **Steps:** 6,250 instead of 2,500. The cosine schedule stretches to the new length. Everything else in `train.py`
  is unchanged: model, batch, learning rate, data slice, evaluation windows.
- **Seeds:** 21 and 22 (fresh).
- **Rival, refit so it is not handicapped:** the same n-gram, now trained on the first 60,000,000 bytes, more than
  the transformer's 51,200,000. Best of orders 1–8 on the evaluation bytes, as before. Already computed
  (`results/tiny_lm/002/ngram_60MB.txt`): **order 8, 1.1736 bpb** (30 MB had given 1.2075).
- **Anti-vacuity, replacing TLM-001's P4** (whose reasoning was wrong): the same model on the same valid bytes in a
  fixed shuffled order (`shufcheck.py`). A model that learned the text's structure must do far worse there. Checked
  on the TLM-001 models (exploration): valid 1.3633 / 1.3698, shuffled 10.4875 / 10.3832. `shufcheck.py` reproduces
  TLM-001's valid bpb exactly. `train_eval.py` is `train.py`'s evaluator copied verbatim so it can be imported.

## Registered predictions (each must hold in both seeds 21 and 22)

| ID | Prediction | Basis |
|---|---|---|
| P1 | **Beats the refit rival:** valid bpb < 1.1736 | TLM-001: 1.3633 at 20.5M bytes, still falling |
| P2 | Known-word rate ≥ 0.90 (`gencheck.py`, unchanged) | TLM-001: 0.9799 / 0.9701 |
| P3 | Copied-span rate ≤ 0.20 | TLM-001: 0.0144 / 0.0318; real stories 0.0782 |
| P4 | Shuffled-valid bpb ≥ 4.0 | TLM-001: 10.49 / 10.38 |
| P5 | Longer training helps: valid bpb ≤ 1.3133, i.e. at least 0.05 below TLM-001's better seed (1.3633) | — |

- **P1 is the real test and may fail.** The rival also improved with more text (1.2075 → 1.1736).
- **Off-ramp:** if P1 fails again, the next step is a change of approach (3.2M parameters or a word-piece tokenizer),
  not more steps at 1M.

## Cases and counts (C-FEAS)

Two runs in parallel, one CPU thread each: about 2 hours (TLM-001's 2,500 steps took 2,909 s). Generation checks
add about 15 minutes.

## Triggered controls (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes: above. |
| Noise | Two seeds; evaluation deterministic (`shufcheck.py` reproduced 1.3633 exactly). |
| Statistics | No population claim; both seeds must pass. |
| Evidence | Numbers from the scripts' printed output, pasted verbatim. |
| Independence | No: SELF-TESTED. Samples published so people can read them. |
| External | TinyStories data (CDLA-Sharing-1.0). |
| Device | Linux container CPU only. S25 NOT VALIDATED. |
| Verdict code | Thresholds applied by hand to printed numbers. Simple comparisons, stated above. |
| Exploration | Yes: the TLM-001 models and the refit rival, disclosed above. |
| Held-out | Yes: valid file never trained on; seeds 21–22 fresh. |
| Generated inputs | Same data as TLM-001, already looked at. |
| People's data | No. |
| Design | Same model, longer schedule, vs a refit rival; supports "this budget, this text". |

## Unrun door

- 3.2M parameters; a word-piece tokenizer; the model in the browser Space.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, coded and wrote this → human validation: not performed →
human editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level:
direction only.*
