"""Tests for dimucomb (run first in every job). MV2 of Munim, Inc.; made with AI agents. Apache-2.0."""
import math
import unittest

import numpy as np

import dimustat as ds
import dimucomb as dc


def truth(a, nb):
    return nb * ds.bkg_probs(np.array(a, float), ds.legendre_basis(len(a)))


class TestRule(unittest.TestCase):
    def test_nexp_untagged(self):
        # (1 - 0.38) / 0.38 = 1.631578...
        self.assertAlmostEqual(dc.nexp_untagged(1.0, 0.38), 0.62 / 0.38, places=12)
        self.assertAlmostEqual(dc.nexp_untagged(21.7, 0.38), 21.7 * 0.62 / 0.38, places=9)
        # rho below 1 is replaced by 1 (conservative); above 1 it is used
        self.assertAlmostEqual(dc.nexp_untagged(10.0, 0.38, 0.8), 10.0 * 0.62 / 0.38, places=9)
        self.assertAlmostEqual(dc.nexp_untagged(10.0, 0.38, 1.1), 10.0 * (1 - 0.418) / 0.418,
                               places=9)
        self.assertEqual(dc.nexp_untagged(10.0, 0.6, 2.0), 0.0)
        with self.assertRaises(ValueError):
            dc.nexp_untagged(1.0, 0.0)


class TestJoint(unittest.TestCase):
    def test_single_category_equals_dimustat(self):
        md = ds.Model(2)
        J = dc.Joint([30.0], [2])
        rng = np.random.default_rng(3)
        n = rng.poisson(truth([-1.5, 0.2], 1400) + 25 * md.sig).astype(float)
        th = np.array([0.8, 1390.0, -1.4, 0.15])
        v1, g1 = J.nll_grad(th, [n])
        v2, g2 = md.nll_grad(np.array([24.0, 1390.0, -1.4, 0.15]), n)
        self.assertAlmostEqual(v1, v2, places=9)
        self.assertAlmostEqual(g1[0], 30.0 * g2[0], places=7)
        np.testing.assert_allclose(g1[1:], g2[1:], rtol=1e-10, atol=1e-10)
        # Asimov sigma: sigma(mu) * N equals dimustat's sigma(n_s)
        nu_b = truth([-1.5, 0.2], 1400)
        s_mu = dc.asimov_sigma(J, [nu_b], 1.0)
        s_ns = ds.asimov_sigma(md, nu_b, 30.0)
        self.assertLess(abs(30.0 * s_mu / s_ns - 1.0), 0.01)

    def test_gradient(self):
        J = dc.Joint([20.0, 35.0], [2, 3])
        rng = np.random.default_rng(4)
        s = J.models[0].sig
        ns = [rng.poisson(truth([-1.5, 0.2], 1000) + 20 * s).astype(float),
              rng.poisson(truth([-1.2, 0.1, -0.05], 2000) + 35 * s).astype(float)]
        th = np.array([0.9, 990.0, -1.45, 0.18, 2010.0, -1.15, 0.12, -0.04])
        v, g = J.nll_grad(th, ns)
        for i in range(len(th)):
            h = 1e-5 * max(1.0, abs(th[i]))
            tp, tm = th.copy(), th.copy()
            tp[i] += h
            tm[i] -= h
            num = (J.nll_grad(tp, ns)[0] - J.nll_grad(tm, ns)[0]) / (2 * h)
            self.assertLess(abs(num - g[i]), 1e-3 * max(1.0, abs(g[i])), msg='param %d' % i)

    def test_recover_asimov(self):
        J = dc.Joint([20.0, 35.0], [2, 2])
        s = J.models[0].sig
        nus = [truth([-1.5, 0.2], 1000) + 0.7 * 20 * s, truth([-1.2, 0.1], 2000) + 0.7 * 35 * s]
        nll, th = dc.fit(J, nus)
        self.assertLess(abs(th[0] - 0.7), 0.02)
        self.assertLess(abs(th[1] - 1000.0), 2.0)
        self.assertLess(abs(th[4] - 2000.0), 2.0)

    def test_two_identical_categories(self):
        # independent identical categories: q_A adds, so sigma(mu) drops by sqrt(2)
        nu_b = truth([-1.5, 0.2], 1400)
        s1 = dc.asimov_sigma(dc.Joint([30.0], [2]), [nu_b], 1.0)
        s2 = dc.asimov_sigma(dc.Joint([30.0, 30.0], [2, 2]), [nu_b, nu_b], 1.0)
        self.assertLess(abs(s2 * math.sqrt(2.0) / s1 - 1.0), 0.02)

    def test_category_without_signal_adds_nothing(self):
        nu_b = truth([-1.5, 0.2], 1400)
        s1 = dc.asimov_sigma(dc.Joint([30.0], [2]), [nu_b], 1.0)
        s2 = dc.asimov_sigma(dc.Joint([30.0, 0.0], [2, 2]), [nu_b, truth([-1.0, 0.1], 3000)], 1.0)
        self.assertLess(abs(s2 / s1 - 1.0), 0.01)

    def test_median_limit_and_q0(self):
        J = dc.Joint([20.0, 35.0], [2, 2])
        s = J.models[0].sig
        nus = [truth([-1.5, 0.2], 1000), truth([-1.2, 0.1], 2000)]
        f, _ = dc.make_sigma_fn(J, nus)
        bonly, free = dc.fits_free_and_bonly(J, nus)
        ul = dc.upper_limit(J, nus, f, free, bonly)
        self.assertLess(abs(ul / (1.95996 * f(ul)) - 1.0), 0.03)
        # q0 grows like mu^2 (small s/b: mu = 0.5 vs 1) and is zero for a deficit
        q_a = dc.q0(J, [nus[0] + 10 * s, nus[1] + 17.5 * s])[0]
        q_b = dc.q0(J, [nus[0] + 20 * s, nus[1] + 35 * s])[0]
        self.assertGreater(q_a, 0.3)
        self.assertLess(abs(q_b / q_a - 4.0), 0.4)
        self.assertEqual(dc.q0(J, [nus[0] - 10 * s, nus[1] - 17.5 * s])[0], 0.0)

    def test_analyse_labels(self):
        nus = [truth([-1.5], 1000), truth([-1.2], 2000)]
        s = ds.signal_template()
        r = dc.analyse([nus[0] + 60 * s, nus[1] + 105 * s], [20.0, 35.0])
        self.assertEqual(r['degrees'], [1, 1])
        self.assertGreater(r['muhat'], 2.5)
        self.assertGreater(r['z0'], 2.0)
        r0 = dc.analyse(nus, [20.0, 35.0])
        self.assertLess(abs(r0['muhat']), 0.05)
        self.assertIn(r0['outcome'], ('EXCLUDED', 'INCONCLUSIVE'))


if __name__ == '__main__':
    unittest.main()
