"""Tests for btagcal (hemisphere double-tag calibration).
MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0."""
import gzip
import json
import math
import os
import random
import tempfile
import unittest

import btagcal as B


def e_line(evt, btp1, btp2, btp3=0.5, ihad4=1, nctr4=12, thz=0.1):
    vals = [1000, evt, ihad4, nctr4, nctr4, 30, 0, 91.2, 50.0, 20.02, 10.0,
            0.5, 0.5, 0.5, btp1, btp2, btp3, 0.5, 0.5, 0.5, 0.9, 0.0, thz, 0.8]
    return "E " + " ".join(("%.8g" % v) if isinstance(v, float) else str(v) for v in vals)


def synth(n, seed=11):
    """b hemispheres: P = U^4 (so e_b(w) = w^0.25); others: P = U (e_x(w) = w).
    Hemispheres independent; the b fraction is R_b."""
    rng = random.Random(seed)
    lines = []
    for i in range(n):
        isb = rng.random() < B.RB
        if isb:
            p1, p2 = rng.random() ** 4, rng.random() ** 4
        else:
            p1, p2 = rng.random(), rng.random()
        lines.append(e_line(i + 1, p1, p2, min(p1, p2)))
    return lines


class TestSolve(unittest.TestCase):
    def exact(self, eb, ex, rho=0.0, rb=B.RB):
        fs = rb * eb + (1 - rb) * ex
        fd = rb * eb * eb * (1 + rho) + (1 - rb) * ex * ex
        return fs, fd

    def test_closed_form(self):
        for eb, ex in ((0.3, 0.01), (0.6, 0.05), (0.15, 0.001)):
            fs, fd = self.exact(eb, ex)
            b, x = B.solve(fs, fd)
            self.assertAlmostEqual(b, eb, places=10)
            self.assertAlmostEqual(x, ex, places=10)

    def test_rho(self):
        fs, fd = self.exact(0.35, 0.02, rho=0.03)
        b0, _ = B.solve(fs, fd, rho=0.0)
        b3, x3 = B.solve(fs, fd, rho=0.03)
        self.assertAlmostEqual(b3, 0.35, places=10)
        self.assertAlmostEqual(x3, 0.02, places=10)
        self.assertGreater(b0, b3)   # ignoring a positive correlation overestimates e_b

    def test_unphysical(self):
        self.assertEqual(B.solve(0.1, 0.0), (None, None))

    def test_pick_wp(self):
        pts = [(w, B.event_eff(w ** 0.25)) for w in B.WPS]
        w = B.pick_wp(pts)
        truth = (1 - math.sqrt(1 - 0.38)) ** 4      # 1-(1-w^.25)^2 = 0.38
        self.assertLess(abs(math.log(w / truth)), math.log(1.5))
        self.assertIsNone(B.pick_wp([(0.1, 0.9), (0.01, 0.8)]))


class TestCounting(unittest.TestCase):
    def test_synthetic_recovery(self):
        cnt = B.Counter()
        for ln in synth(100000):
            cnt.add(B.D.parse_e(ln))
        res = B.summarise(cnt.raw())
        for w in (0.01, 0.001):
            s = res["solution"][repr(w)]["rho_0"]
            self.assertLess(abs(s["e_b"] - w ** 0.25), max(4 * s["e_b_err"], 0.005), w)
            self.assertLess(abs(s["e_x"] - w), max(4 * s["e_x_err"], 0.002), w)
            self.assertGreater(s["e_b_err"], 0)
            self.assertLess(s["e_b_err"], 0.03)
        truth = (1 - math.sqrt(1 - 0.38)) ** 4
        wp = res["wp_hemisphere_for_event_eff_0.38"]
        self.assertLess(abs(math.log(wp / truth)), math.log(1.6))
        self.assertEqual(res["cutflow"]["hadronic"], 100000)

    def test_hadronic_and_bad_hemisphere(self):
        cnt = B.Counter()
        cnt.add(B.D.parse_e(e_line(1, 0.001, 0.5, ihad4=0)))
        cnt.add(B.D.parse_e(e_line(2, -1.0, 0.5)))
        cnt.add(B.D.parse_e(e_line(3, 0.001, 0.5)))
        raw = cnt.raw()
        self.assertEqual(raw["cutflow"]["events"], 3)
        self.assertEqual(raw["cutflow"]["hadronic"], 2)
        self.assertEqual(raw["n_bad_hemisphere"], 1)
        c = raw["counts"][repr(0.01)]
        self.assertEqual((c["n00"], c["n10"], c["n01"], c["n11"]), (0, 1, 0, 0))

    def test_files_and_combine(self):
        lines = synth(4000, seed=3)
        with tempfile.TemporaryDirectory() as d:
            for k, part in enumerate((lines[:2500], lines[2500:])):
                sub = os.path.join(d, "s%d" % k)
                os.mkdir(sub)
                with gzip.open(os.path.join(sub, "data_Y.%d.al.ev.txt.gz" % k), "wt") as fh:
                    fh.write("\n".join(part) + "\n")
                with gzip.open(os.path.join(sub, "mc_Z.%d.ev.txt.gz" % k), "wt") as fh:
                    fh.write("\n".join(part[:10]) + "\n")
                B.main(["--dir", sub, "--out", os.path.join(d, "c%d.json" % k)])
            B.main(["--combine", os.path.join(d, "c0.json"), os.path.join(d, "c1.json"),
                    "--out", os.path.join(d, "t.json")])
            B.main(["--dir", d, "--out", os.path.join(d, "all.json")])
            with open(os.path.join(d, "t.json")) as fh:
                t = json.load(fh)
            with open(os.path.join(d, "all.json")) as fh:
                a = json.load(fh)
        self.assertEqual(t["counts"], a["counts"])
        self.assertEqual(t["cutflow"]["events"], 4000)   # mc files are not counted as data
        self.assertEqual(t["solution"][repr(0.01)]["rho_0"]["e_b"],
                         a["solution"][repr(0.01)]["rho_0"]["e_b"])
        self.assertEqual(t["n_input_files"], 2)          # 0.1.0 kept only the first input's count
        self.assertEqual(t["n_combined"], 2)


class TestPeriods(unittest.TestCase):
    """0.2.0 (plan v0.8): one calibration per period; data and simulation never added."""

    def test_combine_refusals(self):
        lines = synth(600, seed=5)
        with tempfile.TemporaryDirectory() as d:
            with gzip.open(os.path.join(d, "data_Y.1.al.ev.txt.gz"), "wt") as fh:
                fh.write("\n".join(lines[:300]) + "\n")
            with gzip.open(os.path.join(d, "mc_Z.1.ev.txt.gz"), "wt") as fh:
                fh.write("\n".join(lines[300:]) + "\n")
            outs = {}
            for name, args in (("d93", ["--period", "y93"]), ("d94", ["--period", "y94"]),
                               ("d94b", ["--period", "y94"]),
                               ("m94", ["--period", "y94", "--sample", "mc"])):
                outs[name] = os.path.join(d, name + ".json")
                B.main(["--dir", d, "--out", outs[name]] + args)
            js = {}
            for name, p in outs.items():
                with open(p) as fh:
                    js[name] = json.load(fh)
            with self.assertRaises(SystemExit):
                B.main(["--dir", d, "--period", "y/94", "--out", os.path.join(d, "x.json")])
            with self.assertRaises(SystemExit):
                B.main(["--combine", outs["d94"], "--period", "y94", "--out", os.path.join(d, "x.json")])
        self.assertEqual(js["d93"]["period"], "y93")
        self.assertEqual(js["m94"]["sample"], "mc")
        self.assertEqual(js["d94"]["cutflow"]["events"], 300)
        self.assertEqual(js["m94"]["cutflow"]["events"], 300)
        t = B.combine([js["d94"], js["d94b"]])
        self.assertEqual(t["period"], "y94")
        self.assertEqual(t["cutflow"]["events"], 600)
        with self.assertRaises(ValueError):
            B.combine([js["d93"], js["d94"]])          # different periods
        with self.assertRaises(ValueError):
            B.combine([js["d94"], js["m94"]])          # data + simulation


if __name__ == "__main__":
    unittest.main()
