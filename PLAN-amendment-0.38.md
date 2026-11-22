# PLAN amendment v0.38: toyres-ssframe-v1 stopped at 934 toys, still short of the 1,000 its grades need; the one further resume fixed in amendment 0.32 is filed unchanged

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-22. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `toyres-ssframe-v1` returned (resume rule of
amendment 0.32 sec. 3; tests P0-P4 of amendment 0.30). `delphi-rootless-probe-v1` (0.33),
`leescan-v1` (0.34) and `dimu-ntuple-rl-v1` (0.35) are still queued and have returned nothing. No
test, threshold, prior or blinding rule of plan v0.11 or amendments 0.12-0.37 is changed.

## 1. The run

Job `toyres-ssframe-v1`, Dell, 2026-11-22 01:59 to 06:35 UTC (16,520 s), 4 CPUs, peak memory 0.08 GB.
`stats/toyresume.py` 0.1.0 imported `ssframe.py`, `sscontrol.py`, `dmcratio.py`, `aprime_cross.py`,
`aprime_slsm.py` and `aprime_smooth.py` from the repository, every sha256 matching (`fetch.txt`,
`sha256.txt`). Prior: the 309-toy prefix of `ssframe-v1` (`analysis/results/ssframe/v1-partial/
toys.csv`, sha256 `efe74aae...`). Unit tests pass; py_compile printed nothing.

- **Recheck PASS**: toys 0-7 re-run from their seeds, 0 mismatches against the saved values.
- `near_ties` 0: the 5-decimal rounding of the prior file changes no count.
- Toys 309-933 run strictly in order; the job stopped at its 16,000 s budget with a contiguous merged
  prefix of **934** toys, fewer than 1,000 (the CPU time per toy, about 25 s, was higher than the
  0.32 estimate of about 1,150 merged toys assumed).
- **P0 PASS** again (control slope b_ctrl 0.0345 +- 0.0222, closures 3.1340 / 2.2953 / 2.2953, the
  same observed numbers as `ssframe-v1`: constrained Z0 = 2.134, mu_hat 0.618, b_hat 0.0177).
- **P1-P4 NOT GRADABLE** (934 < 1,000).

Raw output: `analysis/results/ssframe/toyres-v1-partial/` (`toyresume.json`, `toys.csv`, `run.txt`,
`tests.txt`, `sha256.txt`, `fetch.txt`, `compile.txt`, `job.json`).

## 2. Disclosure of what we have now seen (not grades)

Counted by us from the saved `toys.csv` with a text search, before writing this amendment:

- **20 of 934** toys reach the observed constrained Z0 = 2.134 (p = 0.021, about 2.03 sigma; +-1
  sigma Poisson on the count gives about 1.94-2.13 sigma). In the 309-toy prefix it was 4 of 309.
- **25 of 934** toys reach Z0 >= 2.0 (2.7 %).

These numbers are information only. They decide nothing below.

## 3. The further resume (amendment 0.32 sec. 3, applied as written)

0.32 fixed: "If a resume job leaves fewer than 1,000, one further resume of the same kind is filed
from its merged file, unchanged. No calibration is extended or stopped because of the values it
shows." So:

- Job **`toyres-ssframe-v2`**: the same `stats/toyresume.py` 0.1.0 and the same imported modules
  and readings, each fetched from this repository and required to match the sha256 that
  `toyres-ssframe-v1` printed (fatal otherwise; helper `jobs/toyres2/fetch_mods2.py`, new file, no
  existing file changed). Prior: the 934-toy merged prefix committed with this amendment. Same
  arguments (`--ntoys 6000 --workers 4 --budget-s 16000`), 4 CPUs, 1 GB.
- Expected merged prefix: about 1,500-1,600 toys. The calibration is graded on that merged prefix
  under amendment 0.30's P1-P4, whatever its numbers say.
- This is the **last** resume of this kind. If `toyres-ssframe-v2` also leaves fewer than 1,000 toys
  (for example because it gets fewer CPUs), P1-P4 stay NOT GRADABLE for good and the significance
  article reports the constrained frame only as "not calibrated" with the disclosure above.
- If its recheck fails (saved toys not reproduced), P1-P4 are NOT GRADABLE for good, as 0.32 says.

## 4. Article status

Unchanged: the significance article (slug `aleph-30-gev-excess-with-its-template-error`) waits for
`toyres-ssframe-v2` and `leescan-v1`. The constrained-frame number stays conditional on the
undecided same-sign drift (0.36).

## 5. Limits

As before: a reading by an AI agent of ALEPH's published figures, not ALEPH's events; one log-linear
drift shape; toys drawn from the fitted background; local significance only.
