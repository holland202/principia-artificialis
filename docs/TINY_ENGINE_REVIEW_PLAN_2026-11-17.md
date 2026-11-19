# TINY-ENGINE review: public software qualification plan (2026-11-17)

Status: source-informed qualification only. No model training, new model inference,
sealed cases, or scientific confirmation is authorized by this plan.

Question: do the released artifacts support their stated measurement scope, and
does the score reader require the registered distinct seeds?

Subject: main `c64be1cb0e2b7680f79705a26e266f399aa02e24`;
tiny-engine package `e3f170ac2e54e72b26f24716d98fd4296e403887`;
RMT package `f083431d5177a2348e8fd68949973f758fa02be1`.
METHOD.md at the main pin governs. The source, card, registration, and archived
scores have already been read. Predictions below are therefore source-informed
software expectations, not novel scientific hypotheses.

## Fixed checks, registered before execution

- P1: executing the original score.py on the original six archived seed files
  prints Q1 HELD, Q2 FAILED, Q3 HELD and exits zero. This is an observation of the
  existing reporting contract, not by itself a claim that exit zero is a defect.
- P2: five copies of the public seed-1 record under distinct seed filenames but
  with the same internal seed ID make original score.py print Q2 HELD.
  This would demonstrate that file multiplicity can substitute for distinct
  registered training seeds. No synthetic record is scientific evidence.
- P3: an empty result directory prints FAILED for all three criteria and exits
  zero. It should not be interpreted by automation as valid or complete evidence.
- P4: the unmodified task_copy generator, evaluated with one NumPy RNG seed (17)
  at T=128,256,512, produces respectively 63,127,127 scored target tokens. The
  latter two samples have identical source/target prefixes; the final sample has
  256 trailing padding tokens. These are implementation counts, not AI scores.

The instrument imports/runs the real source, never a rewritten task generator.
If PyTorch is unavailable, P4 may compile only the original task_copy AST node,
with its original scalar constants and NumPy. That dependency isolation must be
declared and is not a model-execution check. P1-P3 run original score.py as a
subprocess in temporary directories. No production or historical file is edited.

Instrument control: a --sabotage mode changes the expected P1 verdict to an
incorrect one. It must exit nonzero, while the normal instrument must agree
with its recorded observations. The audit's output is pinned separately after
execution. Empty/duplicate input cases are the production scorer challenges.

## Package cleanup

Before deleting either specifically requested temporary branch, compare every
package file with the corresponding public Hugging Face repository at a recorded
revision. Verify small text files by Git blob identity and weight bytes by the
Hub's SHA-256 metadata against local Git bytes, and verify local manifests.
Record the distinction between metadata comparison and downloading every remote
weight. Retain both package commit IDs. If any file lacks a matching public
copy, leave that branch intact. Do not delete experiment branches, tags, or notes.

## Scope, rivals, limits

This is an implementation audit supporting only descriptive/existence claims.
The mundane rival is that the card describes token accuracy and the scorer is
only a report printer; preserve that interpretation and request clearer labels,
not retroactive changes to registered outcomes. No new behavior or independent
model validation can follow. Whole-string autoregressive accuracy, EOS behavior,
repeated-token copying, and novel mechanisms remain unmeasured.

Most likely failures: wrong package/source pin; inadvertently executing training;
misreporting teacher-forced accuracy as free generation. Hash source files, run
only the named scorer/generator, and keep model execution NOT RUN.

## Controls

| Trigger | Answer and implementation |
|---|---|
| Feasibility | yes: list exact package/result files and scored-target counts |
| Noise | no: no model/timing claim; fixed seed and deterministic source checks |
| Statistics | no: no population estimate, effect test, or sampling claim |
| Evidence | yes: original, absent, duplicate/replayed records; freshness is pinned |
| Independence | yes: implementation-informed Codex review of Claude; not blind |
| External | yes: preserve public model-card/source references and source hashes |
| Device | yes: record environment and transfer hashes; phone remains unvalidated |
| Verdict code | yes: wrong expected result must flip audit exit status |
| Exploration | yes: source and public scores seen first; record in FORKS.md |
| Method comparison | no: this does not evaluate the estate's methodology |
| People's data | no: synthetic public tokens; no personal datasets |
| Design | yes: bounded implementation audit; causal/model claims excluded |
| Held-out | no: published checks choose no model; do not open sealed datasets |
| Generated inputs | yes: inspect named copy seed and duplicate fixtures; human inspection pending |

Provenance: Codex (OpenAI; exact executing model identifier is unavailable in this
runtime) reviews code by Claude (Anthropic Opus 5.5). Human validation: none.
Human direction/curation: Chad Holland. Responsibility: Chad Holland.
Review level: direction only. This is source-informed cross-system software work.

Unrun door: a separately approved frozen-weight pilot measuring free-running
whole-string accuracy and first-error position across all six checkpoints,
varying source length, source-target distance, and symbol repetition separately.
