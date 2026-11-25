#!/bin/bash
# dimu-ntuple-rl fetch 0.1.1 -- copy the committed DELPHI-route files into /work and record sha256.
# 0.1.1 (amendments 0.42 and 0.43): the analysis files still come from the SAME pinned commit as
# fetch 0.1.0 (5daccc46...); only the entry wrapper changes to delphi-rootless 0.1.1
# (delphi_rootless.sh + delphi_env.sh from commit 9f575600...). Entry files carry FATAL sha256 pins
# equal to the hashes printed by job delphi-rootless-probe-v2 (out/sha256.txt). The four analysis
# files had no hash printed by any earlier job, so they are pinned by the 40-character commit only
# (raw.githubusercontent.com at a commit sha serves that commit's content); their sha256 is printed
# here and recorded in the results (amendment 0.43, section 3).
# Used unchanged by dimu-ntuple-rl-v2 (amendment 0.44); v1 printed these analysis-file hashes:
# run_ntuple.sh b86eaecb..., mv2user02.car 24758ca8..., validate.py 485fffc7..., test_validate.py 7e704257...
# Part of the open DELPHI test of the ALEPH 30 GeV dimuon excess.
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
set -u
A_COMMIT=5daccc46608c7a47c577bdbaa974745778e7f2e9   # analysis files (unchanged from fetch 0.1.0)
R_COMMIT=9f575600c13bd0fc30e532c1bbd1736012d87996   # delphi-rootless 0.1.1
GH=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev
OUT=${OUT:-/out}
rc=0
get(){  # $1 commit, $2 repo path, $3 expected sha256 of the file as committed
  local dest=/work/$(basename "$2") ok=0
  for k in 1 2 3 4 5; do
    if curl -fsSL --max-time 120 -o "$dest" "$GH/$1/$2"; then ok=1; break; fi
    echo "attempt $k for $2 failed"; sleep 20
  done
  [ $ok = 1 ] || { echo "FETCH FAIL $2"; rc=1; return; }
  local got
  got=$(sha256sum "$dest" | cut -d' ' -f1)
  if [ "$got" != "$3" ]; then
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
# v2: the analysis files are now pinned by the sha256 that v1 printed (FATAL on any difference).
get $A_COMMIT ntuple/run_ntuple.sh        b86eaecb193ba6a75355ff51089f17e29a4ddc379cff1d156b9302e80704c5e2
get $A_COMMIT ntuple/mv2user02.car        24758ca8080335b3b320f99e4b293c87e2a6134a246d2c3bb188b6677b3ae5f3
get $A_COMMIT ntuple/validate.py          485fffc76543c8680b5208b2b7622eb2327eab91623f5c202e6b5082c12d4d0f
get $A_COMMIT ntuple/test_validate.py     7e70425787fe5bd3c0fa39503c4459b38283080e6553ab90cb788059fa5ccc2b
grep -q '^VERSION=0.1.1' /work/delphi_rootless.sh || { echo "delphi_rootless.sh is not 0.1.1"; rc=1; }
grep -q '^set +u' /work/run_ntuple.sh || { echo "run_ntuple.sh lacks the set +u guard around profile sourcing"; rc=1; }
grep -q '^XRDFIX_VERSION=0.1.0' /work/xrdfix.sh || { echo "xrdfix.sh is not 0.1.0"; rc=1; }
{ echo "analysis commit $A_COMMIT"; echo "rootless commit $R_COMMIT"; } > $OUT/sha256.txt
(cd /work && sha256sum ocipull.py delphi_rootless.sh delphi_env.sh run_ntuple.sh mv2user02.car \
   validate.py test_validate.py inner_ntuple.sh fetch.sh xrdfix.sh) | tee -a $OUT/sha256.txt
echo "fetch rc=$rc"
exit $rc
