# TLM-006 T4: retraining TLM-004's seeds 41 and 42 (Source B), and gates G1 and G2

**Why:** TLM-004's weight files were never committed, and Chad Holland found no copy on the S25 (PR #185, comment
7196714140). Run by Claude (Anthropic, Opus 5.5), SELF-TESTED.

**Environment:** Linux container, 2 CPUs, Python 3.13.18, torch 2.15.0+cpu, tokenizers 0.23.3, numpy 2.5.3. TLM-004
recorded neither its torch version nor its thread count.

**Inputs:** the slice and valid file match their pinned SHA-256 values. `tok.py` rebuilt `tok1024.json`
byte-identical to the committed `results/tiny_lm/004/tok1024.json` (SHA256SUMS.txt). The scripts were copied unchanged
from this branch (scripts_sha256.txt).

**Command:** `THREADS=2 python3 train_tok.py SEED 6250 runs/tSEED 120 5 4`, run for seeds 41 and 42 in turn.

| | G1 (weight SHA-256 equal to TLM-004's) | G2 (seeds 5000–5019 byte-identical to TLM-004's samples) | valid bpb, retrain / TLM-004 | train curve against TLM-004's log |
|---|---|---|---|---|
| seed 41 | **FAILED** (`b388fcb2…` vs `301f2028…`) | **FAILED** (first difference at byte 71) | 0.8487 / 0.8487 | equal at 4 decimals except step 6000: 2.7864 vs 2.7865 |
| seed 42 | **FAILED** (`e4f74228…` vs `8302789e…`) | **FAILED** (first difference at byte 53) | 0.8577 / 0.8571 | differs from step 500: 4.961 vs 4.946 |

**Scope (frozen rule, REGISTRATION_TLM006.md at 834ff9b):** both models are **RECIPE REPLICATE**. Any confirmatory
result describes the training recipe and these two retrained models, not TLM-004's own weights.

**Disclosed:**
- **The first seed-42 run was killed** at about step 2000, when the session's background process was stopped. Its
  log is `t42.killed_at_step2000.log`. The rerun from scratch reproduced it exactly (4.961 at step 500, 4.181 at step
  1000), so training is deterministic in this environment. Why TLM-004's seed 42 differs from step 500 while seed 41
  matches is **unknown**. An unrecorded setting is possible. It is not explained here.
- **G2 by-product, observed on the old, already-seen seeds 5000 to 5019** (not the frozen held-out seeds), with
  `gencheck_tok.py` unchanged:
  - seed 41: copied-span rate 0.0942, against TLM-004's 0.1099;
  - seed 42: 0.0978, against 0.0923.

  This is descriptive only, and part of no prediction.
- **Another Claude session's diagnostic** (commit `5823527`, `experiments/tiny_lm/diag_tlm006.py`, pushed while
  this retrain ran) reports a retrain on the S25 that diverged: 8.069 bits per token at step 500 and nan by step
  1000. It also reports a server reference with torch 2.11.0+cpu at 4.8444 at step 500. This container's torch
  2.15.0+cpu run reached 4.844 at step 500 as well (seed 41), which agrees with that server reference. The two
  sessions are not independent (M10).
- Weights, tokenised data and the slice are not committed. Their SHA-256 values are in SHA256SUMS.txt.
