# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""ssframe 0.1.0: ALEPH's 30 GeV excess in its own SMOOTH frame (par3) with the mu mu / e mu
ratio's slope Gaussian-constrained by ALEPH's same-sign muon pairs, toy-calibrated
(PLAN amendment 0.30, tests P0-P4).

Written and published BEFORE job sscontrol-v1 (amendment 0.28) returned, so the control slope
it uses had not been seen by anyone when the tests below were fixed.

* Control slope, exactly as sscontrol 0.1.0 defines it (its helpers and dmcratio / aprime_cross
  are imported unchanged): window W = [15, hi) with every value readable (hi = 38 GeV on the
  committed readings); at zero signal, model "bb", b_SS and b_emu against ALEPH's simulation;
  b_ctrl = b_SS - b_emu, sigma_ctrl = hypot(sigma_SS, sigma_emu).
* Excess: the Fig. 5 reading, 15-50 GeV, aprime_slsm 0.1.0's likelihood (smooth log-cubic e mu
  shape fitted jointly to both spectra, ratio r exp(b (x - 30.40)), ALEPH's fixed signal shape)
  plus a Gaussian constraint term -0.5 ((b - b_ctrl) / sigma_ctrl)^2. Z0 = sqrt(q0) from the
  constrained profile likelihood.
* Calibration: background-only toys drawn from the constrained mu = 0 fit (a, r, b~); in each toy
  both spectra are Poisson-fluctuated AND the auxiliary control value is redrawn,
  b_aux ~ N(b~, sigma_ctrl). Toys are saved as they finish; the run stops submitting at a time
  budget; grades use the contiguous prefix of finished toys and need >= MIN_TOYS of them.

    python ssframe.py --fig5 aleph-fig5.json --dmc aleph-dmc21.json --emu aleph-emu3.json \
        --emuframe /work/emuframe.py --out /out --ntoys 6000 --workers 4 --budget-s 13000

Needs aprime_slsm.py, aprime_smooth.py, sscontrol.py, dmcratio.py and aprime_cross.py next to
this file. Last output line `SSFRAME:`.
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import aprime_slsm as sl
except ImportError:          # pure helpers below stay testable without it
    sl = None
try:
    import sscontrol as ssc
except ImportError:
    ssc = None

VERSION = "mv2 ssframe 0.1.0"
SEED = 20261122
MIN_TOYS = 1000
SLOPE_FREE_OBS = 2.2953      # aprime-slsm-v1 observed par3 Z0 with the slope free (amendment 0.29)
SLOPE_FREE_TOL = 0.01
LOOSE = (0.0, 10.0)          # a constraint this loose must reproduce the slope-free Z0
LOOSE_TOL = 0.01
B_BOUNDS = (-0.2, 0.2)
TESTS = ("P1", "P2", "P3", "P4")


# ----------------------------------------------------------------------------- pure helpers
def clamp(b, lo=B_BOUNDS[0], hi=B_BOUNDS[1]):
    return min(hi, max(lo, b))


def prefix(rows):
    """Rows whose idx form the longest run 0..K-1 with every toy finished, sorted by idx."""
    by = {r["idx"]: r for r in rows}
    out = []
    k = 0
    while k in by:
        out.append(by[k])
        k += 1
    return out


def z_from_count(k, n):
    """Toy-calibrated one-sided Z from k of n toys at or above the observed value; k = 0 gives a
    lower bound from p < 3 / n (same rule as aprime_slsm 0.1.0)."""
    from statistics import NormalDist
    if n <= 0:
        return {"p": None, "Z": None, "lower_bound": False, "k": k, "n": n}
    if k == 0:
        return {"p": 0.0, "Z": NormalDist().inv_cdf(1.0 - 3.0 / n), "lower_bound": True,
                "k": k, "n": n}
    p = k / n
    return {"p": p, "Z": NormalDist().inv_cdf(1.0 - p) if p < 1.0 else float("-inf"),
            "lower_bound": False, "k": k, "n": n}


def gate(obs):
    """P0 of amendment 0.30 from the observed-part dict built by observe()."""
    why = []
    c = obs.get("control") or {}
    if not c.get("dmc_closure_ok"):
        why.append("dmcratio-v1 closure")
    if c.get("window_hi") is None or abs(c["window_hi"] - 38.0) > 1e-9 or not c.get("window_ok"):
        why.append("window")
    if c.get("sigma_ctrl") is None:
        why.append("no control interval")
    if abs(obs.get("closure_b0", 0.0) - (sl.PAR3_OBS if sl else 3.1339963632770744)) >= 0.005:
        why.append("par3 b=0 closure")
    if abs(obs.get("closure_free", 0.0) - SLOPE_FREE_OBS) >= SLOPE_FREE_TOL:
        why.append("slope-free closure")
    if abs(obs.get("closure_loose", 0.0) - obs.get("closure_free", 1e9)) >= LOOSE_TOL:
        why.append("loose-constraint closure")
    return ("PASS", []) if not why else ("FAIL", why)


def grade(obs, rows, min_toys=MIN_TOYS):
    """P0-P4 of amendment 0.30 on a contiguous prefix of toy rows."""
    g = {}
    p0, why = gate(obs)
    g["P0"] = p0 if p0 == "PASS" else "FAIL (%s)" % ", ".join(why)
    if p0 != "PASS":
        for k in TESTS:
            g[k] = "NOT GRADABLE (P0 failed)"
        return g, None
    if len(rows) < min_toys:
        for k in TESTS:
            g[k] = "NOT GRADABLE (only %d toys in the finished prefix, fewer than %d)" % (
                len(rows), min_toys)
        return g, None
    zo = obs["constrained"]["Z0"]
    z = [r["Z0"] for r in rows]
    cal = dict(z_from_count(sum(1 for x in z if x >= zo - 1e-9), len(z)), Z_asym=zo)
    p_ge2 = sum(1 for x in z if x >= 2.0) / len(z)
    gof_k = sum(1 for r in rows if r["dev0"] >= obs["dev0"])
    st = {"calibrated": cal, "p_ge2": p_ge2, "p_ge3": sum(1 for x in z if x >= 3.0) / len(z),
          "mean_Z": sum(z) / len(z), "gof": {"dev_obs": obs["dev0"], "k": gof_k,
                                             "p": gof_k / len(rows)},
          "mean_mu_toys": sum(r["mu"] for r in rows) / len(rows),
          "mean_b0_toys": sum(r["b0"] for r in rows) / len(rows), "ntoys": len(rows)}
    if cal["lower_bound"]:
        g["P1"] = "FAIL" if cal["Z"] >= 3.0 else "UNDETERMINED (no toy reached the observed value)"
        g["P2"] = "FAIL" if cal["Z"] >= 2.0 else "UNDETERMINED (no toy reached the observed value)"
    else:
        g["P1"] = "PASS" if cal["Z"] < 3.0 else "FAIL"
        g["P2"] = "PASS" if cal["Z"] < 2.0 else "FAIL"
    g["P3"] = "PASS" if st["gof"]["p"] >= 0.01 else "FAIL"
    g["P4"] = "PASS" if 0.012 <= p_ge2 <= 0.035 else "FAIL"
    return g, st


# ----------------------------------------------------------------------------- constrained fit
def make_fit_class():
    """ConstrainedSlopeFit, built on aprime_slsm.SlopeFit (imported unchanged)."""

    class ConstrainedSlopeFit(sl.SlopeFit):
        """aprime_slsm's joint likelihood with -0.5 ((b - bc) / sc)^2 added."""

        def __init__(self, edges, s, bc, sc, deg=sl.DEG):
            sl.SlopeFit.__init__(self, edges, s, deg)
            self.set_constraint(bc, sc)

        def set_constraint(self, bc, sc):
            if not sc > 0:
                raise ValueError("sigma of the constraint must be positive")
            self.bc, self.sc = float(bc), float(sc)

        def nll_grad(self, p, n, m):
            f, g = sl.SlopeFit.nll_grad(self, p, n, m)
            z = (p[self.d + 1] - self.bc) / self.sc
            g = g.copy()
            g[self.d + 1] += z / self.sc
            return f + 0.5 * z * z, g

        def fit(self, n, m, mu_fixed=None, b_fixed=None):
            best = sl.SlopeFit.fit(self, n, m, mu_fixed=mu_fixed, b_fixed=b_fixed)
            if b_fixed is not None:
                return best
            # one more start at the constraint's centre (the parent starts at 0, +-0.03)
            np = self.np
            n_ = np.asarray(n, dtype=float)
            m_ = np.asarray(m, dtype=float)
            f0 = self.base.fit(n_, m_, mu_fixed=0.0)
            a0, lnr0 = np.array(f0["a"]), math.log(f0["r"])
            mb = (mu_fixed, mu_fixed) if mu_fixed is not None else (0.0, sl.asm.MU_MAX)
            for mu0 in ([mu_fixed] if mu_fixed is not None else [0.0, 0.8, 2.0]):
                res = self._min(np.concatenate([a0, [lnr0, clamp(self.bc), mu0]]), n_, m_,
                                B_BOUNDS, mb)
                if -float(res.fun) > best["lnL"]:
                    d = self.d
                    best = {"lnL": -float(res.fun), "a": [float(v) for v in res.x[:d]],
                            "r": math.exp(float(res.x[d])), "b": float(res.x[d + 1]),
                            "mu": float(res.x[d + 2])}
            return best

    return ConstrainedSlopeFit


# ----------------------------------------------------------------------------- control slope
def control(fig5, dmc, emu):
    """b_ctrl and sigma_ctrl exactly as sscontrol 0.1.0 computes them, plus its two gates."""
    ac, dm = ssc.ac, ssc.dm
    out = {}
    edges = [float(e) for e in dmc["edges"]]
    if [float(e) for e in emu["edges"]] != edges or [float(e) for e in fig5["edges"]] != edges:
        raise SystemExit("the three readings must share one grid")
    idx = dm.window(edges)
    e50 = edges[idx[0]:idx[-1] + 2]
    x50 = ac.centres(e50)
    z = {k: [dm.fill(dmc[k], dmc["marks"][k], dmc["edges"], 0.0)[i] for i in idx]
         for k in ("os_data", "os_mc", "ss_data", "ss_mc")}
    b_os50 = dm.slope(z["os_data"], z["os_mc"], x50)["b_hat"]
    b_ss50 = dm.slope(z["ss_data"], z["ss_mc"], x50)["b_hat"]
    out["dmc_closure"] = {"b_os_zero": b_os50, "b_ss_zero": b_ss50, "want": ssc.DMC_V1}
    out["dmc_closure_ok"] = (abs(b_os50 - ssc.DMC_V1["b_os_zero"]) < ssc.DMC_TOL
                             and abs(b_ss50 - ssc.DMC_V1["b_ss_zero"]) < ssc.DMC_TOL)
    raw = {k: dm.fill(dmc[k], dmc["marks"][k], dmc["edges"], None)
           for k in ("os_data", "os_mc", "ss_data", "ss_mc")}
    raw["emu_data"] = dm.fill(emu["data"], emu["marks"]["data"], emu["edges"], None)
    raw["emu_mc"] = dm.fill(emu["mc"], emu["marks"]["mc"], emu["edges"], None)
    hi = ssc.readable_hi(edges, list(raw.values()))
    out["window_hi"] = hi
    out["window_ok"] = False
    out["b_ctrl"] = out["sigma_ctrl"] = None
    if hi is None:
        return out
    we = ssc.sub_edges(edges, ssc.LO, hi)
    xw = ac.centres(we)
    w = {k: ssc.cut(edges, v, ssc.LO, hi) for k, v in raw.items()}
    out["window_ok"] = all(v is not None and v >= 0 for vals in w.values() for v in vals)
    if not out["window_ok"]:
        return out
    r0 = ac.R0
    ss = dm.slope(w["ss_data"], w["ss_mc"], xw)
    em = dm.slope([v / r0 for v in w["emu_data"]], [v / r0 for v in w["emu_mc"]], xw)
    out["ss"] = {k: ss.get(k) for k in ("b_hat", "sigma_b", "Z_slope", "b_lo", "b_hi")}
    out["emu"] = {k: em.get(k) for k in ("b_hat", "sigma_b", "Z_slope", "b_lo", "b_hi")}
    out.update(ssc.control_slope(ss, em))
    return out


# ----------------------------------------------------------------------------- observed
def observe(fig5, dmc, emu):
    asm = sl.asm
    ef = asm.ef
    edges, n, v = fig5["edges"], fig5["n"], fig5["v_scaled"]
    m = [vi / ef.R0_ALEPH for vi in v]
    s = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    obs = {"control": control(fig5, dmc, emu)}
    c = obs["control"]
    print("CONTROL dmc closure %s (OS %.5f SS %.5f) | window 15-%s ok %s | b_SS %s sb %s | "
          "b_emu %s sb %s | b_ctrl %s +- %s" % (
              "PASS" if c["dmc_closure_ok"] else "FAIL", c["dmc_closure"]["b_os_zero"],
              c["dmc_closure"]["b_ss_zero"], c["window_hi"], c["window_ok"],
              _f(c.get("ss", {}).get("b_hat")), _f(c.get("ss", {}).get("sigma_b")),
              _f(c.get("emu", {}).get("b_hat")), _f(c.get("emu", {}).get("sigma_b")),
              _f(c["b_ctrl"]), _f(c["sigma_ctrl"])), flush=True)
    sf = sl.SlopeFit(edges, s)
    d0 = sf.discovery(n, m, b_fixed=0.0)
    dfree = sf.discovery(n, m)
    obs["closure_b0"] = d0["Z0"]
    obs["closure_free"] = dfree["Z0"]
    CSF = make_fit_class()
    loose = CSF(edges, s, LOOSE[0], LOOSE[1]).discovery(n, m)
    obs["closure_loose"] = loose["Z0"]
    obs["free"] = {"Z0": dfree["Z0"], "mu_hat": dfree["mu_hat"], "b_hat": dfree["b_hat"],
                   "b_mu0": dfree["b_mu0"]}
    print("CLOSURE par3 b=0 %.4f (want %.4f) | slope free %.4f (want %.4f) | loose constraint "
          "%.4f" % (d0["Z0"], sl.PAR3_OBS, dfree["Z0"], SLOPE_FREE_OBS, loose["Z0"]), flush=True)
    obs["constrained"] = None
    obs["fixed"] = {}
    if c["b_ctrl"] is None or c["sigma_ctrl"] is None or not c["sigma_ctrl"] > 0:
        return obs, None, (edges, s)
    bc, sc = c["b_ctrl"], c["sigma_ctrl"]
    csf = CSF(edges, s, bc, sc)
    dc = csf.discovery(n, m)
    f0, f1 = dc["fit0"], dc["fit1"]
    obs["constrained"] = {"Z0": dc["Z0"], "mu_hat": dc["mu_hat"], "b_hat": dc["b_hat"],
                          "b_mu0": dc["b_mu0"], "r_hat": dc["r_hat"], "lnL1": f1["lnL"],
                          "lnL0": f0["lnL"], "b_ctrl": bc, "sigma_ctrl": sc,
                          "pull_b_mu0": (f0["b"] - bc) / sc, "pull_b_best": (f1["b"] - bc) / sc}
    for tag, b in (("b_ctrl", bc), ("b_ctrl-1s", bc - sc), ("b_ctrl+1s", bc + sc)):
        d = sf.discovery(n, m, b_fixed=clamp(b))
        obs["fixed"][tag] = {"b": clamp(b), "Z0": d["Z0"], "mu_hat": d["mu_hat"]}
    T, lam_n = csf.lam(f0)
    T, lam_n = [float(x) for x in T], [float(x) for x in lam_n]
    obs["truth"] = {"a": f0["a"], "r": f0["r"], "b": f0["b"], "sum_T": sum(T),
                    "sum_lam_n": sum(lam_n),
                    "window_29_32": {"bkg": sum(lam_n[14:17]), "n": sum(n[14:17])}}
    obs["dev0"] = csf.deviance(n, m, f0)
    print("CONSTRAINED Z0=%.4f mu=%.3f b=%.4f b(mu=0)=%.4f pulls %.2f/%.2f | fixed b_ctrl "
          "Z0=%.4f, -1s %.4f, +1s %.4f | bkg 29-32 %.2f vs n %d | dev0 %.2f" % (
              dc["Z0"], dc["mu_hat"], dc["b_hat"], dc["b_mu0"], obs["constrained"]["pull_b_mu0"],
              obs["constrained"]["pull_b_best"], obs["fixed"]["b_ctrl"]["Z0"],
              obs["fixed"]["b_ctrl-1s"]["Z0"], obs["fixed"]["b_ctrl+1s"]["Z0"],
              obs["truth"]["window_29_32"]["bkg"], obs["truth"]["window_29_32"]["n"],
              obs["dev0"]), flush=True)
    return obs, (T, lam_n, f0["b"], sc), (edges, s)


# ----------------------------------------------------------------------------- toys
_G = {}


def _init(emu_path, edges, s, T, lam_n, b_truth, sc):
    if emu_path:
        sl.asm.bind(path=emu_path)
    _G["csf"] = make_fit_class()(edges, s, b_truth, sc)
    _G["T"], _G["lam_n"], _G["b_truth"], _G["sc"] = T, lam_n, b_truth, sc


def one_toy(idx):
    import numpy as np
    rng = np.random.default_rng(SEED + idx)
    n = rng.poisson(np.array(_G["lam_n"])).astype(float)
    m = rng.poisson(np.array(_G["T"])).astype(float)
    b_aux = float(rng.normal(_G["b_truth"], _G["sc"]))
    csf = _G["csf"]
    csf.set_constraint(b_aux, _G["sc"])
    d = csf.discovery(n, m)
    return {"idx": idx, "Z0": d["Z0"], "mu": d["mu_hat"], "b0": d["b_mu0"], "b_aux": b_aux,
            "dev0": csf.deviance(n, m, d["fit0"])}


def write_toys(path, rows):
    with open(path, "w") as f:
        f.write("idx,Z0,mu,b0,b_aux,dev0\n")
        for r in rows:
            f.write("%d,%.5f,%.5f,%.5f,%.5f,%.5f\n" % (r["idx"], r["Z0"], r["mu"], r["b0"],
                                                        r["b_aux"], r["dev0"]))


def _f(x, f="%.4f"):
    return "na" if x is None else f % x


def line(res):
    o, g, st = res["observed"], res["grades"], res.get("stats") or {}
    c = o["control"]
    con = o.get("constrained") or {}
    cal = st.get("calibrated") or {}
    fx = o.get("fixed", {}).get("b_ctrl", {})
    return ("SSFRAME: %s | b_ctrl %s+-%s (SS %s, emu %s, W 15-%s) | closures b0 %.4f free %.4f "
            "loose %.4f | Z0 con %s -> cal %s%s (k=%s of %s) mu %s b %s b(mu=0) %s | fixed "
            "b_ctrl %s | p2 %s gof p %s" % (
                " ".join("%s %s" % (k, g[k].split(" ")[0]) for k in ("P0",) + TESTS),
                _f(c.get("b_ctrl")), _f(c.get("sigma_ctrl")),
                _f(c.get("ss", {}).get("b_hat")), _f(c.get("emu", {}).get("b_hat")),
                c.get("window_hi"), o["closure_b0"], o["closure_free"], o["closure_loose"],
                _f(con.get("Z0")), ">=" if cal.get("lower_bound") else "", _f(cal.get("Z"), "%.3f"),
                cal.get("k"), st.get("ntoys"), _f(con.get("mu_hat"), "%.3f"),
                _f(con.get("b_hat")), _f(con.get("b_mu0")), _f(fx.get("Z0")),
                _f(st.get("p_ge2")), _f((st.get("gof") or {}).get("p"), "%.3f")))


# ----------------------------------------------------------------------------- driver
def run(fig5, dmc, emu, out_dir, ntoys, workers, emu_path, budget_s, save_every=250):
    from multiprocessing import Pool
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    res = {"version": VERSION, "aprime_slsm": sl.VERSION, "aprime_smooth": sl.asm.VERSION,
           "sscontrol": ssc.VERSION, "dmcratio": ssc.dm.VERSION, "aprime_cross": ssc.ac.VERSION,
           "emuframe": sl.asm.ef.VERSION, "seed": SEED, "ntoys_requested": ntoys,
           "budget_s": budget_s, "min_toys": MIN_TOYS}
    path = os.path.join(out_dir, "ssframe.json")
    toys_path = os.path.join(out_dir, "toys.csv")

    def save():
        res["elapsed_s"] = time.time() - t0
        with open(path, "w") as f:
            json.dump(res, f, indent=1, default=str)

    obs, truth, (edges, s) = observe(fig5, dmc, emu)
    res["observed"] = obs
    res["grades"], res["stats"] = grade(obs, [])
    save()
    if truth is None or gate(obs)[0] != "PASS":
        res["stopped"] = "no toys: gate P0 %s" % res["grades"]["P0"]
        save()
        return res
    T, lam_n, b_truth, sc = truth
    rows = []
    stopped = "all toys finished"
    pool = Pool(workers, initializer=_init, initargs=(emu_path, edges, s, T, lam_n, b_truth, sc))
    try:
        for row in pool.imap_unordered(one_toy, range(ntoys), chunksize=4):
            rows.append(row)
            if len(rows) % save_every == 0:
                pre = prefix(rows)
                write_toys(toys_path, pre)
                res["grades"], res["stats"] = grade(obs, pre)
                res["ntoys"], res["finished_any_order"] = len(pre), len(rows)
                save()
                print("toys done %d (prefix %d) of %d, %d s" % (
                    len(rows), len(pre), ntoys, round(time.time() - t0)), flush=True)
            if time.time() - t0 > budget_s:
                stopped = "time budget %d s reached" % budget_s
                break
    finally:
        pool.terminate()
        pool.join()
    pre = prefix(rows)
    write_toys(toys_path, pre)
    res["grades"], res["stats"] = grade(obs, pre)
    res["ntoys"], res["finished_any_order"] = len(pre), len(rows)
    res["stopped"] = stopped
    save()
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--dmc", required=True)
    ap.add_argument("--emu", required=True)
    ap.add_argument("--emuframe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ntoys", type=int, default=6000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-s", type=float, default=13000.0)
    a = ap.parse_args(argv)
    if sl is None or sl.asm is None or ssc is None or ssc.ac is None or ssc.dm is None:
        raise SystemExit("aprime_slsm, aprime_smooth, sscontrol, dmcratio and aprime_cross must "
                         "sit next to this file")
    print("python %s" % sys.version.split()[0], flush=True)
    print("emuframe blob", sl.asm.fetch_emuframe(a.emuframe), flush=True)
    sl.asm.bind(path=a.emuframe)
    load = lambda p: json.load(open(p))
    fig5, dmc, emu = load(a.fig5), load(a.dmc), load(a.emu)
    print("%s with %s, %s, %s; sum n %d, sum v %.1f" % (
        VERSION, sl.VERSION, ssc.VERSION, sl.asm.ef.VERSION, sum(fig5["n"]),
        sum(fig5["v_scaled"])), flush=True)
    res = run(fig5, dmc, emu, a.out, a.ntoys, a.workers, os.path.abspath(a.emuframe), a.budget_s)
    keys = [k for k in ("ntoys", "finished_any_order", "stopped", "stats", "grades") if k in res]
    print(json.dumps({k: res[k] for k in keys}, indent=1, default=str), flush=True)
    print(line(res), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
