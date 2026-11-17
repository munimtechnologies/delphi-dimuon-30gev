"""Tests for eff4f (MV2 of Munim, Inc.; made with AI agents; Apache-2.0).
Hand-built events with known angles; lep4f and evana are optional (skipTest if absent)."""
import math
import unittest

import numpy as np

import eff4f


def part(E, theta_deg, phi_deg):
    t, f = math.radians(theta_deg), math.radians(phi_deg)
    return [E, E * math.sin(t) * math.cos(f), E * math.sin(t) * math.sin(f), E * math.cos(t)]


def event1(extra_pion=False):
    """muon 0 along +x (10 GeV); photon 0.4 GeV at 5 deg, pion 0.7 at 12, pion 5 at 40,
    neutrino 20 at 2 deg (invisible), muon 5 along -x (12 GeV)."""
    ids = [13, 22, 211, 211, 12, -13]
    ch = [-1, 0, 1, 1, 0, 1]
    p4 = [part(10, 90, 0), part(0.4, 90, 5), part(0.7, 90, 12), part(5, 90, 40),
          part(20, 90, 2), part(12, 90, 180)]
    if extra_pion:
        ids.append(-211)
        ch.append(-1)
        p4.append(part(1.0, 60, 90))
    return np.array(ids), np.array(p4, float), np.array(ch, float)


class Geometry(unittest.TestCase):
    def setUp(self):
        self.ids, self.p4, self.ch = event1()
        self.vis = eff4f.visible(self.ids)

    def test_visible_excludes_neutrino(self):
        self.assertEqual(self.vis.tolist(), [True, True, True, True, False, True])

    def test_iso_angle_energy(self):
        # cumulative 0.4 (5 deg), 1.1 (12 deg) -> reaches 1 GeV at 12 deg; neutrino ignored
        self.assertAlmostEqual(eff4f.iso_angle_energy(self.p4, self.vis, 0), 12.0, places=5)
        self.assertAlmostEqual(eff4f.iso_angle_energy(self.p4, self.vis, 0, emax=0.3), 5.0, places=5)
        self.assertAlmostEqual(eff4f.iso_angle_energy(self.p4, self.vis, 5), 140.0, places=5)
        self.assertEqual(eff4f.iso_angle_energy(self.p4, self.vis, 0, emax=100.0), 180.0)

    def test_iso_angle_nearest(self):
        self.assertAlmostEqual(eff4f.iso_angle_nearest(self.p4, self.vis, 0), 40.0, places=5)

    def test_cone_energy(self):
        self.assertAlmostEqual(eff4f.cone_energy(self.p4, self.vis, 0, 30.0), 1.1, places=9)
        self.assertAlmostEqual(eff4f.cone_energy(self.p4, self.vis, 0, 15.0, 3.0), 1.1, places=9)
        self.assertAlmostEqual(eff4f.cone_energy(self.p4, self.vis, 0, 10.0, 3.0), 0.4, places=9)
        self.assertEqual(eff4f.cone_energy(self.p4, self.vis, 5, 30.0), 0.0)

    def test_pair_mass(self):
        # back-to-back massless 10 and 12 GeV muons: m^2 = 2 * 10 * 12 * 2 = 480
        self.assertAlmostEqual(eff4f.pair_mass(self.p4[0] + self.p4[5]), math.sqrt(480.0), places=9)


class Selections(unittest.TestCase):
    def setUp(self):
        self.ids, self.p4, self.ch = event1()
        self.vis = eff4f.visible(self.ids)

    def test_opal(self):
        self.assertTrue(eff4f.sel_opal(self.p4, self.vis, 0, 5))           # alphas 12, 140
        self.assertFalse(eff4f.sel_opal(self.p4, self.vis, 0, 5, a_lo=30.0))
        self.assertTrue(eff4f.sel_opal(self.p4, self.vis, 0, 5, iso="nearest", a_lo=30.0))  # 40, 140
        self.assertFalse(eff4f.sel_opal(self.p4, self.vis, 0, 5, pmin=11.0))
        self.assertFalse(eff4f.sel_opal(self.p4, self.vis, 0, 5, psum=25.0))

    def test_aleph(self):
        self.assertFalse(eff4f.sel_aleph(self.p4, self.vis, 0, 5))          # 1.1 GeV in 30 deg
        self.assertTrue(eff4f.sel_aleph(self.p4, self.vis, 0, 5, emax=2.0))
        self.assertTrue(eff4f.sel_aleph(self.p4, self.vis, 0, 5, cone_deg=4.0))

    def test_l3(self):
        self.assertAlmostEqual(eff4f.l3_d(self.p4, self.vis, 0), 0.11, places=9)
        self.assertAlmostEqual(eff4f.l3_d(self.p4, self.vis, 5), 0.0, places=9)
        self.assertTrue(eff4f.sel_l3(self.p4, self.vis, 0, 5))
        # muons at 90 deg pass |cos| < cos 40; a tiny acceptance removes them
        self.assertFalse(eff4f.sel_l3(self.p4, self.vis, 0, 5, cmax=0.0))

    def test_l3_needs_one_isolated_muon(self):
        # put 3 GeV 8 deg from the second muon: D_min = 0.11 (muon 0), annulus min 1.1 -> fail
        ids, p4, ch = event1()
        ids = np.append(ids, 22)
        p4 = np.vstack([p4, part(3.0, 90, 172)])
        vis = eff4f.visible(ids)
        self.assertAlmostEqual(eff4f.l3_d(p4, vis, 5), 0.25, places=9)
        self.assertFalse(eff4f.sel_l3(p4, vis, 0, 5))
        self.assertTrue(eff4f.sel_l3(p4, vis, 0, 5, emax=1.2))


class Acceptance(unittest.TestCase):
    def test_acceptance(self):
        ids, p4, ch = event1()
        self.assertEqual(eff4f.n_charged(p4, ch), 4)
        self.assertFalse(eff4f.aleph_acceptance(ids, p4, ch, 0, 5))
        ids, p4, ch = event1(extra_pion=True)
        self.assertEqual(eff4f.n_charged(p4, ch), 5)
        self.assertTrue(eff4f.aleph_acceptance(ids, p4, ch, 0, 5))
        vis = eff4f.visible(ids)
        expect = np.linalg.norm(p4[vis, 1:].sum(0))
        self.assertAlmostEqual(eff4f.p_miss(ids, p4), expect, places=9)
        self.assertLess(eff4f.p_miss(ids, p4), 18.0)

    def test_agrees_with_evana(self):
        try:
            import evana
        except ImportError:
            self.skipTest("evana (xkin) not available")
        rng = np.random.default_rng(3)
        n = 40
        E = rng.uniform(0.1, 8.0, n)
        th = np.degrees(np.arccos(rng.uniform(-1, 1, n)))
        ph = rng.uniform(0, 360, n)
        p4 = np.array([part(E[k], th[k], ph[k]) for k in range(n)])
        ids = rng.choice([211, -211, 22, 130, 12, 13, -13], n)
        ch = np.array([{211: 1, -211: -1, 13: -1, -13: 1}.get(int(x), 0) for x in ids], float)
        q = evana.event_quantities(ids, p4, ch)
        self.assertEqual(eff4f.n_charged(p4, ch), q["nch"])
        self.assertAlmostEqual(eff4f.p_miss(ids, p4), q["pmiss"], places=9)
        for k in range(n):
            mu = {"p": float(q["pabs"][k]), "pt": 0.0, "cth": float(q["cth"][k])}
            self.assertEqual(evana.muon_pass(mu), bool(eff4f.pabs(p4)[k] > 2.5 and
                                                       abs(eff4f.costh(p4)[k]) < 0.95))


class Bookkeeping(unittest.TestCase):
    def test_evaluate_and_counts(self):
        ids, p4, ch = event1(extra_pion=True)
        r = eff4f.evaluate(ids, p4, ch, 0, 5)
        self.assertTrue(r["in_window"])          # m = sqrt(480) = 21.9 GeV
        c = eff4f.new_counts()
        eff4f.accumulate(c, r)
        self.assertEqual(c["n_pairs"], 1)
        self.assertEqual(c["n_acc"], 1)
        self.assertEqual(c["pass_acc_win"]["OPAL:nominal"], 1)
        self.assertEqual(c["pass_acc_win"]["ALEPH:nominal"], 0)
        self.assertAlmostEqual(r["opal_alpha_lo"], 12.0, places=5)
        e, de = eff4f.eps_kin(c, "OPAL:nominal")
        self.assertEqual((e, de), (1.0, 0.0))
        m = eff4f.merge(c, eff4f.new_counts())
        self.assertEqual(m["n_acc"], 1)
        self.assertEqual(set(eff4f.KEYS), set(c["pass_acc_win"]))

    def test_window_bookkeeping(self):
        c = eff4f.new_counts()
        base = {k: True for k in eff4f.KEYS}
        eff4f.accumulate(c, dict(base, m=30.0, in_window=True, acc=True))
        eff4f.accumulate(c, dict(base, m=45.0, in_window=False, acc=True))
        eff4f.accumulate(c, dict(base, m=30.0, in_window=True, acc=False))
        self.assertEqual(c["n_acc"], 2)
        self.assertEqual(c["pass_acc_win"]["L3:nominal"], 1)
        self.assertEqual(c["pass_win_any"]["L3:nominal"], 2)
        e, de = eff4f.eps_kin(c, "L3:nominal")
        self.assertAlmostEqual(e, 0.5)
        self.assertAlmostEqual(de, 0.5 / math.sqrt(2.0))


class Statistics(unittest.TestCase):
    def test_bw_fraction(self):
        self.assertAlmostEqual(eff4f.bw_fraction(0.0, float("inf")), 1.0, places=12)
        f = eff4f.bw_fraction(22.0, 40.0)
        self.assertGreater(f, 0.948)
        self.assertLess(f, 0.958)

    def test_z_of(self):
        self.assertAlmostEqual(eff4f.z_of(0.5 * math.erfc(3.0 / math.sqrt(2.0))), 3.0, places=6)
        self.assertEqual(eff4f.z_of(0.0), 37.0)
        self.assertEqual(eff4f.z_of(0.7), 0.0)

    def test_predict_and_confront(self):
        try:
            import lep4f
        except ImportError:
            self.skipTest("lep4f not available")
        pr = eff4f.predict("OPAL", 1.0, id_eff=1.0)
        want = lep4f.rate_acc("nominal") * lep4f.EXPTS["OPAL"]["n_z"] * eff4f.bw_fraction(22.0, 40.0)
        self.assertAlmostEqual(pr, want, places=6)
        self.assertAlmostEqual(eff4f.predict("OPAL", 0.5), 0.5 * 0.86 ** 2 * want, places=6)
        r = eff4f.confront(["L3"], {"L3": 0.5})
        self.assertEqual(r["n_obs"], 0)
        self.assertAlmostEqual(r["s_up_95"], math.log(20.0), places=4)
        self.assertAlmostEqual(r["p_value"], math.exp(-r["pred"]), places=12)
        r2 = eff4f.confront(["OPAL", "L3"], {"OPAL": 0.5, "L3": 0.5})
        self.assertEqual(r2["n_obs"], 1)
        self.assertAlmostEqual(r2["s_up_95"], 4.744, places=2)


if __name__ == "__main__":
    unittest.main()
