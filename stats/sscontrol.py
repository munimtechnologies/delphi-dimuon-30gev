# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""sscontrol 0.1.0: ALEPH's same-sign muon pairs as a control sample for the rising
mu mu / e mu ratio under the 30 GeV excess (PLAN amendment 0.28, tests W0-W5).

dmcratio-v1 (amendment 0.27, graded in NOTE-aprime 0.5 sec. 11) found that opposite-sign (OS)
and same-sign (SS) muon pairs rise against ALEPH's simulation with slopes that agree (pull
-0.57 / -0.09), while e mu pairs follow simulation, but each slope's significance depended on
how the simulation values drawn below Fig. 21's log axis (OFF) were filled. This module removes
that dependence and asks what the same-sign control implies for the excess:

* Window W = [15 GeV, hi), hi = the largest upper edge such that every value of every spectrum
  (OS and SS data and simulation, e mu data and simulation) is readable after the NM -> 0 rule.
  On the committed readings that is 38 GeV (first OFF value: OS simulation at 38-39 GeV).
* In W, at zero signal (Barlow-Beeston, simulation as pseudo-counts of the data's size, ratio
  r exp(b (x - 30.40))): the slope of SS, OS and e mu against simulation; the joint OS + SS slope
  (one b, separate r) with ALEPH's 30 GeV signal floated in OS.
* The control slope b_ctrl = b_SS - b_emu (muon-pair drift against simulation minus the e mu
  drift), sigma_ctrl = hypot(sigma_SS, sigma_emu). ALEPH's simulation predicts no mu mu / e mu
  slope (amendment 0.26: b_MC = -0.005 +- 0.012), so b_ctrl is what a muon-pair effect seen in
  the same-sign control predicts for the data's mu mu / e mu ratio.
* The excess (Fig. 5 reading, 15-50 GeV, the A'-ALEPH "bb" frame of aprime_cross) with the
  ratio's slope Gaussian-constrained to b_ctrl +- sigma_ctrl, and fixed at b_ctrl and b_ctrl
  +- sigma_ctrl (information).

Uses aprime_cross 0.1.0 and dmcratio 0.1.0 unchanged.

    python sscontrol.py --fig5 aleph-fig5.json --dmc aleph-dmc21.json --emu aleph-emu3.json --out /out

Last output line `SSCTRL:`.
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import aprime_cross as ac
except ImportError:          # pure helpers below stay testable without it
    ac = None
try:
    import dmcratio as dm
except ImportError:
    dm = None

VERSION = "mv2 sscontrol 0.1.0"
LO = 15.0
B_RANGE = (-0.2, 0.2)
W_EXPECTED_HI = 38.0
# dmcratio-v1, 15-50 GeV, OFF -> 0 (amendment 0.27 sec. 4): the closure targets of gate W0
DMC_V1 = {"b_os_zero": 0.028042226136997687, "b_ss_zero": 0.04094099040998987}
DMC_TOL = 0.001
TESTS = ("W1", "W2", "W3", "W4", "W5")


# ----------------------------------------------------------------------------- pure helpers
def readable_hi(edges, series, lo=LO):
    """Largest upper edge hi such that no series has a None in any bin of [lo, hi).
    Returns None when the first bin at or above lo is already unreadable."""
    hi = None
    for i in range(len(edges) - 1):
        if edges[i] < lo - 1e-9:
            continue
        if any(s[i] is None for s in series):
            break
        hi = float(edges[i + 1])
    return hi


def sub_edges(edges, lo, hi):
    return [float(e) for e in edges if lo - 1e-9 <= e <= hi + 1e-9]


def cut(edges, values, lo, hi):
    """Values of the bins lying inside [lo, hi]."""
    return [values[i] for i in range(len(edges) - 1)
            if edges[i] >= lo - 1e-9 and edges[i + 1] <= hi + 1e-9]


def control_slope(ss, emu):
    """b_ctrl = b_SS - b_emu and its 1-sigma error (None if either interval is missing)."""
    bc = ss["b_hat"] - emu["b_hat"]
    s1, s2 = ss.get("sigma_b"), emu.get("sigma_b")
    sc = math.hypot(s1, s2) if (s1 is not None and s2 is not None) else None
    return {"b_ctrl": bc, "sigma_ctrl": sc}


def clamp(b):
    return min(B_RANGE[1], max(B_RANGE[0], b))


def grade(r):
    """W0-W5 of amendment 0.28 from the result dict built by run()."""
    g = {}
    w0 = (r.get("C0") == "PASS" and r["dmc_closure"]["ok"]
          and r["window_hi"] is not None and abs(r["window_hi"] - W_EXPECTED_HI) < 1e-9
          and r["window_ok"])
    g["W0"] = "PASS" if w0 else "FAIL"
    if not w0:
        for k in TESTS:
            g[k] = "NOT GRADABLE (W0 failed)"
        return g
    ss, emu = r["slopes_w"]["ss"], r["slopes_w"]["emu"]
    j = r["joint_w_signal_floated"]
    g["W1"] = "PASS" if (ss["b_hat"] > 0 and ss["Z_slope"] >= 2.0) else "FAIL"
    g["W2"] = "PASS" if (j["b_hat"] > 0 and j["Z_slope"] >= 2.0) else "FAIL"
    g["W3"] = "PASS" if abs(emu["Z_slope"]) < 2.0 else "FAIL"
    p = r.get("W4_pull")
    g["W4"] = "NOT GRADABLE (no 1-sigma interval)" if p is None else (
        "PASS" if abs(p) < 2.0 else "FAIL")
    con = r.get("constrained")
    g["W5"] = "NOT GRADABLE (no control interval)" if con is None else (
        "PASS" if con["Z0"] < 2.0 else "FAIL")
    return g


# ----------------------------------------------------------------------------- fits
def joint_slope(os_n, os_m, ss_n, ss_m, xc, s_os=None):
    """One slope b shared by OS and SS against simulation, separate ratios r; ALEPH's signal
    floated (mu >= 0) in OS when s_os is given. Signed Z of b against b = 0 (1 dof)."""
    zeros = [0.0] * len(xc)

    def l_os(b):
        if s_os is None:
            return ac.prof(os_n, os_m, zeros, 0.0, "bb", xc, b)["lnL"]
        best, _ = ac.fit_mu(lambda u: ac.prof(os_n, os_m, s_os, u, "bb", xc, b))
        return best["lnL"]

    def f(b):
        return l_os(b) + ac.prof(ss_n, ss_m, zeros, 0.0, "bb", xc, b)["lnL"]

    b_hat, top = ac.scan_then_golden(f, B_RANGE[0], B_RANGE[1], n=40)
    f0 = f(0.0)
    if f0 > top:
        b_hat, top = 0.0, f0
    q = max(0.0, 2.0 * (top - f0))
    z = math.copysign(math.sqrt(q), b_hat) if q > 0 else 0.0
    return {"b_hat": b_hat, "Z_slope": z, "lnL_free": top, "lnL_const": f0,
            "signal_floated": s_os is not None}


def constrained_discovery(n, m, s, xc, bc, sc):
    """Z0 of the signal (model bb) with the ratio's slope profiled under a Gaussian
    constraint b ~ N(bc, sc)."""
    def pf(mu):
        g = lambda b: ac.prof(n, m, s, mu, "bb", xc, b)["lnL"] - 0.5 * ((b - bc) / sc) ** 2
        b, v = ac.scan_then_golden(g, B_RANGE[0], B_RANGE[1], n=40)
        p = ac.prof(n, m, s, mu, "bb", xc, b)
        return {"r": p["r"], "b": b, "lnL": v}

    best, p0 = ac.fit_mu(pf)
    q0 = max(0.0, 2.0 * (best["lnL"] - p0["lnL"]))
    return {"mu_hat": best["mu"], "b_hat": best["b"], "r_hat": best["r"], "b_mu0": p0["b"],
            "q0": q0, "Z0": math.sqrt(q0), "lnL_best": best["lnL"], "lnL_mu0": p0["lnL"],
            "b_ctrl": bc, "sigma_ctrl": sc}


# ----------------------------------------------------------------------------- run
def run(fig5_path, dmc_path, emu_path, out_dir=None, closure=True):
    if ac is None or dm is None:
        raise SystemExit("aprime_cross.py and dmcratio.py must sit next to this file")
    t0 = time.time()
    el = lambda: time.time() - t0
    print("%s on %s and %s" % (VERSION, ac.VERSION, dm.VERSION), flush=True)
    fig5, dmc, emu = ac.load(fig5_path), ac.load(dmc_path), ac.load(emu_path)
    res = {"version": VERSION, "aprime_cross": ac.VERSION, "dmcratio": dm.VERSION}
    if closure:
        c = ac.closure(fig5)
        res["C0"], res["C0_got"] = c["C0"], c["got"]
        print("C0 %s %s (%.0f s)" % (c["C0"], json.dumps(c["got"]), el()), flush=True)
    edges = [float(e) for e in dmc["edges"]]
    if [float(e) for e in emu["edges"]] != edges or [float(e) for e in fig5["edges"]] != edges:
        raise SystemExit("the three readings must share one grid")

    # gate part: dmcratio-v1 closure, 15-50 GeV, OFF -> 0
    idx = dm.window(edges)
    e50 = edges[idx[0]:idx[-1] + 2]
    x50 = ac.centres(e50)
    z = {k: [dm.fill(dmc[k], dmc["marks"][k], dmc["edges"], 0.0)[i] for i in idx]
         for k in ("os_data", "os_mc", "ss_data", "ss_mc")}
    b_os50 = dm.slope(z["os_data"], z["os_mc"], x50)["b_hat"]
    b_ss50 = dm.slope(z["ss_data"], z["ss_mc"], x50)["b_hat"]
    res["dmc_closure"] = {"b_os_zero": b_os50, "b_ss_zero": b_ss50, "want": DMC_V1,
                          "ok": (abs(b_os50 - DMC_V1["b_os_zero"]) < DMC_TOL
                                 and abs(b_ss50 - DMC_V1["b_ss_zero"]) < DMC_TOL)}
    print("DMC closure %s: OS b %.5f (want %.5f) SS b %.5f (want %.5f) (%.0f s)" % (
        "PASS" if res["dmc_closure"]["ok"] else "FAIL", b_os50, DMC_V1["b_os_zero"], b_ss50,
        DMC_V1["b_ss_zero"], el()), flush=True)

    # the readable window
    raw = {k: dm.fill(dmc[k], dmc["marks"][k], dmc["edges"], None)
           for k in ("os_data", "os_mc", "ss_data", "ss_mc")}
    raw["emu_data"] = dm.fill(emu["data"], emu["marks"]["data"], emu["edges"], None)
    raw["emu_mc"] = dm.fill(emu["mc"], emu["marks"]["mc"], emu["edges"], None)
    hi = readable_hi(edges, list(raw.values()))
    res["window_hi"] = hi
    if hi is None:
        res["window_ok"] = False
        res["grades"] = grade(res)
        print("SSCTRL: no readable window", flush=True)
        return res
    we = sub_edges(edges, LO, hi)
    xw = ac.centres(we)
    w = {k: cut(edges, v, LO, hi) for k, v in raw.items()}
    res["window_ok"] = all(v is not None and v >= 0 for vals in w.values() for v in vals)
    res["window_bins"] = len(xw)
    print("WINDOW %.0f-%.0f GeV, %d bins, all readable: %s" % (LO, hi, len(xw), res["window_ok"]),
          flush=True)
    if not res["window_ok"]:
        res["grades"] = grade(res)
        print("SSCTRL: window not readable", flush=True)
        return res

    r0 = ac.R0
    emu_n = [v / r0 for v in w["emu_data"]]
    emu_m = [v / r0 for v in w["emu_mc"]]
    sl = {"os": dm.slope(w["os_data"], w["os_mc"], xw),
          "ss": dm.slope(w["ss_data"], w["ss_mc"], xw),
          "emu": dm.slope(emu_n, emu_m, xw),
          "mc_ratio": dm.slope(w["os_mc"], emu_m, xw)}   # information: simulation mu mu / e mu
    res["slopes_w"] = sl
    for k in ("os", "ss", "emu", "mc_ratio"):
        print("SLOPE W %s b=%.4f sb=%s Zs=%.2f r=%.3f->%.3f (%.0f s)" % (
            k, sl[k]["b_hat"], dm._fmt(sl[k].get("sigma_b")), sl[k]["Z_slope"],
            sl[k]["sums"]["r_15_25"], sl[k]["sums"]["r_25_50"], el()), flush=True)

    s_w = ac.s_template(we)
    res["joint_w_signal_floated"] = joint_slope(w["os_data"], w["os_mc"], w["ss_data"],
                                                w["ss_mc"], xw, s_w)
    res["joint_w_no_signal"] = joint_slope(w["os_data"], w["os_mc"], w["ss_data"], w["ss_mc"], xw)
    for k in ("joint_w_signal_floated", "joint_w_no_signal"):
        print("JOINT %s b=%.4f Zs=%.2f (%.0f s)" % (k, res[k]["b_hat"], res[k]["Z_slope"], el()),
              flush=True)
    os_sf = dm.signal_floated(w["os_data"], w["os_mc"], we)
    res["os_w_signal_floated"] = os_sf

    ctrl = control_slope(sl["ss"], sl["emu"])
    res["control"] = ctrl
    dedges, n, md = ac.data_window(fig5)
    xd = ac.centres(dedges)
    s = ac.s_template(dedges)
    dsl = ac.slope_mu0(n, md, xd, "bb")
    res["data_slope"] = dsl
    sc = ctrl["sigma_ctrl"]
    res["W4_pull"] = None if (sc is None or dsl.get("sigma_b") is None) else \
        (ctrl["b_ctrl"] - dsl["b_hat"]) / math.hypot(sc, dsl["sigma_b"])
    print("CONTROL b_ctrl=%.4f sc=%s | data b=%.4f sb=%s | pull %s (%.0f s)" % (
        ctrl["b_ctrl"], dm._fmt(sc), dsl["b_hat"], dm._fmt(dsl.get("sigma_b")),
        dm._fmt(res["W4_pull"], "%.3f"), el()), flush=True)

    res["fixed"] = {}
    bcs = [("b_ctrl", ctrl["b_ctrl"])]
    if sc is not None:
        bcs += [("b_ctrl-1s", ctrl["b_ctrl"] - sc), ("b_ctrl+1s", ctrl["b_ctrl"] + sc)]
    for tag, b in bcs:
        d = ac.discovery(n, md, s, "bb", xd, clamp(b))
        res["fixed"][tag] = d
        print("FIXED %s b=%.4f Z0=%.3f mu=%.3f (%.0f s)" % (tag, clamp(b), d["Z0"], d["mu_hat"],
                                                           el()), flush=True)
    res["constrained"] = None
    res["constrained_with_mc"] = None
    if sc is not None:
        con = constrained_discovery(n, md, s, xd, ctrl["b_ctrl"], sc)
        res["constrained"] = con
        print("CONSTRAINED Z0=%.3f mu=%.3f b=%.4f b_mu0=%.4f (%.0f s)" % (
            con["Z0"], con["mu_hat"], con["b_hat"], con["b_mu0"], el()), flush=True)
        smc = sl["mc_ratio"].get("sigma_b")
        if smc is not None:   # information: add the simulation's own mu mu / e mu slope
            bc2 = ctrl["b_ctrl"] + sl["mc_ratio"]["b_hat"]
            con2 = constrained_discovery(n, md, s, xd, bc2, math.hypot(sc, smc))
            res["constrained_with_mc"] = con2
            print("CONSTRAINED+MC b_c=%.4f sc=%.4f Z0=%.3f mu=%.3f (%.0f s)" % (
                bc2, math.hypot(sc, smc), con2["Z0"], con2["mu_hat"], el()), flush=True)

    g = grade(res)
    res["grades"] = g
    res["elapsed_s"] = el()
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "sscontrol.json"), "w") as fh:
            json.dump(res, fh, indent=1, default=str)
    j = res["joint_w_signal_floated"]
    con = res["constrained"] or {}
    fx = res["fixed"]["b_ctrl"]
    print("SSCTRL: W0 %s W1 %s W2 %s W3 %s W4 %s W5 %s | W 15-%.0f | SS b=%.4f sb=%s Zs=%.2f | "
          "OS b=%.4f Zs=%.2f | emu b=%.4f Zs=%.2f | joint(sig) b=%.4f Zs=%.2f | joint(nosig) "
          "b=%.4f Zs=%.2f | ctrl %.4f+-%s | data b %.4f pull %s | Z0 con %s mu %s | Z0 fixed %.3f"
          % (g["W0"], g["W1"], g["W2"], g["W3"], g["W4"], g["W5"], hi, sl["ss"]["b_hat"],
             dm._fmt(sl["ss"].get("sigma_b")), sl["ss"]["Z_slope"], sl["os"]["b_hat"],
             sl["os"]["Z_slope"], sl["emu"]["b_hat"], sl["emu"]["Z_slope"], j["b_hat"],
             j["Z_slope"], res["joint_w_no_signal"]["b_hat"], res["joint_w_no_signal"]["Z_slope"],
             ctrl["b_ctrl"], dm._fmt(sc), dsl["b_hat"], dm._fmt(res["W4_pull"], "%.3f"),
             dm._fmt(con.get("Z0"), "%.3f"), dm._fmt(con.get("mu_hat"), "%.3f"), fx["Z0"]),
          flush=True)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--dmc", required=True)
    ap.add_argument("--emu", required=True)
    ap.add_argument("--out")
    ap.add_argument("--no-closure", action="store_true")
    a = ap.parse_args(argv)
    print("python %s" % sys.version.split()[0], flush=True)
    run(a.fig5, a.dmc, a.emu, a.out, closure=not a.no_closure)
    return 0


if __name__ == "__main__":
    sys.exit(main())
