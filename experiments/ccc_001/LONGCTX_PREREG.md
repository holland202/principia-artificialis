# CCC-001 long-context qualification: does the instrument still work at relay length? (REGISTRATION, NOT RUN)

**Status:** REGISTERED, NOT RUN. Development-only instrument qualification (C-EXPLORE). Self-tested. Committed on
2026-11-22 with relay turn 019, before any harness for it exists and before any model has read a prompt of these
lengths. The only code committed with it prints token counts (no model is loaded):
[`longctx_feasibility.py`](longctx_feasibility.py) and [`prompt_lengths.py`](prompt_lengths.py), with their output
in `results/ccc_001/longctx_feasibility.txt` and `results/ccc_001/prompt_lengths_016.txt`.
This file freezes nothing in CCC-001, reads no relay prefix as arm A and involves no confirmatory item.
**Method:** METHOD.md, WORKFLOW.md and CONTROLS.md as of `main` at `15e3b38cd40871d8fb009d8d1843fb986791da6b`.

## Question (W1)

The frozen rendering ([RELAY_RENDER_FREEZE.md](RELAY_RENDER_FREEZE.md)) turns relay checkpoint 016 into prompts of
8,727 to 8,746 tokens. The instrument has only been checked up to 2,437 tokens (QDIAG, EF64). At which of three
registered lengths does it still (a) fit without truncation, (b) give the same numbers twice, (c) put its mass on
the answer letters and (d) move when told the decision rule? Fitting in the context window does not answer (b)–(d).

## Length of checkpoint 016 (SELF-TESTED, feasibility only)

`prompt_lengths.py` on the archival 016 snapshot, frozen rendering, the 24 development probes under π0:

```
snapshot relay_prefix_016.json sha256 fe8775a1c48731844fb129ae71c759928bdb0cc8c32be69a455e9dc4ae23f6e6 turns 16
turns changed by escaping [1, 5, 9, 13, 15] speakers ['claude']
[original] escaped-turn slots [1, 5, 9, 13, 15]
[original] context tokens 8673 | message-1 content tokens 8636
[original] control tokens in message-1 content: im_start 0 im_end 0
[original] dev-probe full prompt tokens min 8727 median 8737.0 max 8746 | under L: True
[shuffle] escaped-turn slots [7, 1, 9, 3, 5]
[shuffle] dev-probe full prompt tokens min 8727 median 8737.0 max 8746 | under L: True
```

Counts include the default system line, the fixed ACK, the probe and the generation prefix. **Output-token
reserve: 0.** The instrument reads next-token logits at the last prompt position and generates nothing. Escaping is
speaker-asymmetric: it changes only Claude's turns. The shuffle moves those turns to other slots, and the token
count is the same in both orders.

## Lengths (registered, in full prompt tokens)

| Name | Arm-D minimum | Role | From the feasibility run |
|---|---|---|---|
| REF | ≥ 2,440 | short reference, near QDIAG's 2,437 | 44 days, 4 turns, D 2,450–2,469, E 2,543–2,562 |
| N016 | ≥ 8,750 | just above every measured 016 prompt (8,746) | 165 days, 14 turns, D 8,773–8,792, E 8,866–8,885 |
| STRESS | ≥ 18,000 | stress case; checkpoint 032 is projected near 17,600 (NOT RUN) | 340 days, 29 turns, D 18,020–18,039, E 18,113–18,132 |

The 9k candidate from turns 015–018 is replaced by N016. Every 016 prompt is under 9,000, and N016 is the
near-maximum case ChatGPT asked for in turn 018.

## Synthetic context (C-SYNTH; code-defined in `longctx_feasibility.py`)

- Text: the assistant lines of stage Q's `weather_filler` (seed 7), one line per day. A turn is 12 consecutive days
  joined by spaces, and the last turn may be shorter. Speakers alternate, Claude → P1 then ChatGPT → P2. Turn 1
  ends with the fixed `MARKUP` sentence, which contains a literal `<|im_end|>` and `&lt;`, so escaping is exercised.
- Wrapped by the frozen rendering: `OPEN`, turn blocks, `CLOSE`, then `ACK`, all imported from
  `render_feasibility.py`.
- Days: the smallest number for which every arm-D prompt (24 items × π0–π2) is ≥ the target. The arm-D maximum
  must be ≤ target + 150.
- Two turns were printed and read before this was written.

## Arms and relabelings

- **D_T:** synthetic context, then the probe.
- **E_T:** the same context, then the relabeled direct instruction pair (`qdiag.explicit(k)`), then the probe.
- **Relabelings π0, π1, π2** from `qdiag.PI`, the cyclic ones, so each meaning gets each letter once. They carry
  equal weight, as ChatGPT asked in turn 010. The 24 development items, their order and the three formats are the
  same at every length.
- **Every reading is uncached.** There is one full forward pass per prompt, with `logits_to_keep=1`. No KV cache is
  used, so no cache parity claim is needed. Any later cached path needs its own registration.

## Gates at each length T (M2, M5)

- **G0 (handoff).** The harness renders through transformers' `apply_chat_template`, not the jinja2 path. It must
  reproduce all 6 cell digests for T in `longctx_feasibility.txt`, and 0 chat-control tokens inside message 1. If
  not, it stops before loading the model and prints the first differing token.
- **G1 (fit).** Every prompt is < L = 32768, and none is truncated.
- **G2 (noise).** Arm D under π0, read twice in one process, matches to 6 decimals on 24 of 24 items.
- **G3 (read-out parity, REF only).** Arm D under π0 gives the same probabilities to 6 decimals with
  `logits_to_keep=1` and with full logits.
- **G4 (letter mass).** In each of the 6 (arm, π) cells, the median over items of the full-vocabulary softmax mass
  on token IDs 32, 33, 34 is ≥ 0.90.
- **G5 (instruction gain).** Mean over π0–π2 of [mean G(E_T) − mean G(D_T)] ≥ 0.10.
- **G6 (item gain).** On ≥ 14 of 24 items, G(E_T) averaged over π is greater than G(D_T) averaged over π.

**T qualifies** when G0–G6 all hold at T. G3 applies at REF only. **The longest qualified length T\*** is the
largest T that qualifies along with every shorter registered T. It is printed as `LONGEST QUALIFIED <name|NONE>`. A
prompt is covered only if its length is ≤ the arm-D maximum at T\*. Checkpoint 016's development prompts (≤ 8,746)
would be covered by N016 (8,792). Any arm-A probe set is measured again before use.

**Reported, never gated:** per (T, arm, π): mean S, mean G, modal-letter counts and mass; per-π gains; and gain
against length.

**Anti-vacuity (M3).** `--sabotage` replaces the full logit vector with zeros, run at REF. Expected: G4 (mass
3/V), G5 and G6 fail, and the harness exits 1. `--sabotage-escape` disables escaping. Expected: G0 fails because
`MARKUP` puts token 151645 inside message 1, and the harness exits 1 without loading the model.

**Verdict:** one HELD/REFUTED line per gate and length, `LONGEST QUALIFIED`, and a `DIGEST` of all per-item
probabilities to 4 dp. It exits 0 only on the outcome pinned after the run, as QDIAG does. The run may be split by
`--length`, with a summary step computing T\*.

## Disclosed before the run (C-EXPLORE)

The gate thresholds are stage Q's. The π set was chosen after QDIAG's numbers were seen. Applied to QDIAG's
short-context uncached gains, π0 `-0.0491`, π1 `0.2881` and π2 `-0.0015`, the G5 aggregate would be `0.0792`,
below 0.10. The choice was not tuned to pass. Those contexts differ from D_T/E_T, so this predicts nothing.

## What each outcome means

| Result | Reading |
|---|---|
| G0 fails | Renderer and feasibility path disagree; resolve the first differing token; no model reading |
| REF fails G5 or G6 | Model not qualified at any length; longer-length numbers are development descriptives only |
| N016 qualifies, STRESS fails | 016 is covered; 032 needs its measured length checked against a new registered length |
| G4 fails at T | S and G at T describe only the letter-conditional choice; T not qualified |

## Feasibility (C-FEAS)

Uncached passes: 3 lengths × (2 arms × 3 π × 24 + 24 noise repeats) = 504, plus 24 for G3 and 144 for the REF
sabotage. NOT RUN projection, linear from QDIAG's 6.7 s per 2,273 tokens on 2 threads: about 7 s, 26 s and 53 s per
pass, so about 4.3 hours on Qwen2.5-1.5B-Instruct (a lower bound, since attention grows faster than linearly).
Memory: full logits at 18k would take about 5.5 GB in bf16, hence `logits_to_keep=1`. The container has 7 GB.
Qwen2.5-7B on this CPU is not feasible in one session (NOT RUN).

## Model

Qwen2.5-1.5B-Instruct, weights SHA-256 `dd924a11…c6d3ee`, tokenizer files as hashed in the feasibility output.
That model did **not** qualify in stage Q. Running this on it is a development diagnostic of length effects, not
a qualification of a measured model. Running it on another model needs a dated amendment naming the revision and
weights hash before the run. The gates are unchanged.

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Above; token counts committed with this file |
| Noise | G2 at every length |
| Statistics | No population claim; fixed thresholds on 24 fixed items |
| Evidence | Numbers come from printed output, pasted verbatim |
| Independence | No. Claude wrote the construction, gates and code and will run them. SELF-TESTED. ChatGPT proposed the lengths' basis, uncached reporting and the digest handoff; that is not review of a run |
| External | Qwen2.5 weights and tokenizer (Apache-2.0) |
| Device | Linux container CPU. S25 NOT VALIDATED |
| Verdict code | Fail-closed; both sabotages must exit 1 |
| Exploration | Yes; disclosed above |
| Held-out | Development items only; none can confirm CCC-001 |
| Generated inputs | Synthetic weather turns, printed and read before registering |
| People's data | None. The 016 snapshot was tokenized only, and no model read it |
| Design | Instrument qualification; no claim about conversations or commercial assistants |

## Limits

- Weather text is not the relay. This qualifies length, not content. The synthetic turns are about 600 tokens
  each, against about 540 in the relay.
- Only one position for the instruction is tested, right before the probe. An instruction placed before the
  transcript is not tested here.
- The ACK sensitivity (two consecutive `user` messages) is not covered. Whether the template renders it cleanly is
  NOT RUN.

## Open door (M15)

After the renderer (R1–R4) at turn 021: build `longctx.py` against these gates, run G0 and `--sabotage-escape`
first, then REF. The checkpoint-032 prompt length is measured at turn 033 and compared with T\*.

## Provenance (M13)

Lengths in full prompt tokens, a reference and bracketing cases, uncached reporting, equal format weighting, and
the token-ID digest handoff: proposed by ChatGPT (OpenAI) in relay turns 010, 012, 016 and 018. Construction,
gates and code: Claude (Anthropic, Opus 5.5), in a fresh scheduled session, under Chad Holland's standing direction
of 2026-11-21. Human validation: not performed. Human responsibility: Chad Holland. The question behind CCC-001 is
Federico Talens-Alesson's; crediting him implies no endorsement or validation by him.
