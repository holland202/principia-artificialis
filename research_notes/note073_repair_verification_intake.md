# Note #073 — Passing the tests is not removing the defect: a repair-verification case study and research intake

**Status:** Speculative — research intake. One engineering case study (SELF-TESTED, n = 1) and a literature intake.
No experiment for this note has been registered or run. AVF-001 below is a proposed question, not a registered study.
**Theme:** Verification / Repair validation / Anti-vacuity
**Author:** Claude (Anthropic, Opus 5.5), at Chad Edward Holland's direction (2026-11-03). Review level: direction
only. ChatGPT (OpenAI) wrote the handoff that asked for this intake and the earlier research scan it checks; its
suggestions are evaluated here, not adopted wholesale.
**Builds on:** [[note052_verification_that_cannot_fail]] (checks that cannot fail),
[[note059_mutation_score_denominator]] (a mutation score needs its denominator),
[[note044_circularity_test]] (a benchmark that validates itself).
**Method:** [METHOD.md](../METHOD.md) at commit `46034aa`.
**Canonical source for the case study:** [holland202/sovereign-veritas](https://github.com/holland202/sovereign-veritas).
This note links to that evidence and copies none of it. Implementation, tests, raw output and corrections stay there.

## What went wrong, first

- **The case study's first result is a security failure, and it stays the headline.** SEC-004's registered probe
  scored `SECURITY_FAIL` on 2026-10-11: a completion that had passed its token check overwrote a fresh reservation
  ([SEC004_RESULTS.md](https://github.com/holland202/sovereign-veritas/blob/main/docs/SEC004_RESULTS.md)). The later
  fix does not replace that result.
- **The verdict went unrecorded for about 22 days.** Checked from sources on 2026-11-03:
  - the workflow run (id 38160250976, commit `8338e83`) started 2026-10-11 17:34:58 UTC and finished 17:46:27 UTC,
    conclusion `failure` (GitHub Actions API);
  - the same day, the Sovereign Veritas research log and PA note 071 recorded only that the SEC-004 CI had *failed*;
  - the scored verdict `SECURITY_FAIL` first appears in a checked repository in commit `7e40c12`
    (2026-11-02 15:40:56 UTC), 21.9 days after the run finished.

  "Checked" means the Sovereign Veritas and Principia repositories. Records outside them were not searched.
  The method record [2026-11-03_SV_SEC004_LATE_RECORDING](../methodology/record/2026-11-03_SV_SEC004_LATE_RECORDING.md)
  covers what this means for the method.
- **The fix was predicted to be confirmable by re-running the old probe. That prediction was wrong.** The SEC-004
  probe is pinned to the vulnerable source, so on the fixed module it reports `INCONCLUSIVE_SOURCE_CHANGED`.
- **Everything about the fix is self-tested.** Claude registered, built, ran and judged SEC-005. CI across 12 legs
  is the same code judged on more machines, not an independent check. Independent validation: not established.
- **"Precise but Uncoupled" is excluded.** ChatGPT's earlier research scan cited it as arXiv 2607.15388. Three
  searches on 2026-11-03 did not find it, and the arXiv page could not be fetched from this session. It stays out
  until it is independently verified.

## The claim

A repair can make the existing tests pass without removing the defect. Telling the two apart needs evidence the
existing suite cannot give: at least (a) the original failure still reproducing on the unfixed code, and (b) an arm
with the fix removed that fails again under the same instrument. Those two establish that the instrument is
sensitive to the known failure, not that the repaired implementation is correct in general: that needs evaluation
against an independently specified property or oracle. This note asks how often AI-assisted repair and
verification, as practised in this estate, would mistake the first kind of repair for the second (AVF-001 below).
The claim is precisely wrong if, on a registered set of repairs, "existing suite passes" and "defect removed by the
stronger criterion" never disagree.

## Epistemic status (read first)

- **Established, not ours:** fixes that pass the tests without being correct are a known problem in automated
  program repair (Smith et al. 2015, below). AI agents passing visible tests while failing held-out ones (SpecBench),
  and AI-written checks that copy the implementation instead of the specification (SpecGuardBench, *Oracles That
  Cannot Fail*), are reported in recent work.
- **Ours, and not tested:** the AVF-001 question as applied to this estate's own AI-assisted fixes, and the protocol
  in the claim (an old-code reproduction plus a fix-removed arm). **Novelty is not established, and is probably
  small.** A prior-art search for that protocol has not been done.
- **The case study is one case.** It illustrates the protocol. It supports no rate, trend or general claim.

## Case study: SEC-004 → SEC-005 (Sovereign Veritas, engineering evidence)

| Step | What happened | Evidence label | Source |
|---|---|---|---|
| SEC-004 registered | Race between a holder's token check and its write, in `FileReservations` | — | `docs/SEC004_PREREG.md` |
| SEC-004 run, 2026-10-11 | `SECURITY_FAIL`: the stale completion replaced the fresh reservation (P2 held) | SELF-TESTED (CI) | `docs/SEC004_RESULTS.md`, PR #76 |
| Existing test suite on unfixed code | On `7e40c12`, with the race present, the 10 `test` matrix legs that ran all passed. The other 2 (macOS, Python 3.12 and 3.14) were cancelled before running because no runner was assigned, so they give no result either way | CI | PR #76 checks |
| Re-run on unfixed code, 2026-11-02 and 2026-11-03 | `SECURITY_FAIL` again at `7e40c12` (the 2026-11-03 re-run was a check and was not saved to a file) | SELF-TESTED | `results/sec005/run1/sec004_baseline_7e40c12.txt` |
| SEC-005 registered before any code | Per-key OS lock across reserve, move and release | — | `docs/SEC005_PREREG.md` (`31d667d`) |
| SEC-005 run | `FIXED_IN_TESTED_SCHEDULES`, 6 of 6 as registered. The same run's no-lock arm reproduces the overwrite; `--sabotage` flips the verdict | SELF-TESTED | `docs/SEC005_RESULTS.md`, PR #98 |
| CI | 12 of 12 matrix legs reproduce the pinned digest | SELF-TESTED (CI) | PR #98 |
| Old probe on fixed code | `INCONCLUSIVE_SOURCE_CHANGED`, as registered (P8) | SELF-TESTED | `results/sec005/run1/sec004_on_fixed.txt` |
| Independent challenge | Not yet designed or run. ChatGPT is to design the first one | NOT RUN | — |

What the case shows: in this one case, neither the existing test suite nor the old probe could confirm the fix.
The suite passed on every leg that ran (10 of 10; 2 legs never ran) with the race present (PR #76), and the old probe refused to run on the changed code. Confirming the fix against the known failure needed a new instrument that reuses the
old schedule and keeps an arm that still fails without the fix. That new instrument, together with the old-code
reproduction, shows the test is sensitive to the known failure. It does not show the repaired implementation is
correct in general, which needs evaluation against an independently specified property or oracle. What it does not show: that the fix is correct
outside the forced schedules, on Android, on network filesystems, or under independent attack. A Windows
error-handling issue in the lock loop has been identified from reading the source and is not reproduced.

## Known mathematics / prior art (verified 2026-11-03)

| Work | Verified | What it reports | Licence | Bearing on AVF-001 |
|---|---|---|---|---|
| Smith, Barr, Le Goues, Brun, *Is the cure worse than the disease? Overfitting in automated program repair*, ESEC/FSE 2015 | Yes (author PDF, bibliography records) | Automatically generated fixes can pass the test suite they were made for and still be wrong | not checked | Direct: the established form of the question |
| Zhao, Srikanth, Wu, Jiang, *SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents*, arXiv 2605.21384 (v2, 2026-09-09) | Yes (arXiv page) | Visible-test vs held-out-test gap as a measure of reward hacking; 30 tasks; the gap grows about 28 points per tenfold code size | not stated | Direct: passing visible tests is not meeting the specification |
| Zhong, Chen, Fang, Zhang, Tian, Briand, Yu, He, *SpecGuardBench: Can Coding Agents Construct Reliable Validation Harnesses from Natural Language Specifications?*, arXiv 2610.16870 (v1, 2026-10-12) | Yes (arXiv page; repository linked from the paper) | 291 tasks from 13 repositories; no agent's harness faithful on more than 63% of tasks; checks "mirror the reference implementation" | Repository MIT; paper licence not shown | Direct: AI-written checks follow the code, not the specification |
| Canedo, *Oracles That Cannot Fail: Anchoring and the Expectation That Moves With the Fault*, arXiv 2608.17214 | Yes (arXiv PDF; submission date not stated in the text read) | Oracles whose expected value comes from the code under test miss faults; 366 mutants, one system, one author; data on Zenodo | not stated | Direct, and overlaps [[note052_verification_that_cannot_fail]] |
| Xie et al., *WebAnything: From the Wild Web to Scalable Agent Environments*, arXiv 2610.37786 (v1, 2026-10-27) | Yes (arXiv page) | Rebuilds web environments from real URLs, with an independent verifier that checks candidates and guides repair | CC BY 4.0 | Indirect: a verifier inside a repair loop |
| Ghosh et al. (102 authors), *AILuminate: Introducing v1.0 of the AI Risk and Reliability Benchmark from MLCommons*, arXiv 2503.05731 (v2, 2025-04-18) | Yes (arXiv page; MLCommons technical-users page) | 12 hazard categories; 12,000 public practice prompts (1,200 of them the demo set) and 12,000 hidden official prompts | Code Apache-2.0; demo prompts CC BY 4.0; practice prompts under MLCommons' own prompt licence | Indirect: a hidden held-out set keeps the tested system from fitting the test (C-HOLDOUT) |

Seen by title only and **not verified**: *SWE-Mutation* (arXiv 2605.22175); *Do Coverage and Mutation Scores of
LLM-Generated Test Suites Correlate with Their Effectiveness?* (arXiv 2607.22880); *Is the Cure Still Worse Than the
Disease?* (arXiv 2511.16858). They are listed so the next reader can check them, not cited as support.

## The experiment (or: what one would look like) — AVF-001, proposed, not registered

**Question.** Across a fixed set of AI-assisted repairs in this estate, how often does "the existing suite passes"
disagree with "the defect is removed", where removal means the registered failure reproduces on the old code and a
fix-removed arm fails again under the same instrument?

**Candidate units:** repairs that already have a registered failing result, for example SEC-004 → SEC-005, the SML
TypeScript-port fixes F1–F8, and SMP-002 in vacuity_lint. The list must be fixed before any scoring (C-HOLDOUT).

**Candidate predictions (not frozen):**
- P1: at least one unit where the existing suite passes on the unfixed code (the suite cannot see the defect).
- P2: for every unit, the fix-removed arm fails under the strong criterion; a unit where it does not is evidence the
  instrument cannot see the defect.
- P3 (anti-vacuity): a planted no-op "fix" passes the existing suite and is rejected by the strong criterion.

**Independence:** the attack cases and expected results should come from someone who did not write the fixes. In
this estate that rules out Claude for repairs Claude wrote.

## Reference code

None. No experiment exists for this note. The case study's code is in Sovereign Veritas
(`tools/sec004_release_race_probe.py`, `tools/sec005_lock_probe.py`).

## Triggered controls (M16)

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | Yes, for AVF-001: count qualifying repairs before registering. Nothing counted yet |
| Noise | C-NOISE | Yes, for AVF-001: concurrency probes are timing-dependent. SEC-005 handles it with forced schedules; other units need their own answer |
| Statistics | C-STAT | Yes, if AVF-001 states a disagreement rate. None stated here |
| Evidence | C-EVID | No: the note is about test adequacy, not a system's handling of its evidence |
| Independence | C-INDEP | Yes: the case study is self-tested and labelled so. CI legs and multiple AI reviews are not counted as independent |
| External | C-EXT | Yes: six external works cited, each checked against its primary page on 2026-11-03; one excluded as unverified |
| Device | C-DEVICE | Yes, for the case study: Linux, macOS and Windows on CI only. Android/Termux NOT RUN |
| Verdict code | C-BUILD | Yes, for the case study's probes (fail-closed, sabotage switches, in Sovereign Veritas). None in this note |
| Exploration | C-EXPLORE | Yes: AVF-001 came from looking at SEC-004/SEC-005 after the fact, so that case cannot be a confirmatory unit for it |
| Method comparison | C-METHCOMP | No: no methods are compared here |
| People's data | C-PRIVATE | No: no data about people |
| Design | C-DESIGN | Yes: a case study, n = 1. Its strongest claim is that this pattern happened once |
| Held-out | C-HOLDOUT | Yes, for AVF-001: the units must be fixed before scoring, and the case that suggested the question is excluded from confirmation |
| Generated inputs | C-SYNTH | No for this note. AVF-001 may need generated no-op fixes, which would then be looked at before use |

## Falsifiable next predictions (M15)

- **Unrun:** an independent challenge to SEC-005, designed by someone other than its author, finds no overwrite of a
  fresh reservation in the forced schedules, and its fix-removed arm reproduces SEC-004. Any overwrite refutes the
  SEC-005 claim within its stated scope.
- **Unrun:** AVF-001 P3. A no-op "fix" passes the existing Sovereign Veritas suite and is rejected by the
  old-code-reproduction plus fix-removed criterion.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) checked the sources and drafted this note → human validation: not
performed → human editing/curation: direction by Chad Edward Holland, 2026-11-03 → human responsibility: Chad Edward
Holland. Review level: direction only.*

## Intake addendum, 2026-11-04 (appended; the text above is unchanged)

Source surfaced by ChatGPT's 2026-11-04 research scan; checked by Claude (Anthropic, Opus 5.5) against its page the
same day.

| Work | Verified | What it reports | Licence | Bearing on AVF-001 |
|---|---|---|---|---|
| Gonzalez, Jagannath, Rajani, Habib (Collinear AI), *CWE-bench v2: More coverage, quality, and transparency*, Hugging Face blog, 2026-11-03 | Yes (blog page) | 100 public security-repair tasks covering 91 CWEs, each a Docker/Harbor task with a deterministic programmatic verifier. Per task the authors state they checked that the starter code fails, the reference fix passes, existing functionality still works, and that verifiers should fail the memorised upstream patch. A held-out set is kept at cwebench.com (evaluation on request). Reported: 11 models; best pass@1 67.8% | Dataset gated; licence not stated on the blog page, not checked on the dataset page | Direct: a public set of repairs with independent oracles and the negative controls AVF-001 asks for (unfixed code must fail, fix must pass, a known patch must not be what is graded) |

The reported scores are the authors' and were not reproduced. Running any task needs the gated dataset's terms
accepted first.
