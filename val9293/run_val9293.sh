#!/bin/bash
# run_val9293.sh -- validation run 2 (plan section 4j): MV2's ntuple routine on DELPHI's
# 1992 and 1993 Z-pole short DSTs and the matching KK2f Z -> q qbar simulation, for the open
# DELPHI test of the ALEPH 30 GeV dimuon excess.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
# Fetches the published code of github.com/munimtechnologies/delphi-dimuon-30gev (it refuses to
# run older versions), then runs ntuple/run_ntuple.sh once per year. Same blinding as run 1:
# no data dimuon mass above 5 GeV in hadronic events is stored, printed or histogrammed, and
# the spectra written by dimusel are blinded in 26-35 GeV.
#   1992: short92_e2, record 81098, /eos/opendata/delphi/collision-data/Y13723 (172 files),
#         simulation kk2f4146/v92e/91.25
#   1993: record 81166 (93 data 4th processing, ANA_D Fix 2), collision-data/Y12340 (181 files),
#         simulation kk2f4146/v93d/91.25
set -u
RAW=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main
W=/tmp/w
export PYTHONDONTWRITEBYTECODE=1

get(){  # $1 repo path, $2 destination
  local i
  for i in 1 2 3; do
    if command -v curl >/dev/null; then
      curl -fsSL "$RAW/$1?t=$(date +%s)" -o "$2" && return 0
    else
      env -u LD_LIBRARY_PATH -u PYTHONPATH -u PYTHONHOME python3 -c \
        "import sys,urllib.request; open(sys.argv[2],'wb').write(urllib.request.urlopen(sys.argv[1]).read())" \
        "$RAW/$1?t=$(date +%s)" "$2" && return 0
    fi
    sleep 30
  done
  echo "could not fetch $1"; return 1
}

FILES="ntuple/run_ntuple.sh ntuple/mv2user02.car ntuple/validate.py ntuple/test_validate.py
analysis/dimusel.py analysis/test_dimusel.py analysis/btagcal.py analysis/test_btagcal.py
ntuple/configs/hemi_w1e-2.json ntuple/configs/hemi_w3e-3.json ntuple/configs/hemi_w1e-3.json
ntuple/configs/hemi_w3e-4.json ntuple/configs/hemi_w1e-4.json"

ok=0
for attempt in 1 2 3 4; do
  rm -rf $W; mkdir -p $W/configs
  for f in $FILES; do
    case $f in
      ntuple/configs/*) get "$f" "$W/configs/$(basename $f)" ;;
      *) get "$f" "$W/$(basename $f)" ;;
    esac
  done
  if grep -q 'mv2 dimusel 0.3.0' $W/dimusel.py 2>/dev/null && \
     grep -q 'mv2 btagcal 0.2.0' $W/btagcal.py 2>/dev/null && \
     grep -q 'mv2dimu-ntuple 0.3.0' $W/run_ntuple.sh 2>/dev/null; then
    ok=1; break
  fi
  echo "attempt $attempt: published code is not yet dimusel 0.3.0 / btagcal 0.2.0 / run_ntuple 0.3.0; waiting"
  sleep 300
done
if [ $ok != 1 ]; then
  echo "FATAL: the plan v0.8 code is not in the repository; nothing was run"
  exit 2
fi
ls -la $W $W/configs
sha256sum $W/* $W/configs/* 2>/dev/null | tee /out/code_sha256.txt

# point the script at the fetched copies instead of /work
sed 's/\r$//; s#/work/#/tmp/w/#g; s#cd /work #cd /tmp/w #g' $W/run_ntuple.sh > /tmp/run_ntuple.sh
grep -n '/work' /tmp/run_ntuple.sh && echo "WARNING: /work paths left in the script"

echo "===================== 1992 ====================="
OUT=/out/y92 DATA_DIRS=Y13723 DATA_STRIDE=57 DATA_START=1 NDATA=3 \
  MC_VERSION=v92e MC_STRIDE=100 MC_START=1 NMC=2 SLICE=val92 PERIOD=y92 bash /tmp/run_ntuple.sh
echo "1992 exit $?"

echo "===================== 1993 ====================="
OUT=/out/y93 DATA_DIRS=Y12340 DATA_STRIDE=60 DATA_START=1 NDATA=3 \
  MC_VERSION=v93d MC_STRIDE=200 MC_START=1 NMC=2 SLICE=val93 PERIOD=y93 bash /tmp/run_ntuple.sh
echo "1993 exit $?"

for y in y92 y93; do
  echo "== $y validation summary"; head -c 4000 /out/$y/ntuple/validation_val${y#y}.json 2>/dev/null; echo
  echo "== $y runs"; cat /out/$y/ntuple/runs.txt 2>/dev/null
done
