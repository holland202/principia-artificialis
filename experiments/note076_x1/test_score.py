"""Tests for score.py (C-BUILD). Needs a Sovereign Veritas checkout: set SV_ROOT, else skipped.

The scorer must be able to say "differ" and "crash" (M3): every check below that passes for a correct port has a
sabotaged twin that it must fail.
"""
import json
import os
import pathlib
import subprocess
import sys

import pytest

HERE = pathlib.Path(__file__).resolve().parent
SV = os.environ.get("SV_ROOT")
pytestmark = pytest.mark.skipif(not SV, reason="set SV_ROOT to a Sovereign Veritas checkout")
sys.path.insert(0, str(HERE))
import score  # noqa: E402

VERIFIER = [sys.executable, f"{SV}/tools/gate_contract.py", "--serve", "verifier"] if SV else []

WRAP = r'''
import json, subprocess, sys
mode, cmd = sys.argv[1], sys.argv[2:]
lines = sys.stdin.read().splitlines(keepends=True)
out = subprocess.run(cmd, input="".join(lines), capture_output=True, text=True).stdout.splitlines()
for line in out:
    o = json.loads(line)
    if mode == "x_reason" and o["id"].startswith("X") and o["reasons"]:
        o["reasons"] = o["reasons"] + ["sabotage"]
    if mode == "allow":
        o["decision"], o["reasons"] = "ALLOW", []
    if mode == "crash":
        sys.exit(3)
    print(json.dumps(o))
'''


@pytest.fixture
def wrapper(tmp_path):
    p = tmp_path / "wrap.py"
    p.write_text(WRAP)
    return lambda mode: [sys.executable, str(p), mode] + VERIFIER


def run(argv, capsys):
    code = score.main(argv)
    return code, capsys.readouterr().out


def test_vectors_conforming_port(capsys):
    code, out = run(["vectors", "--sv-root", SV, "--"] + VERIFIER, capsys)
    assert code == 0 and "VERDICT  CONFORMS" in out and "L=0 S=0 X=0" in out


def test_vectors_sabotaged_port_is_counted_in_x(wrapper, capsys):
    code, out = run(["vectors", "--sv-root", SV, "--"] + wrapper("x_reason"), capsys)
    assert code == 1 and "L=0 S=0" in out and "X=0" not in out and "MISMATCH X:" in out


def test_vectors_crashing_port_could_not_run(wrapper, capsys):
    with pytest.raises(SystemExit) as e:
        score.main(["vectors", "--sv-root", SV, "--"] + wrapper("crash"))
    assert e.value.code == 2


def test_probes_crash_and_allow(wrapper, capsys, tmp_path):
    code, out = run(["probes", "--sv-root", SV, "--"] + wrapper("crash"), capsys)
    rows = [json.loads(l.split(" ", 2)[2]) for l in out.splitlines()]
    assert code == 0 and len(rows) == 6 and all(r["outcome"] == "CRASH" for r in rows)
    _, out = run(["probes", "--sv-root", SV, "--"] + wrapper("allow"), capsys)
    rows = [json.loads(l.split(" ", 2)[2]) for l in out.splitlines()]
    assert all(r["outcome"] == ["ALLOW", []] for r in rows)


def test_compare_agree_and_differ(tmp_path, capsys):
    same = "".join(f'PROBE {p} {{"outcome": ["DEFER", ["r"]]}}\n' for p, _, _ in score.PROBES)
    other = same.replace('PROBE Q3 {"outcome": ["DEFER", ["r"]]}', 'PROBE Q3 {"outcome": "CRASH"}')
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text(same)
    b.write_text(other)
    assert score.main(["compare", str(a), str(a)]) == 0
    assert score.main(["compare", str(a), str(b)]) == 1
    assert "Q3 DIFFER" in capsys.readouterr().out


def test_compare_rejects_missing_probe(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text('PROBE Q1 {"outcome": "CRASH"}\n')
    assert score.main(["compare", str(a), str(a)]) == 2


def test_probe_inputs_are_the_registered_six():
    gct = score.load_gct(SV)
    probes = score.probe_inputs(gct.read_vectors())
    assert [p for p, _ in probes] == ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]
    q1 = dict(probes)["Q1"]
    assert q1["capability"]["min_evidence_quality"] == 10 ** 400 and q1["record"]["evidence_quality"] == 0.2
