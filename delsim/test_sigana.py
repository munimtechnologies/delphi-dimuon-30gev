"""Tests for sigana (MV2 of Munim, Inc.; made with AI agents; Apache-2.0)."""
import math
import os
import tempfile
import unittest

import numpy as np

import fadgen
import sigana


def lorentz(px, py, pz, m):
    return (px, py, pz, math.sqrt(px * px + py * py + pz * pz + m * m), m)


def make_record(mu1, mu2, xid=32, extra_charged=6):
    """beams(1,2), Z(3), b(4), bbar(5), X(6), mu-(7), mu+(8), FSR copy of mu- (9) final,
    plus extra charged pions and one neutrino."""
    rows = []
    rows.append(((21, 11, 0, 0, 0), lorentz(0, 0, 45.6, 0)))
    rows.append(((21, -11, 0, 0, 0), lorentz(0, 0, -45.6, 0)))
    rows.append(((21, 23, 1, 4, 6), (0, 0, 0, 91.19, 91.19)))
    rows.append(((21, 5, 3, 0, 0), lorentz(10, 0, 0, 4.8)))
    rows.append(((21, -5, 3, 0, 0), lorentz(-10, 0, 0, 4.8)))
    xp = [mu1[i] + mu2[i] for i in range(3)]
    rows.append(((21, xid, 3, 7, 8), lorentz(*xp, 30.4)))
    rows.append(((21, 13, 6, 9, 9), lorentz(*mu1, sigana.MMU)))
    rows.append(((1, -13, 6, 0, 0), lorentz(*mu2, sigana.MMU)))
    rows.append(((1, 13, 7, 0, 0), lorentz(*mu1, sigana.MMU)))
    for k in range(extra_charged):
        rows.append(((1, 211 if k % 2 else -211, 4, 0, 0), lorentz(1.0 + k, 0.5, 0.2, 0.1396)))
    rows.append(((1, 14, 4, 0, 0), lorentz(0, 3.0, 0, 0)))
    K = np.array([r[0] for r in rows], np.int32)
    P = np.array([r[1] for r in rows], np.float32)
    V = np.zeros((len(rows), 5), np.float32)
    return K, P, V


def track(run, evt, i, q, px, py, pz, kmu1=4):
    return {"run": run, "evt": evt, "i": i, "q": q, "lock": 0, "kmu1": kmu1, "kmu3": 0,
            "kel1": 0, "kel2": 0, "vdrphi": 2, "vdz": 1, "px": px, "py": py, "pz": pz,
            "e": math.sqrt(px * px + py * py + pz * pz), "mchi2": 1.0, "qt4": 0.0, "qt5": 0.0,
            "d0": 0.002, "z0": 0.003, "d0bs": 0.004,
            "p": math.sqrt(px * px + py * py + pz * pz)}


def e_line(run, evt, ihad4=1, nctr4=10, btp3=0.005):
    d = {k: 0 for k in sigana.E_FIELDS}
    d.update(run=run, evt=evt, ihad4=ihad4, nctr4=nctr4, btp3=btp3)
    return d


class TestTruth(unittest.TestCase):
    def test_signal_muons_through_fsr_copy(self):
        K, P, V = make_record((5.0, 12.0, 3.0), (-4.0, -10.0, 1.0))
        t = sigana.truth_from_record(K, P)
        self.assertEqual(len(t["mus"]), 2)
        self.assertEqual(sorted(m["q"] for m in t["mus"]), [-1, 1])
        self.assertAlmostEqual(t["m_x"], 30.4, places=3)
        self.assertEqual(t["nch"], 2 + 6)
        self.assertGreater(t["pmiss_vis"], 0)

    def test_background_muon_not_signal(self):
        K, P, V = make_record((5.0, 12.0, 3.0), (-4.0, -10.0, 1.0), xid=511)
        self.assertEqual(len(sigana.truth_from_record(K, P)["mus"]), 0)

    def test_fadgen_roundtrip(self):
        d = tempfile.mkdtemp()
        path = os.path.join(d, "x.fort26")
        with open(path, "wb") as f:
            for k in range(3):
                fadgen.write_event(f, *make_record((5.0 + k, 12.0, 3.0), (-4.0, -10.0, 1.0)))
            fadgen.write_end(f)
        tr = sigana.read_truth(path)
        self.assertEqual(len(tr), 3)
        self.assertTrue(all(len(t["mus"]) == 2 for t in tr))


class TestParse(unittest.TestCase):
    def test_parse_lines_from_fortran_format(self):
        e = ("E" + "".join(" %10d" % v for v in (-1001, 7, 3, 12, 14, 40, 2))
             + "".join(" %13.5E" % v for v in [91.2, 50.0, 20.0, 10.0] + [0.5] * 9 + [0.1, 0.2, 0.97, 0.9]))
        d = sigana.parse_e(e)
        self.assertEqual(d["run"], -1001)
        self.assertEqual(d["evt"], 7)
        self.assertAlmostEqual(d["thr"], 0.9, places=5)
        p = ("P" + "".join(" %11d" % v for v in (-1001, 7, 3, -1, 0, 5, 0, 0, 0, 2, 1))
             + "".join(" %13.5E" % v for v in (3.0, 4.0, 0.0, 5.0, 1.2, 0, 0, 0.01, 0.02, 0.03)))
        q = sigana.parse_p(p)
        self.assertEqual(q["q"], -1)
        self.assertAlmostEqual(q["p"], 5.0, places=4)
        self.assertTrue(sigana.is_muon(q, "standard"))
        self.assertIsNone(sigana.parse_p("P 1 2 3"))


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.truth = []
        for k in range(6):
            K, P, V = make_record((5.0 + k, 12.0, 3.0), (-4.0, -10.0 - k, 1.0))
            self.truth.append(sigana.truth_from_record(K, P))

    def reco_for(self, j, evt, smear=1.01):
        tr = self.truth[j]
        tracks = []
        for i, mu in enumerate(tr["mus"]):
            tracks.append(track(-1001, evt, i + 1, mu["q"], mu["px"] * smear, mu["py"] * smear, mu["pz"] * smear))
        tracks.append(track(-1001, evt, 9, 1, 0.5, 0.5, 0.1, kmu1=0))
        return {"e": e_line(-1001, evt), "tracks": tracks}

    def test_match_and_mass(self):
        ev = self.reco_for(0, 1)
        m = sigana.match_muons(self.truth[0], ev["tracks"])
        self.assertTrue(all(x is not None for x in m))
        mt = sigana.pair_mass(*self.truth[0]["mus"])
        mr = sigana.pair_mass(m[0], m[1])
        self.assertAlmostEqual(mr / mt, 1.01, places=3)

    def test_align_with_dropped_event(self):
        reco = [self.reco_for(0, 1), self.reco_for(1, 2), self.reco_for(3, 3), self.reco_for(4, 4)]
        self.assertEqual(sigana.align(reco, self.truth), [0, 1, 3, 4])

    def test_analyse_counts(self):
        reco = [self.reco_for(j, j + 1) for j in range(6)]
        r = sigana.analyse(reco, self.truth, 6)
        self.assertEqual(r["n_aligned"], 6)
        self.assertEqual(r["mass_resolution"]["n_pairs"], 6)
        self.assertAlmostEqual(r["muon_level"]["eff_track"], 1.0)
        self.assertAlmostEqual(r["muon_level"]["eff_track_all"], 1.0)
        self.assertGreater(r["mass_resolution"]["median_dm"], 0)
        self.assertEqual(r["selection_counts"]["aligned"], 6)
        self.assertEqual(r["selection_counts"]["truth_pair_selected"],
                         r["selection_counts"]["pmiss_lt18"])
        self.assertEqual(r["btag_eff_after_selection"]["0.01"], 1.0)
        self.assertTrue(r["delsim_used_input"])

    def test_wrong_charge_not_matched(self):
        ev = self.reco_for(0, 1)
        for t in ev["tracks"]:
            t["q"] = -t["q"]
        m = sigana.match_muons(self.truth[0], ev["tracks"][:2])
        self.assertTrue(all(x is None for x in m))

    # ---- 0.2.0
    def test_eff_track_all_counts_lost_events(self):
        # events 2 and 5 never reconstructed: 4 aligned events x 2 muons found, 6 x 2 in acceptance
        reco = [self.reco_for(0, 1), self.reco_for(1, 2), self.reco_for(3, 3), self.reco_for(4, 4)]
        r = sigana.analyse(reco, self.truth, 6)
        mu = r["muon_level"]
        self.assertEqual(mu["n_truth_mu_in_acc_all_simulated"], 12)
        self.assertAlmostEqual(mu["eff_track"], 1.0)
        self.assertAlmostEqual(mu["eff_track_all"], round(8 / 12, 4))

    def test_eff_track_all_respects_nsim(self):
        # only the first 4 generated events were simulated; event 4 aligned but beyond nsim
        reco = [self.reco_for(0, 1), self.reco_for(1, 2), self.reco_for(3, 3), self.reco_for(4, 4)]
        r = sigana.analyse(reco, self.truth, 4)
        mu = r["muon_level"]
        self.assertEqual(mu["n_truth_mu_in_acc_all_simulated"], 8)
        self.assertAlmostEqual(mu["eff_track_all"], round(6 / 8, 4))

    def test_hemi_tag_matches_dimusel_rule(self):
        reco = [self.reco_for(j, j + 1) for j in range(4)]
        hem = [(0.002, 0.5), (0.5, 0.02), (-1.0, 0.5), (0.5, 0.5)]
        for ev, (h1, h2) in zip(reco, hem):
            ev["e"]["btp1"], ev["e"]["btp2"] = h1, h2
        r = sigana.analyse(reco, self.truth, 4)
        self.assertEqual(r["selection_counts"]["pmiss_lt18"], 4)
        h = r["hemi_btag_after_selection"]
        self.assertEqual(h["n_selected"], 4)
        self.assertEqual(h["n_valid_hemispheres"], 7)
        self.assertEqual(h["n_selected_no_valid_hemisphere"], 0)
        self.assertAlmostEqual(h["event_tag_eff"]["0.001"], 0.0)
        self.assertAlmostEqual(h["event_tag_eff"]["0.003"], 0.25)
        self.assertAlmostEqual(h["event_tag_eff"]["0.03"], 0.5)
        self.assertAlmostEqual(h["event_tag_eff"]["0.3"], 0.5)
        self.assertAlmostEqual(h["event_tag_eff_err"]["0.03"], 0.25)
        self.assertAlmostEqual(h["per_hemisphere_tag_eff"]["0.03"], round(2 / 7, 4))
        self.assertEqual(set(h["event_tag_eff"]), {str(w) for w in sigana.HEMI_WP})

    def test_hemi_thrust_sample_for_rho_d(self):
        reco = [self.reco_for(j, j + 1) for j in range(4)]
        hem = [(0.002, 0.5), (0.5, 0.02), (-1.0, 0.5), (0.5, 0.5)]
        axes = [(1.0, 0.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0)]
        for ev, (h1, h2), (x, y, z) in zip(reco, hem, axes):
            ev["e"].update(btp1=h1, btp2=h2, thx=x, thy=y, thz=z)
        r = sigana.analyse(reco, self.truth, 4)
        h = r["hemi_btag_after_selection_thrust"]
        self.assertEqual(h["n_selected"], 2)
        self.assertEqual(h["n_valid_hemispheres"], 4)
        self.assertAlmostEqual(h["event_tag_eff"]["0.003"], 0.5)
        self.assertAlmostEqual(h["event_tag_eff"]["0.03"], 1.0)
        self.assertEqual(r["hemi_btag_after_selection"]["n_selected"], 4)

    def test_thrust_cut_matches_dimusel(self):
        try:
            import dimusel
        except ImportError:
            self.skipTest("analysis/dimusel.py not on the path")
        self.assertAlmostEqual(sigana.THRUST_COS_MAX, dimusel.DEFAULTS["thrust_cos_max"])
        self.assertFalse(sigana.thrust_ok({"thx": 0.0, "thy": 0.0, "thz": 0.0}))
        self.assertFalse(sigana.thrust_ok({"thx": 0.1, "thy": 0.0, "thz": 1.0}))
        self.assertTrue(sigana.thrust_ok({"thx": 0.0, "thy": 1.0, "thz": 0.5}))

    def test_hemi_no_valid_hemisphere_is_untagged(self):
        e = {"btp1": -1.0, "btp2": 2.0}
        self.assertFalse(sigana.hemi_tagged(e, 0.3))
        s = sigana.hemi_tag_summary([e])
        self.assertEqual(s["n_selected_no_valid_hemisphere"], 1)
        self.assertEqual(s["n_valid_hemispheres"], 0)
        self.assertIsNone(s["per_hemisphere_tag_eff"]["0.3"])
        self.assertEqual(s["event_tag_eff"]["0.3"], 0.0)

    def test_hemi_grid_matches_btagcal(self):
        try:
            import btagcal
        except ImportError:
            self.skipTest("analysis/btagcal.py not on the path")
        self.assertEqual(tuple(sigana.HEMI_WP), tuple(btagcal.WPS))

    def test_rho_d(self):
        self.assertAlmostEqual(sigana.rho_d(0.30, 0.40), 0.75)
        self.assertIsNone(sigana.rho_d(None, 0.4))
        self.assertIsNone(sigana.rho_d(0.3, 0.0))


if __name__ == "__main__":
    unittest.main()
