# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""dmcratio 0.1.0: do ALEPH's same-sign muon pairs rise against simulation as its opposite-sign
pairs do? (PLAN amendment 0.26 sec. 8, tests G0, G1, D1, D2, S1, S2; amendment 0.27 for the
values drawn below the log axis.)

Inputs, two blind readings of Heister, arXiv:1610.06536 v9:
* data/aleph-dmc21.json  Fig. 21: OS and SS di-muon data against ALEPH's simulation (log axis)
* data/aleph-emu3.json   Fig. 3: e mu data against ALEPH's simulation (plotted, scaled)
and data/aleph-fig5.json (for gate G1 and the closure C0 of aprime_cross).

For each spectrum, data counts n_i against the simulation t_i used as pseudo-counts at the data's
size (Barlow-Beeston, as aprime_cross 0.1.0 does for Fig. 4), ratio r exp(b (x_i - 30.40)),
15-50 GeV, zero signal: b, its 1-sigma interval and its signed Z against a constant ratio.
Fig. 3's values are on the scaled e mu scale of Fig. 5; both data and simulation are divided by
aprime_cross.R0 to reach raw-count size.

Fills (written before any fit):
* NM (no data marker drawn) -> 0 (amendment 0.26 sec. 8).
* OFF (simulation below the bottom of the log axis, reader: in [0, 0.29)): amendment 0.27.
  "zero" fill -> 0.0 (secondary grades, suffix z); "ceil" fill -> 0.29 (sensitivity, suffix c).
  A grade that differs between the two is "reading-dependent".
G0 is graded as written (every value readable after the NM rule), so OFF values make it FAIL.

    python dmcratio.py --fig5 aleph-fig5.json --dmc aleph-dmc21.json --emu aleph-emu3.json --out /out

Last output line `DMCRATIO:`.
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

VERSION = "mv2 dmcratio 0.1.0"
OFF_FILLS = {"zero": 0.0, "ceil": 0.29}
G1_TOL, G1_NEED = 0.6, 30
GRADES = ("D1", "D2", "S1", "S2")


# ----------------------------------------------------------------------------- readings
def fill(values, marks, edges, off_fill):
    """Copy of `values` with nulls filled: NM -> 0.0; OFF -> off_fill (None keeps it null).
    marks = {"NM": [low edges], "OFF": [low edges]}. A null with no mark raises."""
    nm = {round(float(e), 6) for e in marks.get("NM", [])}
    off = {round(float(e), 6) for e in marks.get("OFF", [])}
    out = []
    for e, v in zip(edges, values):
        if v is not None:
            out.append(float(v))
            continue
        k = round(float(e), 6)
        if k in nm:
            out.append(0.0)
        elif k in off:
            out.append(None if off_fill is None else float(off_fill))
        else:
            raise ValueError("null at %s GeV without an NM or OFF mark" % e)
    return out


def g0_as_written(series):
    """Amendment 0.26 G0: every value readable after the NM rule, and non-negative.
    series = {name: list after fill(..., off_fill=None)}."""
    bad = {k: sum(1 for v in vals if v is None) for k, vals in series.items()}
    neg = {k: sum(1 for v in vals if v is not None and v < 0) for k, vals in series.items()}
    ok = all(b == 0 for b in bad.values()) and all(n == 0 for n in neg.values())
    why = ", ".join("%s %d unreadable" % (k, b) for k, b in sorted(bad.items()) if b)
    return {"G0": "PASS" if ok else "FAIL (%s)" % (why or "negative value"),
            "unreadable": bad, "negative": neg}


def g1(emu_data, fig5_v, tol=G1_TOL, need=G1_NEED):
    """R3 data within tol of Fig. 5's e mu reading in at least `need` of the bins."""
    k = sum(1 for a, b in zip(emu_data, fig5_v) if abs(a - b) <= tol + 1e-9)
    diffs = [round(a - b, 3) for a, b in zip(emu_data, fig5_v)]
    return {"G1": "PASS" if k >= need else "FAIL", "agree": k, "of": len(fig5_v),
            "max_abs_diff": max(abs(d) for d in diffs), "diffs": diffs}


def window(edges, lo=15.0, hi=50.0):
    idx = [i for i in range(len(edges) - 1) if edges[i] >= lo - 1e-9 and edges[i + 1] <= hi + 1e-9]
    return idx


# ----------------------------------------------------------------------------- grades
def pull(b1, s1, b2, s2):
    if s1 is None or s2 is None:
        return None
    return (b1 - b2) / math.sqrt(s1 * s1 + s2 * s2)


def grade(os_sl, ss_sl, emu_sl):
    """D1, D2, S1, S2 of amendment 0.26 sec. 8 from three slope_mu0 results."""
    g = {}
    g["D1"] = "PASS" if (os_sl["b_hat"] > 0 and os_sl["Z_slope"] >= 2.0) else "FAIL"
    g["D2"] = "PASS" if abs(emu_sl["Z_slope"]) < 2.0 else "FAIL"
    p = pull(os_sl["b_hat"], os_sl.get("sigma_b"), ss_sl["b_hat"], ss_sl.get("sigma_b"))
    g["pull_os_ss"] = p
    if p is None:
        g["S1"] = g["S2"] = "NOT GRADABLE (no 1-sigma interval)"
    else:
        g["S1"] = "PASS" if (ss_sl["b_hat"] > 0 and ss_sl["Z_slope"] >= 2.0
                             and abs(p) < 2.0) else "FAIL"
        g["S2"] = "PASS" if (ss_sl["Z_slope"] < 1.0 and abs(p) >= 2.0) else "FAIL"
    return g


def agreement(a, b):
    out = {}
    for k in GRADES:
        ga, gb = a.get(k), b.get(k)
        out[k] = ga if ga == gb else "reading-dependent (zero: %s, ceil: %s)" % (ga, gb)
    return out


def ratio_sums(n, m, xc):
    lo = [i for i, x in enumerate(xc) if x < 25.0]
    hi = [i for i, x in enumerate(xc) if x >= 25.0]
    f = lambda idx: sum(n[i] for i in idx) / max(1e-12, sum(m[i] for i in idx))
    return {"r_15_25": f(lo), "r_25_50": f(hi), "n_15_25": sum(n[i] for i in lo),
            "m_15_25": sum(m[i] for i in lo), "n_25_50": sum(n[i] for i in hi),
            "m_25_50": sum(m[i] for i in hi)}


# ----------------------------------------------------------------------------- fits
def slope(n, m, xc):
    sl = ac.slope_mu0(n, m, xc, "bb")
    sl["sums"] = ratio_sums(n, m, xc)
    return sl


def signal_floated(n, m, edges):
    """Information: OS slope with ALEPH's signal floated (degeneracy rule)."""
    xc = ac.centres(edges)
    s = ac.s_template(edges)
    const = ac.discovery(n, m, s, "bb", xc, 0.0)
    free = ac.discovery(n, m, s, "bb", xc, None)
    q = max(0.0, 2.0 * (free["lnL_best"] - const["lnL_best"]))
    z = math.copysign(math.sqrt(q), free["b_hat"]) if q > 0 else 0.0
    return {"b_hat_signal_floated": free["b_hat"], "Z_slope_signal_floated": z,
            "mu_hat_const": const["mu_hat"], "mu_hat_slope": free["mu_hat"],
            "Z0_const": const["Z0"], "Z0_slope": free["Z0"]}


def _fmt(x, f="%.4f"):
    return "na" if x is None else f % x


def sl_part(tag, sl):
    return "%s b=%.4f sb=%s Zs=%.2f r=%.3f->%.3f" % (
        tag, sl["b_hat"], _fmt(sl.get("sigma_b")), sl["Z_slope"], sl["sums"]["r_15_25"],
        sl["sums"]["r_25_50"])


def run(fig5_path, dmc_path, emu_path, out_dir=None, closure=True):
    if ac is None:
        raise SystemExit("aprime_cross.py must sit next to this file")
    t0 = time.time()
    print("%s on %s" % (VERSION, ac.VERSION), flush=True)
    fig5, dmc, emu = ac.load(fig5_path), ac.load(dmc_path), ac.load(emu_path)
    res = {"version": VERSION, "aprime_cross": ac.VERSION, "off_fills": OFF_FILLS}
    if closure:   # module integrity (information): aprime_cross reproduces aprime-ext-v1
        c = ac.closure(fig5)
        res["C0"] = c["C0"]
        res["C0_got"] = c["got"]
        print("C0 %s %s (%.0f s)" % (c["C0"], json.dumps(c["got"]), time.time() - t0), flush=True)
    edges = [float(e) for e in dmc["edges"]]
    if [float(e) for e in emu["edges"]] != edges or [float(e) for e in fig5["edges"]] != edges:
        raise SystemExit("the three readings must share one grid")
    idx = window(edges)
    edges = edges[idx[0]:idx[-1] + 2]
    xc = ac.centres(edges)
    cut = lambda v: [v[i] for i in idx]

    # gates as written (NM -> 0, OFF kept null)
    raw = {k: cut(fill(dmc[k], dmc["marks"][k], dmc["edges"], None))
           for k in ("os_data", "os_mc", "ss_data", "ss_mc")}
    raw["emu_data"] = cut(fill(emu["data"], emu["marks"]["data"], emu["edges"], None))
    raw["emu_mc"] = cut(fill(emu["mc"], emu["marks"]["mc"], emu["edges"], None))
    res["G0_as_written"] = g0_as_written(raw)
    res["G1"] = g1(raw["emu_data"], cut([float(v) for v in fig5["v_scaled"]]))
    os_fig5 = cut([float(v) for v in fig5["n"]])
    res["info_os_vs_fig5"] = {"identical_bins": sum(1 for a, b in zip(raw["os_data"], os_fig5)
                                                    if abs(a - b) < 1e-9), "of": len(os_fig5)}
    print("G0 as written: %s | G1 %s (%d of %d within %.1f, max diff %.2f) | OS data = Fig. 5 n "
          "in %d of %d bins" % (res["G0_as_written"]["G0"], res["G1"]["G1"], res["G1"]["agree"],
                                res["G1"]["of"], G1_TOL, res["G1"]["max_abs_diff"],
                                res["info_os_vs_fig5"]["identical_bins"], len(os_fig5)), flush=True)

    # e mu: no OFF value, so one fit serves both fills
    r0 = ac.R0
    emu_sl = slope([v / r0 for v in raw["emu_data"]], [v / r0 for v in raw["emu_mc"]], xc)
    print("EMU: %s (%.0f s)" % (sl_part("emu", emu_sl), time.time() - t0), flush=True)
    res["emu"] = emu_sl

    per = {}
    for how, val in OFF_FILLS.items():
        f = {k: cut(fill(dmc[k], dmc["marks"][k], dmc["edges"], val))
             for k in ("os_data", "os_mc", "ss_data", "ss_mc")}
        os_sl = slope(f["os_data"], f["os_mc"], xc)
        ss_sl = slope(f["ss_data"], f["ss_mc"], xc)
        g = grade(os_sl, ss_sl, emu_sl)
        g["gate"] = "PASS" if all(v is not None and v >= 0 for vals in f.values() for v in vals) \
            else "FAIL"
        per[how] = {"os": os_sl, "ss": ss_sl, "grades": g,
                    "os_minus_emu": {"diff": os_sl["b_hat"] - emu_sl["b_hat"],
                                     "pull": pull(os_sl["b_hat"], os_sl.get("sigma_b"),
                                                  emu_sl["b_hat"], emu_sl.get("sigma_b"))}}
        print("FILL %s: %s | %s | pull OS-SS %s | D1 %s D2 %s S1 %s S2 %s (%.0f s)" % (
            how, sl_part("OS", os_sl), sl_part("SS", ss_sl), _fmt(g["pull_os_ss"], "%.3f"),
            g["D1"], g["D2"], g["S1"], g["S2"], time.time() - t0), flush=True)
    res["fills"] = per
    res["grades_z"] = {k + "z": per["zero"]["grades"][k] for k in GRADES}
    res["grades_c"] = {k + "c": per["ceil"]["grades"][k] for k in GRADES}
    res["agreement"] = agreement(per["zero"]["grades"], per["ceil"]["grades"])

    # information: OS slope with the signal floated (zero fill)
    fz = {k: cut(fill(dmc[k], dmc["marks"][k], dmc["edges"], 0.0)) for k in ("os_data", "os_mc")}
    res["os_signal_floated"] = signal_floated(fz["os_data"], fz["os_mc"], edges)
    res["elapsed_s"] = time.time() - t0
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "dmcratio.json"), "w") as fh:
            json.dump(res, fh, indent=1, default=str)
    pz, sf = per["zero"], res["os_signal_floated"]
    line = ("DMCRATIO: C0 %s | G0(as written) %s | G1 %s %d/%d | %s | z: %s | %s | pull %s | "
            "c: OS Zs=%.2f SS Zs=%.2f pull %s | agree D1 %s D2 %s S1 %s S2 %s | "
            "OS-emu %.4f pull %s | OS sig-floated b=%.4f Zs=%.2f mu %.3f/%.3f Z0 %.2f/%.2f" % (
                res.get("C0", "not run"), res["G0_as_written"]["G0"].split(" ")[0],
                res["G1"]["G1"], res["G1"]["agree"], res["G1"]["of"], sl_part("emu", emu_sl),
                sl_part("OS", pz["os"]), sl_part("SS", pz["ss"]),
                _fmt(pz["grades"]["pull_os_ss"], "%.3f"), per["ceil"]["os"]["Z_slope"],
                per["ceil"]["ss"]["Z_slope"], _fmt(per["ceil"]["grades"]["pull_os_ss"], "%.3f"),
                res["agreement"]["D1"], res["agreement"]["D2"], res["agreement"]["S1"],
                res["agreement"]["S2"], pz["os_minus_emu"]["diff"],
                _fmt(pz["os_minus_emu"]["pull"], "%.3f"), sf["b_hat_signal_floated"],
                sf["Z_slope_signal_floated"], sf["mu_hat_const"], sf["mu_hat_slope"],
                sf["Z0_const"], sf["Z0_slope"]))
    print(line, flush=True)
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
