#!/usr/bin/env python3
"""Fact-swap pilot (PR #194): the adapter from invented key-value records to Tiny Engine's native recall tokens.

Interface only. This script runs NO model and makes no prediction. It shows exactly what the pinned checkpoint would
receive for one invented fact swap and one distractor-only change, and flags the cases the native format cannot
express as trained (missing key, contradictory key).

Pinned checkpoint (the released version 3, TINY-ENGINE-003 arm B, config CFG3):
  Hugging Face holland202/tiny-engine-165k, revision 60a72cf319a236047c4c1d0a2581bd981f13861e
  engine.py sha256 13c653b80411c5427e861370fe449ca5536a08774595063639393a3366445f50
  weights/engine3_seed11..16.safetensors, sha256 in that revision's SHA256SUMS_v3 (seed 11: fd0f2f7c...a5c482)
Inference entry point (not called here):
  m = engine.TinyEngine(engine.CFG3); m.load_state_dict(safetensors.torch.load_file(path)); m.eval()
  answer_token = int(m(torch.tensor([tokens]))[0, -1].argmax())

Native recall grammar (engine.task_recall): BOS k1 v1 ... kn vn, then QRY k, and the model predicts v at the
position of k. Keys are tokens 1..63, values 64..127 (disjoint halves), BOS 0, SEP 128, QRY 129. In training, keys
in one context are distinct (drawn without replacement) and values may repeat.

The adapter never sees the expected answer. Its symbol table is built from every key and value string in the whole
sample, sorted, before any query is read, so one mapping holds across both members of a pair. Records are serialized
in their supplied order. Nothing is filtered, reordered or selected by the query.

Author: Claude (Anthropic, Opus 5.5). SELF-TESTED only. ChatGPT (OpenAI, Codex) audits it for answer leakage.
Usage:  python -I experiments/tiny_engine/fact_swap_adapter.py
"""
import sys

BOS, SEP, QRY = 0, 128, 129
KEY_TOKENS = range(1, 64)       # 63 key symbols
VAL_TOKENS = range(64, 128)     # 64 value symbols
TRAIN_LENS = (32, 64, 96, 128)


def trained_pairs(T):
    """Pairs per context in engine.task_recall at length T (same formula, restated so no torch import is needed)."""
    n = min(63, max(2, (T - 1) * 2 // 5 // 2 * 2 // 2))
    while (T - 1 - 2 * n) // 3 < 1:
        n -= 1
    return n


def build_table(sample):
    """sample: list of (records, query) over the whole pilot. Returns (key->token, value->token). No answers read."""
    keys = sorted({k for recs, q in sample for k, _ in recs} | {q for _, q in sample})
    vals = sorted({v for recs, _ in sample for _, v in recs})
    both = set(keys) & set(vals)
    if both:
        raise ValueError(f"strings used as both key and value: {sorted(both)} (native format needs disjoint halves)")
    if len(keys) > len(KEY_TOKENS) or len(vals) > len(VAL_TOKENS):
        raise ValueError(f"too many symbols: {len(keys)} keys (max 63), {len(vals)} values (max 64)")
    return dict(zip(keys, KEY_TOKENS)), dict(zip(vals, VAL_TOKENS))


def serialize(records, query, table):
    """(records, query) -> (tokens, status). Signature takes no expected answer; status flags untrained shapes."""
    kt, vt = table
    tokens = [BOS]
    for k, v in records:
        tokens += [kt[k], vt[v]]
    tokens += [QRY, kt[query]]
    rec_keys = [k for k, _ in records]
    status = []
    if len(set(rec_keys)) < len(rec_keys):
        status.append("CONTRADICTION_OR_DUPLICATE_KEY (never in training: keys were distinct)")
    if query not in rec_keys:
        status.append("MISSING_KEY (never in training; no abstain symbol, the model must emit some token)")
    n = len(records)
    if n > max(trained_pairs(T) for T in TRAIN_LENS):
        status.append(f"{n} pairs > {trained_pairs(128)} (most pairs seen at trained lengths)")
    return tokens, status or ["NATIVE"]


def exact_lookup(records, query):
    """Reference arm on the strings: every value recorded for the query key, in order."""
    hits = [v for k, v in records if k == query]
    return repr(hits[0]) if len(hits) == 1 else ("MISSING" if not hits else f"CONFLICT {hits}")


def decode(token, table):
    inv = {t: s for s, t in table[1].items()}
    return inv.get(token, f"<non-value token {token}>")


def show(label, records, query, table):
    toks, status = serialize(records, query, table)
    print(f"{label}: query {query!r}; records {records}")
    print(f"  tokens ({len(toks)}): {toks}")
    print(f"  status: {'; '.join(status)}")
    return toks


def main():
    base = [("locker B2", "lantern"), ("locker K7", "compass"), ("locker M4", "ribbon"), ("locker K9", "marble")]
    swap = [("locker B2", "lantern"), ("locker K7", "whistle"), ("locker M4", "ribbon"), ("locker K9", "marble")]
    dist = [("locker B2", "whistle"), ("locker K7", "compass"), ("locker M4", "ribbon"), ("locker K9", "marble")]
    q = "locker K7"
    missing_q = "locker Z1"
    contra = [("locker K7", "compass"), ("locker B2", "lantern"), ("locker K7", "whistle")]
    sample = [(base, q), (swap, q), (dist, q), (base, missing_q), (contra, q)]
    table = build_table(sample)  # built once, from strings only

    print("symbol table (sorted strings, built before any query is read):")
    print("  keys:  ", table[0])
    print("  values:", table[1])
    print("trained context sizes (pairs per context): "
          + ", ".join(f"T={T}: {trained_pairs(T)}" for T in TRAIN_LENS))
    print()
    a = show("A  base           ", base, q, table)
    b = show("A' fact swap      ", swap, q, table)
    d = show("D  distractor-only", dist, q, table)
    show("M  missing key    ", base, missing_q, table)
    show("C  contradiction  ", contra, q, table)
    print()
    # Structural leakage checks (SELF-TESTED): each edit changes exactly one token, at the edited record's value slot.
    diff_ab = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    diff_ad = [i for i, (x, y) in enumerate(zip(a, d)) if x != y]
    print(f"A vs A' differ only at token index {diff_ab} (record 2's value slot is index 4)")
    print(f"A vs D  differ only at token index {diff_ad} (record 1's value slot is index 2)")
    print(f"query token identical in A, A', D: {a[-2:] == b[-2:] == d[-2:]}; every record present: "
          f"{len(a) == 2 * len(base) + 3}")
    print("exact key lookup on the records (reference arm, not the model): "
          + ", ".join(f"{lab} {exact_lookup(r, qq)}" for lab, r, qq in
                      (("A", base, q), ("A'", swap, q), ("D", dist, q), ("M", base, missing_q), ("C", contra, q)))
          + "  (M and C need an agreed rule before scoring)")
    ok = diff_ab == [4] and diff_ad == [2] and a[-2:] == b[-2:] == d[-2:]
    print("INTERFACE CHECK", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
