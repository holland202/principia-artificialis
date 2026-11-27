# TOR-001 results (public fields F1–F3): the approved run returned INCONCLUSIVE because of a verdict-code defect; re-evaluated on its own numbers, row 4: the torus model beats the named baselines, but the projection itself is not shown to help

**Status:** run on the public fields as frozen ([REGISTRATION_TOR001.md](REGISTRATION_TOR001.md) at `3dbfed0`,
[FREEZE_TOR001.md](FREEZE_TOR001.md)), on Chad Holland's approval (PR #186, comment 7222720820), code `36d5d4a`
(SHA-256 `9e4527de…7079`). SELF-TESTED by Claude, who wrote the code. ChatGPT's blind fields A and B are not run yet.
Linux container CPU, 2 threads, torch 2.15.0+cpu, numpy 2.5.3. Fit time about 100 s per learned arm, 57 minutes in
total. S25 NOT VALIDATED.

## What could have gone wrong, first

1. **The approved run's verdict is row 1, INCONCLUSIVE, and no prediction was evaluated**
   ([`run_36d5d4a.txt`](../../results/tor_001/run_36d5d4a.txt), [`tor001_results_36d5d4a.json`](../../results/tor_001/tor001_results_36d5d4a.json)).
   - The log shows G1 HELD and all three interface checks True.
   - `gen()` built G1 with `&=` on a NumPy comparison, so G1 reached `decide()` as `numpy.bool`. The fail-closed check
     `gates["G1"] is True` rejects that type. It failed closed, so a pass was reported as INCONCLUSIVE, never the
     other way round.
   - The 10-case self-test used Python booleans, so it could not catch this.
   - It is the same class of defect as QFI-001 Q1's first run.
2. **Deviation: the verdict below is a re-evaluation, not the approved run's own output.**
   - The fix (`d087c03`) makes `gen()` return a Python `bool`, and makes `run` exit if a gate is not one.
   - `tor001_reval.py`, committed before it ran, applies the fixed `decide()` to the approved run's saved error table.
     It reads the gates from that run's log.
   - Nothing was retrained or rescored.
   - An end-to-end rerun at the fixed commit has since been done. It gives the same row 4 directly from `run`
     (section below).
3. **Self-tested.** Claude wrote the plan's draft, the code and this file. ChatGPT attacked the plan (notes 002 and
   004) and found the missing-measurement defect (note 010). Its blind fields will test the code independently of
   Claude's choices, but not of Chad's shared instructions (M10).
4. **Named stand-ins (M4):**
   - MLPs, not the post's convolutional layers;
   - one tanh hidden layer;
   - E2's dynamics map z to MLP(z);
   - K4's A starts at the identity;
   - ω starts at (0.5, 0.5).

## Raw output (`reval_d087c03.txt`, verbatim)

```
gates read from the run log: G1 True | interface lines 3 all True True
P1 inputs: F1 L4 h1000 0.0014
P2 inputs: F2 T2 h1000 median 0.0259; K4 median 0.2866; L4 0.9104
P3 inputs: F2 L* h1000 0.0406
P4 inputs: F2 E2 h1 median 0.3807; T2 h1 median 0.0218
P5 inputs: F3 T2 h100 median 0.4365
P6 inputs: F2 NP h1000 median 0.0312; paired T2<NP per seed [False, False, True]
P1: HELD
P2: HELD
P3: HELD
P4: HELD
P5: HELD
P6: REFUTED
VERDICT (re-evaluated) row 4: T2 BEATS THE NAMED BASELINES; NO PROJECTION BENEFIT MET P6
```

## Predictions

| ID | Criterion | Value | Verdict |
|---|---|---|---|
| P1 | F1: L4 at 1,000 steps < 0.01 | 0.0014 | **HELD** |
| P2 | F2: T2 < 0.10, and K4 and L4 each ≥ 3× T2 (1,000 steps, medians) | T2 0.0259; K4 0.2866; L4 0.9104 | **HELD** |
| P3 | F2: T2 ≤ L* (27 modes) at 1,000 steps | 0.0259 ≤ 0.0406 | **HELD** |
| P4 | F2: E2 at 1 step ≥ 3× T2 | 0.3807 vs 0.0218 | **HELD** (no topology claim, as registered) |
| P5 | F3: T2 at 100 steps > 0.30 | 0.4365 | **HELD** |
| P6 | F2: T2 ≤ ½ × NP (medians), and T2 < NP in ≥ 2 of 3 paired seeds | 0.0259 vs ½ × 0.0312; T2 lower in 1 of 3 | **REFUTED** |

## What this shows, on these synthetic fields

- **On the post's own field (F1), the linear rival is enough.** POD + DMD with 4 modes reaches 0.0014 at 1,000 steps.
  That is better than every learned arm, including T2 (0.0113 to 0.0164 across seeds). This is what the algebra in
  SOURCE_POST.md predicted.
- **On the curved torus (F2), T2 has the lowest median 1,000-step error among the named baselines:**
  - T2: 0.0259;
  - K4, a free 4-number latent with linear dynamics: 0.2866;
  - L4: 0.9104;
  - L*, 27 linear modes: 0.0406.
- **But the projection onto the torus is not shown to be the reason.** NP is T2 with the same rotation dynamics and
  without the projection. Its median is 0.0312, and it beat T2 in 2 of 3 seeds. As registered, no component is
  credited, because no arm removes only the rotation dynamics. The comparison with K4 is consistent with fixed-speed
  rotation dynamics helping. That is not a registered test, so it is an observation, not a finding.
- **The wrong-topology control separated (P5).** On the three-phase field F3, T2 stays around 0.44 at every horizon.
  NP and K4 also fail at long horizons (0.95 to 1.48 at 1,000 steps).
  - Observation, not a registered test: L* with 37 linear modes handles F3 well (0.0375 at 1,000 steps). Linear
    dynamics with enough modes covered both tori here.
- **E2 cannot even reconstruct** the fields: its horizon-0 error is 1.19 to 2.22 on F1 and F2. P4's ratio holds, but
  as registered, nothing about tearing is claimed.

## What this does not show

- It shows nothing about language models.
- It does not test the post author's code, which was not seen.
- It shows nothing about convolutional encoders, other noise levels or rarely visited phases.
- It does not establish that a torus constraint is generally useful. In the one place the registration isolated the
  projection (P6), it did not meet its bar.
- The blind fields are not run yet.

## Open (M15)

- **ChatGPT's blind fields A and B** against the same code (approved in comment 7222720820). `score` mode does not
  call `decide()`, so the defect above does not affect them.
- **An arm that removes only the rotation dynamics,** for example the projection with learned free dynamics. Without
  it, no component can be credited.
- **The persistent-homology door** in the registration.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) wrote the code, ran it and wrote this, under a registration attacked
by ChatGPT (OpenAI GPT-6, Codex) notes tor001/chatgpt/002, 004 and 010 → human validation: not performed → direction,
freeze and run approval: Chad Holland, 2026-11-26/27 → human responsibility: Chad Holland. Review level: direction
only. The question is credited to Sushil Pershad's public post, with no endorsement implied.*

## End-to-end rerun at `d087c03` (2026-11-27)

Authority: Chad Holland's direction in live chat on 2026-11-27 to do what is best (paraphrased; recorded in note
tor001/claude/015). Code `tor001.py` at `d087c03`, SHA-256 `e87eeb32…8612`. Raw output:
[`run_d087c03.txt`](../../results/tor_001/run_d087c03.txt) and
[`tor001_results_d087c03.json`](../../results/tor_001/tor001_results_d087c03.json). Verbatim:

```
P1: HELD
P2: HELD
P3: HELD
P4: HELD
P5: HELD
P6: REFUTED
VERDICT row 4: T2 BEATS THE NAMED BASELINES; NO PROJECTION BENEFIT MET P6
```

- **Agreement with the approved run:** 205 of 210 error entries are bitwise identical to the approved run
  (`6b9105d`). The 5 that differ are all F1 / T2 seed 0, the first learned fit; its 1,000-step error is 0.0164 there
  and 0.0289 here. No prediction uses that entry.
- **The other session found the same pattern:** a separate Claude session's second process at `36d5d4a` (`22b09d7`,
  note tor001/claude/014) shows the same 205 of 210. Its first-fit value (0.02891121187522456) is bitwise equal to this rerun's. That points to start-up state affecting only the first fit. This is reproducibility, not
  independence (M10).

## Changes (W9)

- **2026-11-27, after the end-to-end rerun:** added the section above, and edited item 2 of "What could have gone
  wrong" and the Open list. Superseded wording, verbatim: "An end-to-end rerun at the fixed commit has **not** been
  done. That needs Chad's go." and "**An end-to-end rerun at `d087c03`**, to confirm the re-evaluated verdict comes out
  of `run` itself." Edit by Claude (Anthropic, Opus 5.5).
