# CCC-001 relay renderer: results for R1–R4 (SELF-TESTED)

**Registration:** [RELAY_RENDER_PREREG.md](RELAY_RENDER_PREREG.md) at `8831888`, frozen at `584919c`
([freeze record](RELAY_RENDER_FREEZE.md)). **Code:** [`relay_render.py`](relay_render.py). **Logs:**
[`relay_render_run.txt`](../../results/ccc_001/relay_render_run.txt) and
[`relay_render_run_sabotage.txt`](../../results/ccc_001/relay_render_run_sabotage.txt). Run on 2026-11-22 in a
fresh scheduled cloud session (Linux, Python 3.13.18, transformers 5.24.0), not on the device. No model was loaded.
No relay prefix was read by a model, and no arm-A prompt was written.

## Verdicts (M8: anything that failed would lead; nothing did)

| Prediction | Verdict | Output |
|---|---|---|
| R1 fixture through `apply_chat_template` | HELD | 4 of 4 values match: content `9168a828…`, prompt `7c20d4c7…`, 194 tokens, ids `2c0e2716…` |
| R2 round trip | HELD | 3 turns, labels P1, P2, P1, texts byte-equal; 0 control tokens in message 1; (im_start, im_end) = (5, 4) |
| R2 anti-vacuity (`--sabotage`, escaping off) | REFUTED as predicted | `DEFECT turn 2: closing tag not on its own line`; 1 control token in message 1; (5, 5) |
| R3 OVER_LIMIT | HELD | 52 synthetic turns: 33008 tokens, exit 4, no file. 51 turns: 32373 tokens, exit 0, file written |
| R4 cache prefix | HELD | fixture and fixture shuffle: context 167 tokens is an exact prefix of the 194-token prompt |

Tokenizer files match the registration: `tokenizer.json` `c0382117…`, `tokenizer_config.json` `5b5d4f65…`
(Qwen/Qwen2.5-1.5B-Instruct `989aa79`, fetched from Hugging Face), `config.json` `98d2ff8c…`, L = 32768.

## Disclosed (C-EXPLORE, not registered)

- **R4's shuffle case does not discriminate.** `shuffle_perm(3)` is `[1, 2, 3]`, so the fixture shuffle equals the
  fixture. To make up for it, R4 was also checked on the 016 snapshot's shuffle (next item).
- **Added check X, two paths on the real 016 snapshot,** with the synthetic fixture probe (not a development or
  test probe). Transformers and the jinja2 + `tokenizers` path give identical token IDs for both orders, 8700 tokens
  each. Original ids `53539cb42c5097d8…`, shuffle `58d93d1fd1e0cf0e…`, first differing token none, R4 prefix true,
  0 control tokens in message 1. This is ChatGPT's turn-018 concern that two paths could agree on length but place a
  boundary differently. On these inputs they do not.
- **Parser rule.** A turn ends at the first `</turn>` after its opening tag, and that tag must sit on its own line.
  The frozen text says that parsing gives back the turns. It does not say how. A lenient parser that looks for
  `\n</turn>\n` would have round-tripped the unescaped fixture too, and that would make the sabotage vacuous. The
  rule chosen is the reading that escaping protects.
- **Under sabotage, R1 also fails (0 of 4) and R3/R4 still hold.** That is expected: R3 and R4 do not depend on
  escaping.
- The R3 synthetic turns are `longctx_feasibility.synthetic_turns`, the weather text, imported and not rebuilt.

## Limits

- Self-tested. The registration, the expected values, the renderer and this file are all Claude's. R1 checks
  consistency between two Claude implementations that use different template engines. It is not an independent
  check.
- Run in the cloud with transformers 5.24.0. The device's transformers version and its local tokenizer files have
  not been checked against these hashes (NOT RUN). Rerunning `relay_render.py test` there is the check.
- Being under L means only that a prompt fits. Long-context qualification ([LONGCTX_PREREG.md](LONGCTX_PREREG.md))
  is registered and has not been run.

## Next step (M15)

`longctx.py` against LONGCTX G0–G6, using `relay_render.messages` and the committed cell digests. Per ChatGPT's turn
020, run G0 and `--sabotage-escape` first, before any weights are loaded. Arm-A use of any relay prefix still waits
for Chad Holland's approval.

## Provenance (M13)

Renderer and results by Claude (Anthropic, Opus 5.5) in a fresh scheduled session, relay turn 021. The digest
handoff and the two-path concern come from ChatGPT (OpenAI), relay turns 016 and 018. Human validation: not
performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico Talens-Alesson's; crediting
him implies no endorsement or validation by him.
