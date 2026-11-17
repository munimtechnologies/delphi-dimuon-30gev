#!/usr/bin/env python3
"""lep4f: what the published LEP1 four-fermion (mu+ mu- q qbar) counts say about the ALEPH 30 GeV
dimuon excess (arXiv:1610.06536).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

If the 32.31 b-tagged events that arXiv:1610.06536 fits at 30.40 GeV were a boson X made in
Z -> b bbar X, X -> mu+ mu-, ALEPH's own numbers fix the rate of such events with both muons inside
ALEPH's acceptance, per produced hadronic Z decay (analysis/nexp.py's R_A times A_gen):

    R_acc = N_sig / (N_had,A / eff_had,A) / (eff_mu,A^2 * eff_b,A)
          = 5.90e-5 (N_had,A = 1.9M, "nominal")  or  5.09e-5 (2.2M, "low")

In 92-95 % of such events both muons lie more than 20 degrees from every jet above 3 GeV (xkin-v1,
NOTE-kinematics.md). That is the topology the LEP1 four-fermion analyses selected: two
identified leptons isolated from the hadronic jets. Each experiment's published mu mu q qbar
count would then contain

    N_X = mu * R_acc * N_Z,exp * eps_exp

boson events, where eps_exp is that analysis' efficiency for such an event (muon identification,
isolation, momentum and quality cuts). eps_exp was never published for this topology. Given the
observed count n and the Standard Model expectation b, a 95 % CLs upper limit s_up on extra
events gives

    eps_max = s_up / (R_acc * N_Z,exp)

the largest efficiency at which an ALEPH-sized boson (mu = 1) is still allowed. Above eps_max the
published count excludes it. Inputs: hep-ex/9611015 table 1 (counts) and the experiments'
abstracts (hadronic Z counts); see EXPTS.

Statistics: CLs = P(N <= n | s + b) / P(N <= n | b), with b smeared by a Gaussian of relative width
rel (truncated at b >= 0, Cousins-Highland), integrated on a fixed 41-point grid over +-5 sigma.
"""
import argparse
import json
import math
import sys

VERSION = "mv2 lep4f 0.1.0"

# ALEPH 30 GeV excess inputs, identical to analysis/nexp.py 0.2.0 (test_lep4f checks agreement)
ALEPH_N_SIG = 32.31
ALEPH_N_SIG_ERR = 10.87
ALEPH_N_HAD = {"nominal": 1.9e6, "low": 2.2e6}
ALEPH_EFF_HAD = 0.9748
ALEPH_EFF_MU = 0.86
ALEPH_EFF_B = 0.38
READINGS = ("nominal", "low")

L3_Z_PER_PB = 960000.0 / 36.0   # L3, Phys. Lett. B 321 (1994) 283: 36 pb-1 = 960,000 hadronic Z

# Published LEP1 mu+ mu- q qbar results. n_obs and b (SM signal + background expected) as listed
# in hep-ex/9611015 table 1 ("upper line ... expected ... signal + background, lower line ...
# observations"); ALEPH 13 + 0, OPAL 20 + 8, L3 5 + 0.
EXPTS = {
    "ALEPH": dict(ref="Z. Phys. C 66 (1995) 3, data 1989-93", lumi_pb=79.0, n_z=2.0e6,
                  n_z_note="'almost two million hadronic Z decays' (abstract)",
                  n_obs=19, b=13.0),
    "OPAL": dict(ref="Phys. Lett. B 376 (1996) 315", lumi_pb=132.4, n_z=132.4 * L3_Z_PER_PB,
                 n_z_note="not in the abstract; 132.4 pb-1 scaled with L3's 960,000 per 36 pb-1",
                 n_obs=28, b=28.0),
    "L3": dict(ref="Phys. Lett. B 321 (1994) 283", lumi_pb=36.0, n_z=9.6e5,
               n_z_note="'960 000 hadronic Z decays' (abstract)", n_obs=6, b=5.0),
}
B_REL_UNC = 0.10   # hep-ex/9611015: residual uncertainties of the predictions "of the order of 10%"
_NODES = 41
_WIDTH = 5.0


def rate_acc(reading="nominal", n_sig=ALEPH_N_SIG):
    """Boson events with both muons in ALEPH's acceptance per produced hadronic Z (mu = 1)."""
    if reading not in ALEPH_N_HAD:
        raise ValueError("reading must be one of %s" % (READINGS,))
    n_z = ALEPH_N_HAD[reading] / ALEPH_EFF_HAD
    return n_sig / n_z / (ALEPH_EFF_MU * ALEPH_EFF_MU * ALEPH_EFF_B)


def pois_cdf(n, lam):
    """P(N <= n) for a Poisson mean lam >= 0."""
    if n < 0:
        return 0.0
    if lam <= 0.0:
        return 1.0
    ll = math.log(lam)
    return min(1.0, sum(math.exp(k * ll - lam - math.lgamma(k + 1.0)) for k in range(int(n) + 1)))


def cdf_smeared(n, s, b, rel=0.0):
    """P(N <= n | s + b'), b' = b (1 + rel x), x standard normal truncated so that b' >= 0."""
    if rel <= 0.0 or b <= 0.0:
        return pois_cdf(n, s + b)
    num = den = 0.0
    for i in range(_NODES):
        x = -_WIDTH + 2.0 * _WIDTH * i / (_NODES - 1)
        bb = b * (1.0 + rel * x)
        if bb < 0.0:
            continue
        w = math.exp(-0.5 * x * x)
        num += w * pois_cdf(n, s + bb)
        den += w
    return num / den


def cls(n, s, b, rel=0.0):
    return cdf_smeared(n, s, b, rel) / cdf_smeared(n, 0.0, b, rel)


def cls_upper(n, b, rel=0.0, cl=0.95):
    """95 % CLs upper limit on extra (signal) events, by bisection (CLs falls with s)."""
    alpha = 1.0 - cl
    p0 = cdf_smeared(n, 0.0, b, rel)
    f = lambda s: cdf_smeared(n, s, b, rel) / p0 - alpha
    lo, hi = 0.0, max(10.0, 2.0 * n + 10.0)
    while f(hi) > 0.0:
        hi *= 2.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def predicted(n_z, reading="nominal", n_sig=ALEPH_N_SIG):
    """Boson events in acceptance that an ALEPH-sized signal puts into n_z hadronic Z decays."""
    return rate_acc(reading, n_sig) * n_z


def row(n_obs, b, n_z, rel):
    s_up = cls_upper(n_obs, b, rel)
    out = {"n_obs": n_obs, "b": b, "rel_b_unc": rel, "s_up_95": s_up, "n_z": n_z}
    for rd in READINGS:
        pr = predicted(n_z, rd)
        pr_m1 = predicted(n_z, rd, ALEPH_N_SIG - ALEPH_N_SIG_ERR)
        out[rd] = {"n_x_if_eps_1": pr,
                   "eps_max": s_up / pr,
                   "eps_max_aleph_minus_1sigma": s_up / pr_m1,
                   "mu_max_eps_0.3": s_up / (0.3 * pr),
                   "mu_max_eps_0.5": s_up / (0.5 * pr)}
    return out


def table(rels=(0.0, B_REL_UNC)):
    res = {"tool": VERSION, "made_by": "MV2 of Munim, Inc. (made with AI agents)",
           "rate_acc": {rd: rate_acc(rd) for rd in READINGS}, "experiments": {}, "combined": {}}
    for rel in rels:
        key = "rel_%g" % rel
        for name, e in EXPTS.items():
            res["experiments"].setdefault(name, {"ref": e["ref"], "n_z_note": e["n_z_note"]})[key] = \
                row(e["n_obs"], e["b"], e["n_z"], rel)
        # one common efficiency for all three selections (a simplification, labelled as such)
        n = sum(e["n_obs"] for e in EXPTS.values())
        b = sum(e["b"] for e in EXPTS.values())
        nz = sum(e["n_z"] for e in EXPTS.values())
        res["combined"][key] = row(n, b, nz, rel)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    res = table()
    txt = json.dumps(res, indent=1)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(txt)
    print(txt)
    print("\n%-9s %-6s %4s %6s %7s | %9s %8s | %9s %8s" % (
        "expt", "b_unc", "n", "b", "s_up", "NX(eps=1)", "eps_max", "NX low", "eps_low"))
    for rel in (0.0, B_REL_UNC):
        key = "rel_%g" % rel
        rows = [(k, v[key]) for k, v in res["experiments"].items()] + [("combined", res["combined"][key])]
        for name, r in rows:
            print("%-9s %-6s %4d %6.1f %7.2f | %9.1f %8.4f | %9.1f %8.4f" % (
                name, key, r["n_obs"], r["b"], r["s_up_95"], r["nominal"]["n_x_if_eps_1"],
                r["nominal"]["eps_max"], r["low"]["n_x_if_eps_1"], r["low"]["eps_max"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
