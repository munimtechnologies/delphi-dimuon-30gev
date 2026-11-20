# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for sscontrol 0.1.0 on made-up inputs only (no ALEPH numbers)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sscontrol as sc  # noqa: E402


class TestHelpers(unittest.TestCase):
    def test_readable_hi(self):
        edges = [15.0, 16.0, 17.0, 18.0, 19.0, 20.0]
        self.assertEqual(sc.readable_hi(edges, [[1, 1, 1, 1, 1]]), 20.0)
        self.assertEqual(sc.readable_hi(edges, [[1, 1, None, 1, 1], [1, 1, 1, 1, 1]]), 17.0)
        self.assertEqual(sc.readable_hi(edges, [[1, 1, 1, 1, 1], [1, 1, 1, None, None]]), 18.0)
        self.assertIsNone(sc.readable_hi(edges, [[None, 1, 1, 1, 1]]))
        # bins below lo are ignored
        self.assertEqual(sc.readable_hi(edges, [[None, 1, 1, 1, 1]], lo=16.0), 20.0)

    def test_cut_and_sub_edges(self):
        edges = [15.0 + i for i in range(6)]
        vals = [10, 11, 12, 13, 14]
        self.assertEqual(sc.cut(edges, vals, 15.0, 18.0), [10, 11, 12])
        self.assertEqual(sc.sub_edges(edges, 15.0, 18.0), [15.0, 16.0, 17.0, 18.0])
        self.assertEqual(sc.cut(edges, vals, 16.0, 20.0), [11, 12, 13, 14])

    def test_control_slope(self):
        c = sc.control_slope({"b_hat": 0.04, "sigma_b": 0.03}, {"b_hat": -0.01, "sigma_b": 0.04})
        self.assertAlmostEqual(c["b_ctrl"], 0.05)
        self.assertAlmostEqual(c["sigma_ctrl"], 0.05)
        c = sc.control_slope({"b_hat": 0.04, "sigma_b": None}, {"b_hat": 0.0, "sigma_b": 0.01})
        self.assertIsNone(c["sigma_ctrl"])

    def test_clamp(self):
        self.assertEqual(sc.clamp(0.5), 0.2)
        self.assertEqual(sc.clamp(-0.5), -0.2)
        self.assertEqual(sc.clamp(0.01), 0.01)


def fake_result(**kw):
    r = {"C0": "PASS", "dmc_closure": {"ok": True}, "window_hi": 38.0, "window_ok": True,
         "slopes_w": {"ss": {"b_hat": 0.03, "Z_slope": 2.1},
                      "emu": {"b_hat": 0.0, "Z_slope": 0.1}},
         "joint_w_signal_floated": {"b_hat": 0.03, "Z_slope": 2.5},
         "W4_pull": 0.5, "constrained": {"Z0": 1.7}}
    r.update(kw)
    return r


class TestGrade(unittest.TestCase):
    def test_all_pass(self):
        g = sc.grade(fake_result())
        self.assertEqual([g[k] for k in ("W0",) + sc.TESTS], ["PASS"] * 6)

    def test_gate_fails(self):
        for kw in ({"C0": "FAIL"}, {"window_hi": 39.0}, {"window_ok": False},
                   {"dmc_closure": {"ok": False}}, {"window_hi": None}):
            g = sc.grade(fake_result(**kw))
            self.assertEqual(g["W0"], "FAIL")
            self.assertTrue(all(g[k].startswith("NOT GRADABLE") for k in sc.TESTS))

    def test_fails(self):
        r = fake_result(slopes_w={"ss": {"b_hat": -0.03, "Z_slope": -2.1},
                                  "emu": {"b_hat": 0.05, "Z_slope": 2.3}},
                        joint_w_signal_floated={"b_hat": 0.02, "Z_slope": 1.9},
                        W4_pull=-2.2, constrained={"Z0": 2.0})
        g = sc.grade(r)
        self.assertEqual([g[k] for k in sc.TESTS], ["FAIL"] * 5)

    def test_not_gradable(self):
        g = sc.grade(fake_result(W4_pull=None, constrained=None))
        self.assertTrue(g["W4"].startswith("NOT GRADABLE"))
        self.assertTrue(g["W5"].startswith("NOT GRADABLE"))


class TestFits(unittest.TestCase):
    def setUp(self):
        if sc.ac is None:
            self.skipTest("aprime_cross not next to this file")
        self.ac = sc.ac
        self.edges = [26.0 + i for i in range(9)]          # 8 bins around 30.4 GeV
        self.xc = self.ac.centres(self.edges)
        self.t = [60.0 * math.exp(-(x - 26.0) / 6.0) for x in self.xc]

    def test_joint_slope_sign(self):
        rise = [ti * math.exp(0.08 * (x - 30.4)) for ti, x in zip(self.t, self.xc)]
        j = sc.joint_slope(rise, self.t, rise, self.t, self.xc)
        self.assertGreater(j["b_hat"], 0.04)
        self.assertGreater(j["Z_slope"], 0.0)
        flat = sc.joint_slope(list(self.t), self.t, list(self.t), self.t, self.xc)
        self.assertLess(abs(flat["b_hat"]), 0.01)
        self.assertLess(abs(flat["Z_slope"]), 0.3)

    def test_joint_slope_with_signal(self):
        s = self.ac.s_template(self.edges)
        os_n = [ti + si for ti, si in zip(self.t, s)]
        j = sc.joint_slope(os_n, self.t, list(self.t), self.t, self.xc, s)
        self.assertTrue(j["signal_floated"])
        self.assertLess(abs(j["b_hat"]), 0.05)

    def test_constrained_limits(self):
        s = self.ac.s_template(self.edges)
        m = [ti / 0.6 for ti in self.t]
        n = [0.6 * mi * math.exp(0.03 * (x - 30.4)) + 0.6 * si
             for mi, x, si in zip(m, self.xc, s)]
        fixed0 = self.ac.discovery(n, m, s, "bb", self.xc, 0.0)
        free = self.ac.discovery(n, m, s, "bb", self.xc, None)
        tight = sc.constrained_discovery(n, m, s, self.xc, 0.0, 1e-4)
        loose = sc.constrained_discovery(n, m, s, self.xc, 0.0, 10.0)
        self.assertAlmostEqual(tight["Z0"], fixed0["Z0"], delta=0.05)
        self.assertAlmostEqual(loose["Z0"], free["Z0"], delta=0.05)
        self.assertLess(abs(tight["b_hat"]), 1e-3)


if __name__ == "__main__":
    unittest.main()
