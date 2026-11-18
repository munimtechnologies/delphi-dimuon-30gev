"""Unit tests for lephz (MV2 of Munim, Inc.; made with AI agents; Apache-2.0).
Needs efhz.py, eff4f.py, evana.py and lep4f.py next to it (the job fetches them from the public
repo)."""
import math
import unittest

import numpy as np

import efhz
import eff4f
import lep4f
import lephz

MMU, MPI = 0.10566, 0.13957
JET = ((0.1, 1.0, 0.0), (-0.1, 1.0, 0.0), (0.0, 1.0, 0.1), (0.0, 1.0, -0.1))


def sph(th_deg, ph_deg):
    t, p = math.radians(th_deg), math.radians(ph_deg)
    return (math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t))


def part(pid, p, d, q, m):
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    return pid, [math.sqrt(p * p + m * m)] + list(p * d), q


def build(muons=None, extra=(), neutrinos=False):
    """As test_efhz.build: two back-to-back 15 GeV muons at theta 60 / 120 deg in the x-z plane
    (m_mumu = 30 GeV), two 4-pion jets along +-y (7.65 GeV each), total momentum zero."""
    rows = muons or [part(13, 15.0, sph(60, 0), -1.0, MMU), part(-13, 15.0, sph(120, 180), 1.0, MMU)]
    rows = list(rows)
    for s in (1.0, -1.0):
        for k, d in enumerate(JET):
            dd = tuple(s * x for x in d)
            if neutrinos and k in (1, 3):
                rows.append(part(14, 7.65, dd, 0.0, 0.0))
            else:
                q = 1.0 if k % 2 == 0 else -1.0
                rows.append(part(int(211 * q), 7.65, dd, q, MPI))
    rows += list(extra)
    ids = np.array([r[0] for r in rows])
    p4 = np.array([r[1] for r in rows], float)
    ch = np.array([r[2] for r in rows], float)
    return ids, p4, ch


def gamma(e, th, ph):
    return part(22, e, sph(th, ph), 0.0, 0.0)


class TestSelections(unittest.TestCase):
    def test_base_event_passes_all_four(self):
        ids, p4, ch = build()
        r = lephz.evaluate(ids, p4, ch, 0, 1)
        self.assertTrue(r["acc"] and r["in_window"])
        for k in lephz.KEYS:
            self.assertIsInstance(r[k], bool, k)
        for s in lephz.ALL_SET:
            self.assertTrue(r["%s:nominal" % s], s)
        ctx = lephz.make_ctx(ids, p4, ch)
        self.assertTrue(0.66 < ctx["thrust"] < 0.75, ctx["thrust"])   # max 67.9 / 91.2 = 0.744
        # ALEPH96 is efhz's nominal selection (one definition, imported)
        self.assertEqual(r["ALEPH96:nominal"], efhz.select(efhz.make_ctx(ids, p4, ch), 0, 1))

    def test_l3_calorimeter_isolation(self):
        ids, p4, ch = build(extra=[gamma(10.0, 50, 0)])            # 10 GeV, 10 deg from muon 0
        f = lephz.l3_flags(lephz.make_ctx(ids, p4, ch), 0, 1)
        self.assertFalse(f["hcl"])                                  # 10 GeV > 4 GeV
        self.assertTrue(all(v for k, v in f.items() if k != "hcl"), f)
        ids, p4, ch = build(extra=[gamma(2.0, 50, 0)])             # 2 GeV: < 4, product 0
        self.assertTrue(lephz.sel_l3(lephz.make_ctx(ids, p4, ch), 0, 1))
        ids, p4, ch = build(extra=[gamma(2.0, 50, 0), gamma(2.0, 130, 180)])   # one near each
        f = lephz.l3_flags(lephz.make_ctx(ids, p4, ch), 0, 1)
        self.assertFalse(f["hcl"])                                  # product 4 GeV^2 > 1
        self.assertFalse(f["bgo"])                                  # smaller BGO sum 2 GeV > 0.2
        self.assertTrue(f["d"])                                     # D = 0.133 each

    def test_l3_d_product(self):
        for e, want in ((9.0, False), (6.0, True)):                # D = 0.6 / 0.4 for each muon
            ids, p4, ch = build(extra=[gamma(e, 50, 0), gamma(e, 130, 180)])
            ctx = lephz.make_ctx(ids, p4, ch)
            f = lephz.l3_flags(ctx, 0, 1, bgo=None, hcl=None)
            self.assertEqual(f["d"], want, e)
            self.assertEqual(lephz.sel_l3(ctx, 0, 1, bgo=None, hcl=None), want, e)

    def test_l3_has_no_recoil_cut(self):
        # two 25 GeV muons at |cos| = 0.6, m = 30 GeV, recoil ~ 9.9 GeV for sqrt(s) = 91.2
        mu = [part(13, 25.0, (0.8, 0.0, -0.6), -1.0, MMU), part(-13, 25.0, (0.8, 0.0, 0.6), 1.0, MMU)]
        ids, p4, ch = build(muons=mu)
        r = lephz.evaluate(ids, p4, ch, 0, 1, sqrt_s=91.2)
        self.assertLess(r["recoil"], 15.0)
        self.assertTrue(r["in_window"])
        self.assertTrue(r["L3_96:nominal"])
        self.assertFalse(r["ALEPH96:nominal"])        # recoil > 40 GeV
        self.assertFalse(r["DELPHI94:nominal"])       # recoil > 15 GeV
        self.assertFalse(r["OPAL97:nominal"])         # recoil > 25 GeV (stand-in)
        self.assertFalse(r["cut_DELPHI94_recoil"])
        self.assertTrue(r["cut_DELPHI94_iso"])

    def test_l3_multiplicity_and_thrust(self):
        ids, p4, ch = build(neutrinos=True)                         # 4 pions left: 4 clusters
        ctx = lephz.make_ctx(ids, p4, ch)
        self.assertFalse(lephz.l3_flags(ctx, 0, 1)["mult"])
        self.assertTrue(lephz.l3_flags(ctx, 0, 1, nclu_min=4)["mult"])
        ids, p4, ch = build()
        ctx = lephz.make_ctx(ids, p4, ch)
        self.assertFalse(lephz.l3_flags(ctx, 0, 1, thrust_max=0.6)["thrust"])
        self.assertTrue(lephz.l3_flags(ctx, 0, 1, thrust_max=None)["thrust"])
        self.assertFalse(lephz.l3_flags(ctx, 0, 1, cmax=0.4)["p"])   # |cos| = 0.5
        self.assertFalse(lephz.l3_flags(ctx, 0, 1, psum=31.0)["p"])

    def test_delphi_cuts(self):
        ids, p4, ch = build()
        ctx = lephz.make_ctx(ids, p4, ch)
        f = lephz.delphi_flags(ctx, 0, 1)
        self.assertTrue(all(f.values()), f)
        self.assertEqual(len(lephz.rest_jets(ctx, 0, 1, 0.02)), 2)
        self.assertAlmostEqual(lephz.nearest_jet_angle(p4, 0, lephz.rest_jets(ctx, 0, 1, 0.02)), 90.0, places=6)
        self.assertFalse(lephz.delphi_flags(ctx, 0, 1, iso_hard=95.0)["iso"])
        self.assertFalse(lephz.delphi_flags(ctx, 0, 1, recoil_min=70.0)["recoil"])
        self.assertFalse(lephz.delphi_flags(ctx, 0, 1, ycut=2.0)["jets"])      # y = 1.0 merges
        self.assertFalse(lephz.delphi_flags(ctx, 0, 1, phard_min=16.0)["p"])
        mu = [part(13, 15.0, sph(77.5, 0), -1.0, MMU), part(-13, 15.0, sph(102.5, 0), 1.0, MMU)]
        ids, p4, ch = build(muons=mu)
        self.assertAlmostEqual(lephz.opening_deg(p4, 0, 1), 25.0, places=6)
        self.assertFalse(lephz.delphi_flags(lephz.make_ctx(ids, p4, ch), 0, 1)["open"])

    def test_delphi_isolation_rules(self):
        # muon 1 (the softer, 8 GeV) at 30 deg from the +y jet axis: passes "hard" (> 20 deg) and
        # fails "both" (> 40 deg)
        mu = [part(13, 15.0, sph(60, 0), -1.0, MMU), part(-13, 8.0, (0.0, math.cos(math.radians(30)),
                                                                      math.sin(math.radians(30))), 1.0, MMU)]
        ids, p4, ch = build(muons=mu)
        ctx = lephz.make_ctx(ids, p4, ch)
        jets = lephz.rest_jets(ctx, 0, 1, 0.02)
        self.assertAlmostEqual(lephz.nearest_jet_angle(p4, 1, jets), 30.0, places=6)
        self.assertTrue(lephz.delphi_flags(ctx, 0, 1)["iso"])
        self.assertFalse(lephz.delphi_flags(ctx, 0, 1, iso_rule="both")["iso"])
        self.assertFalse(lephz.delphi_flags(ctx, 0, 1, iso_soft=35.0)["iso"])

    def test_durham_agrees_with_eff4f(self):
        rng = np.random.default_rng(7)
        d = eff4f.unit(rng.normal(size=(15, 3)))
        e = rng.uniform(0.5, 10.0, 15)
        p = np.column_stack([e, d * e[:, None]])
        for y in (0.001, 0.005, 0.02, 0.1, 2.0):
            jets = lephz.durham_jets(p, y)
            self.assertEqual(len(jets), eff4f.durham_njets(p, y), y)
            self.assertAlmostEqual(float(jets[:, 0].sum()), float(e.sum()), places=9)
            self.assertTrue(np.all(np.diff(jets[:, 0]) <= 1e-12))

    def test_opal_cuts(self):
        ids, p4, ch = build()
        ctx = lephz.make_ctx(ids, p4, ch)
        self.assertTrue(all(lephz.opal_flags(ctx, 0, 1).values()))
        self.assertFalse(lephz.opal_flags(ctx, 0, 1, pmax=14.0)["p"])
        self.assertFalse(lephz.opal_flags(ctx, 0, 1, recoil_min=62.0)["recoil"])   # recoil 61.2
        ids, p4, ch = build(neutrinos=True)                         # E_vis = 91.2 - 30.6 = 60.6
        self.assertFalse(lephz.opal_flags(lephz.make_ctx(ids, p4, ch), 0, 1)["evis"])


class TestCandidates(unittest.TestCase):
    def test_compatibility(self):
        self.assertEqual([lephz.compatible(c) for c in lephz.SEARCHES["ALEPH96"]["candidates"]],
                         [True, True, False])                       # 66.9 > 91.19 - 26
        self.assertEqual([lephz.compatible(c) for c in lephz.SEARCHES["DELPHI94"]["candidates"]], [True])
        self.assertEqual([lephz.compatible(c) for c in lephz.SEARCHES["OPAL97"]["candidates"]], [False])
        self.assertAlmostEqual(lephz.mll_from_recoil(61.2, 19.3, 7.3), 16.77, delta=0.05)
        self.assertEqual(sum(lephz.n_obs(s) for s in lephz.NOMINAL_SET), 3)
        self.assertEqual(sum(lephz.n_obs(s, "all") for s in lephz.ALL_SET), 5)
        self.assertEqual(lephz.n_obs("L3_96", "all"), 0)

    def test_mll_from_recoil_matches_event(self):
        ids, p4, ch = build()
        s = float(p4[:, 0].sum())
        rec = efhz.recoil_mass(p4, 0, 1, s)
        p = eff4f.pabs(p4)
        self.assertAlmostEqual(lephz.mll_from_recoil(rec, p[0], p[1], s),
                               eff4f.pair_mass(p4[0] + p4[1]), delta=0.01)


class TestConfront(unittest.TestCase):
    def test_predictions(self):
        one = efhz.predict_rate(1.0)
        self.assertAlmostEqual(lephz.predict("ALEPH96", 1.0), 0.8 * one, places=9)
        self.assertAlmostEqual(lephz.predict("ALEPH96", 1.0, btag=1.0), one, places=9)
        self.assertAlmostEqual(lephz.predict("L3_96", 1.0) / one, 3.05 / 4.5, places=9)
        self.assertTrue(30.0 < lephz.predict("DELPHI94", 1.0) < 50.0)
        self.assertAlmostEqual(lephz.predict("L3_96", 0.25), 0.25 * lephz.predict("L3_96", 1.0), places=9)

    def test_combine(self):
        zero = {s: 0.0 for s in lephz.ALL_SET}
        r = lephz.combine(zero)
        self.assertEqual(r["n_obs"], 3)
        self.assertEqual(r["p"], 1.0)
        self.assertEqual(r["mu_max"], float("inf"))
        self.assertTrue(7.0 < r["s_up_95"] < 8.5, r["s_up_95"])
        e = {s: 0.3 for s in lephz.ALL_SET}
        r = lephz.combine(e)
        want = sum(lephz.predict(s, 0.3) for s in lephz.NOMINAL_SET)
        self.assertAlmostEqual(r["pred"], want, places=9)
        self.assertLess(r["p"], 1e-20)
        self.assertEqual(lephz.combine(e, rule="all")["n_obs"], 4)
        self.assertEqual(lephz.combine(e, lephz.ALL_SET, rule="all")["n_obs"], 5)
        self.assertLess(lephz.combine(e)["p"], lephz.combine(e, reading="low")["p"])
        c = lephz.confront_all(e)
        for k in ("nominal3|compatible|central", "nominal3|all|lit1.1e-5", "L3+DELPHI|compatible|central",
                  "L3_96|compatible|low-1sigma", "all4|all|central"):
            self.assertIn(k, c)
            self.assertTrue(0.0 <= c[k]["p"] <= 1.0)
        self.assertGreater(c["nominal3|compatible|lit1.1e-5"]["p"], c["nominal3|compatible|central"]["p"])


class TestCounting(unittest.TestCase):
    def test_accumulate_and_eps(self):
        c = lephz.new_counts()
        ids, p4, ch = build()
        lephz.accumulate(c, lephz.evaluate(ids, p4, ch, 0, 1))
        ids, p4, ch = build(extra=[gamma(2.0, 50, 0), gamma(2.0, 130, 180)])
        r = lephz.evaluate(ids, p4, ch, 0, 1)
        self.assertTrue(r["acc"] and r["in_window"])
        lephz.accumulate(c, r)
        self.assertEqual((c["n_pairs"], c["n_acc"], c["n_acc_win"]), (2, 2, 2))
        self.assertEqual(c["pass"]["L3_96:nominal"], 1)
        self.assertEqual(c["cut"]["cut_L3_96_hcl"], 1)
        self.assertEqual(c["cut"]["cut_L3_96_d"], 2)
        e, err = lephz.eps(c, "L3_96:nominal")
        self.assertAlmostEqual(e, 0.5)
        self.assertAlmostEqual(err, math.sqrt(0.25 / 2))


if __name__ == "__main__":
    unittest.main()
