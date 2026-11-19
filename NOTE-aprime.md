# NOTE-aprime 0.1: ALEPH's 30 GeV excess with its background template's own counting error

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. Text CC BY 4.0; code Apache-2.0. Not a result of the ALEPH
Collaboration.

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
  formula (0.0215 against 0.0228, 0.0015 against 0.00135), so its asymptotic 2.66 can be trusted.
- **"exact" is not.** Treating the unsmoothed template as exact produces false 3-sigma excesses in
  4.7 % of background-only experiments, 35 times the nominal 0.135 %. Calibrated by toys, its
  4.18 sigma is worth 2.46 sigma, in line with "bb".
- Calibrated, the two treatments agree: **about 2.5-2.6 sigma local** for ALEPH's 30 GeV excess in
  the binned electron-muon frame, before any look-elsewhere correction.

## 5. What this means (amendment 0.19's meaning, written before the fit)

P3 FAIL: *ALEPH's 5.35 sigma depends on treating its e mu template as exact; with the template's
Poisson error the local significance in the binned frame is below 3 sigma, before any
look-elsewhere correction. Neither outcome says whether the excess is real.*

We add only what the toys show: the gap between the template-as-exact number and the honest one
is mostly the template's own noise, which the template-as-exact method counts as signal evidence.

## 6. Limits

- The input is one AI agent's reading of a published figure (reader's uncertainty +-0.5 events per
  muon bin, +-0.3 per background bin). Heister's unbinned fit cannot be reproduced exactly from it.
- Heister smoothed his template with a kernel density estimate, which removes part of the
  bin-to-bin noise; our "exact" model uses the raw binned template, so its 35-fold inflation is an
  upper bound for his method, not a measurement of it. Job `aprime-toys-v1` (C3, queued) measures
  how much smoothing removes, on made-up spectra. Our "bb" figure ignores that the true background is
  smooth and is, in that sense, conservative.
- The plotted background is assumed to be the raw e mu count times 0.532. Using 0.45 or 0.60
  moves Z0(bb) between 2.57 and 2.80.
- The fit table's background (1457 events) is about four times what the figures hold (362 pairs);
  the paper does not explain the factor (amendments 0.20-0.23). Our test uses the figures' scale,
  which reproduces Heister's Z_Bi (2.48 against 2.63).
- No look-elsewhere correction is applied; with one, the number would be lower.
