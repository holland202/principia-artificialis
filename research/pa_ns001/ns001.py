"""Bounded analytic channel-profile checker, not a general CFD or AI verifier.

Numerical policy v1 is proposed engineering policy, fixed in CALIBRATION_PLAN.md.
All acceptance comparisons and second differences use exact rationals representing
the supplied binary64 values. Input/reference rounding remains explicitly bounded.
"""
from fractions import Fraction
import math
import sys

POLICY = 'pa-ns001-engineering-v1'
MAX_SAMPLES = 4097
MAX_TOLERANCE = Fraction(1, 10_000)
MAX_SAMPLE_ERROR = Fraction(1, 1_000_000)
MAX_MOMENTUM_ALLOWANCE = Fraction(1, 100)
ROUNDING_FLOOR = 16 * Fraction.from_float(sys.float_info.epsilon)


def _number(value, name):
    if type(value) not in (int, float):
        raise ValueError(f'{name} must be a finite int or float, excluding bool')
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f'{name} is outside binary64 range') from exc
    if not math.isfinite(value):
        raise ValueError(f'{name} must be finite')
    return Fraction.from_float(value)


def _parameters(kind, h, U, mu, G):
    if type(kind) is not str or kind not in ('couette', 'poiseuille'):
        raise ValueError('unknown flow family')
    h, U, mu, G = (_number(v, name) for v, name in
                    ((h, 'h'), (U, 'U'), (mu, 'mu'), (G, 'G')))
    if h <= 0 or mu <= 0:
        raise ValueError('h and mu must be positive')
    amplitude = U if kind == 'couette' else G * h * h / (8 * mu)
    if amplitude and not (Fraction.from_float(sys.float_info.min) <= abs(amplitude)
                          <= Fraction.from_float(sys.float_info.max)):
        raise ValueError('nonzero characteristic velocity must be a normal finite binary64')
    return h, amplitude


def reference(kind, y, h=1.0, U=1.0, mu=1.0, G=2.0):
    """Analytic velocity at 0 <= y <= h; signed drive permits reversed flow.

    U is active only for Couette, G only for Poiseuille. Couette is insensitive
    to mu; Poiseuille identifies G/mu, not either parameter separately.
    """
    height, amplitude = _parameters(kind, h, U, mu, G)
    position = _number(y, 'y')
    if not 0 <= position <= height:
        raise ValueError('y must lie between the channel walls')
    eta = position / height
    shape = eta if kind == 'couette' else 4 * eta * (1 - eta)
    return float(amplitude * shape)


def _deny(reason, status='REJECTED', **metrics):
    return {'accepted': False, 'status': status, 'reason': reason,
            'policy': POLICY, **metrics}


def _finite_metric(value):
    # Extreme finite configuration can give an unrepresentable *ratio*. The
    # verdict remains UNRESOLVABLE; reporting it must not raise OverflowError.
    try:
        result = float(value)
    except OverflowError:
        return None
    return result if math.isfinite(result) else None


def verify(kind, values, *, h=1.0, U=1.0, mu=1.0, G=2.0,
           tolerance=1e-9, sample_error_bound=0.0):
    """Check wall-inclusive, equally spaced samples against a specified solution.

    Configuration is trusted experiment input: invalid configuration raises
    ValueError. Malformed candidate data never produces acceptance. A declared
    physical-velocity rounding bound must be fixed by the protocol, not chosen
    by an AI response. UNRESOLVABLE is not mathematical invalidity.
    """
    _, amplitude = _parameters(kind, h, U, mu, G)
    tol = _number(tolerance, 'tolerance')
    sample_error = _number(sample_error_bound, 'sample_error_bound')
    if not 0 < tol <= MAX_TOLERANCE or sample_error < 0:
        raise ValueError('tolerance must be in (0, 1e-4]; sample error must be nonnegative')
    if type(values) not in (list, tuple) or not 5 <= len(values) <= MAX_SAMPLES:
        return _deny('invalid_sample_container_or_count')
    if any(type(v) not in (int, float) for v in values):
        return _deny('invalid_sample_type')
    try:
        samples = [_number(v, 'sample') for v in values]
    except ValueError:
        return _deny('nonfinite_or_out_of_range_sample')
    if not amplitude:
        if sample_error:
            return _deny('zero_drive_requires_exact_zero_precision', 'UNRESOLVABLE')
        if any(samples):
            return _deny('nonzero_velocity_with_zero_drive')
        return {'accepted': True, 'status': 'ACCEPTED', 'policy': POLICY,
                'profile_error': 0.0, 'boundary_error': 0.0, 'momentum_residual': 0.0,
                'profile_limit': 0.0, 'momentum_limit': 0.0,
                'gates': {'profile': True, 'boundary': True, 'momentum': True}}
    normalized_error = sample_error / abs(amplitude)
    normalized = [v / amplitude for v in samples]
    if any(abs(v) > 1_000_000 for v in normalized):
        return _deny('candidate_velocity_out_of_supported_normalized_range')
    intervals = len(samples) - 1
    error_budget = normalized_error + ROUNDING_FLOOR
    profile_limit = tol + error_budget
    momentum_limit = tol + 4 * error_budget * intervals**2
    if normalized_error > MAX_SAMPLE_ERROR or momentum_limit > MAX_MOMENTUM_ALLOWANCE:
        return _deny('precision_insufficient', 'UNRESOLVABLE',
                     profile_limit=_finite_metric(profile_limit),
                     momentum_limit=_finite_metric(momentum_limit))
    target = [Fraction(i, intervals) if kind == 'couette'
              else Fraction(4 * i * (intervals-i), intervals**2)
              for i in range(len(samples))]
    profile = max(abs(a-b) for a, b in zip(normalized, target))
    boundary = max(abs(normalized[0]-target[0]), abs(normalized[-1]-target[-1]))
    rhs = 0 if kind == 'couette' else -8
    residual = max(abs((normalized[i+1] - 2*normalized[i] + normalized[i-1])
                       * intervals**2 - rhs) for i in range(1, intervals))
    gates = {'profile': profile <= profile_limit,
             'boundary': boundary <= profile_limit,
             'momentum': residual <= momentum_limit}
    accepted = gates['profile'] and gates['boundary'] and gates['momentum']
    return {'accepted': accepted, 'status': 'ACCEPTED' if accepted else 'REJECTED',
            'policy': POLICY, 'gates': gates,
            'profile_error': float(profile), 'boundary_error': float(boundary),
            'momentum_residual': float(residual), 'profile_limit': _finite_metric(profile_limit),
            'momentum_limit': _finite_metric(momentum_limit)}
