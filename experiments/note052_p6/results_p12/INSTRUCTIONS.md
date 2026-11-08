# P12: instructions for the second reviewer

Registered in note052 Amendment 6 (commit `85450df`) before the sample was drawn. The reviewer is ChatGPT (OpenAI),
in the auditor role, at Chad Holland's direction. Any other reviewer can do the same as a separate run.

## Before you rate

Do **not** open any of these until your ratings are committed:
- `experiments/note052_p6/results_p10/handcheck.json` (Claude's verdicts and reasons);
- `experiments/note052_p6/results_p10/score.json` (per-repository TP counts);
- `experiments/note052_p6/results_p12/key.json` (maps R01–R30 to P10's ids);
- the "Amendment 3 results" section of `research_notes/note052_verification_that_cannot_fail.md` (it names the
  8 TPs).

If you have already read any of them, rate anyway and say so in the declaration. The run is then reported as not
blind.

## Rate

For each of R01–R30 in [PACKET.md](PACKET.md), open the link and apply the rules printed there. Give `TP` or `FP`
and a one-line reason. The linter category tells you what the linter claimed. It is not a verdict.

## Submit

1. Commit `experiments/note052_p6/results_p12/ratings_chatgpt.json` on your own branch, in this form:

```json
{"reviewer": "ChatGPT (OpenAI, <model>)",
 "declaration": {"opened_handcheck_json_before_rating": false,
                 "read_amendment3_tp_list_before_rating": false,
                 "notes": "anything that affected blindness"},
 "ratings": [{"id": "R01", "verdict": "FP", "reason": "one line"}]}
```

   `ratings` must hold exactly R01–R30.
2. **After** that commit, run the score and paste its full output in a note on the PR:

```
python3 experiments/note052_p6/run_p12.py score experiments/note052_p6/results_p12 experiments/note052_p6/results_p12/ratings_chatgpt.json
```

The score lists every disagreement with both reasons. Nobody changes a verdict to resolve one. Disagreements go to
Chad.
