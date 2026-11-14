"""Property tests for memdecay2.py: seeded random inputs, no answer key, and the registered mutants.

Run from the repository root:  python3 -m pytest -q experiments/mem_decay_002/test_memdecay2.py
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import memdecay2 as d2  # noqa: E402

SEEDS = range(40)


def rand_store(seed, n=60):
    rng = np.random.default_rng(seed)
    age = rng.uniform(0, 365, n)
    crit = rng.uniform(size=n) < 0.2
    store = {"age": age, "access": age * rng.uniform(size=n), "critical": crit,
             "status": np.where(rng.uniform(size=n) < 0.9, d2.m.CURRENT, d2.m.SUPERSEDED)}
    ex = d2.extras(store, seed)
    sim = rng.uniform(-1, 1, n)
    return rng, store, ex, sim


def rank_of(score, i):
    return int((score > score[i]).sum())


@pytest.fixture(autouse=True)
def no_mutant():
    d2.MUTANT = None
    yield
    d2.MUTANT = None


@pytest.mark.parametrize("seed", SEEDS)
def test_raising_a_floor_never_lowers_rank(seed):
    rng, store, ex, sim = rand_store(seed)
    sim = np.abs(sim)
    w = d2.labels(ex, store["critical"], 0.1)
    i = int(rng.integers(len(sim)))
    before, _ = d2.scores(sim, store, ex, w, "A5", 180.0, 180.0)
    w2 = w.copy()
    w2[i] = min(1.0, w[i] + 0.5)
    after, _ = d2.scores(sim, store, ex, w2, "A5", 180.0, 180.0)
    assert rank_of(after, i) <= rank_of(before, i)


@pytest.mark.parametrize("seed", SEEDS)
def test_a_full_floor_restores_similarity(seed):
    _, store, ex, sim = rand_store(seed)
    sim = np.abs(sim)
    score, _ = d2.scores(sim, store, ex, np.ones(len(sim)), "A5", 180.0, 180.0)
    assert np.allclose(score, sim)


@pytest.mark.parametrize("seed", SEEDS)
def test_more_use_means_slower_decay(seed):
    S_lo, S_hi = np.ones(5), np.full(5, 1 + math.log2(4))
    a = np.full(5, 100.0)
    assert (d2.retrieval_strength(a, S_hi, 180.0) > d2.retrieval_strength(a, S_lo, 180.0)).all()


@pytest.mark.parametrize("seed", SEEDS)
def test_a_pin_never_lowers_rank_and_scores_similarity(seed):
    rng, store, ex, sim = rand_store(seed)
    sim = np.abs(sim)
    w = np.zeros(len(sim))
    i = int(rng.integers(len(sim)))
    before, _ = d2.scores(sim, store, ex, w, "A7", 180.0, 180.0)
    w[i] = 1.0
    after, _ = d2.scores(sim, store, ex, w, "A7", 180.0, 180.0)
    assert after[i] == sim[i] and rank_of(after, i) <= rank_of(before, i)


@pytest.mark.parametrize("seed", SEEDS)
def test_noise_misses_only_critical_and_raises_only_others(seed):
    _, store, ex, _ = rand_store(seed, n=400)
    crit = store["critical"]
    w0, w1 = d2.labels(ex, crit, 0.0), d2.labels(ex, crit, 1.0)
    assert (w0[crit] >= d2.PIN).all() and (w0[~crit] < d2.PIN).all()
    assert (w1[crit] < d2.PIN).all()                      # eps = 1: every critical record missed
    raised = (w1[~crit] >= d2.PIN).mean()
    assert 0.03 < raised < 0.20                           # about eps / 10 of the others raised


@pytest.mark.parametrize("seed", SEEDS)
def test_noise_is_nested_across_eps(seed):
    _, store, ex, _ = rand_store(seed, n=300)
    crit = store["critical"]
    lo = d2.labels(ex, crit, 0.1) < d2.PIN
    hi = d2.labels(ex, crit, 0.3) < d2.PIN
    assert (hi[crit] | ~lo[crit]).all()                   # missed at 0.1 implies missed at 0.3


def test_ttl_with_pins_keeps_exactly_old_pinned_and_young():
    _, store, ex, sim = rand_store(1, n=200)
    w = d2.labels(ex, store["critical"], 0.0)
    _, alive = d2.scores(sim, store, ex, w, "A4L", 180.0, 180.0)
    assert (alive == ((store["age"] <= 180.0) | (w >= d2.PIN))).all()


def test_extras_leave_the_base_store_untouched():
    store, queries = d2.m.build("d2dev")
    before = d2.m.canonical(store, queries)
    d2.extras(store, 20261117)
    assert d2.m.canonical(store, queries) == before


# ---- the registered mutants must each fail at least one test above
MUTANTS = ["floor", "storage", "pins", "no_noise", "wrong_class"]


@pytest.mark.parametrize("mutant", MUTANTS)
def test_mutant_is_killed(mutant):
    d2.MUTANT = mutant
    checks = [
        lambda: test_a_full_floor_restores_similarity(3),
        lambda: test_more_use_means_slower_decay(3),
        lambda: test_a_pin_never_lowers_rank_and_scores_similarity(3),
        lambda: test_noise_misses_only_critical_and_raises_only_others(3),
    ]
    killed = 0
    for check in checks:
        try:
            check()
        except AssertionError:
            killed += 1
    assert killed >= 1, f"mutant {mutant} survived every check"
