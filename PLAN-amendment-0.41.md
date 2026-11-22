# PLAN amendment v0.41: grading `leescan-v2` (global significance) and `toyres-ssframe-v3` (same-sign-constrained frame)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-22. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

This amendment grades two pre-registered jobs. Both finished on the Dell on 2026-11-22 and were read
for the first time in this run. No test, threshold, prior or blinding rule of plan v0.11 or amendments
0.12-0.40 is changed. Grades are copied from the jobs' own printed `LEEFAST:` / `LEESCAN:` /
`SSFRAME:` / `TOYRESUME:` lines and checked by hand against the definitions below.

Raw output is committed with this amendment:
- `analysis/results/leescan/leescan-v2/`: `run.txt`, `leescan.json`, `toys.csv`, `toydiag.csv`,
  `tests.txt`, `sha256.txt`, `fetch.txt`, `job.json`.
- `analysis/results/ssframe/toyres-v3/`: `run.txt`, `toyresume.json`, `toys.csv`, `tests.txt`,
  `sha256.txt`, `fetch.txt`, `job.json`.
- `analysis/results/significance-ladder-0.41.json`: the numbers below in one file. Every value is
  copied from the two outputs above.

## 1. `leescan-v2` (amendments 0.34 and 0.40): the look-elsewhere scan

The job ran from 16:17 to 16:47 UTC (1,812 s; 2 CPUs; peak 0.07 GB). It passed py_compile, the
sha256 fetch of the pinned leescan 0.1.0, and all **13** unit tests of `test_leefast`. The Newton
minimiser cost 1.47 s per toy per worker, against about 1,800 s in v1, so all 2,000 toys finished.
Neither the observed scan nor any toy fell back to L-BFGS-B or hit the iteration cap (0 / 0).

**Gate V (amendment 0.40): PASS.**
- V1: across the 375 observed grid Z values, the largest difference from v1 is 1.0e-6, and at
  30.40 GeV it is 1.5e-13.
- V2: the 36 toy maxima of toys 0-8 agree to 4.9e-6, and all 36 maxima occur at the same mass.
- V3: the toy truth agrees (r 0.63992, sum T 565.692).

| Grade | Definition (amendment 0.34) | Value | Grade | Prior |
|---|---|---|---|---|
| L0 | tests pass; closure 3.134 +- 0.01; scanner = discovery +- 0.002; >= 1,000 toys (+ gate V) | closure 3.1340, scanner 3.1340, 2,000 toys | **PASS** | 90 % (gate V 80 %) |
| L1 | primary E[N(1)] in [1.0, 2.6] | 1.603 +- 0.021 | **PASS** | 70 % |
| L2 | Gross-Vitells P(max Z >= 2) matches the direct toy rate within max(2 binomial sigma, 15 % relative) | GV 0.3805 vs direct 0.3285: difference 0.052, tolerance 0.057 | **PASS (narrow)** | 55 % |
| L3 (headline) | primary global Z of the 30.40 GeV excess (direct toy count) below 2.5 | 36 of 2,000 toys reach Z 3.134: p 0.018, **global Z 2.10** | **PASS** | 80 % |
| L4 | floated-width global Z below primary global Z | 1.92 < 2.10 | **PASS** | 70 % |
| L5 | observed primary scan peaks within 29-32 GeV | maximum 3.133 at 30.50 GeV | **PASS** | 60 % |

**L2 disclosure.** The wording of 0.34 does not say what the "15 % relative" is relative to. The
frozen code (`leescan.py` 0.1.0 line 211, public before the run) uses 15 % of the GV value, which gives
0.057. Taken as 15 % of the direct value, the tolerance would be 0.049 and L2 would FAIL. We grade by
the code that was fixed in advance. Because the margin is small, every Gross-Vitells extrapolation
below the toys' reach is labelled "GV" and treated as approximate. GV gives the larger p at Z = 2,
so here it errs on the conservative side.

**Global significance by width** (direct toy count; GV in brackets):

| Width | Local Z | Global p | Global Z |
|---|---|---|---|
| 1.0 GeV | 3.129 | 0.022 | 2.01 (GV 1.96) |
| **1.78 GeV (primary)** | **3.134** | **0.018** | **2.10 (GV 2.05)** |
| 3.0 GeV | 3.095 | 0.018 | 2.10 (GV 2.10) |
| best of the three | 3.134 | 0.0275 | 1.92 (GV 2.00) |

**The ladder.** This is the pre-registered conversion of each local Z from earlier amendments into a
global Z, using the primary width and the same toys:

| Background frame | Local Z | Global Z, GV | Global Z, direct |
|---|---|---|---|
| Heister, kernel-density background, as published | 5.35 | 4.65 | > 2.97 (0 of 2,000; bound only) |
| par3, constant ratio, toy-calibrated (aprime-smooth-v1) | 3.35 | 2.32 | 2.37 |
| b-bbar MC shape, asymptotic (aprime-aleph-v1) | 2.664 | 1.41 | 1.46 |
| par3 + fitted rising muon ratio (aprime-slsm-v2) | 2.295 | 0.84 | 0.95 |
| par3 + same-sign-constrained ratio (ssframe) | 2.134 | 0.56 | 0.67 |

Amendment 0.34 predicted about 2.0, 2.3, 4.6, 1.4, 0.8 and 0.5 for these rows. Every result is within
0.15 of its prediction.

## 2. `toyres-ssframe-v3` (amendments 0.30, 0.38, 0.39): the final resume

The job ran from 13:32 to 18:08 UTC (16,527 s; 4 CPUs; peak 0.08 GB). Setup, the fetch with the
FATAL sha256 list, py_compile and the unit tests all passed. The recheck re-ran 8 saved toys with
**0 mismatches**. The run stopped at its 16,000 s budget with **1,563 merged toys** (934 prior + 629
new), which is above the 1,000 that amendment 0.38 requires. No near-ties.

| Grade | Definition (amendment 0.30) | Value | Grade | Prior |
|---|---|---|---|---|
| P0 | gate: control, closures 3.1340 / 2.2953 / loose 2.2953, window 15-38 | all reproduced | **PASS** | 85 % |
| P1 | toy-calibrated Z0, same-sign-constrained slope, below 3.0 | 25 of 1,563 toys reach it: p 0.0160, **Z 2.145** | **PASS** | 90 % |
| P2 | ... below 2.0 | 2.145 | **FAIL** | 25 % |
| P3 | GOF of the constrained background-only fit, toy p >= 0.01 | p 0.705 | **PASS** | 85 % |
| P4 | toy rate of Z0 >= 2 in [0.012, 0.035] | 0.0205 | **PASS** | 70 % |

The asymptotic Z0 is 2.134 and the toy-calibrated value is 2.145, so the asymptotic formula holds for
this test. Amendment 0.38 disclosed a partial value, 20 of 934 toys (about 2.03 sigma), before this
resume ran. The final value moved to 2.145 with 1,563 toys. The constrained fit puts mu at 0.618 of the
template signal. With the slope fixed at the control value b_ctrl = 0.0345 per GeV, Z0 is 1.69.

## 3. What the two grades say together

Starting from the published ALEPH spectra (our figure readings) and a smooth background:
- With the muon-to-electron-muon ratio held constant, the 30.4 GeV excess is about 3.1-3.35 sigma
  local and **about 2.1 sigma global** after the scan over 17-48 GeV and three widths.
- Two frames let the ratio follow the data. In the fitted rising-ratio frame it is 2.3 sigma local
  (2.35 toy-calibrated, amendment 0.37). In the same-sign-constrained frame it is 2.1 sigma local.
  In both frames it is **under 1 sigma global**.
- Our look-elsewhere factor alone takes Heister's local 5.35 only to about 4.65 (GV, far beyond the
  toys). Over this scan range, then, the gap between "5 sigma" and "2 sigma" comes from the
  background model, not from the look-elsewhere correction.

## 4. Limits (unchanged, restated)

The inputs are readings of published figures, not ALEPH's events. The toy truth is the
constant-ratio par3 fit. Three widths stand in for a fully floated width. The scan covers 17-48 GeV,
not Heister's 15-50 GeV. GV conversions above about Z = 3 go beyond what 2,000 toys can check. No
physicist has checked any of this.

## 5. Next

- The significance article may now be written (amendment 0.38 sec. 4 condition met).
- `delphi-rootless-probe-v1` and `dimu-ntuple-rl-v1` stay queued. An independent detector (DELPHI open
  data) remains the only real test of the excess. The next amendment is 0.42.
