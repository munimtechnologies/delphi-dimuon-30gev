# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Tests for bound.py (pure standard library)."""
import math
import unittest

import bound


def _cell(n_window, n_defined, f15, near15=0.05):
    d = dict(n_defined=n_defined, n_undefined=n_window - n_defined, f_amin_lt15=f15,
             median_aoth=11.5, f_aoth_lt20=0.9)
    return {"n_window": n_window, "R0.4": d, "R0.7": dict(d), "R1.0": dict(d),
            "nearest_jet_R0.4": dict(f_min_lt15=near15, f_both_lt20=0.0, f_both_gt20=0.0)}


def _summary():
    # the xkin-v1 numbers (p_cut, R = 0.4) for V and P, synthetic elsewhere
    s = {"V": {"p_cut": _cell(16062, 12208, 0.0537), "pt_cut": _cell(16035, 12198, 0.0537)},
         "S": {"p_cut": _cell(14860, 8052, 0.0784), "pt_cut": _cell(14832, 8041, 0.0781)},
         "P": {"p_cut": _cell(16708, 6721, 0.1134), "pt_cut": _cell(16676, 6708, 0.1133)},
         "bkg": {"p_cut": _cell(525, 525, 0.9943), "pt_cut": _cell(525, 525, 0.9943)}}
    return {"tool": "xkin 0.1.0", "samples": s}


class TestPoisson(unittest.TestCase):
    def test_cdf(self):
        self.assertAlmostEqual(bound.poisson_cdf(0, 2.0), math.exp(-2.0), places=12)
        self.assertAlmostEqual(bound.poisson_cdf(2, 1.0), 2.5 * math.exp(-1.0), places=12)
        self.assertEqual(bound.poisson_cdf(-1, 1.0), 0.0)
        self.assertEqual(bound.poisson_cdf(0, 0.0), 1.0)

    def test_upper_limits(self):
        # textbook 95 % one-sided Poisson upper limits for n = 0, 1, 2
        self.assertAlmostEqual(bound.poisson_ul(0), -math.log(0.05), places=6)
        self.assertAlmostEqual(bound.poisson_ul(1), 4.743865, places=5)
        self.assertAlmostEqual(bound.poisson_ul(2), 6.295794, places=5)


class TestNormal(unittest.TestCase):
    def test_phi_and_z(self):
        self.assertAlmostEqual(bound.phi(0.0), 0.5, places=12)
        self.assertAlmostEqual(bound.z_from_p(0.5), 0.0, places=8)
        self.assertAlmostEqual(bound.z_from_p(0.0013498980), 3.0, places=5)
        self.assertAlmostEqual(bound.z_from_p(bound.phi(-5.2)), 5.2, places=6)
        with self.assertRaises(ValueError):
            bound.z_from_p(0.0)


class TestMarginal(unittest.TestCase):
    def test_closed_form_matches_numeric(self):
        for g in (0.71924, 0.49938, 0.35665, 0.28955, 0.05):
            a = bound.marginal_p0(g)
            b = bound.marginal_p(0, g)
            self.assertAlmostEqual(a / b, 1.0, delta=2e-3, msg=str(g))

    def test_no_spread_limit(self):
        self.assertAlmostEqual(bound.marginal_p0(0.5, 10.0, 0.0), math.exp(-5.0), places=12)
        self.assertAlmostEqual(bound.marginal_p(0, 0.5, 10.0, 0.0), math.exp(-5.0), places=12)

    def test_hand_values(self):
        # hand calculation in NOTE-kinematics.md: V ~9.5e-4, S ~1.73e-3, P ~3.3e-3
        self.assertAlmostEqual(bound.marginal_p0(12208 / 16062 * (1 - 0.0537)), 9.5e-4,
                               delta=0.3e-4)
        self.assertAlmostEqual(bound.marginal_p0(8052 / 14860 * (1 - 0.0784)), 1.73e-3,
                               delta=0.03e-3)
        self.assertAlmostEqual(bound.marginal_p0(6721 / 16708 * (1 - 0.1134)), 3.32e-3,
                               delta=0.05e-3)

    def test_more_exceptions_raise_p(self):
        g = 0.35665
        self.assertGreater(bound.marginal_p(1, g), bound.marginal_p(0, g))


class TestBound(unittest.TestCase):
    def test_fractions(self):
        f_def, f_away, g = bound.model_fractions(_cell(100, 80, 0.25), "R0.4")
        self.assertAlmostEqual(f_def, 0.8)
        self.assertAlmostEqual(f_away, 0.75)
        self.assertAlmostEqual(g, 0.6)

    def test_row(self):
        r = bound.bound_row(0.8, 0.75)
        self.assertAlmostEqual(r["g"], 0.6)
        self.assertAlmostEqual(r["ul_boson_events"], -math.log(0.05) / 0.6, places=3)
        self.assertAlmostEqual(r["p_at_fit"], math.exp(-0.6 * bound.N_FIT), places=12)
        self.assertAlmostEqual(r["expected_away_at_fit"], 0.6 * bound.N_FIT, places=3)
        with self.assertRaises(ValueError):
            bound.bound_row(0.0, 0.5)

    def test_xkin_v1_numbers(self):
        res = bound.analyse(_summary())
        rows = {(r["model"], r["cut"], r["R"]): r for r in res["rows"]}
        self.assertEqual(len(res["rows"]), 3 * 2 * 4)
        v = rows[("V", "p_cut", "R0.4")]
        p = rows[("P", "p_cut", "R0.4")]
        s = rows[("S", "p_cut", "R0.4")]
        self.assertAlmostEqual(v["ul_boson_events"], 4.165, delta=0.002)
        self.assertAlmostEqual(s["ul_boson_events"], 5.999, delta=0.002)
        self.assertAlmostEqual(p["ul_boson_events"], 8.400, delta=0.002)
        self.assertAlmostEqual(p["expected_away_at_fit"], 11.523, delta=0.002)
        self.assertAlmostEqual(res["background_check"]["f_amin_lt15_R04"], 0.9943)
        self.assertEqual(res["weakest_hemisphere_reading"]["model"], "P")
        nv = rows[("V", "p_cut", "nearest_R0.4_all_events")]
        self.assertAlmostEqual(nv["g"], 0.95)


if __name__ == "__main__":
    unittest.main()
