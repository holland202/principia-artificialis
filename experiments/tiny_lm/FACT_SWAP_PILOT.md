# Tiny Engine fact-swap pilot

Draft for design review. Awaiting a synthetic sample. Predictions remain open. Run status: not started.

Can the existing lookup checkpoint follow a changed fact in its input? Use invented key–value records. For example, query locker K7 twice with the same question and distractors. Replace its value, compass, with whistle on the second input. Score the pair as correct only if both exact answers match their respective records. Report the number of correct pairs and the denominator.

Claude: inspect the public lookup checkpoint, its vocabulary, input grammar and inference entry point. Pin the revisions and show how each record, the query and the decoded answer map to symbols. Use one fixed mapping across each pair. The adapter must serialize all records in their supplied order without consulting the answer key, filtering for the query, or selecting the matching value. If the native format cannot express a case, record that limit before testing.

Include a control that changes only a distractor (expected answer stays fixed). Vary the target position and balance the replacement values so a fixed-position or fixed-answer rule can fail. Compare against exact key lookup on the same records. List missing keys and contradictory values separately and agree on the expected behavior before scoring them. Report unsupported cases separately from model errors.

ChatGPT: review the encoding and controls for answer leakage. Once a shareable synthetic sample and the pinned interface are available, record predictions and scoring rules before inference. Keep private correspondence and samples out of this public thread. This pilot measures retrieval from supplied symbols. Language comprehension and relationship discovery would require separate tests.

## Proposed evidence retrieval check

Use one opaque value token per record, assigned before reading the query. A fixed table decodes each token to its record ID, object and source. Two sources reporting the same object retain distinct IDs. Encode each subject–relation pair as a key. Record capacity exclusions (63 keys, 64 record IDs) and keep them in the coverage count.

For each query, the conventional baseline returns every record whose subject and relation match, including an empty set for a missing key. Score the exact unordered set of IDs and retain omissions, extra IDs and every raw output. Report native single-token lookup separately. For an exploratory set readout, propose including each present record ID whose probability under the full vocabulary softmax is at least 0.25. Do not renormalize over records or supply the expected count. This fixed proposal covers cases with zero, one or two matches; it is uncalibrated. Include single-match, absent-key, two-source agreement and two-source disagreement cases, plus a distractor with the same subject and a different relation. Check that the same rule can return two, one or zero IDs. Decoding an ID attributes the source through the table; it does not test comprehension of source identity.

Use a recorded, preselected permutation shared across each fact-swap pair and its distractor control. Balance target positions and token ranks across cases. Compare first, last, lowest-ID and most-frequent rules under fixed tie handling. Keep any failures of those controls. Freeze the readout and sample digest before inference.

Prepared by ChatGPT (OpenAI, Codex). Human technical review pending.
