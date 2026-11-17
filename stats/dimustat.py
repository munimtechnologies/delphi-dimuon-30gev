"""dimustat: the pre-registered statistics for the DELPHI test of the ALEPH 30 GeV dimuon excess.

Model (PLAN section 5, made concrete in v0.4):
  * opposite-sign dimuon masses in 15-50 GeV, histogrammed in 50 MeV bins (700 bins; at a
    mass resolution of 0.3-0.75 GeV this is equivalent to an unbinned fit);
  * signal: Breit-Wigner (m, Gamma) convolved with a Gaussian (sigma), i.e. a Voigt profile,
    truncated to 15-50 GeV; yield n_s counts signal events inside 15-50 GeV, as ALEPH's 32.3 does;
  * background: exp(sum_k a_k P_k(t)), P_k Legendre polynomials, t = ln(m) mapped linearly onto
    [-1, 1] over [15, 50] GeV ("log-Legendre" of degree n; n = 1 is a pure power law, the
    exp(-c0 ln x) form of arXiv:1610.06536);
  * extended Poisson likelihood; test statistics q0 (discovery) and q~_mu (upper limits) of
    Cowan, Cranmer, Gross, Vitells, Eur. Phys. J. C71 (2011) 1554, with asymptotic CLs.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import math

import numpy as np
from scipy import optimize, special, stats

LO, HI, BW = 15.0, 50.0, 0.05
EDGES = np.round(np.arange(LO, HI + BW / 2, BW), 6)
CENT = 0.5 * (EDGES[1:] + EDGES[:-1])
NB = len(CENT)

# ALEPH (arXiv:1610.06536 v9, sec. 4.5, unbinned extended fit in 15-50 GeV)
ALEPH = dict(n_sig=32.31, n_sig_err=10.87, mass=30.40, mass_err=0.46, width=1.78,
             width_err=1.14, sigma=0.74, sigma_err=0.10, n_bkg=1457.06, n_bkg_err=89.71,
             n_had=1.9e6)


def legendre_basis(n, x=CENT):
    t = 2.0 * (np.log(x) - math.log(LO)) / (math.log(HI) - math.log(LO)) - 1.0
    return np.array([special.eval_legendre(k, t) for k in range(1, n + 1)])  # (n, NB)


def signal_template(mass=ALEPH['mass'], width=ALEPH['width'], sigma=None, x=CENT, sub=5):
    """Bin probabilities of a Voigt(mass, Gamma=width, sigma) truncated to [LO, HI].
    sigma=None means ALEPH's resolution model sigma = sqrt(6e-4) * mass.
    Each bin is integrated with `sub` sub-points (midpoint rule)."""
    if sigma is None:
        sigma = math.sqrt(6e-4) * mass
    off = (np.arange(sub) + 0.5) / sub - 0.5
    xs = (x[:, None] + off[None, :] * BW).ravel()
    if width <= 0:
        pdf = stats.norm.pdf(xs, mass, sigma)
    else:
        pdf = special.voigt_profile(xs - mass, sigma, 0.5 * width)
    p = pdf.reshape(len(x), sub).mean(1)
    return p / p.sum()


def bkg_probs(a, basis):
    g = a @ basis if len(a) else np.zeros(basis.shape[1])
    g = g - g.max()
    w = np.exp(g)
    return w / w.sum()


class Model:
    """nu_i = n_s * s_i + n_b * b_i(a). Parameters theta = (n_s, n_b, a_1..a_n)."""

    def __init__(self, degree=3, sig=None, mask=None):
        self.degree = degree
        self.basis = legendre_basis(degree)
        self.sig = signal_template() if sig is None else np.asarray(sig, float)
        self.mask = np.ones(NB, bool) if mask is None else np.asarray(mask, bool)

    def nu(self, th):
        return th[0] * self.sig + th[1] * bkg_probs(th[2:], self.basis)

    def nll_grad(self, th, n):
        b = bkg_probs(th[2:], self.basis)
        nu = th[0] * self.sig + th[1] * b
        m = self.mask
        nu_c = np.maximum(nu, 1e-300)
        bad = nu[m] <= 0
        val = float(np.sum(nu[m]) - np.sum(n[m] * np.log(nu_c[m])))
        if np.any(bad):  # a negative expectation anywhere is unphysical
            val += 1e4 + 1e6 * float(np.sum(-nu[m][bad]))
        r = np.where(m, 1.0 - n / nu_c, 0.0)
        g = np.empty(len(th))
        g[0] = float(r @ self.sig)
        g[1] = float(r @ b)
        if len(th) > 2:
            # d b_i / d a_k = b_i (P_ki - <P_k>_b)
            Pk = self.basis
            mean = Pk @ b
            g[2:] = th[1] * ((Pk * b[None, :]) @ r - mean * (b @ r))
        return val, g


def _bounds(model, n, fix_ns):
    ntot = float(np.sum(n[model.mask]))
    # the signal may go negative (needed for q~_mu); nu <= 0 is penalised in nll_grad
    bl = [(fix_ns, fix_ns) if fix_ns is not None else (-0.5 * ntot - 10.0, ntot + 10.0),
          (1e-6, 3.0 * ntot + 30.0)] + [(-40.0, 40.0)] * model.degree
    return bl


def fit(model, n, fix_ns=None, init=None):
    """Minimise the extended NLL. Returns (nll, theta)."""
    n = np.asarray(n, float)
    ntot = float(np.sum(n[model.mask]))
    if init is None:
        init = np.concatenate([[0.0 if fix_ns is None else fix_ns, max(ntot, 1.0)],
                               np.zeros(model.degree)])
    th0 = np.array(init, float)
    if fix_ns is not None:
        th0[0] = fix_ns
    bl = _bounds(model, n, fix_ns)
    th0 = np.clip(th0, [b[0] for b in bl], [b[1] for b in bl])
    best = None
    starts = [th0]
    if init is not None:
        z = th0.copy()
        z[2:] = 0.0
        starts.append(z)
    for s in starts:
        r = optimize.minimize(model.nll_grad, s, args=(n,), jac=True, method='L-BFGS-B',
                              bounds=bl, options=dict(maxiter=2000, ftol=1e-13, gtol=1e-8))
        if best is None or r.fun < best[0]:
            best = (float(r.fun), np.array(r.x))
        if init is None:
            break
    return best


def fits_free_and_bonly(model, n, init=None):
    nll0, th0 = fit(model, n, fix_ns=0.0, init=init)
    i1 = th0.copy()
    i1[0] = max(1.0, 0.02 * np.sum(n))
    nll1, th1 = fit(model, n, init=i1)
    i2 = th0.copy()
    i2[0] = -0.5 * max(1.0, 0.02 * np.sum(n))
    nll2, th2 = fit(model, n, init=i2)
    if nll2 < nll1:
        nll1, th1 = nll2, th2
    if nll1 > nll0:  # free fit can never be worse than the constrained one
        nll1, th1 = nll0, th0
    return (nll0, th0), (nll1, th1)


def q0(model, n, cache=None):
    """Discovery test statistic (one-sided). Returns (q0, n_s_hat, theta_bonly, theta_free)."""
    (nll0, th0), (nll1, th1) = cache or fits_free_and_bonly(model, n)
    q = 2.0 * (nll0 - nll1) if th1[0] > 0 else 0.0
    return max(q, 0.0), float(th1[0]), th0, th1


def qtilde(model, n, mu, free, bonly):
    """q~_mu for an upper limit on n_s = mu (in events)."""
    nll1, th1 = free
    nll0, th0 = bonly
    if th1[0] >= mu:
        return 0.0
    nllm, _ = fit(model, n, fix_ns=mu, init=th1 if th1[0] >= 0 else th0)
    ref = nll1 if th1[0] >= 0 else nll0
    return max(2.0 * (nllm - ref), 0.0)


def asimov_sigma(model, nu_b, mu):
    """sigma of n_s_hat from the background-only Asimov data set: sigma^2 = mu^2 / q_mu,A."""
    nll_b, th_b = fit(model, nu_b)
    nll_m, _ = fit(model, nu_b, fix_ns=mu, init=th_b)
    qa = max(2.0 * (nll_m - nll_b), 1e-12)
    return mu / math.sqrt(qa)


def cls_asymptotic(qt, mu, sigma):
    """CLs for q~_mu (CCGV 2011 eqs. 65-66)."""
    if mu <= 0:
        return 1.0
    qa = (mu / sigma) ** 2
    if qt <= qa:
        pmu = 1.0 - stats.norm.cdf(math.sqrt(qt))
        one_m_pb = stats.norm.cdf(math.sqrt(qa) - math.sqrt(qt))
    else:
        pmu = 1.0 - stats.norm.cdf((qt + qa) / (2.0 * math.sqrt(qa)))
        one_m_pb = stats.norm.cdf((qt - qa) / (2.0 * math.sqrt(qa)))
    return pmu / max(one_m_pb, 1e-300)


def upper_limit(model, n, sigma_of_mu, free, bonly, cl=0.95, tol=0.02):
    """CLs upper limit on n_s (events), asymptotic, by bisection.
    sigma_of_mu: callable giving the Asimov sigma at a given mu."""
    alpha = 1.0 - cl
    nshat = free[1][0]
    lo = max(nshat, 0.0) + 1e-6
    s0 = sigma_of_mu(max(lo, 1.0))
    hi = lo + 6.0 * s0
    for _ in range(6):
        if cls_asymptotic(qtilde(model, n, hi, free, bonly), hi, sigma_of_mu(hi)) < alpha:
            break
        hi += 6.0 * s0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        c = cls_asymptotic(qtilde(model, n, mid, free, bonly), mid, sigma_of_mu(mid))
        if c < alpha:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol * s0:
            break
    return 0.5 * (lo + hi)


def make_sigma_fn(model, nu_b, mus):
    """Interpolated Asimov sigma(mu) on a grid of signal yields."""
    mus = np.asarray(sorted(set(float(m) for m in mus if m > 0)))
    sig = np.array([asimov_sigma(model, nu_b, m) for m in mus])

    def f(mu):
        return float(np.interp(mu, mus, sig))
    return f, dict(zip([round(float(m), 3) for m in mus], [round(float(s), 4) for s in sig]))


def mass_scan(n, degree, masses, width, sigma_frac, bonly_theta=None):
    """Local q0 at each mass hypothesis (width fixed; sigma = sigma_frac * m).
    Returns array of signed local Z (negative when the fitted yield is negative)."""
    n = np.asarray(n, float)
    mb = Model(degree)
    nll0, th0 = fit(mb, n, fix_ns=0.0, init=bonly_theta)
    out = np.zeros(len(masses))
    for j, m in enumerate(masses):
        md = Model(degree, sig=signal_template(m, width, sigma_frac * m))
        best = None
        for s0 in (0.02 * np.sum(n), -0.01 * np.sum(n)):
            i1 = th0.copy()
            i1[0] = s0
            r = fit(md, n, init=i1)
            if best is None or r[0] < best[0]:
                best = r
        nll1, th1 = best
        q = max(2.0 * (nll0 - nll1), 0.0)
        out[j] = math.copysign(math.sqrt(q), th1[0])
    return out


def sideband_mask(lo=26.0, hi=35.0):
    return (CENT < lo) | (CENT > hi)


def choose_degree(n, nmin=1, nmax=5, alpha=0.05):
    """Pre-registered background-degree rule (PLAN v0.4, 5b): fit the background-only model to
    the sidebands 15-26 and 35-50 GeV only (window masked) with degree n = nmin, nmin+1, ...;
    stop at the first n for which adding one more term does not improve -2 ln L by more than
    the chi2(1) quantile at 1 - alpha (3.84). Returns (degree, list of (n, nll))."""
    m = sideband_mask()
    nlls = []
    prev = None
    for d in range(nmin, nmax + 1):
        md = Model(d, mask=m)
        init = None
        if prev is not None:
            init = np.concatenate([prev[1], [0.0]])
        r = fit(md, n, fix_ns=0.0, init=init)
        nlls.append((d, r[0]))
        if prev is not None and 2.0 * (prev[0] - r[0]) < stats.chi2.ppf(1 - alpha, 1):
            return d - 1, nlls
        prev = r
    return nmax, nlls
