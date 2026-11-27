"""Run from this directory: python d1_check.py. Outputs public replay cases and diagnostics."""
import json
import platform
from collections import Counter
from pathlib import Path

import numpy as np

import d1_sld
import qfi_ref

FIELDS = ("F_Q", "F_C", "F_R", "split_resolved")
rng = np.random.default_rng(260115)


def matrix(value):
    if set(value) - {"re", "im"}:
        raise ValueError("unknown matrix field")
    real = np.asarray(value["re"], dtype=float)
    imag = np.asarray(value.get("im", np.zeros_like(real)), dtype=float)
    if real.ndim != 2 or not len(real) or real.shape != real.T.shape or real.shape != imag.shape:
        raise ValueError("bad matrix shape")
    result = real + 1j * imag
    if not np.isfinite(result).all() or not np.allclose(result, result.conj().T, atol=1e-13, rtol=0):
        raise ValueError("expected finite Hermitian matrix")
    return result


def pack(value):
    return dict(re=value.real.tolist(), im=value.imag.tolist())


def read_cases(path):
    seen = set()
    for line in Path(path).read_text().splitlines():
        row = json.loads(line)
        name, expected = row["id"], row["expect"]
        if not isinstance(name, str) or not name or name in seen or not row["source"]:
            raise ValueError("missing or repeated case identifier")
        seen.add(name)
        if not expected or set(expected) - set((*FIELDS, "bookkeeping")):
            raise ValueError("invalid expectations")
        for key, value in expected.items():
            if key in ("split_resolved", "bookkeeping"):
                if type(value) is not bool or (key == "bookkeeping" and not value):
                    raise ValueError("invalid Boolean assertion")
            elif type(value) not in (int, float) or not np.isfinite(value):
                raise ValueError("invalid scalar assertion")
        tol = row.get("tol", 1e-10)
        if not np.isfinite(tol) or tol <= 0:
            raise ValueError("invalid tolerance")
        rho, drho = matrix(row["rho"]), matrix(row["drho"])
        if rho.shape != drho.shape:
            raise ValueError("incompatible derivative")
        yield row, rho, drho
    if not seen:
        raise ValueError("empty file")


def replay(path, impl):
    counts, failures = Counter(), []
    for row, rho, drho in read_cases(path):
        values = impl.qfi_split_ex(rho, drho)
        for key, expected in row["expect"].items():
            counts[key] += 1
            if key == "split_resolved":
                ok = values[key] is expected
            else:
                diff = (values["F_Q"] - values["F_C"] - values["F_R"]
                        if key == "bookkeeping" else values[key] - expected)
                ok = abs(diff) < row.get("tol", 1e-10)
            if not ok:
                failures.append([row["id"], key])
    print("reader", path, impl.__name__, dict(counts), "failures", failures)
    return not failures


def unitary(d):
    q, r = np.linalg.qr(rng.normal(size=(d,d)) + 1j*rng.normal(size=(d,d)))
    diagonal = np.diag(r)
    return q * (diagonal/abs(diagonal))


def trials():
    for d in (2, 3, 4, 6):
        for i in range(32):
            p = rng.exponential(size=d)
            p /= p.sum()
            v = rng.normal(size=d)
            v -= v.mean()
            z = rng.normal(size=(d,d)) + 1j*rng.normal(size=(d,d))
            k = (z-z.conj().T)/2
            off = k * (p[None,:]-p[:,None])
            fc = np.sum(v*v/p)
            fr = np.sum(2*abs(off)**2/(p[:,None]+p[None,:]))
            yield "random", f"d{d}-{i}", np.diag(p), np.diag(v)+off, dict(zip(FIELDS,(fc+fr,fc,fr,bool(np.min(np.diff(np.sort(p)))>1e-6))))
    for scale in (0.5,0.99,1,1.01,1.5,2):
        p = scale*5e-13
        fc = float(p/(1-p) + (scale>1))
        yield "support", str(scale), np.diag([p,1-p]), np.diag([np.sqrt(p),-np.sqrt(p)]), dict(zip(FIELDS,(fc,fc,0.,True)))
    for threshold in (1e-12,1e-6):
        for scale in (0,0.5,0.99,1,1.01,2):
            gap = scale*threshold
            yield "gap", f"{threshold}-{scale}", np.diag([.5-gap/2,.5+gap/2]), np.array([[0.,.1],[.1,0.]]), dict(F_Q=.04,split_resolved=bool(gap>1e-6))
    for row, rho, drho in read_cases("cases/public.jsonl"):
        if row["id"].startswith("P014"):
            expected = {k:v for k,v in row["expect"].items() if k in FIELDS}
            expected["split_resolved"] = False
            yield "kernel", row["id"], rho, drho, expected


def error(a,b,key):
    if key == "split_resolved":
        return 0. if a is b else 2.
    return float(abs(a-b)/(1e-9+1e-7*max(abs(a),abs(b)))) if np.isfinite([a,b]).all() else float("inf")


def main():
    counts, failed, controls = Counter(), Counter(), Counter()
    worst, examples, saved = (-1,None), {}, {}
    max_residual = {}
    resolved = 0
    print("Python", platform.python_version(), "NumPy", np.__version__)
    for group, name, state, derivative, expected in trials():
        u = unitary(len(state))
        for basis, rho, drho in (("original",state,derivative),("rotated",u@state@u.conj().T,u@derivative@u.conj().T)):
            case = f"{group}-{name}-{basis}"
            row = dict(id=case,source="D1 public analytic construction",rho=pack(rho),drho=pack(drho),expect=expected)
            ref = qfi_ref.qfi_split_ex(rho,drho)
            cand = d1_sld.qfi_split_ex(rho,drho)
            residual = abs(ref["F_Q"]-ref["F_C"]-ref["F_R"])
            max_residual[group] = max(max_residual.get(group,0.),residual)
            counts[group] += 1
            bad = False
            for label, a, b in (("candidate/analytic",cand,expected),("reference/analytic",ref,expected),("candidate/reference",cand,{k:ref[k] for k in FIELDS})):
                for key in b:
                    score = error(a[key],b[key],key)
                    if score>worst[0]:
                        worst = score,(case,label,key,row)
                    if score>1:
                        tag = "/".join((group,basis,label,key))
                        examples.setdefault(tag,(row,a[key],b[key]))
                        bad = True
            failed[group] += bad
            if group=="random" and basis=="original" and expected["split_resolved"]:
                resolved += 1
                controls["double"] += error(2*cand["F_Q"],expected["F_Q"],"F_Q")>1
                controls["flag"] += error(False,expected["split_resolved"],"split_resolved")>1
            if group=="random" and name=="d2-0":
                saved[case]=row
            if (group=="support" and name=="1") or (group=="gap" and name.endswith("-1")):
                print("boundary",case,np.linalg.eigvalsh(rho).tolist(),{k:ref[k] for k in FIELDS},cand)
    for label,(row,actual,goal) in sorted(examples.items()):
        print("disagreement",label,row["id"],float(actual),float(goal))
        saved[row["id"]]=row
    case,label,key,row = worst[1]
    saved[case]=row
    print("worst normalized error",worst[0],case,label,key)
    print("point counts",dict(counts),"failed points",dict(failed),"max reference bookkeeping residual",max_residual)
    print("resolved originals",resolved,"controls detected",dict(controls))
    output = Path("cases/d1_replay.jsonl")
    output.write_text("".join(json.dumps(row,allow_nan=False)+"\n" for row in saved.values()))
    valid = resolved>=100 and min(controls.values())==resolved and dict(counts)==dict(random=256,support=12,gap=24,kernel=8)
    for path in ("cases/public.jsonl",output):
        for impl in (qfi_ref,d1_sld):
            valid = replay(path,impl) and valid
    return 0 if valid and not sum(failed.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
