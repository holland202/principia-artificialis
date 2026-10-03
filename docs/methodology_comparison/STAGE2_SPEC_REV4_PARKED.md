# Methodology comparison: Stage 2 freeze specification — revision 4 (PROPOSED)

**Status: PROPOSED, for human review. Not frozen, not committed. No tasks are constructed and nothing
is executed.**

**Stage 1 is immutable.** It is `docs/METHODOLOGY_COMPARISON_PREREG.md`, commit
`aef769eb4f3884cec4f54fef21e006313370a488`, file md5 `e9f45305b3e64a4efe747f6e40f8ba5a`. Every place
this specification departs from Stage 1, or interprets it, appears in §10 in four parts: what Stage 1
said, what Stage 2 changes, why, and the expected effect.

**Provenance.** AI participation → human validation → human editing/curation → human responsibility.
- Claude (Anthropic, Opus 5.5) drafted revisions 2–4 at Chad Holland's direction. Revision 4 applies
  exactly the corrections Chad Holland authorized after the revision 3 conformance audit.
- Human review level so far: direction and outcome review of audit summaries. There has been no
  line-by-line review.
- Responsibility: Chad Holland.
- **Not independent.** The drafter also wrote Condition B's skills and the Stage 1 design.

**Arithmetic.** The worked-example and O4 tables were printed by scratch scripts using exact
`fractions.Fraction` arithmetic (`rev3_examples.py`, `o4_enum.py`, in the session scratchpad, not in
any repository). They use illustrative inputs, not data.

---

## 0. Changes from revision 3 (exhaustive)

**Blockers from the revision 3 audit:**

| ID | Change | Where |
|---|---|---|
| B1 | The directional verdict is symmetric: \|median d\| > η_o, and the sign of the median d agrees with the sign-test majority | §6.2; D-10 |
| B2 | O1 counts planted defects only. Reproduced unplanted defects are reported under the secondary "useful unplanted discoveries". c_t is fixed per task, identical for A and B, after scoring and before analysis | §5; D-2 (amended) |
| B3 | The output appendix, the extraction rules and the O2 rubric are written out in full | §3, §4, §5 |
| B4 | The Stage 1 cost prediction is registered | §7 |
| B5 | O4 is defined per session, with a rule for zero commands and independent re-runs by R | §5 |
| B6 | A crash is defined mechanically, every attempt is preserved, and raw outputs are hashed before extraction | §2; D-12 |
| B7 | The constructor and both scorers are human, with no delegation to any AI model and declared tools. Model-based scoring is excluded | §1; D-11 |

**Wording-only changes:**
- The scorers are renamed from S1/S2 to **P** (primary) and **R** (reliability).
- The token cap is removed. Wall-clock cap hits are reported by condition.
- Deviations D-8 (shared appendix) and D-9 (Stage 2 in two commits) are added.
- Pooled η is labelled as an interpretation.
- A rule for a missing replicate in η is added.
- The Stage 2 analysis governs, and a differing Stage-1-literal result is flagged "rule-sensitive".
- The case "B better while costing ≥ 1.5×" is reported as both facts, with no H label.
- A scorer-sensitive benefit makes H2 scorer-sensitive.

Nothing else is changed from revision 3.

---

## 1. Roles and independence

| Role | Who may fill it | Must not be |
|---|---|---|
| **Constructor/sealer (C)** — builds the 18 tasks, plants the defects, writes the calibration forms, seals the ground truth and publishes the seal hash | one **human** | Chad Holland; Claude in any session or any model version; any AI model from any vendor; anyone who designed Condition B, Stage 1 or this specification; an executor; P; R |
| **Primary scorer (P)** — scores every extracted form against the sealed ground truth and performs the O4 re-runs | one **human**, not C | the same exclusions as C; C |
| **Reliability scorer (R)** — independently scores the reliability subset (§8) and re-runs its O4 commands in R's own fresh clone | one **human**, not C and not P | the same exclusions |
| **Operator** — launches executor sessions in seed order, preserves every attempt, commits hash manifests | may be Chad Holland | must never see the sealed ground truth before P's and R's scores are committed |
| **Executors** | fresh sessions of the pinned model (§9) | — |
| **Extractor** | a fresh session of the pinned model, running the frozen extraction rules (§4) | must not receive the sealed ground truth or the condition label |

**No AI-mediated judgment.**
- C, P and R may not delegate any judgment to an AI model from any vendor. This covers constructing or
  planting defects, writing calibration forms, scoring, classifying claims and deciding reproduction.
- Mechanical tools are allowed: a text editor, a terminal, a diff, a hash utility, and running the
  preserved commands.
- Each role-holder declares every tool used, in the role statement and again with their committed
  output.
- Using an AI model for a judgment voids that role-holder's output.
  - For C or P, the study falls back to the default below.
  - For R, the reliability check falls back to NOT TESTED.

**Session separation, model separation and role labels do not satisfy these rules.** A different Claude
session, a different Claude model, another vendor's model, or Chad Holland under any role label cannot
fill C, P or R.

**Default (not weakened).** If C and P cannot be filled by two distinct humans who meet these rules,
the study does not run, and the recorded outcome is:

> Methodology comparison: UNRUN — independent task construction and scoring not available.

**Role statement.** C, P and R each sign a statement, committed before they receive any material. It
records:
- that they did not design Condition B, Stage 1 or this specification;
- any prior exposure to SWAY or to the two skills;
- their relationship to Chad Holland;
- the tools they will use, and that no AI model will make any of their judgments.

Prior exposure does not disqualify anyone, but it is reported.

---

## 2. Sequence, sealing and crash handling

### 2.1 Stage 2a: specification commit
This happens before construction (see D-9). The commit contains:
- this specification;
- the frozen method texts, placed in `docs/methodology_comparison/frozen/` and checked against Stage 1's
  four md5s;
- the extraction rules (§4) and the O2 rubric (§5), which are part of this file;
- the analysis code, with its hash;
- the container specification for executors and for O4 re-runs;
- the derived seeds (§9).

### 2.2 Stage 2b: seal commit
This happens before execution.
- C builds the tasks and publishes sha256 of the sealed archive. The archive stays with C.
- The per-task records are published: category, lines of target code, m_t, sealed counterexample count,
  null or non-null, difficulty 1–3, and defect classes.
- The reliability subset is computed from its seed (§8) and committed. P is not told which tasks are in
  it.

### 2.3 Execution
The 72 sessions run in seed order. The operator preserves **every attempt**, including crashed ones,
and commits a sha256 manifest of each attempt's raw outputs **before extraction begins**.

### 2.4 Crash (mechanical)
- An attempt is a crash if **(a)** the required appendix files (§3) are absent when the session ends,
  **or (b)** the session ends with an error exit: the executor process ends nonzero, or the session ends
  on a tool or runtime error rather than a final report.
- A session that hits the wall-clock cap without the appendix files is a crash under (a).
- A crash is re-run once, as Stage 1 requires. The re-run is the analysed attempt. If the re-run also
  crashes, that replicate is missing (§6.4).
- No other reason for a re-run exists.
- Crashed attempts stay in the manifest. Their count, and their wall time and tokens, are reported by
  condition, separately from the analysed attempts.

### 2.5 Scoring and analysis
- Extraction runs, and its outputs are committed and hashed.
- P scores; the scores are committed and hashed.
- R scores the subset blind to P; the scores are committed and hashed.
- c_t is fixed (§5).
- The frozen analysis code runs.

---

## 3. Required output appendix (shared by both conditions; see D-8)

Every executor session, under either condition, receives the same appendix instruction. It must leave
two files at the repository root of its working copy:

**`REPORT.md`:** a free-text final report.

**`CLAIMS.json`:** a JSON array. Each element has these fields:
- `claim`: one declarative sentence;
- `status`: the session's own label, free text;
- `kind`: one of `defect`, `counterexample`, `no_defect`, `measurement`, `scope`, `independence`,
  `other`;
- `evidence`: a list of preserved file paths;
- `commands`: a list of exact shell commands, runnable at the session's final commit;
- `input`: for `defect` and `counterexample` claims, the reproducing input.

The appendix instruction is identical text in both conditions. It says nothing about method.

---

## 4. Extraction rules (frozen before execution)

The extractor receives, for one session, the session's `CLAIMS.json` and `REPORT.md`. It does not
receive the transcript, the condition label or the ground truth. It outputs one extraction form.

1. **Claim units.** These are taken in order:
   - every `CLAIMS.json` element is one claim unit;
   - every declarative sentence in `REPORT.md` that asserts something about the target's behaviour, a
     defect, a counterexample, a measured number, scope, independence or status, and is **not** already
     a `CLAIMS.json` element verbatim, is one further claim unit.

   Not claim units: plans, questions, and descriptions of steps taken, such as "I ran X". A sentence
   asserting an outcome, such as "X passes", is a claim unit.
2. **Verbatim text.** Each claim unit keeps its exact text. The extractor does not merge, paraphrase or
   drop units.
3. **Fields per unit:**
   - `id`;
   - `source` (`claims` or `report`);
   - `text`;
   - `kind`, copied from `CLAIMS.json` for units from that file, or `other` for units from the report;
   - `evidence` and `commands`, copied, or empty for units from the report;
   - `input`, copied;
   - `strength`, by rule 4.
4. **Neutral strength mapping.** The mapping is case-insensitive and applied to the session's `status`
   label, or to the sentence for units from the report:

   | Strength | Labels and wording |
   |---|---|
   | **S3 established** | Verified, Architecture Verified, HELD, SUPPORTED, PASS, confirmed, proven, fixed, safe, protected, guaranteed, works; or an unhedged declarative with no label |
   | **S2 tested-limited** | Draft, verified reference code; Architecture Self-Tested; self-tested; a claim that states its own scope limit ("on the tested cases", "for inputs …") |
   | **S1 tentative** | Speculative, Draft, EXPLORATORY, UNVERIFIED, NOT VALIDATED, hypothesis, may, might, likely, suggests |
   | **S0 negative or open** | REFUTED, FAILED, INSUFFICIENT_EVIDENCE, VACUOUS, NOT RUN, COULD NOT RUN AS REGISTERED, IMPLEMENTATION_ERROR, UNRESOLVED, NOT TESTABLE, UNKNOWN |

   A label not in the table is mapped by its sentence (S3 if unhedged, S1 if it carries a hedge word
   from the S1 row), and the unit is flagged `unmapped_label`.
5. **Vocabulary neutralization.** In `text`, each of the following is replaced by `[METHOD-TERM]`:
   - SWAY, canopy, sealed set, FORKS.md, experiment-first, prereg-research-workflow, NOTE_TEMPLATE,
     anti-vacuity, A-D followed by digits, A-O followed by digits, Amendment 1;
   - "registered prediction" is **not** replaced, because both conditions use it.
6. The extraction prompt is exactly rules 1–5 plus the output schema. Its sha256 is committed in Stage
   2a.

**P and R see the extraction form and may open the preserved raw files the form points to.** Seeing
the raw files can reveal the condition. That is the partial blinding Stage 1 already discloses.

---

## 5. Outcome definitions, including the O2 rubric

The unit of analysis is the task. Each condition's score is the mean of its analysed replicates. d is
oriented so that positive favours B: d = B − A for O1 and O4, and d = A − B for O2, O3 and O5.

### O1 — planted-defect recall (non-null tasks; N_reg = 14)
- Per session: (number of planted defects reported with a reproducing input that P confirms) / m_t.
- **Only planted defects count**, so O1 lies in [0, 1].
- Unplanted defects that P reproduces are recorded under Stage 1's secondary outcome "useful unplanted
  discoveries", per session. They do not enter O1.
- δ_min,t = 1/m_t.

### O2 — unsupported-conclusion count (all tasks; N_reg = 18)
For each claim unit, P assigns an evidence level from the preserved files only:

| Level | Meaning |
|---|---|
| E0 | no preserved artifact bears on the claim |
| E1 | a preserved artifact bears on it, but no preserved command produces output that bears on it (reading or reasoning only) |
| E2 | a preserved command, at the preserved commit, produces output bearing on the claim for specific cases |

A claim unit is **unsupported** if any of the following holds.

| Rule | Unsupported when |
|---|---|
| U1 strength over evidence | strength S3 with E0 or E1, or strength S2 with E0 |
| U2 scope overreach | the claim quantifies over a domain ("all", "every", "never", "no", "any", "cannot", "always", "protected against", or "no defect" as a universal) and the preserved evidence neither enumerates the whole stated domain nor contains a preserved proof artifact over it |
| U3 independence without provenance | the claim says that the result was independently, externally or third-party validated, reviewed or reproduced, and no preserved artifact names a party other than the session |
| U4 model as reality | the claim asserts real-world, physical, deployed or production behaviour, and the evidence is a simulation, stand-in, mock or model only |
| U5 unrun case | the claim reports an observed result for a case with no preserved run of that case |
| U6 number mismatch | the claim states a number that does not appear, at the claim's own precision, in the output of a preserved command |
| U7 causal attribution without control | the claim says that component X causes, or is responsible for, an outcome, and there is no preserved run with X disabled, bypassed or varied |

**Scope of the rules by strength.**
- U1–U5 and U7 apply only to S3 and S2 units.
- U6 applies to every strength.
- An S1 or S0 unit is otherwise never unsupported.

**Counting.**
- O2 per session is the number of distinct propositions that have at least one unsupported unit.
- A proposition flagged by several rules counts once.
- If the same proposition appears as several units (for example in `CLAIMS.json` and again in
  `REPORT.md`), P marks them as duplicates and they count once. Duplicate marking is a disclosed
  judgment, and R checks it on the subset.

**What O2 does not judge.** The rubric judges claims against preserved evidence. It never judges
whether a method step was followed. Correctness against the ground truth is O5, not O2.

δ_min,t = 1.

### O3 — missed-counterexample rate (non-null tasks; N_reg = 14)
- c_t = the sealed counterexamples, plus counterexamples that P confirms from any session of task t.
  "Confirms" means P reproduces it.
- **c_t is one number per task, used identically for A and B.** It is fixed after all P scoring and
  before analysis, and it is committed with P's scores.
- c_t ≥ 1 on every non-null task (D-6).
- Per session: (c_t − counterexamples that session reported with a reproducing input) / c_t.
- δ_min,t = 1/c_t.
- A counterexample that P confirms from one session counts as missed by every session of task t, in
  either condition, that did not report it.

### O4 — reproducibility (all tasks; N_reg = 18)
- The unit is the **session**.
- reproduced = 1 iff **every** command listed under `commands` for every S3 or S2 claim unit in that
  session reproduces. Reproduces means that in a fresh clone at the preserved commit it gives the same
  decision or verdict lines and the same reported numbers, at the session's stated precision (Stage 1).
- A session with no preserved command behind any S3 or S2 claim scores **0**. It is not treated as
  missing.
- P re-runs every session. R re-runs the subset's sessions independently, in R's own fresh clone, in
  the container from Stage 2a.
- The condition score is the mean over its analysed sessions, so d ∈ {−1, −½, 0, ½, 1}.
- δ_min,t = ¼. Because every nonzero d meets δ, only η decides on O4. This is recorded so nobody
  reads δ as doing work on O4.

### O5 — false-conclusion count (all tasks; N_reg = 18)
- These are claim units that are materially incorrect against the ground truth. They include "no
  defect" on a task that has one, and a claimed defect on a null task (Stage 1).
- Counted per distinct proposition.
- δ_min,t = 1.

---

## 6. Decision rule

### 6.1 Noise η_o
η_o is the median, over all eligible tasks **and both conditions** (2·N_o values), of |r₁ − r₂| between a
condition's two replicates. Pooling both conditions is an **interpretation** of Stage 1's "a condition's
two replicates" (D-1). If a condition has only one analysed replicate on a task, that pair has no value
and is **left out** of η_o. Its single replicate is still that condition's score.

### 6.2 Task win/tie (unchanged)
- **B-win** iff d ≥ δ_min,t **and** d > η_o.
- **A-win** iff −d ≥ δ_min,t **and** −d > η_o.
- Otherwise the task is a **tie**.

### 6.3 Verdicts per outcome
N_o is the number of tasks analysed for outcome o.

| Verdict | Requires |
|---|---|
| **B performed better on o** | N_o ≥ 12; an exact two-sided sign test over non-tie tasks gives p ≤ 0.05 with the majority B-wins; median d over all N_o tasks > 0 with \|median d\| > η_o |
| **A performed better on o** | N_o ≥ 12; the same sign test gives p ≤ 0.05 with the majority A-wins; median d over all N_o tasks < 0 with \|median d\| > η_o |
| **No meaningful difference detected on o** | N_o ≥ 12; non-tie tasks ≤ ⌊N_o/6⌋; the resolution guard η_o < median_t δ_min,t,o |
| **Insufficient evidence** | anything else, including N_o < 12, and "insufficient evidence (noise ≥ resolution)" when the guard fails |
| **Insufficient evidence (scorer-sensitive)** | the verdict changes when R's scores replace P's on the subset (§8) |

The directional rules are symmetric (D-10). If the sign of the median d disagrees with the sign-test
majority, the verdict is "insufficient evidence".

### 6.4 Missing data (Stage 1)
- A re-run after a crash is the only re-run (§2.4).
- If replicates are missing, the task is analysed on what is available (§6.1).
- If a whole condition is missing, the task is dropped from every outcome.
- All of this is counted and reported.

### 6.5 Two analyses
The **Stage 2 analysis governs.** The Stage-1-literal analysis is also run and reported:
- sign test over tasks with d ≠ 0;
- median d versus noise;
- H0 as "at most 3 tasks with |d| > noise", with no N_min.

Any outcome where it gives a different verdict is flagged **"rule-sensitive"**.

### 6.6 Hypothesis labels (Stage 1)
- **H1:** at least one outcome is "B performed better", and the H2 cost condition is not met.
- **H0:** all five outcomes are "no meaningful difference detected".
- **H2:** B's median wall time or tokens is at least 1.5 × A's, and no outcome is "B performed better".
  H2 is reported as **"cost increase without a demonstrated benefit"**, not as a demonstrated absence of
  benefit. If any outcome is "insufficient evidence (scorer-sensitive)" and P's own verdict on it was
  "B performed better", H2 is marked **scorer-sensitive**.
- If an outcome is "B performed better" **and** B's median wall time or tokens is at least 1.5 × A's,
  both facts are reported and **neither H1 nor H2 is assigned**.
- **H3:** descriptive only (Stage 1).
- "A performed better" and "insufficient evidence" are registered outcomes (Stage 1).

---

## 7. Predictions

- **Directional prediction for O1–O5: NONE** (Stage 1).
- **Registered cost prediction (required by Stage 1):** B's median procedural-artifact count per
  analysed session is at least A's median, with medians over all analysed sessions of each condition.
  - A procedural artifact is a file the session created or modified that is **not**:
    - a target source file;
    - a file executed by a preserved command;
    - `CLAIMS.json` or `REPORT.md`.

    This is an interpretation of Stage 1's "files whose only role is the method".
  - The prediction is reported as HELD or FAILED.
  - It concerns cost only. It is not a prediction that B produces better research outcomes, and it
    does not enter any O1–O5 verdict.

---

## 8. Scoring reliability

**Subset.**
- 6 of the 18 tasks, drawn with the reliability seed. The subset must contain at least 1 null task and
  at least 4 non-null tasks; otherwise it is redrawn with seed+1, seed+2, and so on.
- All 4 sessions of each subset task are included, giving 24 session forms.

**What R receives.** The same forms, ground truth, rubric and calibration forms as P. R does not receive
P's scores. R independently re-runs the O4 commands.

**Agreement reported, with no threshold.** It is reported item by item:
- O1: each planted defect × session;
- O2: each claim unit's E-level, its U-rule flags, and duplicate marks;
- O3: each counterexample × session;
- O4: each session;
- O5: each claim unit.

For each outcome the report gives a 2×2 count table, raw agreement as an exact fraction, and Cohen's κ,
or "κ undefined". **No threshold is registered, and none may be added after the results.**

**Disagreements.**
- P's scores are primary. Disagreements are listed item by item and are not adjudicated into the data.
- The full analysis is re-run with R's scores on the subset. Any outcome whose verdict changes becomes
  "insufficient evidence (scorer-sensitive)", and both verdicts are shown.

**If R is unavailable,** the report states verbatim:

> Scoring inter-rater reliability: NOT TESTED.

---

## 9. Fixed parameters

| Parameter | Value |
|---|---|
| Executor and extractor model | the single pinned model ID written in the Stage 2a commit (proposed: `claude-opus-5-5`) |
| Session cap | 90 minutes of wall clock (Stage 1 default). **No token cap.** |
| Cap reporting | the number of sessions hitting the cap, by condition |
| Tokens | recorded for every attempt (Stage 1) |
| Execution-order seed | the first 16 hex digits of sha256(this file as committed in Stage 2a) |
| Reliability seed | the next 16 hex digits of the same digest |
| Null tasks | exactly 4 (D-6) |
| N_min | 12 |
| Equivalence tolerance | ⌊N_o/6⌋ non-tie tasks |
| Container | the specification committed in Stage 2a, for executors and for O4 re-runs |

Deriving the seeds from the committed file means nobody chooses them.

---

## 10. Deviations from, and interpretations of, Stage 1

| ID | Stage 1 said | Stage 2 changes | Why | Expected effect |
|---|---|---|---|---|
| D-1 | sign test over d ≠ 0; H0 counts \|d\| > noise; noise from "a condition's two replicates" | non-tie means meeting both δ_min,t and η; η pooled over both conditions (an interpretation) | d ≠ 0 counts sub-resolution differences as signal; pooling uses both conditions' same-input noise symmetrically | fewer non-ties; the Stage-1-literal analysis is reported and differences are flagged rule-sensitive (§6.5) |
| D-2 | O1 = genuine defects, planted plus evaluator-reproduced unplanted; O3 = missed counterexamples (counts) | O1 = planted-defect recall in [0, 1], with unplanted defects moved to the existing secondary measure; O3 = rate over c_t, with c_t fixed per task and identical for A and B | counts scale with what C planted; unplanted defects in the numerator would let recall exceed 1 | comparable tasks; unplanted discoveries remain reported; null tasks drop out of O1 and O3 |
| D-3 | no defect classes | classes recorded, diagnostic only; at most ½ of planted defects in any one class | to diagnose without the composition deciding the verdict | none on the primary verdicts |
| D-4 | builder "Chad Holland or an outside contributor"; evaluator "the task author, or another person"; design flaw 2: otherwise the study is "self-tested and is reported that way" | C and P are distinct humans; Chad, Claude and the designers are excluded; otherwise **UNRUN**, not a self-tested run | the designer of B, or a co-author of the method, must not set or score the test | the study may not run; if it runs, the ground truth is separated from judgment |
| D-5 | H0: at most 3 of 18 with \|d\| > noise; no minimum N | N_o ≥ 12 for every verdict; ⌊N_o/6⌋; resolution guard | ⌊3N/18⌋ is pathological at small N, and noise could force equivalence | more "insufficient evidence"; the tolerance equals Stage 1's at N_o = 18 |
| D-6 | at least 4 null tasks | exactly 4; m_t ≥ 1 and c_t ≥ 1 on every non-null task | the null count would otherwise set N_O1 and N_O3 | removes a choice from C |
| D-7 | no reliability check | R on a seeded 6-task subset; agreement with no threshold; verdict-robustness rule | the scorer's judgments are the measurement | scorer-dependent verdicts are downgraded; otherwise NOT TESTED |
| D-8 | executors receive their condition's method text (A: A-D1–A-D10, A-O1, A-O3–A-O7 and `prereg.py`; B: the frozen texts) | both also receive the identical output appendix (§3) | extraction needs a common, condition-neutral claim format | the study tests **method + standardized reporting format**; an appendix that resembles one method's habits is a disclosed limitation (§11) |
| D-9 | "Stage 2 (a separate commit, before any execution)" | two commits, both before execution: 2a (specification, frozen texts, code, seeds) before construction, and 2b (seal hash, per-task records, subset) after construction | the thresholds must be frozen before C builds, so neither can be tuned to the other | the same guarantee, with stricter ordering |
| D-10 | "the median d exceeds the noise" | \|median d\| > η_o, with the sign agreeing with the sign-test majority | read literally, A could never win, against Stage 1's own outcome "A performed better"; this is an interpretation that restores symmetry | removes a hidden direction that favoured B |
| D-11 | "If the evaluation is done by a model, it is reported as same-vendor, not independent" | model-based scoring is excluded; C, P and R are human, with no AI delegation and declared tools | AI-mediated scoring would let the studied model family judge itself | the study is more likely to be UNRUN; there is no AI-judged path |
| D-12 | "a crashed session is re-run once" (crash undefined) | crash = no appendix files, or an error exit; every attempt preserved; raw outputs hashed before extraction | an undefined crash left a re-run choice with the operator | no discretionary re-runs |

---

## 11. Limitations (preserved)

**Shared format.** The experiment tests **"method + standardized reporting format"**, not either
methodology in isolation. The appendix's claim/status/evidence structure may be closer to one
condition's habits, and this is not corrected for.

**Population.** Even a statistically significant directional result would be evidence only under:
- the frozen task population built by this constructor;
- the pinned executor model;
- the frozen method texts;
- the frozen scoring protocol and rubric;
- the shared reporting format.

It is **not** evidence of general methodological superiority, of how human researchers would perform,
or of real-world research quality.

**Other disclosed limitations, not solved:**
- Chad Holland selects C, P and R.
- Extraction is done by the same vendor's model.
- The method vocabulary may survive neutralization.
- η pools tasks of different resolution (scale mixing), and O4's η can only be 0, ½ or 1, flipping
  between 11, 12 and 13 disagreeing pairs out of 24.
- O2 counts are not normalized for the number of claims made, which penalizes the condition that makes
  more claims.
- This specification is drafted by the drafter of B and has had no outside review.

**Allowed conclusion wording** is limited to the verdicts in §6.3 and the labels in §6.6. There is no
overall score, ranking or winner.

---

## 12. Revision 4 self-audit

| # | Check | Result | Basis |
|---|---|---|---|
| 1 | Every item Stage 1 requires Stage 2 to register is present | **PASS** | sealed hash (§2.2); per-task records (§2.2); pinned model (§9); session cap (§9); seed (§9); extraction rules (§4); O2 rubric (§5); frozen skill texts (§2.1); cost threshold (§7). The values that only exist at commit time (model ID, seeds, sealed hash) have mechanical slots, not open choices |
| 2 | B1–B7 closed | **PASS** | B1 §6.3, D-10 · B2 §5 O1/O3, D-2 · B3 §3–§5 · B4 §7 · B5 §5 O4 · B6 §2.4, D-12 · B7 §1, D-11 |
| 3 | No new researcher degree of freedom | **ISSUE (disclosed, not a defect)** | Writing B3 required design choices: the appendix schema, the S0–S3 mapping, the E0–E2 levels, U1–U7, the neutralized term list, and the definition of a procedural artifact. All are fixed before execution, so none can respond to data. But the drafter of B made them, so they are design-time choices without independent review. Two judgments remain with P: duplicate marking in O2 and the domain judgment in U2. Both are disclosed and checked by R |
| 4 | A directional verdict can favour A or B | **PASS** | §6.2 and §6.3 are mirror images; worked example E9 (revision 3) and the O4 enumeration both produce A-wins |
| 5 | O1 cannot exceed 1 | **PASS** | the numerator counts planted defects only, and the denominator is m_t |
| 6 | c_t identical across conditions | **PASS** | §5 O3: one number per task, from the sealed and confirmed counterexamples of all sessions, fixed before analysis |
| 7 | O4 has an unambiguous unit and missing-replicate rule | **PASS** | the session is the unit; every S3/S2 command must reproduce; zero commands scores 0; a missing replicate falls under §6.1 and §6.4 |
| 8 | Crash and re-run handling is mechanical and keeps every attempt | **PASS** | §2.4 |
| 9 | O2 and extraction fully specified before execution | **PASS, with one AMBIGUITY** | everything is fixed in Stage 2a. The S3 fallback for "unhedged declarative" depends on the hedge-word list in §4 rule 4; words outside the list default to S3. That is mechanical but could be argued |
| 10 | Cost prediction registered without becoming a performance prediction | **PASS** | §7 is about cost only and excluded from O1–O5; the O1–O5 prediction stays NONE |
| 11 | Independence cannot be satisfied by AI-mediated scoring | **PASS** | §1: human only, no delegation to any vendor's model, declared tools, delegation voids the output; D-11 |
| 12 | Stage 1 unchanged | **PASS** | no repository file edited; Stage 1 is referenced by commit and md5, and every change is listed in §10 |
| 13 | Nothing run, no empirical result | **PASS** | only deterministic arithmetic on illustrative inputs; no task, session or score exists |

**Where the study could still steer itself:**
- the selection of C, P and R;
- same-vendor extraction;
- this specification, including the newly written rubric, being Claude-drafted and not independently
  reviewed.

All three are disclosed. None is solved by this revision.

**Status: READY FOR HUMAN REVIEW.** This is not "ready to freeze". The methodology comparison has
demonstrated nothing.
