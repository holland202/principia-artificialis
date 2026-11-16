#!/usr/bin/env python3
"""Post-execution pin of the historical review, not a scientific readiness gate.

Codex / OpenAI GPT-6 Astra; self-tested; human review direction only;
editing pending; Chad Holland responsible.
"""
import argparse
from contextlib import redirect_stdout
from io import StringIO
import sys

import audit

RECORDED = (0, "DIGEST 75c67dc70c59b514fbeba81753c48123f4391be849aeda94992f9052e1e67572")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sabotage", action="store_true")
    args = parser.parse_args()
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = audit.run(args.sabotage)
    output = buffer.getvalue()
    sys.stdout.write(output)
    lines = output.splitlines()
    matched = (code, lines[-1] if lines else None) == RECORDED
    print("RECORDED REVIEW " + ("MATCH" if matched else "MISMATCH"))
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
