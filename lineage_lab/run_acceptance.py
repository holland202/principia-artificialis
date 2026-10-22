"""Deterministic acceptance instrument for PA-LINEAGE-001; self-tested only."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from .core import JournalError, _canonical, append, graph, init, read_events

ROOT = Path(__file__).resolve().parent
# Pinned AFTER the first observed registered output (CI run 38612373839), not in prereg.
RECORDED_DIGEST = "209e78c4bb5385a44fb6bf8b3493df37b6786b14a8b63b313712812790af6d66"


def _who():
    return {"contributor": "Fixture (fictional)", "contributor_kind": "human",
            "model": "", "review_level": "none"}


def _idea(parent=None, reason=""):
    return {**_who(), "title": "Toy idea", "claim": "A always exceeds B",
            "parent_id": parent, "reason": reason}


def _test(hypothesis_id, **kw):
    return {**_who(), "hypothesis_id": hypothesis_id,
            "prediction": "P1: A always exceeds B",
            "observation": "Toy B equalled A", "outcome": "REFUTED",
            "evidence_ref": "synthetic:fixture", "scope": "toy case, not real data",
            "lesson": "Universal assertion refuted under toy conditions",
            "next_question": "What are valid narrower conditions?", **kw}


def run():
    results = {}
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "j.jsonl"
        init(path)
        a = append(path, "hypothesis", _idea())
        t = append(path, "result", _test(a["id"]))
        c = append(path, "hypothesis", _idea(a["id"], "toy counterexample"))
        events = read_events(path, require_nonempty=True)
        g = graph(events)
        results["P1"] = "HELD" if (
            len(events) == 3 and events[0]["id"] == a["id"] and
            events[1]["id"] == t["id"] and events[2]["id"] == c["id"] and
            any(e["relation"] == "revises" and e["to"] == a["id"] for e in g["edges"])
        ) else "REFUTED"

        baseline = path.read_bytes()
        denies = 0
        for field in ("prediction", "scope", "evidence_ref"):
            d = _test(a["id"])
            d[field] = ""
            try:
                append(path, "result", d)
            except JournalError:
                denies += 1
        results["P2"] = "HELD" if denies == 3 and path.read_bytes() == baseline else "REFUTED"

        original = path.read_text(encoding="utf-8")
        path.write_text(original.replace("Toy idea", "Bogus idea"), encoding="utf-8")
        try:
            read_events(path, require_nonempty=True)
            results["P3"] = "REFUTED"
        except JournalError:
            results["P3"] = "HELD"
        path.write_text(original, encoding="utf-8")

        denies = 0
        for kind, data in (("hypothesis", _idea("bogus", "fake")), ("result", _test("bogus"))):
            try:
                append(path, kind, data)
            except JournalError:
                denies += 1
        results["P4"] = "HELD" if denies == 2 and path.read_bytes() == baseline else "REFUTED"

        try:
            append(path, "hypothesis", {**_idea(), "scientific_status": "SUPPORTED"})
            denied_status = False
        except JournalError:
            denied_status = True
        g = graph(read_events(path, require_nonempty=True))
        results["P5"] = "HELD" if (
            denied_status and path.read_bytes() == baseline and
            all(n["scientific_status"] == "UNASSESSED" for n in g["nodes"] if n["kind"] == "hypothesis")
            and g["nodes"][1]["outcome"] == "REFUTED"
        ) else "REFUTED"

        benign = subprocess.run([sys.executable, "-m", "lineage_lab", "verify", "--journal", str(path)],
                                capture_output=True, text=True, cwd=ROOT.parent)
        sabotage = subprocess.run([sys.executable, "-m", "lineage_lab", "verify", "--journal",
                                   str(path), "--sabotage"], capture_output=True, text=True, cwd=ROOT.parent)
        results["P6"] = "HELD" if (
            benign.returncode == 0 and "GATE: PASS" in benign.stdout and
            sabotage.returncode == 1 and "mutation detected" in sabotage.stdout
        ) else "REFUTED"

    # Registered P7 is static-source inspection, NOT an executed browser validation.
    html = (ROOT / "explorer.html").read_text(encoding="utf-8")
    static_check = ('id="proposal"' in html and "showDetail" in html
                    and "textContent" in html and "await file.text()" in html
                    and "URL.createObjectURL" in html)
    results["P7"] = "NOT RUN"  # Browser behavior not executed in this instrument.
    print("P7_STATIC_SOURCE_CHECK:", "PRESENT" if static_check else "MISSING",
          "(not browser execution)")
    if not static_check:
        results["P7"] = "IMPLEMENTATION_ERROR"

    for prediction, outcome in results.items():
        print(prediction, outcome)
    held = sum(1 for v in results.values() if v == "HELD")
    print("VERDICT", held, "of", len(results), "as registered")
    digest = hashlib.sha256(_canonical(results).encode("utf-8")).hexdigest()
    print("DIGEST", digest)
    if digest != RECORDED_DIGEST:
        print("GATE: FAIL — acceptance digest differs from separately recorded CI result")
        return 1
    return 0 if all(v == "HELD" for k, v in results.items() if k != "P7") and static_check else 1


if __name__ == "__main__":
    raise SystemExit(run())
