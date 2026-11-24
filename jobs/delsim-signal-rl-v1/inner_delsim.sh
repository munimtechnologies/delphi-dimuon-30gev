#!/bin/bash
# Inner script for delsim-signal-rl-v1: runs INSIDE the DELPHI image via delphi_rootless.sh 0.1.1.
# Runs the committed delsim/run_delsim.sh 0.1.0 (plan v0.11 section 4e) with exactly two
# preparations, both printed:
#   1. its REPO line (xkin/ code fetched at run time) is pinned from 'main' to the staging commit,
#      so the generator code cannot change after staging;
#   2. analysis/dimusel.py and analysis/btagcal.py are placed in /tmp/code first, where
#      run_delsim.sh puts sigana.py, so sigana 0.3.0 can compute dimusel_exact (gates D5, D8)
#      and test_sigana runs its 7 dimusel/btagcal cross-checks instead of skipping them.
#      run_delsim.sh does not wipe /tmp/code.
# Simulation only: no real-data dimuon mass is read, so blinding does not apply.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
export PYTHONDONTWRITEBYTECODE=1
C=87504c33cd461286f251697e6b0ffac2ac98d99f
B=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev
mkdir -p /tmp/code
cp /work/dimusel.py /work/btagcal.py /tmp/code/
sed -e 's/\r$//' -e "s#^REPO=$B/main\$#REPO=$B/$C#" /work/run_delsim.sh > /tmp/run_delsim.sh
echo "DELSIM_RL: prepared run_delsim.sh (diff against committed file follows)"
diff /work/run_delsim.sh /tmp/run_delsim.sh
grep -q "^REPO=$B/$C\$" /tmp/run_delsim.sh && echo "DELSIM_RL: repo pin OK $C" || echo "DELSIM_RL: repo pin FAILED"
ls -la /tmp/code
OUT=/out bash /tmp/run_delsim.sh
rc=$?
echo "DELSIM_RL: run_delsim rc=$rc"
sed 's/^/DELSIM_RL_STATUS: /' /out/delsim/status.txt 2>/dev/null
[ -f /out/delsim/sigana.json ] && echo "DELSIM_RL: sigana.json bytes=$(stat -c %s /out/delsim/sigana.json)" \
  || echo "DELSIM_RL: sigana.json MISSING"
exit $rc
