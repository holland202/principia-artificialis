#!/usr/bin/env python3
"""Inspect PA-JSON-001's saved observations; never rerun the subject conversions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'experiments' / 'pa_json_001'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sabotage', action='store_true')
    args = parser.parse_args()
    try:
        manifest = (STUDY / 'MANIFEST.sha256').read_text().splitlines()
        if not manifest:
            raise ValueError('empty manifest')
        for line in manifest:
            expected, relative = line.split('  ', 1)
            path = (ROOT / relative).resolve()
            if not path.is_relative_to(ROOT):
                raise ValueError('manifest path escapes repository')
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError('archive hash mismatch: ' + relative)
        freeze = json.loads((STUDY / 'FREEZE.json').read_text())
        summary = json.loads((STUDY / 'results' / 'summary.json').read_text())
        for filename, expected in freeze['files'].items():
            actual = hashlib.sha256((STUDY / filename).read_bytes()).hexdigest()
            if actual != expected or summary['source_sha256'][filename] != expected:
                raise ValueError('frozen source mismatch: ' + filename)
        command = ['node', str(STUDY / 'verify.mjs'), str(STUDY / 'results')]
        if args.sabotage:
            command.append('--sabotage')
        checked = subprocess.run(command, text=True, capture_output=True, timeout=60)
        if checked.returncode:
            print(checked.stderr.strip())
            print('GATE: FAIL archive observation check')
            return 1
        verified = json.loads(checked.stdout)
        if args.sabotage:
            raise ValueError('sabotage escaped the observer')
        print('EXPLORATORY ARCHIVE — SELF-TESTED — NOVELTY REJECTED FOR THE SQLITE DEFECT')
        print(json.dumps({'counts':verified['counts'],'observerDisagreements':verified['observerDisagreements'],'generation':summary['generation'],'oracle_checks':summary['oracle_checks'],'environment':{key:summary['environment'][key] for key in ['python','sqlite_version','sqlite_source_id']},'node_original':summary['environment']['node']['node'],'cases_sha256':summary['cases_sha256']}, indent=2))
        profile = json.loads((STUDY / 'results' / 'corpus_profile.json').read_text())
        sample = json.loads((STUDY / 'results' / 'look_sample.json').read_text())
        provenance = json.loads((STUDY / 'SOURCE_PROVENANCE.json').read_text())
        example = next(row for row in sample['cases'] if row['id'] == 0)
        print(json.dumps({'profile':profile,'distinct_look_cases':sample['distinct_cases'],'look_sample_review':sample['human_look'],'source_fix':{'commit':provenance['commit'],'date':provenance['committed_at']},'raw_example':{'id':example['id'],'bits':example['bits'],'input':example['input'],'sqlite_numeric':example['outcomes']['sqlite_numeric'],'sqlite_cast':example['outcomes']['sqlite_cast']}},indent=2))
        print('GATE: PASS archive integrity and stored-observation consistency only')
        print('PA registered confirmation: NOT RUN; empirical validity: NOT RUN; human look: NOT PERFORMED')
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print('GATE: FAIL ' + str(exc))
        return 1

if __name__ == '__main__':
    sys.exit(main())
