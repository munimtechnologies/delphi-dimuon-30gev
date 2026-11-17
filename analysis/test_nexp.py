"""Tests for nexp (MV2 of Munim, Inc.; made with AI agents; Apache-2.0)."""
import json
import os
import tempfile
import unittest

import nexp

# a synthetic DELPHI period: 1.4M produced Z, 85 % hadronic efficiency (thrust cut included),
# signal efficiency 0.35 before the tag, data b efficiency 0.38
P94 = {"n_had_data": 1.19e6, "n_had_mc": 8500, "n_events_mc": 10000, "eff_sel": 0.35, "eps": 0.38}


class TestNexp(unittest.TestCase):
    def test_aleph_eff_sig(self):
        self.assertAlmostEqual(nexp.aleph_eff_sig(0.5), 0.140524, places=9)
        for bad in (0.0, 1.5):
            with self.assertRaises(ValueError):
                nexp.aleph_eff_sig(bad)

    def test_readings_ratio(self):
        r = nexp.rate_per_z(0.4, "low") / nexp.rate_per_z(0.4, "nominal")
        self.assertAlmostEqual(r, 1.9 / 2.2, places=12)
        with self.assertRaises(ValueError):
            nexp.rate_per_z(0.4, "middle")

    def test_n_z_delphi(self):
        n_z, eff = nexp.n_z_delphi(1.2e6, 8000, 10000)
        self.assertAlmostEqual(eff, 0.8, places=12)
        self.assertAlmostEqual(n_z, 1.5e6, places=3)
        with self.assertRaises(ValueError):
            nexp.n_z_delphi(1.2e6, 10001, 10000)
        with self.assertRaises(ValueError):
            nexp.n_z_delphi(1.2e6, 0, 0)

    def test_closure_on_a_known_world(self):
        # true rate 2e-4 per produced Z; ALEPH produced 2.0M Z (1.9M selected at 95 %)
        a_gen, rate_true = 0.3, 2e-4
        eff_a = nexp.aleph_eff_sig(a_gen)
        n_sig = rate_true * 2.0e6 * eff_a
        aleph = dict(n_sig=n_sig, n_had=1.9e6, eff_had=0.95)
        self.assertAlmostEqual(nexp.rate_per_z(a_gen, **aleph), rate_true, places=15)
        y = nexp.period_yields(P94, rate_true)
        self.assertAlmostEqual(y["n_z"], 1.4e6, places=3)
        self.assertAlmostEqual(y["n_t"], 37.24, places=6)
        self.assertAlmostEqual(y["n_u"], 60.76, places=6)
        self.assertAlmostEqual(y["n_t"] + y["n_u"], y["s_before_tag"], places=9)
        t = nexp.totals({"y94": P94}, a_gen, **aleph)
        self.assertAlmostEqual(t["readings"]["nominal"]["n_t"], 37.24, places=6)

    def test_rho(self):
        rate = nexp.rate_per_z(0.3)
        y1 = nexp.period_yields(P94, rate, 1.0)
        y2 = nexp.period_yields(P94, rate, 1.2)
        self.assertAlmostEqual(y2["n_t"], y1["n_t"], places=12)
        self.assertAlmostEqual(y2["n_u"], y2["n_t"] * (1 - 0.456) / 0.456, places=9)
        self.assertLess(y2["n_u"], y1["n_u"])
        with self.assertRaises(ValueError):
            nexp.period_yields(P94, rate, 0.9)
        with self.assertRaises(ValueError):
            nexp.period_yields(dict(P94, eps=0.5), rate, 2.0)

    def test_totals_sum_periods(self):
        one = nexp.totals({"y94": P94}, 0.3)
        two = nexp.totals({"y94": P94, "y95": P94}, 0.3)
        for rd in nexp.READINGS:
            self.assertAlmostEqual(two["readings"][rd]["n_t"], 2 * one["readings"][rd]["n_t"], places=9)
            self.assertAlmostEqual(two["readings"][rd]["n_u"], 2 * one["readings"][rd]["n_u"], places=9)
        self.assertAlmostEqual(one["readings"]["low"]["n_t"] / one["readings"]["nominal"]["n_t"],
                               1.9 / 2.2, places=12)
        with self.assertRaises(ValueError):
            nexp.totals({}, 0.3)

    def test_mu_low_from_nominal(self):
        self.assertAlmostEqual(nexp.mu_low_from_nominal(1.9 / 2.2), 1.0, places=12)
        self.assertLess(nexp.mu_low_from_nominal(0.85), 1.0)
        self.assertGreater(nexp.mu_low_from_nominal(0.87), 1.0)

    def test_combined_label(self):
        c = nexp.combined_label
        self.assertEqual(c("EXCLUDED", "EXCLUDED"), "EXCLUDED")
        self.assertEqual(c("EXCLUDED", "INCONCLUSIVE"), "INCONCLUSIVE")
        self.assertEqual(c("COMPATIBLE", "COMPATIBLE"), "COMPATIBLE")
        self.assertEqual(c("COMPATIBLE", "EXCLUDED"), "INCONCLUSIVE")
        with self.assertRaises(ValueError):
            c("EXCLUDED", "maybe")

    def test_old_v010_formula_bias(self):
        # same world, ALEPH constants as published: signal thrust-cut pass rate 0.85
        a_gen = 0.3
        rate = nexp.rate_per_z(a_gen)
        true_s = nexp.period_yields(P94, rate)["s_before_tag"]
        # v0.10 with sigana's efficiency WITHOUT the thrust cut: off by 1 / eff_had,A
        old_nothrust = nexp.old_v010_formula(a_gen, P94["n_had_data"], 0.35 / 0.85)
        self.assertAlmostEqual(old_nothrust / true_s, 1 / 0.9748, places=6)
        # v0.10 with an efficiency that includes the thrust cut: off by eff_had,D / eff_had,A
        old_thrust = nexp.old_v010_formula(a_gen, P94["n_had_data"], 0.35)
        self.assertAlmostEqual(old_thrust / true_s, 0.85 / 0.9748, places=6)

    def test_cli(self):
        d = tempfile.mkdtemp()
        inp, out = os.path.join(d, "in.json"), os.path.join(d, "out.json")
        with open(inp, "w") as fh:
            json.dump({"a_gen": 0.3, "periods": {"y94": P94}}, fh)
        self.assertEqual(nexp.main(["--inputs", inp, "--out", out]), 0)
        with open(out) as fh:
            r = json.load(fh)
        self.assertEqual(r["tool"], nexp.VERSION)
        self.assertEqual(set(r["readings"]), {"nominal", "low"})
        self.assertAlmostEqual(r["readings"]["low"]["n_t"] / r["readings"]["nominal"]["n_t"],
                               1.9 / 2.2, places=12)


if __name__ == "__main__":
    unittest.main()
