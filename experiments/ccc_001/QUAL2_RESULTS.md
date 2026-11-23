# CCC-001 QUAL2 on Qwen2.5-1.5B: results

**Status:** 1 of 3 as registered. **K3 and K4 REFUTED**: the 1.5B model does not follow even a direct override
instruction. SELF-TESTED, development-only (C-EXPLORE). Registration [QUAL2_PREREG.md](QUAL2_PREREG.md) at `3cff526`
(committed alone, not frozen), run at `7ea7f1f`, outcome pinned in the next commit. 7B is NOT RUN. **No earlier
verdict changes** (M12).

## What could have gone wrong, first

- **Claude's prediction failed.** Claude predicted K1, K3 and K4 HELD for 1.5B. K3 and K4 are REFUTED.
- **Sabotage does not discriminate here.** The sabotage run also scores 1 of 3 (K1 held, K3 and K4 refuted). It
  differs only in digest (`0473dc29…c316`) and in its numbers (all zero shifts). It shows the code reads zeros as
  zeros. It cannot show that K3 or K4 would hold under a working model.
- **Self-tested.** Claude designed the arm, wrote the code, ran it and reads it. No human or ChatGPT review.
- **Designed after seeing every earlier output** (listed in the registration). Arm O had never been run.
- Added check, not registered: arms D and E reproduce stage Q's stored 1.5B readings exactly (`qualify.json`, all
  24 items, both arms). The weights hash `dd924a11…c6d3ee` as pinned; torch `2.15.0+cpu`, transformers `5.24.0`.
- The prompts were printed and read before the run (`results/ccc_001/qual2_prompts.txt`, C-SYNTH).

## Raw output (`results/ccc_001/qual2_run_1.5b.txt`, verbatim)

```
arm D ctx_tokens 0
arm E ctx_tokens 114
arm O ctx_tokens 67
model qwen25-1.5b-instruct
K1 HELD D measured 3 times, identical to 6 dp: True
K3 REFUTED over the 16 non-C items mean p_O(C) - p_D(C) = 0.0344 (>= 0.30), O > D on 9 of 16 (>= 12)
K4 REFUTED over the 16 non-C items mean p_O(C) - p_E(C) = 0.0210 (>= 0.30)
H usable G endpoint headroom 1 - mean G(D) = 0.3764 (>= 0.20)
REPORT arm D: non-C items mean p(A,B,C) 0.4378 0.5620 0.0002 | C items mean p(A,B,C) 0.8720 0.1280 0.0001 | mean G 0.6236 | modal {'A': 14, 'B': 10, 'C': 0}
REPORT arm E: non-C items mean p(A,B,C) 0.6160 0.3704 0.0136 | C items mean p(A,B,C) 0.9825 0.0021 0.0154 | mean G 0.5741 | modal {'A': 18, 'B': 6, 'C': 0}
REPORT arm O: non-C items mean p(A,B,C) 0.4019 0.5635 0.0346 | C items mean p(A,B,C) 0.3951 0.3019 0.3030 | mean G 0.6976 | modal {'A': 11, 'B': 12, 'C': 1}
REPORT O > E on 7 of 16 non-C items
VERDICT 1 of 3 as registered
DIGEST 6705689cf4361400eb18f8d545696298ce2f86f609d08c869c22908f44020e43
```

## Predictions

| ID | Prediction (Claude) | Outcome |
|---|---|---|
| K1 | D identical three times | HELD |
| **K3** | O raises p(C) on the 16 non-C items by ≥ 0.30, on ≥ 12 | **REFUTED**: `0.0344`, 9 of 16 |
| **K4** | O exceeds E by ≥ 0.30 there | **REFUTED**: `0.0210` |
| H | Decision rule on known numbers | usable, `0.3764` |

## What this shows, and what it does not

This model, π0, short context, one wording of O:
- On the 16 items whose key is A or B, a direct instruction to answer C moved p(C) from `0.0002` to `0.0346`. The
  model kept answering A or B (modal C on 1 of 24 items).
- **Post-hoc, not registered:** on the 8 items whose key is C, O did move the model, from p(C) `0.0001` to
  `0.3030`, and mean G rose to `0.6976`. Where the report is weak, the override shifts mass to C. Where the report
  is clear, it does not.
- QUAL2's decision rule says: stop with this model. 1.5B is not QUAL2-qualified. That agrees with stage Q.
- Nothing here is about conversations or about 7B.

## Open (M15)

- 7B on Kaggle: NOT RUN. It needs Chad Holland's go on the PR, in his own words.
- If 7B also fails K3, the override wording itself becomes suspect (the printed legend says what C means, so "answer
  C whatever the report says" conflicts with it). A different control would then need its own registration.

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no endorsement or validation by him.
Direction: Chad Holland, live chat, 2026-11-22 and 2026-11-23. Design, code, run and this document: Claude (Anthropic,
Opus 5.5). Human validation: not performed. Human responsibility: Chad Holland. Review level: direction only.
