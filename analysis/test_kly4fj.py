"""Unit tests for run_kly4fj (no event generation). Every expected number is worked by hand in
the comments. MV2 of Munim, Inc. Made with AI agents. Apache-2.0."""
import math
import unittest

import numpy as np

import run_kly4fj as r


class TestDurham(unittest.TestCase):
    def test_back_to_back_pair(self):
        # two 10 GeV massless particles back to back: d = 2 * 10^2 * (1 - (-1)) = 400
        p = [(10, 0, 0, 10), (10, 0, 0, -10)]
        h = r.durham_history(p)
        self.assertEqual(len(h), 1)
        self.assertAlmostEqual(h[0], 400.0, places=9)
        # E_norm 20: y = 400 / 400 = 1 >= 0.02 -> 2 jets
        self.assertEqual(r.njets_from_history(2, h, 0.02, 20.0), 2)

    def test_collinear_pair_merges_with_full_event_norm(self):
        # 10 GeV each, 10 deg apart: d = 200 (1 - cos 10 deg) = 200 * 0.01519225 = 3.03845
        c, s = math.cos(math.radians(10)), math.sin(math.radians(10))
        p = [(10, 10, 0, 0), (10, 10 * c, 10 * s, 0)]
        h = r.durham_history(p)
        self.assertAlmostEqual(h[0], 3.03845, places=4)
        # E_norm 91: y = 3.03845 / 8281 = 3.67e-4 < 0.02 -> one jet
        self.assertEqual(r.njets_from_history(2, h, 0.02, 91.0), 1)
        # E_norm 10: y = 0.0303845 >= 0.02 -> two jets
        self.assertEqual(r.njets_from_history(2, h, 0.02, 10.0), 2)

    def test_three_particles_order_and_values(self):
        # p1, p2 = 40 GeV along +-x; p3 = 5 GeV along y (90 deg to both)
        # d13 = d23 = 2 * 25 * 1 = 50 (tie: first in row order, (0, 2), is merged)
        # p1' = (45, 40, 5, 0), |p1'| = sqrt(1625) = 40.3113; cos(p1', p2) = -1600 / (40.3113 * 40)
        # = -0.992278; d = 2 * 40^2 * 1.992278 = 6375.29
        p = [(40, 40, 0, 0), (40, -40, 0, 0), (5, 0, 5, 0)]
        h = r.durham_history(p)
        self.assertEqual(len(h), 2)
        self.assertAlmostEqual(h[0], 50.0, places=9)
        self.assertAlmostEqual(h[1], 6375.29, delta=0.05)
        # E_norm 85 (e2 = 7225): y1 = 0.00692 -> 3 jets at 0.005, 2 jets at 0.02
        self.assertEqual(r.njets_from_history(3, h, 0.005, 85.0), 3)
        self.assertEqual(r.njets_from_history(3, h, 0.02, 85.0), 2)

    def test_njets_from_history_non_monotonic(self):
        # stops at the FIRST merge with y >= y_cut: 4 particles, history 1, 5, 3
        self.assertEqual(r.njets_from_history(4, [1.0, 5.0, 3.0], 2.0, 1.0), 3)
        self.assertEqual(r.njets_from_history(4, [1.0, 5.0, 3.0], 6.0, 1.0), 1)
        self.assertEqual(r.njets_from_history(1, [], 0.02, 1.0), 1)
        self.assertEqual(r.njets_from_history(3, [1.0, 2.0], 0.02, 0.0), 3)


class TestHadronicJets(unittest.TestCase):
    def test_muons_removed(self):
        # muons 40 GeV along +-x; two 5 GeV hadrons 10 deg apart near +z
        c, s = math.cos(math.radians(10)), math.sin(math.radians(10))
        ids = np.array([13, -13, 211, -211])
        p4 = np.array([(40, 40, 0, 0), (40, -40, 0, 0), (5, 0, 0, 5), (5, 0, 5 * s, 5 * c)], float)
        seen = np.ones(4, bool)
        hj = r.hadronic_jets(ids, p4, 0, 1, seen)
        # hadrons: d = 50 (1 - cos 10) = 0.759613; E_full = 90, E_had = 10
        self.assertAlmostEqual(hj["e_full"], 90.0)
        self.assertAlmostEqual(hj["e_had"], 10.0)
        self.assertAlmostEqual(hj["y12_full"], 0.759613 / 8100.0, places=8)
        self.assertAlmostEqual(hj["y12_had"], 0.00759613, places=7)
        self.assertEqual(hj["full02"], 1)     # 9.4e-5 < 0.02
        self.assertEqual(hj["had02"], 1)      # 0.0076 < 0.02
        self.assertEqual(hj["full005"], 1)    # 9.4e-5 < 0.005
        # all particles: hadrons merge first (0.76), next merge has d = 200 (cluster at 90 deg to a
        # muon, E_min 10): y = 200 / 8100 = 0.0247 >= 0.02 -> 3 jets
        self.assertEqual(hj["all02"], 3)

    def test_new_pass(self):
        hj = {"full02": 1, "had02": 2, "full005": 3}
        self.assertEqual(r.new_pass({"OPAL:nominal": True}, hj),
                         {"OPAL:hj_full02": False, "OPAL:hj_had02": True, "OPAL:hj_full005": True})
        self.assertEqual(set(r.new_pass({"OPAL:nominal": False}, hj).values()), {False})


class TestAgainstEff4f(unittest.TestCase):
    def test_same_jet_count_as_eff4f(self):
        try:
            import eff4f
        except Exception:
            self.skipTest("eff4f not importable here")
        rng = np.random.default_rng(7)
        for trial in range(20):
            n = int(rng.integers(3, 30))
            mom = rng.normal(size=(n, 3)) * rng.uniform(0.5, 10, size=(n, 1))
            e = np.linalg.norm(mom, axis=1)
            p4 = np.column_stack([e, mom])
            h = r.durham_history(p4)
            for y in (0.02, 0.005):
                self.assertEqual(r.njets_from_history(n, h, y, float(e.sum())),
                                 eff4f.durham_njets(p4, y))

    def test_closure_table_covers_models(self):
        try:
            import kly
        except Exception:
            self.skipTest("kly not importable here")
        self.assertEqual(set(r.KLY4F_V1), set(kly.MODELS))


if __name__ == "__main__":
    unittest.main()
