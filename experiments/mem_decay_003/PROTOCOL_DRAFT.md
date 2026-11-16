> **2026-11-16, later:** superseded in part by [PROTOCOL_REV1.md](PROTOCOL_REV1.md) after Codex's review (PR #159). H1b is withdrawn as a claim about model behaviour, and four scoring defects were found and fixed. Nothing below is edited.

# MEM-DECAY-003 protocol draft: when memory is tight, does losing a correction make an AI confidently wrong?

**State:** DRAFT protocol and qualified instrument. **NOT REGISTERED, NOT RUN.** No model has been called. Owner
approval is needed before any campaign. Codex's requirements (issue #150, comment 6921970649) are answered
point by point below.
**Authors:** Direction: Chad Holland (2026-11-16; ownership confirmed with Codex in issue #150). Design and
instrument: Claude (Anthropic, Opus 5.5). Human review level: direction only. Self-tested.

## 1. What might be new, the closest prior work, and what would kill it

**Already published, so not claimed** (2026-11-16 search; abstract level unless noted):

- **Facts that only matter together, and redundant copies.** *Beyond Marginal Influence: Interaction-Aware Memory
  Selection for LLM Agents* (NeurIPS 2026). It shows that per-record relevance or influence rankings cannot find
  sufficient subsets when evidence is redundant or jointly necessary, and it introduces JointCoreBench with exact
  oracles. **So "independent scoring misses conjunctions" is not a new lead.** Conjunctive and redundant records are
  included here only as coverage, as Codex asked.
- **Evicting indirect prerequisites.** *When Retrieval Fails Before It Begins* (ICML 2026 workshop). Upstream records
  weakly aligned with the query are evicted, and a one-hop dependency-aware rule (DSGC) fixes most of it.
- **Feature-scored retention and value-aware memory.** TraceRetain (ICML 2026, arXiv 2606.29178), MemLens (arXiv
  2607.25992), BudgetMem (arXiv 2511.04919), and OSL-MR on LOCOMO and LongMemEval (arXiv 2606.10616).

**Not found in those works:** what happens to a decision when a *correction* is evicted and the record it
corrected is kept. Neither of the two closest papers mentions superseded records, corrections, or the difference
between answering wrongly and abstaining. JointCoreBench only varies how absence is presented: deletion, UNKNOWN
masks, sentinels.

**Hypothesis H1, in two parts:**

- **H1a, about the selector (engineering; easy to produce by construction).** Task-blind selectors at a fixed budget
  evict corrections more often than the records those corrections supersede.
- **H1b, about the model (the possibly new behaviour).** When memory holds a superseded record and not its
  correction, the model **answers with the stale value instead of UNKNOWN**. Losing memory then turns an abstention
  into a confidently wrong answer.
  - **Measure:** the share of STALE answers among correction-dependent tasks under the "original kept, correction
    evicted" condition.
  - **Matched conditions:** both records kept, only the correction kept, and neither kept.

**What kills the lead:**

- **H1b dies** if, in the "original only" condition, STALE answers are no more frequent than UNKNOWN answers, or the
  rate of confident wrong answers matches the "neither kept" condition. In either case losing a correction behaves
  like ordinary forgetting.
- **H1a carries no weight on its own.** Qualification already shows it can be built in (section 6).

## 2. What the selector can see (frozen)

Selectors receive `selector_view()`: id, text, age and uses only. They never see:

- record kind;
- tasks, questions or answers;
- labels derived from deleting records.

**Evaluation scenarios come from different template families than development:** development uses one family,
facility operations, written by Claude. Evaluation families are written by someone else (section 5). A new seed is
not enough.

**Tested:** every selector gives identical output when every hidden field is scrambled (40 scenarios × 3 budgets).
A selector reading the raw scenario is shown to fail that check.

## 3. Real model execution

- **Model:** Qwen2.5-7B-Instruct, Q4_K_M GGUF (revision `bb5d59e`, as in CST), llama-cpp-python 0.3.37, greedy
  decoding, temperature 0.
- **Answer format:** "ANSWER: <value>" or "ANSWER: UNKNOWN". The prompt says to answer UNKNOWN if the memory does
  not settle the question.
- **Memory budget:** K records, with K ∈ {6, 10} out of about 20 per scenario. Retained records go into the prompt in
  a fixed order (by id), with no retrieval step. So retention is separated from retrieval, and decision correctness
  is reported separately from whether the needed records were retained.
- **Outcomes per task:** CORRECT, STALE, UNKNOWN, WRONG or MALFORMED (`classify()`, tested).
- **Matched conditions for H1b:**
  - full memory;
  - original only;
  - correction only;
  - neither;
  - each selector's actual retained set.
- **Noise:** greedy decoding; 10% of calls rerun to check byte-identical outputs.
- **Archive:** every raw output, with model and file hashes.

## 4. Arms, all at the same budget

| Arm | What |
|---|---|
| random | uniform sample, fixed seed |
| recency | youngest first |
| uses | most used first |
| content | a simple salience rule: constraint words, digits, length |
| **LLM judge** | the same 7B model rates each record's importance 1–5 **one record at a time, task-blind**. This is the realistic content-based selector; not built yet |
| supersession-aware | reserves budget for records that read like corrections (the "fix" arm) |
| noisy labels | MEM-DECAY-002's label model, where meaningful |
| oracle-assisted reference | chooses the set using the answer key, **on development scenarios only**. It is a reference, **not called a ceiling** unless it optimises the same downstream objective at the same budget |

## 5. Who grades

Claude writes the selectors, the harness and `classify()`. That alone stays self-tested.

- **The evaluation scenarios, their answer keys and a challenge set are to be written by Codex** (or someone else)
  against the frozen schema in `memdecay3.py`, and frozen by hash before any evaluation call.
- **Codex has read MEM-DECAY-002 but no MEM-DECAY-003 code**, and will record what it sees.
- **Claude does not see the evaluation scenarios** before the run. Claude only receives their seal.
- **The challenge set should vary what the dev family holds fixed:** long corrections, short originals, corrections
  with no "update" wording, and originals with no constraint words. Without that, H1a is an artefact of my
  templates (section 6).

## 6. Qualification so far (non-confirmatory, dev family only, no model)

- **Tests:** `test_memdecay3.py`, 10 tests, all pass:
  - selector blindness under scrambling, and detection of a leaky selector;
  - the budget limit, rejection of bad output, determinism;
  - every outcome class;
  - consistency of the answer key with the records.
- **What each selector keeps:** [`results/mem_decay_003/qualification_selectors.txt`](../../results/mem_decay_003/qualification_selectors.txt).
  - **Failure first:** the content rule loses the correction while keeping the stale original in **40 of 40** dev
    scenarios. That is **by construction**: I wrote the dev corrections short and wordless, and the originals long
    and full of constraint words, and the rule rewards exactly that. It shows the instrument can register the
    asymmetry. **It is not evidence for H1a.**
  - The supersession-aware arm keeps both in 40 of 40, also by construction.
  - At budget 6, no selector kept both parts of a conjunctive pair more than 5 times in 40.

## 7. Pilot budget (needs owner approval)

The development pilot uses the dev family only, to check the H1b plumbing and noise before any evaluation family
exists:

- 12 scenarios × 4 tasks × (4 matched conditions + 5 selectors × 2 budgets) = 672 calls;
- at about 5–10 s each on this machine with short answers, that is **about 1–2 hours**;
- plus 67 rerun calls for noise.

## 8. Open choices (owner or reviewer)

1. Is the 7B model, the same one as in CST, acceptable, or should a second model be planned from the start?
2. Should the prompt *permit* UNKNOWN (current draft), or say nothing about it? Permitting it is the fair test of
   H1b. Silence measures the default instead.
3. Does the LLM-judge selector rate records one at a time (planned, task-blind), or in context with the other
   records?
4. Minimum effect for H1b: proposed as STALE − UNKNOWN ≥ 0.2 of correction-dependent tasks in "original only",
   to be frozen after the dev pilot and before evaluation.

---
*Provenance (M13): Claude (Anthropic, Opus 5.5) designed and wrote this from Codex's requirements and Chad Holland's
direction → human validation: not performed → human editing/curation: direction by Chad Holland, 2026-11-16 → human
responsibility: Chad Holland. Review level: direction only.*
