"""Tests for lep4f (stdlib only). MV2 of Munim, Inc. Made with AI agents. Apache-2.0."""
import math
import unittest

import lep4f as L

try:  # agreement with analysis/nexp.py when it sits next to this file
    import nexp
except ImportError:  # pragma: no cover
    nexp = None


class TestPoisson(unittest.TestCase):
    def test_cdf_values(self):
        self.assertAlmostEqual(L.pois_cdf(0, 2.0), math.exp(-2.0), places=12)
        self.assertAlmostEqual(L.pois_cdf(1, 2.0), 3.0 * math.exp(-2.0), places=12)
        self.assertEqual(L.pois_cdf(-1, 2.0), 0.0)
        self.assertEqual(L.pois_cdf(3, 0.0), 1.0)
        self.assertAlmostEqual(L.pois_cdf(200, 30.0), 1.0, places=12)

    def test_classical_limits_without_background(self):
        # with b = 0, CLs = P(N <= n | s): the textbook 95 % Poisson upper limits
        for n, want in ((0, 2.9957), (1, 4.7439), (2, 6.2958), (3, 7.7537)):
            self.assertAlmostEqual(L.cls_upper(n, 0.0), want, delta=2e-3)

    def test_zero_observed_independent_of_b(self):
        for b in (0.5, 3.0, 12.0):
            self.assertAlmostEqual(L.cls_upper(0, b), -math.log(0.05), delta=1e-6)

    def test_limit_grows_with_uncertainty_and_count(self):
        a = L.cls_upper(28, 28.0, 0.0)
        b = L.cls_upper(28, 28.0, 0.1)
        self.assertGreater(b, a)
        self.assertGreater(L.cls_upper(30, 28.0), a)
        self.assertLess(L.cls_upper(26, 28.0), a)
        # hand estimate for n = b = 28 (normal approximation with continuity): about 12
        self.assertTrue(10.5 < a < 13.5, a)

    def test_cls_at_limit(self):
        s = L.cls_upper(19, 13.0, 0.1)
        self.assertAlmostEqual(L.cls(19, s, 13.0, 0.1), 0.05, delta=1e-6)

    def test_smeared_reduces_to_plain(self):
        self.assertEqual(L.cdf_smeared(5, 1.0, 4.0, 0.0), L.pois_cdf(5, 5.0))
        self.assertEqual(L.cdf_smeared(5, 1.0, 0.0, 0.2), L.pois_cdf(5, 1.0))


class TestRate(unittest.TestCase):
    def test_hand_values(self):
        # 32.31 / (1.9e6 / 0.9748) / (0.86^2 * 0.38) = 5.8982e-5
        self.assertAlmostEqual(L.rate_acc("nominal") / 5.8982e-5, 1.0, delta=2e-4)
        self.assertAlmostEqual(L.rate_acc("low") / L.rate_acc("nominal"), 1.9 / 2.2, places=12)
        with self.assertRaises(ValueError):
            L.rate_acc("high")

    @unittest.skipIf(nexp is None, "analysis/nexp.py not next to this file")
    def test_agrees_with_nexp(self):
        for rd in L.READINGS:
            for a_gen in (0.5, 0.83, 1.0):
                self.assertAlmostEqual(L.rate_acc(rd), nexp.rate_per_z(a_gen, rd) * a_gen,
                                       delta=1e-15)
        self.assertEqual(L.ALEPH_N_SIG, nexp.ALEPH_N_SIG)
        self.assertEqual(L.ALEPH_N_HAD, nexp.ALEPH_N_HAD)


class TestTable(unittest.TestCase):
    def test_inputs(self):
        self.assertAlmostEqual(L.EXPTS["OPAL"]["n_z"], 3530666.67, delta=0.01)
        self.assertEqual([L.EXPTS[k]["n_obs"] for k in ("ALEPH", "OPAL", "L3")], [19, 28, 6])
        self.assertEqual([L.EXPTS[k]["b"] for k in ("ALEPH", "OPAL", "L3")], [13.0, 28.0, 5.0])

    def test_eps_max_definition(self):
        t = L.table()
        for name, e in L.EXPTS.items():
            for key, rel in (("rel_0", 0.0), ("rel_0.1", 0.1)):
                r = t["experiments"][name][key]
                s_up = L.cls_upper(e["n_obs"], e["b"], rel)
                self.assertAlmostEqual(r["s_up_95"], s_up, places=9)
                for rd in L.READINGS:
                    pr = L.rate_acc(rd) * e["n_z"]
                    self.assertAlmostEqual(r[rd]["n_x_if_eps_1"], pr, places=6)
                    self.assertAlmostEqual(r[rd]["eps_max"], s_up / pr, places=12)
                    self.assertGreater(r[rd]["eps_max_aleph_minus_1sigma"], r[rd]["eps_max"])
                self.assertGreater(r["low"]["eps_max"], r["nominal"]["eps_max"])
        c = t["combined"]["rel_0"]
        self.assertEqual(c["n_obs"], 53)
        self.assertEqual(c["b"], 46.0)

    def test_opal_hand_estimate(self):
        # hand: s_up(28, 28) ~ 12, N_X(eps = 1) = 5.898e-5 * 3.53e6 = 208 -> eps_max ~ 0.06
        r = L.table()["experiments"]["OPAL"]["rel_0"]["nominal"]
        self.assertAlmostEqual(r["n_x_if_eps_1"], 208.25, delta=0.1)
        self.assertTrue(0.045 < r["eps_max"] < 0.07, r["eps_max"])


if __name__ == "__main__":
    unittest.main()
