#!/usr/bin/env python3
"""Build the pinned public-domain SQLite dependency; run no numeric test cases."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

COMMIT='57520227c95396ce39ba6ecaac8d475b78dd3964'
SHA3='e2b869d3003b33c942b7dd7063604fbc53553e1b66609570df39b9b7b558ee81'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--cli',action='store_true')
args=parser.parse_args()
directory=args.out.resolve()
directory.mkdir(parents=True,exist_ok=False)
source=directory/'source'
subprocess.run(['git','clone','--depth','1','--branch','version-3.54.1','https://github.com/sqlite/sqlite.git',str(source)],check=True)
actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
if actual!=COMMIT:raise SystemExit('pinned source commit mismatch')
subprocess.run(['./configure','--disable-readline'],cwd=source,check=True)
subprocess.run(['make','sqlite3.c'],cwd=source,check=True)
actual=hashlib.sha3_256((source/'sqlite3.c').read_bytes()).hexdigest()
if actual!=SHA3:raise SystemExit('official amalgamation SHA3 mismatch')
library=directory/'libsqlite3-pa-json-002.so'
subprocess.run(['cc','-O2','-fPIC','-shared','sqlite3.c','-o',str(library),'-lm','-ldl','-pthread'],cwd=source,check=True)
if args.cli:
    subprocess.run(['cc','-O2','shell.c','sqlite3.c','-o',str(directory/'sqlite3'),'-lm','-ldl','-pthread'],cwd=source,check=True)
print(json.dumps({'library':str(library),'source_git_commit':COMMIT,'amalgamation_sha3_256':actual,'library_sha256':hashlib.sha256(library.read_bytes()).hexdigest()}))
