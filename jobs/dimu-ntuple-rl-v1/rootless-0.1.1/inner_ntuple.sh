#!/bin/bash
# Inner script for dimu-ntuple-rl-v1 (PLAN amendment 0.35): runs INSIDE the DELPHI image via
# delphi_rootless.sh. It is the exact run step of the queued docker job dimu-ntuple-v1, with no
# switches set, so run_ntuple.sh 0.3.0 behaves as 0.1.0: validation slice, every 40th file of
# Y13709, 6 data files, 4 Z->qq simulation files. Blind-safe: no dimuon mass above 5 GeV in
# hadronic data events is shown anywhere.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
export PYTHONDONTWRITEBYTECODE=1
export OUT=/out
sed 's/\r$//' /work/run_ntuple.sh > /tmp/run_ntuple.sh && bash /tmp/run_ntuple.sh
rc=$?
echo "NTUPLE_RL: run_ntuple rc=$rc"
grep -E '^(data|mc) ' /out/ntuple/runs.txt 2>/dev/null | sed 's/^/NTUPLE_RL_RUN: /'
exit $rc
