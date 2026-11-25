# PLAN amendment v0.44: dimu-ntuple-rl-v1 graded (N0 PASS, N1 FAIL at link time); entry fix xrdfix 0.1.0 filed as dimu-ntuple-rl-v2

MV2 of Munim, Inc. (mv2@munimtech.com), 2026-11-25. Made with AI agents working in MV2's name; **not yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written **after** job `dimu-ntuple-rl-v1` finished and **before** `dimu-ntuple-rl-v2` runs. No test, threshold, prior or blinding rule of plan v0.11 or amendments 0.12-0.43 is changed. No dimuon mass from DELPHI data has been computed or looked at: the job stopped before any event was read.

## 1. Grades of `dimu-ntuple-rl-v1` (gates of amendment 0.35)

Job ran on the Dell on 2026-11-25, 06:58-07:19 UTC (1,282 s), image `gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd:latest` (manifest `sha256:fafdb8b45892b350aa1756b697527180b7bc1465df53c3e1a707cb90dcf2c3bc`, rootfs reused from the data volume, 9.5 GB, AlmaLinux 9.8). Input hashes are in `analysis/results/ntuple-rl/v1/sha256.txt`; the three entry files matched their FATAL pins, and the four analysis files came from commit `5daccc46...` (`run_ntuple.sh` b86eaecb..., `mv2user02.car` 24758ca8..., `validate.py` 485fffc7..., `test_validate.py` 7e704257...).

| id | statement (amendment 0.35) | prior | grade | evidence |
|---|---|---|---|---|
| N0 | the image is unpacked and a shell runs inside it | 60 % | **PASS** | `ROOTLESS: R0=PASS R1=PASS method=proot_static statx=PASS env=PASS id=1000:1000 xrdfs=PASS` |
| N1 | the SKELANA job with MV2's USER02 builds (`dump.exe` exists; no `FATAL: build failed`) | 35 % | **FAIL** | `/usr/bin/ld: cannot find -lXrdPosix`, then `FATAL: build failed (rc=127)`, `run_ntuple rc=5` |
| N2 | >= 4 of 6 data files and >= 2 of 4 simulation files read with events > 0 | 30 % | NOT REACHED | build failed on the first file |
| N3 | Z -> mu mu in data: >= 20 pairs, median 88-94 GeV | 20 % | NOT REACHED | |
| N4 | same in simulation | 20 % | NOT REACHED | |

Everything up to the link worked, for the first time on this route: the DELPHI profile set the full environment, all tools were on the PATH (`nypatchy`, `dellib`, `cernlib`, `xrdcp`, `xrdfs`, `gfortran`, `python3`), MV2's USER02 deck was swapped into the official `/delphi/examples/dump` cradle, the 240-file data list and the `kk2f4146` simulation list were built, `xrdcp` copied the first data file `Y13709.1.al` (96,230,400 bytes in 23 s), and `nypatchy` wrote `dump.f` (1,912 lines). The link then stopped.

## 2. Why the link failed

The image is the XRootD build of the DELPHI software (`CERNLIB_XROOTD=ON`, release `almalinux-9-x86_64_xrd`). Its CERNLIB link asks for `-lXrdPosix`, and the linker found no `libXrdPosix.so` in its search path. On Enterprise Linux 9 the unversioned `libXrdPosix.so` is a development link (normally from an `xrootd-*-devel` package), while the run-time library is `libXrdPosix.so.N`. The most likely reading is that the image carries the run-time library (its `xrdcp`/`xrdfs` work) but not the development link where `ld` looks. The v1 job did not list the library directory, so this is not yet proven; v2 prints it first.

## 3. The fix (entry environment only, as 0.35 prescribes for an N1 failure)

`dimu-ntuple-rl-v2` is v1 with one addition: the inner script first sources `xrdfix.sh` 0.1.0 (in `jobs/dimu-ntuple-rl-v2/`). It

- **A.** writes a diagnosis to `/out/xrdfix.txt` (every `libXrd*` in the default library directories, every `libXrdPosix*` in the image, the xrootd RPMs, the `Xrd` lines of the `cernlib` script, `ld`'s search directories), and the job lists the same libraries from outside the image before entry (`/out/outer_xrd.txt`);
- **B.** for `XrdPosix`, `XrdCl`, `XrdUtils` and any other `-lXrd*` named by the `cernlib` script, copies the resolved library (the unversioned link if it resolves, otherwise the newest `lib<name>.so.N` in a default directory, otherwise one found elsewhere in the image) to `/tmp/mv2xrd/lib<name>.so` and puts `/tmp/mv2xrd` first in `LIBRARY_PATH`, which `gcc`/`gfortran` pass to `ld` as `-L`. The executable still records the library's own soname, so at run time the image's library is used;
- **C.** only if `libXrdPosix` is absent from the image altogether, downloads the xrootd client RPMs as a normal user (`dnf download`) into `/tmp`, unpacks them without installing, and adds their `lib64` to `LIBRARY_PATH` and `LD_LIBRARY_PATH`.

Nothing in the image, the DELPHI release, `run_ntuple.sh`, the USER02 deck, `validate.py` or the gates changes. The fetch script is the same, except that the four analysis files are now pinned FATAL by the sha256 values v1 printed. Same data volume (`delphi-al9-rootfs`), same 2 CPUs / 2 GB / 360 min.

## 4. Expectations, written before v2 runs

- XRDFIX prints `result=READY` via route B (a versioned `libXrdPosix.so.N` exists): 70 %. Route C needed: 15 %. Neither works: 15 %.
- Given READY, N1 PASS: 75 %. Other missing link libraries or Fortran/link errors are the main risk; those would be fixed the same way (environment only) in v3 with amendment 0.45.
- Gates N2-N4 keep their 0.35 definitions and priors. If N0-N1 pass, the staged `delsim-signal-rl-v1` is filed unchanged; if N0-N2 pass, also the staged `dimu-val9293-rl-v1`. N3 and N4 must PASS before any DELPHI data enter a physics test.
- If v2 shows the same error with `result=READY`, the cause is not a missing file. The diagnosis then goes into amendment 0.45 before anything else is filed.

## 5. Why this is worth the effort (unchanged)

ALEPH archived data show a dimuon excess near 30 GeV in Z -> b bbar events (Heister, arXiv:1610.06536); MV2's published ALEPH re-analysis puts its global significance at about 2 sigma. DELPHI recorded the same collisions. A first DELPHI look, with the selection fixed in advance, would be the first independent test from a second LEP experiment. This build is the last technical step before that look.
