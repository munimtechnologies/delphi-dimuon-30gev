#!/bin/bash
# run_4f.sh -- the four-fermion background of the ISOLATED selection (NOTE-fourfermion.md), for the
# open DELPHI test of the ALEPH 30 GeV dimuon excess.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
# SIMULATION ONLY: no real-data file is read, so nothing here touches the blinded window.
#   EXCALIBUR e+e- -> mu+ mu- q qbar at the Z pole, sigma = 3.56 +- 0.02 pb (CERN Open Data):
#     81032 1992 gas, 81072 1992 liquid, 81146 1993, 81459 1994, 81539 1995 (one file each)
#   plus 4 KK2f Z -> q qbar files of 1994 (v94c) for the isolated background from ordinary
#   hadronic Z decays.
# Fetches the published ntuple code of github.com/munimtechnologies/delphi-dimuon-30gev (same
# versions as the queued validation jobs), runs ntuple/run_ntuple.sh once with the EXCALIBUR files
# appended to its simulation list, then iso4f.py (copied from /work) on the ntuples.
set -u
RAW=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main
W=/tmp/w
export PYTHONDONTWRITEBYTECODE=1
PY(){ env -u LD_LIBRARY_PATH -u PYTHONPATH -u PYTHONHOME -u PYTHIA8DATA python3 "$@"; }

get(){  # $1 repo path, $2 destination
  local i
  for i in 1 2 3; do
    if command -v curl >/dev/null; then
      curl -fsSL "$RAW/$1?t=$(date +%s)" -o "$2" && return 0
    else
      PY -c "import sys,urllib.request; open(sys.argv[2],'wb').write(urllib.request.urlopen(sys.argv[1]).read())" \
        "$RAW/$1?t=$(date +%s)" "$2" && return 0
    fi
    sleep 30
  done
  echo "could not fetch $1"; return 1
}

FILES="ntuple/run_ntuple.sh ntuple/mv2user02.car ntuple/validate.py ntuple/test_validate.py
analysis/dimusel.py analysis/test_dimusel.py analysis/btagcal.py analysis/test_btagcal.py"

ok=0
for attempt in 1 2 3; do
  rm -rf $W; mkdir -p $W
  for f in $FILES; do get "$f" "$W/$(basename $f)"; done
  if grep -q 'mv2 dimusel 0.3.0' $W/dimusel.py 2>/dev/null && \
     grep -q 'mv2 btagcal 0.2.0' $W/btagcal.py 2>/dev/null && \
     grep -q 'mv2dimu-ntuple 0.3.0' $W/run_ntuple.sh 2>/dev/null; then
    ok=1; break
  fi
  echo "attempt $attempt: published code is not dimusel 0.3.0 / btagcal 0.2.0 / run_ntuple 0.3.0; waiting"
  sleep 120
done
if [ $ok != 1 ]; then echo "FATAL: expected code versions not in the repository"; exit 2; fi
sed 's/\r$//' /work/iso4f.py > $W/iso4f.py
sed 's/\r$//' /work/test_iso4f.py > $W/test_iso4f.py
sha256sum $W/* | tee /out/code_sha256.txt

echo "== iso4f unit tests (before any DELPHI file is read)"
(cd $W && PY -m unittest -v test_iso4f) > /out/tests_iso4f.txt 2>&1; rc=$?
cat /out/tests_iso4f.txt
if [ $rc != 0 ]; then echo "FATAL: iso4f tests failed"; exit 3; fi

# point the script at the fetched copies, and append the EXCALIBUR files to its simulation list
cat > /tmp/patch_mc.txt <<'EOF'
if [ -n "${MC_FILES:-}" ]; then
  for f in $MC_FILES; do echo "$f" >> /tmp/mc_list.txt; done
  echo "MC list with MC_FILES appended:"; cat /tmp/mc_list.txt | tee $R/input_files_${SLICE}_all.txt
fi
EOF
sed 's/\r$//; s#/work/#/tmp/w/#g; s#cd /work #cd /tmp/w #g' $W/run_ntuple.sh > /tmp/run_ntuple.sh
sed -i '/^cat \/tmp\/data_list.txt \/tmp\/mc_list.txt/r /tmp/patch_mc.txt' /tmp/run_ntuple.sh
grep -c 'MC_FILES' /tmp/run_ntuple.sh | sed 's/^/MC_FILES lines in patched script: /'
grep -n '/work' /tmp/run_ntuple.sh && echo "WARNING: /work paths left in the script"

E=/eos/opendata/delphi/simulated-data/ral/excal/mmqq
MCF="$E/v92e/091.2/TAP891863.sdst $E/v92e/091.2/TAP891921.sdst $E/v93d/091.2/TAP891784.sdst"
MCF="$MCF $E/v94c/091.2/TAP891627.sdst $E/v95d/091.2/TAP891709.sdst"

echo "===================== ntuples ====================="
OUT=/out/fourf NDATA=0 MC_VERSION=v94c MC_STRIDE=50 MC_START=7 NMC=4 SLICE=fourf \
  MC_FILES="$MCF" bash /tmp/run_ntuple.sh
echo "ntuple exit $?"
cat /out/fourf/ntuple/runs.txt 2>/dev/null

echo "===================== iso4f ====================="
cd $W && PY iso4f.py --dir /out/fourf/ntuple --out /out/iso4f_fourf.json > /out/iso4f_stdout.txt 2>&1
echo "iso4f exit $?"
head -c 20000 /out/iso4f_stdout.txt
