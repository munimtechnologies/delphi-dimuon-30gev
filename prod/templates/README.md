# Production job templates (plan section 4h) -- NOT filed yet

Filed only after validation run 1 (V1-V5) passes. MV2 of Munim, Inc.; made with AI agents;
Apache-2.0. Copy `prod/run_prod.sh` into the job workdir; set REF to the commit SHA of the code
that passed validation, so every slice of one pass runs identical code.

Common job.json fields:
```
"kind": "compete", "image": "gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd",
"setup": ["id; command -v python3 curl git || true"], "network": true, "data_urls": [],
"data_key": "none", "cpu": 2, "memory_gb": 2, "timeout_minutes": <from dimu-ntuple-v1 per-file timing x files x 1.5>
"run": ["sed 's/\\r$//' /work/run_prod.sh > /tmp/run_prod.sh && REF=<sha> OUT=/out <switches> bash /tmp/run_prod.sh"]
```

| job name | switches |
|---|---|
| dimu-y94s01-v1 ... dimu-y94s08-v1 | DATA_DIRS="Y13709 Y13710" DATA_STRIDE=1 NDATA=54 DATA_START=1,55,109,163,217,271,325,379 NMC=0 PERIOD=y94 SLICE=y94sNN |
| dimu-y95s01-v1 ... dimu-y95s05-v1 | DATA_DIRS=Y13716 DATA_STRIDE=1 NDATA=50 DATA_START=1,51,101,151,201 NMC=0 PERIOD=y95 SLICE=y95sNN |
| dimu-y94mc01-v1 ... | NDATA=0 MC_VERSION=v94c MC_STRIDE=1 NMC=40 MC_START=1,41,... PERIOD=y94 SLICE=y94mcNN |
| dimu-y92s01-v1 ... y92s04 (only if F1 and W1-W5 say so) | DATA_DIRS=Y13723 DATA_STRIDE=1 NDATA=43 DATA_START=1,44,87,130 NMC=0 PERIOD=y92 |
| dimu-y93s01-v1 ... y93s04 (same condition) | DATA_DIRS=Y12340 DATA_STRIDE=1 NDATA=46 DATA_START=1,47,93,139 NMC=0 PERIOD=y93 |

The 1994 list is 429 files: slice 8 (DATA_START=379, NDATA=54) reaches past the end. That is
safe: run_ntuple.sh 0.3.0 selects files with `awk 'NR >= s && (NR - s) % k == 0' | head -$NDATA`,
which simply yields the last 51 files. Confirm the list length in dimu-ntuple-v1's stdout
(Y13709 + Y13710 together) before filing, and that slices 1-8 cover every file exactly once.
