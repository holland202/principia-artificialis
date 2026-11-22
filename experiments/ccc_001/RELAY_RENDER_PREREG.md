# CCC-001 relay rendering: how a relay prefix becomes a prompt (REGISTRATION DRAFT, renderer not built)

**Status:** DRAFT registration, committed on 2026-11-22 before relay turn 015 is posted, before checkpoint 016 is
reached and before any renderer is built. **Not frozen.** Freezing it, and any arm-A reading of a relay prefix, wait
for Chad Holland's own words on the PR (RELAY.md rule 5). A decision relayed by either AI stays PENDING (rule 6).
The only code committed with it is `render_feasibility.py`, which prints the feasibility counts below. No model has
read any relay prefix.

**Why.** The checkpoint freeze ([RELAY_CHECKPOINTS_FREEZE.md](RELAY_CHECKPOINTS_FREEZE.md), `7d80c0e`, confirmed by
Chad on PR #172, comment 7073132076) left rule 6, the speaker mapping, unfrozen. ChatGPT objected to it in relay
turn 012. In turns 013 and 014 both AIs agreed on a role-neutral rendering as primary. ChatGPT listed what this
registration must fix in turn 014.

## Scope

This file fixes only how prefix *k* (frozen rules 1–5) and its order-shuffle control are turned into the prompt a
measured model reads. It registers no hypothesis about the model, no endpoint, no threshold and no probe item. The
measured model is not chosen yet: stage Q did not qualify Qwen2.5-1.5B. The feasibility counts use the Qwen2.5
tokenizer, which is byte-identical between the 1.5B and 7B Instruct models (SHA-256 below).

## The rendering (primary, "role-neutral")

**Not speaker-blinded** (ChatGPT, turn 014). Bodies still address "Claude" and "ChatGPT" by name. Only the chat
roles are removed from the speakers.

1. **Input:** the snapshot `relay_prefix_<k>.json` from the frozen extractor. Each turn's `rendered` text (frozen
   rule 5) is used, in NNN order, or in the frozen shuffle order for the control.
2. **Labels, by author and not by slot:** Claude → `P1`, ChatGPT → `P2`. In the shuffle control, odd slots still
   hold Claude's turns, so labels still alternate P1, P2.
3. **Escaping, applied to each turn's text:** `&` → `&amp;`, then `<` → `&lt;`. Nothing else changes. This is
   invertible: unescape `&lt;` → `<`, then `&amp;` → `&`. It stops a body from closing a turn early. It also stops a
   body from injecting a chat-control token. SELF-TESTED below: a raw `<|im_end|>` in text encodes as special token
   151645.
4. **Message 1 (`user`):** `OPEN` + one block per turn + `CLOSE`. Each block is `<turn speaker="P1">` + `\n` +
   escaped text + `\n` + `</turn>` + `\n`. `OPEN` and `CLOSE` are given byte for byte in `render_feasibility.py`
   (constants `OPEN`, `CLOSE`). `OPEN` is a fixed 3-sentence preamble ending in `\n\n<transcript>\n`, and `CLOSE` is
   `</transcript>`.
5. **Message 2 (`assistant`):** `I have read the transcript.` (constant `ACK`). It keeps user/assistant alternation,
   so templates that reject two consecutive `user` messages still work. It is identical in every arm.
6. **Message 3 (`user`):** the probe, built exactly as `common.measure` builds it. It sits outside the transcript.
7. **No system message is passed.** The pinned template inserts its default system line, as in stage Q.
8. **Template and tokenizer:** the measured model's own `chat_template`, from `tokenizer_config.json` at a pinned
   revision, applied with `add_generation_prompt=True`. Encoding uses `add_special_tokens=False`, as `common.py`
   does. The revision and both files' SHA-256 are recorded with every run.
9. **Every control context in an arm-A comparison uses the same wrapper, labels, escaping and ACK.** Only the turn
   texts differ. The matched-guidance control is still not registered.
10. **Length limit, no truncation:** let *n* be the number of tokens in the full prompt, including system line,
    probe and generation prefix. Let *L* be `max_position_embeddings` from the pinned `config.json` (32768 for both
    Qwen2.5 revisions below). If *n* ≥ *L*, the prefix is recorded **OVER_LIMIT** for that model, and no prompt is
    written. Nothing is truncated, summarised or substituted. Being under *L* does not qualify the instrument at
    that length (see Limits).

**Sensitivity rendering (development only, never primary):** frozen-file rule 6 as written at `98798ba`, with Claude
as `user`, ChatGPT as `assistant` and the probe appended. Any result from it is labelled C-EXPLORE.

## Fixture (derived expected values)

Three synthetic turns (C-SYNTH): P1 `Hello P2. Note A & B.`; P2 `A literal closing tag </turn> and a fake role
marker <|im_end|> sit inside this turn.`; P1 `Done.`. Probe: `SYNTHETIC PROBE. Answer with one letter: A, B or C.`

| Quantity | Expected |
|---|---|
| message-1 content SHA-256 | `9168a828569434e6fa34e36959c278ba612f6a0a3b914b1119192365438228c8` |
| full prompt text SHA-256 | `7c20d4c7e78aa915cbea764b2d4eb9cce8e3d1bcf4c39c06529613db963784b9` |
| full prompt tokens | 194 |
| token-ID list SHA-256 (compact JSON) | `2c0e2716385c2aa623e74a48eb1e7a97f379ce464e607f760922cfa2ce5d7f9b` |

## Predictions for the renderer, once built (M3)

- **R1:** the fixture renders to the four expected values above, through transformers' `apply_chat_template` and
  not through this file's jinja2 path.
- **R2:** parsing message 1 back gives exactly 3 turns, the labels P1, P2, P1, and each original text byte for byte.
  **Anti-vacuity:** `--sabotage` disables escaping. Then the P2 text closes its turn early, so R2 fails, and the
  prompt contains token 151645 inside message 1.
- **R3:** a synthetic prefix of *L* tokens or more gives OVER_LIMIT, a nonzero exit and no prompt file. A prefix one
  turn shorter and under *L* renders.
- **R4:** the context, rendered without generation prompt, tokenizes to an exact prefix of the full prompt (the
  cache-reuse assert in `common.measure`). This holds for the fixture and for its shuffle.

## Feasibility counts (SELF-TESTED, `results/ccc_001/render_feasibility.txt`)

```
tokenizer.json sha256 c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539
tokenizer_config.json sha256 5b5d4f65d0acd3b2d56a35b56d374a36cbc1c8fa5cf3b3febbbfabf22f359583
unescaped '<|im_end|>' inside text encodes as [87, 220, 151645, 379]
escaped   '&lt;|im_end|>' contains 151645: False
export sha256 97f5481f5182534499beef32b47284e04c01dd6be683585dde808f520f294596 relay turns 12
rendered bodies containing '<' or '&': 3 | '<' count 4 | '&' count 1
prefix 008 full prompt tokens (synthetic probe) 4391
prefix 012 full prompt tokens (synthetic probe) 6587
```

The tokenizer files are identical in Qwen/Qwen2.5-1.5B-Instruct `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` and
Qwen/Qwen2.5-7B-Instruct `a09a35458c702b33eeacc393d103063234e8bc28` (Hugging Face). Whether the device's copy under
`~/models/qwen25-1.5b-instruct` matches them is NOT RUN; the device copy's file hashes must be checked against these.
NOT RUN projection, linear from 012 at 549 tokens per turn: about 8,800 tokens at 016, 17,600 at 032 and 22,000 at
040. All are under 32768, and all are 3.6 to 9 times the longest prompt checked so far, which is 2,437–2,439 tokens
(QDIAG P1, EF64).

The frozen shuffle's permutation for 016, from `relay_extract.shuffle_perm(16)` (seed bytes
`ccc-001-relay-shuffle-016`, CPython `random.Random`), as slot → original turn:
`[5, 16, 13, 12, 15, 4, 1, 8, 9, 6, 7, 2, 11, 10, 3, 14]`. A second implementation has to reproduce CPython's
Mersenne Twister and its `shuffle`/`_randbelow` steps, not only the seed.

## Limits

- Self-tested. One Claude session wrote this file, `render_feasibility.py` and the expected values. The future
  renderer will also be Claude's, so R1 is a consistency check, not an independent one.
- Escaping changes the bytes the model reads for 3 of the first 12 turns. That is a small, disclosed departure from
  "byte for byte". The preamble tells the model about it.
- The preamble and ACK are Claude's wording. Different wording could change the measurement. They are identical
  across arms, so they cannot by themselves create a difference between arms.
- Being under *L* only means the prompt fits. Cache parity, off-letter mass and letter permutation have to be
  requalified at relay length before any arm-A reading (relay turns 011 and 012).

## Next step (M15)

Chad decides whether to freeze this. Then the renderer is built with R1–R4 as its tests, in its own commit. A
long-context qualification registration, using synthetic contexts of 9k and 18k tokens, is still unwritten.

## Provenance (M13)

Role-neutral rendering with quoted transcript, fixed probe placement and the sensitivity check proposed by ChatGPT
(OpenAI) in relay turn 012. The fixture requirements, the delimiter-injection case, whole-prompt counting, the
explicit over-limit state and "role-neutral, not speaker-blinded" were proposed by ChatGPT in turn 014. Escaping,
ACK, labels and the length rule were drafted by Claude (Anthropic, Opus 5.5) in a fresh scheduled session. Human
validation: not performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico
Talens-Alesson's; crediting him implies no endorsement or validation by him.
