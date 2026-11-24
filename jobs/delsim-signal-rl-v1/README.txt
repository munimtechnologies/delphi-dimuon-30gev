jobs/delsim-signal-rl-v1/ -- STAGED, NOT FILED (2026-11-24)

The signal simulation of plan v0.11 section 4e (DELPHI detector simulation DELSIM, 1994 detector
v94c, of a 30.4 GeV dimuon signal radiated off the b line in Z -> b bbar), prepared for the
docker-free entry delphi-rootless 0.1.1 that job dimu-ntuple-rl-v1 uses (amendment 0.43). It
measures DELPHI's dimuon mass resolution near 30 GeV and the signal efficiency of the analysis's
own selection. Simulation only: no real-data dimuon mass is read, so blinding does not apply.

It is committed here BEFORE it is filed and before any DELSIM output exists. It will be filed once
dimu-ntuple-rl-v1 shows that the docker-free entry works end to end (gates N0 and N1 of amendment
0.35 PASS); it does not need the data gate N2. Its grades are D1-D8 of plan v0.11 section 4e,
unchanged (D1 route to the condition database; D2 >= 80 % of reconstructed events matched and
median mass within 0.3 GeV; D3 mass resolution 0.25-0.75 GeV; D4 muon-tag efficiency 0.70-0.95;
D5 selection fraction 0.35-0.70; D6 1/p resolution 0.0005-0.0015 GeV^-1 at 15-20 GeV; D7 rho_D
0.60-1.05; D8a-d as in the plan). A step not reached is NOT GRADABLE, never a fail.

What it runs: the committed delsim/run_delsim.sh 0.1.0, pinned by commit
87504c33cd461286f251697e6b0ffac2ac98d99f, inside the public DELPHI image through
rootless/delphi_rootless.sh 0.1.1 (FATAL sha256 pins, as in dimu-ntuple-rl-v1). The entry probe
(delphi-rootless-probe-v2) showed that the image's login profile sets DELSIM_ROOT and
DELPHI_DDB=/eos/opendata/delphi/condition-data; run_delsim.sh tries that default route first.

Two preparations, both printed by the job (inner_delsim.sh):
 1. run_delsim.sh fetches the xkin/ generator code from the branch 'main' at run time; its REPO
    line is pinned to the staging commit instead, so that code cannot change after staging.
 2. A defect found while staging: the docker-era job never placed analysis/dimusel.py or
    analysis/btagcal.py next to sigana.py. sigana 0.3.0 imports dimusel inside a try block and
    returns None when it is missing, so dimusel_exact (needed by gates D5 and D8) would have been
    empty, and 7 of the 21 tests in test_sigana (the dimusel and btagcal cross-checks) would have
    been silently skipped instead of run. Both files are now copied
    into /tmp/code before run_delsim.sh runs; run_delsim.sh does not wipe that folder.

Outputs to commit after it runs (to delsim/results/rl-v1/): out/{fetch.txt,compile.txt,sha256.txt}
and out/delsim/{status.txt,sigana.json,gen/gen_stats.json,tests_sigana.txt,tests_xkin.txt,
code_sha256.txt,title_lines.txt,*.log.tail,smoke_*.errors.txt,sig_V_v94c.mv2ev.txt.gz,
sig_V_v94c.mv2pa.txt.gz} + job.json (no sdst file).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents; not yet checked by a physicist.
Code Apache-2.0; text CC BY 4.0.
