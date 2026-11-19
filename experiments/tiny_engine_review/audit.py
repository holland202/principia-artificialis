"""Source-informed software audit by Codex/OpenAI, 2026-11-17. No model inference.

Exact model identifier unavailable; human direction only: Chad Holland.
Imports the original NumPy task generator via AST dependency isolation, and runs
the original score.py as a subprocess. This does not emulate a trained model.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def run_score(directory):
    process = subprocess.run(
        [sys.executable, str(ROOT / 'experiments/tiny_engine/score.py'), str(directory)],
        text=True, capture_output=True, check=False,
    )
    return {'exit': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr}


def original_copy():
    path = ROOT / 'experiments/tiny_engine/engine.py'
    source = ast.parse(path.read_text())
    selected = []
    for node in source.body:
        if isinstance(node, ast.Assign):
            names = {n.id for target in node.targets for n in ast.walk(target) if isinstance(n, ast.Name)}
            if names & {'N_CONTENT', 'BOS', 'SEP', 'QRY'}:
                selected.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == 'task_copy':
            selected.append(node)
    namespace = {'np': np}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['task_copy']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sabotage', action='store_true')
    args = parser.parse_args()
    original = run_score(ROOT / 'results/tiny_engine')
    with tempfile.TemporaryDirectory() as scratch:
        base = Path(scratch)
        duplicate = base / 'duplicate'
        duplicate.mkdir()
        seed_one = (ROOT / 'results/tiny_engine/seed1.json').read_bytes()
        for index in range(1, 6):
            (duplicate / f'seed{index}.json').write_bytes(seed_one)
        duplicated = run_score(duplicate)
        empty = base / 'empty'
        empty.mkdir()
        absent = run_score(empty)
    task_copy = original_copy()
    counts = []
    samples = {}
    for length in (128, 256, 512):
        tokens, mask = task_copy(np.random.default_rng(17), length)
        count = int(mask.sum())
        counts.append({'T': length, 'copy_tokens': count,
                       'padding_tokens': length - (2 * count + 2),
                       'unique_source_tokens': len(set(tokens[1:count + 1].tolist()))})
        samples[length] = tokens
    equal_prefix = bool(np.array_equal(samples[256], samples[512][:256]))
    source_hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in (
        'experiments/tiny_engine/engine.py', 'experiments/tiny_engine/score.py',
        'results/tiny_engine/seed1.json', 'results/tiny_engine/score.txt')}
    payload = {'original': original, 'duplicate_seed_1': duplicated, 'empty': absent,
               'generator_counts': counts, 'L256_prefix_equals_L512_prefix': equal_prefix,
               'source_sha256': source_hashes,
               'scope': 'PUBLIC SOFTWARE QUALIFICATION; NO MODEL INFERENCE; AST-ISOLATED ORIGINAL GENERATOR'}
    p1_q2 = 'Q2: HELD' if args.sabotage else 'Q2: FAILED'
    outcomes = {
        'P1_archived_report': original['exit'] == 0 and not original['stderr']
            and all(term in original['stdout'] for term in ('Q1: HELD', p1_q2, 'Q3: HELD')),
        'P2_duplicate_seed_accepted': duplicated['exit'] == 0 and not duplicated['stderr']
            and 'Q2: HELD (5/5 seeds' in duplicated['stdout'],
        'P3_absent_report_exit_zero': absent['exit'] == 0 and not absent['stderr']
            and all(f'{q}: FAILED (0/0 seeds' in absent['stdout'] for q in ('Q1', 'Q2', 'Q3')),
        'P4_copy_length_cap': [r['copy_tokens'] for r in counts] == [63, 127, 127]
            and counts[-1]['padding_tokens'] == 256 and equal_prefix,
    }
    payload['outcomes'] = outcomes
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    print(json.dumps(payload, sort_keys=True, indent=2))
    for name, held in outcomes.items():
        print(name, 'HELD' if held else 'REFUTED')
    print(f'VERDICT {sum(outcomes.values())} of {len(outcomes)} as registered')
    print('DIGEST', digest)
    print('These expectations include failures of the historical scorer; they are not AI performance findings.')
    pin = Path(__file__).with_name('recorded.json')
    if pin.exists() and json.loads(pin.read_text()) != {'outcomes': outcomes, 'digest': digest}:
        return 1
    return 0 if all(outcomes.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
