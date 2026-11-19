# CST-MECH qualification instrument

**Instrument qualification only. No new AI-behavior experiment, discovery, or independent validation.**

This develops the leading candidate from the [discovery audit](../../docs/DISCOVERY_SHORTLIST_2026-11-15.md)
without changing [proposal #152](https://github.com/holland202/principia-artificialis/pull/152).
[Registration](../../docs/CST_MECH_QUAL_001_PREREG.md) precedes implementation in git history.
[Results](../../docs/CST_MECH_QUAL_001_RESULTS.md) describe its limits and next gates.

Run with the Python standard library from the repository root.

```bash
python experiments/cst_mech_qual/instrument.py qualify
python experiments/cst_mech_qual/instrument.py qualify --sabotage
python -m unittest discover -s experiments/cst_mech_qual -p test_instrument.py -v
python experiments/cst_mech_qual/instrument.py manifest
```

Normal qualification must reproduce the recorded digest and exit zero. Oracle sabotage must exit
one. These fixtures encode anticipated outcomes, not model completions. Any statistical values
on them test arithmetic only.

`score --archive PATH` checks a JSONL response fixture against this fixed qualification manifest.
Each row contains exactly `trial_id`, `prompt_sha256`, `completion`, and `finish_reason`.
Allowed finish reasons are `stop`, `length`, and `error`. Only `stop` can score correct.
Missing/extra/duplicate trials or invalid schemas invalidate the archive. Malformed, ambiguous,
or truncated completions score wrong. No failed trial may be silently dropped or overwritten.
The prompt asks for a canonical final `DECISION: A` or `DECISION: B` line. This strict parser is
a proposed new format and must not be used to retroactively rescore CST-001 under a changed rule.

The fixture graph has fixed-length node names and constant record count. Only the selected
reports' reachable roots count. Other listed observations are not extra evidence. Both report
orders and both answer-code mappings occur. All these cases are public and permanently disqualified
from confirmation. The two oracle algorithms share an author and are **not independent**.

The N/T/G instruction prefixes are provisional and have unequal token lengths. No tokenizer has
been qualified. The graph-body character match does not claim token matching, natural-language
equivalence, or valid model difficulty. No short-format decoder is implemented.

Proposed statistics expose #152's interaction gate and separately check a directional crossover.
The additional T-versus-G interaction is a specificity diagnostic. These are review tools, not
a frozen scientific decision rule. Sample independence, clustering, effect margins, uncertainty
intervals, multiplicity, and power still require prospective scientific review.

The package has no model runner, paid API access, arbitrary split/seed option, or confirmatory
dataset loader. Full prompt/model/environment provenance must be added before a separately
authorized inference study. The archive fingerprint only binds a fixture response to a prompt,
not to an actual model or a trustworthy execution.

AI participation: Codex / OpenAI GPT-6 Astra. Human validation: direction only. Human
editing/curation pending. Human responsibility: Chad Holland.

Next unrun test: blind graph-oracle and statistical review, followed by separately registered
real-model qualification and a new holdout under independent custody.
