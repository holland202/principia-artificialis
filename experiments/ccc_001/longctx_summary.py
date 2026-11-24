"""CCC-001 LONGCTX summary step (LONGCTX_PREREG.md, "Verdict"): T* from per-length run logs.

T* is the largest registered length that qualifies along with every shorter registered length. A length whose
log is missing or has no `QUALIFIES` line counts as NOT RUN and stops the chain.

usage: python longctx_summary.py REF_LOG [N016_LOG [STRESS_LOG]]
"""
import os
import re
import sys

ORDER = ("REF", "N016", "STRESS")


def main(paths):
    status = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        for line in open(p):
            m = re.match(r"QUALIFIES \[(\w+)\] (yes|no)", line)
            if m:
                status[m.group(1)] = m.group(2) == "yes"
    best = "NONE"
    for name in ORDER:
        s = status.get(name)
        print(f"[{name}]", "NOT RUN" if s is None else ("qualifies" if s else "does not qualify"))
        if not s:
            break
        best = name
    print("LONGEST QUALIFIED", best)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
