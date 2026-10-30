#!/usr/bin/env python3
"""Run one SigmaHQ unittest file as `python <file>` runs it, with full assertion messages (PA-SIGMA-003, D2).

unittest shortens long assertion messages (TestCase.maxDiff is 640 characters). The harness reads rule paths out
of those messages, so this runner sets unittest.TestCase.maxDiff = None and then runs the file as __main__, its
own `if __name__ == "__main__":` block included. No check is changed, and the exit status is the file's own.

Usage: python -I unittest_full.py tests/test_rules.py
"""
import runpy
import sys
import unittest


def main():
    path = sys.argv[1]
    unittest.TestCase.maxDiff = None
    sys.argv = [path]
    runpy.run_path(path, run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
