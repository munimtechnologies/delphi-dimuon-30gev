# PLAN amendment v0.32: both toy calibrations stopped short of 1,000 toys (not gradable yet) and are resumed from their saved toys with every test unchanged; the inverted-b-tag reading is in and committed before its job runs

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-21. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after jobs `aprime-slsm-v2` and `ssframe-v1` returned and the
blind reading of Heister's Fig. 24 came back, **before** job `abtag-v1` has run. No test, threshold
or prior of amendments 0.27, 0.29, 0.30 or 0.31 is changed.

## 1. aprime-slsm-v2 (amendment 0.29): stopped at 869 toys

The job ran 5.5 h on 4 CPUs and stopped at its time budget with a contiguous prefix of **869**
background-only toys, fewer than the 1,000 the grades need. Raw output:
`analysis/results/aprime-slsm/v2-partial/`.

| test | statement (0.27 sec. 6) | result |
|---|---|---|
| L0 | closures (par3 3.1340 both ways) | **PASS** (3.1340 / 3.1340) |
| L3 | the ratio rises at mu = 0 with b > 0, Z >= 2 | **PASS** (b = 0.0266 [0.0149, 0.0384], Z 2.26) |
| L1, L2, L4, L5 | calibrated Z < 3 / < 2; toy rate of Z >= 2 in [1.2 %, 3.5 %]; goodness of fit p >= 0.01 | **NOT GRADABLE** (869 < 1,000) |

Observed (asymptotic): slope free Z0 = 2.295 (mu_hat 0.69, b_hat 0.0107); constant ratio 3.134; the
slope with the signal floated 0.0107 (Z 0.73).

**Disclosure of what we have now seen** (the job prints its running numbers; they are not grades):
on the 869-toy prefix the slope-free Z0 is reached by 11 toys (p 0.0127, calibrated Z 2.24), the
toy rate of Z >= 2 is 3.2 %, the goodness-of-fit p is 0.69, and the constant-ratio Z0 3.134 is
reached by 25 toys when the truth has the fitted slope (calibrated 1.90).

## 2. ssframe-v1 (amendment 0.30): stopped at 309 toys

3.6 h, 4 workers on 2 CPUs, contiguous prefix **309**. Raw output: `analysis/results/ssframe/v1-partial/`.

- **P0 PASS**: control slope reproduced (b_ctrl 0.034512 +- 0.022177, as amendment 0.31 required:
  `CONTROL` line 0.0345 +- 0.0222, b_SS 0.0387, b_emu 0.0042, window 15-38 GeV); closures 3.1340
  (b = 0), 2.2953 (slope free), 2.2953 (loose constraint).
- Observed (asymptotic): **constrained Z0 = 2.134** (mu_hat 0.618, b_hat 0.0177, b at mu = 0 0.0284,
  pulls -0.28 / -0.76); with the slope fixed at b_ctrl 1.69, at b_ctrl - 1 sigma 2.59, at
  b_ctrl + 1 sigma 0.87; background 23.3 against 33 events in 29-32 GeV.
- **P1-P4 NOT GRADABLE** (309 < 1,000).
- **Disclosure**: in the saved 309 toys, 4 reach Z0 >= 2.134 (p 0.013, about 2.2 sigma) and 6 reach
  Z0 >= 2.0 (1.9 %). These are counts we made by reading the saved file; they are not grades.

## 3. Resuming instead of restarting (stats/toyresume.py 0.1.0, new module)

Every toy is a fixed pseudo-experiment (seed + toy index), so a stopped calibration can be
continued. `toyresume.py` imports aprime_slsm 0.1.0 + slsm_chunk 0.1.0, or ssframe 0.1.0, unchanged
(sha256 checked, fatal), recomputes the observed fits and toy truth as their drivers do, reads the
saved prefix, **re-runs toys 0-7 and requires every saved column to agree within 2e-5** (a mismatch
stops the job with no grade), then runs toys K, K+1, ... strictly in order until the requested total
or a 16,000 s budget, and grades the merged prefix with the original grading code (MIN_TOYS 1,000).

Jobs `toyres-slsm-v1` and `toyres-ssframe-v1` (4 CPUs, 1 GB each). Expected merged prefixes: about
1,550 and 1,150 toys on 4 CPUs (fewer if a job gets fewer CPUs).

**Stopping rule, fixed now.** Each calibration is graded on the merged prefix of the FIRST resume job
that leaves at least 1,000 toys, whatever its numbers say. If a resume job leaves fewer than 1,000,
one further resume of the same kind is filed from its merged file, unchanged. No calibration is
extended or stopped because of the values it shows.

Saved prior values carry 5 decimals; a saved toy within 1e-5 of an observed Z0 could compare
differently at full precision. The job prints how many there are (`near_ties`).

## 4. The Fig. 24 reading (inverted b-tag) is committed

`data/aleph-abtag24.json`: one blind reading of Heister's HTML Fig. 24 by an AI reading agent with no
access to our work, from the figure's vector coordinates. Log y axis, 1 GeV bins, ALEPH data against
the simulation's stack (b, c, uds). Data are whole numbers; data markers are missing at 36, 37, 39
and 43-49 GeV (NM -> 0); the simulation is below the axis floor at 43-49 GeV (OFF). Under amendment
0.31's rule the window is therefore **15-43 GeV**, 28 bins, **421 events** (331 at 15-25, 90 at 25-43);
simulation 317.2 and 76.8.

**What we saw while building the file, written down before the job runs.** Plain sums give data /
simulation 1.04 at 15-25 GeV and 1.17 at 25-43 GeV. A hand estimate from these two sums (mean masses
18.9 and 29.6 GeV) gives b_A about 0.011 +- 0.016 per GeV (Z about 0.7) and a pull against b_SS of
about -1.1; the bins at 29-32 GeV hold 8, 4 and 5 events against 8.4, 6.3 and 4.6. If the job
agrees, that is A1 FAIL, A2 PASS, A3 FAIL, A4 PASS, whose pre-written meaning (amendment 0.31 sec. 3)
is: "the inverted-tag sample cannot tell; undecided stays undecided". The grades come from job
`abtag-v1` (stats/abtag.py 0.1.0, unchanged), not from this estimate.

## 5. Limits

As before: readings by AI agents of published figures, not ALEPH's events; the simulation as
pseudo-counts at the data's size (conservative; amendment 0.31 sec. 2); one log-linear drift shape;
no look-elsewhere correction. The partial toy numbers above are information, not results.
