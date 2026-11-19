#!/usr/bin/env python3
"""Pin the exploratory review audit after execution; no model-validity claim.

Codex / OpenAI GPT-6 Astra; self-tested. Human review: direction only;
human editing/curation pending; Chad Holland responsible.
"""
from contextlib import redirect_stdout
from io import StringIO
import sys

import review_20261116


# Separate post-run pin: the digest covers the entire canonical audit payload.
RECORDED = (0, "DIGEST 5d0a39b66947754e383fb4f274308c397361612d76d5e1de6ba10d52e8dd61c7")


def main():
    output = StringIO()
    with redirect_stdout(output):
        status = review_20261116.main()
    text = output.getvalue()
    sys.stdout.write(text)
    lines = text.splitlines()
    observed = (status, lines[-1] if lines else None)
    matched = observed == RECORDED
    print("RECORDED AUDIT " + ("MATCH" if matched else "MISMATCH"))
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
