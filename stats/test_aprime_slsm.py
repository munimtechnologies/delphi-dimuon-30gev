# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for aprime_slsm 0.1.0 on made-up spectra only (no ALEPH numbers)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aprime_slsm as sl  # noqa: E402

try:
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    HAVE_NP = True
except ImportError:
    HAVE_NP = False

EDGES = [15.0 + i for i in range(36)]


class TestPure(unittest.TestCase):
    def test_signed(self):
        self.assertAlmostEqual(sl.signed(4.0, 0.02), 2.0)
        self.assertAlmostEqual(sl.signed(4.0, -0.02), -2.0)
        self.assertEqual(sl.signed(-1e-9, 0.02), 0.0)

    def test_interval(self):
        bs = [0.01 * k for k in range(11)]
        ls = [-0.5 * ((b - 0.05) / 0.02) ** 2 for b in bs]
        lo, hi = sl.interval(bs, ls, 0.0)
        self.assertAlmostEqual(lo, 0.03, delta=0.002)
        self.assertAlmostEqual(hi, 0.07, delta=0.002)
        lo, hi = sl.interval(bs, [0.0] * 11, 0.0)
        self.assertIsNone(lo)

    def test_z_from_count(self):
        z = sl.z_from_count(228, 10000)
        self.assertAlmostEqual(z["Z"], 2.0, delta=0.01)
        self.assertTrue(sl.z_from_count(0, 1000)["lower_bound"])

    def test_grade_gate(self):
        obs = {"closure_b0": 3.0, "closure_parfit": 3.134, "slope_mu0": {"b_hat": 0.03, "Z": 2.5}}
        g = sl.grade(obs, {}, {}, 0.5)
        self.assertEqual(g["L0"], "FAIL")
        self.assertTrue(g["L1"].startswith("NOT GRADABLE"))

    def test_grade(self):
        obs = {"closure_b0": sl.PAR3_OBS, "closure_parfit": sl.PAR3_OBS,
               "slope_mu0": {"b_hat": 0.03, "Z": 2.5}}
        cal = {"slope": {"Z": 1.8, "lower_bound": False}}
        rates = {"slope": {"p_ge2": 0.02}}
        g = sl.grade(obs, cal, rates, 0.3)
        self.assertEqual([g[k] for k in ("L0", "L1", "L2", "L3", "L4", "L5")],
                         ["PASS"] * 6)


@unittest.skipUnless(HAVE_NP and sl.asm is not None, "needs numpy, scipy and aprime_smooth")
class TestFit(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np
        xc = [0.5 * (EDGES[i] + EDGES[i + 1]) for i in range(35)]
        self.xc = np.array(xc)
        self.s = [32.0 * math.exp(-0.5 * ((x - 30.4) / 1.2) ** 2) / (1.2 * math.sqrt(2 * math.pi))
                  for x in xc]
        self.T = np.array([60.0 * math.exp(-(x - 15.0) / 7.0) for x in xc])
        self.sf = sl.SlopeFit(EDGES, self.s)

    def test_gradient(self):
        np = self.np
        n = 0.6 * self.T + 1.0
        m = self.T + 0.5
        d = self.sf.d
        p = np.concatenate([[3.0, -1.5, -0.3, 0.05][:d], [math.log(0.6), 0.02, 0.4]])
        f, g = self.sf.nll_grad(p, n, m)
        for k in range(len(p)):
            e = np.zeros(len(p))
            e[k] = 1e-5
            num = (self.sf.nll_grad(p + e, n, m)[0] - self.sf.nll_grad(p - e, n, m)[0]) / 2e-5
            self.assertAlmostEqual(num, g[k], delta=1e-3 * max(1.0, abs(g[k])))

    def test_b0_matches_parfit(self):
        n = [round(0.6 * t) for t in self.T]
        m = [round(t) for t in self.T]
        a = self.sf.fit(n, m, mu_fixed=0.0, b_fixed=0.0)
        b = self.sf.base.fit(n, m, mu_fixed=0.0)
        self.assertAlmostEqual(a["lnL"], b["lnL"], delta=1e-3)
        self.assertGreaterEqual(a["lnL"], b["lnL"] - 1e-3)

    def test_recovers_slope_on_asimov(self):
        np = self.np
        b_true = 0.03
        n = 0.6 * np.exp(b_true * (self.xc - sl.PIVOT)) * self.T * 20.0
        m = self.T * 20.0
        f = self.sf.fit(n, m, mu_fixed=0.0)
        self.assertAlmostEqual(f["b"], b_true, delta=0.003)
        d = self.sf.discovery(n, m)
        self.assertLess(d["Z0"], 0.5)


if __name__ == "__main__":
    unittest.main()
