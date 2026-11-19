#!/usr/bin/env python3
"""run_klyscan: Ko, Li and Yu's model III (Z -> Z' phi, Z' -> mu mu, phi -> b bbar) between the
three scalar masses computed so far, and above them.

Jobs kly-v1 and kly4f-v1 (NOTE-higgs-searches.md 0.7-0.8, sections 6 and 6b) computed model III
at m_phi = 12, 30.4 and 50 GeV only, which the note lists as a limit. This script runs the SAME
generator, Pythia settings and selections (lephz 0.1.0: the four LEP1 Higgs searches; eff4f 0.2.0:
the three LEP1 four-fermion selections) at m_phi = 15, 20, 25, 35, 40, 45 and 55 GeV, and re-runs Q30
with kly-v1's seed as a closure check (its counts must equal kly-v1's and kly4f-v1's).

For each mass it reports the nominal and weakest-variant efficiencies and the pre-registered
confrontations at the lowest literature rate (Ko, Li and Yu's model-II benchmark, Br 1.1e-5):
  L3 Higgs search alone (0 candidates), weakest variant x 0.78 (calibration ratio, section 5);
  OPAL four-fermion alone (1 event in 20-40 GeV), weakest variant x 0.62;
  OPAL + L3 four-fermion, nominal, weakest, and weakest x (0.62, 0.78).
Expectations S1-S6 are in NOTE-higgs-searches.md section 6d, written before this job ran.

Needs kly.py, lephz.py, efhz.py, eff4f.py, lep4f.py, run_kly4f.py and xkin's xme.py, evana.py,
fadgen.py, run_xkin.py next to it (the job fetches the published ones), numpy, pythia8mc.

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

VERSION = "mv2 klyscan 0.1.0"
ORDER = ("B110", "B180", "B110L", "Q12", "Q30", "Q50")     # run_kly / run_kly4f model order
SCAN = (15.0, 20.0, 25.0, 35.0, 40.0, 45.0, 55.0)
# NOTE-higgs-searches section 3 / section 6: predicted events for efficiency 1 at the lowest
# literature rate, muon identification included (L3 alone: Q12 20.43 / 0.604 = 33.82)
L3H_LIT_EPS1 = 33.83
DELPHI_LIT_EPS1 = 10.38
# calibration ratios (our hadron-level eff / experiments' published Higgs eff), section 5 item 3
CAL = {"L3H": 0.78, "DH": 0.90, "OPAL4f": 0.62, "L34f": 0.78}
# closure references for Q30 (kly-v1 nominal eps to 3 decimals; kly4f-v1 integer counts)
KLY_V1_Q30 = {"ALEPH96:nominal": 0.018, "L3_96:nominal": 0.588, "DELPHI94:nominal": 0.789,
              "OPAL97:nominal": 0.417}
KLY4F_V1_Q30 = (7152, 6366, 4163)   # n_acc, OPAL:nominal, L3:nominal (pass_acc_win)


def scan_label(m):
    return "Q%g" % m


def seed_for(label, base):
    """kly-v1/kly4f-v1 seeds for the six original models; new, distinct seeds for the scan."""
    if label in ORDER:
        return base + 7 * ORDER.index(label) + 1
    m = float(label[1:])
    return base + 7 * (len(ORDER) + SCAN.index(m)) + 1


def register(kly, masses=SCAN):
    """Add model-III labels for the scan masses, copying kind, layout and signal id from Q50."""
    kind, _, layout, sid = kly.MODELS["Q50"]
    added = []
    for m in masses:
        lab = scan_label(m)
        if lab not in kly.MODELS:
            kly.MODELS[lab] = (kind, dict(m_phi=float(m)), layout, sid)
            added.append(lab)
    return added


def poisson_le(k, lam):
    """P(n <= k) for a Poisson mean lam."""
    s, t = 0.0, 1.0
    for i in range(k + 1):
        if i > 0:
            t *= lam / i
        s += t
    return math.exp(-lam) * s


def lam_needed(k, p):
    """Smallest Poisson mean with P(n <= k) <= p (bisection)."""
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if poisson_le(k, mid) > p:
            lo = mid
        else:
            hi = mid
    return hi


def weakest_of(eps, prefix):
    """(key, value) of the lowest efficiency among keys 'prefix:...'."""
    items = [(k, v) for k, v in eps.items() if k.startswith(prefix + ":")]
    return min(items, key=lambda kv: kv[1])


def l3h_alone(eps_value, scale=1.0):
    """L3 Higgs search alone, 0 candidates, lowest literature rate."""
    lam = eps_value * L3H_LIT_EPS1 * scale
    return {"pred": lam, "n_obs": 0, "p": poisson_le(0, lam)}


def run_model(task):
    """Mirror of run_kly.run_model / run_kly4f.run_model (same generation and Pythia settings),
    with both the lephz and the eff4f selections applied to every event."""
    label, n, seed, tmpdir, outdir, budget = task
    import eff4f
    import kly
    import lephz
    import run_xkin
    import xme
    register(kly)
    t0 = time.time()
    kind, par, layout, sig_id = kly.MODELS[label]
    rng = np.random.default_rng(seed)
    ev = kly.generate(label, n, rng)
    lhe = os.path.join(tmpdir, 'klyscan_%s.lhe' % label)
    xme.write_lhe(lhe, layout, ev)
    mphi = par.get("m_phi", 30.4)
    sets = run_xkin.pythia_common(seed % 900000000 + 1) + [
        "Beams:frameType = 4", "Beams:LHEF = %s" % lhe,
        "32:m0 = 30.4", "32:mWidth = 1.78", "32:mMin = 5.", "32:mMax = 85.",
        "35:m0 = 30.4", "35:mWidth = 1.78", "35:mMin = 5.", "35:mMax = 85.",
        "36:m0 = %.3f" % mphi, "36:mWidth = 0.01", "36:mMin = 5.", "36:mMax = 85."]
    py = run_xkin.make_pythia(sets)
    c4 = eff4f.new_counts()
    chz = lephz.new_counts()
    rec = []
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
        r4 = eff4f.evaluate(ids, p4, ch, i, j)
        eff4f.accumulate(c4, r4)
        rh = lephz.evaluate(ids, p4, ch, i, j)
        lephz.accumulate(chz, rh)
        if rh["acc"] and rh["in_window"]:
            rec.append(rh["recoil"])
        if nok % 250 == 0:
            with open(os.path.join(outdir, 'partialscan_%s.json' % label), 'w') as f:
                json.dump(dict(model=label, n_hadronised=nok, counts4f=c4, countshz=chz,
                               seconds=round(time.time() - t0, 1)), f)
    a = np.array(rec, float)
    a = a[np.isfinite(a)]
    rq = [round(float(x), 3) for x in np.quantile(a, (0.05, 0.25, 0.5, 0.75, 0.95))] if len(a) else []
    stats = dict(model=label, kind=kind, params=par, parton=ev['stats'], n_hadronised=nok,
                 n_fail=nfail, n_no_truth_pair=nopair, stopped_by_budget=stopped,
                 seconds=round(time.time() - t0, 1), recoil_quantiles=rq)
    return label, c4, chz, stats


def analyse(label, c4, chz):
    import eff4f
    import lephz
    e4 = {k: eff4f.eps_kin(c4, k)[0] for k in eff4f.KEYS}
    eh = {k: lephz.eps(chz, k)[0] for k in lephz.KEYS}
    nom = {s: eh["%s:nominal" % s] for s in lephz.ALL_SET}
    n_lit = eff4f.n_sig_for_rate(eff4f.R_LIT)
    l3h_w = weakest_of(eh, "L3_96")
    dh_w = weakest_of(eh, "DELPHI94")
    o_w = weakest_of(e4, "OPAL")
    l4_w = weakest_of(e4, "L3")
    al = e4["ALEPH:nominal"]

    def conf(expts, o, l3):
        return eff4f.confront(expts, {"OPAL": o, "L3": l3, "ALEPH": al}, n_sig=n_lit)

    tests = {
        "L3H|nominal|lit": l3h_alone(eh["L3_96:nominal"]),
        "L3H|weakest|lit": l3h_alone(l3h_w[1]),
        "L3H|weakest_x0.78|lit": l3h_alone(l3h_w[1], CAL["L3H"]),
        "OPAL4f|nominal|lit": conf(("OPAL",), e4["OPAL:nominal"], e4["L3:nominal"]),
        "OPAL4f|weakest_x0.62|lit": conf(("OPAL",), o_w[1] * CAL["OPAL4f"], l4_w[1]),
        "OPAL+L3_4f|nominal|lit": conf(("OPAL", "L3"), e4["OPAL:nominal"], e4["L3:nominal"]),
        "OPAL+L3_4f|weakest|lit": conf(("OPAL", "L3"), o_w[1], l4_w[1]),
        "OPAL+L3_4f|weakest_scaled|lit": conf(("OPAL", "L3"), o_w[1] * CAL["OPAL4f"],
                                              l4_w[1] * CAL["L34f"]),
    }
    closure = None
    if label == "Q30":
        closure = (c4["n_acc"] == KLY4F_V1_Q30[0] and
                   c4["pass_acc_win"]["OPAL:nominal"] == KLY4F_V1_Q30[1] and
                   c4["pass_acc_win"]["L3:nominal"] == KLY4F_V1_Q30[2] and
                   all(round(eh[k], 3) == v for k, v in KLY_V1_Q30.items()))
    return dict(eps4f={k: round(v, 4) for k, v in e4.items()},
                epshz={k: round(v, 4) for k, v in eh.items()},
                weakest={"L3H": l3h_w, "DH": dh_w, "OPAL4f": o_w, "L34f": l4_w},
                confront_lephz_nominal=lephz.confront_all(nom), tests=tests, closure=closure)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='/out')
    ap.add_argument('--nsig', type=int, default=8000)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--seed', type=int, default=20261121)   # = run_kly / run_kly4f default
    ap.add_argument('--budget-min', type=float, default=40.0)
    a = ap.parse_args()
    import eff4f
    import kly
    import lephz
    print('VERSIONS', VERSION, kly.VERSION, lephz.VERSION, eff4f.VERSION, flush=True)
    register(kly)
    os.makedirs(a.out, exist_ok=True)
    tmp = '/tmp/klyscan'
    os.makedirs(tmp, exist_ok=True)
    labels = ["Q30"] + [scan_label(m) for m in SCAN]
    tasks = [(m, a.nsig, seed_for(m, a.seed), tmp, a.out, a.budget_min * 60.0) for m in labels]
    with mp.Pool(min(a.workers, len(tasks))) as pool:
        results = pool.map(run_model, tasks, chunksize=1)
    out = dict(tool=VERSION, kly=kly.VERSION, lephz=lephz.VERSION, eff4f=eff4f.VERSION,
               made_by='MV2 of Munim, Inc. (made with AI agents)',
               question="Ko-Li-Yu model III between m_phi = 12, 30.4 and 50 GeV",
               thresholds=dict(L3H_eps_weakest_for_p1e-3=math.log(1000.0) / (L3H_LIT_EPS1 * CAL["L3H"]),
                               lam_needed_1obs_p1e-3=lam_needed(1, 1e-3)),
               models={})
    for label, c4, chz, st in results:
        print('TASK', json.dumps(st, default=str), flush=True)
        out["models"][label] = dict(stats=st, counts4f=c4, countshz=chz, **analyse(label, c4, chz))
    with open(os.path.join(a.out, 'klyscan-summary.json'), 'w') as f:
        json.dump(out, f, indent=1, default=str)

    print('\nmodel III scan: eps vs ALEPH acceptance, 20-40 GeV, no muon ID')
    last = []
    for label, r in out["models"].items():
        e4, eh, t = r["eps4f"], r["epshz"], r["tests"]
        print('%-4s Higgs A/L3/D/O %.3f/%.3f/%.3f/%.3f  4f OPAL/L3 %.3f/%.3f  weakest %s  recoil q %s' % (
            label, eh["ALEPH96:nominal"], eh["L3_96:nominal"], eh["DELPHI94:nominal"],
            eh["OPAL97:nominal"], e4["OPAL:nominal"], e4["L3:nominal"],
            json.dumps(r["weakest"]), json.dumps(r["stats"]["recoil_quantiles"])))
        for k, c in t.items():
            p = c.get("p", c.get("p_value"))
            print('     %-32s n=%d pred=%7.2f p=%.3g' % (k, c["n_obs"], c["pred"], p))
        last.append('%s L3H/DH/O4/L4 %.3f/%.3f/%.3f/%.3f L3Hw*.78 p=%.2g O4w*.62 p=%.2g O+L3w p=%.2g closure=%s' % (
            label, eh["L3_96:nominal"], eh["DELPHI94:nominal"], e4["OPAL:nominal"], e4["L3:nominal"],
            t["L3H|weakest_x0.78|lit"]["p"], t["OPAL4f|weakest_x0.62|lit"]["p_value"],
            t["OPAL+L3_4f|weakest|lit"]["p_value"], r["closure"]))
    print('\nKLYSCAN: ' + ' | '.join(last))
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
