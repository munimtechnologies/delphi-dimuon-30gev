# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""aprime_cross 0.1.0: is the rising mu mu / e mu ratio in ALEPH's 15-50 GeV data also in ALEPH's
own simulation, and in its di-electrons? (PLAN amendment 0.25, tests C0, M0-M3, E0-E3)

aprime-ext-v1 (amendment 0.23, graded in NOTE-aprime 0.3 sec. 8) found that a log-linear
mu mu / e mu ratio

    r_i = r * exp(b * (x_i - 30.40)),   x_i = bin centre (GeV),

fitted at mu = 0 to the blind reading of Heister's Fig. 5 (15-50 GeV) gives b = 0.0266 per GeV
(Z_slope 2.26), and that with b free the 30 GeV excess falls from Z0 = 2.66 to 1.62. This module
asks where the slope comes from, with two new blind readings of the same paper:

* MC: Heister's Fig. 4 (opposite-sign mu mu against e mu, ALEPH simulation only). Does the
  simulation predict the slope (M1-M3)?
* EE: Heister's di-electron spectrum (unbinned-fit figure), against the same e mu template. Is
  the slope shared by e e pairs (E1-E2), or only in mu mu?

Self-contained (no fetch). The likelihood is the same as stats/emuframe.py 0.1.0 /
stats/aprime_ext.py 0.1.0 ("bb": every bin's e mu expectation t_i free, Barlow-Beeston; "exact":
t_i = m_i fixed); test_aprime_cross.py checks it against those modules when they are importable.

    python aprime_cross.py --fig5 aleph-fig5.json --out /out                     (closure C0 only)
    python aprime_cross.py --fig5 aleph-fig5.json --mc aleph-mc4.json --ee aleph-ee.json --out /out
"""
import argparse
import json
import math
import os
import sys
import time

VERSION = "mv2 aprime_cross 0.1.0"
PIVOT = 30.40                  # ratio quoted at ALEPH's fitted mass
B_RANGE = (-0.2, 0.2)          # slope search range, per GeV
LNR_HALF = 4.0                 # ln r searched within +-4 of ln(N/M) (at the pivot)
R0 = 1.0 / (2.0 * 0.94)        # plotted e mu = raw e mu * R0 (Heister Sec. 3.4.1), 0.532
LO, HI = 15.0, 50.0
M0, GAMMA0, SIGMA0 = 30.40, 1.78, 0.745       # ALEPH mu mu signal (emuframe 0.1.0)
N_ALEPH = 32.31                               # mu = 1, mu mu, 15-50 GeV
M_EE, SIGMA_EE, N_EE = 29.18, 0.70, 8.00      # ALEPH e e fit (Heister v9 Sec. 4.9); Gamma as mu mu
UNIVERSALITY = 0.94 ** 2                      # e e / mu mu signal if electrons are 6 % less efficient

# aprime-ext-v1, model bb, 15-50 GeV (NOTE-aprime 0.3 sec. 8)
EXT = {"Z0_const": 2.664038479814576, "Z0_slope": 1.6214319866480056,
       "b_mu0": 0.02663398007642196, "Z_slope": 2.256379371992658}
CLOSURE_TOL = {"Z0_const": 0.01, "Z0_slope": 0.01, "b_mu0": 0.001, "Z_slope": 0.02}
B_HALF_DATA = 0.5 * EXT["b_mu0"]              # M1 threshold, written before any MC reading


# ----------------------------------------------------------------------------- maths
def phi(z):
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def cdf_voigt(x, m, gamma, sigma, n_theta=4000):
    """P(mass < x), Breit-Wigner (FWHM gamma) convolved with a Gaussian (sigma); midpoint rule
    in theta with t = m + (gamma/2) tan(theta), as emuframe 0.1.0."""
    hw = 0.5 * gamma
    if hw <= 0.0:
        return phi((x - m) / sigma)
    if sigma <= 0.0:
        return 0.5 + math.atan((x - m) / hw) / math.pi
    s = 0.0
    for k in range(n_theta):
        th = -0.5 * math.pi + (k + 0.5) * math.pi / n_theta
        s += phi((x - m - hw * math.tan(th)) / sigma)
    return s / n_theta


def s_template(edges, n_sig=N_ALEPH, m=M0, gamma=GAMMA0, sigma=SIGMA0, norm=(LO, HI),
               n_theta=4000):
    """Signal per bin, n_sig events inside `norm`."""
    c = [cdf_voigt(x, m, gamma, sigma, n_theta) for x in edges]
    tot = cdf_voigt(norm[1], m, gamma, sigma, n_theta) - cdf_voigt(norm[0], m, gamma, sigma, n_theta)
    return [n_sig * (c[i + 1] - c[i]) / tot for i in range(len(edges) - 1)]


def xlogy(x, y):
    return 0.0 if x == 0 else x * math.log(y)


def t_hat(n, m, s, r, mu):
    """t >= 0 maximising n ln(r t + mu s) - (r t + mu s) + m ln t - t (emuframe 0.1.0)."""
    ms = mu * s
    if ms == 0.0:
        return (n + m) / (r + 1.0)
    a = r * (r + 1.0)
    b = -(r * (n + m) - (r + 1.0) * ms)
    c = -m * ms
    disc = math.sqrt(b * b - 4.0 * a * c)
    if b > 0.0:
        return -2.0 * c / (b + disc)
    return (-b + disc) / (2.0 * a)


def lnl(n, m, s, rs, mu, model):
    """Log-likelihood (constants dropped) with a per-bin ratio rs[i]."""
    tot = 0.0
    if model == "bb":
        for ni, mi, si, ri in zip(n, m, s, rs):
            t = t_hat(ni, mi, si, ri, mu)
            lam = ri * t + mu * si
            if (ni > 0 and lam <= 0.0) or (mi > 0 and t <= 0.0):
                return float("-inf")
            tot += xlogy(ni, lam) - lam + xlogy(mi, t) - t
        return tot
    if model != "exact":
        raise ValueError(model)
    for ni, mi, si, ri in zip(n, m, s, rs):
        lam = ri * mi + mu * si
        if lam <= 0.0:
            if ni > 0:
                return float("-inf")
            continue
        tot += xlogy(ni, lam) - lam
    return tot


def golden_max(f, a, b, iters=60):
    g = (math.sqrt(5.0) - 1.0) / 2.0
    c, d = b - g * (b - a), a + g * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(iters):
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


def scan_then_golden(f, a, b, n=40):
    xs = [a + (b - a) * k / n for k in range(n + 1)]
    vals = [f(x) for x in xs]
    k = max(range(n + 1), key=lambda i: vals[i])
    x, v = golden_max(f, xs[max(k - 1, 0)], xs[min(k + 1, n)])
    return (xs[k], vals[k]) if vals[k] > v else (x, v)


# ----------------------------------------------------------------------------- binning
def centres(edges):
    return [0.5 * (edges[i] + edges[i + 1]) for i in range(len(edges) - 1)]


def merge(edges, vals, new_edges):
    """Sum `vals` (on `edges`) into the bins of `new_edges`, a subset of `edges`."""
    pos = {round(e, 6): i for i, e in enumerate(edges)}
    out = []
    for a, b in zip(new_edges[:-1], new_edges[1:]):
        ia, ib = pos.get(round(a, 6)), pos.get(round(b, 6))
        if ia is None or ib is None or ib <= ia:
            raise ValueError("edge %s or %s not on the original grid" % (a, b))
        part = vals[ia:ib]
        if any(v is None for v in part):
            raise ValueError("unreadable value in %s-%s" % (a, b))
        out.append(float(sum(part)))
    return out


def common_edges(e1, e2, lo=LO, hi=HI):
    """Edges present in both grids within [lo, hi]; lo and hi must be in both."""
    s1 = {round(e, 6) for e in e1}
    s2 = {round(e, 6) for e in e2}
    com = sorted(e for e in s1 & s2 if lo - 1e-6 <= e <= hi + 1e-6)
    if not com or abs(com[0] - lo) > 1e-6 or abs(com[-1] - hi) > 1e-6:
        raise ValueError("grids do not both contain %s and %s" % (lo, hi))
    return com


# ----------------------------------------------------------------------------- fits
def _x0(n, m):
    big_n, big_m = sum(n), sum(m)
    return math.log(big_n / big_m) if big_n > 0 and big_m > 0 else 0.0


def prof(n, m, s, mu, model, xc, b=None):
    """max over ln r at fixed mu; over b in B_RANGE too when b is None (b = 0.0: constant)."""
    x0 = _x0(n, m)

    def inner(bb):
        w = [math.exp(bb * (xi - PIVOT)) for xi in xc]
        f = lambda x: lnl(n, m, s, [math.exp(x) * wi for wi in w], mu, model)
        return scan_then_golden(f, x0 - LNR_HALF, x0 + LNR_HALF, n=24)

    if b is None:
        bb, _ = scan_then_golden(lambda q: inner(q)[1], B_RANGE[0], B_RANGE[1], n=40)
    else:
        bb = b
    x, v = inner(bb)
    return {"r": math.exp(x), "b": bb, "lnL": v}


def fit_mu(pf, mu_hi=4.0):
    for _ in range(5):
        mu, v = scan_then_golden(lambda u: pf(u)["lnL"], 0.0, mu_hi, n=40)
        if mu < 0.95 * mu_hi:
            break
        mu_hi *= 3.0
    p0 = pf(0.0)
    if p0["lnL"] >= v:
        mu = 0.0
    best = dict(pf(mu))
    best["mu"] = mu
    return best, p0


def discovery(n, m, s, model, xc, b=None):
    """Z0 of the signal with the ratio constant (b=0.0), slope free (b=None) or slope fixed."""
    pf = lambda mu: prof(n, m, s, mu, model, xc, b)
    best, p0 = fit_mu(pf)
    q0 = max(0.0, 2.0 * (best["lnL"] - p0["lnL"]))
    return {"mu_hat": best["mu"], "r_hat": best["r"], "b_hat": best["b"], "r_mu0": p0["r"],
            "b_mu0": p0["b"], "q0": q0, "Z0": math.sqrt(q0), "lnL_best": best["lnL"],
            "lnL_mu0": p0["lnL"]}


def slope_mu0(n, m, xc, model="bb", grid=801):
    """At mu = 0: b_hat, signed Z of the slope against a constant ratio, and the 1-sigma
    interval of b (profile drop 0.5, linear interpolation on a grid over B_RANGE)."""
    s0 = [0.0] * len(n)
    free = prof(n, m, s0, 0.0, model, xc, None)
    const = prof(n, m, s0, 0.0, model, xc, 0.0)
    q = max(0.0, 2.0 * (free["lnL"] - const["lnL"]))
    z = math.copysign(math.sqrt(q), free["b"]) if q > 0 else 0.0
    bs = [B_RANGE[0] + (B_RANGE[1] - B_RANGE[0]) * k / (grid - 1) for k in range(grid)]
    ls = [prof(n, m, s0, 0.0, model, xc, bb)["lnL"] for bb in bs]
    top = max(free["lnL"], max(ls))
    lo_b = hi_b = None
    k_best = max(range(grid), key=lambda i: ls[i])
    for k in range(k_best, 0, -1):
        if ls[k - 1] < top - 0.5 <= ls[k]:
            f = (ls[k] - (top - 0.5)) / (ls[k] - ls[k - 1])
            lo_b = bs[k] - f * (bs[k] - bs[k - 1])
            break
    for k in range(k_best, grid - 1):
        if ls[k + 1] < top - 0.5 <= ls[k]:
            f = (ls[k] - (top - 0.5)) / (ls[k] - ls[k + 1])
            hi_b = bs[k] + f * (bs[k + 1] - bs[k])
            break
    sig = 0.5 * (hi_b - lo_b) if (lo_b is not None and hi_b is not None) else None
    return {"b_hat": free["b"], "r_hat": free["r"], "Z_slope": z, "b_lo": lo_b, "b_hi": hi_b,
            "sigma_b": sig, "lnL_free": free["lnL"], "lnL_const": const["lnL"]}


# ----------------------------------------------------------------------------- inputs
def load(path):
    with open(path) as f:
        return json.load(f)


def data_window(fig5):
    """The Fig. 5 reading on [LO, HI]: edges, mu mu counts n, raw e mu m = v / R0."""
    edges = common_edges(fig5["edges"], fig5["edges"])
    n = merge(fig5["edges"], fig5["n"], edges)
    v = merge(fig5["edges"], fig5["v_scaled"], edges)
    return edges, n, [x / R0 for x in v]


# ----------------------------------------------------------------------------- analyses
def closure(fig5):
    edges, n, m = data_window(fig5)
    xc = centres(edges)
    s = s_template(edges)
    const = discovery(n, m, s, "bb", xc, 0.0)
    slope = discovery(n, m, s, "bb", xc, None)
    sl = slope_mu0(n, m, xc, "bb")
    got = {"Z0_const": const["Z0"], "Z0_slope": slope["Z0"], "b_mu0": sl["b_hat"],
           "Z_slope": sl["Z_slope"]}
    ok = all(abs(got[k] - EXT[k]) < CLOSURE_TOL[k] for k in EXT)
    return {"got": got, "want": EXT, "C0": "PASS" if ok else "FAIL", "const": const,
            "slope": slope, "slope_mu0": sl, "edges": edges}


def analyse_mc(mc, fig5, data_slope):
    """M0-M3. mc = {"edges", "mumu", "emu"} as plotted (normalised to the data mu mu yield)."""
    out = {}
    try:
        edges = common_edges(mc["edges"], mc["edges"])
        a = merge(mc["edges"], mc["mumu"], edges)
        c = merge(mc["edges"], mc["emu"], edges)
    except (ValueError, KeyError) as exc:
        out["M0"] = "FAIL (%s)" % exc
        return out
    out["M0"] = "PASS" if all(x >= 0 for x in a + c) and sum(c) > 0 else "FAIL (negative or empty)"
    if out["M0"] != "PASS":
        return out
    # MC as pseudo-counts of data size: mu mu as plotted, e mu raw = plotted / R0
    m = [x / R0 for x in c]
    xc = centres(edges)
    sl = slope_mu0(a, m, xc, "bb")
    out.update({"edges": edges, "sum_mumu": sum(a), "sum_emu_plotted": sum(c), "slope": sl})
    lo25 = [i for i, x in enumerate(xc) if x < 25.0]
    hi25 = [i for i, x in enumerate(xc) if x >= 25.0]
    out["ratio_15_25"] = sum(a[i] for i in lo25) / max(1e-12, sum(c[i] for i in lo25))
    out["ratio_25_50"] = sum(a[i] for i in hi25) / max(1e-12, sum(c[i] for i in hi25))
    out["M1"] = "PASS" if sl["b_hat"] >= B_HALF_DATA else "FAIL"
    sd, smc = data_slope["sigma_b"], sl["sigma_b"]
    if sd is None or smc is None:
        out["M2"] = "NOT GRADABLE (no 1-sigma interval)"
    else:
        out["M2_pull"] = (data_slope["b_hat"] - sl["b_hat"]) / math.sqrt(sd * sd + smc * smc)
        out["M2"] = "PASS" if abs(out["M2_pull"]) < 2.0 else "FAIL"
    dedges, n, md = data_window(fig5)
    s = s_template(dedges)
    fixed = discovery(n, md, s, "bb", centres(dedges), sl["b_hat"])
    out["data_Z0_bfixed_mc"] = fixed
    out["M3"] = "PASS" if fixed["Z0"] < 2.0 else "FAIL"
    return out


def analyse_ee(ee, fig5, data_slope):
    """E0-E3. ee = {"edges", "n"}: the e e data counts as plotted; e mu template from Fig. 5."""
    out = {}
    try:
        edges = common_edges(ee["edges"], fig5["edges"])
        n = merge(ee["edges"], ee["n"], edges)
        v = merge(fig5["edges"], fig5["v_scaled"], edges)
    except (ValueError, KeyError) as exc:
        out["E0"] = "FAIL (%s)" % exc
        return out
    out["E0"] = "PASS" if all(x >= 0 for x in n) else "FAIL (negative count)"
    if out["E0"] != "PASS":
        return out
    m = [x / R0 for x in v]
    xc = centres(edges)
    sl = slope_mu0(n, m, xc, "bb")
    out.update({"edges": edges, "sum_ee": sum(n), "slope": sl})
    lo25 = [i for i, x in enumerate(xc) if x < 25.0]
    hi25 = [i for i, x in enumerate(xc) if x >= 25.0]
    out["ee_over_v_15_25"] = sum(n[i] for i in lo25) / max(1e-12, sum(v[i] for i in lo25))
    out["ee_over_v_25_50"] = sum(n[i] for i in hi25) / max(1e-12, sum(v[i] for i in hi25))
    out["E1"] = "PASS" if (sl["b_hat"] > 0 and sl["Z_slope"] >= 2.0) else "FAIL"
    sd, se = data_slope["sigma_b"], sl["sigma_b"]
    if sd is None or se is None:
        out["E2"] = "NOT GRADABLE (no 1-sigma interval)"
    else:
        out["E2_pull"] = (data_slope["b_hat"] - sl["b_hat"]) / math.sqrt(sd * sd + se * se)
        out["E2"] = "PASS" if abs(out["E2_pull"]) < 2.0 else "FAIL"
    # E3 (information): e e signal at ALEPH's e e fit values, constant ratio and free slope
    s = s_template(edges, N_EE, M_EE, GAMMA0, SIGMA_EE)
    c = discovery(n, m, s, "bb", xc, 0.0)
    f = discovery(n, m, s, "bb", xc, None)
    out["E3"] = {"const": c, "slope": f, "events_const": c["mu_hat"] * N_EE,
                 "events_slope": f["mu_hat"] * N_EE}
    return out


def universality(ee_res, mumu_events):
    """e e signal events expected from mu mu under lepton universality (information)."""
    return {"expected_ee": UNIVERSALITY * mumu_events,
            "fitted_ee_const": ee_res["E3"]["events_const"]}


def apcross_line(res):
    c = res["closure"]
    parts = ["C0 %s Z0c=%.3f Z0s=%.3f b=%.4f Zs=%.3f sb=%s" % (
        c["C0"], c["got"]["Z0_const"], c["got"]["Z0_slope"], c["got"]["b_mu0"],
        c["got"]["Z_slope"], _f(c["slope_mu0"]["sigma_b"]))]
    mc = res.get("mc")
    if mc is not None:
        if "slope" in mc:
            parts.append("MC b=%.4f sb=%s Zs=%.2f r1525=%.3f r2550=%.3f pull=%s Z0fix=%.3f | "
                         "M0 %s M1 %s M2 %s M3 %s" % (
                             mc["slope"]["b_hat"], _f(mc["slope"]["sigma_b"]),
                             mc["slope"]["Z_slope"], mc["ratio_15_25"], mc["ratio_25_50"],
                             _f(mc.get("M2_pull")), mc["data_Z0_bfixed_mc"]["Z0"], mc["M0"],
                             mc["M1"], mc["M2"], mc["M3"]))
        else:
            parts.append("MC M0 %s" % mc.get("M0"))
    ee = res.get("ee")
    if ee is not None:
        if "slope" in ee:
            parts.append("EE sum=%.0f b=%.4f sb=%s Zs=%.2f q1525=%.3f q2550=%.3f pull=%s "
                         "Nc=%.2f Ns=%.2f Z0c=%.2f Z0s=%.2f | E0 %s E1 %s E2 %s" % (
                             ee["sum_ee"], ee["slope"]["b_hat"], _f(ee["slope"]["sigma_b"]),
                             ee["slope"]["Z_slope"], ee["ee_over_v_15_25"],
                             ee["ee_over_v_25_50"], _f(ee.get("E2_pull")),
                             ee["E3"]["events_const"], ee["E3"]["events_slope"],
                             ee["E3"]["const"]["Z0"], ee["E3"]["slope"]["Z0"], ee["E0"],
                             ee["E1"], ee["E2"]))
        else:
            parts.append("EE E0 %s" % ee.get("E0"))
    return "APCROSS: " + " | ".join(parts)


def _f(x):
    return "na" if x is None else "%.4f" % x


def run(fig5_path, mc_path=None, ee_path=None, out_dir=None):
    t0 = time.time()
    fig5 = load(fig5_path)
    res = {"version": VERSION, "pivot": PIVOT, "r0": R0, "b_range": list(B_RANGE)}
    res["closure"] = closure(fig5)
    print("CLOSURE: %s got %s" % (res["closure"]["C0"], json.dumps(res["closure"]["got"])),
          flush=True)
    sl = res["closure"]["slope_mu0"]
    print("DATA SLOPE: b=%.5f [%s, %s] sigma_b=%s Z=%.3f (%.0f s)" % (
        sl["b_hat"], _f(sl["b_lo"]), _f(sl["b_hi"]), _f(sl["sigma_b"]), sl["Z_slope"],
        time.time() - t0), flush=True)
    gated = res["closure"]["C0"] == "PASS"
    if mc_path:
        res["mc"] = analyse_mc(load(mc_path), fig5, sl) if gated else {
            "M0": "NOT GRADABLE (C0 failed)"}
        print("MC: %s" % json.dumps({k: v for k, v in res["mc"].items()
                                      if k.startswith("M") or k.startswith("ratio")}), flush=True)
    if ee_path:
        res["ee"] = analyse_ee(load(ee_path), fig5, sl) if gated else {
            "E0": "NOT GRADABLE (C0 failed)"}
        if "E3" in res["ee"]:
            res["ee"]["universality"] = universality(
                res["ee"], res["closure"]["const"]["mu_hat"] * N_ALEPH)
        print("EE: %s" % json.dumps({k: v for k, v in res["ee"].items()
                                      if k.startswith("E") and k != "E3"}), flush=True)
    res["elapsed_s"] = time.time() - t0
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "aprime_cross.json"), "w") as f:
            json.dump(res, f, indent=1, default=str)
    line = apcross_line(res)
    print(line, flush=True)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--mc")
    ap.add_argument("--ee")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    print("%s; python %s" % (VERSION, sys.version.split()[0]), flush=True)
    run(a.fig5, a.mc, a.ee, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
