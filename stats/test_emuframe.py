# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for emuframe 0.1.0 on made-up inputs whose answers are known in closed form.
No real data are used."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import emuframe as ef  # noqa: E402


def flat_case(T, r, S, nbins=30, k=15, signal_in_data=True):
    """Asimov set: e mu = T per bin, mu mu = r T (+ S in bin k); signal template S in bin k."""
    m = [float(T)] * nbins
    n = [r * T + (S if (signal_in_data and i == k) else 0.0) for i in range(nbins)]
    s = [S if i == k else 0.0 for i in range(nbins)]
    return n, m, s


class TestBasics(unittest.TestCase):
    def test_z_from_p(self):
        self.assertAlmostEqual(ef.z_from_p(0.5), 0.0, delta=1e-6)
        self.assertAlmostEqual(ef.z_from_p(0.5 * math.erfc(5.0 / math.sqrt(2.0))), 5.0, delta=1e-6)
        self.assertAlmostEqual(ef.z_from_p(0.025), 1.95996, delta=1e-4)

    def test_z_bi_small_cases(self):
        # p = P(Binomial(n_on + n_off, 1/(1+tau)) >= n_on), worked by hand
        self.assertAlmostEqual(ef.z_bi(1, 0, 1.0), 0.0, delta=1e-6)        # p = 1/2
        self.assertAlmostEqual(ef.z_bi(2, 0, 1.0), 0.67449, delta=2e-4)    # p = 1/4
        self.assertAlmostEqual(ef.z_bi(3, 1, 1.0), 0.48878, delta=2e-3)    # p = 5/16

    def test_z_bi_larger_off_sample_is_more_significant(self):
        self.assertGreater(ef.z_bi(90, 124, 1.88), ef.z_bi(90, 66, 1.0))


class TestVoigt(unittest.TestCase):
    edges = [20.0 + i for i in range(21)]

    def test_sums_to_one(self):
        self.assertAlmostEqual(sum(ef.voigt_bin_probs(self.edges)), 1.0, delta=1e-9)

    def test_symmetric(self):
        p = ef.voigt_bin_probs(self.edges, m=30.0)
        for a, b in zip(p, reversed(p)):
            self.assertAlmostEqual(a, b, delta=1e-9)

    def test_gaussian_limit(self):
        p = ef.voigt_bin_probs(self.edges, m=30.0, gamma=1e-6, sigma=1.0)
        c = [ef.phi(x - 30.0) for x in self.edges]
        for i, pi in enumerate(p):
            self.assertAlmostEqual(pi, (c[i + 1] - c[i]) / (c[-1] - c[0]), delta=1e-4)

    def test_cauchy_limit(self):
        p = ef.voigt_bin_probs(self.edges, m=30.0, gamma=2.0, sigma=1e-6)
        c = [0.5 + math.atan(x - 30.0) / math.pi for x in self.edges]
        for i, pi in enumerate(p):
            self.assertAlmostEqual(pi, (c[i + 1] - c[i]) / (c[-1] - c[0]), delta=2e-3)


class TestLikelihood(unittest.TestCase):
    def test_t_hat_stationary(self):
        for n, m, s, r, mu in [(10, 20, 3, 0.5, 1.0), (0, 5, 2, 0.5, 1.0), (40, 9, 7, 1.3, 2.0),
                               (3, 100, 0.5, 0.05, 4.0)]:
            t = ef.t_hat(n, m, s, r, mu)
            g = r * n / (r * t + mu * s) - r + m / t - 1.0
            self.assertLess(abs(g), 1e-9 * (1.0 + r), (n, m, s, r, mu, t, g))

    def test_t_hat_zero_template(self):
        self.assertAlmostEqual(ef.t_hat(7, 0, 2, 0.5, 1.0), 2.0 / 3.0, delta=1e-12)
        self.assertEqual(ef.t_hat(2, 0, 5, 0.5, 1.0), 0.0)
        self.assertAlmostEqual(ef.t_hat(6, 9, 0.0, 0.5, 1.0), 10.0, delta=1e-12)

    def test_t_hat_is_maximum(self):
        n, m, s, r, mu = 10, 20, 3, 0.5, 1.0
        f = lambda t: n * math.log(r * t + mu * s) - (r * t + mu * s) + m * math.log(t) - t
        t = ef.t_hat(n, m, s, r, mu)
        self.assertGreater(f(t), f(1.001 * t))
        self.assertGreater(f(t), f(0.999 * t))

    def test_mu0_ratio_is_n_over_m(self):
        n, m, s = [10, 20, 30, 5], [25, 30, 70, 9], [0, 1, 0, 0]
        for model in ("bb", "exact"):
            r = ef.fit(n, m, s, model, mu_fixed=0.0)["r"]
            self.assertAlmostEqual(r / (65.0 / 134.0), 1.0, delta=1e-6, msg=model)

    def test_asimov_signal_recovered(self):
        t = [1000.0 * math.exp(-i / 20.0) for i in range(30)]
        s = [200.0 if i == 15 else 0.0 for i in range(30)]
        n = [0.5 * ti + si for ti, si in zip(t, s)]
        for model in ("bb", "exact"):
            f = ef.fit(n, t, s, model)
            self.assertAlmostEqual(f["mu"], 1.0, delta=1e-3, msg=model)
            self.assertAlmostEqual(f["r"], 0.5, delta=1e-4, msg=model)


class TestGaussianLimit(unittest.TestCase):
    """One signal bin, 29 sidebands. Var(mu_hat S) = r T (1 + r)(1 + 1/29) with the e mu
    template's Poisson error, r T (1 + 1/29) with the template exact."""

    def test_bb_and_exact(self):
        T, r = 1.0e5, 0.5
        sig_bb = math.sqrt(r * T * (1 + r) * 30.0 / 29.0)
        sig_ex = math.sqrt(r * T * 30.0 / 29.0)
        S = 3.0 * sig_bb
        n, m, s = flat_case(T, r, S)
        z_bb = ef.discovery(n, m, s, "bb")["Z0"]
        z_ex = ef.discovery(n, m, s, "exact")["Z0"]
        self.assertAlmostEqual(z_bb, 3.0, delta=0.05)
        self.assertAlmostEqual(z_ex, S / sig_ex, delta=0.05)
        self.assertAlmostEqual(z_bb / z_ex, 1.0 / math.sqrt(1.0 + r), delta=0.01)

    def test_large_template_limit(self):
        T, r = 1.0e7, 5.0e-3
        S = 3.0 * math.sqrt(r * T * (1 + r) * 30.0 / 29.0)
        n, m, s = flat_case(T, r, S)
        z_bb = ef.discovery(n, m, s, "bb")["Z0"]
        z_ex = ef.discovery(n, m, s, "exact")["Z0"]
        self.assertAlmostEqual(z_bb / z_ex, 1.0 / math.sqrt(1.0 + r), delta=0.005)

    def test_median_expected_limit(self):
        # background-only Asimov data: CLs = 2 (1 - Phi(mu / sigma_mu)) = 0.05 -> mu = 1.96
        T, r = 1.0e5, 0.5
        S = math.sqrt(r * T * (1 + r) * 30.0 / 29.0)   # mu = 1 is one standard deviation
        n, m, s = flat_case(T, r, S, signal_in_data=False)
        self.assertAlmostEqual(ef.upper_limit(n, m, s, "bb"), 1.96, delta=0.05)


class TestDecisions(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(ef.label(0.8, 5.0, 0.0), "EXCLUDED")
        self.assertEqual(ef.label(3.0, 0.5, 2.5), "COMPATIBLE")
        self.assertEqual(ef.label(3.0, 0.5, 1.5), "INCONCLUSIVE")
        self.assertEqual(ef.label(3.0, 2.0, 3.0), "INCONCLUSIVE")
        self.assertEqual(ef.combine("EXCLUDED", "EXCLUDED"), "EXCLUDED")
        self.assertEqual(ef.combine("EXCLUDED", "INCONCLUSIVE"), "INCONCLUSIVE")

    def test_window(self):
        edges = [15.0 + i for i in range(36)]
        self.assertEqual([[edges[i], edges[i + 1]] for i in ef.window_bins(edges)],
                         [[29.0, 30.0], [30.0, 31.0], [31.0, 32.0]])


class TestAlephDriver(unittest.TestCase):
    def test_made_up_spectrum(self):
        edges = [15.0 + i for i in range(36)]
        v = [80.0 * math.exp(-(15.5 + i - 15.0) / 12.0) for i in range(35)]
        n = [round(vi) + (8 if 14 <= i <= 16 else 0) for i, vi in enumerate(v)]
        out = ef.aleph_aprime(edges, n, v)
        self.assertTrue(out["exact_valid"])
        self.assertGreater(out["bb"]["Z0"], 0.5)
        self.assertLess(out["bb"]["Z0"], out["exact"]["Z0"])
        self.assertGreater(out["window"]["Z_Bi_tau_1_over_r0"], out["window"]["Z_Bi_tau1"])
        self.assertEqual(len(out["window"]["bins"]), 3)


if __name__ == "__main__":
    unittest.main()
