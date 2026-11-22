# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""leefast: the look-elsewhere scan of leescan 0.1.0 (PLAN amendment 0.34) with a fast exact
minimiser (PLAN amendment 0.40).

Job leescan-v1 finished only 9 of its 2,000 background-only toys in 14,000 s: each toy needs
1,125 profile fits (125 masses x 3 widths x 3 starting values) and ParFit's L-BFGS-B, run with
ftol 1e-14 and gtol 1e-9, spends up to its 5,000-iteration cap on each of them. Resuming the same
code would take weeks of CPU.

leefast changes ONE thing: how the minimum of the SAME negative log-likelihood is found. It uses
Newton's method with the analytic gradient and Hessian of aprime_smooth.ParFit.nll_grad
(Levenberg damping when the Hessian is not positive definite, Armijo backtracking, the mu >= 0 and
mu <= MU_MAX bounds handled by an active set), from the same three starting values of mu. If a
Newton run fails numerically, that single fit falls back to ParFit's own L-BFGS-B. The likelihood,
data, signal shapes, mass and width grid, toy generator, seeds, statistics and grades are those of
leescan 0.1.0, which is downloaded at a pinned commit, checked by sha256 and used unchanged
(leescan.one_toy, grid_shapes, summarize, grade, line ...).

Gate V (amendment 0.40): the fast scanner must reproduce leescan-v1's L-BFGS-B numbers: all 375
observed Z(mass) values and the 3 Z values at 30.40 GeV (to 0.002), the 9 toys' maximum Z in
every variant (to 0.002), and the toy truth.

    python leefast.py --fetch-only
    python leefast.py --out /out --ntoys 2000 --workers 2 --budget-s 14000 [--prior-csv rows.csv]
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
import urllib.request

VERSION = "mv2 leefast 0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
LEESCAN_COMMIT = "dabf4b2fa8f7edfb7bb24166f2d18729e71a1b4b"
LEESCAN_URL = ("https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/"
               + LEESCAN_COMMIT + "/stats/leescan.py")
LEESCAN_SHA256 = "fec272cc336aac66880413592d98ab0bb807189d093d626aa618855f0e8b045f"
TOL_DEC = 1e-11          # stop when the Newton decrement -G.step is below this (nll units)
ARMIJO = 1e-4
MAXIT = 200
LNR_BOUNDS = (-10.0, 10.0)   # as ParFit._min
V1_TOL = 0.002               # = leescan.SCAN_TOL
V1_GRID_TOL = V1_TOL + 5e-7  # v1ref rounds the observed grid to 6 decimals
V1_TOY_TOL = V1_TOL + 5e-6   # v1 toys.csv has 5 decimals
TRUTH_RTOL = 1e-6


# ----------------------------------------------------------------------------- fetching
def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def fetch_leescan(here=HERE, tries=10, wait=30):
    dest = os.path.join(here, "leescan.py")
    if os.path.exists(dest):
        data = open(dest, "rb").read()
    else:
        data = None
        for k in range(tries):
            try:
                data = urllib.request.urlopen(LEESCAN_URL, timeout=60).read()
                break
            except Exception as exc:   # network hiccup: retry
                print("attempt %d for leescan.py failed: %s" % (k + 1, exc), flush=True)
                time.sleep(wait)
        if data is None:
            raise SystemExit("could not fetch leescan.py")
    h = sha256_bytes(data)
    if h != LEESCAN_SHA256:
        raise SystemExit("leescan.py sha256 %s != %s" % (h, LEESCAN_SHA256))
    with open(dest, "wb") as f:
        f.write(data)
    print("fetched stats/leescan.py @%s (%d bytes) sha256 %s (matches)" % (
        LEESCAN_COMMIT[:12], len(data), h), flush=True)
    return dest


def load_leescan(here=HERE):
    path = os.path.join(here, "leescan.py")
    mod = sys.modules.get("leescan")
    if mod is not None and os.path.abspath(getattr(mod, "__file__", "")) == os.path.abspath(path):
        return mod
    spec = importlib.util.spec_from_file_location("leescan", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["leescan"] = mod          # so worker processes (fork) and pickling find it
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------- linear algebra
def pd_solve(np, H, G):
    """Solve (H + damp I) x = -G with the smallest damp in {0, 1e-10 s, 1e-9 s, ...} that makes
    the matrix positive definite (s = max(1, max |diag H|)). None if impossible or not finite."""
    if not (np.all(np.isfinite(H)) and np.all(np.isfinite(G))):
        return None
    k = len(G)
    scale = max(1.0, float(np.max(np.abs(np.diag(H))))) if k else 1.0
    damp = 0.0
    eye = np.eye(k)
    for _ in range(40):
        try:
            Lc = np.linalg.cholesky(H + damp * eye)
        except np.linalg.LinAlgError:
            damp = 1e-10 * scale if damp == 0.0 else damp * 10.0
            continue
        y = np.linalg.solve(Lc, -G)
        x = np.linalg.solve(Lc.T, y)
        if np.all(np.isfinite(x)):
            return x
        return None
    return None


# ----------------------------------------------------------------------------- the scanner
class FastScanner:
    """Local Z = sqrt(q0) of the par3 frame for a list of signal shapes, as leescan.Scanner,
    with Newton fits of the same likelihood (ParFit.nll_grad) instead of L-BFGS-B."""

    def __init__(self, asm, edges, shapes, starts=(0.0, 0.8, 2.0)):
        import numpy as np
        self.np = np
        self.asm = asm
        self.pf = asm.ParFit(edges, shapes[0], 3)
        self.U = self.pf.U
        self.Ut = np.ascontiguousarray(self.pf.U.T)
        self.lnw = self.pf.lnw
        self.d = self.pf.deg + 1
        self.S = [np.array(s, dtype=float) for s in shapes]
        self.starts = tuple(starts)
        self.mu_max = float(asm.MU_MAX)
        self.n_newton = 0
        self.n_fallback = 0
        self.n_maxit = 0

    def fgh(self, p, n, m, s):
        """nll (as ParFit.nll_grad), its gradient and its Hessian in p = (a, ln r, mu)."""
        np = self.np
        d = self.d
        eta = np.clip(self.U @ p[:d] + self.lnw, -60.0, 60.0)
        T = np.exp(eta)
        B = math.exp(p[d]) * T
        lam = np.maximum(B + p[d + 1] * s, 1e-300)
        f = -(float(m @ eta) - float(T.sum()) + float(n @ np.log(lam)) - float(lam.sum()))
        q = n / lam
        g = q - 1.0                  # d ll / d lam
        h = q / lam                  # - d2 ll / d lam2
        gB = g * B
        hB = h * B
        wxx = gB - hB * B            # d2 ll_n / d eta2 (eta shared by a and ln r)
        waa = wxx - T                # plus the e mu term for a
        wxm = -hB * s                # d2 ll / d eta d mu
        G = np.empty(d + 2)
        G[:d] = -(self.Ut @ ((m - T) + gB))
        G[d] = -float(gB.sum())
        G[d + 1] = -float(g @ s)
        H = np.empty((d + 2, d + 2))
        H[:d, :d] = -((self.Ut * waa) @ self.U)
        c = -(self.Ut @ wxx)
        H[:d, d] = c
        H[d, :d] = c
        H[d, d] = -float(wxx.sum())
        c = -(self.Ut @ wxm)
        H[:d, d + 1] = c
        H[d + 1, :d] = c
        H[d, d + 1] = H[d + 1, d] = -float(wxm.sum())
        H[d + 1, d + 1] = float(h @ (s * s))
        return f, G, H

    def newton(self, p0, n, m, s, mu_lo, mu_hi, maxit=MAXIT):
        """Minimise the nll from p0 with mu in [mu_lo, mu_hi]. Returns (f, p) or None."""
        np = self.np
        d = self.d
        k = d + 1
        nv = d + 2
        self.n_newton += 1
        p = np.array(p0, dtype=float)
        p[k] = min(max(p[k], mu_lo), mu_hi)
        p[d] = min(max(p[d], LNR_BOUNDS[0]), LNR_BOUNDS[1])
        f, G, H = self.fgh(p, n, m, s)
        if not math.isfinite(f):
            return None
        for it in range(maxit):
            fix_mu = (mu_lo == mu_hi) or (p[k] <= mu_lo and G[k] > 0.0) or \
                     (p[k] >= mu_hi and G[k] < 0.0)
            moved = False
            converged = False
            for _attempt in (0, 1):
                free = np.ones(nv, dtype=bool)
                if fix_mu:
                    free[k] = False
                Gf = G[free]
                step = pd_solve(np, H[np.ix_(free, free)], Gf)
                if step is None:
                    return None
                dec = -float(Gf @ step)
                if dec <= TOL_DEC:
                    converged = True
                    break
                t = 1.0
                while t >= 1e-12:
                    pn = p.copy()
                    pn[free] += t * step
                    pn[k] = min(max(pn[k], mu_lo), mu_hi)
                    pn[d] = min(max(pn[d], LNR_BOUNDS[0]), LNR_BOUNDS[1])
                    fn, Gn, Hn = self.fgh(pn, n, m, s)
                    if math.isfinite(fn) and fn <= f - ARMIJO * t * dec:
                        moved = True
                        break
                    t *= 0.5
                if moved or fix_mu:
                    break
                fix_mu = True        # the projected step did not descend: hold mu and retry
            if converged or not moved:
                break
            p, f, G, H = pn, fn, Gn, Hn
        else:
            self.n_maxit += 1
        return f, p

    def _fallback(self, p0, n, m, s, mu_bounds):
        self.n_fallback += 1
        self.pf.s = s
        res = self.pf._min(p0, n, m, mu_bounds)
        return float(res.fun)

    def scan(self, n, m):
        np = self.np
        n = np.asarray(n, dtype=float)
        m = np.asarray(m, dtype=float)
        d = self.d
        a, lnr = self.pf.start(n, m)
        p0 = np.concatenate([np.asarray(a, dtype=float), [lnr, 0.0]])
        r0 = self.newton(p0, n, m, self.S[0], 0.0, 0.0)
        if r0 is None:
            self.n_fallback += 1
            self.pf.s = self.S[0]
            b0 = self.pf.fit(n, m, mu_fixed=0.0)
            f0 = -b0["lnL"]
            pb = np.concatenate([np.array(b0["a"]), [math.log(b0["r"]), 0.0]])
        else:
            f0, pb = r0
            pb = pb.copy()
            pb[d + 1] = 0.0
        out = []
        for s in self.S:
            best = f0
            for mu0 in self.starts:
                ps = pb.copy()
                ps[d + 1] = mu0
                r = self.newton(ps, n, m, s, 0.0, self.mu_max)
                fv = self._fallback(ps, n, m, s, (0.0, self.mu_max)) if r is None else r[0]
                if fv < best:
                    best = fv
            out.append(math.sqrt(max(0.0, 2.0 * (f0 - best))))
        return out, {"f0": f0}


# ----------------------------------------------------------------------------- gate V helpers
def grid_diffs(zgrid, ref_grid, masses):
    """[(abs diff, gamma, mass, fast, v1)] for every grid point, largest first."""
    out = []
    for g, ref in ref_grid.items():
        fast = zgrid[float(g)]
        for i, (zf, zr) in enumerate(zip(fast, ref)):
            out.append((abs(zf - zr), g, masses[i], zf, zr))
    out.sort(reverse=True)
    return out


def toy_diffs(rows_by_idx, ref_zmax, variants):
    """[(abs diff, idx, variant, fast, v1)] for the reference toys present, largest first."""
    out = []
    for idx, ref in ref_zmax.items():
        row = rows_by_idx.get(idx)
        if row is None:
            continue
        for v in variants:
            out.append((abs(row[v + "_zmax"] - ref[v]), idx, v, row[v + "_zmax"], ref[v]))
    out.sort(reverse=True)
    return out


def read_rows(path):
    """Toy rows from a toys.csv written by leescan/leefast (types restored)."""
    rows = []
    with open(path) as f:
        for rec in csv.DictReader(f):
            row = {}
            for key, val in rec.items():
                if key == "idx" or "_n" in key:
                    row[key] = int(round(float(val)))
                else:
                    row[key] = float(val)
            rows.append(row)
    return rows


# ----------------------------------------------------------------------------- workers
_W = {}


def _init(here, edges, flat_shapes, truth_T, truth_r):
    L = load_leescan(here)
    asm = L.load_asm(here)
    L._G["sc"] = FastScanner(asm, edges, flat_shapes)
    L._G["T"], L._G["r"] = truth_T, truth_r
    _W["L"] = L


def _toy(idx):
    L = _W["L"]
    sc = L._G["sc"]
    fb, mx, t = sc.n_fallback, sc.n_maxit, time.time()
    row = L.one_toy(idx)          # leescan 0.1.0's own toy generator (seed SEED + idx)
    row["_fallback"] = sc.n_fallback - fb
    row["_maxit"] = sc.n_maxit - mx
    row["_sec"] = time.time() - t
    return row


# ----------------------------------------------------------------------------- driver
def run(out_dir, ntoys, workers, budget_s, prior_csv=None, here=HERE):
    from multiprocessing import Pool
    import numpy as np
    sys.path.insert(0, here)
    import v1ref
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    L = load_leescan(here)
    asm = L.load_asm(here)
    ef = asm.ef
    fig5 = json.load(open(os.path.join(here, "aleph-fig5.json")))
    edges, n, v = fig5["edges"], fig5["n"], fig5["v_scaled"]
    m = [vi / ef.R0_ALEPH for vi in v]
    res = {"version": VERSION, "leescan": L.VERSION, "aprime_smooth": asm.VERSION,
           "emuframe": ef.VERSION, "seed": L.SEED, "masses": list(L.MASSES),
           "gammas": list(L.GAMMAS), "res": L.RES, "u0": L.U0}
    path = os.path.join(out_dir, "leescan.json")

    def save():
        res["elapsed_s"] = time.time() - t0
        with open(path, "w") as f:
            json.dump(res, f, indent=1)

    # gate: closure (as leescan-v1) with the fast scanner in place of leescan.Scanner
    s0 = [ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges)]
    pf0 = asm.ParFit(edges, s0, 3)
    d0 = pf0.discovery(n, m)
    z_fast0 = FastScanner(asm, edges, [s0]).scan(n, m)[0][0]
    gate = {"Z_par3_closure": d0["Z0"], "Z_scanner_default_shape": z_fast0,
            "closure_ok": abs(d0["Z0"] - L.Z_PAR3_OBS) <= L.CLOSURE_TOL,
            "scanner_ok": abs(z_fast0 - d0["Z0"]) <= L.SCAN_TOL}
    print("CLOSURE par3 Z0=%.4f (want %.3f) fast scanner=%.6f (discovery %.6f)" % (
        d0["Z0"], L.Z_PAR3_OBS, z_fast0, d0["Z0"]), flush=True)

    shapes = L.grid_shapes(ef, edges)
    flat = [s for g in L.GAMMAS for s in shapes[g]]
    obs_shapes = [[ef.N_ALEPH * p for p in ef.voigt_bin_probs(edges, m=L.M_OBS, gamma=g,
                                                               sigma=L.RES * L.M_OBS,
                                                               n_theta=L.NTHETA)]
                  for g in L.GAMMAS]
    print("shapes ready in %.0f s" % (time.time() - t0), flush=True)

    # observed scan + gate V1 (observed grid and Z at 30.40 against leescan-v1)
    t1 = time.time()
    sc = FastScanner(asm, edges, flat + obs_shapes)
    zs, _ = sc.scan(n, m)
    t_obs = time.time() - t1
    zgrid = L.split(zs[:len(flat)])
    z_at_obs = dict(zip(L.GAMMAS, zs[len(flat):]))
    gd = grid_diffs(zgrid, v1ref.Z_GRID, L.MASSES)
    d30 = max(abs(z_at_obs[float(g)] - v1ref.Z_AT_OBS[g]) for g in v1ref.Z_AT_OBS)
    gate.update({"v1_grid_points": len(gd), "v1_grid_maxdiff": gd[0][0], "v1_at30_maxdiff": d30,
                 "v1_grid_ok": len(gd) == 3 * len(L.MASSES) and gd[0][0] <= V1_GRID_TOL
                 and d30 <= V1_TOL,
                 "obs_scan_s": t_obs, "obs_fallbacks": sc.n_fallback, "obs_maxit": sc.n_maxit})
    print("OBSCHECK %d shapes in %.1f s (%d Newton runs, %d fallbacks, %d at maxit); "
          "max |Z_fast - Z_v1| grid %.2e, at 30.40 %.2e" % (
              len(zs), t_obs, sc.n_newton, sc.n_fallback, sc.n_maxit, gd[0][0], d30), flush=True)
    for x in gd[:5]:
        print("OBSDIFF gamma %s mass %.2f fast %.6f v1 %.6f diff %.2e" % (x[1], x[2], x[3], x[4],
                                                                          x[0]), flush=True)
    obs = {"Z_grid": {str(g): zgrid[g] for g in L.GAMMAS},
           "Z_at_30.40": {str(g): z_at_obs[g] for g in L.GAMMAS}}
    for v_ in L.VARIANTS:
        prof = L.variant_profile(zgrid, v_)
        i = max(range(len(prof)), key=lambda k: prof[k])
        obs[v_] = {"zmax": prof[i], "mmax": L.MASSES[i],
                   "upcrossings": {"%.1f" % u: L.count_upcrossings(prof, u) for u in L.LEVELS}}
        print("OBS %s scan max Z=%.3f at %.2f GeV; upcrossings %s (v1 %s)" % (
            v_, prof[i], L.MASSES[i], obs[v_]["upcrossings"], v1ref.OBS_UPCROSSINGS[v_]),
            flush=True)
    z_obs = {"g1.78": d0["Z0"], "g1.0": z_at_obs[1.0], "g3.0": z_at_obs[3.0],
             "float": max(d0["Z0"], z_at_obs[1.0], z_at_obs[3.0])}
    obs["Z_obs_used"] = z_obs
    print("OBS Z at 30.40: g1.0=%.3f g1.78=%.3f (exact emuframe shape %.3f) g3.0=%.3f" % (
        z_at_obs[1.0], z_at_obs[1.78], d0["Z0"], z_at_obs[3.0]), flush=True)

    # toy truth, exactly as leescan-v1 (ParFit.fit), checked against v1
    f0 = pf0.fit(n, m, mu_fixed=0.0)
    truth_T = [float(x) for x in pf0.T(np.array(f0["a"]))]
    gate["truth_ok"] = (abs(f0["r"] / v1ref.TRUTH_R - 1.0) <= TRUTH_RTOL and
                        abs(sum(truth_T) / v1ref.TRUTH_SUM_T - 1.0) <= TRUTH_RTOL)
    print("TRUTH r=%.10f sum_T=%.6f (v1 %.10f %.6f) ok=%s" % (
        f0["r"], sum(truth_T), v1ref.TRUTH_R, v1ref.TRUTH_SUM_T, gate["truth_ok"]), flush=True)
    res.update({"gate": gate, "observed": obs,
                "truth": {"r": f0["r"], "sum_T": sum(truth_T), "T": truth_T}})
    save()

    # toys: earlier rows (if any), then the missing indices, each saved as it finishes
    cols = L.csv_columns()
    rows = read_rows(prior_csv) if prior_csv else []
    done = {r["idx"] for r in rows}
    todo = [i for i in range(ntoys) if i not in done]
    print("TOYS prior %d, to run %d" % (len(rows), len(todo)), flush=True)
    csv_path = os.path.join(out_dir, "toys.csv")
    diag_path = os.path.join(out_dir, "toydiag.csv")
    nfb = nmx = 0
    secs = []
    t2 = time.time()
    with open(csv_path, "w") as fcsv, open(diag_path, "w") as fdiag:
        fcsv.write(",".join(cols) + "\n")
        fdiag.write("idx,sec,fallbacks,maxit\n")

        def put(row):
            fcsv.write(",".join(("%.5f" % row[c]) if isinstance(row[c], float) else str(row[c])
                                for c in cols) + "\n")

        for row in rows:
            put(row)
        fcsv.flush()
        stopped = False
        if todo:
            pool = Pool(workers, initializer=_init, initargs=(here, edges, flat, truth_T, f0["r"]))
            try:
                for row in pool.imap_unordered(_toy, todo, chunksize=2):
                    fb_i = row.pop("_fallback")
                    mx_i = row.pop("_maxit")
                    sec = row.pop("_sec")
                    nfb += fb_i
                    nmx += mx_i
                    secs.append(sec)
                    rows.append(row)
                    put(row)
                    fcsv.flush()
                    fdiag.write("%d,%.3f,%d,%d\n" % (row["idx"], sec, fb_i, mx_i))
                    fdiag.flush()
                    k = len(secs)
                    if k in (10, 50) or k % 100 == 0:
                        print("toys done %d of %d, %.0f s, mean %.2f s per toy per worker, "
                              "fallbacks %d, maxit %d" % (k, len(todo), time.time() - t2,
                                                          sum(secs) / k, nfb, nmx), flush=True)
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

    # gate V2: the 9 toys of leescan-v1
    td = toy_diffs({r["idx"]: r for r in rows}, v1ref.TOYS_ZMAX, L.VARIANTS)
    want = len(v1ref.TOYS_ZMAX) * len(L.VARIANTS)
    gate.update({"v1_toy_values": len(td), "v1_toy_maxdiff": td[0][0] if td else None,
                 "v1_toys_ok": len(td) == want and td[0][0] <= V1_TOY_TOL,
                 "toy_fallbacks": nfb, "toy_maxit": nmx,
                 "mean_s_per_toy_per_worker": (sum(secs) / len(secs)) if secs else None})
    mm = sum(1 for idx, ref in v1ref.TOYS_MMAX.items() for v_ in L.VARIANTS
             if any(r["idx"] == idx and abs(r[v_ + "_mmax"] - ref[v_]) < 1e-6 for r in rows))
    gate["v1_toy_mmax_same"] = mm
    print("TOYCHECK %d of %d v1 toy maxima compared; max |dZ| %s; same argmax mass %d of %d" % (
        len(td), want, ("%.2e" % td[0][0]) if td else "-", mm, want), flush=True)
    for x in td[:5]:
        print("TOYDIFF idx %d %s fast %.5f v1 %.5f diff %.2e" % (x[1], x[2], x[3], x[4], x[0]),
              flush=True)

    gate["ntoys"] = len(rows)
    checks = (("closure", gate["closure_ok"]), ("scanner", gate["scanner_ok"]),
              ("v1 grid", gate["v1_grid_ok"]), ("v1 toys", gate["v1_toys_ok"]),
              ("truth", gate["truth_ok"]), ("toys<%d" % L.MIN_TOYS, len(rows) >= L.MIN_TOYS))
    gate["ok"] = all(ok for _, ok in checks)
    gate["why"] = ", ".join(w for w, ok in checks if not ok)
    summ = L.summarize(rows, z_obs)
    res["summary"] = summ
    res["grades"] = L.grade(gate, summ, obs[L.PRIMARY]["mmax"])
    save()
    return res


def fast_line(res):
    g = res["gate"]
    return ("LEEFAST: toys %d | closure %.4f fast %.4f | v1 grid maxdiff %.2e at30 %.2e ok %s | "
            "v1 toys %d maxdiff %s ok %s | truth %s | fallbacks obs %d toys %d | maxit obs %d "
            "toys %d | s/toy/worker %s | gate %s%s" % (
                g["ntoys"], g["Z_par3_closure"], g["Z_scanner_default_shape"],
                g["v1_grid_maxdiff"], g["v1_at30_maxdiff"], g["v1_grid_ok"], g["v1_toy_values"],
                ("%.2e" % g["v1_toy_maxdiff"]) if g["v1_toy_maxdiff"] is not None else "-",
                g["v1_toys_ok"], g["truth_ok"], g["obs_fallbacks"], g["toy_fallbacks"],
                g["obs_maxit"], g["toy_maxit"],
                ("%.2f" % g["mean_s_per_toy_per_worker"]) if g["mean_s_per_toy_per_worker"]
                else "-", "PASS" if g["ok"] else "FAIL",
                "" if g["ok"] else " (" + g["why"] + ")"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-only", action="store_true")
    ap.add_argument("--out", default="/out")
    ap.add_argument("--ntoys", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--budget-s", type=float, default=14000.0)
    ap.add_argument("--prior-csv", default=None)
    a = ap.parse_args(argv)
    fetch_leescan()
    L = load_leescan()
    L.fetch()                      # aprime_smooth.py, aleph-fig5.json (sha256) and emuframe.py
    if a.fetch_only:
        return
    print(VERSION, "with", L.VERSION, flush=True)
    res = run(a.out, a.ntoys, a.workers, a.budget_s, a.prior_csv)
    print(json.dumps({"gate": res["gate"], "grades": res["grades"],
                      "observed_max": {v: res["observed"][v] for v in L.VARIANTS},
                      "Z_at_30.40": res["observed"]["Z_at_30.40"]}, indent=1), flush=True)
    for v in L.VARIANTS:
        x = res["summary"][v]
        print("SUMMARY %s %s" % (v, json.dumps({"E_N": x["E_N"], "direct": x["direct"],
                                                 "observed": x.get("observed"),
                                                 "conversions": x["conversions"]})), flush=True)
    print(fast_line(res), flush=True)
    try:
        print(L.line(res), flush=True)
    except (TypeError, KeyError, ValueError) as exc:   # e.g. no toys finished
        print("LEESCAN: summary line unavailable (%s); grades %s" % (exc, res["grades"]),
              flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
