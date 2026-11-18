"""Tests for bkgsys (run first in every job). MV2 of Munim, Inc.; made with AI agents. Apache-2.0."""
import math
import unittest

import numpy as np

import dimustat as ds
import bkgsys as bs

SIG = ds.signal_template()
COARSE = np.round(np.arange(-20, 21) * 0.05, 6)   # mu = -1.00 ... 1.00
UPPER = np.round(np.arange(-10, 41) * 0.05, 6)    # mu = -0.50 ... 2.00


def powerlaw(p, total):
    w = ds.CENT ** -p
    return total * w / w.sum()


def c2_untagged():
    """combcast 0.1.0 scenario C2's untagged background: b bbar m^-1 plus half as much m^-3."""
    bt = 1457.06 * 0.84 * 0.8
    bu = bt * (1.0 - 0.38) / 0.38
    return powerlaw(1.0, bu) + 0.5 * powerlaw(3.0, bu)


NU_C2 = 32.31 * 0.84 * 0.8 * (1.0 - 0.38) / 0.38  # 35.43, as printed by dimu-combcast-v1


class TestHelpers(unittest.TestCase):
    def test_c2_inputs_match_combcast_print(self):
        # dimu-combcast-v1 printed bkg_untagged_15_50 = 2396.3 and n_exp_untagged = 35.43
        self.assertAlmostEqual(float(c2_untagged().sum()), 2396.3, delta=0.1)
        self.assertAlmostEqual(NU_C2, 35.43, delta=0.01)

    def test_envelope_and_penalty(self):
        curves = np.array([[5.0, 4.0, 3.0], [3.0, 2.5, 3.5]])
        E, idx = bs.envelope(curves, degrees=(1, 2), penalty=1.0)
        np.testing.assert_allclose(E, [5.0, 4.5, 4.0])
        self.assertEqual(list(idx), [1, 1, 0])
        E2, idx2 = bs.envelope(curves, degrees=(1, 2), penalty=2.0)
        np.testing.assert_allclose(E2, [7.0, 6.0, 5.0])  # [7,6,5] vs [7,6.5,7.5]
        self.assertEqual(list(idx2), [0, 0, 0])

    def test_profile_summary_parabola(self):
        g = bs.GRID
        E = ((g - 0.5) / 0.3) ** 2 + 7.0
        s = bs.profile_summary(g, E)
        self.assertAlmostEqual(s['muhat'], 0.5, places=6)
        self.assertAlmostEqual(s['z0'], 0.5 / 0.3, places=3)
        self.assertAlmostEqual(s['sigma_up'], 0.3, delta=1e-3)
        self.assertAlmostEqual(s['sigma_down'], 0.3, delta=1e-3)
        self.assertAlmostEqual(s['ul_sens'], 1.959964 * 0.3, delta=2e-3)
        self.assertAlmostEqual(s['q1'], (0.5 / 0.3) ** 2, places=3)

    def test_profile_summary_negative_muhat_has_zero_z0(self):
        g = bs.GRID
        s = bs.profile_summary(g, ((g + 0.4) / 0.5) ** 2)
        self.assertAlmostEqual(s['muhat'], -0.4, places=6)
        self.assertEqual(s['z0'], 0.0)

    def test_crossing_nan_when_never(self):
        s = bs.profile_summary(bs.GRID, np.zeros(len(bs.GRID)))
        self.assertTrue(math.isnan(s['sigma_up']))

    def test_cls_limit_closed_form(self):
        # muhat = 0, constant sigma 0.4: CLs = 2 (1 - Phi(mu / 0.4)) = 0.05 at mu = 1.95996 * 0.4
        g = bs.GRID
        E = (g / 0.4) ** 2
        f = bs.sigma_fn_from_asimov(g, E)
        self.assertAlmostEqual(f(1.0), 0.4, places=6)
        ul = bs.cls_upper_limit(g, E, f)
        self.assertAlmostEqual(ul, 1.959964 * 0.4, delta=5e-3)

    def test_choose_degree_spurious_logic(self):
        t = [dict(degree=1, frac=-0.7), dict(degree=2, frac=0.25), dict(degree=3, frac=0.1),
             dict(degree=4, frac=0.05)]
        self.assertEqual(bs.choose_degree_spurious(t), 3)
        t2 = [dict(degree=1, frac=-0.7), dict(degree=2, frac=0.3), dict(degree=3, frac=-0.25)]
        self.assertEqual(bs.choose_degree_spurious(t2), 3)


class TestFits(unittest.TestCase):
    def test_curves_match_direct_fit(self):
        n = powerlaw(1.0, 1600.0) + 30.0 * SIG
        cur = bs.degree_curves(n, 30.0, SIG, degrees=(1,), grid=UPPER)
        i1 = int(np.argmin(np.abs(UPPER - 1.0)))
        direct = 2.0 * ds.fit(ds.Model(1, sig=SIG), n, fix_ns=30.0)[0]
        self.assertAlmostEqual(cur[0, i1], direct, delta=1e-4)

    def test_spurious_zero_for_exact_power_law(self):
        tab = bs.spurious_table(powerlaw(1.0, 1600.0), 30.0, SIG, degrees=(1, 2), grid=COARSE)
        for r in tab:
            self.assertLess(abs(r['mu_spur']), 0.01, r)
            self.assertLess(abs(r['frac']), 0.05, r)
        self.assertEqual(bs.choose_degree_spurious(tab), 1)

    def test_spurious_negative_for_c2_mixture(self):
        # dimu-combcast-v1: degree-1 Asimov fit of C2's untagged category at mu = 1 gave
        # mu_hat = 0.513, i.e. a spurious signal near -0.49
        tab = bs.spurious_table(c2_untagged(), NU_C2, SIG, degrees=(1, 3), grid=COARSE)
        d1, d3 = tab
        self.assertGreater(d1['mu_spur'], -0.62)
        self.assertLess(d1['mu_spur'], -0.36)
        self.assertLess(d1['frac'], -0.5)
        self.assertLess(abs(d3['mu_spur']), 0.5 * abs(d1['mu_spur']))

    def test_envelope_recovers_exact_signal(self):
        n = powerlaw(1.0, 1600.0) + 30.0 * SIG
        cur = bs.degree_curves(n, 30.0, SIG, degrees=(1, 2), grid=UPPER)
        E, idx = bs.envelope(cur, degrees=(1, 2))
        s = bs.profile_summary(UPPER, E)
        self.assertAlmostEqual(s['muhat'], 1.0, delta=0.02)
        i1 = int(np.argmin(np.abs(UPPER - 1.0)))
        self.assertEqual(int(idx[i1]), 0)  # degree 1 is exact; degree 2 pays the penalty


if __name__ == '__main__':
    unittest.main()
