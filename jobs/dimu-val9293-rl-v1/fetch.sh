#!/bin/bash
# dimu-val9293-rl fetch 0.1.0 -- copy the committed DELPHI-route files into /work and record sha256.
# Validation run 2 (plan v0.11 section 4j: 1992 and 1993 short DSTs + KK2f simulation) entered
# through delphi-rootless 0.1.1 instead of docker, exactly as dimu-ntuple-rl-v1 (amendment 0.43).
# Entry files carry FATAL sha256 pins equal to the hashes printed by job delphi-rootless-probe-v2.
# val9293/run_val9293.sh is pinned by its 40-character commit and used UNCHANGED; it fetches the
# analysis code itself and refuses to run unless that code is run_ntuple 0.3.0 / dimusel 0.3.0 /
# btagcal 0.2.0 (all frozen under the plan's version guard); it prints their sha256 itself
# (out/code_sha256.txt).
# Part of the open DELPHI test of the ALEPH 30 GeV dimuon excess.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
set -u
V_COMMIT=0b674847dc411cceac8b9ab67e33eefe806177e0   # repo main at staging (run_val9293.sh)
R_COMMIT=9f575600c13bd0fc30e532c1bbd1736012d87996   # delphi-rootless 0.1.1
GH=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev
OUT=${OUT:-/out}
rc=0
get(){  # $1 commit, $2 repo path, $3 expected sha256 of the file as committed, or COMMIT-ONLY
  local dest=/work/$(basename "$2") ok=0
  for k in 1 2 3 4 5; do
    if curl -fsSL --max-time 120 -o "$dest" "$GH/$1/$2"; then ok=1; break; fi
    echo "attempt $k for $2 failed"; sleep 20
  done
  [ $ok = 1 ] || { echo "FETCH FAIL $2"; rc=1; return; }
  local got
  got=$(sha256sum "$dest" | cut -d' ' -f1)
  if [ "$3" = COMMIT-ONLY ]; then
    echo "PIN COMMIT-ONLY $2 $got (commit ${1})"
  elif [ "$got" != "$3" ]; then
    echo "PIN FAIL $2: got $got want $3"; rc=1
  else
    echo "PIN OK $2 $got"
  fi
  sed -i 's/\r$//' "$dest"
  echo "fetched $2 at ${1:0:12} ($(stat -c %s "$dest") bytes)"
}
get $R_COMMIT rootless/ocipull.py         bb3230f0a211e1d9974ca65197f20863349f25c243c8c9fed841116a7df2b303
get $R_COMMIT rootless/delphi_rootless.sh b57b83c5fc514ea4904f806df332ff60d8af6d1c46f0f9d006971a9c75d40ab2
get $R_COMMIT rootless/delphi_env.sh      fe14fd968d99dd95e1fec20ffed658b8f30dab632cb367916e47c953748b4689
get $V_COMMIT val9293/run_val9293.sh      COMMIT-ONLY
grep -q '^VERSION=0.1.1' /work/delphi_rootless.sh || { echo "delphi_rootless.sh is not 0.1.1"; rc=1; }
grep -q 'mv2dimu-ntuple 0.3.0' /work/run_val9293.sh || { echo "run_val9293.sh does not require run_ntuple 0.3.0"; rc=1; }
{ echo "val9293 commit $V_COMMIT"; echo "rootless commit $R_COMMIT"; } > $OUT/sha256.txt
(cd /work && sha256sum ocipull.py delphi_rootless.sh delphi_env.sh run_val9293.sh inner_val9293.sh fetch.sh) \
   | tee -a $OUT/sha256.txt
echo "fetch rc=$rc"
exit $rc
