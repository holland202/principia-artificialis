# Intake note — 2026-11-25: memory reminders, evidence sufficiency, corrupted experience

This is reference material, not a research note. It registers no predictions of its own, adds nothing to
NOTES_INDEX.md, and records a supplied literature scan, checks it against primary sources, and lists what PA could
test. One reproduction check was registered and run separately (below).

Supplied by Chad Holland on 2026-11-25 as a scan produced by ChatGPT (OpenAI). Checked by Claude (Anthropic,
Opus 5.5). Human review of this note: none.

**Disposition:** C-EXT, three external preprints. None is independent evidence for anything in PA until reproduced.

## What failed or did not hold (read first, M8)

- **BiDE-Mem (arXiv:2611.32088) was not checked.** The arXiv page rate-limited Claude twice. Its numbers
  (LongMemEval 91.80%, +6.23 points over Mnemis on LoCoMo) are CONTRIBUTOR REPORTED by the scan only. NOT RUN / BLOCKED.
- **ExpGuard (arXiv:2611.32085) reports no numbers in its abstract**, only that "extensive experiments demonstrate
  the effectiveness". The scan does not claim numbers, which is correct. No code or data is linked.
- **One Run Is Not Enough (arXiv:2611.19359): the scan's 19% needs scope.** It is measured on 48 tasks, not on the
  98 in the headline. Otherwise every number the scan reports matches the abstract and the authors' committed data.
- **The scan says the paper "links to a Creative Commons license".** The paper is CC BY 4.0; the code repo is
  Apache-2.0. Both are permissive.

## The three papers

| Paper | Checked against | Status |
|---|---|---|
| One Run Is Not Enough (Passos, 14 Nov 2026) | abstract page; repo renorai/gemma4-memory-study at `2eea9c6`; its committed rows | VERIFIED FROM SOURCE for the abstract; headline numbers recomputed from the rows: see [`REPRO_CHECK_PASSOS_RESULTS.md`](REPRO_CHECK_PASSOS_RESULTS.md) |
| From Memory Access to Evidence Sufficiency / BiDE-Mem (Liu et al., 24 Nov 2026) | not reached | NOT RUN / BLOCKED |
| ExpGuard (Chen et al., 24 Nov 2026) | abstract page | VERIFIED FROM SOURCE for the method description; no results to check |

## What PA could use, as questions to kill

1. **How large is MEM-DECAY-003's rerun noise?** Its draft protocol already plans a noise check: greedy decoding at
   temperature 0, with 10% of calls rerun to check for byte-identical outputs (`PROTOCOL_DRAFT.md` lines 66 and 79).
   Passos's 18.8% comes from a multi-step coding agent, not a single greedy call, so it does not transfer directly.
   Question: if that 10% rerun finds any non-identical outputs, what flip rate does it imply for the scored answers,
   and does the planned sample detect effects smaller than that?
2. **Access versus sufficiency (BiDE-Mem's framing).** Does a memory policy that retrieves the relevant record still
   fail when the record is insufficient to justify the answer? Overlaps MEM-DECAY-003's supersession cases and CST-001.
   Prior-art search needed before any novelty claim.
3. **Matched neutralized replay (ExpGuard's method).** Replaying an experience beside a minimally neutralized copy
   from the same checkpoint is a causal test of whether history changes behaviour. It could serve as CST-001's control.

The scan's combined four-condition proposal (no memory / ordinary / evidence-qualified / corrupted) is a proposal, not
a finding; any version of it needs a measured same-condition flip rate before its effects can be read, for the reason in item 1.

## Door (M15)

Open: BiDE-Mem's numbers, and whether its code exists. Open: MEM-DECAY-003's rerun flip rate.

## Correction (2026-11-25, same day, before review)

The first version of this note (`4a8915f`) said MEM-DECAY-003 "has no same-condition repeat arm". That was wrong:
Claude searched `PROTOCOL_REV1.md` only, and the rerun check is in `PROTOCOL_DRAFT.md`. Item 1 is rewritten above;
the wrong claim is kept here.
