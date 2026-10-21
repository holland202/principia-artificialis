# Documentation and evidence integrity: bounded pilot

**Status:** Engineering pilot / source-level checks only. **Not** a scientific finding, adopted SWAY rule, historical documentation correction, or validation of every repository claim.
**Date:** 2026-10-21
**Scope:** New or modified Markdown in a pull request; existing files remain outside the gate until changed. No automatic rewrite or relabeling.
**Owner:** Chad Holland; AI-assisted implementation: ChatGPT (OpenAI GPT-6); human review level: direction only. The owner retains responsibility for merge/publication decisions.

## Why this exists

AI can produce convincing documentation whose local references are broken, whose stated verification has no traceable supporting command or record, or whose claims become stale. The repository already has [method_lint.py](../scripts/method_lint.py) for canonical rules and [check_numbers.py](../scripts/check_numbers.py) for reference-script number matches. Those checks are retained unchanged, including their historical negative findings. This pilot adds a *different* bounded signal, without silently modifying SWAY.

## Implemented mechanical check

- [doc_evidence_check.py](../scripts/doc_evidence_check.py) inspects explicitly named Markdown paths or newly changed Markdown paths in a PR. It fails when an ordinary local Markdown link points to a missing file or leaves the checkout; relative links with `#fragment` verify **only the file**, not the anchor.
- It ignores external URLs and anchor-only references; it **does not claim** to validate them. It ignores fenced and simple inline code; more complex nested Markdown link syntax may require manual review.
- It emits nonblocking `REVIEW_EVIDENCE_POINTER` leads where verification-sounding language appears in a document without an obvious evidence reference. These are heuristic leads only: the tool **cannot** establish that a claim is true, false, stale, or adequately sourced. It must not automatically change a note's status.
- An unreadable required file or broken local link fails closed; a missing diff base yields `COULD NOT RUN` (exit 2), not a green pass.
- It is standard-library-only, read-only, and has `--selftest` and `--sabotage` controls. The sabotage check plants a broken link in a temporary synthetic input, **not** the repository.
- [The isolated workflow](../.github/workflows/doc-evidence-check.yml) runs synthetic unit tests and checks only changed Markdown files on pull requests. No whole-repository backlog is automatically reclassified.

## Local verification and outstanding limits

Before submission, the author ran `python -m unittest discover -s scripts -p test_doc_evidence_check.py -v` against synthetic fixtures in a local working directory: **13 tests passed**, plus a deliberately failing sabotage run produced exit 1. This is a local implementation smoke test; GitHub CI and fresh-clone reproduction remain **NOT RUN / NOT VERIFIED** at this stage. It does not validate published scientific findings.

The checker does **not** check links to outside sites, heading fragments, image contents, raw HTML links, arbitrary prose citations, or most forms of stale factual claim. The regex does not implement the complete CommonMark grammar, including destinations containing unencoded closing parentheses. False positives and missed references remain possible; source inspection and human evidence review are required. For numerical results, continue using the existing number audit; for experimental claims, follow [METHOD.md](../METHOD.md), [WORKFLOW.md](../WORKFLOW.md), [CONTROLS.md](../CONTROLS.md), and [REVIEW_PLAYBOOK.md](../REVIEW_PLAYBOOK.md).

## Acceptance and rollback

A review can accept this pilot if synthetic tests pass, sabotage exits nonzero, a planted broken local link fails, a valid existing local link passes, a verification-language advisory remains nonblocking, and the pull-request comparison fails closed if its base cannot be resolved. CI results are an implementation check, not independent scientific replication. The isolated workflow can be disabled or reverted without affecting `method_lint.py`, `check_numbers.py`, prior numbered notes, or the SWAY method.

**Next open task:** Conduct a distinct human review of false positives and accessibility on a cold clone; expand the detector only if a concrete missed-reference failure justifies it. No whole-repository claims audit was performed as part of this pilot.
