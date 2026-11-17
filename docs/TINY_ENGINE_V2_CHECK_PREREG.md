# TINY-ENGINE-V2-CHECK: bounded release qualification

2026-11-17. Source-informed, development-only; no novelty or independent scientific
validation claim. Chad requested checking and repairing the updated model and
authorized the necessary bounded tests. No training, merge, sealed cases, or
confirmatory campaign. METHOD/WORKFLOW/CONTROLS at
`6ec5c36b6b1210c7cc4af82850a2c0268ca077b1` govern this check.

## Question and scope

Do the repaired scorers reject the named bad inputs, and how do the existing v1
and v2 weights behave when asked to generate complete copies on a fixed public
development matrix? Any software repairs retain the historical scores and are
tested against the original source before and after. The architecture and weights
remain unchanged. The earlier 66–84% description has a later author measurement
of 58–85%; both have already been seen. This is not blind confirmation.

Subject source: `6ec5c36b6b1210c7cc4af82850a2c0268ca077b1` (#164).
Download all six released checkpoints of each version from immutable Hub revision
`360628f433a8c6be5280ed611a639c4e88f3c017`; record URL, SHA-256 and MD5 of every downloaded file and verify the Hub
manifest before inference. Refuse mixed source/weight identities. CPU PyTorch
2.5.1+cpu, safetensors 0.6.2, NumPy version recorded at execution. One CPU thread,
evaluation mode, greedy decoding, deterministic algorithms, no gradients.

## Fixed cases and counts

Three families (distinct symbols; draws from an eight-symbol alphabet; constant
symbol), crossed with source lengths 63 and 127. Six cells, 16 cases per cell:
96 source sequences, 12 trained checkpoints and two untrained controls, giving
1,344 model/case pairs. Generate each cell with NumPy default_rng seeded by
SeedSequence([20261117, family_index, length]), family order as written above.
Content IDs are 1..127. Distinct strings sample without replacement; alphabet8
chooses eight distinct symbols per case and samples positions with replacement;
constant strings use 16 distinct symbol IDs sampled without replacement per cell.
The prefix is BOS + source + SEP; generate exactly the source length. No EOS
contract is introduced. The same cases go to both versions and every checkpoint.

Report integer whole-string correct/total, correct tokens/total, each first-error
position (1-based; null on exact success), and paired teacher-forced counts.
Archive every source and generated sequence, config, checkpoint identity and
software/environment identity. These are descriptions of the fixed cases, not
estimates of reliability on arbitrary text. No p-value or population claim.
The symbolic reference returns the source exactly. Controls are untrained CFG and
CFG2 models, each initialized with torch seed 991. Uniform random full-vocabulary
guessing would have per-token match 1/130; the actual untrained networks need not
be uniform.

## Registered software expectations and diagnostic expectation

- P1: the unchanged #164 scorer refuses duplicates, missing/extra seeds, wrong
  configurations and nonfinite/out-of-range/missing scores; original v1 and v2
  score reports remain byte-identical. Run Claude's existing ten tests as reruns.
- P2: targeted malformed-JSON-object and seed-type checks return a controlled
  invalid-result response (exit 2, no scientific verdict). A JSON array/null or
  boolean seed must not be accepted or escape as an unhandled exception. This is
  a requirement to test, not an assertion that the present code meets it.
- P3: on each of the six paired trained seeds, v2 produces more exact distinct
  127-symbol copies than v1 among the 16 fixed cases. Strict integer comparison.
  This expectation is informed by published results and is non-confirmatory.
  Other matrix cells are descriptive, with no success threshold.
- P4: the symbolic reference is exactly correct on all 96 cases. Deliberately
  corrupting its first output symbol must trigger the audit's failure exit.

Before recording model comparisons, repeat the first distinct 63-symbol case
three times with v2 seed 1, recording logits/argmax identity. If outputs vary,
report noise and do not promote deterministic reproducibility. Do not tune any
behavioral threshold from this check. Interrupt on errors or a 15-minute inference
budget; keep partial outputs and mark remaining cells NOT RUN. No evidence-driven
early stopping, additional seeds, or retraining.

Scorer/schema repairs may follow observed counterexamples. Such repairs get new
tests that first fail on the pinned original. Rerun valid historical reports and
the original tests. A deliberate validator bypass must make the new test fail.
Model parameters are not changed in response to these development results.

## Controls, rivals, and pre-mortem

Rivals: teacher forcing masks autoregressive errors; distinct-only data makes
copying easier; a symbolic copier solves copying perfectly. Measure the first two
explicitly and retain the symbolic baseline. Untrained controls check chance-like
behavior without assuming uniformity.

Pre-mortem: (1) wrong version loads because tensor shapes coincide: pin version,
config and checkpoint hash together; (2) target tokens leak into free generation:
archive source-only prefixes and generated continuations; teacher forcing is a
separate call; (3) empty/malformed records masquerade as evidence: explicit count,
schema and controlled-failure tests. Raw cases expose masking/alignment errors.

| Trigger | Answer and implementation |
|---|---|
| Feasibility | Yes: counts above printed before registration; 12 checkpoints must download or inference stays NOT RUN. |
| Noise | Yes: three repeats before comparisons; fixed CPU execution and recorded identity. |
| Statistics | No population inference: integer descriptions of preselected cases only; no significance claim. |
| Evidence | Yes: valid, missing, malformed, wrong-config and replayed/duplicate records; no time-freshness claim. |
| Independence | Yes: Codex/OpenAI reviewing Claude/Anthropic, implementation-informed; no blind validation or retraining replication. |
| External | Yes: preserve exact Hub card and download identities; reported prior results are context, not this run's evidence. |
| Device | Yes: Linux CPU only; downloaded MD5/SHA-256 recorded; S25/GPU/NPU NOT VALIDATED. |
| Verdict code | Yes: explicit normal and sabotage failures; malformed input denies scoring. |
| Exploration | Yes: published results/code seen; software qualification and descriptive matrix recorded in FORKS.md. |
| Method comparison | No: not the estate's methodology-comparison study. |
| People's data | No: artificial token sequences and public repository artifacts only. |
| Design | Yes: software audit and bounded model diagnostic; supports existence/descriptive claims only, not causal mechanism or reliability. |
| Held-out | No promotion: all new inputs are public development cases; no tuning or confirmation from them. |
| Generated inputs | Yes: save counts, unique cases and first case of each cell; AI inspection only. Human sample review has not occurred, a declared C-SYNTH limitation; no scientific promotion. |

Next unrun door: a separately registered training intervention with fresh seeds
and untouched evaluation cases; cached phone inference measured on the S25.

Provenance: Codex (OpenAI; exact executing model identifier unavailable) authored
this plan after reading Claude (Anthropic Opus 5.5)'s code/results. Human validation:
none; human curation/direction and responsibility: Chad Holland; review level:
direction only. The diagnostic itself is self-tested and source-informed.
