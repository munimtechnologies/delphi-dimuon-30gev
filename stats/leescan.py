# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""leescan: the look-elsewhere effect for ALEPH's 30 GeV di-muon excess in the smooth,
error-aware frame (PLAN amendment 0.34).

NOTE-aprime 0.5 gives LOCAL significances only (par3 smooth frame: 3.134 asymptotic, 3.35
toy-calibrated, at the fixed mass 30.40 GeV). Heister (arXiv:1610.06536 v9, sec. 3.6) floated the
mean in 15-50 GeV and the width, and found that the look-elsewhere effect lowers his significances
by 1.4-1.6 sigma, in his own frame (the smoothed e mu template treated as exact). This module asks
the same question in the frame where the template keeps its counting error (par3, the primary
method of amendment 0.24):

  How often does a background-only spectrum produce, ANYWHERE between 17 and 48 GeV, a local
  excess at least as significant as the one ALEPH saw at 30.40 GeV?

Method (fixed before any run, amendment 0.34):
  * Frame: aprime_smooth.ParFit, degree 3 (par3), joint Poisson fit of the e mu template m and the
    mu mu spectrum n; imported UNCHANGED (stats/aprime_smooth.py, sha256 checked) with
    stats/emuframe.py 0.1.0 (git blob checked by aprime_smooth.fetch_emuframe).
  * Signal: Voigt with Gamma (FWHM) and Gaussian sigma = sqrt(6e-4) * mass (Heister's eq. 1),
    truncated to 15-50 GeV, 32.31 events at mu = 1 (as emuframe). Mass grid 17.00-48.00 GeV in
    0.25 GeV steps (125 points; 2 GeV kept from the ends so no shape is cut in half).
    PRIMARY: Gamma = 1.78 GeV fixed (ALEPH's fitted width). FLOAT: the largest Z over
    Gamma in {1.0, 1.78, 3.0} at each mass (Heister-style floated width, coarse grid).
  * Local Z(mass) = sqrt(q0), q0 one-sided, exactly as ParFit.discovery (same three starts).
  * Toys: background only, drawn from the par3 mu = 0 fit to the reading (the truth that
    aprime-smooth-v1 used); both spectra fluctuated; every toy scanned over the full grid.
  * Global p (primary statement): the fraction of toys whose maximum Z over the grid is at least
    the observed local Z at 30.40 GeV. Gross-Vitells (2010) extrapolation
    p = p_local(Z) + E[N(u0)] exp(-(Z^2 - u0^2) / 2), u0 = 1, is used only for local values the
    toys cannot reach (e.g. Heister's 5.35), and is checked against the toys at Z = 2 (grade L2).

    python leescan.py --fetch-only
    python leescan.py --out /out --ntoys 2000 --workers 2 --budget-s 14000
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

VERSION = "mv2 leescan 0.1.0"
REPO = "https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main/"
HERE = os.path.dirname(os.path.abspath(__file__))
FATAL = {   # sha256 of the exact files earlier jobs ran (fetch_mods.py of amendment 0.32)
    "stats/aprime_smooth.py": "eae6510abcd327c385585095117e1fa3ba1cec8fa5e74aa9d605f230f0ed8d28",
    "data/aleph-fig5.json": "f535d924111e215b71f6a308e6c228cead13680512498517680863b05b7ee626",
}
SEED = 20261121
MASSES = tuple(round(17.0 + 0.25 * k, 2) for k in range(125))      # 17.00 ... 48.00
GAMMAS = (1.0, 1.78, 3.0)
PRIMARY_GAMMA = 1.78
RES = math.sqrt(6e-4)                    # Heister eq. 1: sigma = sqrt(6e-4) * mass
M_OBS = 30.40
STARTS = (0.0, 0.8, 2.0)                 # as aprime_smooth.ParFit.fit
LEVELS = (0.5, 1.0, 1.5, 2.0)
U0 = 1.0
DIRECT_Z = (1.5, 2.0, 2.5, 3.0)
NTHETA = 4000
Z_PAR3_OBS = 3.134                       # NOTE-aprime 0.5 sec. 9 (aprime-smooth-v1)
CLOSURE_TOL = 0.01
SCAN_TOL = 0.002
MIN_TOYS = 1000
VARIANTS = ("g1.78", "g1.0", "g3.0", "float")
PRIMARY = "g1.78"
REFERENCE = (("Heister Z_asym, TKDE frame, as published", 5.35),
             ("par3 toy-calibrated (aprime-smooth-v1)", 3.35),
             ("bb asymptotic (aprime-aleph-v1)", 2.664),
             ("par3 with fitted rising ratio (aprime-slsm-v2)", 2.295),
             ("par3 with same-sign constrained ratio (ssframe-v1)", 2.134))
# grades of amendment 0.34 sec. 3
L1_RANGE = (1.0, 2.6)
L3_MAX = 2.5
L5_WINDOW = (29.0, 32.0)


# ----------------------------------------------------------------------------- pure helpers
def p_from_z(z):
    """One-sided tail 1 - Phi(z)."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def z_from_p(p):
    """Z with 1 - Phi(Z) = p (bisection)."""
    if p <= 0.0:
        return float("inf")
    if p >= 1.0:
        return float("-inf")
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if p_from_z(mid) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def count_upcrossings(zs, u):
    """Number of i with zs[i-1] < u <= zs[i] along the grid."""
    return sum(1 for i in range(1, len(zs)) if zs[i - 1] < u <= zs[i])


def gv_global_p(z, en_u0, u0=U0):
    """Gross-Vitells: p_global = p_local(z) + E[N(u0)] exp(-(z^2 - u0^2) / 2) (one-sided q0)."""
    return min(1.0, p_from_z(z) + en_u0 * math.exp(-0.5 * (z * z - u0 * u0)))


def mean_se(xs):
    n = len(xs)
    if n == 0:
        return None, None
    mu = sum(xs) / n
    if n < 2:
        return mu, None
    var = sum((x - mu) ** 2 for x in xs) / (n - 1)
    return mu, math.sqrt(var / n)


def direct_global(zmax, z_obs):
    """Fraction of toys with max Z >= z_obs; Z_global; lower bound from 3/n if no toy reaches it."""
    n = len(zmax)
    k = sum(1 for z in zmax if z >= z_obs - 1e-9)
    if n == 0:
        return {"k": 0, "n": 0, "p": None, "Z": None, "lower_bound": False}
    if k == 0:
        return {"k": 0, "n": n, "p": 0.0, "Z": z_from_p(3.0 / n), "lower_bound": True}
    p = k / n
    return {"k": k, "n": n, "p": p, "p_se": math.sqrt(p * (1.0 - p) / n), "Z": z_from_p(p),
            "lower_bound": False}


def variant_profile(z_by_gamma, variant):
    """The Z(mass) curve of a variant from {gamma: [Z per mass]}."""
    if variant == "float":
        keys = list(z_by_gamma)
        return [max(z_by_gamma[g][i] for g in keys) for i in range(len(z_by_gamma[keys[0]]))]
    return list(z_by_gamma[float(variant[1:])])


def row_from_profiles(idx, z_by_gamma, masses=MASSES):
    row = {"idx": idx}
    for v in VARIANTS:
        zs = variant_profile(z_by_gamma, v)
        i = max(range(len(zs)), key=lambda k: zs[k])
        row[v + "_zmax"] = zs[i]
        row[v + "_mmax"] = masses[i]
        for u in LEVELS:
            row["%s_n%.1f" % (v, u)] = count_upcrossings(zs, u)
    return row


def csv_columns():
    cols = ["idx"]
    for v in VARIANTS:
        cols += [v + "_zmax", v + "_mmax"] + ["%s_n%.1f" % (v, u) for u in LEVELS]
    return cols


def summarize(rows, z_obs):
    """rows: toy rows; z_obs: {variant: observed local Z at 30.40 GeV}."""
    out = {}
    n = len(rows)
    for v in VARIANTS:
        zmax = [r[v + "_zmax"] for r in rows]
        en = {}
        for u in LEVELS:
            mu, se = mean_se([r["%s_n%.1f" % (v, u)] for r in rows])
            en["%.1f" % u] = {"mean": mu, "se": se}
        direct = {}
        for z in DIRECT_Z:
            d = direct_global(zmax, z)
            d["gv_p"] = gv_global_p(z, en["%.1f" % U0]["mean"]) if n else None
            direct["%.1f" % z] = d
        res = {"ntoys": n, "E_N": en, "direct": direct,
               "mean_zmax": (sum(zmax) / n) if n else None}
        if v in z_obs and n:
            zo = z_obs[v]
            g = direct_global(zmax, zo)
            res["observed"] = {"Z_local": zo, "p_local": p_from_z(zo), "direct": g,
                               "gv_p": gv_global_p(zo, en["%.1f" % U0]["mean"]),
                               "gv_Z": z_from_p(gv_global_p(zo, en["%.1f" % U0]["mean"]))}
        conv = []
        for name, zl in REFERENCE:
            pg = gv_global_p(zl, en["%.1f" % U0]["mean"]) if n else None
            conv.append({"what": name, "Z_local": zl, "gv_p": pg,
                         "gv_Z": z_from_p(pg) if pg is not None else None,
                         "direct": direct_global(zmax, zl) if n else None})
        res["conversions"] = conv
        out[v] = res
    return out


def grade(gate, summ, obs_argmax):
    g = {}
    if not gate["ok"]:
        g["L0"] = "FAIL (%s)" % gate["why"]
        for k in ("L1", "L2", "L3", "L4", "L5"):
            g[k] = "NOT GRADABLE (L0 failed)"
        return g
    g["L0"] = "PASS"
    p = summ[PRIMARY]
    en1 = p["E_N"]["%.1f" % U0]["mean"]
    g["L1"] = "PASS" if L1_RANGE[0] <= en1 <= L1_RANGE[1] else "FAIL"
    d2 = p["direct"]["2.0"]
    pg = d2["gv_p"]
    tol = max(2.0 * math.sqrt(pg * (1.0 - pg) / d2["n"]), 0.15 * pg)
    g["L2"] = "PASS" if abs(d2["p"] - pg) <= tol else "FAIL"
    o = p["observed"]["direct"]
    if o["lower_bound"]:
        g["L3"] = "FAIL" if o["Z"] >= L3_MAX else "UNDETERMINED (no toy reached the observed Z)"
    else:
        g["L3"] = "PASS" if o["Z"] < L3_MAX else "FAIL"
    f = summ["float"]["observed"]["direct"]
    if f["lower_bound"] or o["lower_bound"]:
        g["L4"] = "UNDETERMINED (a lower bound is involved)"
    else:
        g["L4"] = "PASS" if f["Z"] < o["Z"] else "FAIL"
    g["L5"] = "PASS" if L5_WINDOW[0] <= obs_argmax <= L5_WINDOW[1] else "FAIL"
    return g


# ----------------------------------------------------------------------------- fetching
def _get(path, tries=10, wait=30):
    for k in range(tries):
        try:
            return urllib.request.urlopen(REPO + path, timeout=60).read()
        except Exception as exc:   # network hiccup: retry
            print("attempt %d for %s failed: %s" % (k + 1, path, exc), flush=True)
            time.sleep(wait)
    raise SystemExit("could not fetch " + path)


def fetch(here=HERE):
    for path, want in FATAL.items():
        dest = os.path.join(here, os.path.basename(path))
        data = open(dest, "rb").read() if os.path.exists(dest) else _get(path)
        h = hashlib.sha256(data).hexdigest()
        if h != want:
            raise SystemExit("%s sha256 %s != %s" % (path, h, want))
        with open(dest, "wb") as f:
            f.write(data)
        print("fetched %s (%d bytes) sha256 %s (matches)" % (path, len(data), h), flush=True)
    asm = load_asm(here, bind_emuframe=False)
    sha = asm.fetch_emuframe(os.path.join(here, "emuframe.py"))
    print("emuframe.py git blob %s (matches)" % sha, flush=True)


def load_asm(here=HERE, bind_emuframe=True):
    spec = importlib.util.spec_from_file_location("aprime_smooth",
                                                  os.path.join(here, "aprime_smooth.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if bind_emuframe:
        mod.bind(path=os.path.join(here, "emuframe.py"))
    return mod


# ----------------------------------------------------------------------------- scanning
class Scanner:
    """Local Z = sqrt(q0) of the par3 frame for a list of signal shapes; identical to
    ParFit.discovery for each shape (same mu = 0 fit, same three starts, same bounds)."""

    def __init__(self, asm, edges, shapes):
        import numpy as np
        self.np = np
        self.asm = asm
        self.S = [np.array(s, dtype=float) for s in shapes]
        self.pf = asm.ParFit(edges, shapes[0], 3)

    def scan(self, n, m):
        np = self.np
        n = np.asarray(n, dtype=float)
        m = np.asarray(m, dtype=float)
        b0 = self.pf.fit(n, m, mu_fixed=0.0)
        f0 = -b0["lnL"]
        pb = np.concatenate([np.array(b0["a"]), [math.log(b0["r"]), 0.0]])
        out = []
        for s in self.S:
            self.pf.s = s
            best = f0
            for mu0 in STARTS:
                p0 = pb.copy()
                p0[-1] = mu0
                res = self.pf._min(p0, n, m, (0.0, self.asm.MU_MAX))
                if float(res.fun) < best:
                    best = float(res.fun)
            out.append(math.sqrt(max(0.0, 2.0 * (f0 - best))))
        return out, b0


def grid_shapes(ef, edges, masses=MASSES, gammas=GAMMAS, ntheta=NTHETA):
    """{gamma: [s per mass]} with s = N_ALEPH * Voigt bin probabilities."""
    return {g: [[ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges, m=x, gamma=g, sigma=RES * x,
                                                             n_theta=ntheta)]
                for x in masses] for g in gammas}


def split(zs, gammas=GAMMAS, nm=len(MASSES)):
    return {g: zs[k * nm:(k + 1) * nm] for k, g in enumerate(gammas)}


_G = {}


def _init(here, edges, flat_shapes, truth_T, truth_r):
    asm = load_asm(here)
    _G["sc"] = Scanner(asm, edges, flat_shapes)
    _G["T"], _G["r"] = truth_T, truth_r


def one_toy(idx):
    import numpy as np
    rng = np.random.default_rng(SEED + idx)
    T = np.array(_G["T"])
    n = rng.poisson(_G["r"] * T)
    m = rng.poisson(T)
    zs, _ = _G["sc"].scan(n, m)
    return row_from_profiles(idx, split(zs))


# ----------------------------------------------------------------------------- driver
def run(out_dir, ntoys, workers, budget_s, here=HERE):
    from multiprocessing import Pool
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    asm = load_asm(here)
    ef = asm.ef
    fig5 = json.load(open(os.path.join(here, "aleph-fig5.json")))
    edges, n, v = fig5["edges"], fig5["n"], fig5["v_scaled"]
    m = [vi / ef.R0_ALEPH for vi in v]
    res = {"version": VERSION, "aprime_smooth": asm.VERSION, "emuframe": ef.VERSION, "seed": SEED,
           "masses": list(MASSES), "gammas": list(GAMMAS), "res": RES, "u0": U0}
    path = os.path.join(out_dir, "leescan.json")

    def save():
        res["elapsed_s"] = time.time() - t0
        with open(path, "w") as f:
            json.dump(res, f, indent=1)

    # gate: closure with aprime-smooth-v1 and scanner == ParFit.discovery
    s0 = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    pf0 = asm.ParFit(edges, s0, 3)
    d0 = pf0.discovery(n, m)
    z_scan0 = Scanner(asm, edges, [s0]).scan(n, m)[0][0]
    gate = {"Z_par3_closure": d0["Z0"], "Z_scanner_default_shape": z_scan0,
            "closure_ok": abs(d0["Z0"] - Z_PAR3_OBS) <= CLOSURE_TOL,
            "scanner_ok": abs(z_scan0 - d0["Z0"]) <= SCAN_TOL}
    print("CLOSURE par3 Z0=%.4f (want %.3f) scanner=%.4f" % (d0["Z0"], Z_PAR3_OBS, z_scan0),
          flush=True)

    # shapes
    shapes = grid_shapes(ef, edges)
    flat = [s for g in GAMMAS for s in shapes[g]]
    obs_shapes = [[ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges, m=M_OBS, gamma=g,
                                                               sigma=RES * M_OBS, n_theta=NTHETA)]
                  for g in GAMMAS]
    print("shapes ready in %.0f s" % (time.time() - t0), flush=True)

    # observed scan
    sc = Scanner(asm, edges, flat + obs_shapes)
    zs, b0 = sc.scan(n, m)
    zgrid = split(zs[:len(flat)])
    z_at_obs = dict(zip(GAMMAS, zs[len(flat):]))
    obs = {"Z_grid": {str(g): zgrid[g] for g in GAMMAS},
           "Z_at_30.40": {str(g): z_at_obs[g] for g in GAMMAS}}
    for v_ in VARIANTS:
        prof = variant_profile(zgrid, v_)
        i = max(range(len(prof)), key=lambda k: prof[k])
        obs[v_] = {"zmax": prof[i], "mmax": MASSES[i],
                   "upcrossings": {"%.1f" % u: count_upcrossings(prof, u) for u in LEVELS}}
        print("OBS %s scan max Z=%.3f at %.2f GeV" % (v_, prof[i], MASSES[i]), flush=True)
    z_obs = {"g1.78": d0["Z0"], "g1.0": z_at_obs[1.0], "g3.0": z_at_obs[3.0],
             "float": max(d0["Z0"], z_at_obs[1.0], z_at_obs[3.0])}
    obs["Z_obs_used"] = z_obs
    print("OBS Z at 30.40: g1.0=%.3f g1.78=%.3f (exact emuframe shape %.3f) g3.0=%.3f" % (
        z_at_obs[1.0], z_at_obs[1.78], d0["Z0"], z_at_obs[3.0]), flush=True)
    f0 = pf0.fit(n, m, mu_fixed=0.0)
    import numpy as np
    truth_T = [float(x) for x in pf0.T(np.array(f0["a"]))]
    res.update({"gate": gate, "observed": obs,
                "truth": {"r": f0["r"], "sum_T": sum(truth_T), "T": truth_T}})
    save()

    # toys, saved as they finish
    cols = csv_columns()
    csv_path = os.path.join(out_dir, "toys.csv")
    rows = []
    with open(csv_path, "w") as fcsv:
        fcsv.write(",".join(cols) + "\n")
        pool = Pool(workers, initializer=_init, initargs=(here, edges, flat, truth_T, f0["r"]))
        stopped = False
        try:
            for row in pool.imap_unordered(one_toy, range(ntoys), chunksize=2):
                rows.append(row)
                fcsv.write(",".join(("%.5f" % row[c]) if isinstance(row[c], float) else str(row[c])
                                    for c in cols) + "\n")
                fcsv.flush()
                if len(rows) % 100 == 0:
                    print("toys done %d of %d, %.0f s" % (len(rows), ntoys, time.time() - t0),
                          flush=True)
                if time.time() - t0 > budget_s:
                    print("budget reached after %d toys" % len(rows), flush=True)
                    stopped = True
                    break
        finally:
            if stopped:
                pool.terminate()
            else:
                pool.close()
            pool.join()
    rows.sort(key=lambda r: r["idx"])
    gate["ntoys"] = len(rows)
    gate["ok"] = gate["closure_ok"] and gate["scanner_ok"] and len(rows) >= MIN_TOYS
    gate["why"] = ", ".join(w for w, bad in (("closure", not gate["closure_ok"]),
                                             ("scanner", not gate["scanner_ok"]),
                                             ("toys<%d" % MIN_TOYS, len(rows) < MIN_TOYS)) if bad)
    summ = summarize(rows, z_obs)
    res["summary"] = summ
    res["grades"] = grade(gate, summ, obs[PRIMARY]["mmax"])
    save()
    return res


def line(res):
    s, o, g = res["summary"], res["observed"], res["grades"]
    parts = ["toys %d" % res["gate"]["ntoys"],
             "closure %.4f scanner %.4f" % (res["gate"]["Z_par3_closure"],
                                           res["gate"]["Z_scanner_default_shape"])]
    for v in VARIANTS:
        x = s[v]
        ob = x.get("observed", {})
        d = ob.get("direct", {})
        parts.append("%s: obs max %.3f@%.2f; E[N(1)] %.3f+-%.3f; Zloc %.3f -> direct p %s Z %s%s; GV Z %.3f" % (
            v, o[v]["zmax"], o[v]["mmax"], x["E_N"]["1.0"]["mean"], x["E_N"]["1.0"]["se"] or 0.0,
            ob.get("Z_local", float("nan")),
            ("%.4f" % d["p"]) if d.get("p") is not None else "-",
            (">=" if d.get("lower_bound") else "") + (("%.3f" % d["Z"]) if d.get("Z") is not None else "-"),
            "", ob.get("gv_Z", float("nan"))))
    conv = s[PRIMARY]["conversions"]
    parts.append("GV(primary) " + "; ".join("%.3f->%.3f" % (c["Z_local"], c["gv_Z"]) for c in conv))
    d2 = s[PRIMARY]["direct"]["2.0"]
    parts.append("P(max>=2) direct %.4f GV %.4f" % (d2["p"], d2["gv_p"]))
    parts.append(" ".join("%s %s" % (k, v.split(" ")[0]) for k, v in sorted(g.items())))
    return "LEESCAN: " + " | ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-only", action="store_true")
    ap.add_argument("--out", default="/out")
    ap.add_argument("--ntoys", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--budget-s", type=float, default=14000.0)
    a = ap.parse_args(argv)
    fetch()
    if a.fetch_only:
        return
    print(VERSION, flush=True)
    res = run(a.out, a.ntoys, a.workers, a.budget_s)
    print(json.dumps({"gate": res["gate"], "grades": res["grades"],
                      "observed_max": {v: res["observed"][v] for v in VARIANTS},
                      "Z_at_30.40": res["observed"]["Z_at_30.40"]}, indent=1), flush=True)
    for v in VARIANTS:
        x = res["summary"][v]
        print("SUMMARY %s %s" % (v, json.dumps({"E_N": x["E_N"], "direct": x["direct"],
                                                 "observed": x.get("observed"),
                                                 "conversions": x["conversions"]})), flush=True)
    try:
        print(line(res), flush=True)
    except (TypeError, KeyError, ValueError) as exc:   # e.g. no toys finished
        print("LEESCAN: summary line unavailable (%s); grades %s" % (exc, res["grades"]),
              flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
