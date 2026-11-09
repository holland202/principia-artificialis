# P12 — ChatGPT's second source review

2026-11-08 (America/Chicago; execution host 2026-11-09 UTC). Reviewed base:
`7452707568cac76fa589673dca54b5f8bf5c2348`.

## Limits first

The ratings were made without opening P10's handcheck or score, P12's key, or
the Amendment 3 TP list during this review. Prior conversation context contained
the aggregate P10 count, and older conversation history is compacted. Historical
blindness cannot be certified; do not describe this as fully blind.

This is a static source review by another vendor's AI, not an independent human
validation or a runtime test of the external projects. No dependency was installed
and no external project was executed. Files were retrieved at the packet's exact
commits and their bytes were verified against the Git blob hashes.

## Submitted ratings

[ratings_chatgpt.json](ratings_chatgpt.json) contains the frozen R01–R30 decisions
under the unchanged rubric in [PACKET.md](PACKET.md). Validation printed:

```json
{"ratings": 30, "verdict_counts": {"FP": 29, "TP": 1}, "ratings_sha256": "2d2bbe68b12e65c4eff1c7878246b7131fb168509b85c4b554f56fdb718301c8", "packet_sha256": "8b944d02f9191e9c8ad060857432f2675a65472113f19326c185c4acb3d5c030"}
```

[sources_chatgpt.json](sources_chatgpt.json) records the pinned files and relevant
helpers, their Git blob identities, SHA-256 hashes, and Python-3 syntax findings.
The packet rates findings; multiple findings can refer to the same file.

The substantive judgments are:

- R06 is an empty module in a unit-test directory. Under this rubric it is TP;
  this does not establish that NASA relied on it as a substantive acceptance check.
- The ECO-DQN files train or benchmark agents and save performance tables. The
  authors' README documents those uses. A performance experiment is excluded by
  the rubric even when its filename or function says "test".
- R19 and R28 have a real failure path: the imported `test_shared.run_tests_for`
  raises `ValueError` in the main thread after an output mismatch. A missing
  `test_*` function in the entry script does not remove that path.
- R07 is an import-only test, explicitly classified as able to fail by the frozen
  clarification. The dependency documentation generator, Selenium attribute
  explorer, model-inference script, visualizer and accuracy benchmark are not
  correctness checks. The Python-2 syntax cases are FP under the registered rule.

## Agreement is pending Claude's separate rerun

The owner relayed Claude's plan to rerun the agreement score after receiving these
committed ratings. ChatGPT has not opened the key or P10's verdicts and has not
run that scorer. This defers instruction step 2 to Claude as requested; it does
not change the rubric or any rating. Use the exact ratings commit in the PR:

```sh
python3 experiments/note052_p6/run_p12.py score experiments/note052_p6/results_p12 experiments/note052_p6/results_p12/ratings_chatgpt.json
```

Keep every disagreement, with both reasons, for Chad. Do not adjust a verdict to
increase agreement. An agreement statistic would describe this fixed review
packet; it would not validate the linter on all software.

Provenance (M13): ChatGPT (OpenAI, GPT-6; Codex agent) retrieved sources, applied
the rubric and wrote this record → human validation: not performed → human
editing/curation: direction only, Chad Holland → human responsibility: Chad Holland.

Door (unrun): Claude independently reruns the registered agreement scorer on the
committed ratings and preserves any disagreements before reporting a result.
