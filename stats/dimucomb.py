"""dimucomb: one signal strength fitted across several dimuon categories (PLAN v0.9, section 5e).

Why (written before any DELPHI mass in the window is seen): ALEPH's excess (arXiv:1610.06536)
was found in b-tagged events, with a tag that keeps about 38 % of Z -> b bbar events. If the
excess is a boson X produced together with b quarks (Z -> b bbar X, or Z -> h A with A -> b bbar),
then for every tagged signal event about (1 - 0.38) / 0.38 = 1.63 more fail the tag. DELPHI's
"not b-tagged" opposite-sign dimuon spectrum (dimusel category os_mumu_untagged, disjoint from
os_mumu_btag) therefore carries most of such a signal. A simultaneous fit of the two categories,
with one signal strength mu and independent smooth backgrounds, is the most sensitive test of
that hypothesis that the pre-registered pipeline can do.

Model, per category c (histograms on the dimustat grid: 700 bins of 50 MeV over 15-50 GeV):
    nu_c = mu * N_c * s_c + n_b,c * b_c(a_c)
mu = 1 means an ALEPH-sized signal; N_c is the pre-registered expected signal yield in category
c at mu = 1; s_c the signal template; b_c the log-Legendre background of dimustat with its own
degree (chosen per category by the pre-registered sideband rule, dimustat.choose_degree).
theta = [mu, n_b,0, a_0..., n_b,1, a_1..., ...].

Test statistics as in dimustat (Cowan, Cranmer, Gross, Vitells, EPJC 71 (2011) 1554), with the
signal strength mu (not an event count) as the parameter of interest.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import math

import numpy as np
from scipy import optimize

import dimustat as ds

VERSION = "mv2 dimucomb 0.1.0"
ALEPH_EPS_B = 0.38  # ALEPH's event-level b efficiency at its working point (arXiv:1610.06536 sec. 3.2)


def nexp_untagged(n_tagged, eps_b, rho_measured=None):
    """Pre-registered expected signal in the not-tagged category (PLAN v0.9, 5e).

    n_tagged: expected tagged signal at mu = 1 (the N_exp of section 4e).
    eps_b: DELPHI's event-level b efficiency at the chosen working point (data, section 4g).
    rho_measured: signal tag efficiency / inclusive b efficiency (DELSIM signal over data
        double-tag), or None if not measured. The rule uses rho = max(1, rho_measured): rho > 1
        lowers the untagged prediction, rho < 1 would raise it, so taking at least 1 is the
        conservative choice for an exclusion.
    With the same rho for ALEPH and DELPHI, N_tagged does not depend on rho and
    N_untagged = N_tagged * (1 - eps_b * rho) / (eps_b * rho)."""
    if not 0.0 < eps_b < 1.0:
        raise ValueError("eps_b must be in (0, 1)")
    rho = 1.0 if rho_measured is None else max(1.0, float(rho_measured))
    e = eps_b * rho
    if e >= 1.0:
        return 0.0
    return float(n_tagged) * (1.0 - e) / e


class Joint:
    """Several categories sharing one signal strength mu."""

    def __init__(self, nexp, degrees, sigs=None, masks=None):
        self.nexp = [float(x) for x in nexp]
        self.C = len(self.nexp)
        if len(degrees) != self.C:
            raise ValueError("one degree per category")
        self.models = []
        for c in range(self.C):
            sig = None if sigs is None else sigs[c]
            mask = None if masks is None else masks[c]
            self.models.append(ds.Model(int(degrees[c]), sig=sig, mask=mask))
        self.slices = []
        k = 1
        for m in self.models:
            self.slices.append(slice(k, k + 1 + m.degree))
            k += 1 + m.degree
        self.npar = k

    def split(self, th):
        """Per-category dimustat parameter vectors [n_s, n_b, a...]."""
        th = np.asarray(th, float)
        return [np.concatenate([[th[0] * self.nexp[c]], th[self.slices[c]]])
                for c in range(self.C)]

    def nu(self, th):
        return [m.nu(t) for m, t in zip(self.models, self.split(th))]

    def nll_grad(self, th, ns):
        val = 0.0
        g = np.zeros(self.npar)
        for c, (m, thc) in enumerate(zip(self.models, self.split(th))):
            v, gc = m.nll_grad(thc, ns[c])
            val += v
            g[0] += self.nexp[c] * gc[0]
            g[self.slices[c]] = gc[1:]
        return val, g


def _arr(ns):
    return [np.asarray(n, float) for n in ns]


def _bounds(J, ns, fix_mu):
    tots = [float(np.sum(n[m.mask])) for n, m in zip(ns, J.models)]
    sn = max(sum(J.nexp), 1e-9)
    if fix_mu is not None:
        bl = [(fix_mu, fix_mu)]
    else:
        bl = [(-(0.5 * sum(tots) + 10.0) / sn, (sum(tots) + 10.0) / sn)]
    for t, m in zip(tots, J.models):
        bl += [(1e-6, 3.0 * t + 30.0)] + [(-40.0, 40.0)] * m.degree
    return bl, tots


def fit(J, ns, fix_mu=None, init=None):
    """Minimise the summed extended NLL. Returns (nll, theta)."""
    ns = _arr(ns)
    bl, tots = _bounds(J, ns, fix_mu)
    given = init is not None
    if not given:
        init = [0.0 if fix_mu is None else fix_mu]
        for t, m in zip(tots, J.models):
            init += [max(t, 1.0)] + [0.0] * m.degree
    th0 = np.array(init, float)
    if fix_mu is not None:
        th0[0] = fix_mu
    lo = np.array([b[0] for b in bl])
    hi = np.array([b[1] for b in bl])
    th0 = np.clip(th0, lo, hi)
    starts = [th0]
    if given:
        z = th0.copy()
        for c, m in enumerate(J.models):
            s = J.slices[c]
            z[s.start + 1:s.stop] = 0.0
        starts.append(z)
    best = None
    for s in starts:
        r = optimize.minimize(J.nll_grad, s, args=(ns,), jac=True, method='L-BFGS-B',
                              bounds=bl, options=dict(maxiter=4000, ftol=1e-13, gtol=1e-8))
        if best is None or r.fun < best[0]:
            best = (float(r.fun), np.array(r.x))
    return best


def fits_free_and_bonly(J, ns, init=None):
    ns = _arr(ns)
    nll0, th0 = fit(J, ns, fix_mu=0.0, init=init)
    step = max(1.0, 0.02 * sum(float(np.sum(n)) for n in ns)) / max(sum(J.nexp), 1e-9)
    best = None
    for s0 in (step, -0.5 * step):
        i1 = th0.copy()
        i1[0] = s0
        r = fit(J, ns, init=i1)
        if best is None or r[0] < best[0]:
            best = r
    nll1, th1 = best
    if nll1 > nll0:
        nll1, th1 = nll0, th0
    return (nll0, th0), (nll1, th1)


def q0(J, ns, cache=None):
    """One-sided discovery statistic. Returns (q0, mu_hat, theta_bonly, theta_free)."""
    (nll0, th0), (nll1, th1) = cache or fits_free_and_bonly(J, ns)
    q = 2.0 * (nll0 - nll1) if th1[0] > 0 else 0.0
    return max(q, 0.0), float(th1[0]), th0, th1


def qtilde(J, ns, mu, free, bonly):
    nll1, th1 = free
    nll0, th0 = bonly
    if th1[0] >= mu:
        return 0.0
    nllm, _ = fit(J, ns, fix_mu=mu, init=th1 if th1[0] >= 0 else th0)
    ref = nll1 if th1[0] >= 0 else nll0
    return max(2.0 * (nllm - ref), 0.0)


def asimov_sigma(J, nus, mu):
    """sigma(mu_hat) from a background-only Asimov set: sigma^2 = mu^2 / q_mu,A."""
    nll_b, th_b = fit(J, nus)
    nll_m, _ = fit(J, nus, fix_mu=mu, init=th_b)
    qa = max(2.0 * (nll_m - nll_b), 1e-12)
    return mu / math.sqrt(qa)


def make_sigma_fn(J, nus, mus=(0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)):
    mus = np.asarray(sorted(set(float(m) for m in mus if m > 0)))
    sig = np.array([asimov_sigma(J, nus, m) for m in mus])

    def f(mu):
        return float(np.interp(mu, mus, sig))
    return f, {str(round(float(m), 3)): round(float(s), 5) for m, s in zip(mus, sig)}


def bonly_asimov(J, th_bonly):
    """Background-only Asimov histograms from a fitted parameter vector (mu set to 0)."""
    th = np.array(th_bonly, float)
    th[0] = 0.0
    return J.nu(th)


def upper_limit(J, ns, sigma_of_mu, free, bonly, cl=0.95, tol=0.02):
    """Asymptotic CLs upper limit on mu (bisection)."""
    alpha = 1.0 - cl
    lo = max(free[1][0], 0.0) + 1e-6
    s0 = sigma_of_mu(max(lo, 0.5))
    hi = lo + 6.0 * s0
    for _ in range(6):
        if ds.cls_asymptotic(qtilde(J, ns, hi, free, bonly), hi, sigma_of_mu(hi)) < alpha:
            break
        hi += 6.0 * s0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        c = ds.cls_asymptotic(qtilde(J, ns, mid, free, bonly), mid, sigma_of_mu(mid))
        if c < alpha:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol * s0:
            break
    return 0.5 * (lo + hi)


def analyse(ns, nexp, sigs=None, sigma_fn=None):
    """The pre-registered procedure of PLAN v0.9 5e on real (or toy) histograms.

    1. degree per category by the sideband rule (dimustat.choose_degree);
    2. joint b-only and free fits; q0 and Z0; q at mu = 1;
    3. CLs upper limit on mu, sigma from the Asimov set of the b-only fit (or sigma_fn);
    4. outcome: EXCLUDED (limit < 1), COMPATIBLE (2 Delta lnL < 1 at mu = 1 and Z0 >= 2),
       INCONCLUSIVE otherwise (the same labels as section 5)."""
    ns = _arr(ns)
    degrees = [ds.choose_degree(n)[0] for n in ns]
    J = Joint(nexp, degrees, sigs)
    bonly, free = fits_free_and_bonly(J, ns)
    qq, muhat, _, _ = q0(J, ns, cache=(bonly, free))
    z0 = math.sqrt(qq)
    nll1 = fit(J, ns, fix_mu=1.0, init=free[1])[0]
    q1 = max(2.0 * (nll1 - free[0]), 0.0)
    if sigma_fn is None:
        sigma_fn, _ = make_sigma_fn(J, bonly_asimov(J, bonly[1]))
    ul = upper_limit(J, ns, sigma_fn, free, bonly)
    if ul < 1.0:
        oc = 'EXCLUDED'
    elif q1 < 1.0 and z0 >= 2.0:
        oc = 'COMPATIBLE'
    else:
        oc = 'INCONCLUSIVE'
    return dict(degrees=degrees, muhat=muhat, z0=z0, q1=q1, ul=ul, outcome=oc)
