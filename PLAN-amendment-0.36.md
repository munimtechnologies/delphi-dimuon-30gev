# PLAN amendment v0.36: abtag-v1 graded (inverted b-tag): no common drift shown, no 30 GeV excess without the b-tag; undecided stays undecided

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-21. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `abtag-v1` returned (pre-registered in amendment 0.31
sec. 3, data committed in 0.32 sec. 4). `toyres-slsm-v1`, `toyres-ssframe-v1` (0.32),
`delphi-rootless-probe-v1` (0.33), `leescan-v1` (0.34) and `dimu-ntuple-rl-v1` (0.35) are still
queued and have returned nothing. No test, threshold, prior or blinding rule of plan v0.11 or
amendments 0.12-0.35 is changed.

## 1. The run

Job `abtag-v1`, Blade, 2026-11-21 16:17-16:19 UTC, 1 CPU. Code fetched from the repository and
hash-checked: `stats/abtag.py` 0.1.0 (sha256 `fbdddccb...`), `aprime_cross.py` and `dmcratio.py`
identical to the ones `sscontrol-v1` ran. 36 unit tests pass. Raw output: `analysis/results/abtag/v1/`
(`abtag.json`, `run.txt`, `tests.txt`, `sha256.txt`, `fetch.txt`, `job.json`; py_compile printed nothing).

## 2. Grades (amendment 0.31 sec. 3)

| test | statement | prior | result |
|---|---|---|---|
| A0 | gate: C0 passes, b_SS reproduced within 0.001, window reaches >= 30 GeV, data whole, non-negative, >= 100 events | 75 % | **PASS** (C0 Z0 2.664 / 1.621, b_SS 0.03873 exactly, window 15-43 GeV, 28 bins, 421 events, whole, non-negative) |
| A1 | main: b_A > 0 and Z_A >= 2.0 | 40 % | **FAIL** (b_A = 0.0095 +- 0.0130 per GeV, Z_A 0.73) |
| A2 | abs(b_A - b_SS) / hypot(sigma_A, sigma_SS) < 2.0 | 80 % | **PASS** (pull -1.28) |
| A3 | drift specific to b-tagged events: Z_A < 1.0 and (b_SS - b_A)/hypot >= 2.0 | 15 % | **FAIL** (Z_A < 1 holds, but the separation is 1.28 < 2.0) |
| A4 | no 30 GeV excess with the tag inverted: slope-free Z0 < 2.0 | 85 % | **PASS** (Z0 = 0.000, mu_hat = 0; constant ratio also 0.000) |

These are the grades the hand estimate written in 0.32 sec. 4 (before the job ran) expected:
A1 FAIL, A2 PASS, A3 FAIL, A4 PASS.

**Always-reported numbers.** Data / simulation: 331 / 317.2 = 1.044 at 15-25 GeV and 90 / 76.8 = 1.172
at 25-43 GeV. b_A 68 % interval [-0.0035, 0.0225]. Information only (simulation weighted 2.2x, as in
0.31 sec. 2): A b = 0.0094, Z 0.86; SS b = 0.0393, Z 2.49; OS b = 0.0237, Z 1.94.

## 3. What it means (the consequence fixed in 0.31 sec. 3)

**A1 FAIL + A2 PASS: the inverted-tag sample cannot tell; undecided stays undecided.** ALEPH's
events that fail the b-tag rise against ALEPH's simulation by less than the same-sign pairs do, but
the sample is too small to tell "no drift" (0.7 sigma from zero) from "the same drift" (1.3 sigma from
b_SS). So:

- The same-sign drift of 0.31 remains **not established** (W2 FAIL stands). ssframe's P1/P2, when
  graded, stay **conditional** on that drift, as 0.31 sec. 1 required. The unconditional wording
  needed A1 + A2 PASS and is not available.
- A3 FAIL: the drift is **not shown to be confined to b events** either; the muon-identification
  explanation is neither supported nor disfavoured.
- A4 PASS: with the tag inverted, there is **no excess at 30 GeV** (best-fit signal exactly zero),
  in line with Heister's statement for this figure. This is a consistency check of the reading and
  of the fit, not evidence for or against the tagged excess.
- As 0.31 said: no number here says whether the excess is real. Only DELPHI's open data can.

## 4. Information only (computed after the grades; not a test)

An inverse-variance mean of the two control slopes, b_SS = 0.0387 +- 0.0187 and b_A = 0.0095 +-
0.0130, is 0.0190 +- 0.0107 per GeV (1.8 sigma from zero; the two agree, chi2 1.65 for 1 degree of
freedom). It is below the opposite-sign signal-free slope b_mu0 = 0.0266. We do **not** use this
combined slope in any test, because combining the controls was not pre-registered. It is reported
so that a reader can see that the two control samples together point the same way the same-sign
one did, at the same weak level.

## 5. Article status

No article for this grade: an inconclusive control test is not a result. The significance article
(slug `aleph-30-gev-excess-with-its-template-error`) still waits for `toyres-slsm`,
`toyres-ssframe` (>= 1,000 toys each) and `leescan-v1`. Its wording is now fixed in one respect:
ssframe's numbers are stated as conditional on a same-sign drift that two control samples suggest
(1.8 sigma combined, information only) but do not establish.

## 6. Limits

A single blind reading by an AI agent of a published figure, not ALEPH's events; data markers
missing at 36, 37, 39 and 43-49 GeV were read as zero (NM -> 0, rule of 0.31); the simulation as
pseudo-counts at the data's size; one log-linear drift shape; no look-elsewhere correction.
