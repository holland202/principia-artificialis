"""CCC-001 outside-review check (point 6): scan files for bidirectional-control and zero-width characters.

Usage: python experiments/ccc_001/unicode_scan.py FILE [FILE ...]
.json files are parsed and every decoded string is scanned (so \\uXXXX escapes are caught); other files are read as
UTF-8 text. A built-in sabotage control injects U+202E into a copy of the first file's text and must be detected,
or the scan reports VACUOUS and exits 2. Exit 1 if any listed character is found, 0 if none.
"""
import hashlib, json, sys, unicodedata

SUSPECT = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A)) | {
    0x061C, 0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2060, 0xFEFF}


def strings(path, raw):
    if path.endswith(".json"):
        out = []
        def walk(x):
            if isinstance(x, str): out.append(x)
            elif isinstance(x, dict): [walk(k) or walk(v) for k, v in x.items()]
            elif isinstance(x, list): [walk(v) for v in x]
        walk(json.loads(raw))
        return "".join(out)
    return raw


def hits(text):
    found = {}
    for c in text:
        if ord(c) in SUSPECT:
            k = f"U+{ord(c):04X} {unicodedata.name(c, '?')}"
            found[k] = found.get(k, 0) + 1
    return found


def main(paths):
    if not paths:
        print("usage: unicode_scan.py FILE [FILE ...]"); return 2
    any_hit = False
    for i, p in enumerate(paths):
        data = open(p, "rb").read()
        text = strings(p, data.decode("utf-8"))
        h = hits(text)
        any_hit |= bool(h)
        print(f"{p} sha256 {hashlib.sha256(data).hexdigest()} scanned chars {len(text)} "
              f"bidi/zero-width: {h if h else 'none'}")
        if i == 0:
            sab = hits(text[: len(text) // 2] + "‮" + text[len(text) // 2 :])
            ok = sab.get("U+202E RIGHT-TO-LEFT OVERRIDE", 0) == h.get("U+202E RIGHT-TO-LEFT OVERRIDE", 0) + 1
            print(f"sabotage control (U+202E injected into {p}): {'DETECTED' if ok else 'MISSED'}")
            if not ok:
                print("VERDICT VACUOUS"); return 2
    print(f"VERDICT {'FOUND' if any_hit else 'NONE FOUND'} in {len(paths)} files")
    return 1 if any_hit else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
