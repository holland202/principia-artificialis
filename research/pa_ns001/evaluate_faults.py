"""Evaluate constructed fixtures using the real checker, not AI judgments."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from fault_cases import canonical, cases, decode_values
from ns001 import verify


def evaluate(verifier=verify):
    fixtures, outcomes = list(cases()), []
    for row in fixtures:
        kwargs = {k: float(v) for k, v in row['parameters'].items()}
        result = verifier(row['family'], decode_values(row),
                          sample_error_bound=row['sample_error_bound'], **kwargs)
        # A correct status label cannot excuse an absent, non-Boolean or
        # contradictory operational acceptance field.
        matched = (type(result) is dict
                   and result.get('status') == row['expected_status']
                   and type(result.get('accepted')) is bool
                   and result['accepted'] is (row['expected_status'] == 'ACCEPTED'))
        outcomes.append({'id': row['id'], 'expected_status': row['expected_status'],
                         'observed': result, 'matched': matched})
    return fixtures, outcomes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sabotage', choices=('always-accept', 'always-reject'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    checker = verify
    if args.sabotage:
        status = 'ACCEPTED' if args.sabotage == 'always-accept' else 'REJECTED'
        checker = lambda *a, **k: {'accepted': status == 'ACCEPTED', 'status': status}
    fixtures, outcomes = evaluate(checker)
    manifest_bytes = b''.join(canonical(r)+b'\n' for r in fixtures)
    (args.output/'manifest.jsonl').write_bytes(manifest_bytes)
    (args.output/'outcomes.jsonl').write_bytes(b''.join(canonical(r)+b'\n' for r in outcomes))
    summary = {'cases': len(fixtures), 'matched': sum(r['matched'] for r in outcomes),
               'expected_counts': dict(Counter(r['expected_status'] for r in fixtures)),
               'observed_counts': dict(Counter(r['observed']['status'] for r in outcomes)),
               'indistinguishable_controls': sum(r['construction_facts']['indistinguishable'] for r in fixtures),
               'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
               'outcomes_digest': hashlib.sha256(canonical(outcomes)).hexdigest(),
               'failures': [r['id'] for r in outcomes if not r['matched']],
               'classification': 'constructed software checks; not AI performance or scientific validation'}
    (args.output/'summary.json').write_text(json.dumps(summary, sort_keys=True, indent=2)+'\n')
    print(json.dumps(summary, sort_keys=True, indent=2))
    ok = bool(fixtures) and all(r['matched'] for r in outcomes)
    print('P4: '+('HELD' if ok else 'IMPLEMENTATION_ERROR'))
    print('DIGEST '+summary['outcomes_digest'])
    print('GATE: '+('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
