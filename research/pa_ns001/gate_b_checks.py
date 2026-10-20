"""Bounded Gate B regression and audit of existing Stage 2 artifacts. No AI."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from evaluate_faults import evaluate
from fault_cases import canonical
from ns001 import verify

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def malformed_checker(mode):
    def check(*args, **kwargs):
        result = dict(verify(*args, **kwargs))
        if mode == 'flipped':
            result['accepted'] = not result['accepted']
        elif mode == 'missing':
            del result['accepted']
        elif mode == 'integer_one':
            result['accepted'] = 1
        elif mode == 'integer_zero':
            result['accepted'] = 0
        else:
            raise ValueError('unknown engineering control')
        return result
    return check


def status_only_evaluator(checker):
    """Sabotage: deliberately restore the pre-repair comparison."""
    fixtures, outcomes = evaluate(checker)
    for row in outcomes:
        row['matched'] = row['observed']['status'] == row['expected_status']
    return fixtures, outcomes


def audit_existing_calibration():
    path = HERE / 'evidence/stage2/calibration-data1/cases.jsonl'
    data = path.read_bytes()
    original_manifest = json.loads((HERE/'MANIFEST.json').read_text())
    name = path.relative_to(ROOT).as_posix()
    entries = [r for r in original_manifest['files'] if r['path'] == name]
    if len(entries) != 1 or hashlib.sha256(data).hexdigest() != entries[0]['sha256']:
        raise ValueError('historical calibration artifact identity mismatch')
    rows = [json.loads(line) for line in data.splitlines()]
    groups = {'sample_only': [], 'momentum_only': [], 'both': []}
    predicted_ids = []
    for row in rows:
        p = {k: Fraction.from_float(float(v)) for k, v in row['parameters'].items()}
        amplitude = p['U'] if row['family'] == 'couette' else p['G']*p['h']**2/(8*p['mu'])
        sample_error = Fraction.from_float(row['sample_error_bound'])/abs(amplitude)
        allowance = (Fraction.from_float(1e-9)
                     + 4*(sample_error+16*Fraction.from_float(sys.float_info.epsilon))*(row['n']-1)**2)
        sample_exceeded = sample_error > Fraction(1, 1_000_000)
        momentum_exceeded = allowance > Fraction(1, 100)
        if sample_exceeded or momentum_exceeded:
            group = 'both' if sample_exceeded and momentum_exceeded else ('sample_only' if sample_exceeded else 'momentum_only')
            groups[group].append(row['id'])
            predicted_ids.append(row['id'])
    observed_ids = [r['id'] for r in rows if r['current']['status'] == 'UNRESOLVABLE']
    counts = {k: len(v) for k, v in groups.items()}
    return {
        'artifact_sha256': hashlib.sha256(data).hexdigest(),
        'rows': len(rows), 'unique_ids': len({r['id'] for r in rows}),
        'recorded_status_counts': dict(Counter(r['current']['status'] for r in rows)),
        'group_counts': counts, 'groups': groups,
        'sample_cap_total': counts['sample_only']+counts['both'],
        'momentum_cap_total': counts['momentum_only']+counts['both'],
        'all_39_explained': sorted(predicted_ids) == sorted(observed_ids) and len(observed_ids) == 39,
        'classification': 'audit of existing deterministic artifacts; no threshold change or new study',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sabotage', action='store_true')
    args = parser.parse_args()
    evaluator = status_only_evaluator if args.sabotage else evaluate
    controls = []
    for mode in ('flipped', 'missing', 'integer_one', 'integer_zero'):
        fixtures, outcomes = evaluator(malformed_checker(mode))
        controls.append({'mode': mode, 'cases': len(fixtures),
                         'incorrectly_matched': sum(r['matched'] for r in outcomes)})
    fixtures, honest = evaluate()
    pin = json.loads((HERE/'RECORDED.json').read_text())['faults']
    honest_digest = hashlib.sha256(canonical(honest)).hexdigest()
    calibration = audit_existing_calibration()
    checks = {
        'B1_all_malformed_envelopes_fail_matching': all(r['cases'] == 114 and r['incorrectly_matched'] == 0 for r in controls),
        'B1_honest_114_and_digest_unchanged': len(fixtures) == 114 and all(r['matched'] for r in honest) and honest_digest == pin['outcomes_digest'],
        'B4_original_240_rows': calibration['rows'] == 240 and calibration['unique_ids'] == 240,
        'B4_39_causes_match_prediction': calibration['all_39_explained'] and calibration['group_counts'] == {'sample_only': 2, 'momentum_only': 14, 'both': 23},
    }
    # Explicit current-source scope; this is not a whole-repository inventory.
    paths = sorted(HERE.glob('*.py')) + [HERE/name for name in
             ('RECORDED.json', 'GATE_B_SCOPE.md', 'PREREGISTRATION_DRAFT.md')]
    paths += sorted((HERE/'evidence/gate_b/pre_repair').glob('*'))
    source = {}
    for path in paths:
        data = path.read_bytes()
        source[path.relative_to(ROOT).as_posix()] = {
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
            'md5': hashlib.md5(data).hexdigest()}

    report = {
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'command': [sys.executable, *sys.argv], 'python': sys.version, 'platform': platform.platform(),
        'classification': 'same-author CI engineering regression; no independent scientific review or AI study',
        'sources': source, 'controls': controls, 'honest_outcomes_digest': honest_digest,
        'calibration_audit': calibration, 'checks': checks, 'accepted': all(checks.values()),
    }
    print('GATE_B_REPORT_BEGIN')
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    print('GATE_B_REPORT_END')
    print('GATE: '+('PASS' if report['accepted'] else 'FAIL'))
    return 0 if report['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
