#!/bin/bash
# Inner script for dimu-val9293-rl-v1: runs INSIDE the DELPHI image via delphi_rootless.sh 0.1.1.
# It runs the committed val9293/run_val9293.sh unchanged (plan v0.11 section 4j: 3 data files and
# 2 KK2f files per year, 1992 = Y13723 / v92e, 1993 = Y12340 / v93d, PERIOD y92 / y93).
# Blind-safe: no dimuon mass above 5 GeV in hadronic data events is shown anywhere; dimusel
# spectra are blinded in 26-35 GeV.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
export PYTHONDONTWRITEBYTECODE=1
sed 's/\r$//' /work/run_val9293.sh > /tmp/run_val9293.sh && bash /tmp/run_val9293.sh
rc=$?
echo "VAL9293_RL: run_val9293 rc=$rc"
for y in y92 y93; do
  grep -E '^(data|mc) ' /out/$y/ntuple/runs.txt 2>/dev/null | sed "s/^/VAL9293_RL_RUN: $y /"
done
exit $rc
