# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests of envpool. Every number below was worked out by hand first (PLAN-amendment-0.18.md)
or copied from the envtoys.json files the jobs wrote (scipy-computed intervals); the tests
recompute them."""
import json
import os
import unittest

import envpool as ep

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "analysis", "results")

# mu = 1 rows (n, n_EXCLUDED, muhat_mean) as written by the three jobs
V1 = {"fix3|tagged": (62, 1, 1.0236), "fix3|combined": (62, 2, 0.9977),
      "old|tagged": (62, 2, 0.9943), "old|combined": (62, 4, 0.8791)}
V2 = {"fix3|tagged": (60, 4, 0.9457), "fix3|combined": (60, 2, 0.9938),
      "old|tagged": (60, 2, 1.0024), "old|combined": (60, 3, 0.9174)}
V3 = {"fix3|tagged": (44, 1, 0.9561), "fix3|combined": (44, 0, 1.0763),
      "old|tagged": (44, 1, 0.968), "old|combined": (44, 1, 0.9455)}


class TestBinomial(unittest.TestCase):
    def test_cdf_small(self):
        self.assertAlmostEqual(ep.binom_cdf(0, 2, 0.5), 0.25, places=12)
        self.assertAlmostEqual(ep.binom_cdf(1, 2, 0.5), 0.75, places=12)
        self.assertAlmostEqual(ep.binom_cdf(2, 3, 0.5), 0.875, places=12)
        self.assertEqual(ep.binom_cdf(-1, 5, 0.3), 0.0)
        self.assertEqual(ep.binom_cdf(5, 5, 0.3), 1.0)

    def test_cdf_hand_values(self):
        # hand sums of the pmf (amendment 0.18, section 2)
        self.assertAlmostEqual(ep.binom_cdf(6, 166, 0.075), 0.03078, delta=3e-4)
        self.assertAlmostEqual(ep.binom_cdf(6, 166, 0.080), 0.01827, delta=3e-4)
        self.assertAlmostEqual(ep.binom_cdf(4, 166, 0.060), 0.02660, delta=3e-4)
        self.assertAlmostEqual(ep.binom_cdf(4, 166, 0.062), 0.02115, delta=3e-4)

    def test_cp_matches_scipy_values_in_job_files(self):
        # intervals printed by envtoys (scipy.stats.beta) in v2 and v3
        for (k, n), (lo, hi) in {(1, 44): (0.0006, 0.1202), (0, 44): (0.0, 0.0804),
                                 (4, 60): (0.0185, 0.162), (2, 60): (0.0041, 0.1153)}.items():
            a, b = ep.clopper_pearson(k, n)
            self.assertAlmostEqual(a, lo, delta=6e-5, msg=(k, n))
            self.assertAlmostEqual(b, hi, delta=6e-5, msg=(k, n))


class TestPool(unittest.TestCase):
    def pooled(self):
        return ep.pool([V1, V2, V3])

    def test_counts_and_means(self):
        p = self.pooled()
        hand = {"fix3|tagged": (166, 6, 0.977552), "fix3|combined": (166, 4, 1.017124),
                "old|tagged": (166, 5, 0.990257), "old|combined": (166, 8, 0.910543)}
        for k, (n, ex, m) in hand.items():
            self.assertEqual(p[k]["n"], n, k)
            self.assertEqual(p[k]["n_EXCLUDED"], ex, k)
            self.assertAlmostEqual(p[k]["p_EXCLUDED"], ex / 166.0, places=12)
            self.assertAlmostEqual(p[k]["muhat_mean"], m, delta=2e-6, msg=k)

    def test_intervals_bracketed_by_hand(self):
        p = self.pooled()
        lo, hi = p["fix3|tagged"]["p_EXCLUDED_cp95"]
        self.assertTrue(0.075 < hi < 0.080, hi)        # above 0.07: stated in the amendment
        self.assertTrue(0.012 < lo < 0.015, lo)
        lo, hi = p["fix3|combined"]["p_EXCLUDED_cp95"]
        self.assertTrue(0.060 < hi < 0.062, hi)
        self.assertTrue(0.005 < lo < 0.008, lo)

    def test_grades(self):
        g = ep.grade(self.pooled())
        self.assertEqual(g, {"N7": "PASS", "N9": "PASS", "N10": "PASS"})
        # the rule as written: below 150 toys it is undetermined, whatever the rate
        self.assertEqual(ep.grade(ep.pool([V1, V2]))["N7"], "UNDETERMINED")
        # and it can fail: 12 exclusions in test A
        bad = dict(V3)
        bad["fix3|tagged"] = (44, 7, 0.9561)
        self.assertEqual(ep.grade(ep.pool([V1, V2, bad]))["N7"], "FAIL")
        self.assertEqual(ep.grade(self.pooled(), hashes_ok=False)["N9"], "FAIL")

    def test_v3_file_matches(self):
        f = os.path.join(RES, "envtoys-v3", "envtoys.json")
        if not os.path.exists(f):
            self.skipTest("results file not alongside")
        self.assertEqual(ep.batch(json.load(open(f))), V3)

    def test_pool_file_matches(self):
        f = os.path.join(RES, "envtoys-pool", "pool.json")
        if not os.path.exists(f):
            self.skipTest("results file not alongside")
        r = json.load(open(f))
        p = self.pooled()
        for k in ep.KEYS:
            self.assertEqual(r["pooled"][k]["n"], p[k]["n"])
            self.assertEqual(r["pooled"][k]["n_EXCLUDED"], p[k]["n_EXCLUDED"])
            self.assertAlmostEqual(r["pooled"][k]["muhat_mean"], p[k]["muhat_mean"], delta=1e-5)
        self.assertEqual(r["grades"], ep.grade(p))


if __name__ == "__main__":
    unittest.main()
