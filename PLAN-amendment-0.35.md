# PLAN amendment v0.35: the DELPHI validation ntuple, run rootless in parallel with the probe (job `dimu-ntuple-rl-v1` pre-registered); pre-run review of leescan 0.1.0

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-21. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written **before** `dimu-ntuple-rl-v1` has run, and while `abtag-v1`,
`toyres-slsm-v1`, `toyres-ssframe-v1` (amendment 0.32), `delphi-rootless-probe-v1` (0.33) and
`leescan-v1` (0.34) are all still queued: none of them has returned anything. No test, threshold,
prior or blinding rule of plan v0.11 or amendments 0.12-0.34 is changed. The grades of the five
queued jobs will be written in amendments 0.36 and later (one per run), not here.

## 1. Why change the order

Amendment 0.33 sec. 3 said: if the rootless probe passes R1-R4, re-file the five DELPHI jobs through
`delphi_rootless.sh`, ntuple validation first. Jobs now wait many hours in the queue, so doing this
strictly in series costs at least one full queue cycle before the first DELPHI events are seen.
The validation ntuple is **blind-safe by construction** (the Fortran writes no masses;
`validate.py` never stores, prints or histograms a data dimuon mass at or above 5 GeV in events with
5 or more charged tracks). Running it early therefore cannot unblind anything. It also tests more
than the probe does: it builds MV2's own USER02 into the DELPHI SKELANA job, not just the stock
example. So `dimu-ntuple-rl-v1` is filed now, **in parallel** with the probe. This is only a change of
order. The other three DELPHI jobs (`delsim-signal`, `dimu-val9293`, `dimu-fourf`) still wait for a
passing validation, as 0.33 said. `delphi-probe-v1` is superseded by the rootless probe plus this job
and will not be re-filed.

## 2. What the job runs (nothing new in the analysis)

- **Files:** `dntrl/fetch.sh` copies `rootless/ocipull.py`, `rootless/delphi_rootless.sh`,
  `ntuple/run_ntuple.sh` (0.3.0), `ntuple/mv2user02.car`, `ntuple/validate.py` and
  `ntuple/test_validate.py` from **one pinned commit** of this repository
  (`5daccc46608c7a47c577bdbaa974745778e7f2e9`, the amendment-0.34 commit) and writes their sha256 to
  `/out/sha256.txt`. No file is retyped or modified.
- **Inner script:** `dntrl/inner_ntuple.sh` is the run step of the queued docker job
  `dimu-ntuple-v1`, unchanged: `run_ntuple.sh` with **no switches**. In 0.3.0 that is
  exactly the 0.1.0 validation slice: every 40th file of run directory Y13709 (1994), 6 data files,
  4 KK2f Z -> q qbar simulation files.
- **Entry:** `delphi_rootless.sh` 0.1.0 (amendment 0.33), unchanged, in the `python:3.12` image.
  It uses its **own** dataset volume, `delphi-al9-rootfs-nt`. `ocipull` deletes and rebuilds the
  root file system when its completion stamp is missing, so two jobs that unpack into one volume at
  the same time could break each other. The extra volume (one copy of the image) will be removed once
  the DELPHI jobs settle on one cache.
- **Blinding discipline:** the per-file ntuples (`*.ev.txt.gz`, `*.pa.txt.gz`) hold track momenta.
  Data ntuples are **not** committed to the public repository and no dimuon mass above 5 GeV in
  hadronic data events is computed from them before plan v1.x unblinding. Only the validation JSON,
  run logs and simulation outputs are committed.

## 3. Expectations, written before the run

Lines: `OCIPULL:`, `ROOTLESS:`, `NTUPLE_RL:`, `NTUPLE_RL_RUN:` and the `VALIDATION_JSON` block.

| id | statement | our prior |
|---|---|---|
| N0 | the image is unpacked and a shell runs inside it (`ROOTLESS: R0=PASS R1=PASS`) | 60 % |
| N1 | the SKELANA job with MV2's USER02 builds (`dump.exe` exists; no `FATAL: build failed`) | 35 % |
| N2 | at least 4 of the 6 data files and 2 of the 4 simulation files are read with `events` > 0 | 30 % |
| N3 | Z -> mu mu in data (<= 4 charged tracks, two opposite-sign muons with p > 15 GeV): at least 20 pairs, with median mass between 88 and 94 GeV | 20 % |
| N4 | the same Z -> mu mu check passes in simulation (>= 20 pairs, median 88-94 GeV) | 20 % |

The J/psi peak, tag rates, b-tag and impact-parameter distributions are reported, not graded (6
files hold too few J/psi to test).

**Fixed consequences:**

- **N0-N2 PASS:** the DELPHI chain works without docker. The next run files `dimu-val9293-rl-v1`,
  then `delsim-signal-rl-v1` and `dimu-fourf-rl-v1`, the same way (pinned commit, unchanged scripts,
  `-rl` suffix). N3 and N4 must also PASS before any DELPHI data enter a physics test. If they fail,
  the muon selection is studied on Z -> mu mu first, and the plan's blinding is not touched.
- **N0 PASS, N1 FAIL:** read the build log and fix only the entry environment (env, binds, HOME),
  never the analysis code, as in 0.33. The fix is filed as `dimu-ntuple-rl-v2`.
- **N0 FAIL:** as 0.33 R0/R1 FAIL: the exact error goes to needs_sheehan.
- If the probe and this job disagree on entry (one gets in, the other does not), both logs are
  published and the difference is explained before anything else is filed.

## 4. Pre-run review of `stats/leescan.py` 0.1.0 (job `leescan-v1`, amendment 0.34)

Done before the job ran, against the code that will run (`stats/aprime_smooth.py` at sha256
`eae6510a...`):

- `Scanner` swaps the signal shape by assigning `ParFit.s`. This is safe: `ParFit.nll_grad` reads
  `self.s` directly, and `ParFit.__init__` derives nothing else from it.
- The parameter vector (log-polynomial coefficients, ln r, mu) and the bounds ((-10, 10) on ln r,
  (0, MU_MAX = 20) on mu) are the same as `ParFit.fit`. The three starts (0, 0.8, 2.0) begin from the
  mu = 0 fit, as `ParFit.fit` does. Taking the best of the mu = 0 value and the three fits matches
  `ParFit.fit`'s fallback to the mu = 0 fit.
- The toy truth (`m ~ Poisson(T)`, `n ~ Poisson(r T)` from the par3 mu = 0 fit) is the same model
  as the fit's likelihood.
- Upcrossings are counted along the grid only (none at the left edge). This is the usual
  Gross-Vitells convention. The direct global p (the headline) does not depend on it.

No defect found; nothing is changed.
