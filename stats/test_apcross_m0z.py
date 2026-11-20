# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for apcross_m0z 0.1.0 on made-up inputs only (no ALEPH numbers)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apcross_m0z as m  # noqa: E402


def made_up_mc():
    edges = [15.0 + i for i in range(36)]
    mumu = [10.0 - 0.25 * i for i in range(31)] + [None] * 4
    emu = [9.0 - 0.2 * i for i in range(35)]
    return {"edges": edges, "mumu": mumu, "emu": emu}


class TestFill(unittest.TestCase):
    def test_zero(self):
        mc = made_up_mc()
        out, filled = m.fill_nulls(mc, "zero")
        self.assertEqual(out["mumu"][-4:], [0.0] * 4)
        self.assertEqual(filled, [("mumu", 46.0), ("mumu", 47.0), ("mumu", 48.0), ("mumu", 49.0)])
        self.assertEqual(mc["mumu"][-1], None)          # input untouched
        self.assertEqual(out["emu"], mc["emu"])

    def test_other(self):
        mc = made_up_mc()
        out, filled = m.fill_nulls(mc, "other")
        self.assertEqual(out["mumu"][-4:], mc["emu"][-4:])
        self.assertEqual(len(filled), 4)

    def test_emu_null_filled_from_mumu(self):
        mc = made_up_mc()
        mc["emu"][0] = None
        out, filled = m.fill_nulls(mc, "other")
        self.assertEqual(out["emu"][0], mc["mumu"][0])
        self.assertIn(("emu", 15.0), filled)

    def test_both_null_and_unknown_fill_raise(self):
        mc = made_up_mc()
        mc["emu"][-1] = None
        with self.assertRaises(ValueError):
            m.fill_nulls(mc, "other")
        with self.assertRaises(ValueError):
            m.fill_nulls(made_up_mc(), "mean")


class TestHelpers(unittest.TestCase):
    def test_degeneracy(self):
        const = {"lnL_best": -10.0, "mu_hat": 1.0, "Z0": 2.5, "b_hat": 0.0}
        slope = {"lnL_best": -9.5, "mu_hat": 0.6, "Z0": 1.5, "b_hat": 0.02}
        d = m.degeneracy(const, slope)
        self.assertAlmostEqual(d["Z_slope_signal_floated"], 1.0, places=12)
        slope["b_hat"] = -0.02
        self.assertAlmostEqual(m.degeneracy(const, slope)["Z_slope_signal_floated"], -1.0,
                               places=12)
        slope["lnL_best"] = -10.2                         # numerical noise: never negative q
        self.assertEqual(m.degeneracy(const, slope)["Z_slope_signal_floated"], 0.0)

    def test_agreement(self):
        a = {"M1": "FAIL", "M2": "PASS", "M3": "FAIL"}
        b = {"M1": "FAIL", "M2": "FAIL", "M3": "FAIL"}
        g = m.agreement(a, b)
        self.assertEqual(g["M1"], "FAIL")
        self.assertTrue(g["M2"].startswith("reading-dependent"))


class TestWithAprimeCross(unittest.TestCase):
    def setUp(self):
        if m.ac is None:
            self.skipTest("aprime_cross not next to this file")

    def test_zero_fill_passes_gate_where_raw_fails(self):
        ac = m.ac
        edges = [15.0 + i for i in range(36)]
        xc = ac.centres(edges)
        t = [40.0 * math.exp(-(x - 15.0) / 8.0) for x in xc]
        fig5 = {"edges": edges, "n": [round(0.6 * ti) for ti in t],
                "v_scaled": [ti * ac.R0 for ti in t]}
        mc = {"edges": edges, "mumu": [0.6 * ti for ti in t[:31]] + [None] * 4,
              "emu": [ti * ac.R0 for ti in t]}
        ds = {"b_hat": 0.0266, "sigma_b": 0.012}
        self.assertTrue(ac.analyse_mc(mc, fig5, ds)["M0"].startswith("FAIL"))
        mcz, _ = m.fill_nulls(mc, "zero")
        r = ac.analyse_mc(mcz, fig5, ds)
        self.assertEqual(r["M0"], "PASS")
        self.assertIn(r["M1"], ("PASS", "FAIL"))


if __name__ == "__main__":
    unittest.main()
