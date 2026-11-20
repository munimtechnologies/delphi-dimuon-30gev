"""Unit tests for run_klyscan (no event generation). Every expected number is worked by hand in
the comments. MV2 of Munim, Inc. Made with AI agents. Apache-2.0."""
import math
import types
import unittest

import run_klyscan as r


class TestPoisson(unittest.TestCase):
    def test_p_le_1(self):
        # e^-17.3 = e^-17 * e^-0.3 = 4.139938e-8 * 0.7408182 = 3.066941e-8; x (1 + 17.3) = 5.61250e-7
        self.assertAlmostEqual(r.poisson_le(1, 17.30) / 5.61250e-7, 1.0, delta=1e-4)

    def test_p_le_0(self):
        # e^-6.91 = e^-7 * e^0.09 = 9.118820e-4 * 1.094174 = 9.97758e-4
        self.assertAlmostEqual(r.poisson_le(0, 6.91) / 9.97758e-4, 1.0, delta=1e-4)

    def test_lam_needed(self):
        # k = 0: e^-lam = 1e-3 -> lam = ln 1000 = 6.907755
        self.assertAlmostEqual(r.lam_needed(0, 1e-3), 6.907755, places=4)
        # k = 1: e^-9.233 * 10.233 = 9.775958e-5 * 10.233 = 1.000364e-3; slope -lam e^-lam =
        # -9.026e-4, so lam = 9.233 + 3.64e-7 / 9.026e-4 = 9.2334
        self.assertAlmostEqual(r.lam_needed(1, 1e-3), 9.2334, delta=0.002)


class TestThresholds(unittest.TestCase):
    def test_thresholds_dict(self):
        # 0.1.1 fix: string keys; values as in TestL3Higgs.test_threshold and test_lam_needed
        t = r.thresholds()
        self.assertEqual(sorted(t), ["L3H_eps_weakest_for_p1e-3", "lam_needed_1obs_p1e-3"])
        self.assertAlmostEqual(t["L3H_eps_weakest_for_p1e-3"], 0.26178, places=4)
        self.assertAlmostEqual(t["lam_needed_1obs_p1e-3"], 9.2334, delta=0.002)

    def test_version(self):
        self.assertEqual(r.VERSION, "mv2 klyscan 0.1.1")


class TestL3Higgs(unittest.TestCase):
    def test_threshold(self):
        # p < 1e-3 with 0 candidates needs lam >= 6.907755; 33.83 x 0.78 = 26.3874 per unit eps;
        # eps >= 6.907755 / 26.3874 = 0.26178
        self.assertAlmostEqual(math.log(1000.0) / (r.L3H_LIT_EPS1 * r.CAL["L3H"]), 0.26178, places=4)

    def test_q12_pessimistic(self):
        # NOTE section 6: Q12 L3 weakest 0.456 x 33.83 x 0.78 = 12.03265;
        # p = e^-12.03265 = 6.144212e-6 x e^-0.03265 (0.967877) = 5.94684e-6
        t = r.l3h_alone(0.456, r.CAL["L3H"])
        self.assertAlmostEqual(t["pred"], 12.03265, places=4)
        self.assertEqual(t["n_obs"], 0)
        self.assertAlmostEqual(t["p"] / 5.94684e-6, 1.0, delta=1e-4)

    def test_q12_l3_alone_nominal(self):
        # kly-v1: Q12 L3 eps 0.604 -> 0.604 x 33.83 = 20.433 (NOTE table: 20.43)
        self.assertAlmostEqual(r.l3h_alone(0.604)["pred"], 20.433, places=3)


class TestLabelsSeeds(unittest.TestCase):
    def test_labels(self):
        self.assertEqual([r.scan_label(m) for m in r.SCAN],
                         ["Q15", "Q20", "Q25", "Q35", "Q40", "Q45", "Q55"])

    def test_seeds(self):
        b = 20261121
        # Q30 is index 4 in run_kly's order: b + 7 x 4 + 1 = 20261150 (kly-v1's seed)
        self.assertEqual(r.seed_for("Q30", b), 20261150)
        # Q15: b + 7 x (6 + 0) + 1 = 20261164; Q45: b + 7 x (6 + 5) + 1 = 20261199
        self.assertEqual(r.seed_for("Q15", b), 20261164)
        self.assertEqual(r.seed_for("Q45", b), 20261199)
        # Q55: b + 7 x (6 + 6) + 1 = 20261206
        self.assertEqual(r.seed_for("Q55", b), 20261206)
        seeds = [r.seed_for(x, b) for x in r.ORDER] + [r.seed_for(r.scan_label(m), b) for m in r.SCAN]
        self.assertEqual(len(set(seeds)), 13)

    def test_register_fake(self):
        fake = types.SimpleNamespace(MODELS={"Q12": ("zs", dict(m_phi=12.0), "P", 35),
                                             "Q50": ("zs", dict(m_phi=50.0), "P", 35)})
        added = r.register(fake)
        self.assertEqual(added, ["Q15", "Q20", "Q25", "Q35", "Q40", "Q45", "Q55"])
        self.assertEqual(fake.MODELS["Q25"], ("zs", {"m_phi": 25.0}, "P", 35))
        self.assertEqual(fake.MODELS["Q12"], ("zs", {"m_phi": 12.0}, "P", 35))
        self.assertEqual(r.register(fake), [])     # idempotent

    def test_weakest(self):
        e = {"L3_96:nominal": 0.6, "L3_96:cos0.72": 0.45, "L3_96:nothrust": 0.7, "DELPHI94:nominal": 0.1}
        self.assertEqual(r.weakest_of(e, "L3_96"), ("L3_96:cos0.72", 0.45))


class TestPublishedModules(unittest.TestCase):
    """Interface checks against the published kly, lephz and eff4f (skipped if absent)."""

    def test_kly_register(self):
        try:
            import kly
        except ImportError:
            self.skipTest("kly.py not present")
        r.register(kly)
        self.assertEqual(kly.MODELS["Q20"][1], {"m_phi": 20.0})
        self.assertEqual(kly.MODELS["Q20"][0], kly.MODELS["Q50"][0])

    def test_lephz_keys(self):
        try:
            import lephz
        except ImportError:
            self.skipTest("lephz.py not present")
        for s in ("ALEPH96", "L3_96", "DELPHI94", "OPAL97"):
            self.assertIn(s, lephz.ALL_SET)
            self.assertIn(s + ":nominal", lephz.KEYS)

    def test_eff4f_confront(self):
        try:
            import eff4f
        except ImportError:
            self.skipTest("eff4f.py not present")
        n_lit = eff4f.n_sig_for_rate(eff4f.R_LIT)
        # efficiency 1, OPAL alone: 39.171 events (NOTE section 6b hand check)
        c1 = eff4f.confront(("OPAL",), {"OPAL": 1.0, "L3": 1.0, "ALEPH": 1.0}, n_sig=n_lit)
        self.assertAlmostEqual(c1["pred"], 39.171, delta=0.01)
        self.assertEqual(c1["n_obs"], 1)
        # NOTE 6b robustness: OPAL 0.7688 x 0.62 x 39.171 = 18.6711; L3 0.4866 x 0.78 x 10.651 =
        # 4.04257; total 22.7137; p = e^-22.7137 x 23.7137 = 1.366362e-10 x 23.7137 = 3.24015e-9
        c = eff4f.confront(("OPAL", "L3"), {"OPAL": 0.7688 * 0.62, "L3": 0.4866 * 0.78, "ALEPH": 0.5},
                           n_sig=n_lit)
        self.assertAlmostEqual(c["pred"], 22.7137, delta=0.01)
        self.assertAlmostEqual(c["p_value"] / 3.24015e-9, 1.0, delta=0.01)


if __name__ == "__main__":
    unittest.main()
