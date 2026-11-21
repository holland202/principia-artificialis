# CCC-001 stage Q: qualify a deterministic decision instrument on a pinned open model (registration)

**Status:** REGISTERED, NOT RUN. Development-only instrument qualification (C-EXPLORE). Self-tested.
**Date:** 2026-11-21. **Parent design:** [CCC-001 draft](../../challenges/conversation-context-coherence/PREREGISTRATION_DRAFT_2026-11-21.md)
and its [adversarial review](../../challenges/conversation-context-coherence/ADVERSARIAL_REVIEW_2026-11-21.md)
(draft PR #171, head `205f6c2`). This stage does not freeze CCC-001 and tests no claim about conversation maturity.
**Method:** METHOD.md, WORKFLOW.md and CONTROLS.md as of `main` at `eb648899e7372cad41a517dc628056508749e28a`.

## Question (W1)

Before CCC-001 compares conversation histories, is there a measuring instrument that (a) gives the same numbers
every time for the same input, (b) moves when the model is directly told the decision rule, and (c) returns the
chance value when the mechanism is removed?

This answers a precondition from the CCC-001 draft ("qualify E and positive/negative scorer fixtures") and the
review ("measure same-input noise", "qualifying positive controls"). It also gives a first look at the size of the
**length rival**: how much neutral turns alone move the numbers.

## The instrument

- **Model (stand-in, M4):** Qwen2.5-1.5B-Instruct, bf16, CPU, weights SHA-256 `dd924a11…c6d3ee` (the same file
  CST-001 used). Measuring a small open model is a stand-in for the commercial assistants in the original
  question. Nothing here transfers to ChatGPT or Claude.
- **No sampling.** For each probe the harness reads the next-token logits for the letters `A`, `B`, `C` after the
  full chat prompt and renormalises over those three. Per item: **S** = the largest of the three probabilities
  (decision concentration, 1/3 to 1) and **G** = the probability of the answer key (agreement with an
  evidence-based rule). These map onto the review's endpoints 1 (stability) and 2 (correctness), but here on
  fixed items rather than paraphrases.
- **Memory-off by construction:** a local model has no account memory, tools or hidden state; the context is
  exactly the messages passed in.
- **Probe items:** [`probes.py`](probes.py), 24 report-and-claim items, 8 per key (A accept, B reject,
  C not enough evidence). Written by Claude for this stage. They are **development items from now on**: any
  confirmatory CCC-001 run needs new, sealed items written by someone other than Claude.

## Arms (contexts placed before each probe)

| Arm | Context | Role |
|---|---|---|
| D | none | baseline |
| E | the direct instruction in `common.EXPLICIT` (one user turn and one acknowledging assistant turn) | positive control |
| F16 | 16 turns of synthetic weather log (`weather_filler(16)`, 569 tokens) | length rival, short |
| F64 | 64 turns of the same (2,273 tokens) | length rival, long |
| EF64 | E followed by F64 | does a direct instruction survive 2,273 tokens of unrelated turns |

## Predictions (M2, M5)

- **Q1 (same-input noise, C-NOISE).** Arm D measured three times gives identical per-item probabilities to 6
  decimals.
- **Q2 (positive control, gate).** Mean G(E) − mean G(D) ≥ 0.10, **and** G(E) > G(D) on at least 14 of 24 items.
- **Q3 (anti-vacuity, M3).** With `--sabotage`, which replaces the three letter logits with zeros, every item
  reads S = G = 0.333333, Q2 comes out REFUTED and the harness exits 1.
- **Q4 (assay range).** Under E, the most probable letter equals the key on at least 12 of 24 items.

F16, F64 and EF64 carry **no prediction**. They are an exploratory read of the length rival and of instruction
decay (C-EXPLORE), reported in full and not used to pass or fail anything here.

**Decision rule:** Q1, Q2 and Q4 held → this model is qualified as CCC-001's measured model for the S and G
endpoints. Q2 or Q4 refuted → stop with this model, as CST-001 did, and record it; the next candidate would be a
larger open model.

## Pre-mortem (W2)

1. **Letter bias:** the model may put most mass on one letter whatever the report says. S would then be high in
   every arm and G stuck near one third. The per-arm count of modal letters is printed to show it.
2. **Too weak a model:** CST-001's positive control failed with this exact file on a harder task (0 of 64). If that
   repeats, Q2 or Q4 fails and the stage stops, which is a valid outcome.
3. **Cache mistakes:** reusing the context's KV cache could silently misalign tokens. The harness asserts that the
   prefix tokens of every full prompt equal the cached prefix, and fails otherwise.

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Yes: counts in [`results/ccc_001/feasibility.txt`](../../results/ccc_001/feasibility.txt), committed with this file |
| Noise | Yes: Q1 |
| Statistics | No population claim; thresholds are fixed counts on 24 fixed items |
| Evidence | Numbers come from the harness's printed output, pasted verbatim |
| Independence | No: Claude wrote the items, the code and the predictions and will run them. SELF-TESTED |
| External | Qwen2.5 weights (Apache-2.0); prior work below |
| Device | Linux container CPU only. S25 NOT VALIDATED |
| Verdict code | Fail-closed: exit 0 only if Q1–Q4 hold as registered |
| Exploration | Yes: the whole stage is development-only |
| Held-out | The 24 items become development items; none can be used to confirm CCC-001 |
| Generated inputs | Yes: the weather filler is synthetic; four turns were printed and read before registering |
| People's data | None |
| Design | Instrument qualification; supports no claim about conversations or about any commercial assistant |

## Prior work checked before registering

- Earlier question–answer pairs act as implicit few-shot examples and raise consistency (CAPE, arXiv 2508.20385).
- More in-context examples reduce predictive uncertainty (Wang et al., ACL Findings 2025).
- Pointing the other way, persona consistency falls as dialogue grows (arXiv 2511.00222, Llama-3.1-8B), and persona
  drift appears in long agentic coding sessions, measured against a length-matched filler control (ContextEcho,
  arXiv 2605.24279).
- Telling different models apart from their text alone is already easy: 97.1% in a five-way ChatGPT, Claude,
  Grok, Gemini and DeepSeek classification (Sun et al., ICML 2025). A voice test that pairs different models
  measures that known effect; it needs same-model pairs to say anything new.

So "more context makes outputs more consistent" is not new, and the literature goes both ways. The residual
CCC-001 question is whether an accumulated conversation does more than its length (arm B) and its information
(arm C).

## Limits

One small open model; 24 fixed items; a three-letter forced choice is a narrow stand-in for "a pattern of
reasoning and behaviour"; the stage says nothing about conversation maturity.

## Open door (M15)

If the model qualifies: register CCC-001's within-thread checkpoints using this instrument, with arm A taken from
an accumulated conversation whose turns are written before the items that measure it are drawn, and with new
sealed items from an author other than Claude.

## Provenance (M13)

Direction: Chad Holland, 2026-11-21. Question origin: an external correspondent's question, paraphrased in the
CCC-001 draft; credited as a question only, with no endorsement implied. Parent design: ChatGPT (OpenAI, GPT-6).
This stage's design, items and code: Claude (Anthropic, Opus 5.5). Human validation: not performed. Human
editing/curation: direction only. Human responsibility: Chad Holland.
