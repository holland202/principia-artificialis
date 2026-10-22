import json, os, sys, subprocess, tempfile, pathlib
sys.path.insert(0, sys.argv[1])
from lineage_lab.core import (append, init, read_events, graph, _canonical, _digest, JournalError)
W = pathlib.Path(tempfile.mkdtemp(dir=sys.argv[2]))
who = {"contributor": "t", "contributor_kind": "human"}
def fresh(name):
    p = W / name; init(p)
    h = append(p, "hypothesis", {**who, "title": "a", "claim": "b"})
    return p, h
def rewrite(p, events):  # recompute a valid chain over modified events
    prev = "0"*64; out=[]
    for e in events:
        e = dict(e); e["prev_hash"] = prev; e.pop("hash", None)
        e["hash"] = _digest(e); prev = e["hash"]; out.append(e)
    p.write_text("".join(_canonical(e)+"\n" for e in out), encoding="utf-8")
def kind(f):
    try: f(); return "accepted"
    except JournalError as x: return "JournalError: %s" % x
    except Exception as x: return "%s: %s" % (type(x).__name__, x)
# C1
p,h = fresh("c1.jsonl"); print("C1", kind(lambda: read_events(p, True)))
# C2
p,h = fresh("c2.jsonl"); s=p.read_text(); p.write_text(s.replace('"title":"a"','"title":"A"'))
print("C2", kind(lambda: read_events(p)))
# R3
p,h = fresh("r3.jsonl"); ev = read_events(p)
ev.append({"schema":"pa.lineage/1","seq":2,"id":"x2","created_utc":"2026-10-22T00:00:00+00:00","kind":"result",
  "data":{**who,"hypothesis_id":[],"prediction":"p","outcome":"NOT RUN"}})
rewrite(p, ev); print("R3", kind(lambda: read_events(p)))
r = subprocess.run([sys.executable,"-m","lineage_lab","verify","--journal",str(p)],cwd=sys.argv[1],capture_output=True,text=True)
print("R6 exit", r.returncode, "traceback" if "Traceback" in r.stderr else "no-traceback", r.stderr.strip().splitlines()[-1][:120])
# R4
p,h = fresh("r4.jsonl"); ev = read_events(p); ev[0] = dict(ev[0]); ev[0]["kind"] = []
rewrite(p, ev); print("R4", kind(lambda: read_events(p)))
# R5
p,h = fresh("r5.jsonl")
print("R5a", kind(lambda: append(p,"source",{"contributor":"m","contributor_kind":"ai","model":"x","review_level":[],"hypothesis_id":h["id"],"reference":"r"})))
print("R5b", kind(lambda: append(p,"result",{**who,"hypothesis_id":h["id"],"prediction":"p","outcome":[]})))
print("R5c", kind(lambda: append(p,"result",{**who,"hypothesis_id":{"a":1},"prediction":"p","outcome":"NOT RUN"})))
# R7
p,h = fresh("r7.jsonl"); append(p,"hypothesis",{**who,"title":"c","claim":"d"}); ev=read_events(p)
ev[1]=dict(ev[1]); ev[1]["created_utc"]="1999-01-01T00:00:00+00:00"; rewrite(p,ev); print("R7", kind(lambda: read_events(p)))
# R8
p,h = fresh("r8.jsonl")
print("R8", kind(lambda: append(p,"hypothesis",{**who,"title":"c","claim":"d","review_level":123})),
      "graph review_level =", graph(read_events(p))["nodes"][-1]["review_level"])
# R9
m = W/"missing.jsonl"; print("R9", kind(lambda: read_events(m)), "lock created:", (W/"missing.jsonl.lock").exists())
# R10
p,h = fresh("r10.jsonl"); append(p,"hypothesis",{**who,"title":"c","claim":"d"})
lines = p.read_text().splitlines(True); p.write_text("".join(lines[:-1])); print("R10", kind(lambda: read_events(p)))
