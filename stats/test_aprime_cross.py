# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for aprime_cross 0.1.0 on made-up inputs only (no ALEPH numbers)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aprime_cross as ac  # noqa: E402


def grid(lo, hi, step):
    k = int(round((hi - lo) / step))
    return [lo + step * i for i in range(k + 1)]


def asimov(edges, b_true, r=0.6, scale=200.0, decay=8.0, sig=None):
    xc = ac.centres(edges)
    t = [scale * math.exp(-(x - edges[0]) / decay) for x in xc]
    n = [r * math.exp(b_true * (x - ac.PIVOT)) * ti for x, ti in zip(xc, t)]
    if sig is not None:
        n = [ni + si for ni, si in zip(n, sig)]
    return n, t, xc


class TestPieces(unittest.TestCase):
    def test_t_hat_stationary(self):
        for n, m, s, r, mu in [(10, 20, 3.0, 0.5, 1.0), (0, 5, 2.0, 0.7, 0.5), (7, 0, 1.0, 0.6, 2.0),
                               (12, 30, 0.0, 0.5, 1.0)]:
            t = ac.t_hat(n, m, s, r, mu)
            self.assertGreaterEqual(t, 0.0)
            if t > 0:
                d = n * r / (r * t + mu * s) - r + m / t - 1.0
                self.assertAlmostEqual(d, 0.0, places=7)

    def test_template_sums_in_norm_range(self):
        edges = grid(15.0, 50.0, 1.0)
        s = ac.s_template(edges, n_theta=400)
        self.assertAlmostEqual(sum(s), ac.N_ALEPH, places=9)
        self.assertEqual(max(range(len(s)), key=lambda i: s[i]), 15)   # 30-31 GeV bin

    def test_merge_and_common_edges(self):
        e1 = grid(15.0, 50.0, 0.5)
        e2 = grid(15.0, 50.0, 1.0)
        com = ac.common_edges(e1, e2)
        self.assertEqual(len(com), 36)
        vals = [1.0] * (len(e1) - 1)
        self.assertEqual(ac.merge(e1, vals, com), [2.0] * 35)
        with self.assertRaises(ValueError):
            ac.common_edges(grid(15.5, 49.5, 1.0), e2)
        with self.assertRaises(ValueError):
            ac.merge(e2, [1.0] * 34 + [None], e2)

    def test_fixed_slope_is_kept(self):
        edges = grid(15.0, 39.0, 2.0)
        n, t, xc = asimov(edges, 0.0)
        p = ac.prof(n, t, [0.0] * len(n), 0.0, "bb", xc, 0.05)
        self.assertEqual(p["b"], 0.05)


class TestFits(unittest.TestCase):
    def test_slope_recovered(self):
        edges = grid(15.0, 39.0, 2.0)
        n, t, xc = asimov(edges, 0.03)
        sl = ac.slope_mu0(n, t, xc, "bb", grid=81)
        self.assertAlmostEqual(sl["b_hat"], 0.03, delta=0.003)
        self.assertGreater(sl["Z_slope"], 0.5)
        self.assertIsNotNone(sl["sigma_b"])
        self.assertLess(sl["b_lo"], 0.03)
        self.assertGreater(sl["b_hi"], 0.03)

    def test_no_slope_gives_zero(self):
        edges = grid(15.0, 39.0, 2.0)
        n, t, xc = asimov(edges, 0.0)
        sl = ac.slope_mu0(n, t, xc, "bb", grid=81)
        self.assertLess(abs(sl["b_hat"]), 0.003)
        self.assertLess(abs(sl["Z_slope"]), 0.1)

    def test_signal_recovered_constant_ratio(self):
        edges = grid(15.0, 50.0, 1.0)
        s = ac.s_template(edges, n_sig=30.0, n_theta=400)
        n, t, xc = asimov(edges, 0.0, scale=30.0, sig=s)
        d = ac.discovery(n, t, s, "bb", xc, 0.0)
        self.assertAlmostEqual(d["mu_hat"], 1.0, delta=0.02)
        self.assertGreater(d["Z0"], 1.0)


class TestGrades(unittest.TestCase):
    def made_up_fig5(self):
        edges = grid(15.0, 50.0, 1.0)
        n, t, xc = asimov(edges, 0.0, scale=40.0)
        return {"edges": edges, "n": [round(x) for x in n], "v_scaled": [ti * ac.R0 for ti in t]}

    def test_mc_slope_grades(self):
        edges = grid(15.0, 50.0, 1.0)
        a, t, xc = asimov(edges, 0.03, scale=40.0)
        mc = {"edges": edges, "mumu": a, "emu": [ti * ac.R0 for ti in t]}
        data_slope = {"b_hat": 0.0266, "sigma_b": 0.012}
        res = ac.analyse_mc(mc, self.made_up_fig5(), data_slope)
        self.assertEqual(res["M0"], "PASS")
        self.assertEqual(res["M1"], "PASS")
        self.assertEqual(res["M2"], "PASS")
        self.assertIn(res["M3"], ("PASS", "FAIL"))
        self.assertGreater(res["ratio_25_50"], res["ratio_15_25"])

    def test_mc_flat_fails_m1(self):
        edges = grid(15.0, 50.0, 1.0)
        a, t, xc = asimov(edges, 0.0, scale=40.0)
        mc = {"edges": edges, "mumu": a, "emu": [ti * ac.R0 for ti in t]}
        res = ac.analyse_mc(mc, self.made_up_fig5(), {"b_hat": 0.0266, "sigma_b": 0.012})
        self.assertEqual(res["M1"], "FAIL")

    def test_unreadable_bin_fails_gate(self):
        edges = grid(15.0, 50.0, 1.0)
        mc = {"edges": edges, "mumu": [1.0] * 34 + [None], "emu": [1.0] * 35}
        res = ac.analyse_mc(mc, self.made_up_fig5(), {"b_hat": 0.0266, "sigma_b": 0.012})
        self.assertTrue(res["M0"].startswith("FAIL"))
        self.assertNotIn("M1", res)

    def test_misaligned_ee_fails_gate(self):
        ee = {"edges": grid(15.5, 49.5, 1.0), "n": [1] * 34}
        res = ac.analyse_ee(ee, self.made_up_fig5(), {"b_hat": 0.0266, "sigma_b": 0.012})
        self.assertTrue(res["E0"].startswith("FAIL"))


class TestAgainstPublishedModules(unittest.TestCase):
    """Same likelihood and signal as stats/emuframe.py 0.1.0 and stats/aprime_ext.py 0.1.0."""

    def setUp(self):
        try:
            import emuframe   # noqa: F401
            import aprime_ext
        except Exception:     # not next to this file (e.g. a fresh job folder)
            self.skipTest("emuframe / aprime_ext not importable")
        aprime_ext.bind(emuframe)
        self.ext = aprime_ext

    def test_lnl_identical(self):
        n = [12, 7, 0, 3, 9]
        m = [20.0, 11.5, 2.0, 0.4, 15.0]
        s = [0.5, 2.0, 4.0, 1.0, 0.1]
        rs = [0.5, 0.6, 0.7, 0.8, 0.55]
        for model in ("bb", "exact"):
            for mu in (0.0, 0.7, 1.5):
                self.assertAlmostEqual(ac.lnl(n, m, s, rs, mu, model),
                                       self.ext.lnl_r(n, m, s, rs, mu, model), places=9)

    def test_signal_template_identical(self):
        edges = grid(15.0, 50.0, 1.0)
        mine = ac.s_template(edges)
        theirs = self.ext.s_template(edges)
        for a, b in zip(mine, theirs):
            self.assertAlmostEqual(a, b, places=9)


if __name__ == "__main__":
    unittest.main()
