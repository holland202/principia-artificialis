# CCC-001 stage Q results: Qwen2.5-1.5B is not qualified. It is stable, mostly wrong on hearsay, and the direct instruction made it slightly worse (run 2026-11-21)

**Status:** run as registered at `ec1c422` ([QUALIFICATION_PREREG.md](QUALIFICATION_PREREG.md)). Self-tested.
**VERDICT 3 of 4 as registered: Q2 REFUTED; Q1, Q3, Q4 HELD.** By the registered decision rule, this model is
**not qualified** as CCC-001's measured model. Nothing here is evidence for or against conversation maturity.

Raw output: [`results/ccc_001/run.txt`](../../results/ccc_001/run.txt),
[`run_sabotage.txt`](../../results/ccc_001/run_sabotage.txt), [`qualify.json`](../../results/ccc_001/qualify.json)
(every per-item probability), [`cache_check.txt`](../../results/ccc_001/cache_check.txt).

## Failures first

1. **Q2 REFUTED: the positive control did not move the model the right way.** Mean G(E) − G(D) = −0.0495 against a
   registered +0.10. The direct instruction to answer C for hearsay shifted mass toward **A** (modal A on 14 items
   with no context, 18 with the instruction).
2. **The model never chose C.** Across all five arms, the most probable letter was C on **0 of 24** items, including
   the 8 items whose key is C. Hearsay, advertising and single anecdotes were accepted, mostly with near-certainty.
3. **High stability without correctness.** S was 0.9949 with no context while G was 0.6236. This is the case the
   CCC-001 review warned about: a concentrated, repeatable decision that is often wrong. Any CCC-001 endpoint that
   reported S alone would have scored this model as highly "coherent".
4. **The KV-cache path is not bit-identical to a full forward pass.** A check written after the run (W5,
   self-tested) found a largest difference of 0.00178 on 4 items of arm E. It is far too small to change Q2 or Q4,
   but it means cross-arm differences under about 0.002 are not resolvable with this code.
5. **Self-tested throughout:** Claude wrote the items, the code and the predictions, ran them and wrote this.
   Linux container CPU only; S25 NOT VALIDATED.

## Output, pasted verbatim

```
arm D     ctx_tokens     0  S 0.9949  G 0.6236  modal {'A': 14, 'B': 10, 'C': 0}
arm E     ctx_tokens   114  S 0.9440  G 0.5741  modal {'A': 18, 'B': 6, 'C': 0}
arm F16   ctx_tokens   569  S 0.9891  G 0.6236  modal {'A': 14, 'B': 10, 'C': 0}
arm F64   ctx_tokens  2273  S 0.9792  G 0.6215  modal {'A': 14, 'B': 10, 'C': 0}
arm EF64  ctx_tokens  2366  S 0.9045  G 0.5932  modal {'A': 14, 'B': 10, 'C': 0}
Q1 HELD D measured 3 times, identical to 6 dp: True
Q2 REFUTED mean G(E)-G(D) = -0.0495 (>= 0.10), E>D on 14 of 24 (>= 14)
Q3 HELD (fires only under --sabotage)
Q4 HELD E modal letter = key on 14 of 24 (>= 12)
VERDICT 3 of 4 as registered
DIGEST fa3e9cef237fb058c31205d86e346a7dee72ad1fddb0975d281b9f123ad9d38b
exit 1
```

Sabotage run (`--sabotage`): every arm S 0.3333, G 0.3333; Q2 REFUTED (0.0000, 0 of 24); Q3 HELD; VERDICT 2 of 4;
exit 1. The instrument returns the chance value when the mechanism is removed.

## Predictions

| ID | Registered | Observed | Outcome |
|---|---|---|---|
| Q1 | D three times, identical to 6 dp | identical | HELD |
| Q2 | G(E) − G(D) ≥ 0.10 and E > D on ≥ 14 of 24 | −0.0495; 14 of 24 | **REFUTED** |
| Q3 | sabotage gives 0.333333 everywhere, Q2 refuted, exit 1 | as registered | HELD |
| Q4 | E modal letter = key on ≥ 12 of 24 | 14 of 24 | HELD |

Q4 held only because the A- and B-key items are mostly right; it is satisfied by a model that never says C. The
registered threshold did not anticipate that. Recorded, not changed.

## Exploratory reads (no predictions, C-EXPLORE)

- **Length rival:** 2,273 tokens of neutral weather turns lowered S from 0.9949 to 0.9792 and left G almost unchanged
  (0.6236 → 0.6215). In this model, neutral length alone made decisions slightly *less* concentrated.
- **Instruction decay:** the instruction followed by the same 2,273 tokens (EF64) had S 0.9045, the lowest of all
  arms, with modal letters back to the no-context pattern (14 A, 10 B).

## What this shows and does not show

- **Implementation:** the instrument is deterministic on the same input (Q1) and returns chance under sabotage (Q3).
- **Empirical, this model only:** Qwen2.5-1.5B-Instruct accepts unsupported claims and does not take the
  "not enough evidence" rule from a direct instruction on these 24 items. With a positive control that fails, no
  context comparison with this model can show transfer of an evidence procedure.
- **Not shown:** anything about conversation length, maturity, voices, ChatGPT or Claude.

## Open (M15)

1. Re-register stage Q on a larger open model (Qwen2.5-7B-Instruct, 4-bit, as CST-001's amendment used), with new
   items, the same instrument and the same gate.
2. Add Q4's missing condition: a model that never chooses one of the three letters fails assay range.
3. The relay ([RELAY.md](RELAY.md)) keeps building the accumulated conversation that a qualified model would later
   read as arm A.

## Provenance (M13)

Claude (Anthropic, Opus 5.5) designed, ran and wrote this → human validation: not performed → human
editing/curation: direction by Chad Holland, 2026-11-21 → human responsibility: Chad Holland. Review level:
direction only.

## Correction (W9), 2026-11-21

The registered diagnostic ([QDIAG_PREREG.md](QDIAG_PREREG.md), run in [QDIAG_RESULTS.md](QDIAG_RESULTS.md)) narrows
two statements above. The text above is kept as written (M12); the verdict, 3 of 4 with Q2 REFUTED, stands.

- **Failure 2, "The model never chose C":** at least partly a letter effect. When the letters were reassigned, the
  not-enough letter was modal with no context on 12, 3, 0, 10 and 10 of 24 items, and the letter C was rarely modal
  whatever it meant. Q2's failure also depends on the labels: with "not enough" as A, the instruction's gain was
  0.2881 and 0.4149. Letter and position were not separated.
- **Failure 4, "a largest difference of 0.00178 on 4 items":** the full check on all 96 item-arm pairs found
  0.030759 (0.023879 in arm E), with the same modal letter on 96 of 96. Uncached numbers for every arm are in
  QDIAG_RESULTS.md; Q2 recomputed uncached is −0.0491, still failing.

Correction by Claude (Anthropic, Opus 5.5), fresh scheduled session → human validation: not performed → human
responsibility: Chad Holland. Review level: direction only.
