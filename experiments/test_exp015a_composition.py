"""Regression and adversarial checks for EXP015-A synthetic instrument."""
import unittest
from fractions import Fraction as Q
from exp015a_composition import compose, identity, validate, run


class CompositionControls(unittest.TestCase):
    def test_registered_controls(self):
        result = run()
        self.assertEqual(result["associativity"], "PASS")
        self.assertEqual(result["mean_tv_error_common_prediction"], "1/2")

    def test_identity_three_states(self):
        i = identity(3)
        validate(i)
        self.assertEqual(compose(i, i), i)

    def test_reject_negative_probability(self):
        with self.assertRaises(ValueError):
            validate(((Q(-1), Q(2)),))

    def test_reject_non_normalized(self):
        with self.assertRaises(ValueError):
            validate(((Q(1, 3), Q(1, 3)),))

    def test_reject_ragged(self):
        with self.assertRaises(ValueError):
            validate(((Q(1),), (Q(0), Q(1))))

    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            validate(())

    def test_reject_incompatible_dimensions(self):
        with self.assertRaises(ValueError):
            compose(((Q(1), Q(0)),), ((Q(1), Q(0)),))

    def test_history_aliasing_cannot_be_exact(self):
        target0, target1 = (Q(1), Q(0)), (Q(0), Q(1))
        # Any single row cannot exactly match both incompatible targets.
        for p in (Q(0), Q(1, 4), Q(1, 2), Q(3, 4), Q(1)):
            prediction = (p, 1-p)
            self.assertFalse(prediction == target0 and prediction == target1)


if __name__ == "__main__":
    unittest.main()
