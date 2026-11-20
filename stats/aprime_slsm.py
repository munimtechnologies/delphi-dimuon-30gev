# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""aprime_slsm 0.1.0: ALEPH's 30 GeV excess with a smooth background that keeps its counting
error AND a mu mu / e mu ratio allowed to change with mass (PLAN amendment 0.27 part B, L0-L5).

Two graded results pull opposite ways on the blind reading of Heister's Fig. 5
(arXiv:1610.06536 v9), 15-50 GeV:
* aprime-smooth-v1 (amendment 0.24): a smooth log-cubic background fitted jointly to both spectra
  (stats/aprime_smooth.py, "par3") gives Z0 = 3.13, toy-calibrated 3.35, with a CONSTANT ratio.
* aprime-ext-v1 (amendment 0.23): with the bin-by-bin background ("bb") and a log-linear ratio
  r exp(b (x - 30.40)), Z0 falls from 2.66 to 1.62.
This module puts both into one model:

    e mu  m_i ~ Poisson(T_i),       T_i = exp(sum_k a_k u_i^k) (aprime_smooth.ParFit, k <= 3)
    mu mu n_i ~ Poisson(r exp(b (x_i - 30.40)) T_i + mu s_i)

a, r, b free (b in [-0.2, 0.2] per GeV), mu >= 0, ALEPH's fixed signal shape (emuframe 0.1.0).
Calibrated with background-only toys drawn from the mu = 0 slope fit to the reading.

    python aprime_slsm.py --fig5 aleph-fig5.json --emuframe /work/emuframe.py --out /out \
        --ntoys 10000 --workers 2

Needs stats/aprime_smooth.py 0.1.0 next to this file. Last output line `APSLSM:`.
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import aprime_smooth as asm
except ImportError:
    asm = None

VERSION = "mv2 aprime_slsm 0.1.0"
PIVOT = 30.40
B_BOUNDS = (-0.2, 0.2)
DEG = 3
SEED = 20261121
PAR3_OBS = 3.1339963632770744        # aprime-smooth-v1, observed par3 Z0
PAR3_TOL = 0.005
B_GRID = [-0.05 + 0.0025 * k for k in range(69)]     # -0.05 .. 0.12 per GeV


def signed(q, b):
    q = max(0.0, q)
    return math.copysign(math.sqrt(q), b) if q > 0 else 0.0


def interval(bs, ls, top):
    """1-sigma interval of b from a profile (drop 0.5), linear interpolation; None if open."""
    kb = max(range(len(bs)), key=lambda i: ls[i])
    lo = hi = None
    for k in range(kb, 0, -1):
        if ls[k - 1] < top - 0.5 <= ls[k]:
            f = (ls[k] - (top - 0.5)) / (ls[k] - ls[k - 1])
            lo = bs[k] - f * (bs[k] - bs[k - 1])
            break
    for k in range(kb, len(bs) - 1):
        if ls[k + 1] < top - 0.5 <= ls[k]:
            f = (ls[k] - (top - 0.5)) / (ls[k] - ls[k + 1])
            hi = bs[k] + f * (bs[k + 1] - bs[k])
            break
    return lo, hi


def z_from_count(k, n):
    """Toy-calibrated one-sided Z from k of n toys at or above the observed value."""
    from statistics import NormalDist
    if n <= 0:
        return {"p": None, "Z": None, "lower_bound": False, "k": k, "n": n}
    if k == 0:
        return {"p": 0.0, "Z": NormalDist().inv_cdf(1.0 - 3.0 / n), "lower_bound": True,
                "k": k, "n": n}
    p = k / n
    return {"p": p, "Z": NormalDist().inv_cdf(1.0 - p) if p < 1.0 else float("-inf"),
            "lower_bound": False, "k": k, "n": n}


class SlopeFit:
    """Joint fit of e mu (m) and mu mu (n): log-polynomial T, log-linear ratio, fixed signal."""

    def __init__(self, edges, s, deg=DEG):
        self.base = asm.ParFit(edges, s, deg)
        self.np = self.base.np
        self.dx = self.np.array(asm.centres(edges)) - PIVOT
        self.d = deg + 1

    def nll_grad(self, p, n, m):
        np, base, d = self.np, self.base, self.d
        a, lnr, b, mu = p[:d], p[d], p[d + 1], p[d + 2]
        T = base.T(a)
        w = np.exp(np.clip(lnr + b * self.dx, -60.0, 60.0))
        wT = w * T
        lam = np.maximum(wT + mu * base.s, 1e-300)
        ll = np.sum(m * np.log(T) - T) + np.sum(n * np.log(lam) - lam)
        g = n / lam - 1.0
        ga = base.U.T @ ((m - T) + g * wT)
        return -ll, -np.concatenate([ga, [np.sum(g * wT), np.sum(g * wT * self.dx),
                                          np.sum(g * base.s)]])

    def _min(self, p0, n, m, bb, mb):
        from scipy.optimize import minimize
        bounds = [(None, None)] * self.d + [(-10.0, 10.0), bb, mb]
        opts = {"maxiter": 5000, "ftol": 1e-14, "gtol": 1e-9}
        r1 = minimize(self.nll_grad, p0, args=(n, m), jac=True, method="L-BFGS-B",
                      bounds=bounds, options=opts)
        r2 = minimize(self.nll_grad, r1.x, args=(n, m), jac=True, method="L-BFGS-B",
                      bounds=bounds, options=opts)
        return r2 if r2.fun < r1.fun else r1

    def fit(self, n, m, mu_fixed=None, b_fixed=None):
        np = self.np
        n = np.asarray(n, dtype=float)
        m = np.asarray(m, dtype=float)
        f0 = self.base.fit(n, m, mu_fixed=0.0)
        a0, lnr0 = np.array(f0["a"]), math.log(f0["r"])
        b_starts = [b_fixed] if b_fixed is not None else [0.0, 0.03, -0.03]
        mu_starts = [mu_fixed] if mu_fixed is not None else [0.0, 0.8, 2.0]
        bb = (b_fixed, b_fixed) if b_fixed is not None else B_BOUNDS
        mb = (mu_fixed, mu_fixed) if mu_fixed is not None else (0.0, asm.MU_MAX)
        best = None
        for b0 in b_starts:
            for mu0 in mu_starts:
                res = self._min(np.concatenate([a0, [lnr0, b0, mu0]]), n, m, bb, mb)
                if best is None or res.fun < best.fun:
                    best = res
        d = self.d
        return {"lnL": -float(best.fun), "a": [float(v) for v in best.x[:d]],
                "r": math.exp(float(best.x[d])), "b": float(best.x[d + 1]),
                "mu": float(best.x[d + 2])}

    def discovery(self, n, m, b_fixed=None):
        f0 = self.fit(n, m, mu_fixed=0.0, b_fixed=b_fixed)
        f1 = self.fit(n, m, b_fixed=b_fixed)
        if f0["lnL"] > f1["lnL"]:
            f1 = dict(f0)
        q0 = max(0.0, 2.0 * (f1["lnL"] - f0["lnL"]))
        return {"Z0": math.sqrt(q0), "mu_hat": f1["mu"], "b_hat": f1["b"], "r_hat": f1["r"],
                "b_mu0": f0["b"], "fit0": f0, "fit1": f1}

    def lam(self, fit):
        np = self.np
        T = self.base.T(np.array(fit["a"]))
        return T, fit["r"] * np.exp(fit["b"] * self.dx) * T + fit["mu"] * self.base.s

    def deviance(self, n, m, fit):
        np = self.np
        n = np.asarray(n, dtype=float)
        m = np.asarray(m, dtype=float)
        T, lam = self.lam(fit)

        def dev(x, mu_):
            t = np.where(x > 0, x * np.log(np.where(x > 0, x, 1.0) / mu_), 0.0)
            return 2.0 * float(np.sum(t - (x - mu_)))
        return dev(m, T) + dev(n, lam)


# ----------------------------------------------------------------------------- grades
def grade(obs, cal, rates, gof_p, tests_ok=True):
    g = {}
    ok = tests_ok and abs(obs["closure_b0"] - PAR3_OBS) < PAR3_TOL \
        and abs(obs["closure_parfit"] - PAR3_OBS) < PAR3_TOL
    g["L0"] = "PASS" if ok else "FAIL"
    if not ok:
        for k in ("L1", "L2", "L3", "L4", "L5"):
            g[k] = "NOT GRADABLE (L0 failed)"
        return g
    c = cal["slope"]
    if c["lower_bound"]:
        g["L1"] = "FAIL" if c["Z"] >= 3.0 else "UNDETERMINED (no toy reached the observed value)"
        g["L2"] = "FAIL" if c["Z"] >= 2.0 else "UNDETERMINED (no toy reached the observed value)"
    else:
        g["L1"] = "PASS" if c["Z"] < 3.0 else "FAIL"
        g["L2"] = "PASS" if c["Z"] < 2.0 else "FAIL"
    g["L3"] = "PASS" if (obs["slope_mu0"]["b_hat"] > 0 and obs["slope_mu0"]["Z"] >= 2.0) else "FAIL"
    g["L4"] = "PASS" if 0.012 <= rates["slope"]["p_ge2"] <= 0.035 else "FAIL"
    g["L5"] = "PASS" if gof_p >= 0.01 else "FAIL"
    return g


# ----------------------------------------------------------------------------- toys
_G = {}


def _init(emu_path, edges, s, T, lam_n):
    if emu_path:
        asm.bind(path=emu_path)
    _G["sf"] = SlopeFit(edges, s)
    _G["T"], _G["lam_n"] = T, lam_n


def one_toy(idx):
    import numpy as np
    rng = np.random.default_rng(SEED + idx)
    n = rng.poisson(np.array(_G["lam_n"])).astype(float)
    m = rng.poisson(np.array(_G["T"])).astype(float)
    sf = _G["sf"]
    ds = sf.discovery(n, m)
    dc = sf.base.discovery(n, m)              # constant ratio, par3 (information)
    return {"idx": idx, "slope": ds["Z0"], "const": dc["Z0"],
            "dev0": sf.deviance(n, m, ds["fit0"]), "mu": ds["mu_hat"], "b0": ds["b_mu0"]}


# ----------------------------------------------------------------------------- driver
def observe(sf, n, m):
    obs = {}
    c0 = sf.base.discovery(n, m)
    obs["closure_parfit"] = c0["Z0"]
    d0 = sf.discovery(n, m, b_fixed=0.0)
    obs["closure_b0"] = d0["Z0"]
    obs["const"] = {"Z0": d0["Z0"], "mu_hat": d0["mu_hat"], "lnL1": d0["fit1"]["lnL"],
                    "lnL0": d0["fit0"]["lnL"]}
    ds = sf.discovery(n, m)
    obs["slope"] = {"Z0": ds["Z0"], "mu_hat": ds["mu_hat"], "b_hat": ds["b_hat"],
                    "b_mu0": ds["b_mu0"], "r_hat": ds["r_hat"], "lnL1": ds["fit1"]["lnL"],
                    "lnL0": ds["fit0"]["lnL"]}
    obs["slope_mu0"] = {"b_hat": ds["fit0"]["b"],
                        "Z": signed(2.0 * (ds["fit0"]["lnL"] - d0["fit0"]["lnL"]), ds["fit0"]["b"])}
    obs["slope_signal_floated"] = {
        "b_hat": ds["fit1"]["b"],
        "Z": signed(2.0 * (ds["fit1"]["lnL"] - d0["fit1"]["lnL"]), ds["fit1"]["b"])}
    ls = [sf.fit(n, m, mu_fixed=0.0, b_fixed=b)["lnL"] for b in B_GRID]
    top = max(ds["fit0"]["lnL"], max(ls))
    lo, hi = interval(B_GRID, ls, top)
    obs["slope_mu0"].update({"b_lo": lo, "b_hi": hi,
                             "sigma_b": None if lo is None or hi is None else 0.5 * (hi - lo)})
    return obs, ds


def run(fig5, out_dir, ntoys, workers, emu_path):
    import numpy as np
    from multiprocessing import Pool
    ef = asm.ef
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    edges, n, v = fig5["edges"], fig5["n"], fig5["v_scaled"]
    m = [vi / ef.R0_ALEPH for vi in v]
    s = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    sf = SlopeFit(edges, s)
    res = {"version": VERSION, "aprime_smooth": asm.VERSION, "emuframe": ef.VERSION,
           "seed": SEED, "pivot": PIVOT, "deg": DEG, "b_bounds": list(B_BOUNDS)}
    path = os.path.join(out_dir, "aprime_slsm.json")

    def save():
        res["elapsed_s"] = time.time() - t0
        with open(path, "w") as f:
            json.dump(res, f, indent=1)

    obs, ds = observe(sf, n, m)
    res["observed"] = obs
    print("CLOSURE par3 ParFit %.4f, SlopeFit b=0 %.4f (want %.4f)" % (
        obs["closure_parfit"], obs["closure_b0"], PAR3_OBS), flush=True)
    print("OBS const Z0=%.4f mu=%.3f | slope Z0=%.4f mu=%.3f b=%.4f | slope at mu=0 b=%.4f "
          "[%s, %s] Z=%.3f | slope signal floated b=%.4f Z=%.3f (%.0f s)" % (
              obs["const"]["Z0"], obs["const"]["mu_hat"], obs["slope"]["Z0"],
              obs["slope"]["mu_hat"], obs["slope"]["b_hat"], obs["slope_mu0"]["b_hat"],
              obs["slope_mu0"]["b_lo"], obs["slope_mu0"]["b_hi"], obs["slope_mu0"]["Z"],
              obs["slope_signal_floated"]["b_hat"], obs["slope_signal_floated"]["Z"],
              time.time() - t0), flush=True)
    T, lam_n = sf.lam(ds["fit0"])
    T, lam_n = [float(x) for x in T], [float(x) for x in lam_n]
    obs["truth"] = {"a": ds["fit0"]["a"], "r": ds["fit0"]["r"], "b": ds["fit0"]["b"],
                    "sum_T": sum(T), "sum_lam_n": sum(lam_n),
                    "window_29_32": {"bkg": sum(lam_n[14:17]), "n": sum(n[14:17])}}
    obs["dev0"] = sf.deviance(n, m, ds["fit0"])
    save()

    rows = []
    with Pool(workers, initializer=_init, initargs=(emu_path, edges, s, T, lam_n)) as pool:
        for k, row in enumerate(pool.imap_unordered(one_toy, range(ntoys), chunksize=20)):
            rows.append(row)
            if (k + 1) % 500 == 0:
                print("toys done", k + 1, "of", ntoys, round(time.time() - t0), "s", flush=True)
    rows.sort(key=lambda r: r["idx"])
    with open(os.path.join(out_dir, "toys.csv"), "w") as f:
        f.write("idx,slope,const,dev0,mu,b0\n")
        for r in rows:
            f.write("%d,%.5f,%.5f,%.5f,%.5f,%.5f\n" % (r["idx"], r["slope"], r["const"],
                                                        r["dev0"], r["mu"], r["b0"]))
    rates, cal = {}, {}
    for k, zo in (("slope", obs["slope"]["Z0"]), ("const", obs["const"]["Z0"])):
        z = [r[k] for r in rows]
        rates[k] = {"p_ge2": sum(1 for x in z if x >= 2.0) / len(z),
                    "p_ge3": sum(1 for x in z if x >= 3.0) / len(z), "mean_Z": sum(z) / len(z)}
        cal[k] = dict(z_from_count(sum(1 for x in z if x >= zo - 1e-9), len(z)), Z_asym=zo)
    gof_k = sum(1 for r in rows if r["dev0"] >= obs["dev0"])
    res.update({"ntoys": len(rows), "rates": rates, "calibrated": cal,
                "gof": {"dev_obs": obs["dev0"], "k": gof_k, "p": gof_k / len(rows)},
                "mean_mu_toys": sum(r["mu"] for r in rows) / len(rows),
                "mean_b0_toys": sum(r["b0"] for r in rows) / len(rows)})
    res["grades"] = grade(obs, cal, rates, res["gof"]["p"])
    save()
    return res


def line(res):
    o, c, r, g = res["observed"], res["calibrated"], res["rates"], res["grades"]
    f = lambda x: "na" if x is None else "%.4f" % x
    return ("APSLSM: closure parfit=%.4f b0=%.4f | const Z0 %.3f -> cal(slope truth) %s%.2f | "
            "slope Z0 %.3f -> cal %s%.2f (k=%d) mu=%.3f b=%.4f | b(mu=0)=%.4f [%s,%s] Zs=%.2f | "
            "sig-floated b=%.4f Zs=%.2f | rates slope p2=%.4f p3=%.4f | gof p=%.3f | %s" % (
                o["closure_parfit"], o["closure_b0"], o["const"]["Z0"],
                ">=" if c["const"]["lower_bound"] else "", c["const"]["Z"], o["slope"]["Z0"],
                ">=" if c["slope"]["lower_bound"] else "", c["slope"]["Z"], c["slope"]["k"],
                o["slope"]["mu_hat"], o["slope"]["b_hat"], o["slope_mu0"]["b_hat"],
                f(o["slope_mu0"]["b_lo"]), f(o["slope_mu0"]["b_hi"]), o["slope_mu0"]["Z"],
                o["slope_signal_floated"]["b_hat"], o["slope_signal_floated"]["Z"],
                r["slope"]["p_ge2"], r["slope"]["p_ge3"], res["gof"]["p"],
                " ".join("%s %s" % (k, v.split(" ")[0]) for k, v in sorted(g.items()))))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--emuframe", required=True, help="path of emuframe.py (fetched if absent)")
    ap.add_argument("--ntoys", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(argv)
    if asm is None:
        raise SystemExit("aprime_smooth.py must sit next to this file")
    print("emuframe blob", asm.fetch_emuframe(a.emuframe), flush=True)
    asm.bind(path=a.emuframe)
    fig5 = json.load(open(a.fig5))
    print("%s with %s and %s; sum n %d, sum v %.1f" % (
        VERSION, asm.VERSION, asm.ef.VERSION, sum(fig5["n"]), sum(fig5["v_scaled"])), flush=True)
    res = run(fig5, a.out, a.ntoys, a.workers, os.path.abspath(a.emuframe))
    print(json.dumps({k: res[k] for k in ("rates", "calibrated", "gof", "grades")}, indent=1),
          flush=True)
    print(line(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
