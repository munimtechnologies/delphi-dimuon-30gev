# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Licensed under Apache-2.0.
# Made with AI agents working in MV2's name.
"""Tests for injet.py. Run: python -m unittest -v test_injet"""
import json
import math
import os
import random
import unittest

import injet

HERE = os.path.dirname(os.path.abspath(__file__))


class TestBound(unittest.TestCase):
    def test_bound_is_reached(self):
        # symmetric pair on the cone edge, energies saturating the momentum balance
        for a in (5.0, 15.0, 20.0, 37.0, 60.0):
            for rs in (injet.SQRT_S_PEAK, injet.SQRT_S_MAX_LEP1):
                e = rs / (2.0 * (1.0 + math.cos(math.radians(a))))
                self.assertAlmostEqual(injet.pair_mass(e, e, 2.0 * a),
                                       injet.single_jet_mass_bound(a, rs), places=9)

    def test_random_pairs_never_exceed_bound(self):
        rng = random.Random(12345)
        for _ in range(20000):
            a = rng.uniform(1.0, 89.0)
            rs = injet.SQRT_S_PEAK
            # directions within a of the axis; opening angle at most 2a
            th = rng.uniform(0.0, 2.0 * a)
            # the pair's momentum along the axis is at least (E1+E2) cos a; the rest must balance
            esum_max = rs / (1.0 + math.cos(math.radians(a)))
            esum = rng.uniform(0.0, esum_max)
            f = rng.uniform(0.0, 1.0)
            m = injet.pair_mass(f * esum, (1.0 - f) * esum, th)
            self.assertLessEqual(m, injet.single_jet_mass_bound(a, rs) + 1e-9)

    def test_inverse(self):
        for m in (10.0, 28.0, 30.4, 40.0):
            c = injet.min_cone(m)
            self.assertAlmostEqual(injet.single_jet_mass_bound(c), m, places=9)
            self.assertAlmostEqual(injet.min_opening(m), 2.0 * c, places=12)

    def test_hand_values(self):
        # worked by hand in NOTE-injet.md sec. 2 (tan 7.5 deg = 0.1316525, tan 10 deg = 0.1763270)
        self.assertAlmostEqual(injet.single_jet_mass_bound(15, 91.19), 12.005, places=2)
        self.assertAlmostEqual(injet.single_jet_mass_bound(20, 91.19), 16.079, places=2)
        self.assertAlmostEqual(injet.single_jet_mass_bound(20, 94.3), 16.628, places=2)
        self.assertAlmostEqual(injet.single_jet_mass_bound(30, 94.3), 25.268, places=2)
        self.assertAlmostEqual(injet.min_cone(30.4, 91.19), 36.87, places=1)
        self.assertAlmostEqual(injet.min_cone(30.4, 94.3), 35.74, places=1)
        self.assertAlmostEqual(injet.min_opening(30.4, 94.3), 71.47, places=1)
        self.assertAlmostEqual(injet.min_cone(28.0, 94.3), 33.07, places=1)

    def test_l3_scaling(self):
        self.assertAlmostEqual(injet.l3_expected_upper(1.0), 3.77, places=2)
        self.assertAlmostEqual(injet.l3_expected_upper(1.5), 5.65, places=1)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            injet.single_jet_mass_bound(0.0)
        with self.assertRaises(ValueError):
            injet.single_jet_mass_bound(95.0)
        with self.assertRaises(ValueError):
            injet.min_cone(100.0)


class TestResultsFile(unittest.TestCase):
    def test_results_file_matches_code(self):
        path = os.path.join(HERE, "results", "injet", "injet-bounds.json")
        if not os.path.exists(path):
            self.skipTest("results file not present")
        with open(path) as f:
            hand = json.load(f)
        code = injet.results()
        self.assertEqual(hand["version"], code["version"])

        def walk(a, b, where):
            if isinstance(a, dict):
                self.assertEqual(sorted(a), sorted(b), where)
                for k in a:
                    walk(a[k], b[k], where + "/" + k)
            elif isinstance(a, list):
                self.assertEqual(len(a), len(b), where)
                for i, (x, y) in enumerate(zip(a, b)):
                    walk(x, y, "%s[%d]" % (where, i))
            elif isinstance(a, (int, float)) and not isinstance(a, bool):
                self.assertAlmostEqual(a, b, delta=0.011, msg=where)
            else:
                self.assertEqual(a, b, where)

        walk(hand, code, "")


if __name__ == "__main__":
    unittest.main()
