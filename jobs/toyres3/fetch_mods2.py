# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""Second (final) resume of the ssframe toy calibration (PLAN amendment 0.38, under the stopping
rule of amendment 0.32 sec. 3). Fetches, next to this file:

* stats/toyresume.py and stats/test_toyresume.py, and the modules and readings job
  toyres-ssframe-v1 ran, each required to have the sha256 that job printed (fatal otherwise);
* the merged 934-toy prefix of toyres-ssframe-v1 (committed to
  analysis/results/ssframe/toyres-v1-partial/toys.csv in the same run as this file; retried for up
  to one hour in case the commit lands after the job starts), saved as prior-ssframe.csv.

emuframe.py is fetched and blob-checked by aprime_smooth.fetch_emuframe at run time, as before.

    python fetch_mods2.py
"""
import hashlib
import os
import time
import urllib.request

REPO = "https://raw.githubusercontent.com/munimtechnologies/delphi-dimuon-30gev/main/"
HERE = os.path.dirname(os.path.abspath(__file__))
FATAL = {   # from /out/sha256.txt of toyres-ssframe-v1
    "stats/toyresume.py": "1fa929d029d77935eaf63ad82429c4610c9bebe47e3c13c25a258d404308a6b9",
    "stats/test_toyresume.py": "3394ee93aa50479dead2c7454651e347e663ddfcd2cc9419951bd18e8d4b36b4",
    "stats/aprime_smooth.py": "eae6510abcd327c385585095117e1fa3ba1cec8fa5e74aa9d605f230f0ed8d28",
    "stats/aprime_slsm.py": "66225147496757840e59e3a29f810f13f70aca9573902aefb30b466aa419cb57",
    "stats/ssframe.py": "f1bb30e0de34300e95cb246a3494ac2083b543cd8a21623eb6a8b004a7d22125",
    "stats/sscontrol.py": "f5001810421ef6875bbe0146a6eb0eb140319d7805522557036da9c8f3d7638a",
    "stats/dmcratio.py": "43f29aa86475952ef3b482591f4bee99017b789bf2eda2e73008bf22045b2a7c",
    "stats/aprime_cross.py": "3161582977222cca65f826d9b92a58d5979ebd8dee6d359386757c4ea25a83ae",
    "data/aleph-fig5.json": "f535d924111e215b71f6a308e6c228cead13680512498517680863b05b7ee626",
    "data/aleph-dmc21.json": "c0b79dafbc25bc0f0e204f657a95d2c47bc05afd4f6758df312cfaa8d12cc1ba",
    "data/aleph-emu3.json": "f6fe3249c303e07b475487c33e9a8e20e5f1778d7b0abba8bfa7f77810a7c984",
}
PRIOR = ("analysis/results/ssframe/toyres-v1-partial/toys.csv", "prior-ssframe.csv", 934)


def get(path, tries, wait):
    for k in range(tries):
        try:
            return urllib.request.urlopen(REPO + path, timeout=60).read()
        except Exception as exc:
            print("attempt %d for %s failed: %s" % (k + 1, path, exc), flush=True)
            time.sleep(wait)
    raise SystemExit("could not fetch " + path)


def main():
    for path, want in FATAL.items():
        data = get(path, 10, 30)
        h = hashlib.sha256(data).hexdigest()
        if h != want:
            raise SystemExit("%s sha256 %s is not the one toyres-ssframe-v1 ran (%s)" % (
                path, h, want))
        with open(os.path.join(HERE, os.path.basename(path)), "wb") as f:
            f.write(data)
        print("fetched %s (%d bytes) sha256 %s (matches)" % (path, len(data), h), flush=True)
    path, local, rows = PRIOR
    data = None
    for k in range(60):
        try:
            got = urllib.request.urlopen(REPO + path, timeout=60).read()
        except Exception as exc:
            print("prior toys not there yet (%s); waiting 60 s" % exc, flush=True)
            time.sleep(60)
            continue
        n = len([l for l in got.decode().splitlines()[1:] if l.strip()])
        if n == rows:
            data = got
            break
        print("prior toys have %d rows, want %d; waiting 60 s" % (n, rows), flush=True)
        time.sleep(60)
    if data is None:
        raise SystemExit("prior toys %s never appeared with %d rows" % (path, rows))
    with open(os.path.join(HERE, local), "wb") as f:
        f.write(data)
    print("fetched %s -> %s (%d rows, %d bytes) sha256 %s" % (
        path, local, rows, len(data), hashlib.sha256(data).hexdigest()), flush=True)


if __name__ == "__main__":
    main()
