"""CCC-001 closeout: recompute each turn's body SHA-256 from its body text (UTF-8) instead of trusting the stored
body_sha256 field, then compare bodies to earlier prefixes by turn number. Added because relay_check_040.py compares
stored digests only. Usage: relay_check_bodies.py PREFIX_040.json PRIOR_PREFIX.json..."""
import hashlib, json, sys
h = lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest()
t = json.load(open(sys.argv[1]))['turns']
print('stored body_sha256 equals recomputed', sum(h(x['body']) == x['body_sha256'] for x in t), 'of', len(t))
m = {x['nnn']: x['body'] for x in t}
for k in sys.argv[2:]:
    s = json.load(open(k))['turns']
    print('body text equal to', k.split('/')[-1], sum(m.get(x['nnn']) == x['body'] for x in s), 'of', len(s))
