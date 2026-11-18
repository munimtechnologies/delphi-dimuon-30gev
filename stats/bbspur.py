"""bbspur: the five background treatments of PLAN amendment 0.12 (section 5g) on the realistic
b-tagged background shape, a Pythia 8 Z -> b bbar opposite-sign dimuon spectrum. Written and run
BEFORE any DELPHI dimuon mass in the 26-35 GeV window is seen; no DELPHI data are used.

Why (finding of job dimu-forecast-v2, graded 2026-11-18): on noise-free (Asimov) pseudo-data whose
background is the generator-level Z -> b bbar dimuon shape (forecast.py's 'pythia_bb' truth), the
pre-registered sideband rule of 5b picks a degree-2 background, which then fits a spurious signal
of +0.52 ALEPH-sized signals (degree 1: +1.13), and an injected mu = 1 comes back as
mu_hat = 1.54. So test A (b-tagged only) would be biased TOWARDS confirming the ALEPH excess. The
scenarios that amendment 0.12's envcast job scores (combcast's C1-C8) use only power-law and
exponential b-tagged truths, so they cannot see this. This module scores the same five treatments
(old, ss, fix3, env, env_min2; definitions identical to envcast.method_curve) on the Pythia shape,
its tilted variant and forecast's two analytic truths, at the yields of forecast's scenarios
S1-S4, with bkgsys's per-degree profile curves.

Output per truth and scenario: the sideband degree (old), the oracle spurious-signal degree (ss),
the spurious-signal table, and for each treatment the background-only mu_hat (spur), its sigma,
the expected sensitivity ul_sens, and mu_hat and Z0 for an injected ALEPH-sized signal.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import bkgsys as bs
import dimustat as ds
import forecast as fc

VERSION = "mv2 bbspur 0.1.0"
METHODS = ('old', 'ss', 'fix3', 'env', 'env_min2')
TRUTHS = ('pythia_bb', 'pythia_bb_tilt', 'exp9', 'powerlaw3')


def treat_curve(name, curves, d_old, d_ss):
    """Profile curve of one category under a treatment (as envcast.method_curve)."""
    if name == 'old':
        return curves[d_old - 1]
    if name == 'ss':
        return curves[d_ss - 1]
    if name == 'fix3':
        return curves[2]
    if name == 'env':
        return bs.envelope(curves, bs.DEGREES, bs.PENALTY)[0]
    if name == 'env_min2':
        return bs.envelope(curves[1:], bs.DEGREES[1:], bs.PENALTY)[0]
    raise ValueError(name)


def signal(sf):
    A = ds.ALEPH
    return ds.signal_template(A['mass'], A['width'], sf * A['mass'])


def assess(truth, nexp, nb, sig, grid=bs.GRID):
    """All treatments on Asimov data nb * truth (background only) and nb * truth + nexp * sig."""
    nu_b = nb * np.asarray(truth, float)
    cb = bs.degree_curves(nu_b, nexp, sig, grid=grid)
    cs = bs.degree_curves(nu_b + nexp * sig, nexp, sig, grid=grid)
    tab = bs.spurious_table(nu_b, nexp, sig, grid=grid, curves=cb)
    d_old = int(ds.choose_degree(nu_b)[0])
    d_ss = int(bs.choose_degree_spurious(tab))
    row = dict(n_exp=round(float(nexp), 3), n_bkg=round(float(nb), 1), d_old=d_old, d_ss=d_ss,
               spurious_table=tab, methods={})
    for m in METHODS:
        sb = bs.profile_summary(grid, treat_curve(m, cb, d_old, d_ss))
        ss_ = bs.profile_summary(grid, treat_curve(m, cs, d_old, d_ss))
        frac = sb['muhat'] / sb['sigma_up'] if sb['sigma_up'] and sb['sigma_up'] == sb['sigma_up'] else float('nan')
        row['methods'][m] = dict(spur=sb['muhat'], sigma=sb['sigma_up'], spur_over_sigma=round(frac, 4),
                                 ul_sens=sb['ul_sens'], muhat_mu1=ss_['muhat'], z0_mu1=ss_['z0'])
    return row


def task(args):
    tname, truth, sc = args
    t0 = time.time()
    nexp, nb = fc.nexp_nb(sc)
    r = assess(truth, nexp, nb, signal(sc['sf']))
    r.update(truth=tname, scenario=sc['name'], seconds=round(time.time() - t0, 1))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--nbb', type=int, default=1000000)
    ap.add_argument('--bb-seconds', type=float, default=1500)
    ap.add_argument('--seed', type=int, default=20261117)
    ap.add_argument('--minutes', type=float, default=60.0, help='budget for the fits')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    # same seeds and sizes as forecast.py 0.1.1 in dimu-forecast-v2, so the truth is reproduced
    with mp.Pool(a.workers) as pool:
        bb = pool.map(fc.bb_task, [(a.nbb // a.workers, a.seed + 101 + i, a.bb_seconds)
                                   for i in range(a.workers)])
    masses = np.array([m for ms, _ in bb for m in ms])
    gen = [st for _, st in bb]
    print('BB', json.dumps(gen), flush=True)
    truths = fc.truth_shapes(masses if len(masses) else None)
    bw = truths.pop('_bw', None)
    if 'pythia_bb' not in truths:
        print('NO PYTHIA SHAPE: generation failed', flush=True)
        return 2
    np.savetxt(os.path.join(a.out, 'truth_shapes.txt'),
               np.column_stack([ds.CENT] + [truths[k] for k in TRUTHS]),
               header='m_GeV ' + ' '.join(TRUTHS), fmt='%.6e')
    scs = {s['name']: s for s in fc.scen_list('pythia_bb')}
    order = ['S2_9495_r0.8', 'S4_9295_r0.8', 'S1_9495_r1.0', 'S3_9495_r0.6']
    tasks = [(t, truths[t], scs[s]) for s in order for t in TRUTHS]
    deadline = t0 + 60.0 * a.minutes
    res = dict(tool=VERSION, bkgsys=bs.VERSION, forecast=fc.VERSION, kde_bandwidth=bw, bb_generation=gen,
               made_by='MV2 of Munim, Inc. (made with AI agents)', methods=METHODS,
               note='No DELPHI data used. Asimov only.', results=[])
    path = os.path.join(a.out, 'bbspur.jsonl')
    with open(path, 'w') as fo, mp.Pool(a.workers) as pool:
        for r in pool.imap(task, tasks):
            res['results'].append(r)
            fo.write(json.dumps(r) + '\n')
            fo.flush()
            print('ROW %s %s d_old %d d_ss %d | ' % (r['scenario'], r['truth'], r['d_old'], r['d_ss']) +
                  ' | '.join('%s spur %+.3f (%.2f sd) ul %.3f mh1 %.3f' % (
                      m, v['spur'], v['spur_over_sigma'], v['ul_sens'], v['muhat_mu1'])
                      for m, v in r['methods'].items()), flush=True)
            if time.time() > deadline:
                print('BUDGET reached; remaining tasks skipped', flush=True)
                pool.terminate()
                break
    res['wall_s'] = round(time.time() - t0, 1)
    with open(os.path.join(a.out, 'bbspur.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print('SPURIOUS TABLES (pythia_bb):')
    for r in res['results']:
        if r['truth'] == 'pythia_bb':
            print(r['scenario'], json.dumps(r['spurious_table']))
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
