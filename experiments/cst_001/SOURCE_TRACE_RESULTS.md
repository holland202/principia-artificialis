# CST-001 source-tracing probe results

## Archived feasibility result

**State:** alternate analysis of the original development replies. Source pin
[`efc29a9`](https://github.com/holland202/principia-artificialis/tree/efc29a9fb7b5ade73f7469231f03ea2945cba368).
The original positive control failed. The audits below read saved replies and reconstruct
the expected answer from the cited source IDs. They do not constitute new model inference.

All 640 archived trials were present exactly once and each yielded one recognizable decision.
The source-graph check agreed with the generator's answer key for every case. The raw archive
SHA-256 is `845c2a3f441bbcdaef3d181a58100ad9becfcefdb1f6a862b711d57b15b62028`.
The printed dev seal and per-arm counts are in [archive.txt](../../results/cst_001/source_trace_probe/archive.txt).

| Original arm | Correct pairs | Both confirmed | Both insufficient | Reversed, one hop | Reversed, two hops |
|---|---:|---:|---:|---:|---:|
| A, procedure | 0/64 | 22 | 5 | 10/32 | 27/32 |
| B, other procedure | 0/64 | 10 | 21 | 21/32 | 12/32 |
| C, neutral | 0/64 | 33 | 2 | 0/32 | 29/32 |
| D, none | 0/64 | 34 | 7 | 4/32 | 19/32 |
| E, explicit | 0/64 | 34 | 2 | 4/32 | 24/32 |

Here **reversed** means the model confirmed the shared-source variant and withheld
confirmation on the independent-source variant. Among the 320 arm-pairs, every one of
the 150 pairs with different decisions was reversed. The other 170 yielded the same
answer on both versions. The 64 underlying pairs were presented in each arm.

**Example.** In archived case `warehouse-h2-BA-1`, the direct report cited `CS-387`.
The note attached to the shift log cited `CS-387` in one version and `CS-410` in the
other. Both report texts claimed the same item count. The explicit-instruction arm
marked the first confirmed and the second insufficient. This example shows the behavioral
error under the study's rule. It leaves open how the model reached its judgment.

The experiment's original conclusion is bounded by its failed control. It establishes a
reason the conversational-transfer contrast cannot be interpreted on that deployment and its
prompts. It does not establish that the model would fail when the same evidence is shown in a
different format.

Relevant prior work has already measured sensitivity to shared roots and to structured evidence
presentation, quantified overcounting of copied reports, and studied training against provenance
double-counting. The remaining CST-001 question is whether observing the procedure in a
separate conversation changes how models apply it. [Zhang et al.](https://arxiv.org/abs/2610.12788) ·
[Gao et al.](https://arxiv.org/abs/2610.06192) · [Huang et al.](https://arxiv.org/abs/2610.13008)

Provenance. Archived trial design and collection by Claude (Anthropic, Opus 5.5).
Alternate parser, source-graph check, and interpretation by ChatGPT (OpenAI GPT-6 family).
Chad Holland originated the CST-001 hypothesis and directed its continuation. Human validation and
line-by-line review are unrecorded. Research responsibility remains Chad Holland.

## Qwen2.5-1.5B Q4_K_M rerun on fresh development cases

**What failed.** The explicit instruction handled 0/16 pairs. Reversing the quoted
answer options or adding the resolved original source IDs also yielded 0/16. For the
direct source-relation question, all 32 replies reached the 64-token generation limit
without a unique valid answer line. That arm is unresolved as a test of source-relation
recognition. Its completion behavior is recorded below.

| Prompt | Correct pairs | Reversed pairs | Both confirmed | Both insufficient | Pairs with malformed text |
|---|---:|---:|---:|---:|---:|
| E, explicit | 0/16 | 3 | 2 | 11 | 0 |
| O, option order only | 0/16 | 1 | 0 | 15 | 0 |
| L, same or different | 0/16 | 0 | 0 | 0 | 16 |
| G, resolved observation IDs | 0/16 | 5 | 5 | 6 | 0 |

The collector completed 128 case requests and four same-input repeat requests. All four
repeat texts matched. The [scorer output](../../results/cst_001/source_trace_probe/qwen15_score.txt)
records digest `732a5c73159a38c0cc3acb1da6a7133f4bb803836808ebba98e15032655b4f66`.
[Raw model replies](../../results/cst_001/source_trace_probe/qwen15.jsonl) ·
[Environment and model digest](../../results/cst_001/source_trace_probe/environment.txt)

**Sample.** `probe-warehouse-h1-AB-0` has `CS-710` + `CS-710` in the shared version
and `CS-710` + `CS-724` in the independent version. E returned CONFIRMED on both.
O returned INSUFFICIENT on both. G returned CONFIRMED on both. One of the L replies
spent its available output restating the inventory claim and first report. A person
has yet to review this named sample.

**Interpretation.** Option order moved the same-answer tendency in this model and
setting. Supplying the roots did not resolve the errors on the tested pairs. The
original development corpus, weights format, and inference engine differ from this run,
so the difference in reversal counts does not estimate a quantization effect. This is
an exploratory, self-tested CPU result. Human validation, independent replication,
and S25 runs remain pending.

## Qwen2.5-3B Q4_K_M on the same development cases

**What failed.** The explicit prompt reached the 64-token generation limit on 31/32
replies without a unique decision line. Swapping the two options yielded 30/32 such
replies. Thus every pair under both prompts had at least one missing decision. The
direct relation question hit the limit without a unique answer in 23/32 replies.
The 3B explicit results primarily measure completion within this output budget.

| Prompt | Correct pairs | Reversed pairs | Both confirmed | Both insufficient | Pairs with malformed text |
|---|---:|---:|---:|---:|---:|
| E, explicit | 0/16 | 0 | 0 | 0 | 16 |
| O, option order only | 0/16 | 0 | 0 | 0 | 16 |
| L, same or different | 1/16 | 0 | 0 | 1 | 14 |
| G, resolved observation IDs | 3/16 | 7 | 1 | 5 | 0 |

All 32 G replies contained a unique valid decision line. Two of its correct pairs
were one-hop cases and one was a two-hop case. The [scorer output](../../results/cst_001/source_trace_probe/qwen3_score.txt)
records all 128 case requests, exact text matches for all four repeat requests, and
digest `95aafd44d5566b5aec58d6fd114cef1213cafdd9aeebc067311e836f26cbb2b7`.
[Raw model replies](../../results/cst_001/source_trace_probe/qwen3.jsonl)

**Sample.** In `probe-bird_survey-h1-AB-0`, the shared version gives `FT-670` twice.
The independent version gives `FT-670` and `FT-993`. E returned only a partial analysis
on the first and ended with CONFIRMED on the second. G returned INSUFFICIENT and
CONFIRMED, respectively. This pair also got both source relationships right in L.

**Interpretation.** Giving the IDs changed completion as well as paired decisions.
For 3B it produced 32 scorable replies and three correct pairs, with seven pairs
still reversed. The comparison cannot isolate source extraction from response format.
The larger model did not qualify the explicit control for a transfer experiment.
Both completed runs were exploratory CPU measurements on synthetic cases. The
128-pair CST-001 holdout remains sealed and unused. Human sample inspection,
independent replication, and S25 validation remain pending.

## Replay and next test

Run the scorer over the retained raw files, without downloading models.

```bash
python experiments/cst_001/source_trace_probe.py archive results/cst_001/dev_outputs.jsonl
python experiments/cst_001/source_trace_probe.py score --model qwen15 results/cst_001/source_trace_probe/qwen15.jsonl
python experiments/cst_001/source_trace_probe.py score --model qwen3 results/cst_001/source_trace_probe/qwen3.jsonl
```

For a fresh qualification, collect a bounded forced-choice answer with counterbalanced
labels so lengthy restatements cannot consume the available response budget. Include
paired bare-ID and one- or two-hop prose cases. Successful controls on fresh cases
would make the conversation comparison interpretable. Any changes to the corpus,
response constraint, registration, or scoring belong to a new study record.

Provenance. ChatGPT (OpenAI GPT-6 family) authored, ran, and scored this probe on
November 15, 2026. Human direction was provided by Chad Holland, who originated the
hypothesis and holds research responsibility. Human validation is pending.
