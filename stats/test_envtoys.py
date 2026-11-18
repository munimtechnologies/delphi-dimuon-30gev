"""Tests for envtoys (run first in every job). MV2 of Munim, Inc.; made with AI agents. Apache-2.0."""
import math
import time
import unittest

import numpy as np

import bkgsys as bs
import envcast as ec
import envtoys as et


def parabola_curves(grid, centres, widths):
    g = np.asarray(grid, float)
    return np.array([((g - c) / w) ** 2 + 3.0 * k for k, (c, w) in enumerate(zip(centres, widths))])


def parabola_sig_data(keys):
    E = (bs.GRID / 0.5) ** 2
    return {k: (bs.GRID.tolist(), E.tolist()) for k in keys}


class TestBookkeeping(unittest.TestCase):
    def test_task_list_order_counts_seeds(self):
        t = et.task_list(10, 4, 5, 100)
        self.assertEqual([(mu, n) for mu, n, _ in t], [(1.0, 5), (1.0, 5), (0.0, 4)])
        self.assertEqual([s for _, _, s in t], [1100, 1101, 1102])
        t2 = et.task_list(200, 120, 5, 0)
        self.assertEqual(sum(n for mu, n, _ in t2 if mu == 1.0), 200)
        self.assertEqual(sum(n for mu, n, _ in t2 if mu == 0.0), 120)
        self.assertEqual(len(set(s for _, _, s in t2)), len(t2))
        self.assertEqual([mu for mu, _, _ in t2[:6]], [1.0, 1.0, 0.0, 1.0, 1.0, 0.0])

    def test_clopper_pearson(self):
        lo, hi = et.clopper_pearson(0, 200)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 1.0 - 0.025 ** (1.0 / 200), delta=1e-4)  # 0.0183
        lo, hi = et.clopper_pearson(10, 200)
        self.assertLess(lo, 0.05)
        self.assertGreater(hi, 0.05)
        self.assertTrue(math.isnan(et.clopper_pearson(0, 0)[0]))

    def test_summarise_and_criterion_b(self):
        def row(mu, oc):
            r = dict(muhat=1.0, z0=1.0, ul=2.0, outcome=oc)
            return dict(mu=mu, res={'fix3|tagged': r, 'fix3|combined': r})
        rs = [row(1.0, 'EXCLUDED')] * 7 + [row(1.0, 'INCONCLUSIVE')] * 143
        s = et.summarise(rs)
        d = s['mu=1']['fix3|combined']
        self.assertEqual((d['n'], d['n_EXCLUDED']), (150, 7))
        self.assertAlmostEqual(d['p_EXCLUDED'], 0.0467, places=4)
        self.assertEqual(et.criterion_b(s), 'PASS')
        rs2 = [row(1.0, 'EXCLUDED')] * 12 + [row(1.0, 'INCONCLUSIVE')] * 138
        self.assertEqual(et.criterion_b(et.summarise(rs2)), 'FAIL')
        self.assertEqual(et.criterion_b(et.summarise(rs[:100])), 'UNDETERMINED')
        self.assertEqual(et.criterion_b(s, 'old'), 'UNDETERMINED')


class TestOneDefinition(unittest.TestCase):
    def test_outcomes_agree_with_envcast(self):
        g = et.TOY_GRID
        keys = [(m, t) for m in ec.METHODS for t in ('tagged', 'combined')]
        sig_data = parabola_sig_data(keys)
        fns = et.sigma_fns(sig_data)
        cases = [((0.0, 0.1, -0.2, 0.3, 0.0), (0.5, 0.6, 0.55, 0.7, 0.8)),
                 ((1.0, 0.9, 1.2, 1.1, 1.0), (0.4, 0.5, 0.45, 0.6, 0.7)),
                 ((-0.3, 0.2, 0.1, 0.0, 0.4), (0.3, 0.6, 0.5, 0.5, 0.9))]
        for (cT, wT), (cU, wU) in zip(cases, cases[1:] + cases[:1]):
            cur = {'T': parabola_curves(g, cT, wT), 'U': parabola_curves(g, cU, wU)}
            d_old = {'T': 1, 'U': 2}
            row = {c: dict(curves=cur[c].tolist(), d_old=d_old[c]) for c in ('T', 'U')}
            ref = ec.analyse_toy(row, {'T': 1, 'U': 1}, fns)
            mine = et.analyse(cur, d_old, fns, ('fix3', 'old'))
            for k, v in mine.items():
                self.assertEqual(v['outcome'], ref[k]['outcome'], k)
                self.assertAlmostEqual(v['muhat'], ref[k]['muhat'], places=6)
                if v['ul'] == v['ul']:
                    self.assertAlmostEqual(v['ul'], ref[k]['ul'], places=6)


class TestFits(unittest.TestCase):
    def test_partial_curves_match_degree_curves(self):
        b, cats = ec.categories(et.scenario())
        nub, nexp = cats['U']
        grid = np.array([0.0, 0.5, 1.0])
        n = nub + nexp * b['sig']
        part = et.partial_curves(n, nexp, b['sig'], (3, 1, 3), grid=grid)
        ref = bs.degree_curves(n, nexp, b['sig'], degrees=(1, 3), grid=grid)
        np.testing.assert_allclose(part[0], ref[0], atol=1e-6)
        np.testing.assert_allclose(part[2], ref[1], atol=1e-6)
        for j in (1, 3, 4):
            self.assertTrue(np.all(np.isnan(part[j])))

    def test_toy_chunk_runs(self):
        grid = np.round(np.arange(-1, 6) * 0.5, 6)  # -0.5 ... 2.5
        sig_data = parabola_sig_data([(m, t) for m in ('fix3', 'old') for t in ('tagged', 'combined')])
        rows = et.toy_chunk((et.TOY_SCEN, 1.0, 7, 1, time.time() + 3600, True, sig_data, grid))
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(set(r['res']), {'fix3|tagged', 'fix3|combined', 'old|tagged', 'old|combined'})
        for v in r['res'].values():
            self.assertIn(v['outcome'], ('EXCLUDED', 'COMPATIBLE', 'INCONCLUSIVE'))
        self.assertTrue(all(1 <= d <= 5 for d in r['d_old']))
        rows0 = et.toy_chunk((et.TOY_SCEN, 0.0, 7, 3, time.time() - 1, False, sig_data, grid))
        self.assertEqual(rows0, [])  # past the deadline: nothing


if __name__ == '__main__':
    unittest.main()
