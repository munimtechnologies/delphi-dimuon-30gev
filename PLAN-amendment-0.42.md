# PLAN amendment v0.42: rootless probe v1 graded (R0-R3 PASS, R4 FAIL); entry fixed in delphi-rootless 0.1.1; probe v2 pre-registered

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-23. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written **after** job `delphi-rootless-probe-v1` finished and **before**
`delphi-rootless-probe-v2` has run. No test, threshold, prior or blinding rule of plan v0.11 or
amendments 0.12-0.41 is changed. No dimuon mass from DELPHI data has been computed or looked at:
the probe looks at none (it only builds the stock event-dump example).

## 1. Grades of `delphi-rootless-probe-v1` (amendment 0.33, section 3)

Job ran on 2026-11-22, 19:52-20:32 UTC (2,381 s, peak memory 0.31 GB), all steps exit 0. Inputs
by sha256: `ocipull.py` bb3230f0..., `test_ocipull.py` 17406677..., `delphi_rootless.sh` 0.1.0
d46d5664..., `probe/probe.sh` f5c809ff... Results: `analysis/results/rootless/probe-v1/`.

| id | statement | prior | grade | evidence |
|---|---|---|---|---|
| R0 | image pulled, digests verified, unpacked with 0 layer-entry errors | 70 % | **PASS** | `OCIPULL: ok=True layers=22`, `errors: 0`; 101,571 files, 9.5 GB root file system |
| R1 | a method runs `/bin/bash` inside the image | 60 % | **PASS** | first method, `proot`, printed `INSIDE_OK` (AlmaLinux 9.8) |
| R2 | `xrdfs` inside the image lists `/eos/opendata/delphi` | 50 % | **PASS** | collision-data, simulated-data, ... listed in 2 s |
| R3 | probe.sh copies `Y13709.1.al` with xrdcp (exit 0, > 0 bytes) | 45 % | **PASS** | `xrdcp exit 0 in 12 s`, 96,230,400 bytes (equal to the EOS listing) |
| R4 | the stock dump example builds (`dump.sh exit 0`) and its log shows DELPHI events | 30 % | **FAIL** | `dump.sh exit 127`: `dellib: command not found`, `cernlib: command not found`, no `nypatchy` |

Disclosures. (a) ocipull counted 14 `skipped_bad` layer entries besides `errors: 0`; R0 was written
as "0 layer-entry errors", so it is graded PASS by its wording, and the 14 skipped entries are
reported here. (b) One blob (the 2.36 GB layer 7ab697c8...) failed its digest check on the first
attempt and passed on the retry; that is the check working as designed.

So the pre-registered branch is **"R1 PASS, R4 FAIL: read the build log, fix only the entry
environment (env, binds, HOME), never the analysis, and file delphi-rootless-probe-v2."**

## 2. What the logs show

1. **The job runner's proot does not translate `statx`.** Inside the image, `ls` fails on paths that
   exist only inside the image (`ls: cannot access '/delphi/examples'`, `'/home/delphi'`), while
   `find`, `tar`, `cp` and bash's own `[ -d ]` see them, and `ls -la` in the copied example directory
   prints `-?????????` for every entry. That is the known PRoot limitation with newer coreutils
   (proot-me/proot issue #262; support was added upstream in 2021, PR #272). Any DELPHI script that
   relies on `ls` or `stat` would misbehave under it.
2. **The DELPHI tools were not on PATH.** After `bash -l` and an explicit `source /etc/profile`, no
   DELPHI or CERN variable was set and `dellib`, `cernlib`, `nypatchy` were missing, although
   `/etc/profile.d/delphi.sh` exists in the image. The CERN Open Data guide runs the image as the
   image's own user (`--user delphi ... /bin/bash -l`); probe v1 entered as root. Either the profile
   script depends on the user, or it fails silently because of (1). The logs do not show which.

## 3. The fix: `rootless/delphi_rootless.sh` 0.1.1 and `rootless/delphi_env.sh` 0.1.1

Only the way in changes. The image, the analysis code (`ntuple/`, `analysis/`, `stats/`), the
switches and the blinding are unchanged.

- Every way in is checked twice: bash runs (`INSIDE_OK`) **and** `ls -d /delphi/releases` works
  (`STATX_OK`; that path exists only inside the image). Order: system proot, system proot without
  seccomp acceleration, the proot-me v5.5.0 release binary (accepted only if its sha256 equals the
  release's SHA256SUMS; the hash is printed), the same without seccomp, `unshare -r` + `chroot`. The
  first way with both is used; if none has both, the first that runs bash is used and `statx=FAIL`
  is printed.
- The DELPHI environment is checked under the image's `delphi` user id (`proot -i uid:gid`, read
  from the image's `/etc/passwd`) and then as root; the first id under which `dellib`, `cernlib`
  and `nypatchy` are all found is used for the inner script.
- `delphi_env.sh` is sourced after the login profile. It does nothing when the tools are already
  found; otherwise it sources `/etc/profile.d/delphi.sh`, then the first `setup.sh` under `/delphi`
  that provides the tools. It sets `DELPHI_DATA_ROOT` to `/eos/opendata/delphi` if unset, as the
  CERN guide asks.
- For diagnosis it saves `/etc/profile.d/delphi.sh`, the delphi user's shell start-up files, a
  `bash -x` trace of sourcing the profile and a list of DELPHI setup scripts and tools
  (`rootless/delphi_profile.txt`, `rootless/env_*.txt`).

## 4. Probe v2: expectations written before it runs

`delphi-rootless-probe-v2` runs the same `probe/probe.sh` (sha256 f5c809ff..., fetched from commit
dd74c8ccc29ed0ce7487a9f32f13e3fa594b4913 with a fatal checksum test) through delphi-rootless 0.1.1,
reusing the unpacked image in the dataset volume `delphi-al9-rootfs`. Grades come from the
`ROOTLESS:`, `DELPHIENV:`, `METHOD:`, `xrdcp exit` and `dump.sh exit` lines.

| id | statement | our prior |
|---|---|---|
| V1 | R0-R3 PASS again | 85 % |
| V2 | a way in has `STATX_OK` (`statx=PASS`) | 75 % |
| V3 | `DELPHIENV: env=PASS` (dellib, cernlib and nypatchy found) | 55 % |
| V4 | `dump.sh exit 0` and the dump log contains events from `Y13709.1.al` (R4 of amendment 0.33) | 35 % |

What follows is fixed now:

- **V4 PASS**: R4 counts as PASS. Re-file the five DELPHI jobs as `<name>-rl-v1` through
  delphi-rootless 0.1.1 with their committed scripts unchanged, in the plan's order (ntuple
  validation `dimu-ntuple-rl-v1` first; no unblinded mass before plan v1.x).
- **V3 PASS, V4 FAIL**: read the build log; fix only the entry (env, binds, HOME, ids); probe v3.
- **V3 FAIL**: read `delphi_profile.txt`. If the profile needs something a sandbox cannot give
  (CVMFS, AFS, a mounted EOS), say so openly here and in needs_sheehan, and set the environment by
  hand only from what the image's own profile says, in a probe v3 written down before it runs.
- **V1 FAIL**: report the exact error; nothing else changes.

## 5. Why this is worth the effort (unchanged)

As far as we can find, no DELPHI or OPAL test of the ALEPH 30 GeV dimuon excess (Heister,
arXiv:1610.06536) has been published. Our ALEPH-side calibration puts the excess at about 3.1 sigma
local and 2.1 sigma global (amendment 0.41). Only a second detector's events can settle it. The
forecast in the plan is unchanged: with DELPHI 1994-95 data, about a 70 % chance of excluding an
ALEPH-sized signal that is not there; about 95 % with 1992-95. Every result will be published,
whether positive, negative or inconclusive.
