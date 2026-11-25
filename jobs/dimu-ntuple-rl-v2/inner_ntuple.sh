#!/bin/bash
# Inner script for dimu-ntuple-rl-v2 (PLAN amendment 0.44): runs INSIDE the DELPHI image via
# delphi_rootless.sh 0.1.1. Identical to the v1 inner script (amendment 0.35) except for one
# line: it first sources /work/xrdfix.sh, the entry-environment fix for v1's N1 link failure
# ("cannot find -lXrdPosix"). run_ntuple.sh 0.3.0 runs with no switches set, so it behaves as
# 0.1.0: validation slice, every 40th file of Y13709, 6 data files, 4 Z->qq simulation files.
# Blind-safe: no dimuon mass above 5 GeV in hadronic data events is shown anywhere.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
export PYTHONDONTWRITEBYTECODE=1
export OUT=/out
source /work/xrdfix.sh
sed 's/\r$//' /work/run_ntuple.sh > /tmp/run_ntuple.sh && bash /tmp/run_ntuple.sh
rc=$?
echo "NTUPLE_RL: run_ntuple rc=$rc"
grep -E '^(data|mc) ' /out/ntuple/runs.txt 2>/dev/null | sed 's/^/NTUPLE_RL_RUN: /'
exit $rc
