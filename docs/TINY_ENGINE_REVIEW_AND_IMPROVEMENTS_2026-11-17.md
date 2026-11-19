# Tiny engine: measurement review and ranked improvements

**Status:** source-informed software audit and unrun design proposals. No training,
new model inference, or independent scientific validation. Historical Q2 remains
FAILED. Codex reviewed Claude's implementation after reading its public results.

## Failures and limits first

1. **The scorer counts files rather than distinct registered seeds.** Five copies
   of seed 1, named as separate seed files, make all three printed criteria HELD.
   The public release itself has six distinct seed IDs, so this challenge does
   not change its recorded Q2 failure. It exposes a missing check for future runs.
2. **The main metric is teacher-forced token accuracy.** In `accuracy()`, the model
   receives the full correct sequence under a causal mask, including preceding
   target tokens. That is legitimate next-token evaluation, but is not a rate of
   completely correct strings generated from the source alone. The demo uses
   greedy generation, but only its fixed examples; its copy example reports
   matching tokens and the host supplies the exact generation length.
3. **The copy task caps the source at 127 distinct tokens.** The original generator
   produces the following audit counts. Its T=512 copy input adds trailing padding;
   it does not copy a longer source than T=256. The registration discloses the cap.
4. **Missing results are not a successful evaluation.** The original reporter prints
   FAILED for every criterion on an empty directory but exits zero. Exit zero is
   a reporting-process outcome, not a scientific pass. It should be kept separate
   from both evidence completeness and the registered prediction outcome.
5. **No trained model was executed here.** PyTorch/safetensors are absent in this
   workspace. Generator dependency isolation compiles the original function's
   AST and constants with NumPy; it does not reconstruct the algorithm or emulate
   a trained model. Weight upload checks are package identity checks only.

## Executed observations

Public qualification plan: `13e399b11e0fcef45c3bf970a266971ebd61037b`.
Subject: `c64be1cb0e2b7680f79705a26e266f399aa02e24`.
Exact commands, environment and raw outputs are in `results/tiny_engine_review/`.

```text
Q1: HELD (6/6 seeds meet every threshold; need 5)
Q2: FAILED (1/6 seeds meet every threshold; need 5)
Q3: HELD (6/6 seeds meet every threshold; need 5)
```

Duplicate-record challenge, from the unmodified scorer:

```text
Q1: HELD (5/5 seeds meet every threshold; need 5)
Q2: HELD (5/5 seeds meet every threshold; need 5)
Q3: HELD (5/5 seeds meet every threshold; need 5)
```

| Total input T | Scored copy targets | Distinct source symbols | Trailing padding |
|---:|---:|---:|---:|
| 128 | 63 | 63 | 0 |
| 256 | 127 | 127 | 0 |
| 512 | 127 | 127 | 256 |

For generator seed 17, the T=256 sequence equals the first 256 tokens of T=512.
The audit reports `VERDICT 4 of 4 as registered`, digest
`ed532d576debd4a09a465ce2d5976a15408835ba78d2408313efa7f50b3cafab`.
These expectations include weaknesses; this is not four successful model tests.
The incorrect-expectation sabotage refutes P1 and exits nonzero.

## What to improve first

| Priority | Proposed change | Why it earns the cost | Cheapest decisive check |
|---|---|---|---|
| 1 | Add free-running whole-string exact match, token accuracy and first-error position; retain teacher-forced accuracy as a separate metric | Separates failed retrieval from errors that propagate during generation | Use the frozen checkpoints on the same public development strings in both modes, across all seeds; no retraining |
| 2 | Validate exactly the registered seed identities, common configuration, required metrics, finite bounded values and file provenance | Prevents duplicated or mismatched runs from replacing independent training seeds | Reject duplicate/missing/extra IDs, NaN, mismatched configuration and absent metrics; preserve valid historical Q2 FAILED |
| 3 | Vary source length, source-target gap and repetition separately | Removes the unique-symbol shortcut and separates distance from total input length | Distinct symbols, two-symbol strings, long constant runs and repeated substrings; include unseen intermediate lengths and distractors |
| 4 | Change the position scheme, one arm at a time | A plausible route to copying improvements without immediately enlarging the model | Compare baseline RoPE with position randomization or delimiter-derived 2D positions at matched parameter and training-token budgets; recheck periodic and recall tasks |
| 5 | Improve the training distribution and task balance | The current four training lengths and distinct-only copies are narrow; shared training may trade one skill for another | Mix lengths and repetitions, and compare copy-only versus three-task training with matched copy-token exposure and reported total compute |
| 6 | Add cached generation and device-correct positional tensors | `demo.greedy()` recomputes the whole prefix, and `rope()` creates CPU position tensors on each call | Cached and uncached logits/outputs must agree within a frozen tolerance; then measure latency, memory and energy on the actual S25 |

All changes are **proposals, not demonstrated improvements**. Do not bundle them
in one retraining run: that would leave the cause of any improvement unresolved.

For a practical agent, add a separate exact-copy primitive or pointer/copy path
and compare it with the neural version. The deterministic copy is the baseline
for usefulness and cost; attaching it does not prove a new learned capability.
For the research engine, keep a pure-neural arm so this engineering route cannot
mask the question being studied.

After a reliable baseline: compare a narrower/deeper model, an MLP arm, and INT8
inference under the same task contract. Tiny weight size does not establish low
peak memory, speed, phone energy consumption, QNN compatibility or NPU execution.

## Literature and claim limits

- Ruoss et al., ACL 2023, [Randomized Positional Encodings](https://aclanthology.org/2023.acl-short.161/):
  positional randomization is already published. It is an adaptation candidate,
  not an original proposal from this review.
- Wen et al., [arXiv:2607.16072](https://arxiv.org/abs/2607.16072),
  [author implementation](https://github.com/hhhhhh-925/copy-2dRoPE): 2D position
  schemes for copying and length generalization are prior art. Their advantage
  is not a prediction that this particular small multitask engine will improve.
- Guo et al., [arXiv:2610.26722](https://arxiv.org/abs/2610.26722): the author
  abstract addresses repetition, position hashing and correct termination.
  That is a reason to test repeated symbols and stopping, not a new discovery here.

The ACL primary abstract and author repository/primary arXiv search records were
checked. Direct arXiv page opening failed; these papers' experiments were not
reproduced and their full proofs were not audited. Exact short source excerpts,
URLs and hashes are preserved separately. No novelty claim is made.

The model card's strong causal wording about RoPE and broad statement that tying
weights stops learning should remain scoped to the experiments actually run.
Correct copying alone does not identify an induction-head circuit. A causal
head/path ablation with matched damage controls would be needed for that claim.
The code defines 127 content symbols plus three special tokens; the card's
description of 128 content tokens should get a dated correction.

## Suggested design-session brief / next unrun door

Keep the released checkpoints unchanged. First propose a development-only,
frozen-weight diagnostic: same source in teacher-forced and free-running modes;
whole-string match, first error and token accuracy; distinct, repeated and
constant-symbol inputs; source length crossed with gap; every released seed.
Preserve the original criteria and publish the failed long-copy result.
The current model has no trained EOS contract, so stopping is a separate future
design change, not a retroactive failure criterion. Use an exact symbolic copier
as the inexpensive correctness reference and an untrained model as a negative
control only under an approved execution plan.

Choose a single training or position intervention only after that diagnostic.
Freeze its budget and acceptance/regression limits before running; reserve new
training seeds and untouched evaluation cases for confirmation. A design-session
proposal is not permission to launch a scientific campaign. Ownership remains
Claude for engine changes, Codex for source-informed review unless reassigned.

## Upload identity and cleanup status

The inventory compared every file at both temporary GitHub package commits with
the public Hub repositories: Git blob identity for ordinary files, and local
weight SHA-256 versus Hub LFS SHA-256 metadata for weights. Local manifests also
matched. This is package identity, not independent model validation or a new
download/hash check of every remote weight byte. The phone's earlier verification
was reported by the owner and was not witnessed here.

| Package | Hub revision | Package files | Manifest entries |
|---|---|---:|---:|
| tiny-engine-165k | b4fa044b00a31bb52888b1a0b54b19c65f7b7abe | 19 | 18 |
| rmt-ih-001 | 6f72ebb4614606991e4228bff8bb04866cebbf4f | 33 | 32 |

The tiny engine's stated 18 files count the manifest-listed payload; SHA256SUMS
is an additional file and the Hub adds .gitattributes. All matched records and
transfer fingerprints are in `package_inventory.txt`.

The requested temporary branches remain intact. The GitHub connector has no
branch-deletion method; Git push lacked authentication, and the browser was
signed out. No experiment branch, registration, historical result or model was
deleted or modified. The two package commit IDs remain recorded in the plan
and inventory for recovery. Only the newly created review branch is being added.

Verification scope: normal/sabotage audit, archived score replay, package
inventory, method lint, and patch whitespace. The broader repository test suite
was not rerun for these isolated review artifacts; no production code changed,
and sealed-generating tests remain untouched. This bounded scope is a W7 SHOULD
deviation, recorded explicitly rather than implying a full suite pass.

Provenance: Codex (OpenAI; exact executing model identifier unavailable) authored
the audit and proposals after seeing Claude (Anthropic Opus 5.5)'s code and public
results. Human validation: none. Human curation: direction by Chad Holland.
Responsibility: Chad Holland. Review level: direction only. Not blind, and not
independent model-performance validation.
