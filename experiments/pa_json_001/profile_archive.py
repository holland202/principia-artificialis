#!/usr/bin/env python3
"""Post-hoc corpus descriptions and a named sample for a future human look."""
from collections import Counter
import gzip
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent
rows = [json.loads(line) for line in gzip.decompress((ROOT/'results/cases.jsonl.gz').read_bytes()).decode().splitlines()]
profile = Counter()
exponents = set()
values = []
for row in rows:
    bits = int(row['bits'],16)
    x = struct.unpack('>d',bits.to_bytes(8,'big'))[0]
    values.append(x)
    exponent = bits >> 52 & 2047
    exponents.add(exponent)
    profile['negative' if bits >> 63 else 'positive'] += 1
    profile['subnormal' if exponent == 0 else 'normal'] += 1
    profile['integer_valued' if x.is_integer() else 'noninteger_valued'] += 1
    profile['sqlite_numeric_loss' if row['outcomes']['sqlite_numeric']['fidelity_loss'] else 'sqlite_numeric_preserved'] += 1
profile['cases'] = len(rows)
profile['distinct_bit_patterns'] = len({row['bits'] for row in rows})
profile['distinct_exponent_fields'] = len(exponents)
selected = {}
selectors = {
    'first_loss': lambda i: rows[i]['outcomes']['sqlite_numeric']['fidelity_loss'],
    'first_preserved': lambda i: not rows[i]['outcomes']['sqlite_numeric']['fidelity_loss'],
    'first_subnormal': lambda i: (int(rows[i]['bits'],16)>>52 & 2047) == 0,
    'first_integer_valued': lambda i: values[i].is_integer(),
    'first_noninteger_valued': lambda i: not values[i].is_integer(),
    'first_negative': lambda i: values[i] < 0,
}
for name, predicate in selectors.items():
    selected[name] = next(i for i in range(len(rows)) if predicate(i))
selected['smallest_absolute'] = min(range(len(rows)),key=lambda i: abs(values[i]))
selected['largest_absolute'] = max(range(len(rows)),key=lambda i: abs(values[i]))
sample = {'human_look':'NOT PERFORMED','selection':'post-hoc deterministic representatives; named roles may share a case','roles_to_case_ids':selected,'distinct_cases':len(set(selected.values())),'cases':[rows[i] for i in sorted(set(selected.values()))]}
(ROOT/'results/corpus_profile.json').write_text(json.dumps(dict(profile),indent=2)+'\n')
(ROOT/'results/look_sample.json').write_text(json.dumps(sample,indent=2)+'\n')
print(json.dumps({'profile':dict(profile),'roles_to_case_ids':selected,'distinct_look_cases':sample['distinct_cases']},indent=2))
