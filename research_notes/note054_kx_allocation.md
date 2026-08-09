# 054 — Curvature carries the signal. Allocating on it loses to uniform.

**Status:** Draft, verified reference code — ⚠ P2 and P3 refuted, kept
**Reference code:** `scripts/note054_reference.py`
**Result scope:** DEVICE-VERIFIED on Samsung Galaxy S25 Ultra (Termux, aarch64), 2026-08-09.
**Credit:** Chad Edward Holland. Implementation and review with Claude (Anthropic).
**Related:** [[note055_kx_marginal_utility]] · [[note053_soft_hyperdga]]

---

## What failed first: a published number that would not reproduce

The container run reported Spearman(κ, r) = **+0.1170**. The device reported
**+0.1327** on the same deterministic script, same inputs, no randomness in
that path. Every MSE in the file was bit-identical across the two machines.
Only the correlation drifted — and it was the one prediction that *passed*.

The cause was in this note's own code, not the hardware. `spearman()` ranked
by double-`argsort` with no tie correction. `r_true` takes **3 distinct values
across 343 nodes** and κ takes **17**, so nearly every value is tied, and
`np.argsort` defaults to an unstable sort. The result was a property of which
sort path the build took:

```
quicksort  +0.1170        heapsort  +0.1170
mergesort  +0.2076        stable    +0.2076
S25 Ultra  +0.1327   (pre-fix)
tie-corrected midranks    +0.1480   <- correct
```

Four values from one dataset. Fixed with average ranks for ties; device and
container now agree at +0.1480 and P1 still clears its |ρ| > 0.05 bar.

**This is the most useful thing in the note.** The number was wrong in a
published file for a day, and what caught it was running the same script on a
second architecture — not review, not a test. It also draws a line worth
keeping: the two REFUTATIONS were bit-identical on both machines from the
start. Only the passing statistic was fragile. A result that says "no" was
sturdier than the one that said "yes."

## What failed second: the hypothesis

At matched budget, allocating compute by curvature is **2.15× worse than
spreading it evenly**.

```
coupled     (budget 4207 neighbourhood-units, every arm spends it exactly)
    uniform    MSE 0.022744    hops mean 2.327
    kx         MSE 0.048930    hops mean 2.624     P2 FAIL  -1.1513
    inv-kx     MSE 0.090984    hops mean 2.248             -3.0004
    shuffled   MSE 0.056536    hops mean 2.341
    oracle     MSE 0.000000    hops mean 2.210
```

Both directions lose. Spending where geometry is *flat* is worse still, 4×
uniform, so this is not a sign error. A weak allocation signal followed in
either direction is worse than no signal at all.

**P3 refuted, and my registered bar was the wrong shape.** I predicted the kx
arm would go neutral in the decoupled condition — the instrument returning
null when the hypothesis is false. It came in at **−0.3246**. The instrument
does not falsely report a *win*, which was what mattered, but "neutral" was
never available: an arm that spends the same budget worse can only score ≤ 0.
A two-sided bar on a one-sided quantity is a bad registration, and I made the
same error again in [[note055_kx_marginal_utility]] after diagnosing it here.

## What held

```
P0 anti-vacuity  PASS   oracle +1.0000, shuffled -1.4858
P1 correlation   PASS   Spearman(kappa, r) = +0.1480 (tie-corrected)
H1 H2_coupled H2_decoupled H3 H4   all PASS
    oracle allocation reproduces r_i exactly on 343/343 nodes
```

The oracle reaches MSE exactly `0.000000` and recovers the true radius on
every node at the same budget, so there *is* a right answer worth +100% and
something could have found it. Shuffled κ does not beat uniform. The channel
is live and the comparison is unconfounded.

**The finding is the gap between P1 and P2.** Curvature genuinely carries
information about required radius, ρ = +0.1480, and acting on it loses by
2.15×. Predictive correlation and actionable control signal are different
properties, and the distance between them is the whole result.

## Why, mechanically

`K(x)` here is unweighted Forman–Ricci, `F(u,v) = 4 − deg(u) − deg(v)`, meaned
over incident edges (min −7.500, mean −3.082, max 0.000). That is a **degree
expression**. Allocating by it means allocating by inverse degree — pushing
hops toward sparse tree leaves needing radius 2 while starving grid nodes
needing radius 3. Hence `hops mean 2.624` against the oracle's `2.210` at
identical spend: it overspends in the wrong place.

## Harness defect, kept

First run, the allocator started every node at `cmin` and handed out +1 hop in
score order. The budget happened to equal the cost of all-nodes-at-2, so the
first pass lifted everything to 2 and consumed the budget exactly — **all five
arms produced identical allocations and identical MSE**. P0 caught it and
refused to report P1–P3. The gate did its job on run one, before a number
existed to be wrong about. Replaced with bisection on λ plus a deterministic
remainder pass.

## Observation, not a claim

Correcting the tie handling widened the coupled/decoupled separation. Before:
+0.1226 decoupled against +0.1170 coupled, a ratio of 1.08 — the control
barely separated. After: **+0.0743 against +0.1480**, a ratio of 2.0. A
decoupling control that fails to separate is not much of a control, so the
fix improved the instrument and not only the number. This was not registered
and is not claimed.

## Open

**P4, unrun deliberately.** Repeat with Ollivier–Ricci. Forman as used here is
a degree expression, so "curvature failed" and "a degree proxy failed" are not
distinguished by anything in this note. [[note055_kx_marginal_utility]]
reframes the target from required radius to marginal utility per unit cost and
does not close this either.

## Reproduce

```bash
python3 scripts/note054_reference.py
```

Pure NumPy. Runs on a phone. Every number above is pasted from its output.
