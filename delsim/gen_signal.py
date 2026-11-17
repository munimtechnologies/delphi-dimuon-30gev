#!/usr/bin/env python3
"""gen_signal: write xkin signal events (V: vector boson radiated off the b line, m = 30.40 GeV,
Gamma = 1.78 GeV, X -> mu+ mu-, Pythia 8 hadronisation) as DELSIM external-generator input.

Uses run_xkin.run_signal from the public repo (xkin/), so the events are the same model as the
generator-level kinematic study. Also records generator-level acceptance of the ALEPH-like cuts.

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="V", choices=["V", "S", "P"])
    ap.add_argument("--n", type=int, default=460)
    ap.add_argument("--seed", type=int, default=30401)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import run_xkin
    os.makedirs(a.out, exist_ok=True)
    tmp = "/tmp/gen_%s" % a.model
    os.makedirs(tmp, exist_ok=True)
    t0 = time.time()
    model, rows, stats = run_xkin.run_signal(a.model, a.n, a.seed, tmp, a.out, 0, a.n)
    res = {"tool": "mv2 gen_signal 0.1.0", "model": model, "n_requested": a.n, "seed": a.seed,
           "stats": stats, "wall_s": round(time.time() - t0, 1)}
    try:
        res["gen_level_p_cut"] = run_xkin.summarise(rows, False)
    except Exception as e:  # diagnostics only
        res["gen_level_error"] = repr(e)
    with open(os.path.join(a.out, "gen_stats.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    print("GEN_JSON_BEGIN")
    print(json.dumps(res, indent=1, default=str))
    print("GEN_JSON_END")
    fad = stats.get("fadgen", {}) if isinstance(stats, dict) else {}
    print("FADGEN_EVENTS %s" % fad.get("written", 0))
    if not fad.get("written"):
        sys.exit(2)


if __name__ == "__main__":
    main()
