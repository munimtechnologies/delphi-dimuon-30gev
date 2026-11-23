# PLAN amendment v0.43: rootless probe v2 graded (V2, V3 PASS; inner probe stopped early); first DELPHI data job filed through delphi-rootless 0.1.1

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-23. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written **after** job `delphi-rootless-probe-v2` finished and **before**
`dimu-ntuple-rl-v1` has run. No test, threshold, prior or blinding rule of plan v0.11 or amendments
0.12-0.42 is changed. No dimuon mass from DELPHI data has been computed or looked at.

## 1. Grades of `delphi-rootless-probe-v2` (amendment 0.42, section 4)

Job ran on the Blade on 2026-11-23, 11:14-11:28 UTC (820 s, peak memory 0.2 GB). Steps 1-3 exit 0
(syntax, FATAL-pinned fetch from commit dd74c8cc, ocipull unit tests); step 4 exit 1. Inputs by
sha256: `ocipull.py` bb3230f0..., `test_ocipull.py` 17406677..., `delphi_rootless.sh` 0.1.1
b57b83c5fc514ea4904f806df332ff60d8af6d1c46f0f9d006971a9c75d40ab2, `delphi_env.sh` 0.1.1
fe14fd968d99dd95e1fec20ffed658b8f30dab632cb367916e47c953748b4689, `probe/probe.sh` f5c809ff...
Results: `analysis/results/rootless/probe-v2/`.

| id | statement | prior | grade | evidence |
|---|---|---|---|---|
| V1 | R0-R3 PASS again | 85 % | **NOT GRADABLE** (R0, R1, R2 PASS; R3 not reached) | `OCIPULL: ok=True layers=22 ... errors: 0`; bash runs inside; `xrdfs inside: PASS`; the inner probe stopped before its `xrdcp` step |
| V2 | a way in has `STATX_OK` | 75 % | **PASS** | system proot 5.1.0 (apt) runs bash but `statx=no`, with and without seccomp; the proot-me v5.5.0 release binary (sha256 db185300... equal to the release SHA256SUMS) gives `statx=yes` |
| V3 | `DELPHIENV: env=PASS` | 55 % | **PASS** | as the image's `delphi` user (1000:1000), the image's own login profile (`DELPHI_ENV_SOURCE=login`) puts `dellib`, `cernlib` and `nypatchy` on PATH and sets the full DELPHI/CERN environment; the `delphi_env.sh` fall-back was not needed |
| V4 | `dump.sh exit 0` with events from `Y13709.1.al` | 35 % | **NOT GRADABLE** (not reached) | `inner rc=1 in 1 s`; no `xrdcp exit` or `dump.sh exit` line |

Following rule 8 of the plan, a step that never ran is NOT GRADABLE, never PASS or FAIL. V4 did
not pass, so the branch "V4 PASS" of amendment 0.42 does not apply.

## 2. Why the inner probe stopped after 1 second

`probe.sh` 0.1.0 starts with `set -u` and then sources `/etc/profile`, `~/.bash_profile` and
`~/.bashrc` with their errors sent to `/dev/null`. Its log ends exactly after the `ls -la $HOME`
listing that comes just before that loop, and the inner shell exits with code 1 one second after it
starts. The DELPHI profile tests variables that are unset in a fresh shell: the trace of
`/etc/profile.d/delphi.sh` in `rootless/delphi_profile.txt` shows several `[ '' = '' ]` tests right
after `/delphi/unset.sh` clears the DELPHI variables. Under `set -u`, bash ends a non-interactive
shell with status 1 the moment such a variable is expanded, and the message was thrown away by the
`2>/dev/null`. This is our reading of the logs. The error text itself was not captured.

In probe v1 the same loop did no harm. There the proot without `statx` support kept the profile
scripts from taking effect (amendment 0.42, section 2, item 2), so the DELPHI profile never ran.
Version 0.1.1's working `statx` is exactly what let the profile run, and the probe's own `set -u`
then stopped the shell. So the fault is in the probe script, not in the way in. The entry
(`delphi_rootless.sh` 0.1.1) worked as designed: method, ids, binds, environment and xrootd all
passed.

## 3. What is filed instead of a probe v3 (a deviation, stated openly)

For "V3 PASS, V4 FAIL", amendment 0.42 asked for a probe v3 after fixing the entry. The entry needs
no fix. The only defect is the probe's `set -u`, and the analysis script already guards against
it: `ntuple/run_ntuple.sh` 0.3.0 (commit 5daccc46..., unchanged since amendment 0.35) sources the
same profile files between `set +u   # profile scripts may reference unset variables` and `set -u`.
A probe v3 would also test less than the analysis job itself, because `dimu-ntuple-rl-v1` builds the
same stock dump example (with MV2's USER02) as its own first step. So we file **`dimu-ntuple-rl-v1`
directly**. Its gate **N1** (the SKELANA job builds: `dump.exe` exists and there is no `FATAL: build
failed`) takes the place of R4/V4. Gates N0-N4, their priors and every outcome rule of amendment 0.35
are unchanged. The amendment-0.35 rule "probe and this job disagree on entry -> publish both logs and
explain before anything else is filed" still applies.

What differs from the job committed with amendment 0.35 (`jobs/dimu-ntuple-rl-v1/`):

1. **Entry 0.1.1.** `fetch.sh` 0.1.1 takes `delphi_rootless.sh` and the new `delphi_env.sh` from
   commit 9f575600c13bd0fc30e532c1bbd1736012d87996, with FATAL sha256 pins equal to the hashes printed
   by probe v2 (above). `ocipull.py` keeps its pin bb3230f0...
2. **Analysis files pinned by commit only.** `run_ntuple.sh`, `mv2user02.car`, `validate.py` and
   `test_validate.py` come from the same commit 5daccc46608c7a47c577bdbaa974745778e7f2e9 as before. No
   earlier job printed their sha256, so they are pinned by the 40-character commit alone (raw GitHub
   content at a commit sha cannot change). The job prints their sha256 to `out/sha256.txt`, and the
   results will record them. `fetch.sh` also fails the job if `run_ntuple.sh` lacks its `set +u`
   guard.
3. **Data volume.** `data_key` is `delphi-al9-rootfs`, the probe's volume that already holds the
   unpacked 9.5 GB image, instead of `delphi-al9-rootfs-nt`. This is infrastructure only and saves
   a second copy on the Blade's disk.
4. **More printed output.** The last run step also prints the validation JSON and `runs.txt` (both
   blind-safe by construction: amendment 0.35), so a truncated log cannot hide a grade.

The new files are in `jobs/dimu-ntuple-rl-v1/rootless-0.1.1/`. `inner_ntuple.sh` is byte-for-byte
the committed one.

## 4. Expectations, written before the job runs

Priors of amendment 0.35 stand: N0 60 %, N1 35 %, N2 30 %, N3 20 %, N4 20 %. Updated private
expectation after probe v2 (reported, not graded): N0 90 %, N1 55 %, N2 45 %. The rise comes from
V2 and V3 passing. If N1 fails, the build log decides the next step. We fix only the entry
environment or the call into the stock example, never the analysis code, and file it as
`dimu-ntuple-rl-v2`.

## 5. Why this is worth the effort (unchanged)

As far as we can find, no DELPHI or OPAL test of the ALEPH 30 GeV dimuon excess (Heister,
arXiv:1610.06536) has been published. Our ALEPH-side calibration puts the excess at about 3.1 sigma
local and 2.1 sigma global (amendment 0.41; article
https://www.munimtech.com/research/aleph-30-gev-excess-is-about-two-sigma-global). Only a second
detector's events can settle it. Every result will be published, whether positive, negative or
inconclusive.
