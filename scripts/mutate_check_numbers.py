"""Mutant check for scripts/test_check_numbers.py (note062 P8). Each mutant patches a copy of check_numbers.py
in a temp directory, never the file in the repository, and the unit tests must fail on it.

  python scripts/mutate_check_numbers.py scripts
"""
import os, shutil, subprocess, sys, tempfile
SRC = sys.argv[1]
M = [
 ("M1 checker accepts every number (self-test can no longer flag)", "def found(tok, out_tokens, out_values):\n", "def found(tok, out_tokens, out_values):\n    return True\n"),
 ("M2 main ignores a failed self-test", "    if not self_test():\n        sys.exit(1)\n", "    self_test()\n"),
 ("M3 timeout not caught", "    except subprocess.TimeoutExpired:\n        return None, f\"timed out after {timeout} s\"\n", ""),
 ("M4 not-run does not exit 2", "        sys.exit(2)", "        pass"),
 ("M5 filename fallback removed", "            name, how = note_by_filename(num), \" (paired by filename; the note does not name its script)\"", "            pass"),
 ("M6 results/ not created", "    os.makedirs(os.path.join(ROOT, \"results\"), exist_ok=True)\n", ""),
 ("M7 sentence-final period rejected again (pre-P9 pattern)", "(?![\\w])(?!\\.\\d)", "(?![\\w.])"),
]
code = open(os.path.join(SRC, "check_numbers.py")).read()
k = 0
for name, old, new in M:
    assert code.count(old) == 1, name
    d = tempfile.mkdtemp()
    open(os.path.join(d, "check_numbers.py"), "w").write(code.replace(old, new))
    shutil.copy(os.path.join(SRC, "test_check_numbers.py"), d)
    r = subprocess.run([sys.executable, "-I", "-m", "unittest", "discover", "-s", d, "-p", "test_check_numbers.py"], capture_output=True, text=True, cwd=d)
    killed = r.returncode != 0; k += killed
    print(("KILLED  " if killed else "SURVIVED"), name)
    shutil.rmtree(d)
print(f"mutants killed: {k}/{len(M)}")
