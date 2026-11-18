"""Unit tests for bbspur (MV2 of Munim, Inc.; made with AI agents; Apache-2.0).
Needs dimustat.py, bbshape.py, forecast.py and bkgsys.py next to it (the job fetches them)."""
import math
import unittest

import numpy as np

import bbspur
import forecast as fc

GRID = np.round(np.arange(-10, 31) * 0.1, 6)    # mu = -1.0 ... 3.0, contains 0 and 1


class TestTreatments(unittest.TestCase):
    def test_treat_curve(self):
        base = np.array([[9.0, 9.0], [8.0, 8.0], [7.0, 7.0], [1.0, 1.0], [6.0, 6.0]])
        self.assertEqual(bbspur.treat_curve('old', base, 2, 4).tolist(), [8.0, 8.0])
        self.assertEqual(bbspur.treat_curve('ss', base, 2, 4).tolist(), [1.0, 1.0])
        self.assertEqual(bbspur.treat_curve('fix3', base, 2, 4).tolist(), [7.0, 7.0])
        # + penalty x degree: 10, 10, 10, 5, 11 -> 5
        self.assertEqual(bbspur.treat_curve('env', base, 2, 4).tolist(), [5.0, 5.0])
        self.assertEqual(bbspur.treat_curve('env_min2', base, 2, 4).tolist(), [5.0, 5.0])
        low1 = np.array([[0.0, 0.0], [8.0, 8.0], [7.0, 7.0], [6.0, 6.0], [6.0, 6.0]])
        self.assertEqual(bbspur.treat_curve('env', low1, 1, 1).tolist(), [1.0, 1.0])
        self.assertEqual(bbspur.treat_curve('env_min2', low1, 1, 1).tolist(), [10.0, 10.0])
        with self.assertRaises(ValueError):
            bbspur.treat_curve('nope', base, 1, 1)

    def test_asimov_recovers_injected_signal_on_exact_shape(self):
        # forecast's powerlaw3 truth is exactly representable by every background degree
        # (dimu-forecast-v2: spurious 0.000 for degrees 1-5), so every treatment must find no
        # spurious signal and mu_hat = 1 for an injected ALEPH-sized signal (rule: Asimov sanity)
        truth = fc.truth_shapes(None)['powerlaw3']
        r = bbspur.assess(truth, 21.71, 979.1, bbspur.signal(math.sqrt(6e-4)), grid=GRID)
        self.assertEqual(r['d_ss'], 1)
        for m in bbspur.METHODS:
            v = r['methods'][m]
            self.assertLess(abs(v['spur']), 0.02, (m, v))
            self.assertLess(abs(v['muhat_mu1'] - 1.0), 0.03, (m, v))
            self.assertGreater(v['z0_mu1'], 1.0, (m, v))
            self.assertTrue(v['sigma'] > 0.0, (m, v))


if __name__ == '__main__':
    unittest.main()
