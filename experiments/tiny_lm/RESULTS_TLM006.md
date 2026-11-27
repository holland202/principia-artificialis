# TLM-006 results: with 200 fresh samples per seed, neither retrained model's multi-story copying clears the real-story threshold (NEITHER CLEARED)

**Status:** confirmatory run as frozen ([REGISTRATION_TLM006.md](REGISTRATION_TLM006.md) at `834ff9b`,
[FREEZE_TLM006.md](FREEZE_TLM006.md)). Driver `tlm006_drive.py` at `4ce1154` (SHA-256 `1c16f281…d802`), committed
before any run. The samples were committed before the driver read them (`4af3342`). **VERDICT row 9: NEITHER CLEARED.**
SELF-TESTED by Claude, who wrote the driver. ChatGPT's sealed decision-table cases (T6) have not run. Linux container
CPU, 2 processes, about 1 h 50 min. S25 NOT VALIDATED. Authority for the run: Chad Holland's direction in live chat on
2026-11-27, recorded in note tlm006/claude/014 on PR #197.

## What could have gone wrong, first

1. **These are not TLM-004's models.** TLM-004's weight files were never committed, and no copy was found. Both
   retrained models failed G1 (weight hash) and G2 (seeds 5000–5019 reproduce TLM-004's samples), so both are
   **RECIPE REPLICATE** under the frozen scope rule ([retrain record](../../results/tiny_lm/006/retrain/README.md)).
   - Seed 41 matched TLM-004's training curve to four decimals except at one point, with the same validation score.
   - Seed 42 differed from step 500 (validation 0.8577 against 0.8571). The cause is unknown.
   - So this result is about the training recipe and these two retrained models. It does not directly re-test the
     seed-41 model behind TLM-005's 0.0405.
2. **ChatGPT's T6 check has not run.** ChatGPT sealed 13 decision-table cases with expected rows (cases `f0fce0fd…`,
   key `b254f764…`). Until they run against `decide()` at `4ce1154`, only Claude's synthetic self-test (12 of 12) backs
   the decision function. The closeout waits for T6.
3. **Self-tested and not independent.** Claude wrote the driver and ran it. The attributor it imports
   (`tlm005_attrib.py`) passed ChatGPT's blind controls in TLM-005 (CONTRIBUTOR REPORTED). No human has checked the
   numbers (M10).
4. **Run-time hazards, disclosed:**
   - The first seed-42 retrain was killed when a background process was stopped. It was rerun from scratch and matched
     where they overlapped.
   - A separate retrain on the S25 diverged (another Claude session's diagnostic, `5823527`, `6b60685`). It is not
     used here.

## Raw output (`results/tiny_lm/006/confirmatory/confirmatory_run.txt`, excerpt, verbatim)

```
G0 HELD
R fixture: normal U 0 R 1 | --df-any U 1 R 0 (need R >= 1, then R = 0)
t41: E 2341 U 17 R 45 B 0 | u 0.0073 r 0.0192 copy 0.0265 | E per text min 2 q1 10 median 11 q3 14 max 22
t42: E 2287 U 21 R 46 B 0 | u 0.0092 r 0.0201 copy 0.0293 | E per text min 2 q1 9 median 11 q3 14 max 21
null: E 2777 U 52 R 73 B 0 | u 0.0187 r 0.0263 copy 0.0450 | E per text min 7 q1 12 median 13 q3 15 max 42
pos: E 3046 U 2923 R 123 B 0 | u 0.9596 r 0.0404 copy 1.0000 | E per text min 7 q1 11 median 14 q3 16 max 63
--df-any R total over every set: 0 (need 0)
r t41: 0.0192 vs reference max 0.0287 -> no
r t42: 0.0201 vs reference max 0.0287 -> no
r pos: 0.0404 vs reference max 0.0287 -> yes
r null: 0.0263 vs reference max 0.0287 -> no
u t41: 0.0073 vs reference max 0.0215 -> no
u t42: 0.0092 vs reference max 0.0215 -> no
same-input noise t41: r per 20-sample sub-block [0.0129, 0.0161, 0.0271, 0.0085, 0.0051, 0.0206, 0.038, 0.0201, 0.0346, 0.0081]
same-input noise t42: r per 20-sample sub-block [0.0233, 0.0225, 0.0, 0.0275, 0.017, 0.0183, 0.0088, 0.0312, 0.016, 0.0362]
S2 t41: per-text mean r 0.0193 vs reference max 0.0318 (E = 0 texts excluded: 0)
S2 t42: per-text mean r 0.0219 vs reference max 0.0318 (E = 0 texts excluded: 0)
S1 t41: r 0.0192 vs cut-reference max 0.0304 -> no (token cap 334)
S1 t42: r 0.0201 vs cut-reference max 0.0304 -> no (token cap 334)
gates {'G0': True, 'G3': True, 'rfix_R': 1, 'rfix_R_dfany': 0, 'dfany_R_total': 0}
VERDICT row 9: NEITHER CLEARED
```

The 10 reference blocks' r values, from the JSON (SHA-256 `eaf902db…`): 0.0234, 0.0287, 0.0271, 0.0208, 0.0225, 0.0214,
0.0270, 0.0248, 0.0239, 0.0271.

## Gates and controls

| Check | Required | Result |
|---|---|---|
| G0: the TLM-005 lines reproduce | exact | **HELD** |
| G3: valid stories | ≥ 2,600 | **27,631** |
| R fixture | R ≥ 1, then R = 0 under `--df-any` | **1 → 0** |
| `--df-any` sabotage | R = 0 in every set | **0** |
| Positive control (training stories as a pseudo-seed) | clears on r or u | **clears both** (u 0.9596, r 0.0404) |
| Null control (valid stories 2,200–2,399) | reported, not gated | **does not clear** (r 0.0263) |
| B after masking | 0 | **0** in every set |

## What this shows

- **With 200 fresh samples, neither retrained model's multi-story rate clears the real-story threshold.** The rates
  are r 0.0192 (seed 41) and 0.0201 (seed 42), against a maximum of 0.0287 over ten 200-story reference blocks.
  - Both sensitivity analyses agree: S1, references cut to the model's token length (maximum 0.0304), and S2, per-text
    means (maximum 0.0318).
  - Single-story rates (u 0.0073 and 0.0092) are also below every reference block.
  - No model text has a verbatim match of 200 bytes or more. The longest are 109 and 106 bytes.
- **Same-input noise is large at 20 samples.** Seed 41's ten 20-sample sub-blocks range from 0.0051 to 0.0380 in r.
  TLM-005's 0.0405 came from 20 samples of the original seed-41 model. Here, 20-sample blocks from a model trained by
  the same recipe span nearly that whole range. That is consistent with the rival (a 20-sample draw), but it does not
  show it was the cause. As registered, NEITHER CLEARED says only that neither model cleared the threshold on this
  sample.

## What this does not show

- That TLM-004's own seed-41 model had no excess (see item 1 above).
- Anything about how the models learned, larger models, other prompts or other seeds.
- Any false-alarm rate: the threshold is descriptive, as registered.

## Open (M15)

- **T6:** ChatGPT runs its sealed decision-table cases against `decide()` at `4ce1154`. The closeout (W8) follows it.
- **The door:** near-duplicate training stories counted as one document, still open since TLM-005.
- **Separately,** why the S25 retrain diverges (the other session's diagnostic) and why the seed-42 retrain differs
  from TLM-004's log from step 500.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) wrote the driver, ran it and wrote this, under a registration attacked
by ChatGPT (OpenAI GPT-6, Codex) notes tlm006/chatgpt/002, 004 and 006. A second Claude session diagnosed the S25
retrain. Human validation: not performed. Direction, freeze approval and run direction: Chad Holland, 2026-11-25 to
27. Human responsibility: Chad Holland. Review level: direction only.*
