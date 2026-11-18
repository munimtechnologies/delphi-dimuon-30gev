#!/usr/bin/env python3
"""run_eff4f: hadron-level efficiency of the LEP1 mu mu q qbar selections for the three boson
models of xkin (V, S, P), and the confrontation with the published 20-40 GeV dimuon-mass counts.

Needs xkin's xme.py, evana.py, fadgen.py, run_xkin.py and analysis/lep4f.py next to it (the job
fetches them from the public repo), numpy and pythia8mc.

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

EXPTS = ("OPAL", "L3", "ALEPH")
QUANT = (0.05, 0.25, 0.5, 0.75, 0.95)
EXTRA = ("opal_alpha_lo", "opal_alpha_hi", "nch", "njets_y0.02", "aleph_cone30_max", "l3_dmin", "m")


def run_model(task):
    model, n, seed, tmpdir = task
    import xme
    import run_xkin
    t0 = time.time()
    rng = np.random.default_rng(seed)
    ev = xme.generate_pair(n, rng) if model == 'P' else xme.generate_radiation(model, n, rng)
    lhe = os.path.join(tmpdir, 'eff4f_%s.lhe' % model)
    xme.write_lhe(lhe, model, ev)
    sets = run_xkin.pythia_common(seed % 900000000 + 1) + [
        "Beams:frameType = 4", "Beams:LHEF = %s" % lhe,
        "32:m0 = 30.4", "32:mWidth = 1.78", "32:mMin = 5.", "32:mMax = 85.",
        "35:m0 = 30.4", "35:mWidth = 1.78", "35:mMin = 5.", "35:mMax = 85.",
        "36:m0 = 30.4", "36:mWidth = 0.01", "36:mMin = 5.", "36:mMax = 85."]
    py = run_xkin.make_pythia(sets)
    counts = eff4f.new_counts()
    extra = {k: [] for k in EXTRA}
    nok = nfail = nopair = 0
    for _ in range(n):
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
        r = eff4f.evaluate(ids, p4, ch, int(smu[0]), int(smu[1]))
        eff4f.accumulate(counts, r)
        if r["acc"]:
            for k in extra:
                extra[k].append(r[k])
    q = {}
    for k, v in extra.items():
        a = np.array(v, float)
        a = a[np.isfinite(a)]
        q[k] = [round(float(x), 3) for x in np.quantile(a, QUANT)] if len(a) else []
    frac = {}
    if extra["nch"]:
        nch = np.array(extra["nch"])
        nj = np.array(extra["njets_y0.02"])
        frac = {"nch_ge_8": round(float(np.mean(nch >= 8)), 4),
                "nch_ge_6": round(float(np.mean(nch >= 6)), 4),
                "njets_y0.02_ge_2": round(float(np.mean(nj >= 2)), 4)}
    stats = dict(model=model, parton=ev['stats'], n_hadronised=nok, n_fail=nfail,
                 n_no_truth_pair=nopair, seconds=round(time.time() - t0, 1),
                 multiplicity_fractions_in_acceptance=frac)
    return model, counts, q, stats


def yield_options():
    """(tag, reading -> ALEPH yield): central, minus one sigma, and the literature rate."""
    import lep4f
    return (("central", lambda rd: None),
            ("minus1sigma", lambda rd: lep4f.ALEPH_N_SIG - lep4f.ALEPH_N_SIG_ERR),
            ("lit1.1e-5", lambda rd: eff4f.n_sig_for_rate(eff4f.R_LIT, rd)))


def tables(counts_by_model):
    out = {}
    for model, c in counts_by_model.items():
        eps = {k: eff4f.eps_kin(c, k) for k in eff4f.KEYS}
        res = {"n_pairs": c["n_pairs"], "n_acc": c["n_acc"], "n_acc_win": c["n_acc_win"],
               "eps_kin": {k: [round(v[0], 4), round(v[1], 4)] for k, v in eps.items()},
               "confront": {}}
        for variant in eff4f.VARIANT_NAMES:
            e_by = {}
            for ex in EXPTS:
                key = "%s:%s" % (ex, variant)
                e_by[ex] = eps[key][0] if key in eps else eps["%s:nominal" % ex][0]
            for reading in ("nominal", "low"):
                for ys, nsig_of in yield_options():
                    nsig = nsig_of(reading)
                    tag = "%s|%s|%s" % (variant, reading, ys)
                    res["confront"][tag] = {
                        "OPAL": eff4f.confront(["OPAL"], e_by, reading, eff4f.ID_EFF, nsig),
                        "L3": eff4f.confront(["L3"], e_by, reading, eff4f.ID_EFF, nsig),
                        "ALEPH": eff4f.confront(["ALEPH"], e_by, reading, eff4f.ID_EFF, nsig),
                        "OPAL+L3": eff4f.confront(["OPAL", "L3"], e_by, reading, eff4f.ID_EFF, nsig)}
        out[model] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--nsig', type=int, default=10000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20261118)
    ap.add_argument('--models', default='V,S,P')
    a = ap.parse_args()
    import lep4f
    print('VERSIONS', eff4f.VERSION, lep4f.VERSION, flush=True)
    os.makedirs(a.out, exist_ok=True)
    tmp = '/tmp/eff4f'
    os.makedirs(tmp, exist_ok=True)
    models = a.models.split(',')
    tasks = [(m, a.nsig, a.seed + 7 * k + 1, tmp) for k, m in enumerate(models)]
    with mp.Pool(min(a.workers, len(tasks))) as pool:
        results = pool.map(run_model, tasks, chunksize=1)
    counts, quants, stats = {}, {}, []
    for model, c, q, st in results:
        counts[model] = c
        quants[model] = q
        stats.append(st)
        print('TASK', json.dumps(st), flush=True)
    summary = dict(tool=eff4f.VERSION, lep4f=lep4f.VERSION,
                   made_by='MV2 of Munim, Inc. (made with AI agents)',
                   window_GeV=list(eff4f.WINDOW), window_obs=eff4f.WINDOW_OBS,
                   id_eff_per_muon=eff4f.ID_EFF, bw_fraction_gen=eff4f.bw_fraction(*eff4f.GEN_RANGE),
                   r_lit=eff4f.R_LIT, counts=counts, quantiles_in_acceptance=quants, tasks=stats,
                   results=tables(counts))
    with open(os.path.join(a.out, 'eff4f-summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)
    # compact report
    print('\nmodel  n_acc   eps OPAL       eps L3         eps ALEPH   (nominal cuts, 20-40 GeV, no muon ID)')
    for model, res in summary['results'].items():
        e = res['eps_kin']
        print('%-5s %6d  %.3f+-%.3f  %.3f+-%.3f  %.3f+-%.3f' % (
            model, res['n_acc'], e['OPAL:nominal'][0], e['OPAL:nominal'][1], e['L3:nominal'][0],
            e['L3:nominal'][1], e['ALEPH:nominal'][0], e['ALEPH:nominal'][1]))
    print('\nvariant eps:')
    for model, res in summary['results'].items():
        print(model, ' '.join('%s=%.3f' % (k, v[0]) for k, v in res['eps_kin'].items()))
    print('\nconfrontation (ID 0.86^2 per pair; b = 0): n_obs, predicted, s_up, mu_max, p, z')
    for model, res in summary['results'].items():
        for tag in ('nominal|nominal|central', 'nominal|low|minus1sigma', 'nominal|low|lit1.1e-5'):
            for grp, r in res['confront'][tag].items():
                print('%-2s %-26s %-8s n=%d pred=%7.2f s_up=%5.2f mu_max=%.4f p=%.3g z=%.1f' % (
                    model, tag, grp, r['n_obs'], r['pred'], r['s_up_95'], r['mu_max'],
                    r['p_value'], r['z']))
    print('\nworst case over all variants (OPAL+L3, low reading, lit1.1e-5 and minus1sigma):')
    for model, res in summary['results'].items():
        worst = max(((t, r['OPAL+L3']['p_value']) for t, r in res['confront'].items()
                     if '|low|' in t and not t.endswith('|central')), key=lambda x: x[1])
        print(model, worst[0], 'p=%.3g' % worst[1])
    print('\nquantiles (5,25,50,75,95 %) in acceptance:')
    for model, q in quants.items():
        print(model, json.dumps(q))
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
