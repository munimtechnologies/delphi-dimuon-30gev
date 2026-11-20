# PLAN amendment v0.29: aprime-slsm-v1 timed out after its observed fit (L0 and L3 graded: both PASS; with the ratio free to rise, the asymptotic Z0 falls from 3.13 to 2.30); the toys are re-run unchanged by a wrapper that saves them as they finish (job aprime-slsm-v2)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `aprime-slsm-v1` ended and **before job
`aprime-slsm-v2` exists**. Every threshold of amendment 0.27 sec. 6 (L0-L5) is kept as written.
`sscontrol-v1` (amendment 0.28, W0-W5) is still queued; nothing here changes its rules.

## 1. What happened to aprime-slsm-v1

python:3.12, 2 CPUs, 6 h limit. Compile, fetch (aprime_smooth.py 0.1.0, sha256 eae6510a...), and the
8 unit tests passed. The observed fit finished in 7 s and was saved. The 10,000 background-only toys
ran at 0.2-0.3 toys per second: 4,000 had finished at 20,129 s when the job's 6 h limit stopped the
run step (exit 124). `aprime_slsm.run` writes its toys only after the last one, so **no toy result
exists** and nobody has seen one. Raw output, unedited: `analysis/results/aprime-slsm-v1/`
(`aprime_slsm.json`, `run.txt`, `tests.txt`, `fetch.txt`, `compile.txt`, `sha256.txt`, `job.json`).

## 2. Observed fit (from aprime_slsm.json, exactly as written by the job)

| model (Fig. 5 reading, 15-50 GeV, par3 smooth background) | Z0 (asymptotic) | mu_hat | ratio slope b (per GeV) |
|---|---|---|---|
| constant ratio (b = 0): closure against aprime-smooth-v1 | 3.1340 (want 3.1340) | 0.801 | 0 |
| **ratio free to rise** | **2.2953** | 0.690 | 0.0107 |
| slope at zero signal | - | 0 | 0.0266, 1 sigma [0.0149, 0.0384] |

The slope's signed Z against a constant ratio: **2.256 at zero signal** and **0.733 with the
signal floated** (b = 0.0107). Background under 29-32 GeV in the zero-signal slope fit: 23.16
events against 33 observed.

## 3. Grades that need no toy

| | statement (amendment 0.27 sec. 6) | result | grade |
|---|---|---|---|
| L0 | gate: unit tests pass; with b = 0 the new likelihood and aprime_smooth's ParFit both reproduce 3.1340 within 0.005 | 3.1340 and 3.1340; 8 tests OK | **PASS** |
| L3 | at zero signal the ratio rises: b > 0 and signed Z >= 2.0 | b = 0.0266, Z = 2.256 | **PASS** |

L1, L2, L4 and L5 need the toys and are **not graded yet**.

## 4. The re-run: job aprime-slsm-v2 (method unchanged)

`stats/slsm_chunk.py` 0.1.0 (new; aprime_slsm.py and aprime_smooth.py are fetched from main and
must match the sha256 aprime-slsm-v1 ran). It calls aprime_slsm's own `observe`, `one_toy` (seed
20261121 + idx, so toy k is the same pseudo-experiment as in v1), `z_from_count` and `grade`
unchanged. What is new:
- the pre-registered 10,000 toys are requested on 4 workers, and the run stops submitting toys
  after 19,800 s, so the job ends inside its 6 h limit;
- toys and interim grades are saved every 250 toys;
- grades use the **contiguous prefix** of finished toys (idx 0..K-1 all finished), so the graded
  set does not depend on which toys happen to be fast;
- L1, L2, L4 and L5 are graded only if the prefix holds **at least 1,000 toys**; otherwise they
  are reported NOT GRADABLE. L0 and L3 are re-graded from the same observed fit.

With fewer than 10,000 toys the calibration is coarser: at 1,000 toys a calibrated Z near 3 rests on
a handful of toys. Whatever number of toys the prefix holds is reported with every grade.

## 5. Disclosure and priors

This was written after seeing the observed fit above (asymptotic 2.30 with the slope free). No
threshold moved. Our priors, revised after seeing it (the original priors stay in 0.27): L1 (toy-
calibrated Z0 below 3.0) 95 %; L2 (below 2.0) 10 %; L4 (toy rate of Z0 >= 2 in [0.012, 0.035])
70 %; L5 (goodness of fit) 85 %. In aprime-smooth-v1 the toys raised the constant-ratio Z by 0.22,
so we expect about 2.4-2.6.

## 6. What the numbers already say (not a grade)

The pre-written meaning for L1 PASS with L3 PASS (amendment 0.27 sec. 6) is applied only after the
toys. What can be said now: in ALEPH's own frame, a smooth background with a constant mu mu / e mu
ratio puts the excess at 3.13 sigma (asymptotic; 3.35 toy-calibrated), and letting that ratio
change linearly in log with mass lowers it to 2.30 sigma (asymptotic). At zero signal the data
prefer the rising ratio at 2.26 sigma; with the signal floated, that preference falls to 0.73
sigma. In 15-50 GeV, a broad rise and a narrow peak at 30 GeV partly stand in for each other in
these 362 events. ALEPH's same-sign muon pairs (job sscontrol-v1) are the control that can tell
them apart; DELPHI's independent data can decide.

## 7. Limits

Readings by AI agents of published figures, not ALEPH's events. A log-linear ratio is one shape. No
look-elsewhere correction. The time budget and the 1,000-toy minimum were set after v1 timed out,
before any toy result existed.
