#!/bin/bash
# mv2dimu-ntuple 0.3.0 -- build a SKELANA job with MV2's USER02 (mv2user02.car) inside the
# DELPHI container and run it on DELPHI short-DST data and Z->qq simulation files, for the
# open DELPHI test of the ALEPH 30 GeV dimuon excess.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
# Reads only public CERN Open Data (CC0) over xrootd. Writes only to $OUT/ntuple and /tmp.
# Blinding: the Fortran writes no masses; validate.py never shows data dimuon masses above
# 5 GeV in hadronic events; dimusel.py (if present) writes blinded spectra only.
#
# 0.2.0: production slices through environment switches. With no switches set it behaves
# exactly like 0.1.0 (every 40th file of Y13709, 6 data files, 4 simulation files).
#   DATA_DIRS   space-separated EOS run directories, in order (default "Y13709";
#               1992 = "Y13723", 1993 = "Y12340", 1994 = "Y13709 Y13710", 1995 = "Y13716")
#   DATA_STRIDE take every n-th file of the concatenated, number-sorted list (default 40)
#   DATA_START  1-based position in that list of the first file (default 1)
#   NDATA       number of data files (default 6; 0 = none)
#   MC_VERSION  KK2f detector version (default: first of v94c v94c2 v94 found;
#               set v92e for 1992, v93d for 1993)
#   MC_STRIDE / MC_START / NMC  the same for simulation files (defaults 20 / 1 / 4)
#   SLICE       label for this job's outputs (default "val")
#   KEEP_GZ     1 keeps the per-file ntuples in $OUT/ntuple (default 1)
# 0.3.0 (plan v0.8):
#   PERIOD      data-taking period label (y92, y93, y94, y95), passed to dimusel and btagcal
#               as --period (default empty: no label, as 0.2.0)
#   configs/    if /work/configs/*.json exist, dimusel also writes one blinded spectrum per
#               config, $R/spectra_$SLICE_<config name>.json (the pre-declared grid of plan 4h)
# If dimusel.py and btagcal.py sit next to this script, the job also writes
# $R/spectra_$SLICE.json (blinded) and $R/btagcal_$SLICE.json (event-level words only).
set -u
HOME=${HOME:-/root}
OUT=${OUT:-/out}
R=$OUT/ntuple
mkdir -p "$R" 2>/dev/null || { R=/tmp/ntuple; mkdir -p $R; }
DATA_DIRS=${DATA_DIRS:-Y13709}
DATA_STRIDE=${DATA_STRIDE:-40}
DATA_START=${DATA_START:-1}
NDATA=${NDATA:-6}
MC_VERSION=${MC_VERSION:-}
MC_STRIDE=${MC_STRIDE:-20}
MC_START=${MC_START:-1}
NMC=${NMC:-4}
SLICE=${SLICE:-val}
KEEP_GZ=${KEEP_GZ:-1}
PERIOD=${PERIOD:-}
PERARG=""
[ -n "$PERIOD" ] && PERARG="--period $PERIOD"
log(){ echo; echo "==== $(date -u +%H:%M:%S) $*"; }
EOS=root://eospublic.cern.ch/
echo "DATA_DIRS='$DATA_DIRS' DATA_STRIDE=$DATA_STRIDE DATA_START=$DATA_START NDATA=$NDATA MC_VERSION='$MC_VERSION' MC_STRIDE=$MC_STRIDE MC_START=$MC_START NMC=$NMC SLICE=$SLICE PERIOD='$PERIOD'"

log "environment"
id
set +u   # profile scripts may reference unset variables
for f in /etc/profile /home/delphi/.bash_profile /home/delphi/.bashrc "$HOME/.bash_profile" "$HOME/.bashrc" \
         /delphi/setup.sh /cvmfs/delphi.cern.ch/setup.sh; do
  [ -r "$f" ] && source "$f" >/dev/null 2>&1 || true
done
if [ -z "${FCOMP:-}" ]; then
  for s in $(find / -xdev -maxdepth 5 -name 'setup.sh' -path '*delphi*' 2>/dev/null | head -5); do
    echo "sourcing $s"; source "$s" >/dev/null 2>&1 || true
    [ -n "${FCOMP:-}" ] && break
  done
fi
set -u
echo "FCOMP=${FCOMP:-} DELPHI_PAM=${DELPHI_PAM:-} PLINAM=${PLINAM:-}"
for c in nypatchy dellib cernlib xrdcp xrdfs gfortran python3; do printf '%-9s ' $c; command -v $c || echo MISSING; done
# python with the DELPHI library and python paths removed (they can break the system python)
PY(){ env -u LD_LIBRARY_PATH -u PYTHONPATH -u PYTHONHOME -u PYTHIA8DATA python3 "$@"; }

log "locate the dump example"
DS=$(find / -xdev -name dump.sh -path '*dump*' 2>/dev/null | head -1)
EX=""
[ -n "$DS" ] && EX=$(dirname "$DS")
if [ -z "$EX" ] || [ ! -f "$EX/dump.cra" ]; then
  echo "no local example; cloning gitlab.cern.ch/delphi/examples"
  timeout 300 git clone --depth 1 https://gitlab.cern.ch/delphi/examples.git /tmp/git_examples >/dev/null 2>&1 && EX=/tmp/git_examples/dump
fi
echo "example dir: $EX"; ls -la "$EX" 2>&1
B=/tmp/build; rm -rf $B; cp -r "$EX" $B || { echo "FATAL no example"; exit 3; }
cd $B
cp dump.cra $R/dump.cra.orig 2>/dev/null
cat dump.cra
[ -f dump.car ] || { [ -n "${DELPHI_PAM:-}" ] && cp "$DELPHI_PAM/skelana.car" dump.car; }
grep -n -i -E '^\+(DECK|PATCH|KEEP)' dump.car 2>/dev/null | head -400 > $R/dump_car_structure.txt
wc -l $R/dump_car_structure.txt
# where SKELANA keeps simulation truth (for a later flavour-tagged MC study): list the KEEPs
[ -n "${DELPHI_PAM:-}" ] && [ -f "$DELPHI_PAM/skelana.car" ] && \
  grep -n -i -E '^\+KEEP *, *PSC(SIM|VEC|MC)|NVECMC|ISIMRE|IRESIM|KSIM|NSIM' "$DELPHI_PAM/skelana.car" | head -80 > $R/skelana_sim_words.txt

log "swap in MV2 USER02"
sed 's/\r$//' /work/mv2user02.car > /tmp/mv2user02.car
TARGET=""
for f in dump.car dump.cra; do
  grep -q -i -E '^\+DECK *, *USER02[ ,.]' $f 2>/dev/null && { TARGET=$f; break; }
done
if [ -z "$TARGET" ]; then
  echo "FATAL: no '+DECK, USER02' in dump.car or dump.cra"; grep -n -i 'USER02' dump.car dump.cra | head -20
  exit 4
fi
echo "USER02 deck found in $TARGET"
grep -n -i -A12 -E '^\+DECK *, *USER02[ ,.]' $TARGET | head -40 > $R/user02_orig_head.txt
awk -v repl=/tmp/mv2user02.car '
  BEGIN { skip = 0 }
  toupper($0) ~ /^\+DECK *, *USER02[ ,.]/ { while ((getline line < repl) > 0) print line; skip = 1; next }
  skip && toupper($0) ~ /^\+(DECK|PATCH|KEEP|QUIT)/ { skip = 0 }
  !skip { print }' $TARGET > $TARGET.new && mv $TARGET.new $TARGET
grep -c 'MV2DIMU' $TARGET

log "data and simulation file lists"
: > /tmp/data_all.txt
for d in $DATA_DIRS; do
  timeout 120 xrdfs $EOS ls /eos/opendata/delphi/collision-data/$d 2>&1 | grep -E '\.al$' | sort -t. -k2,2n >> /tmp/data_all.txt
done
wc -l /tmp/data_all.txt
cp /tmp/data_all.txt $R/data_all_$SLICE.txt
: > /tmp/data_list.txt
if [ "$NDATA" -gt 0 ]; then
  awk -v s=$DATA_START -v k=$DATA_STRIDE 'NR >= s && (NR - s) % k == 0' /tmp/data_all.txt | head -$NDATA > /tmp/data_list.txt
  if [ ! -s /tmp/data_list.txt ] && [ "$DATA_DIRS" = "Y13709" ]; then
    for i in 1 2 3 4 5 6; do echo /eos/opendata/delphi/collision-data/Y13709/Y13709.$i.al; done | head -$NDATA > /tmp/data_list.txt
  fi
fi
: > /tmp/mc_list.txt
if [ "$NMC" -gt 0 ]; then
  timeout 120 xrdfs $EOS ls /eos/opendata/delphi/simulated-data/cern/kk2f4146 2>&1 | tee $R/mc_versions.txt
  MCV="$MC_VERSION"
  if [ -z "$MCV" ]; then
    for v in v94c v94c2 v94; do grep -q "/$v\$" $R/mc_versions.txt && { MCV=$v; break; }; done
    [ -z "$MCV" ] && MCV=$(grep -m1 -E '/v94' $R/mc_versions.txt | xargs -r basename)
  fi
  echo "MC version: ${MCV:-none}"
  if [ -n "$MCV" ]; then
    timeout 120 xrdfs $EOS ls /eos/opendata/delphi/simulated-data/cern/kk2f4146/$MCV 2>&1 | tee $R/mc_energies.txt
    MCE=$(grep -m1 '91.2' $R/mc_energies.txt)
    [ -n "$MCE" ] && timeout 120 xrdfs $EOS ls $MCE 2>&1 | grep -i 'qqpy' | grep -E 'sdst$' | sort > /tmp/mc_all.txt
    [ -f /tmp/mc_all.txt ] && awk -v s=$MC_START -v k=$MC_STRIDE 'NR >= s && (NR - s) % k == 0' /tmp/mc_all.txt | head -$NMC > /tmp/mc_list.txt
  fi
fi
cat /tmp/data_list.txt /tmp/mc_list.txt | tee $R/input_files_$SLICE.txt

run_one(){  # $1 tag, $2 eos path, $3 first(1)/later(0)
  local tag=$1 path=$2 first=$3 name; name=$(basename "$path")
  log "$tag $name"
  local T0=$(date +%s)
  timeout 1800 xrdcp -f -s "$EOS/$path" /tmp/in.dat; local rc=$?
  local tcp=$(( $(date +%s) - T0 ))
  echo "xrdcp rc=$rc in $tcp s, $(stat -c %s /tmp/in.dat 2>/dev/null) bytes"
  [ $rc -ne 0 ] && { echo "$tag $name xrdcp_failed" >> $R/runs.txt; return; }
  echo "FILE = /tmp/in.dat" > PDLINPUT
  rm -f mv2ev.txt mv2pa.txt
  T0=$(date +%s)
  if [ "$first" = 1 ]; then
    chmod +x dump.sh
    timeout 3600 ./dump.sh > build.txt 2>&1; rc=$?
    tail -80 build.txt > $R/build_tail.txt
    grep -i -E 'error|undefined' build.txt | head -60 > $R/build_errors.txt
    [ -x dump.exe ] || { echo "FATAL: build failed (rc=$rc)"; cat $R/build_tail.txt; exit 5; }
    cp build.txt dump.log
  else
    timeout 3600 ./dump.exe 1>dump.log 2>dump.err; rc=$?
  fi
  local trun=$(( $(date +%s) - T0 ))
  echo "run rc=$rc in $trun s"
  grep -E 'MV2FLG|MV2MTRACK' dump.log | head -3
  grep 'MV2EVT' dump.log | tail -2
  tail -c 3000 dump.log > $R/${tag}_${name}.log.tail; tail -c 3000 dump.err > $R/${tag}_${name}.err.tail 2>/dev/null
  local ne=$(wc -l < mv2ev.txt 2>/dev/null || echo 0) np=$(wc -l < mv2pa.txt 2>/dev/null || echo 0)
  echo "$tag $name rc=$rc events=$ne particle_lines=$np xrdcp_s=$tcp run_s=$trun" | tee -a $R/runs.txt
  [ -f mv2ev.txt ] && gzip -c mv2ev.txt > $R/${tag}_${name}.ev.txt.gz
  [ -f mv2pa.txt ] && gzip -c mv2pa.txt > $R/${tag}_${name}.pa.txt.gz
  rm -f /tmp/in.dat
}

FIRST=1
while read -r p; do [ -n "$p" ] && { run_one data "$p" $FIRST; FIRST=0; }; done < /tmp/data_list.txt
while read -r p; do [ -n "$p" ] && { run_one mc "$p" $FIRST; FIRST=0; }; done < /tmp/mc_list.txt

log "validation (blind-safe)"
if command -v python3 >/dev/null; then
  (cd /work && PY -m unittest -v test_validate 2>&1 | tail -15)
  PY /work/validate.py --dir $R --out $R/validation_$SLICE.json
  if [ -f /work/dimusel.py ] && [ -f /work/btagcal.py ]; then
    log "blinded spectra and b-tag calibration counts"
    (cd /work && PY -m unittest test_dimusel test_btagcal 2>&1 | tail -4)
    PY /work/dimusel.py --dir $R $PERARG --out $R/spectra_$SLICE.json
    for cf in /work/configs/*.json; do
      [ -f "$cf" ] || continue
      cn=$(basename "$cf" .json)
      echo "config $cn: $(tr -d '\n' < "$cf")"
      PY /work/dimusel.py --dir $R $PERARG --config "$cf" --out $R/spectra_${SLICE}_$cn.json > /dev/null
    done
    [ "$NDATA" -gt 0 ] && PY /work/btagcal.py --dir $R $PERARG --out $R/btagcal_$SLICE.json
    [ "$NMC" -gt 0 ] && PY /work/btagcal.py --dir $R $PERARG --sample mc --out $R/btagcal_mc_$SLICE.json
  fi
else
  echo "python3 missing: ntuples kept, no validation"
fi
if [ "$KEEP_GZ" != 1 ]; then rm -f $R/*.ev.txt.gz $R/*.pa.txt.gz; fi
log "done"; ls -la $R | tail -40; du -sh $R
