#!/usr/bin/env python3
"""Metadata screen and replay of already public CST development archives only.

Codex / OpenAI GPT-6 Astra, 2026-11-15. Direction-only human review.
No scientific outcomes are selected or inferred here. No sealed split is read.
"""
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inventory = []
    for directory in ("research_notes", "notes"):
        for path in sorted((ROOT / directory).glob("*.md")):
            lines = path.read_text().splitlines()
            inventory.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path),
                              "title": next((l.lstrip("# ") for l in lines if l.startswith("# ")), ""),
                              "status": next((l for l in lines if "**Status" in l), "not extracted")})
    print(json.dumps({"review_base": "ed2e9dd3b5d7123aab8388b7738ff97c9ed349c7",
                      "research_notes_markdown": sum(r["path"].startswith("research_notes/") for r in inventory),
                      "notes_markdown": sum(r["path"].startswith("notes/") for r in inventory),
                      "screening_only_not_full_text_novelty_proof": inventory}, indent=2, sort_keys=True))


def replay():
    print("ARCHIVE REPLAY ONLY; ORIGINAL AUTHOR SCORER; NO NEW INFERENCE")
    for split, filename, hop in (("dev", "dev_outputs_7b.jsonl", None), ("dev2", "dev2_hop2_7b.jsonl", "2")):
        path = ROOT / "results" / "cst_001" / filename
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        keys = [(r["pair"], r["version"], r["arm"]) for r in rows]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate development archive keys")
        print(json.dumps({"path": str(path.relative_to(ROOT)), "rows": len(rows), "sha256": sha(path),
                          "duplicate_keys": len(keys) - len(set(keys))}, sort_keys=True), flush=True)
        cmd = [sys.executable, str(ROOT / "experiments/cst_001/analyze.py"), split, str(path)]
        if hop:
            cmd.append(hop)
        subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    elif sys.argv[1:] == ["--replay-dev"]:
        replay()
    elif sys.argv[1:] == ["--environment"]:
        print(json.dumps({"python": sys.version, "platform": platform.platform(),
                          "machine": platform.machine(), "packages_required": "Python standard library only",
                          "model_inference": "NOT RUN", "independence": "self-tested; same-vendor proposal review"}, indent=2))
    else:
        raise SystemExit("Only metadata, --replay-dev, or --environment is supported")
