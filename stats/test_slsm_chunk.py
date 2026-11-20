# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for slsm_chunk 0.1.0 on made-up toy rows only (no ALEPH numbers)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import slsm_chunk as sc
except ImportError:  # pragma: no cover
    sc = None


def obs_ok():
    return {"closure_b0": 3.1339963632740275, "closure_parfit": 3.1339963632770744,
            "slope_mu0": {"b_hat": 0.03, "Z": 2.5}, "slope": {"Z0": 2.3},
            "const": {"Z0": 3.1}, "dev0": 30.0}


def rows(n, z=1.0, dev=35.0):
    return [{"idx": i, "slope": z, "const": z, "dev0": dev, "mu": 0.1, "b0": 0.0}
            for i in range(n)]


@unittest.skipUnless(sc is not None and sc.sl is not None, "needs aprime_slsm next to this file")
class TestChunk(unittest.TestCase):
    def test_prefix(self):
        r = [{"idx": i} for i in (0, 1, 2, 4, 5)]
        self.assertEqual([x["idx"] for x in sc.prefix(r)], [0, 1, 2])
        self.assertEqual(sc.prefix([{"idx": 3}]), [])
        self.assertEqual(len(sc.prefix([{"idx": i} for i in (2, 0, 1)])), 3)

    def test_too_few_toys(self):
        g = sc.summarise(obs_ok(), rows(10))["grades"]
        self.assertEqual(g["L0"], "PASS")
        self.assertEqual(g["L3"], "PASS")
        for k in ("L1", "L2", "L4", "L5"):
            self.assertTrue(g[k].startswith("NOT GRADABLE"), k)

    def test_no_toys(self):
        res = sc.summarise(obs_ok(), [])
        self.assertEqual(res["ntoys"], 0)
        self.assertTrue(res["grades"]["L1"].startswith("NOT GRADABLE"))

    def test_counts_match_aprime_slsm(self):
        r = rows(2000, z=1.0)
        for i in range(20):          # 20 of 2000 toys at or above the observed 2.3
            r[i]["slope"] = 2.5
        for i in range(40):          # 40 toys >= 2 in total (p_ge2 = 0.02)
            r[100 + i]["slope"] = 2.1
        res = sc.summarise(obs_ok(), r)
        self.assertEqual(res["calibrated"]["slope"]["k"], 20)
        self.assertAlmostEqual(res["rates"]["slope"]["p_ge2"], 60 / 2000)
        self.assertEqual(res["grades"]["L1"], "PASS")       # p = 0.01 -> Z 2.33 < 3
        self.assertEqual(res["grades"]["L2"], "FAIL")
        self.assertEqual(res["grades"]["L4"], "PASS")
        self.assertEqual(res["grades"]["L5"], "PASS")       # every toy deviance >= observed

    def test_gate_fail_propagates(self):
        o = obs_ok()
        o["closure_b0"] = 3.0
        g = sc.summarise(o, rows(2000))["grades"]
        self.assertEqual(g["L0"], "FAIL")
        self.assertTrue(g["L1"].startswith("NOT GRADABLE (L0"))


if __name__ == "__main__":
    unittest.main()
