#!/usr/bin/env python3
"""btagcal: data-driven calibration of DELPHI's lifetime b-tag by hemisphere double-tagging,
for the DELPHI test of the ALEPH 30 GeV dimuon excess (plan section 4g, new in v0.7).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

Why: N_exp needs DELPHI's b-tag efficiency, and the working point should give about the 38 %
b efficiency ALEPH used. The short-DST ntuple carries no generator-level quark flavour, so the
efficiency is measured in data, the way the LEP R_b measurements did it. Each hadronic event has
two thrust hemispheres with lifetime probabilities QBTPRP(1), QBTPRP(2) (ntuple fields btp1,
btp2). A hemisphere is tagged if 0 <= P < w. With
    f_s = tagged hemispheres / (2 N),   f_d = events with both hemispheres tagged / N,
and a two-class model (b, and everything else "x"):
    f_s = R_b e_b + (1 - R_b) e_x
    f_d = R_b e_b^2 (1 + rho_b) + (1 - R_b) e_x^2
which is solved for e_b and e_x (closed form; rho_b is the b hemisphere correlation, 0 by default
and varied as a systematic). R_b = 0.21629 (PDG). Lumping charm with light quarks biases e_b a
little; this is reported as a limitation, not hidden.

Only 'E' lines (event-level words) are read: no lepton, no mass, nothing about the blind window.
Outputs per working point the raw counts (additive across files and jobs; combine with
--combine) and the solved efficiencies with delta-method statistical errors.

0.2.0 (plan v0.8): the b-tag is calibrated separately for each data-taking period (the vertex
detector measured R-phi only before 1994). --period LABEL records the period; --combine refuses
to add counts from different periods or from data and simulation, and sums n_input_files.

CLI:
  python btagcal.py --dir D [--dir D2] [--period y94] --out cal.json   (data files only)
  python btagcal.py --dir D --sample mc --out cal_mc.json               (simulation files only)
  python btagcal.py --combine a.json b.json --out total.json
"""
import argparse
import glob
import gzip
import json
import math
import os
import sys

import dimusel as D

VERSION = "mv2 btagcal 0.2.0"
RB = 0.21629          # PDG R_b
TARGET_EVENT_EFF = 0.38   # ALEPH's b efficiency (arXiv:1610.06536)
WPS = (0.3, 0.1, 0.03, 0.01, 0.003, 0.001, 3e-4, 1e-4, 3e-5, 1e-5)


def solve(fs, fd, rb=RB, rho=0.0):
    """Two-class double-tag solution. Returns (e_b, e_x) or (None, None) if unphysical."""
    a = rb * (1.0 + rho) + rb * rb / (1.0 - rb)
    b = -2.0 * fs * rb / (1.0 - rb)
    c = fs * fs / (1.0 - rb) - fd
    disc = b * b - 4.0 * a * c
    if disc < 0:
        return None, None
    eb = (-b + math.sqrt(disc)) / (2.0 * a)
    ex = (fs - rb * eb) / (1.0 - rb)
    return eb, ex


def event_eff(e):
    """Efficiency of 'at least one hemisphere tagged' for a class with hemisphere efficiency e
    (hemispheres treated as independent)."""
    return 1.0 - (1.0 - e) ** 2


def _moments(n00, n10, n01, n11):
    N = n00 + n10 + n01 + n11
    fs = (n10 + n01 + 2 * n11) / (2.0 * N)
    fd = n11 / float(N)
    ex2 = (n10 + n01) / (4.0 * N) + n11 / float(N)   # E[x^2], x = (t1 + t2) / 2
    var_fs = (ex2 - fs * fs) / N
    var_fd = fd * (1.0 - fd) / N
    cov = (fd - fs * fd) / N                           # E[x y] = f_d, y = t1 t2
    return N, fs, fd, var_fs, var_fd, cov


def calibrate_counts(c, rb=RB, rho=0.0):
    """c: dict n00, n10, n01, n11 (events by hemisphere tags). Returns the solution and errors."""
    n00, n10, n01, n11 = c["n00"], c["n10"], c["n01"], c["n11"]
    if n00 + n10 + n01 + n11 == 0:
        return None
    N, fs, fd, vs, vd, cv = _moments(n00, n10, n01, n11)
    eb, ex = solve(fs, fd, rb, rho)
    out = dict(N=N, f_s=fs, f_d=fd, e_b=eb, e_x=ex)
    if eb is None:
        return out
    # delta method with numerical derivatives
    h_s = max(1e-7, 1e-4 * fs)
    h_d = max(1e-9, 1e-4 * fd)

    def grads(k):
        ps = solve(fs + h_s, fd, rb, rho)[k]
        ms = solve(fs - h_s, fd, rb, rho)[k]
        pd = solve(fs, fd + h_d, rb, rho)[k]
        md = solve(fs, fd - h_d, rb, rho)[k]
        if None in (ps, ms, pd, md):
            return None
        return (ps - ms) / (2 * h_s), (pd - md) / (2 * h_d)

    for k, name in ((0, "e_b"), (1, "e_x")):
        g = grads(k)
        if g is None:
            out[name + "_err"] = None
        else:
            v = g[0] ** 2 * vs + g[1] ** 2 * vd + 2 * g[0] * g[1] * cv
            out[name + "_err"] = math.sqrt(max(v, 0.0))
    out["purity_single"] = rb * eb / fs if fs > 0 else None
    out["event_eff_b"] = event_eff(eb)
    out["event_eff_x"] = event_eff(max(ex, 0.0))
    ftag = rb * out["event_eff_b"] + (1 - rb) * out["event_eff_x"]
    out["event_purity"] = rb * out["event_eff_b"] / ftag if ftag > 0 else None
    return out


def pick_wp(points, target=TARGET_EVENT_EFF):
    """points: list of (w, event_eff_b) for decreasing w. Log-linear interpolation of w where
    the event efficiency crosses target. Returns w or None."""
    pts = [(w, e) for w, e in points if e is not None and w > 0]
    pts.sort(key=lambda t: -t[0])
    for (w1, e1), (w2, e2) in zip(pts, pts[1:]):
        if (e1 - target) * (e2 - target) <= 0 and e1 != e2:
            t = (target - e1) / (e2 - e1)
            return math.exp(math.log(w1) + t * (math.log(w2) - math.log(w1)))
    return None


class Counter:
    def __init__(self, cfg=None, wps=WPS):
        self.sel = D.Selector(cfg)
        self.wps = tuple(wps)
        self.cf = {k: 0 for k in ("events", "ihad4", "nctr4", "thrust", "hadronic")}
        self.n_bad_hemi = 0
        self.counts = {repr(w): dict(n00=0, n10=0, n01=0, n11=0, n_event_tag=0) for w in self.wps}

    def add(self, e):
        if not self.sel._hadronic(e, self.cf):
            return
        p1, p2, p3 = e["btp1"], e["btp2"], e["btp3"]
        if p1 < 0 or p2 < 0 or p1 > 1 or p2 > 1:
            self.n_bad_hemi += 1
            return
        for w in self.wps:
            c = self.counts[repr(w)]
            t1, t2 = p1 < w, p2 < w
            c["n%d%d" % (t1, t2)] += 1
            c["n_event_tag"] += 1 if 0.0 <= p3 < w else 0

    def add_file(self, path):
        with gzip.open(path, "rt", errors="replace") as fh:
            for ln in fh:
                e = D.parse_e(ln)
                if e:
                    self.add(e)

    def raw(self):
        return {"tool": VERSION, "rb": RB, "config": self.sel.c, "cutflow": self.cf,
                "n_bad_hemisphere": self.n_bad_hemi, "counts": self.counts}


def summarise(raw, rhos=(0.0, 0.03)):
    out = dict(raw)
    table = {}
    for wkey, c in raw["counts"].items():
        row = {"rho_%g" % r: calibrate_counts(c, raw.get("rb", RB), r) for r in rhos}
        n = c["n00"] + c["n10"] + c["n01"] + c["n11"]
        row["event_tag_rate_btp3"] = c["n_event_tag"] / float(n) if n else None
        table[wkey] = row
    out["solution"] = table
    pts = []
    for wkey, row in table.items():
        s = row["rho_0"]
        pts.append((float(wkey), s.get("event_eff_b") if s else None))
    out["wp_hemisphere_for_event_eff_%.2f" % TARGET_EVENT_EFF] = pick_wp(pts)
    return out


def combine(raws):
    """Add the counts of several runs of ONE period and ONE sample (data or mc)."""
    if not raws:
        raise ValueError("nothing to combine")
    tot = json.loads(json.dumps(raws[0]))
    for r in raws[1:]:
        if set(r["counts"]) != set(tot["counts"]):
            raise ValueError("working-point grids differ")
        if r.get("sample") != tot.get("sample"):
            raise ValueError("cannot add %r counts to %r counts" % (r.get("sample"), tot.get("sample")))
        if r.get("period") != tot.get("period"):
            raise ValueError("periods differ (%r, %r): calibrate each period on its own"
                             % (tot.get("period"), r.get("period")))
        if r.get("config") != tot.get("config"):
            raise ValueError("hadronic selections differ")
        for k in tot["cutflow"]:
            tot["cutflow"][k] += r["cutflow"][k]
        tot["n_bad_hemisphere"] += r["n_bad_hemisphere"]
        for w, c in r["counts"].items():
            for k in c:
                tot["counts"][w][k] += c[k]
    tot["n_input_files"] = sum(r.get("n_input_files", 0) for r in raws)
    tot["n_combined"] = len(raws)
    tot["tool"] = VERSION
    tot.pop("solution", None)
    tot = {k: v for k, v in tot.items() if not k.startswith("wp_hemisphere")}
    return tot


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", action="append", default=[])
    ap.add_argument("--combine", nargs="+")
    ap.add_argument("--sample", choices=("data", "mc"), default="data")
    ap.add_argument("--period", help="data-taking period label, e.g. y94 (with --dir)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.combine:
        if a.dir or a.period:
            ap.error("--combine takes no --dir or --period")
        raws = []
        for p in a.combine:
            with open(p) as fh:
                raws.append(json.load(fh))
        raw = combine(raws)
    else:
        if not a.dir:
            ap.error("--dir or --combine is required")
        if a.period is not None and not D.PERIOD_RE.match(a.period):
            ap.error("--period must be 1-32 characters of [A-Za-z0-9_-]")
        cnt = Counter()
        files = sorted(set(f for d in a.dir for f in glob.glob(os.path.join(d, "**", "*.ev.txt.gz"),
                                                                recursive=True)))
        want_data = a.sample == "data"
        files = [f for f in files if D.is_data_tag(f) == want_data]
        for f in files:
            cnt.add_file(f)
        raw = cnt.raw()
        raw["n_input_files"] = len(files)
        raw["sample"] = a.sample
        raw["period"] = a.period
    res = summarise(raw)
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    brief = {w: {"f_s": round(r["rho_0"]["f_s"], 5) if r["rho_0"] else None,
                 "e_b": r["rho_0"] and r["rho_0"]["e_b"] and round(r["rho_0"]["e_b"], 4),
                 "event_eff_b": r["rho_0"] and r["rho_0"].get("event_eff_b") and round(r["rho_0"]["event_eff_b"], 4)}
             for w, r in res["solution"].items()}
    print(json.dumps({"cutflow": res["cutflow"], "per_wp": brief,
                      "wp": res["wp_hemisphere_for_event_eff_%.2f" % TARGET_EVENT_EFF]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
