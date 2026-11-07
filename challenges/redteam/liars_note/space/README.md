---
title: The Liar's Note
emoji: 🤥
colorFrom: gray
colorTo: red
sdk: static
app_file: index.html
pinned: false
license: mit
short_description: Get a wrong number past a research number checker.
tags:
  - red-teaming
  - reproducibility
  - verification
  - challenge
---

# The Liar's Note (PA-C8)

A public challenge from [Principia Artificialis](https://github.com/holland202/principia-artificialis): get a wrong
number past `check_numbers.py`, the checker that enforces the repository's rule that every number in a research note
must match what its code printed.

Paste a note, the output it should match, and which number is the lie. The judge says **WIN** only if the checker
reports that number FOUND while exact decimal arithmetic says the output does not support it. Correct rounding and
coincidences do not count.

- **It runs in your browser.** The unmodified Python files run in Pyodide (Python compiled to WebAssembly), loaded from jsDelivr
  at a pinned version. Nothing you paste is sent anywhere or run as code.
- **Rules, the board and how to submit:**
  [challenges/redteam/liars_note](https://github.com/holland202/principia-artificialis/tree/main/challenges/redteam/liars_note).
  A win counts once a maintainer reproduces it from a clone.
- **No defect is asserted.** The challenge text says what is known.

## Files

`check_numbers.py` and `judge.py` are unmodified copies from the repository, pinned in `MANIFEST.sha256`. The
repository's `scripts/check_space_copies.py` fails if they drift from the originals.

## History

- 2026-11-07: first built as a Gradio app. Gradio Spaces on free hardware now need a PRO subscription, so it was rebuilt as a
  static Space running the same files in the browser. In a test, Pyodide gave the same verdicts as CPython.

## Provenance

Built by Claude (Anthropic, Opus 5.5) → human validation: not performed → human direction: Chad Holland, 2026-11-07
→ human responsibility: Chad Holland. Review level: direction only.
