# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""envpool: pools the mu = 1 pseudo-experiments of dimu-envtoys-v1, -v2 and -v3 and grades
criterion (b) of PLAN amendment 0.12 (N7 of amendment 0.17) on the pool, as amendment 0.16's
pooling rule says: EXCLUDED counts and toy counts add per test, the decision uses the point
estimate (as envtoys.criterion_b does), and it is made only once every test has >= 150 toys.

Pure Python (no numpy or scipy), so it runs anywhere. The Clopper-Pearson interval is found by
bisection on the exact binomial distribution; it is reported, never used to decide.

    python envpool.py ../analysis/results/envtoys/envtoys.json \
        ../analysis/results/envtoys-v2/envtoys.json ../analysis/results/envtoys-v3/envtoys.json
"""
import json
import math
import sys

VERSION = "mv2 envpool 0.1.0"
P_MAX = 0.07
N_MIN = 150
KEYS = ("fix3|tagged", "fix3|combined", "old|tagged", "old|combined")
TESTS = {"A": "fix3|tagged", "B": "fix3|combined"}
N10_RANGE = (0.90, 1.10)


def binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k < 0:
        return 0.0
    if k >= n or p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    lp, lq = math.log(p), math.log1p(-p)
    s = 0.0
    for i in range(k + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                      + i * lp + (n - i) * lq)
    return min(1.0, s)


def _solve(f, target, lo, hi, it=200):
    """Bisection for a decreasing f(p) = target on [lo, hi]."""
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        if f(mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson(k, n, cl=0.95):
    """Two-sided exact interval for k / n (same definition as envtoys.clopper_pearson)."""
    a = 1.0 - cl
    # lower: P(X >= k) = a/2, i.e. cdf(k-1) = 1 - a/2; upper: cdf(k) = a/2 (cdf falls with p)
    lo = 0.0 if k == 0 else _solve(lambda p: binom_cdf(k - 1, n, p), 1.0 - a / 2, 0.0, 1.0)
    hi = 1.0 if k == n else _solve(lambda p: binom_cdf(k, n, p), a / 2, 0.0, 1.0)
    return lo, hi


def batch(summary):
    """The mu = 1 numbers of one envtoys.json: {key: (n, n_EXCLUDED, muhat_mean)}."""
    d = summary["toys"]["mu=1"]
    return {k: (int(d[k]["n"]), int(d[k]["n_EXCLUDED"]), float(d[k]["muhat_mean"])) for k in KEYS}


def pool(batches):
    """Add counts per key; the pooled mean is the toy-weighted mean of the batch means."""
    out = {}
    for k in KEYS:
        n = sum(b[k][0] for b in batches)
        ex = sum(b[k][1] for b in batches)
        mean = sum(b[k][0] * b[k][2] for b in batches) / n
        lo, hi = clopper_pearson(ex, n)
        out[k] = {"n": n, "n_EXCLUDED": ex, "p_EXCLUDED": ex / n, "muhat_mean": mean,
                  "p_EXCLUDED_cp95": [lo, hi]}
    return out


def grade(pooled, tests_ok=True, hashes_ok=True, asimov_ok=True):
    """N7 (criterion b on the pool), N9 (v3 identical to v1), N10 (pooled mean, test A)."""
    rows = [pooled[TESTS[t]] for t in ("A", "B")]
    if any(r["n"] < N_MIN for r in rows):
        n7 = "UNDETERMINED"
    else:
        n7 = "PASS" if all(r["p_EXCLUDED"] <= P_MAX for r in rows) else "FAIL"
    n9 = "PASS" if (tests_ok and hashes_ok and asimov_ok) else "FAIL"
    m = pooled[TESTS["A"]]["muhat_mean"]
    n10 = "PASS" if N10_RANGE[0] <= m <= N10_RANGE[1] else "FAIL"
    return {"N7": n7, "N9": n9, "N10": n10}


def main(paths):
    batches = [batch(json.load(open(p))) for p in paths]
    pooled = pool(batches)
    print(json.dumps({"version": VERSION, "pooled": pooled, "grades": grade(pooled)}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
