import subprocess, sys, shutil, pathlib, tempfile
root = pathlib.Path(sys.argv[1]); out = []
M = {
 "kind": ('if not isinstance(kind, str) or kind not in KINDS', 'if kind not in KINDS'),
 "hypothesis_id": ('if not isinstance(d.get("hypothesis_id"), str) or d["hypothesis_id"] not in hypotheses', 'if d.get("hypothesis_id") not in hypotheses'),
 "outcome": ('if not isinstance(d.get("outcome"), str) or d["outcome"] not in OUTCOMES', 'if d.get("outcome") not in OUTCOMES'),
 "ai_review_level": ('if not isinstance(level, str) or level not in REVIEW:', 'if level not in REVIEW:'),
 "human_review_level": ('elif level is not None and (not isinstance(level, str) or level not in REVIEW):', 'elif False:'),
}
for name, (a, b) in M.items():
    d = pathlib.Path(tempfile.mkdtemp()); shutil.copytree(root / "lineage_lab", d / "lineage_lab")
    p = d / "lineage_lab" / "core.py"; s = p.read_text(); assert s.count(a) == 1, name
    p.write_text(s.replace(a, b))
    r = subprocess.run([sys.executable, "-m", "unittest", "lineage_lab.test_audit_malformed"], cwd=d, capture_output=True, text=True)
    out.append(f"mutant {name}: {'KILLED' if r.returncode != 0 else 'SURVIVED'} ({r.stderr.strip().splitlines()[-1]})")
    shutil.rmtree(d)
# F5: crash mutant against the tightened CI gate
d = pathlib.Path(tempfile.mkdtemp()); shutil.copytree(root / "lineage_lab", d / "lineage_lab")
p = d / "lineage_lab" / "core.py"; s = p.read_text()
a = '            raise JournalError("event digest mismatch")'; assert s.count(a) == 1
p.write_text(s.replace(a, '            raise TypeError("mutant: crash instead of detecting")'))
j = str(d / "j.jsonl")
subprocess.run([sys.executable, "-m", "lineage_lab", "demo", "--journal", j], cwd=d, capture_output=True)
r = subprocess.run([sys.executable, "-m", "lineage_lab", "verify", "--journal", j, "--sabotage"], cwd=d, capture_output=True, text=True)
old_gate = r.returncode == 1; new_gate = old_gate and "mutation detected" in r.stdout
out.append(f"F5 crash mutant: rc={r.returncode}; old gate {'PASSES' if old_gate else 'fails'}; tightened gate {'PASSES' if new_gate else 'FAILS'}")
print("\n".join(out))
