# Copyright 2026 MV2, Munim, Inc. (mv2@munimtech.com). Licensed under Apache-2.0.
# Made with AI agents working in MV2's name.
"""Analytic bounds for the in-jet reading of the ALEPH 30 GeV dimuon excess (NOTE-injet.md).

Pure Python, no dependencies. Three results:

1. single_jet_mass_bound(alpha, sqrt_s): the largest invariant mass a pair of (massless)
   particles can have when BOTH lie within angle alpha of one common axis, in an e+e- event of
   total energy sqrt_s: m_max = sqrt_s * tan(alpha / 2).
   Proof (NOTE-injet.md sec. 2): the rest of the event must balance the pair's momentum, so
   (E1 + E2)(1 + cos alpha) <= sqrt_s; the opening angle is at most 2 alpha and E1 E2 <=
   (E1 + E2)^2 / 4, so m^2 <= (E1 + E2)^2 sin^2 alpha <= s tan^2(alpha / 2).
2. min_cone(m, sqrt_s) and min_opening(m, sqrt_s): the inverse statements.
3. l3_expected_upper(): the largest ALEPH-sized signal L3's 1994-95 sample can hold, scaling
   ALEPH's fitted signal by the ratio of the two experiments' b b-bar -> mu mu samples.
"""
import json
import math

VERSION = "0.1.0"

SQRT_S_PEAK = 91.19      # GeV, Z pole
SQRT_S_MAX_LEP1 = 94.3   # GeV, highest LEP1 scan energy (conservative)
M_ALEPH = 30.40          # GeV, Heister arXiv:1610.06536 v9
S_ALEPH = 32.31          # fitted signal events (default KDE fit)
B_ALEPH = 1457.06        # fitted background events, 15-50 GeV
N_L3_5_50 = 170          # L3 opposite-sign events in 5-50 GeV (Hebbeker & Roth arXiv:1905.01111)
L3_PEAK_EXCESS = (6.4, 7.4)     # data - MC, 29-32 GeV, stat only
L3_SIGNAL_EXCESS = (8.4, 8.6)   # data - MC, 27-34 GeV, stat only


def single_jet_mass_bound(alpha_deg, sqrt_s=SQRT_S_PEAK):
    """Largest pair mass (GeV) with both particles within alpha_deg of one axis."""
    if not 0.0 < alpha_deg <= 90.0:
        raise ValueError("alpha must be in (0, 90] degrees")
    return sqrt_s * math.tan(math.radians(alpha_deg) / 2.0)


def min_cone(m, sqrt_s=SQRT_S_PEAK):
    """Smallest half-angle (deg) of a cone that can hold both particles of a pair of mass m."""
    if not 0.0 < m < sqrt_s:
        raise ValueError("need 0 < m < sqrt_s")
    return math.degrees(2.0 * math.atan(m / sqrt_s))


def min_opening(m, sqrt_s=SQRT_S_PEAK):
    """Smallest opening angle (deg) between the two particles of a pair of mass m."""
    return 2.0 * min_cone(m, sqrt_s)


def pair_mass(e1, e2, theta_deg):
    """Invariant mass of two massless particles."""
    return math.sqrt(2.0 * e1 * e2 * (1.0 - math.cos(math.radians(theta_deg))))


def l3_expected_upper(acc_ratio=1.0):
    """Upper bound on the ALEPH-sized signal in L3's sample.

    Signal assumed produced and accepted in proportion to the b b-bar -> mu mu background
    (acc_ratio = (signal/background acceptance in L3) / (same in ALEPH)). N_L3(15-50 GeV) <=
    N_L3(5-50 GeV) = 170, so this is an upper bound for acc_ratio as given.
    """
    return S_ALEPH / B_ALEPH * N_L3_5_50 * acc_ratio


def results():
    out = {
        "version": VERSION,
        "inputs": {
            "sqrt_s_peak": SQRT_S_PEAK, "sqrt_s_max_lep1": SQRT_S_MAX_LEP1,
            "m_aleph": M_ALEPH, "s_aleph": S_ALEPH, "b_aleph": B_ALEPH,
            "n_l3_5_50": N_L3_5_50, "l3_peak_excess": list(L3_PEAK_EXCESS),
            "l3_signal_excess": list(L3_SIGNAL_EXCESS),
        },
        "single_jet_bound_gev": {},
        "min_cone_deg": {},
        "min_opening_deg": {},
    }
    for a in (15, 20, 25, 30):
        out["single_jet_bound_gev"][str(a)] = {
            "peak": round(single_jet_mass_bound(a, SQRT_S_PEAK), 3),
            "max_lep1": round(single_jet_mass_bound(a, SQRT_S_MAX_LEP1), 3),
        }
    for m in (28.0, M_ALEPH):
        key = "%.2f" % m
        out["min_cone_deg"][key] = {
            "peak": round(min_cone(m, SQRT_S_PEAK), 2),
            "max_lep1": round(min_cone(m, SQRT_S_MAX_LEP1), 2),
        }
        out["min_opening_deg"][key] = {
            "peak": round(min_opening(m, SQRT_S_PEAK), 2),
            "max_lep1": round(min_opening(m, SQRT_S_MAX_LEP1), 2),
        }
    up1 = l3_expected_upper(1.0)
    up15 = l3_expected_upper(1.5)
    out["l3"] = {
        "s_over_b_aleph": round(S_ALEPH / B_ALEPH, 5),
        "expected_upper_acc1": round(up1, 2),
        "expected_upper_acc1p5": round(up15, 2),
        "expected_sigma_upper_acc1": round(up1 / L3_PEAK_EXCESS[1], 2),
        "expected_sigma_upper_acc1p5": round(up15 / L3_PEAK_EXCESS[1], 2),
        "peak_excess_minus_upper_acc1_sigma": round((L3_PEAK_EXCESS[0] - up1) / L3_PEAK_EXCESS[1], 2),
    }
    return out


if __name__ == "__main__":
    print(json.dumps(results(), indent=1, sort_keys=True))
