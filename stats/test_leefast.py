# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Offline tests of leefast 0.1.0 (PLAN amendment 0.40). The fit tests need numpy, scipy and the
fetched leescan.py / aprime_smooth.py / emuframe.py next to this file on a POSIX system;
otherwise they skip."""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import leefast as F   # noqa: E402  (stdlib only at import time)
import v1ref as R     # noqa: E402


def upcross(zs, u):
    return sum(1 for i in range(1, len(zs)) if zs[i - 1] < u <= zs[i])


def _fit_deps():
    if os.name != "posix":
        return "not POSIX"
    try:
        import numpy  # noqa: F401
        import scipy  # noqa: F401
    except Exception:
        return "numpy/scipy absent"
    for f in ("leescan.py", "aprime_smooth.py", "emuframe.py"):
        if not os.path.exists(os.path.join(HERE, f)):
            return f + " not fetched"
    return None


class Reference(unittest.TestCase):
    """The numbers copied from leescan-v1 are internally consistent with what v1 printed."""

    def test_lengths(self):
        self.assertEqual(len(R.MASSES), 125)
        for g in ("1.0", "1.78", "3.0"):
            self.assertEqual(len(R.Z_GRID[g]), 125, g)
        self.assertEqual(sorted(R.TOYS_ZMAX), list(range(9)))
        self.assertEqual(sorted(R.TOYS_MMAX), list(range(9)))

    def test_observed_maxima_as_v1_printed(self):
        # v1 run.txt: g1.78 3.133 @30.50, g1.0 3.120 @30.50, g3.0 3.097 @30.50
        for g, zmax in (("1.78", 3.133), ("1.0", 3.120), ("3.0", 3.097)):
            zs = R.Z_GRID[g]
            i = max(range(len(zs)), key=lambda k: zs[k])
            self.assertEqual(R.MASSES[i], 30.5, g)
            self.assertAlmostEqual(zs[i], zmax, delta=0.0006)

    def test_upcrossings_as_v1(self):
        prof = {"g1.0": R.Z_GRID["1.0"], "g1.78": R.Z_GRID["1.78"], "g3.0": R.Z_GRID["3.0"]}
        prof["float"] = [max(a, b, c) for a, b, c in zip(R.Z_GRID["1.0"], R.Z_GRID["1.78"],
                                                        R.Z_GRID["3.0"])]
        for v, want in R.OBS_UPCROSSINGS.items():
            for u, k in want.items():
                self.assertEqual(upcross(prof[v], u), k, (v, u))

    def test_toy_rows_consistent(self):
        for idx, z in R.TOYS_ZMAX.items():
            self.assertAlmostEqual(z["float"], max(z["g1.0"], z["g1.78"], z["g3.0"]), places=9)
            for v in z:
                self.assertIn(R.TOYS_MMAX[idx][v], R.MASSES)
        # 1 of the 9 v1 toys reaches the observed par3 Z (toy 2, 3.443), as disclosed in 0.40
        self.assertEqual(sum(1 for z in R.TOYS_ZMAX.values()
                             if z["g1.78"] >= R.Z_PAR3_CLOSURE), 1)


class Helpers(unittest.TestCase):
    def test_grid_diffs(self):
        masses = (17.0, 17.25)
        zg = {1.0: [0.1, 0.2], 1.78: [0.3, 0.4]}
        ref = {"1.0": [0.1, 0.25], "1.78": [0.3, 0.4]}
        d = F.grid_diffs(zg, ref, masses)
        self.assertEqual(len(d), 4)
        self.assertAlmostEqual(d[0][0], 0.05)
        self.assertEqual((d[0][1], d[0][2]), ("1.0", 17.25))

    def test_toy_diffs(self):
        rows = {0: {"a_zmax": 1.0, "b_zmax": 2.0}}
        d = F.toy_diffs(rows, {0: {"a": 1.001, "b": 2.0}, 5: {"a": 0.0, "b": 0.0}}, ("a", "b"))
        self.assertEqual(len(d), 2)                  # toy 5 absent: not compared
        self.assertAlmostEqual(d[0][0], 0.001)
        self.assertEqual(d[0][1:3], (0, "a"))

    def test_read_rows(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "toys.csv")
            with open(p, "w") as f:
                f.write("idx,g1.78_zmax,g1.78_mmax,g1.78_n0.5\n3,1.25000,30.50000,2\n")
            rows = F.read_rows(p)
        self.assertEqual(rows, [{"idx": 3, "g1.78_zmax": 1.25, "g1.78_mmax": 30.5,
                                 "g1.78_n0.5": 2}])
        self.assertIsInstance(rows[0]["g1.78_n0.5"], int)

    def test_tolerances(self):
        self.assertAlmostEqual(F.V1_TOL, 0.002)
        self.assertGreater(F.V1_TOY_TOL, F.V1_TOL)
        self.assertEqual(len(F.LEESCAN_COMMIT), 40)
        self.assertEqual(len(F.LEESCAN_SHA256), 64)


class Fits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        why = _fit_deps()
        if why:
            raise unittest.SkipTest(why)
        import numpy as np
        cls.np = np
        cls.L = F.load_leescan(HERE)
        cls.asm = cls.L.load_asm(HERE)
        cls.ef = cls.asm.ef
        cls.edges = [15.0 + k for k in range(36)]

    def shape(self, mass, gamma=1.78):
        return [self.ef.N_ALEPH * p for p in self.ef.voigt_bin_probs(
            self.edges, m=mass, gamma=gamma, sigma=self.L.RES * mass, n_theta=400)]

    def spectra(self, inject_at=None, nsig=0.0, seed=7):
        np = self.np
        rng = np.random.default_rng(seed)
        x = np.array([e + 0.5 for e in self.edges[:-1]])
        T = 120.0 * np.exp(-(x - 15.0) / 7.0) + 0.3
        lam = 0.6 * T
        if inject_at is not None:
            s = np.array(self.ef.voigt_bin_probs(self.edges, m=inject_at, gamma=1.78,
                                                 sigma=self.L.RES * inject_at, n_theta=400))
            lam = lam + nsig * s
        return rng.poisson(lam).astype(float), rng.poisson(T).astype(float)

    def test_value_and_gradient_equal_parfit(self):
        np = self.np
        n, m = self.spectra(inject_at=30.4, nsig=25.0)
        s = self.shape(30.4)
        sc = F.FastScanner(self.asm, self.edges, [s])
        pf = self.asm.ParFit(self.edges, s, 3)
        for p in (np.array([4.0, -1.5, 0.3, -0.1, math.log(0.6), 0.7]),
                  np.array([3.5, -2.5, 0.1, 0.05, math.log(0.5), 0.0])):
            f, G, _ = sc.fgh(p, n, m, np.array(s))
            f2, G2 = pf.nll_grad(p, n, m)
            self.assertAlmostEqual(f, f2, delta=1e-9 * max(1.0, abs(f2)))
            for a, b in zip(G, G2):
                self.assertAlmostEqual(a, b, delta=1e-7 * max(1.0, abs(b)))

    def test_hessian_equals_finite_differences(self):
        np = self.np
        n, m = self.spectra(inject_at=30.4, nsig=25.0)
        s = np.array(self.shape(30.4))
        sc = F.FastScanner(self.asm, self.edges, [s])
        p = np.array([4.0, -1.5, 0.3, -0.1, math.log(0.6), 0.7])
        _, _, H = sc.fgh(p, n, m, s)
        eps = 1e-6
        for j in range(len(p)):
            e = np.zeros(len(p))
            e[j] = eps
            Gp = sc.fgh(p + e, n, m, s)[1]
            Gm = sc.fgh(p - e, n, m, s)[1]
            col = (Gp - Gm) / (2 * eps)
            for i in range(len(p)):
                self.assertAlmostEqual(H[i, j], col[i], delta=1e-4 * max(1.0, abs(col[i])),
                                       msg=(i, j))

    def test_fast_equals_discovery(self):
        n, m = self.spectra(inject_at=30.4, nsig=25.0)
        s0 = [self.ef.N_ALEPH * p for p in self.ef.voigt_bin_probs(self.edges, n_theta=400)]
        d = self.asm.ParFit(self.edges, s0, 3).discovery(n, m)
        z = F.FastScanner(self.asm, self.edges, [s0]).scan(n, m)[0][0]
        self.assertAlmostEqual(z, d["Z0"], delta=1e-3)

    def test_fast_equals_lbfgs_scanner(self):
        for inject, nsig, seed in ((30.4, 25.0, 7), (None, 0.0, 11)):
            n, m = self.spectra(inject_at=inject, nsig=nsig, seed=seed)
            shapes = [self.shape(x, g) for x, g in ((24.0, 1.78), (30.4, 1.0), (40.0, 3.0))]
            zs_slow = self.L.Scanner(self.asm, self.edges, shapes).scan(n, m)[0]
            sc = F.FastScanner(self.asm, self.edges, shapes)
            zs_fast = sc.scan(n, m)[0]
            for a, b in zip(zs_fast, zs_slow):
                self.assertAlmostEqual(a, b, delta=1e-3, msg=(inject, zs_fast, zs_slow))
            self.assertEqual(sc.n_fallback, 0)

    def test_newton_respects_bounds(self):
        np = self.np
        n, m = self.spectra(seed=5)
        s = np.array(self.shape(30.4))
        sc = F.FastScanner(self.asm, self.edges, [s])
        a, lnr = sc.pf.start(n, m)
        r = sc.newton(np.concatenate([a, [lnr, 2.0]]), n, m, s, 0.0, sc.mu_max)
        self.assertIsNotNone(r)
        self.assertGreaterEqual(r[1][-1], 0.0)
        self.assertLessEqual(r[1][-1], sc.mu_max)
        r0 = sc.newton(np.concatenate([a, [lnr, 0.0]]), n, m, s, 0.0, 0.0)
        self.assertEqual(r0[1][-1], 0.0)
        self.assertLessEqual(r[0], r0[0] + 1e-9)     # freeing mu never fits worse


if __name__ == "__main__":
    unittest.main()
