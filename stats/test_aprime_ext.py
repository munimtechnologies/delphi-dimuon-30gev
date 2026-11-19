# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for aprime_ext 0.1.0 on made-up inputs only (no real data).
Needs emuframe.py (stats/emuframe.py 0.1.0) next to this file; skipped otherwise."""
import math
import os
import random
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aprime_ext as ae  # noqa: E402

try:
    import emuframe as _ef  # noqa: E402
    ae.bind(module=_ef)
except ImportError:          # pragma: no cover
    _ef = None


def need_ef(tc):
    if _ef is None:
        tc.skipTest("emuframe.py not available")


class TestLikelihoodPieces(unittest.TestCase):
    def setUp(self):
        need_ef(self)

    def test_constant_ratio_matches_emuframe(self):
        rng = random.Random(7)
        n = [rng.randint(0, 40) for _ in range(20)]
        m = [rng.randint(1, 60) for _ in range(20)]
        s = [rng.random() * 3 for _ in range(20)]
        for r, mu in ((0.5, 0.0), (0.7, 1.3), (1.2, 3.0)):
            self.assertAlmostEqual(ae.lnl_r(n, m, s, [r] * 20, mu, "bb"),
                                   _ef.lnl_bb(n, m, s, r, mu), delta=1e-9)
            self.assertAlmostEqual(ae.lnl_r(n, m, s, [r] * 20, mu, "exact"),
                                   _ef.lnl_exact(n, m, s, r, mu), delta=1e-9)

    def test_signal_template_matches_emuframe_on_15_50(self):
        edges = [15.0 + i for i in range(36)]
        s = ae.s_template(edges, n_theta=400)
        p = _ef.voigt_bin_probs(edges, n_theta=400)
        for a, b in zip(s, p):
            self.assertAlmostEqual(a, _ef.N_ALEPH * b, delta=1e-12)
        self.assertAlmostEqual(sum(s), _ef.N_ALEPH, delta=1e-9)

    def test_signal_tail_below_15_is_small_and_positive(self):
        edges = [5.0 + i for i in range(46)]
        s = ae.s_template(edges, n_theta=400)
        low = sum(s[:10])
        self.assertGreater(low, 0.0)
        self.assertLess(low, 0.05 * _ef.N_ALEPH)
        self.assertAlmostEqual(sum(s[10:]), _ef.N_ALEPH, delta=1e-9)

    def test_combine_readings(self):
        low = {"edges": [5, 6, 7], "n": [1, 2], "v_scaled": [0.5, 1.5]}
        hi = {"edges": [7, 8, 9], "n": [3, 4], "v_scaled": [2.5, 3.5]}
        e, n, v = ae.combine_readings(low, hi)
        self.assertEqual(e, [5, 6, 7, 8, 9])
        self.assertEqual(n, [1, 2, 3, 4])
        self.assertEqual(v, [0.5, 1.5, 2.5, 3.5])
        with self.assertRaises(ValueError):
            ae.combine_readings({"edges": [5, 6], "n": [1], "v_scaled": [1.0]}, hi)


class TestFits(unittest.TestCase):
    def setUp(self):
        need_ef(self)

    def asimov(self, b_true, r_true=0.5, mu_true=0.0):
        edges = [15.0 + i for i in range(36)]
        xc = ae.centres(edges)
        t = [2000.0 * math.exp(-(x - 15.0) / 10.0) for x in xc]
        s = [200.0 * math.exp(-0.5 * ((x - 30.5) / 1.0) ** 2) for x in xc]
        n = [r_true * math.exp(b_true * (x - ae.PIVOT)) * ti + mu_true * si
             for x, ti, si in zip(xc, t, s)]
        return edges, xc, n, t, s

    def test_slope_recovered_at_mu0(self):
        for b_true in (0.0, 0.02, -0.015):
            edges, xc, n, m, s = self.asimov(b_true)
            for model in ("bb", "exact"):
                p = ae.prof_slope(n, m, s, 0.0, model, xc)
                self.assertAlmostEqual(p["b"], b_true, delta=1e-4, msg=(model, b_true))
                self.assertAlmostEqual(p["r"], 0.5, delta=1e-3, msg=(model, b_true))

    def test_const_profile_matches_emuframe(self):
        edges, xc, n, m, s = self.asimov(0.0, mu_true=1.0)
        for model in ("bb", "exact"):
            for mu in (0.0, 1.0):
                a = ae.prof_const(n, m, s, mu, model)
                r, v = _ef.profile_r(n, m, s, mu, model)
                self.assertAlmostEqual(a["lnL"], v, delta=1e-6)
                self.assertAlmostEqual(a["r"], r, delta=1e-5)

    def test_signal_recovered_with_slope(self):
        edges, xc, n, m, s = self.asimov(0.02, mu_true=1.0)
        d = ae.discovery(n, m, s, "exact", "slope", xc)
        self.assertAlmostEqual(d["mu_hat"], 1.0, delta=5e-3)
        self.assertAlmostEqual(d["b_hat"], 0.02, delta=5e-4)
        self.assertGreater(d["Z0"], 3.0)

    def test_slope_z_zero_without_slope(self):
        edges, xc, n, m, s = self.asimov(0.0)
        c = ae.discovery(n, m, s, "exact", "const", xc)
        sl = ae.discovery(n, m, s, "exact", "slope", xc)
        self.assertLess(abs(ae.slope_z(c, sl)), 0.05)
        self.assertLess(sl["Z0"], 0.05)

    def test_split_recovers_two_ratios(self):
        edges = [5.0 + i for i in range(46)]
        m = [100.0] * 45
        n = [40.0] * 10 + [60.0] * 35
        s = [0.0] * 45
        sp = ae.split_test(edges, n, m, s)
        self.assertAlmostEqual(sp["r_lo"], 0.4, delta=1e-5)
        self.assertAlmostEqual(sp["r_hi"], 0.6, delta=1e-5)
        self.assertGreater(sp["Z_split"], 3.0)
        same = ae.split_test(edges, [50.0] * 45, m, s)
        self.assertLess(same["Z_split"], 1e-3)


class TestGrades(unittest.TestCase):
    def test_closure_gate(self):
        def blk(zc_bb, zc_ex, zs_bb, zsl):
            return {"bb": {"const": {"Z0": zc_bb}, "slope": {"Z0": zs_bb}},
                    "exact": {"const": {"Z0": zc_ex}, "slope": {"Z0": 1.0}}, "Z_slope_bb": zsl}
        good = {"15-50": blk(2.6641, 4.1783, 2.1, 1.5), "5-50": blk(1, 1, 3.4, 0)}
        g = ae.grade(good)
        self.assertEqual((g["X0"], g["X1"], g["X2"], g["X3"]), ("PASS", "PASS", "PASS", "FAIL"))
        bad = {"15-50": blk(2.70, 4.1783, 2.1, 1.5)}
        g = ae.grade(bad)
        self.assertEqual(g["X0"], "FAIL")
        self.assertTrue(g["X1"].startswith("NOT GRADABLE"))


if __name__ == "__main__":
    unittest.main()
