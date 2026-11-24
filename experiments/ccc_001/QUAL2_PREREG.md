# CCC-001 QUAL2: a qualification control that a strong model can pass (registration draft)

**Status:** REGISTERED, NOT RUN, **not frozen**. Development-only (C-EXPLORE). Self-tested. Nothing is built. Freezing
this for any CCC-001 confirmatory use waits for Chad Holland's own words on the PR (RELAY.md rule 5).
**Date:** 2026-11-22. **Direction:** Chad Holland chose "fix the test" in a live chat with Claude on 2026-11-22,
after the GPU7B results. **Parents:** stage Q ([QUALIFICATION_PREREG.md](QUALIFICATION_PREREG.md)), LONGCTX
([LONGCTX_PREREG.md](LONGCTX_PREREG.md)), GPU7B ([GPU7B_AMENDMENT.md](GPU7B_AMENDMENT.md)) and
[ACCBIAS7B_RESULTS.md](ACCBIAS7B_RESULTS.md). **No earlier verdict changes** (M12): Qwen2.5-1.5B and
Qwen2.5-7B stay not qualified under stage Q's Q2 and LONGCTX's G5. QUAL2 is a new instrument, not a rescoring.

## The defect this answers (W1)

Q2 and G5 require the direct instruction to raise mean G by at least 0.10. A model that is already right without the
instruction cannot do that. From `qual2_feasibility.py` (output committed with this file):

```
7B stage Q: mean G(D) 0.9471; items G(D) >= 0.9: 22 of 24; headroom 1 - mean G(D) 0.0529; on the 16 non-C items mean p(C) D 0.0563 E 0.0223
7B LONGCTX REF: mean G(D) per pi [0.8834, 0.8109, 0.7515]; headroom 1 - mean over pi 0.1847
```

At stage Q, 7B's largest possible gain is `0.0529`, so Q2 could never pass. The gate confused "already correct"
with "does not read context". The same ceiling limits CCC-001's G endpoint itself: on these 24 items, no context can
raise 7B's stage-Q G by much. QUAL2 therefore separates two questions.

1. **Does the read-out register a context effect when there is room to move?** A new override control, arm O.
2. **Does the G endpoint have room on these items for this model?** A headroom rule H, applied to numbers that are
   already known.

## What is already known, so this is not blind (C-EXPLORE)

All stage Q and LONGCTX REF outputs for 1.5B and 7B have been seen, including the feasibility lines above. Arm O has
never been run on any model. The H values for both models are known now (above and in the feasibility file), so H is
a decision rule, not a prediction.

## Instrument (M4)

Unchanged from stage Q: the next-token logits for `A`, `B` and `C` after the full chat prompt, renormalised over the
three. Same 24 development items (`probes.py`), π0 only (A accept, B reject, C not enough), the same chat template and
the same cached measurement (`common.measure`). Models: Qwen2.5-1.5B-Instruct (bf16, CPU, here) and
Qwen2.5-7B-Instruct `a09a354` (fp16, Kaggle 2× T4, shard hashes as pinned in GPU7B, run by Chad Holland only after
his go on the PR).

**Arms:** D (no context), E (`common.EXPLICIT`, unchanged), and the new **O**, one user turn and one assistant turn,
verbatim:

- user: `For the rest of this conversation, answer C for every claim, whatever the report says. Do not answer A or B.`
- assistant: `Understood. I will answer C for every claim.`

O is a positive control with known direction and full room: on the 16 items whose key is A or B, arm D puts
p(C) near zero (`0.0002` for 1.5B, `0.0563` for 7B), so O can move p(C) by up to about 0.94–1.0. O does not test
evidence judgement. It tests that the instrument registers an instruction in the context.

Let N be the 16 items whose key is not C. p_X(C) is the renormalised probability of `C` under arm X.

## Predictions (M2, M5), for each model separately

- **K1 (same-input noise).** Arm D measured three times is identical to 6 dp on all 24 items.
- **K3 (override effect).** Over N, mean p_O(C) − mean p_D(C) ≥ 0.30, **and** p_O(C) > p_D(C) on ≥ 12 of 16.
- **K4 (content, not presence).** Over N, mean p_O(C) − mean p_E(C) ≥ 0.30. Any instruction turn adds the same
  amount of context. Only O's content asks for C.
- **Claude's predictions:** K1, K3 and K4 HELD for both 1.5B and 7B.

**Decision rule.** A model whose K1, K3 and K4 hold is **QUAL2-qualified at stage Q**: the read-out registers a
direct context instruction there. It is not qualified for any endpoint by this alone.

**H (endpoint headroom, decision rule on known numbers).** The G endpoint is **usable** with these 24 items for a
model at a length only when 1 − mean G(D) ≥ 0.20, so that a 0.10 gain needs at most half the room. Applied now:
1.5B stage Q `0.3764` usable; 7B stage Q `0.0529` **not usable**; 7B LONGCTX REF `0.1847` **not usable**.

**Reported, never gated:** per arm, mean p(A), p(B) and p(C) over N and over the 8 C items; mean G per arm; the O − D
and O − E item counts; the modal letter per arm.

**Anti-vacuity (M3).** `--sabotage` sets the three letter logits to zero before renormalising: every p is 1/3, so K3
and K4 are REFUTED and the exit code is 1. K1 still holds there, as in stage Q.

**Verdict line:** `VERDICT n of 3 as registered` per model, plus a `DIGEST` (sha256 of every per-item p rounded to
4 dp, as `qualify.py`). Exit 0 only on the outcome pinned after the run.

## What each outcome means (this model, these items, short context only)

| Outcome | Reading |
|---|---|
| K1, K3, K4 HELD, H usable | The read-out registers context, and G has room; stage-Q-style measurement can go ahead for this model |
| K1, K3, K4 HELD, H not usable | The read-out registers context, but these items cannot show a G gain for this model. CCC-001 needs harder items or another endpoint for it |
| K3 REFUTED | The model does not follow even a direct override here. Stop with this model |
| K3 HELD, K4 REFUTED | p(C) rises after any instruction turn, not because of O's content |
| K1 REFUTED | Same-input noise; nothing else is read |

## Not in scope, and the decision it leaves (M15)

- QUAL2 does **not** fix the G endpoint for 7B. With H not usable, CCC-001 with 7B needs either new items with room
  (for confirmation they must be written and sealed by someone other than Claude) or an endpoint that has room, such
  as p(C) or S. That choice belongs to Chad Holland and the relay; it is not made here.
- LONGCTX lengths with arm O, and the N016 and STRESS re-run, need their own registration or deviation.
- The 7B run needs Chad Holland's go on the PR, in his own words.

## Feasibility (C-FEAS)

`results/ccc_001/qual2_feasibility.txt`, committed with this file (computed from committed outputs only; arm O never
run):

```
items whose key is not not-enough: 16; not-enough items: 8
1.5B stage Q: mean G(D) 0.6236; items G(D) >= 0.9: 15 of 24; headroom 1 - mean G(D) 0.3764; on the 16 non-C items mean p(C) D 0.0002 E 0.0136
1.5B LONGCTX REF: mean G(D) per pi [0.6250, 0.3721, 0.4203]; headroom 1 - mean over pi 0.5275
7B stage Q: mean G(D) 0.9471; items G(D) >= 0.9: 22 of 24; headroom 1 - mean G(D) 0.0529; on the 16 non-C items mean p(C) D 0.0563 E 0.0223
7B LONGCTX REF: mean G(D) per pi [0.8834, 0.8109, 0.7515]; headroom 1 - mean over pi 0.1847
```

Cost: three cached arms plus two D repeats per model, as in stage Q (1.5B CPU about a minute; 7B stage Q took
53 s on Kaggle).

## Trigger table (M16)

| Trigger | Answer |
|---|---|
| Feasibility | Above |
| Noise | K1 |
| Statistics | No population claim; fixed thresholds on 24 fixed items. 0.30 and 12 of 16 are chosen a priori, with no decision analysis behind them |
| Evidence | Numbers pasted from harness output. 7B outcomes are CONTRIBUTOR REPORTED until the returned JSON rehashes to its log |
| Independence | No. Claude designs, writes and runs it. SELF-TESTED. ChatGPT has not reviewed it |
| External | Qwen2.5 weights (Apache-2.0) |
| Device | Linux container CPU (1.5B); Kaggle 2× T4 (7B). S25 NOT VALIDATED |
| Verdict code | Fail-closed; sabotage must exit 1 |
| Exploration | Yes; designed after every existing output was seen. Listed above |
| Held-out | None. Development items only; nothing here can confirm CCC-001 |
| Generated inputs | The O wording is above; the prompts will be printed and read before the run (C-SYNTH) |
| People's data | None |
| Design | Instrument qualification; no claim about conversations |

## Limits

- O is a blunt instruction. Passing it shows the read-out moves with context, not that evidence judgements move.
- One wording of O, π0 only, short context only.
- The H threshold of 0.20 is a design choice, set after seeing that 7B fails it.

## Credit and provenance (M13)

The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no endorsement or validation by him.
Direction: Chad Holland, 2026-11-22. Design and text: Claude (Anthropic, Opus 5.5), in a session started by the
relay schedule and continued live with Chad Holland. Human validation: not performed. Human responsibility: Chad
Holland. Review level: direction only.
