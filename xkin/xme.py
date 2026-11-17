"""xme: tree-level matrix elements and unweighted parton-level events for three
hypotheses behind the ALEPH 30 GeV dimuon excess (arXiv:1610.06536):

  V : e+ e- -> Z -> b bbar X,  X -> mu+ mu-, X a vector radiated off the b line
  S : e+ e- -> Z -> b bbar phi, phi -> mu+ mu-, phi a scalar radiated off the b line
  P : e+ e- -> Z -> h A,  h -> mu+ mu-, A -> b bbar  (two spin-0 states, Lane-Pritchett type)

Massless b quarks and muons in the matrix element (m_b^2/m_X^2 ~ 2.5 %); Pythia 8 restores
masses when it reads the events. Full spin correlations from explicit helicity spinors.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import numpy as np

SQRT_S = 91.1876
SW2 = 0.23122
VE, AE = -0.5 + 2.0 * SW2, -0.5
VB, AB = -0.5 + (2.0 / 3.0) * SW2, -0.5

_I2 = np.eye(2, dtype=complex)
_Z2 = np.zeros((2, 2), dtype=complex)
_SX = np.array([[0, 1], [1, 0]], dtype=complex)
_SY = np.array([[0, -1j], [1j, 0]], dtype=complex)
_SZ = np.array([[1, 0], [0, -1]], dtype=complex)


def _blk(a, b, c, d):
    return np.block([[a, b], [c, d]])


# Dirac representation, gamma^mu with upper index
GAM = np.array([_blk(_I2, _Z2, _Z2, -_I2), _blk(_Z2, _SX, -_SX, _Z2),
                _blk(_Z2, _SY, -_SY, _Z2), _blk(_Z2, _SZ, -_SZ, _Z2)])
G5 = _blk(_Z2, _I2, _I2, _Z2)
ID4 = np.eye(4, dtype=complex)
METRIC = np.array([1.0, -1.0, -1.0, -1.0])

POL_BASIS = [np.eye(4, dtype=complex)[m] for m in range(4)]
POL_W = [-1.0, 1.0, 1.0, 1.0]  # sum over polarisations -> -g_{mu nu}


def mdot(a, b):
    return a[..., 0] * b[..., 0] - a[..., 1] * b[..., 1] - a[..., 2] * b[..., 2] - a[..., 3] * b[..., 3]


def slash(p):
    """p_mu gamma^mu for contravariant p (real or complex), shape (...,4) -> (...,4,4)."""
    p = np.asarray(p)
    return np.einsum('...m,mij->...ij', p * METRIC, GAM)


def spinors(p):
    """Helicity spinors (+,-) of a massless momentum p (...,4): returns (...,2,4).
    For massless fermions the same pair spans both u and v (p-slash psi = 0) and
    sum_h psi psibar = p-slash, which is all a spin-summed |M|^2 needs."""
    p = np.asarray(p, dtype=float)
    px, py, pz = p[..., 1], p[..., 2], p[..., 3]
    pp = np.sqrt(px * px + py * py + pz * pz)
    cth = np.clip(pz / np.where(pp > 0, pp, 1.0), -1.0, 1.0)
    th = np.arccos(cth)
    ph = np.arctan2(py, px)
    c = np.cos(th / 2) + 0j
    s = np.sin(th / 2) + 0j
    chip = np.stack([c, np.exp(1j * ph) * s], -1)
    chim = np.stack([-np.exp(-1j * ph) * s, c], -1)
    sq = np.sqrt(pp)[..., None]
    up = sq * np.concatenate([chip, chip], -1)
    um = sq * np.concatenate([chim, -chim], -1)
    return np.stack([up, um], -2)


def bar(psi):
    return np.conj(psi) @ GAM[0]


def current(psibar_row, psi, cv=1.0, ca=0.0):
    """J^mu = psibar gamma^mu (cv - ca gamma5) psi."""
    M = np.einsum('mij,jk->mik', GAM, cv * ID4 - ca * G5)
    return np.einsum('...i,mij,...j->...m', psibar_row, M, psi)


def beam_currents(pem, pep, ve=VE, ae=AE):
    """Z currents vbar(e+) gamma^mu (ve - ae g5) u(e-) for the 4 helicity pairs."""
    u = spinors(pem)
    v = spinors(pep)
    out = []
    for a in range(2):
        for b in range(2):
            out.append(current(bar(v[..., b, :]), u[..., a, :], ve, ae))
    return out, [1.0] * 4


def muon_ops(q1, q2):
    """slash(J) with J^nu = ubar(mu-) gamma^nu v(mu+), 4 helicity pairs."""
    u = spinors(q1)
    v = spinors(q2)
    ops = []
    for a in range(2):
        for b in range(2):
            ops.append(slash(current(bar(u[..., a, :]), v[..., b, :])))
    return ops, [1.0] * 4


def quark_amp2(p1, p2, k, zcurs, zw, xops, xw, vb=VB, ab=AB):
    """Spin-summed |ubar(p1) Gamma v(p2)|^2, X (momentum k) emitted from the quark line:
    Gamma = X (p1+k)/D1 Zv - Zv (p2+k)/D2 X,  Zv = slash(Jz)(vb - ab g5).
    zcurs/xops: lists of Z currents and X vertex matrices, each with a weight."""
    P1 = slash(p1 + k)
    P2 = slash(p2 + k)
    D1 = mdot(p1 + k, p1 + k)[:, None, None]
    D2 = mdot(p2 + k, p2 + k)[:, None, None]
    U = spinors(p1)
    V = spinors(p2)
    Ubar = bar(U)
    VA = vb * ID4 - ab * G5
    tot = np.zeros(p1.shape[0])
    for Jz, wz in zip(zcurs, zw):
        Zv = slash(Jz) @ VA
        for X, wx in zip(xops, xw):
            G = (X @ P1 @ Zv) / D1 - (Zv @ P2 @ X) / D2
            A = np.einsum('nhi,nij,nkj->nhk', Ubar, G, V)
            tot += wz * wx * np.sum(np.abs(A) ** 2, axis=(1, 2))
    return tot


def dms_massive_gluon(x1, x2, eps):
    """Diagnostic only: unpolarised Z/gamma* -> q qbar + massive vector, eps = m^2/s
    (form used in the dispersive approach, Dokshitzer-Marchesini-Salam 1996)."""
    return (((x1 + eps) ** 2 + (x2 + eps) ** 2) / ((1 - x1) * (1 - x2))
            - eps / (1 - x1) ** 2 - eps / (1 - x2) ** 2)


# ----------------------------------------------------------------- kinematics
def three_body(E1, E2, m, sqrt_s=SQRT_S):
    """Z rest frame, massless 1 and 2, mass-m particle 3. Returns p1, p2, k, valid."""
    E1 = np.asarray(E1, float)
    E2 = np.asarray(E2, float)
    m = np.broadcast_to(np.asarray(m, float), E1.shape)
    E3 = sqrt_s - E1 - E2
    p3sq = E3 ** 2 - m ** 2
    den = 2 * E1 * E2
    c12 = (p3sq - E1 ** 2 - E2 ** 2) / np.where(den > 0, den, 1.0)
    valid = (E3 >= m) & (np.abs(c12) <= 1) & (E1 > 0) & (E2 > 0)
    c12 = np.clip(c12, -1, 1)
    s12 = np.sqrt(1 - c12 ** 2)
    z = np.zeros_like(E1)
    p1 = np.stack([E1, z, z, E1], -1)
    p2 = np.stack([E2, E2 * s12, z, E2 * c12], -1)
    k = np.stack([E3, -(p1[:, 1] + p2[:, 1]), -(p1[:, 2] + p2[:, 2]), -(p1[:, 3] + p2[:, 3])], -1)
    return p1, p2, k, valid


def random_rotations(n, rng):
    q = rng.normal(size=(n, 4))
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    w, x, y, z = q.T
    return np.stack([
        np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], -1),
        np.stack([2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], -1),
        np.stack([2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)], -1)], -2)


def rotate(p, R):
    out = p.copy()
    out[:, 1:] = np.einsum('nij,nj->ni', R, p[:, 1:])
    return out


def boost(p, beta):
    """Boost 4-vectors p (n,4) by velocity beta (n,3) (rest frame -> frame where it moves)."""
    b2 = np.sum(beta ** 2, -1)
    g = 1.0 / np.sqrt(1.0 - b2)
    bp = np.sum(beta * p[:, 1:], -1)
    g2 = np.where(b2 > 0, (g - 1) / np.where(b2 > 0, b2, 1.0), 0.0)
    E = g * (p[:, 0] + bp)
    sp = p[:, 1:] + (g2 * bp + g * p[:, 0])[:, None] * beta
    return np.concatenate([E[:, None], sp], -1)


def iso_dirs(n, rng):
    c = rng.uniform(-1, 1, n)
    ph = rng.uniform(0, 2 * np.pi, n)
    s = np.sqrt(1 - c * c)
    return np.stack([s * np.cos(ph), s * np.sin(ph), c], -1)


def decay_massless(P, m, rng):
    """Isotropic two-body decay of P (n,4) of mass m into massless particles."""
    n = P.shape[0]
    d = iso_dirs(n, rng)
    h = (np.asarray(m) / 2.0)[:, None]
    a = np.concatenate([h, h * d], -1)
    b = np.concatenate([h, -h * d], -1)
    beta = P[:, 1:] / P[:, 0:1]
    return boost(a, beta), boost(b, beta)


def sample_bw_m2(n, M, G, mlo, mhi, rng):
    a = np.arctan((mlo ** 2 - M ** 2) / (M * G))
    b = np.arctan((mhi ** 2 - M ** 2) / (M * G))
    t = rng.uniform(a, b, n)
    return M ** 2 + M * G * np.tan(t)


def beams(sqrt_s=SQRT_S):
    E = sqrt_s / 2
    return np.array([E, 0, 0, E]), np.array([E, 0, 0, -E])


def radiation_weight(model, p1, p2, q1, q2, zc, zw):
    k = q1 + q2
    if model == 'V':
        xo, xw = muon_ops(q1, q2)
    elif model == 'S':
        xo, xw = [ID4], [1.0]
    else:
        raise ValueError(model)
    return quark_amp2(p1, p2, k, zc, zw, xo, xw, VB, AB)


def generate_radiation(model, n_target, rng, M=30.40, G=1.78, mlo=22.0, mhi=40.0,
                       chunk=50000, sqrt_s=SQRT_S, max_chunks=400):
    """Unweighted e+e- -> Z -> b(p1) bbar(p2) X(-> mu-(q1) mu+(q2)) events."""
    pem, pep = beams(sqrt_s)
    zc, zw = beam_currents(pem, pep)
    acc = {'p1': [], 'p2': [], 'q1': [], 'q2': []}
    nacc = 0
    wmax = None
    nover = 0
    ntried = 0
    for _ in range(max_chunks):
        m2 = sample_bw_m2(chunk, M, G, mlo, mhi, rng)
        m = np.sqrt(m2)
        Emax = (sqrt_s ** 2 - m2) / (2 * sqrt_s)
        E1 = rng.uniform(0, 1, chunk) * Emax
        E2 = rng.uniform(0, 1, chunk) * Emax
        p1, p2, k, valid = three_body(E1, E2, m, sqrt_s)
        idx = np.nonzero(valid)[0]
        ntried += chunk
        if len(idx) == 0:
            continue
        R = random_rotations(len(idx), rng)
        p1 = rotate(p1[idx], R)
        p2 = rotate(p2[idx], R)
        k = rotate(k[idx], R)
        q1, q2 = decay_massless(k, m[idx], rng)
        w = radiation_weight(model, p1, p2, q1, q2, zc, zw) * Emax[idx] ** 2
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
    out['stats'] = dict(model=model, ntried=ntried, nacc=nacc, wmax=wmax, n_over=nover,
                        eff=nacc / max(ntried, 1))
    return out


def kallen(a, b, c):
    return a * a + b * b + c * c - 2 * a * b - 2 * a * c - 2 * b * c


def generate_pair(n_target, rng, M=30.40, G=1.78, MA=30.40, mlo=22.0, mhi=40.0, sqrt_s=SQRT_S):
    """Unweighted e+e- -> Z -> h A events, h -> mu- mu+ (q1,q2), A -> b bbar (p1,p2).
    Z -> two spin-0 states: dN/dcos(theta) ~ 1 - cos^2(theta) w.r.t. the beam."""
    s = sqrt_s ** 2
    pmax = np.sqrt(kallen(s, mlo ** 2, MA ** 2)) / (2 * sqrt_s)
    out = {'p1': [], 'p2': [], 'q1': [], 'q2': []}
    nacc = 0
    ntried = 0
    while nacc < n_target:
        n = 4 * n_target
        m2 = sample_bw_m2(n, M, G, mlo, mhi, rng)
        lam = kallen(s, m2, MA ** 2)
        ok = lam > 0
        pst = np.sqrt(np.where(ok, lam, 0)) / (2 * sqrt_s)
        c = rng.uniform(-1, 1, n)
        keep = ok & (rng.uniform(0, 1, n) < pst / pmax) & (rng.uniform(0, 1, n) < 1 - c * c)
        ntried += n
        m2 = m2[keep]
        pst = pst[keep]
        c = c[keep]
        nk = len(m2)
        ph = rng.uniform(0, 2 * np.pi, nk)
        sn = np.sqrt(1 - c * c)
        d = np.stack([sn * np.cos(ph), sn * np.sin(ph), c], -1)
        Eh = (s + m2 - MA ** 2) / (2 * sqrt_s)
        EA = sqrt_s - Eh
        Ph = np.concatenate([Eh[:, None], pst[:, None] * d], -1)
        PA = np.concatenate([EA[:, None], -pst[:, None] * d], -1)
        q1, q2 = decay_massless(Ph, np.sqrt(m2), rng)
        b1, b2 = decay_massless(PA, np.full(nk, MA), rng)
        for key, arr in (('p1', b1), ('p2', b2), ('q1', q1), ('q2', q2)):
            out[key].append(arr)
        nacc += nk
    res = {key: np.concatenate(v)[:n_target] for key, v in out.items()}
    res['stats'] = dict(model='P', ntried=ntried, nacc=nacc, eff=nacc / max(ntried, 1))
    return res


# ----------------------------------------------------------------- LHE output
def _mass(p):
    return float(np.sqrt(max(p[0] ** 2 - p[1] ** 2 - p[2] ** 2 - p[3] ** 2, 0.0)))


def lhe_particles(model, p1, p2, q1, q2, sqrt_s=SQRT_S):
    """One event as a list of (id, status, m1, m2, col, acol, p4[E,px,py,pz])."""
    pem, pep = beams(sqrt_s)
    Z = np.array([sqrt_s, 0, 0, 0])
    parts = [(11, -1, 0, 0, 0, 0, pem), (-11, -1, 0, 0, 0, 0, pep), (23, 2, 1, 2, 0, 0, Z)]
    if model in ('V', 'S'):
        xid = 32 if model == 'V' else 35
        parts += [(5, 1, 3, 3, 501, 0, p1), (-5, 1, 3, 3, 0, 501, p2),
                  (xid, 2, 3, 3, 0, 0, q1 + q2),
                  (13, 1, 6, 6, 0, 0, q1), (-13, 1, 6, 6, 0, 0, q2)]
    else:
        parts += [(35, 2, 3, 3, 0, 0, q1 + q2), (36, 2, 3, 3, 0, 0, p1 + p2),
                  (13, 1, 4, 4, 0, 0, q1), (-13, 1, 4, 4, 0, 0, q2),
                  (5, 1, 5, 5, 501, 0, p1), (-5, 1, 5, 5, 0, 501, p2)]
    return parts


def write_lhe(path, model, ev, sqrt_s=SQRT_S):
    E = sqrt_s / 2
    n = len(ev['p1'])
    with open(path, 'w') as f:
        f.write('<LesHouchesEvents version="1.0">\n<!-- xkin model %s, MV2 of Munim, Inc. -->\n' % model)
        f.write('<init>\n 11 -11 %.6f %.6f 0 0 0 0 3 1\n 1.0 0.0 1.0 1\n</init>\n' % (E, E))
        for i in range(n):
            parts = lhe_particles(model, ev['p1'][i], ev['p2'][i], ev['q1'][i], ev['q2'][i], sqrt_s)
            f.write('<event>\n %d 1 1.0 %.6f 0.0078125 0.118\n' % (len(parts), sqrt_s))
            for (pid, st, m1, m2, c1, c2, p) in parts:
                f.write(' %d %d %d %d %d %d %.10e %.10e %.10e %.10e %.10e 0. 9.\n'
                        % (pid, st, m1, m2, c1, c2, p[1], p[2], p[3], p[0], _mass(p)))
            f.write('</event>\n')
        f.write('</LesHouchesEvents>\n')
    return n
