# PA-NS-001 preregistration working draft v0.2

**DRAFT — NOT FROZEN, NOT REGISTERED FOR EXECUTION, AI STUDY NOT RUN.**
Owner review and independent oracle review are mandatory before Gate C. This file
does not retrospectively register the Stage 2 engineering checks. Those checks have
already been observed and are permanently excluded from confirmatory inference.
Canonical method followed: METHOD.md at `8a3194f56f400a306778f7a837b51216c3b71220`.
Engineering plan committed before calibration: `4bdaa6535984716fa4816ad5d50c2c55a60e169f`.
Authorship: ChatGPT (OpenAI GPT-6); Chad Holland: direction/authorization.
Human review of this draft: direction only; no independent sign-off.

## 1. Question and scope decision still required
Original question: can external deterministic verification reduce false acceptance
of invalid AI-generated fluid-flow outputs? There are two different experiments:

**A, proposed first:** controlled profile review. The construction oracle supplies
valid/invalid profiles and an AI decides whether to accept them. This measures
AI-assisted acceptance of supplied profiles, **not AI generation or reasoning quality**.
Known class counts permit a justified fixed sample size.

**B, deferred:** AI generates its own profiles. Validity is scored afterwards by an
independently reviewed oracle. The number of invalid outputs is random; a fixed
total of 200 does not guarantee 100 invalid units. A separate precision/power plan
is necessary. Do not silently substitute A for B. Owner selects the research target
before any freeze; the detailed proposal below is A only.

This is an operational error-filtering question on two analytic channel solutions.
It is not a test of general fluid simulation, biological reasoning, SWAY superiority,
physical predictive validity, or the Navier–Stokes existence/smoothness problem.

## 2. Proposed sampling unit and task construction
One independently seeded physical task, one candidate profile, one frozen AI review
response = one unit. Multiple grid points, metrics or fault variants are not extra
samples. No case contributes repeatedly to a primary denominator.

Proposal: 400 invalid units and 400 valid units, with family independently sampled
with probability 1/2 **within each validity class**, rather than fixed family quotas.
This defines an IID mixture estimand for pooled binomial intervals. Expected family
counts are 200 per class; realized counts are reported. If fixed quotas or clusters
are chosen instead, use a separately approved stratified/cluster-aware analysis.

Main tasks, model configuration and generation seed are **not created/reserved yet**.
Freeze the exact generator, physical-domain distribution, grid choices, valid rounding
mixture, fault mixture, seed and hashes before execution. Suggested starting domain:
the six calibrated physical scenarios, grids 21/65/257, signed drive, binary64 or
protocol-fixed normalized decimal representation. Independent review must determine
whether a larger domain or unseen fault mechanisms are necessary to avoid an
overly easy benchmark. Do not tune thresholds or task difficulty after main outcomes.

The 240 calibration cases, 114 engineering fixtures, all diagnostic/adversarial cases,
and any future pilot outputs are development data. None is held out; none may enter
the confirmatory dataset. No protected PA seed ranges are used or authorized.

Invalid labels require an independent analytic argument and a discrepancy exceeding
the approved tolerance/precision contract. Nonidentifiable parameter changes and
zero-drive reversal belong to valid controls, not invented faults. Include wall,
curvature/sign, interior and coordinate faults, plus independently reviewed novel
constructions. Representation errors and physics errors are reported separately.

## 3. Paired arms, controls and costs
All arms receive the **same cached AI response for the same case**:

| Arm | Acceptance rule | Purpose |
|---|---|---|
| B, baseline | strict parsing of the model's accept Boolean | AI review without the external numerical filter |
| V, verified | B accepts AND the full deterministic checker accepts | proposed operational filter |
| R, simplest rival | B accepts AND analytic profile-only check accepts | determine whether momentum checking adds useful value |

R must use the identical input/configuration validation, scale and precision limits;
only the momentum veto is omitted. Implement/review this adapter before freezing;
it is not implemented as an official study arm in Stage 2. An accept-all classifier
is an engineering sabotage control, not the scientific competing baseline.

V is a subset of B **by construction**. False acceptance cannot increase on the same
inputs merely because another veto was added. A positive reduction is useful error
filtering, not proof of improved AI reasoning, scientific novelty or an unbiased oracle.
R may perform just as well; that negative result must lead the report if observed.

Charge each arm the same one AI request and identical input/output token counts;
charge V/R their actual additional CPU time, wall time and memory. Distinguish actual
shared API requests from counterfactual per-arm accounting; do not double-count
requests as observations. Log all failed requests, parsing failures, retries, latency,
tokens and currency if applicable. No spending is authorized by this proposal.
Proposed one request, no response-conditioned retries; transport failures are retained
as abstentions in every arm. A provider retry policy requires advance approval and
all attempts are charged. V/R exceptions or numerical UNRESOLVABLE are nonacceptance.

## 4. Model, prompt and run controls — unresolved fields block Gate C
Freeze provider, exact model snapshot/version, tokenizer, API/version or local model
hash, system/user prompt bytes, decoding settings, randomization and execution order.
Suggested initial decoding: temperature 0, top-p 1, one completion; provider nondeterminism
is still possible. No internet, tools, retrieval, verifier feedback or fault labels are
available to the reviewing model. Provider changes mid-run invalidate pooling unless
handled by a prospectively approved block design; preserve all outcomes as deviations.

Draft prompt contract (not yet final): present channel assumptions, signed h/U/mu/G,
declared wall-inclusive uniform grid and the entire profile at fixed precision. Ask
for strict JSON `{"accept": true/false, "reason": "..."}`. The prompt must not reveal
case identity, validity class, fault name, construction seed or expected answer.
Give all arms the same physical information and mathematical definitions. Freeze
exact token limits after feasibility counts; suggested ceilings are 8192 input and
256 output tokens, subject to tokenizer and resource approval.

Before fixing any stochastic noise bound, repeat an excluded pilot input at least
three times with the identical configuration. The previously proposed 20-case pilot
is also not authorized here. Log same-input variation and all prompts/outputs.
Run a counts-only feasibility script before freeze: eligible tasks/class/family,
token fit, expected requests and cost ceilings, no task contents/truth values.
Pilot task overlap with main is prohibited; no main outcomes may be inspected early.

## 5. Estimands, uncertainty and prospective decisions
Primary false acceptance in arm X: invalid units accepted by X / all invalid units.
False rejection: valid units not accepted by X / all valid units. Abstentions,
unresolved precision, malformed outputs and execution failures stay in denominators.
Also report conditional-on-completion rates, coverage and unresolved counts separately;
never use them to replace the conservative primary operational rates.

Primary paired reduction Delta = FAR(B)-FAR(V). Since V is nested, each invalid unit
is rescued (B accepts, V refuses) or not; Delta is the rescue probability under the
fixed task mixture. Report a 95% equal-tailed exact-binomial Clopper–Pearson interval
for this probability. Verify nesting explicitly; a single V acceptance with B refusal
is an implementation/protocol failure, not a negative statistical effect to ignore.

Proposed minimum meaningful reduction: **5 percentage points**, chosen as an owner
review proposal, not fitted to observations. Support the proposed operational claim
only if the two-sided 95% lower bound for Delta is at least .05 AND the 95% upper
bound for additional valid-case nonacceptance is at most .02. Report both conditions;
this conjunctive decision does not establish a broader intelligence claim.
For every arm also report its individual FAR/FRR and exact intervals. Numerical
inversion is tested, but should be cross-checked with a maintained statistics package
or independent statistician before the actual study analysis is frozen.

Report the exact two-sided McNemar p-value on discordances for B vs V (no early
looks or optional stopping). In the nested design this is descriptive additional
information; the effect-size interval and false-rejection cap govern the claim.
R vs V, family/fault strata, latency and model reasoning text are secondary descriptive
analyses. No post-hoc subgroup becomes a new confirmatory claim. If formally testing
multiple models or comparisons, freeze a family-wise error correction first.

Sample-size arithmetic is executed in `study_design.py`, retained in
`evidence/stage2/planning-arithmetic/`. Under the proposed IID mixture, 400 invalid
units give about 96.4% probability of obtaining a 95% lower bound >=.05 if the true
rescue rate is .10 (30 rescues required). This is an assumption-based operating
characteristic, not an observed AI performance prediction. With zero failures out
of 400 valid units, the two-sided 95% upper bound is approximately .918%.
At the former 200-total planning target (100 invalid/100 valid), zero false acceptances
still permit a two-sided upper bound of 3.62%; the same rescue condition has only
about 41.7% power at true rescue .10. A 200-total pilot cannot substantiate a 1% FAR.
Proving a one-sided 95% upper bound below 1% with zero failures requires 299 invalid
units under the binomial assumptions. Do not confuse one- and two-sided intervals.

800 main requests and all pilot/repeat requests require owner resource approval;
no sample-size expansion or external model calls are authorized by this draft.

## 6. Ground truth, provenance and analysis freeze
Gate B reviewer independently checks the governing ODE, parameter identifiability,
fault constructions, tolerance domain and approximate-profile semantics. A separate
program written by the same AI is insufficient. Reviewer identity, scope and actual
review level are recorded with consent; no reviewer is contacted by this work.

Freeze and hash: task generator and source revisions, private/held-out material access
policy, prompts, oracle, numerical policy, model, randomization, labels, metrics,
analysis code, resource ceilings and stop rules. No main tasks/labels are exposed to
the AI reviewer. Keep task manifest apart from response parser and decision code.
Bind every response/decision to task, specification, source, prompt and response hashes;
missing/stale/replayed/contradictory bindings are UNVERIFIED, never accepted by omission.
Strict JSON parser rejects duplicates, nonfinite values, unknown/missing fields and
booleans where samples are expected. This study adapter remains unbuilt/unreviewed.

No results overwrite prior records. Log time, environment, raw requests/responses,
costs, failures and deviations append-only. Infrastructure safety failure stops the
run for review with its partial data retained; it never produces a confirmatory p-value
under an unplanned stopping rule. A necessary design change gets a new registration
and fresh cases. Independent review precedes any findings release.

## 7. Required trigger table
| Trigger | Control | Answer and disposition |
|---|---|---|
| Feasibility | C-FEAS | yes; counts-only script and cost/token manifest required before freeze |
| Noise | C-NOISE | yes; >=3 identical excluded pilot calls before any stochastic bound |
| Statistics | C-STAT | yes; fixed horizon, exact-binomial intervals/paired test, no early looks |
| Evidence | C-EVID | yes; source/task/response identity, fresh/stale/unavailable/contradictory/same-source/replay controls required |
| Independence | C-INDEP | yes; current work self-tested/same-vendor; independent oracle review pending |
| External | C-EXT | yes; public primary references recorded in PROVENANCE.md |
| Device | C-DEVICE | yes; exact run platform/hashes recorded; no Android or cross-platform performance claim |
| Verdict code | C-BUILD | yes; explicit nonacceptance, positive and sabotage controls |
| Exploration | C-EXPLORE | yes; Stage 2 observed engineering cases excluded; related engineering entry appended to root FORKS.md |
| Method comparison | C-METHCOMP | yes for proposed workflow comparison; applicability of CONTROLS.md's experiment-specific parked protocol requires owner/method reviewer decision before freeze |

## 8. Gates and falsification
Gate A: reproducible local software evidence plus explicit calibration limits.
Gate B: independent oracle/fault review — pending. Gate C: owner chooses A/B,
approves resources/design, resolves control applicability, freezes preregistration
and explicitly authorizes execution — pending. Gate D: independent evidence review
and explicit authorization before public findings, main merge or release — pending.

Possible legitimate outcomes: no baseline false acceptances (no demonstrated benefit),
Delta below .05, too much false rejection, profile-only rival equally effective,
oracle disagreement, unresolved precision or insufficient independent evidence.
Preserve these without relabeling them as success. Next unrun discriminating step:
Gate B specification review and approved task/domain/arm design, not an AI benchmark.
