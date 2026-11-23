#!/bin/bash
# delphi-rootless 0.1.1 -- run a script inside the public DELPHI software image
# (gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd) WITHOUT docker:
# ocipull.py unpacks the image into a root file system, then the script runs in it
# under proot (fallback: unshare+chroot). Same image, same software, same analysis
# scripts; only the way the container is entered changes (amendments 0.33 and 0.42).
#
# 0.1.1 (amendment 0.42) changes ONLY the entry environment, after probe v1 showed that
# the job runner's proot does not translate statx (ls inside the image fails) and that the
# DELPHI tools (dellib, cernlib, nypatchy) were not on PATH for a root login:
#   1. every way in is also checked for statx translation (ls of a path that exists only
#      inside the image); the proot-me v5.5.0 release binary (checked against the release's
#      SHA256SUMS) is tried when the system proot fails that check;
#   2. the script runs under the image's own 'delphi' user id (proot -i), as the CERN Open
#      Data guide runs the image (--user delphi, bash -l), when that gives the DELPHI tools;
#   3. /work/delphi_env.sh is sourced after the login profile;
#   4. the DELPHI profile scripts and a trace of sourcing them are saved for diagnosis.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
#
# Usage: bash delphi_rootless.sh /path/inner.sh   (inner.sh must sit under /tmp or /work)
# Env:   IMAGE  (default the al9_64_xrd image above)
#        CACHE  directory kept between jobs (default /data; falls back to /tmp/cache)
#        OUT    results directory (default /out); this script writes $OUT/rootless/
#        PROOT_STATIC_URL  release folder of the fallback proot (default proot-me v5.5.0)
set -u
VERSION=0.1.1
IMAGE=${IMAGE:-gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd:latest}
OUT=${OUT:-/out}
R=$OUT/rootless
mkdir -p "$R"
INNER=${1:-}
CACHE=${CACHE:-/data}
PROOT_STATIC_URL=${PROOT_STATIC_URL:-https://github.com/proot-me/proot/releases/download/v5.5.0}
if ! mkdir -p "$CACHE/delphi-al9" 2>/dev/null || ! touch "$CACHE/delphi-al9/.w" 2>/dev/null; then
  CACHE=/tmp/cache; mkdir -p $CACHE/delphi-al9
fi
ROOTFS=$CACHE/delphi-al9/rootfs
BLOBS=$CACHE/delphi-al9/blobs
log(){ echo; echo "==== $(date -u +%H:%M:%S) $*"; }
echo "delphi-rootless $VERSION IMAGE=$IMAGE CACHE=$CACHE INNER=$INNER"
log "host"; id; uname -a; nproc; free -m; df -h / /tmp "$CACHE" 2>&1
grep -E '^(Seccomp|CapEff|NoNewPrivs)' /proc/self/status

log "1. pull and unpack the image"
python3 /work/ocipull.py "$IMAGE" --rootfs "$ROOTFS" --blobs "$BLOBS" --summary $R/pull.json
PULL_RC=$?
[ $PULL_RC -ne 0 ] && { echo "ROOTLESS: R0=FAIL pull rc=$PULL_RC version=$VERSION"; cat $R/pull.json; exit 10; }
du -sh "$ROOTFS" 2>/dev/null | tee $R/rootfs_size.txt
head -3 "$ROOTFS/etc/os-release" 2>/dev/null
DID=$(awk -F: '$1=="delphi"{print $3":"$4; exit}' "$ROOTFS/etc/passwd" 2>/dev/null)
echo "delphi user id in image: ${DID:-none}" | tee $R/delphi_uid.txt
df -h "$CACHE" 2>&1 | tail -1

log "2. find proot binaries"
PROOT_APT=$(command -v proot || true)
echo "system proot: ${PROOT_APT:-none}"
if [ -n "$PROOT_APT" ]; then
  dpkg -s proot 2>/dev/null | grep -E '^Version' | sed 's/^/  apt /'
  $PROOT_APT --version 2>&1 | grep -i -E 'v[0-9]+\.[0-9]+' | head -2 | sed 's/^/  /'
fi
PROOT_STATIC=""
if curl -fsSL --retry 3 -o /tmp/proot_static "$PROOT_STATIC_URL/proot" && \
   curl -fsSL --retry 3 -o /tmp/proot_SHA256SUMS "$PROOT_STATIC_URL/SHA256SUMS"; then
  WANT=$(awk '$2=="proot"{print $1; exit}' /tmp/proot_SHA256SUMS)
  GOT=$(sha256sum /tmp/proot_static | cut -d' ' -f1)
  echo "static proot sha256 $GOT (release SHA256SUMS: ${WANT:-missing})" | tee $R/proot_static_sha256.txt
  if [ -n "$WANT" ] && [ "$WANT" = "$GOT" ]; then
    chmod +x /tmp/proot_static && PROOT_STATIC=/tmp/proot_static
    $PROOT_STATIC --version 2>&1 | grep -i -E 'v[0-9]+\.[0-9]+' | head -2 | sed 's/^/  /'
  else
    echo "static proot NOT used: checksum mismatch or missing"
  fi
else
  echo "static proot download failed" | tee $R/proot_static_sha256.txt
fi
echo "static proot: ${PROOT_STATIC:-none}"

# the image config's ENV, then the DELPHI user's home
ENTRY='[ -r /.ocipull-env.sh ] && . /.ocipull-env.sh; export HOME=/home/delphi USER=delphi LOGNAME=delphi OUT=/out; [ -d /home/delphi ] || export HOME=/root; cd /tmp; '
export PROOT_TMP_DIR=/tmp
BINDS="-b /proc -b /dev -b /sys -b /tmp -b /work -b $OUT:/out -b /etc/resolv.conf -b /etc/hosts"
enter(){  # $1 method, $2 uid:gid ("" = root), rest: command string for bash -c
  local m=$1 id=$2; shift 2
  local P="" NS="" IDOPT=""
  [ -n "$id" ] && IDOPT="-i $id"
  case $m in
    proot_apt)              P=$PROOT_APT ;;
    proot_apt_noseccomp)    P=$PROOT_APT; NS=1 ;;
    proot_static)           P=$PROOT_STATIC ;;
    proot_static_noseccomp) P=$PROOT_STATIC; NS=1 ;;
    unshare_chroot) unshare -r -m --propagation private sh -c "
        for d in proc dev sys tmp work out; do mkdir -p '$ROOTFS'/\$d; done
        mount --rbind /proc '$ROOTFS/proc' 2>/dev/null || mount -t proc proc '$ROOTFS/proc'
        mount --rbind /dev '$ROOTFS/dev'; mount --rbind /sys '$ROOTFS/sys'
        mount --bind /tmp '$ROOTFS/tmp'; mount --bind /work '$ROOTFS/work'; mount --bind '$OUT' '$ROOTFS/out'
        cp /etc/resolv.conf '$ROOTFS/etc/resolv.conf' 2>/dev/null
        exec chroot '$ROOTFS' env -i PATH=/usr/bin:/bin TERM=dumb /bin/bash -c \"\$0\"" "$ENTRY $*"
      return $? ;;
  esac
  env -i PATH=/usr/bin:/bin PROOT_TMP_DIR=/tmp TERM=dumb ${NS:+PROOT_NO_SECCOMP=1} \
    "$P" $IDOPT -r "$ROOTFS" $BINDS -w /tmp /bin/bash -c "$ENTRY $*"
}

log "3. try each way in (bash runs AND statx is translated)"
export ROOTFS PROOT_APT PROOT_STATIC BINDS ENTRY OUT PROOT_TMP_DIR
export -f enter
CHECK='head -2 /etc/os-release; id; echo INSIDE_OK; ls -d /delphi/releases >/dev/null 2>&1 && echo STATX_OK; ls -la /etc/profile.d 2>&1 | head -4'
METHOD=""; FIRST=""; STATX=FAIL
for m in proot_apt proot_apt_noseccomp proot_static proot_static_noseccomp unshare_chroot; do
  case $m in
    proot_apt*)    [ -z "$PROOT_APT" ] && { echo "$m: skipped (no system proot)"; continue; } ;;
    proot_static*) [ -z "$PROOT_STATIC" ] && { echo "$m: skipped (no static proot)"; continue; } ;;
  esac
  T0=$(date +%s)
  timeout 300 bash -c 'enter "$1" "" "$2"' _ $m "$CHECK" > /tmp/try_$m.txt 2>&1
  rc=$?
  tail -8 /tmp/try_$m.txt; cp /tmp/try_$m.txt $R/try_$m.txt
  S=no; grep -q STATX_OK /tmp/try_$m.txt && S=yes
  echo "METHOD: $m rc=$rc inside=$(grep -q INSIDE_OK /tmp/try_$m.txt && echo yes || echo no) statx=$S in $(( $(date +%s) - T0 )) s"
  if grep -q INSIDE_OK /tmp/try_$m.txt; then
    [ -z "$FIRST" ] && FIRST=$m
    if [ $S = yes ]; then METHOD=$m; STATX=PASS; break; fi
  fi
done
[ -z "$METHOD" ] && [ -n "$FIRST" ] && METHOD=$FIRST
if [ -z "$METHOD" ]; then
  echo "ROOTLESS: R0=PASS R1=FAIL method=none version=$VERSION"
  exit 11
fi
echo "method: $METHOD statx=$STATX"

log "4. DELPHI environment: which user id gives the DELPHI tools"
cat > /tmp/envchk.sh <<'EOF'
. /work/delphi_env.sh >/dev/null 2>&1
for c in dellib cernlib nypatchy; do printf '%s=' $c; command -v $c || echo MISSING; done
echo "uid=$(id -u) user=$(id -un 2>/dev/null) HOME=$HOME source=${DELPHI_ENV_SOURCE:-unset}"
env | grep -E '^(DELPHI|CERN|FCOMP|FFLAGS|LDFLAGS|PATH=)' | sort | head -40
EOF
IDSEL=""; ENVOK=FAIL
CANDS=""
[ -n "$DID" ] && [ "$METHOD" != unshare_chroot ] && CANDS="$DID"
CANDS="$CANDS root"
for c in $CANDS; do
  idarg=$c; [ $c = root ] && idarg=""
  timeout 300 bash -c 'enter "$1" "$2" "bash -l /tmp/envchk.sh"' _ $METHOD "$idarg" > /tmp/env_${c//:/_}.txt 2>&1
  cp /tmp/env_${c//:/_}.txt $R/env_${c//:/_}.txt
  sed 's/^/  /' /tmp/env_${c//:/_}.txt | head -30
  # a tool counts as present when command -v printed anything (a path, or a function name)
  if [ "$(grep -c -E '^(dellib|cernlib|nypatchy)=.+' /tmp/env_${c//:/_}.txt)" = 3 ] && ! grep -q -E '^(dellib|cernlib|nypatchy)=MISSING' /tmp/env_${c//:/_}.txt; then
    IDSEL=$idarg; ENVOK=PASS; break
  fi
done
if [ $ENVOK = FAIL ]; then IDSEL=$DID; [ "$METHOD" = unshare_chroot ] && IDSEL=""; fi
echo "DELPHIENV: env=$ENVOK id=${IDSEL:-root} method=$METHOD $(grep -h -E '^(dellib|cernlib|nypatchy)=' /tmp/env_*.txt 2>/dev/null | head -3 | tr '\n' ' ')"

log "5. DELPHI profile scripts (diagnosis)"
cat > /tmp/diag.sh <<'EOF'
echo "--- /etc/profile.d/delphi.sh"; head -c 20000 /etc/profile.d/delphi.sh 2>&1; echo
for f in /home/delphi/.bash_profile /home/delphi/.bashrc /home/delphi/.profile; do echo "--- $f"; head -c 8000 "$f" 2>&1; echo; done
echo "--- ls -la /home/delphi"; ls -la /home/delphi 2>&1 | head -40
echo "--- ls -la /delphi"; ls -la /delphi 2>&1 | head -40
echo "--- setup scripts and tools under /delphi"
find /delphi -maxdepth 6 \( -name dellib -o -name cernlib -o -name nypatchy -o -name 'setup*.sh' -o -name 'delphi*.sh' \) 2>/dev/null | head -60
echo "--- trace of sourcing /etc/profile.d/delphi.sh"
bash -x -c '. /etc/profile.d/delphi.sh' 2>&1 | head -300
EOF
timeout 600 bash -c 'enter "$1" "$2" "bash /tmp/diag.sh"' _ $METHOD "$IDSEL" > $R/delphi_profile.txt 2>&1
wc -c $R/delphi_profile.txt
T0=$(date +%s)
enter $METHOD "$IDSEL" 'timeout 120 xrdfs root://eospublic.cern.ch ls /eos/opendata/delphi 2>&1 | head -20' 2>&1 | tee $R/inside_xrdfs.txt
XRD=FAIL; grep -q -E 'collision-data|simulated-data' $R/inside_xrdfs.txt && XRD=PASS
echo "xrdfs inside: $XRD in $(( $(date +%s) - T0 )) s"

if [ -n "$INNER" ]; then
  log "6. run $INNER inside ($METHOD, id ${IDSEL:-root})"
  T0=$(date +%s)
  enter $METHOD "$IDSEL" "bash -l -c '. /work/delphi_env.sh >/dev/null 2>&1; bash $INNER'"
  RC=$?
  echo "inner rc=$RC in $(( $(date +%s) - T0 )) s"
else
  RC=0
fi
echo "ROOTLESS: R0=PASS R1=PASS method=$METHOD statx=$STATX env=$ENVOK id=${IDSEL:-root} xrdfs=$XRD inner_rc=$RC version=$VERSION"
exit $RC
