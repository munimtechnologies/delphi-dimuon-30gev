#!/bin/bash
# delphi-rootless 0.1.0 -- run a script inside the public DELPHI software image
# (gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd) WITHOUT docker:
# ocipull.py unpacks the image into a root file system, then the script runs in it
# under proot (fallbacks: proot without seccomp, unshare+chroot). Same image, same
# software, same analysis scripts; only the way the container is entered changes.
# Part of the open DELPHI test of the ALEPH 30 GeV dimuon excess (amendment 0.33).
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
#
# Usage: bash delphi_rootless.sh /path/inner.sh   (inner.sh must sit under /tmp or /work)
# Env:   IMAGE  (default the al9_64_xrd image above)
#        CACHE  directory kept between jobs (default /data; falls back to /tmp/cache)
#        OUT    results directory (default /out); this script writes $OUT/rootless/
set -u
IMAGE=${IMAGE:-gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd:latest}
OUT=${OUT:-/out}
R=$OUT/rootless
mkdir -p "$R"
INNER=${1:-}
CACHE=${CACHE:-/data}
if ! mkdir -p "$CACHE/delphi-al9" 2>/dev/null || ! touch "$CACHE/delphi-al9/.w" 2>/dev/null; then
  CACHE=/tmp/cache; mkdir -p $CACHE/delphi-al9
fi
ROOTFS=$CACHE/delphi-al9/rootfs
BLOBS=$CACHE/delphi-al9/blobs
log(){ echo; echo "==== $(date -u +%H:%M:%S) $*"; }
echo "delphi-rootless 0.1.0 IMAGE=$IMAGE CACHE=$CACHE INNER=$INNER"
log "host"; id; uname -a; nproc; free -m; df -h / /tmp "$CACHE" 2>&1
cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null | sed 's/^/unprivileged_userns_clone=/'
grep -E '^(Seccomp|CapEff|NoNewPrivs)' /proc/self/status

log "1. pull and unpack the image"
python3 /work/ocipull.py "$IMAGE" --rootfs "$ROOTFS" --blobs "$BLOBS" --summary $R/pull.json
PULL_RC=$?
[ $PULL_RC -ne 0 ] && { echo "ROOTLESS: R0=FAIL pull rc=$PULL_RC"; cat $R/pull.json; exit 10; }
du -sh "$ROOTFS" 2>/dev/null | tee $R/rootfs_size.txt
ls -la "$ROOTFS" | tee $R/rootfs_top.txt
head -3 "$ROOTFS/etc/os-release" 2>/dev/null
ls "$ROOTFS/etc/profile.d" 2>/dev/null | tr '\n' ' '; echo
df -h "$CACHE" 2>&1 | tail -1

log "2. find proot"
PROOT=$(command -v proot || true)
if [ -z "$PROOT" ]; then
  echo "no proot from apt; trying a static release asset from github.com/proot-me/proot"
  python3 - <<'EOF' > /tmp/proot_url.txt 2>/tmp/proot_url.err
import json, urllib.request
req = urllib.request.Request("https://api.github.com/repos/proot-me/proot/releases",
                             headers={"User-Agent": "delphi-rootless/0.1"})
for rel in json.load(urllib.request.urlopen(req, timeout=60)):
    for a in rel.get("assets", []):
        n = a["name"].lower()
        if "x86_64" in n and "static" in n and "care" not in n and not n.endswith((".sig", ".sha256", ".asc")):
            print(a["browser_download_url"]); raise SystemExit
EOF
  U=$(head -1 /tmp/proot_url.txt); echo "asset: ${U:-none}"; cat /tmp/proot_url.err
  if [ -n "$U" ]; then
    curl -fsSL -o /tmp/proot "$U" && chmod +x /tmp/proot && PROOT=/tmp/proot
    sha256sum /tmp/proot 2>/dev/null | tee $R/proot_sha256.txt
  fi
fi
echo "proot: ${PROOT:-none}"; [ -n "$PROOT" ] && $PROOT --version 2>&1 | head -3

# the image config's ENV, then a login shell
ENTRY='[ -r /.ocipull-env.sh ] && . /.ocipull-env.sh; export HOME=/home/delphi USER=delphi OUT=/out; [ -d /home/delphi ] || export HOME=/root; cd /tmp; '
export PROOT_TMP_DIR=/tmp
BINDS="-b /proc -b /dev -b /sys -b /tmp -b /work -b $OUT:/out -b /etc/resolv.conf -b /etc/hosts"
enter(){  # $1 method, rest: command string for bash -c
  local m=$1; shift
  case $m in
    proot)        env -i PATH=/usr/bin:/bin PROOT_TMP_DIR=/tmp TERM=dumb "$PROOT" -r "$ROOTFS" $BINDS -w /tmp /bin/bash -c "$ENTRY $*" ;;
    proot_noseccomp) env -i PATH=/usr/bin:/bin PROOT_TMP_DIR=/tmp PROOT_NO_SECCOMP=1 TERM=dumb "$PROOT" -r "$ROOTFS" $BINDS -w /tmp /bin/bash -c "$ENTRY $*" ;;
    unshare_chroot) unshare -r -m --propagation private sh -c "
        for d in proc dev sys tmp work out; do mkdir -p '$ROOTFS'/\$d; done
        mount --rbind /proc '$ROOTFS/proc' 2>/dev/null || mount -t proc proc '$ROOTFS/proc'
        mount --rbind /dev '$ROOTFS/dev'; mount --rbind /sys '$ROOTFS/sys'
        mount --bind /tmp '$ROOTFS/tmp'; mount --bind /work '$ROOTFS/work'; mount --bind '$OUT' '$ROOTFS/out'
        cp /etc/resolv.conf '$ROOTFS/etc/resolv.conf' 2>/dev/null
        exec chroot '$ROOTFS' env -i PATH=/usr/bin:/bin TERM=dumb /bin/bash -c \"\$0\"" "$ENTRY $*" ;;
  esac
}

log "3. try each way in"
export ROOTFS PROOT BINDS ENTRY OUT PROOT_TMP_DIR
export -f enter
METHOD=""
for m in proot proot_noseccomp unshare_chroot; do
  [ "${m#proot}" != "$m" ] && [ -z "$PROOT" ] && { echo "$m: skipped (no proot)"; continue; }
  T0=$(date +%s)
  timeout 300 bash -c 'enter "$1" "head -2 /etc/os-release; id; echo INSIDE_OK"' _ $m > /tmp/try_$m.txt 2>&1
  rc=$?
  cat /tmp/try_$m.txt | tail -8; cp /tmp/try_$m.txt $R/try_$m.txt
  echo "$m rc=$rc in $(( $(date +%s) - T0 )) s"
  if grep -q INSIDE_OK /tmp/try_$m.txt; then METHOD=$m; break; fi
done
if [ -z "$METHOD" ]; then
  echo "ROOTLESS: R0=PASS R1=FAIL method=none"
  # diagnostic only: can the image's own loader run its bash directly?
  LD=$(ls "$ROOTFS"/lib64/ld-linux-x86-64.so.2 "$ROOTFS"/usr/lib64/ld-linux-x86-64.so.2 2>/dev/null | head -1)
  [ -n "$LD" ] && "$LD" --library-path "$ROOTFS/usr/lib64:$ROOTFS/lib64" "$ROOTFS/usr/bin/bash" -c 'echo LOADER_OK' 2>&1 | tail -2
  exit 11
fi
echo "method: $METHOD"

log "4. tools inside"
enter $METHOD 'for c in bash gfortran gcc nypatchy xrdcp xrdfs python3 git curl pdftotext; do printf "%-9s " $c; command -v $c || echo MISSING; done; source /etc/profile >/dev/null 2>&1; ls /etc/profile.d; env | grep -i -E "delphi|cern|^path=" | sort | head -30' 2>&1 | tee $R/inside_tools.txt
T0=$(date +%s)
enter $METHOD 'timeout 120 xrdfs root://eospublic.cern.ch ls /eos/opendata/delphi 2>&1 | head -20' 2>&1 | tee $R/inside_xrdfs.txt
XRD=FAIL; grep -q -E 'collision-data|simulated-data' $R/inside_xrdfs.txt && XRD=PASS
echo "xrdfs inside: $XRD in $(( $(date +%s) - T0 )) s"

if [ -n "$INNER" ]; then
  log "5. run $INNER inside ($METHOD)"
  T0=$(date +%s)
  enter $METHOD "bash -l $INNER"
  RC=$?
  echo "inner rc=$RC in $(( $(date +%s) - T0 )) s"
else
  RC=0
fi
echo "ROOTLESS: R0=PASS R1=PASS method=$METHOD xrdfs=$XRD inner_rc=$RC"
exit $RC
