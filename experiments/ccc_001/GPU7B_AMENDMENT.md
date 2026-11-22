# CCC-001 amendment: stage Q and LONGCTX on Qwen2.5-7B-Instruct, Kaggle 2× T4 (REGISTRATION, NOT RUN)

**Status:** dated amendment, 2026-11-22, committed alone before any 7B weights are loaded and before the 7B model
reads any probe. Development-only (C-EXPLORE). Self-tested design. It amends
[QUALIFICATION_PREREG.md](QUALIFICATION_PREREG.md) (`ec1c422`) and [LONGCTX_PREREG.md](LONGCTX_PREREG.md)
(`cf1fbcd`) only in **which model runs and where**. Their gates are not changed, and neither file is edited (M12).
Nothing in CCC-001 is frozen by this. No relay prefix is read and no confirmatory item is involved.

**Direction:** Chad Holland, 2026-11-22, in a live chat with Claude (paraphrased, not quoted). He asked for the
largest model possible and a GPU run, and chose Kaggle's free 2× T4. This answers relay turn 023's open question
on the Claude side. ChatGPT has not replied to 023 yet.

## Why

Qwen2.5-1.5B failed stage Q (Q2) and LONGCTX at REF (G5 `0.0523`, G6 12 of 24). The bottleneck is the model, not
the instrument ([LONGCTX_RESULTS.md](LONGCTX_RESULTS.md)). The sandbox CPU cannot hold 7B weights.

## Model (pinned)

- `Qwen/Qwen2.5-7B-Instruct`, revision `a09a35458c702b33eeacc393d103063234e8bc28`. Weight shard SHA-256s, from the
  Hub's LFS metadata:
  - `model-00001-of-00004.safetensors` `a1333e6293854747c481288ea83b348226af178dd565c49b6f9495ba1966aba7`
  - `model-00002-of-00004.safetensors` `f5d25a2772cb825164a2a2c0fb6d51a87e282abf21e4dd75bc5cfb3cd0ea6185`
  - `model-00003-of-00004.safetensors` `8efdec4c1bc12317ae1a38dc42b595ce777738a64deea3fcb8a0a91381bcdfd5`
  - `model-00004-of-00004.safetensors` `1a72d403cdf0c1ec3cb7f289f17b394a01e64394c2e9b3c0f94dbce3faf879bd`
- `config.json` `7463bb0e…c0b03c`: L = 32768, vocab 152064, 28 layers, no sliding window.
- The tokenizer files are **byte-identical** to the 1.5B ones: `tokenizer.json` `c0382117…7539`,
  `tokenizer_config.json` `5b5d4f65…9583`, `vocab.json` `ca10d7e9…0910`, `merges.txt` `599bab54…e5f3`. So every
  prompt is identical to the 1.5B runs. SELF-TESTED here with no weights loaded:
  `CCC_MODEL_DIR=<7B tokenizer only> longctx.py --g0-only` gives G0 HELD at REF, N016 and STRESS, 18 of 18 digests
  ([log](../../results/ccc_001/longctx_g0_qwen7b_tokenizer.txt)).

## Runtime (differs from the CPU runs; disclosed before the run)

- Kaggle notebook, 2× NVIDIA T4 (16 GB each), `device_map="auto"`, **float16**. The T4 has no bfloat16 hardware.
  Every earlier CCC-001 number is bf16 on CPU, so 7B numbers are not comparable digit for digit with anything
  earlier.
- transformers 5.24.0 is installed by the runner. torch, CUDA and accelerate are Kaggle's and are recorded, not
  pinned.
- The harnesses read `CCC_MODEL_DIR`, `CCC_DTYPE` and `CCC_DEVICE_MAP`. Unset, they behave as before. That is
  checked by re-running the pinned 1.5B stage Q and LONGCTX REF outcomes on CPU after the change, before the GPU
  run.
- The runner is `kaggle_gpu7b.py`. It verifies the four shard hashes before loading and stops on any mismatch.

## What runs, in order (all gates as registered)

1. `longctx.py --g0-only`: G0 at all three lengths, with no weights.
2. `qualify.py`: stage Q, Q1–Q4 as registered at `ec1c422`, with the cached path as registered.
3. `qualify.py --sabotage`: expected Q3 HELD with all S = G = 0.333333, exit 1.
4. `longctx.py --length REF`, then `N016`, then `STRESS`: G0–G6 as registered (G3 at REF only). D1's REF-only cut
   applied to the 1.5B model only. All three lengths run here, whatever REF shows, and T\* follows the registered
   rule (`longctx_summary.py`).
5. `longctx.py --length REF --sabotage`: expected G4, G5 and G6 REFUTED, exit 1.

**A 7B model counts as qualified for CCC-001** only if stage Q holds 4 of 4 and T\* covers the length of the prompts
it will read. Checkpoint 016's development prompts (≤ 8,746 tokens) need T\* ≥ N016. A pass here is still
development evidence on synthetic text. Any arm-A use still needs Chad's go on the PR.

**No outcome prediction is registered.** Each gate is a pass criterion. **Fail-closed:** NaN or inf logits under
fp16 make every equality and threshold comparison false, so the affected gates print REFUTED.

## Feasibility (C-FEAS, NOT RUN estimates)

- Weights about 15.2 GB in fp16, split over 2 × 15 GB. With `logits_to_keep=1`, an 18k-token pass adds well under
  1 GB. G3's full logits at REF add about 0.8 GB.
- Passes: stage Q is cached (5 arms plus 2 repeats of D). LONGCTX is 3 × 168 uncached passes, plus 24 for G3 and
  192 for the sabotage, about 5 million prompt tokens. Time on 2× T4 is unknown. Kaggle's session limit is 12 h.

## Limits

- Chad runs it, on his Kaggle account. Claude sees only the returned files, so the outcome is CONTRIBUTOR REPORTED
  until Claude checks that the returned JSON reproduces each printed DIGEST.
- fp16 rather than bf16, and the GPU kernels are not CPU's. G2 and Q1 test same-process repeatability only.
- The same 24 development items and synthetic weather text. This says nothing about conversations.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) wrote the amendment and the runner, in a session started by the relay schedule and
continued live with Chad Holland. Model choice and platform: Chad Holland's direction, 2026-11-22. Human
validation: not performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico
Talens-Alesson's; crediting him implies no endorsement or validation by him.

## Changes (W9)

- **2026-11-22T14:28:19Z:** Chad Holland approved the run on PR #172 in his own words
  ([comment 7080568432](https://github.com/holland202/principia-artificialis/pull/172#issuecomment-7080568432)), as
  RELAY.md rule 5 asks. Before this, his direction was recorded only from chat. He reports he started the Kaggle run
  as `kaggle_gpu7b.py` describes. The run's outcome is NOT RUN here until the returned files arrive. The registered
  text above is unchanged. Between `9c5641b` and the branch head the notebook cloned (`84430f8`), only relay records
  changed, with no harness code (`git diff --stat 9c5641b 84430f8`: 4 files, all records). Appended by Claude
  (Anthropic, Opus 5.5); human responsibility: Chad Holland.
