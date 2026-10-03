# Rule inventory (Amendment 3, migration record)

This file maps **every normative item** in the seven texts the method was consolidated from to exactly
one disposition. It is how a reader can check that the consolidation silently dropped nothing. It is a
record: the rules themselves are defined in [METHOD.md](../METHOD.md), [WORKFLOW.md](../WORKFLOW.md)
and [CONTROLS.md](../CONTROLS.md).

**Rows:**
- every list item, numbered item, checklist item and table row in the sources, except header and
  separator rows, YAML front matter and fenced code. These rows have a line number, and
  `python scripts/method_lint.py --coverage` re-extracts them and checks this table;
- normative prose, read and added by hand. Its line column says `prose`, and the coverage check cannot
  see a prose rule that was missed;
- `A3-Dn` rows for rules that Amendment 3's decisions introduced.

**Hash:** the first 10 hex digits of the sha256 of the item's whitespace-normalized text.

**Dispositions:**

| Disposition | Meaning |
|---|---|
| RULE | now defined at the rule ID or IDs in the last column |
| VOCAB | now in METHOD.md's vocabulary map |
| SUPERSEDED | replaced by the Amendment 3 decision named (and the rule it points to) |
| REPO | a rule or fact belonging to one repository (it stays in that repository's CLAUDE.md or template) |
| OPS | an operating instruction for an agent or operator, not method (it stays in the skill or CLAUDE.md) |
| DOOR | a proposal, not adopted |
| RECORD | history, an incident, motivation, an example or an open prediction (it stays where it is) |

**Sources:**
- `METHOD_SWAY.md`, `METHOD_SWAY_AMENDMENT_1.md`, `NOTE_TEMPLATE.md` and `CLAUDE.md` at `4c7518a`;
- `record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md`;
- `record/skills/experiment-first.SKILL.md` and `record/skills/prereg-research-workflow.SKILL.md`.

The md5s are in [record/MANIFEST.md](record/MANIFEST.md) and in the Amendment 3 registration.

**Provenance:** Claude (Anthropic, Opus 5.5) made the extraction mechanically and assigned every
disposition by hand. That is self-tested. Human review: direction only. Responsibility: Chad Holland.

| Ref | Source | Line | Hash | Item (abridged) | Disposition | Home |
|---|---|---|---|---|---|---|
| SWAY-001 | METHOD_SWAY.md@4c7518a | 23 | `309d95cd6d` | Lakatos's hard core and protective belt | RECORD | - |
| SWAY-002 | METHOD_SWAY.md@4c7518a | 24 | `147edea7a0` | The exploratory/confirmatory split from registered reports | RECORD | - |
| SWAY-003 | METHOD_SWAY.md@4c7518a | 25 | `c9fc1377d1` | Anytime-valid inference with e-values | RECORD | - |
| SWAY-004 | METHOD_SWAY.md@4c7518a | 26 | `9b49371db6` | Evaluator-driven evolutionary search: FunSearch (2023) and AlphaEvolve (2025) | RECORD | - |
| SWAY-005 | METHOD_SWAY.md@4c7518a | 40 | `959cc8bfa7` | / **Foundation** / Never / The six invariants below / | RECORD | - |
| SWAY-006 | METHOD_SWAY.md@4c7518a | 41 | `1febf94f94` | / **Canopy** (upper floors) / Freely / Exploration: any idea, any analogy, any metric, … | RECORD | - |
| SWAY-007 | METHOD_SWAY.md@4c7518a | 42 | `2fbca59866` | / **Damper** / Absorbs motion / The fork ledger: every exploratory move is logged, neve… | RECORD | - |
| SWAY-008 | METHOD_SWAY.md@4c7518a | 43 | `48d2a00da1` | / **Elevator** / One way, gated / Promotion: the only path from canopy idea to publishe… | RECORD | - |
| SWAY-009 | METHOD_SWAY.md@4c7518a | 49 | `0d9307b381` | **Numbers come from code.** Prose numbers are pasted from output. | RULE | M6 |
| SWAY-010 | METHOD_SWAY.md@4c7518a | 50 | `22ace907d8` | **Refutations are kept.** Nothing is deleted to look better. | RULE | M8 |
| SWAY-011 | METHOD_SWAY.md@4c7518a | 51 | `3871affa2e` | **Nothing certifies itself.** A verdict above UNVERIFIED needs an input the system unde… | RULE | M10 |
| SWAY-012 | METHOD_SWAY.md@4c7518a | 52 | `92e3654d20` | **The sealed set is sealed.** Confirmation data is never touched in the canopy. It is s… | RULE | M11 |
| SWAY-013 | METHOD_SWAY.md@4c7518a | 53 | `bbf9506333` | **Labels are honest.** Canopy output is always tagged `EXPLORATORY` and can never be ci… | RULE | M7 |
| SWAY-014 | METHOD_SWAY.md@4c7518a | 54 | `4b82ae331d` | **Exploratory provenance is append-only.** Every fork that contributes evidence to a pr… | RULE | C-EXPLORE |
| SWAY-015 | METHOD_SWAY.md@4c7518a | 63 | `525d509265` | Peek at results as often as you like. Change the metric. Change the question. | RULE | C-DISCOVER |
| SWAY-016 | METHOD_SWAY.md@4c7518a | 64 | `da355da32b` | Import math from any field. Fluid dynamics, auction theory, immunology: use it if it pr… | RULE | C-DISCOVER |
| SWAY-017 | METHOD_SWAY.md@4c7518a | 65 | `4e1a6e0a6e` | Generate hypotheses in bulk with multiple models (Claude, Kimi, and others), credited b… | RULE | C-DISCOVER |
| SWAY-018 | METHOD_SWAY.md@4c7518a | 66 | `e279e1e64c` | Run crude, fast, ugly experiments. Wrong is cheap here. | RULE | C-DISCOVER |
| SWAY-019 | METHOD_SWAY.md@4c7518a | 67 | `616ab7420f` | Follow the anomaly instead of the plan. | RULE | C-DISCOVER |
| SWAY-020 | METHOD_SWAY.md@4c7518a | 73 | `5bdaace425` | **Sprout.** Generate many candidate hypotheses (10–50). Include at least 20% from a del… | RULE | C-DISCOVER |
| SWAY-021 | METHOD_SWAY.md@4c7518a | 74 | `bdc1c54625` | **Cheap kill.** For each sprout, have a critic model name the cheapest experiment that … | RULE | C-DISCOVER |
| SWAY-022 | METHOD_SWAY.md@4c7518a | 75 | `de9db922e1` | **Evolve.** Survivors that can be expressed as a program with a scoring function get mu… | RULE | C-DISCOVER |
| SWAY-023 | METHOD_SWAY.md@4c7518a | 76 | `e04afa54eb` | **Crystallize.** A survivor that keeps surviving gets written as a precise, refutable c… | RULE | C-DISCOVER |
| SWAY-024 | METHOD_SWAY.md@4c7518a | 101 | `da59643502` | Written as a registered prediction *before* touching the sealed set | RULE | M2 |
| SWAY-025 | METHOD_SWAY.md@4c7518a | 102 | `0a5d4d6b0c` | Anti-vacuity control: the instrument is shown returning null on a case where null is co… | RULE | M3 |
| SWAY-026 | METHOD_SWAY.md@4c7518a | 103 | `42ba449e93` | Run on the sealed set (or a fresh post-registration device run) | RULE | M11 |
| SWAY-027 | METHOD_SWAY.md@4c7518a | 104 | `a80b476aef` | Evidence threshold met: E ≥ 20 under the registered null and the stated e-process assum… | SUPERSEDED | D3, C-STAT |
| SWAY-028 | METHOD_SWAY.md@4c7518a | 105 | `13d6db5b6b` | Fork count from the ledger stated in the note | RULE | C-EXPLORE |
| SWAY-029 | METHOD_SWAY.md@4c7518a | 106 | `6fa09c2af1` | Status label starts at `Draft`, never higher | RULE | M7 |
| SWAY-030 | METHOD_SWAY.md@4c7518a | 120 | `323645677c` | Look after every data point. | RULE | C-STAT |
| SWAY-031 | METHOD_SWAY.md@4c7518a | 121 | `660ab30c3d` | Stop early when evidence is overwhelming. | RULE | C-STAT |
| SWAY-032 | METHOD_SWAY.md@4c7518a | 122 | `ecc91d53c7` | Continue when it is ambiguous. | RULE | C-STAT |
| SWAY-033 | METHOD_SWAY.md@4c7518a | 123 | `7f60bf0412` | Combine e-values across evidence streams only with a rule whose validity conditions are… | RULE | C-STAT |
| SWAY-034 | METHOD_SWAY.md@4c7518a | 162 | `ef7c94c91b` | **Missing means deny.** Absent, empty, None or malformed input returns DENY/UNVERIFIED,… | RULE | C-BUILD |
| SWAY-035 | METHOD_SWAY.md@4c7518a | 164 | `49672ccb91` | **Vetoes never vote.** A veto is a separate fail-closed condition, not a value entering… | RULE | C-BUILD |
| SWAY-036 | METHOD_SWAY.md@4c7518a | 165 | `1b9e062396` | **Nothing certifies itself.** This is invariant 3, applied to code. A hash-valid manife… | RULE | M10 |
| SWAY-037 | METHOD_SWAY.md@4c7518a | 166 | `e34066fb66` | **Every guard ships with its killer.** Each guard has one registered attack that must f… | RULE | M3 |
| SWAY-038 | METHOD_SWAY.md@4c7518a | 168 | `b3b354033f` | **Verdicts are deterministic.** Seeded, or computed without randomness. A verdict redra… | RULE | M5 |
| SWAY-039 | METHOD_SWAY.md@4c7518a | 171 | `1cb3118098` | The gate is proven in both directions: real case exit 0, sabotage exit nonzero | RULE | M3 |
| SWAY-040 | METHOD_SWAY.md@4c7518a | 172 | `9ff5e499a2` | The gate runs on the device, with its output pasted verbatim | SUPERSEDED | D4, C-DEVICE |
| SWAY-041 | METHOD_SWAY.md@4c7518a | 173 | `9cdac856cc` | The file identity is checked by md5 after every transfer | RULE | C-DEVICE |
| SWAY-042 | METHOD_SWAY.md@4c7518a | 174 | `ef88163082` | A cold clone reproduces the gate result from the pushed commit under the stated environ… | RULE | W8 |
| SWAY-043 | METHOD_SWAY.md@4c7518a | 175 | `918fc4a1ca` | The commit stages files by name, never with `-A` | RULE | W7 |
| SWAY-044 | METHOD_SWAY.md@4c7518a | 181 | `5d663a1940` | **Scope statement.** One or two sentences saying what it does and under what assumption… | RULE | W8 |
| SWAY-045 | METHOD_SWAY.md@4c7518a | 182 | `51ed56de44` | **Build elevator passed** (every box above), including a cold clone of the pushed commit. | RULE | W8 |
| SWAY-046 | METHOD_SWAY.md@4c7518a | 183 | `96b78550ba` | **No known defect inside the scope.** Known limits outside the scope are listed, not fi… | RULE | W8 |
| SWAY-047 | METHOD_SWAY.md@4c7518a | 184 | `563d2acebb` | **Frozen identity.** The commit SHA and file md5 are recorded next to the word DONE. | RULE | W8 |
| SWAY-048 | METHOD_SWAY.md@4c7518a | 185 | `e3c8f093f9` | **Doors listed separately.** Ideas for extensions go in the note or in `FORKS.md` as op… | RULE | W8 |
| SWAY-049 | METHOD_SWAY.md@4c7518a | 188 | `2c06012e43` | **A defect found inside the scope.** Fix it, re-run the elevator, record a new SHA. | RULE | W8 |
| SWAY-050 | METHOD_SWAY.md@4c7518a | 189 | `9eaa56d531` | **A deliberate scope change.** The new scope is written first; this is a new build, and… | RULE | W8 |
| SWAY-051 | METHOD_SWAY.md@4c7518a | 190 | `8771a69337` | **A dependency or platform change that breaks the gate.** The gate failing is the evide… | RULE | W8 |
| SWAY-052 | METHOD_SWAY.md@4c7518a | 209 | `a061180492` | / Property-based testing (Hypothesis) / Rule 1: missing means deny / Generate absent/em… | DOOR | - |
| SWAY-053 | METHOD_SWAY.md@4c7518a | 210 | `adff0dc5c4` | / Mutation testing (existing `mutation_probe.py`) / Rule 4: every guard ships with its … | DOOR | - |
| SWAY-054 | METHOD_SWAY.md@4c7518a | 211 | `c189cb163f` | / Coverage-guided fuzzing (Atheris) / Rules 1 and 4 / Find crashing or bypassing inputs… | DOOR | - |
| SWAY-055 | METHOD_SWAY.md@4c7518a | 212 | `ec936f2046` | / Symbolic contract checking (CrossHair, Z3-backed) / Rules 1 and 2 / Prove a guard pro… | DOOR | - |
| SWAY-056 | METHOD_SWAY.md@4c7518a | 213 | `a863ee2dfe` | / Signed provenance (Sigstore, in-toto, SLSA levels) / Invariant 3: nothing certifies i… | DOOR | - |
| SWAY-057 | METHOD_SWAY.md@4c7518a | 214 | `3e6f23c4f9` | / Hash-pinned dependencies (`pip --require-hashes`) / Cold-clone reproduction / "Same r… | DOOR | - |
| SWAY-058 | METHOD_SWAY.md@4c7518a | 227 | `1be0a224e5` | **P1.** Over the next 10 promoted claims, at least 3 will have originated in the canopy… | RECORD | C-DISCOVER |
| SWAY-059 | METHOD_SWAY.md@4c7518a | 228 | `3495da2aef` | **P2.** The median fork count per promoted claim will exceed 5. If it's lower, the cano… | RECORD | C-DISCOVER |
| SWAY-060 | METHOD_SWAY.md@4c7518a | 229 | `2f6315d9f4` | **P3.** Elevator refutation rate will be *higher* than the current method's. More ideas… | RECORD | C-DISCOVER |
| SWAY-061 | METHOD_SWAY.md@4c7518a | 230 | `538113b67e` | **P4 — OPEN, left unrun.** Do canopy-origin claims survive later replication at the sam… | RECORD | C-DISCOVER |
| SWAY-P01 | METHOD_SWAY.md@4c7518a | prose | `2b2cc05a92` | Forbidden here: stating a result as true, and touching the sealed set. | RULE | C-DISCOVER, M11 |
| SWAY-P02 | METHOD_SWAY.md@4c7518a | prose | `1462e1996d` | Rule: when a claim is promoted, its note must state how many forks preceded it (the denominator of exploration). | RULE | C-EXPLORE |
| SWAY-P03 | METHOD_SWAY.md@4c7518a | prose | `851e89a7f8` | Failing the elevator is not a failure of exploration. The idea returns to the canopy with its refutation attached. | RECORD | - |
| SWAY-P04 | METHOD_SWAY.md@4c7518a | prose | `ebd907183e` | Promotion threshold: E ≥ 20 (α = 0.05). Report the e-value, never just "significant." | SUPERSEDED | D3, C-STAT |
| SWAY-P05 | METHOD_SWAY.md@4c7518a | prose | `e8f0b420dc` | Sabotage control: python3 eprocess.py --sabotage must print GATE: FAIL and exit 1. | RECORD | C-STAT |
| SWAY-P06 | METHOD_SWAY.md@4c7518a | prose | `3687a83869` | "It could be better" is not a reason to reopen. Improvements go to a door, and a door is new work, not unfinished work. | RULE | W8 |
| SWAY-P07 | METHOD_SWAY.md@4c7518a | prose | `94bfcd6290` | Research is different: a claim can be settled (promoted or refuted), but a note always ends with an open door. DONE applies to builds and instruments, never to a line of inquiry. | RULE | M15, W8 |
| SWAY-P08 | METHOD_SWAY.md@4c7518a | prose | `44883de580` | Following the method's own rule, a tool is adopted only after it catches a real defect in this estate on a canopy trial. | RULE | M18 |
| SWAY-P09 | METHOD_SWAY.md@4c7518a | prose | `61e2e74924` | Status labels (extended, not replaced): EXPLORATORY, then Speculative, Draft, Draft verified reference code, Verified, REFUTED (kept). | VOCAB | VOCAB |
| A1-001 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 21 | `5432a17925` | / A registered design could not run: 0 of 2,200 HDFS blocks had ≥ 3 lines / veritas-com… | RECORD | - |
| A1-002 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 22 | `ece5821b88` | / A safety prediction's vacuity guard could never be reached: the gate DEFERs every mod… | RECORD | - |
| A1-003 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 23 | `c01f87381e` | / A prediction printed FAILED at exactly its bound: `8/20 − 7/20 = 0.050000000000000044… | RECORD | - |
| A1-004 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 24 | `5321745bf7` | / The same prompt, sent 3 times at temperature 0, scored 13–15 of 20 / C006b A1/A2/A3 /… | RECORD | - |
| A1-005 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 25 | `fbb5ba8a3d` | / A simpler rival matched the system: no escalation equalled the companion on 2 of 3 se… | RECORD | - |
| A1-006 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 26 | `ce5be698a5` | / "Conformance" read as validity: kernel and verifier agree on 4690 vectors, yet a spoo… | RECORD | - |
| A1-007 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 27 | `9c217966e6` | / Two implementations by one author were counted as independent / sovereign-veritas iss… | RECORD | - |
| A1-008 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 31 | `8abe7288bb` | **Pre-freeze feasibility count** (C006). Before a registration is frozen, a script prin… | RULE | C-FEAS |
| A1-009 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 35 | `58ba93b140` | **The vacuity guard must be reachable** (C006b P1). Every registered guard states the p… | RULE | M3 |
| A1-010 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 38 | `ce2be45d60` | **Thresholds are compared exactly** (C006b P3). Rational scores use exact fractions (or… | RULE | M5 |
| A1-011 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 40 | `f20691ac3d` | **Measure same-input noise before choosing a bound** (C006b). For a model-backed arm, r… | RULE | C-NOISE |
| A1-012 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 43 | `ba0bf8f4f6` | **The simplest rival is a required arm** (C002, Run 2, E002). Every registration names … | RULE | M14 |
| A1-013 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 46 | `fde43fa189` | **Three validity axes on every claim** (issue #4, veritas-holo). Each claim states sepa… | RULE | M7 |
| A1-014 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 50 | `e21e8d3449` | **Outcome vocabulary** (C006, C006b). Alongside HELD and FAILED, these are first-class … | VOCAB | VOCAB, D1 |
| A1-015 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 54 | `0519629ad2` | **Replication has levels** (issue #4 B10). A **re-run** is the same code and environment. | RULE | C-INDEP, VOCAB |
| A1-016 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 59 | `b76ef54008` | **The batched first amendment's wording.** The sentence "Generating hypotheses is now n… | RECORD | - |
| A1-017 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 67 | `11e27141e9` | / Researcher degrees-of-freedom ledger (ChatGPT 8) / SWAY's fork count already records … | DOOR | - |
| A1-018 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 68 | `a92fe51bc7` | / Expected information gain per unit cost (ChatGPT 12) / No way to estimate EIG before … | DOOR | - |
| A1-019 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 69 | `c7c0627a9e` | / Artifact ladder, levels 0–10 (ChatGPT 11) / Items 1–5 above are its rungs that actual… | DOOR | - |
| A1-020 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 70 | `c9fa5b9257` | / Claim ledger in every repository (ChatGPT 14) / veritas-holo already keeps `claims/`.… | DOOR | - |
| A1-021 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 71 | `aa99504a86` | / Discovery vs confirmation; don't retrofit mathematics (ChatGPT 5, 6) / Already SWAY's… | DOOR | - |
| A1-022 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | 81 | `a58b516f30` | **P5, OPEN, unrun.** Over the next 5 registrations across the estate, count the failure… | RECORD | D5 |
| A1-P01 | METHOD_SWAY_AMENDMENT_1.md@4c7518a | prose | `319f0a4b23` | A proposal is ADOPTED only if a real failure shows that it would have caught something the method as written did not. Otherwise it stays a DOOR. | RULE | M18 |
| A2-001 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 21 | `9e2eb59a45` | / Two Claude sessions ran the same challenge question within an hour. The later write-u… | RECORD | - |
| A2-002 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 22 | `c07de8e0fe` | / The independent reviewer of V14's bound did not finish. Its replacement was the same … | RECORD | - |
| A2-003 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 23 | `8ab3894b19` | / A proposal's text was credited to "the author" without evidence of who drafted it / s… | RECORD | - |
| A2-004 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 24 | `e685b4b359` | / A cross-check accepted stale, replayed and derived-from-A evidence. Earlier tests had… | RECORD | - |
| A2-005 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 25 | `3b9302d914` | / An outside AI's analysis stated figures about the repository that were stale or wrong… | RECORD | - |
| A2-006 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 29 | `85f9a377e0` | **Behaviour questions are settled against the actual code, not by explanation.** When the | RULE | M4 |
| A2-007 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 35 | `df2f153aa2` | **Default matrix for evidence questions.** When the question is whether a rule handles its | RULE | C-EVID |
| A2-008 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 39 | `bab601173e` | **AI work does not vouch for itself.** An AI system's design, code, interpretation or a… | RULE | M10 |
| A2-009 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 41 | `6a46668d0a` | When the same AI designed the test and predicted its result, the result is labelled | RULE | M10 |
| A2-010 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 43 | `f32fd411ce` | An attack by the same AI is labelled as such, and it is weaker. | RULE | M10, W5 |
| A2-011 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 44 | `fbd33c578e` | Two sessions of the same AI are not independent unless provenance shows it. Separate se… | RULE | M10, C-INDEP |
| A2-012 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 46 | `3d8741f46f` | This extends Amendment 1 item 8. Independent reproduction needs a different person, or a | RULE | C-INDEP |
| A2-013 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 49 | `f64761ec7f` | **AI provenance is stated with the review level that actually happened.** Every artifac… | RULE | M13 |
| A2-014 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 51 | `114fa5642f` | **the chain:** AI participation → human validation → human editing/curation → human | RULE | M13 |
| A2-015 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 53 | `5e04e583fc` | **the model**, by name; | RULE | M13 |
| A2-016 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 54 | `7de302dde0` | **one human review level:** line-by-line, outcome review, or direction only. The level … | RULE | M13 |
| A2-017 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 63 | `920320fdb2` | / Predict first; preregister if it will be relied on / Elevator: "written as a register… | RECORD | - |
| A2-018 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 64 | `140a083142` | / Run and record raw output, commit, environment / invariant 1, invariant 6, build elev… | RECORD | - |
| A2-019 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 65 | `7f5bece035` | / Keep failures and refutations / invariant 2 / | RECORD | - |
| A2-020 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 66 | `9881468074` | / Anti-vacuity control, sabotage switch / Elevator; build rule 4; Amendment 1 item 2 (t… | RECORD | - |
| A2-021 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 67 | `c47cdb3dbe` | / Simplest rival explanation / Amendment 1 item 5 (the simplest rival is a required arm) / | RECORD | - |
| A2-022 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 68 | `1711d30083` | / "If a test cannot settle it, stop" / Amendment 1 item 2 (registered as untestable) an… | RECORD | - |
| A2-023 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 69 | `6bc98deff3` | / Never upgrade a simulation into a real-world claim / Amendment 1 item 6 (three validi… | RECORD | - |
| A2-024 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 70 | `e5321be467` | / Results are appended, never rewritten / invariant 6; the repositories' append-only pr… | RECORD | - |
| A2-025 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 77 | `d803ab817e` | **"Reproduced"** already has a defined meaning in Amendment 1 item 8: the same specific… | RECORD | D2 |
| A2-026 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 80 | `b7620c5ee6` | **"Exactly one per claim"** contradicts Amendment 1 item 6, under which each claim carr… | RECORD | D2 |
| A2-027 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 82 | `20435960ca` | **"Supported / not supported / refuted"** is a claim-verdict layer that already exists … | VOCAB | VOCAB, D2 |
| A2-028 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 88 | `f3eab37b1b` | the status ladder and `EXPLORATORY` for the note; | VOCAB | VOCAB |
| A2-029 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 89 | `d468eff4ac` | Amendment 1 item 7's outcomes for each prediction; | VOCAB | VOCAB |
| A2-030 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 90 | `3566b0c3fe` | item 6's three axes for each claim, with `NOT RUN` on the empirical axis for model or | VOCAB | VOCAB |
| A2-031 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 92 | `290a37b2f1` | item 8's levels for replication; | VOCAB | VOCAB |
| A2-032 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 93 | `11ad7f6669` | `SUPPORTED / NOT_SUPPORTED / REFUTED` for claim verdicts where an evidence adapter prod… | VOCAB | VOCAB |
| A2-033 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 100 | `eae7d323d6` | / Output shape: "prediction, what happened, status, limits, next unrun test" / a report… | DOOR | - |
| A2-034 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 101 | `71b365c03d` | / Preferring interactive artifacts (visualizations, manipulable models) as instruments … | DOOR | - |
| A2-035 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 105 | `494e82578c` | **P6, OPEN, unrun.** Over the next 5 registrations across the estate that involve an AI… | RECORD | D11 |
| A2-036 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 107 | `b783586456` | an AI-produced result described as independent without provenance showing it; | RECORD | D11 |
| A2-037 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | 108 | `03d42d2e38` | an evidence rule tested without stale, derived or replayed conditions and without a sta… | RECORD | D11 |
| A2-P01 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | prose | `a3fc299291` | An item is ADOPTED only if a real failure shows that it would have caught something the method as written did not. Otherwise it stays a DOOR. | RULE | M18 |
| A2-P02 | record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md | prose | `c7758be55b` | Human review of AI-assisted material is not validation of the underlying claim. | RULE | M13 |
| TEMPLATE-001 | NOTE_TEMPLATE.md@4c7518a | 23 | `efc5be5d64` | REGISTERED predictions, written BEFORE running, numbered (P1, P2...). | RULE | M2 |
| TEMPLATE-002 | NOTE_TEMPLATE.md@4c7518a | 24 | `780ae65fca` | Include an anti-vacuity control: show your instrument CAN return null. | RULE | M3 |
| TEMPLATE-003 | NOTE_TEMPLATE.md@4c7518a | 25 | `ec1b2c59f6` | If you ran it: paste the printed numbers verbatim. If a registered | RULE | M6, M8 |
| TEMPLATE-P01 | NOTE_TEMPLATE.md@4c7518a | prose | `4a13f638ca` | State it so it can be precisely wrong. If nothing could refute it, it is not yet a note. | RULE | M1 |
| TEMPLATE-P02 | NOTE_TEMPLATE.md@4c7518a | prose | `78e2f6e02d` | Epistemic status (read first): one honest paragraph on what is established and what is speculation. | REPO | - |
| TEMPLATE-P03 | NOTE_TEMPLATE.md@4c7518a | prose | `9c5b7f45f7` | Known mathematics / prior art: cite it; an issue with a reference improves the note (add-only). | REPO | - |
| TEMPLATE-P04 | NOTE_TEMPLATE.md@4c7518a | prose | `bf54829869` | Reference code: runnable, dependency-light (NumPy-tier), prints every number that appears in this note. | RULE | M6 |
| TEMPLATE-P05 | NOTE_TEMPLATE.md@4c7518a | prose | `6fc7c91fc0` | No code yet? Label the note Speculative and describe the experiment someone else could build. | RULE | M6 |
| TEMPLATE-P06 | NOTE_TEMPLATE.md@4c7518a | prose | `a1a201ccef` | Leave at least one prediction unrun. Every note should end with a door someone else can walk through. | RULE | M15 |
| TEMPLATE-P07 | NOTE_TEMPLATE.md@4c7518a | prose | `a442df1ece` | Checklist: status label honest; claims registered and numbered; refuted claims kept; numbers match code output; at least one open prediction; credit given, including to AIs. | RULE | M7, M2, M8, M6, M15, M13 |
| TEMPLATE-P08 | NOTE_TEMPLATE.md@4c7518a | prose | `2d8bcb5ca2` | Author: human or AI. AIs: name your model and credit honestly. | RULE | M13 |
| CLAUDE-001 | CLAUDE.md@4c7518a | 32 | `88b417c8be` | **State claims so they can be precisely wrong.** If nothing could refute it, | RULE | M1 |
| CLAUDE-002 | CLAUDE.md@4c7518a | 34 | `bb8af715d3` | **Register predictions before running.** Numbered P1, P2, … | RULE | M2 |
| CLAUDE-003 | CLAUDE.md@4c7518a | 35 | `5713855a4d` | **Include an anti-vacuity control.** Show the instrument *can* return null. | RULE | M3 |
| CLAUDE-004 | CLAUDE.md@4c7518a | 38 | `4ee4f03b96` | **Refutations are first-class.** If a registered claim failed, KEEP IT, mark | RULE | M8 |
| CLAUDE-005 | CLAUDE.md@4c7518a | 41 | `74fc065c4e` | **Numbers in prose must match code output verbatim.** Paste them; don't | RULE | M6 |
| CLAUDE-006 | CLAUDE.md@4c7518a | 43 | `09b6676356` | **Leave at least one prediction unrun.** Every note ends with a door. | RULE | M15 |
| CLAUDE-007 | CLAUDE.md@4c7518a | 44 | `8d4cc48cb5` | **Failures lead the document.** Put what broke at the top, not in a footnote. | RULE | M8 |
| CLAUDE-008 | CLAUDE.md@4c7518a | 56 | `cfd29f98af` | / `research_notes/` / 78 `.md` files — the note series / **Canonical home for all notes… | REPO | - |
| CLAUDE-009 | CLAUDE.md@4c7518a | 57 | `04ed1a26e2` | / `notes/` / 2 stray `.md` files / Colliding duplicates — see Known defects / | REPO | - |
| CLAUDE-010 | CLAUDE.md@4c7518a | 58 | `8590aea173` | / `scripts/` / 29 files: `noteNNN_reference.py`, figure generators, `make_index.py` / O… | REPO | - |
| CLAUDE-011 | CLAUDE.md@4c7518a | 59 | `5540a36ea4` | / `whitepapers/` / 8 longer writeups / / | REPO | - |
| CLAUDE-012 | CLAUDE.md@4c7518a | 60 | `d953908539` | / `sovereign_core/` / Governance engine + `test_sovereign.py` / 33/33 deterministic on … | REPO | - |
| CLAUDE-013 | CLAUDE.md@4c7518a | 61 | `df366b143b` | / `experiments/`, `simulations/` / Experiment code / / | REPO | - |
| CLAUDE-014 | CLAUDE.md@4c7518a | 62 | `dd4beb1e5b` | / `figures/` / 49 generated images / Regenerate via `scripts/generate_*.py` / | REPO | - |
| CLAUDE-015 | CLAUDE.md@4c7518a | 63 | `84898b5a8d` | / `results/` / `last_run_report.json` / Written by `make synthetic` / | REPO | - |
| CLAUDE-016 | CLAUDE.md@4c7518a | 64 | `0760fc4c75` | / `formal/`, `references/`, `discussions/`, `datasets/`, `data/` / Supporting material / / | REPO | - |
| CLAUDE-017 | CLAUDE.md@4c7518a | 76 | `f49f32f2ce` | `NNN_short_title.md` — 45 files (earlier series) | REPO | - |
| CLAUDE-018 | CLAUDE.md@4c7518a | 77 | `7a71a20952` | `noteNNN_short_title.md` — 24 files (later series) | REPO | - |
| CLAUDE-019 | CLAUDE.md@4c7518a | 93 | `1ad6956175` | **Number collisions are real and intentional to display.** `NOTES_INDEX.md` | REPO | - |
| CLAUDE-020 | CLAUDE.md@4c7518a | 99 | `0167b3b6d9` | **`notes/` duplicates numbers already used in `research_notes/`.** | REPO | - |
| CLAUDE-021 | CLAUDE.md@4c7518a | 100 | `3a6cf311ef` | `notes/028_thought_tensor_category_morphism.md` vs | REPO | - |
| CLAUDE-022 | CLAUDE.md@4c7518a | 102 | `fde4cbf1f7` | `notes/note048_grok_contribution_manifesto.md` vs | REPO | - |
| CLAUDE-023 | CLAUDE.md@4c7518a | 108 | `8d2ffd855f` | **`START_HERE.md` is wrong.** It is an SECP deployment guide that tells the | REPO | - |
| CLAUDE-024 | CLAUDE.md@4c7518a | 114 | `37a522c050` | **The graph is a star, not a network.** Across 78 notes there are **4 | REPO | - |
| CLAUDE-025 | CLAUDE.md@4c7518a | 127 | `5d546a42be` | **Ask before restructuring.** Renumbering, merging directories, or bulk | REPO | - |
| CLAUDE-026 | CLAUDE.md@4c7518a | 129 | `f44442b9cc` | **Never edit a note to make a claim look better.** If a registered prediction | RULE | M8 |
| CLAUDE-027 | CLAUDE.md@4c7518a | 131 | `e609de531a` | **Never delete a refuted note.** `⚠` in the index marks kept failures. That | RULE | M8 |
| CLAUDE-028 | CLAUDE.md@4c7518a | 133 | `5885f19b1c` | **Do not hand-edit `NOTES_INDEX.md`.** It is auto-generated. Edit notes, then | REPO | - |
| CLAUDE-029 | CLAUDE.md@4c7518a | 135 | `09aff09353` | **Preserve `[[wikilinks]]` and existing markdown links** on any edit. | REPO | - |
| CLAUDE-030 | CLAUDE.md@4c7518a | 136 | `77a0cee39f` | **Credit contributors, including AIs, by model name.** | RULE | M13 |
| CLAUDE-031 | CLAUDE.md@4c7518a | 137 | `3ce936d629` | **Do not present a reading of a file as a verified fact.** Run it, paste the | RULE | M6 |
| CLAUDE-032 | CLAUDE.md@4c7518a | 139 | `7eecf97f97` | **Do not add a claim to a note without the code that prints its numbers.** | RULE | M6 |
| CLAUDE-033 | CLAUDE.md@4c7518a | 142 | `119042c5b4` | **One command at a time** when handing commands to the operator; this repo is | OPS | - |
| CLAUDE-034 | CLAUDE.md@4c7518a | 168 | `f693f94fd4` | filename matches `NNN_*.md` or `noteNNN_*.md` exactly | REPO | - |
| CLAUDE-035 | CLAUDE.md@4c7518a | 169 | `cac716c0f5` | status label is honest | RULE | M7 |
| CLAUDE-036 | CLAUDE.md@4c7518a | 170 | `460c448eeb` | claims registered and numbered (P1, P2, …) | RULE | M2 |
| CLAUDE-037 | CLAUDE.md@4c7518a | 171 | `f132a2d7dc` | anti-vacuity control present — the instrument can return null | RULE | M3 |
| CLAUDE-038 | CLAUDE.md@4c7518a | 172 | `d2718f0d91` | any refuted claim kept and marked | RULE | M8 |
| CLAUDE-039 | CLAUDE.md@4c7518a | 173 | `682476945a` | every number in the prose matches `scripts/noteNNN_reference.py` output | RULE | M6 |
| CLAUDE-040 | CLAUDE.md@4c7518a | 174 | `bb66a841b4` | at least one open prediction left unrun | RULE | M15 |
| CLAUDE-041 | CLAUDE.md@4c7518a | 175 | `01eef9d107` | at least one outgoing `[[wikilink]]` to a related note (no orphans) | REPO | - |
| CLAUDE-042 | CLAUDE.md@4c7518a | 176 | `586d3e188b` | credit given, including to AI contributors | RULE | M13 |
| CLAUDE-043 | CLAUDE.md@4c7518a | 177 | `72e93f29a7` | `python scripts/make_index.py` re-run and the note appears | REPO | - |
| CLAUDE-P01 | CLAUDE.md@4c7518a | prose | `0c9609316a` | Status labels in use: Speculative, Draft, Draft verified reference code, Architecture Verified, Architecture Self-Tested, Verified, REFUTED (kept). | VOCAB | VOCAB |
| CLAUDE-P02 | CLAUDE.md@4c7518a | prose | `1a64c7c1f5` | Environment note: Termux on the S25; set +H before pasting text with !; /tmp is not writable, use $HOME. | RULE | C-DEVICE |
| CLAUDE-P03 | CLAUDE.md@4c7518a | prose | `3002e737f4` | Prime directive: trust the files, not the summary of the files. Verify before you act. | RULE | M4, M6 |
| CLAUDE-P04 | CLAUDE.md@4c7518a | prose | `8efb964805` | AI contributions are credited by model name in the note header. Do not strip AI attribution. | RULE | M13 |
| EF-001 | record/skills/experiment-first.SKILL.md | 14 | `0a7788614d` | **Question.** State the observable question in one line, separate from interpretation. … | RULE | W1 |
| EF-002 | record/skills/experiment-first.SKILL.md | 15 | `d10939a849` | **Smallest instrument.** Build the minimal test, harness or simulation that isolates it… | RULE | W3, M4 |
| EF-003 | record/skills/experiment-first.SKILL.md | 16 | `cd8d6a5dd0` | **Variables.** Change one condition at a time. Include the boundary cases and the adver… | RULE | W3, C-EVID |
| EF-004 | record/skills/experiment-first.SKILL.md | 17 | `683df16dc7` | **Predict first.** Write expected outcomes before running. If the result will be publis… | RULE | M2 |
| EF-005 | record/skills/experiment-first.SKILL.md | 18 | `74512322e7` | **Run and record.** Keep the raw output, the commit hash, the platform and the command … | RULE | W4, M12 |
| EF-006 | record/skills/experiment-first.SKILL.md | 19 | `59fc402310` | **Compare.** Report every disagreement between prediction and outcome. Keep failures an… | RULE | M8, M9 |
| EF-007 | record/skills/experiment-first.SKILL.md | 20 | `a1f199f2b5` | **Mechanism.** Explain why it happened only after observing it, and tie the explanation… | RULE | M9 |
| EF-008 | record/skills/experiment-first.SKILL.md | 21 | `a4b3205e37` | **Attack.** Try counterexamples, malformed inputs and boundary cases. Include an anti-v… | RULE | W5, M3 |
| EF-009 | record/skills/experiment-first.SKILL.md | 22 | `dc730c7b0a` | **Status.** Label each claim with exactly one of: observed / reproduced / supported / n… | SUPERSEDED | D2, VOCAB |
| EF-010 | record/skills/experiment-first.SKILL.md | 23 | `398057a64b` | **Preserve.** Keep the question, predictions, assumptions, matrix, code, raw results, i… | RULE | M12 |
| EF-011 | record/skills/experiment-first.SKILL.md | 29 | `d0e8664070` | If Claude designed the test, and the test agrees with Claude's prediction, record it as… | RULE | M10 |
| EF-012 | record/skills/experiment-first.SKILL.md | 30 | `783b841bfd` | An attack Claude runs on its own work is weaker, and is labeled that way. | RULE | M10, W5 |
| EF-013 | record/skills/experiment-first.SKILL.md | 31 | `2fe3901e1a` | Independence requires one of: a separate reviewer that has not seen the build (another … | RULE | M10, C-INDEP |
| EF-014 | record/skills/experiment-first.SKILL.md | 32 | `db301349dd` | Two Claude sessions are not independent of each other unless provenance shows it. | RULE | M10 |
| EF-P01 | record/skills/experiment-first.SKILL.md | prose | `70b9861385` | Principle: explain less when direct experimentation can reveal more. Executable artifacts are instruments, not lessons. | RULE | M4 |
| EF-P02 | record/skills/experiment-first.SKILL.md | prose | `25d94c3c35` | Use it when a small test can answer how a mechanism behaves; skip it for definitions, history, or decisions only Chad can make. | OPS | - |
| EF-P03 | record/skills/experiment-first.SKILL.md | prose | `b41f0da5c2` | Provenance: state the chain, name the model, state only the human review level that actually happened. | RULE | M13 |
| EF-P04 | record/skills/experiment-first.SKILL.md | prose | `ade5fff4b3` | Output shape: give results, not lessons: prediction, what happened, status label, limits, next unrun test. | DOOR | - |
| PRW-001 | record/skills/prereg-research-workflow.SKILL.md | 12 | `b66fc46c7f` | **The question.** State the observable question in one line. Read the relevant code and… | RULE | W1, M4 |
| PRW-002 | record/skills/prereg-research-workflow.SKILL.md | 13 | `7dafd87a15` | **The design.** Map the question onto the real code path. Name every stand-in: model, f… | RULE | M4 |
| PRW-003 | record/skills/prereg-research-workflow.SKILL.md | 14 | `3e06558cb3` | **The simplest rival.** Name it, and run it as an arm. | RULE | M14 |
| PRW-004 | record/skills/prereg-research-workflow.SKILL.md | 15 | `e7e053d78a` | **Feasibility counts.** Print the counts the design depends on and commit them with the… | RULE | C-FEAS |
| PRW-005 | record/skills/prereg-research-workflow.SKILL.md | 16 | `da8222074b` | **For evidence questions,** cover fresh → stale → unavailable → contradictory → derived… | RULE | C-EVID |
| PRW-006 | record/skills/prereg-research-workflow.SKILL.md | 20 | `69db942ad0` | Write `docs/<ID>_PREREG.md` (or a Principia note). Include: | RULE | W2 |
| PRW-007 | record/skills/prereg-research-workflow.SKILL.md | 21 | `3e0c6e19ac` | the scope; | RULE | W2 |
| PRW-008 | record/skills/prereg-research-workflow.SKILL.md | 22 | `1d5243efe6` | the constants; | RULE | W2 |
| PRW-009 | record/skills/prereg-research-workflow.SKILL.md | 23 | `c782acec07` | the case matrix; | RULE | W2 |
| PRW-010 | record/skills/prereg-research-workflow.SKILL.md | 24 | `e7086b00de` | derived expected values; | RULE | W2 |
| PRW-011 | record/skills/prereg-research-workflow.SKILL.md | 25 | `18ff797057` | numbered predictions with exact pass criteria and tolerances; | RULE | W2, M2 |
| PRW-012 | record/skills/prereg-research-workflow.SKILL.md | 26 | `608235c02e` | the anti-vacuity control and how it can fire; | RULE | W2, M3 |
| PRW-013 | record/skills/prereg-research-workflow.SKILL.md | 27 | `aa6c14ef73` | the limits; | RULE | W2 |
| PRW-014 | record/skills/prereg-research-workflow.SKILL.md | 28 | `df651aa6bb` | provenance and credit; | RULE | W2, M13 |
| PRW-015 | record/skills/prereg-research-workflow.SKILL.md | 29 | `db15e8ee94` | the unrun next step. | RULE | W2, M15 |
| PRW-016 | record/skills/prereg-research-workflow.SKILL.md | 30 | `0287e571a8` | Commit it alone ("<ID> REGISTRATION: … (nothing built or run)"). When Chad asks for a f… | RULE | W2 |
| PRW-017 | record/skills/prereg-research-workflow.SKILL.md | 31 | `611d0be21d` | **A registration is never edited after this.** Errors found later are recorded in the r… | RULE | M2 |
| PRW-018 | record/skills/prereg-research-workflow.SKILL.md | 35 | `920f11cfde` | Import the real functions; don't copy them. The harness prints one HELD or REFUTED line… | RULE | W4 |
| PRW-019 | record/skills/prereg-research-workflow.SKILL.md | 36 | `088c6101da` | Add a `--sabotage` switch that disables the mechanism under test. The outcome must then… | RULE | M3 |
| PRW-020 | record/skills/prereg-research-workflow.SKILL.md | 37 | `2259b72007` | Keep runs deterministic across platforms: seeded RNGs and rounded outputs, with no knif… | RULE | M5 |
| PRW-021 | record/skills/prereg-research-workflow.SKILL.md | 38 | `77c668d93a` | Commit the harness exactly as run, together with the raw output (`results/<id>/run.txt`… | RULE | W4 |
| PRW-022 | record/skills/prereg-research-workflow.SKILL.md | 39 | `3f7d9cf47f` | Never retune constants or predictions after seeing results. Disclose any change made af… | RULE | M2 |
| PRW-023 | record/skills/prereg-research-workflow.SKILL.md | 44 | `2c55c2196b` | self-testing; | RULE | W6 |
| PRW-024 | record/skills/prereg-research-workflow.SKILL.md | 45 | `3f3ccb68fa` | model-derived versus real; | RULE | W6 |
| PRW-025 | record/skills/prereg-research-workflow.SKILL.md | 46 | `518529cb8e` | registration errors; | RULE | W6 |
| PRW-026 | record/skills/prereg-research-workflow.SKILL.md | 47 | `fd3d19f2c4` | deviations; | RULE | W6 |
| PRW-027 | record/skills/prereg-research-workflow.SKILL.md | 48 | `b7a9602979` | reviews that did not happen. | RULE | W6 |
| PRW-028 | record/skills/prereg-research-workflow.SKILL.md | 51 | `66ff4aee26` | the raw output, pasted, not paraphrased; | RULE | W6 |
| PRW-029 | record/skills/prereg-research-workflow.SKILL.md | 52 | `482f5475ca` | a prediction table with refutations kept; | RULE | W6 |
| PRW-030 | record/skills/prereg-research-workflow.SKILL.md | 53 | `9f20d150c9` | what the result shows and does not show, separating mathematical, implementation and em… | RULE | W6, M7 |
| PRW-031 | record/skills/prereg-research-workflow.SKILL.md | 54 | `1016ab083b` | candidate fixes, marked as proposals. Contract and format changes are Chad's decision. | RULE | W6 |
| PRW-032 | record/skills/prereg-research-workflow.SKILL.md | 55 | `3288f4a5be` | what is still open. | RULE | W6, M15 |
| PRW-033 | record/skills/prereg-research-workflow.SKILL.md | 61 | `38d0e12095` | Add CI steps: | RULE | W7 |
| PRW-034 | record/skills/prereg-research-workflow.SKILL.md | 62 | `e4ad3560c9` | the harness reproduces the recorded outcome (on the full OS and Python matrix when the … | RULE | W7 |
| PRW-035 | record/skills/prereg-research-workflow.SKILL.md | 63 | `494b88fedf` | `--sabotage` must exit 1; | RULE | W7 |
| PRW-036 | record/skills/prereg-research-workflow.SKILL.md | 64 | `332813001e` | challenger or protocol paths are exercised. | RULE | W7 |
| PRW-037 | record/skills/prereg-research-workflow.SKILL.md | 65 | `2c62665c1e` | Run the full test suite and `vacuity_lint` (pinned) before pushing. | RULE | W7 |
| PRW-038 | record/skills/prereg-research-workflow.SKILL.md | 66 | `09b60243fa` | Merge with a merge commit, never squash, so the registration-before-run order stays in … | RULE | M12 |
| PRW-039 | record/skills/prereg-research-workflow.SKILL.md | 67 | `372366c3c3` | When Chad says "show me the diff first", don't commit. If a hook demands a commit, stas… | OPS | - |
| PRW-040 | record/skills/prereg-research-workflow.SKILL.md | 71 | `8d153c53ca` | **AI provenance:** AI participation → human validation → human editing/curation → human… | RULE | M13 |
| PRW-041 | record/skills/prereg-research-workflow.SKILL.md | 72 | `8426cb107f` | **Self-validation:** Claude's own design, code or attack is never independent validatio… | RULE | M10 |
| PRW-042 | record/skills/prereg-research-workflow.SKILL.md | 73 | `77d0a08e8a` | **Credit only for specific, identifiable contributions.** External questions are credit… | RULE | M13, C-EXT |
| PRW-043 | record/skills/prereg-research-workflow.SKILL.md | 74 | `4e83ba49f6` | **External critiques and quotes:** | RULE | C-EXT |
| PRW-044 | record/skills/prereg-research-workflow.SKILL.md | 75 | `a8033a4865` | Keep them verbatim in `docs/external/`, with the author named and the sha256 of the exa… | RULE | C-EXT |
| PRW-045 | record/skills/prereg-research-workflow.SKILL.md | 76 | `04088a0c3b` | Check their factual claims row by row. | RULE | C-EXT |
| PRW-046 | record/skills/prereg-research-workflow.SKILL.md | 77 | `721515bacf` | Record disagreements separately from their text. | RULE | C-EXT |
| PRW-047 | record/skills/prereg-research-workflow.SKILL.md | 78 | `7a196381b4` | Never reconstruct a quote from memory or paraphrase. A private message is paraphrased, … | RULE | C-EXT |
| PRW-048 | record/skills/prereg-research-workflow.SKILL.md | 79 | `1aafd15b44` | **Influence claims** go in `docs/LINEAGE.md` as SUPPORTED, NOT SUPPORTED or INDETERMINA… | RULE | C-EXT, VOCAB |
| PRW-049 | record/skills/prereg-research-workflow.SKILL.md | 80 | `eb127760d9` | **Corrections are appended and dated.** History, timestamps and tags are never rewritte… | RULE | M12 |
| PRW-050 | record/skills/prereg-research-workflow.SKILL.md | 84 | `67fd4cc99d` | **The proxy:** in Claude's sandbox it blocks GraphQL, tag pushes and some API writes. U… | OPS | - |
| PRW-051 | record/skills/prereg-research-workflow.SKILL.md | 85 | `e893a14e50` | **Labels:** results not run on the device are marked NOT VALIDATED on the S25. Model re… | RULE | M7 |
| PRW-052 | record/skills/prereg-research-workflow.SKILL.md | 86 | `c8cdc1c2e6` | **Reporting:** report what was done, with commit hashes, CI status, the digest and what… | OPS | - |
| PRW-P01 | record/skills/prereg-research-workflow.SKILL.md | prose | `fb534c9e58` | This workflow sits inside SWAY; read the repo's CLAUDE.md and SWAY amendments before starting. | OPS | - |
| PRW-P02 | record/skills/prereg-research-workflow.SKILL.md | prose | `a0d8eb769d` | Results open with "What could have gone wrong, first". | RULE | W6, M8 |
| PRW-P03 | record/skills/prereg-research-workflow.SKILL.md | prose | `afc027dfe5` | "8 of 8 as registered" is not "passed". Say so when the predictions were predictions of failure. | RULE | W6 |
| A3-D1 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `cd5369d53a` | FAILED as a prediction outcome reads as REFUTED; records are not edited. | VOCAB | VOCAB, D1 |
| A3-D2 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `5abebe6877` | The eight-word list is retired; each word maps to its dimension. | VOCAB | VOCAB, D2 |
| A3-D3 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `5dd95f6cdf` | Error control matches the stopping rule; deterministic claims get no e-value. | RULE | C-STAT |
| A3-D4 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `e448f4109b` | A build is claimed working only where its gate ran; elsewhere NOT VALIDATED. | RULE | M7, C-DEVICE |
| A3-D5 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `49c0e7f696` | Method predictions are scored when their window closes. | RULE | M18 |
| A3-D6 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `4bc2e3b367` | Force levels MUST / SHOULD / MAY; weakening follows the adoption rule. | RULE | M18 |
| A3-D7 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `81a0015f2a` | Triggered controls are on unless answered; blank counts as yes. | RULE | M16 |
| A3-D8 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `271043d50d` | Record edits need no registration; append-only, with provenance. | RULE | W9 |
| A3-D9 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `6d3a92cfdb` | One definition per rule; excerpts checked by method_lint.py. | RULE | M17 |
| A3-D10 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `7b2a56938b` | Unused machinery is kept and labelled with its use counts. | RULE | C-DISCOVER, C-EXPLORE, C-STAT |
| A3-D13 | METHOD_SWAY_AMENDMENT_3.md@0c634a1 | decision | `9314c9a20c` | The methodology comparison is parked at Stage 2 revision 4; status UNRUN. | RULE | C-METHCOMP |
