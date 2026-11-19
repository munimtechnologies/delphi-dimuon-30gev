# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""aprime_toys: background-only pseudo-experiments for test A' (PLAN amendment 0.19, sec. 4).

Question: on an ALEPH-sized spectrum (1457 background mu mu pairs in 15-50 GeV, 1 GeV bins, e mu
template 1/r0 = 1.88 times larger), how often does a pure background fluctuation give a local
Z0 >= 2 or >= 3 at the fixed ALEPH mass and shape, when the e mu template is
  bb      fitted with its own Poisson error (emuframe model "bb", the A' method),
  exact   treated as exact, unsmoothed,
  kde1    Gaussian-kernel smoothed (h = 1 GeV) and then treated as exact,
  kde2    smoothed with h = 2 GeV and treated as exact?
Asymptotic one-sided rates: P(Z0 >= 2) = 0.0228, P(Z0 >= 3) = 0.00135.

No real data are used: the shapes are made up (exponential, decay length 4 and 8 GeV).
Also times emuframe.delphi_aprime on a made-up 700-bin (50 MeV) spectrum (C5).

    python aprime_toys.py --out /out --ntoys 1000 --workers 2
"""
import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emuframe as ef  # noqa: E402

VERSION = "mv2 aprime_toys 0.1.0"
EDGES = [15.0 + i for i in range(36)]
N_BKG = 1457.0
SEED = 20261119
MODELS = ("bb", "exact", "kde1", "kde2")


def shape(decay):
    c = [0.5 * (EDGES[i] + EDGES[i + 1]) for i in range(35)]
    w = [math.exp(-(ci - 15.0) / decay) for ci in c]
    tot = sum(w)
    return [N_BKG * wi / tot for wi in w]


def smooth(m, h):
    """Spread each bin's counts with a Gaussian kernel of width h (GeV), renormalised per source
    bin inside 15-50 GeV, so the total is preserved."""
    c = [0.5 * (EDGES[i] + EDGES[i + 1]) for i in range(len(m))]
    out = [0.0] * len(m)
    for i, mi in enumerate(m):
        if mi == 0:
            continue
        k = [math.exp(-0.5 * ((cj - c[i]) / h) ** 2) for cj in c]
        tk = sum(k)
        for j in range(len(m)):
            out[j] += mi * k[j] / tk
    return out


_S = None


def one_toy(args):
    idx, decay = args
    import numpy as np
    rng = np.random.default_rng(SEED + 100000 * int(decay) + idx)
    v = shape(decay)
    n = [int(x) for x in rng.poisson(v)]
    m = [int(x) for x in rng.poisson([vi / ef.R0_ALEPH for vi in v])]
    s = [ef.N_ALEPH * p for p in _S]
    row = {"idx": idx, "decay": decay}
    row["bb"] = ef.discovery(n, m, s, "bb")["Z0"]
    row["exact"] = ef.discovery(n, floor(m), s, "exact")["Z0"]
    row["kde1"] = ef.discovery(n, floor(smooth(m, 1.0)), s, "exact")["Z0"]
    row["kde2"] = ef.discovery(n, floor(smooth(m, 2.0)), s, "exact")["Z0"]
    return row


def floor(t, lo=0.5):
    """A template treated as exact needs t > 0 wherever mu mu counts can appear: every bin is
    floored at 0.5 raw counts (stated rule, same for exact, kde1 and kde2)."""
    return [max(x, lo) for x in t]


def _init():
    global _S
    _S = ef.voigt_bin_probs(EDGES)


def summarise(rows):
    out = {}
    for decay in sorted(set(r["decay"] for r in rows)):
        sub = [r for r in rows if r["decay"] == decay]
        d = {}
        for mdl in MODELS:
            z = [r[mdl] for r in sub if r[mdl] is not None]
            d[mdl] = {"n": len(z), "n_ge2": sum(1 for x in z if x >= 2.0),
                      "n_ge3": sum(1 for x in z if x >= 3.0),
                      "p_ge2": sum(1 for x in z if x >= 2.0) / len(z) if z else None,
                      "p_ge3": sum(1 for x in z if x >= 3.0) / len(z) if z else None,
                      "mean_Z": sum(z) / len(z) if z else None}
        out[str(decay)] = d
    return out


def grade(summary):
    """C1: P(Z_bb >= 2) in [0.009, 0.037] for both shapes. C2: P(Z_exact >= 2) >= 0.035 for both
    shapes. C3 (information): kde2 rate below exact rate."""
    g = {}
    g["C1"] = "PASS" if all(0.009 <= summary[k]["bb"]["p_ge2"] <= 0.037 for k in summary) else "FAIL"
    g["C2"] = "PASS" if all((summary[k]["exact"]["p_ge2"] or 0) >= 0.035 for k in summary) else "FAIL"
    g["C3_info"] = "kde2 < exact" if all(
        summary[k]["kde2"]["p_ge2"] < (summary[k]["exact"]["p_ge2"] or 1) for k in summary) else "not"
    return g


def timing_demo():
    """C5: emuframe.delphi_aprime on a made-up 700-bin spectrum with no signal."""
    import numpy as np
    rng = np.random.default_rng(SEED)
    edges = [15.0 + 0.05 * i for i in range(701)]
    c = [0.5 * (edges[i] + edges[i + 1]) for i in range(700)]
    v = [3000.0 * 0.05 / 6.0 * math.exp(-(ci - 15.0) / 6.0) for ci in c]
    n = [int(x) for x in rng.poisson(v)]
    m = [int(x) for x in rng.poisson([vi * 1.88 for vi in v])]
    t0 = time.time()
    res = ef.delphi_aprime(edges, n, m, 21.7)
    res["seconds"] = time.time() - t0
    res["n_sum"], res["m_sum"] = sum(n), sum(m)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out")
    ap.add_argument("--ntoys", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    tasks = [(i, d) for d in (4, 8) for i in range(a.ntoys)]
    rows = []
    with Pool(a.workers, initializer=_init) as pool:
        for k, row in enumerate(pool.imap_unordered(one_toy, tasks, chunksize=10)):
            rows.append(row)
            if (k + 1) % 200 == 0:
                print("toys done", k + 1, "of", len(tasks), round(time.time() - t0), "s", flush=True)
    rows.sort(key=lambda r: (r["decay"], r["idx"]))
    with open(os.path.join(a.out, "toys.csv"), "w") as f:
        f.write("decay,idx," + ",".join(MODELS) + "\n")
        for r in rows:
            f.write("%d,%d,%s\n" % (r["decay"], r["idx"], ",".join(
                "" if r[mm] is None else "%.5f" % r[mm] for mm in MODELS)))
    summary = summarise(rows)
    grades = grade(summary)
    demo = timing_demo()
    res = {"version": VERSION, "emuframe": ef.VERSION, "seed": SEED, "ntoys_per_shape": a.ntoys,
           "n_bkg": N_BKG, "r0": ef.R0_ALEPH, "summary": summary, "grades": grades,
           "delphi_timing_demo": demo, "seconds": time.time() - t0}
    with open(os.path.join(a.out, "toys.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    parts = []
    for k in summary:
        parts.append("decay%s " % k + " ".join(
            "%s:%s/%s,%s" % (mm, summary[k][mm]["n_ge2"], summary[k][mm]["n"], summary[k][mm]["n_ge3"])
            for mm in MODELS))
    print("APTOYS: %s | C1 %s C2 %s C3 %s | delphi demo %s Z0=%.2f UL=%.2f %.0fs" % (
        " | ".join(parts), grades["C1"], grades["C2"], grades["C3_info"], demo["label"],
        demo["nominal"]["Z0"], demo["nominal"]["UL95"], demo["seconds"]))


if __name__ == "__main__":
    main()
