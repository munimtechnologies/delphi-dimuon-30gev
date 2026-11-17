"""Tests for validate.py (MV2 of Munim, Inc.; made with AI agents; Apache-2.0)."""
import gzip
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate as V  # noqa: E402


def e_line(run, evt, ihad4=1, nctr4=12, nlep=2, btp3=0.001):
    ints = [run, evt, ihad4, nctr4, nctr4 + 1, 40, nlep]
    reals = [91.2, 40.0, 20.0, 10.0, 0.5, 0.5, 0.2, 0.3, 0.3, btp3, 0.4, 0.4, 0.1, 0.0, 0.0, 1.0, 0.9]
    return "E" + "".join(" %10d" % x for x in ints) + "".join(" %13.5E" % x for x in reals)


def p_line(run, evt, i, q, px, py, pz, kmu=4, kel=0, lock=0):
    p = math.sqrt(px * px + py * py + pz * pz)
    ints = [run, evt, i, q, lock, kmu, 7, kel, 0, 2, 2]
    reals = [px, py, pz, math.sqrt(p * p + 0.0195), 1.0, 0.01, 0.02, 0.003, 0.004, 0.005]
    return "P" + "".join(" %11d" % x for x in ints) + "".join(" %13.5E" % x for x in reals)


class TestParse(unittest.TestCase):
    def test_e_roundtrip(self):
        d = V.parse_e(e_line(1234, 56, btp3=0.0042))
        self.assertEqual(d["run"], 1234)
        self.assertEqual(d["evt"], 56)
        self.assertAlmostEqual(d["btp3"], 0.0042, places=6)
        self.assertAlmostEqual(d["thr"], 0.9, places=6)

    def test_p_roundtrip(self):
        d = V.parse_p(p_line(1, 2, 3, -1, 3.0, 4.0, 0.0))
        self.assertEqual(d["q"], -1)
        self.assertAlmostEqual(d["p"], 5.0, places=4)
        self.assertEqual(d["kmu1"], 4)

    def test_bad_lines(self):
        self.assertIsNone(V.parse_e("E 1 2 3"))
        self.assertIsNone(V.parse_p("X"))
        bad = p_line(1, 2, 3, -1, 3.0, 4.0, 0.0).split()
        bad[5] = "***********"
        self.assertIsNone(V.parse_p(" ".join(bad)))


class TestPhysics(unittest.TestCase):
    def test_back_to_back_mass(self):
        a = V.parse_p(p_line(1, 1, 1, 1, 0, 0, 45.0))
        b = V.parse_p(p_line(1, 1, 2, -1, 0, 0, -45.0))
        m = V.pair_mass(a, b)
        self.assertAlmostEqual(m, 2 * math.sqrt(45.0 ** 2 + V.MMU ** 2), places=3)

    def test_jpsi_like_mass(self):
        # two muons with 3.0969/2 GeV each in the J/psi rest frame, along x
        pst = math.sqrt((3.0969 / 2) ** 2 - V.MMU ** 2)
        a = V.parse_p(p_line(1, 1, 1, 1, pst, 0, 0))
        b = V.parse_p(p_line(1, 1, 2, -1, -pst, 0, 0))
        self.assertAlmostEqual(V.pair_mass(a, b), 3.0969, places=3)

    def test_muon_levels(self):
        self.assertTrue(V.is_muon({"kmu1": 4}, "standard"))
        self.assertFalse(V.is_muon({"kmu1": 3}, "standard"))
        self.assertTrue(V.is_muon({"kmu1": 1}, "any"))
        self.assertFalse(V.is_muon({"kmu1": 0}, "any"))


class TestBlinding(unittest.TestCase):
    def test_data_hadronic_high_mass_withheld(self):
        a = V.parse_p(p_line(1, 1, 1, 1, 15.0, 0, 0))
        b = V.parse_p(p_line(1, 1, 2, -1, 0, 15.0, 0))
        self.assertIsNone(V.blinded_mass(a, b, True, 12))
        self.assertIsNotNone(V.blinded_mass(a, b, False, 12))   # simulation
        self.assertIsNotNone(V.blinded_mass(a, b, True, 2))     # low multiplicity

    def test_end_to_end_no_window_mass_in_output(self):
        with tempfile.TemporaryDirectory() as d:
            # one data event with a ~30 GeV pair (must never appear), one with a J/psi
            pst = math.sqrt((3.0969 / 2) ** 2 - V.MMU ** 2)
            ev = [e_line(1, 1), e_line(1, 2)]
            pa = [p_line(1, 1, 1, 1, 15.0, 0, 0), p_line(1, 1, 2, -1, 0, 15.0, 0),
                  p_line(1, 2, 1, 1, pst, 0, 5.0), p_line(1, 2, 2, -1, -pst, 0, 5.0)]
            with gzip.open(os.path.join(d, "data_x.ev.txt.gz"), "wt") as f:
                f.write("\n".join(ev) + "\n")
            with gzip.open(os.path.join(d, "data_x.pa.txt.gz"), "wt") as f:
                f.write("\n".join(pa) + "\n")
            out = os.path.join(d, "v.json")
            subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate.py"),
                            "--dir", d, "--out", out], check=True, capture_output=True)
            r = json.load(open(out))["data"]
            self.assertEqual(r["blind_pairs_not_computed"], 1)
            # the second pair is a J/psi moving along z: m = 3.0969 GeV, bin 2.0 + 10*0.1
            self.assertEqual(r["jpsi_any"]["n"], 1)
            self.assertEqual(r["jpsi_standard"]["hist_2_4p5_0p1"][10], 1)
            self.assertNotIn("mc_os_dimuon_had_0_50_2p5gev", r)
            self.assertNotIn("30.", json.dumps(r["jpsi_any"]))


if __name__ == "__main__":
    unittest.main()
