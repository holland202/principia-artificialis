#!/usr/bin/env python3
"""Describe P11's measurements after scoring (descriptive, not registered; decides nothing).

  python -I experiments/note052_p6/describe_p11.py OUT    OUT is run_p11.py's output folder
"""
import json, sys

o = json.load(open(f"{sys.argv[1]}/score.json"))
per = o["per_repo"]
for t in ("AA", "AB", "BA", "BB"):
    rs = [r for r, v in per.items() if v["transition"] == t]
    if not rs:
        print(f"{t}: 0 repositories")
        continue
    act = [r for r in rs if per[r]["commits_after_pin"] > 0]
    up = sum(per[r]["delta"] > 0 for r in rs)
    down = sum(per[r]["delta"] < 0 for r in rs)
    pin = sum(per[r]["shaped"][0] for r in rs)
    head = sum(per[r]["shaped"][1] for r in rs)
    print(f"{t}: {len(rs)} repositories, {len(act)} with commits after the pin; delta > 0 in {up}, < 0 in {down}; "
          f"verification-shaped files {pin} at pins, {head} at heads")
for r, v in sorted(per.items()):
    if v["transition"] == "BA" or v["delta"] != 0:
        print(f"  {r}: {v['transition']}, commits after pin {v['commits_after_pin']}, shaped {v['shaped'][0]} -> "
              f"{v['shaped'][1]}, unchecked findings {v['findings_unchecked'][0]} -> {v['findings_unchecked'][1]}")
