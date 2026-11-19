#!/usr/bin/env python3
"""run_kly4fj: does OPAL's two-jet requirement remove the light-scalar events if the muons are
taken out before jet finding?

Job kly4f-v1 (NOTE-higgs-searches.md 0.7, section 6b) found that OPAL's four-fermion selection
keeps 85 % of Ko, Li and Yu's model III events with a 12 GeV scalar (Q12), which gave the
light-scalar corner a second exclusion from a second detector (F5 PASS). But eff4f.py clusters
Durham jets on ALL seen particles, muons included, so the two isolated muons always make two
"jets" and OPAL's ">= 2 Durham jets" cut never bites. Our reading of OPAL's paper does not say
whether leptons were removed before jet finding. If they were, the hadrons of a 12 GeV scalar
(mass^2 / E_vis^2 ~ 144 / 8281 = 0.017 < 0.02) would nearly always form ONE jet at y_cut 0.02.

This script regenerates the SAME events as kly-v1 and kly4f-v1 (same generator, seeds, model
order, Pythia settings), re-applies eff4f's selections (closure: every count must equal
kly4f-v1's), and adds three OPAL variants in which the two signal muons are removed before
Durham clustering:
  OPAL:hj_full02   y_cut 0.02,  y normalised by the visible energy of the whole event
  OPAL:hj_had02    y_cut 0.02,  y normalised by the visible energy of the hadrons only
  OPAL:hj_full005  y_cut 0.005, normalised by the whole event
Each requires OPAL:nominal AND >= 2 hadronic Durham jets.

Needs kly.py, eff4f.py, lep4f.py, run_kly4f.py and xkin's xme.py, evana.py, fadgen.py,
run_xkin.py next to it (the job fetches the published ones), numpy, pythia8mc.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

VERSION = "mv2 kly4fj 0.1.0"
EXPTS = ("OPAL", "L3", "ALEPH")
NEW_KEYS = ("OPAL:hj_full02", "OPAL:hj_had02", "OPAL:hj_full005")
# kly4f-v1 (returned 2026-11-19): n_acc and pass_acc_win for OPAL:nominal and L3:nominal
KLY4F_V1 = {"B110": (6778, 5806, 4114), "B180": (6877, 5912, 4098), "B110L": (7049, 6052, 4466),
            "Q12": (7140, 6075, 4367), "Q30": (7152, 6366, 4163), "Q50": (6985, 5705, 3952)}


def durham_history(p4):
    """Durham (E-scheme) clustering of an (N, 4) array (E, px, py, pz) down to one cluster.
    Returns the list of UNNORMALISED distances d = 2 min(E_i, E_j)^2 (1 - cos theta_ij) of the
    pair merged at each step (N - 1 values). y = d / E_norm^2; the merge order does not depend on
    the normalisation, so one history gives the jet count for any normalisation and y_cut."""
    p = np.array(p4, float).reshape(-1, 4).copy()
    hist = []
    while len(p) >= 2:
        e = p[:, 0]
        mom = p[:, 1:]
        pn = np.linalg.norm(mom, axis=1)
        pn = np.where(pn > 0, pn, 1e-12)
        u = mom / pn[:, None]
        c = np.clip(u @ u.T, -1.0, 1.0)
        emin = np.minimum.outer(e, e)
        d = 2.0 * emin ** 2 * (1.0 - c)
        np.fill_diagonal(d, np.inf)
        k = int(np.argmin(d))
        a, b = divmod(k, len(p))
        hist.append(float(d[a, b]))
        p[a] = p[a] + p[b]
        p = np.delete(p, b, axis=0)
    return hist


def njets_from_history(n_particles, hist, ycut, enorm):
    """Exclusive jet count: merge while the smallest y is below y_cut; stop at the first merge
    whose y >= y_cut. Equivalent to eff4f.durham_njets when enorm = sum of the input energies."""
    if n_particles < 2 or enorm <= 0:
        return n_particles
    e2 = enorm ** 2
    for k, d in enumerate(hist):
        if d / e2 >= ycut:
            return n_particles - k
    return 1


def hadronic_jets(ids, p4, i, j, seen):
    """Jet counts with the two signal muons removed. Returns dict of counts, the y of the last
    merge (2 -> 1 hadronic clusters) in both normalisations, and the full-event check count."""
    p4 = np.asarray(p4, float)
    had = seen.copy()
    had[i] = False
    had[j] = False
    e_full = float(p4[seen, 0].sum())
    ph = p4[had]
    e_had = float(ph[:, 0].sum()) if len(ph) else 0.0
    h = durham_history(ph) if len(ph) >= 2 else []
    n = len(ph)
    out = {"full02": njets_from_history(n, h, 0.02, e_full),
           "had02": njets_from_history(n, h, 0.02, e_had),
           "full005": njets_from_history(n, h, 0.005, e_full),
           "y12_full": (h[-1] / e_full ** 2) if (h and e_full > 0) else float("nan"),
           "y12_had": (h[-1] / e_had ** 2) if (h and e_had > 0) else float("nan"),
           "e_had": e_had, "e_full": e_full}
    hs = durham_history(p4[seen]) if int(seen.sum()) >= 2 else []
    out["all02"] = njets_from_history(int(seen.sum()), hs, 0.02, e_full)
    return out


def new_pass(r, hj):
    """The three new OPAL variants: OPAL:nominal AND >= 2 hadronic jets."""
    base = bool(r["OPAL:nominal"])
    return {"OPAL:hj_full02": base and hj["full02"] >= 2,
            "OPAL:hj_had02": base and hj["had02"] >= 2,
            "OPAL:hj_full005": base and hj["full005"] >= 2}


def run_model(task):
    """Mirror of run_kly4f.run_model (same generation, seeds and Pythia settings)."""
    label, n, seed, tmpdir, outdir, budget = task
    import eff4f
    import kly
    import xme
    import run_xkin
    t0 = time.time()
    kind, par, layout, sig_id = kly.MODELS[label]
    rng = np.random.default_rng(seed)
    ev = kly.generate(label, n, rng)
    lhe = os.path.join(tmpdir, 'kly4fj_%s.lhe' % label)
    xme.write_lhe(lhe, layout, ev)
    mphi = par.get("m_phi", 30.4)
    sets = run_xkin.pythia_common(seed % 900000000 + 1) + [
        "Beams:frameType = 4", "Beams:LHEF = %s" % lhe,
        "32:m0 = 30.4", "32:mWidth = 1.78", "32:mMin = 5.", "32:mMax = 85.",
        "35:m0 = 30.4", "35:mWidth = 1.78", "35:mMin = 5.", "35:mMax = 85.",
        "36:m0 = %.3f" % mphi, "36:mWidth = 0.01", "36:mMin = 5.", "36:mMax = 85."]
    py = run_xkin.make_pythia(sets)
    counts = eff4f.new_counts()
    newc = {k: 0 for k in NEW_KEYS}
    njet_mismatch = 0
    nj_hist = {"full02": {}, "had02": {}, "full005": {}}
    y12f, y12h = [], []
    nok = nfail = nopair = 0
    stopped = False
    for k in range(n):
        if time.time() - t0 > budget:
            stopped = True
            break
        if not py.next():
            nfail += 1
            if nfail > 50 and nok == 0:
                break
            continue
        nok += 1
        ids, p4, ch, sig, vtx = run_xkin.extract(py.event, (sig_id,))
        smu = np.nonzero(sig & (np.abs(ids) == 13))[0]
        if len(smu) != 2 or ch[smu[0]] * ch[smu[1]] >= 0:
            nopair += 1
            continue
        i, j = int(smu[0]), int(smu[1])
        r = eff4f.evaluate(ids, p4, ch, i, j)
        eff4f.accumulate(counts, r)
        if r["acc"] and r["in_window"]:
            seen = np.asarray(eff4f.em_or_track(ids), bool)
            hj = hadronic_jets(ids, p4, i, j, seen)
            if hj["all02"] != r["njets_y0.02"]:
                njet_mismatch += 1
            for key, ok in new_pass(r, hj).items():
                if ok:
                    newc[key] += 1
            for v in nj_hist:
                b = str(min(hj[v], 4))
                nj_hist[v][b] = nj_hist[v].get(b, 0) + 1
            y12f.append(hj["y12_full"])
            y12h.append(hj["y12_had"])
        if nok % 250 == 0:
            with open(os.path.join(outdir, 'partial4fj_%s.json' % label), 'w') as f:
                json.dump(dict(model=label, n_hadronised=nok, counts=counts, new=newc,
                               seconds=round(time.time() - t0, 1)), f)
    q = {}
    for key, v in (("y12_had_fullnorm", y12f), ("y12_had_hadnorm", y12h)):
        a = np.array(v, float)
        a = a[np.isfinite(a)]
        q[key] = [round(float(x), 5) for x in np.quantile(a, (0.05, 0.25, 0.5, 0.75, 0.95))] if len(a) else []
    ref = KLY4F_V1.get(label)
    closure = (ref is not None and counts["n_acc"] == ref[0] and
               counts["pass_acc_win"]["OPAL:nominal"] == ref[1] and
               counts["pass_acc_win"]["L3:nominal"] == ref[2])
    stats = dict(model=label, kind=kind, params=par, parton=ev['stats'], n_hadronised=nok,
                 n_fail=nfail, n_no_truth_pair=nopair, stopped_by_budget=stopped,
                 seconds=round(time.time() - t0, 1), closure_kly4f_v1=closure,
                 njets_all_mismatch_vs_eff4f=njet_mismatch, njets_hadronic_hist=nj_hist)
    return label, counts, newc, q, stats


def eps_all(counts, newc):
    import eff4f
    eps = {k: eff4f.eps_kin(counts, k)[0] for k in eff4f.KEYS}
    n = counts["n_acc"]
    for k in NEW_KEYS:
        eps[k] = (newc[k] / n) if n else float("nan")
    return eps


def confrontations(eps):
    """OPAL + L3 at the lowest literature rate, for each hadronic-jet variant of OPAL, with L3
    nominal and with L3's weakest variant; and OPAL alone."""
    import eff4f
    from run_kly4f import weakest
    n_lit = eff4f.n_sig_for_rate(eff4f.R_LIT)
    std = {k: v for k, v in eps.items() if k not in NEW_KEYS}
    l3w = weakest(std, "L3")[1]
    out = {}
    for k in NEW_KEYS:
        tag = k.split(":", 1)[1]
        for l3tag, l3 in (("L3nominal", eps["L3:nominal"]), ("L3weakest", l3w)):
            e = {"OPAL": eps[k], "L3": l3, "ALEPH": eps["ALEPH:nominal"]}
            out["OPAL+L3|%s|%s|lit1.1e-5" % (tag, l3tag)] = eff4f.confront(("OPAL", "L3"), e, n_sig=n_lit)
        e = {"OPAL": eps[k], "L3": eps["L3:nominal"], "ALEPH": eps["ALEPH:nominal"]}
        out["OPAL|%s|lit1.1e-5" % tag] = eff4f.confront(("OPAL",), e, n_sig=n_lit)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--nsig', type=int, default=8000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20261121)   # = run_kly / run_kly4f default
    ap.add_argument('--models', default='B110,B180,B110L,Q12,Q30,Q50')
    ap.add_argument('--budget-min', type=float, default=40.0)
    a = ap.parse_args()
    import eff4f
    import kly
    import lep4f
    print('VERSIONS', VERSION, kly.VERSION, eff4f.VERSION, lep4f.VERSION, flush=True)
    os.makedirs(a.out, exist_ok=True)
    tmp = '/tmp/kly4fj'
    os.makedirs(tmp, exist_ok=True)
    models = a.models.split(',')
    order = 'B110,B180,B110L,Q12,Q30,Q50'.split(',')
    tasks = [(m, a.nsig, a.seed + 7 * order.index(m) + 1, tmp, a.out, a.budget_min * 60.0)
             for m in models]
    with mp.Pool(min(a.workers, len(tasks))) as pool:
        results = pool.map(run_model, tasks, chunksize=1)
    out = dict(tool=VERSION, kly=kly.VERSION, eff4f=eff4f.VERSION, lep4f=lep4f.VERSION,
               made_by='MV2 of Munim, Inc. (made with AI agents)',
               question='OPAL two-jet requirement with the muons removed before jet finding',
               window_obs={e: eff4f.WINDOW_OBS[e]["n_obs"] for e in EXPTS}, models={})
    for label, c, newc, q, st in results:
        print('TASK', json.dumps(st, default=str), flush=True)
        eps = eps_all(c, newc)
        out["models"][label] = dict(stats=st, counts=c, new_counts=newc, quantiles_acc_window=q,
                                    eps={k: round(v, 4) for k, v in eps.items()},
                                    confront=confrontations(eps))
    with open(os.path.join(a.out, 'kly4fj-summary.json'), 'w') as f:
        json.dump(out, f, indent=1, default=str)

    print('\nOPAL with hadrons-only Durham jets; eps vs ALEPH acceptance, 20-40 GeV, no muon ID')
    for label, r in out["models"].items():
        e = r["eps"]
        print('%-6s OPAL:nominal=%.3f  hj_full02=%.3f  hj_had02=%.3f  hj_full005=%.3f  L3:nominal=%.3f' % (
            label, e["OPAL:nominal"], e["OPAL:hj_full02"], e["OPAL:hj_had02"], e["OPAL:hj_full005"],
            e["L3:nominal"]))
        print('       hadronic njets:', json.dumps(r["stats"]["njets_hadronic_hist"]),
              'y12 quantiles:', json.dumps(r["quantiles_acc_window"]))
    print('\nconfrontation at the lowest literature rate (b = 0):')
    for label, r in out["models"].items():
        for k, c in r["confront"].items():
            print('%-6s %-40s n=%d pred=%7.2f p=%.3g z=%.2f' % (
                label, k, c["n_obs"], c["pred"], c["p_value"], c["z"]))
    last = []
    for label, r in out["models"].items():
        e = r["eps"]
        worst = max(r["confront"][k]["p_value"] for k in r["confront"]
                    if k.startswith("OPAL+L3|") and k.endswith("|L3weakest|lit1.1e-5"))
        last.append('%s hj full02/had02/full005 %.3f/%.3f/%.3f worst O+L3w lit p=%.2g closure=%s mism=%d' % (
            label, e["OPAL:hj_full02"], e["OPAL:hj_had02"], e["OPAL:hj_full005"], worst,
            r["stats"]["closure_kly4f_v1"], r["stats"]["njets_all_mismatch_vs_eff4f"]))
    print('\nKLY4FJ: ' + ' | '.join(last))
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
