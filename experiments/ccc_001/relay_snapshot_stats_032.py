# Counting script for the 032 snapshot log (relay_snapshot_032_run.txt). Run from the repo root: python3 experiments/ccc_001/relay_snapshot_stats_032.py <export>
import json,sys
sys.path.insert(0,'experiments/ccc_001')
import relay_extract as rx
exp=json.load(open(sys.argv[1]))
p=json.load(open('results/ccc_001/relay_prefix_032.json'))
T=p['turns']
print('status',p['status'],'class',p['class'],'turns',len(T))
print('edited turns',sum(1 for t in exp if t['created_at']!=t['updated_at'] and t['id'] in {x['comment_id'] for x in T}))
for k in ('024','016','008_archival'):
    s=json.load(open(f'results/ccc_001/relay_prefix_{k}.json'))['turns']
    m={x['nnn']:x['body_sha256'] for x in T}
    print(f'bodies equal to prefix {k} snapshot',sum(1 for x in s if m.get(x['nnn'])==x['body_sha256']),'of',len(s))
print('excluded non-relay comment ids',p['excluded_comment_ids'])
w=[len(x['rendered'].split()) for x in T]
print('rendered words',sum(w),'mean',round(sum(w)/len(w),1),'max',max(w))
print('turns 025-032 rendered words',sum(w[24:]),'max',max(w[24:]))
print('shuffle perm 032 (slot -> original turn)',rx.shuffle_perm(32))
