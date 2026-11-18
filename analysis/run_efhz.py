#!/usr/bin/env python3
"""run_efhz: hadron-level efficiency of ALEPH's LEP1 H l+ l- (Z* -> mu+ mu-) selection for the three
boson models of xkin (V, S, P), and the confrontation with the three H mu+ mu- candidates of
ALEPH's full LEP1 Higgs search (Phys. Lett. B 384 (1996) 427).

Needs xkin's xme.py, evana.py, fadgen.py, run_xkin.py and analysis/eff4f.py, analysis/lep4f.py next
to it (the job fetches them from the public repo), numpy and pythia8mc. Each model stops at a
wall-clock budget and writes partial counts every 500 events.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import efhz

QUANT = (0.05, 0.25, 0.5, 0.75, 0.95)
EXTRA = ("recoil", "pt_sum", "n_iso", "nch", "m")


def run_model(task):
    model, n, seed, tmpdir, outdir, budget = task
    import xme
    import run_xkin
    t0 = time.time()
    rng = np.random.default_rng(seed)
    ev = xme.generate_pair(n, rng) if model == 'P' else xme.generate_radiation(model, n, rng)
    lhe = os.path.join(tmpdir, 'efhz_%s.lhe' % model)
    xme.write_lhe(lhe, model, ev)
    sets = run_xkin.pythia_common(seed % 900000000 + 1) + [
        "Beams:frameType = 4", "Beams:LHEF = %s" % lhe,
        "32:m0 = 30.4", "32:mWidth = 1.78", "32:mMin = 5.", "32:mMax = 85.",
        "35:m0 = 30.4", "35:mWidth = 1.78", "35:mMin = 5.", "35:mMax = 85.",
        "36:m0 = 30.4", "36:mWidth = 0.01", "36:mMin = 5.", "36:mMax = 85."]
    py = run_xkin.make_pythia(sets)
    counts = efhz.new_counts()
    extra = {k: [] for k in EXTRA}
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
        ids, p4, ch, sig, vtx = run_xkin.extract(py.event, (run_xkin.MASS_IDS[model],))
        smu = np.nonzero(sig & (np.abs(ids) == 13))[0]
        if len(smu) != 2 or ch[smu[0]] * ch[smu[1]] >= 0:
            nopair += 1
            continue
        r = efhz.evaluate(ids, p4, ch, int(smu[0]), int(smu[1]))
        efhz.accumulate(counts, r)
        if r["acc"] and r["in_window"]:
            for q in extra:
                extra[q].append(r[q])
        if nok % 500 == 0:
            with open(os.path.join(outdir, 'partial_%s.json' % model), 'w') as f:
                json.dump(dict(model=model, n_hadronised=nok, counts=counts,
                               seconds=round(time.time() - t0, 1)), f)
    q = {}
    for key, v in extra.items():
        a = np.array(v, float)
        a = a[np.isfinite(a)]
        q[key] = [round(float(x), 3) for x in np.quantile(a, QUANT)] if len(a) else []
    frac = {}
    if extra["recoil"]:
        rec = np.array(extra["recoil"])
        frac = {"recoil_gt_40": round(float(np.mean(rec > 40.0)), 4),
                "recoil_gt_50": round(float(np.mean(rec > 50.0)), 4),
                "n_iso_ge_1": round(float(np.mean(np.array(extra["n_iso"]) >= 1)), 4),
                "n_iso_eq_2": round(float(np.mean(np.array(extra["n_iso"]) == 2)), 4)}
    stats = dict(model=model, parton=ev['stats'], n_hadronised=nok, n_fail=nfail,
                 n_no_truth_pair=nopair, stopped_by_budget=stopped,
                 seconds=round(time.time() - t0, 1), fractions_acc_window=frac)
    return model, counts, q, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--nsig', type=int, default=10000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20261119)
    ap.add_argument('--models', default='V,S,P')
    ap.add_argument('--budget-min', type=float, default=35.0, help='wall-clock budget per model')
    a = ap.parse_args()
    import eff4f
    import lep4f
    print('VERSIONS', efhz.VERSION, eff4f.VERSION, lep4f.VERSION, flush=True)
    os.makedirs(a.out, exist_ok=True)
    tmp = '/tmp/efhz'
    os.makedirs(tmp, exist_ok=True)
    models = a.models.split(',')
    tasks = [(m, a.nsig, a.seed + 7 * k + 1, tmp, a.out, a.budget_min * 60.0)
             for k, m in enumerate(models)]
    with mp.Pool(min(a.workers, len(tasks))) as pool:
        results = pool.map(run_model, tasks, chunksize=1)
    out = dict(tool=efhz.VERSION, eff4f=eff4f.VERSION, lep4f=lep4f.VERSION,
               made_by='MV2 of Munim, Inc. (made with AI agents)', aleph96=efhz.ALEPH96,
               f_gen=efhz.f_gen(), id_eff_per_muon=eff4f.ID_EFF, variants=efhz.VARIANTS,
               models={})
    for model, c, q, st in results:
        print('TASK', json.dumps(st), flush=True)
        eps = {k: efhz.eps(c, k) for k in efhz.KEYS}
        out["models"][model] = dict(
            stats=st, counts=c, quantiles_acc_window=q,
            eps={k: [round(v[0], 4), round(v[1], 4)] for k, v in eps.items()},
            confront={k: efhz.confront(v[0]) for k, v in eps.items()})
    with open(os.path.join(a.out, 'efhz-summary.json'), 'w') as f:
        json.dump(out, f, indent=1)

    print('\nALEPH H mu mu selection (PLB 313 (1993) 299 cuts) on boson events; eps vs ALEPH acceptance, '
          '20-40 GeV, no muon ID')
    print('model n_acc  ' + ' '.join('%-9s' % k for k in efhz.KEYS))
    for model, r in out["models"].items():
        print('%-5s %5d  ' % (model, r["counts"]["n_acc"]) +
              ' '.join('%.3f    ' % r["eps"][k][0] for k in efhz.KEYS))
    print('\ncut-by-cut (fraction of acceptance passing each nominal cut / passing all others):')
    for model, r in out["models"].items():
        n = max(r["counts"]["n_acc"], 1)
        print(model, ' '.join('%s=%.3f/%.3f' % (k, r["counts"]["cut"][k] / n, r["counts"]["nm1"][k] / n)
                               for k in efhz.CUTS))
    print('\nconfrontation with ALEPH 1996 (n_obs = 3, all counted as signal, b = 0):')
    for model, r in out["models"].items():
        for v in ("nominal", "both_iso", "recoil50", "strict"):
            c = r["confront"][v]
            print('%-2s %-9s eps=%.3f  rate nominal: pred=%6.1f p=%.2g | rate low-1sigma: pred=%5.1f p=%.2g | '
                  'rate lit: pred=%5.1f p=%.2g | subset id1: pred=%5.1f p=%.2g p_marg=%.2g | '
                  'subset id0.74: pred=%5.1f p_marg=%.2g' % (
                      model, v, c["eps"], c["rate|nominal|central"]["pred"], c["rate|nominal|central"]["p"],
                      c["rate|low|minus1sigma"]["pred"], c["rate|low|minus1sigma"]["p"],
                      c["rate|low|lit1.1e-5"]["pred"], c["rate|low|lit1.1e-5"]["p"],
                      c["subset|id1"]["pred"], c["subset|id1"]["p"], c["subset|id1"]["p_marginal"],
                      c["subset|id0.74"]["pred"], c["subset|id0.74"]["p_marginal"]))
    any_c = next(iter(out["models"].values()))["confront"]["nominal"]
    print('\neps_max (95 %% CLs, n=3, b=0): rate nominal %.4f, subset id1 %.3f' % (
        any_c["eps_max_rate_nominal"], any_c["eps_max_subset_id1"]))
    print('\nquantiles (5,25,50,75,95 %) in acceptance and window:')
    for model, r in out["models"].items():
        print(model, json.dumps(r["quantiles_acc_window"]))
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
