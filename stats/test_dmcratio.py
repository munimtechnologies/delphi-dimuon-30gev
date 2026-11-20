# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for dmcratio 0.1.0 on made-up inputs only (no ALEPH numbers)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dmcratio as d  # noqa: E402

EDGES = [15.0 + i for i in range(36)]


class TestFill(unittest.TestCase):
    def test_nm_and_off(self):
        vals = [3.0, None, None, 1.0]
        marks = {"NM": [16], "OFF": [17]}
        self.assertEqual(d.fill(vals, marks, EDGES, None), [3.0, 0.0, None, 1.0])
        self.assertEqual(d.fill(vals, marks, EDGES, 0.0), [3.0, 0.0, 0.0, 1.0])
        self.assertEqual(d.fill(vals, marks, EDGES, 0.29), [3.0, 0.0, 0.29, 1.0])
        self.assertEqual(vals, [3.0, None, None, 1.0])            # input untouched

    def test_unmarked_null_raises(self):
        with self.assertRaises(ValueError):
            d.fill([1.0, None], {"NM": [], "OFF": []}, EDGES, 0.0)


class TestGates(unittest.TestCase):
    def test_g0(self):
        ok = d.g0_as_written({"a": [1.0, 0.0], "b": [2.0, 3.0]})
        self.assertEqual(ok["G0"], "PASS")
        bad = d.g0_as_written({"a": [1.0, None], "b": [None, None]})
        self.assertTrue(bad["G0"].startswith("FAIL"))
        self.assertEqual(bad["unreadable"], {"a": 1, "b": 2})
        neg = d.g0_as_written({"a": [1.0, -0.1]})
        self.assertTrue(neg["G0"].startswith("FAIL"))

    def test_g1(self):
        a = [10.0] * 35
        b = [10.0] * 30 + [11.0] * 5
        self.assertEqual(d.g1(a, b)["G1"], "PASS")
        b = [10.0] * 29 + [11.0] * 6
        r = d.g1(a, b)
        self.assertEqual((r["G1"], r["agree"]), ("FAIL", 29))
        self.assertEqual(d.g1([1.0], [1.6])["agree"], 1)         # tolerance inclusive

    def test_window(self):
        self.assertEqual(d.window(EDGES), list(range(35)))
        self.assertEqual(d.window([10.0 + i for i in range(41)]), list(range(5, 40)))


class TestGrades(unittest.TestCase):
    def sl(self, b, s, z):
        return {"b_hat": b, "sigma_b": s, "Z_slope": z}

    def test_shared_rise(self):
        g = d.grade(self.sl(0.03, 0.01, 3.0), self.sl(0.035, 0.012, 2.9), self.sl(0.0, 0.01, 0.1))
        self.assertEqual((g["D1"], g["D2"], g["S1"], g["S2"]), ("PASS", "PASS", "PASS", "FAIL"))

    def test_os_only(self):
        g = d.grade(self.sl(0.05, 0.01, 4.0), self.sl(-0.01, 0.01, -0.8), self.sl(0.0, 0.01, 2.5))
        self.assertEqual((g["D1"], g["D2"], g["S1"], g["S2"]), ("PASS", "FAIL", "FAIL", "PASS"))
        self.assertAlmostEqual(g["pull_os_ss"], 0.06 / math.sqrt(2e-4), places=9)

    def test_no_interval(self):
        g = d.grade(self.sl(0.03, None, 3.0), self.sl(0.03, 0.01, 3.0), self.sl(0.0, 0.01, 0.0))
        self.assertTrue(g["S1"].startswith("NOT GRADABLE"))

    def test_agreement(self):
        a = {"D1": "PASS", "D2": "PASS", "S1": "FAIL", "S2": "FAIL"}
        b = {"D1": "PASS", "D2": "PASS", "S1": "PASS", "S2": "FAIL"}
        g = d.agreement(a, b)
        self.assertEqual(g["D1"], "PASS")
        self.assertTrue(g["S1"].startswith("reading-dependent"))

    def test_ratio_sums(self):
        xc = [15.5 + i for i in range(35)]
        r = d.ratio_sums([2.0] * 35, [1.0] * 35, xc)
        self.assertAlmostEqual(r["r_15_25"], 2.0)
        self.assertAlmostEqual(r["n_25_50"], 50.0)


class TestWithAprimeCross(unittest.TestCase):
    def setUp(self):
        if d.ac is None:
            self.skipTest("aprime_cross not next to this file")

    def test_slope_sign_on_made_up_spectra(self):
        ac = d.ac
        xc = ac.centres(EDGES)
        t = [400.0 * math.exp(-(x - 15.0) / 8.0) for x in xc]
        rising = [ti * math.exp(0.05 * (x - 30.4)) for ti, x in zip(t, xc)]
        sl = d.slope(rising, t, xc)
        self.assertGreater(sl["b_hat"], 0.02)
        self.assertGreater(sl["Z_slope"], 0.0)
        flat = d.slope(list(t), list(t), xc)
        self.assertLess(abs(flat["b_hat"]), 0.01)
        self.assertLess(abs(flat["Z_slope"]), 0.5)


if __name__ == "__main__":
    unittest.main()
