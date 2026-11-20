# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for aprime_smooth (made-up inputs only, no ALEPH numbers)."""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import numpy as np  # noqa: F401
    import scipy.optimize  # noqa: F401
    HAVE_DEPS = True
except Exception:   # numpy / scipy absent: skip
    HAVE_DEPS = False

HAVE_EMU = os.path.exists(os.path.join(HERE, "emuframe.py"))

if HAVE_EMU:
    import aprime_smooth as aps
    aps.bind()

EDGES = [15.0 + i for i in range(36)]


def made_up_T(scale=600.0, decay=7.0):
    c = [0.5 * (EDGES[i] + EDGES[i + 1]) for i in range(35)]
    w = [math.exp(-(ci - 15.0) / decay) for ci in c]
    tot = sum(w)
    return [scale * wi / tot for wi in w]


@unittest.skipUnless(HAVE_EMU, "emuframe.py not next to the module")
class TestPure(unittest.TestCase):
    def test_smooth_keeps_total(self):
        m = [0, 3, 10, 0, 7] + [1] * 30
        out = aps.smooth(m, EDGES, 1.0)
        self.assertAlmostEqual(sum(out), sum(m), places=9)
        self.assertTrue(all(x >= 0 for x in out))

    def test_smooth_flat_stays_flat_in_middle(self):
        out = aps.smooth([5.0] * 35, EDGES, 1.0)
        self.assertAlmostEqual(out[17], 5.0, places=6)

    def test_floor(self):
        self.assertEqual(aps.floor([0.0, 0.2, 3.0]), [0.5, 0.5, 3.0])

    def test_z_from_count(self):
        z = aps.z_from_count(228, 10000)
        self.assertAlmostEqual(z["Z"], 2.0, delta=0.01)
        self.assertFalse(z["lower_bound"])
        z0 = aps.z_from_count(0, 10000)
        self.assertTrue(z0["lower_bound"])
        self.assertAlmostEqual(z0["Z"], aps.ef.z_from_p(3e-4), places=9)

    def test_grade_rules(self):
        obs = {"closure_bb": aps.CLOSURE["bb"], "closure_exact": aps.CLOSURE["exact"]}
        rates = {k: {"p_ge2": 0.02} for k in aps.METHODS}
        cal = {k: {"Z": 2.5, "lower_bound": False} for k in aps.METHODS}
        g = aps.grade(obs, cal, rates, 0.3)
        self.assertEqual([g[k] for k in ("K0", "K1", "K2", "K3", "K4")], ["PASS"] * 5)
        cal["par3"] = {"Z": 3.4, "lower_bound": True}
        g = aps.grade(obs, cal, rates, 0.005)
        self.assertEqual(g["K1"], "FAIL")
        self.assertEqual(g["K3"], "FAIL")
        self.assertEqual(g["K4"], "FAIL")
        cal["par3"] = {"Z": 2.9, "lower_bound": True}
        self.assertTrue(aps.grade(obs, cal, rates, 0.3)["K1"].startswith("UNDETERMINED"))
        bad = dict(obs, closure_bb=2.70)
        self.assertEqual(aps.grade(bad, cal, rates, 0.3)["K1"], "NOT GRADABLE (K0 failed)")


@unittest.skipUnless(HAVE_EMU and HAVE_DEPS, "needs emuframe.py, numpy and scipy")
class TestParFit(unittest.TestCase):
    def setUp(self):
        self.s = [32.0 * p for p in aps.ef.voigt_bin_probs(EDGES)]
        self.T = made_up_T()
        self.pf = aps.ParFit(EDGES, self.s, 3)

    def test_gradient(self):
        n = np.array([max(0, round(0.6 * t)) for t in self.T], dtype=float)
        m = np.array([round(t) for t in self.T], dtype=float)
        p = np.array([1.0, -1.2, 0.1, 0.05, math.log(0.6), 0.7])
        f0, g = self.pf.nll_grad(p, n, m)
        for k in range(len(p)):
            e = np.zeros_like(p)
            e[k] = 1e-6
            num = (self.pf.nll_grad(p + e, n, m)[0] - self.pf.nll_grad(p - e, n, m)[0]) / 2e-6
            self.assertAlmostEqual(num, g[k], delta=1e-4 * max(1.0, abs(num)))

    def test_asimov_signal_recovered(self):
        r = 0.6
        n = [r * t + si for t, si in zip(self.T, self.s)]
        best = self.pf.fit(n, self.T)
        self.assertAlmostEqual(best["mu"], 1.0, delta=0.02)
        self.assertAlmostEqual(best["r"], r, delta=0.01)

    def test_asimov_background_only(self):
        r = 0.6
        n = [r * t for t in self.T]
        d = self.pf.discovery(n, self.T)
        self.assertLess(d["Z0"], 1e-3)
        self.assertLess(d["mu_hat"], 1e-3)
        self.assertLess(self.pf.deviance(n, self.T, d["mu0"]), 1e-4)

    def test_signal_gives_significance(self):
        r = 0.6
        n = [r * t + 1.5 * si for t, si in zip(self.T, self.s)]
        d = self.pf.discovery(n, self.T)
        self.assertGreater(d["Z0"], 2.0)


@unittest.skipUnless(HAVE_EMU and HAVE_DEPS, "needs emuframe.py, numpy and scipy")
class TestToyDriver(unittest.TestCase):
    def test_small_toy_run(self):
        T = made_up_T()
        s = [32.0 * p for p in aps.ef.voigt_bin_probs(EDGES)]
        aps._init(None, EDGES, s, T, 0.6)
        row = aps.one_toy(1)
        for k in aps.METHODS:
            self.assertTrue(row[k] >= 0.0 and math.isfinite(row[k]), k)
        self.assertTrue(math.isfinite(row["dev0"]))


if __name__ == "__main__":
    unittest.main()
