#!/usr/bin/env python3
"""PA-JSON-002 registered parsing study and offline observation verification."""
import argparse
from collections import Counter
import ctypes as C
from datetime import datetime, timezone
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import struct
import subprocess
import sys

from cases import corpus, rational

ROOT = Path(__file__).resolve().parent
REGISTRATION = '5089867192d5d42d5c0ab9a3cd1f967cb596bb9f'
SOURCE_ID = '2026-10-16 14:45:20 555e07ef33f69a0957d24d8e555b702464a131d6f1607f4c3c1e4551e8e6ca76'
CORPUS_SHA = '9aa6c77939135ac22fcf74d9818f6d12691205f9325c2f3c56877dedc99a3076'
ROUTES = ('sqlite_json','sqlite_cast','python','javascript')

def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def round_ratio(n,d):
    q,r = divmod(n,d)
    return q + int(2*r > d or (2*r == d and q % 2 != 0))

def expected_bits(value):
    """Correct rounding of an exact Fraction by integer arithmetic only."""
    sign = int(value < 0)
    n,d = abs(value.numerator),value.denominator
    if n == 0:
        return '0000000000000000'
    e = n.bit_length()-d.bit_length()
    if (n < d << e) if e >= 0 else (n << -e < d):
        e -= 1
    if e < -1022:
        bits = round_ratio(n << 1074,d)
    else:
        shift = 52-e
        m = round_ratio(n << shift,d) if shift >= 0 else round_ratio(n,d << -shift)
        if m >= 1 << 53:
            m >>= 1
            e += 1
        bits = (0x7ff0000000000000 if e > 1023
                else ((e+1023) << 52) | (m-(1 << 52)))
    return f'{bits | (sign << 63):016x}'

def calibrate():
    tests = [(Fraction(1),'3ff0000000000000'),(Fraction(-1),'bff0000000000000'),
             (Fraction(1,2),'3fe0000000000000'),(Fraction(5,4),'3ff4000000000000'),
             (Fraction(1,10),'3fb999999999999a'),
             (Fraction(2**53+1),'4340000000000000'),
             (Fraction(2**53+3),'4340000000000002'),
             (Fraction(-(2**53+1)),'c340000000000000'),
             (Fraction(1,2**1074),'0000000000000001'),
             (Fraction(1,2**1075),'0000000000000000')]
    if any(expected_bits(f) != bits for f,bits in tests):
        raise ValueError('exact rounding calibration failed')
    for token in ('1e','-','01'):
        try:
            rational(token)
        except ValueError:
            continue
        raise ValueError('exact token guard accepted malformed JSON')
    return {'rounding_cases':len(tests),'invalid_oracle_cases':3}

class SQLite:
    def __init__(self,path):
        self.lib=C.CDLL(str(Path(path).resolve()))
        functions = {
            'sqlite3_libversion':([],C.c_char_p),'sqlite3_sourceid':([],C.c_char_p),
            'sqlite3_open':([C.c_char_p,C.POINTER(C.c_void_p)],C.c_int),
            'sqlite3_close':([C.c_void_p],C.c_int),
            'sqlite3_prepare_v2':([C.c_void_p,C.c_char_p,C.c_int,C.POINTER(C.c_void_p),C.POINTER(C.c_char_p)],C.c_int),
            'sqlite3_bind_text':([C.c_void_p,C.c_int,C.c_char_p,C.c_int,C.c_void_p],C.c_int),
            'sqlite3_step':([C.c_void_p],C.c_int),'sqlite3_reset':([C.c_void_p],C.c_int),
            'sqlite3_clear_bindings':([C.c_void_p],C.c_int),'sqlite3_finalize':([C.c_void_p],C.c_int),
            'sqlite3_column_type':([C.c_void_p,C.c_int],C.c_int),
            'sqlite3_column_int':([C.c_void_p,C.c_int],C.c_int),
            'sqlite3_column_double':([C.c_void_p,C.c_int],C.c_double),
            'sqlite3_column_text':([C.c_void_p,C.c_int],C.c_char_p),
            'sqlite3_errmsg':([C.c_void_p],C.c_char_p),
        }
        for name,(args,result) in functions.items():
            fn=getattr(self.lib,name);fn.argtypes=args;fn.restype=result
        self.version=self.lib.sqlite3_libversion().decode()
        self.sourceid=self.lib.sqlite3_sourceid().decode()
        if self.version != '3.54.1' or self.sourceid != SOURCE_ID:
            raise ValueError('COULD NOT RUN AS REGISTERED: target library identity mismatch')
        self.db=C.c_void_p()
        if self.lib.sqlite3_open(b':memory:',C.byref(self.db)) != 0:
            raise ValueError('sqlite3_open failed')
        self.statements={}
        statements={
            'sqlite_json':"SELECT json_valid(?1), typeof(json_extract(?1,'$')), json_extract(?1,'$')",
            'sqlite_cast':"SELECT typeof(CAST(?1 AS REAL)), CAST(?1 AS REAL)",
            'valid':"SELECT json_valid(?1)",
        }
        for name,sql in statements.items():
            stmt=C.c_void_p()
            rc=self.lib.sqlite3_prepare_v2(self.db,sql.encode(),-1,C.byref(stmt),None)
            if rc != 0:
                self.close();raise ValueError('sqlite3_prepare_v2 failed')
            self.statements[name]=stmt

    def query(self,route,token):
        stmt=self.statements[route]
        try:
            raw=token.encode('ascii')
            rc=self.lib.sqlite3_bind_text(stmt,1,raw,len(raw),C.c_void_p(-1))
            if rc != 0:
                return {'error':'bind failed','rc':rc}
            rc=self.lib.sqlite3_step(stmt)
            if rc != 100:
                return {'error':self.lib.sqlite3_errmsg(self.db).decode(),'rc':rc}
            if route == 'valid':
                return {'valid':self.lib.sqlite3_column_int(stmt,0)}
            column=2 if route == 'sqlite_json' else 1
            sqltype=self.lib.sqlite3_column_type(stmt,column)
            typetext=self.lib.sqlite3_column_text(stmt,column-1).decode()
            if sqltype not in (1,2):
                return {'error':'nonnumeric result','sql_type':typetext,'type_code':sqltype}
            bits=struct.pack('>d',self.lib.sqlite3_column_double(stmt,column)).hex()
            result={'bits':bits,'sql_type':typetext,'type_code':sqltype,'rc':rc}
            if route == 'sqlite_json':
                result['valid']=self.lib.sqlite3_column_int(stmt,0)
            return result
        finally:
            self.lib.sqlite3_reset(stmt)
            self.lib.sqlite3_clear_bindings(stmt)

    def close(self):
        for stmt in getattr(self,'statements',{}).values():self.lib.sqlite3_finalize(stmt)
        self.statements={}
        if getattr(self,'db',None):self.lib.sqlite3_close(self.db);self.db=None

def python_parse(token):
    try:return {'bits':struct.pack('>d',float(token)).hex()}
    except (ValueError,OverflowError) as exc:return {'error':type(exc).__name__+': '+str(exc)}

def controls(sqlite,sabotage=False):
    result={'oracle':calibrate(),
            'one':sqlite.query('sqlite_json','1e0'),
            'two':sqlite.query('sqlite_json','2e0'),
            'repeated_one':[sqlite.query('sqlite_json','1e0') for _ in range(3)],
            'malformed':[{'token':s,'validation':sqlite.query('valid',s),
                          'extraction':sqlite.query('sqlite_json',s)} for s in ('1e','-','01')]}
    if sabotage:result['one']['bits']='3ff0000000000001'
    return result

def control_gate(control):
    return (control['oracle']=={'rounding_cases':10,'invalid_oracle_cases':3}
            and control['one'].get('bits')=='3ff0000000000000'
            and control['two'].get('bits')=='4000000000000000'
            and all(x==control['repeated_one'][0] and x.get('bits')=='3ff0000000000000' for x in control['repeated_one'])
            and len(control['repeated_one'])==3
            and [x['token'] for x in control['malformed']]==['1e','-','01']
            and all(x['validation']=={'valid':0} and x['extraction'].get('rc')==1 and 'error' in x['extraction'] for x in control['malformed']))

def analyze(rows,control):
    generated=list(corpus())
    input_bytes=b''.join(canonical(row)+b'\n' for row in generated)
    if digest(input_bytes)!=CORPUS_SHA or len(rows)!=512:
        raise ValueError('frozen corpus identity/count mismatch')
    counts={route:Counter(pairs=512) for route in ROUTES}
    small_padding_ok=True
    all_json_numeric=True
    for row,expected_case in zip(rows,generated,strict=True):
        if row['case'] != expected_case:
            raise ValueError('case identity changed')
        exact=rational(expected_case['token'])
        if exact != rational(expected_case['baseline']):
            raise ValueError('unequal rational inputs')
        bits=expected_bits(exact)
        if row['expected_bits'] != bits:
            raise ValueError('stored exact-oracle value changed')
        for route in ROUTES:
            obs=row['observed'][route]
            baseline,transformed=obs['baseline'],obs['transformed']
            c=counts[route]
            c['errors']+=int('error' in baseline)+int('error' in transformed)
            if 'bits' in baseline and 'bits' in transformed:
                c['pair_disagreements']+=int(baseline['bits']!=transformed['bits'])
            c['baseline_oracle_mismatches']+=int(baseline.get('bits')!=bits)
            c['transformed_oracle_mismatches']+=int(transformed.get('bits')!=bits)
            if route.startswith('sqlite_') and expected_case['padding'] in (0,1):
                small_padding_ok &= baseline.get('bits')==bits and transformed.get('bits')==bits
        j=row['observed']['sqlite_json']['transformed']
        all_json_numeric &= j.get('valid')==1 and j.get('sql_type')=='real' and j.get('type_code')==2 and j.get('rc')==100
    unit={row['case']['family']:row for row in rows if row['case']['coefficient']==1 and row['case']['power']==0 and row['case']['sign']==1 and row['case']['padding']==100000}
    p2=True
    for family,wanted in [('integer_padding','7ff0000000000000'),('fraction_padding','0000000000000000')]:
        row=unit[family]
        for route in ('sqlite_json','sqlite_cast'):
            obs=row['observed'][route]
            p2 &= obs['baseline'].get('bits')=='3ff0000000000000' and obs['transformed'].get('bits')==wanted
        j=row['observed']['sqlite_json']['transformed']
        p2 &= j.get('valid')==1 and j.get('sql_type')=='real'
    held={
        'P1':counts['sqlite_json']['pair_disagreements']>=1,
        'P2':bool(p2),
        'P3':all(counts[r]['errors']==0 and counts[r]['baseline_oracle_mismatches']==0 and counts[r]['transformed_oracle_mismatches']==0 for r in ('python','javascript')),
        'P4':bool(control_gate(control) and small_padding_ok),
        'P5':bool(all_json_numeric),
    }
    keys=('pairs','errors','pair_disagreements','baseline_oracle_mismatches','transformed_oracle_mismatches')
    return {'counts':{route:{key:counts[route][key] for key in keys} for route in ROUTES},
            'outcomes':{p:'HELD' if value else 'REFUTED' for p,value in held.items()},
            'held':sum(held.values()),'predictions':5,'controls':control,'corpus_sha256':CORPUS_SHA}

def announce(summary):
    for key,outcome in summary['outcomes'].items():print(key+': '+outcome)
    print(f"VERDICT {summary['held']} of {summary['predictions']} as registered")
    print('DIGEST '+summary['digest'])
    print(json.dumps(summary['counts'],indent=2))
    print('SELF-TESTED; human look NOT PERFORMED; empirical validity NOT RUN; novelty UNRESOLVED')

def verify(directory):
    raw=gzip.decompress((directory/'observations.jsonl.gz').read_bytes())
    rows=[json.loads(line) for line in raw.decode().splitlines()]
    stored=json.loads((directory/'summary.json').read_text())
    control=json.loads((directory/'controls.json').read_text())
    computed=analyze(rows,control)
    computed['observations_sha256']=digest(raw)
    computed['digest']=digest(canonical(computed))
    if stored!=computed:raise ValueError('stored observations/summary do not agree')
    return computed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sqlite-lib',type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--verify',type=Path)
    parser.add_argument('--sabotage',action='store_true')
    args=parser.parse_args()
    try:
        if args.verify:
            summary=verify(args.verify)
            if args.sabotage:
                control=json.loads((args.verify/'controls.json').read_text())
                control['one']['bits']='3ff0000000000001'
                if control_gate(control):raise ValueError('sabotage escaped')
                print('GATE: FAIL planted unit-control mismatch');return 1
        else:
            if not args.sqlite_lib or not args.out:raise ValueError('library and new output directory required')
            if args.out.exists():raise ValueError('output directory already exists; refusing another subject run')
            sqlite=SQLite(args.sqlite_lib)
            try:
                control=controls(sqlite,args.sabotage)
                if not control_gate(control):
                    print('GATE: FAIL unit-control mismatch');return 1
                generated=list(corpus())
                node=json.loads(subprocess.run(['node',str(ROOT/'node_parse.mjs')],
                    input=json.dumps([{k:case[k] for k in ('id','baseline','token')} for case in generated]),text=True,capture_output=True,check=True,timeout=60).stdout)
                if len(node['rows'])!=len(generated):raise ValueError('JavaScript row count mismatch')
                rows=[]
                for case,js in zip(generated,node['rows'],strict=True):
                    if js['id']!=case['id']:raise ValueError('JavaScript identity mismatch')
                    observed={r:{'baseline':sqlite.query(r,case['baseline']),'transformed':sqlite.query(r,case['token'])} for r in ('sqlite_json','sqlite_cast')}
                    observed['python']={'baseline':python_parse(case['baseline']),'transformed':python_parse(case['token'])}
                    observed['javascript']={k:js[k] for k in ('baseline','transformed')}
                    rows.append({'case':case,'expected_bits':expected_bits(rational(case['baseline'])),'observed':observed})
                summary=analyze(rows,control)
                raw=b''.join(canonical(row)+b'\n' for row in rows)
                summary['observations_sha256']=digest(raw)
                summary['digest']=digest(canonical(summary))
                args.out.mkdir(parents=True,exist_ok=False)
                (args.out/'observations.jsonl.gz').write_bytes(gzip.compress(raw,mtime=0))
                (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
                (args.out/'controls.json').write_text(json.dumps(control,indent=2)+'\n')
                metadata={'registration':REGISTRATION,'executed_at_utc':datetime.now(timezone.utc).isoformat(),'sqlite_version':sqlite.version,'sqlite_sourceid':sqlite.sourceid,'library_sha256':digest(args.sqlite_lib.read_bytes()),'python':sys.version,'node':node['node'],'platform':platform.platform(),'source_sha256':{p.name:digest(p.read_bytes()) for p in (ROOT/'run.py',ROOT/'cases.py',ROOT/'node_parse.mjs')}}
                (args.out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
            finally:sqlite.close()
        if not summary['outcomes']['P4']=='HELD':raise ValueError('instrument controls failed')
        recorded=ROOT/'RECORDED.json'
        if recorded.exists():
            pin=json.loads(recorded.read_text())
            if pin!={'outcomes':summary['outcomes'],'digest':summary['digest']}:
                raise ValueError('pinned deterministic outcome changed')
        announce(summary)
        print('GATE: PASS instrument consistency only')
        return 0
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
        print('GATE: FAIL '+str(exc));return 1

if __name__=='__main__':sys.exit(main())
