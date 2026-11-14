"""Tests for rmt037.py on seeded synthetic matrices only (no model weights). Mutant checks included."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmt037 as r  # noqa: E402


@pytest.mark.parametrize("seed", range(20))
def test_qk_levels_match_full_svd(seed):
    rng = np.random.default_rng(seed)
    wq, wk = rng.normal(size=(96, 8)), rng.normal(size=(96, 8))
    full = np.sort(np.linalg.svd(wq @ wk.T, compute_uv=False))[::-1][:8]
    assert np.allclose(np.sort(r.qk_levels(wq, wk))[::-1], full, rtol=1e-9)


@pytest.mark.parametrize("seed", range(20))
def test_sym_levels_match_full_eigh(seed):
    rng = np.random.default_rng(seed)
    wq, wk = rng.normal(size=(96, 8)), rng.normal(size=(96, 8))
    s = (wq @ wk.T + wk @ wq.T) / 2
    full = np.linalg.eigvalsh(s)
    nz = np.sort(full[np.argsort(np.abs(full))[-16:]])
    assert np.allclose(np.sort(r.sym_levels(wq, wk)), nz, atol=1e-9 * np.abs(full).max())


def test_ratio_known_values():
    rr, z = r.ratios([0, 1, 3, 4])           # spacings 1, 2, 1 -> ratios 0.5, 0.5
    assert np.allclose(rr, [0.5, 0.5]) and z == 0
    rr, z = r.ratios([0, 1, 1, 2])           # spacings 1, 0, 1 -> both pairs have a zero gap
    assert np.allclose(rr, [0.0, 0.0]) and z == 0
    rr, z = r.ratios([0, 0, 0])               # all gaps zero: dropped and counted
    assert len(rr) == 0 and z == 1


def test_statistic_separates_goe_from_poisson():
    rng = np.random.default_rng(1)
    goe = r.ref_pool("GOE", 64, "bulk", rng, reps=200)[0]
    poi = r.ref_pool("POIS", 64, "bulk", rng, reps=200)[0]
    assert abs(goe - r.R_GOE) < 0.03 and abs(poi - r.R_POI) < 0.03


def test_ratios_are_scale_and_shift_invariant():
    rng = np.random.default_rng(2)
    lv = rng.normal(size=50)
    a, _ = r.ratios(lv)
    b, _ = r.ratios(3.7 * lv + 11.0)
    assert np.allclose(a, b)


def test_regions_partition_by_rank():
    lv = np.arange(100.0)
    reg = r.regions(lv[::-1])
    assert reg["bulk"][0] == 10 and reg["bulk"][-1] == 89 and list(reg["edge"]) == list(range(90, 100))


def test_shuffled_arm_keeps_values_and_breaks_alignment():
    rng = np.random.default_rng(3)
    c = rng.normal(size=(64, 3 * 64))
    rows_t = r.collect([c], 4, "TRAINED", np.random.default_rng(0))
    rows_s = r.collect([c], 4, "SHUF", np.random.default_rng(0))
    assert not np.allclose(rows_t[0][2], rows_s[0][2])


@pytest.mark.parametrize("mutant", ["no_sort", "max_over_min", "no_qr"])
def test_mutants_are_killed(mutant, monkeypatch):
    orig_ratios, orig_qk = r.ratios, r.qk_levels
    if mutant == "no_sort":
        def bad(levels):
            s = np.diff(np.asarray(levels, float))
            a, b = s[:-1], s[1:]
            mx = np.maximum(np.abs(a), np.abs(b))
            return np.minimum(np.abs(a), np.abs(b)) / mx, 0
        monkeypatch.setattr(r, "ratios", bad)
    if mutant == "max_over_min":
        def bad(levels):
            rr, z = orig_ratios(levels)
            return np.where(rr > 0, 1 / np.where(rr > 0, rr, 1), 0), z
        monkeypatch.setattr(r, "ratios", bad)
    if mutant == "no_qr":
        monkeypatch.setattr(r, "qk_levels", lambda wq, wk: np.linalg.svd(wq.T @ wk, compute_uv=False))
    failures = 0
    for check in (lambda: test_ratio_known_values(), lambda: test_qk_levels_match_full_svd(0),
                  lambda: test_statistic_separates_goe_from_poisson()):
        try:
            check()
        except AssertionError:
            failures += 1
    assert failures >= 1, f"{mutant} survived"
