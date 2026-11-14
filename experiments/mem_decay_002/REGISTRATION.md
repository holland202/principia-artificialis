# MEM-DECAY-002: decay modelled on human memory, with importance labels that can be wrong

**State:** REGISTERED, NOT RUN. Committed before any code for this experiment exists and before either new split is
generated.
**Authors:** Direction: Chad Holland (2026-11-13: design decay like human memory; 2026-11-14: proceed). Design:
Claude (Anthropic, Opus 5.5). Human review level: direction only. Everything here is **self-tested** (M10).
**Builds on:** [MEM-DECAY-001](../mem_decay_001/RESULTS.md) and its [P6](../mem_decay_001/RESULTS_P6.md), which found:
no single half-life lets pure rank decay keep critical records *and* suppress stale ones; pins protect critical records;
the status filter stops revoked records. Its open door was "decay with pins".
**Method:** [METHOD.md](../../METHOD.md).

## Question

Human memory is often modelled with two strengths (Bjork and Bjork's New Theory of Disuse, 1992):

- **storage strength** grows with use and does not decay;
- **retrieval strength** is how accessible a memory is now. It falls with time since last use, and falls more slowly
  when storage strength is high.

Important memories also resist forgetting. Two questions follow.

1. Does a store that ranks by retrieval strength, with use slowing the decay, recover what MEM-DECAY-001's age decay
   lost?
2. Does protection by graded importance survive **importance labels that are wrong some of the time**? Every real
   system has to guess importance. MEM-DECAY-001's pins used the true critical flag.

Prior art, not a new idea: Bjork and Bjork (1992); ACT-R base-level activation (Anderson and Lebiere, 1998);
MemoryBank's Ebbinghaus-style decay for LLM memory (Zhong et al., 2023). This is a test of whether that family of
designs does the two jobs in this generator. It does not claim novelty.

## Store and splits

The MEM-DECAY-001 generator (`memdecay.py`) is reused unchanged. It provides the categories, the vectors, `age`,
`access` (days since last access), `critical`, `status`, and top-5 retrieval with guard G1 (current status only). Two
new fields come from a separate generator seeded `seed + 7`, so the base store is byte-identical to what
`memdecay.build` returns for the same seed:

- **use count** `n_i`. Critical records get 0, as MEM-DECAY-001 defines them: never accessed since written. Every
  other record gets Poisson(2). If `n_i = 0`, the effective access age is the record's age.
- **importance label** `w'_i`. True importance `w_i` is U(0.8, 1.0) for critical records and U(0, 0.3) for the rest.
  At noise level ε, each critical record is **missed** with probability ε, and its label is redrawn from U(0, 0.3).
  Each other record is **falsely raised** with probability ε/10, and its label is redrawn from U(0.8, 1.0). One
  uniform draw per record is used for every ε, so a record mislabelled at ε = 0.1 is also mislabelled at ε = 0.3.
  ε ∈ {0, 0.1, 0.3}.

| Split | Seed | Queries per category | Filler | Use |
|---|---|---|---|---|
| dev | 20261117 | 50 | 1,000 | code checks only, no decision about design or thresholds |
| test | 20261116 | 200 | 8,000 | the registered run, sealed before scoring |

T is the median **filler** age, as in P6. Half-life h = T for every decaying arm. Pins use the threshold
`w' ≥ 0.5`. These are rules, not values tuned on data.

## Arms (guard G1, top-5, nothing deleted unless stated)

| Arm | Score or rule | What it isolates |
|---|---|---|
| A0 | similarity | no decay (reference) |
| A3 | `sim · 2^(−age / h)` | MEM-DECAY-001's age decay (reference) |
| A4L | TTL: delete age > T, except records with `w' ≥ 0.5` | pinned TTL with **labels**, not the true flag |
| A6 | `sim · R`, with `R = 2^(−a / (h · S))`, `a` the effective access age and `S = 1 + log2(1 + n)` | dual strength, no importance |
| A5 | `sim · max(w', R)` | dual strength plus a **graded importance floor** |
| A7 | `sim · 2^(−age / h)`, except records with `w' ≥ 0.5` score `sim` | age decay **with pins** (the P6 door) |

## Predictions

Rates are on the test split. "Critical" is the critical record in the top-5. "Stale" is the new value above the stale
one. "Current" is an old ordinary fact in the top-5. Beliefs are for calibration only.

| ID | Prediction | Belief |
|---|---|---|
| Q1 | A6 critical ≤ 0.05 at every ε. Critical records are never used, so use-based decay cannot save them. This holds by construction: an instrument check, not a finding | 0.97 |
| Q2 | A5 critical at ε = 0 lies in [0.20, 0.70]. A graded floor below 1 often loses to six fresh, related competitors. Arithmetic: the critical record's similarity is about 0.97 against about 0.91 for each competitor, so it needs `w'` above roughly 0.92 | 0.6 |
| Q3 | A7 at ε = 0: critical ≥ 0.95 **and** stale ≥ 0.95. Decay with pins does both jobs pure decay could not | 0.85 |
| Q4 | At ε = 0.3, A4L critical and A7 critical each lie in [0.60, 0.80]. Label-based protection is capped by label recall, here an expected 0.70 | 0.85 |
| Q5 | A6 current > A3 current + 0.10 at ε = 0. Decay by time since last use keeps more old ordinary facts than decay by age | 0.7 |
| Q6 | A6 stale < A3 stale − 0.05 at ε = 0. Recently used stale values also decay more slowly | 0.6 |
| Q7 | At ε = 0.3, no arm other than A0 (which forgets nothing) has critical recall above 0.85 | 0.9 |

**Interpretation, fixed now.**

- Q3 holding answers the P6 door: pins plus decay do both jobs. It costs what A3 costs on current recall. Q3 failing
  means the pinned set itself crowds out or misses records.
- Q4 and Q7 holding together mean protection is capped by label quality, whatever mechanism uses the labels. The
  research question then moves to how importance gets labelled, not how decay works.
- Q5 and Q6 measure the human-memory mechanism on its own, as a trade-off. Neither result says the mechanism is good
  or bad overall.

## Controls (M3)

| ID | Control | Expected |
|---|---|---|
| NC1 | A5 with every floor set to 0 | top-5 identical to A6 on every test query |
| NC2 | A7 with no pins | top-5 identical to A3 on every test query |
| NC3 | A6 with `S ≡ 1` and effective access age replaced by age | top-5 identical to A3 on every test query |
| NC4 | A4L at ε = 0 (no false raises at ε = 0) against A4, which pins by the true flag | top-5 identical on every test query |
| NC5 | Labels shuffled across records at ε = 0 | A7 critical ≤ 0.10. Pins only help when they land on the right records |

Mutants the tests must kill (C-BUILD): the floor ignored in A5; storage strength ignored in A6; pins ignored in A7;
the label noise not applied; the label noise applied to the wrong class. Property tests use seeded random stores with
no answer key: for example, raising a record's floor never lowers its rank, and a pin never lowers a record's rank.

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes; NumPy only, minutes on a laptop-class CPU |
| Noise | C-NOISE | Deterministic; a second run must give the same digest |
| Statistics | C-STAT | One fixed test split, n = 200 per category, Wilson intervals reported; no stopping rule, no peeking |
| Evidence | C-EVID | Self-tested synthetic evidence (M10). Says nothing about real embeddings or real use patterns |
| Independence | C-INDEP | Generator, arms, tests and predictions are all Claude-written |
| Holdout | C-HOLDOUT | Design decided from MEM-DECAY-001's results, which are already public; judged on a new seed. Dev is used for code checks only |
| Generated inputs | C-SYNTH | The run prints label and use-count summaries per class before scoring; they are checked against the rules above |
| Exploration | C-EXPLORE | Q2's range comes from arithmetic on the generator's spreads, done before this file was committed. Nothing was run |
| Design | C-DESIGN | Simulation with fixed synthetic inputs; it can show what a mechanism does in this generator, not in deployed memory |
| Others | C-DEVICE, C-EXT, C-PRIVATE, C-METHCOMP | Not triggered: container run, no outside material, no people's data, no methodology comparison |

## Door (M15)

Left unrun on purpose: a learned importance labeller, where labels come from the content rather than from noise
added to the truth. Real use logs. And the competitor count, also left open by P6.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed and wrote this registration → human validation: not
performed → human editing/curation: direction by Chad Holland, 2026-11-13 and 2026-11-14 → human responsibility: Chad
Holland. Review level: direction only.*
