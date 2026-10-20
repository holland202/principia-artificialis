"""Behavioral, mathematical and negative controls for the bounded Stage 2 build."""
from fractions import Fraction
import hashlib
import json
import math
import unittest

from analytic_oracle import characteristic, construction_is_identical, exact_samples, polynomial
from evaluate_faults import evaluate
from fault_cases import canonical, cases
from ns001 import reference, verify

UNIT = dict(h='1', U='1', mu='1', G='2')


def profile(family='couette', n=21, params=None):
    return [float(x) for x in exact_samples(family, params or UNIT, n)]


class TestStage2(unittest.TestCase):
    def test_hand_derived_five_point_vectors(self):
        self.assertEqual([reference('couette', i/4) for i in range(5)], [0, .25, .5, .75, 1])
        self.assertEqual([reference('poiseuille', i/4) for i in range(5)], [0, .1875, .25, .1875, 0])
        self.assertTrue(verify('poiseuille', [0, .1875, .25, .1875, 0])['accepted'])

    def test_polynomial_satisfies_ode_and_walls_exactly(self):
        parameters = dict(h='3/7', U='-11/5', mu='2/3', G='-7/4')
        for family in ('couette', 'poiseuille'):
            a, b, c = polynomial(family, parameters)
            h = Fraction(parameters['h'])
            self.assertEqual(c, 0)
            self.assertEqual(a*h*h+b*h+c, Fraction(parameters['U']) if family == 'couette' else 0)
            self.assertEqual(2*a, 0 if family == 'couette' else -Fraction(parameters['G'])/Fraction(parameters['mu']))
            values = exact_samples(family, parameters, 33)
            dy = h/32
            for i in range(1, 32):
                self.assertEqual((values[i+1]-2*values[i]+values[i-1])/dy**2, 2*a)

    def test_nonidentifiable_parameters(self):
        changed = dict(UNIT, mu='2')
        self.assertTrue(construction_is_identical('couette', UNIT, changed))
        self.assertFalse(construction_is_identical('poiseuille', UNIT, changed))
        self.assertTrue(construction_is_identical('poiseuille', UNIT, dict(UNIT, mu='2', G='4')))

    def test_signed_and_zero_drives(self):
        for family in ('couette', 'poiseuille'):
            params = dict(UNIT, U='-3', G='-6')
            kwargs = {k: float(v) for k, v in params.items()}
            self.assertTrue(verify(family, profile(family, params=params), **kwargs)['accepted'])
            self.assertTrue(verify(family, [0.0]*21, U=0, G=0)['accepted'])
            self.assertFalse(verify(family, [1e-100]*21, U=0, G=0)['accepted'])
            self.assertEqual(verify(family, [0.0]*21, U=0, G=0, sample_error_bound=1e-12)['status'], 'UNRESOLVABLE')

    def test_invalid_parameters_and_tolerances_raise(self):
        for key in ('h', 'mu', 'U', 'G', 'tolerance', 'sample_error_bound'):
            for bad in (math.nan, math.inf, -math.inf, True, '1', None, 1+0j, 10**1000):
                with self.subTest(key=key, value_type=type(bad).__name__):
                    with self.assertRaises(ValueError):
                        verify('couette', profile(), **{key: bad})
        for config in (dict(h=0), dict(h=-1), dict(mu=0), dict(mu=-1),
                       dict(tolerance=0), dict(tolerance=-1), dict(tolerance=.001),
                       dict(sample_error_bound=-1)):
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    verify('couette', profile(), **config)

    def test_configuration_checked_before_candidate_data(self):
        for family in ('wrong', None, True, {}):
            with self.assertRaises(ValueError):
                verify(family, [math.nan]*21)
        with self.assertRaises(ValueError):
            verify('couette', None, h=-1)

    def test_malformed_candidate_containers_fail_closed(self):
        for values in (None, [], [0]*4, [0]*4098, '', '0'*21, {}, iter([0]*21)):
            with self.subTest(container_type=type(values).__name__):
                self.assertFalse(verify('couette', values)['accepted'])
        self.assertTrue(verify('couette', tuple(profile()))['accepted'])

    def test_malformed_samples_fail_closed(self):
        for bad in (math.nan, math.inf, -math.inf, None, '0', False, {}, 1j, 10**1000):
            data = profile()
            data[0] = bad
            self.assertFalse(verify('couette', data)['accepted'])

    def test_reference_domain_and_types(self):
        for y in (-.1, 1.1, math.inf, math.nan, True, '0.5'):
            with self.assertRaises(ValueError):
                reference('couette', y)
        with self.assertRaises(ValueError):
            reference('unknown', .5)

    def test_characteristic_range_is_explicit(self):
        for kwargs in (dict(U=5e-324), dict(h=1e300, G=1e300), dict(h=1e-300, G=1e-300)):
            family = 'couette' if 'U' in kwargs else 'poiseuille'
            with self.assertRaises(ValueError):
                verify(family, profile(family), **kwargs)
        # Previously dy**2 underflowed here; no physical finite differences now.
        self.assertTrue(verify('couette', profile(), h=1e-200)['accepted'])

    def test_dimensional_scale_changes_do_not_hide_stopped_flow(self):
        for speed in (1e-100, 1e-12, 1, 1e100):
            good = [speed*i/20 for i in range(21)]
            self.assertTrue(verify('couette', good, U=speed)['accepted'])
            self.assertFalse(verify('couette', [0.0]*21, U=speed)['accepted'])

    def test_nonbinary_and_maximum_grids(self):
        for n in (101, 1001, 4097):
            for family in ('couette', 'poiseuille'):
                self.assertTrue(verify(family, profile(family, n))['accepted'])

    def test_legitimate_rounded_profile_with_declared_precision(self):
        amplitude = float(characteristic('poiseuille', UNIT))
        values = [amplitude*round(v/amplitude, 6) for v in profile('poiseuille', 65)]
        self.assertFalse(verify('poiseuille', values)['accepted'])
        self.assertTrue(verify('poiseuille', values, sample_error_bound=amplitude*5e-7)['accepted'])

    def test_unresolvable_precision_is_visible_and_not_accepted(self):
        values = [round(v, 6) for v in profile('poiseuille', 1025)]
        result = verify('poiseuille', values, sample_error_bound=5e-7)
        self.assertFalse(result['accepted'])
        self.assertEqual(result['status'], 'UNRESOLVABLE')
        self.assertGreater(result['momentum_limit'], .01)
        self.assertEqual(verify('couette', profile(), sample_error_bound=.01)['status'], 'UNRESOLVABLE')

    def test_extreme_finite_rounding_budget_does_not_crash_reporting(self):
        result = verify('couette', [1e-300*i/20 for i in range(21)],
                        U=1e-300, sample_error_bound=1e300)
        self.assertFalse(result['accepted'])
        self.assertEqual(result['status'], 'UNRESOLVABLE')
        self.assertIsNone(result['momentum_limit'])

    def test_profile_guard_has_a_reachable_unique_failure(self):
        n = 257
        values = [i/(n-1) + 1e-6*(i/(n-1))*(1-i/(n-1)) for i in range(n)]
        result = verify('couette', values, sample_error_bound=5e-11)
        self.assertTrue(result['gates']['boundary'])
        self.assertTrue(result['gates']['momentum'])
        self.assertFalse(result['gates']['profile'])
        self.assertFalse(result['accepted'])

    def test_momentum_guard_has_a_reachable_unique_failure(self):
        n = 1025
        values = [i/(n-1) + (2e-10*(-1)**i if 0 < i < n-1 else 0) for i in range(n)]
        result = verify('couette', values)
        self.assertTrue(result['gates']['profile'])
        self.assertTrue(result['gates']['boundary'])
        self.assertFalse(result['gates']['momentum'])
        self.assertFalse(result['accepted'])

    def test_wall_shift_has_zero_curvature_but_wrong_boundaries(self):
        result = verify('couette', [x+.125 for x in profile()])
        self.assertTrue(result['gates']['momentum'])
        self.assertFalse(result['gates']['boundary'])
        self.assertFalse(result['accepted'])

    def test_all_constructed_fixtures_match_separate_labels(self):
        fixtures, outcomes = evaluate()
        self.assertEqual(len(fixtures), 114)
        self.assertEqual(sum(r['expected_status'] == 'ACCEPTED' for r in fixtures), 38)
        self.assertEqual([r['id'] for r in outcomes if not r['matched']], [])

    def test_fixture_generation_and_content_hashes_are_deterministic(self):
        first, second = list(cases()), list(cases())
        self.assertEqual(canonical(first), canonical(second))
        self.assertEqual(len({r['id'] for r in first}), len(first))
        for row in first:
            payload = {k: v for k, v in row.items() if k != 'case_sha256'}
            self.assertEqual(hashlib.sha256(canonical(payload)).hexdigest(), row['case_sha256'])
        json.loads(canonical(first))  # Strict JSON: nonfinite values use tagged tokens.

    def test_always_accept_and_always_reject_both_fail_the_gate(self):
        for status in ('ACCEPTED', 'REJECTED'):
            _, outcomes = evaluate(lambda *a, **k: {'accepted': status == 'ACCEPTED', 'status': status})
            self.assertTrue(any(not r['matched'] for r in outcomes))


if __name__ == '__main__':
    unittest.main()
