#!/bin/bash
# xrdfix 0.1.0 (PLAN amendment 0.44) -- entry-environment fix for job dimu-ntuple-rl-v2.
# Sourced (not executed) by inner_ntuple.sh INSIDE the DELPHI image, before run_ntuple.sh.
#
# Why: dimu-ntuple-rl-v1 passed N0 (image unpacked, shell inside, DELPHI tools found, xrdcp read
# a data file) but failed N1 at link time: "/usr/bin/ld: cannot find -lXrdPosix". The image's
# XRootD-enabled CERNLIB (CERNLIB_XROOTD=ON, release almalinux-9-x86_64_xrd) links -lXrdPosix,
# and the unversioned libXrdPosix.so was not found where ld looks.
#
# What it does (environment only; the image, the DELPHI release and every analysis file stay
# untouched, as amendment 0.35 requires for an N1 failure):
#  A. writes a diagnosis to /out/xrdfix.txt: every libXrd* in the default library dirs, every
#     libXrdPosix* in the image, the xrootd RPMs, the Xrd lines of the cernlib script, ld's
#     search dirs;
#  B. for each XRootD library the link may ask for, if no unversioned lib<name>.so resolves in a
#     default dir, copies the newest versioned lib<name>.so.N (or the resolved .so) to
#     /tmp/mv2xrd/lib<name>.so and prepends /tmp/mv2xrd to LIBRARY_PATH (gcc hands LIBRARY_PATH
#     directories to ld as -L). A copy, not a symlink, so no proot link translation is involved;
#  C. only if libXrdPosix is absent from the image altogether: downloads the xrootd client RPMs
#     as a normal user with 'dnf download' into /tmp, unpacks them with rpm2archive (or
#     rpm2cpio+cpio), and adds their lib64 to LIBRARY_PATH and LD_LIBRARY_PATH.
# It never exits the calling shell. It prints 'XRDFIX:' summary lines.
# Part of the open DELPHI test of the ALEPH 30 GeV dimuon excess.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

XRDFIX_VERSION=0.1.0
XD=/tmp/mv2xrd
XLOG=/out/xrdfix.txt
mkdir -p "$XD" /out 2>/dev/null
xrd_prune_find() {  # $1 = name pattern; searches the image, skipping pseudo and bound dirs
  timeout 300 find / \( -path /proc -o -path /sys -o -path /dev -o -path /eos -o -path /tmp \
      -o -path /work -o -path /out -o -path /data \) -prune -o -name "$1" -print 2>/dev/null
}
{
  echo "xrdfix $XRDFIX_VERSION at $(date -u +%H:%M:%S) uid=$(id -u)"
  echo "--- A1. libXrd* in default library dirs"
  ls -la /usr/lib64/libXrd* /usr/lib/libXrd* /lib64/libXrd* /usr/local/lib64/libXrd* 2>&1 | head -120
  echo "--- A2. libXrdPosix* anywhere in the image"
  xrd_prune_find 'libXrdPosix*' | head -50
  echo "--- A3. xrootd packages"
  rpm -qa 2>/dev/null | grep -i xrootd | sort
  echo "--- A4. Xrd in the cernlib script"
  cl=$(command -v cernlib 2>/dev/null); echo "cernlib=$cl"
  [ -n "$cl" ] && grep -n -i xrd "$cl" | head -40
  echo "--- A5. ld search dirs"
  ld --verbose 2>/dev/null | grep -o 'SEARCH_DIR("[^"]*")' | tr '\n' ' '; echo
  echo "--- A6. LIBRARY_PATH before: ${LIBRARY_PATH:-<unset>}  LD_LIBRARY_PATH before: ${LD_LIBRARY_PATH:-<unset>}"
} > "$XLOG" 2>&1

# Library names to cover: XrdPosix (the one v1 missed) plus any -lXrd* named by the cernlib script.
xrd_names="XrdPosix XrdCl XrdUtils"
if [ -n "${cl:-}" ] && [ -r "$cl" ]; then
  xrd_names="$xrd_names $(grep -o -- '-lXrd[A-Za-z0-9]*' "$cl" | sed 's/^-l//' | tr '\n' ' ')"
fi
xrd_names=$(echo $xrd_names | tr ' ' '\n' | sort -u | tr '\n' ' ')
xrd_missing=""
xrd_extra_ld=""
for n in $xrd_names; do
  src=""
  for d in /usr/lib64 /usr/lib /lib64 /usr/local/lib64 /usr/local/lib; do
    if [ -e "$d/lib$n.so" ]; then src=$(readlink -f "$d/lib$n.so"); how="unversioned-present"; break; fi
  done
  if [ -z "$src" ]; then
    src=$(ls -1 /usr/lib64/lib$n.so.* /usr/lib/lib$n.so.* /lib64/lib$n.so.* /usr/local/lib64/lib$n.so.* \
          2>/dev/null | sort -V | tail -1)
    how="versioned-default-dir"
  fi
  if [ -z "$src" ]; then
    src=$(xrd_prune_find "lib$n.so*" | sort -V | tail -1)
    how="found-elsewhere"
    [ -n "$src" ] && xrd_extra_ld="$xrd_extra_ld:$(dirname "$src")"
  fi
  if [ -n "$src" ] && cp -L "$src" "$XD/lib$n.so" 2>>"$XLOG"; then
    echo "XRDFIX: $n $how -> $XD/lib$n.so copied from $src" | tee -a "$XLOG"
  else
    xrd_missing="$xrd_missing $n"
    echo "XRDFIX: $n NOT FOUND in the image" | tee -a "$XLOG"
  fi
done

# Step C: libXrdPosix absent from the image -> fetch the xrootd client RPMs as a normal user.
case " $xrd_missing " in
  *" XrdPosix "*)
    R=/tmp/mv2xrdrpm; mkdir -p "$R/dl" "$R/root"
    echo "--- C. dnf download (libXrdPosix absent)" >> "$XLOG"
    timeout 900 dnf -q -y --setopt=cachedir=/tmp/mv2dnf download --destdir "$R/dl" \
      xrootd-client-libs xrootd-libs xrootd-client-devel xrootd-devel >> "$XLOG" 2>&1
    echo "dnf rc=$?" >> "$XLOG"
    for p in "$R"/dl/*.rpm; do
      [ -e "$p" ] || continue
      if command -v rpm2archive >/dev/null 2>&1 && rpm2archive "$p" >> "$XLOG" 2>&1 && [ -e "$p.tgz" ]; then
        tar -xzf "$p.tgz" -C "$R/root" >> "$XLOG" 2>&1
      elif command -v cpio >/dev/null 2>&1; then
        (cd "$R/root" && rpm2cpio "$p" | cpio -idm --quiet) >> "$XLOG" 2>&1
      fi
      echo "unpacked $(basename "$p")" >> "$XLOG"
    done
    if ls "$R"/root/usr/lib64/libXrdPosix.so* >/dev/null 2>&1; then
      xrd_extra_ld="$xrd_extra_ld:$R/root/usr/lib64"
      export LIBRARY_PATH="$R/root/usr/lib64${LIBRARY_PATH:+:$LIBRARY_PATH}"
      echo "XRDFIX: XrdPosix fetched by dnf into $R/root/usr/lib64" | tee -a "$XLOG"
      xrd_missing=$(echo " $xrd_missing " | sed 's/ XrdPosix / /')
    else
      echo "XRDFIX: XrdPosix could not be fetched" | tee -a "$XLOG"
    fi
    ;;
esac

export LIBRARY_PATH="$XD${LIBRARY_PATH:+:$LIBRARY_PATH}"
if [ -n "$xrd_extra_ld" ]; then
  export LD_LIBRARY_PATH="${xrd_extra_ld#:}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
{
  echo "--- after: LIBRARY_PATH=$LIBRARY_PATH LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-<unset>}"
  ls -la "$XD"
} >> "$XLOG" 2>&1
if [ -z "$(echo $xrd_missing)" ]; then xrd_result=READY; else xrd_result="MISSING:$(echo $xrd_missing | tr ' ' ',')"; fi
echo "XRDFIX: version=$XRDFIX_VERSION result=$xrd_result names=$(echo $xrd_names | tr ' ' ',')" | tee -a "$XLOG"
