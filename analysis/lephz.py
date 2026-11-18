#!/usr/bin/env python3
"""lephz: do the four LEP1 Standard Model Higgs searches (ALEPH, DELPHI, L3, OPAL; e+e- -> H Z*,
Z* -> mu+ mu-) leave room for a boson reading of the ALEPH 30 GeV dimuon excess
(arXiv:1610.06536 v9: 32.31 +- 10.87 events at 30.40 GeV, Gamma 1.78 GeV)?

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

analysis/efhz.py 0.1.0 confronts the boson models (V, S radiated off b quarks; P = Z -> h A) with
ALEPH's own LEP1 Higgs search. This module adds the other three LEP1 searches, whose cuts and
candidates MV2's reading agents read on 2026-11-18 (readings/lephz-notes.md), and combines all
four. Hadron level (Pythia 8), no detector simulation, muon identification as a factor.

Searches (selection as coded here; "stand-in" marks a value the reading did not give):
  ALEPH96  PLB 384 (1996) 427: ~4.5M hadronic Z 1989-95. efhz's nominal H l+ l- selection
           (PLB 313 (1993) 299 cuts: p > 3, p1 + p2 > 20, m_ll > 5, sum pT to thrust > 15 GeV,
           ONE lepton isolated, >= 6 (8) tracks, recoil > 40 GeV). The 1996 paper adds a b-tag
           (P_uds < 0.05) that the reading lists among the H mu mu cuts: a factor BTAG (0.8
           stand-in; the boson events contain b bbar). Candidates: three, Higgs (recoil) masses
           49.7 +- 0.5, 51.5 +- 0.5, 66.9 +- 0.3 GeV; m_ll not given.
  L3_96    PLB 385 (1996) 454: 3.05M hadronic Z 1991-94. High-mass mu mu H0 selection: > 4 tracks,
           >= 8 clusters, thrust < 0.92, p1 + p2 > 20 GeV, each p > 3.4 GeV; both muons isolated:
           D = E_jet / p_mu - 1 < 2.5 for each and D1 * D2 < 0.25 (E_jet: muon + visible energy in
           a 25 deg cone, as eff4f.l3_d); smaller of the two BGO energies in a 3-15 deg annulus
           < 0.2 GeV; hadron-calorimeter energy in a 3-30 deg annulus < 4 GeV for each and
           product < 1 GeV^2 (annulus energies: all visible particles, which is stricter than a
           calorimeter); NO m_mumu and NO recoil cut. Muon chambers |cos theta| < 0.8 (stand-in).
           Candidates: none.
  DELPHI94 NPB 421 (1994) 3: 935,616 hadronic Z used for mu mu, 1991-92. >= 6 charged; opposite
           charges, p > 5 GeV each, opening angle > 30 deg, larger p > 10 GeV; mass recoiling
           against the pair > 15 GeV; visible mass of the rest > 10 GeV; >= 2 jets in the rest
           (Durham, y_cut 0.02 stand-in); muon-jet angles: the harder muon > 40 deg, the other
           > 20 deg from the nearest jet; |cos theta| < 0.9 (stand-in). Candidates: one mu mu
           event, recoil 27.8 +- 1.9 GeV, m_ll not given.
  OPAL97   ZPC 73 (1997) 189: ~160 pb^-1 to end 1995 (">5 million Z0 decays"; 3.5M hadronic used
           here, conservative). Each muon 5 < p < 30 GeV, p1 + p2 > 20 GeV, E_vis > 80 GeV; recoil
           cut and isolation from PLB 327 (1994) 397, not read: recoil > 25 GeV and OPAL's 1996
           four-fermion isolation angles (30 / 10 deg) as stand-ins; displaced-vertex tag as a
           factor BTAG 0.5 (stand-in). Candidate: one, recoil 61.2 +- 1.0 GeV, muon momenta 19.3
           and 7.3 GeV. OPAL97 is NOT in the nominal combination (too many stand-ins).

Which candidates can be signal: the recoil mass against a muon pair of mass m is at most
sqrt(s) - m, so a candidate is signal-compatible only if recoil - 2 sigma <= sqrt(s) - M_LO with
M_LO = 26 GeV (ALEPH's 30.40 - 2.5 Gamma). Where momenta are given (OPAL), m_ll follows exactly
from the recoil: m^2 = M_rec^2 - s + 2 sqrt(s) (p1 + p2) for massless muons; it must reach
[M_LO, M_HI] within 2 sigma of the recoil. Rule "all" counts every candidate (conservative).

Efficiency as in efhz/eff4f: eps = N(ALEPH acceptance AND selection AND 20 < m_mumu < 40) /
N(ALEPH acceptance). Prediction for a search: R_acc x N_had x f_gen x eps x ID_EFF^2 x BTAG.
"""
import math

import numpy as np

import eff4f
import efhz
import evana

VERSION = "mv2 lephz 0.1.0"

SQRT_S = 91.19
M_LO, M_HI = 26.0, 35.0
EM_IDS = (11, 22)

SEARCHES = {
    "ALEPH96": dict(ref="Phys. Lett. B 384 (1996) 427 (CERN-PPE/96-079)", years="1989-1995",
                    n_had=4.5e6, n_had_note="'about 4.5 million hadronic Z decays'", btag=0.8,
                    candidates=[dict(recoil=49.7, err=0.5), dict(recoil=51.5, err=0.5),
                                dict(recoil=66.9, err=0.3)],
                    note="three H mu mu candidates; Higgs (recoil) masses as listed; m_ll not given"),
    "L3_96": dict(ref="Phys. Lett. B 385 (1996) 454 (CERN-PPE/96-095)", years="1991-1994",
                  n_had=3.05e6, n_had_note="3.05 million hadronic Z (~114 pb-1)", btag=1.0,
                  candidates=[], note="no candidate in the high-mass mu mu H0 selection"),
    "DELPHI94": dict(ref="Nucl. Phys. B 421 (1994) 3 (CERN-PPE/94-46)", years="1991-1992",
                     n_had=935616.0, n_had_note="935616 hadronic Z used for the mu mu channel",
                     btag=1.0, candidates=[dict(recoil=27.8, err=1.9)],
                     note="one mu mu event (1992), recoil 27.8 +- 1.9 GeV; m_ll not given"),
    "OPAL97": dict(ref="Z. Phys. C 73 (1997) 189 (CERN-PPE/96-118)", years="1989-1995",
                   n_had=3.5e6, n_had_note="~160 pb-1, '>5 million Z0 decays' x 0.7 (conservative)",
                   btag=0.5, candidates=[dict(recoil=61.2, err=1.0, p=(19.3, 7.3))],
                   note="one mu mu H0 candidate, recoil 61.2 +- 1.0 GeV, muon momenta 19.3 and 7.3 GeV"),
}
NOMINAL_SET = ("ALEPH96", "L3_96", "DELPHI94")
ALL_SET = ("ALEPH96", "L3_96", "DELPHI94", "OPAL97")


# ------------------------------------------------------------------ candidates
def mll_from_recoil(recoil, p1, p2, sqrt_s=SQRT_S):
    """Dimuon mass from the recoil mass and the two muon momenta (massless muons, no ISR)."""
    m2 = recoil * recoil - sqrt_s * sqrt_s + 2.0 * sqrt_s * (p1 + p2)
    return math.sqrt(m2) if m2 > 0.0 else 0.0


def compatible(c, m_lo=M_LO, m_hi=M_HI, nsig=2.0, sqrt_s=SQRT_S):
    """Can this candidate be a signal event with M_LO <= m_mumu <= M_HI?"""
    if c["recoil"] - nsig * c["err"] > sqrt_s - m_lo:
        return False
    if "p" in c:
        lo = mll_from_recoil(max(c["recoil"] - nsig * c["err"], 0.0), *c["p"], sqrt_s=sqrt_s)
        hi = mll_from_recoil(c["recoil"] + nsig * c["err"], *c["p"], sqrt_s=sqrt_s)
        return hi >= m_lo and lo <= m_hi
    return True


def n_obs(search, rule="compatible"):
    cands = SEARCHES[search]["candidates"]
    if rule == "all":
        return len(cands)
    return int(sum(compatible(c) for c in cands))


# ------------------------------------------------------------------ helpers
def durham_jets(p4, ycut):
    """Durham jets (E-scheme), y_ij = 2 min(E_i, E_j)^2 (1 - cos) / E_vis^2, E_vis = summed input
    energy; same algorithm as eff4f.durham_njets but returns the jets [E, px, py, pz]."""
    p = np.array(p4, float).reshape(-1, 4)
    n = len(p)
    if n < 2:
        return p
    evis2 = float(p[:, 0].sum()) ** 2
    if evis2 <= 0.0:
        return p
    while n >= 2:
        u = eff4f.unit(p[:, 1:])
        c = np.clip(u @ u.T, -1.0, 1.0)
        emin = np.minimum.outer(p[:, 0], p[:, 0])
        y = 2.0 * emin ** 2 * (1.0 - c) / evis2
        np.fill_diagonal(y, np.inf)
        k = int(np.argmin(y))
        a, b = divmod(k, n)
        if y[a, b] >= ycut:
            break
        p[a] = p[a] + p[b]
        p = np.delete(p, b, axis=0)
        n -= 1
    return p[np.argsort(-p[:, 0])]


def nearest_jet_angle(p4, k, jets, emin=1.0):
    """Angle (deg) between particle k and the nearest jet above emin (180 if none)."""
    jets = np.asarray(jets, float).reshape(-1, 4)
    jets = jets[jets[:, 0] > emin]
    if len(jets) == 0:
        return 180.0
    u = eff4f.unit(np.asarray(p4, float)[k, 1:])
    return float(np.degrees(np.arccos(np.clip(eff4f.unit(jets[:, 1:]) @ u, -1.0, 1.0))).min())


def opening_deg(p4, i, j):
    return float(eff4f.angles_deg(p4, i)[j])


def make_ctx(ids, p4, charge, sqrt_s=None):
    ctx = efhz.make_ctx(ids, p4, charge, sqrt_s)
    vis = ctx["vis"]
    _, thr = evana.thrust_axis(ctx["p4"][vis, 1:])
    ctx["thrust"] = thr
    ctx["seen"] = eff4f.em_or_track(ids)
    ctx["em"] = vis & np.isin(np.abs(ctx["ids"]), EM_IDS)
    ctx["evis"] = float(ctx["p4"][vis, 0].sum())
    ctx["_jets"] = {}
    return ctx


def rest_mask(ctx, i, j):
    m = ctx["vis"].copy()
    m[[i, j]] = False
    return m


def rest_jets(ctx, i, j, ycut):
    key = (i, j, ycut)
    if key not in ctx["_jets"]:
        m = rest_mask(ctx, i, j) & ctx["seen"]
        ctx["_jets"][key] = durham_jets(ctx["p4"][m], ycut)
    return ctx["_jets"][key]


# ------------------------------------------------------------------ the selections
def sel_aleph96(ctx, i, j, **kw):
    return efhz.select(ctx, i, j, **kw)


def l3_flags(ctx, i, j, pmin=3.4, psum=20.0, cmax=0.8, ntrk_min=5, nclu_min=8, thrust_max=0.92,
             dmax=2.5, dprod=0.25, jet_deg=25.0, bgo=(3.0, 15.0, 0.2), hcl=(3.0, 30.0, 4.0, 1.0),
             bgo_mask="vis"):
    """Each cut of L3's high-mass mu mu H0 selection (None: cut not applied)."""
    p4 = ctx["p4"]
    p = eff4f.pabs(p4)
    c = eff4f.costh(p4)
    vis = ctx["vis"]
    f = {}
    f["p"] = bool(min(p[i], p[j]) > pmin and p[i] + p[j] > psum and max(abs(c[i]), abs(c[j])) < cmax)
    rest = rest_mask(ctx, i, j)
    nclu = int(np.sum(rest & (p4[:, 0] > 0.1)))
    f["mult"] = bool(ctx["nch"] >= ntrk_min and nclu >= nclu_min)
    f["thrust"] = True if thrust_max is None else bool(ctx["thrust"] < thrust_max)
    d = [eff4f.l3_d(p4, vis, k, jet_deg) for k in (i, j)]
    f["d"] = bool(max(d) < dmax and d[0] * d[1] < dprod)
    if bgo is None:
        f["bgo"] = True
    else:
        mb = ctx["em"] if bgo_mask == "em" else vis
        f["bgo"] = bool(min(eff4f.cone_energy(p4, mb, k, bgo[1], bgo[0]) for k in (i, j)) < bgo[2])
    if hcl is None:
        f["hcl"] = True
    else:
        eh = [eff4f.cone_energy(p4, vis, k, hcl[1], hcl[0]) for k in (i, j)]
        f["hcl"] = bool(max(eh) < hcl[2] and eh[0] * eh[1] < hcl[3])
    return f


def sel_l3(ctx, i, j, **kw):
    return all(l3_flags(ctx, i, j, **kw).values())


def delphi_flags(ctx, i, j, pmin=5.0, phard_min=10.0, cmax=0.9, open_min=30.0, ntrk_min=6,
                 recoil_min=15.0, mvis_min=10.0, ycut=0.02, njet_min=2, jet_emin=1.0,
                 iso_hard=40.0, iso_soft=20.0, iso_rule="hard"):
    p4 = ctx["p4"]
    p = eff4f.pabs(p4)
    c = eff4f.costh(p4)
    f = {}
    f["p"] = bool(min(p[i], p[j]) > pmin and max(p[i], p[j]) > phard_min
                  and max(abs(c[i]), abs(c[j])) < cmax)
    f["open"] = bool(opening_deg(p4, i, j) > open_min)
    f["mult"] = bool(ctx["nch"] >= ntrk_min)
    f["recoil"] = bool(efhz.recoil_mass(p4, i, j, ctx["sqrt_s"]) > recoil_min)
    rest = rest_mask(ctx, i, j)
    f["mvis"] = bool(eff4f.pair_mass(p4[rest].sum(0)) > mvis_min) if rest.any() else False
    jets = rest_jets(ctx, i, j, ycut)
    f["jets"] = bool(int(np.sum(jets[:, 0] > jet_emin)) >= njet_min) if len(jets) else njet_min <= 0
    a = {k: nearest_jet_angle(p4, k, jets, jet_emin) for k in (i, j)}
    hard, soft = (i, j) if p[i] >= p[j] else (j, i)
    if iso_rule == "hard":
        f["iso"] = bool(a[hard] > iso_hard and a[soft] > iso_soft)
    elif iso_rule == "sorted":
        f["iso"] = bool(max(a.values()) > iso_hard and min(a.values()) > iso_soft)
    else:  # "both"
        f["iso"] = bool(min(a.values()) > iso_hard)
    return f


def sel_delphi(ctx, i, j, **kw):
    return all(delphi_flags(ctx, i, j, **kw).values())


def opal_flags(ctx, i, j, pmin=5.0, pmax=30.0, psum=20.0, cmax=0.95, recoil_min=25.0,
               evis_min=80.0, a_hi=30.0, a_lo=10.0):
    p4 = ctx["p4"]
    p = eff4f.pabs(p4)
    c = eff4f.costh(p4)
    f = {}
    f["p"] = bool(min(p[i], p[j]) > pmin and max(p[i], p[j]) < pmax and p[i] + p[j] > psum
                  and max(abs(c[i]), abs(c[j])) < cmax)
    f["recoil"] = True if recoil_min is None else bool(
        efhz.recoil_mass(p4, i, j, ctx["sqrt_s"]) > recoil_min)
    f["evis"] = bool(ctx["evis"] > evis_min)
    seen = ctx["seen"]
    a = sorted((eff4f.iso_angle_energy(p4, seen, i, exclude=j),
                eff4f.iso_angle_energy(p4, seen, j, exclude=i)))
    f["iso"] = bool(a[1] >= a_hi and a[0] >= a_lo)
    return f


def sel_opal97(ctx, i, j, **kw):
    return all(opal_flags(ctx, i, j, **kw).values())


VARIANTS = {
    "ALEPH96": {"nominal": (sel_aleph96, {}),
                "both_iso": (sel_aleph96, {"n_iso": 2}),
                "strict": (sel_aleph96, dict(efhz.VARIANTS["strict"]))},
    "L3_96": {"nominal": (sel_l3, {}),
              "jet40": (sel_l3, {"jet_deg": 40.0}),
              "cos0.72": (sel_l3, {"cmax": 0.72}),
              "bgo_em": (sel_l3, {"bgo_mask": "em"}),
              "nothrust": (sel_l3, {"thrust_max": None})},
    "DELPHI94": {"nominal": (sel_delphi, {}),
                 "ycut0.005": (sel_delphi, {"ycut": 0.005}),
                 "iso_both40": (sel_delphi, {"iso_rule": "both"}),
                 "cos0.95": (sel_delphi, {"cmax": 0.95})},
    "OPAL97": {"nominal": (sel_opal97, {}),
               "recoil40": (sel_opal97, {"recoil_min": 40.0}),
               "iso_both30": (sel_opal97, {"a_lo": 30.0})},
}
KEYS = ["%s:%s" % (s, v) for s in VARIANTS for v in VARIANTS[s]]
FLAG_FNS = {"L3_96": l3_flags, "DELPHI94": delphi_flags, "OPAL97": opal_flags}


def evaluate(ids, p4, charge, i, j, sqrt_s=None):
    ctx = make_ctx(ids, p4, charge, sqrt_s)
    p4 = ctx["p4"]
    m = eff4f.pair_mass(p4[i] + p4[j])
    out = {"m": m, "in_window": bool(eff4f.WINDOW[0] < m < eff4f.WINDOW[1]),
           "acc": bool(eff4f.aleph_acceptance(ids, p4, charge, i, j))}
    for s, vs in VARIANTS.items():
        for name, (fn, kw) in vs.items():
            out["%s:%s" % (s, name)] = bool(fn(ctx, i, j, **kw))
    for s, fn in FLAG_FNS.items():
        for k, v in fn(ctx, i, j).items():
            out["cut_%s_%s" % (s, k)] = v
    out["recoil"] = efhz.recoil_mass(p4, i, j, ctx["sqrt_s"])
    out["thrust"] = ctx["thrust"]
    out["l3_d"] = sorted(eff4f.l3_d(p4, ctx["vis"], k) for k in (i, j))
    return out


# ------------------------------------------------------------------ counting
def cut_keys():
    return ["cut_L3_96_" + k for k in ("p", "mult", "thrust", "d", "bgo", "hcl")] + \
           ["cut_DELPHI94_" + k for k in ("p", "open", "mult", "recoil", "mvis", "jets", "iso")] + \
           ["cut_OPAL97_" + k for k in ("p", "recoil", "evis", "iso")]


def new_counts():
    return {"n_pairs": 0, "n_acc": 0, "n_acc_win": 0, "pass": {k: 0 for k in KEYS},
            "cut": {k: 0 for k in cut_keys()}}


def accumulate(c, r):
    c["n_pairs"] += 1
    if not r["acc"]:
        return c
    c["n_acc"] += 1
    if not r["in_window"]:
        return c
    c["n_acc_win"] += 1
    for k in KEYS:
        if r[k]:
            c["pass"][k] += 1
    for k in cut_keys():
        if r.get(k):
            c["cut"][k] += 1
    return c


def eps(c, key):
    n = c["n_acc"]
    if n == 0:
        return float("nan"), float("nan")
    e = c["pass"][key] / n
    return e, math.sqrt(max(e * (1.0 - e), 0.0) / n)


# ------------------------------------------------------------------ confrontation
def predict(search, e, reading="nominal", n_sig=None, id_eff=eff4f.ID_EFF, btag=None):
    import lep4f
    s = SEARCHES[search]
    if n_sig is None:
        n_sig = lep4f.ALEPH_N_SIG
    b = s["btag"] if btag is None else btag
    return lep4f.rate_acc(reading, n_sig) * s["n_had"] * efhz.f_gen() * e * id_eff ** 2 * b


def combine(eps_by, searches=NOMINAL_SET, reading="nominal", n_sig=None, rule="compatible",
            btag_scale=1.0):
    """Summed prediction of several searches against their summed signal-compatible candidates
    (b = 0: every compatible candidate counted as possible signal, conservative)."""
    import lep4f
    n = sum(n_obs(s, rule) for s in searches)
    pred = sum(predict(s, eps_by[s], reading, n_sig, btag=SEARCHES[s]["btag"] * btag_scale)
               for s in searches)
    s_up = lep4f.cls_upper(n, 0.0)
    p = lep4f.pois_cdf(n, pred)
    return {"searches": list(searches), "rule": rule, "n_obs": n, "s_up_95": s_up, "pred": pred,
            "mu_max": (s_up / pred) if pred > 0 else float("inf"), "p": p, "z": eff4f.z_of(p)}


def confront_all(eps_by):
    """The standard set of readings for one model. eps_by: search -> efficiency."""
    import lep4f
    out = {}
    lit = {r: eff4f.n_sig_for_rate(eff4f.R_LIT, r) for r in ("nominal", "low")}
    readings = [("central", "nominal", None), ("low-1sigma", "low", lep4f.ALEPH_N_SIG - lep4f.ALEPH_N_SIG_ERR),
                ("lit1.1e-5", "low", lit["low"])]
    for tag, reading, nsig in readings:
        for sset_name, sset in (("nominal3", NOMINAL_SET), ("all4", ALL_SET), ("L3+DELPHI", ("L3_96", "DELPHI94"))):
            for rule in ("compatible", "all"):
                out["%s|%s|%s" % (sset_name, rule, tag)] = combine(eps_by, sset, reading, nsig, rule)
        for s in ALL_SET:
            out["%s|compatible|%s" % (s, tag)] = combine(eps_by, (s,), reading, nsig, "compatible")
    return out
