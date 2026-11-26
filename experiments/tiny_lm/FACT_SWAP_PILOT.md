# Tiny Engine fact-swap pilot

Draft for design review. Awaiting a synthetic sample. Predictions remain open. Run status: not started.

Can the existing lookup checkpoint follow a changed fact in its input? Use invented key–value records. For example, query locker K7 twice with the same question and distractors. Replace its value, compass, with whistle on the second input. Score the pair as correct only if both exact answers match their respective records. Report the number of correct pairs and the denominator.

Claude: inspect the public lookup checkpoint, its vocabulary, input grammar and inference entry point. Pin the revisions and show how each record, the query and the decoded answer map to symbols. Use one fixed mapping across each pair. The adapter must serialize all records in their supplied order without consulting the answer key, filtering for the query, or selecting the matching value. If the native format cannot express a case, record that limit before testing.

Include a control that changes only a distractor (expected answer stays fixed). Vary the target position and balance the replacement values so a fixed-position or fixed-answer rule can fail. Compare against exact key lookup on the same records. List missing keys and contradictory values separately and agree on the expected behavior before scoring them. Report unsupported cases separately from model errors.

ChatGPT: review the encoding and controls for answer leakage. Once a shareable synthetic sample and the pinned interface are available, record predictions and scoring rules before inference. Keep private correspondence and samples out of this public thread. This pilot measures retrieval from supplied symbols. Language comprehension and relationship discovery would require separate tests.

Prepared by ChatGPT (OpenAI, Codex). Human technical review pending.
