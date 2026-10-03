# SWAY Amendment 3: one canonical method, triggered controls, one vocabulary map — registration

**Status:** REGISTERED 2026-10-03, in a commit of its own. Nothing described here is built yet. This
file is not edited after this commit. Results go in `METHOD_SWAY_AMENDMENT_3_RESULTS.md`.

**Adoption:** delegated. Chad Holland wrote, on 2026-10-03: "Proceed and adopt a new methodology as
you see fit modify whatever you think is best for my goals." The amendment is adopted when the pull
request that builds it merges with its migration checks (P8) recorded. It is **not validated** as
better than what it replaces: P6 and P7 below are open.

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
- **AI participation:**
  - Claude (Anthropic, Opus 5.5) audited the method, wrote the design review, and drafted this
    amendment and every file it builds.
  - ChatGPT (OpenAI; model version not recorded) supplied ten architecture suggestions (C1–C10),
    preserved verbatim with Chad Holland's directions (A1–A7) in
    `methodology/record/external/2026-10-03_chad-holland_chatgpt_refactoring-plan.txt`
    (sha256 `50928b984e791c9a16a45dace0d9149072c3c9a4e703cc7c1af560961206ef86`). The `.txt` copy is
    added with the build; its hash is stated here first.
- **Human validation:** direction only. Chad Holland read summaries of the audit and the design review,
  not this text line by line.
- **Human editing/curation:** none before adoption.
- **Responsibility:** Chad Holland.
- **Self-tested.** The audit, its 12-of-12 coverage check and the migration checks below were designed
  by the same AI that drafted the rules.

## What broke (failures lead)

| # | Finding | Where |
|---|---|---|
| F1 | **Contradiction.** The outcome of a registered prediction is "HELD and FAILED" in Amendment 1 item 7, and in the veritas-companion and veritas-holo records. It is HELD/REFUTED in the prereg-research-workflow skill and in the sovereign-veritas, principia and evidence-ledger harnesses | `METHOD_SWAY_AMENDMENT_1.md` item 7; for example veritas-holo `experiments/E004_group_state/RESULTS.md`, sovereign-veritas `tools/recovery_admissibility.py` |
| F2 | **Contradiction.** The experiment-first skill (md5 `e5fa5a566fa9055f6293926c6db90dfc`, step 9) requires exactly one of eight status words per claim. The Amendment 2 draft rejected that list because it conflicts with Amendment 1 items 6 and 8 | skill step 9; Amendment 2 draft, "Not adopted" |
| F3 | **Contradiction.** SWAY's elevator requires E ≥ 20 for every promotion, but almost every promoted result in the estate is deterministic, where an e-value has no null distribution. The requirement is silently skipped. Separately, the methodology-comparison Stage 1 (`aef769e`, a registration under SWAY) uses a fixed-horizon exact sign test with p ≤ 0.05, which E ≥ 20 as written does not allow | `METHOD_SWAY.md` "Elevator"; `docs/METHODOLOGY_COMPARISON_PREREG.md` on branch `methodology-comparison-registration` |
| F4 | **Duplication.** Across the 7 method texts listed under "The sources" below: <br>• the AI-provenance chain is written in 3 (both skills and the Amendment 2 draft), and again, in other words, in Chad Holland's saved preferences and in the sovereign-veritas `AI_PROVENANCE.md` draft; <br>• anti-vacuity in 7; <br>• self-validation in 3; <br>• the evidence ladder in 3; <br>• "failures lead" in 5 | the 7 sources; the counting script is in the appendix |
| F5 | **Overlap.** Two skills restate one loop: 8 of experiment-first's 10 steps appear in prereg-research-workflow | the two skills |
| F6 | **Unused machinery.** Across 11 local clones of the estate's repositories: `FORKS.md` has 1 entry (F-001, the Amendment 1 review itself). The e-value machinery (`scripts/eprocess.py`, E ≥ 20) is used by 0 experiments or notes. **Correction to the 2026-10-03 audit:** it reported "1 experiment (veritas-companion C002)". That was a false match: the word "single-valued" contains "e-value". | commands in the appendix |
| F7 | **Vocabulary sprawl.** There are 8 label sets with no single map: note status; prediction outcome (Amendment 1 item 7); the validity axes; replication levels; the eight-word list; lineage status; claim status in code (sovereign-veritas `epistemic.py`, `ebll/evaluator.py`); and the repository summary in `PROVENANCE.md`. The audit counted 7 and missed the last one. Also: the note-status list has 5 labels in NOTE_TEMPLATE.md and README.md but 7 in CLAUDE.md, and README.md says EBLL outcomes use "the SWAY Amendment 1 vocabulary" while listing SUPPORTED/REFUTED, which are claim statuses, not Amendment 1 outcomes | NOTE_TEMPLATE.md, CLAUDE.md, README.md, PROVENANCE.md |
| F8 | **Contradiction.** SWAY's build elevator requires the gate to run on the device for any "working" claim. The prereg-research-workflow skill, and sovereign-veritas practice, instead label results that were not run on the device as NOT VALIDATED on the S25 | `METHOD_SWAY.md` "Build elevator"; skill §7 |
| F9 | **A registered method prediction expired unscored.** Amendment 1's P5 counts failures over "the next 5 registrations across the estate". By commit subject, in the 11 local clones, those were C008 (veritas-companion `53fee1c`), EL-007 (evidence-ledger `d2da7b8`), XB-1 (sovereign-veritas `7a8351e`), XB-2 (sovereign-veritas `4a4d02a`) and note064 (principia `99e666d`). The window closed on 2026-10-02 at 13:28 CT. Nobody scored P5, and no rule says when predictions about the method are scored | `METHOD_SWAY_AMENDMENT_1.md` P5 |
| F10 | **Cost.** The methodology-comparison Stage 2 specification grew to about the length of the method it tests: 5,224 words in revision 4, against 7,687 words for the 7 method texts (`wc -w`). Its status is UNRUN | revision 4, kept in the session scratchpad |

## Decisions

| ID | Decision | Reason |
|---|---|---|
| D1 | The canonical prediction outcome is **REFUTED**. FAILED, where it appears in records before this amendment as the outcome of a registered prediction, is read as REFUTED. Those records are not edited | FAILED collides with outputs from a different dimension in the same repositories: `GATE: FAIL`, `GATE FAILED`, pytest `FAILED`, `SOME SUITES FAILED`, `execution_status = FAILED` |
| D2 | The eight-word status list is retired as a single-status scheme. Each of its words is mapped to the dimension it belongs to, in METHOD.md's vocabulary map. The skill's frozen text is kept as record | F2. One word per claim cannot carry three validity axes and a replication level |
| D3 | **The e-value requirement is scoped:** <br>• **Deterministic claims** (same input → same output, no sampling): the promotion evidence is a registered prediction, a pinned outcome, a sabotage control and a run after registration. No e-value is computed. <br>• **Sample-based claims:** a test whose error guarantee holds under the stopping rule actually used. That is a registered fixed-horizon test (exact where possible) when the sample size and analysis are fixed in advance and nobody looks early, or an anytime-valid e-process with E ≥ 20 (α = 0.05) when data are inspected sequentially or stopping depends on the data | SWAY's own stated reason for e-values is optional stopping. This also makes Stage 1's fixed-horizon sign test conform |
| D4 | A build is claimed working only in the environments where its gate ran. Every other environment, including the S25, is NOT VALIDATED there. A claim about the device needs a run on the device | F8. It keeps SWAY's requirement for device claims and matches the labelling practice |
| D5 | Predictions about the method are scored when their window closes, and the scoring is appended to the amendment's results. Amendment 1's P5 is overdue. It is this amendment's door | F9 |
| D6 | **Force levels** with consequences: <br>• **MUST:** breaking it blocks promotion and is reported first as a deviation. <br>• **SHOULD:** departing from it needs one written reason. <br>• **MAY:** an optional technique. <br>Weakening a MUST, or retiring a rule, follows the adoption rule (a recorded reason, in a dated amendment) | ChatGPT C2, with the guard from the design review: the grading must not become a quiet way to weaken a rule |
| D7 | **Triggered controls, on unless answered.** Every registration carries a trigger table. Each row is answered yes, or no with a reason. A blank row counts as yes. A missed trigger found later is a deviation | ChatGPT C5, with the discretion problem closed. This generalizes the evidence ladder's existing "cover each row or state why skipped" |
| D8 | Record edits (documentation, attribution, lineage, corrections) are not experiments and need no registration. They stay append-only and carry provenance | The audit's F9. This writes down existing practice |
| D9 | **Single source.** Each normative rule is defined once, under an ID, in `METHOD.md`, `WORKFLOW.md` or `CONTROLS.md`. Other files cite the ID or carry a verbatim excerpt that `scripts/method_lint.py` checks. Excerpts are allowed where agents read, for example `CLAUDE.md` | F4; ChatGPT C1 and C8. Agents rarely follow links, so a pointer alone would weaken protection |
| D10 | **Unused machinery is kept and labelled:** <br>• the discovery loop: AVAILABLE — NOT USED SINCE ADOPTION; <br>• the fork ledger: used only for method amendments (F-001, and F-002 for this amendment), never for a research claim; <br>• the e-value process: AVAILABLE — NOT USED SINCE ADOPTION (0 uses). <br>The labels are updated when use is recorded | F6; Chad Holland's direction A5 |
| D11 | The Amendment 2 draft, never adopted separately, has its items 10–13 adopted through this amendment. Its text is committed as record, and its P6 is carried forward unchanged | F4; it avoids a second adoption path for the same rules |
| D12 | **Not adopted:** <br>• ChatGPT C3 (proportionality as a free principle): it is replaced by D7. Researcher judgment before the failure modes are known is the least reliable input. <br>• C6 (a separate decision tree): it would be a third copy of the loop. <br>• C10's ratio: it cannot be measured. <br>• A "high-consequence" trigger: it is a door, because no incident shows it yet. <br>**Adopted with guards:** C1, C2, C4 (reordered, so the attack is designed at registration), C5, C7 (each rule keeps a citation to its incident or source), C8, C9 (minimal) | the design review of 2026-10-03 |
| D13 | The methodology comparison is parked at Stage 2 revision 4. It is not frozen and not committed as a Stage 2 registration, and its status is UNRUN — independent task construction and scoring not available. Its Condition B texts stay pinned by md5, with copies in `methodology/record/skills/`. After this amendment, Condition B is a superseded method; that is recorded on its branch | Chad Holland's direction A7; F10 |

## What is built (design, frozen here)

| File | Role |
|---|---|
| `METHOD.md` | Canonical. The core rules (M-IDs) with force and sources; the trigger table; the vocabulary map; the change-control rule |
| `WORKFLOW.md` | Canonical for the procedure (W-IDs): question → register → build → run → attack → record → review → close; record edits |
| `CONTROLS.md` | Canonical for the triggered controls (C-IDs), the AVAILABLE — NOT USED machinery, and pointers to the doors |
| `methodology/RULE_INVENTORY.md` | Every normative item in the seven sources below, with exactly one disposition: a rule ID, a vocabulary entry, superseded by a decision, a repository or operations rule, a door, or record |
| `scripts/method_lint.py` | Stdlib only. Checks that each ID is defined once, in a canonical file; that every trigger points to a defined control; that the excerpts are verbatim; that every inventory home resolves; that every defined rule has at least one inventory source; that the record copies match their md5s; and that no deprecated outcome token appears in canonical text. Modes: `--coverage` re-extracts the sources; `--selftest` plants every defect class; `--sabotage` must exit 1 |
| `methodology/record/` | Verbatim copies, by md5, of the two skills and of the external plan text |
| `METHOD_SWAY_AMENDMENT_2.md` | The draft, verbatim, with a dated status header |
| Notices | A dated pointer at the top of `METHOD_SWAY.md` and `METHOD_SWAY_AMENDMENT_1.md`. `CLAUDE.md` "The method (binding)" becomes a checked excerpt of METHOD.md. `NOTE_TEMPLATE.md` gains the trigger table. `README.md` points to METHOD.md and corrects the EBLL vocabulary sentence |
| `FORKS.md` | Append F-002 (this audit) |
| CI | The lint, its self-test and its sabotage control, added to `verify-all-notes` |

**Not changed:**
- Stage 1;
- every research note, result, record and external text;
- `NOTES_INDEX.md`;
- `scripts/eprocess.py`;
- other repositories. None of them has a CLAUDE.md, and their mentions of SWAY are records. veritas-companion's `.github/copilot-instructions.md` says "FAILED or REFUTED", which is consistent with D1, so it is left alone.

**The sources inventoried, with feasibility counts.** These were printed before this registration by
a scratch copy of the extraction rule. The rule takes list items, numbered items, checklist items, and
table rows other than header and separator rows; YAML front matter and fenced code are skipped.

| Source | Identity | Items |
|---|---|---|
| `METHOD_SWAY.md` | `4c7518a`, md5 `aae4d54fa2c92e6869085884b70c1960` | 61 |
| `METHOD_SWAY_AMENDMENT_1.md` | `4c7518a`, md5 `a051e7da4c4564445d1174db0be59b07` | 22 |
| Amendment 2 draft | md5 `261ffe7597c093b0b6b92296b5fa1e11` | 37 |
| `NOTE_TEMPLATE.md` | `4c7518a`, md5 `def8d93cf496a21a32efe7cc047f27c4` | 3 |
| `CLAUDE.md` | `4c7518a`, md5 `465206e261de1c6e19218b7072b693da` | 43 |
| experiment-first skill | md5 `e5fa5a566fa9055f6293926c6db90dfc` | 14 |
| prereg-research-workflow skill | md5 `0992bc29efb422d6eff751c972a0ef46` | 52 |
| **Total** | | **232** |

Normative prose that is not a list item, such as NOTE_TEMPLATE's paragraphs and SWAY's "Forbidden
here", is inventoried by hand. The coverage check cannot see it (see the limits below).

## Trigger table for this amendment (its own D7, applied to itself)

| Trigger | Answer |
|---|---|
| Feasibility: does the design depend on counts in its inputs? | **Yes.** The counts are above, printed before registration |
| Noise: can an arm give different outputs for the same input? | No. Extraction and lint are deterministic |
| Statistical: is a rate or difference estimated from samples? | No |
| Evidence: is the question whether a rule handles its evidence? | No |
| Independence: does a claim say independent or replicated? | No. Everything here is labelled self-tested |
| External: is outside material used? | **Yes.** ChatGPT's suggestions and Chad Holland's directions are preserved verbatim with sha256 |
| Device: is there a claim about a device or platform? | No. The lint runs in the container and in CI; it is NOT VALIDATED on the S25 |
| Build: does the artifact return a verdict? | **Yes.** `method_lint.py`: missing input is a failure, never a pass; every violation fails; the sabotage control must exit 1 |
| Exploration: did anything run before registration produce outputs on the registered cases? | **Yes.** The audit, its counts and the feasibility counts above were produced before this commit. That is logged as F-002, and P8a re-derives the counts with the committed code |
| Methodology comparison? | No. This amendment changes the method the comparison would test (D13) |

## Simplest rival

Fix the three contradictions in place and leave the seven documents as they are.
**Not run as an arm:** within this change there is no outcome measure that applies to both. That is a
recorded deviation from Amendment 1 item 5, and it is kept. The consequence: P7 cannot tell
consolidation apart from this rival, so a P7 that holds is weak evidence.

## Predictions

**P8, migration integrity, scored in the results of the pull request that builds this:**
- **P8a.** The committed extractor (`method_lint.py --coverage`) prints the same per-source counts as
  above (61, 22, 37, 3, 43, 14, 52; total 232). Every extracted item has exactly one inventory row,
  matched by source, line and text hash. Unplaced items: 0. Any other count refutes P8a.
- **P8b.** `python scripts/method_lint.py` exits 0 on the migrated tree.
- **P8c.** `python scripts/method_lint.py --selftest` detects every planted defect class and exits 0.
  The classes are: a duplicate definition; a definition outside the canonical files; excerpt drift; an
  inventory home that resolves to nothing; a defined rule with no inventory source; a trigger pointing
  to an undefined control; a deprecated outcome token in canonical text; and a record copy whose md5
  changed. `--sabotage` exits 1.
- **P8d.** The existing checks are unchanged:
  - `python sovereign_core/test_sovereign.py` gives 33 passed;
  - `make synthetic` exits 0;
  - `python scripts/make_index.py` changes nothing in `NOTES_INDEX.md` except its date line;
  - CI `verify-all-notes` is green on the pull request.

**P7, simplification, OPEN.** Over the next 5 registrations across the estate after the merge, no
defect is found that only removed or merged text would have caught. "Removed or merged" means an
inventory row whose disposition is not a rule ID. One such defect refutes P7, and the refutation is
kept.

**P6, carried unchanged from the Amendment 2 draft, OPEN.** Over the next 5 registrations that involve
an AI-designed test or a question about evidence, count two kinds of failure:
- an AI-produced result described as independent without provenance showing it;
- an evidence rule tested without stale, derived or replayed conditions and without a stated reason.

Prediction: 0. One or more refutes the amendment for that purpose.

**Scoring (D5):** the P6 and P7 windows open at the merge commit. Each is scored when its fifth
registration lands, and the scoring is appended to the results file. Scoring by the AI that drafted
this amendment is labelled self-tested.

## Limits

- The coverage check sees list items and table rows only. Normative prose was read and inventoried by
  hand, and a missed prose rule would not be detected.
- The lint detects duplicate IDs and drifting excerpts. It does not detect a rule restated in different
  words without an ID.
- The counts in F6 and F9 come from 11 local clones, and from commit subjects in the case of F9.
  Repositories that are not cloned locally are not counted.
- Every check here is self-tested (see provenance).

## Next unrun test

Score Amendment 1's P5 on its closed window (C008, EL-007, XB-1, XB-2, note064). Count the five failure
classes it names: infeasible data, an unreachable guard, a float threshold, a bound inside noise, and a
missing rival. The prediction was at most 1.

## Appendix: how the counts were taken

```
grep -c '^20[0-9][0-9]-' FORKS.md                          # 1 (F-001)
git grep -l -i -F "e-value"  (each of the 11 repositories)  # METHOD_SWAY.md only, apart from false
                                                            # matches: "single-valued", "match-the-value"
git grep -l -F "eprocess"                                   # METHOD_SWAY.md only, apart from "preprocessing"
git log --all --since="2026-09-30 09:32 -0500" --until="2026-10-02 13:30 -0500" \
    --format="%ad|%h|%s" | grep -i -E "regist|prereg|predict|freeze|frozen"   # the P5 window
```

F4: each source is whitespace-normalized, then searched case-insensitively. A source counts once if it
matches:
- **provenance chain:** `AI participation → human validation`
- **anti-vacuity:** `anti-vacuity|vacuity guard|can return null|sabotage`
- **self-validation:** `vouch for itself|never independent validation|self-tested\*\*|labelled \*\*self-tested|record it as \*\*self-tested|Label it self-tested`
- **ladder:** `fresh → stale`
- **failures lead:** `Failures lead the document|failures lead|What could have gone wrong, first`

Every note ends with a door. This one does too.
