# PLAN amendment v0.37: toyres-slsm-v1 graded (1,584 toys): with a rising muon/electron-muon ratio the ALEPH 30 GeV excess is 2.35 sigma local, not 3.1; the constant-ratio 3.13 sigma is worth 1.93 sigma if the ratio really rises

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-22. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `toyres-slsm-v1` returned (resume rule of amendment
0.32 sec. 3; tests of amendment 0.27 sec. 6). `toyres-ssframe-v1` (0.32), `delphi-rootless-probe-v1`
(0.33), `leescan-v1` (0.34) and `dimu-ntuple-rl-v1` (0.35) are still queued and have returned
nothing. No test, threshold, prior or blinding rule of plan v0.11 or amendments 0.12-0.36 is changed.

## 1. The run

Job `toyres-slsm-v1`, Dell, 2026-11-21 19:46 to 2026-11-22 00:19 UTC (16,377 s), 2 CPUs, peak memory
0.08 GB. `stats/toyresume.py` 0.1.0 imported `aprime_slsm.py` 0.1.0, `aprime_smooth.py` 0.1.0 and
`slsm_chunk.py` 0.1.0 from the repository, every sha256 matching (`fetch.txt`). Prior: the 869-toy
prefix of `aprime-slsm-v2` (`analysis/results/aprime-slsm/v2-partial/toys.csv`, sha256 `6ed3681d...`).
6 unit tests pass; py_compile printed nothing.

- **Recheck PASS**: toys 0-7 re-run from their seeds, 0 mismatches against the saved values.
- Toys 869-1583 run strictly in order; the job stopped at its 16,000 s budget with a contiguous
  merged prefix of **1,584** toys (>= 1,000, so under 0.32 sec. 3 this is the graded calibration;
  no further resume of this kind is filed).
- `near_ties`: 0 (slope) and 0 (constant), so the 5-decimal rounding of the prior file changes no count.

Raw output: `analysis/results/toyres-slsm/v1/` (`toyresume.json`, `toys.csv`, `run.txt`, `tests.txt`,
`sha256.txt`, `fetch.txt`, `compile.txt`, `job.json`).

## 2. Grades (amendment 0.27 sec. 6)

| test | statement | prior | result |
|---|---|---|---|
| L0 | gate: with b = 0 the new likelihood and ParFit both give par3's Z0 = 3.1340 within 0.005 | 90 % | **PASS** (3.1340 / 3.1340) |
| L1 | main: slope free, toy-calibrated Z0 < 3.0 | 85 % | **PASS** (Z0 2.295 asymptotic; 15 of 1,584 toys reach it, p = 0.0095, **calibrated Z = 2.35**) |
| L2 | slope free, toy-calibrated Z0 < 2.0 | 45 % | **FAIL** (2.35) |
| L3 | at zero signal b > 0 with signed Z >= 2.0 against a constant ratio | 70 % | **PASS** (b = 0.0266 per GeV, 68 % [0.0149, 0.0384], Z 2.26) |
| L4 | toys' rate of Z0 >= 2 (slope free) in [0.012, 0.035] | 80 % | **PASS** (0.0234) |
| L5 | deviance of the mu = 0 slope fit has toy p >= 0.01 | 85 % | **PASS** (55.20; 1,107 of 1,584 toys larger, p = 0.70) |

Counting uncertainty of the main number: 15 toys of 1,584 gives p between about 0.0071 and 0.0119
(+-1 sigma Poisson on k), i.e. calibrated Z between about 2.26 and 2.45. L1 and L2 are decided at
any value in that range.

**Always-reported numbers.** b = 0 (constant ratio): Z0 3.134, mu_hat 0.801. Slope free: Z0 2.295,
mu_hat 0.690, b_hat 0.0107. Slope with the signal floated: b 0.0107, signed Z 0.73. Constant-ratio
Z0 3.134 calibrated on the slope-truth toys: **42 of 1,584 reach it, p = 0.0265, Z = 1.93**. Toy
rates, slope free: Z0 >= 2 in 2.34 %, >= 3 in 0.13 %, mean 0.36; constant ratio on the same toys:
>= 2 in 17.2 %, >= 3 in 3.3 %, mean 1.14. Background under 29-32 GeV in the slope truth: 23.2
against 33 events observed.

What the partial prefix had shown (disclosed in 0.32 sec. 1): 11 of 869 toys (p 0.0127, Z 2.24) and
25 of 869 for the constant ratio (Z 1.90). The 715 new toys moved the numbers by less than their
counting error.

## 3. What it means (the consequence fixed in 0.27 sec. 6)

**L1 and L3 both pass**, so the pre-written meaning applies: the excess clears 3 sigma only if the
mu mu / e mu ratio is assumed constant. The data favour a rising ratio (2.26 sigma at zero signal),
and under it the excess is **2.35 sigma local** (toy-calibrated). The 3.1-3.4 sigma figures depend on
an assumption the data disfavour. Seen from the other side: if the ratio really rises as fitted,
background alone gives a constant-ratio excess as large as ALEPH's figure shows in 2.7 % of
pseudo-experiments (1.93 sigma).

**L2 FAIL** (the less likely outcome was "passes", prior 45 %): with a smooth background the excess
does not fall below 2 sigma local. The earlier 1.62 sigma with a bin-by-bin background and a rising
ratio (aprime-ext-v1) therefore owed part of its reduction to the freedom of the bin-by-bin
background, as 0.27 anticipated in the opposite case for L1. The smooth-background, rising-ratio
number 2.35 is the one we will quote as the local significance in this frame.

**L4 and L5 PASS**: the asymptotic formula is accurate here (2.34 % of toys reach 2 sigma against
2.28 % expected) and the background model describes the spectrum (p = 0.70).

In every case (0.27): a broad rise and a narrow peak partly substitute for each other, so a free slope
also absorbs some of any real signal. **These are local significances; no look-elsewhere correction
is applied** (that is `leescan-v1`, still queued). Only DELPHI's data, which ALEPH did not use, can
show whether the excess is real.

## 4. Where the ALEPH-side numbers now stand (all local, ALEPH Fig. 5 reading)

| frame | asymptotic Z0 | toy-calibrated Z | status |
|---|---|---|---|
| Heister's exact template, constant ratio | 4.18 | 2.33-2.46 | graded earlier |
| par3 smooth background, constant ratio | 3.13 | 3.35 (constant truth) / 1.93 (rising truth) | graded (this amendment for the rising truth) |
| par3, rising ratio, slope free | 2.295 | **2.35** | **graded here** |
| par3, ratio constrained by same-sign control | 2.134 | pending (`toyres-ssframe-v1`) | conditional on an unestablished drift (0.36) |

**Information only (an estimate, not a grade).** `leescan-v1` (0.34) scans the constant-ratio
frame and was predicted, before running, to find about 1.66 upcrossings of Z = 1 and a global Z of
about 2.0 for the 3.1 sigma local excess. If the same upcrossing count is applied to the rising-
ratio frame (Gross-Vitells: p_global = p_local + 1.66 exp(-(Z^2 - 1)/2)), the 2.35 sigma local
excess would be worth about **0.8-0.9 sigma globally** (p about 0.18-0.21). The upcrossing count in
this frame has not been measured; no test uses this number.

## 5. Article status

No article yet. The significance article (slug `aleph-30-gev-excess-with-its-template-error`) waits,
as fixed in the playbook and 0.36 sec. 5, for `toyres-ssframe-v1` (>= 1,000 toys) and `leescan-v1`.

## 6. Limits

A reading by an AI agent of ALEPH's published Fig. 5, not ALEPH's events; one log-linear drift shape;
toys drawn from the fitted background, so the calibration is conditional on that model; local
significance only.
