#!/usr/bin/env python3
"""sigana: DELPHI detector response to a 30 GeV dimuon signal (simulation only).

Compares the generated signal events (DELSIM input, FADGEN format) with the reconstructed
short-DST events written by MV2's SKELANA USER02 (mv2user02s.car), and measures:
  - tracking and muon-identification efficiency for the two signal muons,
  - the efficiency of ALEPH-like event cuts and of DELPHI b-tag working points,
  - the dimuon mass resolution at 30 GeV and the 1/p resolution versus p,
  - impact parameters of prompt signal muons.
Everything here is simulation, so no blinding applies.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

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


def analyse(reco, truth, nsim):
    n_used = min(nsim, len(truth)) if nsim else len(truth)
    r = {"n_truth_events": len(truth), "n_simulated_requested": n_used, "n_reco_events": len(reco)}
    r["generator_level"] = gen_level(truth[:n_used])
    al = align(reco, truth)
    pairs = [(ev, truth[j]) for ev, j in zip(reco, al) if j is not None]
    r["n_aligned"] = len(pairs)
    r["f_reco_aligned"] = frac(len(pairs), len(reco))

    # muon-level efficiencies (truth muons in acceptance, in aligned events)
    n_acc = n_trk = n_any = n_std = 0
    dinv = {i: [] for i in range(len(P_BINS) - 1)}
    d0, z0, mchi2 = [], [], []
    dm, dm_rel, m_reco_matched, m_true_matched = [], [], [], []
    for ev, tr in pairs:
        m = match_muons(tr, ev["tracks"])
        for mu, t in zip(tr["mus"], m):
            if not in_acc(mu):
                continue
            n_acc += 1
            if t is None:
                continue
            n_trk += 1
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
    r["muon_level"] = {"n_truth_mu_in_acc": n_acc, "eff_track": frac(n_trk, n_acc),
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
    r["hist_reco_os_mumu_15_50_0p5"] = np.histogram(reco_m, bins=70, range=(15, 50))[0].tolist() if reco_m else []
    r["delsim_used_input"] = bool(len(dm) >= 0.3 * max(1, len(reco)))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fadgen", required=True)
    ap.add_argument("--ev", required=True)
    ap.add_argument("--pa", required=True)
    ap.add_argument("--nsim", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    truth = read_truth(a.fadgen)
    reco = read_ntuple(a.ev, a.pa)
    res = {"tool": "mv2 sigana 0.1.0", "made_by": "MV2 of Munim, Inc. (made with AI agents)"}
    res.update(analyse(reco, truth, a.nsim))
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("SIGANA_JSON_BEGIN")
    print(json.dumps(res, indent=1))
    print("SIGANA_JSON_END")


if __name__ == "__main__":
    main()
