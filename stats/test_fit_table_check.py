"""Tests for fit_table_check (MV2 of Munim, Inc.; Apache-2.0; made with AI agents)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fit_table_check as F  # noqa: E402


class TestIdentity(unittest.TestCase):
    def test_rho_recovers_constructed_value(self):
        # build a consistent table: N = 400, ds = 12, db = 22, rho = -0.5
        ds, db, rho = 12.0, 22.0, -0.5
        n = ds * ds + db * db + 2 * rho * ds * db
        s = 40.0
        b = n - s
        self.assertAlmostEqual(F.implied_rho(s, ds, b, db), rho, places=9)

    def test_rescaled_table_recovers_k(self):
        # same table with the background printed 4x larger: k = 4 gives back rho = -0.5
        ds, db, rho = 12.0, 22.0, -0.5
        n = ds * ds + db * db + 2 * rho * ds * db
        s, b = 40.0, n - 40.0
        self.assertAlmostEqual(F.implied_rho(s, ds, 4 * b, 4 * db, k=4.0), rho, places=9)
        kmin, kmax = F.allowed_k(s, ds, 4 * b, 4 * db)
        self.assertLessEqual(kmin, 4.0)
        self.assertGreaterEqual(kmax, 4.0)
        self.assertGreaterEqual(F.implied_rho(s, ds, 4 * b, 4 * db, k=kmin), -1.0 - 1e-9)
        self.assertAlmostEqual(F.implied_rho(s, ds, 4 * b, 4 * db, k=kmin), -1.0, places=6)


class TestHeister(unittest.TestCase):
    h = F.HEISTER

    def test_printed_table_impossible_as_in_fit_counts(self):
        rho = F.implied_rho(self.h["s"], self.h["ds"], self.h["b"], self.h["db"])
        self.assertLess(rho, -3.40)
        self.assertGreater(rho, -3.45)

    def test_allowed_k(self):
        kmin, kmax = F.allowed_k(self.h["s"], self.h["ds"], self.h["b"], self.h["db"])
        self.assertGreater(kmin, 2.50)
        self.assertLess(kmin, 2.55)
        self.assertGreater(kmax, 35.0)
        self.assertLess(kmax, 40.0)
        for k in (kmin * 1.001, 4.41, 10.0):
            self.assertTrue(F.rho_upper_ok(self.h["s"], self.h["ds"], self.h["b"], self.h["db"], k))

    def test_figure_scale_gives_plausible_rho(self):
        # fitted curve of the fit figure sums to 362.7 in 15-50 GeV -> b_in = 330.4, k = 4.41
        rho = F.implied_rho(self.h["s"], self.h["ds"], self.h["b"], self.h["db"], k=4.41)
        self.assertGreater(rho, -0.40)
        self.assertLess(rho, -0.36)


class TestSignalShape(unittest.TestCase):
    def test_normalisation(self):
        tot = sum(F.signal_in_bins([-1000.0, 30.4, 1000.0]))
        self.assertAlmostEqual(tot, F.HEISTER["s"], delta=0.1)

    def test_window_29_32(self):
        w = F.signal_in_bins([29.0, 30.0, 31.0, 32.0])
        self.assertEqual(len(w), 3)
        self.assertGreater(sum(w), 18.0)
        self.assertLess(sum(w), 20.5)
        self.assertGreater(w[1], w[0])
        self.assertGreater(w[1], w[2])


if __name__ == "__main__":
    unittest.main()
