#!/usr/bin/env python3
"""PA-SIGMA-001 post-hoc check (EXPLORATORY; prompted by run 1, not registered): how can a one-event sample
give two matches?

Usage: python duplicate_match_check.py SIGMA_CHECKOUT EVTX_CHECKER

For rule 06d71506-7beb-4f22-8888-e2e5e2ca7fd8 (the one test with an over-match warning on the unmutated
rules), it reads the sample with python-evtx (records, record numbers, the header's next record number) and
runs the runner's own `run_evtx_batch` on the rule alone. It prints how many match lines the runner counts
and how many distinct events they carry (sha256 of each line's `Event` field). No event content is printed.
"""
import contextlib
import hashlib
import io
import json
import os
import sys

import Evtx.Evtx as evtx
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from feasibility import RULE_PATHS, load_runner  # noqa: E402

RULE = "06d71506-7beb-4f22-8888-e2e5e2ca7fd8"


def main(sigma, checker):
    sigma, checker = os.path.abspath(sigma), os.path.abspath(checker)
    runner = load_runner(sigma)
    os.chdir(sigma)
    rules, _, _ = runner.find_rules_with_tests(RULE_PATHS)
    r = [x for x in rules if x["id"] == RULE][0]
    t = r["tests"][0]
    with open(r["path"], encoding="utf-8") as f:
        rule = yaml.safe_load(f)
    print(f"rule {RULE}: logsource {rule['logsource']}, condition {rule['detection']['condition']!r}, "
          f"match_count {t.get('match_count')}")
    with evtx.Evtx(t["path"]) as log:
        nums = [rec.record_num() for rec in log.records()]
        head = log.get_file_header()
        print(f"sample (python-evtx): records {len(nums)}, record numbers {nums}, "
              f"header next record number {head.next_record_number()}, chunks {head.chunk_count()}")
    with contextlib.redirect_stdout(io.StringIO()):
        m = runner.run_evtx_batch([(r, 0, t)], checker, "tests/thor.yml")
    lines = m.get(RULE, [])
    events = [hashlib.sha256(json.dumps(json.loads(ln)["Event"], sort_keys=True).encode()).hexdigest() for ln in lines]
    print(f"runner's match lines for the rule: {len(lines)}; distinct Event payloads among them: {len(set(events))}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(*sys.argv[1:]))
