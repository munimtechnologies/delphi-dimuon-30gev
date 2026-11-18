#!/usr/bin/env python3
"""eff4f: generator-level efficiency of the published LEP1 mu+ mu- q qbar selections (ALEPH 1995,
OPAL 1996, L3 1994) for boson readings of the ALEPH 30 GeV dimuon excess (arXiv:1610.06536), and
what the dimuon-mass distributions those papers show then imply.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

analysis/lep4f.py 0.1.0 bounded the efficiency eps at which an ALEPH-sized boson could hide in the
published mu mu q qbar *totals*. This module estimates eps itself, at hadron level (Pythia 8),
with each paper's cuts as read from the papers (two independent readings, 2026-11-17; see
NOTE-fourfermion.md):

  OPAL  PLB 376 (1996) 315 (CERN-PPE/96-031): N_trk >= 8; >= 2 Durham jets (charged tracks and
        unassociated EM clusters; y_cut not stated: 0.02 nominal, 0.005 variant); each lepton
        p >= 5 GeV, |p1| + |p2| >= 15 GeV; opposite charge; isolation angle alpha = largest
        half-angle of a cone around the lepton with E_cone < 1 GeV, E_cone = energy of all tracks
        and unassociated EM clusters, "excluding both the lepton candidate itself, and also the
        nearest other lepton candidate if it lies within the cone"; alpha_1 >= 30 deg,
        alpha_2 >= 10 deg; no m_ll cut; no |cos theta| limit stated (0.95 nominal; 0.9 and 0.98
        variants). Here "tracks and EM clusters" = every visible particle except neutrons and K_L
        (Pythia keeps K_S and Lambda stable at tau0Max 10 mm; their decays give tracks/photons),
        and the excluded lepton is the partner signal muon (a b-decay lepton nearby is kept,
        which is stricter). Not modelled: the dE/dx electron veto on two hadronic tracks (always
        passed by b-quark events at generator level).
  ALEPH ZPC 66 (1995) 3 (CERN-PPE/94-169): >= 6 good charged tracks; two "energetic, isolated,
        identified" leptons; < 1 GeV of other energy in a 30 deg cone; momentum cut in the paper's
        ref. 20 (PLB 313 (1993) 299), not read: 3 GeV assumed (2 and 5 GeV variants); no m_ll cut.
        Cone energy counts all visible particles (stricter).
  L3    PLB 321 (1994) 283: p_mu >= 3 GeV; min over muons of D = E_jet / p_mu - 1 < 0.4; min over
        muons of the energy in a 3-15 deg annulus < 0.7 GeV (ECAL in the paper; all visible
        energy here, which is stricter); muon chambers taken as 40-140 deg (the paper's generator
        cut); no m_ll cut. E_jet is approximated by the energy in a 25 deg cone (40 deg variant).

Muon identification is not simulated: predictions multiply by ID_EFF per muon (ALEPH's 0.86, as a
stand-in). Variant "OPAL:v010" is version 0.1.0's OPAL selection (all visible energy, no partner
exclusion, no multiplicity cuts), kept for comparison.

The efficiency is defined against the acceptance that analysis/lep4f.py's rate R_acc refers to
(both muons p > 2.5 GeV, |cos theta| < 0.95, >= 5 charged particles, |p_miss| < 18 GeV, as in
xkin's evana + run_xkin.summarise):

    eps_kin = N(ALEPH acceptance AND selection AND 20 < m_mumu < 40) / N(ALEPH acceptance)

Events outside that acceptance that pass a selection are not counted (conservative).
"""
import math

import numpy as np

VERSION = "mv2 eff4f 0.2.0"

NU = (12, 14, 16)
NOT_EM_OR_TRACK = (2112, 130)      # neutron, K_L: no track, no EM cluster (OPAL's E_cone, jets)
COS40 = math.cos(math.radians(40.0))
ID_EFF = 0.86                      # per muon, ALEPH's value (arXiv:1610.06536), used as a stand-in
WINDOW = (20.0, 40.0)
GEN_RANGE = (22.0, 40.0)           # xme.generate_radiation / generate_pair defaults (mlo, mhi)
BW_M, BW_G = 30.40, 1.78           # ALEPH's fitted mass and width, as in xme / run_xkin
YCUTS = (0.02, 0.005)              # Durham y_cut for OPAL's ">= 2 jets" (not stated in the paper)
OPAL_NTRK_MIN = 8
ALEPH_NTRK_MIN = 6
# Z -> b bbar mu mu branching ratio quoted from the ALEPH excess by Ko, Li and Yu
# (arXiv:1610.07526): 1.1e-5 of all Z decays; per hadronic Z with Gamma_had / Gamma_Z = 0.69911.
# It is close to the raw yield 32 / (number of Z) with no b-tag or muon-ID correction. Used as a
# lowest-rate reading, taken as if every such event were inside ALEPH's acceptance.
BR_LIT = 1.1e-5
R_LIT = BR_LIT / 0.69911

# Published dimuon-mass information for the mu mu q qbar events at the Z pole, read off the papers'
# figures by two independent reading agents on 2026-11-17 (both readings agree).
WINDOW_OBS = {
    "OPAL": dict(n_obs=1, note="Fig. 3b (final event selection, sqrt(s) ~ m_Z), 10 GeV bins: 0-10: 19, "
                 "10-20: 3, 20-30: 1, 30-40: 0, 40-50: 1, 50-60: 1, 60-70: 2, 70-80: 1, 80-100: 0 "
                 "(sum 28 = observed); all of 20-40 counted"),
    "L3": dict(n_obs=0, note="Fig. 7a, m(mu mu) of the 6 events: 0-10: 1, 10-20: 1, 60-70: 2, "
               "80-90: 2; none in 20-40 GeV"),
    "ALEPH": dict(n_obs=4, note="no mu-mu-only mass plot; Fig. 13b, e e q q and mu mu q q combined "
                  "(29 events, 19 mu mu): 2 in 20-30, 2 in 30-40 GeV, all counted as mu mu "
                  "(upper bound)"),
}


# ------------------------------------------------------------------ geometry
def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n > 0, n, 1.0)


def visible(ids):
    return ~np.isin(np.abs(np.asarray(ids)), NU)


def em_or_track(ids):
    """Particles that leave a track or an EM cluster (OPAL's E_cone and jet inputs)."""
    a = np.abs(np.asarray(ids))
    return ~np.isin(a, NU) & ~np.isin(a, NOT_EM_OR_TRACK)


def pabs(p4):
    return np.linalg.norm(np.asarray(p4, float)[:, 1:], axis=1)


def costh(p4):
    p4 = np.asarray(p4, float)
    p = pabs(p4)
    return np.where(p > 0, p4[:, 3] / np.where(p > 0, p, 1.0), 0.0)


def pair_mass(P):
    return math.sqrt(max(P[0] ** 2 - P[1] ** 2 - P[2] ** 2 - P[3] ** 2, 0.0))


def angles_deg(p4, i):
    """Angle in degrees between particle i and every particle (itself: 0)."""
    u = unit(np.asarray(p4, float)[:, 1:])
    return np.degrees(np.arccos(np.clip(u @ u[i], -1.0, 1.0)))


def _others(vis, i, exclude=None):
    m = np.array(vis, bool).copy()
    m[i] = False
    if exclude is not None:
        m[exclude] = False
    return m


def iso_angle_energy(p4, vis, i, emax=1.0, exclude=None):
    """Half-angle (deg) of the largest cone around particle i that holds less than emax GeV of
    other visible energy: the angle at which the cumulative energy, nearest first, reaches emax.
    180 if all other visible energy together stays below emax. Particle `exclude` (index or
    None) is left out of the cone energy (OPAL: the nearest other lepton candidate)."""
    p4 = np.asarray(p4, float)
    m = _others(vis, i, exclude)
    if not m.any():
        return 180.0
    ang = angles_deg(p4, i)[m]
    e = p4[m, 0]
    order = np.argsort(ang, kind="stable")
    cum = np.cumsum(e[order])
    k = np.nonzero(cum >= emax)[0]
    if len(k) == 0:
        return 180.0
    return float(ang[order][k[0]])


def iso_angle_nearest(p4, vis, i, emin=1.0, exclude=None):
    """Angle (deg) to the nearest other visible particle with energy above emin (looser variant)."""
    p4 = np.asarray(p4, float)
    m = _others(vis, i, exclude) & (p4[:, 0] > emin)
    if not m.any():
        return 180.0
    return float(angles_deg(p4, i)[m].min())


def cone_energy(p4, vis, i, hi_deg, lo_deg=0.0):
    """Other visible energy at lo_deg <= angle < hi_deg from particle i."""
    p4 = np.asarray(p4, float)
    ang = angles_deg(p4, i)
    sel = _others(vis, i) & (ang >= lo_deg) & (ang < hi_deg)
    return float(p4[sel, 0].sum())


def durham_njets(p4, ycut):
    """Number of Durham (k_T) jets at y_cut, E-scheme recombination,
    y_ij = 2 min(E_i, E_j)^2 (1 - cos theta_ij) / E_vis^2 with E_vis the summed input energy."""
    p = np.array(p4, float).reshape(-1, 4)
    n = len(p)
    if n < 2:
        return n
    evis2 = float(p[:, 0].sum()) ** 2
    if evis2 <= 0.0:
        return n
    while n >= 2:
        u = unit(p[:, 1:])
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
    return n


# ------------------------------------------------------------------ acceptance behind R_acc
def n_charged(p4, charge):
    p = pabs(p4)
    c = costh(p4)
    return int(np.sum((np.asarray(charge, float) != 0) & (p > 0.2) & (np.abs(c) < 0.95)))


def p_miss(ids, p4):
    vis = visible(ids)
    if not vis.any():
        return 0.0
    return float(np.linalg.norm(np.asarray(p4, float)[vis, 1:].sum(0)))


def aleph_acceptance(ids, p4, charge, i, j):
    """Both muons p > 2.5 GeV and |cos theta| < 0.95; >= 5 charged (p > 0.2, |cos| < 0.95);
    |visible p_miss| < 18 GeV. Same definitions as xkin/evana.py + run_xkin.summarise."""
    p = pabs(p4)
    c = costh(p4)
    for k in (i, j):
        if not (p[k] > 2.5 and abs(c[k]) < 0.95):
            return False
    return n_charged(p4, charge) >= 5 and p_miss(ids, p4) < 18.0


# ------------------------------------------------------------------ the three selections
def sel_opal(p4, vis, i, j, pmin=5.0, psum=15.0, cmax=0.95, a_hi=30.0, a_lo=10.0, emax=1.0,
             iso="energy", exclude_partner=False):
    """OPAL's lepton cuts on muons i, j; `vis` is the set that counts in E_cone."""
    p = pabs(p4)
    c = costh(p4)
    if min(p[i], p[j]) < pmin or p[i] + p[j] < psum:
        return False
    if max(abs(c[i]), abs(c[j])) >= cmax:
        return False
    f = iso_angle_energy if iso == "energy" else iso_angle_nearest
    xi, xj = (j, i) if exclude_partner else (None, None)
    a = sorted((f(p4, vis, i, emax, exclude=xi), f(p4, vis, j, emax, exclude=xj)))
    return a[1] >= a_hi and a[0] >= a_lo


def sel_aleph(p4, vis, i, j, pmin=3.0, cmax=0.95, cone_deg=30.0, emax=1.0):
    p = pabs(p4)
    c = costh(p4)
    for k in (i, j):
        if p[k] < pmin or abs(c[k]) >= cmax:
            return False
        if cone_energy(p4, vis, k, cone_deg) >= emax:
            return False
    return True


def l3_d(p4, vis, k, jet_deg=25.0):
    """D = E_jet / p_mu - 1, E_jet = muon energy + other visible energy within jet_deg."""
    p4 = np.asarray(p4, float)
    p = float(pabs(p4)[k])
    if p <= 0.0:
        return math.inf
    return (p4[k, 0] + cone_energy(p4, vis, k, jet_deg)) / p - 1.0


def sel_l3(p4, vis, i, j, pmin=3.0, cmax=COS40, dmax=0.4, jet_deg=25.0, ann=(3.0, 15.0), emax=0.7):
    p = pabs(p4)
    c = costh(p4)
    for k in (i, j):
        if p[k] < pmin or abs(c[k]) >= cmax:
            return False
    d = min(l3_d(p4, vis, i, jet_deg), l3_d(p4, vis, j, jet_deg))
    e = min(cone_energy(p4, vis, i, ann[1], ann[0]), cone_energy(p4, vis, j, ann[1], ann[0]))
    return d < dmax and e < emax


# ------------------------------------------------------------------ event context + variants
def make_ctx(ids, p4, charge):
    """Event-level quantities the selections share."""
    p4 = np.asarray(p4, float)
    vis = visible(ids)
    seen = em_or_track(ids)
    return {"p4": p4, "vis": vis, "seen": seen, "nch": n_charged(p4, charge),
            "njets": {y: durham_njets(p4[seen], y) for y in YCUTS}}


def opal_ctx(ctx, i, j, seen=True, exclude_partner=True, mult=True, ycut=YCUTS[0],
             ntrk_min=OPAL_NTRK_MIN, **kw):
    if mult and (ctx["nch"] < ntrk_min or ctx["njets"][ycut] < 2):
        return False
    mask = ctx["seen"] if seen else ctx["vis"]
    return sel_opal(ctx["p4"], mask, i, j, exclude_partner=exclude_partner, **kw)


def aleph_ctx(ctx, i, j, nmin=ALEPH_NTRK_MIN, **kw):
    if ctx["nch"] < nmin:
        return False
    return sel_aleph(ctx["p4"], ctx["vis"], i, j, **kw)


def l3_ctx(ctx, i, j, **kw):
    return sel_l3(ctx["p4"], ctx["vis"], i, j, **kw)


VARIANTS = {
    "OPAL": {"nominal": (opal_ctx, {}),
             "nomult": (opal_ctx, {"mult": False}),
             "ycut0.005": (opal_ctx, {"ycut": 0.005}),
             "iso_nearest": (opal_ctx, {"iso": "nearest"}),
             "both_30deg": (opal_ctx, {"a_lo": 30.0}),
             "cos0.9": (opal_ctx, {"cmax": 0.9}),
             "cos0.98": (opal_ctx, {"cmax": 0.98}),
             "v010": (opal_ctx, {"seen": False, "exclude_partner": False, "mult": False})},
    "ALEPH": {"nominal": (aleph_ctx, {}),
              "pmin2": (aleph_ctx, {"pmin": 2.0}),
              "pmin5": (aleph_ctx, {"pmin": 5.0}),
              "cos0.9": (aleph_ctx, {"cmax": 0.9})},
    "L3": {"nominal": (l3_ctx, {}),
           "jet40": (l3_ctx, {"jet_deg": 40.0}),
           "cos0.7": (l3_ctx, {"cmax": 0.7}),
           "pmin5": (l3_ctx, {"pmin": 5.0})},
}
KEYS = ["%s:%s" % (e, v) for e in VARIANTS for v in VARIANTS[e]]
VARIANT_NAMES = sorted({v for e in VARIANTS for v in VARIANTS[e]})


def evaluate(ids, p4, charge, i, j):
    """All selections for one event with signal muons i, j."""
    ctx = make_ctx(ids, p4, charge)
    p4 = ctx["p4"]
    m = pair_mass(p4[i] + p4[j])
    out = {"m": m, "in_window": bool(WINDOW[0] < m < WINDOW[1]),
           "acc": bool(aleph_acceptance(ids, p4, charge, i, j))}
    for expt, vs in VARIANTS.items():
        for name, (fn, kw) in vs.items():
            out["%s:%s" % (expt, name)] = bool(fn(ctx, i, j, **kw))
    a = sorted((iso_angle_energy(p4, ctx["seen"], i, exclude=j),
                iso_angle_energy(p4, ctx["seen"], j, exclude=i)))
    out["opal_alpha_lo"], out["opal_alpha_hi"] = a[0], a[1]
    out["nch"] = ctx["nch"]
    out["njets_y0.02"] = ctx["njets"][0.02]
    out["aleph_cone30_max"] = max(cone_energy(p4, ctx["vis"], i, 30.0),
                                  cone_energy(p4, ctx["vis"], j, 30.0))
    out["l3_dmin"] = min(l3_d(p4, ctx["vis"], i), l3_d(p4, ctx["vis"], j))
    return out


def new_counts():
    c = {"n_pairs": 0, "n_acc": 0, "n_acc_win": 0, "pass_acc_win": {}, "pass_win_any": {}}
    for k in KEYS:
        c["pass_acc_win"][k] = 0
        c["pass_win_any"][k] = 0
    return c


def accumulate(c, r):
    c["n_pairs"] += 1
    if r["acc"]:
        c["n_acc"] += 1
        if r["in_window"]:
            c["n_acc_win"] += 1
    for k in KEYS:
        if r[k] and r["in_window"]:
            c["pass_win_any"][k] += 1
            if r["acc"]:
                c["pass_acc_win"][k] += 1
    return c


def merge(a, b):
    out = new_counts()
    for x in (a, b):
        for k in ("n_pairs", "n_acc", "n_acc_win"):
            out[k] += x[k]
        for d in ("pass_acc_win", "pass_win_any"):
            for k in KEYS:
                out[d][k] += x[d][k]
    return out


def eps_kin(c, key):
    """(eps, binomial error) for one selection key."""
    n = c["n_acc"]
    if n == 0:
        return float("nan"), float("nan")
    e = c["pass_acc_win"][key] / n
    return e, math.sqrt(max(e * (1.0 - e), 0.0) / n)


# ------------------------------------------------------------------ what the mass plots imply
def bw_fraction(lo, hi, M=BW_M, G=BW_G):
    """Fraction of xme's Breit-Wigner in m^2 with lo < m < hi, relative to all m >= 0."""
    f = lambda m: math.atan((m * m - M * M) / (M * G))
    return (f(hi) - f(lo)) / (math.pi / 2.0 - f(0.0))


def z_of(p):
    """One-sided Gaussian significance of a p-value (37 for p <= 1e-300)."""
    if p >= 0.5:
        return 0.0
    if p <= 1e-300:
        return 37.0
    lo, hi = 0.0, 37.5
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 0.5 * math.erfc(mid / math.sqrt(2.0)) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def n_sig_for_rate(rate, reading="nominal"):
    """The ALEPH signal yield that lep4f.rate_acc turns into `rate` per hadronic Z (rate_acc is
    linear in the yield)."""
    import lep4f
    ref = lep4f.ALEPH_N_SIG
    return ref * rate / lep4f.rate_acc(reading, ref)


def predict(expt, eps, reading="nominal", id_eff=ID_EFF, n_sig=None):
    """Boson events an ALEPH-sized signal puts into expt's 20-40 GeV mu mu q qbar sample."""
    import lep4f
    if n_sig is None:
        n_sig = lep4f.ALEPH_N_SIG
    f_gen = bw_fraction(*GEN_RANGE)
    return lep4f.rate_acc(reading, n_sig) * lep4f.EXPTS[expt]["n_z"] * f_gen * eps * id_eff ** 2


def confront(expts, eps_by_expt, reading="nominal", id_eff=ID_EFF, n_sig=None):
    """Observed 20-40 GeV counts of several experiments against the boson prediction (b = 0,
    which makes the CLs limit and the p-value conservative)."""
    import lep4f
    n = sum(WINDOW_OBS[e]["n_obs"] for e in expts)
    pred = sum(predict(e, eps_by_expt[e], reading, id_eff, n_sig) for e in expts)
    unit_pred = sum(predict(e, 1.0, reading, id_eff, n_sig) for e in expts)
    s_up = lep4f.cls_upper(n, 0.0)
    p = lep4f.pois_cdf(n, pred)
    return {"expts": list(expts), "n_obs": n, "s_up_95": s_up, "pred": pred,
            "mu_max": (s_up / pred) if pred > 0 else float("inf"),
            "p_value": p, "z": z_of(p), "pred_if_eps_1": unit_pred}
