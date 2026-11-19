# PLAN amendment v0.18: the background treatment is settled (criterion (b) passes on 166 pseudo-experiments)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents; not yet checked by a
physicist. CC BY 4.0 (text); code Apache-2.0.

This amendment is part of the pre-registration. It extends PLAN.md v0.11 and amendments 0.12-0.17
and will be merged into PLAN.md v1.0. It is published **before any DELPHI dimuon mass in the
26-35 GeV window has been seen**. No DELPHI data are used below.

## 1. What job dimu-envtoys-v3 returned

`stats/envtoys.py` 0.1.0 ran from 01:18 to 06:26 UTC on 2026-11-19 (0.08 GB peak, 2 workers on 2
CPUs, 568 s per toy). All eight sha256 sums in `sha256.txt` equal v1's and v2's (envtoys.py
7259a115..., bkgsys.py 6bf2cb86...). All 17 unit tests passed. The 300-minute budget gave **44
toys with mu = 1** (seed 20281119), fewer than the 60-70 hoped for but more than the 28 needed.
Outputs: `analysis/results/envtoys-v3/`.

## 2. The pool (`stats/envpool.py` 0.1.0, `analysis/results/envtoys-pool/pool.json`)

Per the pooling rule of amendment 0.16, EXCLUDED counts and toy counts add per test. The pooled
mean is the toy-weighted mean of the three batch means. Every number was worked out by hand and is
recomputed by `stats/test_envpool.py`.

| mu = 1 | v1 | v2 | v3 | **pool** |
|---|---|---|---|---|
| fix3, test A (b-tagged): EXCLUDED | 1/62 | 4/60 | 1/44 | **6/166 = 0.036** |
| fix3, test B (combined): EXCLUDED | 2/62 | 2/60 | 0/44 | **4/166 = 0.024** |
| old rule, test B: EXCLUDED | 4/62 | 3/60 | 1/44 | 8/166 = 0.048 |
| fix3, test A: mean mu_hat | 1.0236 | 0.9457 | 0.9561 | **0.9776** |
| fix3, test B: mean mu_hat | 0.9977 | 0.9938 | 1.0763 | 1.0171 |
| old rule, test B: mean mu_hat | 0.8791 | 0.9174 | 0.9455 | 0.9105 |

Exact 95 % (Clopper-Pearson) intervals, bracketed by hand from the binomial sums and checked by the
test: test A 0.012-0.015 to **0.075-0.080**; test B 0.005-0.008 to 0.060-0.062. For example,
P(X <= 6 | n = 166, p = 0.075) = 0.0307 and P(X <= 6 | p = 0.080) = 0.0183, so the upper end for
test A lies between 0.075 and 0.080.

## 3. Grades of the expectations written in amendment 0.17, section 3

| | expectation | result | grade |
|---|---|---|---|
| N9 | all unit tests pass; v3's Asimov numbers and code hashes equal v1's | 17/17 OK; 8/8 hashes equal; fix3 test B spurious -0.001, ul_sens 1.0566, mu_hat 0.999; old test B 0.7326 | **PASS** |
| N7 (= N1, criterion (b)) | pooled fix3 P(EXCLUDED, mu = 1) <= 0.07 for tests A and B, n >= 150 | 166 toys per test; 0.036 (A), 0.024 (B) | **PASS** (prior 95 %) |
| N10 | pooled fix3 mean mu_hat at mu = 1, test A, in [0.90, 1.10] | 0.9776 | **PASS** |

**Consequence, as written in amendment 0.17:** criterion (b) passes, so the **fixed degree-3
background in every category ("fix3") is the background treatment of plan v1.0**. The fallback of
amendment 0.12 is not used.

## 4. What this does and does not establish

- **Stated plainly:** the rule decides on the point estimate, as written in amendment 0.12 and coded
  in `envtoys.criterion_b`. For test A the upper end of the exact 95 % interval (0.075-0.080) is
  still slightly above 0.07. So the data do not prove the false-exclusion rate is below 7 %; they
  show the best estimate is about half of it. Test B's interval lies wholly below 0.07.
- The fix3 fit is unbiased for a real ALEPH-sized signal: pooled mean fitted signal 0.98 (test A)
  and 1.02 (test B). The old degree rule is biased low in test B (0.91), as amendments 0.12-0.15
  found by other means.
- The sensitivity limit reported in amendment 0.16 stands: with no boson present, DELPHI's combined
  test excludes an ALEPH-sized one in only about 43 % of pseudo-experiments (30 toys), so
  INCONCLUSIVE remains a likely outcome if the excess is not real.
- These are pseudo-experiments built from simulation shapes and yields (combcast 0.1.0). They test
  the statistics, not the DELPHI detector.

## 5. What is next

The statistics part of plan v1.0 is now frozen. Plan v1.0 still needs the DELPHI open-data jobs
(`delphi-probe-v1`, `dimu-ntuple-v1`, `delsim-signal-v1`, `dimu-val9293-v1`, `dimu-fourf-v1`),
which have not started, and kly4f-v1 (F1-F5, NOTE-higgs-searches 0.6 section 6b) is still waiting
for compute. No further toy top-ups are planned.
