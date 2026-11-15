"""CST-001 source-tracing development probe. ChatGPT (OpenAI), 2026-11-15.

Reuses the public CST-001 generator and explicit instruction. The archive
reader checks the earlier record without running its model. All new
inference runs on a local, temporary llama.cpp CPU server.
"""

import argparse
from collections import Counter
import hashlib
import http.client
import itertools
import json
from pathlib import Path
import random
import re
import socket
import subprocess
import sys
import time

import cases
import exposures


ARMS = "EOLG"
MODELS = {
    "qwen15": "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
    "qwen3": "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
}
SOURCE_ID = re.compile(r"\b[A-Z]{2,}-[0-9]{3}\b")
CHOOSE = re.compile(r"\**\s*DECISION\s*:\s*\**\s*(CONFIRMED|INSUFFICIENT)\s*\**\s*\.?", re.I)
RELATION = re.compile(r"\**\s*SOURCE RELATION\s*:\s*\**\s*(SAME|DIFFERENT)\s*\**\s*\.?", re.I)
PATTERNS = {
    ("INSUFFICIENT", "CONFIRMED"): "correct",
    ("CONFIRMED", "INSUFFICIENT"): "reversed",
    ("CONFIRMED", "CONFIRMED"): "both_confirmed",
    ("INSUFFICIENT", "INSUFFICIENT"): "both_insufficient",
}
SYSTEM = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def root_ids(prompt, hop):
    """Follow the single intermediate-document link when the case has one."""
    reports = [line for line in prompt.splitlines() if re.match(r"^Report [12]: ", line)]
    notes = [line for line in prompt.splitlines() if line.startswith("A note attached to the ")]
    if len(reports) != 2 or len(notes) != hop - 1:
        raise ValueError("source graph has the wrong number of reports or notes")

    roots = []
    for report in reports:
        source = report.split("Its source line reads: ", 1)[1]
        found = SOURCE_ID.findall(source)
        if not found:
            document = re.fullmatch(r"taken from the (.+)\.", source)
            if not document or not notes or not notes[0].startswith(f"A note attached to the {document[1]},"):
                raise ValueError("intermediate document link is missing")
            found = SOURCE_ID.findall(notes[0])
        if len(found) != 1:
            raise ValueError("source must resolve to one observation ID")
        roots.append(found[0])
    return roots


def outcome(arm, content):
    pattern = RELATION if arm == "L" else CHOOSE
    labels = [m[1].upper() for line in content.splitlines() if (m := pattern.fullmatch(line.strip()))]
    if len(labels) != 1:
        return "MALFORMED"
    if arm == "L":
        return {"SAME": "INSUFFICIENT", "DIFFERENT": "CONFIRMED"}[labels[0]]
    return labels[0]


def build():
    rng = random.Random(7415)
    previous = {v["prompt"] for p in cases.build("dev", 2) for v in p["versions"]}
    pairs = []
    prompts = {}
    for domain_index, domain in enumerate(cases.DOMAINS):
        for hop in (1, 2):
            order = "AB" if (domain_index + hop) % 2 else "BA"
            pair = cases.make_pair(rng, domain, hop, order, 0)
            pair["pair"] = "probe-" + pair["pair"]
            for variant in pair["versions"]:
                prompt = variant["prompt"]
                if prompt in previous or not prompt.endswith(cases.ASK):
                    raise ValueError("probe prompt is not fresh or has the wrong question")
                sources = root_ids(prompt, hop)
                answer = "INSUFFICIENT" if len(set(sources)) == 1 else "CONFIRMED"
                if variant["answer"] != answer:
                    raise ValueError("source graph disagrees with the case generator")
                variants = {
                    "E": prompt,
                    "O": prompt.removesuffix(cases.ASK) + cases.ASK.replace(
                        '"DECISION: CONFIRMED" or "DECISION: INSUFFICIENT"',
                        '"DECISION: INSUFFICIENT" or "DECISION: CONFIRMED"',
                    ),
                    "L": prompt.removesuffix(cases.ASK) + (
                        "Trace both reports to their original observations. Compare their exact source IDs. "
                        'End with "SOURCE RELATION: SAME" or "SOURCE RELATION: DIFFERENT".'
                    ),
                    "G": prompt.removesuffix(cases.ASK) + (
                        f"Original observation IDs after following the links:\nReport 1: {sources[0]}\n"
                        f"Report 2: {sources[1]}\n\n" + cases.ASK
                    ),
                }
                if len(set(variants.values())) != len(ARMS):
                    raise ValueError("two prompt versions coincide")
                for arm, text in variants.items():
                    key = (arm, pair["pair"], variant["version"])
                    user = exposures.test_message("E", text)
                    prompts[key] = (
                        f"<|im_start|>system\n{SYSTEM}<|im_end|>\n"
                        f"<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"
                    )
            pairs.append(pair)
    if len(set(prompts.values())) != len(prompts):
        raise ValueError("duplicate rendered prompt")
    return pairs, prompts


def load_jsonl(path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def summarize(pairs, arms, outputs):
    result = {}
    for arm in arms:
        counts = Counter({**dict.fromkeys(PATTERNS.values(), 0), "malformed": 0})
        hops = {hop: Counter(correct=0, reversed=0) for hop in (1, 2)}
        for pair in pairs:
            seen = tuple(outputs[(arm, pair["pair"], name)] for name in ("SHARED", "INDEPENDENT"))
            pattern = PATTERNS.get(seen, "malformed")
            counts[pattern] += 1
            if pattern in ("correct", "reversed"):
                hops[pair["hop"]][pattern] += 1
        result[arm] = dict(total=dict(counts), hops={k: dict(v) for k, v in hops.items()})
    return result


def archive(path):
    pairs = cases.build("dev", 2)
    expected = {(arm, p["pair"], v["version"]) for arm, p in itertools.product("ABCDE", pairs) for v in p["versions"]}
    for pair in pairs:
        for variant in pair["versions"]:
            a, b = root_ids(variant["prompt"], pair["hop"])
            expected_label = "INSUFFICIENT" if a == b else "CONFIRMED"
            if variant["answer"] != expected_label:
                raise ValueError(f"archive answer key conflicts with source IDs: {pair['pair']}")
    outputs = {}
    for row in load_jsonl(path):
        key = (row["arm"], row["pair"], row["version"])
        if key in outputs or key not in expected:
            raise ValueError(f"unexpected or duplicate archive trial: {key}")
        outputs[key] = outcome(key[0], row["output"])
    if set(outputs) != expected:
        raise ValueError("archive is missing trials")
    with path.open("rb") as stream:
        print("ARCHIVE SHA256", hashlib.file_digest(stream, "sha256").hexdigest())
    print("ARCHIVE DEV SEAL", cases.seal(pairs))
    return summarize(pairs, "ABCDE", outputs)


def prompt_digest(prompt):
    return hashlib.sha256(prompt.encode()).hexdigest()


def repeat_keys(pairs):
    return {("E", pairs[0]["pair"], version) for version in ("SHARED", "INDEPENDENT")}


def analyze(pairs, prompts, rows, model):
    originals = {}
    repeats = {}
    for row in rows:
        key = (row["arm"], row["pair"], row["version"])
        rep = row["repeat"]
        if (key not in prompts or row["model"] != model
                or row["prompt_sha256"] != prompt_digest(prompts[key])):
            raise ValueError(f"trial identity mismatch: {key}")
        if type(rep) is not int or rep not in (0, 1, 2) or (rep and key not in repeat_keys(pairs)):
            raise ValueError(f"unexpected repeat: {key} / {rep}")
        if not isinstance(row["output"], str):
            raise ValueError(f"trial output is not text: {key}")
        dest, idx = (repeats, (key, rep)) if rep else (originals, key)
        if idx in dest:
            raise ValueError(f"duplicate trial: {idx}")
        dest[idx] = row["output"]
    if set(originals) != set(prompts) or len(repeats) != 4:
        raise ValueError("incomplete trial set")
    if any(text != originals[key] for (key, _), text in repeats.items()):
        raise ValueError("exact-input repeats produced different text")
    decided = {key: outcome(key[0], content) for key, content in originals.items()}
    return summarize(pairs, ARMS, decided)


def report(result):
    for arm, counts in result.items():
        print(arm, json.dumps(counts, sort_keys=True))
    print("DIGEST", identity(result))


def feasible(pairs, prompts):
    print("PROBE CASE SEAL", cases.seal(pairs))
    print("PROMPT SEAL", identity(sorted((key, prompt_digest(prompt)) for key, prompt in prompts.items())))
    print("PAIRS", len(pairs), "DOMAINS", len({p["domain"] for p in pairs}))
    print("HOP / ORDER", sorted(Counter((p["hop"], p["order"]) for p in pairs).items()))
    print("VERSION", sorted(Counter(v["version"] for p in pairs for v in p["versions"]).items()))
    print("PROMPTS", len(prompts), "EXTRA REPEATS", len(repeat_keys(pairs)) * 2)


def record(model, key, prompt, output, repeat, **details):
    arm, pair, version = key
    return {"model": model, "arm": arm, "pair": pair, "version": version, "repeat": repeat,
            "prompt_sha256": prompt_digest(prompt), "output": output, **details}


def fail_expected(fn, phrase):
    try:
        fn()
    except ValueError as exc:
        if phrase in str(exc):
            return
        raise
    raise ValueError(f"expected failure: {phrase}")


def selftest(pairs, prompts, sabotage):
    rows = []
    for key, prompt in prompts.items():
        arm, _, version = key
        independent = version == "INDEPENDENT"
        if sabotage and arm == "G":
            independent = not independent
        if arm == "L":
            line = "SOURCE RELATION: DIFFERENT" if independent else "SOURCE RELATION: SAME"
        else:
            line = "DECISION: CONFIRMED" if independent else "DECISION: INSUFFICIENT"
        rows.append(record("fixture", key, prompt, line, 0))
        if key in repeat_keys(pairs):
            for repeat in (1, 2):
                rows.append(record("fixture", key, prompt, line, repeat))
    result = analyze(pairs, prompts, rows, "fixture")
    fail_expected(lambda: analyze(pairs, prompts, rows[:-1], "fixture"), "incomplete")
    fail_expected(lambda: analyze(pairs, prompts, rows + [rows[0]], "fixture"), "duplicate")
    assert outcome("E", "DECISION: CONFIRMED\nDECISION: INSUFFICIENT") == "MALFORMED"
    constant = {key: "CONFIRMED" for key in prompts}
    assert all(r["total"]["correct"] == 0 for r in summarize(pairs, ARMS, constant).values())
    for arm, r in result.items():
        if r["total"]["correct"] != len(pairs):
            print(f"FAILED: {arm} fixture decisions do not match the source graph")
            return 1
    print("CONTROL PASS: correct, constant, contradictory, incomplete and duplicate fixtures")
    return 0


def request(port, path, data=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=45)
    try:
        if data is None:
            connection.request("GET", path)
        else:
            connection.request("POST", path, json.dumps(data), {"Content-Type": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            raise RuntimeError(f"{path} returned HTTP {response.status}")
        return json.load(response)
    finally:
        connection.close()


def run(args, pairs, prompts):
    with args.gguf.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != MODELS[args.model]:
            raise ValueError("model hash does not match pinned file")
    version = subprocess.run([str(args.server), "--version"], capture_output=True, text=True, check=True)
    if "build 12244, commit d5bbcd1f3" not in version.stdout + version.stderr:
        raise ValueError("unexpected llama.cpp build")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    command = [
        str(args.server), "--offline", "--host", "127.0.0.1", "--port", str(port),
        "--model", str(args.gguf), "--alias", args.model, "--ctx-size", "1536", "--parallel", "1",
        "--threads", "4", "--threads-batch", "4", "--gpu-layers", "0", "--no-context-shift",
        "--no-cache-prompt", "--no-webui", "--no-slots",
    ]

    jobs = list(prompts)
    random.Random(74151).shuffle(jobs)
    schedule = [(key, 0) for key in jobs] + [
        (key, rep) for rep in (1, 2) for key in sorted(repeat_keys(pairs))
    ]
    with args.log.open("xb") as log, args.out.open("x", encoding="utf-8", buffering=1) as out:
        server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(150):
                if server.poll() is not None:
                    raise RuntimeError(f"model server exited; see {args.log}")
                try:
                    if request(port, "/health").get("status") == "ok":
                        break
                except (OSError, RuntimeError):
                    time.sleep(0.2)
            else:
                raise RuntimeError("model server did not become ready")
            names = {row["id"] for row in request(port, "/v1/models")["data"]}
            if names != {args.model}:
                raise RuntimeError(f"model server reports unexpected identity: {names}")
            for i, (key, repeat) in enumerate(schedule, 1):
                prompt = prompts[key]
                response = request(port, "/completion", {
                    "prompt": prompt, "temperature": 0, "seed": 0, "n_predict": 64,
                    "cache_prompt": False, "return_tokens": True,
                })
                if response.get("truncated") or not isinstance(response.get("content"), str):
                    raise ValueError(f"truncated prompt or invalid response: {key}")
                row = record(args.model, key, prompt, response["content"], repeat,
                             stop_type=response.get("stop_type"), tokens=response.get("tokens"),
                             tokens_evaluated=response.get("tokens_evaluated"))
                out.write(json.dumps(row, sort_keys=True) + "\n")
                if i % 32 == 0 or i == len(schedule):
                    print(f"{args.model}: {i}/{len(schedule)} requests written", flush=True)
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
    analyze(pairs, prompts, load_jsonl(args.out), args.model)
    print("SAME-INPUT REPEATS: 4/4 matched")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("feasible")
    check = sub.add_parser("selftest")
    check.add_argument("--sabotage", action="store_true")
    old = sub.add_parser("archive")
    old.add_argument("input", type=Path)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--server", type=lambda p: Path(p).resolve(), required=True)
    run_parser.add_argument("--gguf", type=Path, required=True)
    run_parser.add_argument("--out", type=Path, required=True)
    run_parser.add_argument("--log", type=Path, required=True)
    score_parser = sub.add_parser("score")
    score_parser.add_argument("input", type=Path)
    for command in (run_parser, score_parser):
        command.add_argument("--model", choices=MODELS, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "archive":
            report(archive(args.input))
            return 0
        pairs, prompts = build()
        if args.command == "feasible":
            feasible(pairs, prompts)
        elif args.command == "selftest":
            return selftest(pairs, prompts, args.sabotage)
        elif args.command == "run":
            run(args, pairs, prompts)
        elif args.command == "score":
            result = analyze(pairs, prompts, load_jsonl(args.input), args.model)
            print("SAME-INPUT REPEATS: 4/4 matched")
            report(result)
    except (OSError, RuntimeError, ValueError, KeyError, IndexError, subprocess.SubprocessError) as exc:
        print(f"UNVERIFIED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
