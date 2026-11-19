"""fit_table_check: what the printed uncertainties of an extended maximum-likelihood fit allow.

MV2 of Munim, Inc. (mv2@munimtech.com). Apache-2.0. Made with AI agents working in MV2's name.

In an extended unbinned maximum-likelihood fit with a signal yield s and a background yield b,
the likelihood factorises into Poisson(N | s + b) times a mixture term that depends only on the
fraction s / (s + b) and the shape parameters. So the fitted total is s + b = N and its Hesse
variance is exactly N, whatever the shapes:

    Var(s) + Var(b) + 2 rho sigma_s sigma_b = N.

Given printed values s +- ds and b +- db this fixes the correlation rho; |rho| <= 1 is required.
If the printed background is a rescaled number (b_printed = k x b_in_fit, db likewise), the same
identity gives the range of k the printed table allows. Pure standard library.
"""
import math

VERSION = "0.1.0"

# Heister, arXiv:1610.06536 v9, table of the unbinned fit (15-50 GeV)
HEISTER = {"s": 32.31, "ds": 10.87, "b": 1457.06, "db": 89.71,
           "mass": 30.40, "bw_width": 1.78, "gauss_width": 0.74}


def implied_rho(s, ds, b, db, k=1.0):
    """Correlation of (s, b/k) implied by Var(s + b/k) = s + b/k."""
    bk, dbk = b / k, db / k
    n = s + bk
    return (n - ds * ds - dbk * dbk) / (2.0 * ds * dbk)


def allowed_k(s, ds, b, db):
    """Range [k_min, k_max] of the rescaling k for which rho >= -1 (u = 1/k).

    rho >= -1  <=>  s + b u >= (db u - ds)^2  <=>  A u^2 - B u + C <= 0 with
    A = db^2, B = 2 db ds + b, C = ds^2 - s. (rho <= +1 is checked separately by rho_upper_ok.)
    Returns (k_min, k_max); k_max is math.inf when the lower root is <= 0.
    """
    A = db * db
    B = 2.0 * db * ds + b
    C = ds * ds - s
    disc = B * B - 4.0 * A * C
    if disc < 0:
        raise ValueError("no k allows |rho| <= 1")
    r = math.sqrt(disc)
    u_hi = (B + r) / (2.0 * A)
    u_lo = (B - r) / (2.0 * A)
    k_min = 1.0 / u_hi
    k_max = math.inf if u_lo <= 0 else 1.0 / u_lo
    return k_min, k_max


def rho_upper_ok(s, ds, b, db, k):
    return implied_rho(s, ds, b, db, k) <= 1.0


def _voigt_tch(x, m, gamma_fwhm, sigma):
    """Thompson-Cox-Hastings pseudo-Voigt CDF at x (Lorentz FWHM gamma_fwhm, Gauss sigma)."""
    fg = 2.0 * math.sqrt(2.0 * math.log(2.0)) * sigma
    fl = gamma_fwhm
    f = (fg ** 5 + 2.69269 * fg ** 4 * fl + 2.42843 * fg ** 3 * fl ** 2
         + 4.47163 * fg ** 2 * fl ** 3 + 0.07842 * fg * fl ** 4 + fl ** 5) ** 0.2
    q = fl / f
    eta = 1.36603 * q - 0.47719 * q * q + 0.11116 * q ** 3
    hw = f / 2.0
    sg = f / (2.0 * math.sqrt(2.0 * math.log(2.0)))
    cl = 0.5 + math.atan((x - m) / hw) / math.pi
    cg = 0.5 * (1.0 + math.erf((x - m) / (sg * math.sqrt(2.0))))
    return eta * cl + (1.0 - eta) * cg


def signal_in_bins(edges, n_sig=None, m=None, gamma_fwhm=None, sigma=None):
    """Approximate signal counts per bin for Heister's fitted Breit-Wigner x Gauss (pseudo-Voigt).

    The BW width is taken as the full width (an assumption; the paper's table says 'BW width')."""
    h = HEISTER
    n_sig = h["s"] if n_sig is None else n_sig
    m = h["mass"] if m is None else m
    gamma_fwhm = h["bw_width"] if gamma_fwhm is None else gamma_fwhm
    sigma = h["gauss_width"] if sigma is None else sigma
    c = [_voigt_tch(e, m, gamma_fwhm, sigma) for e in edges]
    return [n_sig * (c[i + 1] - c[i]) for i in range(len(edges) - 1)]


def report():
    h = HEISTER
    out = {"tool": "mv2 fit_table_check " + VERSION}
    out["rho_if_printed_is_in_fit"] = implied_rho(h["s"], h["ds"], h["b"], h["db"], 1.0)
    out["k_min"], out["k_max"] = allowed_k(h["s"], h["ds"], h["b"], h["db"])
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
