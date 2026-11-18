#!/usr/bin/env python3
"""run_kly4f: do the LEP1 four-fermion measurements (e+e- -> mu+ mu- q qbar at the Z pole) also
exclude the two published models of Ko, Li and Yu (arXiv:1610.07526) for the ALEPH 30 GeV excess?

Job kly-v1 (NOTE-higgs-searches.md 0.6, section 6) showed that the LEP1 Higgs searches exclude
both models. One case is held up by a single search: model III with a light scalar (Q12,
m_phi = 12 GeV) escapes the DELPHI, ALEPH and OPAL Higgs searches through their recoil-mass cuts,
and only L3's search (no recoil cut) closes it. This script applies the OPAL, L3 and ALEPH
four-fermion selections of eff4f.py (one definition; the selections of NOTE-fourfermion.md) to
the SAME events as kly-v1: same generator (kly.py), same seeds, same model order, same Pythia
settings. So n_hadronised and n_fail must equal kly-v1's (closure).

Needs kly.py, eff4f.py, lep4f.py and xkin's xme.py, evana.py, fadgen.py, run_xkin.py next to it
(the job fetches the published ones from the public repo), numpy, pythia8mc.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import eff4f
import kly

VERSION = "mv2 kly4f 0.1.0"
EXPTS = ("OPAL", "L3", "ALEPH")
# kly-v1 (2026-11-18): hadronised events and Pythia failures per model, for the closure check
KLY_V1 = {"B110": (7675, 325), "B180": (7688, 312), "B110L": (7786, 214),
          "Q12": (8000, 0), "Q30": (8000, 0), "Q50": (8000, 0)}


def weakest(eps_by_key, expt):
    """(variant, eps) of the variant of `expt` with the smallest efficiency."""
    vals = [(k.split(":", 1)[1], v) for k, v in eps_by_key.items() if k.split(":", 1)[0] == expt]
    return min(vals, key=lambda kv: kv[1])


def run_model(task):
    """Mirror of run_kly.run_model (same generation, seeds and Pythia settings), with eff4f's
    four-fermion selections in place of lephz's Higgs-search selections."""
    label, n, seed, tmpdir, outdir, budget = task
    import xme
    import run_xkin
    t0 = time.time()
    kind, par, layout, sig_id = kly.MODELS[label]
    rng = np.random.default_rng(seed)
    ev = kly.generate(label, n, rng)
    lhe = os.path.join(tmpdir, 'kly4f_%s.lhe' % label)
    xme.write_lhe(lhe, layout, ev)
    mphi = par.get("m_phi", 30.4)
    sets = run_xkin.pythia_common(seed % 900000000 + 1) + [
        "Beams:frameType = 4", "Beams:LHEF = %s" % lhe,
        "32:m0 = 30.4", "32:mWidth = 1.78", "32:mMin = 5.", "32:mMax = 85.",
        "35:m0 = 30.4", "35:mWidth = 1.78", "35:mMin = 5.", "35:mMax = 85.",
        "36:m0 = %.3f" % mphi, "36:mWidth = 0.01", "36:mMin = 5.", "36:mMax = 85."]
    py = run_xkin.make_pythia(sets)
    counts = eff4f.new_counts()
    alpha_lo, nch, njets, l3d = [], [], [], []
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
            alpha_lo.append(r["opal_alpha_lo"])
            nch.append(r["nch"])
            njets.append(r["njets_y0.02"])
            l3d.append(r["l3_dmin"])
        if nok % 250 == 0:
            with open(os.path.join(outdir, 'partial4f_%s.json' % label), 'w') as f:
                json.dump(dict(model=label, n_hadronised=nok, counts=counts,
                               seconds=round(time.time() - t0, 1)), f)
    q = {}
    for key, v in (("opal_alpha_lo", alpha_lo), ("nch", nch), ("njets_y0.02", njets),
                   ("l3_dmin", l3d)):
        a = np.array(v, float)
        a = a[np.isfinite(a)]
        q[key] = [round(float(x), 3) for x in np.quantile(a, (0.05, 0.25, 0.5, 0.75, 0.95))] if len(a) else []
    frac_lt2jets = round(float(np.mean(np.array(njets) < 2)), 4) if njets else None
    stats = dict(model=label, kind=kind, params=par, parton=ev['stats'], n_hadronised=nok,
                 n_fail=nfail, n_no_truth_pair=nopair, stopped_by_budget=stopped,
                 seconds=round(time.time() - t0, 1), frac_acc_win_lt2jets_y002=frac_lt2jets,
                 closure_kly_v1=(KLY_V1.get(label) == (nok, nfail)))
    return label, counts, q, stats


def confrontations(eps_nom, eps_weak):
    """OPAL + L3 (the 20-40 GeV mass information that does not overlap the excess data) and each
    alone; central rate and the lowest literature rate (Ko, Li and Yu's own model-II rate)."""
    n_lit = eff4f.n_sig_for_rate(eff4f.R_LIT)
    out = {}
    for tag, eps in (("nominal", eps_nom), ("weakest", eps_weak)):
        for name, ex in (("OPAL+L3", ("OPAL", "L3")), ("OPAL", ("OPAL",)), ("L3", ("L3",))):
            out["%s|%s|central" % (name, tag)] = eff4f.confront(ex, eps)
            out["%s|%s|lit1.1e-5" % (name, tag)] = eff4f.confront(ex, eps, n_sig=n_lit)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--nsig', type=int, default=8000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20261121)   # = run_kly's default: same events
    ap.add_argument('--models', default='B110,B180,B110L,Q12,Q30,Q50')
    ap.add_argument('--budget-min', type=float, default=30.0, help='wall-clock budget per model')
    a = ap.parse_args()
    import lep4f
    print('VERSIONS', VERSION, kly.VERSION, eff4f.VERSION, lep4f.VERSION, flush=True)
    os.makedirs(a.out, exist_ok=True)
    tmp = '/tmp/kly4f'
    os.makedirs(tmp, exist_ok=True)
    models = a.models.split(',')
    # identical task seeds to run_kly.main (a.seed + 7 k + 1, k = position in the default order)
    order = 'B110,B180,B110L,Q12,Q30,Q50'.split(',')
    tasks = [(m, a.nsig, a.seed + 7 * order.index(m) + 1, tmp, a.out, a.budget_min * 60.0)
             for m in models]
    with mp.Pool(min(a.workers, len(tasks))) as pool:
        results = pool.map(run_model, tasks, chunksize=1)
    out = dict(tool=VERSION, kly=kly.VERSION, eff4f=eff4f.VERSION, lep4f=lep4f.VERSION,
               made_by='MV2 of Munim, Inc. (made with AI agents)',
               reference='Ko, Li, Yu, arXiv:1610.07526 (models II and III)',
               window_obs={e: eff4f.WINDOW_OBS[e]["n_obs"] for e in EXPTS}, models={})
    for label, c, q, st in results:
        print('TASK', json.dumps(st, default=str), flush=True)
        eps = {k: eff4f.eps_kin(c, k)[0] for k in eff4f.KEYS}
        nom = {e: eps["%s:nominal" % e] for e in EXPTS}
        weak = {e: weakest(eps, e)[1] for e in EXPTS}
        out["models"][label] = dict(stats=st, counts=c, quantiles_acc_window=q,
                                    eps={k: round(v, 4) for k, v in eps.items()},
                                    weakest={e: weakest(eps, e) for e in EXPTS},
                                    confront=confrontations(nom, weak))
    with open(os.path.join(a.out, 'kly4f-summary.json'), 'w') as f:
        json.dump(out, f, indent=1, default=str)

    print('\nLEP1 four-fermion selections on Ko-Li-Yu model events; eps vs ALEPH acceptance, 20-40 GeV, no muon ID')
    for label, r in out["models"].items():
        print('%s n_acc=%d  ' % (label, r["counts"]["n_acc"]) +
              '  '.join('%s=%.3f' % (k, r["eps"][k]) for k in eff4f.KEYS))
    print('\nweakest variant per experiment:')
    for label, r in out["models"].items():
        print(label, json.dumps(r["weakest"]))
    print('\nconfrontation (b = 0; observed in 20-40 GeV: %s):' % json.dumps(out["window_obs"]))
    for label, r in out["models"].items():
        for k, c in r["confront"].items():
            print('%-6s %-26s n=%d pred=%7.2f s_up=%5.2f mu_max=%.4f p=%.3g z=%.2f' % (
                label, k, c["n_obs"], c["pred"], c["s_up_95"], c["mu_max"], c["p_value"], c["z"]))
    print('\nquantiles (5,25,50,75,95 %) in acceptance and window:')
    for label, r in out["models"].items():
        print(label, json.dumps(r["quantiles_acc_window"]),
              'frac <2 jets (y 0.02):', r["stats"]["frac_acc_win_lt2jets_y002"],
              'closure:', r["stats"]["closure_kly_v1"])
    last = []
    for label, r in out["models"].items():
        e = r["eps"]
        c = r["confront"]
        last.append('%s eps O/L3/A %.3f/%.3f/%.3f O+L3 lit p=%.2g weakest p=%.2g closure=%s' % (
            label, e["OPAL:nominal"], e["L3:nominal"], e["ALEPH:nominal"],
            c["OPAL+L3|nominal|lit1.1e-5"]["p_value"], c["OPAL+L3|weakest|lit1.1e-5"]["p_value"],
            r["stats"]["closure_kly_v1"]))
    print('\nKLY4F: ' + ' | '.join(last))
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
