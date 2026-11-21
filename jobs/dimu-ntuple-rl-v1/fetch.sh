#!/bin/bash
# dimu-ntuple-rl fetch 0.1.0 -- copy the committed DELPHI-route files into /work from ONE pinned
# commit of github.com/munimtechnologies/delphi-dimuon-30gev (content-addressed), and record sha256.
# Part of the open DELPHI test of the ALEPH 30 GeV dimuon excess (PLAN amendment 0.35).
# MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
set -u
COMMIT=${COMMIT:-5daccc46608c7a47c577bdbaa974745778e7f2e9}
BASE=https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/$COMMIT
OUT=${OUT:-/out}
rc=0
for p in rootless/ocipull.py rootless/delphi_rootless.sh \
         ntuple/run_ntuple.sh ntuple/mv2user02.car ntuple/validate.py ntuple/test_validate.py; do
  dest=/work/$(basename "$p")
  ok=0
  for k in 1 2 3 4 5; do
    if curl -fsSL --max-time 120 -o "$dest" "$BASE/$p"; then ok=1; break; fi
    echo "attempt $k for $p failed"; sleep 20
  done
  [ $ok = 1 ] || { echo "FETCH FAIL $p"; rc=1; continue; }
  sed -i 's/\r$//' "$dest"
  echo "fetched $p ($(stat -c %s "$dest") bytes)"
done
echo "commit $COMMIT" > $OUT/sha256.txt
(cd /work && sha256sum ocipull.py delphi_rootless.sh run_ntuple.sh mv2user02.car validate.py \
   test_validate.py inner_ntuple.sh fetch.sh) | tee -a $OUT/sha256.txt
exit $rc
