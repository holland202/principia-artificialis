# CCC-001 long-context qualification: deviations from the registered plan (committed before any model reading)

**Registration:** [LONGCTX_PREREG.md](LONGCTX_PREREG.md) at `cf1fbcd`. That file is not edited (M12). This file
records, before the harness is run and before any model reads a prompt from it, how the first run departs from the
plan in the registration's "Open door". Development-only (C-EXPLORE). Self-tested.

## D1. Scope of the first run: REF only (2026-11-22, relay turn 023)

- **Run:** G0 and `--sabotage-escape` with no weights loaded, at all three lengths. Then REF on
  Qwen2.5-1.5B-Instruct: G0–G6 (G3 included) and `--sabotage` (zero logits) at REF.
- **Not run:** N016 and STRESS model readings. They are reported `NOT RUN`, never as failures or passes.
- **Consequence for the verdict:** `LONGEST QUALIFIED` can only be `REF` or `NONE` in this run. If REF qualifies,
  the longest *demonstrated* length is REF. Nothing about checkpoint 016's length (≤ 8,746 tokens) is covered.
- **Why:** Qwen2.5-1.5B did not qualify in stage Q, so a full sweep on it would be a length diagnostic of an
  unqualified model, at about 4.3 h of CPU (NOT RUN projection in the registration). The registration's T\* rule
  requires every shorter registered length to qualify, so REF decides eligibility for both longer lengths. This
  order was proposed by ChatGPT (OpenAI) in relay turn 020, taken up by Claude in turn 021, and supported in turn
  022, which also asked that the REF-only scope be documented before scoring.
- **Failure reporting (turn 022):** if REF fails, the results name the failing gate, so that a rendering defect
  (G0), a runtime limit (G1), noise (G2), read-out (G3), letter mass (G4) and a weak response to the instruction
  (G5, G6) stay distinguishable.

## D2. Implementation choices the registration left open (stated before the run)

- G0 compares, per (length, arm, π) cell, the SHA-256 of the list of per-item token-ID SHA-256s, exactly as
  `longctx_feasibility.py` prints it, against the 18 digests committed in `results/ccc_001/longctx_feasibility.txt`.
  The harness renders with transformers `apply_chat_template(..., tokenize=False, add_generation_prompt=True)` and
  encodes with `add_special_tokens=False`, as `common.render` does. Message-1 content is encoded alone to count
  chat-control tokens (151644, 151645).
- The number of synthetic days per length is taken from the committed feasibility output (REF 44, N016 165,
  STRESS 340), and the harness checks that those days still meet the registered window under the transformers
  path.
- G2 and G3 compare probabilities after rounding to 6 decimals, the precision `qdiag.readout` already uses.
- G6 counts strict inequality: an item counts only if its π-averaged G(E) is greater than its π-averaged G(D).
- `--sabotage` keeps every forward pass and replaces the logit vector at the last position with zeros before the
  read-out (`qdiag.readout`), so its code path matches the real run except for that line.

## Provenance (M13)

Claude (Anthropic, Opus 5.5), fresh scheduled session, under Chad Holland's standing direction of 2026-11-21. The
REF-first order is ChatGPT's proposal (relay turns 020, 022). Human validation: not performed. Human
responsibility: Chad Holland. The question behind CCC-001 is Federico Talens-Alesson's; crediting him implies no
endorsement or validation by him.
