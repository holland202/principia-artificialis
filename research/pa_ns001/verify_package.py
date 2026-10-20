"""Check a source/evidence manifest against local bytes; consistency, not authenticity."""
import argparse
import hashlib
import json
from pathlib import Path


def check(root, manifest):
    if type(manifest) is not dict or manifest.get('schema') != 'pa-ns001-package/1':
        raise ValueError('unknown or absent manifest schema')
    files = manifest.get('files')
    if type(files) is not list or not files:
        raise ValueError('empty or missing file inventory')
    root = Path(root).resolve()
    seen, failures = set(), []
    for row in files:
        if type(row) is not dict or set(row) != {'path', 'bytes', 'sha256', 'md5'}:
            raise ValueError('malformed inventory entry')
        name = row['path']
        if type(name) is not str or not name or name in seen:
            raise ValueError('missing or duplicate path')
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe path')
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError('symlink/path escape')
        seen.add(name)
        if not path.is_file():
            failures.append({'path': name, 'reason': 'missing'})
            continue
        data = path.read_bytes()
        if (len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']
                or hashlib.md5(data).hexdigest() != row['md5']):
            failures.append({'path': name, 'reason': 'content_or_size_mismatch'})
    return {'accepted': not failures, 'checked_files': len(files), 'failures': failures,
            'scope': 'listed bytes only; an authenticated source commit/provenance review is also required'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args()
    try:
        result = check(args.root, json.loads(args.manifest.read_text()))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'accepted': False, 'reason': str(exc)}, sort_keys=True))
        print('GATE: FAIL')
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    print('GATE: '+('PASS' if result['accepted'] else 'FAIL'))
    return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
