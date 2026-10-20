import math
import unittest

from study_design import binomial_cdf, exact_interval, paired_exact_pvalue


class TestStudyDesign(unittest.TestCase):
    def test_published_nist_interval(self):
        lower, upper = exact_interval(4, 20, .10)
        # NIST's worked example gives approximate six-decimal roots; its upper
        # root differs by about 9e-7 from full numeric inversion. Do not copy
        # the displayed root as an exact constant.
        self.assertAlmostEqual(lower, .071354, delta=1.5e-6)
        self.assertAlmostEqual(upper, .401029, delta=1.5e-6)
        self.assertAlmostEqual(binomial_cdf(4, 20, upper), .05, places=12)
        self.assertAlmostEqual(binomial_cdf(3, 20, lower), .95, places=12)

    def test_binomial_closed_forms_and_symmetry(self):
        self.assertAlmostEqual(binomial_cdf(1, 4, .5), 5/16)
        for n in (1, 20, 400):
            lower, upper = exact_interval(0, n)
            self.assertEqual(lower, 0)
            self.assertAlmostEqual(upper, 1-.025**(1/n), places=12)
            opposite = exact_interval(n, n)
            self.assertAlmostEqual(opposite[0], 1-upper, places=12)
            self.assertEqual(opposite[1], 1)

    def test_paired_conditional_exact_test(self):
        self.assertEqual(paired_exact_pvalue(0, 0), 1)
        self.assertEqual(paired_exact_pvalue(10, 0), 2/1024)
        self.assertEqual(paired_exact_pvalue(3, 7), paired_exact_pvalue(7, 3))
        self.assertEqual(paired_exact_pvalue(5, 5), 1)

    def test_invalid_interval_inputs(self):
        for values in ((0, 0, .05), (2, 1, .05), (-1, 3, .05), (0, 3, math.nan), (True, 3, .05)):
            with self.assertRaises(ValueError):
                exact_interval(*values)


if __name__ == '__main__':
    unittest.main()
