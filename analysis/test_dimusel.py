"""Tests for dimusel (blinding, categories, cuts, jets, unblind gate).
MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0."""
import gzip
import json
import math
import os
import tempfile
import unittest

import dimusel as D

MMU = D.MMU
MEL = D.MEL


def e_line(run=1000, evt=1, ihad4=1, nctr4=12, btp3=0.001, thz=0.1):
    vals = [run, evt, ihad4, nctr4, nctr4, 30, 2, 91.2, 50.0, 20.02,10.0,
            0.5, 0.5, 0.5, 0.5, 0.5, btp3, 0.5, 0.5, 0.5, 0.9, 0.0, thz, 0.8]
    return "E " + " ".join(str(v) for v in vals)


def p_line(run, evt, i, q, px, py, pz, e, kmu1=0, kel1=0, d0=0.01, z0=0.02):
    ints = [run, evt, i, q, 0, kmu1, 0, kel1, 0, 2, 2]
    reals = [px, py, pz, e, 1.0, 0.0, 0.0, d0, z0, d0]
    return "P " + " ".join(str(v) for v in ints) + " " + " ".join("%.6f" % v for v in reals)


def pair_momenta(m, p=20.0, mass=MMU, mass2=None):
    """Two tracks of momentum p in the x-y plane with invariant mass m."""
    m2 = mass if mass2 is None else mass2
    e1 = math.sqrt(p * p + mass * mass)
    e2 = math.sqrt(p * p + m2 * m2)
    cth = (mass * mass + m2 * m2 + 2 * e1 * e2 - m * m) / (2 * p * p)
    sth = math.sqrt(max(0.0, 1 - cth * cth))
    return (p, 0.0, 0.0), (p * cth, p * sth, 0.0)


def make_event(run, evt, m, q1=-1, q2=1, flav=("mu", "mu"), balance=True, extra=()):
    masses = {"mu": MMU, "e": MEL}
    a, b = pair_momenta(m, mass=masses[flav[0]], mass2=masses[flav[1]])
    lines = []
    for i, (v, q, f) in enumerate(((a, q1, flav[0]), (b, q2, flav[1])), start=1):
        p = math.sqrt(sum(x * x for x in v))
        lines.append(p_line(run, evt, i, q, v[0], v[1], v[2], math.sqrt(p * p + masses[f] ** 2),
                            kmu1=1 if f == "mu" else 0, kel1=4 if f == "e" else 0))
    sx, sy, sz = a[0] + b[0], a[1] + b[1], a[2] + b[2]
    k = 3
    for v in extra:
        lines.append(p_line(run, evt, k, 0, v[0], v[1], v[2], math.sqrt(sum(x * x for x in v))))
        sx += v[0]; sy += v[1]; sz += v[2]
        k += 1
    if balance:
        # two neutral "jets" balancing the event, along -z/+z tilted to keep them far from leptons
        bx, by, bz = -sx, -sy, -sz
        lines.append(p_line(run, evt, k, 0, bx, by, bz + 15.0, math.sqrt(bx * bx + by * by + (bz + 15) ** 2)))
        lines.append(p_line(run, evt, k + 1, 0, 0.0, 0.0, -15.0, 15.0))
    return lines


def fine_bin(m):
    return int((m - D.FINE_LO) / D.FINE_BW)


class Base(unittest.TestCase):
    def run_sel(self, events, is_data=True, unblind=False, cfg=None):
        sel = D.Selector(cfg, unblind=unblind)
        for e, parts in events:
            sel.process_event(D.parse_e(e), [D.parse_p(p) for p in parts], is_data)
        return sel.result()["samples"]["data" if is_data else "mc"]


class TestParse(unittest.TestCase):
    def test_parse_e_p(self):
        e = D.parse_e(e_line())
        self.assertEqual(e["run"], 1000)
        self.assertAlmostEqual(e["btp3"], 0.001)
        p = D.parse_p(p_line(1, 2, 3, -1, 3.0, 4.0, 0.0, 5.0, kmu1=4))
        self.assertAlmostEqual(p["p"], 5.0)
        self.assertEqual(p["kmu1"], 4)
        self.assertIsNone(D.parse_e("E 1 2 3"))
        self.assertIsNone(D.parse_p("P ***"))

    def test_pair_mass(self):
        for m in (3.1, 20.02,30.4, 45.0):
            a, b = pair_momenta(m)
            ta = D.parse_p(p_line(1, 1, 1, 1, *a, 0.0))
            tb = D.parse_p(p_line(1, 1, 2, -1, *b, 0.0))
            self.assertAlmostEqual(D.pair_mass(ta, tb, MMU, MMU), m, places=4)


class TestBlinding(Base):
    def test_window_data_btag_hidden(self):
        r = self.run_sel([(e_line(), make_event(1000, 1, 30.42))])
        c = r["categories"]["os_mumu_btag"]
        self.assertTrue(c["blinded"])
        self.assertNotIn("n_15_50", c)
        self.assertIsNone(c["fine"][fine_bin(30.42)])
        self.assertEqual(sum(x for x in c["fine"] if x is not None), 0)
        self.assertEqual(sum(x for x in c["coarse"] if x is not None), 0)
        self.assertEqual(r["cutflow"]["pmiss_pass"], 1)

    def test_all_os_same_flavour_blind(self):
        evs = [(e_line(evt=1, btp3=0.5), make_event(1000, 1, 30.02)),
               (e_line(evt=2, btp3=0.001), make_event(1000, 2, 30.02, flav=("e", "e")))]
        r = self.run_sel(evs)
        for cat in ("os_mumu_untagged", "os_mumu_antitag", "os_ee_btag"):
            c = r["categories"][cat]
            self.assertEqual(sum(x for x in c["fine"] if x is not None), 0, cat)

    def test_window_edges(self):
        r = self.run_sel([(e_line(evt=1), make_event(1000, 1, 25.97)),
                          (e_line(evt=2), make_event(1000, 2, 26.01)),
                          (e_line(evt=3), make_event(1000, 3, 35.02))])
        f = r["categories"]["os_mumu_btag"]["fine"]
        self.assertEqual(f[fine_bin(25.97)], 1)
        self.assertIsNone(f[fine_bin(26.01)])
        self.assertEqual(f[fine_bin(35.02)], 1)
        self.assertEqual(sum(x for x in f if x is not None), 2)

    def test_sideband_visible(self):
        r = self.run_sel([(e_line(), make_event(1000, 1, 20.02))])
        self.assertEqual(r["categories"]["os_mumu_btag"]["fine"][fine_bin(20.02)], 1)

    def test_controls_open(self):
        evs = [(e_line(evt=1), make_event(1000, 1, 30.02, q1=1, q2=1)),
               (e_line(evt=2), make_event(1000, 2, 30.02, flav=("mu", "e")))]
        r = self.run_sel(evs)
        self.assertEqual(r["categories"]["ss_mumu_btag"]["fine"][fine_bin(30.02)], 1)
        self.assertEqual(r["categories"]["os_emu_btag"]["fine"][fine_bin(30.02)], 1)
        self.assertEqual(r["categories"]["os_emu_btag"]["n_15_50"], 1)

    def test_mc_open(self):
        r = self.run_sel([(e_line(run=-1001), make_event(-1001, 1, 30.42))], is_data=False)
        c = r["categories"]["os_mumu_btag"]
        self.assertFalse(c["blinded"])
        self.assertEqual(c["fine"][fine_bin(30.42)], 1)

    def test_unblind_flag(self):
        r = self.run_sel([(e_line(), make_event(1000, 1, 30.42))], unblind=True)
        self.assertEqual(r["categories"]["os_mumu_btag"]["fine"][fine_bin(30.42)], 1)

    def test_unblind_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "PLAN.md")
            with open(p, "w") as fh:
                fh.write("# Analysis plan v0.5: does DELPHI see ALEPH's 30 GeV dimuon excess?\n")
            with self.assertRaises(SystemExit):
                D.check_unblind_plan(p)
            with open(p, "w") as fh:
                fh.write("# Analysis plan v1.0: frozen\n")
            self.assertEqual(len(D.check_unblind_plan(p)), 64)


class TestCuts(Base):
    def test_pmiss_veto(self):
        r = self.run_sel([(e_line(), make_event(1000, 1, 20.02,balance=False))])
        self.assertEqual(r["cutflow"]["pmiss_pass"], 0)
        self.assertEqual(r["categories"]["os_mumu_btag"]["fine"][fine_bin(20.02)], 0)

    def test_hadronic_cuts(self):
        evs = [(e_line(evt=1, ihad4=0), make_event(1000, 1, 20.02)),
               (e_line(evt=2, nctr4=4), make_event(1000, 2, 20.02)),
               (e_line(evt=3, thz=5.0), make_event(1000, 3, 20.02)),
               (e_line(evt=4), make_event(1000, 4, 20.02))]
        r = self.run_sel(evs)
        cf = r["cutflow"]
        self.assertEqual((cf["events"], cf["ihad4"], cf["nctr4"], cf["hadronic"]), (4, 3, 2, 1))
        self.assertEqual(r["categories"]["os_mumu_btag"]["fine"][fine_bin(20.02)], 1)

    def test_btag_split(self):
        evs = [(e_line(evt=1, btp3=0.5), make_event(1000, 1, 20.02))]
        r = self.run_sel(evs)
        self.assertEqual(r["categories"]["os_mumu_btag"]["fine"][fine_bin(20.02)], 0)
        self.assertEqual(r["categories"]["os_mumu_untagged"]["fine"][fine_bin(20.02)], 1)
        self.assertEqual(r["categories"]["os_mumu_antitag"]["fine"][fine_bin(20.02)], 1)
        self.assertEqual(r["cutflow"]["antitag"], 1)

    def test_isolation(self):
        # a 10 GeV neutral 5 degrees from muon 1 (along +x) makes it non-isolated
        ang = math.radians(5)
        near = (10 * math.cos(ang), 0.0, 10 * math.sin(ang))
        r1 = self.run_sel([(e_line(), make_event(1000, 1, 20.02))], is_data=False)
        r2 = self.run_sel([(e_line(), make_event(1000, 1, 20.02,extra=(near,)))], is_data=False)
        self.assertEqual(r1["categories"]["os_mumu_btag_iso"]["fine"][fine_bin(20.02)], 1)
        self.assertEqual(r2["categories"]["os_mumu_btag_iso"]["fine"][fine_bin(20.02)], 0)
        self.assertEqual(r2["categories"]["os_mumu_btag"]["fine"][fine_bin(20.02)], 1)

    def test_lepton_cuts(self):
        lines = make_event(1000, 1, 20.02)
        p = D.parse_p(lines[0])
        c = dict(D.DEFAULTS)
        self.assertTrue(D.lepton_ok(p, c))
        c["d0_max"] = 0.001
        self.assertFalse(D.lepton_ok(p, c))
        with self.assertRaises(ValueError):
            D.Selector({"no_such_cut": 1})


class TestJets(unittest.TestCase):
    def test_antikt(self):
        parts = [[10, 10, 0, 0], [1, math.cos(0.1), math.sin(0.1), 0], [8, -8, 0, 0]]
        jets = D.antikt_jets(parts, 0.4)
        self.assertEqual(len(jets), 2)
        self.assertAlmostEqual(jets[0][0], 11.0)
        jets = D.antikt_jets(parts, 0.05)
        self.assertEqual(len(jets), 3)


class TestEndToEnd(unittest.TestCase):
    def test_main(self):
        with tempfile.TemporaryDirectory() as d:
            for tag, run in (("data", 1000), ("mc", -1001)):
                ev = [e_line(run=run, evt=1), e_line(run=run, evt=2)]
                pa = make_event(run, 1, 30.42) + make_event(run, 2, 18.02)
                with gzip.open(os.path.join(d, "%s_X.al.ev.txt.gz" % tag), "wt") as fh:
                    fh.write("\n".join(ev) + "\n")
                with gzip.open(os.path.join(d, "%s_X.al.pa.txt.gz" % tag), "wt") as fh:
                    fh.write("\n".join(pa) + "\n")
            out = os.path.join(d, "o.json")
            D.main(["--dir", d, "--out", out])
            with open(out) as fh:
                res = json.load(fh)
            data = res["samples"]["data"]["categories"]["os_mumu_btag"]["fine"]
            mc = res["samples"]["mc"]["categories"]["os_mumu_btag"]["fine"]
            self.assertIsNone(data[fine_bin(30.42)])
            self.assertEqual(data[fine_bin(18.02)], 1)
            self.assertEqual(mc[fine_bin(30.42)], 1)
            self.assertEqual(res["samples"]["data"]["files"], 1)
            self.assertFalse(res["unblinded"])


if __name__ == "__main__":
    unittest.main()
