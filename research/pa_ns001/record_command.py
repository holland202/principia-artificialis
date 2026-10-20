"""Record one local command without replacing earlier evidence. No network operations."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a command is required')
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parent
    source_hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted(root.rglob('*')) if p.is_file()
                     and 'evidence' not in p.relative_to(root).parts
                     and '__pycache__' not in p.parts}
    started = datetime.now(timezone.utc).isoformat()
    begin = time.perf_counter()
    # Do not serialize environment variables, credentials, or unrelated workspaces.
    clean_env = {k: os.environ[k] for k in ('PATH', 'TMPDIR', 'XDG_CACHE_HOME') if k in os.environ}
    clean_env['PYTHONNOUSERSITE'] = '1'
    clean_env['PYTHONDONTWRITEBYTECODE'] = '1'
    proc = subprocess.run(command, capture_output=True, env=clean_env, check=False)
    for name, data in [('stdout.txt', proc.stdout), ('stderr.txt', proc.stderr)]:
        (args.output / name).write_bytes(data)
    metadata = {
        'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'command': command, 'cwd': 'repository root', 'exit_code': proc.returncode,
        'elapsed_seconds': time.perf_counter() - begin,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'python': sys.version, 'platform': platform.platform(),
        'source_sha256': source_hashes,
        'stdout_sha256': hashlib.sha256(proc.stdout).hexdigest(),
        'stderr_sha256': hashlib.sha256(proc.stderr).hexdigest(),
        'classification': 'local software engineering evidence; no AI study',
    }
    (args.output / 'RUN.json').write_text(json.dumps(metadata, indent=2, sort_keys=True) + '\n')
    sys.stdout.buffer.write(proc.stdout)
    sys.stderr.buffer.write(proc.stderr)
    print(f'RECORDED exit={proc.returncode} in {args.output}')
    return proc.returncode


if __name__ == '__main__':
    raise SystemExit(main())
