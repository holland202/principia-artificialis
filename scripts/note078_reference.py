#!/usr/bin/env python3
"""Verify PA-JSON-002's saved observations. No new subject execution or network."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'experiments/pa_json_002'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sabotage',action='store_true')
args=parser.parse_args()
try:
    meta=json.loads((STUDY/'results/metadata.json').read_text())
    for name,wanted in meta['source_sha256'].items():
        if hashlib.sha256((STUDY/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('executed source identity changed: '+name)
    lines=(STUDY/'MANIFEST.sha256').read_text().splitlines()
    if not lines:raise ValueError('empty manifest')
    for line in lines:
        wanted,relative=line.split('  ',1)
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT) or hashlib.sha256(path.read_bytes()).hexdigest()!=wanted:
            raise ValueError('artifact identity mismatch: '+relative)
    command=[sys.executable,str(STUDY/'run.py'),'--verify',str(STUDY/'results')]
    if args.sabotage:command.append('--sabotage')
    result=subprocess.run(command,text=True,capture_output=True,timeout=60)
    print(result.stdout,end='')
    if result.stderr:print(result.stderr,end='')
    if result.returncode==0:
        print(json.dumps({'profile':json.loads((STUDY/'results/PROFILE.json').read_text()),
                          'look_sample':{k:json.loads((STUDY/'results/LOOK_SAMPLE.json').read_text())[k] for k in ('human_look','distinct_cases','roles_to_case_ids')},
                          'metadata':meta},indent=2))
        print('POST-HOC CLI WITNESSES (same author, not independent):')
        print((STUDY/'results/minimal_cli.stdout.txt').read_text(),end='')
    sys.exit(result.returncode)
except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
    print('GATE: FAIL '+str(exc));sys.exit(1)
