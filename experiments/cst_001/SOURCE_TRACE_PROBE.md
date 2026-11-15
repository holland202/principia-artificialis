# CST-001 source-tracing probe plan

**Date:** November 15, 2026. **Status:** exploratory, precommitted development plan. The
[CST-001 feasibility record](FEASIBILITY.md) and its original holdout are the historical basis.
Method at [efc29a9](https://github.com/holland202/principia-artificialis/tree/efc29a9fb7b5ade73f7469231f03ea2945cba368).

## Question

Where do the one-root and two-root decisions change when the model is asked for the source
relation, shown the resolved original IDs, or offered the same answer labels in reverse order?

The archived Qwen2.5-1.5B bf16 run scored 0/64 pairs with the explicit tracing instruction (E).
Its scoring and the source-ID manipulation are checked from saved data. The comparison below
probes sensitivity to the way the task is asked. It gives no direct observation of internal
computation and supplies no new test of conversational transfer.

## Fixed run

- Use 16 fresh synthetic pairs, one for each of the original eight domains at each of the two
  hops. Use **Python 3.12**, the existing `cases.make_pair` generator and development seed 7415.
  Alternate AB/BA by domain and reverse that schedule between hops. Use new pair IDs, round-trip
  the observed root IDs against the oracle, and require byte-distinct prompts from the old dev
  split. The original 128-pair CST-001 test split remains outside all model requests.
- Conditions **E**, **O**, **L**, **G**. E uses the explicit prompt from PR #147. O changes only the
  order of the two quoted answer strings in the final question. L uses the same evidence and
  tracing reminder, but asks whether the original IDs are SAME or DIFFERENT. G keeps E's question
  and adds the resolved original IDs in report order before it. Give each prompt an isolated
  context. Order the 128 prompts with a shuffle seeded at 74151, identically for both models.
- Run Qwen2.5-1.5B-Instruct and Qwen2.5-3B-Instruct Q4_K_M. Use llama.cpp b12244
  (commit d5bbcd1f3), x86-64 CPU, four threads, one slot, context 1536, zero GPU layers,
  temperature 0, seed 0, cache off, and a limit of 64 output tokens. Use the Qwen chat envelope
  and its standard helpful-assistant system text. Read exact reply text. Model file hashes and
  engine identity are checked before any prompt. The two deployments share a family and format.
  The historical bf16 and new Q4 runs also differ in engine and decoding configuration.
- Record the first potential case in E for both versions two more times after the fixed schedule
  (three observations of each exact input). Archive all replies with 128 scored records and four
  repeat records per completed model. Stop scoring on missing or duplicate trials, incorrect
  prompt identity, transport failure or any mismatch on the repeated texts. Malformed model
  text on a present trial counts as wrong. Retain every such reply.
- Score correctness on both versions of a pair. Report all four recognizable response patterns,
  unparseable pairs, and correct/reversed pairs by hop. L substitutes SAME for INSUFFICIENT and
  DIFFERENT for CONFIRMED. Read a few mismatches before interpreting the totals. There is one
  fixed horizon and no population inference or significance test in this probe.

## Instrument controls and limits

The root observer reads the report lines and any intermediate-source link, checks the expected
graph shape, and verifies that the resulting relation agrees with the deterministic answer key.
A successful fixture must handle both IDs being the same and having two different IDs. A constant
answer can never earn a correct pair. The real scorer must flag a planted inversion of a complete
synthetic response set, and reject a missing or duplicate trial. One contradictory response must
parse as malformed. This catches scoring mistakes before either deployment is tested.

The older study already used explicit instructions and attempted free-form reasoning on a subset.
The new probe distinguishes the effect of changing the requested answer from the effect of
supplying the IDs. Supplying the IDs also repeats part of the input, so a gain there would not
identify a latent source-extraction deficit by itself. The L prompt changes the task and label
wording, and O tests only option-order sensitivity in this prompt. Both users and models could
respond to cues other than the intended procedure. Fresh synthetic inputs support description of
these deployments and prompts. Human inspection and independent replication remain pending.

| Control | Application |
|---|---|
| C-FEAS | Counts, seals, classes and domain/hop counts printed before model inference. |
| C-NOISE | Three copies of each version of the same E pair per model, with an exact-text gate. |
| C-STAT | Fixed complete schedule and finite-corpus counts. |
| C-EVID | Same-root and independent-root only. Freshness, revocation, unavailable and conflicting evidence are outside this agreement scenario. |
| C-INDEP | Alternate review of the archive by ChatGPT. The new probe is self-tested by its author. |
| C-EXT | Official model metadata and weights; pinned engine source and release. No external text is used in the stimuli. |
| C-DEVICE | CPU container observation only. S25 unmeasured. |
| C-BUILD | Explicit benign, inversion, malformed, missing and duplicate checks. |
| C-EXPLORE | Historical dev motivated the probe. The fresh probe remains exploratory. |
| C-METHCOMP | Prompt-condition probe, outside the SWAY methodology comparison study. |
| C-PRIVATE | Fictional cases and local inference. |
| C-DESIGN | Within-case descriptive comparison of several prompt renderings on the pinned deployments. |
| C-HOLDOUT | Uses a distinct development seed. The original CST-001 holdout remains outside inference. |
| C-SYNTH | Record class and domain coverage, named examples, and whether a person inspected them. |

If a model can apply E and the untouched neutral baseline has room for improvement, the next
study is the preregistered comparison between a procedure-demonstrating dialogue and the
style-matched control. If neither model qualifies, use the per-arm patterns to choose one
change to the feasibility instrument before trying a fresh sample.

Provenance. Chad Holland originated CST-001 and directed its continuation. Claude (Anthropic,
Opus 5.5) authored the original design and feasibility run. ChatGPT (OpenAI GPT-6 family) drafted
this probe after checking the archive. Human validation and line-by-line review are unrecorded.
Human review of this plan is direction only. Research responsibility remains Chad Holland.
