#!/usr/bin/env python3
"""Post-hoc descriptions of the frozen observations; no subject execution."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
rows=[json.loads(line) for line in gzip.decompress((ROOT/'results/observations.jsonl.gz').read_bytes()).decode().splitlines()]
classes=Counter()
by_padding=Counter()
for row in rows:
    c=row['case'];o=row['observed']['sqlite_json']
    bits=int(o['transformed']['bits'],16)
    if o['baseline']['bits']==o['transformed']['bits']:
        label='preserved'
    elif bits & 0x7fffffffffffffff == 0:
        label='negative_zero' if bits>>63 else 'positive_zero'
    elif bits & 0x7fffffffffffffff == 0x7ff0000000000000:
        label='negative_infinity' if bits>>63 else 'positive_infinity'
    else:
        label='other_changed_value'
    classes[label]+=1
    if label!='preserved':by_padding[(c['family'],c['padding'])]+=1
profile={'cases':len(rows),'distinct_tokens':len({r['case']['token'] for r in rows}),
         'distinct_exact_values':len({(r['case']['expected_numerator'],r['case']['expected_denominator']) for r in rows}),
         'outcome_classes':dict(classes),
         'disagreements_by_family_and_padding':[{'family':f,'padding':n,'cases':count} for (f,n),count in sorted(by_padding.items())]}
roles={'benign_identity':0,'unit_positive_infinity':12,'unit_positive_zero':28,
       'unit_negative_infinity':44,'unit_negative_zero':60,'benign_noninteger_small_padding':193,
       'integer_midpoint_rounding_control':256}
sample=[]
for case_id in sorted(set(roles.values())):
    row=rows[case_id];c=dict(row['case']);token=c.pop('token')
    sample.append({'case':c,'token_bytes':len(token),'token_sha256':hashlib.sha256(token.encode()).hexdigest(),
                   'token_prefix':token[:24],'token_suffix':token[-24:],
                   'expected_bits':row['expected_bits'],'observed':row['observed']})
look={'human_look':'NOT PERFORMED','selection':'post-hoc named registered witnesses and benign cases',
      'roles_to_case_ids':roles,'distinct_cases':len(sample),'cases':sample}
(ROOT/'results/PROFILE.json').write_text(json.dumps(profile,indent=2)+'\n')
(ROOT/'results/LOOK_SAMPLE.json').write_text(json.dumps(look,indent=2)+'\n')
print(json.dumps({'profile':profile,'look_roles':roles,'distinct_look_cases':len(sample)},indent=2))
