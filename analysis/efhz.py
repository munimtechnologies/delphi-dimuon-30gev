#!/usr/bin/env python3
"""efhz: would ALEPH's own LEP1 Higgs search (e+e- -> H Z*, Z* -> mu+ mu-) have seen a boson
reading of the ALEPH 30 GeV dimuon excess (arXiv:1610.06536)?

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

ALEPH's final LEP1 Standard Model Higgs search (Phys. Lett. B 384 (1996) 427, CERN-PPE/96-079)
used "about 4.5 million hadronic Z decays" recorded in 1989-1995 and found **three candidates in
the H mu+ mu- channel**, "consistent with the expected electroweak l+ l- q qbar background"
(abstract). The H l+ l- channel selects exactly what a boson X -> mu+ mu- produced with b quarks
would give: two energetic muons, at least one of them isolated, recoiling against hadrons. The
1992-95 data in which arXiv:1610.06536 found the excess are part of that sample.

This module applies the H l+ l- selection of ALEPH's earlier LEP1 Higgs paper (Phys. Lett. B 313
(1993) 299, CERN-PPE/93-110), as read by MV2's reading agent on 2026-11-18, at hadron level
(Pythia 8) to the boson models of NOTE-kinematics.md:
  - each lepton p > 3 GeV; scalar sum of the two lepton momenta > 20 GeV; m_ll > 5 GeV;
  - sum over the two leptons of the momentum transverse to the thrust axis > 15 GeV (the paper's
    wording, "sum of pT relative to the thrust axis", is read this way; the axis is that of all
    visible particles; variant `pt_had` uses the hadrons only, variant `nopt` drops the cut);
  - at least ONE lepton isolated: no other charged particle within a 30 deg half-angle cone and
    less than 1 GeV of neutral energy in the same cone, "apart from identified bremsstrahlung
    photons" (here: photons within BREM_DEG of the muon are not counted);
  - >= 6 charged tracks, carrying more than 10 % of sqrt(s) (our reading of "(> 10 % of sqrt(s))");
    >= 8 charged tracks when the missing energy exceeds 10 % of sqrt(s);
  - recoil mass against the lepton pair > 40 GeV.
The 1996 paper's own cuts are not yet read; variants bracket likely changes (both leptons
isolated, recoil > 50 GeV, no recoil cut, tighter momentum and angle cuts).

Efficiency, as in eff4f: eps = N(ALEPH acceptance AND selection AND 20 < m_mumu < 40) /
N(ALEPH acceptance), acceptance as behind lep4f's rate R_acc. Muon identification is not
simulated. Two confrontations with the three observed candidates (all counted as possible signal,
no background subtracted, which is conservative):
  rate:   predicted = R_acc x N_had(1989-95) x f_gen x eps x ID_EFF^2;
  subset: the 32.31 +- 10.87 fitted excess events are themselves in the 1992-95 part of the Higgs
          search's sample; predicted = N_sig x f_gen x eps x id_ratio, where id_ratio is the
          chance that a muon pair identified in arXiv:1610.06536 is also identified by the Higgs
          search (1 nominal; 0.86^2 as a pessimistic variant). This needs no luminosity or
          b-tag conversion at all.
"""
import math

import numpy as np

import eff4f
import evana

VERSION = "mv2 efhz 0.1.0"

CONE_DEG = 30.0
NEUTRAL_EMAX = 1.0
BREM_DEG = 2.0
GOOD_P, GOOD_COS = 0.2, 0.95          # a "good charged track", as eff4f.n_charged
ALEPH96 = dict(ref="Phys. Lett. B 384 (1996) 427 (CERN-PPE/96-079)", years="1989-1995",
               n_had=4.5e6, n_had_note="'about 4.5 million hadronic Z decays' (abstract)",
               n_obs=3, n_obs_note="three candidates in the H mu+ mu- channel, 'consistent with the "
               "expected electroweak l+ l- q qbar background' (abstract); masses not yet read")


# ------------------------------------------------------------------ event quantities
def good_charged(p4, charge):
    p = eff4f.pabs(p4)
    c = eff4f.costh(p4)
    return (np.asarray(charge, float) != 0) & (p > GOOD_P) & (np.abs(c) < GOOD_COS)


def recoil_mass(p4, i, j, sqrt_s):
    """Mass recoiling against particles i and j, for a beam four-vector (sqrt_s, 0, 0, 0)."""
    p4 = np.asarray(p4, float)
    P = p4[i] + p4[j]
    m2 = (sqrt_s - P[0]) ** 2 - P[1] ** 2 - P[2] ** 2 - P[3] ** 2
    return math.sqrt(m2) if m2 > 0 else 0.0


def pt_sum(p4, i, j, axis):
    """Sum over particles i, j of |p x axis| (axis a unit vector)."""
    p4 = np.asarray(p4, float)
    return float(sum(np.linalg.norm(np.cross(p4[k, 1:], axis)) for k in (i, j)))


def isolated(p4, ids, charge, vis, k, cone=CONE_DEG, emax=NEUTRAL_EMAX, brem_deg=BREM_DEG):
    """ALEPH (PLB 313 (1993) 299): no other charged particle inside the cone, and less than emax
    of neutral energy in it, photons within brem_deg of particle k not counted."""
    p4 = np.asarray(p4, float)
    ids = np.asarray(ids)
    ang = eff4f.angles_deg(p4, k)
    others = np.ones(len(p4), bool)
    others[k] = False
    inside = others & (ang < cone)
    if np.any(inside & good_charged(p4, charge)):
        return False
    neutral = inside & np.asarray(vis, bool) & (np.asarray(charge, float) == 0)
    brem = (ids == 22) & (ang < brem_deg)
    return float(p4[neutral & ~brem, 0].sum()) < emax


def make_ctx(ids, p4, charge, sqrt_s=None):
    p4 = np.asarray(p4, float)
    ids = np.asarray(ids)
    charge = np.asarray(charge, float)
    vis = eff4f.visible(ids)
    if sqrt_s is None:
        sqrt_s = float(p4[:, 0].sum())      # ISR is off in the generation: all final energy
    gc = good_charged(p4, charge)
    ax_all, _ = evana.thrust_axis(p4[vis, 1:])
    return {"ids": ids, "p4": p4, "charge": charge, "vis": vis, "sqrt_s": sqrt_s,
            "nch": int(gc.sum()), "ech": float(p4[gc, 0].sum()),
            "emiss": sqrt_s - float(p4[vis, 0].sum()), "axis_all": ax_all}


def hadron_axis(ctx, i, j):
    m = ctx["vis"].copy()
    m[[i, j]] = False
    ax, _ = evana.thrust_axis(ctx["p4"][m, 1:])
    return ax


def cut_flags(ctx, i, j, pmin=3.0, psum=20.0, mll_min=5.0, pt_min=15.0, pt_axis="all", n_iso=1,
              nch_min=6, nch_min_miss=8, ech_frac=0.10, miss_frac=0.10, recoil_min=40.0,
              cmax=0.95):
    """Each cut of the selection, True when passed (None thresholds: cut not applied)."""
    p4 = ctx["p4"]
    p = eff4f.pabs(p4)
    c = eff4f.costh(p4)
    s = ctx["sqrt_s"]
    f = {}
    f["p"] = bool(min(p[i], p[j]) > pmin and max(abs(c[i]), abs(c[j])) < cmax)
    f["psum"] = bool(p[i] + p[j] > psum)
    f["mll"] = bool(eff4f.pair_mass(p4[i] + p4[j]) > mll_min)
    if pt_min is None:
        f["pt"] = True
    else:
        ax = ctx["axis_all"] if pt_axis == "all" else hadron_axis(ctx, i, j)
        f["pt"] = bool(pt_sum(p4, i, j, ax) > pt_min)
    niso = sum(isolated(p4, ctx["ids"], ctx["charge"], ctx["vis"], k) for k in (i, j))
    f["iso"] = bool(niso >= n_iso)
    need = nch_min_miss if ctx["emiss"] > miss_frac * s else nch_min
    f["mult"] = bool(ctx["nch"] >= need and ctx["ech"] > ech_frac * s)
    f["recoil"] = True if recoil_min is None else bool(recoil_mass(p4, i, j, s) > recoil_min)
    return f


def select(ctx, i, j, **kw):
    return all(cut_flags(ctx, i, j, **kw).values())


VARIANTS = {
    "nominal": {},
    "both_iso": {"n_iso": 2},
    "norecoil": {"recoil_min": None},
    "recoil50": {"recoil_min": 50.0},
    "pt_had": {"pt_axis": "had"},
    "nopt": {"pt_min": None},
    "cos0.9": {"cmax": 0.9},
    "pmin5": {"pmin": 5.0},
    "strict": {"n_iso": 2, "recoil_min": 50.0, "pmin": 5.0, "pt_axis": "had", "cmax": 0.9},
}
KEYS = list(VARIANTS)
CUTS = ("p", "psum", "mll", "pt", "iso", "mult", "recoil")


def evaluate(ids, p4, charge, i, j, sqrt_s=None):
    ctx = make_ctx(ids, p4, charge, sqrt_s)
    p4 = ctx["p4"]
    m = eff4f.pair_mass(p4[i] + p4[j])
    out = {"m": m, "in_window": bool(eff4f.WINDOW[0] < m < eff4f.WINDOW[1]),
           "acc": bool(eff4f.aleph_acceptance(ids, p4, charge, i, j))}
    for name, kw in VARIANTS.items():
        out[name] = select(ctx, i, j, **kw)
    flags = cut_flags(ctx, i, j)
    for k in CUTS:
        out["cut_" + k] = flags[k]
    out["recoil"] = recoil_mass(p4, i, j, ctx["sqrt_s"])
    out["pt_sum"] = pt_sum(p4, i, j, ctx["axis_all"])
    out["n_iso"] = int(sum(isolated(p4, ctx["ids"], ctx["charge"], ctx["vis"], k) for k in (i, j)))
    out["nch"] = ctx["nch"]
    return out


# ------------------------------------------------------------------ counting
def new_counts():
    return {"n_pairs": 0, "n_acc": 0, "pass": {k: 0 for k in KEYS},
            "cut": {k: 0 for k in CUTS}, "nm1": {k: 0 for k in CUTS}}


def accumulate(c, r):
    c["n_pairs"] += 1
    if not r["acc"]:
        return c
    c["n_acc"] += 1
    if not r["in_window"]:
        return c
    for k in KEYS:
        if r[k]:
            c["pass"][k] += 1
    for k in CUTS:
        if r["cut_" + k]:
            c["cut"][k] += 1
        if all(r["cut_" + q] for q in CUTS if q != k):
            c["nm1"][k] += 1        # passes every nominal cut except possibly k
    return c


def eps(c, key):
    n = c["n_acc"]
    if n == 0:
        return float("nan"), float("nan")
    e = c["pass"][key] / n
    return e, math.sqrt(max(e * (1.0 - e), 0.0) / n)


# ------------------------------------------------------------------ confrontation
def f_gen():
    return eff4f.bw_fraction(*eff4f.GEN_RANGE)


def predict_rate(e, reading="nominal", n_sig=None, id_eff=eff4f.ID_EFF, n_had=ALEPH96["n_had"]):
    import lep4f
    if n_sig is None:
        n_sig = lep4f.ALEPH_N_SIG
    return lep4f.rate_acc(reading, n_sig) * n_had * f_gen() * e * id_eff ** 2


def predict_subset(e, n_sig=None, id_ratio=1.0):
    import lep4f
    if n_sig is None:
        n_sig = lep4f.ALEPH_N_SIG
    return n_sig * f_gen() * e * id_ratio


def p_subset_marginal(e, id_ratio=1.0, n_obs=ALEPH96["n_obs"], npts=4001):
    """P(N <= n_obs) with the excess yield drawn from a Gaussian 32.31 +- 10.87 truncated at 0."""
    import lep4f
    mu, sd = lep4f.ALEPH_N_SIG, lep4f.ALEPH_N_SIG_ERR
    xs = np.linspace(0.0, mu + 8.0 * sd, npts)
    w = np.exp(-0.5 * ((xs - mu) / sd) ** 2)
    ps = np.array([lep4f.pois_cdf(n_obs, predict_subset(e, x, id_ratio)) for x in xs])
    return _trap(w * ps, xs) / _trap(w, xs)


def _trap(y, x):
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def confront(e):
    """All readings for one efficiency e."""
    import lep4f
    n = ALEPH96["n_obs"]
    s_up = lep4f.cls_upper(n, 0.0)
    out = {"n_obs": n, "s_up_95": s_up, "eps": e}
    for reading in ("nominal", "low"):
        for tag, nsig in (("central", None), ("minus1sigma", lep4f.ALEPH_N_SIG - lep4f.ALEPH_N_SIG_ERR),
                          ("lit1.1e-5", eff4f.n_sig_for_rate(eff4f.R_LIT, reading))):
            pred = predict_rate(e, reading, nsig)
            p = lep4f.pois_cdf(n, pred)
            out["rate|%s|%s" % (reading, tag)] = {"pred": pred, "p": p, "z": eff4f.z_of(p)}
    for idr_tag, idr in (("id1", 1.0), ("id0.74", eff4f.ID_EFF ** 2)):
        pred = predict_subset(e, None, idr)
        p = lep4f.pois_cdf(n, pred)
        pm = p_subset_marginal(e, idr)
        out["subset|%s" % idr_tag] = {"pred": pred, "p": p, "z": eff4f.z_of(p),
                                      "p_marginal": pm, "z_marginal": eff4f.z_of(pm)}
    out["eps_max_rate_nominal"] = s_up / predict_rate(1.0)
    out["eps_max_subset_id1"] = s_up / predict_subset(1.0)
    return out
