#!/usr/bin/env python3
"""Pre-registration eligibility counts only; no SQLite/Python-float/JS parsing."""
from collections import Counter
import hashlib
import json
from cases import corpus, rational

rows = list(corpus())
eligible = [r for r in rows if rational(r['token']) == rational(r['baseline'])]
canonical = ''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in rows).encode()
counts = {'cases':len(rows),'exact_equivalent_cases':len(eligible),
          'distinct_transformed_tokens':len({r['token'] for r in rows}),
          'distinct_baseline_values':len({rational(r['baseline']) for r in rows}),
          'nonidentity_spellings':sum(r['token'] != r['baseline'] for r in rows),
          'maximum_token_bytes':max(len(r['token'].encode()) for r in rows),
          'total_transformed_token_bytes':sum(len(r['token'].encode()) for r in rows),
          'by_family':dict(Counter(r['family'] for r in rows)),
          'by_sign':dict(Counter(r['sign'] for r in rows)),
          'by_padding':dict(Counter(r['padding'] for r in rows)),
          'corpus_sha256':hashlib.sha256(canonical).hexdigest(),
          'subject_parsers_invoked':0}
print(json.dumps(counts,indent=2,sort_keys=True))
