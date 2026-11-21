# PLAN amendment v0.33: a rootless way into the DELPHI software image, so the DELPHI jobs can finally run; feasibility probe pre-registered

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-21. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written **before** job `delphi-rootless-probe-v1` has run, while
`abtag-v1`, `toyres-slsm-v1` and `toyres-ssframe-v1` (amendment 0.32) are still queued. No test,
threshold, prior or blinding rule of plan v0.11 or amendments 0.12-0.32 is changed.

## 1. Why

The whole point of this repository is the first independent test of the ALEPH 30 GeV dimuon excess
(Heister, arXiv:1610.06536) with a second LEP experiment's data: DELPHI's open data (CC0,
doi:10.7483/OPENDATA.DELPHI.0X8O.FBUH). As far as we can find, no DELPHI or OPAL test of it has
been published. Every ALEPH-side result we have published so far (the LEP1 four-fermion check, the
significance calibrations, the same-sign control) works from ALEPH's published figures. Only DELPHI's
own events can say whether a second detector sees the bump.

The DELPHI data exist only in DELPHI's ZEBRA formats and need DELPHI's Fortran software stack
(CERNLIB, SKELANA/dstana, simana). That stack ships as the public image
`gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd` (AlmaLinux 9, xrootd), per the CERN
Open Data guide "Running the DELPHI software stack using Docker". The five jobs filed on that image
(`delphi-probe-v1`, `dimu-ntuple-v1`, `delsim-signal-v1`, `dimu-val9293-v1`, `dimu-fourf-v1`) have
**never started**, while every `python:3.12` job does. We do not know why (registry access, image
size or a runner allow-list). Waiting has not helped for weeks, so this amendment removes the
dependence on the job runner pulling that image.

## 2. What changes: only how the container is entered

New, separate files under `rootless/` (no existing module is modified, per the version guard):

- `rootless/ocipull.py` 0.1.0: a standard-library puller for public OCI/Docker images. It gets an
  anonymous pull token, picks the linux/amd64 manifest, checks every blob against its sha256
  digest, and applies the layers in order with OCI whiteouts. Every path, symlink and hard link is
  resolved inside the root, so no layer can write outside it. It writes the image's ENV to
  `/.ocipull-env.sh`. Tests: `rootless/test_ocipull.py` (offline: reference and auth parsing,
  platform choice, whiteouts, opaque directories, symlink escapes, hard links, loops).
- `rootless/delphi_rootless.sh` 0.1.0: unpacks the image into a cache directory (kept between jobs
  in the dataset volume `delphi-al9-rootfs`). It then tries, in this fixed order, `proot`,
  `proot` without seccomp acceleration, and `unshare -r` + `chroot`, and runs a given script
  inside with `/out`, `/work` and `/tmp` bound.

The software, the image, the analysis code (`ntuple/`, `analysis/`, `stats/`) and the blinding are
the same as in the docker route. A job that runs `ntuple/run_ntuple.sh` through
`delphi_rootless.sh` is the same pre-registered job (same switches, same outputs) and is graded by
the same rules. Only the job name gets the suffix `-rl`.

## 3. Feasibility probe `delphi-rootless-probe-v1`: expectations written before it runs

It runs the unchanged `probe/probe.sh` (delphi-probe 0.1.0, which looks at **no** dimuon mass)
inside the unpacked image. The grades come from the `OCIPULL:`, `ROOTLESS:`, `xrdcp exit` and
`dump.sh exit` lines.

| id | statement | our prior |
|---|---|---|
| R0 | image pulled, digests verified, unpacked with 0 layer-entry errors | 70 % |
| R1 | at least one method runs `/bin/bash` inside the image (`INSIDE_OK`) | 60 % |
| R2 | `xrdfs` inside the image lists `/eos/opendata/delphi` | 50 % |
| R3 | probe.sh copies `Y13709.1.al` with xrdcp (exit 0, file > 0 bytes) | 45 % |
| R4 | the stock dump example builds (`dump.sh exit 0`) and its log shows DELPHI events | 30 % |

R0-R4 are feasibility gates, not physics. What follows from them is fixed now:

- **R1-R4 PASS**: re-file the five DELPHI jobs as `<name>-rl-v1` through `delphi_rootless.sh`,
  each with its committed script unchanged, in the plan's order (ntuple validation first; no
  unblinded mass before plan v1.x).
- **R1 PASS, R4 FAIL**: read the build log, fix only the entry environment (env, binds, HOME),
  never the analysis, and file `delphi-rootless-probe-v2`.
- **R0 or R1 FAIL**: report the exact error in needs_sheehan (image access or sandbox limits) and
  keep the docker jobs queued.

## 4. Sensitivity, restated (unchanged)

From the repository's own forecast (`forecast.py`): with DELPHI 1994-95 data the main test raises
the chance of excluding an ALEPH-sized signal that is not there from about 40 % to about 70 %, and
to about 95 % with 1992-95 data. If the excess is not real, an INCONCLUSIVE result is still the
most likely single outcome on the smaller sample. Every result will be published: positive,
negative or inconclusive.
