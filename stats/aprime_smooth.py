# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""aprime_smooth: ALEPH's 30 GeV excess with a SMOOTH background that keeps its counting error
(PLAN amendment 0.24).

NOTE-aprime 0.1 fitted the blind reading of Heister's Fig. 5 (arXiv:1610.06536 v9) with the e mu
template's Poisson error kept bin by bin ("bb", Z0 = 2.66) and with the binned template treated as
exact ("exact", Z0 = 4.18). "bb" ignores that the true background is smooth, so it is conservative.
Job aprime-toys-v1 then showed (table scale, made-up shapes) that smoothing the template with a
1 GeV kernel before treating it as exact removes most of the false-excess inflation. This module
asks what the excess is worth when the background's smoothness IS used and its counting error is
ALSO kept, and calibrates every method with background-only toys at the figure's own scale.

Methods (all with ALEPH's fixed signal: Voigt, 30.40 GeV, Gamma 1.78, sigma 0.745, mu = 1 is
32.31 events in 15-50 GeV, from stats/emuframe.py 0.1.0, fetched and blob-checked):
  bb, exact      emuframe's two treatments (closure with NOTE-aprime 0.1)
  kde05/kde1/kde2  e mu template smoothed with a Gaussian kernel of 0.5/1/2 GeV, treated as exact
                 (the binned analogue of Heister's KDE method; every bin floored at 0.5 counts)
  par2/par3/par4 joint fit: e mu m_i ~ Poisson(T_i), mu mu n_i ~ Poisson(r T_i + mu s_i),
                 T_i = exp(sum_k a_k u_i^k), u = (x - 32.5) / 17.5, k <= degree; a, r free.
                 The template's counting error enters through the fitted a; smoothness is used.
                 par3 is the PRIMARY method (amendment 0.24).

Toys: background-only, drawn from the par3 mu = 0 joint fit to the reading (a smooth truth);
both spectra fluctuated; every method applied to every toy.

    python aprime_smooth.py --fetch-only --emuframe /work/emuframe.py
    python aprime_smooth.py --fig5 aleph-fig5.json --emuframe /work/emuframe.py --out /out \
        --ntoys 10000 --workers 2
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
import urllib.request

VERSION = "mv2 aprime_smooth 0.1.0"
EMUFRAME_URL = ("https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/"
                "main/stats/emuframe.py")
EMUFRAME_BLOB = "d55c900fdb45aa9f8a6099a142079a510c3afdfa"   # stats/emuframe.py 0.1.0
CLOSURE = {"bb": 2.6640384798138936, "exact": 4.178326392781588}   # aprime-aleph-v1
CLOSURE_TOL = 0.005
SEED = 20261120
FLOOR = 0.5
KDE_H = {"kde05": 0.5, "kde1": 1.0, "kde2": 2.0}
PAR_DEG = {"par2": 2, "par3": 3, "par4": 4}
PRIMARY = "par3"
METHODS = ("bb", "exact") + tuple(KDE_H) + tuple(PAR_DEG)
U_CENTRE, U_HALF = 32.5, 17.5
MU_MAX = 20.0

ef = None


# ----------------------------------------------------------------------------- emuframe
def git_blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def fetch_emuframe(dest, tries=10, wait=30):
    """Fetch stats/emuframe.py 0.1.0 to dest (unless present) and check its git blob sha."""
    data = None
    if os.path.exists(dest):
        data = open(dest, "rb").read()
    else:
        for k in range(tries):
            try:
                data = urllib.request.urlopen(EMUFRAME_URL, timeout=60).read()
                break
            except Exception as exc:   # network hiccup: retry
                print("fetch attempt %d failed: %s" % (k + 1, exc), flush=True)
                time.sleep(wait)
        if data is None:
            raise SystemExit("could not fetch emuframe.py")
        with open(dest, "wb") as f:
            f.write(data)
    sha = git_blob_sha(data)
    if sha != EMUFRAME_BLOB:
        raise SystemExit("emuframe.py blob %s != published %s" % (sha, EMUFRAME_BLOB))
    return sha


def bind(module=None, path=None):
    """Use an emuframe module: given, loaded from a path, or imported from sys.path."""
    global ef
    if module is not None:
        ef = module
    elif path is not None:
        spec = importlib.util.spec_from_file_location("emuframe", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ef = mod
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import emuframe as mod   # noqa: E402
        ef = mod
    return ef


# ----------------------------------------------------------------------------- helpers
def centres(edges):
    return [0.5 * (edges[i] + edges[i + 1]) for i in range(len(edges) - 1)]


def smooth(m, edges, h):
    """Spread each bin's counts with a Gaussian kernel of width h (GeV), renormalised per source
    bin inside the range, so the total is preserved (same rule as aprime_toys 0.1.0)."""
    c = centres(edges)
    out = [0.0] * len(m)
    for i, mi in enumerate(m):
        if mi == 0:
            continue
        k = [math.exp(-0.5 * ((cj - c[i]) / h) ** 2) for cj in c]
        tk = sum(k)
        for j in range(len(m)):
            out[j] += mi * k[j] / tk
    return out


def floor(t, lo=FLOOR):
    return [max(x, lo) for x in t]


def z_from_count(k, n):
    """Toy-calibrated Z from k of n toys at or above the observed value. If k == 0 the value is a
    lower bound, computed from the 95 % upper limit on p (3 / n)."""
    if n <= 0:
        return {"p": None, "Z": None, "lower_bound": False}
    if k == 0:
        return {"p": 0.0, "Z": ef.z_from_p(3.0 / n), "lower_bound": True}
    return {"p": k / n, "Z": ef.z_from_p(k / n), "lower_bound": False}


# ----------------------------------------------------------------------------- emuframe methods
def z_emu(n, m, s, model):
    """Z0 and mu_hat with emuframe's fit (model "bb" or "exact")."""
    best = ef.fit(n, m, s, model)
    b0 = ef.fit(n, m, s, model, mu_fixed=0.0)
    q0 = max(0.0, 2.0 * (best["lnL"] - b0["lnL"]))
    return {"Z0": math.sqrt(q0), "mu_hat": best["mu"], "r_hat": best["r"]}


# ----------------------------------------------------------------------------- parametric fit
class ParFit:
    """Joint Poisson fit of the e mu (m) and mu mu (n) spectra with a log-polynomial shape."""

    def __init__(self, edges, s, deg):
        import numpy as np
        self.np = np
        x = np.array(centres(edges))
        w = np.diff(np.array(edges, dtype=float))
        u = (x - U_CENTRE) / U_HALF
        self.U = np.vstack([u ** k for k in range(deg + 1)]).T
        self.lnw = np.log(w)
        self.s = np.array(s, dtype=float)
        self.deg = deg

    def T(self, a):
        np = self.np
        return np.exp(np.clip(self.U @ a + self.lnw, -60.0, 60.0))

    def nll_grad(self, p, n, m):
        np = self.np
        d = self.deg + 1
        a, lnr, mu = p[:d], p[d], p[d + 1]
        T = self.T(a)
        r = math.exp(lnr)
        lam = r * T + mu * self.s
        lam = np.maximum(lam, 1e-300)
        ll = np.sum(m * np.log(T) - T) + np.sum(n * np.log(lam) - lam)
        g_lam = n / lam - 1.0
        ga = self.U.T @ ((m - T) + g_lam * r * T)
        glnr = np.sum(g_lam * r * T)
        gmu = np.sum(g_lam * self.s)
        return -ll, -np.concatenate([ga, [glnr, gmu]])

    def start(self, n, m):
        np = self.np
        y = np.log(np.maximum(m, 0.5))
        wt = np.sqrt(np.maximum(m, 0.5))
        a, *_ = np.linalg.lstsq(self.U * wt[:, None], (y - self.lnw) * wt, rcond=None)
        lnr = math.log(max(n.sum(), 0.5) / max(m.sum(), 0.5))
        return a, lnr

    def _min(self, p0, n, m, mu_bounds):
        from scipy.optimize import minimize
        d = self.deg + 1
        bounds = [(None, None)] * d + [(-10.0, 10.0), mu_bounds]
        res = minimize(self.nll_grad, p0, args=(n, m), jac=True, method="L-BFGS-B",
                       bounds=bounds, options={"maxiter": 5000, "ftol": 1e-14, "gtol": 1e-9})
        return res

    def fit(self, n, m, mu_fixed=None):
        """Returns dict(lnL, mu, r, a). mu >= 0; mu_fixed fixes it."""
        np = self.np
        n = np.asarray(n, dtype=float)
        m = np.asarray(m, dtype=float)
        a, lnr = self.start(n, m)
        if mu_fixed is not None:
            p0 = np.concatenate([a, [lnr, mu_fixed]])
            best = self._min(p0, n, m, (mu_fixed, mu_fixed))
            # polish from the solution once more (L-BFGS-B can stop early on flat valleys)
            best2 = self._min(best.x, n, m, (mu_fixed, mu_fixed))
            if best2.fun < best.fun:
                best = best2
        else:
            b0 = self.fit(n, m, mu_fixed=0.0)
            best = None
            for mu0 in (0.0, 0.8, 2.0):
                p0 = np.concatenate([np.array(b0["a"]), [math.log(b0["r"]), mu0]])
                res = self._min(p0, n, m, (0.0, MU_MAX))
                if best is None or res.fun < best.fun:
                    best = res
            if b0["lnL"] > -best.fun:
                return dict(b0)
        d = self.deg + 1
        return {"lnL": -float(best.fun), "mu": float(best.x[d + 1]),
                "r": math.exp(float(best.x[d])), "a": [float(v) for v in best.x[:d]]}

    def discovery(self, n, m):
        b0 = self.fit(n, m, mu_fixed=0.0)
        best = self.fit(n, m)
        q0 = max(0.0, 2.0 * (best["lnL"] - b0["lnL"]))
        return {"Z0": math.sqrt(q0), "mu_hat": best["mu"], "r_hat": best["r"], "mu0": b0}

    def deviance(self, n, m, fit0):
        """Poisson deviance of a fit over both spectra."""
        np = self.np
        n = np.asarray(n, dtype=float)
        m = np.asarray(m, dtype=float)
        T = self.T(np.array(fit0["a"]))
        lam = fit0["r"] * T + fit0["mu"] * self.s

        def dev(x, mu_):
            t = np.where(x > 0, x * np.log(np.where(x > 0, x, 1.0) / mu_), 0.0)
            return 2.0 * np.sum(t - (x - mu_))
        return float(dev(m, T) + dev(n, lam))


# ----------------------------------------------------------------------------- one data set
def evaluate(edges, n, m, s, pars, methods=METHODS):
    """Z0 of every method on one data set (m = raw e mu counts). pars: {name: ParFit}."""
    out = {}
    for meth in methods:
        if meth == "bb":
            out[meth] = z_emu(n, m, s, "bb")
        elif meth == "exact":
            out[meth] = z_emu(n, floor(m), s, "exact")
        elif meth in KDE_H:
            out[meth] = z_emu(n, floor(smooth(m, edges, KDE_H[meth])), s, "exact")
        elif meth in PAR_DEG:
            d = pars[meth].discovery(n, m)
            out[meth] = {"Z0": d["Z0"], "mu_hat": d["mu_hat"], "r_hat": d["r_hat"]}
            if meth == PRIMARY:
                out[meth]["dev0"] = pars[meth].deviance(n, m, d["mu0"])
    return out


# ----------------------------------------------------------------------------- toys
_G = {}


def _init(emu_path, edges, s, truth_T, truth_r):
    if emu_path:
        bind(path=emu_path)
    _G["edges"], _G["s"] = edges, s
    _G["T"], _G["r"] = truth_T, truth_r
    _G["pars"] = {k: ParFit(edges, s, d) for k, d in PAR_DEG.items()}


def one_toy(idx):
    import numpy as np
    rng = np.random.default_rng(SEED + idx)
    T = np.array(_G["T"])
    n = [int(x) for x in rng.poisson(_G["r"] * T)]
    m = [int(x) for x in rng.poisson(T)]
    res = evaluate(_G["edges"], n, m, _G["s"], _G["pars"])
    row = {"idx": idx}
    for k, v in res.items():
        row[k] = v["Z0"]
    row["dev0"] = res[PRIMARY]["dev0"]
    row["mu_par3"] = res[PRIMARY]["mu_hat"]
    return row


# ----------------------------------------------------------------------------- grades
def grade(obs, cal, rates, gof_p):
    g = {}
    ok = (abs(obs["closure_bb"] - CLOSURE["bb"]) < CLOSURE_TOL
          and abs(obs["closure_exact"] - CLOSURE["exact"]) < CLOSURE_TOL
          and 0.015 <= rates["bb"]["p_ge2"] <= 0.031)
    g["K0"] = "PASS" if ok else "FAIL"
    if not ok:
        for k in ("K1", "K2", "K3", "K4"):
            g[k] = "NOT GRADABLE (K0 failed)"
        return g
    c3 = cal[PRIMARY]
    if c3["lower_bound"]:          # no toy reached the observed value: Z_cal >= bound
        g["K1"] = ("FAIL" if c3["Z"] >= 3.0 else
                   "UNDETERMINED (no toy reached the observed value; lower bound below 3)")
    else:
        g["K1"] = "PASS" if c3["Z"] < 3.0 else "FAIL"
    g["K2"] = "PASS" if 0.012 <= rates[PRIMARY]["p_ge2"] <= 0.035 else "FAIL"
    g["K3"] = "PASS" if gof_p >= 0.01 else "FAIL"
    k1 = cal["kde1"]
    g["K4"] = "PASS" if (not k1["lower_bound"] and not c3["lower_bound"]
                         and abs(k1["Z"] - c3["Z"]) <= 0.3) else "FAIL"
    return g


# ----------------------------------------------------------------------------- driver
def run(fig5, out_dir, ntoys, workers, emu_path):
    import numpy as np
    from multiprocessing import Pool
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    edges, n, v = fig5["edges"], fig5["n"], fig5["v_scaled"]
    r0 = ef.R0_ALEPH
    m = [vi / r0 for vi in v]
    s = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    pars = {k: ParFit(edges, s, d) for k, d in PAR_DEG.items()}
    res = {"version": VERSION, "emuframe": ef.VERSION, "seed": SEED, "r0": r0, "floor": FLOOR,
           "primary": PRIMARY, "n_sum": sum(n), "v_sum": sum(v), "m_sum": sum(m)}
    path = os.path.join(out_dir, "aprime_smooth.json")

    def save():
        res["elapsed_s"] = time.time() - t0
        with open(path, "w") as f:
            json.dump(res, f, indent=1)

    obs = {"closure_bb": z_emu(n, m, s, "bb")["Z0"], "closure_exact": z_emu(n, m, s, "exact")["Z0"]}
    print("CLOSURE bb=%.4f exact=%.4f" % (obs["closure_bb"], obs["closure_exact"]), flush=True)
    obs["methods"] = evaluate(edges, n, m, s, pars)
    for k in METHODS:
        print("OBS %s Z0=%.4f mu_hat=%.4f" % (k, obs["methods"][k]["Z0"], obs["methods"][k]["mu_hat"]),
              flush=True)
    # truth for the toys: par3 joint fit at mu = 0
    f0 = pars[PRIMARY].fit(n, m, mu_fixed=0.0)
    truth_T = [float(x) for x in pars[PRIMARY].T(np.array(f0["a"]))]
    obs["truth"] = {"a": f0["a"], "r": f0["r"], "T": truth_T, "sum_T": sum(truth_T),
                    "sum_rT": f0["r"] * sum(truth_T)}
    obs["truth_window_29_32"] = {"rT": f0["r"] * sum(truth_T[14:17]),
                                 "n": sum(n[14:17]), "v_scaled": sum(v[14:17])}
    print("TRUTH par3 mu=0: r=%.4f sum T=%.1f sum rT=%.1f window rT=%.2f n=%d" % (
        f0["r"], sum(truth_T), f0["r"] * sum(truth_T), obs["truth_window_29_32"]["rT"],
        obs["truth_window_29_32"]["n"]), flush=True)
    res["observed"] = obs
    save()

    rows = []
    with Pool(workers, initializer=_init, initargs=(emu_path, edges, s, truth_T, f0["r"])) as pool:
        for k, row in enumerate(pool.imap_unordered(one_toy, range(ntoys), chunksize=20)):
            rows.append(row)
            if (k + 1) % 500 == 0:
                print("toys done", k + 1, "of", ntoys, round(time.time() - t0), "s", flush=True)
    rows.sort(key=lambda r: r["idx"])
    with open(os.path.join(out_dir, "toys.csv"), "w") as f:
        cols = list(METHODS) + ["dev0", "mu_par3"]
        f.write("idx," + ",".join(cols) + "\n")
        for r in rows:
            f.write("%d,%s\n" % (r["idx"], ",".join("%.5f" % r[c] for c in cols)))

    rates, cal = {}, {}
    for k in METHODS:
        z = [r[k] for r in rows]
        zo = obs["methods"][k]["Z0"]
        rates[k] = {"p_ge2": sum(1 for x in z if x >= 2.0) / len(z),
                    "p_ge3": sum(1 for x in z if x >= 3.0) / len(z),
                    "mean_Z": sum(z) / len(z)}
        kk = sum(1 for x in z if x >= zo - 1e-9)
        cal[k] = dict(z_from_count(kk, len(z)), k=kk, n=len(z), Z_asym=zo)
    dev_obs = obs["methods"][PRIMARY]["dev0"]
    gof_k = sum(1 for r in rows if r["dev0"] >= dev_obs)
    gof_p = gof_k / len(rows)
    res.update({"ntoys": len(rows), "rates": rates, "calibrated": cal,
                "gof": {"dev_obs": dev_obs, "k": gof_k, "p": gof_p,
                        "dev_toy_mean": sum(r["dev0"] for r in rows) / len(rows)},
                "mean_mu_par3_toys": sum(r["mu_par3"] for r in rows) / len(rows)})
    res["grades"] = grade(obs, cal, rates, gof_p)
    save()
    return res


def line(res):
    o, c, r = res["observed"]["methods"], res["calibrated"], res["rates"]
    parts = ["closure bb=%.3f ex=%.3f" % (res["observed"]["closure_bb"],
                                           res["observed"]["closure_exact"])]
    for k in METHODS:
        parts.append("%s %.2f->%s%.2f p2=%.4f p3=%.4f" % (
            k, o[k]["Z0"], ">=" if c[k]["lower_bound"] else "", c[k]["Z"], r[k]["p_ge2"],
            r[k]["p_ge3"]))
    parts.append("par3 mu_hat=%.3f gof p=%.3f" % (o[PRIMARY]["mu_hat"], res["gof"]["p"]))
    parts.append(" ".join("%s %s" % (k, v.split(" ")[0]) for k, v in sorted(res["grades"].items())))
    return "APSMOOTH: " + " | ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fig5")
    ap.add_argument("--out")
    ap.add_argument("--emuframe", required=True, help="path of emuframe.py (fetched if absent)")
    ap.add_argument("--fetch-only", action="store_true")
    ap.add_argument("--ntoys", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(argv)
    sha = fetch_emuframe(a.emuframe)
    print("emuframe blob", sha, flush=True)
    if a.fetch_only:
        return
    bind(path=a.emuframe)
    fig5 = json.load(open(a.fig5))
    print("%s with %s; sum n %d, sum v %.1f" % (VERSION, ef.VERSION, sum(fig5["n"]),
                                                 sum(fig5["v_scaled"])), flush=True)
    res = run(fig5, a.out, a.ntoys, a.workers, os.path.abspath(a.emuframe))
    print(json.dumps({k: res[k] for k in ("rates", "calibrated", "gof", "grades",
                                          "mean_mu_par3_toys")}, indent=1), flush=True)
    print(line(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
