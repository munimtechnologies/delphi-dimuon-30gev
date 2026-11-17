"""run_xkin: would a real 30 GeV boson look like ALEPH's dimuon excess?

Generates signal hypotheses V, S, P (see xme.py) at parton level, hadronises them with
Pythia 8 (pythia8mc), generates inclusive Z -> b bbar background with Pythia 8, and measures
at generator level the quantities ALEPH reported for its excess (arXiv:1610.06536):
muon - leading-jet angles (sec. 4.2), muon multiplicity (4.4), cos theta* (4.7), and the
acceptance of ALEPH-like cuts. It also writes hadron-level signal events for a later
DELPHI detector simulation (DELSIM).

No detector simulation, no b-tag, no impact-parameter cut: this is a kinematic study.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import csv
import gzip
import json
import math
import multiprocessing as mp
import os
import sys
import time

import numpy as np

import xme
import evana
import fadgen

WIN = (26.0, 35.0)
MASS_IDS = {'V': 32, 'S': 35, 'P': 35}


def pythia_common(seed):
    return ["Print:quiet = on", "Next:numberCount = 0", "PDF:lepton = off",
            "PartonLevel:ISR = off", "PartonLevel:MPI = off",
            "ParticleDecays:limitTau0 = on", "ParticleDecays:tau0Max = 10.",
            "Random:setSeed = on", "Random:seed = %d" % seed]


def make_pythia(settings):
    import pythia8mc
    py = pythia8mc.Pythia()
    for s in settings:
        if not py.readString(s):
            print("WARN pythia rejected setting:", s, flush=True)
    if not py.init():
        raise RuntimeError("pythia init failed")
    return py


def extract(ev, sig_ids):
    ids, p4, ch, sig, vtx = [], [], [], [], []
    for i in range(ev.size()):
        p = ev[i]
        if not p.isFinal():
            continue
        pid = p.id()
        s = False
        if abs(pid) == 13:
            j = i
            while ev[j].idAbs() == 13 and ev[j].mother1() > 0:
                j = ev[j].mother1()
            s = ev[j].idAbs() in sig_ids
        ids.append(pid)
        p4.append((p.e(), p.px(), p.py(), p.pz()))
        ch.append(p.charge())
        sig.append(s)
        vtx.append((p.xProd(), p.yProd(), p.zProd(), p.tProd(), p.m()))
    return (np.array(ids), np.array(p4, float).reshape(-1, 4), np.array(ch, float),
            np.array(sig, bool), np.array(vtx, float).reshape(-1, 5))


def muon_indices(ev):
    n = 0
    for i in range(ev.size()):
        p = ev[i]
        if p.idAbs() == 13 and p.isFinal():
            n += 1
    return n


def run_signal(model, n, seed, tmpdir, outdir, nwrite, nfad=0):
    t0 = time.time()
    rng = np.random.default_rng(seed)
    if model == 'P':
        ev = xme.generate_pair(n, rng)
    else:
        ev = xme.generate_radiation(model, n, rng)
    stats = dict(ev['stats'])
    stats['t_parton_s'] = round(time.time() - t0, 1)
    # parton-level truth before any hadronisation (for acceptance cross-checks)
    m_true = [evana.minkowski_mass(a + b) for a, b in zip(ev['q1'], ev['q2'])]
    stats['m_parton_mean'] = float(np.mean(m_true))
    lhe = os.path.join(tmpdir, 'xkin_%s.lhe' % model)
    xme.write_lhe(lhe, model, ev)
    sets = pythia_common(seed % 900000000 + 1) + [
        "Beams:frameType = 4", "Beams:LHEF = %s" % lhe,
        "32:m0 = 30.4", "32:mWidth = 1.78", "32:mMin = 5.", "32:mMax = 85.",
        "35:m0 = 30.4", "35:mWidth = 1.78", "35:mMin = 5.", "35:mMax = 85.",
        "36:m0 = 30.4", "36:mWidth = 0.01", "36:mMin = 5.", "36:mMax = 85."]
    py = make_pythia(sets)
    rows = []
    nfail = 0
    nok = 0
    nsig2 = 0
    hadf = gzip.open(os.path.join(outdir, 'hadron_events_%s.txt.gz' % model), 'wt') if nwrite else None
    if hadf:
        hadf.write('# xkin model %s hadron-level final state (Pythia 8, tau0Max 10 mm); '
                   'per event: "E ievt npart", then "id px py pz E m x y z t" (GeV, mm). '
                   'MV2 of Munim, Inc., made with AI agents, CC BY 4.0\n' % model)
    fad_path = os.path.join(outdir, 'fadgen_%s.fort26' % model) if nfad else None
    fadf = open(fad_path, 'wb') if fad_path else None
    nfad_written = 0
    for iev in range(n):
        if not py.next():
            nfail += 1
            if nfail > 50 and nok == 0:
                break
            continue
        nok += 1
        if fadf and nfad_written < nfad:
            K, P, V = fadgen.lujets_from_pythia(py.event)
            fadgen.write_event(fadf, K, P, V)
            nfad_written += 1
        ids, p4, ch, sig, vtx = extract(py.event, (MASS_IDS[model],))
        if hadf and nok <= nwrite:
            hadf.write('E %d %d\n' % (nok, len(ids)))
            for k in range(len(ids)):
                hadf.write('%d %.6e %.6e %.6e %.6e %.5e %.4e %.4e %.4e %.4e\n'
                           % (ids[k], p4[k, 1], p4[k, 2], p4[k, 3], p4[k, 0], vtx[k, 4],
                              vtx[k, 0], vtx[k, 1], vtx[k, 2], vtx[k, 3]))
        smu = np.nonzero(sig & (np.abs(ids) == 13))[0]
        if len(smu) != 2 or ch[smu[0]] * ch[smu[1]] >= 0:
            continue
        nsig2 += 1
        evq = evana.event_quantities(ids, p4, ch)
        mus = [evana.muon_info(evq, i) for i in np.nonzero(np.abs(ids) == 13)[0]]
        by_i = {m['i']: m for m in mus}
        row = evana.pair_row(evq, by_i[int(smu[0])], by_i[int(smu[1])])
        row['n_mu_p'] = int(sum(evana.muon_pass(m) for m in mus))
        row['n_mu_pt'] = int(sum(evana.muon_pass(m, True) for m in mus))
        row['sample'] = model
        rows.append(row)
    if hadf:
        hadf.close()
    if fadf:
        fadgen.write_end(fadf)
        fadf.close()
        # read back and validate: energy of K=1/4 entries, signal muons present
        nread, bad_e, no_mu, nmax = 0, 0, 0, 0
        for K, P, V in fadgen.read_fadgen(fad_path):
            nread += 1
            nmax = max(nmax, len(K))
            fin = np.isin(K[:, 0], (1, 4))
            if abs(float(P[fin, 3].sum()) - xme.SQRT_S) > 0.05:
                bad_e += 1
            if np.sum(fin & (np.abs(K[:, 1]) == 13)) < 2:
                no_mu += 1
        stats['fadgen'] = dict(written=nfad_written, read_back=nread, energy_mismatch=bad_e,
                               fewer_than_2_final_muons=no_mu, max_entries=nmax,
                               bytes=os.path.getsize(fad_path))
    stats.update(n_hadronised=nok, n_fail=nfail, n_truth_pair=nsig2,
                 t_total_s=round(time.time() - t0, 1))
    return model, rows, stats


def run_background(n, seed, tag):
    t0 = time.time()
    sets = pythia_common(seed) + [
        "Beams:idA = 11", "Beams:idB = -11", "Beams:eCM = 91.1876",
        "WeakSingleBoson:ffbar2gmZ = on", "WeakZ0:gmZmode = 2",
        "23:onMode = off", "23:onIfAny = 5"]
    py = make_pythia(sets)
    rows = []
    nok = 0
    n2mu = 0
    for iev in range(n):
        if not py.next():
            continue
        nok += 1
        if muon_indices(py.event) < 2:
            continue
        n2mu += 1
        ids, p4, ch, sig, vtx = extract(py.event, ())
        mu_idx = np.nonzero(np.abs(ids) == 13)[0]
        # quick pre-selection: some opposite-sign pair with p > 2 GeV and 10 < m < 60
        good = [i for i in mu_idx if np.linalg.norm(p4[i, 1:]) > 2.0]
        cand = []
        for a in range(len(good)):
            for b in range(a + 1, len(good)):
                i, j = good[a], good[b]
                if ch[i] * ch[j] < 0:
                    m = evana.minkowski_mass(p4[i] + p4[j])
                    if 10.0 < m < 60.0:
                        cand.append((i, j))
        if not cand:
            continue
        evq = evana.event_quantities(ids, p4, ch)
        mus = {int(i): evana.muon_info(evq, i) for i in mu_idx}
        n_p = int(sum(evana.muon_pass(m) for m in mus.values()))
        n_pt = int(sum(evana.muon_pass(m, True) for m in mus.values()))
        for (i, j) in cand:
            row = evana.pair_row(evq, mus[int(i)], mus[int(j)])
            row['n_mu_p'] = n_p
            row['n_mu_pt'] = n_pt
            row['sample'] = 'bkg'
            rows.append(row)
    stats = dict(model='bkg', tag=tag, n_generated=nok, n_ge2mu=n2mu, n_pairs=len(rows),
                 t_total_s=round(time.time() - t0, 1))
    return 'bkg', rows, stats


def run_task(task):
    kind = task[0]
    try:
        if kind == 'bkg':
            return run_background(task[1], task[2], task[3])
        return run_signal(kind, task[1], task[2], task[3], task[4], task[5], task[6])
    except Exception as e:  # report, don't kill the pool
        import traceback
        traceback.print_exc()
        return kind, [], dict(model=kind, error=repr(e))


def frac(x, n):
    return None if n == 0 else round(x / n, 4)


def summarise(rows, use_pt=False, win=WIN, Rs=evana.RS):
    sel = [r for r in rows if (r['pass_pt'] if use_pt else r['pass_p'])
           and r['nch'] >= 5 and r['pmiss'] < 18.0]
    inwin = [r for r in sel if win[0] < r['m'] < win[1]]
    nmu_key = 'n_mu_pt' if use_pt else 'n_mu_p'
    s = dict(n_pairs_all=len(rows), n_pass_cuts=len(sel),
             n_pass_15_50=sum(1 for r in sel if 15 < r['m'] < 50), n_window=len(inwin))
    s['f_ge3mu_window'] = frac(sum(1 for r in inwin if r[nmu_key] >= 3), len(inwin))
    s['f_cone_max_lt2_window'] = frac(sum(1 for r in inwin if r['cone_max'] < 2.0), len(inwin))
    s['f_cone_max_lt5_window'] = frac(sum(1 for r in inwin if r['cone_max'] < 5.0), len(inwin))
    cst = np.array([r['cst'] for r in inwin if not math.isnan(r['cst'])])
    s['f_abs_cst_gt_0p8_window'] = frac(int(np.sum(np.abs(cst) > 0.8)), len(cst))
    s['cst_hist_10bins'] = np.histogram(cst, bins=10, range=(-1, 1))[0].tolist() if len(cst) else []
    for R in Rs:
        a = np.array([r['amin_%.1f' % R] for r in inwin], float)
        o = np.array([r['aoth_%.1f' % R] for r in inwin], float)
        ok = ~np.isnan(a)
        a, o = a[ok], o[ok]
        k = 'R%.1f' % R
        s[k] = dict(n_defined=int(ok.sum()), n_undefined=int((~ok).sum()),
                    f_amin_lt15=frac(int(np.sum(a < 15)), len(a)),
                    f_aoth_lt20=frac(int(np.sum(o < 20)), len(a)),
                    f_both=frac(int(np.sum((a < 15) & (o < 20))), len(a)),
                    f_aoth_gt30=frac(int(np.sum(o > 30)), len(a)),
                    median_amin=None if not len(a) else round(float(np.median(a)), 2),
                    median_aoth=None if not len(a) else round(float(np.median(o)), 2),
                    hist_amin_5deg=np.histogram(a, bins=18, range=(0, 90))[0].tolist(),
                    hist_aoth_5deg=np.histogram(o, bins=18, range=(0, 90))[0].tolist())
    nm = np.array([r['near_min'] for r in inwin], float)
    no = np.array([r['near_oth'] for r in inwin], float)
    ok = ~np.isnan(nm)
    s['nearest_jet_R0.4'] = dict(f_min_lt15=frac(int(np.sum(nm[ok] < 15)), int(ok.sum())),
                                 f_both_lt20=frac(int(np.sum((nm[ok] < 20) & (no[ok] < 20))), int(ok.sum())),
                                 f_both_gt20=frac(int(np.sum(nm[ok] > 20)), int(ok.sum())))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--nsig', type=int, default=20000)
    ap.add_argument('--nbkg', type=int, default=600000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20261117)
    ap.add_argument('--nwrite', type=int, default=200)
    ap.add_argument('--nfad', type=int, default=100)
    a = ap.parse_args()
    out = os.path.join(a.out, 'xkin')
    os.makedirs(out, exist_ok=True)
    tmp = '/tmp/xkin'
    os.makedirs(tmp, exist_ok=True)
    nb = a.nbkg // 2
    tasks = [('bkg', nb, a.seed + 11, 'b1'), ('bkg', a.nbkg - nb, a.seed + 12, 'b2'),
             ('V', a.nsig, a.seed + 1, tmp, out, a.nwrite, a.nfad),
             ('S', a.nsig, a.seed + 2, tmp, out, a.nwrite, a.nfad),
             ('P', a.nsig, a.seed + 3, tmp, out, 0, 0)]
    t0 = time.time()
    with mp.Pool(a.workers) as pool:
        results = pool.map(run_task, tasks, chunksize=1)
    rows_by = {}
    stats = []
    for kind, rows, st in results:
        rows_by.setdefault(kind, []).extend(rows)
        stats.append(st)
        print('TASK', json.dumps(st), flush=True)
    # diagnostic: compare the matrix element with the massive-gluon formula
    rng = np.random.default_rng(5)
    m = 30.40
    E1 = rng.uniform(5, 40, 4000)
    E2 = rng.uniform(5, 40, 4000)
    p1, p2, k, valid = xme.three_body(E1, E2, np.full(4000, m))
    p1, p2, k = p1[valid], p2[valid], k[valid]
    me = xme.quark_amp2(p1, p2, k, xme.POL_BASIS, xme.POL_W,
                        [xme.slash(e) for e in xme.POL_BASIS], xme.POL_W, 1.0, 0.0)
    x1 = 2 * p1[:, 0] / xme.SQRT_S
    x2 = 2 * p2[:, 0] / xme.SQRT_S
    r = me / xme.dms_massive_gluon(x1, x2, (m / xme.SQRT_S) ** 2)
    dms = dict(n=int(len(r)), ratio_rel_spread=float(np.std(r) / np.mean(r)))
    print('DMS_DIAGNOSTIC', json.dumps(dms), flush=True)

    summary = dict(tool='xkin 0.1.0', made_by='MV2 of Munim, Inc. (made with AI agents)',
                   window_GeV=list(WIN), cuts='2 OS muons p>2.5 GeV (or pT>2.5), |cos|<0.95; '
                   '>=5 charged (p>0.2, |cos|<0.95); |p_miss(visible)|<18 GeV; generator level',
                   wall_s=round(time.time() - t0, 1), tasks=stats, dms_diagnostic=dms, samples={})
    for kind, rows in rows_by.items():
        summary['samples'][kind] = dict(p_cut=summarise(rows, False), pt_cut=summarise(rows, True))
        with gzip.open(os.path.join(out, 'pairs_%s.csv.gz' % kind), 'wt', newline='') as f:
            if rows:
                keys = sorted(rows[0].keys())
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                for rr in rows:
                    w.writerow(rr)
    with open(os.path.join(out, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)
    print('SUMMARY_JSON_BEGIN')
    print(json.dumps(summary, indent=1))
    print('SUMMARY_JSON_END')
    # compact table
    print('\n%-4s %-7s %7s %7s %8s %8s %8s %8s %8s %8s' % ('smp', 'cut', 'nwin', 'R', 'amin<15',
          'aoth<20', 'both', 'aoth>30', '>=3mu', 'iso<2'))
    for kind in ('V', 'S', 'P', 'bkg'):
        if kind not in summary['samples']:
            continue
        for cut in ('p_cut', 'pt_cut'):
            s = summary['samples'][kind][cut]
            for R in evana.RS:
                d = s['R%.1f' % R]
                print('%-4s %-7s %7d %7.1f %8s %8s %8s %8s %8s %8s' % (
                    kind, cut, s['n_window'], R, d['f_amin_lt15'], d['f_aoth_lt20'], d['f_both'],
                    d['f_aoth_gt30'], s['f_ge3mu_window'], s['f_cone_max_lt2_window']))
    sys.stdout.flush()


if __name__ == '__main__':
    main()
