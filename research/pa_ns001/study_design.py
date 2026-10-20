"""Prospective fixed-horizon design arithmetic, never AI evaluation data.

Binomial-CDF inversion follows NIST's exact-interval equations; numeric root
calculation uses binary64, not exact symbolic endpoints. Independent known-value
tests accompany it. No scipy/statsmodels dependency or third-party code copied.
"""
import json
import math


def binomial_cdf(k, n, p):
    if k < 0:
        return 0.0
    if k >= n or p == 0:
        return 1.0
    if p == 1:
        return 0.0
    logs = [math.lgamma(n+1)-math.lgamma(j+1)-math.lgamma(n-j+1)
            + j*math.log(p)+(n-j)*math.log1p(-p) for j in range(k+1)]
    largest = max(logs)
    return min(1.0, math.exp(largest)*math.fsum(math.exp(x-largest) for x in logs))


def exact_interval(k, n, alpha=.05):
    """Equal-tailed Clopper-Pearson interval, numeric inversion of binomial CDF."""
    if (type(k) is not int or type(n) is not int or not 0 <= k <= n <= 5000
            or n == 0 or type(alpha) not in (int, float) or not 0 < alpha < 1):
        raise ValueError('invalid interval configuration')

    def root(count, target):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo+hi)/2
            if binomial_cdf(count, n, mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo+hi)/2

    lower = 0.0 if k == 0 else root(k-1, 1-alpha/2)
    upper = 1.0 if k == n else root(k, alpha/2)
    return lower, upper


def paired_exact_pvalue(rescued, harmed):
    """Two-sided exact McNemar/sign test conditional on discordant paired cases."""
    if type(rescued) is not int or type(harmed) is not int or min(rescued, harmed) < 0:
        raise ValueError('nonnegative discordance counts required')
    discordant = rescued + harmed
    if not discordant:
        return 1.0
    # Exact integer numerator and denominator before final float conversion.
    numerator = 2 * sum(math.comb(discordant, j) for j in range(min(rescued, harmed)+1))
    return min(1.0, numerator / 2**discordant)


def design_numbers():
    planning = []
    for n in (100, 200, 400):
        critical = next(k for k in range(n+1) if 1-binomial_cdf(k-1, n, .05) <= .025)
        planning.append({'invalid_units': n, 'minimum_rescued_for_95pct_lower_bound_at_least_5pp': critical,
                         'power_if_true_rescue_rate_10pct': 1-binomial_cdf(critical-1, n, .10),
                         'zero_failure_95pct_two_sided_upper': exact_interval(0, n)[1],
                         'zero_failure_95pct_one_sided_upper': -math.expm1(math.log(.05)/n)})
    return {'classification': 'prospective arithmetic under IID Bernoulli assumptions, not observations',
            'planning_scenarios': planning,
            'zero_failure_units_for_one_sided_95pct_upper_below_1pct': math.ceil(math.log(.05)/math.log(.99)),
            'published_NIST_4_of_20_90pct_interval': exact_interval(4, 20, .10),
            'paired_exact_example_10_rescued_0_harmed': paired_exact_pvalue(10, 0)}


if __name__ == '__main__':
    print(json.dumps(design_numbers(), sort_keys=True, indent=2, allow_nan=False))
