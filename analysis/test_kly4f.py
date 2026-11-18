"""Unit tests for run_kly4f (no event generation). MV2 of Munim, Inc. Made with AI agents. Apache-2.0."""
import unittest

import eff4f
import run_kly4f as r


class TestKly4f(unittest.TestCase):
    def test_weakest_picks_minimum_of_one_experiment(self):
        eps = {"OPAL:nominal": 0.8, "OPAL:both_30deg": 0.5, "L3:nominal": 0.3, "L3:jet40": 0.6}
        self.assertEqual(r.weakest(eps, "OPAL"), ("both_30deg", 0.5))
        self.assertEqual(r.weakest(eps, "L3"), ("nominal", 0.3))

    def test_every_eff4f_experiment_has_window_counts(self):
        for e in r.EXPTS:
            self.assertIn(e, eff4f.WINDOW_OBS)
            self.assertIn("%s:nominal" % e, eff4f.KEYS)

    def test_confrontations_keys_and_monotonic(self):
        lo = r.confrontations({"OPAL": 0.1, "L3": 0.1, "ALEPH": 0.1}, {"OPAL": 0.05, "L3": 0.05, "ALEPH": 0.05})
        hi = r.confrontations({"OPAL": 0.8, "L3": 0.6, "ALEPH": 0.6}, {"OPAL": 0.5, "L3": 0.4, "ALEPH": 0.4})
        self.assertEqual(len(lo), 12)
        for k in lo:
            self.assertGreater(hi[k]["pred"], lo[k]["pred"])
            self.assertLessEqual(hi[k]["p_value"], lo[k]["p_value"])
        # OPAL + L3 count in 20-40 GeV is 1 (OPAL Fig. 3b) + 0 (L3 Fig. 7a)
        self.assertEqual(hi["OPAL+L3|nominal|central"]["n_obs"], 1)
        # the lowest literature rate predicts fewer events than the central rate
        self.assertLess(hi["OPAL+L3|nominal|lit1.1e-5"]["pred"], hi["OPAL+L3|nominal|central"]["pred"])

    def test_closure_table_covers_models(self):
        import kly
        self.assertEqual(set(r.KLY_V1), set(kly.MODELS))


if __name__ == "__main__":
    unittest.main()
