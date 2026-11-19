# CST-MECH-QUAL-001 instrument qualification registration

2026-11-15. **REGISTERED instrument checks only. AI-behavior study NOT REGISTERED / NOT RUN.**
Method pin: `ed2e9dd3b5d7123aab8388b7738ff97c9ed349c7` (METHOD, WORKFLOW, CONTROLS).
Review target: PR #152 at `fe8997441bfbcaaf3be0fb679fc706a47800a628`.
Owner: Chad Holland. Design and implementation: Codex, OpenAI GPT-6 Astra.
AI participation → human validation: direction only → human editing/curation: pending
→ human responsibility: Chad Holland. Same-vendor review of ChatGPT's proposal, self-tested
instrument. No independent model execution or scientific validation is claimed.

## Question and scope

Can an executable qualification package distinguish the proposed positive interaction from
the stated shallow-harm/deep-benefit crossover, and reject corrupt source-task archives?
This is a deterministic software audit. Constructed outcome tables and fabricated response
fixtures are stand-ins, explicitly not outputs of an AI model. They cannot establish any
empirical effect. No inference backend, development split, or confirmatory split will be added.
No old sealed data will be instantiated, read, or compared for content overlap.

## Fixed predictions, before implementation or execution

- **Q1:** A constructed table with a shallow benefit in one quarter of blocks and a deep
  benefit in every block satisfies #152's proposed interaction gate, while a crossover gate
  requiring shallow harm rejects it. Use exactly 64 blocks, binary paired correctness, an
  interaction threshold of 1/4 and an exact one-sided nonzero-sign tail at most 1/20.
  This is a counterexample to the gate's interpretation, not a model-behavior refutation.
- **Q2:** A proposed directional gate accepts the planted full crossover and rejects no effect,
  deep-only improvement, both-depth benefit, and the reverse crossover. Require mean shallow
  change at most -1/8, mean deep change at least 1/8, and the respective directional exact
  sign tails at most 1/20. Their conjunction is an intersection-union test conditional on
  independent blocks and the sign-test nulls. It is not a confidence interval for either mean.
  A generic arm reproducing the tracing arm must defeat an additional specificity check.
- **Q3:** Qualification graphs have two distinct terminal roots, two selected final reports,
  and two intermediate records. Fixed-width identifiers and identical record counts keep
  graph rendering length constant across depth/truth transformations. Both reachable-root
  equality and inequality occur at maximum depths one and two, in both report orders and
  both answer-code mappings. An independently specified terminal-label propagation oracle
  and path-following oracle agree on every qualification graph. Cycles and dangling edges
  are rejected, including in unused records. Renaming nodes cannot change the gold decision.
- **Q4:** The result reader rejects empty, missing, duplicate, extra, wrong-prompt-hash, and
  malformed-schema archives. A completion scores only with exactly one canonical decision
  line at the end and a normal stop. Ambiguous, truncated, or missing decisions score wrong.
  Always-one-label responses score no correct SHARED/INDEPENDENT pairs. This is qualification
  conformance, not a proof that every invalid archive is detected.
- **Q5:** Hand-computable exact sign-tail boundaries agree, ties do not count as successes,
  and impossible inputs are rejected. Normal qualification exits zero. `--sabotage` inverts
  the graph answer oracle on the actual scoring path and must make the same gate exit one.

The fixture manifest will use only the literal namespace `CST-MECH-QUAL-001`, fixed synthetic
graph blocks, N/T/G instruction conditions, and long-format responses. No seed selector exists.
Counts and hashes will be printed by the implementation and committed with the raw results.
The final instrument outcome/digest will be pinned in a subsequent commit (W4).

## Rival, pre-mortem and limits

The simplest rival is that a positive interaction is only a larger improvement at depth two.
Q1 puts this rival directly through the proposed gate. Generic-carefulness equality is a second
explicit fixture. Matching characters in a graph does not establish tokenizer matching or equal
semantic difficulty. Both oracles are by one author and require a blind external implementation.

Likely failures: a duplicate silently overwrites a record (Q4), a final-line parser accepts two
answers (Q4), or an inverted oracle is not on the live path (Q5). A failing qualification blocks
any claim of a qualified instrument. It does not authorize repair of a scientific hypothesis.

No p-value on these selected fixtures is empirical evidence. Report exact rational values.
Proposed effect margins are instrument constants, not a frozen scientific protocol. Runtime,
model/tokenizer identities, sample-size justification, human case review, noise checks, new
holdout custody, and independent scoring must be resolved before a model study is registered.
Do not open the old holdout to prove disjointness. A custodian can compare sealed fingerprints
later without disclosing prompts. New qualification cases are permanently ineligible for confirmation.

## Triggered controls

| Trigger | Control | Answer |
|---|---|---|
| Feasibility | C-FEAS | No sampled-input eligibility claim. The deterministic fixture matrix is defined here. Print its counts before any future scientific registration. |
| Noise | C-NOISE | No stochastic inference or timing claim. Future inference requires separate repeated-input qualification. |
| Statistics | C-STAT | Yes, test exact-tail arithmetic on constructed tables only. No inferential claim from them. |
| Evidence | C-EVID | Yes, shared/derived and independent roots only. Freshness, staleness, contradiction, unavailable observations and replay are out of scope. |
| Independence | C-INDEP | Yes, self-tested and same-vendor review. Independent validation pending. |
| External | C-EXT | Yes, source excerpts and hashes in the discovery audit's external-source record. |
| Device | C-DEVICE | No device claim. Record the local environment without extrapolation. |
| Verdict code | C-BUILD | Yes, eager validation and sabotage on the live oracle path. |
| Exploration | C-EXPLORE | Yes, inherited CST development observations shaped the candidate. Record this audit fork. No confirmatory outputs inspected. |
| Method comparison | C-METHCOMP | No estate-methodology comparison. This is instrument qualification. |
| People's data | C-PRIVATE | No personal data. Synthetic identifiers only. |
| Design | C-DESIGN | Yes, deterministic audit and literature review. Existence/conformance only. |
| Held-out | C-HOLDOUT | No evidence is used both to select and judge an empirical claim. These are public qualification fixtures. Old holdouts remain untouched. |
| Generated inputs | C-SYNTH | Yes, print the matrix and retain named samples. Human inspection remains pending and prevents promotion to a scientific assay. |

## Next unrun test

A reviewer who has not seen the implementation writes a graph oracle and audits the proposed
statistical test. Then separately register and qualify the real-model runner. Owner approval
is required for a confirmatory campaign and any merge.
