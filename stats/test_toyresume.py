# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Unit tests for toyresume 0.1.0's pure helpers, on made-up toys only."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import toyresume as tr  # noqa: E402

SLSM = ("idx,slope,const,dev0,mu,b0\n0,0.00000,1.05069,71.93847,0.00000,0.02816\n"
        "1,2.50000,1.08416,87.41746,0.70000,0.03188\n")
SSF = "idx,Z0,mu,b0,b_aux,dev0\n0,0.00000,0.00000,0.03263,0.01970,82.55328\n"


class TestCsv(unittest.TestCase):
    def test_parse_and_format_roundtrip(self):
        rows = tr.parse_csv(SLSM, "slsm")
        self.assertEqual([r["idx"] for r in rows], [0, 1])
        self.assertAlmostEqual(rows[1]["slope"], 2.5)
        self.assertEqual(tr.format_rows(rows, "slsm"), SLSM)
        rows = tr.parse_csv(SSF, "ssframe")
        self.assertEqual(tr.format_rows(rows, "ssframe"), SSF)

    def test_wrong_header(self):
        with self.assertRaises(ValueError):
            tr.parse_csv(SSF, "slsm")

    def test_contiguous(self):
        self.assertTrue(tr.contiguous([{"idx": 0}, {"idx": 1}, {"idx": 2}]))
        self.assertFalse(tr.contiguous([{"idx": 0}, {"idx": 2}]))
        self.assertFalse(tr.contiguous([{"idx": 1}]))
        self.assertTrue(tr.contiguous([]))


class TestCompare(unittest.TestCase):
    def test_match_within_rounding(self):
        saved = tr.parse_csv(SLSM, "slsm")
        fresh = [dict(r) for r in saved]
        fresh[0]["const"] = 1.050694      # rounds to the saved 1.05069
        fresh[1]["dev0"] = 87.417456      # rounds to 87.41746
        self.assertEqual(tr.compare(saved, fresh, "slsm"), [])

    def test_mismatch(self):
        saved = tr.parse_csv(SLSM, "slsm")
        fresh = [dict(r) for r in saved]
        fresh[1]["slope"] = 2.6
        bad = tr.compare(saved, fresh, "slsm")
        self.assertEqual(len(bad), 1)
        self.assertEqual(bad[0][:2], (1, "slope"))
        fresh[0]["idx"] = 5
        self.assertEqual(tr.compare(saved, fresh, "slsm")[0][1], "idx")

    def test_near_ties(self):
        rows = tr.parse_csv(SLSM, "slsm")
        self.assertEqual(tr.near_ties(rows, "slsm", {"slope": 2.500004, "const": 3.0}),
                         {"slope": 1, "const": 0})
        self.assertEqual(tr.near_ties(rows, "slsm", {"slope": None}), {})


if __name__ == "__main__":
    unittest.main()
