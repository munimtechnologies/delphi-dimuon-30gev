"""Unit tests for efhz (MV2 of Munim, Inc.; made with AI agents; Apache-2.0).
Needs eff4f.py, evana.py and lep4f.py next to it (the job fetches them from the public repo)."""
import math
import unittest

import numpy as np

import efhz
import eff4f
import lep4f

MMU, MPI, MN = 0.10566, 0.13957, 0.93957
JET = ((0.1, 1.0, 0.0), (-0.1, 1.0, 0.0), (0.0, 1.0, 0.1), (0.0, 1.0, -0.1))


def sph(th_deg, ph_deg):
    t, p = math.radians(th_deg), math.radians(ph_deg)
    return (math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t))


def part(pid, p, d, q, m):
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    return pid, [math.sqrt(p * p + m * m)] + list(p * d), q


def build(muons=None, extra=(), neutrinos=False):
    """Two back-to-back 15 GeV muons in the x-z plane (m_mumu = 30 GeV), two 4-pion jets along +-y
    (7.65 GeV each), total momentum zero. `neutrinos` turns two pions per jet into neutrinos."""
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


class TestEvent(unittest.TestCase):
    def test_base_event_passes_every_cut(self):
        ids, p4, ch = build()
        self.assertLess(np.linalg.norm(p4[:, 1:].sum(0)), 1e-9)
        ctx = efhz.make_ctx(ids, p4, ch)
        self.assertEqual(ctx["nch"], 10)
        f = efhz.cut_flags(ctx, 0, 1)
        self.assertTrue(all(f.values()), f)
        r = efhz.evaluate(ids, p4, ch, 0, 1)
        self.assertTrue(r["acc"] and r["in_window"])
        self.assertEqual(r["n_iso"], 2)
        for k in efhz.KEYS:
            self.assertIn(k, r)
            self.assertIsInstance(r[k], bool)
        self.assertTrue(r["nominal"] and r["both_iso"] and r["strict"])

    def test_recoil_back_to_back(self):
        ids, p4, ch = build()
        s = float(p4[:, 0].sum())
        e_ll = p4[0, 0] + p4[1, 0]
        self.assertAlmostEqual(efhz.recoil_mass(p4, 0, 1, s), s - e_ll, places=6)
        self.assertGreater(efhz.recoil_mass(p4, 0, 1, s), 60.0)

    def test_recoil_cut_alone_rejects_energetic_pair(self):
        # two 25 GeV muons, opening angle with cos = 0.28 -> m ~ 30 GeV, |p_ll| = 40 GeV
        # directions (0.8, 0, -+0.6): |cos theta| = 0.6, far from the jets along +-y
        mu = [part(13, 25.0, (0.8, 0.0, -0.6), -1.0, MMU), part(-13, 25.0, (0.8, 0.0, 0.6), 1.0, MMU)]
        ids, p4, ch = build(muons=mu)
        ctx = efhz.make_ctx(ids, p4, ch, sqrt_s=91.2)
        P = p4[0] + p4[1]
        want = math.sqrt((91.2 - P[0]) ** 2 - P[1] ** 2 - P[2] ** 2 - P[3] ** 2)
        self.assertAlmostEqual(efhz.recoil_mass(p4, 0, 1, 91.2), want, places=9)
        self.assertLess(want, 40.0)
        self.assertGreater(eff4f.pair_mass(P), 20.0)
        f = efhz.cut_flags(ctx, 0, 1)
        self.assertFalse(f["recoil"])
        self.assertTrue(all(v for k, v in f.items() if k != "recoil"), f)
        self.assertTrue(efhz.select(ctx, 0, 1, recoil_min=None))
        self.assertFalse(efhz.select(ctx, 0, 1))

    def test_charged_track_in_cone(self):
        near1 = part(211, 1.0, sph(40, 0), 1.0, MPI)      # 20 deg from muon 0
        near2 = part(-211, 1.0, sph(140, 180), -1.0, MPI)  # 20 deg from muon 1
        ids, p4, ch = build(extra=[near1])
        r = efhz.evaluate(ids, p4, ch, 0, 1)
        self.assertEqual(r["n_iso"], 1)
        self.assertTrue(r["nominal"])
        self.assertFalse(r["both_iso"])
        ids, p4, ch = build(extra=[near1, near2])
        r = efhz.evaluate(ids, p4, ch, 0, 1)
        self.assertEqual(r["n_iso"], 0)
        self.assertFalse(r["nominal"])
        self.assertFalse(r["cut_iso"])

    def test_neutral_energy_and_brem(self):
        spoil = part(-211, 1.0, sph(140, 180), -1.0, MPI)  # muon 1 never isolated here
        cases = [(part(22, 0.5, sph(50, 0), 0.0, 0.0), True),     # 0.5 GeV at 10 deg: isolated
                 (part(22, 1.5, sph(50, 0), 0.0, 0.0), False),    # 1.5 GeV at 10 deg: not
                 (part(22, 1.5, sph(59, 0), 0.0, 0.0), True),     # 1 deg: bremsstrahlung, ignored
                 (part(2112, 1.169, sph(50, 0), 0.0, MN), False),  # neutral hadron counts
                 (part(14, 5.0, sph(50, 0), 0.0, 0.0), True)]     # a neutrino is invisible
        for extra, want in cases:
            ids, p4, ch = build(extra=[spoil, extra])
            self.assertEqual(efhz.isolated(p4, ids, ch, eff4f.visible(ids), 0), want, extra[0])
            self.assertEqual(efhz.evaluate(ids, p4, ch, 0, 1)["nominal"], want, extra[0])

    def test_missing_energy_needs_eight_tracks(self):
        ids, p4, ch = build(neutrinos=True)
        ctx = efhz.make_ctx(ids, p4, ch)
        self.assertEqual(ctx["nch"], 6)
        self.assertGreater(ctx["emiss"], 0.1 * ctx["sqrt_s"])
        self.assertFalse(efhz.cut_flags(ctx, 0, 1)["mult"])
        self.assertTrue(efhz.cut_flags(ctx, 0, 1, nch_min_miss=6)["mult"])
        ids, p4, ch = build()
        self.assertTrue(efhz.cut_flags(efhz.make_ctx(ids, p4, ch), 0, 1)["mult"])

    def test_pt_sum(self):
        ids, p4, ch = build()
        self.assertAlmostEqual(efhz.pt_sum(p4, 0, 1, np.array([0.0, 1.0, 0.0])), 30.0, places=6)
        self.assertAlmostEqual(efhz.pt_sum(p4, 0, 1, efhz.eff4f.unit(p4[0, 1:])), 0.0, places=6)
        ctx = efhz.make_ctx(ids, p4, ch)
        ax = efhz.hadron_axis(ctx, 0, 1)
        self.assertAlmostEqual(abs(ax[1]), 1.0, places=9)
        self.assertTrue(efhz.cut_flags(ctx, 0, 1, pt_min=20.0)["pt"])
        self.assertFalse(efhz.cut_flags(ctx, 0, 1, pt_min=35.0)["pt"])   # at most 30 possible
        self.assertTrue(efhz.cut_flags(ctx, 0, 1, pt_min=29.0, pt_axis="had")["pt"])

    def test_momentum_and_mass_cuts(self):
        ids, p4, ch = build()
        ctx = efhz.make_ctx(ids, p4, ch)
        self.assertTrue(efhz.cut_flags(ctx, 0, 1, psum=29.0)["psum"])
        self.assertFalse(efhz.cut_flags(ctx, 0, 1, psum=31.0)["psum"])
        self.assertFalse(efhz.cut_flags(ctx, 0, 1, pmin=16.0)["p"])
        self.assertFalse(efhz.cut_flags(ctx, 0, 1, mll_min=31.0)["mll"])
        self.assertFalse(efhz.cut_flags(ctx, 0, 1, cmax=0.4)["p"])   # |cos| = 0.5


class TestCounting(unittest.TestCase):
    def test_accumulate_and_eps(self):
        c = efhz.new_counts()
        ids, p4, ch = build()
        efhz.accumulate(c, efhz.evaluate(ids, p4, ch, 0, 1))
        near = [part(211, 1.0, sph(40, 0), 1.0, MPI), part(-211, 1.0, sph(140, 180), -1.0, MPI)]
        ids, p4, ch = build(extra=near)
        efhz.accumulate(c, efhz.evaluate(ids, p4, ch, 0, 1))
        self.assertEqual((c["n_pairs"], c["n_acc"]), (2, 2))
        self.assertEqual(c["pass"]["nominal"], 1)
        self.assertEqual(c["pass"]["norecoil"], 1)
        self.assertEqual(c["nm1"]["iso"], 2)
        self.assertEqual(c["cut"]["iso"], 1)
        e, err = efhz.eps(c, "nominal")
        self.assertAlmostEqual(e, 0.5)
        self.assertAlmostEqual(err, math.sqrt(0.25 / 2))


class TestConfront(unittest.TestCase):
    def test_rate_prediction(self):
        one = efhz.predict_rate(1.0)
        want = lep4f.rate_acc("nominal") * 4.5e6 * eff4f.bw_fraction(*eff4f.GEN_RANGE) * 0.86 ** 2
        self.assertAlmostEqual(one, want, places=9)
        self.assertTrue(150.0 < one < 220.0, one)
        self.assertAlmostEqual(efhz.predict_rate(0.5), 0.5 * one, places=9)
        self.assertLess(efhz.predict_rate(1.0, "low"), one)

    def test_subset_prediction_and_pvalues(self):
        self.assertAlmostEqual(efhz.predict_subset(1.0), 32.31 * eff4f.bw_fraction(22.0, 40.0), places=9)
        self.assertAlmostEqual(efhz.p_subset_marginal(0.0), 1.0, places=9)
        a, b = efhz.p_subset_marginal(0.3), efhz.p_subset_marginal(0.8)
        self.assertTrue(1.0 > a > b > 0.0, (a, b))
        # marginalising over the yield uncertainty can only weaken a strong exclusion
        self.assertGreater(b, lep4f.pois_cdf(3, efhz.predict_subset(0.8)))

    def test_confront_keys_and_limits(self):
        r = efhz.confront(0.5)
        self.assertTrue(7.0 < r["s_up_95"] < 8.5, r["s_up_95"])
        self.assertAlmostEqual(r["eps_max_subset_id1"], r["s_up_95"] / efhz.predict_subset(1.0))
        self.assertAlmostEqual(r["eps_max_rate_nominal"], r["s_up_95"] / efhz.predict_rate(1.0))
        for k in ("rate|nominal|central", "rate|low|minus1sigma", "rate|low|lit1.1e-5",
                  "subset|id1", "subset|id0.74"):
            self.assertIn(k, r)
            self.assertTrue(0.0 <= r[k]["p"] <= 1.0)
        self.assertLess(r["rate|nominal|central"]["p"], r["rate|low|lit1.1e-5"]["p"])
        self.assertLess(r["subset|id1"]["pred"], r["rate|nominal|central"]["pred"])


if __name__ == "__main__":
    unittest.main()
