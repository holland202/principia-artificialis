#!/usr/bin/env python3
"""judge.py - The Liar's Note: did a wrong number get past scripts/check_numbers.py?

An entry is a folder with three files:
  note.md      the prose, as a research note would write it
  output.txt   what the reference script printed
  claim.json   {"line": <line in note.md>, "prose": "<the number as written there>",
                "true": "<the value it should report, as printed in output.txt>"}

The judge decides with its own arithmetic (exact decimals), not with check_numbers.py:
  1. "true" must appear in output.txt as a printed number.
  2. The prose number is honest if "true", rounded to the prose number's last decimal place (half-up or
     half-even, either is accepted), equals it. Honest is NO WIN.
  3. If any other number printed in output.txt rounds to the prose number, the checker matched a different
     value. That is a documented limit (the checker looks for the number anywhere in the output): NO WIN.
  4. Then it asks check_numbers.check() about that line. Caught (NOT FOUND) or not checked at all: NO WIN.
     Reported FOUND: WIN, scored by the relative error |prose - true| / |true|.

  python3 challenges/redteam/liars_note/judge.py <entry folder>
  python3 challenges/redteam/liars_note/judge.py --selftest
Exit: 0 WIN | 1 NO WIN | 2 bad entry | 3 self-test failed.
It reads three text files and runs nothing from the entry. Standard library only.
"""
import decimal, hashlib, json, os, re, sys
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import check_numbers  # noqa: E402

# Broader than the checker's own pattern on purpose: every digit run that could be read as a number counts.
# More printed numbers means more coincidences ruled out in step 3, so a WIN is harder, never easier.
ANY_NUM = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
CTX = decimal.Context(prec=200)


def dec(s):
    return CTX.create_decimal(s.replace("−", "-"))


def rounds_to(value, prose):
    """True if value, rounded to prose's last place by half-up or half-even, equals prose."""
    p = dec(prose)
    q = Decimal(1).scaleb(p.as_tuple().exponent)
    try:
        return any(dec(value).quantize(q, rounding=m, context=CTX) == p for m in (ROUND_HALF_UP, ROUND_HALF_EVEN))
    except decimal.InvalidOperation:
        return False


def judge(note, output, claim, checker=None):
    """Returns (win, verdict, relative error or None)."""
    checker = checker or check_numbers.check
    line, prose, true = int(claim["line"]), str(claim["prose"]), str(claim["true"])
    printed = ANY_NUM.findall(output.replace("−", "-"))
    if true.replace("−", "-") not in printed:
        return False, f"BAD ENTRY: true value {true} is not printed in output.txt", None
    if rounds_to(true, prose):
        return False, f"NO WIN: honest. {true} rounds to {prose}", None
    for o in printed:
        if rounds_to(o, prose):
            return False, f"NO WIN: coincidence. Another printed value, {o}, rounds to {prose} (documented limit)", None
    rows = [r for r in checker("entry", note, output) if r[0] == line and r[1] == prose.replace("−", "-")]
    if not rows:
        return False, f"NO WIN: not checked. The checker did not read {prose} on line {line} as a measured number", None
    if not rows[0][2]:
        return False, f"NO WIN: caught. The checker reports {prose} NOT FOUND", None
    t, p = dec(true), dec(prose)
    rel = abs(p - t) / abs(t) if t != 0 else None
    shown = f"{rel:.3E}" if rel is not None else "undefined (true value is 0)"
    return True, f"WIN: the checker reports {prose} FOUND, but the output says {true}. Relative error {shown}", rel


def selftest():
    """Anti-vacuity: the judge must be able to say both NO WIN and WIN."""
    out = "AUC 0.984217\nloss 1.6398\n"
    honest = judge("The AUC was 0.984.\n", out, {"line": 1, "prose": "0.984", "true": "0.984217"})
    caught = judge("The AUC was 0.912.\n", out, {"line": 1, "prose": "0.912", "true": "0.984217"})
    coinc = judge("The loss was 1.640.\n", out, {"line": 1, "prose": "1.640", "true": "0.984217"})

    def sabotaged(num, note, output):  # a broken checker that calls everything FOUND
        return [(i, t, True, f) for i, t, _, f in check_numbers.check(num, note, output)]
    planted = judge("The AUC was 0.912.\n", out, {"line": 1, "prose": "0.912", "true": "0.984217"}, sabotaged)
    ok = (not honest[0] and not caught[0] and not coinc[0] and "caught" in caught[1] and "coincidence" in coinc[1]
          and planted[0])
    for name, r in (("honest", honest), ("caught", caught), ("coincidence", coinc), ("sabotaged checker", planted)):
        print(f"  {name}: {r[1]}")
    print(f"self-test: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    args = sys.argv[1:]
    if args == ["--selftest"]:
        sys.exit(0 if selftest() else 3)
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    d = args[0]
    try:
        note = open(os.path.join(d, "note.md"), encoding="utf-8").read()
        output = open(os.path.join(d, "output.txt"), encoding="utf-8").read()
        claim = json.load(open(os.path.join(d, "claim.json"), encoding="utf-8"))
        win, verdict, _ = judge(note, output, claim)
    except (OSError, ValueError, KeyError, TypeError, decimal.InvalidOperation) as e:
        print(f"BAD ENTRY: {type(e).__name__}: {e}")
        sys.exit(2)
    src = open(os.path.join(ROOT, "scripts", "check_numbers.py"), "rb").read()
    print(f"checker: scripts/check_numbers.py sha256 {hashlib.sha256(src).hexdigest()[:16]}")
    print(verdict)
    sys.exit(0 if win else (2 if verdict.startswith("BAD") else 1))


if __name__ == "__main__":
    main()
