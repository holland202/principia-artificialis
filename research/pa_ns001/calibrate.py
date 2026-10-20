"""Fixed-matrix engineering calibration; no AI or held-out challenges."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics

from analytic_oracle import characteristic, exact_samples
from ns001 import verify

GRIDS = (5, 21, 65, 257, 1025)
SCENARIOS = {
    'unit': dict(h='1', U='1', mu='1', G='2'),
    'small_velocity': dict(h='1', U='1e-8', mu='1', G='8e-8'),
    'large_velocity': dict(h='1', U='1e6', mu='1', G='8e6'),
    'short_channel': dict(h='1e-6', U='2', mu='1e-3', G='8e9'),
    'long_channel': dict(h='1e6', U='2', mu='1e3', G='8e-9'),
    'reverse': dict(h='0.5', U='-3', mu='0.25', G='-24'),
}


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def load_original():
    path = Path(__file__).parent / 'evidence/stage2/baseline/original_ns001.py'
    spec = importlib.util.spec_from_file_location('original_ns001', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rendered_samples(exact, amplitude, rendering):
    if rendering == 'binary64':
        return [float(v) for v in exact], 0.0
    if rendering.startswith('physical_decimal_'):
        places = int(rendering.rsplit('_', 1)[1])
        lattice = 10**places
        return [float(Fraction(round(v*lattice), lattice)) for v in exact], float(Fraction(1, 2*lattice))
    if rendering == 'normalized_decimal_10':
        lattice = 10**10
        return [float(amplitude*Fraction(round(v/amplitude*lattice), lattice)) for v in exact], float(abs(amplitude) / (2*lattice))
    raise ValueError('unknown rendering')


def matrix_rows():
    old = load_original()
    for family in ('couette', 'poiseuille'):
        for scenario, parameters in SCENARIOS.items():
            kwargs = {k: float(v) for k, v in parameters.items()}
            for n in GRIDS:
                exact = exact_samples(family, parameters, n)
                amplitude = characteristic(family, parameters)
                for rendering in ('binary64', 'physical_decimal_10', 'physical_decimal_6', 'normalized_decimal_10'):
                    values, error = rendered_samples(exact, amplitude, rendering)
                    current = verify(family, values, sample_error_bound=error, **kwargs)
                    legacy = old.verify(family, values, **kwargs)
                    normalized = [Fraction.from_float(v)/amplitude for v in values]
                    curvature = 0 if family == 'couette' else -8
                    r = max(abs((normalized[i+1]-2*normalized[i]+normalized[i-1])*(n-1)**2-curvature)
                            for i in range(1, n-1))
                    profile = max(abs(Fraction.from_float(v)-t)/abs(amplitude) for v, t in zip(values, exact))
                    yield {'id': f'{family}/{scenario}/n{n}/{rendering}', 'family': family,
                           'scenario': scenario, 'n': n, 'parameters': parameters, 'rendering': rendering,
                           'sample_error_bound': error, 'analytic_normalized_profile_error': float(profile),
                           'analytic_normalized_momentum_residual': float(r),
                           'original': legacy, 'current': current}


def summarize(rows):
    groups = {}
    for n in GRIDS:
        residuals = sorted(r['analytic_normalized_momentum_residual'] for r in rows if r['n'] == n)
        groups[str(n)] = {'count': len(residuals), 'min': residuals[0],
                          'median': statistics.median(residuals),
                          'p95_nearest_rank': residuals[math.ceil(.95*len(residuals))-1],
                          'max': residuals[-1]}
    return {'cases': len(rows), 'original_accepted': sum(r['original']['accepted'] for r in rows),
            'current_accepted': sum(r['current']['accepted'] for r in rows),
            'current_rejected': sum(r['current']['status'] == 'REJECTED' for r in rows),
            'current_unresolvable': sum(r['current']['status'] == 'UNRESOLVABLE' for r in rows),
            'unrounded_current_accepted': sum(r['current']['accepted'] for r in rows if r['rendering'] == 'binary64'),
            'unrounded_cases': sum(r['rendering'] == 'binary64' for r in rows),
            'residual_by_grid': groups,
            'classification': 'descriptive fixed engineering matrix; not population estimates or AI results'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sabotage', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    rows = list(matrix_rows())
    digest = hashlib.sha256(canonical(rows)).hexdigest()
    (args.output/'cases.jsonl').write_bytes(b''.join(canonical(r)+b'\n' for r in rows))
    summary = summarize(rows)
    summary['digest'] = digest
    (args.output/'summary.json').write_text(json.dumps(summary, sort_keys=True, indent=2)+'\n')
    print(json.dumps(summary, sort_keys=True, indent=2))
    ok = (len(rows) == 240 and summary['unrounded_current_accepted'] == 60
          and summary['current_rejected'] == 0 and not args.sabotage)
    print('P3: '+('HELD' if ok else 'IMPLEMENTATION_ERROR'))
    print('DIGEST '+digest)
    print('GATE: '+('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
