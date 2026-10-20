"""Reproduce pinned software checks only. No AI, external services or scientific study."""
import argparse
import json
import re
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sabotage', action='store_true', help='substitute an always-accept fixture checker; must fail')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).parent
    pinned = json.loads((root/'RECORDED.json').read_text())
    if pinned.get('schema') != 'pa-ns001-engineering-outcomes/1':
        raise ValueError('missing pinned outcome schema')
    history = []

    def run(name, command, expected_exit=0):
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        (args.output/(name+'.stdout.txt')).write_text(proc.stdout)
        (args.output/(name+'.stderr.txt')).write_text(proc.stderr)
        ok = proc.returncode == expected_exit
        history.append({'name': name, 'command': command, 'exit_code': proc.returncode,
                        'expected_exit': expected_exit, 'matched': ok})
        print(name, 'exit', proc.returncode, 'expected', expected_exit)
        return ok

    python = sys.executable
    for name, flags in (('normal', []), ('optimized', ['-O']), ('docstrings_removed', ['-OO'])):
        run('tests_'+name, [python, *flags, '-m', 'unittest', 'discover', '-s', str(root), '-p', 'test_*.py', '-v'])
        stderr = (args.output/('tests_'+name+'.stderr.txt')).read_text()
        count = re.search(r'Ran (\d+) tests? in ', stderr)
        history.append({'name': 'test_count_'+name,
                        'matched': bool(count) and int(count.group(1)) == pinned['tests']})
    for repetition in range(1, 4):
        destination = args.output / f'calibration{repetition}'
        run(f'calibration{repetition}', [python, str(root/'calibrate.py'), '--output', str(destination)])
        summary = json.loads((destination/'summary.json').read_text())
        expected = pinned['calibration']
        match = all(summary[k] == v for k, v in expected.items())
        history.append({'name': f'calibration{repetition}_pinned', 'matched': match})
    destination = args.output/'faults'
    command = [python, str(root/'evaluate_faults.py'), '--output', str(destination)]
    if args.sabotage:
        command += ['--sabotage', 'always-accept']
    run('faults', command)
    summary = json.loads((destination/'summary.json').read_text())
    history.append({'name': 'faults_pinned', 'matched': all(summary[k] == v for k, v in pinned['faults'].items())})
    for mode in ('always-accept', 'always-reject'):
        run('control_'+mode, [python, str(root/'evaluate_faults.py'), '--output', str(args.output/mode), '--sabotage', mode], 1)
    run('selected_mutants', [python, str(root/'mutation_checks.py'), '--output', str(args.output/'mutants')])
    report = {'classification': 'software validation only; AI evaluation NOT RUN', 'checks': history,
              'accepted': all(r['matched'] for r in history)}
    (args.output/'summary.json').write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
    print('GATE: '+('PASS' if report['accepted'] else 'FAIL'))
    return 0 if report['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
