"""Recompute the PA-QM-OBS-001 source identity hashes, with a negative control.

Usage (from the repository root):
    python3 experiments/qm_obs_001_audit/verify_identity_hashes.py
    python3 experiments/qm_obs_001_audit/verify_identity_hashes.py --negative-control

Each `## Sxx` entry in the sources file gives one identity line (in a ```text block) and its recorded
SHA-256 of exactly the UTF-8 bytes of that line, with no trailing newline. This script recomputes every
digest and compares it with the recorded one.

Exit codes (fail-closed, C-BUILD):
  0  every entry matches and the count equals --expect (default 10)
  1  at least one entry does not match (each mismatch is named)
  2  COULD NOT CHECK: missing or unreadable file, an entry without a line or a digest, or a count other
     than --expect. A file this script cannot read is never reported as a match.

--negative-control copies the file to a temporary directory and changes one character of S02's identity
line ("Muller" -> "Müller", the spelling the audit flagged). It then checks the copy, and it exits 0
("NEGATIVE CONTROL HELD") only if the check returns 1 and names S02. The original file is not touched.

Standard library only. Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-13.
SELF-TESTED: Claude wrote both this script and its tests. A run by someone else is what would count as
a reproduction.
"""
import argparse
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[2] / "docs" / "external" / "PA_QM_OBS_001_SOURCES_2026-10-21.md"
ENTRY = re.compile(r"^## (S\d+)\s*$", re.M)
LINE = re.compile(r"```text\n(.*?)\n```", re.S)
DIGEST = re.compile(r"\*\*Identity SHA-256:\*\*\s*`([0-9a-f]{64})`")


class CouldNotCheck(Exception):
    pass


def parse(text):
    """Return [(id, identity_line, recorded_digest)] in file order, or raise CouldNotCheck."""
    starts = [(m.group(1), m.start()) for m in ENTRY.finditer(text)]
    if not starts:
        raise CouldNotCheck("no '## Sxx' entries found")
    entries = []
    for i, (sid, pos) in enumerate(starts):
        block = text[pos:starts[i + 1][1] if i + 1 < len(starts) else len(text)]
        lines, digests = LINE.findall(block), DIGEST.findall(block)
        if len(lines) != 1 or len(digests) != 1:
            raise CouldNotCheck(f"{sid}: expected one identity line and one digest, "
                                f"found {len(lines)} and {len(digests)}")
        entries.append((sid, lines[0], digests[0]))
    ids = [e[0] for e in entries]
    if len(set(ids)) != len(ids):
        raise CouldNotCheck("duplicate entry ids")
    return entries


def check(path, expect):
    """Print one line per entry and a summary; return the exit code."""
    try:
        text = Path(path).read_text(encoding="utf-8")
        entries = parse(text)
        if len(entries) != expect:
            raise CouldNotCheck(f"found {len(entries)} entries, expected {expect}")
    except (OSError, UnicodeDecodeError, CouldNotCheck) as exc:
        print(f"COULD NOT CHECK: {exc}")
        return 2
    bad = []
    for sid, line, recorded in entries:
        got = hashlib.sha256(line.encode("utf-8")).hexdigest()
        ok = got == recorded
        print(f"{sid}  {'MATCH   ' if ok else 'MISMATCH'}  {got}")
        if not ok:
            bad.append(sid)
    if bad:
        print(f"RESULT {len(entries) - len(bad)}/{len(entries)} MATCH; MISMATCH: {', '.join(bad)}")
        return 1
    print(f"RESULT {len(entries)}/{len(entries)} MATCH")
    return 0


def negative_control(path, expect):
    original = Path(path).read_bytes()
    text = original.decode("utf-8")
    if text.count("Markus P. Muller") != 1:
        print("COULD NOT RUN NEGATIVE CONTROL: S02 marker not found exactly once")
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "mutated.md"
        copy.write_text(text.replace("Markus P. Muller", "Markus P. Müller"), encoding="utf-8")
        print("Negative control: S02 'Muller' -> 'Müller' in a temporary copy")
        rc = check(copy, expect)
    if Path(path).read_bytes() != original:
        print("COULD NOT RUN NEGATIVE CONTROL: original file changed")
        return 2
    if rc == 1:
        print("NEGATIVE CONTROL HELD: the one-character change was detected")
        return 0
    print(f"NEGATIVE CONTROL FAILED: the check returned {rc}, expected 1")
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", nargs="?", default=str(DEFAULT))
    ap.add_argument("--expect", type=int, default=10)
    ap.add_argument("--negative-control", action="store_true")
    args = ap.parse_args(argv)
    return negative_control(args.path, args.expect) if args.negative_control else check(args.path, args.expect)


if __name__ == "__main__":
    sys.exit(main())
