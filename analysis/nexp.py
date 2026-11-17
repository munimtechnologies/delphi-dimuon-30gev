#!/usr/bin/env python3
"""nexp: the expected signal of an ALEPH-sized 30 GeV boson in DELPHI (PLAN v0.11, section 5f).

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. Apache-2.0.

"ALEPH-sized" (mu = 1 in tests A and B) means: the signal rate per produced hadronic Z decay that
ALEPH's fitted 32.31 events imply, given ALEPH's efficiencies, times the number of hadronic Z
decays DELPHI produced, times DELPHI's efficiency for the same signal model. Written out:

    R_A    = N_sig,A / (N_had,A / eff_had,A) / eff_sig,A
    eff_sig,A = A_gen * eff_mu,A^2 * eff_b,A            (A_gen: generator-level acceptance)
    N_Z,D  = N_had,D / eff_had,D                        (per period; eff_had,D from KK2f q qbar
                                                          simulation through the same selection)
    S_D    = R_A * N_Z,D * eff_sel,D                    (signal pairs passing every dimusel cut
                                                          before the b-tag; eff_sel,D from
                                                          sigana 0.3.0 "dimusel_exact")
    N_T    = S_D * eps_D                                (eps_D: data b efficiency at the WP, 4g)
    N_U    = N_T * (1 - eps_D * rho) / (eps_D * rho)    (test B, rho = max(1, rho_D))

Both hadronic efficiencies must be divided out. DELPHI's hadronic selection includes a thrust-axis
cut (|cos theta_T| <= 0.866) that keeps only about 85 % of hadronic Z decays, so DELPHI's hadronic
count is NOT the number of Z decays it produced. Plan v0.10 multiplied DELPHI's hadronic count by
an efficiency ratio and so mixed these normalisations (review 2026-11-17-nexp-normalisation.md).

ALEPH's hadronic selection applied to the SIGNAL events (at least five good tracks, charged energy
above 15 % of sqrt(s)) is taken as fully efficient once A_gen's own cuts (at least 5 charged, both
muons p > 2.5 GeV, abs(cos theta) < 0.95, dimuon mass 15-50 GeV) are passed. If it were h < 1, R_A
would be too small by the factor h and mu = 1 slightly smaller than ALEPH-sized, which can only
make EXCLUDED harder to reach (review 2026-11-17-forecast-k-r.md).

ALEPH normalisation ambiguity: arXiv:1610.06536 reports about 1.9M hadronic events after its
selection where about 2.2M were expected ("has to be double checked with ALEPH experts"). If the
shortfall is a loss that ordinary hadronic events suffer but the signal does not, R_A is too large
by 2.2/1.9. Both readings are computed: "nominal" (N_had,A = 1.9M) and "low" (2.2M). A result
is labelled EXCLUDED or COMPATIBLE only if it holds under both readings (combined_label).

New in 0.2.0: forecast_kr gives the k and r that stats/forecast.py and stats/combcast.py (PLAN 5c,
5e) must use when they are re-run with measured inputs, so that their N_exp = 32.31 k r equals
this module's nominal N_T exactly. k is a ratio of SELECTED hadronic counts (ALEPH's 1457
background pairs were found among its 1.9M selected events), and r is then the ratio of signal
efficiencies per selected hadronic event:
    r = (eff_sel,D * eps_D / eff_had,D) / (eff_sig,A / eff_had,A)
(N_had-weighted over periods). The forecast's background, 1457 k r, then carries exactly one
assumption: that DELPHI's background efficiency relative to ALEPH's equals r.
"""
import argparse
import json
import sys

VERSION = "mv2 nexp 0.2.0"

ALEPH_N_SIG = 32.31            # arXiv:1610.06536 v9, fitted signal events (15-50 GeV, b-tagged)
ALEPH_N_SIG_ERR = 10.87
ALEPH_N_HAD = {"nominal": 1.9e6,   # hadronic events after ALEPH's selection (sec. 2.2)
               "low": 2.2e6}       # the number the paper says was expected (footnote 1)
ALEPH_EFF_HAD = 0.9748         # ALEPH charged-track hadronic selection (hep-ex/9904007 table 1)
ALEPH_EFF_MU = 0.86            # average muon identification efficiency (1610.06536)
ALEPH_EFF_B = 0.38             # b efficiency of ALEPH's tag (1610.06536 sec. 3.2)
READINGS = ("nominal", "low")
LABELS = ("EXCLUDED", "COMPATIBLE", "INCONCLUSIVE")


def aleph_eff_sig(a_gen, eff_mu=ALEPH_EFF_MU, eff_b=ALEPH_EFF_B):
    """ALEPH's efficiency for the signal model: generator-level acceptance x muon ID^2 x b-tag."""
    if not 0.0 < a_gen <= 1.0:
        raise ValueError("generator-level acceptance must be in (0, 1]: %r" % (a_gen,))
    return a_gen * eff_mu * eff_mu * eff_b


def rate_per_z(a_gen, reading="nominal", n_sig=ALEPH_N_SIG, n_had=None,
               eff_had=ALEPH_EFF_HAD, eff_mu=ALEPH_EFF_MU, eff_b=ALEPH_EFF_B):
    """R_A: signal events (X -> mu mu, any acceptance) per produced hadronic Z implied by ALEPH."""
    if n_had is None:
        if reading not in ALEPH_N_HAD:
            raise ValueError("reading must be one of %s" % (READINGS,))
        n_had = ALEPH_N_HAD[reading]
    n_z = n_had / eff_had
    return n_sig / n_z / aleph_eff_sig(a_gen, eff_mu, eff_b)


def n_z_delphi(n_had_data, n_had_mc, n_events_mc):
    """Produced hadronic Z decays in one DELPHI period, and the hadronic-selection efficiency
    measured on KK2f Z -> q qbar simulation passed through the same dimusel selection."""
    if n_events_mc <= 0 or not 0 < n_had_mc <= n_events_mc:
        raise ValueError("need 0 < n_had_mc <= n_events_mc")
    eff = n_had_mc / n_events_mc
    return n_had_data / eff, eff


def period_yields(p, rate, rho=1.0):
    """Expected signal in one period. p: dict with n_had_data, n_had_mc, n_events_mc,
    eff_sel (signal, dimusel_exact, before the tag) and eps (data b efficiency at the WP)."""
    eps = p["eps"]
    if not 0.0 < eps < 1.0:
        raise ValueError("eps must be in (0, 1)")
    if rho < 1.0:
        raise ValueError("rho is max(1, rho_D), never below 1")
    if eps * rho >= 1.0:
        raise ValueError("eps * rho must be below 1 (eps=%g, rho=%g)" % (eps, rho))
    if not 0.0 < p["eff_sel"] <= 1.0:
        raise ValueError("eff_sel must be in (0, 1]")
    n_z, eff_had = n_z_delphi(p["n_had_data"], p["n_had_mc"], p["n_events_mc"])
    s = rate * n_z * p["eff_sel"]
    n_t = s * eps
    n_u = n_t * (1.0 - eps * rho) / (eps * rho)
    return {"n_z": n_z, "eff_had": eff_had, "s_before_tag": s, "n_t": n_t, "n_u": n_u}


def totals(periods, a_gen, rho=1.0, readings=READINGS, **aleph):
    """Sum the expected signal over periods (dict label -> period dict) for each ALEPH reading."""
    if not periods:
        raise ValueError("no periods")
    out = {"tool": VERSION, "a_gen": a_gen, "rho": rho, "readings": {}}
    for rd in readings:
        rate = rate_per_z(a_gen, rd, **aleph)
        per = {lab: period_yields(p, rate, rho) for lab, p in sorted(periods.items())}
        out["readings"][rd] = {
            "rate_per_z": rate,
            "periods": per,
            "n_t": sum(v["n_t"] for v in per.values()),
            "n_u": sum(v["n_u"] for v in per.values()),
        }
    return out


def forecast_kr(periods, a_gen):
    """k and r for stats/forecast.py and stats/combcast.py (PLAN 5c, 5e) re-run with measured
    inputs. k = sum of DELPHI's selected hadronic counts / ALEPH's 1.9M selected events (the sample
    in which ALEPH's 1457 background pairs were found); r = nominal N_T / (32.31 k), so that the
    forecast's N_exp = 32.31 k r equals N_T exactly. Under the "low" reading the forecast limits
    are multiplied by mu_low_from_nominal(1), as in 5f; k is NOT changed (the background lives in
    the selected sample either way)."""
    t = totals(periods, a_gen, readings=("nominal",))
    n_had = sum(float(p["n_had_data"]) for p in periods.values())
    if n_had <= 0:
        raise ValueError("no selected hadronic events")
    k = n_had / ALEPH_N_HAD["nominal"]
    n_t = t["readings"]["nominal"]["n_t"]
    r = n_t / (ALEPH_N_SIG * k)
    per_r = {}
    for lab, p in sorted(periods.items()):
        _, eff_had = n_z_delphi(p["n_had_data"], p["n_had_mc"], p["n_events_mc"])
        per_r[lab] = ((p["eff_sel"] * p["eps"] / eff_had) /
                      (aleph_eff_sig(a_gen) / ALEPH_EFF_HAD))
    return {"k": k, "r": r, "n_t_nominal": n_t, "r_per_period": per_r}


def mu_low_from_nominal(mu_nominal):
    """mu = 1 under the "low" reading is a smaller signal, so the same fitted number of events is
    a larger mu: mu_low = mu_nominal * N_had,A(low) / N_had,A(nominal)."""
    return mu_nominal * ALEPH_N_HAD["low"] / ALEPH_N_HAD["nominal"]


def combined_label(label_nominal, label_low):
    """The reported outcome: a claim stands only if both readings make it."""
    for x in (label_nominal, label_low):
        if x not in LABELS:
            raise ValueError("unknown label %r" % (x,))
    return label_nominal if label_nominal == label_low else "INCONCLUSIVE"


def old_v010_formula(a_gen, n_had_data, eff_sig_delphi_vs_simulated, reading="nominal"):
    """Plan v0.10's N_exp before the tag, kept only to quantify its bias in the review note:
    (ALEPH rate per hadronic event) x (DELPHI hadronic count) x (DELPHI eff / ALEPH eff)."""
    rate_per_had = ALEPH_N_SIG / ALEPH_N_HAD[reading]
    return rate_per_had * n_had_data * eff_sig_delphi_vs_simulated / aleph_eff_sig(a_gen)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--inputs", required=True,
                    help="JSON: {a_gen, rho, periods: {label: {n_had_data, n_had_mc, "
                         "n_events_mc, eff_sel, eps}}}")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    with open(a.inputs) as fh:
        inp = json.load(fh)
    res = totals(inp["periods"], inp["a_gen"], inp.get("rho", 1.0))
    res["forecast_kr"] = forecast_kr(inp["periods"], inp["a_gen"])
    with open(a.out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
