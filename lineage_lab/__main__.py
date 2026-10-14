"""Local CLI for PA-LINEAGE-001. Standard library only; never contacts remote services."""
import argparse
import json
import sys
from pathlib import Path

from .core import JournalError, _canonical, _check_events, append, graph, init, read_events


def actor(p):
    p.add_argument("--contributor", required=True, help="Credited name or agent label")
    p.add_argument("--contributor-kind", choices=["human", "ai"], required=True)
    p.add_argument("--model", default="", help="Required when contributor is an AI")
    p.add_argument("--review-level", choices=["none", "direction only", "outcome review", "line-by-line"], default="none")


def actor_data(a):
    return {"contributor": a.contributor, "contributor_kind": a.contributor_kind,
            "model": a.model, "review_level": a.review_level}


def journal(p):
    p.add_argument("--journal", required=True, help="Existing JSONL journal file")


def parser():
    p = argparse.ArgumentParser(description="PA Scientific Lineage Lab (local, self-reported research history)")
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("init", help="Create an empty local journal (refuses overwrite)")
    journal(q)
    q = sub.add_parser("demo", help="Create fictional branching research examples")
    journal(q)
    q = sub.add_parser("hypothesis", help="Register a new or revised hypothesis")
    journal(q); actor(q)
    q.add_argument("--title", required=True)
    q.add_argument("--claim", required=True)
    q.add_argument("--parent-id")
    q.add_argument("--reason", default="", help="Required for a revision")
    q = sub.add_parser("result", help="Attach a contributor-reported prediction outcome")
    journal(q); actor(q)
    q.add_argument("--hypothesis-id", required=True)
    q.add_argument("--prediction", required=True)
    q.add_argument("--outcome", required=True)
    q.add_argument("--observation", default="")
    q.add_argument("--evidence-ref", default="")
    q.add_argument("--scope", default="")
    q.add_argument("--lesson", default="")
    q.add_argument("--next-question", default="")
    q = sub.add_parser("source", help="Cite a source (not automatically authenticated)")
    journal(q); actor(q)
    q.add_argument("--hypothesis-id", required=True)
    q.add_argument("--reference", required=True)
    q.add_argument("--description", default="")
    q = sub.add_parser("verify", help="Check chain and event schema; NOT scientific truth")
    journal(q); q.add_argument("--sabotage", action="store_true")
    q = sub.add_parser("export", help="Export safe graph JSON for offline viewer")
    journal(q); q.add_argument("--out", required=True)
    q = sub.add_parser("admit", help="Explicitly admit locally saved JSON proposal")
    journal(q); q.add_argument("--proposal", required=True)
    return p


def demo(path):
    init(path)
    who = {"contributor": "Example researcher (fictional)", "contributor_kind": "human",
           "model": "", "review_level": "none"}
    a = append(path, "hypothesis", {**who, "title": "Five agents always outperform one",
                                    "claim": "For every evaluation case, five collaborating agents have greater accuracy than one.",
                                    "parent_id": None, "reason": ""})
    append(path, "source", {**who, "hypothesis_id": a["id"],
                            "reference": "synthetic:classroom-example", "description": "Not a real research citation"})
    append(path, "result", {**who, "hypothesis_id": a["id"],
                           "prediction": "Five agents beat one in every constructed test case.",
                           "observation": "One toy case ties the single-agent baseline.",
                           "outcome": "REFUTED", "evidence_ref": "synthetic:toy-case-only",
                           "scope": "Fictional classroom exercise; NOT an empirical benchmark",
                           "lesson": "A universal statement fails when a counterexample exists.",
                           "next_question": "Under which conditions does collaboration improve performance?"})
    b = append(path, "hypothesis", {**who, "title": "Conditional multi-agent benefit",
                                    "claim": "Collaboration might help when agents make less-correlated errors.",
                                    "parent_id": a["id"], "reason": "A counterexample defeats the universal form."})
    print("DEMO: FICTIONAL DATA ONLY; no real scientific result")
    print("root:", a["id"])
    print("revision:", b["id"])
    print("journal:", path)


def main(argv=None):
    p = parser()
    a = p.parse_args(argv)
    try:
        path = Path(a.journal)
        if a.command == "init":
            init(path)
            print("INIT: empty journal", str(path))
        elif a.command == "demo":
            demo(path)
        elif a.command in ("hypothesis", "result", "source"):
            who = actor_data(a)
            if a.command == "hypothesis":
                data = {**who, "title": a.title, "claim": a.claim,
                        "parent_id": a.parent_id, "reason": a.reason}
            elif a.command == "result":
                data = {**who, "hypothesis_id": a.hypothesis_id,
                        "prediction": a.prediction, "observation": a.observation,
                        "outcome": a.outcome, "evidence_ref": a.evidence_ref,
                        "scope": a.scope, "lesson": a.lesson, "next_question": a.next_question}
            else:
                data = {**who, "hypothesis_id": a.hypothesis_id,
                        "reference": a.reference, "description": a.description}
            e = append(path, a.command, data)
            print("APPENDED", e["kind"], e["id"], e["hash"])
        elif a.command == "verify":
            events = read_events(path, require_nonempty=True)
            if a.sabotage:
                mutated = json.loads(_canonical(events))
                first = mutated[0]
                first["created_utc"] = "2000-01-01T00:00:00+00:00"
                try:
                    _check_events(mutated, require_nonempty=True)
                except JournalError:
                    print("GATE: FAIL — planted mutation detected")
                    return 1
                print("GATE: PASS — FAILURE: mutation was accepted")
                return 0
            print("GATE: PASS", "events=" + str(len(events)), "head=" + events[-1]["hash"])
        elif a.command == "export":
            events = read_events(path, require_nonempty=True)
            output = Path(a.out)
            if output.resolve() == path.resolve():
                raise JournalError("cannot overwrite journal with export")
            output.write_text(json.dumps(graph(events), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print("EXPORTED", str(output))
        elif a.command == "admit":
            proposal_path = Path(a.proposal)
            if proposal_path.stat().st_size > 100000:
                raise JournalError("proposal too large")
            proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
            if not isinstance(proposal, dict) or set(proposal) != {"kind", "data"}:
                raise JournalError("proposal must contain only kind and data")
            event = append(path, proposal["kind"], proposal["data"])
            print("ADMITTED after local CLI invocation:", event["id"])
    except (JournalError, FileNotFoundError, OSError, ValueError, KeyError) as exc:
        print("GATE: FAIL —", str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
