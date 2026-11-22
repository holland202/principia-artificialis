# CCC-001 stage Q diagnostics results: the cache path drifts by up to 0.031, and both "never chose C" and Q2's failure depend on which letter means "not enough" (run 2026-11-21)

**Status:** run as registered at `4726f42` ([QDIAG_PREREG.md](QDIAG_PREREG.md)). Development-only (C-EXPLORE).
Self-tested. Linux container CPU; S25 NOT VALIDATED.
**VERDICT 4 of 7 as registered: P1, P5, P6 REFUTED; P0, P2, P3, P4 HELD.** This is not a pass. P2 and P6 were
predictions that stage Q's failure reproduces. **Stage Q's verdict does not change** (M12): Qwen2.5-1.5B stays not
qualified. What changes is what the recorded refutation means.

Raw output: [`qdiag_run.txt`](../../results/ccc_001/qdiag_run.txt),
[`qdiag_run_sabotage.txt`](../../results/ccc_001/qdiag_run_sabotage.txt),
[`qdiag.json`](../../results/ccc_001/qdiag.json) (every per-item probability and mass),
[`qdiag_prompts.txt`](../../results/ccc_001/qdiag_prompts.txt) (relabeled prompts, printed and read before the run),
[`qdiag_summary.txt`](../../results/ccc_001/qdiag_summary.txt) (from [`qdiag_summary.py`](qdiag_summary.py)).
Harness: [`qdiag.py`](qdiag.py), run at `7cffcbd`, outcome pinned at `b898f94`.

## What could have gone wrong, first

1. **P1 REFUTED: the cached read-out is not within 0.01 of a full forward pass.** The largest difference is
   0.030759 (arm EF64), and already 0.023879 in arm E with a 114-token prefix. The earlier 4-item check (0.00178)
   understated it by more than ten times. No modal letter changed (96 of 96). Stage Q's context-arm numbers are
   re-reported from the uncached path below.
2. **P5 REFUTED: "the model never chose C" was at least partly about the letter.** With no context, the
   not-enough letter was modal on 12, 3, 0, 10 and 10 of 24 items under the five relabelings (registered: ≤ 2 each).
   Whatever meaning it carried, the letter C was modal on 0 of 24 under four relabelings and 3 under the fifth.
3. **P6 REFUTED: Q2's failure depends on the labels.** Under π1 and π5, the two mappings where "not enough" is A,
   the direct instruction raises G by 0.2881 (E > D on 16 of 24) and 0.4149 (22 of 24). By both of Q2's registered
   components that would pass. Under π2, π3 and π4 it fails.
4. **Letter and position move together.** The option line lists A, B, C in order, so every relabeling moves the
   meaning's letter and its place in the line at once. Items 2 and 3 cannot say whether the model favours the
   letter or the first position. This limit was registered.
5. **Harness defect: modal ties go to A.** `modal` takes the first maximum. Under sabotage every probability is
   1/3, so π1 and π5 report "D picks not-enough (A) on 24 of 24". That is the tie rule, not a choice. It touches
   the sabotage reading; whether any unsabotaged item ties was not checked (NOT RUN). Recorded, not fixed.
6. **Additions after registration, before the run:** the `SUPP` lines (Q2 components per mapping, modal-flip
   margins, P3 prefix positions, an equal-length unrelated cache "P3b", per-item mass) were asked for in
   `ccc-relay/chatgpt/004`. They are reported and never gated. The digest also covers the uncached masses. No
   prediction, threshold or item changed.
7. **Self-tested throughout.** Claude wrote the registration, the harness and this file and ran it. ChatGPT
   proposed and reviewed the checks; nobody reviewed the run.

## Output, pasted verbatim (the `SUPP P4` per-item lines are in the raw file)

```
P0 HELD max |p - qualify.json| over D and E (48 items x 3) = 0.000000 (<= 0.01)
P1 REFUTED cached vs uncached, arms E F16 F64 EF64: max diff 0.030759 (<= 0.01), same modal letter on 96 of 96 (= 96)
SUPP P1 arm E     max diff 0.023879  prompt tokens 185..187
SUPP P1 arm F16   max diff 0.015122  prompt tokens 640..642
SUPP P1 arm F64   max diff 0.026870  prompt tokens 2344..2346
SUPP P1 arm EF64  max diff 0.030759  prompt tokens 2437..2439
P2 HELD uncached mean G(E)-G(D) = -0.0491 (< 0.10)
SUPP P2 uncached Q2 components: gain -0.0491 (>= 0.10 to pass), E>D on 14 of 24 (>= 14 to pass), Q2 fails
P3 HELD arm E probes on F16 cache vs arm E uncached: max diff 0.983731 (> 0.01)
SUPP P3 positions: E prefix 114 tokens, F16 cache 569 tokens; suffix starts at position 569 instead of 114
SUPP P3b (development check, not registered) E probes on an unrelated 114-token cache (first 114 tokens of F16's prefix), positions as arm E: max diff 0.982705
P4 HELD median letter mass per arm (>= 0.90 each): D 1.0000  E 1.0000  F16 1.0000  F64 1.0000  EF64 1.0000
SUPP P4 mean G(E)-G(D) on the 24 items with mass >= 0.90 in both D and E: -0.0491
SUPP pi1 {'accept': 'B', 'reject': 'C', 'notenough': 'A'}: D modal {'A': 12, 'B': 12, 'C': 0}, E modal {'A': 0, 'B': 18, 'C': 6}; D picks not-enough (A) on 12 of 24; Q2 gain 0.2881, E>D on 16 of 24, Q2 would pass
SUPP pi2 {'accept': 'C', 'reject': 'A', 'notenough': 'B'}: D modal {'A': 18, 'B': 3, 'C': 3}, E modal {'A': 0, 'B': 11, 'C': 13}; D picks not-enough (B) on 3 of 24; Q2 gain -0.0015, E>D on 10 of 24, Q2 fails
SUPP pi3 {'accept': 'B', 'reject': 'A', 'notenough': 'C'}: D modal {'A': 18, 'B': 6, 'C': 0}, E modal {'A': 7, 'B': 13, 'C': 4}; D picks not-enough (C) on 0 of 24; Q2 gain 0.0758, E>D on 14 of 24, Q2 fails
SUPP pi4 {'accept': 'A', 'reject': 'C', 'notenough': 'B'}: D modal {'A': 14, 'B': 10, 'C': 0}, E modal {'A': 15, 'B': 6, 'C': 3}; D picks not-enough (B) on 10 of 24; Q2 gain 0.0715, E>D on 17 of 24, Q2 fails
SUPP pi5 {'accept': 'C', 'reject': 'B', 'notenough': 'A'}: D modal {'A': 10, 'B': 14, 'C': 0}, E modal {'A': 4, 'B': 6, 'C': 14}; D picks not-enough (A) on 10 of 24; Q2 gain 0.4149, E>D on 22 of 24, Q2 would pass
P5 REFUTED arm D picks the not-enough letter on [12, 3, 0, 10, 10] of 24 for pi1-pi5 (<= 2 each)
P6 REFUTED mean G(E)-G(D) for pi1-pi5 = [0.2881, -0.0015, 0.0758, 0.0715, 0.4149] (< 0.10 each)
VERDICT 4 of 7 as registered
DIGEST 924281cae187830dd557af5a4d024ce44a9e815b0293a4e63ea8e7ae3b635a06
exit 1
```

Sabotage (`--sabotage`, every logit set to zero): P0 REFUTED (0.666662), P4 REFUTED (medians 0.0000, i.e. 3/151936),
P3 REFUTED (0.000000), VERDICT 3 of 7, `SABOTAGE expected P0 REFUTED and P4 REFUTED: True`, exit 1.

Stage Q re-reported from the uncached path (P1's registered consequence), from `qdiag_summary.py`:

```
uncached arm D     S 0.9949 G 0.6236 modal {'A': 14, 'B': 10, 'C': 0}
uncached arm E     S 0.9463 G 0.5745 modal {'A': 18, 'B': 6, 'C': 0}
uncached arm F16   S 0.9893 G 0.6237 modal {'A': 14, 'B': 10, 'C': 0}
uncached arm F64   S 0.9784 G 0.6221 modal {'A': 14, 'B': 10, 'C': 0}
uncached arm EF64  S 0.9060 G 0.5931 modal {'A': 14, 'B': 10, 'C': 0}
```

The cached path in this session reproduced stage Q's `run.txt` summary for every arm (same file).

## Predictions

| ID | Registered | Observed | Outcome |
|---|---|---|---|
| P0 | D and E reproduce `qualify.json` within 0.01 | 0.000000 | HELD |
| P1 | cached vs uncached ≤ 0.01 and modal 96 of 96 | 0.030759; 96 of 96 | **REFUTED** |
| P2 | uncached gain < 0.10 | −0.0491 | HELD (failure reproduces) |
| P3 | E probes on F16 cache differ by > 0.01 | 0.983731 | HELD |
| P4 | median letter mass ≥ 0.90 in every arm | 1.0000 in all five | HELD |
| P5 | D picks not-enough letter on ≤ 2 of 24, each πk | 12, 3, 0, 10, 10 | **REFUTED** |
| P6 | gain < 0.10, each πk | 0.2881, −0.0015, 0.0758, 0.0715, 0.4149 | **REFUTED** |

## What this shows and does not show

- **Implementation:** the cache path agrees with a full pass on every modal letter but not to 0.01; differences
  under about 0.03 between cached arms are not resolvable with this code. The parity check can see a wrong cache,
  both with moved positions (P3) and with the same positions (P3b). S and G are not hiding off-letter mass (P4).
- **Empirical, this model, these 24 items:** the no-context choice tracks the letter or its position more than the
  meaning; the third option was almost never chosen whatever it meant. The direct instruction helps strongly when
  "not enough" is listed first as A, and not otherwise. Stage Q's sentence "does not take the not-enough rule from a
  direct instruction" holds only for the registered labels.
- **Not shown:** whether the effect is the letter A or the first position; anything about other models,
  conversations, maturity or voices.

## Open (M15)

1. Separate letter from position (ChatGPT's proposal in `ccc-relay/chatgpt/004`): keep the meaning order fixed and
   swap letters, then keep letters fixed and move the options. Register first.
2. The next stage Q (Qwen2.5-7B-Instruct, 4-bit, items written by someone other than Claude) reads uncached, reports
   letter mass and gates over all six labelings rather than one.
3. Fix the tie rule in `modal` in a new harness version; this one stays as run.

## Provenance (M13)

Question origin for CCC-001: Federico Talens-Alesson, credited as the question's originator only; no endorsement or
validation by him is implied. Checks proposed and reviewed (registration only) by ChatGPT (OpenAI) in the relay.
Harness, run and this file by Claude (Anthropic, Opus 5.5) in a fresh scheduled session under Chad Holland's standing
direction of 2026-11-21. Human validation: not performed. Human editing/curation: direction only. Human
responsibility: Chad Holland.
