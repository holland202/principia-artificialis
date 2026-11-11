# Intake note — 2026-11-11: prompt-injection data curation; AIPOCH workbench

Reference material, not a research note: no registered predictions, no
reference code, nothing here enters NOTES_INDEX.md. Two items from a
read-only public-source scan by ChatGPT (2026-11-11), each then checked
against its source by Claude (Anthropic) the same day. Labels follow the
house vocabulary. Neither item was reproduced.

## Correction before merge (M8, W9) — read this first

The first draft of this note (commit `71698e3`, PR #133) marked two of the
scan's claims about AIPOCH as NOT CONFIRMED and "corrected" the scan. **The
scan was right and the draft was wrong.** Review re-checked against the
repository's git tags rather than a rendered page:

- `v1.2.1` exists, tagged `a18fd48`, committed 2026-11-10T20:33-08:00
  (2026-11-11 UTC) — matching the scan's "v1.2.1, updated 2026-11-11".
- The README at `v1.2.1` carries the CORE-Bench-Hard figure: "36 of 37 test
  tasks correctly (97.30% task accuracy)", "The final tally includes retests."

The draft's "v1.0.6, October 2026" matches tag `v1.0.6` (`a6c6540`,
2026-10-29) — it read a stale copy of the page and labelled it VERIFIED FROM
SOURCE. One of its quotes ("replay checks do not establish scientific
validity") is in the README at `v1.0.6` and no longer in the README at
`v1.2.1`; the draft mixed two versions without saying so.

Superseded draft text, verbatim:

> VERIFIED FROM SOURCE (repository page, read 2026-11-11): latest release
> shown is **v1.0.6, October 2026**

> NOT CONFIRMED against that page: the scan's "v1.2.1, updated 2026-11-11" and
> a "CORE-Bench-Hard 36/37 including retests" figure. The page read today
> shows neither. The scan may have read a different or newer surface; until
> someone points at where those claims live, they carry no weight here.

Lesson for the intake method: a rendered web page is not a pinned source. Cite
a tag or commit hash for any version-dependent claim (C-EXT). Because the same
drafting session also checked Item 1, Item 1's article-level claims are
relabelled below as checked by the drafter only.

## 1. Ethan Cao — "Actionable Interpretability: Curating Effective Prompt Injection 'Exams' for Fine-Tuning SLMs"

Hugging Face community article, 2026-11-09.
https://huggingface.co/blog/JuneWay128/actionable-interpretability-curating-effective-pro

VERIFIED FROM SOURCE at review (pinned): the code repository
github.com/JuneWayne/Verbalizing-LLMs-For-AI-Defense is public; `main` was at
`c9ecf76` (2026-11-09). That tree contains **no LICENSE or COPYING file** and
its README does not mention a license — check before any reuse.

CHECKED BY THE DRAFTING SESSION ONLY — the article page could not be reached
from the review session, so these were **not re-checked**, and the drafting
session's AIPOCH check failed (above):
- Fine-tunes Qwen2.5-7B-Instruct with LoRA (rank 16, alpha 32); compares
  **eight** selection methods for 256 training pairs from FIPI: random,
  TF-IDF diversity, model-failed instances, logistic regression, linear SVM,
  two-layer NN, and two J-Lens variants.
- Author-reported: the LLMail-fitted J-Lens selection gave the lowest attack
  success rate across six benchmarks — while J-Lens classifiers had *worse*
  raw classification accuracy than the linear probes. The selector that
  classifies worse trains the more robust model; that inversion is the
  interesting claim.
- The author states the robustness/completion trade-off plainly ("lower ASR
  does not equate to 100% task completion") and reports token-repetition
  failures; completion is not quantified beyond safe-prompt testing.
- In-distribution caveat stated by the author: one of the six benchmarks is
  FIPI's own held-out split.
- The full synthetic dataset is withheld (author cites privacy).

Correction to the scan as received: the scan said reproduction "would require
verifying access to the selected datasets, code" — the code is public (pinned
above); it is the dataset that is withheld.

Possible PA fit, stated as questions to kill, not endorsements: does
selection-by-probe beat selection-by-accuracy on a task we can run locally?
Does lower attack success cost completion (the author's own open trade-off)?
Both would need a registered design and a local model before becoming a note.

## 2. AIPOCH Open-Science

https://github.com/aipoch/open-science — local-first research workbench.

VERIFIED FROM SOURCE at review, pinned to tag `v1.2.1` (`a18fd48`):
- License: Apache-2.0 (LICENSE file).
- Benchmarks named in the README: AstaBench, ASI-Bench, BiomniBench-DA and
  CORE-Bench-Hard. CORE-Bench-Hard: "36 of 37 test tasks correctly (97.30%
  task accuracy)" in a local evaluation with DeepSeek Flash and the official
  programmatic scorer; "The November 6 tally includes retests and is not a
  first-pass success rate." This is the project's own figure. Not reproduced
  here.
- Replay vs re-execution, in the README: "Received verification records
  describe the sender’s checks, not a rerun on this computer." In the docs at
  the same tag: "Matching replay outputs does not establish sound methods or
  scientific validity" (`docs/known-limitations.md`).

The useful part for this program: AIPOCH's replay-vs-re-execution vocabulary
matches the distinction Sovereign Veritas and Sovereign Workbench draw between
a verified record and a verified outcome (EO-1), and is worth citing when that
distinction needs an outside reference — cite the tag, not the page.

## Provenance

Scan: ChatGPT (read-only, public sources, no repositories modified).
First draft and its source checks: a Claude session (Anthropic; the draft
named the model as Claude Fable 5), on the owner's direction, 2026-11-11.
Review, re-check against pinned git tags, and this correction: Claude
(Anthropic, Opus 5.5), on the owner's direction, 2026-11-11.
Human validation: not performed. Human review level: direction only — the
owner had not read this note at commit time. Human responsibility: Chad
Holland. Nothing here is independent validation of either item.
