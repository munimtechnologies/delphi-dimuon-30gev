# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Fetch the published stats/abtag.py 0.1.0 (amendment 0.31 sec. 3), stats/aprime_cross.py 0.1.0
and stats/dmcratio.py 0.1.0 (checked against the sha256 that jobs dmcratio-v1 and sscontrol-v1
ran), their tests, and stats/emuframe.py, stats/aprime_ext.py (for test_aprime_cross's
cross-check) next to this file. A sha256 mismatch is reported, not fatal: gate A0 re-runs C0 and
sscontrol-v1's same-sign slope."""
import hashlib
import os
import time
import urllib.request

BASE = "https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main/stats/"
HERE = os.path.dirname(os.path.abspath(__file__))
WANT = {"aprime_cross.py": "3161582977222cca65f826d9b92a58d5979ebd8dee6d359386757c4ea25a83ae",
        "test_aprime_cross.py": "6611916124829b485c5a09c913bd1a3aab51392a5c4bb1cd22943aef9e15498b",
        "dmcratio.py": "43f29aa86475952ef3b482591f4bee99017b789bf2eda2e73008bf22045b2a7c",
        "test_dmcratio.py": "e25f59d19fc1a8be0a88bbfcc153d33a3788307307a34dc3af814f206d4efcbf"}

for name in ("abtag.py", "test_abtag.py", "aprime_cross.py", "test_aprime_cross.py",
             "emuframe.py", "aprime_ext.py", "dmcratio.py", "test_dmcratio.py"):
    data = None
    for k in range(10):
        try:
            data = urllib.request.urlopen(BASE + name, timeout=60).read()
            break
        except Exception as exc:
            print("attempt %d for %s failed: %s" % (k + 1, name, exc), flush=True)
            time.sleep(30)
    if data is None:
        raise SystemExit("could not fetch " + name)
    h = hashlib.sha256(data).hexdigest()
    note = ""
    if name in WANT:
        note = " (matches sscontrol-v1)" if h == WANT[name] else " (DIFFERS from %s)" % WANT[name]
    with open(os.path.join(HERE, name), "wb") as f:
        f.write(data)
    print("fetched %s (%d bytes) sha256 %s%s" % (name, len(data), h, note), flush=True)
