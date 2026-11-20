# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for ssframe 0.1.0 on made-up inputs only (no ALEPH numbers)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import ssframe as sf
except ImportError:  # pragma: no cover
    sf = None

try:
    import numpy  # noqa: F401
    import scipy  # noqa: F401
    HAVE_NP = True
except ImportError:  # pragma: no cover
    HAVE_NP = False


def obs_ok(**kw):
    o = {"control": {"dmc_closure_ok": True, "window_hi": 38.0, "window_ok": True,
                     "b_ctrl": 0.04, "sigma_ctrl": 0.03},
         "closure_b0": 3.1339963632770744, "closure_free": 2.2953, "closure_loose": 2.2950,
         "constrained": {"Z0": 2.2}, "dev0": 30.0}
    o.update(kw)
    return o


def rows(n, z=1.0, dev=35.0):
    return [{"idx": i, "Z0": z, "dev0": dev, "mu": 0.1, "b0": 0.0, "b_aux": 0.0}
            for i in range(n)]


@unittest.skipUnless(sf is not None, "ssframe not next to this file")
class TestPure(unittest.TestCase):
    def test_prefix(self):
        r = [{"idx": i} for i in (0, 1, 2, 4, 5)]
        self.assertEqual([x["idx"] for x in sf.prefix(r)], [0, 1, 2])
        self.assertEqual(sf.prefix([{"idx": 3}]), [])

    def test_clamp(self):
        self.assertEqual(sf.clamp(0.5), 0.2)
        self.assertEqual(sf.clamp(-0.5), -0.2)
        self.assertEqual(sf.clamp(0.01), 0.01)

    def test_z_from_count(self):
        z = sf.z_from_count(10, 1000)
        self.assertAlmostEqual(z["Z"], 2.326, places=2)
        self.assertFalse(z["lower_bound"])
        z0 = sf.z_from_count(0, 1000)
        self.assertTrue(z0["lower_bound"])
        self.assertAlmostEqual(z0["Z"], 2.748, places=2)

    def test_gate_pass(self):
        self.assertEqual(sf.gate(obs_ok())[0], "PASS")

    def test_gate_fails(self):
        bad = [{"closure_b0": 3.0}, {"closure_free": 2.4}, {"closure_loose": 2.31},
               {"control": dict(obs_ok()["control"], window_hi=39.0)},
               {"control": dict(obs_ok()["control"], dmc_closure_ok=False)},
               {"control": dict(obs_ok()["control"], sigma_ctrl=None)},
               {"control": dict(obs_ok()["control"], window_ok=False)}]
        for kw in bad:
            g, st = sf.grade(obs_ok(**kw), rows(2000))
            self.assertTrue(g["P0"].startswith("FAIL"), kw)
            self.assertIsNone(st)
            for k in sf.TESTS:
                self.assertTrue(g[k].startswith("NOT GRADABLE (P0"), (kw, k))

    def test_too_few_toys(self):
        g, st = sf.grade(obs_ok(), rows(999))
        self.assertEqual(g["P0"], "PASS")
        self.assertIsNone(st)
        for k in sf.TESTS:
            self.assertTrue(g[k].startswith("NOT GRADABLE (only 999"), k)

    def test_grades(self):
        r = rows(2000)
        for i in range(20):              # 20 toys at or above the observed 2.2
            r[i]["Z0"] = 2.5
        for i in range(30):              # 50 toys >= 2 in all: p_ge2 = 0.025
            r[100 + i]["Z0"] = 2.05
        g, st = sf.grade(obs_ok(), r)
        self.assertEqual(st["calibrated"]["k"], 20)
        self.assertAlmostEqual(st["p_ge2"], 0.025)
        self.assertEqual(g["P1"], "PASS")      # p 0.01 -> Z 2.33
        self.assertEqual(g["P2"], "FAIL")
        self.assertEqual(g["P3"], "PASS")      # every toy deviance >= observed
        self.assertEqual(g["P4"], "PASS")
        r2 = rows(2000, dev=10.0)              # no toy deviance reaches the observed 30
        r2[0]["Z0"] = 2.3
        g2, st2 = sf.grade(obs_ok(), r2)
        self.assertEqual(g2["P3"], "FAIL")
        self.assertEqual(g2["P4"], "FAIL")      # p_ge2 = 1 / 2000
        # k = 1 of 2000 -> p 0.0005 -> Z 3.29 >= 3, so P1 and P2 FAIL
        self.assertEqual(st2["calibrated"]["k"], 1)
        self.assertAlmostEqual(st2["calibrated"]["Z"], 3.29, places=2)
        self.assertEqual(g2["P1"], "FAIL")
        self.assertEqual(g2["P2"], "FAIL")

    def test_lower_bound(self):
        r = rows(1000)
        g, st = sf.grade(obs_ok(constrained={"Z0": 4.0}), r)
        self.assertTrue(st["calibrated"]["lower_bound"])
        self.assertTrue(g["P1"].startswith("UNDETERMINED"))   # bound 2.75 < 3
        self.assertEqual(g["P2"], "FAIL")                    # bound 2.75 >= 2


@unittest.skipUnless(sf is not None and sf.sl is not None and sf.sl.asm is not None and HAVE_NP,
                     "needs numpy, scipy and aprime_slsm / aprime_smooth next to this file")
class TestConstrainedFit(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np
        self.edges = [15.0 + i for i in range(36)]
        xc = [0.5 * (self.edges[i] + self.edges[i + 1]) for i in range(35)]
        self.s = [8.0 * math.exp(-0.5 * ((x - 30.4) / 1.2) ** 2) for x in xc]
        self.T = [60.0 * math.exp(-(x - 15.0) / 7.0) + 0.3 for x in xc]
        self.m = [round(t) for t in self.T]
        self.n = [round(0.6 * t * math.exp(0.03 * (x - 30.4)) + 0.7 * si)
                  for t, x, si in zip(self.T, xc, self.s)]
        self.CSF = sf.make_fit_class()

    def test_gradient(self):
        np = self.np
        c = self.CSF(self.edges, self.s, 0.02, 0.015)
        p = np.array([2.0, -1.5, 0.3, -0.1, math.log(0.6), 0.035, 0.7])
        n, m = np.array(self.n, float), np.array(self.m, float)
        f, g = c.nll_grad(p, n, m)
        for k in range(len(p)):
            h = 1e-6
            dp = np.zeros(len(p))
            dp[k] = h
            num = (c.nll_grad(p + dp, n, m)[0] - c.nll_grad(p - dp, n, m)[0]) / (2 * h)
            self.assertAlmostEqual(num, g[k], delta=1e-4 * max(1.0, abs(num)), msg=str(k))
        base = sf.sl.SlopeFit(self.edges, self.s)
        f0, _ = base.nll_grad(p, n, m)
        self.assertAlmostEqual(f - f0, 0.5 * ((0.035 - 0.02) / 0.015) ** 2, places=9)

    def test_limits(self):
        base = sf.sl.SlopeFit(self.edges, self.s)
        free = base.discovery(self.n, self.m)
        fixed0 = base.discovery(self.n, self.m, b_fixed=0.0)
        loose = self.CSF(self.edges, self.s, 0.0, 10.0).discovery(self.n, self.m)
        tight = self.CSF(self.edges, self.s, 0.0, 1e-4).discovery(self.n, self.m)
        self.assertAlmostEqual(loose["Z0"], free["Z0"], delta=0.01)
        self.assertAlmostEqual(tight["Z0"], fixed0["Z0"], delta=0.02)
        self.assertLess(abs(tight["b_hat"]), 1e-3)

    def test_set_constraint(self):
        c = self.CSF(self.edges, self.s, 0.0, 0.02)
        c.set_constraint(0.05, 0.01)
        self.assertEqual((c.bc, c.sc), (0.05, 0.01))
        with self.assertRaises(ValueError):
            c.set_constraint(0.0, 0.0)


if __name__ == "__main__":
    unittest.main()
