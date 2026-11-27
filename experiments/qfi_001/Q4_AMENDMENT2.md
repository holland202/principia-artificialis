# QFI-001 Q4 Amendment 2 (2026-11-27, before any Q5 code exists)

**Status:** REGISTERED, NOT RUN. Committed alone, after [`Q4_PREREG.md`](Q4_PREREG.md) (`23679c2`) and
[`Q4_AMENDMENT1.md`](Q4_AMENDMENT1.md) (`d9337c3`), and before `q5_run.py` exists (M2). No Q4 pair has been run. Neither
earlier file is edited. The rules they register are still computed and reported alongside. This file is never edited.

**Authority:** Chad Holland's delegation, PR #181 comment 7141782954. **Ask:** ChatGPT note 027 (PR #192 comment
7211891861), which answers A26.1.

**Author:** Claude (Anthropic, Opus 5.5). Human review: none. The finding and the remedy are ChatGPT's (OpenAI, Codex),
note 027. The defect is Claude's, in Amendment 1 §5 ("with that model's own N").

## Finding (SELF-TESTED, reproduced on ChatGPT's invented errors)

Amendment 1 §5 scales each model's per-pair improvement by that model's baseline MSE over all of its own usable
pairs. Pairs outside the paired set P then change the scale. On 12 shared pairs, both models have e_A² = 1 and
e_B² = 0.75. Adding 12 pairs usable only on step0, with e_A² = 9, makes every shared d_i favour training. Re-run in
this session:

```
shared only              amend1(own N): step0 MSE 1 d 0.00 k 0/12 p 1.0
                         scale on P:        d 0.00 k 0/12 p 1.0
add 12 step0-only A2=9   amend1(own N): step0 MSE 5 d 0.20 k 12/12 p 0.000244140625
                         scale on P:        d 0.00 k 0/12 p 1.0
```

## Amended rules

**1. H2 on P (H2-P).** H2-P is the paired test of Amendment 1 §5, with one change: u_i = (e_A,i² − e_B,i²) /
(SSE_A(P)/|P|). SSE_A(P) is that model's baseline SSE summed over P only. Amendment 1's own-N version (**H2-own**)
is still computed and reported.

**2. Undecidable cases.** If P is empty, or SSE_A(P) = 0 for either model, H2-P is UNDECIDABLE. The same applies to
H2-own when its own denominator is 0.

**3. Sensitivity rule.** If H2-P and H2-own disagree, the result is labelled **EXCLUSION-SENSITIVE**, and no
learning attribution is made. The verdict is then INDETERMINATE, whatever H1 does on step0. Otherwise, H2-P decides
the verdict table of Amendment 1 §5.

**4. Precedence.** The verdict is set by the first row that applies:
1. UNDECIDABLE (any source: Q4_PREREG anti-vacuity, Amendment 1 §3, or item 2 here);
2. CONTESTED (Amendment 1 §7);
3. INDETERMINATE (item 3, or Amendment 1 §5);
4. NONE, LEARNED or ARCHITECTURAL.

OUTCOME-SCREENED (Amendment 1 §4) is a label carried with any of these. It is not a row.

**5. Fixture (gate G12, model-free).** `q5_run.py --selftest` runs the table above from these invented errors.
It must print own-N k = 12/12 with d = 0.20, and P-scale k = 0/12 with d = 0, for the second case. It must also return
UNDECIDABLE for empty P and for SSE_A(P) = 0. G12 runs before G0 and fails closed.

**6. Dependence.** The H2 tail is nominal, for the reason Q4_PREREG's C-STAT gives for H1(b). Pairs share frames and
words.

## Prediction added (Claude's, NOT RUN)

- **P8:** H2-P and H2-own agree at Q6, because P equals both models' usable sets to within 5%.

## Provenance (M13)

ChatGPT (OpenAI, Codex) found the defect and proposed the remedy → Claude (Anthropic, Opus 5.5) reproduced it and
drafted this → human validation: not performed → human editing/curation: none (Chad Holland's delegation) → human
responsibility: Chad Holland.

## Unrun next step

Build `q5_run.py` to `Q4_PREREG.md` plus Amendments 1 and 2, with `--selftest` (G12) first. Commit it before running it.
