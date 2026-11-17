"""Tests for xkin (matrix elements, kinematics, jets, LHE). Apache-2.0. MV2 of Munim, Inc."""
import math
import os
import tempfile
import unittest

import numpy as np

import xme
import evana


def rand_config(n, m, rng, sqrt_s=xme.SQRT_S):
    out = []
    while sum(len(o[0]) for o in out) < n:
        Emax = (sqrt_s ** 2 - m ** 2) / (2 * sqrt_s)
        E1 = rng.uniform(0.05, 0.95, 4 * n) * Emax
        E2 = rng.uniform(0.05, 0.95, 4 * n) * Emax
        p1, p2, k, v = xme.three_body(E1, E2, np.full(4 * n, m), sqrt_s)
        out.append((p1[v], p2[v], k[v]))
    p1 = np.concatenate([o[0] for o in out])[:n]
    p2 = np.concatenate([o[1] for o in out])[:n]
    k = np.concatenate([o[2] for o in out])[:n]
    return p1, p2, k


class TestDirac(unittest.TestCase):
    def test_clifford(self):
        g = np.diag(xme.METRIC)
        for a in range(4):
            for b in range(4):
                ac = xme.GAM[a] @ xme.GAM[b] + xme.GAM[b] @ xme.GAM[a]
                self.assertTrue(np.allclose(ac, 2 * g[a, b] * xme.ID4))
            self.assertTrue(np.allclose(xme.GAM[a] @ xme.G5 + xme.G5 @ xme.GAM[a], 0))

    def test_spinors(self):
        rng = np.random.default_rng(1)
        d = xme.iso_dirs(50, rng)
        E = rng.uniform(1, 40, 50)
        p = np.concatenate([E[:, None], E[:, None] * d], -1)
        p = np.vstack([p, [[3.0, 0, 0, -3.0], [2.0, 0, 0, 2.0]]])
        S = xme.spinors(p)
        ps = xme.slash(p)
        for h in range(2):
            self.assertTrue(np.allclose(np.einsum('nij,nj->ni', ps, S[:, h, :]), 0, atol=1e-10))
        ssum = sum(np.einsum('ni,nj->nij', S[:, h, :], xme.bar(S[:, h, :])) for h in range(2))
        self.assertTrue(np.allclose(ssum, ps, atol=1e-10))

    def test_scalar_decay_sum_is_2m2(self):
        # independent of the trace identity: explicit spinors, random boosted decays
        rng = np.random.default_rng(11)
        m = rng.uniform(20.0, 42.0, 200)
        d = xme.iso_dirs(200, rng)
        pk = rng.uniform(0.0, 40.0, 200)[:, None] * d
        K = np.concatenate([np.sqrt(np.sum(pk ** 2, -1) + m ** 2)[:, None], pk], -1)
        q1, q2 = xme.decay_massless(K, m, rng)
        self.assertTrue(np.allclose(xme.scalar_decay_sum(q1, q2), 2.0 * m ** 2, rtol=1e-9))


class TestME(unittest.TestCase):
    def test_ward_identity(self):
        rng = np.random.default_rng(2)
        p1, p2, k = rand_config(200, 30.4, rng)
        R = xme.random_rotations(len(p1), rng)
        p1, p2, k = xme.rotate(p1, R), xme.rotate(p2, R), xme.rotate(k, R)
        q1, q2 = xme.decay_massless(k, np.full(len(k), 30.4), rng)
        zc, zw = xme.beam_currents(*xme.beams())
        good = xme.radiation_weight('V', p1, p2, q1, q2, zc, zw)
        # replace the X current by its momentum: the amplitude must vanish
        kk = xme.quark_amp2(p1, p2, k, zc, zw, [xme.slash(k + 0j)], [1.0])
        scale = xme.quark_amp2(p1, p2, k, zc, zw, [xme.slash(np.array([30.4, 0, 0, 0]) + 0j)], [1.0])
        self.assertTrue(np.all(good > 0))
        self.assertLess(float(np.max(kk / scale)), 1e-18)

    def test_ert_massless_limit(self):
        rng = np.random.default_rng(3)
        m = 1e-4
        p1, p2, k = rand_config(300, m, rng)
        x1 = 2 * p1[:, 0] / xme.SQRT_S
        x2 = 2 * p2[:, 0] / xme.SQRT_S
        sel = (x1 < 0.97) & (x2 < 0.97) & (x1 + x2 > 1.05)
        pol = [xme.slash(e) for e in xme.POL_BASIS]
        for vb, ab in ((1.0, 0.0), (0.3, 0.7)):
            me = xme.quark_amp2(p1[sel], p2[sel], k[sel], xme.POL_BASIS, xme.POL_W, pol, xme.POL_W, vb, ab)
            ert = (x1[sel] ** 2 + x2[sel] ** 2) / ((1 - x1[sel]) * (1 - x2[sel]))
            r = me / ert
            self.assertLess(float(np.std(r) / np.mean(r)), 1e-4, (vb, ab))

    def test_lorentz_invariance(self):
        rng = np.random.default_rng(4)
        p1, p2, k = rand_config(100, 30.4, rng)
        R = xme.random_rotations(len(p1), rng)
        p1, p2, k = xme.rotate(p1, R), xme.rotate(p2, R), xme.rotate(k, R)
        q1, q2 = xme.decay_massless(k, np.full(len(k), 30.4), rng)
        pem, pep = xme.beams()
        for model in ('V', 'S'):
            zc, zw = xme.beam_currents(pem, pep)
            w0 = xme.radiation_weight(model, p1, p2, q1, q2, zc, zw)
            beta = np.array([[0.3, -0.2, 0.25]])
            B = lambda p: xme.boost(p, np.repeat(beta, len(p), 0))
            zc2, zw2 = xme.beam_currents(B(pem[None, :])[0], B(pep[None, :])[0])
            w1 = xme.radiation_weight(model, B(p1), B(p2), B(q1), B(q2), zc2, zw2)
            self.assertTrue(np.allclose(w0, w1, rtol=1e-8), model)

    def test_s_weight_carries_decay_factor(self):
        # 0.2.0: S = (scalar emission off the b line) x sum|ubar(q1) v(q2)|^2
        rng = np.random.default_rng(12)
        p1, p2, k = rand_config(100, 26.0, rng)
        q1, q2 = xme.decay_massless(k, np.full(len(k), 26.0), rng)
        zc, zw = xme.beam_currents(*xme.beams())
        prod = xme.quark_amp2(p1, p2, k, zc, zw, [xme.ID4], [1.0])
        w = xme.radiation_weight('S', p1, p2, q1, q2, zc, zw)
        self.assertTrue(np.allclose(w, prod * xme.scalar_decay_sum(q1, q2), rtol=1e-9))
        self.assertTrue(np.allclose(w / prod, 2.0 * 26.0 ** 2, rtol=1e-9))


class TestGeneration(unittest.TestCase):
    def check(self, ev, lo=22.0, hi=40.0):
        tot = ev['p1'] + ev['p2'] + ev['q1'] + ev['q2']
        self.assertTrue(np.allclose(tot[:, 0], xme.SQRT_S, atol=1e-8))
        self.assertTrue(np.allclose(tot[:, 1:], 0, atol=1e-8))
        for key in ('p1', 'p2', 'q1', 'q2'):
            self.assertTrue(np.allclose(xme.mdot(ev[key], ev[key]), 0, atol=1e-6))
        m = np.sqrt(xme.mdot(ev['q1'] + ev['q2'], ev['q1'] + ev['q2']))
        self.assertTrue(np.all((m > lo - 1e-6) & (m < hi + 1e-6)))
        self.assertLess(abs(np.median(m) - 30.4), 1.0)

    def test_radiation(self):
        rng = np.random.default_rng(5)
        for model in ('V', 'S'):
            ev = xme.generate_radiation(model, 300, rng, chunk=20000)
            self.assertEqual(len(ev['p1']), 300)
            self.check(ev)
            self.assertEqual(ev['stats']['n_over'], 0)

    def test_pair(self):
        rng = np.random.default_rng(6)
        ev = xme.generate_pair(500, rng)
        self.check(ev)
        mbb = np.sqrt(xme.mdot(ev['p1'] + ev['p2'], ev['p1'] + ev['p2']))
        self.assertTrue(np.allclose(mbb, 30.4, atol=1e-6))
        # sin^2 distribution of the h direction: <cos^2> = 1/5
        h = ev['q1'] + ev['q2']
        c = h[:, 3] / np.linalg.norm(h[:, 1:], axis=1)
        self.assertLess(abs(np.mean(c ** 2) - 0.2), 0.03)

    def test_pair_accept_prob_is_cubic(self):
        self.assertAlmostEqual(float(xme.pair_accept_prob(0.5, 1.0)), 0.125, places=12)
        self.assertAlmostEqual(float(xme.pair_accept_prob(2.0, 2.0)), 1.0, places=12)
        pmax = float(xme.pair_pstar(22.0 ** 2, 30.4))
        # Z -> h A momentum at m_h = m_A = 30.4: sqrt(s/4 - m^2)
        self.assertAlmostEqual(float(xme.pair_pstar(30.4 ** 2, 30.4)),
                               math.sqrt(xme.SQRT_S ** 2 / 4 - 30.4 ** 2), places=9)
        self.assertGreater(pmax, float(xme.pair_pstar(30.4 ** 2, 30.4)))

    def test_pair_lineshape_follows_bw_times_pstar_cubed(self):
        M, G, MA, lo, hi = 30.40, 1.78, 30.40, 22.0, 40.0
        n_grid = 200000
        dx = (hi ** 2 - lo ** 2) / n_grid
        x = lo ** 2 + (np.arange(n_grid) + 0.5) * dx
        f = xme.pair_pstar(x, MA) ** 3 / ((x - M ** 2) ** 2 + (M * G) ** 2)
        mean_expected = float(np.sum(np.sqrt(x) * f) / np.sum(f))
        rng = np.random.default_rng(13)
        ev = xme.generate_pair(20000, rng, M=M, G=G, MA=MA, mlo=lo, mhi=hi)
        m = np.sqrt(xme.mdot(ev['q1'] + ev['q2'], ev['q1'] + ev['q2']))
        se = float(np.std(m)) / math.sqrt(len(m))
        self.assertLess(abs(float(np.mean(m)) - mean_expected), 4.0 * se,
                        (float(np.mean(m)), mean_expected, se))

    def test_lhe(self):
        rng = np.random.default_rng(7)
        ev = xme.generate_radiation('V', 20, rng, chunk=20000)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 't.lhe')
            xme.write_lhe(path, 'V', ev)
            txt = open(path).read()
        self.assertEqual(txt.count('<event>'), 20)
        self.assertIn(xme.VERSION, txt)
        block = txt.split('<event>')[1].split('</event>')[0].strip().splitlines()
        self.assertEqual(int(block[0].split()[0]), 8)
        fin = [l.split() for l in block[1:] if l.split()[1] == '1']
        pz = sum(float(f[8]) for f in fin)
        e = sum(float(f[9]) for f in fin)
        self.assertAlmostEqual(e, xme.SQRT_S, places=5)
        self.assertAlmostEqual(pz, 0.0, places=5)


class TestEvana(unittest.TestCase):
    def test_jets_and_thrust(self):
        rng = np.random.default_rng(8)
        parts = []
        for axis in (np.array([0.6, 0.0, 0.8]), np.array([-0.6, 0.0, -0.8])):
            for _ in range(10):
                d = evana.unit(axis + 0.05 * rng.normal(size=3))
                E = rng.uniform(1, 8)
                parts.append(np.concatenate([[E], E * d]))
        p4 = np.array(parts)
        jets = evana.ee_genkt(p4, 0.4)
        self.assertEqual(len(jets), 2)
        self.assertAlmostEqual(jets[:, 0].sum(), p4[:, 0].sum(), places=8)
        ax, t = evana.thrust_axis(p4[:, 1:])
        self.assertGreater(abs(ax @ np.array([0.6, 0, 0.8])), 0.99)
        self.assertGreater(t, 0.95)

    def test_cos_theta_star(self):
        # mu- emitted along the flight direction in the rest frame -> cos = +1
        m = 30.0
        a = np.array([m / 2, 0, 0, m / 2])
        b = np.array([m / 2, 0, 0, -m / 2])
        beta = np.array([[0.0, 0.0, 0.5]])
        A = xme.boost(a[None, :], beta)[0]
        Bm = xme.boost(b[None, :], beta)[0]
        self.assertAlmostEqual(evana.cos_theta_star(A, Bm), 1.0, places=8)
        self.assertAlmostEqual(evana.cos_theta_star(Bm, A), -1.0, places=8)
        self.assertAlmostEqual(evana.minkowski_mass(A + Bm), m, places=8)

    def test_hemi_angle(self):
        jets = np.array([[20.0, 0, 0, 20.0], [5.0, 0, 5.0, 0.0], [18.0, 0, 0, -18.0]])
        t = np.array([0, 0, 1.0])
        mu = evana.unit(np.array([0.0, math.sin(math.radians(10)), math.cos(math.radians(10))]))
        self.assertAlmostEqual(evana.hemi_leading_angle(mu, jets, t), 10.0, places=6)


class TestFadgen(unittest.TestCase):
    def test_round_trip_and_layout(self):
        import fadgen
        import struct
        rng = np.random.default_rng(9)
        events = []
        for n in (3, 7):
            K = rng.integers(-5, 30, size=(n, 5)).astype(np.int32)
            P = rng.normal(size=(n, 5)).astype(np.float32)
            V = rng.normal(size=(n, 5)).astype(np.float32)
            events.append((K, P, V))
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'f.fadgen')
            with open(path, 'wb') as f:
                for K, P, V in events:
                    fadgen.write_event(f, K, P, V)
                fadgen.write_end(f)
            raw = open(path, 'rb').read()
            back = list(fadgen.read_fadgen(path))
        # first record: reclen = 4 + 60*3, N = 3, first particle K(1) right after
        self.assertEqual(struct.unpack('<iii', raw[:12]), (184, 3, int(events[0][0][0, 0])))
        # particle block = K(5) int32 then P(5) float32 then V(5) float32
        self.assertAlmostEqual(struct.unpack('<f', raw[8 + 20:8 + 24])[0], float(events[0][1][0, 0]), places=6)
        self.assertEqual(raw[-12:], struct.pack('<iii', 4, 0, 4))
        self.assertEqual(len(raw), (8 + 180 + 4) + (8 + 420 + 4) + 12)
        self.assertEqual(len(back), 2)
        for (K, P, V), (K2, P2, V2) in zip(events, back):
            self.assertTrue(np.array_equal(K, K2))
            self.assertTrue(np.array_equal(P, P2))
            self.assertTrue(np.array_equal(V, V2))


if __name__ == '__main__':
    unittest.main()
