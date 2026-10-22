# Note #066 — The Ambiguity Engine: an instrument's strength is what it cannot tell apart

**Status:** Speculative (the general claim); **claim 2 REFUTED on AMB-2 (kept)**. AMB-2: 3 of 4 registered
predictions held, B3 refuted (registered at `62334da`, before its code). One registered result elsewhere
(sovereign-veritas AMB-1, held); one exploratory check, unregistered.
**Theme:** Verification / Experimental Design / AI-assisted Search
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's direction (2026-10-05). Proposals from
other AI systems that Chad collected are credited by model name below; their text is not reproduced.
**Builds on:** [[note052_verification_that_cannot_fail]] (an instrument that cannot return null),
[[note059_mutation_score_denominator]] (mutation testing looks at *nearby* programs; this looks at distant
ones), sovereign-veritas PV-1 and AMB-1 (external links below)
**Method:** [METHOD.md](../METHOD.md) at commit `8003fee`.

## What broke (read first)

- **AMB-2 B3 — REFUTED (kept). Claim 2 fails on design quality.** Choosing the surrogate's next sample where
  it most misjudged the design did *not* give better designs than random samples at equal budget: mean final
  low-band T_full 0.4740 (ENGINE) against 0.4774 (RANDOM), ENGINE lower in 5 of 10 seeds (registered: ≥ 7).
  What the engine did do is make the surrogate honest: mean final gap 0.0281 (ENGINE) against 0.2568
  (RANDOM) and 0.3765 (NONE). That gap comparison was not registered as a prediction (B4 compared ENGINE with
  round 0 only), so it is an observation, not a result. The lesson as it stands: **removing ambiguity is
  not the same as improving the thing measured.** The engine bought an accurate instrument, not a better
  chain.
- **Google AI's proposal is wrong as stated (argument, not experiment).** It proposed a passive solid lattice
  in which geometry alone lets heat flow A→B but not B→A. Ordinary (linear) heat conduction is reciprocal;
  geometry alone cannot do that. Thermal diodes need temperature-dependent conductivity or other
  nonlinearity. Its "phonon lenses" also do little in metals at room temperature, where electrons carry
  most of the heat.
- **Gemini's "broadband" shock-scattering claim failed at low frequency** in the exploratory 1-D check below:
  a random chain still passes 0.608 of low-band energy.
- **Copilot's "Self-Differentiating Verifier" is rejected on design grounds:** a verifier that re-derives its
  own rules per claim is self-authorization, and choosing the rule set "that resists the most attacks"
  rewards whatever the attack suite measures.
- **The exploratory numbers quoted in conversation (24.69% → 0.05%) are not AMB-1's numbers.** AMB-1's
  registered learner gave 1,235 → 28 of 10,000.

## The claim

For any instrument V (a test suite, a verifier, a sensor array, a dataset, a simulator) and a meaning map M
(the decision, the claim's strength, the world state, the design's real performance):

1. **Ambiguity** is the rate at which objects V puts in the same class differ under M.
2. A loop that alternately (a) **finds** an ambiguous pair and (b) **buys** the cheapest new observation that
   splits it lowers the ambiguity rate faster than adding the same number of observations at random.

Precisely wrong if: on a registered task, disagreement-chosen observations do no better than random ones
at equal budget (AMB-2, B3 below), or the ambiguity rate is already ~0 before the loop (B2).

## Epistemic status (read first)

Each move is known (prior art below). Whether the combination, with the ambiguity rate published as an
instrument's strength, is new is **UNKNOWN**; no literature search has been done. AMB-1 supports the claim
for one instrument (a contract-vector suite) and one learner, and it had **no random-addition arm**, so it
does not test claim 2. AMB-2 is the first test of claim 2.

## Known mathematics / prior art

Distinguishing experiments for finite automata (Moore 1956); version spaces (Mitchell 1982); learning with
counterexamples, L* (Angluin 1987); counterexample-guided inductive synthesis (Solar-Lezama et al. 2006);
model-discrimination design (Box & Hill 1967) and Bayesian optimal experimental design; noninterference
(Goguen & Meseguer 1982); active learning and multi-fidelity / surrogate-based optimisation; Anderson
localisation (1958) for the chain check. If this is one of these under another name, an issue with the
citation improves the note.

## Where the proposals came from (credit, with verdicts)

| Source (model) | Proposal, paraphrased | Role here |
|---|---|---|
| Claude (Opus 5.5) | Impostor programs that pass every test vector; add their disagreements as vectors | The "find" move; AMB-1 |
| ChatGPT | "Epistemic inflation": a claim grows stronger with no new information | Recast: same verifier class, different meaning = ambiguity; PV-1 is one instance |
| ChatGPT | Theory-conflict engine: choose the experiment where models disagree most | The "buy" move (Box & Hill) |
| ChatGPT | Conserved-quantity discovery, virtual sensors, evolving definitions, scientific adversary | Same two moves in other instruments; prior art exists for each |
| Perplexity | Meta-Compiler Foundry: evolve design grammars, not designs | A generator the engine could police; no small first test |
| Gemini | Non-periodic metamaterial for broadband shock scattering | Exploratory check below: partly supported, fails at low frequency |
| Grok | Causal-graph fabricator | Too broad to test; its example (fracture as load path) has prior art |
| Google AI | Passive one-way thermal lattice | Wrong as stated (reciprocity) |
| Copilot | Verifier that re-derives its own rules | Rejected (self-authorization); its tournament kernel survives only offline, frozen, human-adopted |

## Results so far

**AMB-1 (sovereign-veritas, registered, 4 of 4 held, self-tested, container).** Five stdlib decision-tree
impostors each reproduce all 4,690 Gate contract vectors; the worst says ALLOW where the Gate does not on
1,235 of 10,000 inputs built from the contract's own values; after 800 disagreement-chosen vectors, 28.
Kernel and package verifier agree on all 20,000. Source and numbers: `docs/AMB1_RESULTS.md` in
[holland202/sovereign-veritas PR #55](https://github.com/holland202/sovereign-veritas/pull/55). Not reprinted
by this note's reference code.

**Exploratory chain check (unregistered; printed by `scripts/note066_reference.py --explore`).** A 1-D
mass-spring chain of 200 masses between uniform leads (k = 1, lead mass 2), mean transmission over
ω ∈ [0.05, √2 − 0.05]; low band ω < 0.5. The uniform chain is the control and must pass everything:

```
uniform (control)    mean T 1.000   low band(w<0.5) 1.000   high band 1.000
periodic 1,3,1,3     mean T 0.539   low band(w<0.5) 0.991   high band 0.303
random U[1,3]        mean T 0.231   low band(w<0.5) 0.608   high band 0.034
graded 1->3          mean T 0.768   low band(w<0.5) 0.957   high band 0.670
```

Lossless: scattering only, no dissipation.

## The experiment: AMB-2 (registered here, before `scripts/note066_reference.py` implements it)

**Question.** When a design is optimised against a cheap surrogate, does choosing the surrogate's next sample
where it most misjudges the design (the engine) close the surrogate-vs-truth gap better than random samples?

**Setup (constants).** Chain of N = 100 masses, each in [1, 3], k = 1, leads of mass 2. Goal: minimise
low-band transmission. *Truth* T_full = mean T over 200 evenly spaced ω in [0.05, 0.5]. *Surrogate* T_S = mean
T over a sample set S, initially {0.1, 0.2, 0.3, 0.4}. *Optimiser:* hill climbing from all masses = 2, 500
generations, each mutating 5 random masses by N(0, 0.3), clipped to [1, 3], accepted if T_S does not increase;
`numpy.random.default_rng(seed)`. Seeds 0–9. 6 rounds. Each round re-optimises from the start against the
current S, then each arm adds one frequency to S:
- **ENGINE:** the ω on the 200-point grid where the current design's T is largest (one full evaluation, the
  "bought" observation);
- **RANDOM:** a uniform random ω in [0.05, 0.5] (its own seeded generator);
- **NONE:** nothing.
Score per arm and seed: T_full and gap = T_full − T_S of the design optimised in the last round.

**Predictions.**
- **B1 (control).** The uniform chain gives T_full = 1.000.
- **B2 (ambiguity exists).** Round 0, mean over seeds: T_S of the optimised design ≤ 0.5 × its T_full.
- **B3 (claim 2).** After 6 rounds: mean T_full(ENGINE) < mean T_full(RANDOM), and ENGINE is lower in at
  least 7 of 10 seeds.
- **B4.** Mean ENGINE gap after 6 rounds ≤ ⅓ of the mean round-0 gap.
- **B5 (`--sabotage`).** The surrogate is the full 200-point grid. The round-0 gap is then 0, B2 is REFUTED,
  and the script exits 1.
- **B6 (door, unrun).** An independent second instrument (time-domain integration) instead of a sampled
  surrogate; 2-D lattices; damping.

If B3 fails, claim 2 is refuted for this task and the failure stays here. If B2 fails, the task has no
ambiguity to remove and AMB-2 says nothing about claim 2.

## AMB-2 results (run after `62334da`; raw output `results/note066/run.txt`)

Two implementation choices the registration left open, decided before the run and disclosed here: each
optimisation starts a fresh `default_rng(seed)`, so rounds differ only through S; and "6 rounds" was run as
six (add one frequency, re-optimise) steps after the round-0 optimisation, so every bought frequency is used
by the final design.

```
== AMB-2 (registered run)
  seed 0: round0 T_full 0.4913 T_S 0.1245 | final T_full ENGINE 0.5409  RANDOM 0.4685  NONE 0.4913 | ENGINE gap 0.0609
  seed 1: round0 T_full 0.5161 T_S 0.1592 | final T_full ENGINE 0.4922  RANDOM 0.4353  NONE 0.5161 | ENGINE gap -0.0383
  seed 2: round0 T_full 0.5000 T_S 0.1475 | final T_full ENGINE 0.4103  RANDOM 0.5071  NONE 0.5000 | ENGINE gap 0.0234
  seed 3: round0 T_full 0.5107 T_S 0.1683 | final T_full ENGINE 0.4034  RANDOM 0.4614  NONE 0.5107 | ENGINE gap 0.0438
  seed 4: round0 T_full 0.5223 T_S 0.1313 | final T_full ENGINE 0.4924  RANDOM 0.4767  NONE 0.5223 | ENGINE gap 0.0520
  seed 5: round0 T_full 0.5151 T_S 0.1492 | final T_full ENGINE 0.4709  RANDOM 0.4442  NONE 0.5151 | ENGINE gap 0.0030
  seed 6: round0 T_full 0.5477 T_S 0.1786 | final T_full ENGINE 0.4482  RANDOM 0.5302  NONE 0.5477 | ENGINE gap -0.0519
  seed 7: round0 T_full 0.5352 T_S 0.1127 | final T_full ENGINE 0.4479  RANDOM 0.4579  NONE 0.5352 | ENGINE gap 0.0145
  seed 8: round0 T_full 0.5236 T_S 0.1490 | final T_full ENGINE 0.5544  RANDOM 0.5032  NONE 0.5236 | ENGINE gap 0.1117
  seed 9: round0 T_full 0.5728 T_S 0.1494 | final T_full ENGINE 0.4790  RANDOM 0.4893  NONE 0.5728 | ENGINE gap 0.0621
  mean round0 T_full 0.5235  T_S 0.1470  gap 0.3765
  mean final T_full  ENGINE 0.4740  RANDOM 0.4774  NONE 0.5235;  ENGINE lower than RANDOM in 5 of 10 seeds
  mean final gap     ENGINE 0.0281  RANDOM 0.2568  NONE 0.3765;  B1 uniform T_full 1.000
  B1  HELD
  B2  HELD
  B3  REFUTED
  B4  HELD
VERDICT 3 of 4 as registered (B5 is --sabotage; B6 is the door)
DIGEST 2db69064d8a970c9ceff2167826626d683674fbb238d68721ab19cac0d382592
```

| | prediction | outcome |
|---|---|---|
| B1 | uniform chain T_full = 1.000 | HELD |
| B2 | round-0 mean T_S ≤ 0.5 × T_full | HELD (0.1470 vs 0.5235): optimising against 4 samples fooled the surrogate |
| B3 | ENGINE beats RANDOM on T_full, ≥ 7 of 10 seeds | **REFUTED** (0.4740 vs 0.4774; 5 of 10) |
| B4 | ENGINE final gap ≤ ⅓ round-0 gap | HELD (0.0281 vs 0.3765 / 3 = 0.1255) |
| B5 | `--sabotage` exits 1 | HELD (`results/note066/sabotage.txt`: B2 REFUTED, exit 1) |

Self-tested by Claude (Opus 5.5); container only; NOT VALIDATED on the S25.

## Reference code

`scripts/note066_reference.py` (NumPy). At the registration commit (`62334da`) it implemented only
`--explore`; the AMB-2 arms were added afterwards (`8d4d3f7`) and the outcome pinned (`f0b2abe`). The default
run prints every number in this note and exits 0 only on the recorded outcome.

## Triggered controls (M16)

| Trigger | Answer (yes / no + reason) |
|---|---|
| Feasibility | yes: AMB-2 timing counted before registering (300 surrogate evaluations 0.20 s; 20 full 0.06 s; uniform control 1.0) |
| Noise | no: all arms seeded and deterministic |
| Statistics | yes: B3 compares means over 10 seeds and a 7-of-10 count; no wider claim |
| Evidence | yes: the claim is about what an instrument can distinguish |
| Independence | yes: everything is self-tested by Claude; AMB-1 and AMB-2 are not independent replications |
| External | yes: proposals from other AI systems, paraphrased and credited, not quoted; AMB-1 cited from sovereign-veritas |
| Device | no: no device claim; nothing run on the S25 |
| Verdict code | yes: AMB-2 prints HELD/REFUTED and has a sabotage arm (B5) |
| Exploration | yes: the chain check and an AMB-1 pilot ran before registration and are labelled exploratory |
| Method comparison | yes: ENGINE vs RANDOM vs NONE at equal budget |

## Falsifiable next predictions (M15)

- **A registered ENGINE-vs-RANDOM gap comparison** on AMB-2: the observation above (0.0281 vs 0.2568) predicts
  ENGINE's gap is lower in at least 8 of 10 fresh seeds (seeds 10-19).
- **Engine plus exploitation:** spend half the budget on disagreement samples and half on the optimiser's
  own choice; does T_full then beat RANDOM? (Claim 2 restated so it could survive; unregistered.)
- AMB-1 with a RANDOM arm: 800 random recombined vectors leave the worst impostor above 28 of 10,000.
- The Go port of the Gate agrees with the kernel on AMB-1's 20,000 recombined inputs.
