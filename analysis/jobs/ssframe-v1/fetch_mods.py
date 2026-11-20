# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Fetch the published modules ssframe 0.1.0 builds on, next to this file.

aprime_smooth.py and aprime_slsm.py must be byte-identical to the files job aprime-slsm-v1 ran
(fatal otherwise). aprime_cross.py and dmcratio.py are checked against the sha256 job
dmcratio-v1 ran; sscontrol.py's sha256 is printed (it must be the file job sscontrol-v1 fetches;
gate P0 re-runs dmcratio-v1's closure through it). emuframe.py is fetched and blob-checked by
aprime_smooth.fetch_emuframe at run time."""
import hashlib
import os
import time
import urllib.request

BASE = "https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main/stats/"
HERE = os.path.dirname(os.path.abspath(__file__))
FATAL = {
    "aprime_smooth.py": "eae6510abcd327c385585095117e1fa3ba1cec8fa5e74aa9d605f230f0ed8d28",
    "aprime_slsm.py": "66225147496757840e59e3a29f810f13f70aca9573902aefb30b466aa419cb57",
}
SOFT = {
    "aprime_cross.py": "3161582977222cca65f826d9b92a58d5979ebd8dee6d359386757c4ea25a83ae",
    "dmcratio.py": "43f29aa86475952ef3b482591f4bee99017b789bf2eda2e73008bf22045b2a7c",
}

for name in ("aprime_smooth.py", "aprime_slsm.py", "aprime_cross.py", "dmcratio.py",
             "sscontrol.py"):
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
    if name in FATAL and h != FATAL[name]:
        raise SystemExit("%s sha256 %s is not the one aprime-slsm-v1 ran (%s)" % (name, h,
                                                                                 FATAL[name]))
    note = ""
    if name in FATAL:
        note = " (matches aprime-slsm-v1)"
    elif name in SOFT:
        note = " (matches dmcratio-v1)" if h == SOFT[name] else " (DIFFERS from %s)" % SOFT[name]
    with open(os.path.join(HERE, name), "wb") as f:
        f.write(data)
    print("fetched %s (%d bytes) sha256 %s%s" % (name, len(data), h, note), flush=True)
