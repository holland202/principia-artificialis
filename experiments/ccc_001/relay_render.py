"""CCC-001 relay renderer. Registration: RELAY_RENDER_PREREG.md (8831888), frozen at 584919c.

Turns a frozen-extractor snapshot (relay_prefix_<k>.json) into the prompt a measured model would read, through
transformers' `apply_chat_template`. The OPEN/CLOSE/ACK bytes, labels, escaping and fixture are imported from
render_feasibility.py at 8831888 (frozen), not copied. No model is loaded here.

Status: archival tooling. Rendering a relay prefix for an arm-A reading still needs Chad Holland's approval.

usage:
  python relay_render.py test TOKDIR [--sabotage]                 # registered predictions R1-R4 (+ disclosed extras)
  python relay_render.py render TOKDIR SNAPSHOT --order original|shuffle --probe-file F --out PROMPT.txt

render exit: 0 written; 4 OVER_LIMIT (nothing written); 3 defect (nothing written).
test exit: 0 if every check holds; 1 otherwise.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relay_extract as rx  # noqa: E402  (frozen shuffle construction)
import render_feasibility as rf  # noqa: E402  (frozen OPEN, CLOSE, ACK, LABEL, FIXTURE, PROBE, esc)

IM_START, IM_END = 151644, 151645
EXPECT = {  # RELAY_RENDER_PREREG.md, "Fixture (derived expected values)"
    "content_sha256": "9168a828569434e6fa34e36959c278ba612f6a0a3b914b1119192365438228c8",
    "prompt_sha256": "7c20d4c7e78aa915cbea764b2d4eb9cce8e3d1bcf4c39c06529613db963784b9",
    "tokens": 194,
    "ids_sha256": "2c0e2716385c2aa623e74a48eb1e7a97f379ce464e607f760922cfa2ce5d7f9b",
}
OPEN_TAG = re.compile(r'<turn speaker="(P1|P2)">\n')


class Defect(Exception):
    pass


class OverLimit(Exception):
    pass


def sha(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode("utf-8")).hexdigest()


def ids_sha(ids):
    return sha(json.dumps(ids, separators=(",", ":")))


def unesc(s):
    return s.replace("&lt;", "<").replace("&amp;", "&")


def content(turns, escape=True):
    """Frozen step 4. turns: [(speaker, text)]. escape=False is the --sabotage path only."""
    if escape:
        return rf.content(turns)
    return rf.OPEN + "".join(f'<turn speaker="{rf.LABEL[a]}">\n{t}\n</turn>\n' for a, t in turns) + rf.CLOSE


def messages(turns, probe, escape=True):
    """Frozen steps 4-7: transcript (user), fixed ACK (assistant), probe (user); no system message."""
    return [{"role": "user", "content": content(turns, escape)}, {"role": "assistant", "content": rf.ACK},
            {"role": "user", "content": probe}]


def parse(c):
    """Inverse of step 4. A turn ends at the FIRST `</turn>` after its opening tag (the reading escaping protects).
    Returns [(label, unescaped text)]; raises Defect on any framing error."""
    if not (c.startswith(rf.OPEN) and c.endswith(rf.CLOSE)):
        raise Defect("OPEN/CLOSE framing")
    s, out, i = c[len(rf.OPEN):len(c) - len(rf.CLOSE)], [], 0
    while i < len(s):
        m = OPEN_TAG.match(s, i)
        if not m:
            raise Defect(f"no opening tag at offset {i}")
        j = s.find("</turn>", m.end())
        if j < 0 or s[j - 1] != "\n" or s[j + 7:j + 8] != "\n":
            raise Defect(f"turn {len(out) + 1}: closing tag not on its own line")
        out.append((m.group(1), unesc(s[m.end():j - 1])))
        i = j + 8
    return out


class Renderer:
    def __init__(self, tokdir):
        from transformers import AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(tokdir)
        self.L = json.load(open(os.path.join(tokdir, "config.json")))["max_position_embeddings"]
        self.files = {f: sha(open(os.path.join(tokdir, f), "rb").read())
                      for f in ("tokenizer.json", "tokenizer_config.json", "config.json")}

    def text(self, msgs, gen):
        return self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=gen)

    def ids(self, s):
        return self.tok(s, add_special_tokens=False).input_ids

    def prompt(self, turns, probe, escape=True):
        """Frozen step 10: full prompt or OverLimit. Returns (text, ids, msgs)."""
        msgs = messages(turns, probe, escape)
        p = self.text(msgs, True)
        ids = self.ids(p)
        if len(ids) >= self.L:
            raise OverLimit(f"OVER_LIMIT: {len(ids)} tokens >= L {self.L}")
        return p, ids, msgs


def snapshot_turns(snap, order):
    """Frozen step 1: rendered texts in NNN order, or in the frozen shuffle order."""
    t = sorted(snap["turns"], key=lambda x: x["nnn"])
    k = len(t)
    if [x["nnn"] for x in t] != list(range(1, k + 1)) or snap.get("checkpoint", k) != k:
        raise Defect("snapshot turns are not 1..k")
    if any(x["speaker"] != ("claude" if x["nnn"] % 2 else "chatgpt") for x in t):
        raise Defect("speaker parity")
    by = {x["nnn"]: x for x in t}
    perm = list(range(1, k + 1)) if order == "original" else rx.shuffle_perm(k)
    return [(by[n]["speaker"], by[n]["rendered"]) for n in perm], perm


def cmd_render(a):
    r = Renderer(a.tokdir)
    try:
        snap = json.load(open(a.snapshot, encoding="utf-8"))
        turns, perm = snapshot_turns(snap, a.order)
        probe = open(a.probe_file, encoding="utf-8").read()
        p, ids, _ = r.prompt(turns, probe)
    except OverLimit as e:
        print(e)
        return 4
    except Defect as e:
        print("DEFECT", e)
        return 3
    open(a.out, "w", encoding="utf-8").write(p)
    print(f"rendered {len(turns)} turns order {a.order} perm {perm} tokens {len(ids)} "
          f"prompt sha256 {sha(p)} ids sha256 {ids_sha(ids)} -> {a.out}")
    return 0


def check(name, ok, detail=""):
    print(f"{name}: {'HELD' if ok else 'REFUTED'}" + (f" | {detail}" if detail else ""))
    return ok


def cmd_test(a):
    import transformers
    r = Renderer(a.tokdir)
    esc = not a.sabotage
    print("transformers", transformers.__version__, "| L", r.L, "| sabotage (escaping off)" if a.sabotage else "")
    for f, h in r.files.items():
        print(f, "sha256", h)
    ok = True

    # R1: fixture through apply_chat_template
    c = content(rf.FIXTURE, esc)
    p, ids, msgs = r.prompt(rf.FIXTURE, rf.PROBE, esc)
    got = {"content_sha256": sha(c), "prompt_sha256": sha(p), "tokens": len(ids), "ids_sha256": ids_sha(ids)}
    for k, v in got.items():
        print(f"  R1 {k}: {v} (expected {EXPECT[k]})")
    ok &= check("R1 fixture values, 4 of 4", got == EXPECT, f"{sum(got[k] == EXPECT[k] for k in EXPECT)} of 4 match")

    # R2: round trip, plus where the chat-control tokens fall
    try:
        back = parse(c)
        r2 = back == [(rf.LABEL[s], t) for s, t in rf.FIXTURE]
        d = f"{len(back)} turns, labels {[b[0] for b in back]}, texts equal {[b[1] == t for b, (_, t) in zip(back, rf.FIXTURE)]}"
    except Defect as e:
        r2, d = False, f"DEFECT {e}"
    cids = r.ids(c)
    inside = cids.count(IM_START) + cids.count(IM_END)
    print(f"  R2 control tokens inside message-1 content: {inside} | im_start/im_end in full prompt "
          f"({ids.count(IM_START)}, {ids.count(IM_END)}), structure expects (5, 4)")
    ok &= check("R2 round trip", r2 and inside == 0 and (ids.count(IM_START), ids.count(IM_END)) == (5, 4), d)

    # R3: OVER_LIMIT at >= L via the CLI, and one turn shorter renders
    import longctx_feasibility as lf
    pool = lf.synthetic_turns(1200)
    lo, hi = 1, len(pool)
    assert len(r.ids(r.text(messages(pool, rf.PROBE), True))) >= r.L, "synthetic pool too short for R3"
    while lo < hi:  # smallest m with n(pool[:m]) >= L
        mid = (lo + hi) // 2
        if len(r.ids(r.text(messages(pool[:mid], rf.PROBE), True))) >= r.L:
            hi = mid
        else:
            lo = mid + 1
    m = lo
    n_over = len(r.ids(r.text(messages(pool[:m], rf.PROBE), True)))
    n_under = len(r.ids(r.text(messages(pool[:m - 1], rf.PROBE), True)))
    with tempfile.TemporaryDirectory(dir=os.path.expanduser("~")) as td:
        pf = os.path.join(td, "probe.txt")
        open(pf, "w").write(rf.PROBE)
        res = {}
        for tag, mm in (("over", m), ("under", m - 1)):
            sp = os.path.join(td, f"snap_{tag}.json")
            json.dump({"checkpoint": mm, "turns": [{"nnn": i + 1, "speaker": s, "rendered": t}
                                                   for i, (s, t) in enumerate(pool[:mm])]}, open(sp, "w"))
            out = os.path.join(td, f"prompt_{tag}.txt")
            cp = subprocess.run([sys.executable, os.path.abspath(__file__), "render", a.tokdir, sp, "--order",
                                 "original", "--probe-file", pf, "--out", out], capture_output=True, text=True)
            res[tag] = (cp.returncode, os.path.exists(out), cp.stdout.strip().split("\n")[-1][:90])
            print(f"  R3 {tag}: {mm} synthetic turns, exit {res[tag][0]}, prompt file written {res[tag][1]} | {res[tag][2]}")
    print(f"  R3 token counts: {m} turns {n_over} (>= L {r.L}); {m - 1} turns {n_under}")
    ok &= check("R3 OVER_LIMIT", res["over"][:2] == (4, False) and res["under"][:2] == (0, True)
                and n_over >= r.L > n_under)

    # R4: context without generation prompt is an exact token prefix of the full prompt (fixture and its shuffle)
    perm3 = rx.shuffle_perm(3)
    fx_shuf = [rf.FIXTURE[n - 1] for n in perm3]
    r4 = []
    for tag, turns in (("fixture", rf.FIXTURE), ("fixture shuffle", fx_shuf)):
        msgs = messages(turns, rf.PROBE, esc)
        pre, full = r.ids(r.text(msgs[:2], False)), r.ids(r.text(msgs, True))
        r4.append(full[:len(pre)] == pre)
        print(f"  R4 {tag}: context {len(pre)} tokens, full {len(full)}, prefix {r4[-1]}")
    print(f"  R4 note: shuffle_perm(3) = {perm3}; the frozen permutation for k=3 is the identity, so this case does not discriminate")
    ok &= check("R4 cache prefix", all(r4))

    # Disclosed extras (not registered): two-path agreement and R4 on a real-length shuffle
    snapf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "results", "ccc_001", "relay_prefix_016.json")
    if os.path.exists(snapf) and not a.sabotage:
        import jinja2
        from tokenizers import Tokenizer
        tdir = a.tokdir
        tk = Tokenizer.from_file(os.path.join(tdir, "tokenizer.json"))
        ct = jinja2.Environment(trim_blocks=True, lstrip_blocks=True).from_string(
            json.load(open(os.path.join(tdir, "tokenizer_config.json")))["chat_template"])
        snap = json.load(open(snapf, encoding="utf-8"))
        x = True
        for order in ("original", "shuffle"):
            turns, perm = snapshot_turns(snap, order)
            msgs = messages(turns, rf.PROBE)
            a_ids = r.ids(r.text(msgs, True))
            b_ids = tk.encode(ct.render(messages=msgs, add_generation_prompt=True, tools=None),
                              add_special_tokens=False).ids
            pre = r.ids(r.text(msgs[:2], False))
            first = next((i for i, (u, v) in enumerate(zip(a_ids, b_ids)) if u != v), None)
            print(f"  X 016 {order}: transformers {len(a_ids)} tokens ids {ids_sha(a_ids)[:16]} | jinja2 {len(b_ids)} "
                  f"ids {ids_sha(b_ids)[:16]} | equal {a_ids == b_ids} first diff {first} | R4 prefix {a_ids[:len(pre)] == pre}"
                  f" | control tokens in content {sum(r.ids(msgs[0]['content']).count(t) for t in (IM_START, IM_END))}")
            x &= a_ids == b_ids and a_ids[:len(pre)] == pre
        ok &= check("X two paths agree on 016 (original, shuffle) and R4 holds there (added, not registered)", x)
    print("ALL HELD" if ok else "NOT ALL HELD")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("test")
    t.add_argument("tokdir")
    t.add_argument("--sabotage", action="store_true")
    rr = sub.add_parser("render")
    rr.add_argument("tokdir")
    rr.add_argument("snapshot")
    rr.add_argument("--order", choices=("original", "shuffle"), required=True)
    rr.add_argument("--probe-file", required=True)
    rr.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    return cmd_test(a) if a.cmd == "test" else cmd_render(a)


if __name__ == "__main__":
    sys.exit(main())
