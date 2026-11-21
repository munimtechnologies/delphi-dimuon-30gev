# PLAN amendment v0.34: the look-elsewhere effect for ALEPH's 30 GeV excess in the error-aware smooth frame (job `leescan-v1` pre-registered)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-21. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written **before** job `leescan-v1` has run, while `abtag-v1`,
`toyres-slsm-v1`, `toyres-ssframe-v1` (amendment 0.32) and `delphi-rootless-probe-v1` (amendment
0.33) are still queued. No test, threshold, prior or blinding rule of plan v0.11 or amendments
0.12-0.33 is changed. The grades of `delphi-rootless-probe-v1` (R0-R4) will be written in the next
amendment number, not here.

## 1. Why

Every significance in NOTE-aprime 0.5 is **local**: it tests a signal fixed at 30.40 GeV with
ALEPH's fitted width. The excess was found by looking at the whole spectrum, so an honest
statement needs the probability that background alone makes an excess this strong **anywhere**
in the range that was looked at (the look-elsewhere effect).

Heister did this in his own frame (arXiv:1610.06536 v9, sec. 3.6). He floated the mean in 15-50 GeV
and the width, and found that the look-elsewhere effect lowers his significances by 1.4-1.6 sigma
(single exponential 4.0 to 2.6, double exponential 3.6 to 2.4, TKDE 4.9 to 2.9 sigma). His frame
treats the smoothed electron-muon template as exact. Our primary frame (par3, amendment 0.24) keeps
the template's counting error and gives 3.134 sigma asymptotic and 3.35 sigma toy-calibrated at the
fixed mass. Nobody has yet computed the global significance in a frame that keeps the template's
error. The significance article (playbook) needs this number, so it is fixed in advance here.

## 2. Method (new module `stats/leescan.py` 0.1.0; nothing existing is modified)

- **Frame:** `aprime_smooth.ParFit`, degree 3, imported unchanged (sha256 `eae6510a...` checked),
  with `emuframe.py` 0.1.0 (git blob checked). Same data: the blind Fig. 5 reading
  `data/aleph-fig5.json` (sha256 `f535d924...`), e mu counts = reading / 0.532.
- **Signal hypotheses:** Voigt profile with FWHM Gamma and Gaussian sigma = sqrt(6e-4) x mass
  (Heister's eq. 1), 32.31 events at mu = 1, truncated to 15-50 GeV. Mass grid 17.00-48.00 GeV in
  0.25 GeV steps (125 points). We stay 2 GeV inside Heister's 15-50 GeV, so no shape is cut in
  half. This range is slightly narrower than his, which makes the correction a little smaller
  than for the full range.
  - **PRIMARY (`g1.78`):** Gamma = 1.78 GeV fixed (ALEPH's fitted width): "the particle ALEPH saw,
    at any mass".
  - **FLOAT:** at each mass, the largest Z over Gamma in {1.0, 1.78, 3.0} (a coarse version of
    Heister's floated width). Gamma 1.0 and 3.0 alone are also reported.
- **Local Z(mass):** sqrt(q0), one-sided, computed exactly as `ParFit.discovery` (same mu = 0
  fit, same three starting values 0, 0.8, 2.0, mu <= 20). Gate: the scanner must reproduce
  `ParFit.discovery` at ALEPH's own shape to 0.002, and that must reproduce aprime-smooth-v1's
  3.134 to 0.01.
- **Toys:** 2,000 background-only toys (seed 20261121), drawn from the par3 mu = 0 fit to the
  reading, the same truth as aprime-smooth-v1. Both spectra are fluctuated and every toy is
  scanned over the whole grid. Each toy row is saved as it finishes. A 14,000 s budget stops the
  loop. At least 1,000 toys are needed to grade. Fewer means NOT GRADABLE, and the job is resumed
  as `leescan-v2` from the saved rows (rule of amendment 0.32 sec. 3, applied unchanged).
- **Global p (primary statement):** the fraction of toys whose **maximum** Z over the grid is at
  least the observed local Z at 30.40 GeV. Because it compares the observed value with toys
  scored by the same statistic, it needs no asymptotic formula.
- **Extrapolation (secondary):** Gross and Vitells (Eur. Phys. J. C 70 (2010) 525):
  p_global(Z) = p_local(Z) + E[N(u0)] exp(-(Z^2 - u0^2)/2), with u0 = 1 and E[N(u0)] the mean
  number of upcrossings of level u0 per toy. It is used only for local values beyond the toys'
  reach (Heister's 5.35) and for the other frames' values (2.664, 2.295, 2.134). Applying a par3
  E[N] to another frame is an approximation and is labelled as one.

## 3. Expectations, written before the run

**Analytic prediction.** For a matched filter with a roughly Gaussian shape of width sigma_s, the
Rice formula gives E[N(u)] = (1/2 pi) integral sqrt(lambda2(m)) dm exp(-u^2/2), with
lambda2 = 1/(2 sigma_s^2). The Voigt FWHM (Gamma 1.78, sigma = 0.0245 m) is 2.24, 2.89 and
3.84 GeV at 17, 30.4 and 48 GeV. Taking sigma_s = FWHM/2.355, plus the 1 GeV binning in quadrature
(1/12 GeV^2), gives sqrt(lambda2) = 0.71, 0.56 and 0.43 per GeV. So the integral over 17-48 GeV is
about 17.2, E[N(u)] is about 2.74 exp(-u^2/2), and **E[N(1)] is about 1.66**. Then:

| local Z (frame) | predicted global Z (primary, fixed width) |
|---|---|
| 3.134 (par3, observed at 30.40) | **about 2.0** (p about 0.021) |
| 3.35 (par3 toy-calibrated) | about 2.3 |
| 5.35 (Heister, TKDE frame) | about 4.6 |
| 2.664 (bb) | about 1.4 |
| 2.295 (par3 + rising ratio) | about 0.8 |
| 2.134 (par3 + same-sign constrained ratio) | about 0.5 |

Known reasons the prediction can miss: the Lorentzian tails lengthen the correlation, which
means fewer upcrossings. The cubic background absorbs broad features. Above about 38 GeV the
spectrum has 0-3 events per bin, where the field is far from Gaussian: single events over a
background of about 0.1 can make sharp local spikes, which means more upcrossings at low levels
and a heavier tail.

**Grades** (`LEESCAN:` line):

| id | statement | our prior |
|---|---|---|
| L0 | gate: unit tests pass, closure (3.134 +- 0.01), scanner = discovery (+- 0.002), >= 1,000 toys | 90 % |
| L1 | primary E[N(1)] lies in [1.0, 2.6] | 70 % |
| L2 | Gross-Vitells from u0 = 1 matches the toys' direct P(max Z >= 2) within max(2 binomial sigma, 15 % relative) | 55 % |
| L3 (headline) | primary global Z of the observed 30.40 GeV excess (direct toy count) is below 2.5 | 80 % |
| L4 | the floated-width global Z is below the primary global Z | 70 % |
| L5 | the observed primary scan peaks between 29.0 and 32.0 GeV (not, e.g., at the sparse 38-41 GeV bins) | 60 % |

**Fixed consequences:**

- The significance article quotes the **direct-count** primary global Z (L0 PASS) next to the local
  values, and the floated-width value as Heister's convention. If L2 FAILS, the Gross-Vitells
  conversions (Heister's 5.35 and the other frames) are reported as "indicative only" and are not
  quoted as numbers in the article's headline.
- If L5 FAILS, the article reports where the scan peaks. The global p of the 30.40 GeV excess is
  still the one defined above (toys' maximum vs the observed Z at 30.40 GeV). A larger peak elsewhere
  is reported as such, never used to change the definition.
- No threshold above is moved after the run. Every number is published, whatever it shows.

## 4. Limits, stated in advance

- The local values come from readings of a published figure (reader uncertainty about +-0.5 events
  per mu mu bin, +-0.3 per e mu bin), not from ALEPH's events.
- The toys' truth is the par3 constant-ratio fit. The rising-ratio and same-sign frames
  (amendments 0.27 and 0.30) have their own, not yet computed, global corrections. Here they get
  only the approximate Gross-Vitells conversion.
- The toys' maximum is taken on a 0.25 GeV grid, while the observed value is at exactly 30.40 GeV.
  Missing a toy peak between grid points makes the global p very slightly too small (anti-
  conservative, negligible at this step size compared with a resolution of 0.4 GeV or more).
- Three widths are a coarse stand-in for a continuously floated width.
