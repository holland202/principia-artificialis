# CCC-001 accept-shift decomposition on the GPU7B outputs: results

**Status:** 2 of 3 as registered (**T1 REFUTED**), SELF-TESTED, development-only (C-EXPLORE). Registration
[ACCBIAS7B_PREREG.md](ACCBIAS7B_PREREG.md) at `37fe6ac` (committed alone, before any 7B output existed). Harness and
1.5B dry run at `fc42769`, run at `c04d1a9`, outcome pinned in the next commit. No qualification verdict changes
(M12).

## What could have gone wrong, first

- **T1 is refuted by a small margin.** 7B REF π1 gives Δ_acc `-0.004510`. A sign rule passes or fails on tiny values,
  and fp16 on T4 differs from the CPU runs, so this is a sign at 6 dp, not evidence of a reversed effect.
- **Self-tested, not blind.** Claude registered, built, ran and reads this. ChatGPT's turn 028 is design input. No
  human reviewed it. Predictions were transfer predictions from published 1.5B numbers.
- **What was seen before the run.** Before `fc42769`, Claude had seen the notebook's printed summary (gate verdicts
  and G gains, which Chad Holland pasted), hashed the zip, listed its files and printed the top-level keys of the
  two JSON files. No Δ value was seen before the run.
- **Custody is through Chad's accounts.** The zip came from his Google Drive. Its SHA-256 `ccbf5939…3b2d` equals the
  hash the notebook printed. That shows the file is the one the notebook wrote, not who ran the notebook.
- **Only REF and stage Q exist.** N016 and STRESS ran out of GPU memory inside `scaled_dot_product_attention`
  (`results/ccc_001/gpu7b/longctx_N016.txt`, traceback). They are ABSENT, not failed.
- Deviations from the registration: none known. Added beyond it and disclosed: before the 7B run, the rehash code
  was checked against the 1.5B files (`qualify.json` and `longctx_ref.json` reproduce their logs' DIGESTs).

## Raw output (`results/ccc_001/accbias7b_run.txt`, verbatim)

```
V  runner.txt shows all four registered shard hashes OK: True
V  qualify_7b.json rehash 684294d466d7de01... vs stageq.txt DIGEST 684294d466d7de01...: True
V  longctx_REF_7b.json rehash be28907f5adfe57e... vs longctx_REF.txt DIGEST be28907f5adfe57e...: True
V  N016 ABSENT (no JSON returned; not a failure of V)
V  STRESS ABSENT (no JSON returned; not a failure of V)
V HELD custody gate
P0 HELD keys and finite p asserted; bookkeeping max 2.00e-06 (<= 5e-6); E:=D gives 0 in every cell: True
T1 REFUTED 7B REF d_acc per pi [0.086268, -0.004510, 0.195446] (> 0 each)
T2 HELD 7B stage Q d_acc (E-D, pi0) 0.042487 (> 0)
REPORT 7B   Q E-D: d_acc +0.042487 d_rej -0.019887 d_ne -0.022600 | items d_acc up/down 9/6 of 24
REPORT 1.5B Q E-D: d_acc +0.155644 d_rej -0.169676 d_ne +0.014032 | items d_acc up/down 18/5 of 24
REPORT 7B   Q EF64-F64: d_acc +0.006653 d_rej -0.028222 d_ne +0.021569 | items d_acc up/down 6/15 of 24
REPORT 1.5B Q EF64-F64: d_acc +0.053724 d_rej -0.075297 d_ne +0.021574 | items d_acc up/down 14/10 of 24
REPORT 7B   REF pi0: d_acc +0.086268 d_rej -0.108320 d_ne +0.022052 | items d_acc up/down 7/16 of 24
REPORT 1.5B REF pi0: d_acc +0.105711 d_rej -0.123310 d_ne +0.017599 | items d_acc up/down 21/3 of 24
REPORT 7B   REF pi1: d_acc -0.004510 d_rej +0.026256 d_ne -0.021746 | items d_acc up/down 9/7 of 24
REPORT 1.5B REF pi1: d_acc +0.093951 d_rej +0.297205 d_ne -0.391155 | items d_acc up/down 21/3 of 24
REPORT 7B   REF pi2: d_acc +0.195446 d_rej -0.272454 d_ne +0.077008 | items d_acc up/down 9/11 of 24
REPORT 1.5B REF pi2: d_acc +0.313284 d_rej -0.552207 d_ne +0.238923 | items d_acc up/down 17/7 of 24
REPORT N016 ABSENT
REPORT STRESS ABSENT
VERDICT 2 of 3 as registered
DIGEST ae276cb60a19fff6954b77198e267182e4d28f94e5e83c6abbfe3d888b41110d
```

Sabotage (`accbias7b_run_sabotage.txt`): V and P0 HELD, T1 and T2 REFUTED (all zeros), `VERDICT 1 of 3`, digest
`e51f989e…74cd`, exit 1. After pinning, the normal run exits 0. Dry run on 1.5B (`accbias7b_dry_15b.txt`):
REF Δ_acc per π `[0.105711, 0.093951, 0.313284]`, equal to ACCBIAS, exit 0.

## Predictions

| ID | Prediction | Outcome |
|---|---|---|
| V | Shard hashes OK; each JSON rehashes to its log's DIGEST | HELD (N016, STRESS ABSENT) |
| P0 | Keys, finite p, bookkeeping, identity | HELD |
| **T1** | 7B REF Δ_acc > 0 under each π | **REFUTED**: π1 `-0.004510` |
| T2 | 7B stage Q Δ_acc > 0 | HELD, `0.042487` |

## Custody consequence

V held, so the GPU7B qualification outcomes in the notebook's logs are now backed by files that reproduce their
DIGESTs: stage Q `VERDICT 3 of 4` (Q2 REFUTED) and LONGCTX REF `VERDICT 6 of 7` (G5 REFUTED, `0.0973`). They are no
longer only CONTRIBUTOR REPORTED. They still ran on Chad Holland's account and were not re-run here.

## What this shows, and what it does not

This model (Qwen2.5-7B-Instruct, fp16, 2× T4), these 24 development items and synthetic weather text only:
- At short context with accept as A in slot 1, the instruction raises p(accept) on average (T2), by much less than
  in 1.5B (`+0.042487` against `+0.155644`).
- At REF, the accept shift is positive under π0 and π2 and about zero, slightly negative, under π1 (T1 REFUTED).
- **Post-hoc, not registered:** under π0 and π2 the mean is positive while more items move down than up (7/16 and
  9/11). The positive means rest on a minority of items with large shifts. In 1.5B most items moved up.
- Nothing here is about conversations, and nothing can confirm CCC-001.

## Open (M15)

- N016 and STRESS at 7B: a re-run needs a registered deviation changing only the attention path or memory layout,
  and Chad Holland's go. Hypothesis, NOT RUN: the out-of-memory allocations (8.06 and 33.94 GiB) scale as L².
- The A-penalty and letter × slot questions at REF still need their own crossing (ACCBIAS7B "Not claimed").

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no endorsement or validation by
him. The Kaggle run: Chad Holland's account and direction. Registration, harness, run and this document: Claude
(Anthropic, Opus 5.5), in a session started by the relay schedule and continued live with Chad Holland. Design input:
ChatGPT (OpenAI), relay turn 028. Human validation: not performed. Human responsibility: Chad Holland. Review level:
none.
