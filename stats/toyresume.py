# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""toyresume 0.1.0: continue a stopped toy calibration from its saved contiguous prefix
(PLAN amendment 0.32).

Jobs aprime-slsm-v2 (slsm_chunk 0.1.0, amendment 0.29) and ssframe-v1 (ssframe 0.1.0, amendment
0.30) stopped at their time budgets with 869 and 309 toys in their contiguous prefixes, fewer
than the 1,000 their grades need. Every toy is a fixed pseudo-experiment (seed + idx), so the
calibration can be continued instead of restarted. This module:

* imports the original modules UNCHANGED (aprime_slsm 0.1.0 + slsm_chunk 0.1.0, or ssframe
  0.1.0) and recomputes the observed fits and the toy truth exactly as their drivers do;
* reads the saved prior toys (toys.csv of the stopped job; must be idx 0..K-1, contiguous);
* RECHECK: re-runs toys 0..R-1 and requires every saved column to agree within 2e-5 (the CSV
  keeps 5 decimals). A mismatch stops the job: no grade from mixed toys;
* runs toys K, K+1, ... IN ORDER (pool.imap, ordered) until the requested total or the time
  budget, saving the merged prefix as it goes, so the merged set is always contiguous 0..N-1;
* grades the merged prefix with the original grading code (slsm_chunk.summarise /
  aprime_slsm.line, or ssframe.grade / ssframe.line), MIN_TOYS 1,000 unchanged.

Saved prior values carry 5 decimals; a prior toy within 1e-5 of an observed Z0 could in principle
compare differently than at full precision (reported as `near_ties`).

    python toyresume.py --kind slsm --prior prior-slsm.csv --fig5 aleph-fig5.json \
        --emuframe /work/emuframe.py --out /out --ntoys 10000 --workers 4 --budget-s 20000
    python toyresume.py --kind ssframe --prior prior-ssframe.csv --fig5 aleph-fig5.json \
        --dmc aleph-dmc21.json --emu aleph-emu3.json --emuframe /work/emuframe.py --out /out \
        --ntoys 6000 --workers 4 --budget-s 20000

Last output line `TOYRESUME:`, preceded by the original module's own summary line.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import aprime_slsm as sl
except ImportError:          # pure helpers below stay testable without numpy / scipy
    sl = None
try:
    import slsm_chunk as sc
except ImportError:
    sc = None
try:
    import ssframe as sf
except ImportError:
    sf = None

VERSION = "mv2 toyresume 0.1.0"
COLS = {"slsm": ("idx", "slope", "const", "dev0", "mu", "b0"),
        "ssframe": ("idx", "Z0", "mu", "b0", "b_aux", "dev0")}
ZKEYS = {"slsm": ("slope", "const"), "ssframe": ("Z0",)}
TOL = 2e-5
RECHECK = 8


# ----------------------------------------------------------------------------- pure helpers
def parse_csv(text, kind):
    """Rows of a saved toys.csv as dicts (idx int, the rest float); header must match."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    head = tuple(lines[0].split(","))
    if head != COLS[kind]:
        raise ValueError("header %s is not %s" % (head, COLS[kind]))
    rows = []
    for l in lines[1:]:
        v = l.split(",")
        if len(v) != len(head):
            raise ValueError("bad row %r" % l)
        r = {"idx": int(v[0])}
        r.update({k: float(x) for k, x in zip(head[1:], v[1:])})
        rows.append(r)
    return rows


def contiguous(rows):
    """True when rows are exactly idx 0..K-1 in order."""
    return all(r["idx"] == i for i, r in enumerate(rows))


def format_rows(rows, kind):
    cols = COLS[kind]
    out = [",".join(cols)]
    for r in rows:
        out.append("%d," % r["idx"] + ",".join("%.5f" % r[k] for k in cols[1:]))
    return "\n".join(out) + "\n"


def compare(saved, fresh, kind, tol=TOL):
    """List of (idx, column, saved, fresh) that differ by more than tol after 5-decimal rounding."""
    bad = []
    for a, b in zip(saved, fresh):
        if a["idx"] != b["idx"]:
            bad.append((a["idx"], "idx", a["idx"], b["idx"]))
            continue
        for k in COLS[kind][1:]:
            if abs(round(float(b[k]), 5) - float(a[k])) > tol:
                bad.append((a["idx"], k, a[k], b[k]))
    return bad


def near_ties(rows, kind, observed, eps=1e-5):
    """Saved toys whose Z lies within eps of an observed Z0 (rounding could flip them)."""
    out = {}
    for k in ZKEYS[kind]:
        zo = observed.get(k)
        if zo is None:
            continue
        out[k] = sum(1 for r in rows if abs(r[k] - zo) <= eps)
    return out


# ----------------------------------------------------------------------------- set-ups
def setup_slsm(fig5, emu_path):
    """Observed fits and toy truth exactly as slsm_chunk 0.1.0's run() computes them."""
    asm = sl.asm
    ef = asm.ef
    edges, n, v = fig5["edges"], fig5["n"], fig5["v_scaled"]
    m = [vi / ef.R0_ALEPH for vi in v]
    s = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    fit = sl.SlopeFit(edges, s)
    obs, ds = sl.observe(fit, n, m)
    T, lam_n = fit.lam(ds["fit0"])
    T, lam_n = [float(x) for x in T], [float(x) for x in lam_n]
    obs["truth"] = {"a": ds["fit0"]["a"], "r": ds["fit0"]["r"], "b": ds["fit0"]["b"],
                    "sum_T": sum(T), "sum_lam_n": sum(lam_n),
                    "window_29_32": {"bkg": sum(lam_n[14:17]), "n": sum(n[14:17])}}
    obs["dev0"] = fit.deviance(n, m, ds["fit0"])
    print("OBS slsm: closure parfit %.4f b0 %.4f | const Z0 %.4f | slope Z0 %.4f mu %.3f b %.4f "
          "| dev0 %.4f | sum_T %.4f sum_lam_n %.4f" % (
              obs["closure_parfit"], obs["closure_b0"], obs["const"]["Z0"], obs["slope"]["Z0"],
              obs["slope"]["mu_hat"], obs["slope"]["b_hat"], obs["dev0"], sum(T), sum(lam_n)),
          flush=True)
    return obs, sl._init, (emu_path, edges, s, T, lam_n), sl.one_toy


def setup_ssframe(fig5, dmc, emu, emu_path):
    obs, truth, (edges, s) = sf.observe(fig5, dmc, emu)
    if truth is None or sf.gate(obs)[0] != "PASS":
        return obs, None, None, None
    T, lam_n, b_truth, sigc = truth
    return obs, sf._init, (emu_path, edges, s, T, lam_n, b_truth, sigc), sf.one_toy


def grade_rows(kind, obs, rows):
    if kind == "slsm":
        res = {"observed": obs}
        res.update(sc.summarise(obs, rows))
        return res
    g, st = sf.grade(obs, rows)
    return {"observed": obs, "grades": g, "stats": st, "ntoys": len(rows)}


def summary_line(kind, res):
    if kind == "slsm":
        return sl.line(res) if res.get("ntoys") else "APSLSM: no toys"
    return sf.line(res)


# ----------------------------------------------------------------------------- driver
def run(kind, prior_rows, obs, init, initargs, one_toy, out_dir, ntoys, workers, budget_s,
        recheck=RECHECK, save_every=100):
    from multiprocessing import Pool
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    jpath = os.path.join(out_dir, "toyresume.json")
    tpath = os.path.join(out_dir, "toys.csv")
    res = {"version": VERSION, "kind": kind, "prior_toys": len(prior_rows),
           "ntoys_requested": ntoys, "budget_s": budget_s, "recheck": recheck}

    def save(rows):
        with open(tpath, "w") as f:
            f.write(format_rows(rows, kind))
        res.update(grade_rows(kind, obs, rows))
        res["merged_toys"] = len(rows)
        res["elapsed_s"] = time.time() - t0
        with open(jpath, "w") as f:
            json.dump(res, f, indent=1, default=str)

    k0 = len(prior_rows)
    pool = Pool(workers, initializer=init, initargs=initargs)
    stopped = "all toys finished"
    rows = list(prior_rows)
    try:
        r = min(recheck, k0)
        fresh = list(pool.imap(one_toy, range(r), chunksize=1))
        bad = compare(prior_rows[:r], fresh, kind)
        res["recheck_result"] = {"n": r, "mismatches": [list(b) for b in bad]}
        print("RECHECK %s: %d saved toys re-run, %d mismatches (%.0f s)" % (
            "PASS" if not bad else "FAIL", r, len(bad), time.time() - t0), flush=True)
        if bad:
            for b in bad[:10]:
                print("  mismatch idx %s %s saved %s fresh %s" % b, flush=True)
            res["stopped"] = "recheck failed: saved toys are not reproduced"
            res["grades_valid"] = False
            with open(jpath, "w") as f:
                json.dump(res, f, indent=1, default=str)
            return res
        res["grades_valid"] = True
        for row in pool.imap(one_toy, range(k0, ntoys), chunksize=2):
            rows.append(row)
            if (len(rows) - k0) % save_every == 0:
                save(rows)
                print("toys merged %d (new %d), %d s" % (len(rows), len(rows) - k0,
                                                          round(time.time() - t0)), flush=True)
            if time.time() - t0 > budget_s:
                stopped = "time budget %d s reached" % budget_s
                break
    finally:
        pool.terminate()
        pool.join()
    if not contiguous(rows):
        raise SystemExit("merged toys are not contiguous; this should not happen")
    res["stopped"] = stopped
    zo = {k: (obs[k]["Z0"] if kind == "slsm" else None) for k in ZKEYS[kind]}
    if kind == "ssframe":
        zo = {"Z0": (obs.get("constrained") or {}).get("Z0")}
    res["near_ties"] = near_ties(prior_rows, kind, zo)
    save(rows)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kind", choices=("slsm", "ssframe"), required=True)
    ap.add_argument("--prior", required=True)
    ap.add_argument("--fig5", required=True)
    ap.add_argument("--dmc")
    ap.add_argument("--emu")
    ap.add_argument("--emuframe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ntoys", type=int, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget-s", type=float, default=20000.0)
    a = ap.parse_args(argv)
    print("python %s, %s" % (sys.version.split()[0], VERSION), flush=True)
    if sl is None or sl.asm is None:
        raise SystemExit("aprime_slsm.py and aprime_smooth.py must sit next to this file")
    if a.kind == "slsm" and sc is None:
        raise SystemExit("slsm_chunk.py must sit next to this file")
    if a.kind == "ssframe" and (sf is None or sf.ssc is None):
        raise SystemExit("ssframe.py, sscontrol.py, dmcratio.py, aprime_cross.py needed")
    print("emuframe blob", sl.asm.fetch_emuframe(a.emuframe), flush=True)
    sl.asm.bind(path=a.emuframe)
    emu_path = os.path.abspath(a.emuframe)
    load = lambda p: json.load(open(p))
    prior = parse_csv(open(a.prior).read(), a.kind)
    if not contiguous(prior):
        raise SystemExit("prior toys are not idx 0..K-1")
    print("PRIOR %s: %d toys, idx 0..%d" % (a.kind, len(prior), len(prior) - 1), flush=True)
    fig5 = load(a.fig5)
    if a.kind == "slsm":
        obs, init, initargs, one = setup_slsm(fig5, emu_path)
    else:
        obs, init, initargs, one = setup_ssframe(fig5, load(a.dmc), load(a.emu), emu_path)
        if init is None:
            print("TOYRESUME: ssframe gate P0 failed, no toys run", flush=True)
            return 1
    res = run(a.kind, prior, obs, init, initargs, one, a.out, a.ntoys, a.workers, a.budget_s)
    keys = [k for k in ("prior_toys", "merged_toys", "stopped", "recheck_result", "near_ties",
                        "rates", "calibrated", "gof", "stats", "grades") if k in res]
    print(json.dumps({k: res[k] for k in keys}, indent=1, default=str), flush=True)
    if res.get("grades_valid"):
        print(summary_line(a.kind, res), flush=True)
    g = res.get("grades") or {}
    print("TOYRESUME: %s prior %d merged %s | recheck %s | %s | %s" % (
        a.kind, res["prior_toys"], res.get("merged_toys"),
        "PASS" if res.get("grades_valid") else "FAIL", res.get("stopped"),
        " ".join("%s %s" % (k, str(v).split(" ")[0]) for k, v in sorted(g.items()))),
        flush=True)
    return 0 if res.get("grades_valid") else 2


if __name__ == "__main__":
    sys.exit(main())
