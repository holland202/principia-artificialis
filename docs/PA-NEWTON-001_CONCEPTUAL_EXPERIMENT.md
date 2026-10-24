# PA-NEWTON-001 — Conceptual experiment: authorization-to-physical-effect binding in a simulated robot

**Date:** 2026-10-14  
**State:** CONCEPTUAL DESIGN / UNFROZEN PROPOSAL — **NOT RUN, NOT VALIDATED, NO EXPERIMENTAL RESULT**  
**Category:** candidate physical-AI / robotics safety experiment; not a numbered PA research note or a new finding.  
**Research direction:** Chad Holland (proposal to use NVIDIA Newton with PA and Sovereign Veritas).  
**Drafted by:** ChatGPT (OpenAI GPT-6); **human review:** direction only, not line-by-line. The NVIDIA training material belongs to its authors; no affiliation or endorsement is implied.  
**Method reference:** [METHOD.md](../METHOD.md), [WORKFLOW.md](../WORKFLOW.md), [CONTROLS.md](../CONTROLS.md) at PA main commit `05078579b674f8a93cc56de4eba3d5fa6511d159`; rules referenced by ID only.  
**Source identity:** [NVIDIA Newton course learning objectives, user-supplied excerpt](external/nvidia_newton_fundamentals_user_excerpt_2026-10-14.md).  
**Related external project (read-only):** [Sovereign Veritas](https://github.com/holland202/sovereign-veritas), **v0.2.0 maintenance-only**, release tag `ecd4de9`; do not change that repository for this experiment. Confirm full annotated tag and exact source commit before building an adapter.  

> **Status note, 2026-10-22 (W9).** Sovereign Veritas's maintenance-only period ended on 2026-10-22 ([sovereign-veritas #88](https://github.com/holland202/sovereign-veritas/pull/88)). The lines here that call it maintenance-only are kept as written on 2026-10-14. This experiment still treats SV as read-only and version-pinned by choice.

**Status axes:** Mathematical: NOT RUN; implementation: NOT RUN; empirical: NOT RUN. Simulator/physics integration: NOT BUILT.

## Central falsifiable question

> In a pinned NVIDIA Newton robot simulation, does an existing Sovereign Veritas authorization and its exported verification record actually bind **the exact command that the simulator consumes and the observed simulated effect**, or can post-decision substitution, missing/stale state, or incomplete effect records permit a mismatch while the offline verifier still reports the package internally consistent?

The question is about **whether different observations are bound together correctly**, not a claim that Newton, a signature, or Sovereign Veritas proves physical truth. A failure under a constructed perturbation may be a useful observed limitation; a pass must not be extrapolated to physical robots.

## Motivation / existing negative findings

Sovereign Veritas already documents mismatches between authorized action records and execution/effect boundaries: [SV-ATTACK-001 Q1/Q3](https://github.com/holland202/sovereign-veritas/blob/main/docs/SV_ATTACK_001_RESULTS.md), [EO-1](https://github.com/holland202/sovereign-veritas/blob/main/docs/EO1_RESULTS.md), and [execution-boundary results](https://github.com/holland202/sovereign-veritas/blob/main/docs/EXECUTION_BOUNDARY_RESULTS.md). Those are **previously reported results in another harness**, not predictions of what Newton will show. Reproducing the same class of defect in Newton would be an *extension to a new simulated substrate*, not evidence of novel physics or a novel attack.

NVIDIA's [Newton Fundamentals](https://docs.nvidia.com/learning/physical-ai/getting-started-with-newton/latest/newton-fundamentals/overview.html) covers the `ModelBuilder` → `Model` → `State`/`Control`/`Contacts` → `Solver` stepping loop, CUDA graph capture, Franka control, IK and rigid–deformable coupled manipulation. The [coupled manipulation lesson](https://docs.nvidia.com/learning/physical-ai/getting-started-with-newton/latest/newton-fundamentals/coupled-manipulation.html) uses a `SolverMuJoCo` arm, `SolverVBD` cable and `SolverCoupledProxy` to expose gripper contact to the cable. These are external vendor-described **capabilities**, not PA measurements or endorsement.

## Staged instrument design (not implemented)

**Stage 0 — preflight only.** Before preregistration, check the chosen exact Newton revision, dependency/license/asset source, GPU compatibility, solver variant, simulation determinism, collision and gripper behavior, and the Sovereign Veritas v0.2.0 tag. Produce feasibility counts and version/environment fingerprints **without examining sealed experimental cases**. A cloud CUDA GPU is a plausible target; the Snapdragon S25 is a control/review terminal rather than an assumed CUDA executor. No cloud allocation has been authorized by this document.

**Stage 1 — minimal arm control.** Use the smallest reproducible rigid Franka scene before cable deformation. Capture at least four *separately owned* records, with declared writer/provenance:
1. Proposed request: pose or joint-target vector, units, frame, allowed workspace, deadline and nonce.
2. Gate input and decision: frozen command bytes/semantic canonical form, policy, evidence freshness/identity, Gate version/digest, `ALLOW`/`DEFER`/`REFUSE`.
3. Simulator-consumed command: exact joint target/torque buffer values **after IK and immediately before** the solver step; hash raw typed arrays and keep raw arrays. The proposal-level task-space pose is **not identical** to a joint-space control vector, so bind the explicitly authorized transformation/IK version or authorize the resulting joint vector.
4. Observed simulator effect: joint state, end-effector pose, contacts, any cable state, timestamps/step indices. This is simulated observation, not a physical-world effect receipt.

Use an *independent trace collector* that is not writable by the proposer/gate-wrapper, as far as the design permits. Calling the same wrapper twice is not independent. Specify what can attest to the actual GPU-consumed buffer and what cannot; naive host-side logging is not proof.

**Stage 2 — deliberate changes.** Introduce post-approval command substitution, stale/unavailable runtime evidence, nonce reuse, erroneous measurement labeling, and a guard-bypass/no-op executor case. All interventions use harmless local simulation fixtures, not real robot controllers. In cases explicitly intended to violate constraints, a refusal or mismatch should be observable; avoid an instrument that always returns FAIL or always returns PASS.

**Stage 3 — cable manipulation (conditional).** Only after the rigid-arm control works, adapt the course's Franka/cable pick-and-place example. Separate command-envelope checks from physically simulated metrics: gripper-payload contacts, payload position, workspace corridor, overshoot, deformation, and solver stability. Register numeric tolerances from independent calibration runs and preserve units and coordinate frames. Handle contact solver nondeterminism before interpreting any numerical threshold.

**Stage 4 — optional performance comparison.** If stable, investigate Python/driver overhead and CUDA graph capture. This is a separate performance experiment, with version-specific warm-up, matched workloads and repetitions; never assert vendor example timing as a PA result. CUDA graph capture can replay previously captured buffers; the design must explicitly test whether changing authorizations and target values is correctly reflected inside captured execution.

## Candidate test matrix (ideas only, NOT a frozen registration)

| ID | Candidate intervention | Observable contrast | Candidate interpretation; all NOT RUN |
|---|---|---|---|
| N1 | Benign authorized, fixed target | Gate ALLOW; bound target equals simulator-consumed control; trace explains resulting motion | Establish a positive baseline and measurement path |
| N2 | Explicit REFUSE / DEFER and no approved substitute | No actuator-target update is consumed from rejected request | Negative path; does not prove all bypasses absent |
| N3 | Mutate target vector **after** ALLOW, before solver | Source authorization target ≠ consumed target; cross-boundary checker rejects | Test time-of-check/time-of-use binding |
| N4 | Replace fresh sensor evidence with unavailable or stale evidence | Explicit evidence policy returns documented reject/defer outcome; no silent promotion to fresh | Gate policy and evidence freshness must be version pinned |
| N5 | Replay old authorized command for new timestep or nonce | Replayed command refused or separately labelled; old record retained | Freshness must be enforced beyond hash equality |
| N6 | Bypass executor guard or record wrong/no-effect while verifier reads only wrapper record | Independent consumed-command/effect trace disagrees with wrapper package | Distinguish internal consistency from physical-simulation evidence |
| N7 | Captured GPU execution graph continues after command changes | Compare authorized/consumed buffers and recorded state under direct launches vs capture | Detect stale binding; no assumed failure |
| N8 | Arm grasps deformable cable; deliberate target or parameter alteration | Contact and payload trace differ from authorized action under registered quantitative limits | Requires validated Stage 1 and separate calibration |

**No pass thresholds have been frozen.** Before any confirmatory run, choose exact scene, seeds/replications, perturbations, time windows, tolerances, correct notion of consumed control, and predictions with explicit `HELD`/`REFUTED` criteria in a separate `docs/PA-NEWTON-001_PREREG.md` **commit before running** (M2/W2). Any exploratory test stays EXPLORATORY and never becomes retroactive confirmation (M11/C-EXPLORE).

## Baseline, anti-vacuity and attack requirements

- **Simplest rival (M14):** direct comparison between an immutable approved command payload and the consumed control, plus an independent post-step state/event log. Also compare a plain policy check (or OPA/Cedar adapter if scoped later) with the full evidence-package verifier **without attributing all benefits to the gate**.
- **Anti-vacuity (M3):** benign case passes while a planted unauthorized vector alteration reliably flips the check; record separate simulator guard-bypass and collector-bypass controls. A checker that always rejects is a broken instrument.
- **Independent source truth:** signed or digest-consistent *records* can still faithfully contain untrue sensor reports. An independent simulated effect probe requires different ownership and a separately checkable ground-truth instrument. Even that cannot establish real-world safety.
- **Hazard scope:** simulation only. No publishing action commands for real robot hardware, no network-controllable actuators, and no autonomous execution of third-party supplied code.
- **Immutable provenance:** pin full SHA for PA, Newton, relevant URDF/assets, the frozen Sovereign Veritas revision, adapter and independent collector; preserve scene, config, environment, input traces, simulation stdout/stderr, exit codes and hashes. Capture physical GPU properties, driver/CUDA/Python/library versions, expected vs observed. Runs on another platform are NOT VALIDATED until separately observed.

## Trigger assessment — preliminary design, not a frozen W2 registration (M16)

| Trigger | Control | Candidate answer |
|---|---|---|
| Feasibility | C-FEAS | yes: test cases, asset availability and eligible GPU/scene configurations determine whether the design can run |
| Noise | C-NOISE | yes: floating-point GPU and contact/IK solver outcomes may vary; repeated-input calibration before bounds |
| Statistics | C-STAT | yes if any reported rate, speedup, mean or sample-derived comparison is claimed; no statistical claims yet |
| Evidence | C-EVID | yes: fresh, stale, unavailable, contradictory, same-source derived, and replayed evidence cases must be addressed |
| Independence | C-INDEP | yes: verifier, collector, gate and author must be separately identified; same-author runs are self-tested |
| External | C-EXT | yes: Newton and Sovereign Veritas are external to PA's experiment; source/copy identity must be recorded |
| Device | C-DEVICE | yes: GPU/OS-specific behavior and transfers require device evidence; S25 remains NOT VALIDATED |
| Verdict code | C-BUILD | yes: no unchecked/missing inputs can result in an invented PASS or unauthorized motion |
| Exploration | C-EXPLORE | yes if there is any preliminary solver iteration or calibration used to shape the study |
| Method comparison | C-METHCOMP | no, unless a later proposal explicitly claims competing methodology effects; if triggered use its protocol |

## Scope exclusions and interpretation

- NOT CLAIMED: an implemented Newton adapter; runnable Franka simulation; CUDA speedup; validated AI control; physical hardware safety; independent security assessment; proof that the Gate can authenticate measurements or certify true physical effects.
- Do not add features directly to Sovereign Veritas v0.2.0 (maintenance-only). Put **read-only/version-pinned compatibility code** in a new PA experiment module after registration. Do not weaken or silently override original policy.
- A deliberate attack that achieves unauthorized simulated movement may be a supported counterexample to a *specific binding claim*. It does not establish a rate, physical deployment exploitability, or a universal negative.
- Never treat prior `CONSISTENT` outcomes, Newton solver success, and independently observed simulated effects as synonymous.

## Expected artifact / output schema (future proposal)

A validated experiment run would preserve: `experiment_id`, `registration_commit`, `scene_sha`, `gate_revision`, `sim_revision`, `toolchain`, `run_nonce`, `requested_task`, `approved_control`, `consumed_control`, `trace_hash`, `simulated_effect`, `evidence_origin`, `runtime_state`, `prediction_outcomes`, `deviations`, `exit_code`. The independent collector's origin and trust boundary must be explicit. Store bulky raw arrays in separate hash-identified files, not only a prose summary.

## Open doors (M15)

1. Confirm exact public versions of the Newton coupled-solver example and its runtime requirements; verify license/asset access and clean clone.
2. Define stable command identity across task-space pose → IK → joint target; choose numeric canonicalization and which transformations authorization covers.
3. Establish independent collection of simulator-consumed GPU buffers and physical-simulation state, including checks for captured-graph stale buffers.
4. Register a preflight feasibility/sabotage protocol with device/environment and bounded cases before code or experiments.
5. Study whether PA's Scientific Lineage Lab can ingest **clearly labelled** future results without automatically promoting a reported prediction outcome to scientific truth. That interface is separately under draft review in PR #49.

**Decision:** record for technical review and future preregistration; **do not execute** or allocate cloud resources on this intake alone.

*Vincit Omnia Veritas — Truth Conquers All.*
