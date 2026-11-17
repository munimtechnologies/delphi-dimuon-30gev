"""evana: generator-level event analysis in the style of the ALEPH 30 GeV dimuon study
(arXiv:1610.06536 sec. 4.2/4.4/4.7): thrust hemispheres, e+e- anti-kt jets built without
leptons, muon - leading-jet angles, cos(theta*), muon multiplicity, missing momentum.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import math
import numpy as np

NU = (12, 14, 16)
RS = (0.4, 0.7, 1.0)


def unit(v):
    v = np.asarray(v, float)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n > 0, n, 1.0)


def angle_deg(u, v):
    return float(np.degrees(np.arccos(np.clip(np.dot(u, v), -1.0, 1.0))))


def thrust_axis(p3):
    p3 = np.asarray(p3, float).reshape(-1, 3)
    if len(p3) == 0:
        return np.array([0.0, 0.0, 1.0]), 0.0
    mags = np.linalg.norm(p3, axis=1)
    tot = mags.sum()
    if tot <= 0:
        return np.array([0.0, 0.0, 1.0]), 0.0
    order = np.argsort(-mags)[:6]
    seeds = [p3[i] for i in order]
    for a in range(min(3, len(order))):
        for b in range(a + 1, min(4, len(order))):
            seeds.append(p3[order[a]] + p3[order[b]])
            seeds.append(p3[order[a]] - p3[order[b]])
    best_n, best_t = np.array([0.0, 0.0, 1.0]), -1.0
    for s in seeds:
        ns = np.linalg.norm(s)
        if ns <= 0:
            continue
        n = s / ns
        for _ in range(40):
            sg = np.sign(p3 @ n)
            sg[sg == 0] = 1.0
            nn = (sg[:, None] * p3).sum(0)
            nrm = np.linalg.norm(nn)
            if nrm <= 0:
                break
            nn = nn / nrm
            done = np.allclose(nn, n, atol=1e-12)
            n = nn
            if done:
                break
        t = np.abs(p3 @ n).sum() / tot
        if t > best_t:
            best_n, best_t = n, t
    return best_n, float(best_t)


def ee_genkt(p4, R, p=-1.0):
    """FastJet-style generalised kt for e+e- (ee_genkt), E-scheme. p=-1 is anti-kt.
    d_ij = min(E_i^2p, E_j^2p)(1-cos theta_ij)/(1-cos R), d_iB = E_i^2p.
    Returns jets [E,px,py,pz] sorted by energy."""
    act = np.array(p4, float).reshape(-1, 4)
    jets = []
    denom = 1.0 - math.cos(R)
    while len(act) > 0:
        if len(act) == 1:
            jets.append(act[0].copy())
            break
        E = act[:, 0]
        u = unit(act[:, 1:])
        Ep = E ** (2 * p)
        cosij = np.clip(u @ u.T, -1.0, 1.0)
        dij = np.minimum(Ep[:, None], Ep[None, :]) * (1.0 - cosij) / denom
        np.fill_diagonal(dij, np.inf)
        flat = int(np.argmin(dij))
        i, j = divmod(flat, len(act))
        iB = int(np.argmin(Ep))
        if dij[i, j] < Ep[iB]:
            act[i] = act[i] + act[j]
            act = np.delete(act, j, axis=0)
        else:
            jets.append(act[iB].copy())
            act = np.delete(act, iB, axis=0)
    jets = np.array(jets, float).reshape(-1, 4)
    return jets[np.argsort(-jets[:, 0])]


def hemi_leading_angle(umu, jets, taxis, emin=1.0):
    """Angle between a muon and the most energetic jet in the muon's thrust hemisphere."""
    if len(jets) == 0:
        return float('nan')
    uj = unit(jets[:, 1:])
    smu = 1.0 if float(umu @ taxis) >= 0 else -1.0
    sj = np.where(uj @ taxis >= 0, 1.0, -1.0)
    m = (sj == smu) & (jets[:, 0] > emin)
    if not m.any():
        return float('nan')
    cand = np.nonzero(m)[0]
    k = cand[np.argmax(jets[cand, 0])]
    return angle_deg(umu, uj[k])


def nearest_jet_angle(umu, jets, emin=3.0):
    m = jets[:, 0] > emin if len(jets) else np.zeros(0, bool)
    if not np.any(m):
        return float('nan')
    uj = unit(jets[m, 1:])
    return float(np.degrees(np.arccos(np.clip(uj @ umu, -1, 1))).min())


def minkowski_mass(P):
    return math.sqrt(max(P[0] ** 2 - P[1] ** 2 - P[2] ** 2 - P[3] ** 2, 0.0))


def cos_theta_star(p_neg, p_pos):
    """cos of the mu- direction in the dimuon rest frame w.r.t. the dimuon flight direction."""
    P = p_neg + p_pos
    beta = P[1:] / P[0]
    b2 = float(beta @ beta)
    if b2 <= 0:
        return float('nan')
    g = 1.0 / math.sqrt(1.0 - b2)
    bp = float(beta @ p_neg[1:])
    # boost by -beta
    sp = p_neg[1:] + ((g - 1.0) * bp / b2 - g * p_neg[0]) * beta
    return float(unit(sp) @ unit(P[1:]))


def event_quantities(ids, p4, charge, Rs=RS):
    """Event-level quantities from final-state particles (generator level)."""
    ids = np.asarray(ids)
    p4 = np.asarray(p4, float).reshape(-1, 4)
    charge = np.asarray(charge, float)
    aid = np.abs(ids)
    vis = ~np.isin(aid, NU)
    p3 = p4[:, 1:]
    pabs = np.linalg.norm(p3, axis=1)
    cth = np.where(pabs > 0, p3[:, 2] / np.where(pabs > 0, pabs, 1.0), 0.0)
    acc98 = np.abs(cth) < 0.98
    nch = int(np.sum((charge != 0) & (pabs > 0.2) & (np.abs(cth) < 0.95)))
    pmiss = float(np.linalg.norm(p3[vis].sum(0))) if vis.any() else 0.0
    jet_in = vis & acc98 & ~np.isin(aid, (11, 13))
    taxis, thr = thrust_axis(p3[vis & acc98])
    jets = {R: ee_genkt(p4[jet_in], R) for R in Rs}
    return dict(nch=nch, pmiss=pmiss, taxis=taxis, thrust=thr, jets=jets, pabs=pabs, cth=cth,
                vis=vis, p4=p4, ids=ids, charge=charge)


def muon_info(evq, i, Rs=RS, cone_deg=15.0):
    p4 = evq['p4']
    u = unit(p4[i, 1:])
    pt = math.hypot(p4[i, 1], p4[i, 2])
    vis = evq['vis'].copy()
    vis[i] = False
    others = p4[vis]
    if len(others):
        ang = np.degrees(np.arccos(np.clip(unit(others[:, 1:]) @ u, -1, 1)))
        cone = float(others[ang < cone_deg, 0].sum())
    else:
        cone = 0.0
    info = dict(i=int(i), q=float(evq['charge'][i]), p=float(evq['pabs'][i]), pt=pt,
                cth=float(evq['cth'][i]), cone=cone)
    for R in Rs:
        info['hemi_%.1f' % R] = hemi_leading_angle(u, evq['jets'][R], evq['taxis'])
    info['near'] = nearest_jet_angle(u, evq['jets'][Rs[0]])
    return info


def muon_pass(mu, use_pt=False, pcut=2.5, ccut=0.95):
    mom = mu['pt'] if use_pt else mu['p']
    return (mom > pcut) and (abs(mu['cth']) < ccut)


def pair_row(evq, ma, mb, Rs=RS):
    p4 = evq['p4']
    pa, pb = p4[ma['i']], p4[mb['i']]
    m = minkowski_mass(pa + pb)
    neg, pos = (pa, pb) if ma['q'] < 0 else (pb, pa)
    row = dict(m=m, cst=cos_theta_star(neg, pos), nch=evq['nch'], pmiss=evq['pmiss'],
               pass_p=bool(muon_pass(ma) and muon_pass(mb)),
               pass_pt=bool(muon_pass(ma, True) and muon_pass(mb, True)),
               cone_max=max(ma['cone'], mb['cone']))
    for R in Rs:
        key = 'hemi_%.1f' % R
        a, b = ma[key], mb[key]
        if math.isnan(a) or math.isnan(b):
            row['amin_%.1f' % R] = float('nan')
            row['aoth_%.1f' % R] = float('nan')
        else:
            row['amin_%.1f' % R] = min(a, b)
            row['aoth_%.1f' % R] = max(a, b)
    a, b = ma['near'], mb['near']
    row['near_min'] = float('nan') if (math.isnan(a) or math.isnan(b)) else min(a, b)
    row['near_oth'] = float('nan') if (math.isnan(a) or math.isnan(b)) else max(a, b)
    return row
