#!/usr/bin/env python3
"""sigana: DELPHI detector response to a 30 GeV dimuon signal (simulation only).

Compares the generated signal events (DELSIM input, FADGEN format) with the reconstructed
short-DST events written by MV2's SKELANA USER02 (mv2user02s.car), and measures:
  - tracking and muon-identification efficiency for the two signal muons,
  - the efficiency of ALEPH-like event cuts and of DELPHI b-tag working points,
  - the dimuon mass resolution at 30 GeV and the 1/p resolution versus p,
  - impact parameters of prompt signal muons.
Everything here is simulation, so no blinding applies.

0.2.0 (PLAN v0.10, section 4e): the signal's b-tag efficiency is now also measured with the
SAME hemisphere tag that analysis/dimusel.py uses in btag_mode "hemi" (an event is tagged if
min(QBTPRP(1), QBTPRP(2)) < w over hemispheres with a valid probability in [0, 1]), on the
working-point grid of analysis/btagcal.py. The per-hemisphere rate is reported too, for
comparison with btagcal's hemisphere efficiency e_b. The 0.1.0 numbers based on the event
probability QBTPRP(3) are kept unchanged.
Also new: eff_track_all, whose denominator is every in-acceptance signal muon of the simulated
events, so events in which both muons were lost (never aligned) count as losses; eff_track
(aligned events only) is kept and is biased upward by those events.

0.3.0 (PLAN v0.11, section 4e step 7 and 5f): "dimusel_exact". The signal efficiency that enters
N_exp is now measured with analysis/dimusel.py's OWN code and configuration (imported, not
re-implemented): its hadronic selection including the thrust-axis cut, its missing-momentum
cut over all particles, its lepton cuts including |d0| and |z0|, its muon tag and its pair-mass
range. 0.1.0/0.2.0's selection had no thrust-axis and no d0/z0 cut, so it was not the selection
the data pass. The block gives, per hemisphere working point, the fraction of simulated signal
events whose signal pair lands in os_mumu_btag (eff_T) and in os_mumu_untagged (eff_U), and the
tag efficiency of the selected signal events, which is the rho_D numerator from v0.11. dimusel
is looked for next to this file, then in ../analysis (the repository layout).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import collections
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_ANALYSIS = os.path.join(os.path.dirname(HERE), "analysis")
if os.path.isdir(_ANALYSIS) and _ANALYSIS not in sys.path:
    sys.path.append(_ANALYSIS)

VERSION = "mv2 sigana 0.3.0"
MMU = 0.1056584
SIG_IDS = (32, 35, 36)
NEUTRINOS = (12, 14, 16)
E_FIELDS = ["run", "evt", "ihad4", "nctr4", "nctrk", "nvecp", "nlep",
            "ecmas", "echar", "emneu", "ehneu",
            "btn1", "btn2", "btn3", "btp1", "btp2", "btp3", "bts1", "bts2", "bts3",
            "thx", "thy", "thz", "thr"]
E_INT = ("run", "evt", "ihad4", "nctr4", "nctrk", "nvecp", "nlep")
P_INT = ["run", "evt", "i", "q", "lock", "kmu1", "kmu3", "kel1", "kel2", "vdrphi", "vdz"]
P_REAL = ["px", "py", "pz", "e", "mchi2", "qt4", "qt5", "d0", "z0", "d0bs"]
BTAG_WP = (0.1, 0.03, 0.01, 0.003, 0.001)
# hemisphere working points: the grid of analysis/btagcal.py (WPS), so rho_D exists at every
# point btagcal can choose
HEMI_WP = (0.3, 0.1, 0.03, 0.01, 0.003, 0.001, 3e-4, 1e-4, 3e-5, 1e-5)
THRUST_COS_MAX = 0.866   # dimusel DEFAULTS thrust_cos_max
P_BINS = (2.5, 5.0, 10.0, 15.0, 20.0, 30.0, 46.0)


# ------------------------------------------------------------------ parsing
def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def parse_e(line):
    f = line.split()
    if not f or f[0] != "E" or len(f) != 1 + len(E_FIELDS):
        return None
    try:
        return {k: (int(v) if k in E_INT else float(v)) for k, v in zip(E_FIELDS, f[1:])}
    except ValueError:
        return None


def parse_p(line):
    f = line.split()
    if not f or f[0] != "P" or len(f) != 1 + len(P_INT) + len(P_REAL):
        return None
    try:
        d = {k: int(v) for k, v in zip(P_INT, f[1:1 + len(P_INT)])}
        d.update({k: float(v) for k, v in zip(P_REAL, f[1 + len(P_INT):])})
    except ValueError:
        return None
    d["p"] = math.sqrt(d["px"] ** 2 + d["py"] ** 2 + d["pz"] ** 2)
    return d


def read_ntuple(ev_path, pa_path):
    """Reconstructed events in file order: [{'e': E-dict, 'tracks': [P-dicts]}]."""
    events = []
    index = {}
    with _open(ev_path) as fh:
        for ln in fh:
            d = parse_e(ln)
            if d is None:
                continue
            index[(d["run"], d["evt"])] = len(events)
            events.append({"e": d, "tracks": []})
    if pa_path and os.path.exists(pa_path):
        with _open(pa_path) as fh:
            for ln in fh:
                d = parse_p(ln)
                if d is None:
                    continue
                k = index.get((d["run"], d["evt"]))
                if k is not None:
                    events[k]["tracks"].append(d)
    return events


# ------------------------------------------------------------------ truth
def truth_from_record(K, P):
    """Signal muons and generator-level quantities of one LUJETS-style event."""
    n = len(K)
    final = np.isin(K[:, 0], (1, 4))
    mus = []
    m_x = float("nan")
    for i in np.nonzero(final & (np.abs(K[:, 1]) == 13))[0]:
        j = int(K[i, 2]) - 1
        guard = 0
        while 0 <= j < n and abs(int(K[j, 1])) == 13 and guard < 50:
            j = int(K[j, 2]) - 1
            guard += 1
        if 0 <= j < n and abs(int(K[j, 1])) in SIG_IDS:
            q = -1 if K[i, 1] == 13 else 1
            mus.append({"q": q, "px": float(P[i, 0]), "py": float(P[i, 1]),
                        "pz": float(P[i, 2]), "e": float(P[i, 3])})
            m_x = float(P[j, 4])
    for m in mus:
        m["p"] = math.sqrt(m["px"] ** 2 + m["py"] ** 2 + m["pz"] ** 2)
    vis = final & ~np.isin(np.abs(K[:, 1]), NEUTRINOS)
    pvis = P[vis, :3].astype(float).sum(axis=0)
    pch = []
    for i in np.nonzero(final)[0]:
        if abs(int(K[i, 1])) in (11, 13, 211, 321, 2212, 3112, 3222, 3312, 3334):
            p = float(np.linalg.norm(P[i, :3]))
            if p > 0.2 and abs(float(P[i, 2])) < 0.95 * p:
                pch.append(p)
    return {"mus": mus, "m_x": m_x, "pmiss_vis": float(np.linalg.norm(pvis)),
            "nch": len(pch), "e_vis": float(P[vis, 3].astype(float).sum())}


def read_truth(path):
    import fadgen
    return [truth_from_record(K, P) for K, P, V in fadgen.read_fadgen(path)]


# ------------------------------------------------------------------ kinematics
def pair_mass(a, b, m=MMU):
    e1 = math.sqrt(a["p"] ** 2 + m * m)
    e2 = math.sqrt(b["p"] ** 2 + m * m)
    px, py, pz = a["px"] + b["px"], a["py"] + b["py"], a["pz"] + b["pz"]
    return math.sqrt(max((e1 + e2) ** 2 - (px * px + py * py + pz * pz), 0.0))


def angle_deg(a, b):
    c = (a["px"] * b["px"] + a["py"] * b["py"] + a["pz"] * b["pz"]) / max(a["p"] * b["p"], 1e-12)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def cos_theta(t):
    return t["pz"] / max(t["p"], 1e-12)


def in_acc(t, pcut=2.5, ccut=0.95):
    return t["p"] > pcut and abs(cos_theta(t)) < ccut


def is_muon(t, level="any"):
    k = t["kmu1"]
    if level == "any":
        return k > 0
    return (k >> 2) & 1 == 1


def match_muons(truth, tracks, max_angle=1.0, max_dp=0.25):
    """For each truth signal muon, the best same-charge reconstructed track (or None)."""
    out = []
    used = set()
    for mu in truth["mus"]:
        best, ba = None, max_angle
        for k, t in enumerate(tracks):
            if t["q"] != mu["q"] or k in used or t["p"] <= 0:
                continue
            a = angle_deg(mu, t)
            if a < ba and abs(t["p"] / mu["p"] - 1.0) < max_dp:
                best, ba = k, a
        if best is not None:
            used.add(best)
        out.append(None if best is None else tracks[best])
    return out


def align(reco, truth, look=8):
    """Assign each reconstructed event to a generated event. DELSIM keeps the input order but
    may drop events, so only forward steps are allowed. Returns list of truth indices or None."""
    ptr = 0
    res = []
    for ev in reco:
        cands = []
        k_evt = ev["e"]["evt"] - 1
        if 0 <= k_evt < len(truth) and k_evt >= ptr:
            cands.append(k_evt)
        cands += [j for j in range(ptr, min(ptr + look, len(truth))) if j != k_evt]
        best, bscore = None, 0
        for j in cands:
            m = match_muons(truth[j], ev["tracks"])
            score = sum(1 for x in m if x is not None)
            if score > bscore:
                best, bscore = j, score
            if score == 2:
                break
        if best is not None:
            ptr = best + 1
        res.append(best)
    return res


def robust_sigma(x):
    x = np.asarray(x, float)
    if len(x) < 4:
        return None
    q25, q75 = np.percentile(x, [25, 75])
    return float((q75 - q25) / 1.349)


def frac(a, b):
    return None if not b else round(a / b, 4)


def binom_err(a, b):
    if not b:
        return None
    p = a / b
    return round(math.sqrt(max(p * (1.0 - p), 0.0) / b), 4)


def valid_hemis(e):
    """Hemisphere lifetime probabilities usable for tagging (same rule as dimusel._hemis)."""
    return [x for x in (e["btp1"], e["btp2"]) if 0.0 <= x <= 1.0]


def hemi_tagged(e, wp):
    """dimusel btag_mode 'hemi': at least one valid hemisphere with probability below wp."""
    h = valid_hemis(e)
    return bool(h) and min(h) < wp


def hemi_tag_summary(selected_e, wps=HEMI_WP):
    """Event-level and per-hemisphere tag rates of the selected signal events."""
    n = len(selected_e)
    hemis = [x for e in selected_e for x in valid_hemis(e)]
    ev, ev_err, per_h = {}, {}, {}
    for wp in wps:
        k = sum(1 for e in selected_e if hemi_tagged(e, wp))
        ev[str(wp)] = frac(k, n)
        ev_err[str(wp)] = binom_err(k, n)
        per_h[str(wp)] = frac(sum(1 for x in hemis if x < wp), len(hemis))
    return {"n_selected": n,
            "n_selected_no_valid_hemisphere": sum(1 for e in selected_e if not valid_hemis(e)),
            "n_valid_hemispheres": len(hemis),
            "event_tag_eff": ev, "event_tag_eff_err": ev_err,
            "per_hemisphere_tag_eff": per_h}


def thrust_ok(e, cos_max=THRUST_COS_MAX):
    """dimusel's hadronic thrust-axis cut (QBTTHR within 30-150 degrees), which btagcal's data
    efficiency eps also passes; an empty axis fails, as in dimusel."""
    n = math.sqrt(e["thx"] ** 2 + e["thy"] ** 2 + e["thz"] ** 2)
    return n > 0 and abs(e["thz"]) / n <= cos_max


def rho_d(sig_event_eff, data_event_eff):
    """PLAN 5e: rho_D = signal event tag efficiency / data Z->bb event tag efficiency at the same
    hemisphere working point; test B then uses rho = max(1, rho_D)."""
    if sig_event_eff is None or not data_event_eff:
        return None
    return sig_event_eff / data_event_eff


# ------------------------------------------------------------------ dimusel-exact (0.3.0)
def _dimusel():
    try:
        import dimusel
    except ImportError:
        return None
    return dimusel


def as_dimusel_track(t):
    """A sigana track with the extra key dimusel's lepton cuts read (cos theta)."""
    d = dict(t)
    d["cth"] = t["pz"] / t["p"] if t["p"] > 0 else 0.0
    return d


def dimusel_exact(triples, n_used, cfg=None, wps=HEMI_WP):
    """PLAN 4e step 7 (v0.11): efficiency of dimusel's OWN selection for the signal pair.

    triples: (reconstructed event, truth record, generated-event index) of aligned events; the
    denominator is the n_used simulated events. A simulated event is "selected" when, with
    dimusel's code and configuration (btag_mode forced to "hemi"): it passes dimusel's hadronic
    selection (IHAD4, NCTR4, thrust axis); the missing momentum of all its particles is below
    pmiss_max; both generated signal muons are matched to tracks that pass dimusel's lepton cuts
    (p, |cos theta|, |d0|, |z0|) and muon tag at mu_level; the two have opposite charge; and
    their mass lies in dimusel's histogram range [15, 50) GeV. A selected event's signal pair is
    then the entry dimusel puts in os_mumu_btag (tagged at w) or os_mumu_untagged (not tagged).
    Variants without the thrust-axis cut and without the d0/z0 cuts show what each cut costs.
    """
    ds = _dimusel()
    if ds is None:
        return {"error": "analysis/dimusel.py not importable"}
    c = dict(cfg or {})
    c["btag_mode"] = "hemi"
    sel = ds.Selector(c)                                  # refuses unknown keys
    sel_nothrust = ds.Selector(dict(c, thrust_cos_max=1.0))
    c_nod0z0 = dict(sel.c, d0_max=1e9, z0_max=1e9)
    scratch = collections.Counter()
    n = {"aligned_simulated": 0, "hadronic": 0, "hadronic_no_thrust": 0,
         "pair_selected": 0, "pair_selected_no_thrust": 0, "pair_selected_no_d0z0": 0}
    n_t = {w: 0 for w in wps}
    for ev, tr, j in triples:
        if j is None or j >= n_used:
            continue
        n["aligned_simulated"] += 1
        e = ev["e"]
        had = sel._hadronic(e, scratch)
        had_nt = sel_nothrust._hadronic(e, scratch)
        n["hadronic"] += int(had)
        n["hadronic_no_thrust"] += int(had_nt)
        parts = ev["tracks"]
        if not had_nt or not parts or len(tr["mus"]) != 2:
            continue
        sx = sum(t["px"] for t in parts)
        sy = sum(t["py"] for t in parts)
        sz = sum(t["pz"] for t in parts)
        if math.sqrt(sx * sx + sy * sy + sz * sz) >= sel.c["pmiss_max"]:
            continue
        m = match_muons(tr, parts)
        if m[0] is None or m[1] is None:
            continue
        a, b = as_dimusel_track(m[0]), as_dimusel_track(m[1])
        if a["q"] * b["q"] >= 0:
            continue
        if not all(ds.is_muon(t, sel.c["mu_level"]) and ds.lepton_ok(t, c_nod0z0) for t in (a, b)):
            continue
        mass = ds.pair_mass(a, b, ds.MMU, ds.MMU)
        if not ds.FINE_LO <= mass < ds.FINE_HI:
            continue
        d0z0 = all(ds.lepton_ok(t, sel.c) for t in (a, b))
        n["pair_selected_no_d0z0"] += int(had)
        n["pair_selected_no_thrust"] += int(d0z0)
        if not (had and d0z0):
            continue
        n["pair_selected"] += 1
        h = sel._hemis(e)
        for w in wps:
            if h and min(h) < w:
                n_t[w] += 1
    k = n["pair_selected"]
    out = {"dimusel_version": ds.VERSION, "config": sel.c, "n_simulated": n_used, "counts": n,
           "eff_sel": frac(k, n_used), "eff_sel_err": binom_err(k, n_used),
           "eff_sel_no_thrust": frac(n["pair_selected_no_thrust"], n_used),
           "thrust_pass_given_rest": frac(k, n["pair_selected_no_thrust"]),
           "d0z0_pass_given_rest": frac(k, n["pair_selected_no_d0z0"]),
           "n_T": {}, "eff_T": {}, "eff_U": {}, "tag_eff_selected": {},
           "tag_eff_selected_err": {}}
    for w in wps:
        out["n_T"][str(w)] = n_t[w]
        out["eff_T"][str(w)] = frac(n_t[w], n_used)
        out["eff_U"][str(w)] = frac(k - n_t[w], n_used)
        out["tag_eff_selected"][str(w)] = frac(n_t[w], k)
        out["tag_eff_selected_err"][str(w)] = binom_err(n_t[w], k)
    return out


# ------------------------------------------------------------------ analysis
def gen_level(truth):
    n = len(truth)
    two = [t for t in truth if len(t["mus"]) == 2 and t["mus"][0]["q"] * t["mus"][1]["q"] < 0]
    acc = [t for t in two if all(in_acc(m) for m in t["mus"])]
    acc_nch = [t for t in acc if t["nch"] >= 5]
    acc_pm = [t for t in acc_nch if t["pmiss_vis"] < 18.0]
    acc_m = [t for t in acc_pm if 15.0 <= pair_mass(t["mus"][0], t["mus"][1]) <= 50.0]
    return {"n_generated": n, "n_two_signal_muons": len(two),
            "f_both_in_acceptance": frac(len(acc), n), "f_and_nch_ge5": frac(len(acc_nch), n),
            "f_and_pmiss_lt18": frac(len(acc_pm), n), "f_and_m_15_50": frac(len(acc_m), n),
            "m_true_q10_50_90": [round(float(v), 3) for v in np.percentile(
                [pair_mass(t["mus"][0], t["mus"][1]) for t in two], [10, 50, 90])] if two else None}


def analyse(reco, truth, nsim, cfg=None):
    n_used = min(nsim, len(truth)) if nsim else len(truth)
    r = {"n_truth_events": len(truth), "n_simulated_requested": n_used, "n_reco_events": len(reco)}
    r["generator_level"] = gen_level(truth[:n_used])
    al = align(reco, truth)
    pairs = [(ev, truth[j]) for ev, j in zip(reco, al) if j is not None]
    r["n_aligned"] = len(pairs)
    r["f_reco_aligned"] = frac(len(pairs), len(reco))

    # muon-level efficiencies (truth muons in acceptance, in aligned events)
    n_acc = n_trk = n_any = n_std = 0
    n_trk_used = 0
    dinv = {i: [] for i in range(len(P_BINS) - 1)}
    d0, z0, mchi2 = [], [], []
    dm, dm_rel, m_reco_matched, m_true_matched = [], [], [], []
    for (ev, tr), j in zip(pairs, [j for j in al if j is not None]):
        m = match_muons(tr, ev["tracks"])
        for mu, t in zip(tr["mus"], m):
            if not in_acc(mu):
                continue
            n_acc += 1
            if t is None:
                continue
            n_trk += 1
            if j < n_used:
                n_trk_used += 1
            n_any += is_muon(t)
            n_std += is_muon(t, "standard")
            d0.append(abs(t["d0"]))
            z0.append(abs(t["z0"]))
            if is_muon(t):
                mchi2.append(t["mchi2"])
            for b in range(len(P_BINS) - 1):
                if P_BINS[b] <= mu["p"] < P_BINS[b + 1]:
                    dinv[b].append(1.0 / t["p"] - 1.0 / mu["p"])
        if len(tr["mus"]) == 2 and m[0] is not None and m[1] is not None:
            mt = pair_mass(tr["mus"][0], tr["mus"][1])
            mr = pair_mass(m[0], m[1])
            dm.append(mr - mt)
            dm_rel.append((mr - mt) / mt)
            m_reco_matched.append(mr)
            m_true_matched.append(mt)
    n_acc_all = sum(1 for t in truth[:n_used] for mu in t["mus"] if in_acc(mu))
    r["muon_level"] = {"n_truth_mu_in_acc": n_acc, "eff_track": frac(n_trk, n_acc),
                       "n_truth_mu_in_acc_all_simulated": n_acc_all,
                       "eff_track_all": frac(n_trk_used, n_acc_all),
                       "eff_mutag_any_given_track": frac(n_any, n_trk),
                       "eff_mutag_standard_given_track": frac(n_std, n_trk),
                       "abs_d0_cm_q50_90": [round(float(v), 4) for v in np.percentile(d0, [50, 90])] if d0 else None,
                       "abs_z0_cm_q50_90": [round(float(v), 4) for v in np.percentile(z0, [50, 90])] if z0 else None,
                       "mu_chi2_q50_90": [round(float(v), 3) for v in np.percentile(mchi2, [50, 90])] if mchi2 else None}
    r["inv_p_resolution"] = [{"p_lo": P_BINS[b], "p_hi": P_BINS[b + 1], "n": len(v),
                              "sigma_inv_p": None if robust_sigma(v) is None else round(robust_sigma(v), 6)}
                             for b, v in dinv.items()]
    sig = robust_sigma(dm)
    core = [x for x in dm if abs(x) < 3.0]
    r["mass_resolution"] = {
        "n_pairs": len(dm),
        "median_dm": None if not dm else round(float(np.median(dm)), 4),
        "sigma_iqr": None if sig is None else round(sig, 4),
        "sigma_iqr_rel": None if robust_sigma(dm_rel) is None else round(robust_sigma(dm_rel), 5),
        "rms_core_3gev": None if not core else round(float(np.sqrt(np.mean(np.square(core)))), 4),
        "f_abs_dm_gt_2gev": frac(sum(1 for x in dm if abs(x) > 2.0), len(dm)),
        "median_m_true": None if not m_true_matched else round(float(np.median(m_true_matched)), 3),
        "median_m_reco": None if not m_reco_matched else round(float(np.median(m_reco_matched)), 3),
        "hist_dm_m3_p3_0p2": np.histogram(dm, bins=30, range=(-3, 3))[0].tolist() if dm else [],
        "aleph_sigma_at_30p4": round(math.sqrt(6e-4) * 30.4, 4),
    }

    # event selection (denominator: simulated events)
    cuts = {"aligned": 0, "ihad4": 0, "nctr4_ge5": 0, "os_mu_pair_15_50_any": 0,
            "pmiss_lt18": 0, "os_mu_pair_15_50_standard": 0, "truth_pair_selected": 0}
    btag = {wp: 0 for wp in BTAG_WP}
    btp3 = []
    reco_m = []
    selected_e = []
    for ev, tr in pairs:
        e = ev["e"]
        cuts["aligned"] += 1
        if e["ihad4"] <= 0:
            continue
        cuts["ihad4"] += 1
        if e["nctr4"] < 5:
            continue
        cuts["nctr4_ge5"] += 1
        pp = best_os_pair(ev["tracks"])
        if not pp:
            continue
        cuts["os_mu_pair_15_50_any"] += 1
        sx = sum(t["px"] for t in ev["tracks"])
        sy = sum(t["py"] for t in ev["tracks"])
        sz = sum(t["pz"] for t in ev["tracks"])
        if math.sqrt(sx * sx + sy * sy + sz * sz) >= 18.0:
            continue
        cuts["pmiss_lt18"] += 1
        selected_e.append(e)
        m = match_muons(tr, ev["tracks"])
        ids = {id(x) for x in m if x is not None}
        if len(ids) == 2 and any({id(a), id(b)} == ids for (_, a, b) in pp):
            cuts["truth_pair_selected"] += 1
        reco_m += [p[0] for p in pp]
        if best_os_pair(ev["tracks"], "standard"):
            cuts["os_mu_pair_15_50_standard"] += 1
        btp3.append(e["btp3"])
        for wp in BTAG_WP:
            if 0.0 <= e["btp3"] < wp:
                btag[wp] += 1
    r["selection_counts"] = cuts
    r["selection_eff_vs_simulated"] = {k: frac(v, n_used) for k, v in cuts.items()}
    r["btag_eff_after_selection"] = {str(wp): frac(v, cuts["pmiss_lt18"]) for wp, v in btag.items()}
    r["btag_eff_vs_simulated"] = {str(wp): frac(v, n_used) for wp, v in btag.items()}
    r["btp3_q10_50_90_selected"] = [round(float(v), 6) for v in np.percentile(btp3, [10, 50, 90])] if btp3 else None
    r["hemi_btag_after_selection"] = hemi_tag_summary(selected_e)
    # v0.10's rho_D numerator, kept as a cross-check of 0.3.0's dimusel_exact tag efficiency
    r["hemi_btag_after_selection_thrust"] = hemi_tag_summary([e for e in selected_e if thrust_ok(e)])
    r["hist_reco_os_mumu_15_50_0p5"] = np.histogram(reco_m, bins=70, range=(15, 50))[0].tolist() if reco_m else []
    # 0.3.0: the selection the data pass (PLAN 4e step 7); eff_sel enters N_exp (5f) and
    # tag_eff_selected is the rho_D numerator (5e)
    triples = [(ev, truth[j], j) for ev, j in zip(reco, al) if j is not None]
    r["dimusel_exact"] = dimusel_exact(triples, n_used, cfg)
    if "eff_sel" in r["dimusel_exact"]:
        r["dimusel_exact"]["ratio_to_0p1_selection"] = frac(r["dimusel_exact"]["counts"]["pair_selected"],
                                                            cuts["pmiss_lt18"])
    r["delsim_used_input"] = bool(len(dm) >= 0.3 * max(1, len(reco)))
    return r


def best_os_pair(tracks, level="any", lo=15.0, hi=50.0):
    """All opposite-sign muon-tagged pairs in acceptance with mass in [lo, hi]."""
    mus = [t for t in tracks if t["q"] != 0 and in_acc(t) and is_muon(t, level)]
    pairs = []
    for i in range(len(mus)):
        for j in range(i + 1, len(mus)):
            if mus[i]["q"] * mus[j]["q"] < 0:
                m = pair_mass(mus[i], mus[j])
                if lo <= m <= hi:
                    pairs.append((m, mus[i], mus[j]))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fadgen", required=True)
    ap.add_argument("--ev", required=True)
    ap.add_argument("--pa", required=True)
    ap.add_argument("--nsim", type=int, default=0)
    ap.add_argument("--config", help="JSON file of dimusel selection overrides (per period)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfg = None
    if a.config:
        with open(a.config) as fh:
            cfg = json.load(fh)
    truth = read_truth(a.fadgen)
    reco = read_ntuple(a.ev, a.pa)
    res = {"tool": VERSION, "made_by": "MV2 of Munim, Inc. (made with AI agents)"}
    res.update(analyse(reco, truth, a.nsim, cfg))
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("SIGANA_JSON_BEGIN")
    print(json.dumps(res, indent=1))
    print("SIGANA_JSON_END")


if __name__ == "__main__":
    main()
