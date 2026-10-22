#!/usr/bin/env python3
"""Bounded documentary-integrity checker: links fail; scientific claims require review.

Standard library only; read-only. Does not inspect external URLs, validate anchors,
prove a claim's truth, run experiment code, or rewrite files.

Usage:
  python scripts/doc_evidence_check.py --paths docs/new.md README.md
  python scripts/doc_evidence_check.py --changed-base origin/main
  python scripts/doc_evidence_check.py --selftest
  python scripts/doc_evidence_check.py --sabotage  # must exit 1 (planted broken link)

Broken local Markdown link targets are failures. Verification-like language without an
obvious provenance pointer is a nonblocking REVIEW lead, never a scientific verdict.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
INLINE = re.compile(r'(?<!!)!?\[[^\]\n]+\]\(\s*(<[^>]+>|[^\s)]+)')
REFERENCE = re.compile(r'^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)')
CLAIM = re.compile(r'\b(?:verified|validated|reproduced|(?:tests?|ci|checks?)\s+(?:have\s+)?pass(?:ed)?)\b', re.I)
TRACE = re.compile(r'(?:reference code|evidence (?:source|file|link)|results/|commit\s+[0-9a-f]{7,40}|sha-?256|raw output|run command|https?://)', re.I)


def visible_lines(body):
    fenced = False
    for number, line in enumerate(body.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith('```') or stripped.startswith('~~~'):
            fenced = not fenced
            continue
        if fenced:
            continue
        # Inline-code segments are not Markdown links to check.
        line = re.sub(r'`+[^`\n]*`+', '', line)
        yield number, line


def resolve_local(root, document, target):
    """None means external/anchor-only; otherwise return (exists, label)."""
    target = target.strip('<>')
    if not target or target.startswith('#') or target.startswith('//'):
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or target.startswith('/'):
        return None  # GitHub Pages root-relative and external links are not verified.
    if not parts.path:
        return None
    try:
        relpath = unquote(parts.path)
        dest = (root / document.parent / relpath).resolve()
        root_abs = root.resolve()
        if not dest.is_relative_to(root_abs):
            return (False, 'link escapes repository')
        return (dest.exists(), relpath)
    except (ValueError, OSError):
        return (False, 'unresolvable local link')


def audit_text(root, document, body):
    """Report (failures, review leads). No automatic truth/status inference."""
    errors, advisories = [], []
    visible = list(visible_lines(body))
    any_trace = bool(TRACE.search('\n'.join(line for _, line in visible)))
    for line_no, line in visible:
        for match in list(INLINE.finditer(line)) + ([REFERENCE.match(line)] if REFERENCE.match(line) else []):
            if match is None:
                continue
            link = match.group(1)
            result = resolve_local(root, document, link)
            if result is not None and not result[0]:
                errors.append(f'{document}:{line_no}: BROKEN_LOCAL_LINK {link} ({result[1]})')
        if CLAIM.search(line) and not any_trace:
            advisories.append(f'{document}:{line_no}: REVIEW_EVIDENCE_POINTER verification language with no obvious source pointer in file; manual review required')
    return errors, advisories


def audit_file(root, name):
    candidate = root / name
    path = candidate.resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return [f'{name}: MISSING_INPUT or path outside repository'], []
    try:
        body = path.read_text(encoding='utf-8')
    except (UnicodeError, OSError) as exc:
        return [f'{name}: UNREADABLE_INPUT {type(exc).__name__}'], []
    return audit_text(root, Path(name), body)


def changed_md_files(root, base):
    proc = subprocess.run(['git', '-C', str(root), 'diff', '--name-only', '--diff-filter=ACMR', '-z', f'{base}...HEAD'], capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError('git diff failed (missing base ref or history)')
    return [p for p in proc.stdout.decode('utf-8').split('\0') if p.endswith('.md')]


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'good.txt').write_text('ok', encoding='utf-8')
        errors, _ = audit_text(root, Path('doc.md'), '[ok](good.txt)')
        if errors:
            return False
        planted, _ = audit_text(root, Path('doc.md'), '[bad](missing___plant.txt)')
        return len(planted) == 1 and 'BROKEN_LOCAL_LINK' in planted[0]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--paths', nargs='+')
    mode.add_argument('--changed-base')
    mode.add_argument('--selftest', action='store_true')
    mode.add_argument('--sabotage', action='store_true')
    args = p.parse_args(argv)
    if args.selftest or args.sabotage:
        passed = selftest()
        print('INSTRUMENT_SELFTEST ' + ('PASS' if passed else 'FAIL'))
        if args.sabotage:
            print('BROKEN_LOCAL_LINK planted; gate refuses success' if passed else 'Sabotage not detected')
            return 1  # planted defect must yield nonzero status
        return 0 if passed else 1
    if not args.paths and not args.changed_base:
        p.error('supply --paths, --changed-base, --selftest, or --sabotage')
    try:
        paths = args.paths if args.paths else changed_md_files(ROOT, args.changed_base)
    except (RuntimeError, UnicodeError) as exc:
        print('COULD NOT RUN: ' + str(exc))
        return 2
    errors, advisories = [], []
    for file in sorted(set(path for path in paths if path.endswith('.md'))):
        e, a = audit_file(ROOT, file)
        errors.extend(e)
        advisories.extend(a)
    for message in errors + advisories:
        print(message)
    print(f'DOC_EVIDENCE_CHECK: {len(errors)} broken/missing, {len(advisories)} review leads; {len(set(paths))} paths requested')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
