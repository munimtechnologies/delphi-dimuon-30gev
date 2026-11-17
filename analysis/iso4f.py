#!/usr/bin/env python3
"""iso4f: isolated opposite-sign dimuons in DELPHI SIMULATION, with exactly dimusel's selection, for
the isolated test of the ALEPH 30 GeV dimuon excess (NOTE-fourfermion.md).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

dimusel 0.3.0 has an isolated category only together with the b-tag (os_mumu_btag_iso). A boson
made with b quarks has both muons isolated in 92-95 % of events (xkin-v1) but passes the b-tag only
38 % of the time, while b-decay muons are almost never isolated (0 of 525 Pythia events). The
isolated selection WITHOUT the b-tag is therefore the most sensitive test of the boson
reading; its irreducible background is four-fermion e+e- -> mu+ mu- q qbar, which DELPHI
simulated with EXCALIBUR at the Z pole for every year (CERN Open Data records 81032, 81072,
81146, 81459, 81539; sigma = 3.56 +- 0.02 pb).

This module reads MV2DIMU ntuples of simulation only (file names starting with "mc" or "sig";
real-data files are refused, so nothing here can unblind data) and writes, per input file and
summed: dimusel's cut flow, every opposite-sign muon pair passing dimusel's cuts with its mass,
b-tag flag, both muons' smallest angle to a jet above iso_jet_emin, and the isolation flag;
plus counts in 5 GeV bins (0-90) and in the 26-35 GeV window for: all pairs, isolated, isolated
and b-tagged (must equal dimusel's os_mumu_btag_iso; tested), isolated and untagged.
The event loop is dimusel.Selector.process_event's own sequence of calls (hadronic, b-tag,
missing momentum, leptons, anti-kt jets without leptons, isolation), reusing its functions.
"""
import argparse
import glob
import gzip
import json
import math
import os
import sys

import dimusel as D

VERSION = "mv2 iso4f 0.1.0"
BIN5 = 5.0
NBIN5 = 18
CATS = ("all", "iso", "iso_btag", "iso_untagged")


def min_jet_angle(lep, jets, emin):
    u = D._unit((lep["px"], lep["py"], lep["pz"]))
    best = 180.0
    for j in jets:
        if j[0] <= emin:
            continue
        v = D._unit(j[1:])
        c = max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1] + u[2] * v[2]))
        best = min(best, math.degrees(math.acos(c)))
    return best


def new_cutflow():
    return {k: 0 for k in ("events", "ihad4", "nctr4", "thrust", "hadronic", "btag", "antitag",
                           "with_P_lines", "pmiss_pass", "two_leptons", "os_mumu_pairs")}


def event_pairs(sel, e, parts, cf):
    """dimusel's selection for one event; returns the opposite-sign muon pairs as dicts."""
    c = sel.c
    if not sel._hadronic(e, cf):
        return []
    bt, at = sel._btag(e), sel._antitag(e)
    cf["btag"] += bt
    cf["antitag"] += at
    if not parts:
        return []
    cf["with_P_lines"] += 1
    sx = sum(t["px"] for t in parts)
    sy = sum(t["py"] for t in parts)
    sz = sum(t["pz"] for t in parts)
    if math.sqrt(sx * sx + sy * sy + sz * sz) >= c["pmiss_max"]:
        return []
    cf["pmiss_pass"] += 1
    mus = [t for t in parts if D.lepton_ok(t, c) and D.is_muon(t, c["mu_level"])]
    mu_ids = {t["i"] for t in mus}
    els = [t for t in parts if t["i"] not in mu_ids and D.lepton_ok(t, c)
           and D.is_electron(t, c["el_min"])]
    if len(mus) + len(els) < 2:
        return []
    cf["two_leptons"] += 1
    lep_ids = mu_ids | {t["i"] for t in els}
    jet_in = [[t["e"], t["px"], t["py"], t["pz"]] for t in parts
              if t["i"] not in lep_ids and abs(t["cth"]) < 0.98 and t["e"] > 0]
    jets = D.antikt_jets(jet_in, 0.4)
    out = []
    for i in range(len(mus)):
        for j in range(i + 1, len(mus)):
            a, b = mus[i], mus[j]
            if a["q"] * b["q"] >= 0:
                continue
            cf["os_mumu_pairs"] += 1
            iso = D.isolated(a, jets, c) and D.isolated(b, jets, c)
            out.append({"run": e["run"], "evt": e["evt"],
                        "m": round(D.pair_mass(a, b, D.MMU, D.MMU), 4),
                        "btag": bool(bt), "iso": bool(iso),
                        "ang": [round(min_jet_angle(a, jets, c["iso_jet_emin"]), 2),
                                round(min_jet_angle(b, jets, c["iso_jet_emin"]), 2)],
                        "p": [round(a["p"], 3), round(b["p"], 3)],
                        "njets_above_emin": sum(1 for x in jets if x[0] > c["iso_jet_emin"])})
    return out


def categories(pr):
    cats = ["all"]
    if pr["iso"]:
        cats.append("iso")
        cats.append("iso_btag" if pr["btag"] else "iso_untagged")
    return cats


def empty_counts():
    return {k: {"bins5_0_90": [0] * NBIN5, "window_26_35": 0, "range_15_50": 0} for k in CATS}


def add_pair(counts, pr):
    m = pr["m"]
    for k in categories(pr):
        if 0.0 <= m < BIN5 * NBIN5:
            counts[k]["bins5_0_90"][int(m / BIN5)] += 1
        if D.in_window(m):
            counts[k]["window_26_35"] += 1
        if 15.0 <= m < 50.0:
            counts[k]["range_15_50"] += 1


def read_file(ev_path):
    events = []
    with gzip.open(ev_path, "rt", errors="replace") as fh:
        for ln in fh:
            d = D.parse_e(ln)
            if d:
                events.append(d)
    parts = {}
    pa_path = ev_path.replace(".ev.txt.gz", ".pa.txt.gz")
    if os.path.exists(pa_path):
        with gzip.open(pa_path, "rt", errors="replace") as fh:
            for ln in fh:
                d = D.parse_p(ln)
                if d:
                    parts.setdefault((d["run"], d["evt"]), []).append(d)
    return events, parts


def run(paths, cfg=None):
    sel = D.Selector(cfg)
    res = {"tool": VERSION, "dimusel": D.VERSION, "config": sel.c, "files": {},
           "total": {"cutflow": new_cutflow(), "counts": empty_counts()}, "pairs": []}
    for p in paths:
        if D.is_data_tag(p):
            raise SystemExit("iso4f reads simulation only; refusing data file %s" % p)
        events, parts = read_file(p)
        cf, cnt = new_cutflow(), empty_counts()
        for e in events:
            for pr in event_pairs(sel, e, parts.get((e["run"], e["evt"])), cf):
                add_pair(cnt, pr)
                add_pair(res["total"]["counts"], pr)
                pr["file"] = os.path.basename(p)
                res["pairs"].append(pr)
        for k, v in cf.items():
            res["total"]["cutflow"][k] += v
        res["files"][os.path.basename(p)] = {"cutflow": cf, "counts": cnt}
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", required=True)
    ap.add_argument("--glob", default="mc*.ev.txt.gz")
    ap.add_argument("--config")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    cfg = None
    if a.config:
        with open(a.config) as fh:
            cfg = json.load(fh)
    paths = sorted(glob.glob(os.path.join(a.dir, "**", a.glob), recursive=True))
    res = run(paths, cfg)
    res["n_input_files"] = len(paths)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    summ = dict(res)
    summ.pop("pairs")
    print(json.dumps(summ, indent=1))
    win = [pr for pr in res["pairs"] if 20.0 <= pr["m"] < 40.0]
    print("PAIRS_20_40 (%d)" % len(win))
    for pr in win:
        print(json.dumps(pr))
    return 0


if __name__ == "__main__":
    sys.exit(main())
