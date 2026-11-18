# PLAN amendment v0.15: grading of dimu-bbspur-v1 (the b-tagged background shape)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-18. Made with AI agents; not yet checked by a
physicist. CC BY 4.0 (text); code Apache-2.0.

This amendment is part of the pre-registration. It extends PLAN.md v0.11 and amendments 0.12,
0.13 and 0.14 and will be merged into PLAN.md v1.0. It is published **before any DELPHI dimuon
mass in the 26-35 GeV window has been seen**. No DELPHI data are used below. It changes no rule:
it records the grades of the expectations written in amendment 0.13, section 3.

## 1. What job dimu-bbspur-v1 returned

`stats/bbspur.py` 0.1.0 (with bkgsys 0.1.0 and forecast 0.1.1) ran on 2026-11-18 from 11:15 to
12:29 UTC. Both unit tests passed. It generated 1,000,000 Pythia 8 Z -> b bbar events (two seeds,
19,584 opposite-sign dimuon pairs, 4,797 in 15-50 GeV), the same sample as dimu-forecast-v2, and
scored the five background treatments of amendment 0.12 on noise-free (Asimov) pseudo-data of the
b-tagged spectrum (test A). Its 70-minute budget covered 9 of the 12 planned rows; the three it
skipped (the tilted, exponential and power-law truths at S1 yields) are not needed for any grade.
Outputs: `stats/results/bbspur/`.

"spur" is the fitted signal strength on background-only data, in units of an ALEPH-sized signal;
"sd" is spur divided by its statistical standard deviation sigma; "mh1" is the fitted strength
when an ALEPH-sized signal (mu = 1) is injected. Criterion (a): |spur| <= 0.2 sigma and
|mh1 - 1| <= 0.2 sigma.

| scenario (truth, yields) | rule degree | old: spur (sd), mh1 | fix3 | env |
|---|---|---|---|---|
| **C9** Pythia b bbar, S2 | 2 | **+0.520 (0.80), 1.542** | +0.018 (0.02), 1.015 | +0.018 (0.02), 1.015 |
| **C10** tilted Pythia, S2 | 2 | **+0.589 (0.82), 1.610** | -0.035 (-0.04), 0.958 | -0.035 (-0.04), 0.958 |
| **C11** Pythia b bbar, S4 | 2 | **+0.520 (1.11), 1.542** | +0.018 (0.03), 1.015 | -0.053 (-0.10), 0.937 |
| **C12** exponential 9 GeV, S2 | 2 | +0.126 (0.19), **1.132** | -0.001 (-0.00), 0.999 | +0.126 (0.19), **1.132** |
| power law m^-3, S2 (closure) | 1 | 0.000, 1.000 | 0.000, 1.000 | 0.000, 1.000 |
| extra: tilted Pythia, S4 | 3 | -0.035 (-0.06), 0.958 | -0.035 (-0.06), 0.958 | -0.065 (-0.11), 0.925 |
| extra: exponential, S4 | 2 | **+0.126 (0.27), 1.132** | -0.001 (-0.00), 0.999 | **+0.126 (0.27), 1.132** |
| extra: Pythia b bbar, S1 | 2 | **+0.520 (0.89), 1.542** | +0.018 (0.03), 1.015 | +0.018 (0.03), 1.015 |

(`env_min2` equals `env` in every row except the power law; `ss`, which uses the truth, is not
eligible and is shown in the outputs only.)

Spurious signal by fixed degree on the Pythia b bbar truth (S2): degree 1 +1.13, **2 +0.52**,
3 +0.02, 4 -0.05, 5 +0.06. These match the hand-copied forecast-v2 table in amendment 0.13 exactly.

## 2. Grades of the expectations written in amendment 0.13, section 3

| | expectation | result | grade |
|---|---|---|---|
| M1 | both unit tests pass, incl. the exact-power-law Asimov check | 2 of 2 ok; power law spur <= 0.0002, mh1 1.0001 for every treatment | **PASS** |
| M2 | C9: rule picks degree 2, old spur +0.45 to +0.60, mh1 1.45-1.62 | degree 2, +0.520, 1.5415 | **PASS** |
| M3 | old fails (a) in C9 | 0.80 sigma | **PASS** |
| M4 | fix3 passes (a) in C9 and C12 | 0.02 sigma, mh1 1.015; 0.00 sigma, mh1 0.999 | **PASS** |
| M5 | env passes (a) in C9 (prior about 70 %) | 0.02 sigma, mh1 1.015 | **PASS** |
| M6 | in C11 the sideband rule picks degree 3 or more (prior about 60 %) | it picks **degree 2** again; spur 1.11 sigma | **FAIL** |

**What M6 means.** With the 1992-95 yields (S4, 1,865 background events in the window) the
pre-registered sideband rule still keeps degree 2 on the realistic Pythia shape, and the bias
grows to 1.11 standard deviations because the statistical error shrinks while the shape bias
does not. More data do not rescue the old rule; it is out for good (it already was, since
amendment 0.14).

## 3. What the decision rule now says

Amendment 0.13 made criterion (a) apply in C1-C12. Over C9-C12:

- **fix3 passes in all four** (largest |spur| 0.04 sigma, largest |mh1 - 1| 0.042, in C10), and in
  every extra row. Together with amendment 0.14 (C1-C8), fix3 passes criterion (a) in all twelve
  scenarios.
- `env` passes in C9, C10 and C11, and sits at the edge in C12 (0.19 sigma; |mh1 - 1| = 0.132
  against 0.2 sigma = 0.130). With the 1992-95 yields the same exponential truth gives it 0.27
  sigma. It was already ineligible (amendment 0.14, C6 test B).
- `old` fails in C9, C10 and C11.

So nothing changes: **fix3 stays the only eligible treatment** and becomes the background
treatment of plan v1.0 if it passes criterion (b) in job `dimu-envtoys-v1` (expectations N0-N5,
amendment 0.14, still queued). The combined test-B Asimov run in C2 with the C9 truth in the tagged
category (amendment 0.13, section 2) will be made with fix3 before the freeze. On the evidence
here its tagged-category spurious signal is about +0.02 of an ALEPH-sized signal.

The price stays as stated in 0.14: degree 3 everywhere loses about 10-15 % in expected
sensitivity against the (biased) lower degrees.

## 4. Status of the other jobs

Returned since 0.14: `efhz-v1` (graded in NOTE-higgs-searches.md 0.3, J1-J7). Still waiting for
compute: `dimu-envtoys-v1`, `lephz-v1`, and the DELPHI open-data jobs (`delphi-probe-v1`,
`dimu-ntuple-v1`, `delsim-signal-v1`, `dimu-val9293-v1`, `dimu-fourf-v1`).
