# Intake note — 2026-11-11: prompt-injection data curation; AIPOCH workbench

Reference material, not a research note: no registered predictions, no
reference code, nothing here enters NOTES_INDEX.md. Two items from a
read-only public-source scan by ChatGPT (2026-11-11), each then checked
against its source by Claude (Anthropic, model Claude Fable 5) the same day.
Labels follow the house vocabulary. Neither item was reproduced.

## 1. Ethan Cao — "Actionable Interpretability: Curating Effective Prompt Injection 'Exams' for Fine-Tuning SLMs"

Hugging Face community article, 2026-11-09.
https://huggingface.co/blog/JuneWay128/actionable-interpretability-curating-effective-pro

VERIFIED FROM SOURCE (the article page):
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
- Code and configs: github.com/JuneWayne/Verbalizing-LLMs-For-AI-Defense.
  The full synthetic dataset is withheld (author cites privacy); **no license
  is stated** on the page for code or data — check before any reuse.

Corrections to the scan as received: the scan said reproduction "would
require verifying access to the selected datasets, code" — the code is
public; it is the dataset that is withheld, and the missing license is
blanket, not per-artifact.

Possible PA fit, stated as questions to kill, not endorsements: does
selection-by-probe beat selection-by-accuracy on a task we can run locally?
Does lower attack success cost completion (the author's own open trade-off)?
Both would need a registered design and a local model before becoming a note.

## 2. AIPOCH Open-Science

https://github.com/aipoch/open-science — local-first research workbench,
Apache-2.0.

VERIFIED FROM SOURCE (repository page, read 2026-11-11): latest release
shown is **v1.0.6, October 2026**; benchmark section covers AstaBench,
ASI-Bench and BiomniBench-DA, described by the project itself as
self-reported and not directly comparable; and the replay/re-execution
distinction is real and well put — "replay checks do not establish
scientific validity"; imported verification records are the sender's checks,
"not a rerun on this computer."

NOT CONFIRMED against that page: the scan's "v1.2.1, updated 2026-11-11" and
a "CORE-Bench-Hard 36/37 including retests" figure. The page read today
shows neither. The scan may have read a different or newer surface; until
someone points at where those claims live, they carry no weight here.

The verified part is the useful part for this program: AIPOCH's
replay-vs-re-execution vocabulary matches the distinction Sovereign Veritas
and Sovereign Workbench draw between a verified record and a verified
outcome (EO-1), and is worth citing when that distinction needs an outside
reference.

## Provenance

Scan: ChatGPT (read-only, public sources, no repositories modified). Source
checks, corrections and this note: Claude (Anthropic, model Claude Fable 5),
on the owner's direction, 2026-11-11. Human review level: the owner directed
intake but had not reviewed this note at commit time. Nothing here is
independent validation of either item.
