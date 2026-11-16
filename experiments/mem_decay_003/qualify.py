"""Descriptive selector qualification on the public dev family. No model is called.

For each selector and budget, over 40 dev scenarios: how often each task's evidence requirement is retained, and how
often the retained records LICENSE the stale value for the correction task (original kept, correction lost). The dev
family is Claude-written; numbers here describe this instrument on these templates, not memory systems in general.
Written by Claude (Anthropic, Opus 5.5), 2026-11-16 (REV1; the draft's table was produced by an unsaved inline script)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dev_family as D  # noqa: E402
import memdecay3 as M  # noqa: E402

N = 40
SCEN = [D.scenario(s) for s in range(N)]
print(f"QUALIFICATION REV1 (descriptive, dev family only, no model), {N} scenarios of {len(SCEN[0]['records'])} records")
for budget in (6, 10):
    print(f"budget {budget}")
    for name in M.SELECTORS:
        retained = {k: 0 for k in ("correction", "singleton", "conjunctive", "redundant")}
        stale_licensed = 0
        for sc in SCEN:
            kept = M.run_selector(name, sc, budget, seed=7)
            for t in sc["tasks"]:
                retained[t["type"]] += M.retained_requirements(t, kept)
                if t["type"] == "correction" and M.licensed_answer(t, kept) == t["stale"]:
                    stale_licensed += 1
        cells = "  ".join(f"{k} {v}/{N}" for k, v in retained.items())
        print(f"  {name:18s}  retained: {cells}  stale_licensed {stale_licensed}/{N}")
