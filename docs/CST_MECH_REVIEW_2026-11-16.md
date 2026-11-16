# CST review follow-up: shortcuts confirmed, scoring remedy not sufficient

**The cases are not ready for a scientific model assay.** Claude identified a naming shortcut
in Codex's qualification graphs and a repetition shortcut in Claude's original CST generator.
Codex reproduced both. The older Q1–Q5 instrument outcomes remain unchanged, but those checks
did not test shortcut resistance and must not be read as validating a source-tracing assay.

**Status:** POST-REVIEW AUDIT / EXPLORATORY / NO NEW MODEL INFERENCE.
Reviewed implementation: `d52981a3663a6c011d2d190b6fdb940beb531163`.
Claude review: [note 004](https://github.com/holland202/principia-artificialis/pull/153#pullrequestreview-5918948985).
Claude metric proposal: [note 003](https://github.com/holland202/principia-artificialis/issues/150#issuecomment-6914633536).

Provenance: Claude (Anthropic, Opus 5.5) identified the two shortcuts. Codex / OpenAI GPT-6 Astra
reproduced them and constructed the threshold counterexample below. Human validation: direction
only. Human editing/curation pending. Human responsibility: Chad Holland. This is cross-vendor
review followed by author reproduction of code properties, not independent model inference.

## What was run

```bash
python experiments/cst_mech_qual/review_20261116.py
python experiments/cst_mech_qual/review_20261116.py --sabotage
```

The [raw output](../results/cst_mech_qual/review_20261116.txt) is retained and was read before
writing this record. Expectations are retrodictions after review, not preregistered discoveries.
Exit zero means the audit reproduced the named failures, not that the generator is qualified.
Sabotage reverses the actual naming heuristic and must make the audit exit one.
Expected counts are exact; an empty or incomplete corpus cannot count as reproducing a shortcut.

Design: deterministic post-review audit, supporting existence/conformance claims on these
named inputs only. Mathematical validity: the displayed threshold counterexample is computed
exactly. Implementation validity: self-tested on Linux x86_64, Python 3.12.14. New empirical
model behavior: NOT RUN. S25/other-device execution: NOT VALIDATED.

```text
qualification naming heuristic: 32 / 32
original repetition heuristic: 320 / 320
AUDIT CHECKS REPRODUCED
DIGEST 5d0a39b66947754e383fb4f274308c397361612d76d5e1de6ba10d52e8dd61c7
```

The script reads rendered qualification records for the naming shortcut. It does not inspect
gold answers to choose predictions. For the original task it checks only `qual`, `dev`, and
`dev2`, using the fixed public-case counts described in the script. It has no confirmatory
split option. No sealed split or new model output is used.

## Corrections to the proposed metric interpretation

Claude's archive counts reproduce, but the statement that pair accuracy *equals* the marginal
product in every arm/depth does not. For example, the observed development D/hop-2 pair count
is 0 whereas the product expectation is 7/4; E/hop-2 is 12 versus 25/2. Approximate agreement
does not establish independent errors or that matched pairing is uninformative. The raw output
preserves exact fractions for every D/E archive cell.

Youden J is sensitivity minus false-positive rate at a decision threshold. It is a useful
descriptive measure, but is not generally invariant to a threshold shift. The script holds
all continuous scores and their discrimination fixed, then adds the same offset to both depths.

| Constructed scores only | J before offset | J after offset | AUC before and after |
|---|---:|---:|---:|
| Shallow | 1 | 1/4 | 1 |
| Deep | 1/4 | 1 | 1 |

This produces the desired J crossover without improving discrimination at either depth.
It does not prove that bias explains the archived CST observations; it refutes the general
claim that a J crossover alone rules that explanation out. d-prime likewise requires its
measurement assumptions to be stated, rather than being automatically treated as bias-free.

## Next gate, before any new inference

1. **Freeze a separate generator qualification specification.** Keep the old fixtures and their
   negative findings. Use opaque identifiers and shuffled record order. Balance which selected
   report has the indirect path. Explicit root/record types can be stated in the task; node-name
   suffixes must not encode the correct decision.
2. **Break superficial shortcuts by construction.** Include repeated irrelevant identifiers
   with genuinely distinct roots, and alias relations that share an origin without the same
   source spelling in both reports. Define alias semantics and whether they add logical depth
   before generation. Pair rewired graphs so superficial identifier counts can remain fixed
   while the correct answer changes. Review actual prompts for unintended new cues.
3. **Use exact fixture checks.** Test named suffix, repetition, position and substring heuristics
   on predeclared counterfactual pairs. Do not claim "at chance" because a binomial test on
   correlated, constructed cases failed to reject a null. Fixed-balanced conformance and an
   empirical chance-performance claim are different statements.
4. **Resolve the estimand.** Keep pair accuracy and per-truth confusion counts. Choose whether
   the scientific claim is an output crossover or improved source discrimination. The latter
   needs extra measurements or interventions that can distinguish discrimination from decision
   criterion. If using continuous log-odds/ranks, freeze extraction, answer-code mapping and
   scoring position before inference. AUC alone does not prove a tracing mechanism either.
5. **Then prepare a concrete pilot.** Lock exact prompts, model files, tokenizer/runtime,
   raw-response schema, independent scorer, controls, failure rules and compute budget. The
   previous proposed response count is provisional until foil/control counts are fixed. The
   real-model pilot and confirmatory campaign remain unrun. Chad retains campaign and merge approval.

Codex owns the generator/qualification changes. Claude is asked to challenge the construction
and supply an oracle with its actual review exposure recorded. The other ChatGPT session owns
revision of #152's estimand and primary gate. Another model's review is not independent model
reproduction. No participant should duplicate inference while this assay gate is unresolved.

## Additional prior art

Claude supplied *Evidence Laundering: Deep Research Agents Mistake Correlated Sources for
Independent Evidence*. Codex fetched the [primary PDF](https://aclanthology.org/2026.emnlp-main.509.pdf)
and inspected the corpus design, reported contrasts, provenance defense and limitations. It
studies correlated-source credence and a structural provenance defense, with copied and
cross-linked auxiliary variants. This is further prior art for the broad failure mode, not
proof of the exact CST depth/instruction crossover. The [supplemental source record](external/discovery_audit_20261115/sources_20261116.json)
retains a short verbatim excerpt and PDF hash without altering the earlier source snapshot.

The earlier shortlist remains provisional. No novel result has been established. If the
corrected cases cannot distinguish a source-sensitive response from the mundane rivals, stop
this candidate and move to the next ranked hypothesis rather than rescuing it after the fact.

## Validation record

The original recorded qualification output still matches byte for byte. The new audit reproduces
both shortcuts and the constructed threshold counterexample; its live naming-rule sabotage exits
one. The pinned vacuity lint reports no findings in the package, and method lint reports no
violations. These are author checks, not independent scientific validation.

The first suite attempt could not import pytest. A temporary Python 3.12.14 environment with
pytest 9.2.0 was then used. Its first complete run reported two dashboard failures because this
single-branch clone lacked the pinned FIT-001 commit. Fetching
`02ef6d1eadc245041ff371e256e411e0c79a02cc` resolved those failures without changing tracked code.
Both runs and the initial import failure remain in `results/cst_mech_qual/review_20261116*`.
The completed rerun printed:

```text
478 passed, 7 skipped, 2 warnings, 111 subtests passed in 4.39s
```

The existing W7 scope exception remains: `experiments/cst_001/test_cst001.py` was excluded
because it instantiates the old sealed split. The warnings concern an existing pytest-plugin
deprecation and a pre-existing RMT mutation's invalid divide. No failure was fixed by relaxing a
test or changing research outputs. The [environment record](../results/cst_mech_qual/review_20261116_environment.json)
and [file hashes](../results/cst_mech_qual/review_20261116_manifest.sha256) identify this audit.
