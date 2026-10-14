# EGRR P1 — Statistical Feasibility Assessment

Status: EXPLORATORY MATHEMATICAL ANALYSIS ONLY.
Not registered, approved, or confirmatory.

## Original target

For an independent synthetic case:

r = 1 - MSE_covariance / MSE_magnitude

H0: E[r] <= 0.10
H1: E[r] > 0.10

Proposed n = 100; one-sided alpha = 0.05.
Neither the decision rule nor sample size is approved.

## Generator and numerical policy

The v0.5 proposal uses standard-normal weight, calibration
and evaluation arrays, with 64x32 weights, 256x64 calibration
inputs and 1024x64 evaluation inputs.

The proposal rejects invalid/nonfinite arithmetic and marks
MSE_magnitude <= 1e-12 as an instrument failure.

The threshold is provisional. Treating undefined cases as
failures rather than silently dropping them is important,
but does not by itself establish a population mean test.

## Feasibility of a lower support bound

For nonnegative MSE values and a positive denominator:

r <= 1.

However, the proposal does not establish a useful finite
lower bound L such that r >= L for every eligible case.

The standard-normal generator has unbounded mathematical
support. Finite floating-point representation, numerical
guarding and rejection of undefined cases do not establish
a useful nonvacuous population support bound.

A numerical range imposed by the representation would also
require explicit analysis of the selection/failure policy
and its relationship to the target population.

Conclusion: no useful pre-data lower bound is presently proven.

## Feasibility of a variance upper bound

Finite exploratory sample variance is not a proven upper
bound on population Var(r).

The current proposal contains no mathematical derivation
of Var(r) <= V from the generator, quantizer, selectors
and denominator behavior.

Conclusion: a defensible numerical V is presently unavailable.

## Conditional fixed-horizon option

If independent cases and a proven finite population variance
upper bound V were established, Cantelli's inequality gives
a conservative rejection threshold:

mean(r) > 0.10 + sqrt(19*V/100)

For observed mean excess d = mean(r) - 0.10 > 0:

p_bound = (V/100) / (V/100 + d*d)

Otherwise p_bound = 1.

These are conditional mathematical statements, NOT an
approved or currently usable EGRR decision rule.

For illustration, if V = 0.01 were genuinely proven,
the threshold would be about 0.143589.
For V = 0.1 it would be about 0.237840.
Neither variance bound has been established for EGRR.

## Analytical rare-negative null killer

Construct an independent case-level variable r:

- probability 0.995: uniform on [0.199, 0.201]
- probability 0.005: exactly -20.02

Its population mean is:

0.995*0.2 + 0.005*(-20.02) = 0.0989

Thus H0 is true.

The probability that 100 independent observations miss
the rare negative branch entirely is:

0.995**100, approximately 0.6058.

In that event, the sample looks close to a stable 20% gain.
This demonstrates a specific tail-risk for unqualified
t-test or percentile-bootstrap mean claims.

This is an analytical example, NOT an EGRR experiment.

## Population and numerical-failure qualification

The original estimand is the mean of paired relative gains over
the specified independent-case population. A rule rejecting cases
with MSE_magnitude <= 1e-12 does not establish that the original
ratio is defined over that entire population.

Conditioning on numerically valid cases would change the target
population and therefore cannot be introduced silently.

Failing the entire instrument when any case is invalid prevents
selective deletion, but may leave no confirmatory mean verdict.
A defensible population definition and treatment of undefined
ratios require maintainer agreement before registration.

Finite floating-point arithmetic must not be mistaken for a
useful statistical tail bound. Any machine-representation bound
would need explicit derivation, handling of underflow/overflow,
and a demonstration of useful power at n=100.

For illustration, the conditional Cantelli rejection threshold
at V=0.01 is 14.3589%, and at V=0.1 is 23.7840%.
Neither V has been proven. These numerical examples do not
establish actual rejection probability or power for EGRR.

Consequently, neither a uniformly valid 5%-level population
mean claim nor useful power has been demonstrated.

## Current statistical decision

Population-mean P1: UNRESOLVED / NOT APPROVED.

Do not replace the estimand with the probability of a 10%
gain. A binomial analysis of that probability would be
a separately named secondary research question.

A fixed set of 100 seed outcomes could be described exactly,
but descriptive case summaries are not population-inference
claims and do not carry a 5% type-I-error guarantee.

No held-out generator seeds have been executed for this note.

## Future exploratory instrument controls

Propose independently specified benign, zero-effect null,
and rare-negative null cases for statistical instrumentation.

For any candidate procedure, report its false-success
behavior, exact source, commands, seed identity, stdout,
stderr and exit status. Controls are not confirmatory
EGRR evaluations.

Approval of a procedure must precede any held-out
confirmatory EGRR execution.

## Remaining obligations

Keep M16, M13, C-EXPLORE and provenance open.
Preserve the original P1, original investigator credit,
protocol revision history and prior exploratory work.

No merge or canonical methodology change requested.
