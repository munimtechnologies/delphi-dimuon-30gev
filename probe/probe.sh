#!/bin/bash
# delphi-probe 0.1.0 -- feasibility probe for an independent DELPHI open-data test of the
# ALEPH 30 GeV opposite-sign dimuon excess in Z -> b bbar events (arXiv:1610.06536).
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
# Reads only public CERN Open Data (CC0) over xrootd. Writes only to $OUT/probe and /tmp.
set -u
HOME=${HOME:-/root}
OUT=${OUT:-/out}
P=$OUT/probe
mkdir -p "$P" 2>/dev/null || true
if ! touch "$P/.w" 2>/dev/null; then P=/tmp/probe; mkdir -p $P; echo "WARN /out not writable, using $P"; fi
log(){ echo; echo "==== $*"; }

# --- 1. environment -------------------------------------------------------------------
log "id / os / home"
id; head -3 /etc/os-release; echo "HOME=$HOME"; ls -la "$HOME" 2>&1 | head -40
for f in /etc/profile /home/delphi/.bash_profile /home/delphi/.bashrc "$HOME/.bash_profile" "$HOME/.bashrc"; do
  [ -r "$f" ] && source "$f" >/dev/null 2>&1 || true
done
log "profile.d"; ls /etc/profile.d/ 2>&1
log "env (filtered)"
env | grep -i -E 'delphi|cern|pam|fcomp|fflags|ldflags|xrd|eos|^path=' | sort | head -80 | tee $P/env.txt
log "commands"
for c in nypatchy dellib cernlib xrdcp xrdfs gfortran gcc pdftotext python3 git runsim des dstana; do
  printf '%-10s ' $c; command -v $c || echo MISSING
done | tee $P/commands.txt
log "nproc / mem / disk"; nproc; free -m; df -h /tmp /out 2>&1

# --- 2. find examples, cradles and pam files --------------------------------------------
log "find examples and .car files"
timeout 600 find / -xdev \( -name 'dump.cra' -o -name 'dump.sh' -o -name 'dump.car' -o -name 'skelana.car' \
  -o -iname 'muflag*.car' -o -iname 'aabtag*.car' -o -iname 'phdst*.car' -o -name 'stdcdes.car' \) \
  2>/dev/null | head -60 | tee $P/found_files.txt
PAM=${DELPHI_PAM:-}
if [ -n "$PAM" ] && [ -d "$PAM" ]; then ls -la "$PAM" > $P/pam_list.txt 2>&1; fi
EX=$(dirname "$(grep -m1 '/dump.sh$' $P/found_files.txt 2>/dev/null)" 2>/dev/null)
if [ -n "$EX" ] && [ -d "$EX" ]; then
  echo "examples dir: $EX"; tar -czf $P/examples_dump.tgz -C "$EX" . 2>/dev/null
  EXROOT=$(dirname "$EX"); ls -la "$EXROOT" | tee $P/examples_root_list.txt
  tar -czf $P/examples_all.tgz -C "$EXROOT" . 2>/dev/null
  ls -la $P/examples_all.tgz
fi
SK=$(grep -m1 '/skelana.car$' $P/found_files.txt 2>/dev/null)
[ -z "$SK" ] && [ -n "$PAM" ] && [ -f "$PAM/skelana.car" ] && SK="$PAM/skelana.car"
if [ -n "$SK" ]; then
  ls -la "$SK"
  grep -n -E '^\+(DECK|KEEP|PATCH)' "$SK" > $P/skelana_decks.txt 2>/dev/null
  wc -l $P/skelana_decks.txt
  head -c 6000000 "$SK" | gzip > $P/skelana.car.gz
fi
for pat in 'muflag*.car' 'aabtag*.car' 'stdcdes.car'; do
  for f in $(grep -i "/${pat%\*.car}" $P/found_files.txt 2>/dev/null | head -3); do
    b=$(basename "$f"); head -c 3000000 "$f" | gzip > "$P/$b.gz"; echo "saved $b"
  done
done

# --- 3. nickname catalogue: how does FAT = short94_c2 resolve? --------------------------
log "nickname catalogue search"
CAT=$(timeout 600 grep -rIl -m1 'short94_c2' /delphi /opt /usr/local /home/delphi /cvmfs /etc 2>/dev/null | head -5)
echo "files mentioning short94_c2:"; echo "$CAT" | tee $P/catalogue_files.txt
for f in $CAT; do
  echo "--- $f"; grep -n -i -E 'short9[2-5]|kk2f4146|bb' "$f" 2>/dev/null | head -200 >> $P/catalogue_lines.txt
done
grep -c . $P/catalogue_lines.txt 2>/dev/null

# --- 4. data access over xrootd ----------------------------------------------------------
log "xrootd listing"
timeout 120 xrdfs root://eospublic.cern.ch ls /eos/opendata/delphi 2>&1 | head -40 | tee $P/eos_top.txt
timeout 120 xrdfs root://eospublic.cern.ch ls /eos/opendata/delphi/collision-data 2>&1 | head -400 > $P/eos_collision_dirs.txt
wc -l $P/eos_collision_dirs.txt
timeout 120 xrdfs root://eospublic.cern.ch ls -l /eos/opendata/delphi/collision-data/Y13709 2>&1 | head -500 > $P/eos_Y13709.txt
wc -l $P/eos_Y13709.txt; head -3 $P/eos_Y13709.txt
log "xrdcp one short94 file"
T0=$(date +%s)
timeout 1200 xrdcp -f -s root://eospublic.cern.ch//eos/opendata/delphi/collision-data/Y13709/Y13709.1.al /tmp/d1.al
echo "xrdcp exit $? in $(( $(date +%s) - T0 )) s"; ls -la /tmp/d1.al 2>&1 | tee $P/xrdcp_result.txt
echo "seconds=$(( $(date +%s) - T0 ))" >> $P/xrdcp_result.txt

# --- 5. manuals and data policy as text --------------------------------------------------
log "manuals"
mkdir -p /tmp/docs
for u in documentation/skelana/skelana.pdf documentation/skelana/99_175_prog_239.pdf \
         documentation/data-policy/DELPHI_Data_preservation-8.pdf; do
  b=$(basename $u)
  timeout 300 xrdcp -f -s root://eospublic.cern.ch//eos/opendata/delphi/$u /tmp/docs/$b && echo "got $b"
  if command -v pdftotext >/dev/null; then pdftotext -layout /tmp/docs/$b $P/${b%.pdf}.txt 2>/dev/null && echo "text $b";
  elif python3 -c 'import pypdf' 2>/dev/null; then
    python3 - "/tmp/docs/$b" "$P/${b%.pdf}.txt" <<'EOF' 2>&1 | tail -2
import sys, pypdf
src = sys.argv[1]; dst = sys.argv[2]
r = pypdf.PdfReader(src)
with open(dst, 'w') as f:
    for i, pg in enumerate(r.pages):
        f.write('\n=== page %d\n' % (i + 1)); f.write(pg.extract_text() or '')
print('pages', len(r.pages))
EOF
  else cp /tmp/docs/$b $P/ 2>/dev/null; fi
done
ls -la $P/*.txt 2>/dev/null
[ -f $P/DELPHI_Data_preservation-8.txt ] && head -c 12000 $P/DELPHI_Data_preservation-8.txt

# --- 6. public example repositories ------------------------------------------------------
log "git clone examples"
cd /tmp
for r in examples modern-delphi-examples; do
  timeout 300 git clone --depth 1 https://gitlab.cern.ch/delphi/$r.git /tmp/git_$r >/dev/null 2>&1 \
    && tar -czf $P/git_$r.tgz -C /tmp/git_$r --exclude=.git . && echo "cloned $r" || echo "clone $r failed"
done

# --- 7. run the stock dump example on the first events of the local file -----------------
log "dump example on Y13709.1.al"
if [ -n "$EX" ] && [ -f /tmp/d1.al ]; then
  rm -rf /tmp/dump && cp -r "$EX" /tmp/dump && cd /tmp/dump
  echo "FILE = /tmp/d1.al" > PDLINPUT
  chmod +x dump.sh
  T0=$(date +%s); timeout 1500 ./dump.sh > dump_build.txt 2>&1; echo "dump.sh exit $? in $(( $(date +%s) - T0 )) s"
  tail -40 dump_build.txt | tee $P/dump_build_tail.txt
  ls -la
  for f in dump.log dump.err dump.ylog; do
    [ -f $f ] && { wc -c $f; head -c 1500000 $f > $P/$f.head; tail -c 200000 $f > $P/$f.tail; }
  done
  [ -f dump.log ] && grep -c -i -E 'run|event' dump.log
fi
log "done"; ls -la $P; du -sh $P
