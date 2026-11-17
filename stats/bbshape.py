"""bbshape: generator-level shape of the opposite-sign dimuon mass spectrum in Z -> b bbar
(Pythia 8, e+e- at 91.19 GeV), with ALEPH-like cuts (arXiv:1610.06536): both muons p > 2.5 GeV
and |cos theta| < 0.95, at least 5 charged particles, visible missing momentum < 18 GeV.
Muon momenta are smeared with a DELPHI-like resolution sigma(1/p) = 0.0006 (+) 0.008/p GeV^-1.
No b-tag, no detector simulation: this is only a realistic smooth shape for the forecast toys.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import math
import time

import numpy as np


def settings(seed):
    return ["Print:quiet = on", "Next:numberCount = 0", "PDF:lepton = off",
            "PartonLevel:ISR = off", "PartonLevel:MPI = off",
            "ParticleDecays:limitTau0 = on", "ParticleDecays:tau0Max = 10.",
            "Random:setSeed = on", "Random:seed = %d" % seed,
            "Beams:idA = 11", "Beams:idB = -11", "Beams:eCM = 91.1876",
            "WeakSingleBoson:ffbar2gmZ = on", "WeakZ0:gmZmode = 2",
            "23:onMode = off", "23:onIfAny = 5"]


def smear_p4(p4, rng, a=0.0006, b=0.008):
    p3 = p4[1:]
    p = float(np.linalg.norm(p3))
    s = math.hypot(a, b / p)
    inv = 1.0 / p + rng.normal(0.0, s)
    if inv <= 0:
        inv = 1.0 / p
    pn = 1.0 / inv
    q3 = p3 * (pn / p)
    m = 0.1056584
    return np.array([math.sqrt(pn * pn + m * m), q3[0], q3[1], q3[2]])


def mass(a, b):
    P = a + b
    return math.sqrt(max(P[0] ** 2 - P[1] ** 2 - P[2] ** 2 - P[3] ** 2, 0.0))


def generate(n_events, seed, max_seconds=1e9):
    """Returns (masses of OS pairs in 10-60 GeV passing cuts, stats dict)."""
    import pythia8mc
    py = pythia8mc.Pythia()
    for s in settings(seed):
        py.readString(s)
    if not py.init():
        raise RuntimeError("pythia init failed")
    rng = np.random.default_rng(seed + 7)
    t0 = time.time()
    out = []
    nok = 0
    npair_os = 0
    for _ in range(n_events):
        if time.time() - t0 > max_seconds:
            break
        if not py.next():
            continue
        nok += 1
        ev = py.event
        mus = []
        nch = 0
        vis = np.zeros(3)
        for i in range(ev.size()):
            p = ev[i]
            if not p.isFinal():
                continue
            ida = p.idAbs()
            if ida in (12, 14, 16):
                continue
            px, py_, pz = p.px(), p.py(), p.pz()
            pa = math.sqrt(px * px + py_ * py_ + pz * pz)
            cth = pz / pa if pa > 0 else 0.0
            if abs(cth) < 0.98:
                vis += (px, py_, pz)
            if p.charge() != 0 and pa > 0.2 and abs(cth) < 0.95:
                nch += 1
            if ida == 13 and pa > 2.0 and abs(cth) < 0.95:
                mus.append((p.charge(), np.array([p.e(), px, py_, pz])))
        if len(mus) < 2 or nch < 5 or np.linalg.norm(vis) >= 18.0:
            continue
        sm = [(q, smear_p4(v, rng)) for q, v in mus]
        sm = [(q, v) for q, v in sm if np.linalg.norm(v[1:]) > 2.5]
        for i in range(len(sm)):
            for j in range(i + 1, len(sm)):
                if sm[i][0] * sm[j][0] < 0:
                    npair_os += 1
                    m = mass(sm[i][1], sm[j][1])
                    if 10.0 < m < 60.0:
                        out.append(m)
    st = dict(seed=seed, n_generated=nok, n_os_pairs=npair_os, n_10_60=len(out),
              n_15_50=int(sum(1 for m in out if 15 < m < 50)), seconds=round(time.time() - t0, 1))
    return np.array(out), st


def kde_probs(masses, centers, bw=None):
    """Gaussian KDE with reflection at 10 and 60 GeV, evaluated at bin centres, normalised over
    the given bins. Silverman bandwidth unless bw is given."""
    x = np.asarray(masses, float)
    if bw is None:
        bw = 1.06 * np.std(x) * len(x) ** (-0.2)
    pts = np.concatenate([x, 2 * 10.0 - x, 2 * 60.0 - x])
    c = np.asarray(centers, float)
    dens = np.zeros(len(c))
    for k in range(0, len(pts), 4000):
        d = (c[:, None] - pts[None, k:k + 4000]) / bw
        dens += np.exp(-0.5 * d * d).sum(1)
    return dens / dens.sum(), float(bw)
