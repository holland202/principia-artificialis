"""MEM-DECAY-001 S1: does SML's retrieval decay undo its `protected` flag? SML is used through its public API, unchanged.

Usage (from the repository root, with SML cloned at the pinned commit):
    git clone https://github.com/holland202/sovereign-memory-layer /path/to/sml
    git -C /path/to/sml checkout 6262dbe362c77e2cf8ecf9c326517c494dc125e8
    python3 experiments/mem_decay_001/sml_arm.py --sml /path/to/sml [--expect-digest D]

Each case builds a fresh SML store (MemoryStore(create=True)) with a fixed clock. It holds:
  1 critical record   protected=True, weight 1.0, 220-365 days old, embedding very close to the query
  6 competitors       protected=False, weight 1.0, 0-30 days old, related embeddings, different keys
  20 filler           random embeddings, 0-365 days old
Then it calls retrieve() and recall() with SML's default half_life (30 days) and threshold (0.15), top_k = 5.
Registered in REGISTRATION_S1.md before any case was run. Exit: 0 ran; 1 a control failed or the digest differs;
2 COULD NOT RUN (SML missing or not at the pinned commit).
Written by Claude (Anthropic, Opus 5.5), 2026-11-13. SELF-TESTED only.
"""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

PIN = "6262dbe362c77e2cf8ecf9c326517c494dc125e8"
CASES, COMPETITORS, FILLER, SEED = 50, 6, 20, 20261116
DAY = 86400.0
NOW = 2_000_000_000.0


def load_sml(path):
    root = Path(path).resolve()
    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=30).stdout.strip()
    except OSError as exc:
        raise SystemExit(f"COULD NOT RUN: {exc}")
    if head != PIN:
        print(f"COULD NOT RUN: SML at {root} is at {head or 'no commit'}, expected {PIN}")
        sys.exit(2)
    sys.path.insert(0, str(root))
    from sml.memory import DIM, MemoryStore  # noqa: E402
    return DIM, MemoryStore


def unit(v):
    return v / np.linalg.norm(v)


def build_case(store, rng, dim, critical_age_days):
    kv = unit(rng.normal(size=dim))
    q = unit(kv + 0.6 * rng.normal(size=dim) / math.sqrt(dim))
    near = lambda base, s: unit(base + s * rng.normal(size=dim) / math.sqrt(dim)).tolist()
    prov = {"source": "mem-decay-001-s1", "locator": "synthetic", "sha256": "0" * 64}
    crit = store.put("critical", "constraint-value", provenance=prov, protected=True, weight=1.0,
                     timestamp=NOW - critical_age_days * DAY, embedding=near(q, 0.25))
    for j in range(COMPETITORS):
        store.put(f"competitor{j}", f"value{j}", provenance=prov, weight=1.0,
                  timestamp=NOW - float(rng.uniform(0, 30)) * DAY, embedding=near(q, 0.45))
    for j in range(FILLER):
        store.put(f"filler{j}", f"f{j}", provenance=prov,
                  timestamp=NOW - float(rng.uniform(0, 365)) * DAY, embedding=unit(rng.normal(size=dim)).tolist())
    return crit, q.tolist()


def run_cases(MemoryStore, dim, age_lo, age_hi, seed, half_life=None):
    rng = np.random.default_rng(seed)
    methods = ("similarity", "recency", "importance", "protected")
    hits = {f"retrieve/{m}": 0 for m in methods}
    hits.update({f"recall/{m} KNOWN": 0 for m in methods})
    extra = {} if half_life is None else {"half_life": half_life}
    with tempfile.TemporaryDirectory() as tmp:
        for c in range(CASES):
            store = MemoryStore(Path(tmp) / f"case{c}", create=True, max_records=64,
                                max_bytes=4_000_000, clock=lambda: NOW)
            crit, q = build_case(store, rng, dim, float(rng.uniform(age_lo, age_hi)))
            for m in methods:
                top = [h["record"]["id"] for h in store.retrieve("critical", method=m, top_k=5, embedding=q, **extra)]
                hits[f"retrieve/{m}"] += crit in top
                rec = store.recall("critical", method=m, top_k=5, embedding=q, **extra)
                hits[f"recall/{m} KNOWN"] += rec["status"] == "KNOWN"
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description="MEM-DECAY-001 S1 (SML arm)")
    ap.add_argument("--sml", required=True)
    ap.add_argument("--expect-digest")
    a = ap.parse_args(argv)
    dim, MemoryStore = load_sml(a.sml)
    print(f"MEM-DECAY-001 S1 | SML {PIN[:7]} | python {sys.version.split()[0]} numpy {np.__version__} | dim {dim}")
    print(f"{CASES} cases; each: 1 protected critical (220-365 d), {COMPETITORS} newer competitors (0-30 d), "
          f"{FILLER} filler; SML defaults half_life 30 d, threshold 0.15; top_k 5")
    main_hits = run_cases(MemoryStore, dim, 220, 365, SEED)
    ctrl_recent = run_cases(MemoryStore, dim, 0, 1, SEED + 1)
    ctrl_inf = run_cases(MemoryStore, dim, 220, 365, SEED, half_life=1e15)
    for label, h in (("main (old protected critical)", main_hits),
                     ("control A: critical 0-1 days old", ctrl_recent),
                     ("control B: half_life 1e15 s", ctrl_inf)):
        print(f"\n{label}")
        for k, v in h.items():
            print(f"  {k:28} {v:>3}/{CASES} {v / CASES:.3f}")
    r = lambda h, k: h[k] / CASES
    preds = {
        "S1a retrieve/similarity finds the old protected critical record in >= 0.95 of cases":
            r(main_hits, "retrieve/similarity") >= 0.95,
        "S1b retrieve/protected finds it in <= 0.05 of cases (decay buries a protected record)":
            r(main_hits, "retrieve/protected") <= 0.05,
        "S1c recall(key, method=protected) answers KNOWN in <= 0.05 of cases (stored but reported UNKNOWN)":
            r(main_hits, "recall/protected KNOWN") <= 0.05,
        "S1d recall(key) with the default method (similarity) answers KNOWN in >= 0.95 of cases":
            r(main_hits, "recall/similarity KNOWN") >= 0.95,
    }
    controls = {
        "control A: a recent protected critical is found by retrieve/protected in >= 0.95":
            r(ctrl_recent, "retrieve/protected") >= 0.95,
        "control B: with no effective decay, retrieve/protected finds it in >= 0.95":
            r(ctrl_inf, "retrieve/protected") >= 0.95,
    }
    print()
    for k, v in preds.items():
        print(f"{'HELD   ' if v else 'REFUTED'} {k}")
    rc = 0
    for k, v in controls.items():
        print(f"{'HELD  ' if v else 'FAILED'} {k}")
        rc |= 0 if v else 1
    dg = hashlib.sha256(json.dumps({"main": main_hits, "A": ctrl_recent, "B": ctrl_inf},
                                   sort_keys=True).encode()).hexdigest()
    print(f"DIGEST {dg}")
    if a.expect_digest and a.expect_digest != dg:
        print(f"DIGEST MISMATCH (expected {a.expect_digest})")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
