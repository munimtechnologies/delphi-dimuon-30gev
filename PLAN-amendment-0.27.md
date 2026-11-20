# PLAN amendment v0.27: smooth background graded (K1 failed: 3.1-3.4 sigma with a constant ratio); same-sign readings in, G0 fails as written on values below the log axis, and their rule fixed before any fit; next, smooth background AND a rising ratio together (tests L0-L5)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `aprime-smooth-v1` returned and after the two blind
readings of amendment 0.26 sec. 8 came back, **before any fit of those readings and before job
`aprime-slsm-v1` exists**. Every threshold of amendments 0.24-0.26 is kept. `apcross-v1`
(amendment 0.26) is still queued; nothing here changes its rules.

## 1. aprime-smooth-v1 graded (amendment 0.24): K1 FAILED

Full grades in [NOTE-aprime.md](NOTE-aprime.md) 0.4, section 9; raw output in
`analysis/results/aprime-smooth/`. In short: K0 (gate) PASS, **K1 FAIL** (the primary smooth
method, a log-cubic background fitted jointly to both spectra, gives Z0 = 3.13 asymptotic and
**3.35 toy-calibrated**, 4 of 10,000 background-only toys at or above it), K2 PASS (it is
calibrated), K3 PASS (it describes the reading, p = 0.54), K4 FAIL (the 1 GeV-smoothed template
treated as exact gives 3.04 calibrated, 0.32 from par3, against a 0.3 limit). Our expectation,
written before the job, was "between 3 and 4"; it was met.

So with a **constant** mu mu / e mu ratio, the excess in ALEPH's own frame is above 3 sigma
local when the background's smoothness is used, and NOTE-aprime 0.1's 2.66 was the figure of a
conservative method, as amendment 0.24 sec. 4 said it would be in this case. The draft article
"drops to 2.6 sigma" is withdrawn.

## 2. The same-sign and e mu readings, committed exactly as read

Both made by AI reading agents with no access to this repository, completed 2026-11-20
07:17-07:29 UTC, from the figures' vector coordinates.

- **R21** (`data/aleph-dmc21.json`): HTML Fig. 21, both panels "Events / 1 GeV", **logarithmic**
  y axis from about 0.293, 1 GeV bins; simulation drawn as a stack (b, c, uds). Data read exactly
  (marker centres), simulation to +-0.005. 21 data bins have **no marker drawn** (NM: OS 9, SS 12)
  and **20 simulation values lie below the bottom of the log axis** (OFF: OS 8, SS 12; the reader:
  "unknown, somewhere in 0 to 0.29").
- **R3** (`data/aleph-emu3.json`): HTML Fig. 3, linear 0-70, 1 GeV bins, data points and one
  simulation line, +-0.05 per bin; 10 NM data bins (40-49 GeV), no OFF.

Consistency, seen while committing (not a test): R21's opposite-sign data equal the Fig. 5
reading's muon counts in all 35 bins (NM as 0), and R3's data lie within 0.2 of Fig. 5's e mu
values in every bin. Wherever both exceed 1, R21's opposite-sign simulation is Fig. 4's simulated
mu mu times about 1.05, and R3's simulation equals Fig. 4's simulated e mu to 0.1 in 15-42 GeV
(above that both lie on the axis floor). Four independent readings of four figures agree.

## 3. G0 graded as written: FAIL

G0 (amendment 0.26 sec. 8) required every R21 and R3 value in 15-50 GeV to be readable after the
NM -> 0 rule. The 20 OFF simulation values are not, so **G0 fails as written**, and D1, D2, S1, S2
cannot be graded under 0.26 alone. The playbook lesson of amendment 0.26 (separate "no marker" from
"off the axis") was applied to the reading request, but the gate did not foresee a log axis whose
floor hides small simulation values. The job reports G0 as written.

## 4. What is added (secondary, labelled as such in every report)

stats/dmcratio.py 0.1.0 (a new module; aprime_cross.py is not changed) fits each spectrum as
amendment 0.26 sec. 8 says, with the OFF values filled in two ways:

| fill | rule | grades |
|---|---|---|
| zero | OFF -> 0.0 (the lower end of the reader's range) | **D1z, D2z, S1z, S2z** (secondary) |
| ceil | OFF -> 0.29 (the upper end) | D1c, D2c, S1c, S2c (sensitivity) |

NM -> 0 in both (amendment 0.26). Thresholds are those of amendment 0.26 sec. 8, unchanged. A grade
that differs between the fills is reported as **reading-dependent**. D2 uses R3 only, which has no
OFF value, so D2z = D2c. G1 is graded as written. Information: the C0 closure of aprime_cross (module
integrity), the opposite-sign slope with ALEPH's signal floated, and b_OS - b_emu with its pull.
Job `dmcratio-v1`; last line `DMCRATIO:`.

## 5. Disclosure: what we saw before writing this

The rule above was written after seeing the readings. Plain arithmetic on them (the readers' own
sums; OFF bins left out). It is not a test and was not fitted.

| data / simulation | 15-25 GeV | 25-50 GeV |
|---|---|---|
| opposite-sign mu mu (Fig. 21 left) | 257 / 252.8 = 1.017 | 105 / 77.7 = 1.351 |
| same-sign mu mu (Fig. 21 right) | 186 / 195.1 = 0.953 | 49 / 36.9 = 1.328 |
| e mu (Fig. 3) | 239.5 / 226.3 = 1.058 | 62.1 / 66.0 = 0.941 |

On these sums both muon samples rise against simulation above 25 GeV by about a third, and the
e mu data fall slightly. Where they rise differs: opposite-sign pairs exceed simulation in
25-31 GeV (78 against 58.2) and agree in 32-37 GeV (19 against 16.7); same-sign pairs agree in
25-31 GeV (31 against 31.3) and exceed simulation in 32-37 GeV (17 against 5.7). Heister's paper
says only that the same-sign spectrum shows "no excess". Our priors after seeing this (not before):
D1z 70 %, D2z 75 %, S1z 40 %, S2z 15 %. A 32-37 GeV same-sign cluster found by eye is not a
result, and we will not treat it as one.

## 6. Next test, pre-registered now: a smooth background AND a rising ratio (tests L0-L5)

Two graded answers now pull opposite ways: the smooth background raises the excess to 3.1-3.4
sigma (constant ratio), and a log-linear ratio lowers it to 1.62 (bin-by-bin background,
aprime-ext-v1). Amendment 0.24 sec. 4 named the next step: combine them.

**Method** (stats/aprime_slsm.py 0.1.0; job `aprime-slsm-v1`; imports stats/aprime_smooth.py
0.1.0 unchanged). Input: data/aleph-fig5.json, 15-50 GeV. e mu m_i ~ Poisson(T_i), T = exp(cubic)
as par3; mu mu n_i ~ Poisson(r exp(b (x_i - 30.40)) T_i + mu s_i), b free in [-0.2, 0.2] per GeV;
ALEPH's fixed signal (emuframe 0.1.0, blob-checked). Toys: 10,000 background-only pseudo-experiments
from the mu = 0 slope fit to the reading, both spectra fluctuated. Toy-calibrated Z as in
amendment 0.24.

| | statement | prior |
|---|---|---|
| L0 | **gate**: unit tests pass, and with b fixed at 0 the new likelihood and aprime_smooth's own ParFit both reproduce par3's Z0 = 3.1340 within 0.005. If not, L1-L5 are NOT GRADABLE | 90 % |
| L1 | **main**: with the slope free, the toy-calibrated Z0 is below 3.0 | 85 % |
| L2 | with the slope free, the toy-calibrated Z0 is below 2.0 | 45 % |
| L3 | at zero signal the ratio rises: b > 0 and its signed Z against a constant ratio >= 2.0 | 70 % |
| L4 | calibration: the toys' rate of Z0 >= 2 (slope free) is in [0.012, 0.035] | 80 % |
| L5 | the mu = 0 slope fit describes the reading: toy p-value of its deviance >= 0.01 | 85 % |

Reported whatever happens: Z0 and mu_hat with b = 0 and with b free; b at mu = 0 with its 1-sigma
interval; the slope's signed Z with the signal floated (the degeneracy rule); the constant-ratio
par3 Z0 calibrated on the slope-truth toys; the toys' rates; the background under 29-32 GeV. Last
line `APSLSM:`.

**Meaning, written now.**
- **L1 PASS with L3 PASS**: in ALEPH's own frame, with the background's smoothness used and its
  counting error kept, the excess passes 3 sigma local only if the mu mu / e mu ratio is assumed
  constant; the data prefer a rising ratio, and with it the excess is below 3 sigma. The 3.1-3.4
  sigma of section 1 is then conditional on an assumption the data disfavour, and the question
  moves to where the rise comes from (dmcratio-v1 and, for DELPHI, test A' with its own ratio check).
- **L1 FAIL**: the excess survives a rising ratio at 3 sigma or more once smoothness is used; the
  1.62 of aprime-ext-v1 then came mostly from the bin-by-bin background's freedom, and the excess
  is more robust in ALEPH's frame than NOTE-aprime 0.3 sec. 8 suggested. We will say so first.
- **L3 FAIL**: with a smooth background the rise is not significant; aprime-ext-v1's 2.26 owed much
  to template noise.
- Whatever happens: in 15-50 GeV a broad rise and a narrow peak are partly interchangeable
  (NOTE-aprime sec. 8d), so "slope free" also absorbs part of any real signal. No statement here
  says whether the excess is real; only data ALEPH did not use (DELPHI's) can.

## 7. Limits

Readings by AI agents of published figures, not ALEPH's events. The simulation histograms are
normalised and used as pseudo-counts at the data's size, which overstates their noise if ALEPH's
simulation is larger than its data. A log-linear ratio is one shape. The OFF rule (sec. 4) and the
priors in sec. 5 were written after the readings were seen; the L0-L5 test was written before its
job existed, but after the two results it combines were known. No look-elsewhere correction.
