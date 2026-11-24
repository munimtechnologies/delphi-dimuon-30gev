jobs/dimu-val9293-rl-v1/ -- STAGED, NOT FILED (2026-11-24)

Validation run 2 of plan v0.11 (section 4j: DELPHI 1992 and 1993 short DSTs, 3 data files and
2 KK2f Z->qq simulation files per year), prepared for the docker-free entry delphi-rootless 0.1.1
that job dimu-ntuple-rl-v1 uses (amendment 0.43).

It is committed here BEFORE dimu-ntuple-rl-v1 has returned, so the exact job is fixed in public
before any of its gates (N0-N4) is known. It will be filed only if N0, N1 and N2 of amendment 0.35
pass, together with amendment 0.44, which will record the sha256 values of the analysis files.
Its grades are W1-W5 of plan v0.11 section 4j, unchanged; W3 compares with the 1994 median |z0|
from dimu-ntuple-rl-v1.

What it runs: the committed val9293/run_val9293.sh, unchanged, pinned by commit
0b674847dc411cceac8b9ab67e33eefe806177e0, inside the public DELPHI image through
rootless/delphi_rootless.sh 0.1.1 (FATAL sha256 pins, as in dimu-ntuple-rl-v1). run_val9293.sh
fetches the analysis code itself and refuses to run unless it is run_ntuple 0.3.0, dimusel 0.3.0
and btagcal 0.2.0 (frozen under the plan's version guard). It prints their sha256 itself.

Blinding is unchanged: no dimuon mass above 5 GeV in hadronic data events is stored, printed or
histogrammed, and dimusel spectra are blinded in 26-35 GeV. Data ntuples are never committed.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents; not yet checked by a physicist.
Code Apache-2.0; text CC BY 4.0.
