"""bkgsys: background-shape systematics for the DELPHI test of the ALEPH 30 GeV dimuon excess
(PLAN v0.12, section 5g). Written BEFORE any DELPHI dimuon mass in the 26-35 GeV window is seen;
no DELPHI data are used here.

Why (finding of job dimu-combcast-v1, 2026-11-18): on noise-free (Asimov) pseudo-data whose
not-b-tagged background is a mixture of a Z -> b bbar power law (m^-1) and a softer non-b part
(m^-3), the pre-registered sideband degree rule of 5b (dimustat.choose_degree) keeps a
degree-1 log-Legendre background, and the fit then returns a signal strength of 0.51 for an
injected ALEPH-sized signal (mu = 1): a spurious signal of about -0.5 in mu, i.e. -17 events, or
-0.7 statistical standard deviations. A negative spurious signal makes a false EXCLUSION of the
ALEPH boson more likely. The sideband rule alone does not protect the untagged category.

This module provides three things, all on the dimustat grid (700 bins of 50 MeV, 15-50 GeV):
  1. degree_curves: -2 ln L(mu) at fixed signal strength on a mu grid, for each background
     degree (profiled over the background normalisation and shape), with warm starts;
  2. spurious_table / choose_degree_spurious: the spurious signal of each degree on a
     background-only template (the "spurious-signal test" of ATLAS H -> gamma gamma, e.g.
     Phys. Rev. D 90 (2014) 112015), and the lowest degree whose |spurious signal| is below
     max_frac (0.2) of its statistical standard deviation;
  3. envelope: the discrete-profiling method of Dauncey, Kenzie, Wardle and Davies,
     JINST 10 (2015) P04015 (arXiv:1408.6865): at each mu take the minimum over degrees of
     -2 ln L + penalty x (number of shape parameters), penalty 1 nominal.
Categories are independent apart from mu, so a joint envelope is the sum of the per-category
envelopes (the minimum over degrees separates by category at fixed mu).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import math

import numpy as np
from scipy import stats

import dimustat as ds

VERSION = "mv2 bkgsys 0.1.0"
DEGREES = (1, 2, 3, 4, 5)
PENALTY = 1.0
MAX_FRAC = 0.2
GRID = np.round(np.arange(-40, 81) * 0.05, 6)  # mu = -2.00 ... 4.00, includes 0 and 1


def degree_curves(n, nexp, sig, degrees=DEGREES, grid=GRID):
    """-2 ln L at fixed mu (n_s = mu * nexp) for each degree; array (len(degrees), len(grid)).
    Each curve is scanned outward from the grid point nearest mu = 0 with warm starts."""
    n = np.asarray(n, float)
    grid = np.asarray(grid, float)
    out = np.empty((len(degrees), len(grid)))
    i0 = int(np.argmin(np.abs(grid)))
    for j, d in enumerate(degrees):
        md = ds.Model(int(d), sig=sig)
        nll, th0 = ds.fit(md, n, fix_ns=float(grid[i0]) * nexp)
        out[j, i0] = 2.0 * nll
        for idx in (range(i0 + 1, len(grid)), range(i0 - 1, -1, -1)):
            th = th0
            for i in idx:
                nll, th = ds.fit(md, n, fix_ns=float(grid[i]) * nexp, init=th)
                out[j, i] = 2.0 * nll
    return out


def envelope(curves, degrees=DEGREES, penalty=PENALTY):
    """Minimum over degrees of curve + penalty * degree. Returns (E, index of the chosen degree)."""
    pen = penalty * np.asarray(degrees, float)[:, None]
    c = np.asarray(curves, float) + pen
    return c.min(axis=0), c.argmin(axis=0)


def _crossing(grid, E, i_from, emin, level, step):
    """Linear interpolation of the first grid point, walking from i_from in direction step,
    where E - emin reaches level. nan if never."""
    i = i_from
    while 0 <= i + step < len(grid):
        j = i + step
        if E[j] - emin >= level:
            a, b = E[i] - emin, E[j] - emin
            t = (level - a) / (b - a) if b != a else 0.0
            return float(grid[i] + t * (grid[j] - grid[i]))
        i = j
    return float('nan')


def profile_summary(grid, E):
    """muhat (parabolic refinement), minimum, signed Z0 = sqrt(E(0) - Emin) (0 if muhat <= 0),
    one-sigma crossings (Delta = 1) and the 95 % one-sided crossing (Delta = 3.84) above muhat."""
    grid = np.asarray(grid, float)
    E = np.asarray(E, float)
    k = int(np.argmin(E))
    muhat, emin = float(grid[k]), float(E[k])
    if 0 < k < len(grid) - 1:
        em, e0, ep = E[k - 1], E[k], E[k + 1]
        den = em - 2.0 * e0 + ep
        if den > 0:
            h = grid[k + 1] - grid[k]
            muhat = float(grid[k] - 0.5 * h * (ep - em) / den)
            emin = float(e0 - (ep - em) ** 2 / (8.0 * den))
    i0 = int(np.argmin(np.abs(grid)))
    q0 = max(float(E[i0]) - emin, 0.0) if muhat > 0 else 0.0
    up1 = _crossing(grid, E, k, emin, 1.0, +1)
    dn1 = _crossing(grid, E, k, emin, 1.0, -1)
    up95 = _crossing(grid, E, k, emin, stats.chi2.ppf(0.95, 1), +1)
    i1 = int(np.argmin(np.abs(grid - 1.0)))
    return dict(muhat=round(muhat, 4), z0=round(math.sqrt(q0), 4),
                sigma_up=round(up1 - muhat, 4), sigma_down=round(muhat - dn1, 4),
                mu95=round(up95, 4), ul_sens=round(up95 - muhat, 4),
                q1=round(max(float(E[i1]) - emin, 0.0), 4))


def spurious_table(nu_b, nexp, sig, degrees=DEGREES, grid=GRID, curves=None):
    """Spurious signal of each degree on a background-only template nu_b (no signal in it):
    mu_spur = fitted mu, sigma = its statistical standard deviation (Delta(-2 ln L) = 1 above the
    minimum, i.e. at the template's own statistics), frac = mu_spur / sigma."""
    if curves is None:
        curves = degree_curves(nu_b, nexp, sig, degrees, grid)
    rows = []
    for j, d in enumerate(degrees):
        s = profile_summary(grid, curves[j])
        sig_ = s['sigma_up']
        frac = s['muhat'] / sig_ if sig_ and sig_ == sig_ else float('nan')
        rows.append(dict(degree=int(d), mu_spur=s['muhat'], n_spur=round(s['muhat'] * nexp, 3),
                         sigma=sig_, frac=round(frac, 4)))
    return rows


def choose_degree_spurious(table, max_frac=MAX_FRAC):
    """Lowest degree with |frac| < max_frac; if none, the degree with the smallest |frac|."""
    for r in table:
        if abs(r['frac']) < max_frac:
            return r['degree']
    return min(table, key=lambda r: abs(r['frac']) if r['frac'] == r['frac'] else 1e9)['degree']


def cls_upper_limit(grid, E, sigma_fn, alpha=0.05):
    """Asymptotic CLs upper limit on mu from a profile curve E(mu) (= -2 ln L up to a constant),
    with q~_mu (CCGV 2011): reference is min E if muhat >= 0, else E(0). sigma_fn(mu) gives the
    Asimov standard deviation. Linear interpolation between grid points in log CLs."""
    grid = np.asarray(grid, float)
    E = np.asarray(E, float)
    s = profile_summary(grid, E)
    muhat = s['muhat']
    i0 = int(np.argmin(np.abs(grid)))
    ref = float(E.min()) if muhat >= 0 else float(E[i0])
    prev = None
    for i, mu in enumerate(grid):
        if mu <= max(muhat, 0.0):
            continue
        qt = max(float(E[i]) - ref, 0.0)
        c = ds.cls_asymptotic(qt, float(mu), sigma_fn(float(mu)))
        if c < alpha:
            if prev is None:
                return float(mu)
            (m0, c0) = prev
            l0, l1, la = math.log(max(c0, 1e-300)), math.log(max(c, 1e-300)), math.log(alpha)
            t = (l0 - la) / (l0 - l1) if l0 != l1 else 1.0
            return float(m0 + t * (mu - m0))
        prev = (float(mu), c)
    return float('nan')


def sigma_fn_from_asimov(grid, E_asimov_bonly):
    """sigma(mu) = mu / sqrt(q_A(mu)), q_A(mu) = E_A(mu) - E_A(muhat_A), from a background-only
    Asimov profile (mu > muhat_A only). Interpolated on the grid; constant beyond its ends."""
    grid = np.asarray(grid, float)
    E = np.asarray(E_asimov_bonly, float)
    s = profile_summary(grid, E)
    m0 = s['muhat']
    emin = float(E.min())
    mus, sg = [], []
    for i, mu in enumerate(grid):
        if mu - m0 > 0.05:
            qa = max(float(E[i]) - emin, 1e-12)
            mus.append(float(mu - m0))
            sg.append((mu - m0) / math.sqrt(qa))
    mus, sg = np.array(mus), np.array(sg)

    def f(mu):
        return float(np.interp(mu, mus, sg))
    return f
