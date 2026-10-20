"""Selected in-memory source mutations; every mutant must trigger actual test failures."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest

MUTANTS = {
    'always_accept': ("accepted = gates['profile'] and gates['boundary'] and gates['momentum']", 'accepted = True'),
    'always_reject': ("accepted = gates['profile'] and gates['boundary'] and gates['momentum']", 'accepted = False'),
    'profile_disabled': ("'profile': profile <= profile_limit", "'profile': True"),
    'momentum_disabled': ("'momentum': residual <= momentum_limit", "'momentum': True"),
    'precision_disabled': ('if normalized_error > MAX_SAMPLE_ERROR or momentum_limit > MAX_MOMENTUM_ALLOWANCE:', 'if False:'),
    'tolerance_cap_disabled': ('if not 0 < tol <= MAX_TOLERANCE or sample_error < 0:', 'if tol <= 0 or sample_error < 0:'),
    'nonfinite_accepted': ("return _deny('nonfinite_or_out_of_range_sample')", "return {'accepted': True, 'status': 'ACCEPTED'}"),
    'poiseuille_rhs_sign': ("rhs = 0 if kind == 'couette' else -8", "rhs = 0 if kind == 'couette' else 8"),
}


def child(name):
    root = Path(__file__).parent
    source = (root/'ns001.py').read_text()
    before, after = MUTANTS[name]
    if source.count(before) != 1:
        raise RuntimeError('mutation location is missing or ambiguous')
    module = types.ModuleType('ns001')
    exec(compile(source.replace(before, after), 'ns001_MUTANT_'+name, 'exec'), module.__dict__)
    sys.modules['ns001'] = module
    suite = unittest.defaultTestLoader.discover(str(root), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'mutant': name, 'tests_run': result.testsRun,
                      'failures': [t.id() for t, _ in result.failures],
                      'errors': [t.id() for t, _ in result.errors]}, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mutant', choices=tuple(MUTANTS))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.mutant:
        return child(args.mutant)
    if args.output is None:
        parser.error('--output is required')
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).parent
    def source_snapshot():
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob('*.py'))}
    before_snapshot = source_snapshot()
    baseline_command = [sys.executable, '-m', 'unittest', 'discover', '-s', str(root), '-p', 'test_*.py', '-v']
    baseline = subprocess.run(baseline_command, capture_output=True, text=True, check=False)
    (args.output/'baseline.stdout.txt').write_text(baseline.stdout)
    (args.output/'baseline.stderr.txt').write_text(baseline.stderr)
    if baseline.returncode != 0:
        print('GATE: FAIL — unmutated baseline fails; mutations cannot be credited')
        return 1
    results = []
    for name in MUTANTS:
        command = [sys.executable, str(Path(__file__)), '--mutant', name]
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        (args.output/(name+'.stdout.txt')).write_text(proc.stdout)
        (args.output/(name+'.stderr.txt')).write_text(proc.stderr)
        metadata = json.loads(proc.stdout.splitlines()[-1]) if proc.stdout else {}
        detected = (proc.returncode == 1 and metadata.get('tests_run', 0) >= 20
                    and bool(metadata.get('failures')) and metadata.get('errors') == [])
        results.append({'name': name, 'command': command, 'exit_code': proc.returncode,
                        'detected_by_test_failures': detected, **metadata})
    frozen = source_snapshot() == before_snapshot
    report = {'baseline_command': baseline_command, 'baseline_exit_code': baseline.returncode,
              'source_snapshot_sha256': before_snapshot, 'source_unchanged_during_run': frozen,
              'mutants': results}
    (args.output/'summary.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps(results, indent=2, sort_keys=True))
    ok = frozen and all(r['detected_by_test_failures'] for r in results)
    print(f'SELECTED MUTANTS: {sum(r["detected_by_test_failures"] for r in results)}/{len(results)} detected')
    print('GATE: '+('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
