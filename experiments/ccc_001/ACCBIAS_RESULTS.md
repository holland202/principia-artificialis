# CCC-001 accept-shift decomposition: results (post-hoc reanalysis, development diagnostic)

**Registration:** [ACCBIAS_PREREG.md](ACCBIAS_PREREG.md) at `f416f86`, committed alone before the harness existed.
**Harness:** [accbias.py](accbias.py), run at `1211a39`; the outcome is pinned in the next commit. Relay turn 027,
2026-11-22. Development-only (C-EXPLORE). No model was loaded and no forward pass was made. Pure Python 3.13 on a
Linux container. S25 NOT VALIDATED. **VERDICT 4 of 4 as registered.** These were Claude's own predictions, so the
result is self-tested. No earlier verdict changes (M12), and Qwen2.5-1.5B-Instruct stays not qualified.

## What could have gone wrong, first

- **Self-tested.** Claude wrote the registration, the harness and this file, and ran it. ChatGPT (OpenAI) proposed
  the rival and the reporting rules (`ccc-relay/chatgpt/024`, `026`). That is design input, not a review of this
  run.
- **Not blind.** The inputs and some aggregates were already public, as the registration lists. P3 was partly
  informed by the published accept-item gains, and the Δ_ne table is partly derivable from QORDER's published table.
- **Unqualified model, 24 development items, one instruction wording.** This describes one small model's answer
  format. It says nothing about conversations or about CCC-001's hypothesis.
- **The shuffle null on the minimum turned out weak (reading after the run).** With one strongly negative cell, the
  observed minimum (`-0.214725`) sits inside the shuffled distribution. The informative null line is "all 9 > 0":
  0 of 2,000 shuffles, against 7 of 9 positive observed. The positive count under shuffles was not registered and is
  not reported.
- **Sabotage.** Under `--sabotage` every cell is 0, so P1 holds by construction and P2 and P3 refute. The control
  shows the instrument can change outcome; it does not test P1.
- **No CI step.** No CCC-001 harness has a CI step on this branch, and none was added here.

## Raw output (pasted from [accbias_run.txt](../../results/ccc_001/accbias_run.txt))

```
P0a arm-D not-enough cell means vs qorder_run.txt: max |diff| 4.57e-07 (<= 1e-6)
P0b arm-E gains per not-enough cell: max |diff| 2.80e-05 (<= 5e-5), E>D counts equal: True
P0c LONGCTX per-pi gains [-0.0294, 0.2321, -0.0457] vs longctx_ref_run.txt [-0.0294, 0.2321, -0.0457]: equal True
P0d bookkeeping |d_acc+d_rej+d_ne| max: QORDER 2.85e-16 (<= 1e-12), LONGCTX 2.00e-06 (<= 5e-6)
P0e identity E:=D: 27 QORDER and 9 LONGCTX cell values exactly 0: True
P0 HELD reproduction and bookkeeping gate (a-e all required)
P1 HELD QORDER accept cells with d_acc <= 0: 2 of 9 (>= 1); smallest -0.214725 at letter A slot 2
P2 HELD d_acc letter range 0.310391 > slot range 0.167150
P3 HELD LONGCTX REF d_acc per pi [0.105711, 0.093951, 0.313284] (> 0 each)
REPORT d_accept by its own letter x slot (cell mean; items up/down of 24; pairs up/down/zero of 96):
REPORT   letter A: s=1 +0.091547 it 18/6 pr 64/32/0  s=2 -0.214725 it 1/23 pr 11/85/0  s=3 -0.110671 it 4/20 pr 25/71/0
REPORT   letter B: s=1 +0.200698 it 19/5 pr 69/27/0  s=2 +0.091864 it 16/8 pr 55/41/0  s=3 +0.016194 it 14/10 pr 55/41/0
REPORT   letter C: s=1 +0.253956 it 23/1 pr 91/5/0  s=2 +0.167612 it 17/7 pr 58/38/0  s=3 +0.275755 it 19/5 pr 62/34/0
REPORT d_reject by its own letter x slot (cell mean; items up/down of 24; pairs up/down/zero of 96):
REPORT   letter A: s=1 -0.400006 it 0/24 pr 5/91/0  s=2 -0.330353 it 3/21 pr 11/85/0  s=3 -0.030068 it 8/16 pr 29/67/0
REPORT   letter B: s=1 +0.221976 it 21/3 pr 74/22/0  s=2 -0.217447 it 3/21 pr 26/70/0  s=3 -0.098375 it 2/22 pr 22/74/0
REPORT   letter C: s=1 +0.342248 it 23/1 pr 75/21/0  s=2 -0.262256 it 0/24 pr 8/88/0  s=3 +0.022251 it 11/13 pr 41/55/0
REPORT d_notenough by its own letter x slot (cell mean; items up/down of 24; pairs up/down/zero of 96):
REPORT   letter A: s=1 -0.222554 it 10/14 pr 29/67/0  s=2 -0.207441 it 5/19 pr 23/73/0  s=3 +0.051327 it 11/13 pr 46/50/0
REPORT   letter B: s=1 +0.197582 it 21/3 pr 80/16/0  s=2 -0.079713 it 5/19 pr 27/69/0  s=3 +0.066695 it 12/12 pr 45/51/0
REPORT   letter C: s=1 +0.133138 it 20/4 pr 81/15/0  s=2 -0.012808 it 6/18 pr 33/63/0  s=3 +0.053574 it 16/8 pr 60/36/0
REPORT d_acc letter means A -0.077950 B +0.102919 C +0.232441 | slot means 1 +0.182067 2 +0.014917 3 +0.060426
REPORT inside each accept cell, where the change comes from (d_acc, d_rej, d_ne):
REPORT   letter A: s=1 +0.091547 -0.117142 +0.025595  s=2 -0.214725 +0.086738 +0.127987  s=3 -0.110671 +0.103542 +0.007130
REPORT   letter B: s=1 +0.200698 -0.245789 +0.045091  s=2 +0.091864 +0.002909 -0.094773  s=3 +0.016194 +0.014773 -0.030966
REPORT   letter C: s=1 +0.253956 -0.286626 +0.032670  s=2 +0.167612 -0.082550 -0.085063  s=3 +0.275755 -0.227884 -0.047870
REPORT min |d_acc cell| 0.016194
REPORT LONGCTX pi0 (accept=A): d_acc +0.105711 d_rej -0.123310 d_ne +0.017599 | items d_acc up/down 21/3 of 24
REPORT LONGCTX pi1 (accept=B): d_acc +0.093951 d_rej +0.297205 d_ne -0.391155 | items d_acc up/down 21/3 of 24
REPORT LONGCTX pi2 (accept=C): d_acc +0.313284 d_rej -0.552207 d_ne +0.238923 | items d_acc up/down 17/7 of 24
REPORT shuffle null (2000 shuffles, seed 20261122, same draw for E and D): observed min -0.214725; shuffled min p5 -0.300472 p50 -0.252517 p95 -0.205646; fraction min >= observed 182/2000; fraction all 9 > 0 0/2000
VERDICT 4 of 4 as registered
DIGEST fe5ebe886d716fdbd27fc34bd23361839e5adad71eccf73c9aca4db09c75ff9c
```

Sabotage ([accbias_run_sabotage.txt](../../results/ccc_001/accbias_run_sabotage.txt)): `P1 HELD … 9 of 9`,
`P2 REFUTED`, `P3 REFUTED`, `VERDICT 2 of 4 as registered`, `DIGEST c11244d6…826d`, exit 1. After pinning, the
real run exits 0 and a re-run is byte-identical.

## Predictions

| ID | Registered (Claude's prediction) | Outcome |
|---|---|---|
| P0 | Reproduce published QORDER and LONGCTX numbers; bookkeeping; identity zeros | HELD (a–e) |
| P1 | At least one QORDER accept cell has Δ_acc ≤ 0 (the semantic rival predicted all 9 > 0) | HELD: 2 of 9, (A,2) `-0.214725` and (A,3) `-0.110671` |
| P2 | Δ_acc letter range > slot range | HELD: `0.310391` > `0.167150` |
| P3 | LONGCTX REF Δ_acc > 0 in every π | HELD: `0.105711`, `0.093951`, `0.313284` |

## What this shows and does not show

**Observed (this model, these items, short context for QORDER):**
- The instruction raises p(accept letter) in 7 of 9 cells.
- It lowers it in both cells where accept is A and not in first place.
- Ordered by accept's letter, the mean shift rises from A to C: `-0.077950`, `+0.102919`, `+0.232441`.
- At LONGCTX REF it rises under every π, and for 17–21 of 24 items per π.

**Reading (interpretation, after the run):**
- Neither pure account fits. A uniform semantic accept shift is refuted at the sign level (P1).
- A pure letter account does not fit either: (A,1) is positive (`+0.091547`, 18 of 24 items up).
- The data are consistent with a general shift toward accept, offset by a shift away from the letter A that is
  strongest when A is not first.
- That reading was not registered. It needs its own test before anyone relies on it.

**Where accept's gain comes from:**
- Of the 7 positive cells, 4 take the gain mainly from reject: (A,1), (B,1), (C,1) and (C,3). For example, (C,1)
  has reject `-0.286626` and not-enough `+0.032670`. Two, (B,2) and (B,3), take it mainly from not-enough. In
  (C,2) the two shares are about equal (`-0.082550`, `-0.085063`).
- In the (A,2) cell, accept's loss goes to both other answers.

**Not shown:** anything about conversations, about other models, or about CCC-001. LONGCTX confounds π, letter and
slot. The QORDER and LONGCTX tables are kept separate, as registered.

## Open (M15)

NOT RUN:
- The same decomposition on the GPU7B outputs (amendment `5b4807c`), once their returned JSON reproduces the
  recorded digests.
- A registered test of the post-hoc reading: a fixed accept shift plus an A-avoidance term. One way to test it is
  the positive-cell count under shuffles, registered before it is read.

## Provenance (M13)

Question origin for CCC-001: Federico Talens-Alesson, credited as the question's originator only; no endorsement
or validation by him is implied. Rival and reporting rules: ChatGPT (OpenAI). Registration, harness, run and this
file: Claude (Anthropic, Opus 5.5), in a fresh scheduled session under Chad Holland's standing direction of
2026-11-21. Human validation: not performed. Human editing/curation: direction only. Human responsibility: Chad
Holland.
