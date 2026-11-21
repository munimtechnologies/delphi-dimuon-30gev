# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Fetch, next to this file, the exact published modules and readings that jobs aprime-slsm-v2
and ssframe-v1 ran (sha256 must match, fatal otherwise), and the saved toy prefixes of those two
jobs (committed to analysis/results/ in the same run as this file; retried for up to 1 hour in
case the commit lands after the job starts). emuframe.py is fetched and blob-checked by
aprime_smooth.fetch_emuframe at run time.

    python fetch_mods.py slsm|ssframe
"""
import hashlib
import os
import sys
import time
import urllib.request

REPO = "https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main/"
HERE = os.path.dirname(os.path.abspath(__file__))
FATAL = {   # from /out/sha256.txt of aprime-slsm-v2 and ssframe-v1
    "stats/aprime_smooth.py": "eae6510abcd327c385585095117e1fa3ba1cec8fa5e74aa9d605f230f0ed8d28",
    "stats/aprime_slsm.py": "66225147496757840e59e3a29f810f13f70aca9573902aefb30b466aa419cb57",
    "stats/slsm_chunk.py": "3b27243a9d8a40af5760d4171fda8b87243b8fa030ca938b67e4ba0aaa9c2009",
    "stats/ssframe.py": "f1bb30e0de34300e95cb246a3494ac2083b543cd8a21623eb6a8b004a7d22125",
    "stats/sscontrol.py": "f5001810421ef6875bbe0146a6eb0eb140319d7805522557036da9c8f3d7638a",
    "stats/dmcratio.py": "43f29aa86475952ef3b482591f4bee99017b789bf2eda2e73008bf22045b2a7c",
    "stats/aprime_cross.py": "3161582977222cca65f826d9b92a58d5979ebd8dee6d359386757c4ea25a83ae",
    "data/aleph-fig5.json": "f535d924111e215b71f6a308e6c228cead13680512498517680863b05b7ee626",
    "data/aleph-dmc21.json": "c0b79dafbc25bc0f0e204f657a95d2c47bc05afd4f6758df312cfaa8d12cc1ba",
    "data/aleph-emu3.json": "f6fe3249c303e07b475487c33e9a8e20e5f1778d7b0abba8bfa7f77810a7c984",
}
PRIOR = {"slsm": ("analysis/results/aprime-slsm/v2-partial/toys.csv", "prior-slsm.csv", 869),
         "ssframe": ("analysis/results/ssframe/v1-partial/toys.csv", "prior-ssframe.csv", 309)}


def get(path, tries, wait):
    for k in range(tries):
        try:
            return urllib.request.urlopen(REPO + path, timeout=60).read()
        except Exception as exc:
            print("attempt %d for %s failed: %s" % (k + 1, path, exc), flush=True)
            time.sleep(wait)
    raise SystemExit("could not fetch " + path)


def main(kind):
    for path, want in FATAL.items():
        data = get(path, 10, 30)
        h = hashlib.sha256(data).hexdigest()
        if h != want:
            raise SystemExit("%s sha256 %s is not the one the stopped jobs ran (%s)" % (
                path, h, want))
        with open(os.path.join(HERE, os.path.basename(path)), "wb") as f:
            f.write(data)
        print("fetched %s (%d bytes) sha256 %s (matches)" % (path, len(data), h), flush=True)
    path, local, rows = PRIOR[kind]
    for k in range(60):
        data = None
        try:
            data = urllib.request.urlopen(REPO + path, timeout=60).read()
        except Exception as exc:
            print("prior toys not there yet (%s); waiting 60 s" % exc, flush=True)
            time.sleep(60)
            continue
        n = len([l for l in data.decode().splitlines()[1:] if l.strip()])
        if n == rows:
            break
        print("prior toys have %d rows, want %d; waiting 60 s" % (n, rows), flush=True)
        data = None
        time.sleep(60)
    if data is None:
        raise SystemExit("prior toys %s never appeared with %d rows" % (path, rows))
    with open(os.path.join(HERE, local), "wb") as f:
        f.write(data)
    print("fetched %s -> %s (%d rows, %d bytes) sha256 %s" % (
        path, local, rows, len(data), hashlib.sha256(data).hexdigest()), flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "slsm")
