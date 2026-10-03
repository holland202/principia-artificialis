---
name: "experiment-first"
description: "Standing procedure for Chad's research/engineering: answer questions about system behavior by building the smallest executable test against the real code, not by explaining. Use for SV, governance, evidence, agents, perf, critiques."
---

# Experiment-first working procedure

Principle: explain less when direct experimentation can reveal more. Executable artifacts are instruments for investigation, not lessons. This is not a teaching workflow.

Use it when the question is about how a mechanism, rule, algorithm or system actually behaves and a small test can answer it. Skip it for pure definitions, history, or decisions that only Chad can make.

## Procedure

1. **Question.** State the observable question in one line, separate from interpretation. If a running test cannot settle the question, say so and stop here.
2. **Smallest instrument.** Build the minimal test, harness or simulation that isolates it. Run the real repository code where possible, not a reconstruction. State every assumption and every stand-in ("model", "fake backend", "constructed input").
3. **Variables.** Change one condition at a time. Include the boundary cases and the adversarial ones. For evidence questions, use the default ladder: fresh → stale → unavailable → contradictory → derived-from-the-same-source → replayed.
4. **Predict first.** Write expected outcomes before running. If the result will be published or relied on, commit the predictions before the code (prereg-first), as the repos already do.
5. **Run and record.** Keep the raw output, the commit hash, the platform and the command line. Pin a digest when the result should be reproducible.
6. **Compare.** Report every disagreement between prediction and outcome. Keep failures and refutations. A held prediction is not evidence that the system is valid.
7. **Mechanism.** Explain why it happened only after observing it, and tie the explanation to specific code or spec lines. Mark interpretation as interpretation.
8. **Attack.** Try counterexamples, malformed inputs and boundary cases. Include an anti-vacuity control showing the instrument can fail (a sabotage switch, a planted defect). Ask which assumption would have to break for the conclusion to be wrong.
9. **Status.** Label each claim with exactly one of: observed / reproduced / supported / not supported / refuted / unknown / not tested / simulation-only. Never upgrade a simulation, a constructed input or a model result into a real-world claim.
10. **Preserve.** Keep the question, predictions, assumptions, matrix, code, raw results, interpretation, limits, corrections, provenance and commit. Results are appended to, never rewritten.

## Self-validation rule

Claude's own explanation, experiment design, interpretation or code is never independent validation of itself.

- If Claude designed the test, and the test agrees with Claude's prediction, record it as **self-tested**.
- An attack Claude runs on its own work is weaker, and is labeled that way.
- Independence requires one of: a separate reviewer that has not seen the build (another agent or model, labeled as same-vendor if it is), a human reviewer, or reproduction by another person.
- Two Claude sessions are not independent of each other unless provenance shows it.

## Provenance

State the chain: AI participation → human validation → human editing/curation → human responsibility. Name the model. State only the human review level that actually happened (line-by-line / outcome review / direction only).

## Output shape

Give results, not lessons: the prediction, what happened, the status label, the limits, and the next unrun test. Prose explanation is kept to what the evidence needs.