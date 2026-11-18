"""envcast: which background treatment should the DELPHI 30 GeV test use? (PLAN v0.12, 5g)
Written and run BEFORE any DELPHI dimuon mass in the window is seen; no DELPHI data are used.

Uses the eight pseudo-data scenarios of combcast 0.1.0 (C1-C8; same truths, same signal yields)
and compares five background treatments, all computed from the SAME per-degree profile curves
(bkgsys.degree_curves), so differences come only from the treatment:
  old       the pre-registered sideband degree rule of 5b (dimustat.choose_degree), per category
  ss        the spurious-signal rule (lowest degree with |spurious| < 0.2 sigma) applied to the
            TRUE background shape (an oracle: in the real analysis the template is simulation)
  fix3      degree 3 in every category
  env       discrete-profiling envelope over degrees 1-5, penalty 1 per shape parameter
  env_min2  the same envelope over degrees 2-5
Tests: tagged = test A (b-tagged only), untagged, combined = test B (one mu across both).

Part 1, Asimov: for each scenario, category and treatment, the background-only spurious signal,
the expected sensitivity (ul_sens = 95 % one-sided crossing minus mu_hat, about 1.96 sigma), and
mu_hat and Z0 for an injected ALEPH-sized signal (mu = 1).
Part 2, toys (scenario C2, mu = 0 and 1, under a wall-clock budget, written chunk by chunk):
outcomes of tests A and B for each treatment, with the CLs sigma(mu) of each treatment taken
from its background-only Asimov profile.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import math
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import dimustat as ds
import combcast as cc
import bkgsys as bs

TOOL = "mv2 envcast 0.1.0"
METHODS = ('old', 'ss', 'fix3', 'env', 'env_min2')
TOY_GRID = np.round(np.arange(-15, 36) * 0.1, 6)  # mu = -1.5 ... 3.5
TOY_SCEN = 'C2_9495_f1.5'


def method_curve(name, curves, d_old, d_ss):
    """Profile curve (-2 ln L(mu) up to a constant) of one category under a treatment."""
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


def categories(sc):
    b = cc.build(sc)
    return b, {'T': (b['tb'], b['nt']), 'U': (b['ub'], b['nu'])}


def asimov_block(sc):
    b, cats = categories(sc)
    info, prof_b, prof_s = {}, {}, {}
    for c, (nub, nexp) in cats.items():
        cb = bs.degree_curves(nub, nexp, b['sig'])
        cs = bs.degree_curves(nub + nexp * b['sig'], nexp, b['sig'])
        tab = bs.spurious_table(nub, nexp, b['sig'], curves=cb)
        d_old = ds.choose_degree(nub)[0]
        d_ss = bs.choose_degree_spurious(tab)
        env_idx_mu1 = int(bs.envelope(cs)[1][int(np.argmin(np.abs(bs.GRID - 1.0)))])
        info[c] = dict(n_exp=round(nexp, 3), d_old=d_old, d_ss=d_ss, spurious_table=tab,
                       env_degree_at_mu1=bs.DEGREES[env_idx_mu1])
        for m in METHODS:
            prof_b[(c, m)] = method_curve(m, cb, d_old, d_ss)
            prof_s[(c, m)] = method_curve(m, cs, d_old, d_ss)
    res = dict(categories=info, tests={})
    sig_fns = {}
    for m in METHODS:
        for test, cl in (('tagged', ('T',)), ('untagged', ('U',)), ('combined', ('T', 'U'))):
            Eb = sum(prof_b[(c, m)] for c in cl)
            Es = sum(prof_s[(c, m)] for c in cl)
            sb, ss_ = bs.profile_summary(bs.GRID, Eb), bs.profile_summary(bs.GRID, Es)
            res['tests'].setdefault(m, {})[test] = dict(
                spur=sb['muhat'], sigma_bonly=sb['sigma_up'], ul_sens=sb['ul_sens'],
                muhat_mu1=ss_['muhat'], z0_mu1=ss_['z0'], sigma_up_mu1=ss_['sigma_up'],
                sigma_down_mu1=ss_['sigma_down'])
            if test != 'untagged':
                sig_fns[(m, test)] = (bs.GRID.tolist(), Eb.tolist())
        t = res['tests'][m]
        t['ratio_ul_sens_combined_over_tagged'] = round(
            t['combined']['ul_sens'] / t['tagged']['ul_sens'], 4)
    return res, sig_fns


def toy_chunk(args):
    scname, mu, seed, ntoy, deadline = args
    sc = [s for s in cc.SCEN if s['name'] == scname][0]
    b, cats = categories(sc)
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(ntoy):
        if time.time() > deadline:
            break
        row = dict(mu=mu, seed=seed)
        for c, (nub, nexp) in cats.items():
            n = rng.poisson(nub + mu * nexp * b['sig']).astype(float)
            cur = bs.degree_curves(n, nexp, b['sig'], grid=TOY_GRID)
            row[c] = dict(curves=np.round(cur, 6).tolist(), d_old=ds.choose_degree(n)[0])
        rows.append(row)
    return rows


def analyse_toy(row, d_ss, sig_fns):
    out = {}
    curves = {c: np.array(row[c]['curves']) for c in ('T', 'U')}
    for m in METHODS:
        for test, cl in (('tagged', ('T',)), ('combined', ('T', 'U'))):
            E = sum(method_curve(m, curves[c], row[c]['d_old'], d_ss[c]) for c in cl)
            s = bs.profile_summary(TOY_GRID, E)
            ul = bs.cls_upper_limit(TOY_GRID, E, sig_fns[(m, test)])
            if ul == ul and ul < 1.0:
                oc = 'EXCLUDED'
            elif s['q1'] < 1.0 and s['z0'] >= 2.0:
                oc = 'COMPATIBLE'
            else:
                oc = 'INCONCLUSIVE'
            out[m + '|' + test] = dict(muhat=s['muhat'], z0=s['z0'], ul=round(ul, 4), outcome=oc)
    return out


def summarise(results):
    summ = {}
    for mu in sorted(set(r['mu'] for r in results)):
        rs = [r for r in results if r['mu'] == mu]
        for key in rs[0]['res']:
            v = [r['res'][key] for r in rs]
            mh = np.array([x['muhat'] for x in v])
            ul = np.array([x['ul'] for x in v], float)
            d = dict(n=len(v), muhat_mean=round(float(mh.mean()), 4),
                     muhat_std=round(float(mh.std()), 4),
                     ul_median=round(float(np.nanmedian(ul)), 4) if np.any(ul == ul) else None,
                     z0_median=round(float(np.median([x['z0'] for x in v])), 4))
            for oc in ('EXCLUDED', 'COMPATIBLE', 'INCONCLUSIVE'):
                d['p_' + oc] = round(sum(1 for x in v if x['outcome'] == oc) / len(v), 4)
            summ.setdefault('mu=%g' % mu, {})[key] = d
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--ntoy', type=int, default=200, help='per mu value')
    ap.add_argument('--toy-minutes', type=float, default=75.0)
    ap.add_argument('--seed', type=int, default=20261118)
    a = ap.parse_args()
    out = os.path.join(a.out, 'envcast')
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    res = dict(tool=TOOL, bkgsys=bs.VERSION, made_by='MV2 of Munim, Inc. (made with AI agents)',
               methods=METHODS, penalty=bs.PENALTY, max_frac=bs.MAX_FRAC,
               note='No DELPHI data used. Truths and yields of combcast 0.1.0.', asimov={})
    sig_store = {}
    for sc in cc.SCEN:
        r, fns = asimov_block(sc)
        res['asimov'][sc['name']] = r
        sig_store[sc['name']] = fns
        print('ASIMOV', sc['name'], json.dumps(r), flush=True)
        with open(os.path.join(out, 'asimov.json'), 'w') as f:
            json.dump(res['asimov'], f, indent=1)
    res['t_asimov_s'] = round(time.time() - t0, 1)

    print('\nASIMOV TABLE (spur = background-only mu_hat; ul = ul_sens; mh1 = mu_hat at mu = 1)')
    for name, r in res['asimov'].items():
        for m in METHODS:
            t = r['tests'][m]
            print('%-24s %-8s | A spur %+.3f ul %.3f mh1 %.3f | U spur %+.3f ul %.3f mh1 %.3f | '
                  'B spur %+.3f ul %.3f mh1 %.3f z0 %.2f | B/A %.3f' % (
                      name, m, t['tagged']['spur'], t['tagged']['ul_sens'], t['tagged']['muhat_mu1'],
                      t['untagged']['spur'], t['untagged']['ul_sens'], t['untagged']['muhat_mu1'],
                      t['combined']['spur'], t['combined']['ul_sens'], t['combined']['muhat_mu1'],
                      t['combined']['z0_mu1'], t['ratio_ul_sens_combined_over_tagged']), flush=True)
        print('%-24s degrees: T old %d ss %d env@1 %d | U old %d ss %d env@1 %d' % (
            name, r['categories']['T']['d_old'], r['categories']['T']['d_ss'],
            r['categories']['T']['env_degree_at_mu1'], r['categories']['U']['d_old'],
            r['categories']['U']['d_ss'], r['categories']['U']['env_degree_at_mu1']), flush=True)

    # toys
    fns = {k: bs.sigma_fn_from_asimov(np.array(g), np.array(E))
           for k, (g, E) in sig_store[TOY_SCEN].items()}
    cat = res['asimov'][TOY_SCEN]['categories']
    d_ss = {c: cat[c]['d_ss'] for c in ('T', 'U')}
    deadline = time.time() + 60.0 * a.toy_minutes
    tasks, k = [], 0
    chunk = 10
    for i in range(0, a.ntoy, chunk):
        for mu in (0.0, 1.0):
            tasks.append((TOY_SCEN, mu, a.seed + 1000 + k, min(chunk, a.ntoy - i), deadline))
            k += 1
    results = []
    path = os.path.join(out, 'toys.jsonl')
    with open(path, 'w') as fo, mp.Pool(a.workers) as pool:
        for rows in pool.imap_unordered(toy_chunk, tasks):
            for row in rows:
                rr = dict(mu=row['mu'], seed=row['seed'], d_old=[row['T']['d_old'], row['U']['d_old']],
                          res=analyse_toy(row, d_ss, fns))
                results.append(rr)
                fo.write(json.dumps(rr) + '\n')
            fo.flush()
    res['toys'] = summarise(results) if results else {}
    res['toy_scenario'] = TOY_SCEN
    res['wall_s'] = round(time.time() - t0, 1)
    with open(os.path.join(out, 'envcast.json'), 'w') as f:
        json.dump(res, f, indent=1)

    print('\nTOYS %s (n per mu shown)' % TOY_SCEN)
    for mukey, d in res['toys'].items():
        for key, v in d.items():
            print('TOYS %s %-20s n %d muhat %.3f +- %.3f | P(excl) %.3f P(compat) %.3f | ul_med %s' % (
                mukey, key, v['n'], v['muhat_mean'], v['muhat_std'], v['p_EXCLUDED'],
                v['p_COMPATIBLE'], v['ul_median']))
    print('SUMMARY_JSON_BEGIN')
    print(json.dumps({k: v for k, v in res.items() if k != 'asimov'}, indent=1))
    print('SUMMARY_JSON_END')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
