"""Reproduce limitations of the unmodified, source-pinned initial verifier."""
import importlib.util
import json
from pathlib import Path


def main():
    path = Path(__file__).parent / 'evidence/stage2/baseline/original_ns001.py'
    spec = importlib.util.spec_from_file_location('original_ns001', path)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    rows = []

    def capture(case, operation):
        try:
            result = operation()
            rows.append({'case': case, 'result': result})
        except Exception as exc:
            rows.append({'case': case, 'exception': type(exc).__name__, 'message': str(exc)})

    valid = [old.reference('couette', i / 20) for i in range(21)]
    capture('incorrect_zero_profile_infinite_tolerance',
            lambda: old.verify('couette', [0.0] * 21, tolerance=float('inf')))
    capture('boolean_samples', lambda: old.verify('couette', [False] * 20 + [True]))
    capture('string_samples', lambda: old.verify('couette', ['0'] * 21))
    capture('nan_tolerance', lambda: old.verify('couette', valid, tolerance=float('nan')))
    capture('unknown_flow_and_nonfinite_data',
            lambda: old.verify('unknown', [float('nan')] * 21))
    capture('underflow_grid_spacing', lambda: old.verify('couette', valid, h=1e-200))
    capture('tiny_valid_flow_replaced_by_zero',
            lambda: old.verify('couette', [0.0] * 21, U=1e-12))
    for n in (21, 257, 1025, 4097):
        capture(f'correct_poiseuille_n{n}',
                lambda n=n: old.verify('poiseuille', [old.reference('poiseuille', i/(n-1)) for i in range(n)]))
        capture(f'rounded_correct_poiseuille_n{n}',
                lambda n=n: old.verify('poiseuille', [round(old.reference('poiseuille', i/(n-1)), 6) for i in range(n)]))
    for row in rows:
        print(json.dumps(row, sort_keys=True, allow_nan=False))
    print('DIAGNOSTIC ONLY: observations are limitations of the original software, not AI findings.')


if __name__ == '__main__':
    main()
