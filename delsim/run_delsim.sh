#!/bin/bash
# mv2-delsim-signal 0.1.0 -- DELPHI detector simulation (DELSIM, 1994 detector v94c) of a
# 30.4 GeV dimuon signal radiated off the b line in Z -> b bbar, for the open DELPHI test of the
# ALEPH 30 GeV dimuon excess (arXiv:1610.06536). Measures DELPHI's dimuon mass resolution and
# signal efficiency. Simulation only: no real-data dimuon mass is looked at.
# Stages: 0 env; 1 python (uv); 2 code + unit tests; 3 generate (xkin V model -> FADGEN);
# 4 condition-data access + 3-event built-in smoke test (default env, xrootd, local copy);
# 5 two-pass runsim -gext with LUDECV TRUE; 6 SKELANA ntuple (mv2user02s.car); 7 sigana.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
# Reads public CERN Open Data (CC0) and MV2's public repo; writes only to $OUT/delsim and /tmp.
set -u
HOME=${HOME:-/root}
OUT=${OUT:-/out}
R=$OUT/delsim
mkdir -p "$R" 2>/dev/null || { R=/tmp/delsim_out; mkdir -p $R; }
NEV=${NEV:-400}
NGEN=$(( NEV + (NEV + 9) / 10 + 30 ))
EBEAM=${EBEAM:-45.594}
VERSION=${VERSION:-v94c}
EOS=root://eospublic.cern.ch/
DDBPATH=/eos/opendata/delphi/condition-data
REPO=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main
W=/work
log(){ echo; echo "==== $(date -u +%H:%M:%S) $*"; }
status(){ echo "$1=$2" | tee -a $R/status.txt; }
: > $R/status.txt

# ---------------------------------------------------------------- 0. environment
log "0 environment"
id; head -2 /etc/os-release; nproc; free -m; df -h /tmp $OUT 2>&1
set +u
for f in /etc/profile /home/delphi/.bash_profile /home/delphi/.bashrc "$HOME/.bash_profile" "$HOME/.bashrc"; do
  [ -r "$f" ] && source "$f" >/dev/null 2>&1 || true
done
set -u
env | grep -i -E 'delphi|ddb|cern|xrd|eos|^path=|ld_library' | sort | tee $R/env.txt | head -60
for c in runsim xrdcp xrdfs curl git python3 gfortran nypatchy; do printf '%-9s ' $c; command -v $c || echo MISSING; done | tee $R/commands.txt
command -v runsim >/dev/null && { head -c 20000 "$(command -v runsim)" > $R/runsim_script_head.txt 2>/dev/null; grep -n -i -E 'DDB|condition|eos|xrd' "$(command -v runsim)" | head -40; }
status runsim "$(command -v runsim || echo missing)"

# ---------------------------------------------------------------- 1. python
log "1 python via uv (isolated from the DELPHI LD_LIBRARY_PATH)"
export UV_CACHE_DIR=/tmp/uvcache UV_PYTHON_INSTALL_DIR=/tmp/uvpy
mkdir -p /tmp/uv
PY=""
if timeout 300 curl -fsSL -o /tmp/uv/uv.tgz https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz \
   && tar xzf /tmp/uv/uv.tgz -C /tmp/uv; then
  UV=$(find /tmp/uv -name uv -type f | head -1)
  echo "uv: $UV"
  if [ -n "$UV" ] && env -u LD_LIBRARY_PATH timeout 900 "$UV" venv -q /tmp/venv --python 3.12 \
     && env -u LD_LIBRARY_PATH timeout 1200 "$UV" pip install -q --python /tmp/venv/bin/python 'numpy>=1.26' 'pythia8mc==8.318.3'; then
    PY=/tmp/venv/bin/python
  fi
fi
if [ -z "$PY" ] && command -v python3 >/dev/null; then
  echo "uv route failed; trying system python3 venv"
  env -u LD_LIBRARY_PATH python3 -m venv /tmp/venv2 \
    && env -u LD_LIBRARY_PATH timeout 1200 /tmp/venv2/bin/python -m pip install -q 'numpy>=1.26' 'pythia8mc==8.318.3' \
    && PY=/tmp/venv2/bin/python
fi
status python "${PY:-none}"
PYRUN(){ env -u LD_LIBRARY_PATH -u PYTHIA8DATA -u PYTHONPATH -u PYTHONHOME PYTHONDONTWRITEBYTECODE=1 "$PY" "$@"; }

# ---------------------------------------------------------------- 2. code + tests
log "2 code and unit tests"
mkdir -p /tmp/code
for f in xme.py evana.py fadgen.py run_xkin.py test_xkin.py; do
  timeout 120 curl -fsSL -o /tmp/code/$f $REPO/xkin/$f || echo "fetch $f FAILED"
done
for f in sigana.py test_sigana.py gen_signal.py; do sed 's/\r$//' $W/$f > /tmp/code/$f; done
sha256sum /tmp/code/*.py | tee $R/code_sha256.txt
if [ -n "$PY" ]; then
  (cd /tmp/code && PYRUN -m unittest -v test_sigana 2>&1 | tee $R/tests_sigana.txt | tail -20)
  (cd /tmp/code && timeout 1800 env -u LD_LIBRARY_PATH -u PYTHIA8DATA -u PYTHONPATH -u PYTHONHOME PYTHONDONTWRITEBYTECODE=1 "$PY" -m unittest test_xkin 2>&1 | tail -8 | tee $R/tests_xkin.txt)
fi

# ---------------------------------------------------------------- 3. generate
log "3 generate $NGEN V-model events (xkin + Pythia 8) as FADGEN"
FAD=$R/gen/fadgen_V.fort26
if [ -n "$PY" ]; then
  (cd /tmp/code && timeout 3600 env -u LD_LIBRARY_PATH -u PYTHIA8DATA -u PYTHONPATH -u PYTHONHOME PYTHONDONTWRITEBYTECODE=1 "$PY" gen_signal.py --model V --n $NGEN --seed 30401 --out $R/gen 2>&1 | tail -60)
fi
NFAD=$(grep -m1 -o '"written": [0-9]*' $R/gen/gen_stats.json 2>/dev/null | grep -o '[0-9]*$')
NFAD=${NFAD:-0}
status fadgen_events $NFAD
ls -la $R/gen 2>&1

# ---------------------------------------------------------------- 4. condition data + smoke test
log "4 condition data and DELSIM smoke test"
echo "DELPHI_DDB=${DELPHI_DDB:-unset}"
ls -la "${DELPHI_DDB:-/nonexistent}" 2>&1 | head -30 > $R/ddb_env_ls.txt
ls -la /eos/opendata/delphi 2>&1 | head -10 >> $R/ddb_env_ls.txt
timeout 300 xrdfs $EOS ls -l $DDBPATH > $R/ddb_top.txt 2>&1
head -40 $R/ddb_top.txt
timeout 1200 xrdfs $EOS ls -l -R $DDBPATH > /tmp/ddb_tree.txt 2>&1
head -4000 /tmp/ddb_tree.txt > $R/ddb_tree_head.txt
DDB_FILES=$(grep -c '^-' /tmp/ddb_tree.txt)
DDB_BYTES=$(awk '/^-/{s+=$(NF-1)} END{printf "%.0f", s+0}' /tmp/ddb_tree.txt)
status ddb_files "$DDB_FILES"; status ddb_bytes "$DDB_BYTES"

try_smoke(){  # $1 label; success = a short DST was written
  local d=/tmp/smoke_$1; rm -rf $d; mkdir -p $d; cd $d
  local T0=$(date +%s)
  timeout 2400 runsim -VERSION $VERSION -LABO CERN -NRUN 1000 -EBEAM 45.625 -igen mumu -NEVMAX 3 > run.log 2>&1
  local rc=$?
  ls -la > $R/smoke_$1.ls.txt
  tail -c 8000 run.log > $R/smoke_$1.log.tail
  grep -i -E 'ddb|condition|cannot|not found|no such|error|fatal|abort|open' run.log | head -80 > $R/smoke_$1.errors.txt
  local s; s=$(ls simana.*sdst 2>/dev/null | head -1)
  echo "smoke $1 rc=$rc t=$(( $(date +%s) - T0 ))s sdst=${s:-none} bytes=$( [ -n "$s" ] && stat -c %s $s)" | tee -a $R/status.txt
  [ -n "$s" ] && [ -s "$s" ]
}
SIMOK=""
if ! command -v runsim >/dev/null; then
  echo "runsim missing"
elif try_smoke default; then SIMOK=default
else
  OLD=${DELPHI_DDB:-}
  export DELPHI_DDB="${EOS}${DDBPATH}"
  if try_smoke xrootd; then SIMOK=xrootd
  else
    if [ -n "$OLD" ]; then export DELPHI_DDB=$OLD; else unset DELPHI_DDB; fi
    FREE=$(df -B1 --output=avail /tmp | tail -1)
    if [ "${DDB_BYTES:-0}" -gt 0 ] && [ "$DDB_BYTES" -lt 6000000000 ] && [ "$FREE" -gt $(( DDB_BYTES + 3000000000 )) ]; then
      mkdir -p /tmp/ddb
      T0=$(date +%s)
      timeout 5400 xrdcp -r -f -s "${EOS}${DDBPATH}" /tmp/ddb/; echo "xrdcp ddb rc=$? in $(( $(date +%s) - T0 )) s"
      du -sh /tmp/ddb; ls /tmp/ddb | head
      LOC=/tmp/ddb/condition-data; [ -d $LOC ] || LOC=/tmp/ddb
      export DELPHI_DDB=$LOC
      if try_smoke localcopy; then SIMOK=localcopy
      elif mkdir -p /eos/opendata/delphi 2>/dev/null && ln -sfn $LOC /eos/opendata/delphi/condition-data; then
        export DELPHI_DDB=/eos/opendata/delphi/condition-data
        try_smoke eoslink && SIMOK=eoslink
      else
        echo "cannot create /eos/opendata/delphi (not root?)"
      fi
    else
      status ddb_copy "skipped (bytes=$DDB_BYTES free=$FREE)"
    fi
  fi
fi
status sim_mode "${SIMOK:-none}"

# ---------------------------------------------------------------- 5. signal through DELSIM
SDST=""
if [ -n "$SIMOK" ] && [ "$NFAD" -gt 20 ]; then
  NEVRUN=$NEV
  MAXRUN=$(( NFAD * 10 / 11 - 2 ))
  [ $NEVRUN -gt $MAXRUN ] && NEVRUN=$MAXRUN
  status nev_simulated $NEVRUN
  log "5 DELSIM $VERSION on $NEVRUN signal events (EBEAM $EBEAM)"
  S=/tmp/sig; rm -rf $S; mkdir -p $S; cd $S
  cp $FAD my_events.fadgen
  timeout 1800 runsim -VERSION $VERSION -LABO CERN -NRUN 1001 -EBEAM $EBEAM -NEVMAX 5 -gext my_events.fadgen > prerun.log 2>&1
  echo "prerun rc=$?"; tail -c 4000 prerun.log > $R/prerun.log.tail
  MODE=singlepass
  if [ -f simlocal.title ]; then
    cp simlocal.title $R/simlocal.title.orig
    if grep -q -i -E '^[[:space:]]*JSHORT' simlocal.title; then
      awk '{print} toupper($0) ~ /^[[:space:]]*JSHORT/ {print "LUDECV   TRUE"}' simlocal.title \
        | sed -E "s/^([[:space:]]*[Nn][Ee][Vv][Mm][Aa][Xx][[:space:]=]+)[0-9]+/\1$NEVRUN/" > simlocal_edit.title
      cp simlocal_edit.title $R/simlocal_edit.title
      grep -n -i -E 'nevmax|nevt|xyzp|xyzw|igener|ludecv|jshort|ebeam' simlocal_edit.title | tee $R/title_lines.txt
      MODE=twopass_ludecv
    fi
  fi
  rm -f simana.* FOR* fort.* simdec.data igtots.logn delsimrn.out88 scanlist.sumr T.FSEQ1 simlocal.title
  ln -sf my_events.fadgen fort.18
  T0=$(date +%s)
  if [ "$MODE" = twopass_ludecv ]; then
    timeout 18000 runsim -VERSION $VERSION -LABO CERN -NRUN 1001 -EBEAM $EBEAM -NEVMAX $NEVRUN -gext my_events.fadgen -STITL simlocal_edit.title > main.log 2>&1
  else
    timeout 18000 runsim -VERSION $VERSION -LABO CERN -NRUN 1001 -EBEAM $EBEAM -NEVMAX $NEVRUN -gext my_events.fadgen > main.log 2>&1
  fi
  RC=$?; DT=$(( $(date +%s) - T0 ))
  status sim_run_mode $MODE; status sim_rc $RC; status sim_seconds $DT
  tail -c 12000 main.log > $R/main.log.tail
  grep -i -E 'igener|fatal|error|sxluze|events? (processed|read|written)' main.log | head -80 > $R/main.log.grep
  ls -la | tee $R/sim_ls.txt
  SDST=$(ls $S/simana.*sdst 2>/dev/null | head -1)
  status sdst "${SDST:-none}"
fi

# ---------------------------------------------------------------- 6. ntuple on the simulated signal
if [ -n "$SDST" ] && [ -s "$SDST" ]; then
  log "6 SKELANA ntuple (mv2user02s) on $SDST"
  DS=$(find / -xdev -name dump.sh -path '*dump*' 2>/dev/null | head -1)
  EX=""; [ -n "$DS" ] && EX=$(dirname "$DS")
  if [ -z "$EX" ] || [ ! -f "$EX/dump.cra" ]; then
    timeout 300 git clone --depth 1 https://gitlab.cern.ch/delphi/examples.git /tmp/git_examples >/dev/null 2>&1 && EX=/tmp/git_examples/dump
  fi
  echo "example dir: $EX"
  B=/tmp/build; rm -rf $B; cp -r "$EX" $B && cd $B
  [ -f dump.car ] || { [ -n "${DELPHI_PAM:-}" ] && cp "$DELPHI_PAM/skelana.car" dump.car; }
  sed 's/\r$//' $W/mv2user02s.car > /tmp/mv2user02s.car
  TARGET=""
  for f in dump.car dump.cra; do grep -q -i -E '^\+DECK *, *USER02[ ,.]' $f 2>/dev/null && { TARGET=$f; break; }; done
  if [ -n "$TARGET" ]; then
    awk -v repl=/tmp/mv2user02s.car '
      BEGIN { skip = 0 }
      toupper($0) ~ /^\+DECK *, *USER02[ ,.]/ { while ((getline line < repl) > 0) print line; skip = 1; next }
      skip && toupper($0) ~ /^\+(DECK|PATCH|KEEP|QUIT)/ { skip = 0 }
      !skip { print }' $TARGET > $TARGET.new && mv $TARGET.new $TARGET
    echo "FILE = $SDST" > PDLINPUT
    chmod +x dump.sh
    T0=$(date +%s); timeout 3600 ./dump.sh > build.txt 2>&1; echo "dump.sh rc=$? in $(( $(date +%s) - T0 )) s"
    tail -60 build.txt > $R/ntuple_build_tail.txt
    grep -i -E 'error|undefined' build.txt | head -60 > $R/ntuple_build_errors.txt
    grep -E 'MV2FLG|MV2MTRACK|MV2EVT' dump.log 2>/dev/null | head -8
    tail -c 4000 dump.log > $R/ntuple_dump.log.tail 2>/dev/null
    for f in mv2ev.txt mv2pa.txt; do [ -f $f ] && { wc -l $f; gzip -c $f > $R/sig_V_$VERSION.${f%.txt}.txt.gz; }; done
  else
    echo "no USER02 deck found"; status ntuple "no_user02_deck"
  fi
  # ---------------------------------------------------------------- 7. analysis
  if [ -n "$PY" ] && [ -f $R/sig_V_$VERSION.mv2ev.txt.gz ]; then
    log "7 sigana"
    (cd /tmp/code && PYRUN sigana.py --fadgen $FAD --ev $R/sig_V_$VERSION.mv2ev.txt.gz \
      --pa $R/sig_V_$VERSION.mv2pa.txt.gz --nsim ${NEVRUN:-0} --out $R/sigana.json)
  fi
  SZ=$(stat -c %s "$SDST")
  if [ "$SZ" -lt 400000000 ]; then gzip -c "$SDST" > $R/sig_V_$VERSION.sdst.gz; fi
fi
[ -f $FAD ] && gzip -f $FAD
log "done"; cat $R/status.txt; ls -la $R; du -sh $R
