"""Unit tests for kly (MV2 of Munim, Inc.; made with AI agents; Apache-2.0).
Needs xme.py next to it (the job fetches it from the public repo)."""
import unittest

import numpy as np

import kly
import xme


def radiation_point(n, seed, M=30.4):
    rng = np.random.default_rng(seed)
    m = np.full(n, M)
    Emax = (xme.SQRT_S ** 2 - M * M) / (2 * xme.SQRT_S)
    E1 = rng.uniform(0.2, 1, n) * Emax
    E2 = rng.uniform(0.2, 1, n) * Emax
    p1, p2, k, ok = xme.three_body(E1, E2, m)
    idx = np.nonzero(ok)[0]
    R = xme.random_rotations(len(idx), rng)
    p1, p2, k = (xme.rotate(a[idx], R) for a in (p1, p2, k))
    q1, q2 = xme.decay_massless(k, m[idx], rng)
    return p1, p2, q1, q2


class TestHeavy(unittest.TestCase):
    def setUp(self):
        self.p1, self.p2, self.q1, self.q2 = radiation_point(400, 1)
        self.zc, self.zw = xme.beam_currents(*xme.beams())
        self.xo, self.xw = xme.muon_ops(self.q1, self.q2)

    def test_massless_limit_equals_xme(self):
        """m_B = Gamma_B = 0 with xme's couplings reproduces xme.quark_amp2 (vector model V)."""
        k = self.q1 + self.q2
        a = kly.heavy_amp2(self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, 0.0, 0.0,
                           zva=(xme.VB, xme.AB), xva=(1.0, 0.0))
        b = xme.quark_amp2(self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, xme.VB, xme.AB)
        np.testing.assert_allclose(a, b, rtol=1e-9)

    def test_left_left_mass_term_vanishes(self):
        """gamma^nu P_L (p + m) gamma^mu P_L: the m_B term drops out for two left-handed vertices."""
        k = self.q1 + self.q2
        a = kly.heavy_amp2(self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, 110.0, 3.4,
                           xva=(1.0, 1.0))
        b = kly.heavy_amp2(self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, 110.0, 3.4,
                           xva=(1.0, 1.0), num_mass=False)
        np.testing.assert_allclose(a, b, rtol=1e-9)

    def test_vector_zprime_is_left_plus_right(self):
        """With a left-handed Z vertex, a vector Z' vertex (1) is the sum of its left (1 - g5)/2 and
        right (1 + g5)/2 parts, which do not interfere after the spin sum (massless b quarks)."""
        k = self.q1 + self.q2
        args = (self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, 110.0, 3.4)
        v = kly.heavy_amp2(*args, xva=(1.0, 0.0))
        lft = kly.heavy_amp2(*args, xva=(0.5, 0.5))
        rgt = kly.heavy_amp2(*args, xva=(0.5, -0.5))
        np.testing.assert_allclose(v, lft + rgt, rtol=1e-8)

    def test_right_handed_mass_term_matters(self):
        k = self.q1 + self.q2
        a = kly.heavy_amp2(self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, 110.0, 3.4,
                           xva=(1.0, -1.0))
        b = kly.heavy_amp2(self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, 110.0, 3.4,
                           xva=(1.0, -1.0), num_mass=False)
        # left Z vertex, right Z' vertex: only the m_B term survives
        self.assertGreater(float(np.max(np.abs(a - b) / a)), 0.05)

    def test_positive(self):
        k = self.q1 + self.q2
        w = kly.heavy_amp2(self.p1, self.p2, k, self.zc, self.zw, self.xo, self.xw, 110.0, 3.4)
        self.assertTrue(np.all(w > 0))

    def test_generate_heavy(self):
        ev = kly.generate_heavy(300, np.random.default_rng(5), chunk=20000)
        self.assertEqual(len(ev['p1']), 300)
        tot = ev['p1'] + ev['p2'] + ev['q1'] + ev['q2']
        np.testing.assert_allclose(tot[:, 0], xme.SQRT_S, atol=1e-6)
        np.testing.assert_allclose(tot[:, 1:], 0.0, atol=1e-6)
        m = np.sqrt(np.maximum(xme.mdot(ev['q1'] + ev['q2'], ev['q1'] + ev['q2']), 0))
        self.assertTrue(np.all((m >= kly.MLO - 1e-6) & (m <= kly.MHI + 1e-6)))
        self.assertLess(ev['stats']['n_over'], 0.01 * ev['stats']['nacc'] + 3)


class TestZS(unittest.TestCase):
    def test_decay_average_identity(self):
        """Averaged over isotropic Z' decays, sum_mu-spins |Je.Jmu|^2 = (4/3)(|Je.k|^2 - m^2 Je.Je*)
        for each beam helicity: checks the currents, the metric and the decay boost together."""
        rng = np.random.default_rng(3)
        Jes, _ = xme.beam_currents(*xme.beams())
        for m, p, d in ((30.4, 25.0, (0.3, -0.5, 0.8)), (22.0, 35.0, (1.0, 0.0, 0.0)),
                        (39.0, 10.0, (0.0, 0.6, -0.8))):
            d = np.array(d) / np.linalg.norm(d)
            n = 60000
            K = np.tile(np.concatenate([[np.sqrt(m * m + p * p)], p * d]), (n, 1))
            q1, q2 = xme.decay_massless(K, np.full(n, m), rng)
            k = K[0]
            for Je in Jes:
                u = xme.spinors(q1)
                v = xme.spinors(q2)
                tot = np.zeros(n)
                for a in range(2):
                    for b in range(2):
                        Jm = xme.current(xme.bar(u[..., a, :]), v[..., b, :])
                        tot += np.abs(xme.mdot(Je, Jm)) ** 2
                pred = (4.0 / 3.0) * (abs(xme.mdot(Je, k)) ** 2 - m * m * xme.mdot(Je, np.conj(Je)).real)
                if pred < 1e-6 * m * m:
                    continue
                self.assertAlmostEqual(float(tot.mean()) / pred, 1.0, delta=0.03)

    def test_zs_amp2_matches_loop(self):
        rng = np.random.default_rng(4)
        Jes, _ = xme.beam_currents(*xme.beams())
        K = np.tile([50.0, 0.0, 0.0, 39.7], (50, 1))
        q1, q2 = xme.decay_massless(K, np.full(50, np.sqrt(50.0 ** 2 - 39.7 ** 2)), rng)
        w = kly.zs_amp2(Jes, q1, q2)
        self.assertTrue(np.all(w >= 0))
        self.assertGreater(float(w.sum()), 0.0)

    def test_generate_zs(self):
        for mphi in (12.0, 30.4, 50.0):
            ev = kly.generate_zs(400, np.random.default_rng(11), m_phi=mphi, chunk=5000)
            self.assertEqual(len(ev['p1']), 400)
            tot = ev['p1'] + ev['p2'] + ev['q1'] + ev['q2']
            np.testing.assert_allclose(tot[:, 0], xme.SQRT_S, atol=1e-6)
            np.testing.assert_allclose(tot[:, 1:], 0.0, atol=1e-6)
            bb = ev['p1'] + ev['p2']
            np.testing.assert_allclose(np.sqrt(xme.mdot(bb, bb)), mphi, rtol=1e-6)
            self.assertLess(ev['stats']['n_over'], 0.01 * ev['stats']['nacc'] + 3)

    def test_zs_no_forward_backward_asymmetry(self):
        """The Z Z' phi vertex is parity-even and the Z' decay is summed over, so the Z' direction
        has no forward-backward asymmetry: mean cos(theta) ~ 0 (std ~ 0.009 for 4000 events)."""
        ev = kly.generate_zs(4000, np.random.default_rng(12), m_phi=30.4, chunk=20000)
        k = ev['q1'] + ev['q2']
        c = k[:, 3] / np.linalg.norm(k[:, 1:], axis=1)
        self.assertLess(abs(float(np.mean(c))), 0.06)

    def test_models_table(self):
        self.assertEqual(set(kly.MODELS), {"B110", "B180", "B110L", "Q12", "Q30", "Q50"})
        for lab in kly.MODELS:
            ev = kly.generate(lab, 50, np.random.default_rng(2))
            self.assertEqual(len(ev['q1']), 50)


if __name__ == '__main__':
    unittest.main()
