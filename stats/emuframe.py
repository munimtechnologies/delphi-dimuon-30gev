# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""emuframe: test A' of the DELPHI plan (amendment 0.19) and the A'-ALEPH re-evaluation.

The opposite-sign mu mu mass spectrum is fitted against the opposite-sign e mu spectrum of the
SAME data, which is ALEPH's own background frame (Heister, arXiv:1610.06536). Unlike ALEPH's
default significance (Z_asym = 5.35, smoothed template treated as exact), the e mu template's own
Poisson error is kept, bin by bin (Barlow and Beeston 1993, one nuisance per bin, profiled in
closed form).

Model, per bin i:
    e mu counts  m_i ~ Poisson(t_i)
    mu mu counts n_i ~ Poisson(r * t_i + mu * s_i)
t_i: true e mu expectation (one free nuisance per bin, "bb"), r: mu mu / e mu ratio of the
background (free, shared by all bins), s_i: signal expected at mu = 1 (Voigt profile), mu >= 0.
Model "exact" fixes t_i = m_i (the template is treated as exact; r stays free), the binned,
unsmoothed analogue of ALEPH's Z_asym.

Discovery: one-sided q0, Z0 = sqrt(q0). Limits: q~_mu with asymptotic CLs (Cowan, Cranmer,
Gross and Vitells 2011, eqs. 65-66), sigma from the background-only Asimov set. Z_Bi: Cousins,
Linnemann and Tucker (2008), exact for integer counts.

Pure Python (no numpy or scipy), so it runs anywhere.
"""
import json
import math
import sys

VERSION = "mv2 emuframe 0.1.0"
LO, HI = 15.0, 50.0
M0, GAMMA0, SIGMA0 = 30.40, 1.78, 0.745      # Heister v9 fit; sigma = sqrt(6e-4) * 30.40
N_ALEPH = 32.31                              # fitted signal events, 15-50 GeV
R0_ALEPH = 1.0 / (2.0 * 0.94)                # mu mu / e mu: pair-count factor 2, e eff. 6 % lower
R0_RANGE = (0.45, 0.60)                      # pre-registered sensitivity range for R0_ALEPH
WINDOW_HALF = 2.0 * SIGMA0                   # Z_Bi window: bins with centre within m0 +- 2 sigma


# ----------------------------------------------------------------------------- basic functions
def phi(x):
    """Standard normal CDF."""
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def z_from_p(p):
    """One-sided Z with 1 - Phi(Z) = p (bisection; p in (0, 1))."""
    if p <= 0.0:
        return float("inf")
    if p >= 1.0:
        return float("-inf")
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 0.5 * math.erfc(mid / math.sqrt(2.0)) > p:     # upper tail falls as mid rises
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


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


def z_bi(n_on, n_off, tau):
    """Cousins-Linnemann-Tucker Z_Bi: p = I_{1/(1+tau)}(n_on, n_off + 1)
    = P(Binomial(n_on + n_off, 1/(1+tau)) >= n_on), integer counts."""
    n_on, n_off = int(round(n_on)), int(round(n_off))
    if n_on <= 0:
        return 0.0
    rho = 1.0 / (1.0 + tau)
    p = 1.0 - binom_cdf(n_on - 1, n_on + n_off, rho)
    return z_from_p(p)


# ----------------------------------------------------------------------------- signal shape
def _cdf_voigt(x, m, gamma, sigma, n_theta):
    """P(observed mass < x) for a Breit-Wigner (FWHM gamma) convolved with a Gaussian (sigma).
    The Breit-Wigner is integrated with t = m + (gamma/2) tan(theta), so each midpoint in theta
    carries weight 1/n_theta."""
    hw = 0.5 * gamma
    if hw <= 0.0:
        return phi((x - m) / sigma) if sigma > 0 else (1.0 if x > m else 0.0)
    if sigma <= 0.0:
        return 0.5 + math.atan((x - m) / hw) / math.pi
    s = 0.0
    for k in range(n_theta):
        th = -0.5 * math.pi + (k + 0.5) * math.pi / n_theta
        s += phi((x - m - hw * math.tan(th)) / sigma)
    return s / n_theta


def voigt_bin_probs(edges, m=M0, gamma=GAMMA0, sigma=SIGMA0, n_theta=4000):
    """Probability per bin of a Voigt profile truncated to [edges[0], edges[-1]] (sums to 1)."""
    c = [_cdf_voigt(x, m, gamma, sigma, n_theta) for x in edges]
    tot = c[-1] - c[0]
    return [(c[i + 1] - c[i]) / tot for i in range(len(edges) - 1)]


# ----------------------------------------------------------------------------- likelihood
def _xlogy(x, y):
    return 0.0 if x == 0 else x * math.log(y)


def t_hat(n, m, s, r, mu):
    """Barlow-Beeston: the t >= 0 maximising n ln(r t + mu s) - (r t + mu s) + m ln t - t.
    Stationarity gives r (r + 1) t^2 - [r (n + m) - (r + 1) mu s] t - m mu s = 0."""
    ms = mu * s
    if ms == 0.0:
        return (n + m) / (r + 1.0)
    a = r * (r + 1.0)
    b = -(r * (n + m) - (r + 1.0) * ms)
    c = -m * ms
    disc = math.sqrt(b * b - 4.0 * a * c)
    if b > 0.0:                           # avoid cancellation
        return -2.0 * c / (b + disc)
    return (-b + disc) / (2.0 * a)


def lnl_bb(n, m, s, r, mu):
    """Log-likelihood profiled over every t_i (constants dropped)."""
    tot = 0.0
    for ni, mi, si in zip(n, m, s):
        t = t_hat(ni, mi, si, r, mu)
        lam = r * t + mu * si
        if (ni > 0 and lam <= 0.0) or (mi > 0 and t <= 0.0):
            return float("-inf")
        tot += _xlogy(ni, lam) - lam + _xlogy(mi, t) - t
    return tot


def lnl_exact(n, m, s, r, mu):
    """Log-likelihood with the template treated as exact (t_i = m_i)."""
    tot = 0.0
    for ni, mi, si in zip(n, m, s):
        lam = r * mi + mu * si
        if lam <= 0.0:
            if ni > 0:
                return float("-inf")
            continue
        tot += _xlogy(ni, lam) - lam
    return tot


LNL = {"bb": lnl_bb, "exact": lnl_exact}


def _golden_max(f, a, b, tol=1e-11, it=300):
    g = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(it):
        if abs(b - a) < tol:
            break
        if fc >= fd:
            b, d, fd = d, c, fc
            c = b - g * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + g * (b - a)
            fd = f(d)
    x = 0.5 * (a + b)
    return x, f(x)


def _scan_then_golden(f, a, b, n=40):
    xs = [a + (b - a) * k / n for k in range(n + 1)]
    vals = [f(x) for x in xs]
    k = max(range(n + 1), key=lambda i: vals[i])
    x, v = _golden_max(f, xs[max(k - 1, 0)], xs[min(k + 1, n)])
    return (xs[k], vals[k]) if vals[k] > v else (x, v)


def profile_r(n, m, s, mu, model="bb"):
    """max over r of lnL(r, mu): returns (r_hat, lnL). Searched in ln r within +-2 of ln(N/M)."""
    lnl = LNL[model]
    big_n, big_m = sum(n), sum(m)
    x0 = math.log(big_n / big_m) if big_n > 0 and big_m > 0 else 0.0
    x, v = _scan_then_golden(lambda x: lnl(n, m, s, math.exp(x), mu), x0 - 2.0, x0 + 2.0)
    return math.exp(x), v


def fit(n, m, s, model="bb", mu_fixed=None, mu_hi=10.0):
    """Maximum-likelihood fit with mu >= 0. Returns {"mu", "r", "lnL"}."""
    if mu_fixed is not None:
        r, v = profile_r(n, m, s, mu_fixed, model)
        return {"mu": mu_fixed, "r": r, "lnL": v}
    prof = lambda mu: profile_r(n, m, s, mu, model)[1]
    for _ in range(6):
        mu, v = _scan_then_golden(prof, 0.0, mu_hi)
        if mu < 0.95 * mu_hi:
            break
        mu_hi *= 4.0
    v0 = prof(0.0)
    if v0 >= v:
        mu, v = 0.0, v0
    r, v = profile_r(n, m, s, mu, model)
    return {"mu": mu, "r": r, "lnL": v}


def discovery(n, m, s, model="bb", best=None):
    """One-sided q0 and Z0 = sqrt(q0); also 2 Delta lnL at mu = 1."""
    best = best or fit(n, m, s, model)
    b0 = fit(n, m, s, model, mu_fixed=0.0)
    b1 = fit(n, m, s, model, mu_fixed=1.0)
    q0 = max(0.0, 2.0 * (best["lnL"] - b0["lnL"]))
    return {"mu_hat": best["mu"], "r_hat": best["r"], "r_hat_mu0": b0["r"], "q0": q0,
            "Z0": math.sqrt(q0), "dll_mu1": max(0.0, 2.0 * (best["lnL"] - b1["lnL"]))}


# ----------------------------------------------------------------------------- limits (CLs)
def asimov_bkg(n, m, s, model="bb"):
    """Background-only Asimov set from the mu = 0 fit to the data."""
    r = fit(n, m, s, model, mu_fixed=0.0)["r"]
    if model == "bb":
        t = [t_hat(ni, mi, si, r, 0.0) for ni, mi, si in zip(n, m, s)]
    else:
        t = list(m)
    return [r * ti for ti in t], t


def _qtilde(n, m, s, mu, model, best):
    if best["mu"] >= mu:
        return 0.0
    return max(0.0, 2.0 * (best["lnL"] - profile_r(n, m, s, mu, model)[1]))


def cls(mu, n, m, s, model="bb", best=None, asimov=None):
    """Asymptotic CLs for q~_mu (Cowan et al. 2011, eqs. 65-66)."""
    best = best or fit(n, m, s, model)
    na, ma = asimov or asimov_bkg(n, m, s, model)
    best_a = {"mu": 0.0, "lnL": profile_r(na, ma, s, 0.0, model)[1]}
    q = _qtilde(n, m, s, mu, model, best)
    qa = _qtilde(na, ma, s, mu, model, best_a)
    if qa <= 0.0:
        return 1.0
    sq, sqa = math.sqrt(q), math.sqrt(qa)
    if q <= qa:
        p_mu, clb = 1.0 - phi(sq), phi(sqa - sq)
    else:
        p_mu = 1.0 - phi((q + qa) / (2.0 * sqa))
        clb = 1.0 - phi((q - qa) / (2.0 * sqa))
    return p_mu / clb if clb > 0.0 else 1.0


def upper_limit(n, m, s, model="bb", alpha=0.05, best=None, tol=1e-4):
    """mu at which CLs = alpha (95 % CL for alpha = 0.05)."""
    best = best or fit(n, m, s, model)
    asi = asimov_bkg(n, m, s, model)
    f = lambda mu: cls(mu, n, m, s, model, best, asi)
    lo = best["mu"]
    hi = max(1.0, 2.0 * lo)
    while f(hi) > alpha and hi < 1e5:
        lo, hi = hi, 2.0 * hi
    for _ in range(100):
        if hi - lo < tol:
            break
        mid = 0.5 * (lo + hi)
        if f(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ----------------------------------------------------------------------------- decisions
def label(ul, dll_mu1, z0):
    """Test A outcome rule of PLAN v0.11, applied to A'."""
    if ul < 1.0:
        return "EXCLUDED"
    if dll_mu1 < 1.0 and z0 >= 2.0:
        return "COMPATIBLE"
    return "INCONCLUSIVE"


def combine(label_nominal, label_low):
    """EXCLUDED or COMPATIBLE only if both N_had readings give it."""
    return label_nominal if label_nominal == label_low else "INCONCLUSIVE"


def window_bins(edges, m0=M0, half=WINDOW_HALF):
    return [i for i in range(len(edges) - 1) if abs(0.5 * (edges[i] + edges[i + 1]) - m0) <= half]


# ----------------------------------------------------------------------------- drivers
def aleph_aprime(edges, n, v_scaled, r0=R0_ALEPH, r0_range=R0_RANGE):
    """A'-ALEPH (amendment 0.19, sec. 3): n = mu mu data per bin, v_scaled = ALEPH's binned e mu
    background as plotted (already scaled to mu mu), r0 = assumed mu mu / e mu scale, so the raw
    e mu counts are v_scaled / r0."""
    s = [N_ALEPH * p for p in voigt_bin_probs(edges)]
    out = {"version": VERSION, "r0": r0, "n_sum": sum(n), "v_sum": sum(v_scaled),
           "exact_valid": all(not (ni > 0 and vi <= 0) for ni, vi in zip(n, v_scaled))}
    for model in ("bb", "exact"):
        m_raw = [v / r0 for v in v_scaled]
        out[model] = discovery(n, m_raw, s, model)
    out["ratio_bb_exact"] = (out["bb"]["Z0"] / out["exact"]["Z0"]) if out["exact"]["Z0"] > 0 else None
    out["bb_r0_variants"] = {}
    for rv in r0_range:
        out["bb_r0_variants"][str(rv)] = discovery(n, [v / rv for v in v_scaled], s, "bb")["Z0"]
    w = window_bins(edges)
    n_on, v_off = sum(n[i] for i in w), sum(v_scaled[i] for i in w)
    out["window"] = {"bins": [[edges[i], edges[i + 1]] for i in w], "n_on": n_on,
                     "bkg_scaled": v_off, "excess": n_on - v_off,
                     "Z_Bi_tau1": z_bi(n_on, v_off, 1.0),
                     "Z_Bi_tau_1_over_r0": z_bi(n_on, v_off / r0, 1.0 / r0)}
    return out


def delphi_aprime(edges, n_mumu, m_emu, n_exp_nominal, sigma=SIGMA0, low_factor=0.864):
    """A' for DELPHI (amendment 0.19, sec. 2): both N_had readings, model "bb" (primary)."""
    probs = voigt_bin_probs(edges, sigma=sigma)
    res = {"version": VERSION}
    labels = {}
    for name, nexp in (("nominal", n_exp_nominal), ("low", low_factor * n_exp_nominal)):
        s = [nexp * p for p in probs]
        best = fit(n_mumu, m_emu, s, "bb")
        d = discovery(n_mumu, m_emu, s, "bb", best)
        d["UL95"] = upper_limit(n_mumu, m_emu, s, "bb", best=best)
        d["label"] = label(d["UL95"], d["dll_mu1"], d["Z0"])
        res[name] = d
        labels[name] = d["label"]
    res["label"] = combine(labels["nominal"], labels["low"])
    return res


def main(argv):
    """python emuframe.py aleph <json with edges, n, v_scaled>"""
    if len(argv) >= 2 and argv[0] == "aleph":
        d = json.load(open(argv[1]))
        print(json.dumps(aleph_aprime(d["edges"], d["n"], d["v_scaled"]), indent=1))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
