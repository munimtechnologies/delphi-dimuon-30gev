# PLAN amendment v0.17: dimu-envtoys-v2 graded; criterion (b) still needs a v3 top-up

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents; not yet checked by a
physicist. CC BY 4.0 (text); code Apache-2.0.

This amendment is part of the pre-registration. It extends PLAN.md v0.11 and amendments 0.12-0.16
and will be merged into PLAN.md v1.0. It is published **before any DELPHI dimuon mass in the
26-35 GeV window has been seen**. No DELPHI data are used below.

## 1. What job dimu-envtoys-v2 returned

`stats/envtoys.py` 0.1.0 ran from 18:20 UTC on 2026-11-18 to 23:32 UTC (0.09 GB peak). The code is
byte-identical to v1: all eight sha256 sums in `sha256.txt` match v1's. All 17 unit tests of
test_envtoys and test_bkgsys passed. The job was given 2 CPUs for 4 workers, so a toy took 1208 s
instead of v1's 514 s. The 300-minute budget gave **60 toys with mu = 1** (seed 20271119), not
about 140. Outputs: `analysis/results/envtoys-v2/`.

| mu = 1 | fix3, test A (b-tagged) | fix3, test B (combined) | old, test B |
|---|---|---|---|
| v2: toys | 60 | 60 | 60 |
| v2: mean mu_hat (std) | 0.946 (0.853) | 0.994 (0.506) | 0.917 (0.497) |
| v2: EXCLUDED | 4/60 = 0.067 | 2/60 = 0.033 | 3/60 = 0.050 |
| v1: EXCLUDED | 1/62 | 2/62 | 4/62 |
| **pooled v1 + v2: EXCLUDED** | **5/122 = 0.041** | **4/122 = 0.033** | 7/122 = 0.057 |
| pooled 95 % interval (Poisson approximation) | 0.013-0.096 | 0.009-0.084 | 0.023-0.118 |
| pooled mean mu_hat | 0.986 | 0.996 | 0.898 |

## 2. Grades of the expectations written in amendment 0.16, section 3

| | expectation | result | grade |
|---|---|---|---|
| N6 | all unit tests pass; v2's Asimov numbers equal v1's | 17/17 OK; fix3 test B spurious -0.001, ul_sens 1.0566, mu_hat 0.999; old test B 0.7326; code identical | **PASS** |
| N7 (= N1) | pooled fix3 P(EXCLUDED, mu = 1) <= 0.07 for tests A and B, graded only if pooled n >= 150 | n = 122 per test; interim 0.041 (A) and 0.033 (B) | **UNDETERMINED** (pooled count below 150) |
| N8 | pooled fix3 mean mu_hat at mu = 1 in [0.92, 1.08], test B | 0.996 | **PASS** |

Both interim values are inside the hand estimate of 0.02-0.04 written in amendment 0.14. The upper
ends of their intervals are still above 0.07, which is why the 150-toy rule exists.

## 3. Job dimu-envtoys-v3 (second top-up), written before it runs

As the pooling rule of amendment 0.16 requires: same code (`stats/envtoys.py` 0.1.0, fetched from
this repository, unchanged), same scenario C2, mu = 1 toys only, a third disjoint master seed
(`--seed 20281119`; chunk seeds 20282119 and up), **2 workers on 2 CPUs** (so no worker waits for a
core), 300-minute budget. At v1's per-toy speed this gives about 70 toys, and at least 28 are needed.

**Pooling rule (unchanged):** EXCLUDED counts and toy counts of v1, v2 and v3 add, per test.
Criterion (b) and N7 are graded once the pooled count is at least 150 per test. If it is still
below 150, a v4 with seed 20291119 follows under the same rule.

Expectations for v3:
- N9: all unit tests pass, and v3's Asimov numbers and code hashes equal v1's.
- N7 graded on the pool, as written. **Prior 95 % PASS.** With 5/122 and 4/122 already in, test A
  passes if v3 adds no more than 7 exclusions in 60 toys (at the interim rate about 2-3 are expected).
- N10: pooled fix3 mean mu_hat at mu = 1 for test A in [0.90, 1.10] (pooled now: 0.986).

If N7 passes, fix3 is the background treatment of plan v1.0. If it fails, the fallback of amendment
0.12 applies.

## 4. Status of the other jobs (no change to their expectations)

Still waiting for compute: kly4f-v1 (F1-F5, NOTE-higgs-searches 0.6 section 6b) and the DELPHI
open-data jobs (`delphi-probe-v1`, `dimu-ntuple-v1`, `delsim-signal-v1`, `dimu-val9293-v1`,
`dimu-fourf-v1`).
