# PLAN amendment v0.24: ALEPH's excess with a smooth background that keeps its counting error (tests K0-K4)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after `aprime-toys-v1` was graded (NOTE-aprime 0.2 sec. 7)
and **before job `aprime-smooth-v1` has produced any number**. `aprime-ext-v1` (amendment 0.23) is
still queued; nothing here changes its rules. Nothing in earlier grades changes.

## 1. Why

NOTE-aprime 0.1 gave two figures for ALEPH's 30 GeV excess on the blind reading of Heister's Fig. 5:
Z0 = 2.66 with the electron-muon template's Poisson error kept bin by bin ("bb"), and 4.18 with the
binned template treated as exact. "bb" lets every bin's true background float independently, so
it throws away the fact that the real background is a smooth function of mass. It is calibrated
(its false-excess rates match the nominal ones) but it is **conservative**: it gives up power.

The calibration toys (NOTE-aprime 0.2 sec. 7) add a second fact. At the fit table's scale, a
template smoothed with a 1 GeV Gaussian kernel and then treated as exact raises the false 2-sigma
rate only from 2.3 % to 3.8-4.4 %, while the unsmoothed template raises it to 9.7-12.5 %. Heister
smoothed his template with a kernel density estimate. So the 35-fold inflation quoted in NOTE-aprime
0.1 does not carry over to his method, and **2.66 may understate the excess**. The question a
physicist would ask next is: what is the significance when the background's smoothness is used
and its counting error is kept, and how well calibrated is each method at the figure's own scale?

## 2. Method (job `aprime-smooth-v1`, stats/aprime_smooth.py 0.1.0)

Input: the same blind reading (data/aleph-fig5.json, 15-50 GeV, 35 bins of 1 GeV); raw e mu counts
m_i = v_i / 0.532. ALEPH's signal fixed as before (Voigt 30.40 / 1.78 / 0.745 GeV; mu = 1 is 32.31
events). emuframe 0.1.0 fetched and blob-checked (d55c900f), unchanged.

| method | background |
|---|---|
| bb, exact | emuframe 0.1.0 (closure with NOTE-aprime 0.1) |
| kde05, kde1, kde2 | e mu template smoothed with a Gaussian kernel of 0.5, 1, 2 GeV, then treated as exact (binned analogue of Heister's KDE method) |
| **par3 (primary)**, par2, par4 | joint Poisson fit: e mu m_i ~ Poisson(T_i), mu mu n_i ~ Poisson(r T_i + mu s_i), T_i = exp(cubic (quadratic, quartic) in mass); shape and r free, so the template's counting error enters through the fitted shape |

Exact-type templates are floored at 0.5 raw counts per bin (the rule of aprime-toys 0.1.0).
Calibration: 10,000 background-only pseudo-experiments drawn from the par3 mu = 0 fit to the
reading (a smooth truth), both spectra fluctuated, every method applied to every toy. Toy-calibrated
Z = the one-sided Z of the fraction of toys at or above the observed Z0; if no toy reaches it, Z is
reported as a lower bound from p < 3 / 10,000.

## 3. Statements (written before any output)

| | statement | prior |
|---|---|---|
| K0 | **gate**: closure Z0(bb) = 2.664 and Z0(exact, unfloored) = 4.178 within 0.005, and the toys' "bb" rate of Z0 >= 2 is in [0.015, 0.031]. If not, K1-K4 are NOT GRADABLE | 90 % |
| K1 | **main**: the toy-calibrated Z of par3 is below 3.0 | 30 % |
| K2 | par3 is calibrated: its toys' rate of Z0 >= 2 is in [0.012, 0.035] | 80 % |
| K3 | par3 describes the reading: the toy p-value of its mu = 0 deviance (both spectra) is at least 0.01 | 80 % |
| K4 | the 1 GeV smoothed template treated as exact, once calibrated by toys, agrees with par3 within 0.3 in Z | 50 % |

Reported whatever happens: every method's asymptotic Z0, toy-calibrated Z, rates of Z0 >= 2 and
>= 3, mu_hat; the truth's background under 29-32 GeV; the deviance and its toy p-value. Last line
`APSMOOTH:`.

**Priors.** K1's prior is low because a smooth background pinned by 35 bins of e mu data has a much
smaller error under 30 GeV than one bin's own count; our rough expectation, made before the job,
is a calibrated par3 value between 3 and 4. We write that down so that a result there cannot be
presented as a surprise.

## 4. Meaning, written now

- **K1 PASS** (calibrated par3 below 3.0): even with the background's smoothness used, ALEPH's
  excess in its own electron-muon frame is below 3 sigma local. NOTE-aprime 0.1's conclusion
  stands with a stronger method behind it.
- **K1 FAIL** (3.0 or more): NOTE-aprime 0.1's 2.66 is the figure of a method that discards the
  background's smoothness, not the honest significance. With the template's counting error kept and
  its smoothness used, the local excess is at least 3 sigma, and most of the gap between 2.66 and
  4-5 sigma was lost information, not template noise. **We will say so in NOTE-aprime 0.3 and in
  any article before it is published**; the draft article "drops to 2.6 sigma" is held until this
  job is graded.
- **K3 FAIL**: the cubic shape does not describe the reading; K1 is then reported but not used for
  any headline, and par4 is shown beside it.
- **K4** tells how far Heister's style of method (smoothed template as exact) departs from a
  calibrated one at this scale, which bears on his 5.35.
- Whatever happens, no statement here says whether the excess is real. A mass-dependent mu mu / e mu
  ratio (amendment 0.23, `aprime-ext-v1`) would raise the background under 30 GeV in every method;
  combining a smooth shape with a slope is the next step once both jobs are graded.

## 5. Limits

The input is an AI agent's reading of a published figure, not ALEPH's events. A log-polynomial is
one family of smooth shapes; par2 and par4 are reported to show the dependence. The truth for the
toys is itself fitted to the reading. No look-elsewhere correction is applied.
