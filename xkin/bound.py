# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Munim, Inc. (MV2). Made with AI agents working in MV2's name.
"""bound.py: what ALEPH's muon-jet angle statement allows for a b-associated 30 GeV boson.

ALEPH (arXiv:1610.06536 v9, sec. 4.2, Fig. 16a) reports that "in all cases one of the two
muons from di-muons is closer than 15 degrees to one of the leading jets" (anti-kt jets built
without leptons, leading jet per thrust hemisphere; events where leading jets are defined).
xkin (PLAN section 4b) gives, per signal model, the fraction of signal events that would enter
that plot (f_defined) and the fraction of those with no muon within 15 degrees (f_away).

For a signal of N boson events, the number that would contradict ALEPH's statement is Poisson
with mean g N, g = f_defined * f_away. This script reports, per model, cut and jet radius:
  - the expected number of contradicting events if the fitted 32.31 events were all signal;
  - the 95 % CL upper limit on N given k_obs contradicting events (k_obs = 0 by default);
  - p_at_fit = P(at most k_obs | N = 32.31);
  - p_marginal = the same, averaged over ALEPH's fitted yield N ~ Normal(32.31, 10.87) cut at 0.
Generator level only; see NOTE-kinematics.md for the limits of this reading.
Pure standard library.
"""
import argparse
import json
import math

VERSION = "mv2 xkin-bound 0.1.0"
N_FIT = 32.31      # ALEPH fitted signal events (arXiv:1610.06536 v9)
S_FIT = 10.87      # its uncertainty
MODELS = ("V", "S", "P")
CUTS = ("p_cut", "pt_cut")
RS = ("R0.4", "R0.7", "R1.0")


def poisson_cdf(k, lam):
    """P(X <= k) for X ~ Poisson(lam)."""
    if lam < 0:
        raise ValueError("lam must be >= 0")
    if k < 0:
        return 0.0
    term = math.exp(-lam)
    s = term
    for i in range(1, int(k) + 1):
        term *= lam / i
        s += term
    return min(s, 1.0)


def poisson_ul(k, cl=0.95):
    """Classical one-sided upper limit on a Poisson mean after observing k."""
    alpha = 1.0 - cl
    lo, hi = 0.0, 1.0
    while poisson_cdf(k, hi) > alpha:
        hi *= 2.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if poisson_cdf(k, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def phi(z):
    """Standard normal CDF."""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def z_from_p(p):
    """One-sided significance z with phi(-z) = p."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    lo, hi = -40.0, 40.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if phi(-mid) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def marginal_p0(g, mu=N_FIT, sigma=S_FIT):
    """E[exp(-g N)] for N ~ Normal(mu, sigma) truncated to N >= 0 (closed form, k_obs = 0)."""
    if sigma <= 0:
        return math.exp(-g * mu)
    z = (mu - g * sigma ** 2) / sigma
    pz = phi(z)
    if pz <= 0.0:
        return 0.0
    return math.exp(-g * mu + 0.5 * (g * sigma) ** 2 + math.log(pz)) / phi(mu / sigma)


def marginal_p(k, g, mu=N_FIT, sigma=S_FIT, n=20000):
    """E[P(X <= k | g N)] for N ~ Normal(mu, sigma) truncated to N >= 0 (trapezoid rule)."""
    if sigma <= 0:
        return poisson_cdf(k, g * mu)
    hi = mu + 10.0 * sigma
    h = hi / n
    num = den = 0.0
    for i in range(n + 1):
        x = i * h
        w = math.exp(-0.5 * ((x - mu) / sigma) ** 2)
        c = 0.5 if i in (0, n) else 1.0
        num += c * w * poisson_cdf(k, g * x)
        den += c * w
    return num / den


def model_fractions(s, R):
    """s = summary['samples'][model][cut]; returns f_defined, f_away, g."""
    nwin = s["n_window"]
    d = s[R]
    if nwin <= 0 or d["f_amin_lt15"] is None:
        raise ValueError("empty window")
    f_def = d["n_defined"] / nwin
    f_away = 1.0 - d["f_amin_lt15"]
    return f_def, f_away, f_def * f_away


def bound_row(f_def, f_away, k_obs=0, n_fit=N_FIT, s_fit=S_FIT, cl=0.95):
    g = f_def * f_away
    if g <= 0:
        raise ValueError("g must be > 0")
    p_fit = poisson_cdf(k_obs, g * n_fit)
    p_marg = marginal_p(k_obs, g, n_fit, s_fit)
    row = dict(f_defined=round(f_def, 5), f_away=round(f_away, 5), g=round(g, 5),
               expected_away_at_fit=round(g * n_fit, 3),
               ul_boson_events=round(poisson_ul(k_obs, cl) / g, 3),
               p_at_fit=p_fit, z_at_fit=round(z_from_p(p_fit), 3) if 0 < p_fit < 1 else None,
               p_marginal=p_marg,
               z_marginal=round(z_from_p(p_marg), 3) if 0 < p_marg < 1 else None)
    if k_obs == 0:
        row["p_marginal_closed_form"] = marginal_p0(g, n_fit, s_fit)
    return row


def analyse(summary, k_obs=0, n_fit=N_FIT, s_fit=S_FIT):
    samples = summary["samples"]
    out = dict(tool=VERSION, made_by="MV2 of Munim, Inc. (made with AI agents)",
               source=summary.get("tool"), k_obs=k_obs, n_fit=n_fit, s_fit=s_fit, rows=[])
    for m in MODELS:
        for cut in CUTS:
            s = samples[m][cut]
            for R in RS:
                f_def, f_away, _ = model_fractions(s, R)
                row = dict(model=m, cut=cut, R=R, n_window=s["n_window"])
                row.update(bound_row(f_def, f_away, k_obs, n_fit, s_fit))
                out["rows"].append(row)
            # secondary reading: nearest jet above 3 GeV, every window event counted
            nj = s["nearest_jet_R0.4"]
            row = dict(model=m, cut=cut, R="nearest_R0.4_all_events", n_window=s["n_window"])
            row.update(bound_row(1.0, 1.0 - nj["f_min_lt15"], k_obs, n_fit, s_fit))
            out["rows"].append(row)
    if "bkg" in samples:
        b = samples["bkg"]["p_cut"]
        out["background_check"] = dict(
            n_window=b["n_window"], f_amin_lt15_R04=b["R0.4"]["f_amin_lt15"],
            median_aoth_R04=b["R0.4"]["median_aoth"], f_aoth_lt20_R04=b["R0.4"]["f_aoth_lt20"],
            f_both_gt20_nearest=b["nearest_jet_R0.4"]["f_both_gt20"])
    worst = max((r for r in out["rows"] if r["R"].startswith("R")),
                key=lambda r: r["ul_boson_events"])
    out["weakest_hemisphere_reading"] = dict(model=worst["model"], cut=worst["cut"],
                                             R=worst["R"], ul=worst["ul_boson_events"],
                                             p_marginal=worst["p_marginal"])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--summary", required=True, help="xkin summary.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--k-obs", type=int, default=0)
    a = ap.parse_args()
    with open(a.summary) as f:
        summary = json.load(f)
    res = analyse(summary, a.k_obs)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    print(VERSION)
    print("%-3s %-7s %-24s %7s %7s %7s %8s %8s %10s %6s" % (
        "mod", "cut", "R", "f_def", "f_away", "g", "exp@fit", "UL95", "p_marg", "z"))
    for r in res["rows"]:
        print("%-3s %-7s %-24s %7.4f %7.4f %7.4f %8.2f %8.2f %10.3g %6s" % (
            r["model"], r["cut"], r["R"], r["f_defined"], r["f_away"], r["g"],
            r["expected_away_at_fit"], r["ul_boson_events"], r["p_marginal"], r["z_marginal"]))
    if "background_check" in res:
        print("background:", json.dumps(res["background_check"]))


if __name__ == "__main__":
    main()
