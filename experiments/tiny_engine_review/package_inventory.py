"""Log public package identity before deleting requested transfer branches.

Codex/OpenAI, 2026-11-17; human direction: Chad Holland. No model execution.
Hub LFS metadata is checked; remote weight bytes are not downloaded by this log.
"""
import hashlib
import json
import subprocess
import urllib.request

PACKAGES = (
    ('tiny-engine-165k', 'e3f170ac2e54e72b26f24716d98fd4296e403887'),
    ('rmt-ih-001', 'f083431d5177a2348e8fd68949973f758fa02be1'),
)


def api(path):
    with urllib.request.urlopen('https://huggingface.co/api/models/holland202/' + path, timeout=30) as response:
        return json.load(response)


def git_bytes(ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'])


for name, ref in PACKAGES:
    info = api(name)
    revision = info['sha']
    remote = {entry['path']: entry for entry in api(f'{name}/tree/{revision}?recursive=true&expand=false')
              if entry['type'] == 'file'}
    local = subprocess.check_output(['git', 'ls-tree', '-r', ref], text=True).splitlines()
    expected = {}
    for line in git_bytes(ref, 'SHA256SUMS').decode().splitlines():
        sha, path = line.split(None, 1)
        expected[path.strip()] = sha
    rows = []
    for line in local:
        metadata, path = line.split('\t', 1)
        git_blob = metadata.split()[2]
        data = git_bytes(ref, path)
        sha256 = hashlib.sha256(data).hexdigest()
        other = remote.get(path, {})
        method = 'Hub LFS SHA-256 metadata' if 'lfs' in other else 'Git blob ID'
        match = other.get('lfs', {}).get('oid') == sha256 if 'lfs' in other else other.get('oid') == git_blob
        rows.append({'path': path, 'bytes': len(data), 'sha256': sha256,
                     'md5': hashlib.md5(data).hexdigest(), 'hub_match': match,
                     'comparison': method,
                     'local_manifest_match': expected.get(path) == sha256 if path in expected else None})
    print(json.dumps({'repo': 'holland202/' + name, 'github_package_commit': ref,
                      'hugging_face_revision': revision, 'files': rows,
                      'package_files': len(rows), 'manifest_entries': len(expected),
                      'hub_only_files': sorted(set(remote) - {row['path'] for row in rows}),
                      'all_hub_entries_match': all(row['hub_match'] for row in rows),
                      'all_manifest_entries_match': all(row['local_manifest_match'] is not False for row in rows)
                        and set(expected) <= {row['path'] for row in rows},
                      'remote_weight_bytes_downloaded': False}, sort_keys=True, indent=2))
