# D1 public differential check

**Overall FAIL against the registered pointwise criteria.** All 128 random constructions matched their analytic totals, components and flags in both coordinates. Both deliberately incorrect controls were detected on all 128 resolved originals. Failures were concentrated at numerical boundaries in this seed and environment.

| Stratum | Points including coordinate changes | Failed points |
|---|---:|---:|
| Random | 256 | 0 |
| Support cutoff | 12 | 4 |
| Gap thresholds | 24 | 1 |
| Public kernel cases | 8 | 2 |

A failed point has at least one registered disagreement. The two coordinates are paired observations. At the exact nominal support cutoff a commuting derivative acquired D1 rotation 0.999791 after conjugation. The reference returned effectively zero. At 1.01 times the cutoff the same construction gave a negative D1 rotation (−0.000164849); the reference classical value also missed the analytic construction target. At the nominal gap threshold of 1e-6, both flags changed after conjugation. At 1e-12 the diagnostic components exchanged roles while the split remained withheld. The unequal-small original has reference bookkeeping residual 0.1. Subtracting to get D1 rotation enforces bookkeeping by construction and supplies no independent check of that identity.

Analytic expectations describe the construction before float64 representation and unitary conjugation. The rounded matrices can lie on either side of a hard cutoff. This run measures end-to-end numerical sensitivity and does not assign every discrepancy to an implementation error. Only public synthetic states were used. Both implementations use NumPy eigensolvers; the reference and public cases were visible before registration. Q3 activation interchange awaits a pinned producer artifact.

## Replay

Registration 69e790f5db392b3ed805e96e85ef3792237fdf24, implementation 988a6d0d433f4ac309339cbf8e1b3a4758f99f15, public reference and runner bc9930daf9943eb6d7fa5d50801b489628e5efbb. Run in experiments/qfi_001 with Python 3.12.14 and NumPy 2.3.5.

```sh
export OPENBLAS_NUM_THREADS=1
python d1_check.py
for cases in cases/public.jsonl cases/d1_replay.jsonl; do
  for impl in qfi_ref d1_sld; do
    python run_cases.py "$cases" --impl "$impl"
  done
done
```

D1_RUN.txt contains the first run, including exact-boundary spectra before and after conjugation and the worst normalized error. The registered comparison uses mixed absolute and relative tolerance. The two JSONL readers use the same per-row absolute tolerance (default 1e-10). Each reader evaluated 27 expectations on the eight original rows and 22 on the seven selected replay rows per implementation. Both readers passed all eight originals for both implementations. Replay failed on three rows for the reference and four for D1. The unequal-small original does not assert a rotation value in either JSONL suite; its inter-implementation disagreement is checked directly by the differential harness. Failure exits are expected and preserved.

Next check: replay the saved commuting cutoff pair in a second numerical environment and record both state and SLD-operator eigenvalues relative to their support masks before proposing a change.
