# SWAY Amendment 4: people's data, study design, held-out data, source checks, generated inputs, pre-mortems and raw-output inspection — registration

**Status:** REGISTERED 2026-10-22, in a commit of its own, at METHOD.md as of `a5e1b5f`. Nothing described
here is built yet. This file is not edited after this commit. Results go in
`METHOD_SWAY_AMENDMENT_4_RESULTS.md`.

**Adoption:** by the owner. Chad Holland directed on 2026-10-22 that material improving SWAY be added. The
amendment is adopted when the pull request that builds it is merged by him. Until then the current
METHOD.md, WORKFLOW.md and CONTROLS.md govern. It is **not validated** as an improvement: P1–P3 below are
open.

**Provenance:** AI participation → human validation → human editing/curation → human responsibility.
- **AI participation:** Claude (Anthropic, Opus 5.5) compared SWAY with research-design and AI-research
  material the owner supplied, verified the cited claims, and drafted this amendment and its build.
- **Human validation:** direction only. Chad Holland supplied the material and the direction; he has not
  read this text line by line.
- **Human editing/curation:** none before adoption.
- **Responsibility:** Chad Holland.
- **Self-tested.** The gap search and the incidents below were found by the same AI that drafted the rules.

## Where the candidates came from

- Images of research-design and AI-research-method material the owner collected on 2026-10-22 (UKRIO's
  research-integrity principles, research-design charts, an ML training/testing diagram, a 10-step AI
  research workflow, Saïd Business School's recommendations on AI use, Maze's roles of AI in research,
  a synthetic-data-with-expert-validation loop). They are motivation only (C-EXT): none of their figures
  is relied on here.
- Anthropic's essay *Claude-shaped science* (anthropic.com/research/claude-shaped-science, read
  2026-10-22). It recommends rigid success criteria, inspecting plots and results yourself rather than
  trusting automated checks, adversarial checking in separate sessions, and bringing in experts early. It
  names premature "done" claims and correct calculations leading to wrong conclusions as failure modes.
- Anthropic's Claude Science announcement (read 2026-10-22): a reviewer agent that "checks citations and
  calculations" and flags "untraceable numbers", and figures that carry "the exact code and environment
  that produced it".

**Gap search (`grep -ci` over METHOD.md, WORKFLOW.md, CONTROLS.md at `a5e1b5f`):** 0 matches each for
`ethic`, `privacy|personal data|consent`, `causal|causation|correlat`, `observational|experimental
design|case study|design type`, `held.out|holdout|leak`, `pre-mortem|premortem`, `conflict of interest`,
`human subject|participant`.

## What broke (failures lead)

Each rule below is proposed only with a real incident that the method as written did not catch (M18).

| # | Incident | Where | Rule it motivates |
|---|---|---|---|
| F1 | People's data and restricted material were handled case by case. The EGRR contributor's evidence package carried his absolute local path in its records, and a path rule had to be written into the acceptance contract afterwards. The honeypot's third-party IP addresses were protected only by a line written ad hoc into one registration. A private repository was found holding another private repository's handoff notes, which would have been published with it | EGRR evidence intake (private report, 2026-10-22) and the acceptance contract's evidence rules; `experiments/pa_honey_001/PREREG.md`; the private repository is not named here | D1 C-PRIVATE |
| F2 | A design that cannot answer its question reached the intake stage. PA-QM-OBS-001 proposed an empirical consciousness-causation arm. The audit showed that, for its simplest model class, the hypothesis cannot be told apart from ordinary dephasing by any measurement. Nothing in SWAY asks what kind of claim a design can support | `docs/PA_QM_OBS_001_AUDIT_2026-10-22.md` §3.3 | D2 C-DESIGN |
| F3 | Selection and evaluation used the same data. EGRR's reported MSE improvement used "the same calibration inputs … for selection and evaluation". The dashboard card records this as the observation's limitation; no rule flagged it before it was reported | `data/dashboard/egrr_card.json`, observation 1 | D3 C-HOLDOUT |
| F4 | Two AI-generated summaries the owner received on 2026-10-22 attributed claims to Anthropic pages that do not contain them. Not on the cited pages: a five-step "AI scientific method", "318,000 protein designs", an "80% / 20%" split, firmware-level safety interlocks for the Model Hardware Standard, a QuEra lock in "6 seconds" over "700 trials", and Leica's involvement. The real items they mixed in (BootLoops, the Model Hardware Standard, QuEra's 99.3%) are on those pages. C-EXT requires claims to be checked, but it does not say that each claim is checked against the specific source cited for it | the two attachments; the pages, read 2026-10-22 | D4 (C-EXT, one added item) |
| F5 | Generated inputs were judged by counts, not by looking at them. DIFF-001's first generator produced 1,990 REFUSE and 10 DEFER in 2,000 cases, so it almost never reached the paths under test; this was caught only because the smoke run's decision mix was printed. A later synthetic red-team run reported as "96 scenarios" was 2 scenario classes repeated 48 times | `experiments/DIFF-001/PREREG.md` (sovereign-veritas, smoke 1 and amendment A1); the red-team run's record is private | D5 C-SYNTH |
| F6 | Instruments failed silently in ways a short pre-mortem would have named. The honeypot's port-80 sensor lost every request until D4, because two units shared a state directory: "could this record nothing?" was never asked. A dashboard test hard-coded "92 notes" and broke the next time a note was added | `experiments/pa_honey_001/DEVIATIONS.md` D4; `scripts/test_make_dashboard.py` (fix `452c8b4`) | D6 (W2, one added item) |
| F7 | A conclusion was drawn from a summary of a failure, not the failure itself. An AI-written briefing to the owner on 2026-10-22 concluded that note066 "can't go in as is" from a CI summary whose logs had not been opened. The raw log showed an unrelated dashboard-test fixture, already fixed in `452c8b4` | job `119793234107` log, principia-artificialis | D7 (W6, one added item) |
| F8 | **Self-reported deviation, this session.** WORKFLOW W7 says commits stage files by name, never `-A`. Claude used `git add -A` for PRs #92, #93 and #94 on 2026-10-22. Each diff was checked file by file before pushing and held only the intended files, but the rule was not followed | those PRs' commits | none (an existing rule, not followed) |

## Decisions (built in the next commit)

- **D1 — C-PRIVATE (new control, MUST when triggered).**
  - **Trigger:** the work collects, stores or publishes data about identifiable people (including IP
    addresses, names and messages), or handles material its owner marked private or restricted.
  - **Requires:**
    - say what is collected and why it is needed, and collect no more;
    - say who can see the raw data, where it is kept and when it is deleted;
    - say what is published, in what reduced form;
    - record the owner's or the contributor's permission for anything restricted.
  - Private-repository and restricted material never enters a public repository or a repository that may
    become public.
- **D2 — C-DESIGN (new control, MUST when triggered).**
  - **Trigger:** a claim goes beyond "this code, on these inputs, gives this output". That is, it is about
    a cause, a population, people's behaviour, or a field.
  - **Requires:**
    - name the design: experiment, observational study, correlational study, case study, simulation,
      audit, or literature review;
    - name the strongest kind of claim that design supports (causal, associational, descriptive, or
      existence);
    - state any claim stronger than that as out of scope.
- **D3 — C-HOLDOUT (new control, MUST when triggered).**
  - **Trigger:** anything is selected, tuned, trained or thresholded on data.
  - **Requires:**
    - the data used to decide is separated, before running, from the data used to judge;
    - the split is recorded with its identities (hashes or seeds);
    - a result judged on the deciding data is labelled in-sample and does not count toward the claim.
- **D4 — C-EXT, one added item.** Each specific claim taken from outside material is checked against
  the source cited for that claim, not only against the material that repeats it. AI-generated summaries
  are outside material. A claim that cannot be found at its cited source is recorded as not found there
  and is not used.
- **D5 — C-SYNTH (new control, MUST when triggered).**
  - **Trigger:** generated or synthetic inputs (generators, mutators, scenarios, synthetic datasets) feed
    a result.
  - **Requires, before the result counts:**
    - report how the generated cases fall across the outcome classes they are meant to reach;
    - report how many distinct kinds of case there are, as opposed to repeats;
    - have a person look at a small named sample.
- **D6 — W2, one added item: a pre-mortem.** The registration lists the two or three likeliest ways
  the instrument could record nothing, or the wrong thing, and how each would show up.
- **D7 — W6, one added item: open the raw output.** Before results are written, at least one raw output
  per prediction (a log, a file, a plot) is opened and read, not only a summary or an automated pass.
  This is the essay's "inspect plots and results yourself". When the raw output cannot be opened, the
  prediction stays `NOT RUN` or `UNRESOLVED`.

## Doors (not adopted; no incident yet, per M18)

- **A conflict-of-interest line** in registrations: who gains if the result comes out a certain way. This
  is relevant now that sovereign-veritas may be sold, but no case yet shows it would have caught
  something.
- **The AI's role per study** (generated cases, judged results, wrote code, drafted text), as an addition
  to M13.
- **Agreement statistics** (for example Cohen's kappa) when people or models classify text.
- **Question-selection bias** (*Claude-shaped science*): record why a question matters, apart from being
  easy for the model.
- **Model time estimates are not data:** measure runtime on a pilot instead.
- **Bring in experts early:** a named outside reviewer before a study in an unfamiliar field.
- **Physical devices:** where safety limits are enforced (device, driver or agent) before any agent
  actuates hardware. This connects to the Model Hardware Standard and to the existing no-actuation rule
  for the industrial gate.

## Predictions about the method (scored under M18)

| ID | Prediction | Credence | Window | Precisely wrong if |
|---|---|---|---|---|
| P1 | Each of the next 5 registrations across the estate answers every new trigger row (C-PRIVATE, C-DESIGN, C-HOLDOUT, C-SYNTH): none is left blank | 0.7 | the next 5 registrations, or 2026-12-31, whichever comes first | any of those registrations leaves a new row blank |
| P2 | At least 1 of those 5 registrations answers a new trigger "yes" and records a concrete design change because of it | 0.6 | same | none does |
| P3 | After the build, `method_lint.py` reports 0 violations, `--coverage` PASS and `--selftest` exit 0 | 0.9 | the build PR | any of the three fails |

## Build checks (migration, recorded in the build PR)

- `python scripts/method_lint.py`, `--coverage`, `--selftest` and `--sabotage` (expecting exit 1).
- The index excerpts in CLAUDE.md and NOTE_TEMPLATE.md are updated, and match.
- `methodology/RULE_INVENTORY.md` gains one `A4-Dn` row per decision.
