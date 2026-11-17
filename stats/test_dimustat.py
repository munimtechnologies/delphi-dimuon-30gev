"""Tests for dimustat (run first in every job). MV2 of Munim, Inc.; made with AI agents. Apache-2.0."""
import math
import unittest

import numpy as np

import dimustat as ds
import bbshape


def truth(a, nb):
    return nb * ds.bkg_probs(np.array(a, float), ds.legendre_basis(len(a)))


class TestShapes(unittest.TestCase):
    def test_signal_template(self):
        s = ds.signal_template()
        self.assertAlmostEqual(s.sum(), 1.0, places=12)
        self.assertLess(abs(ds.CENT[np.argmax(s)] - 30.40), 0.06)
        # Voigt FWHM (Olivero-Longbothum) for Gamma 1.78, sigma 0.745: about 2.6 GeV
        half = s.max() / 2
        above = ds.CENT[s >= half]
        fwhm = above.max() - above.min()
        fg = 2.3548 * math.sqrt(6e-4) * 30.40
        fl = 1.78
        fv = 0.5346 * fl + math.sqrt(0.2166 * fl ** 2 + fg ** 2)
        self.assertLess(abs(fwhm - fv), 0.15)

    def test_gaussian_limit(self):
        s = ds.signal_template(30.0, 0.0, 0.5)
        m = float((ds.CENT * s).sum())
        v = float(((ds.CENT - m) ** 2 * s).sum())
        self.assertLess(abs(m - 30.0), 1e-3)
        self.assertLess(abs(math.sqrt(v) - 0.5), 0.01)

    def test_kde(self):
        rng = np.random.default_rng(1)
        x = rng.uniform(10, 60, 5000)
        p, bw = bbshape.kde_probs(x, ds.CENT)
        self.assertAlmostEqual(p.sum(), 1.0, places=10)
        # uniform input -> nearly flat density (reflection removes edge loss)
        self.assertLess(p.max() / p.min(), 1.3)


class TestFit(unittest.TestCase):
    def test_gradient(self):
        md = ds.Model(3)
        rng = np.random.default_rng(2)
        nu = truth([-1.2, 0.3, -0.1], 1500) + 30 * md.sig
        n = rng.poisson(nu).astype(float)
        th = np.array([25.0, 1480.0, -1.1, 0.25, -0.05])
        v, g = md.nll_grad(th, n)
        for i in range(len(th)):
            h = 1e-5 * max(1.0, abs(th[i]))
            tp, tm = th.copy(), th.copy()
            tp[i] += h
            tm[i] -= h
            num = (md.nll_grad(tp, n)[0] - md.nll_grad(tm, n)[0]) / (2 * h)
            self.assertLess(abs(num - g[i]), 1e-3 * max(1.0, abs(g[i])), msg='param %d' % i)

    def test_recover_asimov(self):
        md = ds.Model(2)
        nu_b = truth([-1.5, 0.2], 1400)
        nll, th = ds.fit(md, nu_b + 30 * md.sig)
        self.assertLess(abs(th[0] - 30.0), 0.3)
        self.assertLess(abs(th[1] - 1400.0), 1.0)
        self.assertLess(abs(th[2] + 1.5), 0.01)

    def test_q0_scaling(self):
        md = ds.Model(2)
        nu_b = truth([-1.5, 0.2], 1400)
        q1 = ds.q0(md, nu_b + 20 * md.sig)[0]
        q2 = ds.q0(md, nu_b + 40 * md.sig)[0]
        self.assertGreater(q1, 0.3)
        self.assertLess(abs(q2 / q1 - 4.0), 0.4)
        self.assertEqual(ds.q0(md, nu_b - 10 * md.sig)[0], 0.0)

    def test_median_cls_limit(self):
        # On the background-only Asimov set the CLs median limit is sigma * Phi^-1(1 - 0.05/2)
        md = ds.Model(2)
        nu_b = truth([-1.5, 0.2], 1400)
        f, _ = ds.make_sigma_fn(md, nu_b, [10, 20, 30, 40, 60, 90])
        bonly, free = ds.fits_free_and_bonly(md, nu_b)
        ul = ds.upper_limit(md, nu_b, f, free, bonly)
        self.assertLess(abs(ul / (1.95996 * f(ul)) - 1.0), 0.03)

    def test_cls_values(self):
        self.assertAlmostEqual(ds.cls_asymptotic(0.0, 1.0, 0.5), 0.5 / 0.9772498680518208, places=6)
        self.assertLess(ds.cls_asymptotic(9.0, 1.0, 0.5), 0.05)

    def test_choose_degree(self):
        nu1 = truth([-2.0], 3000)
        d, _ = ds.choose_degree(nu1)
        self.assertEqual(d, 1)
        nu3 = truth([-2.0, 0.6, -0.4], 200000)
        d, _ = ds.choose_degree(nu3)
        self.assertGreaterEqual(d, 3)

    def test_mass_scan_peaks(self):
        md = ds.Model(2)
        nu = truth([-1.5, 0.2], 1400) + 80 * md.sig
        masses = np.arange(24.0, 37.01, 1.0)
        z = ds.mass_scan(nu, 2, masses, 1.78, math.sqrt(6e-4))
        self.assertLess(abs(masses[int(np.argmax(z))] - 30.0), 1.01)
        self.assertGreater(z.max(), 1.5)


if __name__ == '__main__':
    unittest.main()
