"""Fail-closed loading of per-seed results for the registered scorers (score.py, score2.py).

Added 2026-11-17 after Codex (OpenAI) showed, in draft PR #163, that the scorers counted files, not distinct seeds:
five copies of one seed's result passed as five seeds. Reproduced by Claude against score2.py before this fix
(five copies of seed 1 -> every criterion HELD 5/5; two of six results -> an ordinary FAILED, not an error).

A result set is scored only if: the files are exactly seed1.json..seedN.json for the registered seeds; each file's
"seed" field matches its file name; no two files hold the same seed or identical scores; every file's config equals
the registered config; every registered score key is present and is a number in [0, 1]. Anything else exits 2
with the reason, and no verdict is printed.
Written by Claude (Anthropic, Opus 5.5). SELF-TESTED only."""
import json
import math
import sys
from pathlib import Path

REGISTERED_SEEDS = (1, 2, 3, 4, 5, 6)


class InvalidResults(Exception):
    pass


def load(directory, cfg, keys, seeds=REGISTERED_SEEDS):
    d = Path(directory)
    files = sorted(d.glob("seed*.json"))
    names = {p.name for p in files}
    want = {f"seed{s}.json" for s in seeds}
    if names != want:
        raise InvalidResults(f"expected exactly {sorted(want)}; found {sorted(names)}")
    out, seen_scores = [], set()
    for s in seeds:
        p = d / f"seed{s}.json"
        try:
            r = json.loads(p.read_text())
        except (OSError, ValueError) as e:
            raise InvalidResults(f"{p.name}: unreadable ({e})") from e
        if r.get("seed") != s:
            raise InvalidResults(f"{p.name}: seed field is {r.get('seed')!r}, expected {s}")
        if json.loads(json.dumps(cfg)) != r.get("cfg"):
            raise InvalidResults(f"{p.name}: config does not match the registered config")
        sc = r.get("scores")
        if not isinstance(sc, dict):
            raise InvalidResults(f"{p.name}: no scores")
        for k in keys:
            v = sc.get(k)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) or not 0 <= v <= 1:
                raise InvalidResults(f"{p.name}: score {k!r} missing or not a number in [0, 1] ({v!r})")
        fp = json.dumps(sc, sort_keys=True)
        if fp in seen_scores:
            raise InvalidResults(f"{p.name}: scores identical to another seed's (duplicated result?)")
        seen_scores.add(fp)
        out.append(r)
    return out


def load_or_exit(directory, cfg, keys):
    try:
        return load(directory, cfg, keys)
    except InvalidResults as e:
        print(f"INVALID RESULT SET, no verdict: {e}")
        sys.exit(2)
