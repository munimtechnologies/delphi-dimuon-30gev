# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""aprime_ext: does a mass-dependent mu mu / e mu ratio change A'-ALEPH? (PLAN amendment 0.23)

A'-ALEPH (amendment 0.19 sec. 3, graded in NOTE-aprime 0.1) fitted ALEPH's opposite-sign mu mu
spectrum against its e mu spectrum with ONE mu mu / e mu ratio r for all masses. The blind
readings of Heister's Fig. 5 (15-50 GeV, ALEPHK) and of its 5-15 GeV bins (ALEPHLOW2) show the
mu mu data at 0.96 of the scaled e mu background in 5-15 GeV and 1.20 in 15-50 GeV. This module
refits with a log-linear ratio

    r_i = r * exp(b * (x_i - 30.40)),   x_i = bin centre (GeV),

(r is the ratio AT the signal mass, b free), on 15-50 GeV and on 5-50 GeV, for emuframe's two
template treatments ("bb": the e mu template's Poisson error kept, Barlow-Beeston; "exact": the
template treated as exact). It also tests, at mu = 0, one ratio for 5-15 GeV against another for
15-50 GeV ("split").

The likelihood pieces (t_hat, the Voigt CDF, ALEPH's fixed signal) come from stats/emuframe.py
0.1.0, unchanged (git blob d55c900f checked when it is fetched).

    python aprime_ext.py --fetch-only --emuframe /work/emuframe.py
    python aprime_ext.py --fig5 aleph-fig5.json --low aleph-low2.json --emuframe /work/emuframe.py --out /out
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

VERSION = "mv2 aprime_ext 0.1.0"
EMUFRAME_URL = ("https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/"
                "main/stats/emuframe.py")
EMUFRAME_BLOB = "d55c900fdb45aa9f8a6099a142079a510c3afdfa"   # stats/emuframe.py 0.1.0
PIVOT = 30.40                     # the ratio r is quoted at ALEPH's fitted mass
B_RANGE = (-0.2, 0.2)             # slope search range, per GeV
LNR_HALF = 4.0                    # ln r searched within +-4 of ln(N/M)
CLOSURE = {"bb": 2.6640384798138936, "exact": 4.178326392781588}   # aprime-aleph-v1
CLOSURE_TOL = 0.005

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
        import emuframe as mod   # noqa: E402
        ef = mod
    return ef


# ----------------------------------------------------------------------------- inputs
def centres(edges):
    return [0.5 * (edges[i] + edges[i + 1]) for i in range(len(edges) - 1)]


def s_template(edges, n_sig=None, norm=(15.0, 50.0), n_theta=4000):
    """ALEPH's fixed signal (Voigt, m 30.40, Gamma 1.78, sigma 0.745) per bin, with n_sig events
    in the NORMALISATION range (15-50 GeV, where Heister's 32.31 were fitted). Bins outside that
    range get the same profile's tail, so 5-15 GeV bins carry the small tail below 15 GeV."""
    n_sig = ef.N_ALEPH if n_sig is None else n_sig
    cdf = lambda x: ef._cdf_voigt(x, ef.M0, ef.GAMMA0, ef.SIGMA0, n_theta)
    c = [cdf(x) for x in edges]
    tot = cdf(norm[1]) - cdf(norm[0])
    return [n_sig * (c[i + 1] - c[i]) / tot for i in range(len(edges) - 1)]


def combine_readings(low, fig5):
    """5-15 GeV reading followed by the 15-50 GeV reading (edges must meet at 15 GeV)."""
    if abs(low["edges"][-1] - fig5["edges"][0]) > 1e-9:
        raise ValueError("readings do not meet: %s vs %s" % (low["edges"][-1], fig5["edges"][0]))
    edges = list(low["edges"]) + list(fig5["edges"][1:])
    n = list(low["n"]) + list(fig5["n"])
    v = list(low["v_scaled"]) + list(fig5["v_scaled"])
    if not (len(edges) == len(n) + 1 == len(v) + 1):
        raise ValueError("bin count mismatch")
    return edges, n, v


# ----------------------------------------------------------------------------- likelihood
def lnl_r(n, m, s, rs, mu, model):
    """emuframe's likelihood with a per-bin ratio rs[i] (constants dropped)."""
    tot = 0.0
    if model == "bb":
        for ni, mi, si, ri in zip(n, m, s, rs):
            t = ef.t_hat(ni, mi, si, ri, mu)
            lam = ri * t + mu * si
            if (ni > 0 and lam <= 0.0) or (mi > 0 and t <= 0.0):
                return float("-inf")
            tot += ef._xlogy(ni, lam) - lam + ef._xlogy(mi, t) - t
        return tot
    for ni, mi, si, ri in zip(n, m, s, rs):
        lam = ri * mi + mu * si
        if lam <= 0.0:
            if ni > 0:
                return float("-inf")
            continue
        tot += ef._xlogy(ni, lam) - lam
    return tot


def _x0(n, m):
    big_n, big_m = sum(n), sum(m)
    return math.log(big_n / big_m) if big_n > 0 and big_m > 0 else 0.0


def prof_const(n, m, s, mu, model):
    """max over r (one ratio for all bins) at fixed mu."""
    x0 = _x0(n, m)
    k = len(n)
    f = lambda x: lnl_r(n, m, s, [math.exp(x)] * k, mu, model)
    x, v = ef._scan_then_golden(f, x0 - LNR_HALF, x0 + LNR_HALF, n=24)
    return {"r": math.exp(x), "b": 0.0, "lnL": v}


def prof_slope(n, m, s, mu, model, xc, b_range=B_RANGE):
    """max over (r, b) at fixed mu; r_i = r exp(b (x_i - PIVOT))."""
    x0 = _x0(n, m)

    def inner(b):
        w = [math.exp(b * (xi - PIVOT)) for xi in xc]
        f = lambda x: lnl_r(n, m, s, [math.exp(x) * wi for wi in w], mu, model)
        return ef._scan_then_golden(f, x0 - LNR_HALF, x0 + LNR_HALF, n=24)

    b, _ = ef._scan_then_golden(lambda bb: inner(bb)[1], b_range[0], b_range[1], n=40)
    x, v = inner(b)
    return {"r": math.exp(x), "b": b, "lnL": v}


def fit_mu(prof, mu_hi=4.0):
    """mu >= 0 maximising prof(mu)["lnL"]; returns (best dict with "mu", mu = 0 dict)."""
    for _ in range(5):
        mu, v = ef._scan_then_golden(lambda u: prof(u)["lnL"], 0.0, mu_hi, n=40)
        if mu < 0.95 * mu_hi:
            break
        mu_hi *= 3.0
    p0 = prof(0.0)
    if p0["lnL"] >= v:
        mu = 0.0
    best = dict(prof(mu))
    best["mu"] = mu
    return best, p0


def discovery(n, m, s, model, kind, xc=None):
    if kind == "const":
        prof = lambda mu: prof_const(n, m, s, mu, model)
    elif kind == "slope":
        prof = lambda mu: prof_slope(n, m, s, mu, model, xc)
    else:
        raise ValueError(kind)
    best, p0 = fit_mu(prof)
    q0 = max(0.0, 2.0 * (best["lnL"] - p0["lnL"]))
    p1 = prof(1.0)
    return {"mu_hat": best["mu"], "r_hat": best["r"], "b_hat": best["b"], "r_mu0": p0["r"],
            "b_mu0": p0["b"], "q0": q0, "Z0": math.sqrt(q0), "lnL_best": best["lnL"],
            "lnL_mu0": p0["lnL"], "dll_mu1": max(0.0, 2.0 * (best["lnL"] - p1["lnL"]))}


def slope_z(res_const, res_slope):
    """Signed significance of the slope at mu = 0 (1 dof): sign(b) sqrt(2 Delta lnL)."""
    q = max(0.0, 2.0 * (res_slope["lnL_mu0"] - res_const["lnL_mu0"]))
    return math.copysign(math.sqrt(q), res_slope["b_mu0"]) if q > 0 else 0.0


def split_test(edges, n, m, s, cut=15.0, model="bb"):
    """At mu = 0: one ratio below `cut`, another above, against one common ratio."""
    lo = [i for i in range(len(n)) if edges[i + 1] <= cut + 1e-9]
    hi = [i for i in range(len(n)) if edges[i] >= cut - 1e-9]
    sub = lambda idx, arr: [arr[i] for i in idx]
    a = prof_const(sub(lo, n), sub(lo, m), sub(lo, s), 0.0, model)
    b = prof_const(sub(hi, n), sub(hi, m), sub(hi, s), 0.0, model)
    c = prof_const(n, m, s, 0.0, model)
    q = max(0.0, 2.0 * (a["lnL"] + b["lnL"] - c["lnL"]))
    return {"model": model, "cut": cut, "r_lo": a["r"], "r_hi": b["r"], "r_all": c["r"],
            "n_lo": sum(sub(lo, n)), "m_lo": sum(sub(lo, m)), "n_hi": sum(sub(hi, n)),
            "m_hi": sum(sub(hi, m)), "Z_split": math.sqrt(q)}


# ----------------------------------------------------------------------------- grades
def grade(res):
    g = {}
    c = res["15-50"]
    ok = all(abs(c[mdl]["const"]["Z0"] - CLOSURE[mdl]) < CLOSURE_TOL for mdl in ("bb", "exact"))
    g["X0"] = "PASS" if ok else "FAIL"
    if not ok:
        for k in ("X1", "X2", "X3"):
            g[k] = "NOT GRADABLE (X0 failed)"
        return g
    g["X1"] = "PASS" if c["bb"]["slope"]["Z0"] < 3.0 else "FAIL"
    g["X2"] = "PASS" if abs(c["Z_slope_bb"]) < 2.0 else "FAIL"
    w = res.get("5-50")
    if w is not None:
        g["X3"] = "PASS" if w["bb"]["slope"]["Z0"] < 3.0 else "FAIL"
    return g


# ----------------------------------------------------------------------------- driver
def run(fig5, low, out_dir, ranges=("15-50", "5-50")):
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    r0 = ef.R0_ALEPH
    sets = {"15-50": (fig5["edges"], fig5["n"], fig5["v_scaled"])}
    if "5-50" in ranges:
        sets["5-50"] = combine_readings(low, fig5)
    res = {"version": VERSION, "emuframe": ef.VERSION, "pivot": PIVOT, "r0": r0,
           "b_range": list(B_RANGE)}
    path = os.path.join(out_dir, "aprime_ext.json")

    def save():
        res["elapsed_s"] = time.time() - t0
        with open(path, "w") as f:
            json.dump(res, f, indent=1)

    for label in ranges:
        edges, n, v = sets[label]
        m = [vi / r0 for vi in v]
        s = s_template(edges)
        xc = centres(edges)
        block = {"edges": [edges[0], edges[-1]], "n_sum": sum(n), "v_sum": sum(v),
                 "s_sum": sum(s), "bb": {}, "exact": {}}
        res[label] = block
        for kind in ("const", "slope"):
            for model in ("bb", "exact"):
                t1 = time.time()
                d = discovery(n, m, s, model, kind, xc)
                d["seconds"] = time.time() - t1
                block[model][kind] = d
                print("FIT %s %s %s: Z0=%.3f mu_hat=%.3f r_hat=%.4f b_hat=%.4f b_mu0=%.4f "
                      "dll_mu1=%.3f (%.0f s)" % (label, model, kind, d["Z0"], d["mu_hat"],
                                                  d["r_hat"], d["b_hat"], d["b_mu0"],
                                                  d["dll_mu1"], d["seconds"]), flush=True)
                save()
        for model in ("bb", "exact"):
            block["Z_slope_" + model] = slope_z(block[model]["const"], block[model]["slope"])
        print("SLOPE %s: Z_slope_bb=%.3f Z_slope_exact=%.3f" % (
            label, block["Z_slope_bb"], block["Z_slope_exact"]), flush=True)
        if label == "5-50":
            res["split"] = split_test(edges, n, m, s)
            print("SPLIT: %s" % json.dumps(res["split"]), flush=True)
        save()
    res["grades"] = grade(res)
    save()
    return res


def apext_line(res):
    a = res["15-50"]
    parts = ["X0 bb=%.3f ex=%.3f" % (a["bb"]["const"]["Z0"], a["exact"]["const"]["Z0"]),
             "15-50 slope Z0bb=%.3f Z0ex=%.3f b=%.4f muhat=%.3f Zslope=%.2f" % (
                 a["bb"]["slope"]["Z0"], a["exact"]["slope"]["Z0"], a["bb"]["slope"]["b_mu0"],
                 a["bb"]["slope"]["mu_hat"], a["Z_slope_bb"])]
    w = res.get("5-50")
    if w is not None:
        parts.append("5-50 const Z0bb=%.3f Z0ex=%.3f | slope Z0bb=%.3f Z0ex=%.3f b=%.4f "
                     "muhat=%.3f Zslope=%.2f" % (
                         w["bb"]["const"]["Z0"], w["exact"]["const"]["Z0"],
                         w["bb"]["slope"]["Z0"], w["exact"]["slope"]["Z0"],
                         w["bb"]["slope"]["b_mu0"], w["bb"]["slope"]["mu_hat"], w["Z_slope_bb"]))
    sp = res.get("split")
    if sp is not None:
        parts.append("split r_lo=%.4f r_hi=%.4f Z=%.2f" % (sp["r_lo"], sp["r_hi"], sp["Z_split"]))
    parts.append(" ".join("%s %s" % (k, v) for k, v in sorted(res["grades"].items())))
    return "APEXT: " + " | ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fig5")
    ap.add_argument("--low")
    ap.add_argument("--out")
    ap.add_argument("--emuframe", required=True, help="path of emuframe.py (fetched if absent)")
    ap.add_argument("--fetch-only", action="store_true")
    a = ap.parse_args(argv)
    sha = fetch_emuframe(a.emuframe)
    print("emuframe blob", sha, flush=True)
    if a.fetch_only:
        return
    bind(path=a.emuframe)
    fig5 = json.load(open(a.fig5))
    low = json.load(open(a.low))
    print("%s with %s; 15-50: sum n %d, sum v %.1f; 5-15: sum n %d, sum v %.1f" % (
        VERSION, ef.VERSION, sum(fig5["n"]), sum(fig5["v_scaled"]), sum(low["n"]),
        sum(low["v_scaled"])), flush=True)
    res = run(fig5, low, a.out)
    print(apext_line(res), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
