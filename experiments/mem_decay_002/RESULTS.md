# MEM-DECAY-002: results (run 2026-11-14)

**Status:** run as registered at `c5b714c` ([REGISTRATION.md](REGISTRATION.md)). Code and seal committed at `5aaa9f2`
before the test split was scored. SELF-TESTED. **7 of 7 predictions held; 5 of 5 controls held.**

- **Seal:** `5636518b7638d0e0c246978aaeeb1505d92430e75ded16314cf9e401e476c22b`
- **Digest:** `20985e380a3e97305f217d10f184f83df5455b31d80941774f5cda322f643fd2`. A second run was byte-identical.
- **Raw output:** [`results/mem_decay_002/test.txt`](../../results/mem_decay_002/test.txt), and the rerun, dev run,
  seal and test log beside it.
- **Tests:** 247 passed, including the five registered mutants, each killed.
- **Environment:** Python 3.13.18, NumPy 2.5.3, x86_64 container.

## What is weaker than it looks (M8)

- **Several predictions held by construction or by arithmetic.** That is a weakness of the registration, not a
  finding.
  - Q1 was registered as an instrument check.
  - Q3, Q4 and Q7 follow almost directly from how pins and labels were defined. A record pinned at its true label
    is kept, and a missed critical record behaves like an unpinned one.
  - The predictions that could have failed on mechanism were Q2, Q5 and Q6.
- **Synthetic store, synthetic use counts, synthetic label noise.** Use counts are independent of relevance: every
  non-critical record gets Poisson(2). In real use, frequently used facts are probably also the ones asked for, and
  that would favour A6 more than this generator does. That is not measured here.
- **The realised label recall at ε = 0.3 was 0.645, not the expected 0.70.** The C-SYNTH line printed it at sealing:
  129 of 200 critical records labelled ≥ 0.5. Q4's range still held.
- **No arm is good on every category.** This run does not produce a recommended policy, only a map of trade-offs.

## Results (test split, guard G1, top-5; rates out of 200)

| Arm | ε | current | stale | contradictory | critical | revoked leak | adversarial |
|---|---|---|---|---|---|---|---|
| A0 no decay | any | 0.985 | 0.485 | 0.975 | 1.000 | 0.000 | 1.000 |
| A3 age decay | any | 0.320 | 0.975 | 0.075 | 0.000 | 0.000 | 0.000 |
| A4L pinned TTL, labels | 0 | 0.510 | 0.985 | 0.240 | 1.000 | 0.000 | 0.160 |
| | 0.1 | 0.520 | 0.970 | 0.245 | 0.830 | 0.000 | 0.170 |
| | 0.3 | 0.530 | 0.970 | 0.255 | 0.645 | 0.000 | 0.185 |
| A6 dual strength | any | 0.805 | 0.655 | 0.515 | 0.000 | 0.000 | 0.255 |
| A5 dual strength + graded floor | 0 | 0.805 | 0.650 | 0.510 | 0.455 | 0.000 | 0.255 |
| | 0.1 | 0.805 | 0.645 | 0.515 | 0.365 | 0.000 | 0.260 |
| | 0.3 | 0.805 | 0.645 | 0.535 | 0.285 | 0.000 | 0.265 |
| A7 age decay + pins | 0 | 0.315 | 0.970 | 0.075 | 1.000 | 0.000 | 0.000 |
| | 0.1 | 0.320 | 0.955 | 0.075 | 0.830 | 0.000 | 0.010 |
| | 0.3 | 0.340 | 0.955 | 0.085 | 0.645 | 0.000 | 0.030 |

Wilson intervals are in the raw output.

## Predictions

| ID | Result | Observed |
|---|---|---|
| Q1 | HELD | A6 critical 0.000 at every ε |
| Q2 | HELD | A5 critical at ε = 0: 0.455 (registered range [0.20, 0.70]; the registration's arithmetic, w' above about 0.92 of U(0.8, 1.0), implies about 0.4) |
| Q3 | HELD | A7 at ε = 0: critical 1.000, stale 0.970 |
| Q4 | HELD | At ε = 0.3: A4L 0.645, A7 0.645 |
| Q5 | HELD | A6 current 0.805 against A3 0.320 |
| Q6 | HELD | A6 stale 0.655 against A3 0.975 |
| Q7 | HELD | At ε = 0.3 the highest non-A0 critical recall was 0.645 |

## Controls

| ID | Result |
|---|---|
| NC1 A5 with zero floors gives A6's top-5 on every query | HELD |
| NC2 A7 with no pins gives A3's top-5 | HELD |
| NC3 A6 with S = 1 and access age = age gives A3's top-5 | HELD |
| NC4 A4L at ε = 0 gives the true-flag A4's top-5 | HELD |
| NC5 labels shuffled: A7 critical ≤ 0.10 | HELD (0.025) |

## What this shows (C-DESIGN: simulation; this generator, these synthetic inputs, top-5)

1. **Decay with pins does both jobs that pure decay could not.** This answers the P6 door: critical 1.000 and stale
   0.970 together. It keeps A3's costs: old ordinary facts 0.315, contradictions 0.075, old targets with newer
   look-alikes 0.000.
2. **Protection equals label recall, exactly.** At ε = 0.1 and 0.3, A4L's and A7's critical recall (166/200 and
   129/200) is exactly the number of critical records labelled ≥ 0.5. The mechanism adds nothing, and takes nothing
   away, beyond the label. **How importance gets labelled is now the limiting question, not how decay works.**
3. **A graded importance floor below 1 is not protection.** With perfect labels, A5 kept 0.455 of critical records,
   against 1.000 for a pin. Six fresher look-alikes outrank a record whose floor is 0.8–0.9, so a floor has to be
   about 1 to protect. That makes it a pin.
4. **The human-memory mechanism is a trade-off, not a fix.** Decaying by time since last use, slowed by use (A6),
   kept far more old ordinary facts than age decay (0.805 against 0.320). Contradictions and adversarial recall
   improved too. But it suppressed stale values much less (0.655 against 0.975), because a stale value that was
   used recently decays slowly too. Never-used critical records were lost entirely.
5. **False raises were cheap here.** At ε = 0.3, 377 of 12,000 ordinary records were pinned by mistake, and stale
   suppression moved from 0.985 to 0.970 for A4L.
6. **The status filter again stopped every revoked record, in every arm** (leak 0.000).

## Doors (M15), unrun

- **A6 with pins.** Use-based decay for ordinary records plus pins for labelled ones. By the parts measured here it
  should combine A6's current recall with label-recall protection, with stale around 0.65. That is a prediction to
  register, not a result.
- **Supersession links with A6.** Supersession links handle the linked half of stale values in every arm. Would
  they make up A6's stale loss?
- **A learned importance labeller.** Labels from content, not truth plus noise. Since protection equals label
  recall, this is the experiment that matters most next.
- **Use counts correlated with relevance**, and real use logs.
- **Competitor count**, still open from P6.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed, wrote, ran and wrote up this experiment → human validation:
not performed → human editing/curation: direction by Chad Holland, 2026-11-13 and 2026-11-14 → human
responsibility: Chad Holland. Review level: direction only.*
