"""CCC-001 040 export check: turns 001-040 once in order; bodies equal to earlier prefix snapshots. Usage: relay_check_040.py PREFIX_040.json PRIOR_PREFIX.json..."""
import json,sys
p=json.load(open(sys.argv[1])); t=p['turns']
print('keys',sorted(t[0].keys()))
print('turn numbers 001-040 once, in order:', [x['nnn'] for x in t]==[f'{i:03d}' if isinstance(t[0]['nnn'],str) else i for i in range(1,41)])
m={x['nnn']:x['body_sha256'] for x in t}
for k in sys.argv[2:]:
    s=json.load(open(k))['turns']
    print('bodies equal to',k.split('/')[-1],sum(1 for x in s if m.get(x['nnn'])==x['body_sha256']),'of',len(s))
