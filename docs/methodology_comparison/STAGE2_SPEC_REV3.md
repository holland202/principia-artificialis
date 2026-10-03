# Methodology comparison: Stage 2 freeze specification, revision 3 (PROPOSED)

**Status: PROPOSED. Not committed, not frozen. No tasks constructed, nothing executed.**
Stage 1 (`docs/METHODOLOGY_COMPARISON_PREREG.md`, commit `aef769eb4f3884cec4f54fef21e006313370a488`) is
immutable. Every place where this specification departs from Stage 1 is listed under "Deviations from
Stage 1", in four parts.

**Provenance:** Claude (Opus 5.5) drafted this revision at Chad Holland's direction, from reviewer feedback
he relayed. Review level so far: direction only. Claude drafted Condition B's skills and the Stage 1
design, so this specification is **not independent** of the thing it tests.

**Arithmetic:** every number in the worked examples and threshold tables was printed by a scratch script
using exact `fractions.Fraction` arithmetic (`rev3_examples.py`, session scratchpad, not in any repository).
None of it depends on experimental data.

---

## 0. What changed from revision 2

| # | Change | Reason |
|---|---|---|
| R3-1 | The constructor/sealer and the scorer are different people, and both are role-excluded | item 1: one person holding both the ground truth and the scoring can steer both |
| R3-2 | A second scorer on a preregistered subset, plus a verdict-robustness rule | item 2: scoring reproducibility was untested |
| R3-3 | Worked examples for the δ_min/η rule; the rule itself is unchanged | item 3 |
| R3-4 | The "no meaningful difference" rule gets a minimum analysed N and a resolution guard | item 4: ⌊3N/18⌋ is pathological below N = 12 (section 5) |
| R3-5 | Exactly 4 null tasks, and at least one sealed counterexample per non-null task | the per-outcome N would otherwise be a constructor choice (section 5.3) |
| R3-6 | A degrees-of-freedom audit and the self-audit | items 9 and 10 |

Kept from revision 2 without change:
- the independence gate and its default text;
- defect classes as diagnostic only, with a soft cap of no class over half the planted defects;
- the outcome definitions O1–O5 and their δ_min values;
- η as defined;
- the win and tie rule;
- the H2 rule;
- reporting both the Stage 1-literal and the Stage 2 analyses;
- directional prediction NONE;
- the shared-format and population limitations.

---

## 1. Roles and independence (R3-1)

| Role | Who may fill it | Must not be |
|---|---|---|
| **Constructor/sealer (C)** builds the 18 tasks, plants defects, writes the calibration forms, seals the ground truth and publishes the seal hash | one person | Chad Holland; Claude in any session; anyone who designed Condition B, Stage 1 or this specification; an executor; a scorer |
| **Primary scorer (S1)** scores all extracted forms against the sealed ground truth, and performs O4 re-runs | one person, ≠ C | the same exclusions; C |
| **Second scorer (S2)** independently scores the reliability subset (section 3) | one person, ≠ C, ≠ S1 | the same exclusions |
| **Operator** launches executor sessions in seed order and preserves artifacts | may be Chad Holland | must never see the sealed ground truth before scoring is committed |
| **Executors** | fresh sessions of the pinned model | — |
| **Extractor** | a fresh session of the pinned model with a frozen extraction prompt (hash committed before execution) | must not be given the sealed ground truth or the condition label |

**Gate (unchanged from revision 2 and not weakened):** if C and S1 cannot both be filled by distinct
people who meet these rules, the study does not run. The recorded outcome is:

> Methodology comparison: UNRUN — independent task construction and scoring not available.

A missing S2 does not stop the study; see section 3.

**Role declaration:** C, S1 and S2 each sign a short statement before receiving any materials. It
records:
- that they did not design Condition B, Stage 1 or this specification;
- any prior exposure to SWAY or the two skills;
- their relationship to Chad Holland.

The statement is committed. Prior exposure is not disqualifying, but it is reported.

---

## 2. Sealing sequence

1. This specification is frozen in a commit of its own. The commit includes:
   - the model pin;
   - the budget;
   - the randomization seed;
   - the reliability-subset seed;
   - the extraction prompt hash.
2. C builds the tasks and seals the ground truth. C publishes `sha256(sealed archive)` in a commit before
   any execution. The archive stays with C.
3. The task IDs and their recorded characteristics are published. The reliability subset is computed
   from the committed seed over the published task IDs, and the selection is committed. S1 is **not told**
   which tasks are in the subset until S1's scores are committed.
4. Execution runs (72 sessions), then extraction.
5. S1 scores. S1's scores are committed and hashed.
6. S2 scores the subset blind to S1. S2's scores are committed and hashed.
7. The analysis code runs on the committed scores. It is frozen and hashed before step 4.

---

## 3. Scoring reliability (R3-2)

**Subset (fixed before execution):**
- 6 of the 18 tasks, drawn with the committed reliability seed;
- the subset must contain at least 1 null task and at least 4 non-null tasks; the draw is repeated with
  seed+1, seed+2, … until it does;
- all 4 sessions of each subset task are scored, so 24 session-forms.

**What S2 receives:** the same extracted forms, sealed ground truth, rubric and calibration forms as S1.
S2 does not receive S1's scores.

**Agreement reported (no threshold, fixed now):**

| Item level | Judgment |
|---|---|
| O1 | each planted defect × session: discovered / missed |
| O2 | each extracted claim: supported / unsupported |
| O3 | each sealed counterexample × session: reported / missed |
| O4 | each session: reproduced / not |
| O5 | each claim: false / not false |

For each outcome the report gives:
- the 2×2 count table;
- raw agreement (agreements / items, as an exact fraction);
- Cohen's κ, or "κ undefined" where a marginal is degenerate.

**No agreement threshold is registered, and none may be added after the results.**

**Disagreement handling (fixed now):**
- The primary analysis uses S1's scores. Disagreements are not adjudicated into the data.
- Every disagreeing item is listed with both judgments.
- **Verdict-robustness rule:** the full analysis is re-run with S2's scores replacing S1's on the subset.
  If any outcome's verdict changes, the verdict reported for that outcome is "insufficient evidence
  (scorer-sensitive)". Both verdicts are shown.
- This rule ties the consequence of disagreement to the verdict itself, so no agreement number has to be
  chosen.

**If S2 is unavailable:** the study may still run, and the report states, verbatim:

> Scoring inter-rater reliability: NOT TESTED.

The verdict-robustness rule then cannot be applied, and this is listed as a limitation.

---

## 4. Win / tie rule (unchanged) and worked examples (R3-3)

**Orientation:** for each task t and outcome o, each condition's score is the mean of its 2 replicates.
d = B − A for "higher is better" outcomes (O1, O4). d = A − B for "lower is better" outcomes (O2, O3, O5).
Positive d favours B.

**Rule:**
- **B-win** iff d ≥ δ_min,t **and** d > η_o.
- **A-win** iff −d ≥ δ_min,t **and** −d > η_o.
- Otherwise the task is a **tie**.

**Both inequalities are deliberate:**
- d ≥ δ_min,t means one whole unit of the outcome's resolution on that task.
- d > η_o is strict: a difference equal to the typical same-input disagreement is not distinguishable
  from it.

**δ_min,t (from revision 2):**

| Outcome | Measure | δ_min,t |
|---|---|---|
| O1 | recall (discovered / m_t) | 1/m_t |
| O2 | unsupported-conclusion count | 1 |
| O3 | missed-counterexample rate | 1/c_t |
| O4 | reproduced (0/1 per session) | 1/4 |
| O5 | false-conclusion count | 1 |

**η_o:** the median, over all tasks eligible for outcome o and both conditions (2·N_o values), of
|r₁ − r₂|.

**The η = 0 concern** ("any nonzero d wins") is answered by δ_min. With η = 0, a win still needs one full
resolution unit. Example E10 below shows a nonzero d that does not win when η = 0.

**Worked examples.** The replicate values are illustrative inputs, not data.

| ID | Outcome, task | A reps | B reps | A mean | B mean | d | δ_min | η | d ≥ δ? | \|d\| > η? | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | O1, m_t = 3 | 2/3, 2/3 | 3/3, 2/3 | 2/3 | 5/6 | 1/6 | 1/3 | 1/3 | no | no | tie (below resolution) |
| E2 | O1, m_t = 3 | 1/3, 1/3 | 3/3, 2/3 | 1/3 | 5/6 | 1/2 | 1/3 | 1/3 | yes | yes | **B-win (both met)** |
| E3 | O1, m_t = 4 | 1/4, 2/4 | 2/4, 3/4 | 3/8 | 5/8 | 1/4 | 1/4 | 1/4 | yes | no | **tie: δ met, η blocks** |
| E4 | O2 | 3, 4 | 1, 2 | 7/2 | 3/2 | 2 | 1 | 1 | yes | yes | **B-win (both met)** |
| E5 | O2 | 2, 3 | 1, 2 | 5/2 | 3/2 | 1 | 1 | 1 | yes | no | **tie: δ met, η blocks** |
| E6 | O3, c_t = 5 | 3/5, 2/5 | 1/5, 1/5 | 1/2 | 1/5 | 3/10 | 1/5 | 1/5 | yes | yes | **B-win (both met)** |
| E7 | O3, c_t = 2 | 1/2, 0 | 1/2, 1/2 | 1/4 | 1/2 | −1/4 | 1/2 | 0 | no (−d = 1/4 < 1/2) | yes | tie: η exceeded, δ not |
| E8 | O4 | 0, 1 | 1, 1 | 1/2 | 1 | 1/2 | 1/4 | 1/2 | yes | no | **tie: δ met, η blocks** |
| E9 | O4 | 1, 1 | 0, 0 | 1 | 0 | −1 | 1/4 | 1/2 | −d ≥ δ: yes | yes | **A-win (both met)** |
| E10 | O5 | 0, 0 | 1, 0 | 0 | 1/2 | −1/2 | 1 | 0 | no | yes | tie: η = 0 does not make a win |

Notes on the examples:
- E1 to E3 are O1 tasks with several planted defects (m_t = 3 and 4).
- E3, E5 and E8 meet δ but are blocked by η.
- E2, E4, E6 and E9 meet both thresholds.
- E9 shows that the rule is symmetric: A can win.

**An observation about O4 (not a change):** with 2 binary replicates, d ∈ {−1, −1/2, 0, 1/2, 1}. So
δ_min = 1/4 is met by every nonzero d, and on O4 only η discriminates. This is recorded so that nobody
reads δ_min = 1/4 as doing any work on O4.

**A known limitation of η (scale mixing), retained:**
- η_o pools tasks with different resolution. An O1 task with m_t = 1 has replicate differences in {0, 1};
  one with m_t = 4 has them in steps of 1/4.
- For O2 and O5 the counts are not normalized, so tasks with more claims contribute larger differences.
- A per-task η would rest on 2 values per condition and is too unstable to use.
- Pooling is therefore kept, and the δ_min,t term carries the task-specific scale.
- The report also lists every task's replicate differences, so a reader can see whether one coarse task
  dominates η.

---

## 5. "No meaningful difference" rule (R3-4, R3-5)

### 5.1 Analysis of ⌊3·N_o/18⌋

| N_o | ⌊3N_o/18⌋ non-ties allowed | Allowed fraction | Smallest possible sign-test p (all non-ties one way) | Fewest same-sign wins for p ≤ 0.05 | 95% one-sided upper bound on the non-tie rate if 0 non-ties are observed |
|---|---|---|---|---|---|
| 5 | 0 | 0 | 0.0625 | none (impossible) | 0.4507 |
| 6 | 1 | 1/6 | 0.03125 | 6 of 6 | 0.3930 |
| 12 | 2 | 1/6 | 0.00049 | 10 of 12 | 0.2209 |
| 14 | 2 | 1/7 | 0.00012 | 12 of 14 | 0.1926 |
| 18 | 3 | 1/6 | 0.00001 | 14 of 18 | 0.1533 |

**The defect.** At small N the rule fails in both directions at once.
- At N_o = 5 it demands zero non-ties, which is maximally strict. Yet even a perfect result (5 of 5 ties)
  is compatible with a true non-tie rate as high as 45%.
- So "no meaningful difference" could be declared from an analysed set too small to bound the effect.
- At the same N, a directional verdict is impossible (p ≥ 0.0625).
- The verdict space collapses onto "equivalent" or "insufficient", decided by a handful of tasks.
- At N_o = 6, one non-tie is allowed out of six, and the upper bound is still 39%.
- The floor also makes the allowed fraction jump (1/6, then 1/7 at N = 14).

**Retained:** the tolerance of 1/6 of analysed tasks. This is Stage 1's "3 of 18", and moving it now
would be a post-design change with no new information.

### 5.2 Replacement rule (fixed now)

For each outcome o, with N_o = the number of tasks analysed for o after all exclusions:

1. **Minimum analysed N.** If N_o < 12, the verdict for o is "insufficient evidence", whatever the data.
   - **Justification:** 12 is two-thirds of the registered 18. Losing more than a third of the tasks means
     the analysed population is no longer the registered one.
   - At N_o = 12, both a directional verdict (10 of 12) and an equivalence verdict are reachable.
   - The threshold is fixed before construction, from the design alone.
2. **Equivalence.** "No meaningful difference detected" on o requires all three of:
   - N_o ≥ 12;
   - number of non-tie tasks ≤ ⌊N_o/6⌋;
   - **resolution guard:** η_o < median_t δ_min,t,o.
3. **Why the resolution guard.** If same-input noise is at least as large as the typical meaningful unit,
   every task ties by construction. "Equivalent" would then mean only "the instrument cannot see the
   differences we defined as meaningful". In that case the verdict is "insufficient evidence
   (noise ≥ resolution)". This is an anti-vacuity control on the null verdict itself: the equivalence
   instrument must be capable of returning "not equivalent".
4. **Directional verdicts.** These are unchanged from Stage 1 and revision 2: an exact two-sided sign test
   over non-tie tasks gives p ≤ 0.05, and the median d exceeds η_o. They now also require N_o ≥ 12.

### 5.3 Fixing N_o before construction (R3-5)

O1 is undefined on null tasks (m_t = 0), and O3 is undefined where c_t = 0. Under Stage 1's "at least 4
null tasks", the constructor's choice of null count would set N_O1 and N_O3. With 7 nulls, for example,
N_O1 = 11 and O1 becomes "insufficient evidence" automatically. To remove that freedom:
- **exactly 4** of the 18 tasks are null tasks;
- every non-null task has m_t ≥ 1 and at least c_t ≥ 1 sealed counterexample. A reproducing input for a
  planted defect counts.
- So N_reg = 14 for O1 and O3, and 18 for O2, O4 and O5.
- O1 and O3 therefore reach "insufficient evidence" after 3 exclusions.
- O2, O4 and O5 reach it after 7.
- This asymmetry is reported up front.

---

## 6. Limitations preserved

**Shared format (preserved, not weakened).**
- Both conditions are given the same output appendix (CLAIMS.json and the reporting fields).
- So the experiment tests **"method + standardized reporting format"**, not either methodology in
  isolation.
- Any difference, or the absence of one, is a property of the method together with that format.

**Population (preserved, made explicit).** Even a statistically significant directional result would be
evidence only under all of the following:
- the frozen task population (these 18 tasks, built by this constructor);
- the pinned executor model;
- the frozen method texts (Condition A as reconstructed in Stage 1; Condition B at the frozen md5s);
- the frozen scoring protocol and rubric;
- the shared reporting format.

It is **not** evidence of general methodological superiority, of how human researchers would perform,
or of performance on this estate's real history (excluded by Stage 1).

**Directional prediction: NONE** for O1–O5 (unchanged). The cost direction stays as Stage 1 registered
it.

**Allowed wording of conclusions:**
- "B performed better on outcome o under these conditions";
- "no meaningful difference detected on o";
- "A performed better on o under these conditions";
- "effects differed by task category (descriptive)";
- "insufficient evidence".

No overall score, ranking or winner.

---

## 7. Deviations from Stage 1 (four-part form)

| ID | Stage 1 said | Stage 2 changes | Why | Expected methodological effect |
|---|---|---|---|---|
| D-1 (rev 2) | sign test over tasks with d ≠ 0; H0 counts tasks with \|d\| > noise | a task is non-tie only if it meets both δ_min,t and η | d ≠ 0 counts sub-resolution differences (E1) as signal | fewer non-ties: harder to reach a directional verdict, easier to reach equivalence. Stage 1-literal results are reported alongside |
| D-2 (rev 2) | O1 and O3 as counts | O1 as recall (/m_t), O3 as a missed rate (/c_t) | counts scale with how many defects the constructor planted per task | tasks become comparable; tasks with m_t = 0 or c_t = 0 drop out of O1 and O3 (see D-6) |
| D-3 (rev 2) | no defect classes | defect classes recorded, diagnostic only, soft cap ≤ ½ per class | to diagnose sensitivity without letting the composition decide the verdict | none on the primary verdict; adds descriptive tables |
| D-4 (rev 2, amended rev 3) | builder "Chad Holland or an outside contributor"; evaluator "the task author, or another person who executed nothing" | C and S1 are distinct people; Chad, Claude and the designers are excluded from both; otherwise UNRUN | the designer of B, or a co-author of the method, must not set or score the test; one person holding both the ground truth and the scoring can steer both | the study may not run (a likely outcome, stated in advance); if it runs, the ground truth is separated from the judgment |
| D-5 (rev 3) | H0: at most 3 of 18 tasks with \|d\| > noise; no minimum N | N_o ≥ 12 for any verdict; non-ties ≤ ⌊N_o/6⌋; resolution guard η_o < median δ_min | Stage 1's "3 of 18" generalized as ⌊3N/18⌋ is pathological at small N (section 5.1), and noise can force equivalence | more "insufficient evidence", fewer unsupported equivalence claims; at N_o = 18 the tolerance equals Stage 1's |
| D-6 (rev 3) | "at least 4" null tasks | exactly 4; every non-null task has m_t ≥ 1 and c_t ≥ 1 | the null count would otherwise fix N_O1 and N_O3 and could trigger D-5's minimum | removes a constructor freedom; Stage 1's lower bound is still met |
| D-7 (rev 3) | no scoring-reliability check | S2 on a 6-task seeded subset; agreement reported without a threshold; the verdict-robustness rule | the scorer's judgments are the measurement, and their reproducibility was untested | verdicts that depend on which scorer scored are downgraded; if no S2, "NOT TESTED" is stated |

---

## 8. Remaining researcher degrees of freedom

| Decision | Can it move the verdict? | Status |
|---|---|---|
| δ_min per outcome, the win/tie rule, the strict ">" on η | yes | fixed before task construction (this spec) |
| N_min = 12, the tolerance ⌊N/6⌋, the resolution guard | yes | fixed before task construction |
| Null count = 4; m_t ≥ 1, c_t ≥ 1 on non-null tasks | yes | fixed before task construction |
| Model pin, 90-min cap, token cap, tool access, task-text template | yes | fixed before task construction |
| Randomization seed, reliability-subset seed | yes (order, subset) | fixed before task construction |
| Which tasks, which defects, defect classes, difficulty, m_t, c_t | **yes, strongly** | independently decided by C, sealed and hashed before execution; class composition is a **limitation** (it shapes what "discovery" means) |
| The calibration forms | yes (exclusions) | independently decided by C, sealed |
| Extraction prompt and neutral-field mapping | yes (partial blinding) | fixed before execution (hash committed); same-vendor extraction is a **limitation** |
| The "unsupported conclusion" rubric (O2) | yes | fixed before execution; its application is independently decided by S1 and checked by S2 |
| Judgment calls while scoring | yes | independently decided (S1), subset-checked (S2), robustness rule |
| O4 re-run environment | yes | fixed before execution (container spec committed); S1 runs it |
| Missing-data handling, one rerun | yes | fixed (Stage 1) |
| Calibration-failure exclusion, detection-floor flag | yes | mechanical, given the sealed forms |
| Analysis code | yes | fixed before execution (hash committed) |
| Which secondary or descriptive tables to highlight | interpretation only | **limitation**: all registered tables are reported in full, and no new ones are promoted to primary |
| Choosing C, S1 and S2 | yes | made by Chad Holland, a co-author of B. **Limitation**: role declarations are committed, but the selection itself is not independent |
| The decision to declare UNRUN | yes (whether a result exists) | fixed rule (section 1); not discretionary |
| The executor's prior exposure to SWAY and skill ideas | yes | uncontrollable; **limitation** (Stage 1) |

---

## 9. Revision 3 self-audit

Checked against: **Register → freeze → build the smallest discriminating test → observe → attack →
preserve failures → distinguish observation from interpretation → never let the artifact certify
itself.**

| Step | Status in the design |
|---|---|
| Register | Stage 1 committed (`aef769e`); this spec is to be committed alone before any construction |
| Freeze | the thresholds, seeds, model, budget, extraction prompt and analysis code are hashed before execution; the ground truth is sealed by hash before execution |
| Smallest discriminating test | 18 tasks × 2 conditions × 2 replicates is the Stage 1 minimum. It is small enough that "insufficient evidence" is a likely and acceptable outcome, and is stated as such |
| Observe | scores come from the sealed ground truth and the committed scorer outputs, not from the executors' self-reports |
| Attack | calibration forms (the instrument must return "missed"); the resolution guard (equivalence must be able to fail); S2 with verdict robustness (scoring must reproduce); the sign test (direction can favour A, as in E9) |
| Preserve failures | the Stage 1-literal analysis is reported beside the Stage 2 analysis; all deviations are listed; exclusions, disagreements and UNRUN are reported as outcomes |
| Observation vs interpretation | per-outcome verdicts only; the population and format limitations are bound to every verdict; no overall winner |
| Never let the artifact certify itself | Claude and Chad are excluded from C, S1 and S2; the default is UNRUN |

**Where the study could still certify itself, or be steered:**

1. **Role selection.** Chad Holland picks C, S1 and S2. A choice of sympathetic or familiar people is not
   prevented, only disclosed. Partial mitigation: committed role declarations. Not solved.
2. **Same-vendor pipeline.** The executors and the extractor are the same model family that drafted
   Condition B. The extractor normalizes vocabulary, and that normalization could favour the vocabulary
   it shares with B. Reported, not solved.
3. **This specification is Claude-drafted.** Every threshold here was chosen by the drafter of B, before
   any data and with an attempt to make them neutral, but not independently. Freezing removes
   post-results tuning, not design-time bias. An outside review of this spec before freezing would reduce
   it. That review has not happened.
4. **Constructor composition.** The constructor still decides what kinds of defects exist. Classes are
   diagnostic only, but the planted set defines "discovery" for O1 and O3.
5. **η pooling.** A few coarse tasks can raise η_o and push the result toward ties. The resolution guard
   stops this from becoming "equivalence". It can still suppress a directional verdict, and the per-task
   listing makes that visible.
6. **"Insufficient evidence" is cheap.** Several rules here push toward it. That is the conservative
   direction, but a reader must not take it as "no difference".

**Claims this document makes about results: none.** The methodology comparison has demonstrated
nothing. Current status: designed, not constructed, not run. If the independent roles are not filled,
the status is:

> Methodology comparison: UNRUN — independent task construction and scoring not available.
