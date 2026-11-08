#!/usr/bin/env python3
"""Reproduce the frozen numeric-conversion study; Python standard library + Node."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import sqlite3
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
N = 16384
PREFIX = 'numeric-stability-v1|'
TOKEN = re.compile(r'\[(-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\]\Z')
SQL = {
    'sqlite_numeric': "SELECT json_array(json_extract(?, '$[0]'))",
    'sqlite_token': "SELECT json_array(? -> '$[0]')",
    'sqlite_cast': "SELECT '[' || CAST(json_extract(?, '$[0]') AS TEXT) || ']'",
    'sqlite_printf17': "SELECT '[' || printf('%!.17g', json_extract(?, '$[0]')) || ']'",
}

def bits_of(x):
    return struct.unpack('>Q', struct.pack('>d', x))[0]

def float_of(bits):
    return struct.unpack('>d', struct.pack('>Q', bits))[0]

def exact_token(document):
    """A deliberately small RFC-8259 parser: exactly [number], no float parsing."""
    match = TOKEN.fullmatch(document)
    if match is None:
        return None
    text = match.group(1).lower()
    mantissa, _, exponent = text.partition('e')
    exponent = int(exponent) if exponent else 0
    whole, _, fractional = mantissa.partition('.')
    numerator = int(whole + fractional)
    scale = exponent - len(fractional)
    if scale >= 0:
        return Fraction(numerator * 10**scale)
    return Fraction(numerator, 10**(-scale))

def interval(x):
    f = Fraction.from_float(x)
    previous = math.nextafter(x, -math.inf)
    following = math.nextafter(x, math.inf)
    lo_neighbor = Fraction.from_float(previous) if math.isfinite(previous) else -Fraction(2**1024)
    hi_neighbor = Fraction.from_float(following) if math.isfinite(following) else Fraction(2**1024)
    return (lo_neighbor + f) / 2, (hi_neighbor + f) / 2, bits_of(x) % 2 == 0

def faithful(document, bounds):
    f = exact_token(document)
    if f is None:
        return False
    lo, hi, even = bounds
    return lo <= f <= hi if even else lo < f < hi

def corpus():
    rows, seen, rejected = [], set(), Counter()
    i = 0
    while len(rows) < N:
        digest = hashlib.sha256((PREFIX + str(i)).encode('ascii')).digest()
        bits = int.from_bytes(digest[:8], 'big')
        i += 1
        if (bits >> 52) & 2047 == 2047:
            rejected['nonfinite'] += 1
            continue
        if bits & ((1 << 63)-1) == 0:
            rejected['zero'] += 1
            continue
        if bits in seen:
            rejected['duplicate'] += 1
            continue
        seen.add(bits)
        x = float_of(bits)
        rows.append({'id': len(rows), 'bits': f'{bits:016x}', 'input': '[' + repr(x) + ']'})
    return rows, {'draws': i, 'rejected': dict(rejected)}

def oracle_checks(rows):
    for row in rows:
        x = float_of(int(row['bits'], 16))
        bounds = interval(x)
        if not faithful(row['input'], bounds):
            raise RuntimeError('oracle refused original repr: ' + row['bits'])
        adjacent = math.nextafter(x, math.copysign(math.inf, x))
        if math.isfinite(adjacent) and faithful('[' + repr(adjacent) + ']', bounds):
            raise RuntimeError('oracle accepted distinct neighbor: ' + row['bits'])
    for x in [1.0, math.nextafter(1.0, math.inf), -1.0, -math.nextafter(1.0, math.inf), sys.float_info.max, -sys.float_info.max, math.ulp(0.0), -math.ulp(0.0)]:
        lo, hi, even = interval(x)
        for endpoint in (lo, hi):
            # Every binary rational has a terminating decimal; construct exactly.
            numerator, denominator = endpoint.numerator, endpoint.denominator
            k = denominator.bit_length()-1
            digits = str(abs(numerator) * 5**k).zfill(k+1)
            token = ('-' if numerator < 0 else '') + (digits[:-k]+'.'+digits[-k:] if k else digits)
            if faithful('[' + token + ']', (lo, hi, even)) != even:
                raise RuntimeError('oracle midpoint parity failure')
    for document in ['[null]', '[NaN]', '[Infinity]', '[1,2]', '[01]', '[+1]', '[1.]', '[]']:
        if faithful(document, interval(1.0)):
            raise RuntimeError('oracle accepted invalid numeric document')
    return {'originals_accepted':len(rows), 'finite_adjacent_values_rejected':len(rows), 'midpoint_cases':16, 'malformed_or_nonnumeric_cases':8}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT/'results')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    rows, generation = corpus()
    checks = oracle_checks(rows)
    node = json.loads(subprocess.run(['node', str(ROOT/'node_transform.mjs')], input=json.dumps([r['input'] for r in rows]), text=True, capture_output=True, check=True, timeout=60).stdout)
    if len(node['rows']) != N:
        raise RuntimeError('Node row count mismatch')
    connection = sqlite3.connect(':memory:')
    counters = {name:Counter(n=N) for name in ['python_json','node_json',*SQL,'constant_zero_control']}
    cases_path = args.out/'cases.jsonl'
    with cases_path.open('w') as stream:
        for row, node_row in zip(rows, node['rows'], strict=True):
            x = float_of(int(row['bits'], 16))
            bounds = interval(x)
            outcomes = {'node_json':node_row}
            transformations = {
                'python_json':lambda s:json.dumps(json.loads(s),separators=(',',':'),allow_nan=False),
                **{name:(lambda s,q=q:connection.execute(q,(s,)).fetchone()[0]) for name,q in SQL.items()},
                'constant_zero_control':lambda s:'[0]',
            }
            for name, transform in transformations.items():
                try:
                    first = transform(row['input'])
                    outcomes[name] = {'first':first,'second':transform(first)}
                except Exception as exc:
                    outcomes[name] = {'error':f'{type(exc).__name__}: {exc}'}
            for name, outcome in outcomes.items():
                counter = counters[name]
                if 'error' in outcome:
                    counter['errors'] += 1
                    continue
                stable = outcome['first'] == outcome['second']
                loss = not faithful(outcome['first'],bounds)
                outcome['stable'] = stable
                outcome['fidelity_loss'] = loss
                counter['stable'] += stable
                counter['fidelity_loss'] += loss
                counter['stable_and_lossy'] += stable and loss
            stream.write(json.dumps({**row,'outcomes':outcomes},separators=(',',':'))+'\n')
    summary = {
        'sample_size':N,'corpus_prefix':PREFIX,'generation':generation,
        'oracle_checks':checks,'counts':{name:{key:count[key] for key in ['n','errors','fidelity_loss','stable','stable_and_lossy']} for name,count in counters.items()},
        'environment':{'python':sys.version,'platform':platform.platform(),'sqlite_version':sqlite3.sqlite_version,'sqlite_source_id':connection.execute('select sqlite_source_id()').fetchone()[0],'sqlite_compile_options':[r[0] for r in connection.execute('pragma compile_options')],'node':node['versions']},
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'PROTOCOL.md',ROOT/'run.py',ROOT/'node_transform.mjs']},
        'cases_sha256':hashlib.sha256(cases_path.read_bytes()).hexdigest(),
    }
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'counts':summary['counts'],'oracle_checks':checks,'cases_sha256':summary['cases_sha256']},indent=2))

if __name__ == '__main__':
    main()
