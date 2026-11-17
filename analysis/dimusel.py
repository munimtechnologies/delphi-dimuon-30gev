#!/usr/bin/env python3
"""dimusel: event selection and blinded spectra for the DELPHI test of the ALEPH 30 GeV
dimuon excess (plan sections 4, 5 and 5b).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

Input: the MV2DIMU ntuple written by ntuple/mv2user02.car, one pair of files per DELPHI
input file: <tag>_<name>.ev.txt.gz ('E' lines, every event) and <tag>_<name>.pa.txt.gz
('P' lines, every particle of events with at least two lepton candidates). Files whose tag
starts with "mc" or "sig" are simulation; everything else is treated as real data.

Output: one JSON file with the cut flow, the hadronic and b-tagged event counts (the
denominators for N_exp), and per-category mass histograms in the 700 bins of 50 MeV over
15-50 GeV used by stats/dimustat.py, plus a coarse 0-90 GeV histogram in 0.5 GeV bins.

Blinding (plan section 5; fixed in v0.1, applied more strictly here): in real data, for the
BLINDED categories (every opposite-sign mumu and ee category: b-tagged, isolated, untagged
and anti-tagged), no pair with a mass in
[26, 35) GeV is stored, counted, printed or histogrammed. Histogram bins overlapping the
window are written as null. No count that could be subtracted to recover the window is
written (the categories carry no "total" for data). The window opens only with
--unblind <PLAN.md>, where the file's first line must read "# Analysis plan v1.x"; the
file's SHA-256 is then recorded in the output.
Controls (same-sign mumu and all e-mu pairs) and simulation are never blinded.
"""
import argparse
import glob
import gzip
import hashlib
import json
import math
import os
import re
import sys

MMU = 0.1056584
MEL = 0.000511
WIN_LO, WIN_HI = 26.0, 35.0
FINE_LO, FINE_HI, FINE_BW = 15.0, 50.0, 0.05
NFINE = 700
COARSE_LO, COARSE_HI, COARSE_BW = 0.0, 90.0, 0.5
NCOARSE = 180

E_FIELDS = ["run", "evt", "ihad4", "nctr4", "nctrk", "nvecp", "nlep",
            "ecmas", "echar", "emneu", "ehneu",
            "btn1", "btn2", "btn3", "btp1", "btp2", "btp3", "bts1", "bts2", "bts3",
            "thx", "thy", "thz", "thr"]
E_INT = ("run", "evt", "ihad4", "nctr4", "nctrk", "nvecp", "nlep")
P_INT = ["run", "evt", "i", "q", "lock", "kmu1", "kmu3", "kel1", "kel2", "vdrphi", "vdz"]
P_REAL = ["px", "py", "pz", "e", "mchi2", "qt4", "qt5", "d0", "z0", "d0bs"]

# Selection defaults. Values marked TBD are placeholders until plan v1.0 fixes them from
# the validation run (4d) and simulation (4e); they are all command-line/config options.
DEFAULTS = dict(
    min_nctr4=5,            # >= 5 good charged tracks (plan 4.1)
    need_ihad4=True,        # team-4 hadronic tag (plan 4.1)
    thrust_cos_max=0.866,   # thrust axis 30-150 degrees (plan 4.1, as arXiv:2510.18762)
    btag_wp=0.01,           # TBD: event b-tag probability QBTPRP(3) below this = b-tagged
    antitag_min=0.1,        # inverted b-tag control: QBTPRP(3) above this
    mu_level="any",         # "any" MUCAL2 tag (KMUID(1) > 0) or "standard" (bit 2)
    el_min=4,               # ELECID KELID(1) >= 4 ("standard"); KELID(2) != 0 = conversion
    p_min=2.5,              # lepton momentum (GeV)
    cos_max=0.95,           # lepton |cos theta|
    d0_max=0.2,             # TBD: |d0| to the primary vertex (cm)
    z0_max=1.0,             # TBD: |z0| to the primary vertex (cm)
    pmiss_max=18.0,         # visible missing momentum (GeV), ALEPH's cascade veto
    iso_deg=20.0,           # isolated selection: both leptons > iso_deg from every jet
    iso_jet_emin=3.0,       # ... with E > iso_jet_emin, anti-kt R = 0.4, leptons removed
)

# Stricter than the plan's letter: the plan allows the inverted-b-tag mumu control before
# unblinding, but untagged and anti-tagged Z -> b bbar events would still carry most of a
# real signal (the b-tag keeps only about 38 % of b events). So every opposite-sign
# same-flavour category stays blind in data; only same-sign and e-mu controls are open.
BLINDED = ("os_mumu_btag", "os_mumu_btag_iso", "os_mumu_untagged", "os_mumu_antitag",
           "os_ee_btag", "os_ee_btag_iso", "os_ee_antitag")
CONTROLS = ("ss_mumu_btag", "ss_mumu_untagged", "os_emu_btag", "ss_emu_btag", "os_emu_untagged")


def parse_e(line):
    f = line.split()
    if not f or f[0] != "E" or len(f) != 1 + len(E_FIELDS):
        return None
    try:
        return {k: (int(v) if k in E_INT else float(v)) for k, v in zip(E_FIELDS, f[1:])}
    except ValueError:  # Fortran overflow asterisks
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
    d["cth"] = d["pz"] / d["p"] if d["p"] > 0 else 0.0
    return d


def pair_mass(a, b, ma, mb):
    e1 = math.sqrt(a["p"] ** 2 + ma * ma)
    e2 = math.sqrt(b["p"] ** 2 + mb * mb)
    px, py, pz = a["px"] + b["px"], a["py"] + b["py"], a["pz"] + b["pz"]
    return math.sqrt(max((e1 + e2) ** 2 - (px * px + py * py + pz * pz), 0.0))


def in_window(m):
    return WIN_LO <= m < WIN_HI


def is_muon(t, level):
    k = t["kmu1"]
    if level == "any":
        return k > 0
    if level == "standard":
        return (k >> 2) & 1 == 1
    raise ValueError(level)


def is_electron(t, el_min):
    return t["kel1"] >= el_min and t["kel2"] == 0


def lepton_ok(t, c):
    return (t["q"] != 0 and t["p"] > c["p_min"] and abs(t["cth"]) < c["cos_max"]
            and abs(t["d0"]) < c["d0_max"] and abs(t["z0"]) < c["z0_max"])


def _unit(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return (v[0] / n, v[1] / n, v[2] / n) if n > 0 else (0.0, 0.0, 1.0)


def antikt_jets(parts, R=0.4):
    """e+e- anti-kt (ee_genkt, p = -1, E-scheme) on [E, px, py, pz] lists; pure Python, so
    the module has no numpy dependency. Same definition as xkin/evana.py ee_genkt."""
    act = [list(x) for x in parts if x[0] > 0]
    jets = []
    denom = 1.0 - math.cos(R)
    while act:
        if len(act) == 1:
            jets.append(act.pop())
            break
        us = [_unit(a[1:]) for a in act]
        ep = [a[0] ** -2 for a in act]
        best, bi, bj = float("inf"), -1, -1
        for i in range(len(act)):
            for j in range(i + 1, len(act)):
                cij = us[i][0] * us[j][0] + us[i][1] * us[j][1] + us[i][2] * us[j][2]
                d = min(ep[i], ep[j]) * (1.0 - max(-1.0, min(1.0, cij))) / denom
                if d < best:
                    best, bi, bj = d, i, j
        ib = min(range(len(act)), key=lambda k: ep[k])
        if best < ep[ib]:
            act[bi] = [x + y for x, y in zip(act[bi], act[bj])]
            del act[bj]
        else:
            jets.append(act.pop(ib))
    return sorted(jets, key=lambda j: -j[0])


def isolated(lep, jets, c):
    u = _unit((lep["px"], lep["py"], lep["pz"]))
    for j in jets:
        if j[0] <= c["iso_jet_emin"]:
            continue
        v = _unit(j[1:])
        cang = max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1] + u[2] * v[2]))
        if math.degrees(math.acos(cang)) <= c["iso_deg"]:
            return False
    return True


class Hist:
    __slots__ = ("fine", "coarse")

    def __init__(self):
        self.fine = [0] * NFINE
        self.coarse = [0] * NCOARSE

    def fill(self, m):
        if FINE_LO <= m < FINE_HI:
            self.fine[min(NFINE - 1, int((m - FINE_LO) / FINE_BW + 1e-9))] += 1
        if COARSE_LO <= m < COARSE_HI:
            self.coarse[min(NCOARSE - 1, int((m - COARSE_LO) / COARSE_BW + 1e-9))] += 1


def _blind_bins(h, lo, bw, n):
    out = []
    for i in range(n):
        a, b = lo + i * bw, lo + (i + 1) * bw
        out.append(None if (b > WIN_LO + 1e-9 and a < WIN_HI - 1e-9) else h[i])
    return out


class Selector:
    def __init__(self, cfg=None, unblind=False):
        self.c = dict(DEFAULTS)
        if cfg:
            unknown = set(cfg) - set(DEFAULTS)
            if unknown:
                raise ValueError("unknown config keys: %s" % sorted(unknown))
            self.c.update(cfg)
        self.unblind = unblind
        self.samples = {}

    def _sample(self, kind):
        if kind not in self.samples:
            self.samples[kind] = dict(
                files=0, cutflow={k: 0 for k in (
                    "events", "ihad4", "nctr4", "thrust", "hadronic", "btag", "antitag",
                    "with_P_lines", "pmiss_pass")},
                hists={k: Hist() for k in BLINDED + CONTROLS})
        return self.samples[kind]

    def _hadronic(self, e, cf):
        c = self.c
        cf["events"] += 1
        if c["need_ihad4"] and e["ihad4"] <= 0:
            return False
        cf["ihad4"] += 1
        if e["nctr4"] < c["min_nctr4"]:
            return False
        cf["nctr4"] += 1
        if c["thrust_cos_max"] < 1.0:  # >= 1 disables the cut
            n = math.sqrt(e["thx"] ** 2 + e["thy"] ** 2 + e["thz"] ** 2)
            if n <= 0 or abs(e["thz"]) / n > c["thrust_cos_max"]:
                return False
        cf["thrust"] += 1
        cf["hadronic"] += 1
        return True

    def _btag(self, e):
        return 0.0 <= e["btp3"] < self.c["btag_wp"]

    def _antitag(self, e):
        return e["btp3"] > self.c["antitag_min"]

    def _fill(self, s, cat, m, is_data):
        """The ONLY place a mass enters a histogram. Blinded data pairs in the window are
        dropped here without any trace."""
        if is_data and not self.unblind and cat in BLINDED and in_window(m):
            return
        s["hists"][cat].fill(m)

    def process_event(self, e, parts, is_data):
        s = self._sample("data" if is_data else "mc")
        cf = s["cutflow"]
        if not self._hadronic(e, cf):
            return
        bt, at = self._btag(e), self._antitag(e)
        cf["btag"] += bt
        cf["antitag"] += at
        if not parts:
            return
        cf["with_P_lines"] += 1
        c = self.c
        sx = sum(t["px"] for t in parts)
        sy = sum(t["py"] for t in parts)
        sz = sum(t["pz"] for t in parts)
        if math.sqrt(sx * sx + sy * sy + sz * sz) >= c["pmiss_max"]:
            return
        cf["pmiss_pass"] += 1
        mus = [t for t in parts if lepton_ok(t, c) and is_muon(t, c["mu_level"])]
        mu_ids = {t["i"] for t in mus}
        els = [t for t in parts if t["i"] not in mu_ids and lepton_ok(t, c)
               and is_electron(t, c["el_min"])]
        if len(mus) + len(els) < 2:
            return
        lep_ids = mu_ids | {t["i"] for t in els}
        jet_in = [[t["e"], t["px"], t["py"], t["pz"]] for t in parts
                  if t["i"] not in lep_ids and abs(t["cth"]) < 0.98 and t["e"] > 0]
        jets = antikt_jets(jet_in, 0.4)
        iso = {t["i"]: isolated(t, jets, c) for t in mus + els}

        def pairs(xs, ys=None):
            if ys is None:
                for i in range(len(xs)):
                    for j in range(i + 1, len(xs)):
                        yield xs[i], xs[j]
            else:
                for a in xs:
                    for b in ys:
                        yield a, b

        for a, b in pairs(mus):
            m = pair_mass(a, b, MMU, MMU)
            if a["q"] * b["q"] < 0:
                if bt:
                    self._fill(s, "os_mumu_btag", m, is_data)
                    if iso[a["i"]] and iso[b["i"]]:
                        self._fill(s, "os_mumu_btag_iso", m, is_data)
                else:
                    self._fill(s, "os_mumu_untagged", m, is_data)
                if at:
                    self._fill(s, "os_mumu_antitag", m, is_data)
            else:
                self._fill(s, "ss_mumu_btag" if bt else "ss_mumu_untagged", m, is_data)
        for a, b in pairs(els):
            if a["q"] * b["q"] >= 0:
                continue
            m = pair_mass(a, b, MEL, MEL)
            if bt:
                self._fill(s, "os_ee_btag", m, is_data)
                if iso[a["i"]] and iso[b["i"]]:
                    self._fill(s, "os_ee_btag_iso", m, is_data)
            if at:
                self._fill(s, "os_ee_antitag", m, is_data)
        for a, b in pairs(mus, els):
            m = pair_mass(a, b, MMU, MEL)
            if a["q"] * b["q"] < 0:
                self._fill(s, "os_emu_btag" if bt else "os_emu_untagged", m, is_data)
            elif bt:
                self._fill(s, "ss_emu_btag", m, is_data)

    def process_file(self, ev_path, is_data):
        pa_path = ev_path.replace(".ev.txt.gz", ".pa.txt.gz")
        events = []
        with gzip.open(ev_path, "rt", errors="replace") as fh:
            for ln in fh:
                d = parse_e(ln)
                if d:
                    events.append(d)
        parts = {}
        if os.path.exists(pa_path):
            with gzip.open(pa_path, "rt", errors="replace") as fh:
                for ln in fh:
                    d = parse_p(ln)
                    if d:
                        parts.setdefault((d["run"], d["evt"]), []).append(d)
        self._sample("data" if is_data else "mc")["files"] += 1
        for e in events:
            self.process_event(e, parts.get((e["run"], e["evt"])), is_data)

    def result(self):
        out = {"tool": "mv2 dimusel 0.1.0", "config": self.c, "unblinded": self.unblind,
               "window_gev": [WIN_LO, WIN_HI], "blinded_categories": list(BLINDED),
               "fine_bins": [FINE_LO, FINE_HI, FINE_BW], "coarse_bins": [COARSE_LO, COARSE_HI, COARSE_BW],
               "samples": {}}
        for kind, s in self.samples.items():
            cats = {}
            for name, h in s["hists"].items():
                blind = kind == "data" and not self.unblind and name in BLINDED
                if blind:
                    cats[name] = {"blinded": True,
                                  "fine": _blind_bins(h.fine, FINE_LO, FINE_BW, NFINE),
                                  "coarse": _blind_bins(h.coarse, COARSE_LO, COARSE_BW, NCOARSE)}
                else:
                    cats[name] = {"blinded": False, "fine": h.fine, "coarse": h.coarse,
                                  "n_15_50": sum(h.fine)}
            out["samples"][kind] = {"files": s["files"], "cutflow": s["cutflow"], "categories": cats}
        return out


def is_data_tag(path):
    base = os.path.basename(path).lower()
    return not (base.startswith("mc") or base.startswith("sig"))


def check_unblind_plan(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    first = raw.decode("utf-8", "replace").splitlines()[0] if raw else ""
    if not re.match(r"^# Analysis plan v1\.\d+\b", first):
        raise SystemExit("refusing to unblind: %s does not start with '# Analysis plan v1.x'" % path)
    return hashlib.sha256(raw).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", action="append", required=True, help="ntuple folder (repeatable)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", help="JSON file with selection overrides")
    ap.add_argument("--unblind", metavar="PLAN_MD")
    a = ap.parse_args(argv)
    cfg = None
    if a.config:
        with open(a.config) as fh:
            cfg = json.load(fh)
    sha = check_unblind_plan(a.unblind) if a.unblind else None
    sel = Selector(cfg, unblind=bool(sha))
    files = sorted(set(f for d in a.dir for f in glob.glob(os.path.join(d, "**", "*.ev.txt.gz"),
                                                              recursive=True)))
    for f in files:
        sel.process_file(f, is_data_tag(f))
    res = sel.result()
    res["unblind_plan_sha256"] = sha
    res["n_input_files"] = len(files)
    with open(a.out, "w") as fh:
        json.dump(res, fh)
    summ = {k: {"files": v["files"], "cutflow": v["cutflow"]} for k, v in res["samples"].items()}
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
