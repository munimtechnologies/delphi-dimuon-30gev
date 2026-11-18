# PLAN amendment v0.14: grading of dimu-envcast-v1 and the toy test of the chosen background treatment

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-18. Made with AI agents; not yet checked by a
physicist. CC BY 4.0 (text); code Apache-2.0.

This amendment is part of the pre-registration. It extends PLAN.md v0.11 and amendments 0.12 and
0.13 and will be merged into PLAN.md v1.0. It is published **before any DELPHI dimuon mass in the
26-35 GeV window has been seen**. No DELPHI data are used below.

## 1. What job dimu-envcast-v1 returned

`stats/envcast.py` 0.1.0 with `stats/bkgsys.py` 0.1.0 ran on 2026-11-18 from 08:48 to 10:28 UTC
(job `dimu-envcast-v1`). All 11 bkgsys unit tests passed and the Asimov part covered all eight
scenarios C1-C8. The toy part stopped at its 75-minute budget after **11 toys at mu = 0 and 10
at mu = 1**, not the planned 200, because every toy fitted all five background degrees on the
whole mu grid (about 7 minutes per toy per worker). Outputs: `analysis/results/envcast/`.

Asimov results for test B (one signal strength across the b-tagged and not-b-tagged spectra),
where "spur" is the fitted mu on background-only data, sigma is its statistical standard deviation,
and "mh1" is the fitted mu when an ALEPH-sized signal (mu = 1) is injected:

| scenario | old: spur / sigma, mh1 | fix3 | env | env_min2 |
|---|---|---|---|---|
| C1 power laws | 0.00, 1.000 | 0.00, 1.000 | 0.00, 1.000 | 0.00, 1.000 |
| C2 mixed untagged (f 1.5) | **-0.56**, **0.733** | -0.00, 0.999 | +0.04, 1.020 | +0.04, 1.022 |
| C3 (f 2.0) | +0.01, 1.004 | -0.01, 0.996 | +0.01, 1.004 | +0.01, 1.004 |
| C4 (f 3.0) | -0.04, 0.975 | -0.01, 0.996 | -0.04, 0.975 | -0.05, 0.972 |
| C5 (92-95 data) | +0.06, 1.020 | -0.00, 0.999 | +0.06, 1.020 | +0.06, 1.022 |
| C6 exponential b bbar | **+0.29**, **1.132** | +0.01, 1.005 | **+0.29**, **1.132** | **+0.29**, **1.132** |
| C7 non-b same shape | 0.00, 1.000 | 0.00, 1.000 | 0.00, 1.000 | 0.00, 1.000 |
| C8 resolution 1.2 % | **-0.51**, **0.773** | -0.00, 0.999 | +0.04, 1.017 | +0.04, 1.018 |

Test B's expected 95 % sensitivity in C2 (ul_sens, in units of the ALEPH signal): old 0.911 (biased),
fix3 1.057, env 0.958, env_min2 1.000; test A (b-tagged only): old/env 1.402, fix3 1.604.

### Grades of the expectations written in amendment 0.12, section 3

| | expectation | result | grade |
|---|---|---|---|
| K0 | `old` reproduces combcast's mu_hat(mu = 1) within 0.03 | C2 U 0.5134, C8 U 0.589, C6 T 1.1323, C7 U 1.000, C4 U 0.9372, tagged power laws 1.000 | **PASS** |
| K1 | C2 untagged degree 1: spurious in [-0.56, -0.42], abs/sigma >= 0.6 | -0.4725; 0.4725 / 0.6189 = 0.76 | **PASS** |
| K2 | `ss` degree 1 in power-law tagged categories; >= 2 in C2 U, C8 U, C6 T | 1 in all seven; 2, 2, 2 | **PASS** |
| K3 | `env` passes criterion (a) | fails in C6 test B: spurious 0.126 = 0.29 sigma (also test A 0.19 sigma, at the edge) | **FAIL** |
| K4 | `env` ul_sens(B, C2) <= 1.25 x `ss` | 0.958 vs 0.958 (ratio 1.00) | **PASS** |
| K5 | chosen treatment: C2 ratio ul_sens(B)/ul_sens(A) in 0.60-0.85 | fix3 0.659 (provisional, see section 2) | **PASS** (provisional) |
| K6 | C2 toys, test B, mu = 1: P(EXCL) `old` 0.07-0.25; chosen <= 0.07 | old 1/10, fix3 0/10 | **not graded** (10 toys) |
| K7 | C2 toys, test B, mu = 0: P(EXCL) chosen 0.45-0.85 | fix3 5/11 | **not graded** (11 toys) |

**Why `env` fails (K3).** In C6 the Z -> b bbar shape is an exponential, not a power law, in both
categories. The envelope is a minimum of -2 ln L plus one unit per shape parameter. With an injected
signal it prefers degree 2 in both categories, because degree 3 improves the fit by less than the
one-unit penalty, yet degree 2 leaves a spurious signal of +0.13 in each category. In test B the two
biases add while the statistical error shrinks, so the combined bias is 0.29 sigma. A positive
spurious signal would make a false "COMPATIBLE" verdict more likely (a false confirmation of ALEPH).
The prior written in 0.12 ("about even odds") was honest: it went the other way.

## 2. What the decision rule of 0.12 now says

Criterion (a), all eight scenarios, tests A and B, |spurious| <= 0.2 sigma and |mh1 - 1| <= 0.2
sigma_up: **`fix3` passes; `old`, `env` and `env_min2` fail** (`ss` passes but uses the truth and
is not eligible). So `fix3` is the only candidate, and it becomes the background treatment of plan
v1.0 **if it passes criterion (b)**: in scenario C2 with a true ALEPH-sized boson,
P(EXCLUDED) <= 0.07 for test A and for test B. If it fails (b), the fallback of 0.12 applies
(smallest worst-case |spurious|/sigma plus a Gaussian additive mu term).

Price of the safe choice: in C2, test B's expected sensitivity is 1.057 with fix3 against 0.958
for env (about 10 % weaker), and test A's is 1.604 against 1.402.

## 3. Job dimu-envtoys-v1 and its expectations, written before it runs

New code: `stats/envtoys.py` 0.1.0 with `stats/test_envtoys.py` (6 tests). It reuses
`envcast.asimov_block`, `envcast.method_curve`, the same scenario (C2), Poisson draws, mu grid,
CLs sigma(mu) and outcome rules. A unit test checks that its outcome code agrees with
`envcast.analyse_toy` (one definition). It fits only degree 3 in every toy, plus the sideband-rule
degree in the mu = 1 toys (for `old`). Plan: 200 toys at mu = 1 and 120 at mu = 0, under a
195-minute budget, written chunk by chunk (order 1, 1, 0, ... so mu = 1 fills first). Criterion (b)
is graded only with at least 150 toys at mu = 1; otherwise it is UNDETERMINED and the job is
re-run with more time.

- N0 (closure): the job's Asimov C2 numbers equal envcast's: fix3 test B spurious -0.001, ul_sens
  1.0566, mh1 0.999; old test B mh1 0.7326 (same code, so exact to 1e-4).
- N1 (criterion b): fix3 P(EXCLUDED | mu = 1) <= 0.07 for test A and for test B. Hand estimate:
  about 0.02-0.04 (an unbiased Gaussian estimator with sigma 0.53 and a CLs limit near
  mu_hat + 1.96 sigma gives 0.025; CLs is a little conservative). **Prior: 85 % PASS.**
- N2 (= K6, `old`): P(EXCLUDED | mu = 1), test B, in 0.07-0.25 (hand 0.13), i.e. the old rule's
  bias raises the false-exclusion rate of a real boson above 0.05.
- N3 (= K7): fix3 P(EXCLUDED | mu = 0), test B, in 0.45-0.85. Honest note added now (not a change
  of the range): with fix3's Asimov ul_sens of 1.06 the median CLs limit lies near 1.0-1.1, so I
  now expect a value near the lower edge (about 0.40-0.50); a value below 0.45 means that DELPHI
  alone excludes an ALEPH-sized boson less than half the time even when it is absent.
- N4: fix3 at mu = 1: mean mu_hat in [0.90, 1.10] for tests A and B; the standard deviation of
  mu_hat for test B in [0.45, 0.65] (Asimov sigma_up 0.53-0.56).
- N5: fix3 at mu = 0: mean mu_hat for test B in [-0.10, +0.10] (no spurious signal in toys).

What each outcome means for the DELPHI test: N1 PASS fixes the background treatment of plan v1.0
(fix3), which is merged into PLAN v1.0 at freeze. N1 FAIL triggers the 0.12 fallback, written and
tested before unblinding. In every case the treatment is also run on DELPHI's own simulated
background (KK2f q qbar through the full selection) before unblinding, as 0.12 requires.

## 4. Status of the other jobs (no change to their expectations)

`dimu-bbspur-v1` (amendment 0.13, M1-M6), `efhz-v1` and `lephz-v1` (NOTE-higgs-searches, J1-J7 and
L1-L10), and the DELPHI open-data jobs (`delphi-probe-v1`, `dimu-ntuple-v1`, `delsim-signal-v1`,
`dimu-val9293-v1`, `dimu-fourf-v1`) are still waiting for compute.
