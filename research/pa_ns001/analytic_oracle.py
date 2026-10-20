"""Polynomial construction oracle with no ns001 imports or AI verdicts.

Separate implementation by the same ChatGPT author: NOT independent review.
Parameters are exact decimal/rational strings; calibration measures the difference
from binary64 configuration too. Derivation is in ORACLE_AND_FAULTS.md.
"""
from fractions import Fraction


def polynomial(kind, parameters):
    height = Fraction(str(parameters['h']))
    viscosity = Fraction(str(parameters['mu']))
    if height <= 0 or viscosity <= 0:
        raise ValueError('positive height and viscosity required')
    if kind == 'couette':
        return Fraction(0), Fraction(str(parameters['U'])) / height, Fraction(0)
    if kind == 'poiseuille':
        a = -Fraction(str(parameters['G'])) / (2 * viscosity)
        return a, -a * height, Fraction(0)
    raise ValueError('unknown family')


def exact_samples(kind, parameters, n):
    if type(n) is not int or n < 5:
        raise ValueError('at least five samples required')
    a, b, c = polynomial(kind, parameters)
    height = Fraction(str(parameters['h']))
    return [a*y*y+b*y+c for y in (height*Fraction(i, n-1) for i in range(n))]


def characteristic(kind, parameters):
    a, b, _ = polynomial(kind, parameters)
    height = Fraction(str(parameters['h']))
    return b * height if kind == 'couette' else a*height**2/4 + b*height/2


def construction_is_identical(kind, left, right):
    return (Fraction(str(left['h'])) == Fraction(str(right['h']))
            and polynomial(kind, left) == polynomial(kind, right))
