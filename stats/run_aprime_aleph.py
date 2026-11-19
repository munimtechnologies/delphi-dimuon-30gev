# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""run_aprime_aleph: A'-ALEPH (PLAN amendment 0.19 sec. 3; amendment 0.20).

1. Fetches stats/emuframe.py from the public repository (main) and checks its git blob sha
   against the published 0.1.0 (d55c900f...), unless --emuframe points to a local copy.
2. Runs emuframe.aleph_aprime on the blind reading aleph-fig5.json and writes
   OUT/aleph_aprime.json at once (graded P1-P4), plus a profile-likelihood scan in mu.
3. Amendment 0.20 toys: background-only pseudo-experiments drawn from the reading's OWN mu = 0 fit
   (model "bb": n_i ~ Pois(r t_i), m_i ~ Pois(t_i)); each fitted with "bb" and "exact" at ALEPH's
   fixed mass and shape. Toy p-value = (1 + #{Z0_toy >= Z0_obs}) / (N + 1). Partial results are
   written every 1000 toys.

    python run_aprime_aleph.py --data aleph-fig5.json --out /out --ntoys 10000 --workers 4
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
import time
import urllib.request
from multiprocessing import Pool

VERSION = "mv2 run_aprime_aleph 0.1.0"
EMUFRAME_URL = ("https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/"
                "main/stats/emuframe.py")
EMUFRAME_BLOB = "d55c900fdb45aa9f8a6099a142079a510c3afdfa"   # stats/emuframe.py 0.1.0 on main
SEED = 20261120

ef = None


def git_blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_emuframe(path, out_dir):
    global ef
    if path is None:
        data = urllib.request.urlopen(EMUFRAME_URL, timeout=60).read()
        path = os.path.join(out_dir, "emuframe.py")
        with open(path, "wb") as f:
            f.write(data)
    else:
        data = open(path, "rb").read()
    sha = git_blob_sha(data)
    if sha != EMUFRAME_BLOB:
        raise SystemExit("emuframe.py blob %s != published %s" % (sha, EMUFRAME_BLOB))
    spec = importlib.util.spec_from_file_location("emuframe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ef = mod
    return path, sha


def poisson(rng, lam):
    """Exact Poisson draw by inversion (lam <= ~500 is safe in double precision)."""
    if lam <= 0.0:
        return 0
    u = rng.random()
    k, p = 0, math.exp(-lam)
    c = p
    while u > c:
        k += 1
        p *= lam / k
        c += p
        if k > 10000:
            break
    return k


def z0_only(n, m, s, model):
    best = ef.fit(n, m, s, model)
    l0 = ef.profile_r(n, m, s, 0.0, model)[1]
    q0 = max(0.0, 2.0 * (best["lnL"] - l0))
    return math.sqrt(q0), best["mu"]


_TOY = None


def _init(emu_path, toy):
    global _TOY, ef
    spec = importlib.util.spec_from_file_location("emuframe", emu_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ef = mod
    _TOY = toy


def one_toy(i):
    rng = random.Random(SEED * 100003 + i)
    r, t, s = _TOY["r"], _TOY["t"], _TOY["s"]
    n = [poisson(rng, r * ti) for ti in t]
    m = [poisson(rng, ti) for ti in t]
    out = {"i": i}
    for model in ("bb", "exact"):
        if model == "exact":
            # the exact model is undefined when a bin has n > 0 and m = 0; floor at 0.5 counts,
            # as in aprime_toys (amendment 0.19 sec. 4)
            mm = [max(mi, 0.5) for mi in m]
        else:
            mm = m
        z, mu = z0_only(n, mm, s, model)
        out[model] = [z, mu]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ntoys", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--emuframe", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    emu_path, sha = load_emuframe(a.emuframe, a.out)
    print("emuframe", ef.VERSION, "blob", sha, flush=True)

    d = json.load(open(a.data))
    edges, n, v = d["edges"], d["n"], d["v_scaled"]
    assert len(edges) == len(n) + 1 == len(v) + 1, "bin count mismatch"
    print("reading: sum n = %d, sum v = %.1f, sum(n - v) 29-32 = %.2f" % (
        sum(n), sum(v), sum(n[i] - v[i] for i in range(len(n)) if 29 <= edges[i] < 32)), flush=True)

    res = ef.aleph_aprime(edges, n, v)
    res["runner"] = VERSION
    res["emuframe_blob"] = sha
    with open(os.path.join(a.out, "aleph_aprime.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1), flush=True)

    # transparency: profile likelihood in mu (trap: flat minimum), both models
    s = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    m_raw = [vi / ef.R0_ALEPH for vi in v]
    scan = {}
    for model in ("bb", "exact"):
        l_best = ef.fit(n, m_raw, s, model)["lnL"]
        rows = []
        for k in range(0, 13):
            mu = 0.25 * k
            r, l = ef.profile_r(n, m_raw, s, mu, model)
            rows.append([mu, r, 2.0 * (l_best - l)])
        scan[model] = rows
        print("SCAN", model, " ".join("%.2f:%.2f" % (x[0], x[2]) for x in rows), flush=True)
    with open(os.path.join(a.out, "scan.json"), "w") as f:
        json.dump(scan, f, indent=1)
    zb, ze = res["bb"]["Z0"], res["exact"]["Z0"]
    rv = res["bb_r0_variants"]
    print("APALEPH: Z0_bb=%.3f Z0_exact=%.3f ratio=%s mu_hat_bb=%.3f mu_hat_exact=%.3f "
          "r_hat_bb=%.4f Z0_bb(r0=0.45)=%.3f Z0_bb(r0=0.60)=%.3f n_on=%d bkg=%.2f "
          "Z_Bi_tau1=%.3f Z_Bi_tau1/r0=%.3f" % (
              zb, ze, ("%.3f" % res["ratio_bb_exact"]) if res["ratio_bb_exact"] else "None",
              res["bb"]["mu_hat"], res["exact"]["mu_hat"], res["bb"]["r_hat"],
              rv["0.45"], rv["0.6"], res["window"]["n_on"], res["window"]["bkg_scaled"],
              res["window"]["Z_Bi_tau1"], res["window"]["Z_Bi_tau_1_over_r0"]), flush=True)

    # amendment 0.20 toys, generated from the reading's own background-only bb fit
    b0 = ef.fit(n, m_raw, s, "bb", mu_fixed=0.0)
    r0hat = b0["r"]
    t = [ef.t_hat(ni, mi, si, r0hat, 0.0) for ni, mi, si in zip(n, m_raw, s)]
    toy = {"r": r0hat, "t": t, "s": s}
    with open(os.path.join(a.out, "toy_truth.json"), "w") as f:
        json.dump(toy, f, indent=1)
    print("toy truth: r = %.4f, sum r t = %.1f, sum t = %.1f" % (r0hat, r0hat * sum(t), sum(t)),
          flush=True)
    results = []

    def write_partial(final=False):
        out = {"version": VERSION, "seed": SEED, "n_done": len(results), "final": final,
               "obs": {"bb": zb, "exact": ze}}
        for model in ("bb", "exact"):
            zs = [x[model][0] for x in results]
            nn = len(zs)
            if nn == 0:
                continue
            k = sum(1 for z in zs if z >= res[model]["Z0"] - 1e-12)
            p = (1.0 + k) / (nn + 1.0)
            out[model] = {"n_ge_obs": k, "p_toy": p, "Z_toy": ef.z_from_p(p),
                          "p_asym": 1.0 - ef.phi(res[model]["Z0"]),
                          "rate_Z_ge_2": sum(1 for z in zs if z >= 2.0) / nn,
                          "rate_Z_ge_3": sum(1 for z in zs if z >= 3.0) / nn,
                          "mean_mu_hat": sum(x[model][1] for x in results) / nn}
        out["elapsed_s"] = time.time() - t0
        with open(os.path.join(a.out, "toys.json"), "w") as f:
            json.dump(out, f, indent=1)
        return out

    with Pool(a.workers, initializer=_init, initargs=(emu_path, toy)) as pool:
        for x in pool.imap_unordered(one_toy, range(a.ntoys), chunksize=20):
            results.append(x)
            if len(results) % 1000 == 0:
                o = write_partial()
                print("toys %d: %s" % (len(results), json.dumps({k: o.get(k) for k in ("bb", "exact")})),
                      flush=True)
    with open(os.path.join(a.out, "toys_raw.json"), "w") as f:
        json.dump(sorted(results, key=lambda x: x["i"]), f)
    o = write_partial(final=True)
    print("APTOY: N=%d bb: k=%d p_toy=%.5f Z_toy=%.3f (asym %.3f) rate2=%.4f rate3=%.4f | "
          "exact: k=%d p_toy=%.5f Z_toy=%.3f (asym %.3f) rate2=%.4f rate3=%.4f | %.0f s" % (
              o["n_done"], o["bb"]["n_ge_obs"], o["bb"]["p_toy"], o["bb"]["Z_toy"], zb,
              o["bb"]["rate_Z_ge_2"], o["bb"]["rate_Z_ge_3"],
              o["exact"]["n_ge_obs"], o["exact"]["p_toy"], o["exact"]["Z_toy"], ze,
              o["exact"]["rate_Z_ge_2"], o["exact"]["rate_Z_ge_3"], o["elapsed_s"]), flush=True)


if __name__ == "__main__":
    main()
