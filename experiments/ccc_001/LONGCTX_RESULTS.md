# CCC-001 long-context qualification: REF results (development diagnostic, model not qualified)

**Registration:** [LONGCTX_PREREG.md](LONGCTX_PREREG.md) at `cf1fbcd`. **Deviations, committed before any model
reading:** [LONGCTX_DEVIATIONS.md](LONGCTX_DEVIATIONS.md) at `633ed1e`. **Harness:** [longctx.py](longctx.py), run
at `c537acb`, outcome pinned at `80c7fc1`. Relay turn 023, 2026-11-22. Development-only (C-EXPLORE). Nothing in
CCC-001 is frozen by this, no relay prefix was read by a model and no confirmatory item is involved.

## What could have gone wrong, first

- **Self-tested.** Claude wrote the construction, the gates, the harness and the deviations, and ran them.
  ChatGPT (OpenAI) proposed the REF-first order and the digest handoff; that is not a review of this run.
- **The model is not qualified.** Qwen2.5-1.5B-Instruct failed stage Q. It fails here again, at REF, on the same
  two instruction-gain criteria. Nothing below qualifies a measured model.
- **Scope cut (D1).** Only REF was read by the model. N016 and STRESS are **NOT RUN**. Because REF failed, the
  registration's T\* rule makes both ineligible whatever they would show.
- **The `--sabotage` control only discriminates G4.** G5 and G6 already fail in the real run, so their failure
  under zero logits shows nothing new. G4 (mass `1.0000` real, `0.0000` sabotaged) is the gate the control tests.
- **G2 and G3 are same-process, same-machine checks.** Linux container CPU, 2 threads, torch 2.15.0+cpu,
  transformers 5.24.0. S25 NOT VALIDATED.
- **Synthetic text.** Weather turns, not the relay. This says nothing about conversations.

## Raw output

G0 with no weights loaded ([longctx_g0.txt](../../results/ccc_001/longctx_g0.txt)): all 18 cell digests match the
committed feasibility output, at all three lengths, with 0 control tokens inside message 1.

```
VERDICT 3 of 3 as registered
DIGEST fa5c56adae8c2c43aa231b9936de16473a1516a7e2f9876efac22305a1e09a9b
```

`--sabotage-escape` ([log](../../results/ccc_001/longctx_g0_sabotage_escape.txt)), exit 1, weights not loaded:

```
G0 [REF] REFUTED 6 cell digests and window; control tokens inside message-1 content: 1 (= 0)
  [REF] first differing token (arm D pi0 item 0) at position 696: harness [220, 151645, 323] ' <|im_end|> and' vs feasibility [609, 4832, 26] ' &lt;'; lengths 2459 vs 2467
VERDICT 0 of 3 as registered
```

REF ([longctx_ref_run.txt](../../results/ccc_001/longctx_ref_run.txt), weights `dd924a11…c6d3ee`, 18 min 48 s):

```
G1 HELD longest prompt 2562 tokens (< L 32768); no truncation is applied anywhere
G2 HELD arm D pi0 read twice: equal to 6 dp on 24 of 24 (= 24), max diff 0.000000
G3 HELD arm D pi0 logits_to_keep=1 vs full logits: equal to 6 dp on 24 of 24 (= 24), max diff 0.000000
G4 HELD median letter mass per cell (>= 0.90 each): Dpi0 1.0000  Dpi1 1.0000  Dpi2 1.0000  Epi0 1.0000  Epi1 1.0000  Epi2 1.0000
G5 REFUTED mean over pi0-pi2 of mean G(E)-G(D) = 0.0523 (>= 0.10); per pi [-0.0294, 0.2321, -0.0457]
G6 REFUTED items with pi-averaged G(E) > G(D): 12 of 24 (>= 14)
REPORT item gain by stage-Q key (pi-averaged G(E)-G(D)): A 0.2887 (n=8)  B -0.0576 (n=8)  C -0.0741 (n=8)
LONGEST QUALIFIED NONE (only REF was read: D1)
VERDICT 5 of 7 as registered
DIGEST 1ebd6751e49dcb09d4118dd86188efb9d7613b7631f8d6eb9f9a8c5916eb57c4
```

`--sabotage` ([log](../../results/ccc_001/longctx_ref_run_sabotage.txt)), exit 1:
`G4 REFUTED … Dpi0 0.0000 …`, `G5 REFUTED … 0.0000`, `G6 REFUTED … 0 of 24`,
`SABOTAGE expected G4, G5 and G6 REFUTED: True`, `VERDICT 4 of 7 as registered`.

A second run of the pinned harness at `80c7fc1` ([log](../../results/ccc_001/longctx_ref_rerun.txt)) printed
`DIGEST 1ebd6751e49dcb09d4118dd86188efb9d7613b7631f8d6eb9f9a8c5916eb57c4`, `RECORDED match` and exited 0.

## Gate table (REF)

| Gate | Result | Number |
|---|---|---|
| G0 handoff | HELD | 6 of 6 digests, 0 control tokens |
| G1 fit | HELD | max 2,562 < 32,768 |
| G2 noise | HELD | 24 of 24, max diff 0.000000 |
| G3 read-out parity | HELD | 24 of 24, max diff 0.000000 |
| G4 letter mass | HELD | median 1.0000 in all 6 cells |
| **G5 instruction gain** | **REFUTED** | 0.0523 < 0.10 |
| **G6 item gain** | **REFUTED** | 12 of 24 < 14 |
| N016, STRESS | NOT RUN | D1 |

## What this shows and does not show

- **Implementation (self-tested):** the transformers path reproduces the feasibility path's token IDs at all three
  lengths, escaping keeps `<|im_end|>` out of message 1 and disabling it puts it there, and `logits_to_keep=1`
  changes nothing at 6 dp at REF.
- **Empirical, this model, synthetic text:** at about 2,450–2,560 tokens the instruction fails to move the model by
  the registered amount. Per the registration's outcome table, the model is not qualified at any length; longer
  lengths would be development descriptives only.
- **Post-hoc, not gated:** the per-π gains have the same sign pattern as QDIAG's short contexts (π0 `-0.0491`,
  π1 `0.2881`, π2 `-0.0015`, quoted in the registration): only π1, where "not enough" is A, gains. Averaged over π,
  the instruction raises G on accept-keyed items (`0.2887`) and lowers it on reject (`-0.0576`) and not-enough
  (`-0.0741`) items. That fits a letter or position effect interacting with the instruction better than evidence
  following; it is an interpretation, not tested here.
- **Not shown:** anything at 8,750 or 18,000 tokens, anything about the relay, any other model.

## Open (M15)

- A model that passes stage Q is needed before N016 is worth reading. On this CPU, 7B is not feasible (NOT RUN).
- The placement registration agreed in turns 021–022 (both slots outside the transcript) is drafted next, not run.

## Provenance (M13)

Claude (Anthropic, Opus 5.5), fresh scheduled session, under Chad Holland's standing direction of 2026-11-21.
REF-first order and the token-ID digest handoff: ChatGPT (OpenAI), relay turns 018, 020, 022. Human validation:
not performed. Human responsibility: Chad Holland. The question behind CCC-001 is Federico Talens-Alesson's;
crediting him implies no endorsement or validation by him.
