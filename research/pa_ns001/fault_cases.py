"""Deterministic public engineering fixtures; intentionally no ns001 import."""
from fractions import Fraction
import hashlib
import json

from analytic_oracle import characteristic, exact_samples

SEED = 'PA-NS-001:STAGE2:ENGINEERING:2026-10-20:v1'
FAULTS = ('correct', 'wall_shift', 'sign_reversal', 'gradient_sign',
          'viscosity_mismatch', 'joint_gradient_viscosity_scale', 'interior_spike',
          'nonfinite', 'nonuniform_grid', 'rounding_only', 'coarse_linear_interpolant',
          'missing_endpoint', 'boolean_sample', 'stopped_flow')


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def cases():
    for family in ('couette', 'poiseuille'):
        for scenario, params in (
                ('unit', dict(h='1', U='1', mu='1', G='2')),
                ('small_velocity', dict(h='1', U='1e-8', mu='1', G='8e-8'))):
            for n in (21, 65):
                original = exact_samples(family, params, n)
                amplitude = characteristic(family, params)
                for fault in FAULTS:
                    identity = f'{family}/{scenario}/n{n}/{fault}'
                    entropy = hashlib.sha256((SEED+'|'+identity).encode()).digest()
                    index = 1 + int.from_bytes(entropy[:4], 'big') % (n-2)
                    samples = list(original)
                    generating = dict(params)
                    error = Fraction(0)
                    expected = 'REJECTED'
                    indistinguishable = False
                    if fault == 'correct':
                        expected = 'ACCEPTED'
                    elif fault == 'wall_shift':
                        samples = [v + amplitude/10 for v in samples]
                    elif fault == 'sign_reversal':
                        samples = [-v for v in samples]
                    elif fault in ('gradient_sign', 'viscosity_mismatch', 'joint_gradient_viscosity_scale'):
                        if fault == 'gradient_sign':
                            generating['G'] = str(-Fraction(params['G']))
                        else:
                            generating['mu'] = str(2*Fraction(params['mu']))
                            if fault == 'joint_gradient_viscosity_scale':
                                generating['G'] = str(2*Fraction(params['G']))
                        samples = exact_samples(family, generating, n)
                        indistinguishable = samples == original
                        expected = 'ACCEPTED' if indistinguishable else 'REJECTED'
                    elif fault == 'interior_spike':
                        samples[index] += amplitude * Fraction(10 + entropy[4] % 5, 200)
                    elif fault == 'nonfinite':
                        samples[index] = {'special': 'nan'}
                    elif fault == 'nonuniform_grid':
                        from analytic_oracle import polynomial
                        a, b, c = polynomial(family, params)
                        height = Fraction(params['h'])
                        samples = [a*y*y+b*y+c for y in (height*Fraction(i, n-1)**2 for i in range(n))]
                    elif fault == 'rounding_only':
                        lattice = 10**10
                        samples = [amplitude * Fraction(round(v/amplitude*lattice), lattice) for v in samples]
                        error = abs(amplitude) / (2*lattice)
                        expected = 'ACCEPTED'
                    elif fault == 'coarse_linear_interpolant':
                        # Linear interpolation through analytic values at eta=0,1/2,1.
                        midpoint, last = original[(n-1)//2], original[-1]
                        samples = [(2*Fraction(i, n-1)*midpoint if 2*i <= n-1
                                    else midpoint + (2*Fraction(i, n-1)-1)*(last-midpoint))
                                   for i in range(n)]
                        indistinguishable = samples == original
                        expected = 'ACCEPTED' if indistinguishable else 'REJECTED'
                    elif fault == 'missing_endpoint':
                        samples.pop()
                    elif fault == 'boolean_sample':
                        samples[0] = False
                    elif fault == 'stopped_flow':
                        samples = [Fraction(0)] * n
                    finite_exact = (len(samples) == len(original)
                                    and all(type(v) is Fraction for v in samples))
                    facts = {'indistinguishable': indistinguishable, 'generating_parameters': generating}
                    if finite_exact:
                        maximum = max(abs(a-b)/abs(amplitude) for a, b in zip(samples, original))
                        facts['exact_normalized_profile_difference'] = str(maximum)
                        if expected == 'REJECTED' and maximum == 0:
                            raise RuntimeError('invalid fixture lacks a mathematical discrepancy')
                    values = [float(v) if type(v) is Fraction else v for v in samples]
                    row = {'id': identity, 'family': family, 'fault': fault, 'parameters': params,
                           'n_declared': n, 'values': values, 'sample_error_bound': float(error),
                           'expected_status': expected, 'construction_facts': facts,
                           'seed': SEED, 'entropy_sha256': entropy.hex(),
                           'classification': 'public synthetic engineering fixture; not held-out study data'}
                    row['case_sha256'] = hashlib.sha256(canonical(row)).hexdigest()
                    yield row
    for family in ('couette', 'poiseuille'):
        params = dict(h='1', U='0', mu='1', G='0')
        row = {'id': f'{family}/zero_drive/sign_reversal', 'family': family,
               'fault': 'zero_drive_sign_reversal', 'parameters': params, 'n_declared': 21,
               'values': [-0.0]*21, 'sample_error_bound': 0.0, 'expected_status': 'ACCEPTED',
               'construction_facts': {'indistinguishable': True}, 'seed': SEED,
               'classification': 'public synthetic engineering fixture; not held-out study data'}
        row['case_sha256'] = hashlib.sha256(canonical(row)).hexdigest()
        yield row


def decode_values(row):
    return [float('nan') if type(v) is dict and v == {'special': 'nan'} else v
            for v in row['values']]
