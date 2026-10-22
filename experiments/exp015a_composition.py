"""EXP015-A: exact rational Markov composition and hidden-history counterexample."""
from fractions import Fraction as Q


def compose(a, b):
    """Row-stochastic matrices: apply a, then b."""
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("incompatible dimensions")
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(len(b))), Q(0))
                       for j in range(len(b[0]))) for i in range(len(a)))


def identity(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def validate(m):
    if not m or any(len(row) != len(m[0]) for row in m):
        raise ValueError("ragged or empty matrix")
    if any(any(x < 0 for x in row) or sum(row) != 1 for row in m):
        raise ValueError("not row stochastic")


def run():
    a = ((Q(1, 2), Q(1, 2)), (Q(1, 4), Q(3, 4)))
    b = ((Q(3, 4), Q(1, 4)), (Q(1, 3), Q(2, 3)))
    c = ((Q(2, 3), Q(1, 3)), (Q(1, 5), Q(4, 5)))
    for m in (a, b, c):
        validate(m)
    assert compose(compose(a, b), c) == compose(a, compose(b, c))
    assert compose(a, identity(2)) == a == compose(identity(2), a)
    # Two histories share observed state x=0 but demand different next-state laws.
    history0_next = (Q(1), Q(0))
    history1_next = (Q(0), Q(1))
    assert history0_next != history1_next
    common_prediction = (Q(1, 2), Q(1, 2))
    tv = lambda p, q: sum((abs(x-y) for x, y in zip(p, q)), Q(0)) / 2
    assert (tv(common_prediction, history0_next) + tv(common_prediction, history1_next)) / 2 == Q(1, 2)
    return {"associativity": "PASS", "left_right_identity": "PASS",
            "history_independent_transition": "REFUTED for constructed example",
            "mean_tv_error_common_prediction": "1/2"}


if __name__ == "__main__":
    import json
    print(json.dumps(run(), sort_keys=True))
