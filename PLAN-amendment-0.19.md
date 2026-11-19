# PLAN amendment v0.19: test A' (ALEPH's electron-muon frame) and a re-evaluation of ALEPH's own significance

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

This amendment is part of the pre-registration. It extends PLAN.md v0.11 and amendments 0.12-0.18
and will be merged into PLAN.md v1.0. It is published **before any DELPHI dimuon mass in the
26-35 GeV window has been seen, and before the per-bin reading of ALEPH's Fig. 5 that section 3
grades exists**. Code: [stats/emuframe.py](stats/emuframe.py) 0.1.0, tests
[stats/test_emuframe.py](stats/test_emuframe.py) (made-up inputs only), toys
[stats/aprime_toys.py](stats/aprime_toys.py).

## 1. Why

NOTE-injet 0.2 (sec. 7) graded R1 as failed, so, as pre-registered there, **test A' becomes the
primary DELPHI test**. A' fits the opposite-sign mu mu spectrum against the opposite-sign e mu
spectrum of the same data, which is how ALEPH built its background (Heister, arXiv:1610.06536 v9,
sec. 3.4). Reading Heister's statistics section again for this amendment (arXiv HTML, 2026-11-19):

- Z_asym = 5.35 comes from an unbinned fit in which "a single parameter of interest, i.e. the number
  of signal events, is assumed to be free" and "the number of background events is treated as a
  nuisance parameter". The **shape** of the background is the kernel-smoothed e mu template,
  taken as exact. Its own counting error does not enter.
- Z_Bi = 2.63 uses "n_on and n_off ... obtained around the fitted mass using a 2 sigma wide area
  (tau = 1)". With tau = 1 the off-sample is taken to be the same size as the background it
  predicts, but ALEPH's e mu sample is about 1.88 times the mu mu background (pair-count factor 2,
  electron efficiency "about 6% less"), so tau = 1 understates the off-sample.
- The paper gives no count of e mu pairs and no kernel bandwidth.

So neither published number is the local significance with the template's actual Poisson error
included. emuframe computes exactly that: one Barlow-Beeston nuisance per bin (profiled in closed
form), a free mu mu / e mu ratio r, and the fixed ALEPH signal shape (Voigt, m = 30.40 GeV,
Gamma = 1.78 GeV, sigma = 0.745 GeV). Model "exact" is the same fit with the binned, unsmoothed
template treated as exact. In the Gaussian limit the two differ by a factor 1/sqrt(1 + r), about
0.81 for r = 0.532 (unit test `TestGaussianLimit`).

## 2. Test A' for DELPHI (primary)

- **Spectra.** The b-tagged (plan v0.11 tag) opposite-sign mu mu spectrum and the b-tagged
  opposite-sign e mu spectrum, same events, same lepton momentum and angle cuts, DELPHI's standard
  electron tag; every opposite-sign e mu pair in an event is counted, as ALEPH did. 15-50 GeV,
  700 bins of 50 MeV, as test A. The e mu spectrum is not same-flavour and is not blinded by
  `dimusel.py`; it may be inspected in full before unblinding.
- **Fit.** emuframe model "bb": mu mu ~ Poisson(r t_i + mu s_i), e mu ~ Poisson(t_i), r free.
  Signal: Voigt with m = 30.40 GeV, Gamma = 1.78 GeV, sigma = DELPHI's simulated resolution
  (delsim) or 0.745 GeV until it exists; s at mu = 1 is N_exp from `analysis/nexp.py`, under both
  hadronic-count readings (nominal, and low = 0.864 x nominal).
- **Outcomes** (test A's rule of plan v0.11): EXCLUDED if the 95 % CL CLs upper limit on mu is
  below 1; COMPATIBLE if 2 Delta lnL < 1 at mu = 1 and Z0 >= 2; INCONCLUSIVE otherwise. EXCLUDED or
  COMPATIBLE only if both readings give it.
- **A and A' together.** A' is primary, test A (fixed degree-3 background, amendment 0.18) is
  reported beside it. If one gives EXCLUDED and the other COMPATIBLE, the overall statement is
  INCONCLUSIVE and both are shown.
- **Checks before unblinding.** (i) The ratio r fitted on the sidebands (15-26 and 35-50 GeV)
  is compared with DELPHI simulation's mu mu / e mu ratio; a difference above 3 standard
  deviations is investigated before the window is opened and is not "fixed" by a free factor.
  (ii) I1 of NOTE-injet sec. 5 carries over. (iii) The median expected upper limit on the
  background-only Asimov set is computed from simulation and published before unblinding; if it
  is above 1, INCONCLUSIVE is the likely outcome and we will say so in advance.

## 3. A'-ALEPH: ALEPH's own excess with its template's Poisson error (graded on a blind reading)

**Input.** A blind per-bin reading of Heister's Fig. 5 (HTML numbering: mu mu data against the
binned e mu data used as background; 1 GeV bins), filed as a hands goal this run: for every bin in
15-50 GeV the mu mu count n_i and the plotted e mu background v_i. The raw e mu counts are
m_i = v_i / r0 with **r0 = 1 / (2 x 0.94) = 0.532** (primary); 0.45 and 0.60 are reported as a
sensitivity range. If the reader can read e mu error bars in at least five bins with v_i >= 5, the
implied r0 (median of err^2 / v) is reported as information and does not replace 0.532.
`emuframe.aleph_aprime` computes everything below.

**P0 (reading check, gates P1-P4).** The reading's sum of (n_i - v_i) over 29-32 GeV is within
17.8 +- 3.0 events (the first blind reading, NOTE-injet sec. 7). If not, P1-P4 are NOT GRADABLE and
a second blind reading is requested.

| | statement | expectation |
|---|---|---|
| P1 | Z0 with the template treated as exact (binned, unsmoothed) is at least 3.0 | PASS |
| P2 | Z0(bb) / Z0(exact) lies in [0.70, 0.92] | PASS (Gaussian value 0.81) |
| P3 | **Z0(bb), ALEPH's excess with its template's Poisson error, is at least 3.0** | no confident expectation; scaling Heister's 4-5 sigma by 0.81 gives 3.2-4.3, but a binned unsmoothed template loses information |
| P4 | the bb fit's signal strength mu_hat is in [0.5, 1.5] (ALEPH's 32.3 events) | PASS |

Reported whatever happens: Z0(bb), Z0(exact), Z0(bb) for r0 = 0.45 and 0.60, and Z_Bi in the
bins whose centres lie within 30.40 +- 1.49 GeV with tau = 1 (Heister's choice, compared with his
2.63) and with tau = 1/r0.

**Meaning, written now.** P3 PASS: the excess stays at or above 3 sigma local in ALEPH's own frame
even when the template's counting error is included, so a template fluctuation cannot carry it and
only DELPHI's data can decide. P3 FAIL: ALEPH's 5.35 sigma depends on treating its e mu template as
exact; with the template's Poisson error the local significance in the binned frame is below 3
sigma, before any look-elsewhere correction. Neither outcome says whether the excess is real.
Limits: the unsmoothed per-bin template ignores that the true background is smooth, so Z0(bb) is a
conservative figure; Z0(exact) is an optimistic one. Section 4 measures how much each departs from
its nominal false-positive rate.

## 4. Calibration toys (job aprime-toys-v1; made-up spectra, no real data)

1000 background-only pseudo-experiments for each of two made-up exponential shapes (decay length 4
and 8 GeV; 1457 background mu mu pairs in 15-50 GeV, e mu template 1.88 times larger, 1 GeV bins),
each fitted at ALEPH's fixed mass and shape with the template (a) "bb", (b) exact, (c) smoothed with
a Gaussian kernel of 1 GeV and (d) 2 GeV, then treated as exact (every exact-type template floored at
0.5 counts per bin, so empty bins cannot make the fit undefined). Asymptotic rates: P(Z0 >= 2) =
0.0228, P(Z0 >= 3) = 0.00135.

| | statement | expectation |
|---|---|---|
| C1 | P(Z0(bb) >= 2) lies in [0.009, 0.037] for both shapes (the A' method is calibrated) | PASS |
| C2 | P(Z0(exact) >= 2) is at least 0.035 for both shapes (an unsmoothed template taken as exact inflates false excesses) | PASS (Gaussian estimate 0.053) |
| C3 | information: the 2 GeV-smoothed rate is below the unsmoothed exact rate | - |
| C4 | all unit tests pass | PASS |
| C5 | information: `delphi_aprime` on a made-up 700-bin spectrum runs and returns a label; time | - |

If C1 fails, A' uses toy-calibrated p-values (the toys' own Z0 distribution) instead of the
asymptotic formula, for both DELPHI and A'-ALEPH; the thresholds above are not changed.

## 5. Limits

The ALEPH input will be read by eye from a published figure by one AI reading agent; Heister's
unbinned KDE fit cannot be reproduced exactly from it. r0 rests on Heister's two stated factors.
The toys use made-up shapes and test the statistics, not any detector. None of this is a result of
the ALEPH, DELPHI, L3 or OPAL Collaborations.
