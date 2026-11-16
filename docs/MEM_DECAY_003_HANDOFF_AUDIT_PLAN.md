# MEM-DECAY-003 handoff audit: public qualification only

Date: 2026-11-16. Design: deterministic code/design audit, not a model experiment.
Status at this commit: PLAN / NOT RUN. The anticipated defects below were identified
by reading public source. They are disclosed inspection-derived checks, not novel
scientific predictions. No evaluation family is being created or sealed here.

Reviewed source: PR #158 at `2a7ee5dc23ee594d54e76c19440843c2e8bdfb64`, merged in
`1ceb6aa323c8a9c4c2fcfc3f47617521dc790e86`. Follow METHOD.md, WORKFLOW.md and
CONTROLS.md at the merge commit. The original source/results will not be modified.

## Question and exact checks

Can the current scorer/schema support the requested held-out evaluation without
misclassifying valid answers, treating absent evidence as retained, or confusing
hidden history with observable evidence?

| ID | Anticipated observation on the real imported code | Benign/control case |
|---|---|---|
| A1 | The dev singleton's exact answer, rendered as `ANSWER: 6 p.m.`, is classified WRONG | `ANSWER: Room C` for Room C is CORRECT |
| A2 | A dev redundant task with no records retained is reported satisfied | The same function rejects a missing conjunctive requirement and accepts an actually retained redundant record |
| A3 | Two contradictory ANSWER lines are accepted according to the last line | A response without the required prefix is MALFORMED |
| A4 | Selecting `m001` identifies the correction in every one of the 40 public dev scenarios and ignores scrambled hidden fields | Rotate the visible IDs and update references: the same literal-ID rule no longer identifies corrections |
| A5 | An unchanged-history world and a correction-evicted world can have identical retained-record/question projections but different world-state keys | Restoring the correction makes the projection different |

A3 is an existing intentional parser convention (its unit test expects this),
flagged for prospective output-contract review rather than called an accidental
implementation regression. A5 uses the real selector projection plus a named
constructed decision-view encoder; the proposed inference prompt builder does
not exist yet. It is an identifiability counterexample, not measured model behavior.

The runner will print raw observations before interpretation and an exact canonical
SHA-256 digest. Exit zero means the inspection-derived audit observations were
reproduced. It does not mean the study is ready. A live-path sabotage substitutes a
classifier that accepts the exact punctuated gold answer; A1 must change and the
audit must exit one. The output will be pinned in a later commit.

## Scope, controls and provenance

No model execution; no old or new sealed dataset access; no inferential statistics.
Only public dev fixtures and public constructed counterexamples are used. The 40
dev repetitions are one template family, not independent evidence of a population
rate. This audit does not fix Claude's selector or production scorer.

M16: feasibility yes (fixed public fixtures/counts); noise no (deterministic);
statistics no (exact code properties, no population claim); evidence yes (absent,
contradictory and superseded records; freshness/replay outside this bounded scope);
independence yes (separate-vendor code review, not blind); external yes (retain
source excerpts/hashes and check literature against primary sources); device no
(no device-general claim); verdict code yes (live sabotage and exact counts);
exploration yes (source-informed checks logged in FORKS.md); methodology comparison
no; people's data no (synthetic public fixtures); design yes (audit/existence);
held-out no (no confirmation or tuned scientific effect); generated inputs yes
(named public samples reviewed by AI, human sample review pending).

Exposure: Codex has read the full draft, memdecay3.py, dev_family.py and
test_memdecay3.py. Any future evaluation authoring is therefore implementation-
informed, not blind to Claude's design. Claude can still remain unaware of future
evaluation contents under an explicit custody protocol.

AI participation: Codex / OpenAI GPT-6 Astra, reviewing Claude Opus 5.5's work.
Human validation: direction only. Human editing/curation: pending. Human
responsibility: Chad Holland. Audit code is self-tested; cross-vendor review does
not constitute independent empirical replication.

Door: after the semantic contract and study claim are corrected, freeze the
evaluation author/custodian roles, then author and seal untouched evaluation cases.
