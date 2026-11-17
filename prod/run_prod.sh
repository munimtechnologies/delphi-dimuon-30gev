#!/bin/bash
# run_prod.sh -- one full-data production slice (plan section 4h) for the open DELPHI test of
# the ALEPH 30 GeV dimuon excess. MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents.
# Apache-2.0.
#
# Same fetch-and-run pattern as val9293/run_val9293.sh, with two differences for production:
#   REF   the git ref to fetch: a commit SHA pins the exact code of a production pass
#         (default "main"; the SHA-256 of every fetched file is written to $OUT/code_sha256.txt
#         either way)
#   NEED  '|'-separated version strings that must all appear in the fetched files
#         (default: the plan v0.8 code, dimusel 0.3.0, btagcal 0.2.0, run_ntuple 0.3.0)
# Every other switch (DATA_DIRS, DATA_STRIDE, DATA_START, NDATA, MC_VERSION, MC_STRIDE,
# MC_START, NMC, SLICE, PERIOD, KEEP_GZ, OUT) is passed unchanged to ntuple/run_ntuple.sh.
# Blinding is unchanged: the Fortran writes no masses, validate.py never shows a data dimuon
# mass above 5 GeV in hadronic events, and dimusel writes spectra blinded in 26-35 GeV.
#
# Examples (one job each; see prod/templates/):
#   1994 slice 3: OUT=/out DATA_DIRS="Y13709 Y13710" DATA_STRIDE=1 DATA_START=109 NDATA=54 \
#                 NMC=0 PERIOD=y94 SLICE=y94s03 bash run_prod.sh
#   1994 MC 1:    OUT=/out NDATA=0 MC_VERSION=v94c MC_STRIDE=1 MC_START=1 NMC=40 \
#                 PERIOD=y94 SLICE=y94mc01 bash run_prod.sh
set -u
REF=${REF:-main}
NEED=${NEED:-mv2 dimusel 0.3.0|mv2 btagcal 0.2.0|mv2dimu-ntuple 0.3.0}
OUT=${OUT:-/out}
RAW=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/$REF
W=/tmp/w
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$OUT"

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

have_all(){
  local IFS='|' s
  for s in $NEED; do
    grep -qF "$s" $W/*.py $W/*.sh 2>/dev/null || { echo "missing: $s"; return 1; }
  done
  return 0
}

ok=0
for attempt in 1 2 3; do
  rm -rf $W; mkdir -p $W/configs
  for f in $FILES; do
    case $f in
      ntuple/configs/*) get "$f" "$W/configs/$(basename $f)" ;;
      *) get "$f" "$W/$(basename $f)" ;;
    esac
  done
  if have_all; then ok=1; break; fi
  echo "attempt $attempt: fetched code at ref '$REF' lacks a required version; waiting"
  sleep 300
done
if [ $ok != 1 ]; then
  echo "FATAL: required code versions ($NEED) not found at ref '$REF'; nothing was run"
  exit 2
fi
echo "ref=$REF" > "$OUT/code_ref.txt"
sha256sum $W/* $W/configs/* 2>/dev/null | tee "$OUT/code_sha256.txt"

# point the runner at the fetched copies instead of /work
sed 's/\r$//; s#/work/#/tmp/w/#g; s#cd /work #cd /tmp/w #g' $W/run_ntuple.sh > /tmp/run_ntuple.sh
grep -n '/work' /tmp/run_ntuple.sh && echo "WARNING: /work paths left in the script"

T0=$(date +%s)
OUT="$OUT" bash /tmp/run_ntuple.sh
rc=$?
T1=$(date +%s)
echo "run_ntuple exit $rc after $((T1 - T0)) s"
echo "{\"slice\": \"${SLICE:-}\", \"period\": \"${PERIOD:-}\", \"ref\": \"$REF\", \"exit\": $rc, \"seconds\": $((T1 - T0))}" \
  > "$OUT/prod_status.json"
ls -la "$OUT/ntuple" 2>/dev/null | head -50
for f in "$OUT"/ntuple/btagcal_*.json "$OUT"/ntuple/spectra_*.json; do
  [ -f "$f" ] && { echo "== $(basename $f)"; head -c 1500 "$f"; echo; }
done
exit $rc
