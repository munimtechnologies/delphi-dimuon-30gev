# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Offline tests of leescan 0.1.0 (amendment 0.34). The fit tests need numpy, scipy and the
fetched aprime_smooth.py / emuframe.py next to this file on a POSIX system; otherwise they skip."""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    import leescan as L
except Exception as exc:   # pragma: no cover
    L = None
    IMPORT_ERR = exc


def _fit_deps():
    if os.name != "posix":
        return "not POSIX"
    try:
        import numpy  # noqa: F401
        import scipy  # noqa: F401
    except Exception:
        return "numpy/scipy absent"
    for f in ("aprime_smooth.py", "emuframe.py"):
        if not os.path.exists(os.path.join(HERE, f)):
            return f + " not fetched"
    return None


class Pure(unittest.TestCase):
    def setUp(self):
        if L is None:
            self.fail("import failed: %s" % IMPORT_ERR)

    def test_grid(self):
        self.assertEqual(len(L.MASSES), 125)
        self.assertEqual(L.MASSES[0], 17.0)
        self.assertEqual(L.MASSES[-1], 48.0)
        self.assertIn(L.PRIMARY_GAMMA, L.GAMMAS)

    def test_p_z_roundtrip(self):
        for z in (0.5, 1.0, 2.0, 3.134, 5.35):
            self.assertAlmostEqual(L.z_from_p(L.p_from_z(z)), z, places=6)
        self.assertAlmostEqual(L.p_from_z(3.0), 0.0013499, places=6)

    def test_upcrossings(self):
        self.assertEqual(L.count_upcrossings([0.0, 1.2, 0.5, 1.5, 2.0], 1.0), 2)
        self.assertEqual(L.count_upcrossings([1.5, 1.4, 0.2], 1.0), 0)   # starts above: not counted
        self.assertEqual(L.count_upcrossings([0.0, 1.0], 1.0), 1)        # touching counts

    def test_gv(self):
        self.assertAlmostEqual(L.gv_global_p(3.0, 0.0), L.p_from_z(3.0))
        p = L.gv_global_p(3.134, 1.71)
        self.assertAlmostEqual(p, L.p_from_z(3.134) + 1.71 * math.exp(-0.5 * (3.134 ** 2 - 1.0)))
        self.assertTrue(1.9 < L.z_from_p(p) < 2.1)     # the prediction written in amendment 0.34
        self.assertEqual(L.gv_global_p(0.1, 50.0), 1.0)

    def test_direct(self):
        d = L.direct_global([0.5, 1.0, 2.5, 3.5], 2.5)
        self.assertEqual((d["k"], d["n"]), (2, 4))
        self.assertAlmostEqual(d["p"], 0.5)
        d = L.direct_global([0.5, 1.0], 4.0)
        self.assertTrue(d["lower_bound"])
        self.assertAlmostEqual(d["Z"], L.z_from_p(1.5))

    def test_rows_and_summary(self):
        nm = len(L.MASSES)
        rows = []
        for idx in range(4):
            zg = {g: [0.0] * nm for g in L.GAMMAS}
            zg[1.78][10] = 1.2 + idx          # one bump per toy
            zg[1.0][20] = 2.2                  # a narrower bump elsewhere
            rows.append(L.row_from_profiles(idx, zg))
        self.assertEqual(rows[0]["g1.78_zmax"], 1.2)
        self.assertEqual(rows[0]["g1.78_mmax"], L.MASSES[10])
        self.assertEqual(rows[0]["g1.78_n1.0"], 1)
        self.assertEqual(rows[0]["float_n1.0"], 2)
        self.assertEqual(rows[3]["float_zmax"], 4.2)
        self.assertEqual(set(L.csv_columns()) - set(rows[0]), set())
        s = L.summarize(rows, {"g1.78": 3.0, "float": 3.0})
        self.assertAlmostEqual(s["g1.78"]["E_N"]["1.0"]["mean"], 1.0)
        self.assertEqual(s["g1.78"]["observed"]["direct"]["k"], 2)    # 3.2 and 4.2
        self.assertEqual(s["float"]["observed"]["direct"]["k"], 2)
        self.assertEqual(len(s["g1.78"]["conversions"]), len(L.REFERENCE))

    def test_grade_gate(self):
        g = L.grade({"ok": False, "why": "closure"}, {}, 30.5)
        self.assertTrue(g["L0"].startswith("FAIL"))
        self.assertTrue(all(g[k].startswith("NOT GRADABLE") for k in ("L1", "L2", "L3", "L4", "L5")))


class Fits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        why = _fit_deps()
        if why:
            raise unittest.SkipTest(why)
        cls.asm = L.load_asm(HERE)
        cls.ef = cls.asm.ef
        cls.edges = [15.0 + k for k in range(36)]

    def spectra(self, inject_at=None, nsig=0.0, seed=7):
        import numpy as np
        rng = np.random.default_rng(seed)
        x = np.array([e + 0.5 for e in self.edges[:-1]])
        T = 120.0 * np.exp(-(x - 15.0) / 7.0) + 0.3
        lam = 0.6 * T
        if inject_at is not None:
            s = np.array(self.ef.voigt_bin_probs(self.edges, m=inject_at, gamma=1.78,
                                                 sigma=L.RES * inject_at, n_theta=400))
            lam = lam + nsig * s
        return rng.poisson(lam), rng.poisson(T)

    def test_scanner_equals_discovery(self):
        n, m = self.spectra(inject_at=30.4, nsig=25.0)
        s0 = [self.ef.N_ALEPH * p for p in self.ef.voigt_bin_probs(self.edges, n_theta=400)]
        d = self.asm.ParFit(self.edges, s0, 3).discovery(n, m)
        z = L.Scanner(self.asm, self.edges, [s0]).scan(n, m)[0][0]
        self.assertAlmostEqual(z, d["Z0"], places=4)

    def test_scan_finds_injected_bump(self):
        n, m = self.spectra(inject_at=36.0, nsig=30.0, seed=3)
        masses = (22.0, 26.0, 30.0, 34.0, 36.0, 38.0, 42.0)
        shapes = [[self.ef.N_ALEPH * p for p in self.ef.voigt_bin_probs(
            self.edges, m=x, gamma=1.78, sigma=L.RES * x, n_theta=400)] for x in masses]
        zs, _ = L.Scanner(self.asm, self.edges, shapes).scan(n, m)
        best = masses[max(range(len(zs)), key=lambda i: zs[i])]
        self.assertTrue(34.0 <= best <= 38.0, (best, zs))
        self.assertGreater(max(zs), 3.0)


if __name__ == "__main__":
    unittest.main()
