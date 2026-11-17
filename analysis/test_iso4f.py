"""Tests for iso4f: agreement with dimusel on a hand-built ntuple, categories, data refusal.
MV2 of Munim, Inc. Made with AI agents. Apache-2.0."""
import gzip
import math
import os
import shutil
import tempfile
import unittest

import dimusel as D
import iso4f as I

MPI = 0.13957
MMU = 0.1056584


def eline(run, evt, btp3):
    f = [run, evt, 1, 10, 10, 10, 2, 91.0, 60.0, 20.0, 10.0, 0, 0, 0, 0.5, 0.5, btp3, 0, 0, 0,
         1.0, 0.0, 0.0, 0.9]
    return "E " + " ".join(str(x) for x in f)


def pline(run, evt, i, q, kmu1, px, py, pz, m):
    e = math.sqrt(px * px + py * py + pz * pz + m * m)
    ints = [run, evt, i, q, 0, kmu1, 0, 0, 0, 0, 0]
    reals = [px, py, pz, e, 0.0, 0.0, 0.0, 0.01, 0.02, 0.01]
    return "P " + " ".join(str(x) for x in ints) + " " + " ".join("%.6f" % x for x in reals)


HADRONS = [(1, 8.0, 0.5, 0.0), (-1, 7.0, -0.5, 0.3), (1, 6.0, 0.2, -0.2),
           (-1, -8.0, 0.4, 0.0), (1, -7.0, -0.3, 0.2), (-1, -6.0, 0.0, 0.1)]


def event(run, evt, btp3, mu1, mu2):
    ps = [pline(run, evt, k + 1, q, 0, x, y, z, MPI) for k, (q, x, y, z) in enumerate(HADRONS)]
    ps.append(pline(run, evt, 7, 1, 1, mu1[0], mu1[1], mu1[2], MMU))
    ps.append(pline(run, evt, 8, -1, 1, mu2[0], mu2[1], mu2[2], MMU))
    return eline(run, evt, btp3), ps


ISO1, ISO2 = (0.0, 15.0, 3.0), (0.0, -12.0, 5.0)        # 90 degrees from both jets, m ~ 27.0
NEAR1, FAR2 = (9.0, 1.0, 0.5), (-0.5, -12.0, 5.0)       # first muon ~7 degrees from the +x jet


def write_ntuple(folder, tag, evs):
    ev = os.path.join(folder, tag + ".ev.txt.gz")
    with gzip.open(ev, "wt") as fe, gzip.open(ev.replace(".ev.", ".pa."), "wt") as fp:
        for el, ps in evs:
            fe.write(el + "\n")
            for p in ps:
                fp.write(p + "\n")
    return ev


class TestIso4f(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.evs = [event(1, 1, 0.001, ISO1, ISO2),     # b-tagged, isolated
                    event(1, 2, 0.001, NEAR1, FAR2),    # b-tagged, not isolated
                    event(1, 3, 0.5, ISO1, ISO2)]       # untagged, isolated
        self.path = write_ntuple(self.d, "mc_test_TAP1.sdst", self.evs)

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_counts(self):
        r = I.run([self.path])
        t = r["total"]["counts"]
        self.assertEqual(t["all"]["range_15_50"], 3)
        self.assertEqual(t["iso"]["range_15_50"], 2)
        self.assertEqual(t["iso_btag"]["range_15_50"], 1)
        self.assertEqual(t["iso_untagged"]["range_15_50"], 1)
        self.assertEqual(t["iso"]["window_26_35"], 2)
        self.assertEqual(len(r["pairs"]), 3)
        near = [p for p in r["pairs"] if p["evt"] == 2][0]
        self.assertFalse(near["iso"])
        self.assertLess(near["ang"][0], 10.0)
        self.assertGreater(near["ang"][1], 20.0)
        iso = [p for p in r["pairs"] if p["evt"] == 1][0]
        self.assertTrue(iso["iso"])
        self.assertAlmostEqual(iso["m"], 26.98, delta=0.05)
        self.assertGreater(min(iso["ang"]), 80.0)

    def test_agrees_with_dimusel(self):
        r = I.run([self.path])
        sel = D.Selector()
        sel.process_file(self.path, D.is_data_tag(self.path))
        mc = sel.result()["samples"]["mc"]
        cats = mc["categories"]
        self.assertEqual(cats["os_mumu_btag_iso"]["n_15_50"], r["total"]["counts"]["iso_btag"]["range_15_50"])
        self.assertEqual(cats["os_mumu_btag"]["n_15_50"],
                         sum(1 for p in r["pairs"] if p["btag"] and 15 <= p["m"] < 50))
        self.assertEqual(cats["os_mumu_untagged"]["n_15_50"],
                         sum(1 for p in r["pairs"] if not p["btag"] and 15 <= p["m"] < 50))
        for k in ("events", "hadronic", "btag", "with_P_lines", "pmiss_pass"):
            self.assertEqual(mc["cutflow"][k], r["total"]["cutflow"][k], k)

    def test_refuses_data(self):
        p = write_ntuple(self.d, "data_Y13709.1.al", self.evs[:1])
        with self.assertRaises(SystemExit):
            I.run([p])

    def test_categories(self):
        self.assertEqual(I.categories({"iso": False, "btag": True}), ["all"])
        self.assertEqual(I.categories({"iso": True, "btag": True}), ["all", "iso", "iso_btag"])
        self.assertEqual(I.categories({"iso": True, "btag": False}), ["all", "iso", "iso_untagged"])

    def test_main_writes(self):
        out = os.path.join(self.d, "o.json")
        self.assertEqual(I.main(["--dir", self.d, "--out", out]), 0)
        self.assertTrue(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
