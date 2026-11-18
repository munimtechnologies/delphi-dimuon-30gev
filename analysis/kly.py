#!/usr/bin/env python3
"""kly: the two published models of Ko, Li and Yu (arXiv:1610.07526) for the ALEPH 30 GeV dimuon
excess, as parton-level event generators, so that the LEP1 Higgs-search selections of lephz.py can
be applied to them.

  B : Ko-Li-Yu "model II". A Z' (30.4 GeV, -> mu+ mu-) couples the b quark to a heavy vector-like
      singlet B quark (no Z' b bbar coupling), so it escapes the LHC Drell-Yan bound that excludes
      a plain b-coupled boson. At LEP1: e+e- -> Z -> b B*bar, B*bar -> bbar Z' (and the conjugate).
      The paper's eq. (4): (g'_b / 2) Z'_rho bbar gamma^rho B (pure vector) and
      (g_W sin 2 theta_L / 4 c_W) Z_mu bbar gamma^mu P_L B (left-handed, from b-B mixing), + h.c.;
      no diagonal Z' b b coupling (by assumption). So the Z vertex is gamma^mu P_L and the Z'
      vertex gamma^rho; with a vector Z' vertex the m_B term of the B propagator (p-slash + m_B) /
      (p^2 - m_B^2 + i m_B Gamma_B) contributes. Benchmarks of the paper: III m_B = 110 GeV,
      Gamma_B = 3.4 GeV; IV m_B = 180 GeV, Gamma_B = 124.4 GeV. Variant B110L (Z' vertex
      left-handed, m_B term drops out) brackets the chirality.
  Q : Ko-Li-Yu "model III". Z -> Z' phi, Z' -> mu+ mu-, phi -> b bbar, through a Z_mu Z'^mu phi
      vertex. Spin-1 + spin-0, unlike xme's P (two spin-0 states). The paper shows m_phi = 10, 50
      and 80 GeV; here 12 (lowest mass at which a b bbar pair can still form two B mesons), 30 and
      50 GeV.

Massless b quarks and muons in the matrix element, as in xme.py (Pythia restores masses). Full
helicity amplitudes with xme's spinors. Unweighting by hit-or-miss against twice the largest
weight of the first chunk; the number of events above that maximum is reported.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import numpy as np

import xme

VERSION = "mv2 kly 0.1.0"

M_X, G_X = 30.40, 1.78
MLO, MHI = 22.0, 40.0
BENCH = {"III": dict(mB=110.0, GB=3.4), "IV": dict(mB=180.0, GB=124.4)}


def chiral(v, a):
    """v - a gamma5 (v = a = 1: 2 P_L; v = 1, a = -1: 2 P_R; a = 0: vector)."""
    return v * xme.ID4 - a * xme.G5


def heavy_amp2(p1, p2, k, zcurs, zw, xops, xw, mB, GB, zva=(1.0, 1.0), xva=(1.0, 0.0),
               num_mass=True):
    """Spin-summed |ubar(p1) Gamma v(p2)|^2 for Z -> b bbar X through a heavy quark B:
    Gamma = Xv (p1 + k + m_B) Zv / D1 - Zv (p2 + k - m_B) Xv / D2,
    Zv = slash(Jz)(zv - za g5), Xv = X (xv - xa g5), D = (p + k)^2 - m_B^2 + i m_B Gamma_B.
    With m_B = Gamma_B = 0, zva = (VB, AB), xva = (1, 0) this is xme.quark_amp2."""
    m = mB if num_mass else 0.0
    P1 = xme.slash(p1 + k) + m * xme.ID4
    P2 = xme.slash(p2 + k) - m * xme.ID4
    D1 = (xme.mdot(p1 + k, p1 + k) - mB * mB + 1j * mB * GB)[:, None, None]
    D2 = (xme.mdot(p2 + k, p2 + k) - mB * mB + 1j * mB * GB)[:, None, None]
    U = xme.spinors(p1)
    V = xme.spinors(p2)
    Ubar = xme.bar(U)
    ZC = chiral(*zva)
    XC = chiral(*xva)
    tot = np.zeros(p1.shape[0])
    for Jz, wz in zip(zcurs, zw):
        Zv = xme.slash(Jz) @ ZC
        for X, wx in zip(xops, xw):
            Xv = X @ XC
            G = (Xv @ P1 @ Zv) / D1 - (Zv @ P2 @ Xv) / D2
            A = np.einsum('nhi,nij,nkj->nhk', Ubar, G, V)
            tot += wz * wx * np.sum(np.abs(A) ** 2, axis=(1, 2))
    return tot


def generate_heavy(n_target, rng, mB=110.0, GB=3.4, zva=(1.0, 1.0), xva=(1.0, 0.0), M=M_X, G=G_X,
                   mlo=MLO, mhi=MHI, chunk=50000, sqrt_s=xme.SQRT_S, max_chunks=400):
    """Unweighted e+e- -> Z -> b(p1) bbar(p2) Z'(-> mu-(q1) mu+(q2)) events of model B.
    Phase space as xme.generate_radiation (flat Dalitz plot x Breit-Wigner in m^2)."""
    pem, pep = xme.beams(sqrt_s)
    zc, zw = xme.beam_currents(pem, pep)
    acc = {'p1': [], 'p2': [], 'q1': [], 'q2': []}
    nacc = nover = ntried = 0
    wmax = None
    for _ in range(max_chunks):
        m2 = xme.sample_bw_m2(chunk, M, G, mlo, mhi, rng)
        m = np.sqrt(m2)
        Emax = (sqrt_s ** 2 - m2) / (2 * sqrt_s)
        E1 = rng.uniform(0, 1, chunk) * Emax
        E2 = rng.uniform(0, 1, chunk) * Emax
        p1, p2, k, valid = xme.three_body(E1, E2, m, sqrt_s)
        idx = np.nonzero(valid)[0]
        ntried += chunk
        if len(idx) == 0:
            continue
        R = xme.random_rotations(len(idx), rng)
        p1 = xme.rotate(p1[idx], R)
        p2 = xme.rotate(p2[idx], R)
        k = xme.rotate(k[idx], R)
        q1, q2 = xme.decay_massless(k, m[idx], rng)
        xo, xw = xme.muon_ops(q1, q2)
        w = heavy_amp2(p1, p2, q1 + q2, zc, zw, xo, xw, mB, GB, zva, xva) * Emax[idx] ** 2
        if wmax is None:
            wmax = 2.0 * float(w.max())
        nover += int(np.sum(w > wmax))
        keep = rng.uniform(0, 1, len(idx)) * wmax < w
        for key, arr in (('p1', p1), ('p2', p2), ('q1', q1), ('q2', q2)):
            acc[key].append(arr[keep])
        nacc += int(keep.sum())
        if nacc >= n_target:
            break
    out = {key: np.concatenate(v)[:n_target] for key, v in acc.items()}
    out['stats'] = dict(model='B', mB=mB, GB=GB, zva=list(zva), xva=list(xva), ntried=ntried,
                        nacc=nacc, wmax=wmax, n_over=nover, eff=nacc / max(ntried, 1))
    return out


def zs_amp2(Jes, q1, q2):
    """Sum over beam and muon helicities of |Je . Jmu|^2 for Z -> Z' phi, Z' -> mu-(q1) mu+(q2)
    (Z_mu Z'^mu phi vertex; the k k terms of both propagators vanish against conserved currents)."""
    u = xme.spinors(q1)
    v = xme.spinors(q2)
    tot = np.zeros(q1.shape[0])
    for a in range(2):
        for b in range(2):
            Jm = xme.current(xme.bar(u[..., a, :]), v[..., b, :])
            for Je in Jes:
                tot += np.abs(xme.mdot(Je, Jm)) ** 2
    return tot


def generate_zs(n_target, rng, m_phi=30.4, M=M_X, G=G_X, mlo=MLO, mhi=MHI, sqrt_s=xme.SQRT_S,
                chunk=40000, max_chunks=400):
    """Unweighted e+e- -> Z -> Z'(-> mu-(q1) mu+(q2)) phi(-> b(p1) bbar(p2)) events of model Q.
    Weight = two-body phase space (p*) x zs_amp2; Z' mass from a Breit-Wigner in m^2."""
    s = sqrt_s ** 2
    pem, pep = xme.beams(sqrt_s)
    Jes, _ = xme.beam_currents(pem, pep)
    out = {'p1': [], 'p2': [], 'q1': [], 'q2': []}
    nacc = nover = ntried = 0
    wmax = None
    for _ in range(max_chunks):
        m2 = xme.sample_bw_m2(chunk, M, G, mlo, mhi, rng)
        lam = xme.kallen(s, m2, m_phi ** 2)
        ok = lam > 0
        ntried += chunk
        m2 = m2[ok]
        nk = len(m2)
        if nk == 0:
            continue
        pst = np.sqrt(lam[ok]) / (2 * sqrt_s)
        d = xme.iso_dirs(nk, rng)
        Ez = (s + m2 - m_phi ** 2) / (2 * sqrt_s)
        Pz = np.concatenate([Ez[:, None], pst[:, None] * d], -1)
        Pp = np.concatenate([(sqrt_s - Ez)[:, None], -pst[:, None] * d], -1)
        q1, q2 = xme.decay_massless(Pz, np.sqrt(m2), rng)
        b1, b2 = xme.decay_massless(Pp, np.full(nk, m_phi), rng)
        w = pst * zs_amp2(Jes, q1, q2)
        if wmax is None:
            wmax = 2.0 * float(w.max())
        nover += int(np.sum(w > wmax))
        keep = rng.uniform(0, 1, nk) * wmax < w
        for key, arr in (('p1', b1), ('p2', b2), ('q1', q1), ('q2', q2)):
            out[key].append(arr[keep])
        nacc += int(keep.sum())
        if nacc >= n_target:
            break
    res = {key: np.concatenate(v)[:n_target] for key, v in out.items()}
    res['stats'] = dict(model='Q', m_phi=m_phi, ntried=ntried, nacc=nacc, wmax=wmax, n_over=nover,
                        eff=nacc / max(ntried, 1))
    return res


# label -> (generator kind, parameters, LHE layout of xme.write_lhe, signal-muon mother id)
MODELS = {
    "B110": ("heavy", dict(mB=110.0, GB=3.4), "V", 32),
    "B180": ("heavy", dict(mB=180.0, GB=124.4), "V", 32),
    "B110L": ("heavy", dict(mB=110.0, GB=3.4, xva=(1.0, 1.0)), "V", 32),
    "Q12": ("zs", dict(m_phi=12.0), "P", 35),
    "Q30": ("zs", dict(m_phi=30.4), "P", 35),
    "Q50": ("zs", dict(m_phi=50.0), "P", 35),
}


def generate(label, n, rng):
    kind, par, _, _ = MODELS[label]
    if kind == "heavy":
        return generate_heavy(n, rng, **par)
    return generate_zs(n, rng, **par)
