#!/usr/bin/env python3
"""The Liar's Note Space ships copies of two files. Fail if a copy differs from its original or from MANIFEST.sha256.

  python scripts/check_space_copies.py          exit 0 identical, 1 drift, 2 a file is missing
"""
import hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPACE = os.path.join(ROOT, "challenges", "redteam", "liars_note", "space")
PAIRS = {"check_numbers.py": os.path.join(ROOT, "scripts", "check_numbers.py"),
         "judge.py": os.path.join(ROOT, "challenges", "redteam", "liars_note", "judge.py")}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    try:
        manifest = dict(reversed(l.split()) for l in open(os.path.join(SPACE, "MANIFEST.sha256")) if l.strip())
        rows = [(n, sha(os.path.join(SPACE, n)), sha(o), manifest.get(n)) for n, o in PAIRS.items()]
    except OSError as e:
        print(f"MISSING: {e}")
        return 2
    bad = 0
    for name, copy, orig, pinned in rows:
        ok = copy == orig == pinned
        bad += not ok
        print(f"{'OK   ' if ok else 'DRIFT'} {name}: copy {copy[:16]} original {orig[:16]} manifest {(pinned or '-')[:16]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
