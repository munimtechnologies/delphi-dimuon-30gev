#!/usr/bin/env python3
"""run_lephz: hadron-level efficiencies of the four LEP1 H Z*(-> mu+ mu-) selections (ALEPH 1996,
L3 1996, DELPHI 1994, OPAL 1997) for the three boson models of xkin (V, S, P), and the combined
confrontation with their signal-compatible candidates.

Needs lephz.py, efhz.py, analysis/eff4f.py, analysis/lep4f.py and xkin's xme.py, evana.py,
fadgen.py, run_xkin.py next to it (the job fetches the published ones from the public repo), numpy
and pythia8mc. Each model stops at a wall-clock budget and writes partial counts every 250 events.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import lephz

QUANT = (0.05, 0.25, 0.5, 0.75, 0.95)


def run_model(task):
    model, n, seed, tmpdir, outdir, budget = task
    import xme
    import run_xkin
    t0 = time.time()
    rng = np.random.default_rng(seed)
    ev = xme.generate_pair(n, rng) if model == 'P' else xme.generate_radiation(model, n, rng)
    lhe = os.path.join(tmpdir, 'lephz_%s.lhe' % model)
    xme.write_lhe(lhe, model, ev)
    sets = run_xkin.pythia_common(seed % 900000000 + 1) + [
        "Beams:frameType = 4", "Beams:LHEF = %s" % lhe,
        "32:m0 = 30.4", "32:mWidth = 1.78", "32:mMin = 5.", "32:mMax = 85.",
        "35:m0 = 30.4", "35:mWidth = 1.78", "35:mMin = 5.", "35:mMax = 85.",
        "36:m0 = 30.4", "36:mWidth = 0.01", "36:mMin = 5.", "36:mMax = 85."]
    py = run_xkin.make_pythia(sets)
    counts = lephz.new_counts()
    rec, thr, dlo, dhi = [], [], [], []
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
        r = lephz.evaluate(ids, p4, ch, int(smu[0]), int(smu[1]))
        lephz.accumulate(counts, r)
        if r["acc"] and r["in_window"]:
            rec.append(r["recoil"])
            thr.append(r["thrust"])
            dlo.append(r["l3_d"][0])
            dhi.append(r["l3_d"][1])
        if nok % 250 == 0:
            with open(os.path.join(outdir, 'partial_%s.json' % model), 'w') as f:
                json.dump(dict(model=model, n_hadronised=nok, counts=counts,
                               seconds=round(time.time() - t0, 1)), f)
    q = {}
    for key, v in (("recoil", rec), ("thrust", thr), ("l3_d_min", dlo), ("l3_d_max", dhi)):
        a = np.array(v, float)
        a = a[np.isfinite(a)]
        q[key] = [round(float(x), 3) for x in np.quantile(a, QUANT)] if len(a) else []
    frac = {}
    if rec:
        r_ = np.array(rec)
        frac = {"recoil_gt_40": round(float(np.mean(r_ > 40.0)), 4),
                "recoil_gt_sqrt_s_minus_m_lo": round(float(np.mean(r_ > lephz.SQRT_S - lephz.M_LO)), 4),
                "recoil_lt_15": round(float(np.mean(r_ < 15.0)), 4)}
    stats = dict(model=model, parton=ev['stats'], n_hadronised=nok, n_fail=nfail,
                 n_no_truth_pair=nopair, stopped_by_budget=stopped,
                 seconds=round(time.time() - t0, 1), fractions_acc_window=frac)
    return model, counts, q, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--nsig', type=int, default=8000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20261120)
    ap.add_argument('--models', default='V,S,P')
    ap.add_argument('--budget-min', type=float, default=40.0, help='wall-clock budget per model')
    a = ap.parse_args()
    import eff4f
    import efhz
    import lep4f
    print('VERSIONS', lephz.VERSION, efhz.VERSION, eff4f.VERSION, lep4f.VERSION, flush=True)
    os.makedirs(a.out, exist_ok=True)
    tmp = '/tmp/lephz'
    os.makedirs(tmp, exist_ok=True)
    models = a.models.split(',')
    tasks = [(m, a.nsig, a.seed + 7 * k + 1, tmp, a.out, a.budget_min * 60.0)
             for k, m in enumerate(models)]
    with mp.Pool(min(a.workers, len(tasks))) as pool:
        results = pool.map(run_model, tasks, chunksize=1)
    out = dict(tool=lephz.VERSION, efhz=efhz.VERSION, eff4f=eff4f.VERSION, lep4f=lep4f.VERSION,
               made_by='MV2 of Munim, Inc. (made with AI agents)', searches=lephz.SEARCHES,
               f_gen=efhz.f_gen(), id_eff_per_muon=eff4f.ID_EFF,
               variants={s: {v: kw for v, (_, kw) in vs.items()} for s, vs in lephz.VARIANTS.items()},
               n_obs={s: {"compatible": lephz.n_obs(s), "all": lephz.n_obs(s, "all")} for s in lephz.ALL_SET},
               pred_if_eps_1={s: lephz.predict(s, 1.0) for s in lephz.ALL_SET},
               models={})
    for model, c, q, st in results:
        print('TASK', json.dumps(st), flush=True)
        eps = {k: lephz.eps(c, k) for k in lephz.KEYS}
        nom = {s: eps["%s:nominal" % s][0] for s in lephz.ALL_SET}
        out["models"][model] = dict(stats=st, counts=c, quantiles_acc_window=q,
                                    eps={k: [round(v[0], 4), round(v[1], 4)] for k, v in eps.items()},
                                    confront_nominal=lephz.confront_all(nom))
    with open(os.path.join(a.out, 'lephz-summary.json'), 'w') as f:
        json.dump(out, f, indent=1, default=str)

    print('\nLEP1 H Z*(mu mu) selections on boson events; eps vs ALEPH acceptance, 20-40 GeV, no muon ID')
    for model, r in out["models"].items():
        print('%s n_acc=%d  ' % (model, r["counts"]["n_acc"]) +
              '  '.join('%s=%.3f' % (k, r["eps"][k][0]) for k in lephz.KEYS))
    print('\ncut-by-cut (fraction of acceptance-and-window events passing each nominal cut):')
    for model, r in out["models"].items():
        n = max(r["counts"]["n_acc"], 1)
        print(model, ' '.join('%s=%.3f' % (k[4:], v / n) for k, v in r["counts"]["cut"].items()))
    print('\npredicted events for eps = 1 (ALEPH central rate):',
          json.dumps({s: round(v, 1) for s, v in out["pred_if_eps_1"].items()}))
    print('signal-compatible candidates:', json.dumps(out["n_obs"]))
    print('\nconfrontation (nominal selections; b = 0):')
    for model, r in out["models"].items():
        for k in ("nominal3|compatible|central", "nominal3|all|central", "nominal3|compatible|low-1sigma",
                  "nominal3|compatible|lit1.1e-5", "nominal3|all|lit1.1e-5", "L3+DELPHI|all|central",
                  "L3+DELPHI|all|lit1.1e-5", "all4|all|central", "L3_96|compatible|central",
                  "DELPHI94|compatible|central", "ALEPH96|compatible|central", "OPAL97|compatible|central"):
            c = r["confront_nominal"][k]
            print('%s %-34s n=%d pred=%7.2f s_up=%5.2f mu_max=%.4f p=%.3g z=%.2f' % (
                model, k, c["n_obs"], c["pred"], c["s_up_95"], c["mu_max"], c["p"], c["z"]))
    print('\nquantiles (5,25,50,75,95 %) in acceptance and window:')
    for model, r in out["models"].items():
        print(model, json.dumps(r["quantiles_acc_window"]), json.dumps(r["stats"]["fractions_acc_window"]))
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
