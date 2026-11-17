"""forecast: how likely is a DELPHI LEP1 analysis to exclude, or to confirm, an ALEPH-sized
30 GeV dimuon signal? Written and run BEFORE any DELPHI dimuon mass in the window is seen.

For each scenario (DELPHI hadronic-Z count relative to ALEPH's 1.9M = k, DELPHI efficiency
relative to ALEPH's = r, mass resolution), background-only and signal toys are drawn from a
generator-level Z -> b bbar opposite-sign dimuon shape (bbshape.py), scaled to ALEPH's fitted
background (1457 events in 15-50 GeV) times k*r. Each toy is analysed with exactly the
pre-registered procedure of PLAN v0.4 section 5:
  1. background degree chosen on the sidebands (dimustat.choose_degree);
  2. fixed-hypothesis fit (m = 30.40, Gamma = 1.78 GeV), signal yield in units of
     N_exp = 32.31 * k * r;
  3. outcomes: EXCLUDED (95 % CLs upper limit below N_exp), COMPATIBLE (mu = 1 inside the 68 %
     profile-likelihood interval AND background-only rejected at Z0 >= 2), INCONCLUSIVE (else).
Also: Asimov medians, a spurious-signal table (bias of each background degree on the
generator shape), and look-elsewhere toys for the 15-50 GeV free-mass scan.

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
from scipy import stats

import dimustat as ds

A = ds.ALEPH
MUS = (0.0, 0.66, 1.0)  # 0.66 = ALEPH's yield minus one standard deviation (21.4 / 32.3)


def truth_shapes(bb_masses):
    """Background truth shapes (bin probabilities over 15-50 GeV)."""
    out = {}
    if bb_masses is not None and len(bb_masses) >= 500:
        p, bw = __import__('bbshape').kde_probs(bb_masses, ds.CENT)
        out['pythia_bb'] = p
        out['_bw'] = bw
        t = 2.0 * (np.log(ds.CENT) - math.log(ds.LO)) / (math.log(ds.HI) - math.log(ds.LO)) - 1.0
        q = p * (1.0 + 0.3 * t)
        out['pythia_bb_tilt'] = q / q.sum()
    w = np.exp(-3.0 * np.log(ds.CENT))
    out['powerlaw3'] = w / w.sum()
    w = np.exp(-ds.CENT / 9.0)
    out['exp9'] = w / w.sum()
    return out


def scen_list(main_truth):
    return [
        dict(name='S1_9495_r1.0', k=0.84, r=1.0, sf=math.sqrt(6e-4), truth=main_truth),
        dict(name='S2_9495_r0.8', k=0.84, r=0.8, sf=math.sqrt(6e-4), truth=main_truth),
        dict(name='S3_9495_r0.6', k=0.84, r=0.6, sf=math.sqrt(6e-4), truth=main_truth),
        dict(name='S4_9295_r0.8', k=1.6, r=0.8, sf=math.sqrt(6e-4), truth=main_truth),
        dict(name='S5_9495_r0.8_res1.2pc', k=0.84, r=0.8, sf=0.012, truth=main_truth),
        dict(name='S6_9495_r0.8_altshape', k=0.84, r=0.8, sf=math.sqrt(6e-4), truth='exp9'),
    ]


def nexp_nb(sc):
    return A['n_sig'] * sc['k'] * sc['r'], A['n_bkg'] * sc['k'] * sc['r']


def analyse(n, sig, nexp, sigma_fns):
    """The pre-registered procedure on one histogram. sigma_fns: degree -> sigma(mu) or None."""
    d, _ = ds.choose_degree(n)
    md = ds.Model(d, sig=sig)
    bonly, free = ds.fits_free_and_bonly(md, n)
    q0, nshat, _, _ = ds.q0(md, n, cache=(bonly, free))
    z0 = math.sqrt(q0)
    nll1 = ds.fit(md, n, fix_ns=nexp, init=free[1])[0]
    q1 = max(2.0 * (nll1 - free[0]), 0.0)
    if sigma_fns.get(d) is None:
        return dict(d=d, muhat=nshat / nexp, z0=z0, q1=q1, ul=float('nan'), outcome='?')
    ul = ds.upper_limit(md, n, sigma_fns[d], free, bonly) / nexp
    if ul < 1.0:
        oc = 'EXCLUDED'
    elif q1 < 1.0 and z0 >= 2.0:
        oc = 'COMPATIBLE'
    else:
        oc = 'INCONCLUSIVE'
    return dict(d=d, muhat=nshat / nexp, z0=z0, q1=q1, ul=ul, outcome=oc)


def build_sigma_fns(nu_b, sig, nexp, degrees=(1, 2, 3, 4, 5)):
    fns, tab = {}, {}
    for d in degrees:
        md = ds.Model(d, sig=sig)
        f, t = ds.make_sigma_fn(md, nu_b, [nexp * x for x in (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)])
        fns[d] = f
        tab[d] = t
    return fns, tab


def toy_task(args):
    sc, truth, mu, ntoy, seed = args
    nexp, nb = nexp_nb(sc)
    sig = ds.signal_template(A['mass'], A['width'], sc['sf'] * A['mass'])
    nu_b = nb * truth
    fns, _ = build_sigma_fns(nu_b, sig, nexp)
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(ntoy):
        n = rng.poisson(nu_b + mu * nexp * sig).astype(float)
        try:
            r = analyse(n, sig, nexp, fns)
        except Exception as e:  # keep going; count failures
            r = dict(error=repr(e))
        rows.append(r)
    return sc['name'], mu, rows


def lee_task(args):
    sc, truth, ntoy, seed, masses = args
    nexp, nb = nexp_nb(sc)
    nu_b = nb * truth
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(ntoy):
        n = rng.poisson(nu_b).astype(float)
        d, _ = ds.choose_degree(n)
        z = ds.mass_scan(n, d, masses, A['width'], sc['sf'])
        # upcrossings of Z = 1 and Z = 2 (Gross-Vitells)
        up1 = int(np.sum((z[1:] >= 1.0) & (z[:-1] < 1.0)))
        up2 = int(np.sum((z[1:] >= 2.0) & (z[:-1] < 2.0)))
        out.append(dict(zmax=float(z.max()), mmax=float(masses[int(np.argmax(z))]), up1=up1,
                        up2=up2, d=d))
    return out


def summarise_toys(rows):
    ok = [r for r in rows if 'error' not in r]
    s = dict(n=len(rows), n_failed=len(rows) - len(ok))
    if not ok:
        return s
    for oc in ('EXCLUDED', 'COMPATIBLE', 'INCONCLUSIVE'):
        s['p_' + oc] = round(sum(1 for r in ok if r['outcome'] == oc) / len(ok), 4)
    ul = np.array([r['ul'] for r in ok])
    z0 = np.array([r['z0'] for r in ok])
    mu = np.array([r['muhat'] for r in ok])
    s.update(ul_median=round(float(np.nanmedian(ul)), 3),
             ul_16_84=[round(float(np.nanpercentile(ul, 16)), 3), round(float(np.nanpercentile(ul, 84)), 3)],
             z0_median=round(float(np.median(z0)), 3),
             p_z0_ge2=round(float(np.mean(z0 >= 2)), 4), p_z0_ge3=round(float(np.mean(z0 >= 3)), 4),
             muhat_mean=round(float(np.mean(mu)), 4), muhat_std=round(float(np.std(mu)), 4),
             degree_counts={str(d): int(sum(1 for r in ok if r['d'] == d)) for d in range(1, 6)})
    return s


def asimov_block(sc, truth):
    nexp, nb = nexp_nb(sc)
    sig = ds.signal_template(A['mass'], A['width'], sc['sf'] * A['mass'])
    nu_b = nb * truth
    d, _ = ds.choose_degree(nu_b)
    md =ds.Model(d, sig=sig)
    f, tab = ds.make_sigma_fn(md, nu_b, [nexp * x for x in (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)])
    bonly, free = ds.fits_free_and_bonly(md, nu_b)
    ul = ds.upper_limit(md, nu_b, f, free, bonly) / nexp
    nu_s = nu_b + nexp * sig
    q0, nshat, _, _ = ds.q0(md, nu_s)
    win = (ds.CENT > A['mass'] - 2.5) & (ds.CENT < A['mass'] + 2.5)
    return dict(n_exp=round(nexp, 2), n_bkg_15_50=round(nb, 1),
                n_bkg_window_pm2p5=round(float(nu_b[win].sum()), 1),
                sig_frac_in_window_pm2p5=round(float(sig[win].sum()), 3),
                asimov_degree=d, sigma_nexp_units=round(f(nexp) / nexp, 4),
                median_ul_nexp_units=round(ul, 3), asimov_z0_if_aleph_sized=round(math.sqrt(q0), 3),
                asimov_muhat=round(nshat / nexp, 4))


def spurious_table(truths, sc):
    """Fit Asimov background-only truth with S+B for degree 1..5: fitted n_s / sigma_stat."""
    nexp, nb = nexp_nb(sc)
    sig = ds.signal_template(A['mass'], A['width'], sc['sf'] * A['mass'])
    out = {}
    for name, tr in truths.items():
        if name.startswith('_'):
            continue
        nu_b = nb * tr
        row = {}
        for d in (1, 2, 3, 4, 5):
            md = ds.Model(d, sig=sig)
            bonly, free = ds.fits_free_and_bonly(md, nu_b)
            s = ds.asimov_sigma(md, nu_b, nexp)
            row[str(d)] = dict(nshat=round(float(free[1][0]), 3), over_sigma=round(float(free[1][0]) / s, 3),
                               over_nexp=round(float(free[1][0]) / nexp, 3),
                               chi2_bonly_vs_truth=round(float(2 * bonly[0] - 2 * _sat(nu_b)), 3))
        out[name] = row
    return out


def _sat(n):
    m = n > 0
    return float(np.sum(n[m]) - np.sum(n[m] * np.log(n[m])))


def bb_task(args):
    n, seed, maxs = args
    import bbshape
    try:
        m, st = bbshape.generate(n, seed, maxs)
        return m.tolist(), st
    except Exception as e:
        return [], dict(seed=seed, error=repr(e))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--nbb', type=int, default=600000)
    ap.add_argument('--bb-seconds', type=float, default=2400)
    ap.add_argument('--ntoy', type=int, default=300)
    ap.add_argument('--nlee', type=int, default=200)
    ap.add_argument('--seed', type=int, default=20261117)
    a = ap.parse_args()
    out = os.path.join(a.out, 'forecast')
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    res = dict(tool='dimustat forecast 0.1.0', made_by='MV2 of Munim, Inc. (made with AI agents)',
               aleph_input=A, note='No DELPHI data used. Toys from a generator-level shape.')

    # 1. background shape
    with mp.Pool(a.workers) as pool:
        bb = pool.map(bb_task, [(a.nbb // a.workers, a.seed + 101 + i, a.bb_seconds)
                                for i in range(a.workers)])
    masses = np.array([m for ms, _ in bb for m in ms])
    res['bb_generation'] = [st for _, st in bb]
    print('BB', json.dumps(res['bb_generation']), flush=True)
    if len(masses):
        h, _ = np.histogram(masses, bins=np.arange(10, 61, 1.0))
        res['bb_hist_10_60_1GeV'] = h.tolist()
        np.savetxt(os.path.join(out, 'bb_os_dimuon_masses.txt.gz'), masses, fmt='%.4f')
        n_gen = sum(st.get('n_generated', 0) for _, st in bb)
        res['bb_pairs_15_50_per_zbb'] = float(np.sum((masses > 15) & (masses < 50)) / max(n_gen, 1))
        res['bb_frac_26_35_of_15_50'] = float(np.sum((masses > 26) & (masses < 35)) /
                                              max(np.sum((masses > 15) & (masses < 50)), 1))
    truths = truth_shapes(masses if len(masses) else None)
    res['kde_bandwidth'] = truths.pop('_bw', None)
    main_truth = 'pythia_bb' if 'pythia_bb' in truths else 'powerlaw3'
    res['main_truth'] = main_truth
    np.savetxt(os.path.join(out, 'truth_shapes.txt'),
               np.column_stack([ds.CENT] + [truths[k] for k in truths]),
               header='m_GeV ' + ' '.join(truths.keys()), fmt='%.6e')

    scs = scen_list(main_truth)
    # 2. Asimov medians
    res['asimov'] = {}
    for sc in scs:
        res['asimov'][sc['name']] = asimov_block(sc, truths[sc['truth']])
        print('ASIMOV', sc['name'], json.dumps(res['asimov'][sc['name']]), flush=True)
    # 3. spurious signal
    res['spurious'] = spurious_table(truths, scs[1])
    print('SPURIOUS', json.dumps(res['spurious']), flush=True)
    res['t_before_toys_s'] = round(time.time() - t0, 1)

    # 4. toys
    tasks = []
    k = 0
    chunk = max(1, a.ntoy // 4)
    for sc in scs:
        for mu in MUS:
            left = a.ntoy
            while left > 0:
                nt = min(chunk, left)
                tasks.append((sc, truths[sc['truth']], mu, nt, a.seed + 1000 + k))
                left -= nt
                k += 1
    with mp.Pool(a.workers) as pool:
        tr = pool.map(toy_task, tasks, chunksize=1)
    allrows = {}
    for name, mu, rows in tr:
        allrows.setdefault(name, {}).setdefault(str(mu), []).extend(rows)
    res['toys'] = {name: {mu: summarise_toys(r) for mu, r in d.items()} for name, d in allrows.items()}
    with open(os.path.join(out, 'toys.json'), 'w') as f:
        json.dump(allrows, f)
    print('TOYS', json.dumps(res['toys']), flush=True)
    res['t_after_toys_s'] = round(time.time() - t0, 1)

    # 5. look-elsewhere, main scenario S2, free-mass scan 16-49 GeV (Gamma fixed 1.78)
    masses_scan = np.round(np.arange(16.0, 49.0001, 0.25), 3)
    sc = scs[1]
    per = max(1, a.nlee // (2 * a.workers))
    lt = []
    left, j = a.nlee, 0
    while left > 0:
        nt = min(per, left)
        lt.append((sc, truths[sc['truth']], nt, a.seed + 5000 + j, masses_scan))
        left -= nt
        j += 1
    with mp.Pool(a.workers) as pool:
        lr = pool.map(lee_task, lt, chunksize=1)
    lee = [r for part in lr for r in part]
    zmax = np.array([r['zmax'] for r in lee])
    up1 = np.mean([r['up1'] for r in lee]) if lee else float('nan')
    gv = {}
    for z in (2.0, 3.0, 4.0, 5.0):
        pl = 1.0 - stats.norm.cdf(z)
        pg = pl + up1 * math.exp(-(z * z - 1.0) / 2.0)
        gv[str(z)] = dict(p_local=pl, p_global_toys=float(np.mean(zmax >= z)) if lee else None,
                          p_global_gross_vitells=pg, z_global_gv=float(stats.norm.isf(min(pg, 0.5))))
    res['lee'] = dict(scenario=sc['name'], n_toys=len(lee), mean_upcrossings_z1=float(up1),
                      zmax_median=float(np.median(zmax)) if lee else None,
                      zmax_quantiles_50_90_95_99=[float(np.percentile(zmax, q)) for q in (50, 90, 95, 99)] if lee else None,
                      global=gv)
    print('LEE', json.dumps(res['lee']), flush=True)
    with open(os.path.join(out, 'lee_toys.json'), 'w') as f:
        json.dump(lee, f)
    res['wall_s'] = round(time.time() - t0, 1)
    with open(os.path.join(out, 'forecast.json'), 'w') as f:
        json.dump(res, f, indent=1)

    # compact table
    print('\nSCENARIO                    Nexp   Bwin  medUL  Z0(A)  | mu=0: P(excl)  | mu=1: P(compat) P(excl) P(Z0>=2) | mu=0.66: P(excl)')
    for sc in scs:
        n = sc['name']
        asv = res['asimov'][n]
        t = res['toys'].get(n, {})
        g = lambda mu, key: t.get(str(mu), {}).get(key)
        print('%-26s %6.1f %6.1f %6.3f %6.3f | %13s | %15s %7s %8s | %s' % (
            n, asv['n_exp'], asv['n_bkg_window_pm2p5'], asv['median_ul_nexp_units'],
            asv['asimov_z0_if_aleph_sized'], g(0.0, 'p_EXCLUDED'), g(1.0, 'p_COMPATIBLE'),
            g(1.0, 'p_EXCLUDED'), g(1.0, 'p_z0_ge2'), g(0.66, 'p_EXCLUDED')))
    print('SUMMARY_JSON_BEGIN')
    print(json.dumps({k: v for k, v in res.items() if k not in ('bb_hist_10_60_1GeV',)}, indent=1))
    print('SUMMARY_JSON_END')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
