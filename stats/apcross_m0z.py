# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""apcross_m0z 0.1.0: PLAN amendment 0.26. Runs stats/aprime_cross.py 0.1.0 unchanged on the two
blind readings (MC4: ALEPH simulation, EE25: ALEPH di-electrons) and adds the secondary,
labelled analysis of amendment 0.26.

Why: the MC4 reading has four unreadable di-muon values (46-49 GeV, "no marker drawn"), so the
pre-registered gate M0 of amendment 0.25 fails as written and M1-M3 are not gradable under 0.25.
Amendment 0.26 (written before any fit of the readings) fixes how such bins are filled:

* "zero"  (secondary grades M1z-M3z): a null value becomes 0.0 (ROOT, which drew the figure,
  draws no marker for an empty bin unless asked to);
* "other" (sensitivity M1f-M3f): a null value becomes the other spectrum's value in the same
  bin (ratio 1 there).

The thresholds are those of amendment 0.25, unchanged. A grade that differs between "zero" and
"other" is reported as reading-dependent.

Also (information, playbook rule on degeneracy): the significance of the ratio's slope with the
signal floated, for the mu mu data and for the e e data, from the fits aprime_cross already makes.

    python apcross_m0z.py --fig5 aleph-fig5.json --mc aleph-mc4.json --ee aleph-ee25.json --out /out

Last output line `APCROSS2:`.
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

VERSION = "mv2 apcross_m0z 0.1.0"
GRADES = ("M1", "M2", "M3")


def fill_nulls(mc, how):
    """Copy of an MC reading with null values filled; returns (copy, [(spectrum, low edge)])."""
    out = {"edges": list(mc["edges"]), "mumu": list(mc["mumu"]), "emu": list(mc["emu"])}
    filled = []
    for key, other in (("mumu", "emu"), ("emu", "mumu")):
        for i, v in enumerate(mc[key]):
            if v is not None:
                continue
            if how == "zero":
                out[key][i] = 0.0
            elif how == "other":
                o = mc[other][i]
                if o is None:
                    raise ValueError("both spectra unreadable at %s GeV" % mc["edges"][i])
                out[key][i] = float(o)
            else:
                raise ValueError("unknown fill %r" % how)
            filled.append((key, mc["edges"][i]))
    return out, filled


def degeneracy(const, slope):
    """Signed Z of the ratio's slope with the signal floated in both fits (mu >= 0)."""
    q = max(0.0, 2.0 * (slope["lnL_best"] - const["lnL_best"]))
    z = math.copysign(math.sqrt(q), slope["b_hat"]) if q > 0 else 0.0
    return {"Z_slope_signal_floated": z, "b_hat_signal_floated": slope["b_hat"],
            "mu_hat_const": const["mu_hat"], "mu_hat_slope": slope["mu_hat"],
            "Z0_const": const["Z0"], "Z0_slope": slope["Z0"]}


def agreement(a, b):
    """Per grade: the common grade, or 'reading-dependent' when the two fills differ."""
    out = {}
    for k in GRADES:
        ga, gb = a.get(k), b.get(k)
        out[k] = ga if ga == gb else "reading-dependent (zero: %s, other: %s)" % (ga, gb)
    return out


def _g(d, k, fmt="%.4f"):
    v = d.get(k) if isinstance(d, dict) else None
    return "na" if v is None else (fmt % v if isinstance(v, (int, float)) else str(v))


def mc_part(tag, r):
    if "slope" not in r:
        return "%s M0 %s" % (tag, r.get("M0"))
    sl = r["slope"]
    return ("%s b=%.4f sb=%s Zs=%.2f r1525=%.3f r2550=%.3f pull=%s Z0fix=%.3f M1 %s M2 %s M3 %s" % (
        tag, sl["b_hat"], _g(sl, "sigma_b"), sl["Z_slope"], r["ratio_15_25"], r["ratio_25_50"],
        _g(r, "M2_pull", "%.3f"), r["data_Z0_bfixed_mc"]["Z0"], r["M1"], r["M2"], r["M3"]))


def run(fig5_path, mc_path, ee_path, out_dir=None):
    if ac is None:
        raise SystemExit("aprime_cross.py must sit next to this file")
    t0 = time.time()
    print("%s on %s" % (VERSION, ac.VERSION), flush=True)
    # 1. amendment 0.25 exactly as written (C0 again, M0-M3, E0-E3)
    prim = ac.run(fig5_path, mc_path, ee_path, out_dir)
    res = {"version": VERSION, "aprime_cross": ac.VERSION, "primary": {
        "C0": prim["closure"]["C0"], "M0": prim.get("mc", {}).get("M0"),
        "E": {k: v for k, v in prim.get("ee", {}).items() if k in ("E0", "E1", "E2")}}}
    gated = prim["closure"]["C0"] == "PASS"
    sl = prim["closure"]["slope_mu0"]
    fig5, mc = ac.load(fig5_path), ac.load(mc_path)
    # 2. amendment 0.26: secondary (zero) and sensitivity (other) fills
    sec = {}
    for how in ("zero", "other"):
        mcf, filled = fill_nulls(mc, how)
        r = ac.analyse_mc(mcf, fig5, sl) if gated else {"M0": "NOT GRADABLE (C0 failed)"}
        r["filled"] = filled
        sec[how] = r
        print("MC-%s: %s (%.0f s)" % (how, mc_part(how, r), time.time() - t0), flush=True)
    res["secondary"] = sec
    res["grades_z"] = {k + "z": sec["zero"].get(k) for k in GRADES}
    res["grades_f"] = {k + "f": sec["other"].get(k) for k in GRADES}
    res["agreement"] = agreement(sec["zero"], sec["other"])
    # 3. degeneracy (information)
    deg = {"data": degeneracy(prim["closure"]["const"], prim["closure"]["slope"])}
    if "E3" in prim.get("ee", {}):
        deg["ee"] = degeneracy(prim["ee"]["E3"]["const"], prim["ee"]["E3"]["slope"])
        res["universality"] = prim["ee"].get("universality")
    res["degeneracy"] = deg
    res["elapsed_s"] = time.time() - t0
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "apcross_m0z.json"), "w") as f:
            json.dump(res, f, indent=1, default=str)
    ee = prim.get("ee", {})
    eslope = ee.get("slope", {})
    uni = res.get("universality") or {}
    line = ("APCROSS2: C0 %s | M0(0.25) %s | %s | %s | agree M1 %s M2 %s M3 %s | "
            "EE E0 %s E1 %s E2 %s b=%s sb=%s Zs=%s pull=%s | DEG data Zs=%.2f mu=%.3f/%.3f ee Zs=%s | "
            "UNIV ee_expected=%s ee_fitted=%s" % (
                res["primary"]["C0"], res["primary"]["M0"], mc_part("Mz", sec["zero"]),
                mc_part("Mf", sec["other"]), res["agreement"]["M1"], res["agreement"]["M2"],
                res["agreement"]["M3"], ee.get("E0"), ee.get("E1"), ee.get("E2"),
                _g(eslope, "b_hat"), _g(eslope, "sigma_b"), _g(eslope, "Z_slope", "%.2f"),
                _g(ee, "E2_pull", "%.3f"), deg["data"]["Z_slope_signal_floated"],
                deg["data"]["mu_hat_const"], deg["data"]["mu_hat_slope"],
                _g(deg.get("ee", {}), "Z_slope_signal_floated", "%.2f"),
                _g(uni, "expected_ee", "%.2f"), _g(uni, "fitted_ee_const", "%.2f")))
    print(line, flush=True)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--mc", required=True)
    ap.add_argument("--ee", required=True)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    print("python %s" % sys.version.split()[0], flush=True)
    run(a.fig5, a.mc, a.ee, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
