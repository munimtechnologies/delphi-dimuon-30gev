#!/usr/bin/env python3
"""Blind-safe validation of the MV2DIMU ntuple (DELPHI open data, 1994).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

Reads <tag>_<file>.ev.txt.gz and .pa.txt.gz written by mv2user02.car and reports
detector-level checks: Z -> mu mu in low-multiplicity events, J/psi -> mu mu in hadronic
events, muon and electron tag rates, b-tag probability distribution, impact parameters
and missing momentum, data vs simulation.

Blinding (plan v0.2 sec. 5, stricter here): for DATA events with 5 or more charged tracks,
no dimuon mass at or above BLIND_MIN_GEV is ever stored, printed or histogrammed (only the
count of withheld pairs). Simulation is unrestricted.
"""
import argparse
import glob
import gzip
import json
import math
import os
from collections import Counter, defaultdict

MMU = 0.1056584
BLIND_MIN_GEV = 5.0
E_FIELDS = ["run", "evt", "ihad4", "nctr4", "nctrk", "nvecp", "nlep",
            "ecmas", "echar", "emneu", "ehneu",
            "btn1", "btn2", "btn3", "btp1", "btp2", "btp3", "bts1", "bts2", "bts3",
            "thx", "thy", "thz", "thr"]
P_INT = ["run", "evt", "i", "q", "lock", "kmu1", "kmu3", "kel1", "kel2", "vdrphi", "vdz"]
P_REAL = ["px", "py", "pz", "e", "mchi2", "qt4", "qt5", "d0", "z0", "d0bs"]


def parse_e(line):
    f = line.split()
    if not f or f[0] != "E" or len(f) != 1 + len(E_FIELDS):
        return None
    d = {}
    try:
        for k, v in zip(E_FIELDS, f[1:]):
            d[k] = int(v) if k in ("run", "evt", "ihad4", "nctr4", "nctrk", "nvecp", "nlep") else float(v)
    except ValueError:  # Fortran overflow asterisks
        return None
    return d


def parse_p(line):
    f = line.split()
    if not f or f[0] != "P" or len(f) != 1 + len(P_INT) + len(P_REAL):
        return None
    try:
        d = {k: int(v) for k, v in zip(P_INT, f[1:1 + len(P_INT)])}
        d.update({k: float(v) for k, v in zip(P_REAL, f[1 + len(P_INT):])})
    except ValueError:  # Fortran overflow asterisks
        return None
    d["p"] = math.sqrt(d["px"] ** 2 + d["py"] ** 2 + d["pz"] ** 2)
    return d


def pair_mass(a, b, m=MMU):
    """Invariant mass of two tracks with mass hypothesis m (GeV)."""
    e1 = math.sqrt(a["p"] ** 2 + m * m)
    e2 = math.sqrt(b["p"] ** 2 + m * m)
    px, py, pz = a["px"] + b["px"], a["py"] + b["py"], a["pz"] + b["pz"]
    m2 = (e1 + e2) ** 2 - (px * px + py * py + pz * pz)
    return math.sqrt(max(m2, 0.0))


def blinded_mass(a, b, is_data, nctr4):
    """Mass, or None when blinding forbids recording it (data, >= 5 charged tracks,
    m >= BLIND_MIN_GEV). A withheld mass is dropped at once and never stored, printed or
    histogrammed; only the number of withheld pairs is reported."""
    m = pair_mass(a, b)
    if is_data and nctr4 >= 5 and m >= BLIND_MIN_GEV:
        return None
    return m


def is_muon(t, level="any"):
    k = t["kmu1"]
    if level == "any":
        return k > 0
    if level == "standard":
        return (k >> 2) & 1 == 1
    raise ValueError(level)


def quantiles(xs, qs=(0.1, 0.5, 0.9)):
    if not xs:
        return None
    s = sorted(xs)
    return [round(s[min(len(s) - 1, int(q * len(s)))], 5) for q in qs]


def hist(xs, lo, hi, step):
    n = int(round((hi - lo) / step))
    h = [0] * n
    for x in xs:
        if lo <= x < hi:
            h[min(n - 1, int((x - lo) / step))] += 1
    return h


def read_sample(paths_ev, paths_pa):
    events, parts = {}, defaultdict(list)
    for p in paths_ev:
        with gzip.open(p, "rt") as fh:
            for ln in fh:
                d = parse_e(ln)
                if d:
                    events[(p, d["run"], d["evt"])] = d
    for p in paths_pa:
        key_file = p.replace(".pa.txt.gz", ".ev.txt.gz")
        with gzip.open(p, "rt") as fh:
            for ln in fh:
                d = parse_p(ln)
                if d:
                    parts[(key_file, d["run"], d["evt"])].append(d)
    return events, parts


def analyse(events, parts, is_data):
    r = {"n_events": len(events)}
    had = [e for e in events.values() if e["ihad4"] > 0]
    r["n_ihad4"] = len(had)
    r["n_nctr4_ge5"] = sum(1 for e in events.values() if e["nctr4"] >= 5)
    r["ecmas_q"] = quantiles([e["ecmas"] for e in events.values()])
    edges = [0.0, 1e-4, 1e-3, 1e-2, 1e-1, 1.0000001]
    bt = Counter()
    for e in had:
        x = e["btp3"]
        lab = "out_of_range"
        for lo, hi in zip(edges[:-1], edges[1:]):
            if lo <= x < hi:
                lab = "%g-%g" % (lo, min(hi, 1.0))
        bt[lab] += 1
    r["btag_event_prob_pos_ip"] = {k: round(v / max(1, len(had)), 5) for k, v in sorted(bt.items())}
    r["thrust_q"] = quantiles([e["thr"] for e in had])
    r["nlep_per_had_event"] = dict(sorted(Counter(min(e["nlep"], 4) for e in had).items()))

    kmu, kel, lockbit0 = Counter(), Counter(), Counter()
    d0s, z0s, d0bs, pmiss, zmm, jpsi_any, jpsi_std = [], [], [], [], [], [], []
    mc_os_all, mc_os_btag = [], []
    n_blind_skipped = 0
    for key, tracks in parts.items():
        ev = events.get(key)
        if ev is None:
            continue
        ch = [t for t in tracks if t["q"] != 0]
        sx = sum(t["px"] for t in tracks); sy = sum(t["py"] for t in tracks); sz = sum(t["pz"] for t in tracks)
        if ev["nctr4"] >= 5:
            pmiss.append(math.sqrt(sx * sx + sy * sy + sz * sz))
        mus = [t for t in ch if t["p"] > 2.0 and is_muon(t)]
        for t in ch:
            if t["p"] > 2.0:
                kmu[t["kmu1"]] += 1
                kel[t["kel1"]] += 1
        for t in mus:
            lockbit0[t["lock"] & 1] += 1
            d0s.append(abs(t["d0"])); z0s.append(abs(t["z0"])); d0bs.append(abs(t["d0bs"]))
        if ev["nctr4"] <= 4:
            hard = sorted([t for t in mus if t["p"] > 15.0], key=lambda t: -t["p"])
            if len(hard) >= 2 and hard[0]["q"] * hard[1]["q"] < 0:
                zmm.append(pair_mass(hard[0], hard[1]))
            continue
        for i in range(len(mus)):
            for j in range(i + 1, len(mus)):
                a, b = mus[i], mus[j]
                if a["q"] * b["q"] >= 0:
                    continue
                m = blinded_mass(a, b, is_data, ev["nctr4"])
                if m is None:
                    n_blind_skipped += 1
                    continue
                if m < BLIND_MIN_GEV:
                    jpsi_any.append(m)
                    if is_muon(a, "standard") and is_muon(b, "standard"):
                        jpsi_std.append(m)
                if not is_data:
                    mc_os_all.append(m)
                    if 0.0 <= ev["btp3"] < 0.01:
                        mc_os_btag.append(m)
    r["kmu1_values_p_gt2"] = {str(k): v for k, v in kmu.most_common(12)}
    r["kel1_values_p_gt2"] = {str(k): v for k, v in sorted(kel.items())}
    r["muon_lock_bit0"] = dict(lockbit0)
    r["muon_abs_d0_q"] = quantiles(d0s)
    r["muon_abs_z0_q"] = quantiles(z0s)
    r["muon_abs_d0bs_q"] = quantiles(d0bs)
    r["pmiss_lepton_had_events_q"] = quantiles(pmiss)
    r["zmumu"] = {"n": len(zmm), "hist_60_110_2gev": hist(zmm, 60, 110, 2), "q": quantiles(zmm)}
    r["jpsi_any"] = {"n": len(jpsi_any), "hist_2_4p5_0p1": hist(jpsi_any, 2.0, 4.5, 0.1)}
    r["jpsi_standard"] = {"n": len(jpsi_std), "hist_2_4p5_0p1": hist(jpsi_std, 2.0, 4.5, 0.1)}
    r["blind_pairs_not_computed"] = n_blind_skipped
    if not is_data:
        r["mc_os_dimuon_had_0_50_2p5gev"] = hist(mc_os_all, 0, 50, 2.5)
        r["mc_os_dimuon_had_btag001_0_50_2p5gev"] = hist(mc_os_btag, 0, 50, 2.5)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {"tool": "mv2dimu validate 0.1.0", "blind_min_gev": BLIND_MIN_GEV}
    for tag in ("data", "mc"):
        ev = sorted(glob.glob(os.path.join(a.dir, tag + "_*.ev.txt.gz")))
        pa = sorted(glob.glob(os.path.join(a.dir, tag + "_*.pa.txt.gz")))
        if not ev:
            res[tag] = {"n_files": 0}
            continue
        events, parts = read_sample(ev, pa)
        res[tag] = analyse(events, parts, is_data=(tag == "data"))
        res[tag]["n_files"] = len(ev)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print("VALIDATION_JSON_BEGIN")
    print(json.dumps(res, indent=1))
    print("VALIDATION_JSON_END")


if __name__ == "__main__":
    main()
