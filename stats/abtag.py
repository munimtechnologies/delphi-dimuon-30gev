# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""abtag 0.1.0: do ALEPH's opposite-sign muon pairs rise against ALEPH's simulation also in
events whose b-tag was INVERTED? (PLAN amendment 0.31 sec. 3, tests A0-A4.)

sscontrol-v1 (amendment 0.28, graded in amendment 0.31 sec. 1) found that same-sign muon pairs
in b-tagged events rise against ALEPH's simulation (b_SS = 0.0387 +- 0.0187 per GeV, Z 2.09 on
15-38 GeV) while e mu pairs do not, but the joint opposite- plus same-sign slope with the 30 GeV
signal floated stayed below 2 sigma (W2 FAIL), so the drift was not established. Heister
(arXiv:1610.06536 v9, HTML Fig. 24) shows the opposite-sign di-muon spectrum for events with the
b-tag inverted (P_H,mass,max < 2), with the Z decay flavours drawn in colour. Those events are a
sample independent of the b-tagged one. If the rise is a property of ALEPH's muon pairs in
general (muon identification, fake muons, the simulation's muon kinematics), it should appear
there too; if it is tied to b events (cascade decays) or to the excess, it should not.

Input: data/aleph-abtag24.json, a blind reading of Fig. 24 on 1 GeV bins (or any grid that has
an edge at 15 GeV): {"edges", "data", "mc", "marks": {"data": {"NM": [], "OFF": []},
"mc": {"NM": [], "OFF": []}}}. NM (no data marker) -> 0; OFF (hidden / below a log axis) ->
unreadable (amendment 0.28's window rule). The b-tagged readings (Fig. 21, Fig. 3) and Fig. 5
are used for the gate only.

Window W_A = [15 GeV, hi), hi the largest edge with every data and simulation value of Fig. 24
readable after the NM rule. Model "bb" of aprime_cross (simulation as pseudo-counts at the
data's size), ratio r exp(b (x - 30.40)), zero signal: b_A, its 1-sigma interval, signed Z.

Uses aprime_cross 0.1.0 and dmcratio 0.1.0 unchanged (fetched from main).

    python abtag.py --abtag aleph-abtag24.json --fig5 aleph-fig5.json \
        --dmc aleph-dmc21.json --emu aleph-emu3.json --out /out

Last output line `ABTAG:`.
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

VERSION = "mv2 abtag 0.1.0"
LO = 15.0
MIN_HI = 30.0                # W_A must reach at least 30 GeV (15 one-GeV bins)
MIN_EVENTS = 100.0           # data events needed in W_A
WHOLE_TOL = 0.05             # data must be whole numbers (events, not a normalised scale)
SS_WINDOW_HI = 38.0
# sscontrol-v1 (amendment 0.31 sec. 1): same-sign slope in W = [15, 38) GeV, OFF never used
SSCTRL_V1 = {"b_ss": 0.03873158526861547, "sigma_ss": 0.018716037139196902,
             "b_emu": 0.0042191796953754464}
SS_TOL = 0.001
MC_WEIGHT_INFO = 2.2         # Heister sec. 2.2: ~8 M simulated vs ~3.7 M data events (information)
TESTS = ("A1", "A2", "A3", "A4")


# ----------------------------------------------------------------------------- pure helpers
def readable_hi(edges, series, lo=LO):
    """Largest upper edge hi such that no series has a None in any bin of [lo, hi).
    None when the first bin at or above lo is unreadable or lo is not reached."""
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
    return [values[i] for i in range(len(edges) - 1)
            if edges[i] >= lo - 1e-9 and edges[i + 1] <= hi + 1e-9]


def fill_nm(values, marks, edges):
    """NM -> 0.0, OFF -> None; a null with no mark raises (as dmcratio.fill with off_fill None)."""
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
            out.append(None)
        else:
            raise ValueError("null at %s GeV without an NM or OFF mark" % e)
    return out


def whole_numbers(vals, tol=WHOLE_TOL):
    return all(abs(v - round(v)) <= tol for v in vals)


def pull(b1, s1, b2, s2):
    if s1 is None or s2 is None:
        return None
    return (b1 - b2) / math.hypot(s1, s2)


def ratio_halves(n, m, xc, split=25.0):
    lo = [i for i, x in enumerate(xc) if x < split]
    hi = [i for i, x in enumerate(xc) if x >= split]
    f = lambda idx: sum(n[i] for i in idx) / max(1e-12, sum(m[i] for i in idx))
    return {"r_lo": f(lo), "r_hi": f(hi), "n_lo": sum(n[i] for i in lo),
            "m_lo": sum(m[i] for i in lo), "n_hi": sum(n[i] for i in hi),
            "m_hi": sum(m[i] for i in hi), "split": split}


def gate(r):
    """A0 of amendment 0.31 sec. 3: a list of reasons it fails (empty = PASS)."""
    why = []
    if r.get("C0") != "PASS":
        why.append("aprime_cross closure C0 %s" % r.get("C0"))
    if not r.get("ss_closure", {}).get("ok"):
        why.append("sscontrol-v1 same-sign slope not reproduced")
    hi = r.get("window_hi")
    if hi is None or hi < MIN_HI - 1e-9:
        why.append("readable window ends at %s GeV (< %.0f)" % (hi, MIN_HI))
    else:
        if not r.get("window_nonneg"):
            why.append("negative value in the window")
        if not r.get("data_whole"):
            why.append("data are not whole numbers of events")
        if (r.get("n_events") or 0.0) < MIN_EVENTS:
            why.append("fewer than %.0f data events in the window" % MIN_EVENTS)
    return why


def grade(r):
    g = {}
    why = gate(r)
    g["A0"] = "PASS" if not why else "FAIL (%s)" % "; ".join(why)
    if why:
        for k in TESTS:
            g[k] = "NOT GRADABLE (A0 failed)"
        return g
    a = r["slope_a"]
    g["A1"] = "PASS" if (a["b_hat"] > 0 and a["Z_slope"] >= 2.0) else "FAIL"
    p = r.get("pull_a_minus_ss")
    if p is None:
        g["A2"] = g["A3"] = "NOT GRADABLE (no 1-sigma interval)"
    else:
        g["A2"] = "PASS" if abs(p) < 2.0 else "FAIL"
        g["A3"] = "PASS" if (a["Z_slope"] < 1.0 and -p >= 2.0) else "FAIL"
    g["A4"] = "PASS" if r["excess_slope_free"]["Z0"] < 2.0 else "FAIL"
    return g


def _fmt(x, f="%.4f"):
    return "na" if x is None else f % x


# ----------------------------------------------------------------------------- run
def run(abtag_path, fig5_path, dmc_path, emu_path, out_dir=None, closure=True):
    if ac is None or dm is None:
        raise SystemExit("aprime_cross.py and dmcratio.py must sit next to this file")
    t0 = time.time()
    el = lambda: time.time() - t0
    print("%s on %s and %s" % (VERSION, ac.VERSION, dm.VERSION), flush=True)
    res = {"version": VERSION, "aprime_cross": ac.VERSION, "dmcratio": dm.VERSION}
    fig5, dmc, emu, ab = (ac.load(fig5_path), ac.load(dmc_path), ac.load(emu_path),
                          ac.load(abtag_path))
    if closure:
        c = ac.closure(fig5)
        res["C0"], res["C0_got"] = c["C0"], c["got"]
        print("C0 %s %s (%.0f s)" % (c["C0"], json.dumps(c["got"]), el()), flush=True)
    else:
        res["C0"] = "not run"

    # gate part 2: sscontrol-v1's same-sign slope in [15, 38) GeV
    e21 = [float(e) for e in dmc["edges"]]
    raw = {k: dm.fill(dmc[k], dmc["marks"][k], dmc["edges"], None)
           for k in ("os_data", "os_mc", "ss_data", "ss_mc")}
    raw["emu_data"] = dm.fill(emu["data"], emu["marks"]["data"], emu["edges"], None)
    raw["emu_mc"] = dm.fill(emu["mc"], emu["marks"]["mc"], emu["edges"], None)
    hi21 = readable_hi(e21, list(raw.values()))
    ok21 = hi21 is not None and abs(hi21 - SS_WINDOW_HI) < 1e-9
    b_ss = s_ss = None
    w21 = None
    if ok21:
        we21 = sub_edges(e21, LO, hi21)
        x21 = ac.centres(we21)
        w21 = {k: cut(e21, v, LO, hi21) for k, v in raw.items()}
        ss = dm.slope(w21["ss_data"], w21["ss_mc"], x21)
        b_ss, s_ss = ss["b_hat"], ss.get("sigma_b")
        ok21 = abs(b_ss - SSCTRL_V1["b_ss"]) < SS_TOL
    res["ss_closure"] = {"window_hi": hi21, "b_ss": b_ss, "sigma_ss": s_ss,
                         "want": SSCTRL_V1["b_ss"], "ok": ok21}
    print("SS closure %s: b_SS %s (want %.5f) sb %s window 15-%s (%.0f s)" % (
        "PASS" if ok21 else "FAIL", _fmt(b_ss, "%.5f"), SSCTRL_V1["b_ss"], _fmt(s_ss), hi21, el()),
        flush=True)

    # the Fig. 24 reading
    ea = [float(e) for e in ab["edges"]]
    da = fill_nm(ab["data"], ab["marks"]["data"], ea)
    ma = fill_nm(ab["mc"], ab["marks"]["mc"], ea)
    hi = readable_hi(ea, [da, ma])
    res["window_hi"] = hi
    res["grid"] = {"lo": ea[0], "hi": ea[-1], "bins": len(ea) - 1}
    if hi is None or hi < MIN_HI - 1e-9:
        res["grades"] = grade(res)
        print("ABTAG: A0 %s" % res["grades"]["A0"], flush=True)
        _dump(res, out_dir)
        return res
    we = sub_edges(ea, LO, hi)
    xw = ac.centres(we)
    n = cut(ea, da, LO, hi)
    m = cut(ea, ma, LO, hi)
    res["window_bins"] = len(xw)
    res["window_nonneg"] = all(v >= 0 for v in n + m)
    res["data_whole"] = whole_numbers(n)
    res["n_events"] = sum(n)
    res["mc_sum"] = sum(m)
    res["halves"] = ratio_halves(n, m, xw)
    print("WINDOW A 15-%.0f GeV, %d bins, data %.0f events, simulation %.1f, whole %s, nonneg %s"
          % (hi, len(xw), sum(n), sum(m), res["data_whole"], res["window_nonneg"]), flush=True)
    h = res["halves"]
    print("HALVES data/sim 15-25 %.0f/%.1f = %.3f | 25-%.0f %.0f/%.1f = %.3f" % (
        h["n_lo"], h["m_lo"], h["r_lo"], hi, h["n_hi"], h["m_hi"], h["r_hi"]), flush=True)
    if gate(res):
        res["grades"] = grade(res)
        print("ABTAG: A0 %s" % res["grades"]["A0"], flush=True)
        _dump(res, out_dir)
        return res

    a = dm.slope(n, m, xw)
    res["slope_a"] = a
    print("SLOPE A b=%.4f sb=%s Zs=%.2f [%s, %s] (%.0f s)" % (
        a["b_hat"], _fmt(a.get("sigma_b")), a["Z_slope"], _fmt(a.get("b_lo")),
        _fmt(a.get("b_hi")), el()), flush=True)
    res["pull_a_minus_ss"] = pull(a["b_hat"], a.get("sigma_b"), b_ss, s_ss)
    print("PULL A-SS %s (b_SS %.4f +- %s)" % (_fmt(res["pull_a_minus_ss"], "%.3f"), b_ss,
                                              _fmt(s_ss)), flush=True)

    s = ac.s_template(we)
    res["excess_slope_free"] = ac.discovery(n, m, s, "bb", xw, None)
    res["excess_const"] = ac.discovery(n, m, s, "bb", xw, 0.0)      # information
    for k in ("excess_slope_free", "excess_const"):
        d = res[k]
        print("EXCESS %s Z0=%.3f mu=%.3f b=%.4f (%.0f s)" % (k, d["Z0"], d["mu_hat"], d["b_hat"],
                                                            el()), flush=True)

    # information, not graded: simulation weighted as MC_WEIGHT_INFO times the data's size
    info = {"weight": MC_WEIGHT_INFO}
    k = MC_WEIGHT_INFO
    info["a"] = dm.slope(n, [k * v for v in m], xw)
    x21 = ac.centres(sub_edges(e21, LO, SS_WINDOW_HI))
    info["ss"] = dm.slope(w21["ss_data"], [k * v for v in w21["ss_mc"]], x21)
    info["os"] = dm.slope(w21["os_data"], [k * v for v in w21["os_mc"]], x21)
    res["info_mc_weight"] = info
    print("INFO weight %.1f: A b=%.4f Zs=%.2f | SS b=%.4f Zs=%.2f | OS b=%.4f Zs=%.2f (%.0f s)" % (
        k, info["a"]["b_hat"], info["a"]["Z_slope"], info["ss"]["b_hat"], info["ss"]["Z_slope"],
        info["os"]["b_hat"], info["os"]["Z_slope"], el()), flush=True)

    g = grade(res)
    res["grades"] = g
    res["elapsed_s"] = el()
    _dump(res, out_dir)
    ex = res["excess_slope_free"]
    print("ABTAG: A0 %s A1 %s A2 %s A3 %s A4 %s | W 15-%.0f n %.0f | A b=%.4f sb=%s Zs=%.2f | "
          "r %.3f->%.3f | pull A-SS %s | Z0 free %.3f mu %.3f | Z0 const %.3f | info w%.1f A Zs=%.2f"
          % (g["A0"].split(" ")[0], g["A1"], g["A2"], g["A3"], g["A4"], hi, sum(n), a["b_hat"],
             _fmt(a.get("sigma_b")), a["Z_slope"], h["r_lo"], h["r_hi"],
             _fmt(res["pull_a_minus_ss"], "%.3f"), ex["Z0"], ex["mu_hat"],
             res["excess_const"]["Z0"], k, info["a"]["Z_slope"]), flush=True)
    return res


def _dump(res, out_dir):
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "abtag.json"), "w") as fh:
            json.dump(res, fh, indent=1, default=str)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--abtag", required=True)
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--dmc", required=True)
    ap.add_argument("--emu", required=True)
    ap.add_argument("--out")
    ap.add_argument("--no-closure", action="store_true")
    a = ap.parse_args(argv)
    print("python %s" % sys.version.split()[0], flush=True)
    run(a.abtag, a.fig5, a.dmc, a.emu, a.out, closure=not a.no_closure)
    return 0


if __name__ == "__main__":
    sys.exit(main())
