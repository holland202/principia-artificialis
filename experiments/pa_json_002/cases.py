"""Frozen input construction only; no subject parser is invoked here."""
from fractions import Fraction
import re

COEFFICIENTS = (1, 125, 9007199254740993, 18014398509481983)
POWERS = (0, -2)
SIGNS = (1, -1)
PADDINGS = (0, 1, 18, 19, 20, 9998, 9999, 10000, 10001, 10002,
            99998, 99999, 100000, 100001, 100002, 131072)
FAMILIES = ('integer_padding', 'fraction_padding')
NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z')

def rational(token):
    """Read the full token exactly, cancelling decimal zeros before big integers."""
    if NUMBER.fullmatch(token) is None:
        raise ValueError('not an RFC-8259 number')
    negative = token.startswith('-')
    mantissa, _, power = token.lstrip('-').lower().partition('e')
    whole, _, fraction = mantissa.partition('.')
    digits = (whole + fraction).lstrip('0')
    if not digits:
        return Fraction(0)
    trimmed = digits.rstrip('0')
    exponent = (int(power) if power else 0) - len(fraction) + len(digits)-len(trimmed)
    coefficient = int(trimmed) * (-1 if negative else 1)
    return (Fraction(coefficient * 10**exponent) if exponent >= 0
            else Fraction(coefficient, 10**(-exponent)))

def corpus():
    case_id = 0
    for coefficient in COEFFICIENTS:
        digits = str(coefficient)
        for power in POWERS:
            for sign in SIGNS:
                prefix = '-' if sign < 0 else ''
                baseline = prefix + digits + 'e' + str(power)
                expected = Fraction(coefficient * sign) * (10**power if power >= 0 else Fraction(1,10**(-power)))
                for family in FAMILIES:
                    for padding in PADDINGS:
                        if family == 'integer_padding':
                            token = prefix + digits + '0'*padding + 'e' + str(power-padding)
                        else:
                            token = prefix + '0.' + '0'*padding + digits + 'e' + str(power+padding+len(digits))
                        yield {'id':case_id,'coefficient':coefficient,'power':power,'sign':sign,
                               'family':family,'padding':padding,'baseline':baseline,'token':token,
                               'expected_numerator':expected.numerator,'expected_denominator':expected.denominator}
                        case_id += 1
