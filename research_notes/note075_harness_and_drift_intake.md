# Note #075 — Same model, different harness; same model, different week: an intake on what a score is a score of

**Status:** Speculative — research intake. Two external sources, checked against their own pages on 2026-11-04. No
experiment registered or run.
**Theme:** Measurement / Agent evaluation / Drift
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's direction (2026-11-04). Review level: direction
only. The sources came from ChatGPT's (OpenAI) 2026-11-04 research scan; its summaries were checked, not adopted.
**Builds on:** [[note036_verified_models_drift_ledgers]] (a model change must be tracked against prior claims),
[[note073_repair_verification_intake]] (a score is evidence only about what its instrument can see).
**Method:** [METHOD.md](../METHOD.md) at commit `46034aa`.

## What went wrong, first

- **One claim in the scan did not check out.** The scan said livenerf's results were updated 2026-11-03 with three
  completed post-launch windows. The project README, read 2026-11-04, gives its latest results as 2026-10-23 with
  **two** post-launch windows. The project's results file could not be fetched from this session. This note uses
  only what was read: two windows, as of 2026-10-23.
- Nothing here was reproduced. Every number below is the authors' own.

## The claim

An agent's score is a measurement of a model *inside a harness*, at a *time*. Two of the inputs that a single number
hides (the harness around the model, and when it was measured) can be large enough to dominate it. A claim about a
model that does not hold the harness and the date fixed is precisely wrong if a second measurement, changing only
one of them, moves the score by more than the claim's stated margin.

## Epistemic status (read first)

- **Reported by others, not tested here:** a large harness effect on one benchmark sample (IBM Research, below), and
  no detected drift in one model over two windows (livenerf, below).
- **Ours, and not tested:** that the Sovereign Veritas question (what decides whether an action runs) is a harness
  property that model-level scores do not measure. Novelty is not claimed.

## Known mathematics / prior art (verified 2026-11-04)

| Work | Verified | What it reports | Licence | Bearing |
|---|---|---|---|---|
| Marreed, Murthi, Muthusamy et al. (IBM Research), *Same Model, Different Harness: CUGA, Hermes, and Deep Agents*, Hugging Face blog, 2026-11-03 | Yes (blog page) | One open-weight model (GLM-5.3-flash) on 90 AppWorld tasks, one attempt each: tasks passed CUGA 73/90 (81.1%), Hermes 42/90 (46.7%), Deep Agents 27/90 (30.0%). Authors' caveats: one 90-task sample; setups not identical (CUGA used an AppWorld configuration the others did not; Deep Agents got two small fixes); "the runs did not use policies, so they do not measure policy enforcement" | CUGA Apache-2.0 (per the post); the evaluation fork's licence not stated | The harness, not the model, moved the score by about 50 points. Policy enforcement, the part Sovereign Veritas is about, was outside the measurement |
| ninjahawk, *livenerf*, GitHub (README read 2026-11-04) | Yes (README) | A preregistered, long-running benchmark for whether Claude Opus 5.5 gets worse after launch. Rule: a change is called only if the 99% interval excludes zero in two consecutive 10-day windows, the effect is at least 3 points, and a control arm does not move. As of 2026-10-23: two post-launch windows, "no change" in both (+0.007 ± 0.018; −0.015 ± 0.018) | MIT | A working drift ledger with a fixed detection rule and a control arm. "No change met the rule" is not proof that nothing changed |

## The experiment (or: what one would look like) — proposed, not registered

Hold one model and one task set fixed and run Sovereign Veritas's gate inside two different agent harnesses. Registered
question: does the gate's ALLOW / DEFER / REFUSE decision depend on the harness when the proposed action is the same?
The gate is meant to decide from the action and policy alone, so the prediction would be no dependence; any case
where it depends refutes that.

## Reference code

None.

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes, for the proposed experiment: harnesses and tasks to be counted before registering |
| Noise | C-NOISE | Yes: agent runs are stochastic; same-input noise must be measured first |
| Statistics | C-STAT | Yes, if a rate is claimed. None claimed here |
| Evidence | C-EVID | No: no evidence-handling rule is tested here |
| Independence | C-INDEP | Yes: all numbers are the authors'; nothing reproduced |
| External | C-EXT | Yes: two external sources, checked against their pages; one scan claim found wrong and not used |
| Device | C-DEVICE | No |
| Verdict code | C-BUILD | No: no verdict code here |
| Exploration | C-EXPLORE | Yes: the sources came from an exploratory scan |
| Method comparison | C-METHCOMP | Yes, in the sources (harness comparison). Not performed here |
| People's data | C-PRIVATE | No |
| Design | C-DESIGN | Yes: the sources are one-benchmark comparisons and one observational series; they support claims about those settings only |
| Held-out | C-HOLDOUT | Yes, for the proposed experiment: tasks fixed before any run |
| Generated inputs | C-SYNTH | No |

## Falsifiable next predictions (M15)

- **Unrun:** the Sovereign Veritas gate returns the same decision for the same proposed action and policy under two
  different agent harnesses, on a registered task set. Any difference refutes it.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) checked the sources and drafted this note → human validation: not
performed → human editing/curation: direction by Chad Edward Holland, 2026-11-04 → human responsibility: Chad Edward
Holland. Review level: direction only.*
