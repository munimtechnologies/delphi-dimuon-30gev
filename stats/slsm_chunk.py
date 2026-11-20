# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""slsm_chunk 0.1.0: runs aprime_slsm 0.1.0's pre-registered test (PLAN amendment 0.27 sec. 6,
L0-L5) UNCHANGED, but saves the toys while they finish and stops at a time budget, so a timeout
can no longer lose them (PLAN amendment 0.29).

Job aprime-slsm-v1 ran 4,000 of its 10,000 toys in 6 h and was killed by the job timeout
before it wrote a single toy (aprime_slsm.run only writes them at the end). This wrapper:
* imports aprime_slsm 0.1.0 (and through it aprime_smooth 0.1.0) unchanged: same likelihood,
  same observed fits (aprime_slsm.observe), same toy generator (aprime_slsm.one_toy, seed
  20261121 + idx, so toy idx k is the same pseudo-experiment it was in v1), same grades
  (aprime_slsm.grade);
* asks for the pre-registered 10,000 toys, and stops submitting at --budget-s;
* grades on the CONTIGUOUS PREFIX of finished toys (idx 0..K-1 all finished), so the graded
  set does not depend on which toys happen to be fast;
* needs at least MIN_TOYS toys in the prefix to grade L1, L2, L4, L5; otherwise they are
  NOT GRADABLE. L0 and L3 use the observed fit only.

    python slsm_chunk.py --fig5 aleph-fig5.json --emuframe /work/emuframe.py --out /out \
        --ntoys 10000 --workers 4 --budget-s 17400

Last output line `APSLSM:` (aprime_slsm.line), preceded by `SLSMCHUNK:`.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import aprime_slsm as sl
except ImportError:          # pragma: no cover - only when the sibling module is absent
    sl = None

VERSION = "mv2 slsm_chunk 0.1.0"
MIN_TOYS = 1000
TOY_KEYS = ("slope", "const")


def prefix(rows):
    """Rows whose idx form the longest run 0..K-1 with every toy finished, sorted by idx."""
    by = {r["idx"]: r for r in rows}
    out = []
    k = 0
    while k in by:
        out.append(by[k])
        k += 1
    return out


def summarise(obs, rows, min_toys=MIN_TOYS):
    """Rates, calibration, goodness of fit and grades exactly as aprime_slsm.run computes them,
    on the given rows; toy-based grades are NOT GRADABLE below min_toys."""
    res = {"ntoys": len(rows)}
    if rows:
        rates, cal = {}, {}
        for k, zo in (("slope", obs["slope"]["Z0"]), ("const", obs["const"]["Z0"])):
            z = [r[k] for r in rows]
            rates[k] = {"p_ge2": sum(1 for x in z if x >= 2.0) / len(z),
                        "p_ge3": sum(1 for x in z if x >= 3.0) / len(z),
                        "mean_Z": sum(z) / len(z)}
            cal[k] = dict(sl.z_from_count(sum(1 for x in z if x >= zo - 1e-9), len(z)), Z_asym=zo)
        gof_k = sum(1 for r in rows if r["dev0"] >= obs["dev0"])
        res.update({"rates": rates, "calibrated": cal,
                    "gof": {"dev_obs": obs["dev0"], "k": gof_k, "p": gof_k / len(rows)},
                    "mean_mu_toys": sum(r["mu"] for r in rows) / len(rows),
                    "mean_b0_toys": sum(r["b0"] for r in rows) / len(rows)})
        g = sl.grade(obs, cal, rates, res["gof"]["p"])
    else:
        dummy_cal = {"slope": {"Z": 0.0, "lower_bound": False}}
        g = sl.grade(obs, dummy_cal, {"slope": {"p_ge2": 0.0}}, 1.0)
    if len(rows) < min_toys and g.get("L0") == "PASS":
        for k in ("L1", "L2", "L4", "L5"):
            g[k] = "NOT GRADABLE (only %d toys in the finished prefix, fewer than %d)" % (
                len(rows), min_toys)
    res["grades"] = g
    return res


def write_toys(path, rows):
    with open(path, "w") as f:
        f.write("idx,slope,const,dev0,mu,b0\n")
        for r in rows:
            f.write("%d,%.5f,%.5f,%.5f,%.5f,%.5f\n" % (r["idx"], r["slope"], r["const"],
                                                        r["dev0"], r["mu"], r["b0"]))


def run(fig5, out_dir, ntoys, workers, emu_path, budget_s, save_every=250):
    from multiprocessing import Pool
    asm = sl.asm
    ef = asm.ef
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    edges, n, v = fig5["edges"], fig5["n"], fig5["v_scaled"]
    m = [vi / ef.R0_ALEPH for vi in v]
    s = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    sf = sl.SlopeFit(edges, s)
    res = {"version": sl.VERSION, "wrapper": VERSION, "aprime_smooth": asm.VERSION,
           "emuframe": ef.VERSION, "seed": sl.SEED, "pivot": sl.PIVOT, "deg": sl.DEG,
           "b_bounds": list(sl.B_BOUNDS), "ntoys_requested": ntoys, "budget_s": budget_s,
           "min_toys": MIN_TOYS}
    path = os.path.join(out_dir, "aprime_slsm.json")
    toys_path = os.path.join(out_dir, "toys.csv")

    def save():
        res["elapsed_s"] = time.time() - t0
        with open(path, "w") as f:
            json.dump(res, f, indent=1)

    obs, ds = sl.observe(sf, n, m)
    res["observed"] = obs
    print("CLOSURE par3 ParFit %.4f, SlopeFit b=0 %.4f (want %.4f)" % (
        obs["closure_parfit"], obs["closure_b0"], sl.PAR3_OBS), flush=True)
    print("OBS const Z0=%.4f | slope Z0=%.4f mu=%.3f b=%.4f | b(mu=0)=%.4f Z=%.3f | "
          "sig-floated b=%.4f Z=%.3f" % (
              obs["const"]["Z0"], obs["slope"]["Z0"], obs["slope"]["mu_hat"],
              obs["slope"]["b_hat"], obs["slope_mu0"]["b_hat"], obs["slope_mu0"]["Z"],
              obs["slope_signal_floated"]["b_hat"], obs["slope_signal_floated"]["Z"]), flush=True)
    T, lam_n = sf.lam(ds["fit0"])
    T, lam_n = [float(x) for x in T], [float(x) for x in lam_n]
    obs["truth"] = {"a": ds["fit0"]["a"], "r": ds["fit0"]["r"], "b": ds["fit0"]["b"],
                    "sum_T": sum(T), "sum_lam_n": sum(lam_n),
                    "window_29_32": {"bkg": sum(lam_n[14:17]), "n": sum(n[14:17])}}
    obs["dev0"] = sf.deviance(n, m, ds["fit0"])
    save()

    rows = []
    stopped = "all toys finished"
    pool = Pool(workers, initializer=sl._init, initargs=(emu_path, edges, s, T, lam_n))
    try:
        for row in pool.imap_unordered(sl.one_toy, range(ntoys), chunksize=4):
            rows.append(row)
            if len(rows) % save_every == 0:
                pre = prefix(rows)
                write_toys(toys_path, pre)
                res.update(summarise(obs, pre))
                res["finished_any_order"] = len(rows)
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
    res.update(summarise(obs, pre))
    res["finished_any_order"] = len(rows)
    res["stopped"] = stopped
    save()
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--emuframe", required=True)
    ap.add_argument("--ntoys", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-s", type=float, default=17400.0)
    a = ap.parse_args(argv)
    if sl is None or sl.asm is None:
        raise SystemExit("aprime_slsm.py and aprime_smooth.py must sit next to this file")
    asm = sl.asm
    print("emuframe blob", asm.fetch_emuframe(a.emuframe), flush=True)
    asm.bind(path=a.emuframe)
    fig5 = json.load(open(a.fig5))
    print("%s around %s with %s and %s; sum n %d, sum v %.1f" % (
        VERSION, sl.VERSION, asm.VERSION, asm.ef.VERSION, sum(fig5["n"]),
        sum(fig5["v_scaled"])), flush=True)
    res = run(fig5, a.out, a.ntoys, a.workers, os.path.abspath(a.emuframe), a.budget_s)
    keys = [k for k in ("ntoys", "finished_any_order", "stopped", "rates", "calibrated", "gof",
                        "mean_mu_toys", "mean_b0_toys", "grades") if k in res]
    print(json.dumps({k: res[k] for k in keys}, indent=1), flush=True)
    print("SLSMCHUNK: prefix toys %d, finished %d, %s" % (
        res["ntoys"], res["finished_any_order"], res["stopped"]), flush=True)
    if res["ntoys"] > 0:
        print(sl.line(res), flush=True)
    else:
        print("APSLSM: no toys finished; grades %s" % res["grades"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
