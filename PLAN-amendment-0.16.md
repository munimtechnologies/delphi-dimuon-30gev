# PLAN amendment v0.16: first grading of dimu-envtoys-v1 and a top-up job for criterion (b)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-18. Made with AI agents; not yet checked by a
physicist. CC BY 4.0 (text); code Apache-2.0.

This amendment is part of the pre-registration. It extends PLAN.md v0.11 and amendments 0.12-0.15
and will be merged into PLAN.md v1.0. It is published **before any DELPHI dimuon mass in the
26-35 GeV window has been seen**. No DELPHI data are used below.

## 1. What job dimu-envtoys-v1 returned

`stats/envtoys.py` 0.1.0 ran from 14:00 to 17:22 UTC on 2026-11-18 (4 CPUs, 0.09 GB). All unit
tests of test_envtoys and test_bkgsys passed. The toys were slower than planned: **514 s per toy
per worker**, so the 195-minute budget gave **62 toys with a true ALEPH-sized signal (mu = 1) and
30 without (mu = 0)**, not 200 and 120. Criterion (b) needs at least 150 toys at mu = 1, so the job
itself reports it as UNDETERMINED, as amendment 0.14 section 3 required. Outputs:
`analysis/results/envtoys/` (envtoys.json, asimov.json, toys.jsonl, run.txt, tests.txt,
sha256.txt).

| | fix3, test A (b-tagged) | fix3, test B (combined) | old, test B |
|---|---|---|---|
| mu = 1: toys | 62 | 62 | 62 |
| mu = 1: mean mu_hat (std) | 1.024 (0.856) | 0.998 (0.566) | 0.879 (0.517) |
| mu = 1: P(EXCLUDED) (95 % interval) | 1/62 = 0.016 (0.000-0.087) | 2/62 = 0.032 (0.004-0.112) | 4/62 = 0.065 (0.018-0.157) |
| mu = 1: P(COMPATIBLE) | 0.129 | 0.258 | 0.339 |
| mu = 0: toys | 30 | 30 | - |
| mu = 0: mean mu_hat (std) | 0.113 (0.780) | 0.024 (0.490) | - |
| mu = 0: P(EXCLUDED) (95 % interval) | 8/30 = 0.267 (0.123-0.459) | 13/30 = 0.433 (0.255-0.626) | - |
| mu = 0: median upper limit | 1.66 | 1.08 | - |

## 2. Grades of the expectations written in amendment 0.14, section 3

| | expectation | result | grade |
|---|---|---|---|
| N0 | Asimov C2 closure: fix3 test B spurious -0.001, ul_sens 1.0566, mh1 0.999; old test B mh1 0.7326 | -0.001, 1.0566, 0.999; 0.7326 (exact) | **PASS** |
| N1 | fix3 P(EXCLUDED, mu = 1) <= 0.07 for tests A and B (needs >= 150 toys) | A 0.016, B 0.032 with 62 toys | **UNDETERMINED** (interim values inside the hand estimate 0.02-0.04) |
| N2 | old, test B: P(EXCLUDED, mu = 1) in 0.07-0.25 | 0.065 (0.018-0.157), 62 toys | **FAIL as written** (point value just below the range; not significant) |
| N3 | fix3, test B: P(EXCLUDED, mu = 0) in 0.45-0.85 | 0.433 (0.255-0.626), 30 toys | **FAIL as written** (at the lower edge, as the honest note in 0.14 expected) |
| N4 | fix3, mu = 1: mean mu_hat in [0.90, 1.10] for A and B; std (B) in [0.45, 0.65] | 1.024, 0.998; 0.566 | **PASS** |
| N5 | fix3, mu = 0: mean mu_hat (B) in [-0.10, +0.10] | +0.024 | **PASS** |

**What the failures mean.**
- *N2.* In toys the old sideband rule is less biased than on noise-free pseudo-data: its mean
  mu_hat at mu = 1 is 0.879, against 0.733 on the Asimov data set. A likely reason is that with
  Poisson noise the rule sometimes picks a higher degree in the not-b-tagged category, which
  removes the bias in those toys. The old rule is already excluded by criterion (a) (amendments
  0.14 and 0.15: biases of -0.56 and +0.52 sigma on noise-free data), so N2 does not change any
  decision. It only means the toy-level penalty of the old rule is smaller than expected.
- *N3.* With fix3, DELPHI's combined test excludes an ALEPH-sized boson in about 43 % of
  background-only experiments (median upper limit 1.08 times the ALEPH signal). That is the
  sensitivity the plan has to live with in scenario C2: **if there is no boson, DELPHI alone
  will more often than not return INCONCLUSIVE, not EXCLUDED.** This is reported now, before
  unblinding, so it cannot be explained away afterwards. Adding the not-b-tagged category raises the
  exclusion rate from 27 % (test A, b-tagged only) to 43 % (test B).

## 3. Job dimu-envtoys-v2 (top-up for criterion b), written before it runs

Same code (`stats/envtoys.py` 0.1.0, unchanged, fetched from this repository), same scenario C2,
**mu = 1 toys only** (`--ntoy1 160 --ntoy0 0`), a different master seed (`--seed 20271119`, so its
chunk seeds 20272119 and up do not overlap v1's 20262119 and up), 4 workers, 300-minute budget.
At v1's speed this gives about 140 toys.

**Pooling rule (fixed now, before v2 runs).** Criterion (b) is graded on all mu = 1 toys of v1
and v2 together: the EXCLUDED counts and the toy counts add, per test. It is graded only if the
pooled count is at least 150 per test; otherwise it stays UNDETERMINED and a v3 top-up with a third
disjoint seed follows under the same rule. v2 alone is also reported, but it does not decide.
N1 is then graded as written (P <= 0.07 for test A and for test B).

Expectations for v2 (new):
- N6: all unit tests pass and v2's Asimov numbers equal v1's (N0 closure again).
- N7: pooled fix3 P(EXCLUDED, mu = 1) <= 0.07 for test A and test B (= N1). Hand estimate 0.02-0.04;
  **prior 85 % PASS** (unchanged from 0.14).
- N8: pooled fix3 mean mu_hat at mu = 1 within [0.92, 1.08] for test B.

If N7 passes, fix3 is the background treatment of plan v1.0. If it fails, the fallback of 0.12
applies (smallest worst-case |spurious|/sigma plus a Gaussian additive mu term), written and tested
before unblinding.

## 4. Status of the other jobs (no change to their expectations)

Returned and graded: efhz-v1, lephz-v1 and kly-v1 (NOTE-higgs-searches.md 0.6: J1-J7, L1-L10,
K1-K9), dimu-bbspur-v1 (amendment 0.15). Still waiting for compute: the DELPHI open-data jobs
(`delphi-probe-v1`, `dimu-ntuple-v1`, `delsim-signal-v1`, `dimu-val9293-v1`, `dimu-fourf-v1`).
