#!/usr/bin/env python3
"""Post-hoc description (not registered; decides nothing): how other readers see three Part C tokens.

  python3 -I experiments/pa_json_002_claude/interop_posthoc.py WORK
Readers: Python json.loads, Node JSON.parse, the system SQLite behind Python's sqlite3 module, and the verified
3.54.1 observer built in WORK. Standard library only, plus node.
"""
import json, os, sqlite3, struct, subprocess, sys, tempfile

TOKENS = {"42 hidden in a zero (X3 42:0)": "42" + "0" * 10000 + "e-100000",
          "10 hidden in a zero (X1 k=1)": "1" + "0" * 10001 + "e-100000",
          "0.1 hidden in an overflow (X2 j=1)": "0." + "0" * 10000 + "1e100000"}
work = sys.argv[1]
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
    f.write("\n".join(TOKENS.values()) + "\n")
    path = f.name
node = subprocess.run(["node", "-e", "require('fs').readFileSync(process.argv[1],'utf8').trim().split('\\n')"
                       ".forEach(t=>console.log(String(JSON.parse(t))))", path], capture_output=True, text=True)
obs = subprocess.run([os.path.join(work, "observer"), path], capture_output=True, text=True).stdout.splitlines()
os.remove(path)
db = sqlite3.connect(":memory:")
print(f"system SQLite (Python's sqlite3 module): {sqlite3.sqlite_version}; observer: {obs[0][1:].split(chr(9))[0]}")
for (name, tok), js, row in zip(TOKENS.items(), node.stdout.splitlines(), obs[1:]):
    sys_cast, sys_json = db.execute("SELECT CAST(?1 AS REAL), json_extract(?1,'$')", (tok,)).fetchone()
    mine = struct.unpack(">d", bytes.fromhex(row.split("\t")[4]))[0]
    print(f"{name}: {len(tok)} characters")
    print(f"  Python json.loads {json.loads(tok)!r}   Node JSON.parse {js}   "
          f"system SQLite CAST {sys_cast!r} json_extract {sys_json!r}   SQLite 3.54.1 json_extract {mine!r}")
