# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for abtag 0.1.0 on made-up inputs only (no ALEPH numbers)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import abtag as ab  # noqa: E402


class TestHelpers(unittest.TestCase):
    def test_readable_hi(self):
        edges = [14.0, 15.0, 16.0, 17.0, 18.0]
        self.assertEqual(ab.readable_hi(edges, [[None, 1, 1, 1]]), 18.0)
        self.assertEqual(ab.readable_hi(edges, [[1, 1, None, 1], [1, 1, 1, 1]]), 16.0)
        self.assertIsNone(ab.readable_hi(edges, [[1, None, 1, 1]]))

    def test_fill_nm(self):
        edges = [15.0, 16.0, 17.0, 18.0]
        out = ab.fill_nm([3, None, None], {"NM": [16], "OFF": [17]}, edges)
        self.assertEqual(out, [3.0, 0.0, None])
        with self.assertRaises(ValueError):
            ab.fill_nm([3, None, 1], {"NM": [], "OFF": []}, edges)

    def test_whole_numbers(self):
        self.assertTrue(ab.whole_numbers([3.0, 4.02, 0.0]))
        self.assertFalse(ab.whole_numbers([3.0, 4.3]))

    def test_pull(self):
        self.assertAlmostEqual(ab.pull(0.05, 0.03, 0.01, 0.04), 0.8)
        self.assertIsNone(ab.pull(0.05, None, 0.01, 0.04))

    def test_cut_sub_edges(self):
        edges = [15.0 + i for i in range(6)]
        self.assertEqual(ab.cut(edges, [1, 2, 3, 4, 5], 16.0, 19.0), [2, 3, 4])
        self.assertEqual(ab.sub_edges(edges, 16.0, 19.0), [16.0, 17.0, 18.0, 19.0])

    def test_ratio_halves(self):
        h = ab.ratio_halves([10, 10, 30, 30], [10, 10, 10, 10], [20.5, 24.5, 25.5, 30.5])
        self.assertAlmostEqual(h["r_lo"], 1.0)
        self.assertAlmostEqual(h["r_hi"], 3.0)


def fake(**kw):
    r = {"C0": "PASS", "ss_closure": {"ok": True}, "window_hi": 40.0, "window_nonneg": True,
         "data_whole": True, "n_events": 500.0,
         "slope_a": {"b_hat": 0.04, "Z_slope": 2.5, "sigma_b": 0.015},
         "pull_a_minus_ss": 0.1, "excess_slope_free": {"Z0": 0.5}}
    r.update(kw)
    return r


class TestGrade(unittest.TestCase):
    def test_pass(self):
        g = ab.grade(fake())
        self.assertEqual(g["A0"], "PASS")
        self.assertEqual([g[k] for k in ab.TESTS], ["PASS", "PASS", "FAIL", "PASS"])

    def test_gate(self):
        for kw in ({"C0": "FAIL"}, {"ss_closure": {"ok": False}}, {"window_hi": 29.0},
                   {"window_hi": None}, {"data_whole": False}, {"n_events": 99.0},
                   {"window_nonneg": False}):
            g = ab.grade(fake(**kw))
            self.assertTrue(g["A0"].startswith("FAIL"), kw)
            self.assertTrue(all(g[k].startswith("NOT GRADABLE") for k in ab.TESTS))

    def test_flat_b_specific(self):
        g = ab.grade(fake(slope_a={"b_hat": -0.01, "Z_slope": -0.8, "sigma_b": 0.01},
                          pull_a_minus_ss=-2.3, excess_slope_free={"Z0": 2.4}))
        self.assertEqual([g[k] for k in ab.TESTS], ["FAIL", "FAIL", "PASS", "FAIL"])

    def test_steeper(self):
        g = ab.grade(fake(slope_a={"b_hat": 0.12, "Z_slope": 6.0, "sigma_b": 0.01},
                          pull_a_minus_ss=4.0))
        self.assertEqual(g["A1"], "PASS")
        self.assertEqual(g["A2"], "FAIL")
        self.assertEqual(g["A3"], "FAIL")

    def test_no_interval(self):
        g = ab.grade(fake(pull_a_minus_ss=None))
        self.assertTrue(g["A2"].startswith("NOT GRADABLE"))
        self.assertTrue(g["A3"].startswith("NOT GRADABLE"))


class TestFits(unittest.TestCase):
    def setUp(self):
        if ab.ac is None or ab.dm is None:
            self.skipTest("aprime_cross / dmcratio not next to this file")
        self.ac, self.dm = ab.ac, ab.dm
        self.edges = [15.0 + i for i in range(16)]
        self.xc = self.ac.centres(self.edges)
        self.t = [200.0 * math.exp(-(x - 15.0) / 8.0) for x in self.xc]

    def test_slope_sign(self):
        rise = [ti * math.exp(0.06 * (x - 30.4)) for ti, x in zip(self.t, self.xc)]
        a = self.dm.slope(rise, self.t, self.xc)
        self.assertGreater(a["b_hat"], 0.04)
        flat = self.dm.slope(list(self.t), self.t, self.xc)
        self.assertLess(abs(flat["b_hat"]), 0.01)


if __name__ == "__main__":
    unittest.main()
