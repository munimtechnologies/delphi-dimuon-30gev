# PLAN amendment v0.21: the fit figure holds 362 pairs, and the fit table's own errors say its background is a rescaled number

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration; extends amendment 0.20. Written after the second blind reading
(hands goal `ALEPHFIT`) came back and **before** `aprime-aleph-v1` (A'-ALEPH, P1-P4) or
`aprime-toys-v1` (C1-C5) have produced any number. Nothing in P1-P4 or C1-C5 is changed.

## 1. The reading, and amendment 0.20's rule

An AI reading agent with no access to this repository read Heister's figure of the unbinned fit
(arXiv:1610.06536 v9, HTML Figure 7; the text calls it Fig. 9), bin by bin, data and fitted curve
([data/aleph-fitfig.json](data/aleph-fitfig.json), committed exactly as read).

- **Data: 362 muon pairs in 15-50 GeV**, 33 in 29-32 GeV. Every one of the 35 bins agrees with the
  independent blind reading of Fig. 5 ([data/aleph-fig5.json](data/aleph-fig5.json)).
- **Fitted curve: 362.7 events in 15-50 GeV** (sum of the curve at the bin centres, by hand), 33.9
  in 29-32 GeV.
- The printed table under the fit is unchanged: 32.31 +- 10.87 signal, "background events
  (overall)" 1457.06 +- 89.71.

Amendment 0.20 section 2 fixed what this decides: 1,489 +- 20 % entries would have meant that Fig. 5
shows a different sample; **362 +- 20 % means the figures agree and the table's background number
is unexplained.** The reading gives 362, so the second branch applies: **Fig. 5 and the fit figure
show the same sample, and A'-ALEPH (P1-P4 on Fig. 5) speaks for the sample ALEPH fitted.**

## 2. Why the table says 1457 (analysis after the reading; information, not pre-registered)

**(a) The curve.** In an extended maximum-likelihood fit the fitted total equals the number of
events fitted. The curve integrates to 362.7 over 15-50 GeV, the data to 362. So the fit's total
in its own range is about 363, not 1,489.

**(b) The table's own errors.** In an extended fit the likelihood factorises into
Poisson(N | s + b) and a term that depends only on s/(s + b) and the shapes, so the Hesse variance
of s + b is exactly N:

    sigma_s^2 + sigma_b^2 + 2 rho sigma_s sigma_b = N = s + b.

With the printed numbers (10.87, 89.71, N = 1489.37) this needs **rho = -3.42**, which is
impossible (|rho| <= 1). Any extra constraint on b would only lower Var(s + b), so this holds for
a constrained background too. If instead the printed background (and its error) is k times the
background inside the fit, |rho| <= 1 needs **k >= 2.52** (and k <= 37). The curve gives
k = 1457.06 / (362.7 - 32.31) = **4.41**, and then rho = -0.38, an ordinary value for a peak on a
falling background. Code and tests: [stats/fit_table_check.py](stats/fit_table_check.py)
(`python -m unittest -v test_fit_table_check`).

**(c) The background under the peak.** Taking the fitted signal as a Breit-Wigner (full width 1.78
GeV, our reading of "BW width") smeared by a 0.74 GeV Gaussian at 30.40 GeV and approximating it with
a pseudo-Voigt profile, 19.2 of the 32.31 signal events fall in 29-32 GeV. The curve there is 33.9,
leaving **about 14.7 background events**, against 15.4 in the binned electron-muon background of
Fig. 5. At the table's scale it would be about 65.

**Reading.** The table's "(overall)" background is a normalisation of the smooth electron-muon
background over a range wider than the fit window, about 4.4 times the number of background
events inside 15-50 GeV. We cannot see the wider range in the paper (the figures are drawn from 5
GeV with a y axis that ends at 70); a reading of the 5-15 GeV region is requested (section 4).
Everything in the paper's significances (Z_asym 5.35, Z_Bi 2.63) goes with the figure's scale, as
amendment 0.20 found by hand. **This removes the "scale puzzle" as a limit on A'-ALEPH.**

## 3. Consequences, fixed now

1. A'-ALEPH (`aprime-aleph-v1`, toys at the reading's own scale) is graded as written, with no
   "speaks only for Fig. 5's sample" caveat. The summary still says the input is a by-eye reading.
2. `aprime-toys-v1` (built at 1457 background pairs) is graded as written (C1-C5). Its toys are
   about 4.4 times larger than ALEPH's fitted sample, so they calibrate the method for a sample of
   that size (closer to what DELPHI may give) and are **not** used for A'-ALEPH, as amendment 0.20
   rule 3 already says.
3. Nothing here touches the boson exclusions (NOTE-higgs-searches.md, NOTE-fourfermion.md): those
   use the excess's rate, 32.31 events in ALEPH's acceptance, not the background count.

## 4. One more reading, and what it decides (written before it is made)

Hands goal `ALEPHLOW` reads the 5-15 GeV bins of the fit figure and of Fig. 5 (data, curve,
electron-muon background, and whether any bin runs off the top of the axis), and copies any
sentence on the mass range of the electron-muon sample or its kernel-density estimate.

- **If** the sentences or the 5-15 GeV bins show a background over a wider range whose
  normalisation brings the total within 1,489 +- 20 % (or the background curve integrated over the
  stated range within 1,457 +- 20 %), section 2's reading is confirmed and is written as such.
- **If** the paper states a background range of 15-50 GeV only, section 2's identity still stands
  (it does not depend on the range), but the reason for the factor stays unexplained and is
  reported as found.
- Off-scale bins are reported as "not readable"; nothing is extrapolated.

## 5. Limits

Two by-eye readings by AI agents of the same author's figures; the curve values carry +-0.2 to
+-0.7 events each. The identity in section 2(b) is exact for a Hesse error matrix of an extended
fit; if the printed errors came from MINOS or from a different method, it holds only
approximately, though a factor of 3.4 beyond the bound is far outside any such difference. The
pseudo-Voigt split in 2(c) is approximate (to a few tenths of an event). None of this is a result of
the ALEPH Collaboration.
