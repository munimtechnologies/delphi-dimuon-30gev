"""envtoys: criterion (b) of PLAN amendment 0.12 (section 5g) with enough pseudo-experiments.
Written and run BEFORE any DELPHI dimuon mass in the 26-35 GeV window is seen; no DELPHI data used.

Why (job dimu-envcast-v1, graded in PLAN amendment 0.14): on noise-free pseudo-data only `fix3`
(log-Legendre degree 3 in every category) passes criterion (a) among the eligible background
treatments; the envelope `env` fails it in scenario C6 (test B spurious signal 0.29 sigma). The
toy part of envcast, which tests criterion (b), finished only 10-11 toys per signal strength in its
75-minute budget, because it fitted all five degrees in every toy. This module fits only what is
needed: degree 3 in every toy, plus the sideband-rule degree (`old`, a reference for expectation
K6) in the toys with a true ALEPH-sized signal (mu = 1).

Same scenario (combcast C2_9495_f1.5), same Poisson draws per toy (T then U), same mu grid, same
CLs sigma(mu) from the background-only Asimov profile, same outcome rules as envcast; agreement of
the outcome code with envcast.analyse_toy is a unit test (one definition).

Criterion (b): P(EXCLUDED | mu = 1) <= 0.07 for test A (b-tagged only) and test B (combined).
Called only with at least N_MIN toys at mu = 1; otherwise UNDETERMINED.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np
from scipy import stats

import dimustat as ds
import combcast as cc
import bkgsys as bs
import envcast as ec

TOOL = "mv2 envtoys 0.1.0"
TOY_SCEN = ec.TOY_SCEN
TOY_GRID = ec.TOY_GRID
FIX = 3
P_MAX = 0.07
N_MIN = 150
TESTS = (('tagged', ('T',)), ('combined', ('T', 'U')))


def scenario(name=TOY_SCEN):
    return [s for s in cc.SCEN if s['name'] == name][0]


def outcome(E, grid, sig_fn):
    """Outcome of one test from its profile curve; the rules of envcast.analyse_toy."""
    s = bs.profile_summary(grid, E)
    ul = bs.cls_upper_limit(grid, E, sig_fn)
    if ul == ul and ul < 1.0:
        oc = 'EXCLUDED'
    elif s['q1'] < 1.0 and s['z0'] >= 2.0:
        oc = 'COMPATIBLE'
    else:
        oc = 'INCONCLUSIVE'
    return dict(muhat=s['muhat'], z0=s['z0'], ul=round(ul, 4), outcome=oc)


def analyse(curves, d_old, sig_fns, methods, grid=TOY_GRID):
    """curves: {'T': array (5, len(grid)), 'U': ...} with nan rows for degrees not fitted."""
    out = {}
    for m in methods:
        for test, cl in TESTS:
            E = sum(ec.method_curve(m, np.asarray(curves[c]), d_old[c], 0) for c in cl)
            out[m + '|' + test] = outcome(E, grid, sig_fns[(m, test)])
    return out


def partial_curves(n, nexp, sig, degrees, grid=TOY_GRID):
    """Curves for the listed degrees only, placed in a (5, len(grid)) array (other rows nan)."""
    full = np.full((len(bs.DEGREES), len(grid)), np.nan)
    ds_ = sorted(set(int(d) for d in degrees))
    cur = bs.degree_curves(n, nexp, sig, degrees=ds_, grid=grid)
    for j, d in enumerate(ds_):
        full[d - 1] = cur[j]
    return full


def sigma_fns(sig_data):
    """sigma(mu) functions from {(method, test): (grid, E_asimov_bonly)}. Built inside each worker:
    the closures of bkgsys.sigma_fn_from_asimov cannot be pickled, the arrays can."""
    return {k: bs.sigma_fn_from_asimov(np.array(g), np.array(E)) for k, (g, E) in sig_data.items()}


def toy_chunk(args):
    scname, mu, seed, ntoy, deadline, with_old, sig_data, grid = args
    sig_fns = sigma_fns(sig_data)
    b, cats = ec.categories(scenario(scname))
    rng = np.random.default_rng(seed)
    methods = ('fix3', 'old') if with_old else ('fix3',)
    rows = []
    for k in range(ntoy):
        if time.time() > deadline:
            break
        t0 = time.time()
        curves, d_old = {}, {}
        for c, (nub, nexp) in cats.items():
            n = rng.poisson(nub + mu * nexp * b['sig']).astype(float)
            d_old[c] = int(ds.choose_degree(n)[0])
            degs = (FIX, d_old[c]) if with_old else (FIX,)
            curves[c] = partial_curves(n, nexp, b['sig'], degs, grid=grid)
        rows.append(dict(mu=mu, seed=seed, k=k, d_old=[d_old['T'], d_old['U']],
                         res=analyse(curves, d_old, sig_fns, methods, grid=grid),
                         sec=round(time.time() - t0, 1)))
    return rows


def clopper_pearson(k, n, cl=0.95):
    """Two-sided Clopper-Pearson interval for a binomial fraction k / n."""
    if n == 0:
        return (float('nan'), float('nan'))
    a = 1.0 - cl
    lo = 0.0 if k == 0 else float(stats.beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - a / 2, k + 1, n - k))
    return (round(lo, 4), round(hi, 4))


def summarise(results):
    summ = {}
    for mu in sorted(set(r['mu'] for r in results)):
        rs = [r for r in results if r['mu'] == mu]
        keys = sorted(set(k for r in rs for k in r['res']))
        for key in keys:
            v = [r['res'][key] for r in rs if key in r['res']]
            mh = np.array([x['muhat'] for x in v])
            ul = np.array([x['ul'] for x in v], float)
            d = dict(n=len(v), muhat_mean=round(float(mh.mean()), 4),
                     muhat_std=round(float(mh.std(ddof=1)), 4) if len(v) > 1 else None,
                     ul_median=round(float(np.nanmedian(ul)), 4) if np.any(ul == ul) else None,
                     z0_median=round(float(np.median([x['z0'] for x in v])), 4))
            for oc in ('EXCLUDED', 'COMPATIBLE', 'INCONCLUSIVE'):
                k = sum(1 for x in v if x['outcome'] == oc)
                d['n_' + oc] = k
                d['p_' + oc] = round(k / len(v), 4)
            d['p_EXCLUDED_cp95'] = clopper_pearson(d['n_EXCLUDED'], len(v))
            summ.setdefault('mu=%g' % mu, {})[key] = d
    return summ


def criterion_b(summ, method='fix3', p_max=P_MAX, n_min=N_MIN):
    """PASS / FAIL / UNDETERMINED for criterion (b) of amendment 0.12."""
    d = summ.get('mu=1', {})
    rows = [d.get(method + '|' + t) for t, _ in TESTS]
    if any(r is None or r['n'] < n_min for r in rows):
        return 'UNDETERMINED'
    return 'PASS' if all(r['p_EXCLUDED'] <= p_max for r in rows) else 'FAIL'


def task_list(ntoy1, ntoy0, chunk, seed):
    """Chunks in the order 1, 1, 0, 1, 1, 0, ... so mu = 1 (criterion b) fills first."""
    c1 = [(1.0, min(chunk, ntoy1 - i)) for i in range(0, ntoy1, chunk)]
    c0 = [(0.0, min(chunk, ntoy0 - i)) for i in range(0, ntoy0, chunk)]
    out = []
    while c1 or c0:
        for _ in range(2):
            if c1:
                out.append(c1.pop(0))
        if c0:
            out.append(c0.pop(0))
    return [(mu, n, seed + 1000 + k) for k, (mu, n) in enumerate(out)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--ntoy1', type=int, default=200, help='toys with mu = 1')
    ap.add_argument('--ntoy0', type=int, default=120, help='toys with mu = 0')
    ap.add_argument('--chunk', type=int, default=5)
    ap.add_argument('--minutes', type=float, default=200.0, help='wall-clock budget for toys')
    ap.add_argument('--seed', type=int, default=20261119)
    a = ap.parse_args()
    out = os.path.join(a.out, 'envtoys')
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    deadline = t0 + 60.0 * a.minutes

    # sigma(mu) of each treatment from its background-only Asimov profile (as envcast)
    asim, sig_store = ec.asimov_block(scenario())
    cat = asim['categories']
    for m in ('fix3', 'old'):
        t = asim['tests'][m]
        print('ASIMOV %s %-5s | A spur %+.4f ul %.4f mh1 %.4f | B spur %+.4f ul %.4f mh1 %.4f' % (
            TOY_SCEN, m, t['tagged']['spur'], t['tagged']['ul_sens'], t['tagged']['muhat_mu1'],
            t['combined']['spur'], t['combined']['ul_sens'], t['combined']['muhat_mu1']), flush=True)
    print('ASIMOV degrees: T old %d | U old %d (sec %.0f)' % (
        cat['T']['d_old'], cat['U']['d_old'], time.time() - t0), flush=True)
    with open(os.path.join(out, 'asimov.json'), 'w') as f:
        json.dump(asim, f, indent=1)
    sig_data = {k: v for k, v in sig_store.items() if k[0] in ('fix3', 'old')}

    tasks = [(TOY_SCEN, mu, sd, n, deadline, mu == 1.0, sig_data, TOY_GRID)
             for mu, n, sd in task_list(a.ntoy1, a.ntoy0, a.chunk, a.seed)]
    results = []
    path = os.path.join(out, 'toys.jsonl')
    with open(path, 'w') as fo, mp.Pool(a.workers) as pool:
        for rows in pool.imap(toy_chunk, tasks):
            for row in rows:
                results.append(row)
                fo.write(json.dumps(row) + '\n')
            fo.flush()
            if rows:
                n1 = sum(1 for r in results if r['mu'] == 1.0)
                n0 = len(results) - n1
                print('PROGRESS mu1 %d mu0 %d t %.0f s' % (n1, n0, time.time() - t0), flush=True)
    summ = summarise(results) if results else {}
    res = dict(tool=TOOL, envcast=ec.TOOL, bkgsys=bs.VERSION,
               made_by='MV2 of Munim, Inc. (made with AI agents)', scenario=TOY_SCEN,
               note='No DELPHI data used. Truths and yields of combcast 0.1.0.',
               p_max=P_MAX, n_min=N_MIN, toys=summ,
               criterion_b_fix3=criterion_b(summ, 'fix3'),
               criterion_b_old=criterion_b(summ, 'old'),
               mean_sec_per_toy=round(float(np.mean([r['sec'] for r in results])), 1) if results else None,
               wall_s=round(time.time() - t0, 1))
    with open(os.path.join(out, 'envtoys.json'), 'w') as f:
        json.dump(res, f, indent=1)
    print('\nTOYS %s' % TOY_SCEN)
    for mukey, d in summ.items():
        for key, v in d.items():
            print('TOYS %s %-14s n %d muhat %.3f +- %s | P(excl) %.3f %s P(compat) %.3f | ul_med %s' % (
                mukey, key, v['n'], v['muhat_mean'], v['muhat_std'], v['p_EXCLUDED'],
                v['p_EXCLUDED_cp95'], v['p_COMPATIBLE'], v['ul_median']), flush=True)
    print('CRITERION_B fix3 %s | old %s' % (res['criterion_b_fix3'], res['criterion_b_old']))
    print('SUMMARY_JSON_BEGIN')
    print(json.dumps(res, indent=1))
    print('SUMMARY_JSON_END')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
