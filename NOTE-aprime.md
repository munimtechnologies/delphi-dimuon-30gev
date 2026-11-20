# NOTE-aprime 0.3: ALEPH's 30 GeV excess with its background template's own counting error

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. Text CC BY 4.0; code Apache-2.0. Not a result of the ALEPH
Collaboration.

Version 0.3 adds section 8 (job `aprime-ext-v1`, amendment 0.23, graded: with a mu mu / e mu
ratio allowed to change with mass, the excess falls from 2.66 to 1.62 sigma). Version 0.2 added
section 7 (the calibration toys of amendment 0.19 sec. 4, job `aprime-toys-v1`) and changed what
section 6 says about the 35-fold inflation. **Status of the headline:** the 2.66 sigma of section 3
is the figure of a method that ignores the background's smoothness, so in that respect it is
conservative; amendment 0.24 (job `aprime-smooth-v1`, still queued) decides that. Section 8 shows
a second assumption, a mass-independent mu mu / e mu ratio, that the excess leans on in the other
direction. Amendment 0.25 pre-registers the test of where the rising ratio comes from.

This note grades test **A'-ALEPH** (PLAN amendment 0.19 sec. 3, P1-P4, written before the input
existed) and reports the toys of amendment 0.20 sec. 3 (rules written before any fit). Job
`aprime-aleph-v1` (python:3.12, 10,000 toys, 4,289 s). Raw outputs, unedited:
[analysis/results/aprime-aleph/](analysis/results/aprime-aleph/) (`aleph_aprime.json`, `scan.json`,
`toys.json`, `toys_raw.json`, `toy_truth.json`, `run.txt`, `sha256.txt`, and the `emuframe.py` the
job fetched, git blob d55c900f = stats/emuframe.py 0.1.0).

## 1. The question

Heister (arXiv:1610.06536 v9) reports 32.3 +- 10.9 opposite-sign muon pairs at 30.40 GeV in
b-tagged Z decays of archived ALEPH data, with a local significance of 5.35 sigma (unbinned fit,
signal free, background shape = a kernel-smoothed template made from the same events' opposite-sign
electron-muon pairs, **treated as exact**) and Z_Bi = 2.63 (on/off counting, tau = 1). The
electron-muon template is itself a finite sample with its own Poisson noise. Neither published
number includes that noise. A'-ALEPH asks: **how significant is the excess when it is included?**

## 2. Input and method

- Input: a blind per-bin reading of Heister's Fig. 5 (HTML numbering), 15-50 GeV, 1 GeV bins:
  362 muon pairs, 300.9 scaled electron-muon background ([data/aleph-fig5.json](data/aleph-fig5.json)).
  Reading check P0 passed (amendment 0.20).
- Raw electron-muon counts m_i = v_i / 0.532 (Heister's factors: twice as many e mu pairs, electron
  efficiency 6 % lower).
- Model "bb": mu mu ~ Poisson(r t_i + mu s_i), e mu ~ Poisson(t_i), one free t_i per bin
  (Barlow-Beeston), free ratio r, ALEPH's fixed signal shape (Voigt, 30.40 GeV, Gamma 1.78 GeV,
  sigma 0.745 GeV), mu = 1 is 32.31 events. Model "exact": the same with t_i = m_i fixed (the
  binned, unsmoothed analogue of ALEPH's method).
- Toys: 10,000 background-only pseudo-experiments drawn from the reading's own mu = 0 "bb" fit
  (r = 0.640; 362.0 muon pairs and 565.7 electron-muon pairs expected), both the muon and the
  electron-muon spectra fluctuated, each fitted with both models.

## 3. Grades (amendment 0.19, thresholds unchanged)

| | statement | expectation | result | grade |
|---|---|---|---|---|
| P1 | Z0(exact) >= 3.0 | PASS | 4.178 | **PASS** |
| P2 | Z0(bb) / Z0(exact) in [0.70, 0.92] | PASS (0.81) | 0.638 | **FAIL** |
| P3 | **Z0(bb) >= 3.0** (headline) | none | **2.664** | **FAIL** |
| P4 | mu_hat(bb) in [0.5, 1.5] | PASS | 0.813 | **PASS** |

Expectations met: 2 of the 3 that were written (P2's Gaussian estimate was wrong: at these low
counts per bin the template's noise costs more than the large-sample factor 1/sqrt(1 + r)).

Amendment 0.20 rule 4: the asymptotic Z0(bb) (2.664) and its toy-calibrated value (2.605) lie on
the **same** side of 3.0, so P3 is a clear FAIL, not "borderline".

Reported whatever happened:

| quantity | value |
|---|---|
| Z0(bb), r0 = 0.532 / 0.45 / 0.60 | 2.664 / 2.795 / 2.566 |
| Z0(exact) | 4.178 |
| mu_hat bb / exact | 0.813 / 0.960 (26.3 / 31.0 events) |
| fitted ratio r (mu free) bb / exact | 0.5935 / 0.5851 |
| Z_Bi, bins 29-32 GeV, n_on 33, bkg 15.4, tau = 1 (Heister's choice; his value 2.63) | 2.476 |
| Z_Bi, same bins, tau = 1/r0 (the e mu sample's true size) | 2.858 |
| 2 Delta lnL at mu = 1, bb / exact | 0.351 / 0.020 |

The profile scans in mu have single, clean minima (bb near 0.75-1.0, exact near 1.0;
[scan.json](analysis/results/aprime-aleph/scan.json)).

## 4. Toys (amendment 0.20 sec. 3; information except where rule 3 applies)

| | bb | exact |
|---|---|---|
| observed Z0 (asymptotic) | 2.664 | 4.178 |
| toys with Z0 >= observed (of 10,000) | 45 | 68 |
| toy p-value | 0.00460 | 0.00690 |
| **toy-calibrated Z** | **2.605** | **2.462** |
| rate of Z0 >= 2 (nominal 0.0228) | 0.0215 | 0.1624 |
| rate of Z0 >= 3 (nominal 0.00135) | 0.0015 | 0.0467 |
| mean fitted mu (no signal in toys) | 0.107 | 0.206 |

- **"bb" is calibrated** at the reading's scale: its false-excess rates match the asymptotic
  formula (0.0215 against 0.0228, 0.0015 against 0.00135), so its asymptotic 2.66 can be trusted
  as a p-value of that method.
- **"exact" is not.** Treating the unsmoothed template as exact produces false 3-sigma excesses in
  4.7 % of background-only experiments, 35 times the nominal 0.135 %. Calibrated by toys, its
  4.18 sigma is worth 2.46 sigma, in line with "bb".
- These toys were drawn from the "bb" mu = 0 fit, which copies the reading's bin-to-bin bumps into
  the truth. A smooth truth is used in amendment 0.24.

## 5. What this means (amendment 0.19's meaning, written before the fit)

P3 FAIL: *ALEPH's 5.35 sigma depends on treating its e mu template as exact; with the template's
Poisson error the local significance in the binned frame is below 3 sigma, before any
look-elsewhere correction. Neither outcome says whether the excess is real.*

Section 7 qualifies this (added in 0.2, after the toys): the "binned frame" in that sentence
matters. "bb" treats every bin's background as unrelated to its neighbours. A method that uses the
background's smoothness can be both calibrated and more powerful, so whether the excess is above or
below 3 sigma local is **not yet decided**; amendment 0.24 decides it.

## 6. Limits

- The input is one AI agent's reading of a published figure (reader's uncertainty +-0.5 events per
  muon bin, +-0.3 per background bin). Heister's unbinned fit cannot be reproduced exactly from it.
- Heister smoothed his template with a kernel density estimate. The 35-fold inflation of section 4
  is for the **unsmoothed** template and does not describe his method: section 7 shows that a
  1 GeV smoothing removes most of it (at the table's scale). Our "bb" figure ignores that the true
  background is smooth and is conservative.
- The plotted background is assumed to be the raw e mu count times 0.532. Using 0.45 or 0.60
  moves Z0(bb) between 2.57 and 2.80.
- The fit table's background (1457 events) is about four times what the figures hold (362 pairs);
  the paper does not explain the factor (amendments 0.20-0.23). Our test uses the figures' scale,
  which reproduces Heister's Z_Bi (2.48 against 2.63).
- No look-elsewhere correction is applied; with one, the number would be lower.
- Sections 3-7 assume, as Heister does, one mu mu / e mu ratio for all masses. Section 8 tests that.

## 7. Calibration toys of amendment 0.19 sec. 4 (job `aprime-toys-v1`, graded 2026-11-20)

Made-up spectra only, no ALEPH data: 1,000 background-only pseudo-experiments for each of two
exponential shapes (decay length 4 and 8 GeV), 1,457 background muon pairs in 15-50 GeV (the fit
table's scale), e mu template 1.88 times larger, 1 GeV bins, ALEPH's fixed signal shape. Raw
outputs: [analysis/results/aprime-toys/](analysis/results/aprime-toys/) (`toys.json`, `toys.csv`,
`run.txt`, `tests.txt`, `versions.txt`, `sha256.txt`). 391 s, peak memory 0.05 GB.

| method | decay 4: rate Z0 >= 2 | Z0 >= 3 | decay 8: rate Z0 >= 2 | Z0 >= 3 |
|---|---|---|---|---|
| nominal | 0.0228 | 0.00135 | 0.0228 | 0.00135 |
| bb (template error kept) | 0.023 | 0 | 0.023 | 0 |
| exact (unsmoothed template) | 0.125 | 0.034 | 0.097 | 0.013 |
| kde1 (1 GeV kernel, as exact) | 0.038 | 0.001 | 0.044 | 0.003 |
| kde2 (2 GeV kernel, as exact) | 0.001 | 0 | 0.017 | 0.001 |

| | statement | expectation | result | grade |
|---|---|---|---|---|
| C1 | P(Z0(bb) >= 2) in [0.009, 0.037], both shapes | PASS | 0.023 / 0.023 | **PASS** |
| C2 | P(Z0(exact) >= 2) >= 0.035, both shapes | PASS (Gaussian 0.053) | 0.125 / 0.097 | **PASS** |
| C3 | information: kde2 rate below exact rate | - | 0.001 < 0.125; 0.017 < 0.097 | yes |
| C4 | all unit tests pass | PASS | 18 of 18 | **PASS** |
| C5 | information: delphi_aprime on a made-up 700-bin spectrum | - | runs, label INCONCLUSIVE, Z0 0.00, UL95 1.40 (low reading 1.62), 7.1 s | done |

Expectations met: 3 of 3. C1 PASS means the A' method needs no toy calibration (amendment 0.19's
fallback is not triggered).

What the toys show (observations on graded outputs, not new tests):
- At the table's scale the unsmoothed template treated as exact inflates false 2-sigma excesses
  4-5 fold (5.5 fold with the steep shape); the Gaussian estimate (0.053) was too low.
- A 1 GeV kernel removes most of that: the rate falls to 0.038-0.044, still 1.7-1.9 times nominal.
  At 3 sigma, 1 and 3 toys of 1,000 against 1.35 expected are too few to say more.
- A 2 GeV kernel over-corrects on the steep shape (0.001, mean Z 0.13): smoothing a steeply
  falling spectrum near the edge of the range distorts its shape, and the fit then prefers no
  signal. Smoothing is not free of bias; how much depends on the bandwidth, which Heister does not
  give.
- C5: the DELPHI version of A' runs in 7 s on 700 bins. On a made-up spectrum with no signal and
  21.7 expected signal events at mu = 1, the 95 % upper limit it found on that one spectrum
  (1.40) is above 1: with that expected signal and that much background, A' could fail to exclude
  even when no signal is present. This is a made-up
  spectrum, not DELPHI's, and is not the pre-unblinding Asimov check of amendment 0.19 sec. 2 (iii).

Consequence for this note: section 6's statement that the 35-fold inflation is an "upper bound"
for Heister's method is confirmed and sharpened. With a kernel near 1 GeV the inflation is small.
So the gap between Heister's 5.35 and our 2.66 cannot be put down mostly to template noise until a
method that uses smoothness and keeps the template's error has been calibrated on the reading
itself. That is amendment 0.24.

## 8. A mass-dependent mu mu / e mu ratio (amendment 0.23, job `aprime-ext-v1`, graded 2026-11-20)

Job `aprime-ext-v1` (python:3.12, stats/aprime_ext.py 0.1.0, 80 s; 10 of 10 unit tests on made-up
inputs passed; emuframe 0.1.0 fetched, blob d55c900f checked). Inputs: the Fig. 5 reading
(15-50 GeV) and the ALEPHLOW2 reading (5-15 GeV: 421 muon pairs, 440.4 scaled e mu). The ratio is
r_i = r exp(b (x_i - 30.40 GeV)), b free in [-0.2, 0.2] per GeV. Raw outputs, unedited:
[analysis/results/aprime-ext/](analysis/results/aprime-ext/) (`aprime_ext.json`, `run.txt`,
`tests.txt`, `fetch.txt`, `sha256.txt`, `job.json`, and our grades `grades-aprime-ext.json`).

### 8a. Every fit

| range | ratio | Z0 bb | Z0 exact | mu_hat bb (events) | b at mu = 0, bb (per GeV) |
|---|---|---|---|---|---|
| 15-50 GeV | constant | **2.664** | 4.178 | 0.813 (26.3) | - |
| 15-50 GeV | log-linear | **1.621** | 2.997 | 0.655 (21.2) | 0.0266 |
| 5-50 GeV | constant | 3.309 | 4.932 | 0.930 (30.0) | - |
| 5-50 GeV | log-linear | **1.352** | 2.614 | 0.517 (16.7) | 0.0249 |

| slope at mu = 0, signed Z (1 dof) | bb | exact |
|---|---|---|
| 15-50 GeV | 2.256 | 2.934 |
| 5-50 GeV | 3.961 | 4.991 |

Split test (bb, mu = 0, one ratio below 15 GeV and another above): r = 0.5085 (5-15 GeV) against
0.6399 (15-50 GeV), Z = 2.55 (the by-hand 2.5 of amendment 0.23 was not a prediction for it).

### 8b. Grades (amendment 0.23 sec. 3, thresholds unchanged)

| | statement | prior | result | grade |
|---|---|---|---|---|
| X0 | gate: constant ratio, 15-50 GeV, reproduces Z0(bb) 2.664 and Z0(exact) 4.178 within 0.005 | 90 % | 2.664 / 4.178 | **PASS** |
| X1 | **main**: Z0(bb), free slope, 15-50 GeV, below 3.0 | 90 % | **1.621** | **PASS** |
| X2 | abs(Z_slope(bb, 15-50 GeV, mu = 0)) < 2.0 | 50 % | 2.256 | **FAIL** |
| X3 | Z0(bb), free slope, 5-50 GeV, below 3.0 | 85 % | 1.352 | **PASS** |

Expectations met: 3 of the 3 written with a prior above 50 % (X2's 50 % was no expectation).

### 8c. Meaning (written in amendment 0.23 before the job ran), applied

X1 PASS with Z0(bb) much lower than 2.66, and X2 FAIL. Amendment 0.23 wrote for this case:
*in ALEPH's own frame, the excess leans on the assumption that the mu mu / e mu ratio does not
change with mass, and the data themselves show that it does. The most economical reading is then
a lepton-flavour-dependent background shape, not a particle.* We apply it as written, with the
qualifications of 8d. As before, nothing here says whether the excess is real; only data ALEPH did
not use can say that.

### 8d. Observations made after seeing the output (not tests)

1. **In 15-50 GeV alone, a slope and a bump are almost interchangeable.** With the signal floated,
   adding the slope gains only 2 Delta lnL = 0.62 (bb; Z 0.79) and 0.13 (exact), from the
   `lnL_best` values in `aprime_ext.json`. Slope and signal together against neither give
   2 Delta lnL = 7.72 (bb, 2 dof). So the 15-50 GeV reading says "the muon pairs rise above the
   e mu template towards 30 GeV and beyond", but on its own it cannot say whether as a narrow
   peak or as a broad rise. Including 5-15 GeV, the slope is preferred even with the signal
   floated (2 Delta lnL 6.58, bb), but below 15 GeV other things change the ratio too: the muon
   and electron momentum cuts differ (2.5 against 2 GeV), and Heister notes that ALEPH's
   simulation puts Upsilon resonances into the muon pairs near 10 GeV.
2. **Plain counts from the reading show the same thing.** Muon pairs over scaled e mu: 15-25 GeV
   257 / 238.7 = 1.08; 25-29 GeV 45 / 29.0 = 1.55; 29-32 GeV 33 / 15.4 = 2.14; 32-50 GeV
   27 / 17.8 = 1.52. Outside the signal window, above 25 GeV, the muon pairs exceed the template by
   about 1.5 on both sides of the peak (72 against 46.8). Scaled to its neighbours rather than to
   the 15-50 GeV average (1.20), the background under 29-32 GeV would be about 23.7, and the excess
   about 9 events instead of 17.6.
3. **Size of the slope.** b = 0.0266 per GeV means the ratio rises by a factor of 1.30 every
   10 GeV; at 30.4 GeV it is 0.80, against Heister's constant 0.532 (= 1 / (2 x 0.94)).

**The question this raises, which a physicist would ask first:** is the rising ratio expected?
Heister states that the lepton identification efficiencies do not depend on the pair mass in
5-50 GeV, and that in ALEPH's simulation the muon pairs agree with the e mu pairs "within their
errors" (his Fig. 4). Real sources of a rise exist (hadrons faking muons more often at high
momentum; same-flavour pairs from virtual photons radiated in Z -> q qbar, which give e e and
mu mu but no e mu). Amendment 0.25 pre-registers two blind readings that tell these apart:
ALEPH's own simulation (Fig. 4) and ALEPH's di-electrons, against the same e mu template.

### 8e. Limits of section 8

The same reading limits as section 6. A log-linear ratio is one shape among many. The 5-15 GeV
bins come from a second reading of the same figure. The meaning in 8c was written before the job
but after the binned ratios had been seen (amendment 0.23 says so). No look-elsewhere correction.
