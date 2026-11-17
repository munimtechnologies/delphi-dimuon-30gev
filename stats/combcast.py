"""combcast: how much does the all-flavour test of PLAN v0.9 (section 5e) gain over the
b-tagged-only replica of ALEPH's analysis? Written and run BEFORE any DELPHI dimuon mass in the
window is seen; no DELPHI data are used.

Categories: T = opposite-sign mumu, b-tagged (dimusel os_mumu_btag); U = opposite-sign mumu,
not b-tagged (os_mumu_untagged; the complement of T, so the two are disjoint).
At mu = 1 (ALEPH-sized): N_T = 32.31 k r (the N_exp of plan section 5c), and
N_U = N_T (1 - eps) / eps (rule of 5e with rho = 1), eps = 0.38.
Background: B_T = 1457.06 k r with a smooth Z -> b bbar shape; B_U = B_T (1 - eps) / eps times
f_u, where the b bbar part keeps T's shape and the extra (f_u - 1) part (charm, light-quark
fakes) has its own, softer shape. k = DELPHI hadronic Z / ALEPH's 1.9M (0.84 for 1994-95,
1.6 for 1992-95), r = DELPHI / ALEPH selection efficiency.

Reports, per scenario, Asimov medians for the tagged-only, untagged-only and combined tests,
and for the two main scenarios paired toys (the same pseudo-data analysed both ways with the
full pre-registered procedure, dimucomb.analyse).

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
import dimucomb as dc

A = ds.ALEPH
EPS = dc.ALEPH_EPS_B
TOOL = "mv2 combcast 0.1.0"


def shape(name):
    x = ds.CENT
    if name == 'powerlaw1':
        w = x ** -1.0
    elif name == 'powerlaw3':
        w = x ** -3.0
    elif name == 'exp9':
        w = np.exp(-x / 9.0)
    else:
        raise ValueError(name)
    return w / w.sum()


SCEN = [
    dict(name='C1_9495_f1.0', k=0.84, r=0.8, f=1.0, bb='powerlaw1', nonb='powerlaw3', sf=math.sqrt(6e-4)),
    dict(name='C2_9495_f1.5', k=0.84, r=0.8, f=1.5, bb='powerlaw1', nonb='powerlaw3', sf=math.sqrt(6e-4)),
    dict(name='C3_9495_f2.0', k=0.84, r=0.8, f=2.0, bb='powerlaw1', nonb='powerlaw3', sf=math.sqrt(6e-4)),
    dict(name='C4_9495_f3.0', k=0.84, r=0.8, f=3.0, bb='powerlaw1', nonb='powerlaw3', sf=math.sqrt(6e-4)),
    dict(name='C5_9295_f1.5', k=1.6, r=0.8, f=1.5, bb='powerlaw1', nonb='powerlaw3', sf=math.sqrt(6e-4)),
    dict(name='C6_9495_f1.5_bbexp9', k=0.84, r=0.8, f=1.5, bb='exp9', nonb='powerlaw3', sf=math.sqrt(6e-4)),
    dict(name='C7_9495_f1.5_nonb_same', k=0.84, r=0.8, f=1.5, bb='powerlaw1', nonb='powerlaw1', sf=math.sqrt(6e-4)),
    dict(name='C8_9495_f1.5_res1.2pc', k=0.84, r=0.8, f=1.5, bb='powerlaw1', nonb='powerlaw3', sf=0.012),
]
TOY_SCEN = ('C2_9495_f1.5', 'C5_9295_f1.5')


def build(sc):
    """Truth backgrounds, signal yields and template for one scenario."""
    nt = A['n_sig'] * sc['k'] * sc['r']
    nu = dc.nexp_untagged(nt, EPS)
    bt = A['n_bkg'] * sc['k'] * sc['r']
    bu_bb = bt * (1.0 - EPS) / EPS
    tb = bt * shape(sc['bb'])
    ub = bu_bb * shape(sc['bb']) + (sc['f'] - 1.0) * bu_bb * shape(sc['nonb'])
    sig = ds.signal_template(A['mass'], A['width'], sc['sf'] * A['mass'])
    return dict(nt=nt, nu=nu, tb=tb, ub=ub, sig=sig)


def tests_of(b):
    return {'tagged': ([b['tb']], [b['nt']]),
            'untagged': ([b['ub']], [b['nu']]),
            'combined': ([b['tb'], b['ub']], [b['nt'], b['nu']])}


def asimov_block(sc):
    b = build(sc)
    win = (ds.CENT > A['mass'] - 2.5) & (ds.CENT < A['mass'] + 2.5)
    out = dict(n_exp_tagged=round(b['nt'], 2), n_exp_untagged=round(b['nu'], 2),
               bkg_tagged_15_50=round(float(b['tb'].sum()), 1),
               bkg_untagged_15_50=round(float(b['ub'].sum()), 1),
               bkg_tagged_window_pm2p5=round(float(b['tb'][win].sum()), 1),
               bkg_untagged_window_pm2p5=round(float(b['ub'][win].sum()), 1))
    for name, (nus, nexp) in tests_of(b).items():
        degs = [ds.choose_degree(n)[0] for n in nus]
        J = dc.Joint(nexp, degs, sigs=[b['sig']] * len(nus))
        f, tab = dc.make_sigma_fn(J, nus)
        bonly, free = dc.fits_free_and_bonly(J, nus)
        ul = dc.upper_limit(J, nus, f, free, bonly)
        q0, muhat, _, _ = dc.q0(J, [n + x * b['sig'] for n, x in zip(nus, nexp)])
        out[name] = dict(degrees=degs, sigma_mu_at_1=round(f(1.0), 4), median_ul_mu=round(ul, 3),
                         asimov_z0_mu1=round(math.sqrt(q0), 3), asimov_muhat_mu1=round(muhat, 4))
    out['ratio_ul_combined_over_tagged'] = round(out['combined']['median_ul_mu'] /
                                                 out['tagged']['median_ul_mu'], 3)
    return out


def toy_task(args):
    sc, mu, ntoy, seed = args
    b = build(sc)
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(ntoy):
        nt = rng.poisson(b['tb'] + mu * b['nt'] * b['sig']).astype(float)
        nu = rng.poisson(b['ub'] + mu * b['nu'] * b['sig']).astype(float)
        row = {}
        for name, ns, nexp in (('tagged', [nt], [b['nt']]),
                               ('combined', [nt, nu], [b['nt'], b['nu']])):
            try:
                row[name] = dc.analyse(ns, nexp, sigs=[b['sig']] * len(ns))
            except Exception as e:  # count failures, keep going
                row[name] = dict(error=repr(e))
        rows.append(row)
    return sc['name'], mu, rows


def summarise(rows, name):
    ok = [r[name] for r in rows if 'error' not in r[name]]
    s = dict(n=len(rows), n_failed=len(rows) - len(ok))
    if not ok:
        return s
    for oc in ('EXCLUDED', 'COMPATIBLE', 'INCONCLUSIVE'):
        s['p_' + oc] = round(sum(1 for r in ok if r['outcome'] == oc) / len(ok), 4)
    ul = np.array([r['ul'] for r in ok])
    z0 = np.array([r['z0'] for r in ok])
    mh = np.array([r['muhat'] for r in ok])
    s.update(ul_median=round(float(np.median(ul)), 3),
             ul_16_84=[round(float(np.percentile(ul, 16)), 3), round(float(np.percentile(ul, 84)), 3)],
             z0_median=round(float(np.median(z0)), 3), p_z0_ge2=round(float(np.mean(z0 >= 2)), 4),
             p_z0_ge3=round(float(np.mean(z0 >= 3)), 4),
             muhat_mean=round(float(np.mean(mh)), 4), muhat_std=round(float(np.std(mh)), 4))
    return s


def paired(rows):
    both = [r for r in rows if 'error' not in r['tagged'] and 'error' not in r['combined']]
    if not both:
        return {}
    t = np.array([r['tagged']['outcome'] == 'EXCLUDED' for r in both])
    c = np.array([r['combined']['outcome'] == 'EXCLUDED' for r in both])
    return dict(n=len(both), excl_both=int(np.sum(t & c)), excl_tagged_only=int(np.sum(t & ~c)),
                excl_combined_only=int(np.sum(~t & c)), excl_neither=int(np.sum(~t & ~c)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--ntoy', type=int, default=200)
    ap.add_argument('--seed', type=int, default=20261118)
    a = ap.parse_args()
    out = os.path.join(a.out, 'combcast')
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    res = dict(tool=TOOL, dimucomb=dc.VERSION, made_by='MV2 of Munim, Inc. (made with AI agents)',
               eps_b=EPS, aleph_input=A, note='No DELPHI data used. Smooth background shapes.')
    res['asimov'] = {}
    for sc in SCEN:
        res['asimov'][sc['name']] = asimov_block(sc)
        print('ASIMOV', sc['name'], json.dumps(res['asimov'][sc['name']]), flush=True)
    res['t_asimov_s'] = round(time.time() - t0, 1)

    tasks, k = [], 0
    chunk = max(1, a.ntoy // 4)
    for sc in SCEN:
        if sc['name'] not in TOY_SCEN:
            continue
        for mu in (0.0, 1.0):
            left = a.ntoy
            while left > 0:
                n = min(chunk, left)
                tasks.append((sc, mu, n, a.seed + 1000 + k))
                left -= n
                k += 1
    with mp.Pool(a.workers) as pool:
        tr = pool.map(toy_task, tasks, chunksize=1)
    allrows = {}
    for name, mu, rows in tr:
        allrows.setdefault(name, {}).setdefault(str(mu), []).extend(rows)
    res['toys'] = {name: {mu: dict(tagged=summarise(r, 'tagged'), combined=summarise(r, 'combined'),
                                   paired=paired(r))
                          for mu, r in d.items()} for name, d in allrows.items()}
    with open(os.path.join(out, 'toys.json'), 'w') as f:
        json.dump(allrows, f)
    res['wall_s'] = round(time.time() - t0, 1)
    with open(os.path.join(out, 'combcast.json'), 'w') as f:
        json.dump(res, f, indent=1)

    print('\nSCENARIO                     N_T   N_U   B_T(+-2.5)  B_U(+-2.5) | medUL tag  unt  comb  ratio | Z0 tag  comb')
    for sc in SCEN:
        r = res['asimov'][sc['name']]
        print('%-27s %5.1f %5.1f %9.1f %11.1f | %8.3f %5.3f %5.3f %6.3f | %6.3f %5.3f' % (
            sc['name'], r['n_exp_tagged'], r['n_exp_untagged'], r['bkg_tagged_window_pm2p5'],
            r['bkg_untagged_window_pm2p5'], r['tagged']['median_ul_mu'], r['untagged']['median_ul_mu'],
            r['combined']['median_ul_mu'], r['ratio_ul_combined_over_tagged'],
            r['tagged']['asimov_z0_mu1'], r['combined']['asimov_z0_mu1']))
    for name, d in res['toys'].items():
        for mu, v in d.items():
            print('TOYS %s mu=%s tagged P(excl)=%s comb P(excl)=%s | tagged P(compat)=%s comb P(compat)=%s | paired %s' % (
                name, mu, v['tagged'].get('p_EXCLUDED'), v['combined'].get('p_EXCLUDED'),
                v['tagged'].get('p_COMPATIBLE'), v['combined'].get('p_COMPATIBLE'), json.dumps(v['paired'])))
    print('SUMMARY_JSON_BEGIN')
    print(json.dumps(res, indent=1))
    print('SUMMARY_JSON_END')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
