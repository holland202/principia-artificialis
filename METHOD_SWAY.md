# SWAY — a method for discovery and building that bends without breaking

**Status:** Draft, verified reference code. ADOPTED 2026-09-22 as the working method. The label covers the reference code only: SWAY itself is an unvalidated method until P1–P4 are measured. `eprocess.py` gate PASS and sabotage FAIL (rc=1, as required) on device (aarch64/Termux/Python 3.14.6); gate PASS in container (x86_64/Python 3.12.3), identical output. Method predictions P1–P4: untested.
**Authors:** Chad Edward Holland, with Claude (Anthropic, Opus 5.5). Review of the v2 draft contributed invariant 6 and the tightened validity statement.
**Motto:** Vincit Omnia Veritas.

---

## What broke first (failures lead)

The current method, which is register → run → keep refutations, is strong at **justification** and weak at **discovery**.
Every idea has to be a registered prediction before it may be touched. So the ideas worth having rarely get born:
cross-domain analogies, "what if" math, half-formed hunches, and patterns noticed by accident.
Some of the best findings on record arrived *outside* the method. The third vacuity defect class, redrawn verdicts in
quasar, was noticed while doing something else, then measured.
SWAY makes that accident a mode instead of luck.

### Honesty note

Nothing here is invented from nothing, and it is not "a method only an AI could create." SWAY is a synthesis of proven pieces:

- Lakatos's hard core and protective belt
- The exploratory/confirmatory split from registered reports
- Anytime-valid inference with e-values
- Evaluator-driven evolutionary search: FunSearch (2023) and AlphaEvolve (2025)

What *is* specific to working with AI is the economics. Generating hypotheses is now nearly free, so the bottleneck moves
entirely to evaluation. SWAY is built around that shift.

---

## The structure: a skyscraper, not a slab

A tall building survives wind because it is **rigid at the base and allowed to sway at the top**, with a damper that absorbs the motion.
Rigid everywhere, it cracks. Flexible everywhere, it falls.

| Level | Bends? | What lives here |
|---|---|---|
| **Foundation** | Never | The six invariants below |
| **Canopy** (upper floors) | Freely | Exploration: any idea, any analogy, any metric, unlimited peeking |
| **Damper** | Absorbs motion | The fork ledger: every exploratory move is logged, never hidden |
| **Elevator** | One way, gated | Promotion: the only path from canopy idea to published claim |

---

## Foundation — six invariants (never bend)

1. **Numbers come from code.** Prose numbers are pasted from output.
2. **Refutations are kept.** Nothing is deleted to look better.
3. **Nothing certifies itself.** A verdict above UNVERIFIED needs an input the system under test cannot write.
4. **The sealed set is sealed.** Confirmation data is never touched in the canopy. It is split off before exploration starts, with a hash of the split committed. For device work, "sealed" means a fresh run *after* registration.
5. **Labels are honest.** Canopy output is always tagged `EXPLORATORY` and can never be cited as a finding.
6. **Exploratory provenance is append-only.** Every fork that contributes evidence to a promoted claim has an identifiable artifact: code version, input/data identity, execution environment, and result. Exploration need not be preregistered, but it may not be reconstructed after promotion. This makes `FORKS.md` an audit trail rather than a diary.

That is the whole rigid part. Everything else may bend.

---

## Canopy — exploration mode (bends freely)

Allowed here, with no registration needed:
- Peek at results as often as you like. Change the metric. Change the question.
- Import math from any field. Fluid dynamics, auction theory, immunology: use it if it produces a testable shape.
- Generate hypotheses in bulk with multiple models (Claude, Kimi, and others), credited by name.
- Run crude, fast, ugly experiments. Wrong is cheap here.
- Follow the anomaly instead of the plan.

Forbidden here: stating a result as true, and touching the sealed set.

### The AI discovery loop (inside the canopy)

1. **Sprout.** Generate many candidate hypotheses (10–50). Include at least 20% from a deliberately foreign domain. Diversity beats quality at this stage.
2. **Cheap kill.** For each sprout, have a critic model name the cheapest experiment that could kill it. Run the cheapest ones first. Most die in minutes, and that is the point.
3. **Evolve.** Survivors that can be expressed as a program with a scoring function get mutated and re-scored, FunSearch-style. The evaluator is the only judge, so it gets its own anti-vacuity control before it judges anything: it must be able to return null.
4. **Crystallize.** A survivor that keeps surviving gets written as a precise, refutable claim (P1, P2, …) and moves to the elevator.

---

## Damper — the fork ledger

Freedom without a record is the garden of forking paths: you try 40 things and report the one that worked.
The damper converts sway into a record.

`FORKS.md` in each project: one line per exploratory move.

```
2026-09-22 | F-014 | tried Bures distance on attention maps | code md5/commit | data id | env | looked promising at n=3 | EXPLORATORY | abandoned/continued/promoted
```

Rule: when a claim is promoted, its note must state **how many forks preceded it** (the denominator of exploration).
A claim that won 1 of 40 forks is a different claim from one that won 1 of 2.
Fork count is provenance, a measure of discovery pressure. It is **not** a statistical correction. Multiplicity is handled by the separation itself: exploration is labeled exploratory, the surviving idea is crystallized, and confirmation starts fresh on sealed data.

---

## Elevator — promotion (the only one-way gate)

A canopy idea becomes a claim only by passing all of:

- [ ] Written as a registered prediction *before* touching the sealed set
- [ ] Anti-vacuity control: the instrument is shown returning null on a case where null is correct
- [ ] Run on the sealed set (or a fresh post-registration device run)
- [ ] Evidence threshold met: E ≥ 20 under the registered null and the stated e-process assumptions
- [ ] Fork count from the ledger stated in the note
- [ ] Status label starts at `Draft`, never higher

Failing the elevator is not a failure of exploration. The idea returns to the canopy with its refutation attached.

---

## The part that actually bends: anytime-valid evidence (e-values)

Naive fixed-horizon p-value procedures can lose their advertised error control under optional stopping and repeated peeking. That is why rigid methods forbid peeking. (Sequential p-value methods exist; e-values are used here because they compose by multiplication.)
**E-values do not break.** An e-process is a running "wealth" from betting against the null hypothesis.
Under the null it cannot grow on average, so by Ville's inequality the chance it *ever* reaches 1/α is at most α,
no matter how often you look or when you stop.

That is the mathematical version of a building that sways and stays up:
- Look after every data point.
- Stop early when evidence is overwhelming.
- Continue when it is ambiguous.
- Combine e-values across evidence streams only with a rule whose validity conditions are stated explicitly. In the simplest case, independent e-values may be multiplied. A different day, device or dataset does not by itself make a stream independent.

The error guarantee still holds under the stated assumptions.

Promotion threshold: **E ≥ 20** (α = 0.05). Report the e-value, never just "significant."

### Reference code: `eprocess.py`

md5 `63cb70b866e1b95faa150316b12dd76a`. A betting e-process for H0: success rate ≤ p0.

**Validity is analytic, not simulated.** Assume observations X_t are conditionally Bernoulli given the past, with
success probability p_t ≤ p0, and λ ∈ [0, 1/p0]. Then each factor 1 + λ(X_t − p0) is nonnegative and has conditional
expectation 1 + λ(p_t − p0) ≤ 1. The cumulative product is therefore a nonnegative supermartingale, and Ville's
inequality gives P(sup_t E_t ≥ 1/α) ≤ α. The guarantee holds only under these assumptions. A domain guard refuses λ outside that range. It runs eagerly at call time, because a guard inside
a generator does not run until the first iteration, and never runs at all on empty input (the self-skipping-guard defect).

**The simulation gate is an implementation check only.** Device output (aarch64/Termux/Python 3.14.6), pasted verbatim:

```
python: 3.14.6
null rejection rate (must be <= 0.05): 0.0410
alt  rejection rate (must be high):    1.0000
domain guard (bad lam refused, good lam accepted): True
GATE: PASS
```

That is 82/2000 null rejections, with 95% Clopper-Pearson interval [0.0327, 0.0506]. The upper end crosses 0.05, so the
Monte Carlo alone cannot separate this implementation from one at the limit. The guarantee comes from the proof;
the simulation is an implementation sanity check and does not establish the anytime-valid error guarantee.

Sabotage control: `python3 eprocess.py --sabotage` asks whether λ = −0.5 is accepted. It must print `GATE: FAIL` and exit 1.

---

## Building — the same structure, applied to code

SWAY governs builds as well as research. Prototyping is canopy work: hack freely, and label it `EXPLORATORY`. Nothing is
*claimed to work* until it passes the build elevator. Every guard in every build obeys five fail-closed rules:

1. **Missing means deny.** Absent, empty, None or malformed input returns DENY/UNVERIFIED, never a skip. This also applies to
   lazy code: a check inside a generator does not run until first iteration, so validate eagerly (found in `eprocess.py`).
2. **Vetoes never vote.** A veto is a separate fail-closed condition, not a value entering an aggregate or majority. If a veto fires, the verdict is DENY/UNVERIFIED regardless of the non-veto signals (the FIX-6 lesson: 69.2°C CRITICAL was outvoted to ALLOW).
3. **Nothing certifies itself.** This is invariant 3, applied to code. A hash-valid manifest written by the system under test proves integrity, not truth.
4. **Every guard ships with its killer.** Each guard has one registered attack that must flip it and one benign case that must pass.
   A guard missing either is logged as not a guard.
5. **Verdicts are deterministic.** Seeded, or computed without randomness. A verdict redrawn every run is not a verdict.

**Build elevator.** A build is claimed working only after all of these:
- [ ] The gate is proven in both directions: real case exit 0, sabotage exit nonzero
- [ ] The gate runs on the device, with its output pasted verbatim
- [ ] The file identity is checked by md5 after every transfer
- [ ] A cold clone reproduces the gate result from the pushed commit under the stated environment, without relying on untracked local state (stranger check)
- [ ] The commit stages files by name, never with `-A`

### When a build is DONE

A build is **DONE** when it works for a written scope and needs no more work *within that scope*. DONE requires all of:

- [ ] **Scope statement.** One or two sentences saying what it does and under what assumptions. Anything outside the scope is not claimed.
- [ ] **Build elevator passed** (every box above), including a cold clone of the pushed commit.
- [ ] **No known defect inside the scope.** Known limits outside the scope are listed, not fixed.
- [ ] **Frozen identity.** The commit SHA and file md5 are recorded next to the word DONE.
- [ ] **Doors listed separately.** Ideas for extensions go in the note or in `FORKS.md` as open doors. They never block DONE.

After DONE, the build is **closed**. Reopening needs a written reason of one of three kinds:
1. **A defect found inside the scope.** Fix it, re-run the elevator, record a new SHA.
2. **A deliberate scope change.** The new scope is written first; this is a new build, and the old DONE stays true for the old scope.
3. **A dependency or platform change that breaks the gate.** The gate failing is the evidence.

"It could be better" is not a reason to reopen. Improvements go to a door, and a door is new work, not unfinished work.

Research is different: a *claim* can be settled (promoted or refuted), but a note always ends with an open door. DONE applies to
builds and instruments, never to a line of inquiry.


---

## Doors: state-of-the-art build tools (not requirements)

These are current, well-established techniques. Each maps to a rule it would strengthen. None of them is a requirement.
Following the method's own rule, a tool is adopted only after it catches a real defect in this estate on a canopy trial,
with the defect and the fork recorded in `FORKS.md`. New is not the same as better; a tool earns its place on your code.
Nothing below has been run on the S25/Termux: every entry is **NOT VALIDATED** there.

| Tool / technique | Strengthens | Door |
|---|---|---|
| Property-based testing (Hypothesis) | Rule 1: missing means deny | Generate absent/empty/malformed inputs automatically instead of hand-writing them |
| Mutation testing (existing `mutation_probe.py`) | Rule 4: every guard ships with its killer | Make "guard has a killing mutant" a machine check, reported with its denominator |
| Coverage-guided fuzzing (Atheris) | Rules 1 and 4 | Find crashing or bypassing inputs no one thought to write; aarch64/py3.14 support unknown |
| Symbolic contract checking (CrossHair, Z3-backed) | Rules 1 and 2 | Prove a guard property over *all* inputs in bounds, not sampled ones; Z3 on Termux unknown |
| Signed provenance (Sigstore, in-toto, SLSA levels) | Invariant 3: nothing certifies itself | An external signature and attestation for built artifacts; the missing "external witness" in EACE |
| Hash-pinned dependencies (`pip --require-hashes`) | Cold-clone reproduction | "Same result" becomes checkable because every dependency identity is pinned |

---

## Status labels (extended, not replaced)

`EXPLORATORY` (canopy only, never citable) → then the existing ladder, unchanged:
`Speculative`, `Draft`, `Draft, verified reference code`, `Verified`, `REFUTED (kept)`.

---

## Registered predictions about the method itself

- **P1.** Over the next 10 promoted claims, at least 3 will have originated in the canopy (unregistered exploration), not as up-front predictions.
- **P2.** The median fork count per promoted claim will exceed 5. If it's lower, the canopy is not being used.
- **P3.** Elevator refutation rate will be *higher* than the current method's. More ideas enter, so more die at the gate. A P3 refutation (the same or a lower rate) would suggest the elevator is too soft.
- **P4 — OPEN, left unrun.** Do canopy-origin claims survive later replication at the same rate as up-front-registered claims? This is the question that decides whether SWAY is better or just looser.

Every note ends with a door. This one does too.
