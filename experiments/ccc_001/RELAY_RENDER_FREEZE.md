# Freeze record: RELAY_RENDER_PREREG.md

**Frozen file:** [`RELAY_RENDER_PREREG.md`](RELAY_RENDER_PREREG.md) as committed at `8831888`, SHA-256
`71a47f710960374f9fccf8a936dfafc2037ca763be67ffba0498687d41d61dc9`.
**Frozen at:** 2026-11-22T04:14:23Z. Relay turn 015 was the latest turn. Checkpoint 016 had not been reached, and no
renderer had been built.
**Owner approval:** Chad Holland, in his own words on PR #172
([comment 7074059377](https://github.com/holland202/principia-artificialis/pull/172#issuecomment-7074059377)), as
RELAY.md rule 5 asks. Recorded here by Claude (Anthropic, Opus 5.5).

## What is frozen

- The primary role-neutral rendering, steps 1–10. That covers the P1/P2 labels by author, `&`/`<` escaping, the
  `OPEN`/`CLOSE`/`ACK` bytes as given in `render_feasibility.py` at `8831888`, probe placement, the pinned template,
  no system message, and the OVER_LIMIT rule with no truncation.
- The sensitivity rendering's status: development only, never primary.
- The fixture and its four expected values.
- Predictions R1–R4 and the `--sabotage` anti-vacuity check.

Rule 6 of `RELAY_CHECKPOINTS_PREREG.md` (the role mapping) is now settled as the sensitivity rendering only. The
frozen checkpoint file itself is unchanged.

## What is not frozen

- The measured model, the probe items, any endpoint, threshold or prediction about a model.
- Experimental (arm-A) use of any prefix. That is still a separate approval by Chad.
- The matched-guidance control.
- Long-context qualification. It has not been registered.

## Open at the moment of freezing (disclosed)

Relay turn 015 asked ChatGPT to attack two choices that are now frozen. One is the fixed assistant ACK, a short
line in the model's own role. The other is escaping, compared with failing closed on a delimiter collision.
ChatGPT had not answered when Chad froze the file. If ChatGPT's answer shows a defect, it is recorded as a dated
deviation here or in the results, or it goes into a new registration. The frozen file is never edited.

## Errors found later

Errors are recorded as dated deviations here or in the results. The frozen file is never edited.

## Provenance (M13)

Freeze record written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-22. Human validation:
not performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico Talens-Alesson's;
crediting him implies no endorsement or validation by him.
