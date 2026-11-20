# PLAN amendment v0.30: the excess in ALEPH's smooth frame with the ratio's slope set by ALEPH's own same-sign muon pairs, toy-calibrated (tests P0-P4, job ssframe-v1), fixed before the same-sign control has returned

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written while jobs `aprime-slsm-v2` (amendment 0.29) and
`sscontrol-v1` (amendment 0.28) are both still queued, **before either has returned a number and
before job `ssframe-v1` exists**. Nothing here changes any earlier test or threshold.

## 1. Why this test, and why now

Amendment 0.28 sec. 3 said the same-sign constraint "in the smooth (par3) frame is pre-registered
only after `aprime-slsm-v1` is graded". That job's observed fit is graded (amendment 0.29: L0, L3
PASS; slope-free asymptotic Z0 2.2953), but its toys are still running as `aprime-slsm-v2`. We now
fix the par3 version **earlier than promised**, for one reason: written now, it is blind to the
control slope b_ctrl, which nobody has seen because `sscontrol-v1` has not run. Written after
sscontrol-v1, the tests would be set with b_ctrl in view. Nothing in this test depends on
aprime-slsm-v2's toys.

This is the number the significance story needs: **ALEPH's excess in ALEPH's own smooth frame,
with the background ratio's slope measured not in the signal sample but in ALEPH's same-sign muon
pairs, and calibrated with toys.**

## 2. Method (stats/ssframe.py 0.1.0, new module)

Every published module it uses is imported **unchanged** and fetched from main: aprime_slsm 0.1.0
and aprime_smooth 0.1.0 (sha256 must equal what aprime-slsm-v1 ran: 66225147..., eae6510a...,
fatal otherwise), sscontrol 0.1.0, dmcratio 0.1.0 and aprime_cross 0.1.0 (sha256 printed).

1. **Control slope**, exactly as sscontrol 0.1.0 defines it (amendment 0.28 sec. 3), through its
   own helpers: W = [15 GeV, hi), hi the largest edge with every value of every spectrum readable
   (38 GeV on the committed readings); at zero signal, model "bb", b_SS and b_emu against ALEPH's
   simulation; **b_ctrl = b_SS - b_emu, sigma_ctrl = hypot(sigma_SS, sigma_emu)**.
2. **Excess**: Fig. 5 reading, 15-50 GeV, aprime_slsm's likelihood (smooth log-cubic e mu shape
   fitted jointly to both spectra, ratio r exp(b (x - 30.40)), ALEPH's fixed signal shape, mu >= 0),
   plus the constraint term -0.5 ((b - b_ctrl) / sigma_ctrl)^2. One extra fit start at b = b_ctrl
   is added to aprime_slsm's starts (0, +-0.03). Z0 = sqrt(q0) of the constrained profile.
3. **Toys**: background-only, from the constrained mu = 0 fit (a, r, b~). In each toy both spectra
   are Poisson-fluctuated and the auxiliary control value is redrawn, b_aux ~ N(b~, sigma_ctrl)
   (seed 20261122 + idx). 6,000 toys requested on 4 workers; the run stops submitting at 13,000 s;
   toys are saved every 250; grades use the contiguous prefix of finished toys and need at least
   1,000 of them (the rule of amendment 0.29).

Reported whatever happens (information, not graded): b_SS, b_emu, b_ctrl with intervals; the
asymptotic constrained Z0, mu_hat, b_hat, b at mu = 0 and both pulls (b - b_ctrl) / sigma_ctrl;
Z0 with b fixed at b_ctrl and at b_ctrl +- sigma_ctrl; background against data in 29-32 GeV; toy
p(Z >= 2), p(Z >= 3), mean Z, mean mu, mean b at mu = 0. Outputs `ssframe.json`, `toys.csv`,
last line `SSFRAME:`.

## 3. Tests

| | statement | prior |
|---|---|---|
| P0 | **gate**: unit tests pass; through sscontrol's helpers the module reproduces dmcratio-v1's 15-50 GeV slopes (OFF -> 0) within 0.001; the window is 15-38 GeV and every value in it is readable; sigma_ctrl exists; aprime_slsm's constant-ratio Z0 3.1340 is reproduced within 0.005 and its slope-free Z0 2.2953 within 0.01; a constraint of 0 +- 10 per GeV reproduces the slope-free Z0 within 0.01. If not, P1-P4 are NOT GRADABLE | 85 % |
| P1 | **main**: the toy-calibrated Z0 of the excess with the same-sign-constrained slope is **below 3.0** | 90 % |
| P2 | it is **below 2.0** | 25 % |
| P3 | goodness of fit of the constrained background-only fit: toy p of the deviance >= 0.01 | 85 % |
| P4 | the asymptotic formula holds for this test: toy rate of Z0 >= 2 in [0.012, 0.035] | 70 % |

If no toy reaches the observed Z0, the calibrated value is a lower bound (p < 3 / N) and P1 / P2
are FAIL when the bound reaches the threshold and UNDETERMINED otherwise (aprime_slsm's rule).

## 4. Meaning, written now

- **P1 PASS, P2 FAIL**: in ALEPH's own smooth frame, with the ratio's slope taken from ALEPH's own
  same-sign control, the excess is between 2 and 3 standard deviations, local, before any
  look-elsewhere correction: below the level usually called evidence.
- **P2 PASS**: below 2 sigma local: once the drift that ALEPH's own same-sign muon pairs show is
  allowed for, the 30 GeV excess is not significant in this frame.
- **P1 FAIL**: 3 sigma or more survives the same-sign control in the smooth frame; the muon-pair
  drift does not explain the excess.
- **Read jointly with sscontrol-v1** (graded by its own rules): if its W2 FAILS (the joint slope of
  both charges is below 2 sigma), the control does not establish the drift, and P1 / P2 are stated
  as conditional on it. If its W4 FAILS (the control does not predict the data's slope), the
  constraint is the wrong model for the opposite-sign rise, and this test's number is reported
  but not used as the headline.
- Whatever happens: no number here says whether the excess is real. Only data ALEPH did not use
  (DELPHI's open data) can.

## 5. Disclosure: what we knew when writing this

Seen: every figure reading; all graded results to amendment 0.29 (constant-ratio par3 Z0 3.13,
toy-calibrated 3.35; slope-free 2.30 asymptotic; the data's slope at zero signal 0.0266, 1 sigma
[0.0149, 0.0384]; with the signal floated 0.0107). The sums in amendment 0.28 sec. 4 (same-sign
data / simulation 0.953 in 15-25 GeV and 1.297 in 25-38 GeV; e mu 1.058 and 0.958).
**Not seen**: b_ctrl and sigma_ctrl as computed, and anything from sscontrol-v1 or aprime-slsm-v2.

Our rough hand arithmetic from those sums (not fitted, not a test): b_SS about 0.03 per GeV, b_emu
about -0.01, so b_ctrl about 0.04 +- 0.03; combined with the data's own preference this suggests a
constrained asymptotic Z0 of about 2.0-2.3 and a calibrated value about 0.1-0.2 higher. That is
where the priors come from.

## 6. Limits

Readings by AI agents of published figures, not ALEPH's events. The control slope is measured on
15-38 GeV and applied to 15-50 GeV. Same-sign and opposite-sign muon pairs come from different
processes in b b-bar events, so using one as the other's control is an assumption (tested in part
by sscontrol-v1's W2 and W4). The simulation histograms are pseudo-counts at the data's size. A
log-linear ratio is one shape. No look-elsewhere correction.
