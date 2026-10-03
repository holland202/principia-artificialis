#!/usr/bin/env python3
"""method_lint.py — consistency check for the canonical method (Amendment 3, D9; METHOD.md M17).

Standard library only. Reads files; writes nothing.

  python scripts/method_lint.py              structural check            exit 0 clean, 1 violations
  python scripts/method_lint.py --coverage   inventory covers sources    exit 0, 1, or 2 (COULD NOT RUN)
  python scripts/method_lint.py --selftest   every planted defect found  exit 0, else 1
  python scripts/method_lint.py --sabotage   a planted defect            must exit 1

Structural checks (each violation prints one line with its code):
  DUP         an ID is defined more than once
  PLACE       a definition sits outside its canonical file (M: METHOD.md, W: WORKFLOW.md, C-: CONTROLS.md)
  INDEX       METHOD.md's index and the definitions disagree (ID, force or title)
  TRIGGER     a trigger points to an undefined control
  EXCERPT     an excerpt differs from its canonical block
  HOME        an inventory row points to an undefined rule, or has an unknown disposition
  NO_SOURCE   a defined rule has no inventory row
  RECORD      a record copy no longer matches its md5
  DEPRECATED  a retired outcome word appears in canonical text outside the alias block
  MISSING     a file the check needs is absent (missing means deny)

Limits: it cannot see a rule restated in other words without its ID, and coverage sees list items and
table rows only (prose is inventoried by hand).
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANON = {"METHOD.md": r"M\d+", "WORKFLOW.md": r"W\d+", "CONTROLS.md": r"C-[A-Z]+"}
INVENTORY = "methodology/RULE_INVENTORY.md"
MANIFEST = "methodology/record/MANIFEST.md"
DEPRECATED = [r"\bFAILED\b", r"simulation-only"]
DISPOSITIONS = {"RULE", "VOCAB", "SUPERSEDED", "REPO", "OPS", "DOOR", "RECORD"}
DECISIONS = {f"D{i}" for i in range(1, 14)}
PINNED = "4c7518a7e84c746d50b483970a8832949d065d48"
SOURCES = {  # key: (kind, location)
    "SWAY": ("git", "METHOD_SWAY.md"),
    "A1": ("git", "METHOD_SWAY_AMENDMENT_1.md"),
    "TEMPLATE": ("git", "NOTE_TEMPLATE.md"),
    "CLAUDE": ("git", "CLAUDE.md"),
    "A2": ("file", "methodology/record/drafts/METHOD_SWAY_AMENDMENT_2_DRAFT.md"),
    "EF": ("file", "methodology/record/skills/experiment-first.SKILL.md"),
    "PRW": ("file", "methodology/record/skills/prereg-research-workflow.SKILL.md"),
}
REF_KEYS = set(SOURCES) | {"A3"}  # A3: rules introduced by Amendment 3 itself
EXPECTED_COUNTS = {"SWAY": 61, "A1": 22, "A2": 37, "TEMPLATE": 3, "CLAUDE": 43, "EF": 14, "PRW": 52}

DEF = re.compile(r"^\s*- \*\*([A-Z][A-Z0-9-]*\d*|C-[A-Z]+)\*\* · (MUST|SHOULD|MAY) · \*\*(.+?)\*\*")
ITEM = re.compile(r"^\s*(?:[-*+]\s+(?:\[[ xX]\]\s+)?|\d+\.\s+)(\S.*)$")
SEP = re.compile(r"^\s*\|[\s:|-]+\|?\s*$")


def norm(text):
    return re.sub(r"\s+", " ", text).strip()


def short_hash(text):
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()[:10]


def title_key(t):
    return norm(t).rstrip(".").strip()


# ---------------------------------------------------------------- loading
def load_tree(root=ROOT):
    """Every Markdown file except under .git and methodology/record, plus record copies as bytes."""
    text, raw = {}, {}
    for p in root.rglob("*.md"):
        rel = p.relative_to(root).as_posix()
        if rel.startswith(".git/") or "/node_modules/" in rel:
            continue
        if rel.startswith("methodology/record/") and rel != MANIFEST:
            continue
        try:
            text[rel] = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
    rec = root / "methodology" / "record"
    if rec.is_dir():
        for p in rec.rglob("*"):
            if p.is_file():
                raw[p.relative_to(root).as_posix()] = p.read_bytes()
    return text, raw


def block(text, name, kind="canonical"):
    m = re.search(rf"<!-- {kind}:{re.escape(name)} -->\n(.*?)\n<!-- /{kind}:{re.escape(name)} -->", text, re.S)
    return m.group(1) if m else None


def table_rows(block_text):
    rows = []
    lines = block_text.split("\n")
    for i, line in enumerate(lines):
        if not line.strip().startswith("|") or SEP.match(line):
            continue
        if i + 1 < len(lines) and SEP.match(lines[i + 1]):
            continue  # header
        rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


# ---------------------------------------------------------------- structural check
def check(text, raw):
    errs = []
    for f in list(CANON) + [INVENTORY, MANIFEST]:
        if f not in text:
            errs.append(f"MISSING {f}")
    if errs:
        return errs

    defs = {}  # id -> (file, force, title)
    for f, body in text.items():
        for line in body.split("\n"):
            m = DEF.match(line)
            if not m:
                continue
            rid, force, title = m.group(1), m.group(2), m.group(3)
            if rid in defs:
                errs.append(f"DUP {rid} defined in {defs[rid][0]} and {f}")
                continue
            defs[rid] = (f, force, title_key(title))
            home = next((c for c, pat in CANON.items() if re.fullmatch(pat, rid)), None)
            if home != f:
                errs.append(f"PLACE {rid} defined in {f}; its canonical file is {home}")

    for f in CANON:
        if not any(DEF.match(line) for line in text[f].split("\n")):
            errs.append(f"MISSING no rule definitions found in {f}")

    index = block(text["METHOD.md"], "index")
    if index is None:
        errs.append("MISSING METHOD.md index block")
    else:
        seen = set()
        for row in table_rows(index):
            if len(row) < 3:
                continue
            rid, force, title = row[0], row[1], title_key(row[2])
            seen.add(rid)
            if rid not in defs:
                errs.append(f"INDEX {rid} is indexed but not defined")
            elif (defs[rid][1], defs[rid][2]) != (force, title):
                errs.append(f"INDEX {rid}: index says {force} '{title}', definition says {defs[rid][1]} '{defs[rid][2]}'")
        for rid in defs:
            if rid not in seen:
                errs.append(f"INDEX {rid} is defined but not indexed")

    trig = block(text["METHOD.md"], "triggers")
    if trig is None:
        errs.append("MISSING METHOD.md triggers block")
    else:
        for row in table_rows(trig):
            if len(row) >= 3 and row[2] not in defs:
                errs.append(f"TRIGGER '{row[0]}' points to undefined control {row[2]}")

    for f, body in text.items():
        for m in re.finditer(r"<!-- excerpt: ([\w.]+)#([\w-]+) -->\n(.*?)\n<!-- /excerpt -->", body, re.S):
            src, name, content = m.group(1), m.group(2), m.group(3)
            canon = block(text.get(src, ""), name)
            if canon is None:
                errs.append(f"EXCERPT {f}: {src}#{name} has no canonical block")
            elif content.strip() != canon.strip():
                errs.append(f"EXCERPT {f}: differs from {src}#{name}")

    homes = set()
    for row in table_rows(text[INVENTORY]):
        if len(row) < 7 or row[0].split("-")[0] not in REF_KEYS:
            continue
        disp, home = row[5], row[6]
        if disp not in DISPOSITIONS:
            errs.append(f"HOME {row[0]}: unknown disposition '{disp}'")
            continue
        for h in [x.strip() for x in home.split(",") if x.strip() and x.strip() != "-"]:
            if h == "VOCAB" or h in DECISIONS or h in defs:
                homes.add(h)
            else:
                errs.append(f"HOME {row[0]}: home '{h}' is not a defined rule, VOCAB or a decision")
        if disp in ("RULE", "VOCAB", "SUPERSEDED") and home.strip() in ("", "-"):
            errs.append(f"HOME {row[0]}: disposition {disp} needs a home")
    for rid in defs:
        if rid not in homes:
            errs.append(f"NO_SOURCE {rid} has no inventory row")

    for row in table_rows(text[MANIFEST]):
        if len(row) < 2:
            continue
        path = "methodology/record/" + row[0].strip("`")
        want = row[1].strip("`")
        data = raw.get(path)
        if data is None:
            errs.append(f"RECORD {path} is missing")
        elif hashlib.md5(data).hexdigest() != want:
            errs.append(f"RECORD {path} md5 {hashlib.md5(data).hexdigest()} != {want}")

    for f in CANON:
        body = re.sub(r"<!-- aliases -->.*?<!-- /aliases -->", "", text[f], flags=re.S)
        for pat in DEPRECATED:
            for m in re.finditer(pat, body):
                errs.append(f"DEPRECATED {f}: '{m.group(0)}' outside the alias block")
    return errs


# ---------------------------------------------------------------- coverage
def extract_items(text):
    lines = text.split("\n")
    out, i, fenced = [], 0, False
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    for n in range(i, len(lines)):
        line = lines[n]
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.lstrip().startswith("|"):
            if SEP.match(line) or (n + 1 < len(lines) and SEP.match(lines[n + 1])):
                continue
            out.append((n + 1, norm(line)))
            continue
        m = ITEM.match(line)
        if m:
            out.append((n + 1, norm(m.group(1))))
    return out


def source_text(key):
    kind, loc = SOURCES[key]
    if kind == "file":
        p = ROOT / loc
        return p.read_text(encoding="utf-8") if p.exists() else None
    try:
        ok = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{PINNED}^{{commit}}"],
                            capture_output=True).returncode == 0
        if not ok:
            return None
        r = subprocess.run(["git", "-C", str(ROOT), "show", f"{PINNED}:{loc}"], capture_output=True)
        return r.stdout.decode("utf-8") if r.returncode == 0 else None
    except OSError:
        return None


def coverage():
    text, _ = load_tree()
    if INVENTORY not in text:
        print("MISSING inventory")
        return 1
    rows = {}
    for row in table_rows(text[INVENTORY]):
        if len(row) >= 7 and row[0].split("-")[0] in SOURCES and row[2] != "prose":
            rows.setdefault((row[0].split("-")[0], row[2], row[3].strip("`")), []).append(row)
    bad, total = 0, 0
    for key in SOURCES:
        body = source_text(key)
        if body is None:
            print(f"COULD NOT RUN: source {key} unavailable (pinned commit {PINNED[:7]} not in history?)")
            return 2
        its = extract_items(body)
        total += len(its)
        missing = [(ln, t) for ln, t in its if len(rows.get((key, str(ln), short_hash(t)), [])) != 1]
        flag = "" if len(its) == EXPECTED_COUNTS[key] else f"  (registered count {EXPECTED_COUNTS[key]})"
        print(f"{key:9s} items {len(its):3d}  without exactly one inventory row: {len(missing)}{flag}")
        for ln, t in missing:
            print(f"   UNPLACED {key}:{ln} {short_hash(t)} {t[:70]}")
        bad += len(missing) + (len(its) != EXPECTED_COUNTS[key])
    print(f"TOTAL items {total}  (registered 232)")
    disp = {}
    for row in table_rows(text[INVENTORY]):
        if len(row) >= 7 and row[0].split("-")[0] in REF_KEYS:
            disp[row[5]] = disp.get(row[5], 0) + 1
    print("inventory rows by disposition: " + ", ".join(f"{k} {v}" for k, v in sorted(disp.items())))
    print("COVERAGE: " + ("PASS" if bad == 0 and total == 232 else "FAIL"))
    return 0 if bad == 0 and total == 232 else 1


# ---------------------------------------------------------------- self-test and sabotage
def plant(text, raw, kind):
    t, r = dict(text), dict(raw)
    if kind == "DUP":
        t["WORKFLOW.md"] += "\n- **W1** · MUST · **Frame the question.** planted duplicate\n"
    elif kind == "PLACE":
        t["README.md"] = t.get("README.md", "") + "\n- **M99** · MUST · **Planted rule.** defined outside METHOD.md\n"
    elif kind == "INDEX":
        t["METHOD.md"] = t["METHOD.md"].replace("| M2 | MUST | Register before observing |", "| M2 | SHOULD | Register before observing |")
    elif kind == "TRIGGER":
        t["METHOD.md"] = t["METHOD.md"].replace("| C-FEAS | |", "| C-NOPE | |", 1)
    elif kind == "EXCERPT":
        f = next((k for k, v in t.items() if "<!-- excerpt: METHOD.md#index -->" in v), None)
        if f:  # no excerpt to corrupt means the plant does nothing, and the self-test reports MISSED
            t[f] = t[f].replace("| M1 | MUST |", "| M1 | MAY |", 1)
    elif kind == "HOME":
        t[INVENTORY] = re.sub(r"\| RULE \| M1 \|", "| RULE | M99 |", t[INVENTORY], count=1)
    elif kind == "NO_SOURCE":
        t[INVENTORY] = re.sub(r"\| RULE \| M18 \|", "| RULE | M17 |", t[INVENTORY])
    elif kind == "DEPRECATED":
        t["WORKFLOW.md"] += "\nA prediction that did not hold is marked FAILED.\n"
    elif kind == "RECORD":
        k = next(iter(sorted(x for x in r if not x.endswith("MANIFEST.md"))))
        r[k] = r[k] + b" "
    elif kind == "MISSING":
        t.pop("CONTROLS.md", None)
    elif kind == "EMPTY":
        t["CONTROLS.md"] = "\n".join(x for x in t["CONTROLS.md"].split("\n") if not DEF.match(x))
    return t, r


CLASSES = [("DUP", "DUP"), ("PLACE", "PLACE"), ("INDEX", "INDEX"), ("TRIGGER", "TRIGGER"),
           ("EXCERPT", "EXCERPT"), ("HOME", "HOME"), ("NO_SOURCE", "NO_SOURCE"),
           ("DEPRECATED", "DEPRECATED"), ("RECORD", "RECORD"), ("MISSING", "MISSING"),
           ("EMPTY", "MISSING")]  # (planted defect, code that must report it)


def selftest():
    text, raw = load_tree()
    base = check(text, raw)
    if base:
        print("SELFTEST cannot start: the real tree has violations")
        for e in base:
            print("  " + e)
        return 1
    ok = True
    for kind, code in CLASSES:
        t, r = plant(text, raw, kind)
        errs = check(t, r)
        hit = any(e.startswith(code) for e in errs)
        print(f"{'DETECTED' if hit else 'MISSED  '} {kind:10s} as {code:10s} ({len(errs)} violation(s))")
        ok &= hit
    print("SELFTEST: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--coverage" in argv:
        return coverage()
    if "--selftest" in argv:
        return selftest()
    text, raw = load_tree()
    if "--sabotage" in argv:
        text, raw = plant(text, raw, "DUP")
    errs = check(text, raw)
    for e in errs:
        print(e)
    print(f"method_lint: {len(errs)} violation(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
