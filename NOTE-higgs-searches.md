# NOTE-higgs-searches: do the four LEP1 Higgs searches leave room for a 30 GeV boson?

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.5, 2026-11-18 (0.1-0.4 earlier the same day).
Made with AI agents working in MV2's name. Not an ALEPH, DELPHI, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** Section 3 is a hand calculation written before any
efficiency was measured; sections 4 and 5 are measured (jobs `efhz-v1` and `lephz-v1`, both
returned 2026-11-18). Section 6 is a new job (`kly-v1`, queued) whose expectations K1-K9 are
written below before it runs. Expectations J1-J7 and L1-L10 (section 8) were written before their
jobs ran. Text CC BY 4.0, code Apache-2.0.

**What changed in 0.5.**
1. *The L3 reading question is settled.* A second reading of L3's paper (readings/lephz-d-notes.md)
   confirms that the high-mass mu mu H0 selection has **no recoil-mass cut**: "recoil"
   appears only in the background sentence ("0.65 +- 0.11 events for a recoil mass greater than 30
   GeV"). The most pessimistic combination in section 5 is now p = 1.5e-6 (scalar, 4.7 standard
   deviations) instead of 8e-5.
2. *Prior art credited.* Ko, Li and Yu (arXiv:1610.07526, 2016) already showed at parton level that
   their three boson models do not reproduce ALEPH's muon-jet angles, and that a boson coupling
   directly to b bbar is excluded by LHC Drell-Yan data. Section 6 and section 11 say what this
   note adds.
3. *Section 6 (new): Ko, Li and Yu's two surviving models.* Their model II (a Z' that couples the b
   quark to a heavy vector-like B quark, built to escape the LHC bound) and model III (Z -> Z' phi)
   were not among our three models. Job `kly-v1` applies the four LEP1 Higgs-search selections to
   both. Expectations K1-K9 are written before it runs.

## 1. The argument

The ALEPH 30 GeV dimuon excess (arXiv:1610.06536 v9: 32.31 +- 10.87 b-tagged events at 30.40
GeV, Gamma 1.78 GeV) has been read as a new boson X -> mu+ mu- produced with b quarks (a vector
or scalar radiated off the b line, or Z -> h A). At hadron level, such a boson's muons are
isolated from the jets in about 90-95 % of events (NOTE-kinematics.md, NOTE-fourfermion.md).

Two energetic isolated leptons recoiling against hadrons is exactly what the LEP1 Standard Model
Higgs searches selected in e+e- -> H Z*, Z* -> l+ l-. All four LEP experiments ran this search
on their full Z-peak data and found a handful of candidates, consistent with background.
ALEPH's own search contains the 1992-95 data in which the excess was found.

## 2. The four searches

| search | data | selection (short; full text in readings/lephz-notes.md) | candidates |
|---|---|---|---|
| ALEPH, PLB 384 (1996) 427 | ~4.5M hadronic Z, 1989-95 | each lepton p > 3, sum > 20 GeV, m_ll > 5, sum pT to thrust > 15 GeV; ONE lepton isolated (30 deg cone); >= 6 tracks; recoil > 40 GeV; b-tag P_uds < 0.05 | 3: recoil 49.7, 51.5, 66.9 GeV |
| L3, PLB 385 (1996) 454 | 3.05M hadronic Z, 1991-94 | > 4 tracks, >= 8 clusters, thrust < 0.92; p1 + p2 > 20, each > 3.4 GeV; BOTH muons isolated (D < 2.5 each, D1 D2 < 0.25; calorimeter cones); **no m_mumu or recoil cut** (confirmed by a second reading) | **0** (high-mass selection) |
| DELPHI, NPB 421 (1994) 3 | 935,616 hadronic Z, 1991-92 | >= 6 charged; p > 5 each, p_max > 10 GeV, opening > 30 deg; recoil > 15, visible rest mass > 10 GeV; >= 2 jets; muons > 40 / > 20 deg from jets | 1: recoil 27.8 +- 1.9 GeV |
| OPAL, ZPC 73 (1997) 189 | ~160 pb^-1 to 1995 (3.5M hadronic Z used, conservative) | 5 < p < 30 GeV each, sum > 20; E_vis > 80 GeV; displaced vertex; a recoil-mass cut that replaces the earlier 25 GeV hadronic-mass cut, value not stated; isolation of PLB 327 (1994) 397 | 1: recoil 61.2 +- 1.0 GeV, p = 19.3, 7.3 GeV |

Published efficiencies for the Higgs signal itself (Z* -> mu mu) at m_H = 30-60 GeV: L3 37.0, 37.1,
36.1, 32.3 % at 30, 40, 50, 60 GeV; DELPHI 53-55 %; ALEPH 48 % at 60 GeV; OPAL 9-31 %.

**Which candidates can be signal.** The mass recoiling against a muon pair of mass m is at most
sqrt(s) - m. A boson event with m_mumu >= 26 GeV has a recoil mass of at most 65.2 GeV, so
ALEPH's 66.9 +- 0.3 GeV candidate (about 5.7 standard deviations above) is not counted. The OPAL
candidate's muon momenta fix its dimuon mass at 16.8 GeV (6.4-23.0 GeV within 2 sigma of the
recoil), so it is not counted either. The two other ALEPH candidates and the DELPHI event are
counted as possible signal, with no background subtracted. Rule "all" counts every candidate.

## 3. Hand bound (common efficiency eps; written in 0.1-0.2, before any efficiency was measured)

Prediction for a search = R_acc x N_had x f_gen x eps x ID^2 x b-tag factor, with R_acc =
5.90e-5 boson events per hadronic Z in ALEPH's acceptance (lep4f, central reading), f_gen =
0.953, ID^2 = 0.86^2, b-tag factor 0.8 for ALEPH 1996 (stand-in) and 0.5 for OPAL's vertex
requirement. Events for eps = 1: **ALEPH 149.7, L3 126.8, DELPHI 38.9** (OPAL 72.8). 95 % CLs
limits with b = 0: s_up = 3.00, 4.74, 6.30, 7.75, 9.15, 10.51 for n = 0-5.

| combination | n counted | predicted for eps = 1 | eps allowed (95 % CLs) |
|---|---|---|---|
| **ALEPH + L3 + DELPHI**, signal-compatible, ALEPH central rate | 3 | 315.5 | **< 0.025** |
| same, every candidate counted | 4 | 315.5 | < 0.029 |
| same, low hadronic-count reading and yield minus 1 sigma | 3 | 180.8 | < 0.043 |
| same, lowest literature rate (Br 1.1e-5, Ko, Li, Yu) | 3 | 84.2 | < 0.092 |
| **L3 alone** (0 candidates; also tests Z -> h A) | 0 | 126.9 | **< 0.024** |
| L3 + DELPHI (the searches that test Z -> h A) | 1 | 165.8 | < 0.029 |
| L3 + DELPHI, lowest literature rate | 1 | 44.2 | < 0.107 |
| ALEPH subset: the 32 excess events themselves (2 compatible) | 2 | 30.8 | < 0.205 |

The measured L3 and DELPHI efficiencies (section 5: 0.54-0.82) are about 18-33 times these
bounds.

## 4. Measured: ALEPH's own search (job efhz-v1)

`analysis/efhz.py` 0.1.0 applied ALEPH's H l+ l- selection (as read; the 1996 paper's cuts match
the 1993 ones used here, apart from the b-tag) to 10,000 Pythia 8 events per model, at hadron
level, with no muon identification. eps = fraction of events in ALEPH's acceptance and the
20-40 GeV window that pass. Outputs: `analysis/results/efhz/`.

| model | nominal | both muons isolated | recoil > 50 | no recoil cut | strict (all tightenings) |
|---|---|---|---|---|---|
| V (vector off b) | **0.498** | 0.234 | 0.278 | 0.717 | 0.118 |
| S (scalar off b) | **0.270** | 0.133 | 0.093 | 0.712 | 0.036 |
| P (Z -> h A) | **0.018** | 0.007 | 0.004 | 0.655 | 0.001 |

The recoil cut decides it. It keeps 64 % of V, 35 % of S and 3 % of P events (every other cut
keeps 67-99 %). In the scalar model the boson takes more of the energy: the median mass recoiling
against the muon pair is 34.6 GeV, against 45.7 GeV for the vector and 30.4 GeV (= m_h) for Z -> h A.

ALEPH's search alone (three candidates, b = 0; the b-tag cost of ALEPH 1996 bracketed by factors
0.8 and 0.4) excludes the vector under every rate reading (worst p = 0.011) and the scalar at the
excess's central rate (p <= 2.7e-6), but **not** the scalar at the lowest literature rate
(p = 0.006-0.21) nor in the reading that uses only the 32 excess events (p = 0.10). Details in
version 0.3 of this note (git history).

## 5. Measured: all four searches (job lephz-v1)

`analysis/lephz.py` 0.1.0 applied the L3, DELPHI and OPAL selections (and ALEPH's, through
efhz.select: one definition) to about 7,600-8,000 hadronised events per model, at hadron level,
with no muon identification (the common factor 0.86^2 is in the predictions). All 14 unit tests
passed. Outputs and sha256 of every source file: `analysis/results/lephz/`.

**Efficiency** (fraction of events in ALEPH's acceptance and the 20-40 GeV window that pass):

| model | ALEPH96 | L3_96 | DELPHI94 | OPAL97 |
|---|---|---|---|---|
| V (vector off b) | 0.498 | **0.554** | **0.744** | 0.543 |
| S (scalar off b) | 0.262 | **0.535** | **0.691** | 0.387 |
| P (Z -> h A) | 0.019 | **0.644** | **0.816** | 0.373 |
| weakest variant, V / S / P | strict 0.112 / 0.034 / 0.002 | cos0.72: 0.442 / 0.404 / 0.520 | iso_both40: 0.627 / 0.604 / 0.730 | iso_both30 0.359 / 0.280; recoil40 0.444 / 0.229 / 0.007 |

L3's variants (a 40 deg jet cone for D, muon acceptance |cos theta| < 0.72 instead of 0.8, an
electromagnetic-only BGO cone, no thrust cut) move its efficiency by at most 0.13; DELPHI's
(y_cut 0.005, both muons > 40 deg from jets, |cos theta| < 0.95) by at most 0.12. ALEPH's S value
(0.262) agrees with efhz-v1 (0.270) within the statistics of independent samples.

**Confrontation** (nominal selections, b = 0, p = Poisson probability of n or fewer):

| combination | candidates | rate | V: predicted, p | S: predicted, p | P: predicted, p |
|---|---|---|---|---|---|
| ALEPH + L3 + DELPHI | 3 compatible | central | 173.8, 3e-70 | 133.9, 3e-53 | 116.3, 9e-46 |
| ALEPH + L3 + DELPHI | 3 compatible | low (yield - 1 sigma) | 99.6, 9e-39 | 76.8, 4e-29 | 66.6, 6e-25 |
| ALEPH + L3 + DELPHI | all 4 | lowest literature | 46.4, 1.5e-15 | 35.7, 2.3e-11 | 31.0, 1.5e-9 |
| **L3 + DELPHI (no ALEPH)** | all 1 | central | 99.2, 8e-42 | 94.8, 7e-40 | 113.4, 6e-48 |
| **L3 + DELPHI (no ALEPH)** | all 1 | lowest literature | **26.5, 9e-11** | **25.3, 3e-10** | **30.3, 2e-12** |
| L3 alone | 0 | central | 70.3, 3e-31 | 67.9, 3e-30 | 81.7, 3e-36 |
| DELPHI alone | 1 | central | 28.9, 8e-12 | 26.9, 6e-11 | 31.8, 5e-13 |
| ALEPH alone (b-tag 0.8) | 2 compatible | central | 74.6, 1e-29 | 39.2, 8e-15 | 2.8, 0.47 |
| OPAL alone (vertex 0.5) | 0 compatible | central | 39.5, 7e-18 | 28.2, 6e-13 | 27.1, 2e-12 |

At 95 % CLs, ALEPH + L3 + DELPHI allow at most **4.5 % (V), 5.8 % (S) and 6.7 % (P)** of the
excess's central rate. All four searches together (5 candidates): p = 9e-84, 4e-62, 3e-54.

**Robustness, by hand from the job's numbers** (lowest literature rate throughout; every
candidate counted as signal):

1. *ALEPH's b-tag cost at 0.4 instead of 0.8* (ALEPH + L3 + DELPHI, 4 candidates): predicted
   36.4 / 30.5 / 30.6 events, p = 1.3e-11 / 2.3e-9 / 2.1e-9 (V / S / P).
2. *No ALEPH, weakest L3 and DELPHI variants* (cos0.72, iso_both40; 1 candidate): predicted
   21.5 / 19.9 / 25.2, p = 1.1e-8 / 4.6e-8 / 3.1e-10.
3. *Calibration to the experiments' own detector-level efficiencies.* Our P model resembles the
   Higgs signal the searches were built for (two muons with about 30 GeV recoiling). Our hadron-
   level eps x 0.86^2 for P against the published Higgs efficiency at the nearest mass: L3 0.476
   vs 0.370 (m_H = 30 GeV), ratio 0.78; DELPHI 0.604 vs 0.546 (m_H = 35 GeV), ratio 0.90; OPAL
   (with its vertex factor 0.5) 0.138 vs 0.086 (m_H = 30 GeV), ratio 0.62. So our selections are
   about 10-60 % more efficient than the real ones, as expected without a detector simulation; the
   topologies differ, so this is a rough guide only. Scaling L3 by 0.78 and DELPHI by 0.90 on top
   of item 2: p = 4.7e-7 / 1.5e-6 / 2.6e-8. (For the scalar, by hand: L3 0.404 x 33.83 x 0.78 =
   10.66 and DELPHI 0.604 x 10.38 x 0.90 = 5.64 events, total 16.30; P(n <= 1) = e^-16.30 x 17.30
   = 1.44e-6.)
4. *The L3 recoil question, settled.* Version 0.4 asked whether L3's high-mass selection also
   required a recoil mass above 30 GeV, because its background was quoted "for a recoil mass
   greater than 30 GeV". A second, independent reading of the paper (2026-11-18, readings/lephz-d-notes.md) finds
   no recoil, missing-mass or Higgs-mass requirement in the cut list of section 5.1; the recoil
   value appears only in the background sentence, and the limit is set where the expected number
   of events is 3, with zero mu mu events selected. The selection as coded (no recoil cut) is
   therefore the paper's. Version 0.4's stacked case with a hypothetical recoil cut (p = 8e-5) is
   withdrawn.

The most pessimistic combination we can construct, for the scalar, now has **p = 1.5e-6 (4.7
standard deviations)**: no ALEPH, the weakest L3 and DELPHI variants, both scaled down to the
experiments' own published efficiencies, the lowest rate in the literature, and the DELPHI
candidate counted as signal. OPAL97 is shown for completeness but is not used in any headline
number: its recoil-cut value is not stated and its calibration ratio is the worst (0.62).

**Independence.** The L3 Higgs search (1991-94) shares data with L3's four-fermion measurement
(1991-92), and OPAL's two analyses share data too, so these are separate selections, not
independent data sets. DELPHI's 1991-92 data are in neither four-fermion constraint. DELPHI's
search alone, at the lowest literature rate, predicts 7.7 / 7.2 / 8.5 events against 1 (p = 3.9e-3
/ 6.3e-3 / 2.0e-3): a second detector, on its own, excludes all three models at 99 %.

## 6. Ko, Li and Yu's two other models (job kly-v1, queued; expectations written before it runs)

**Why.** Ko, Li and Yu (arXiv:1610.07526) considered three models. Their model I, a boson coupling
directly to b bbar and mu mu, is our V and S; they showed it is excluded by LHC Drell-Yan
production b bbar -> X -> mu mu (one benchmark also by Z -> 4b), so for V and S the LEP1 results here are an
independent exclusion from the same collider, not a first one. Their **model II** was built to
escape that bound: a Z' (30.4 GeV, -> mu mu) couples the b quark to a heavy vector-like singlet
quark B and not to b bbar, so at LEP1 it is made in Z -> b B*bar, B*bar -> bbar Z'. Their
**model III** is Z -> Z' phi with Z' -> mu mu and phi -> b bbar (spin 1 + spin 0, unlike our P).
Their own benchmark III of model II (m_B = 110 GeV, Gamma_B = 3.4 GeV, g'_b = 0.7, sin theta_L ~
0.5) gives Gamma(Z -> b bbar mu mu) = 2.75e-5 GeV, i.e. Br = 1.1e-5: **the "lowest literature
rate" used throughout this note is this model's own fitted rate.** Benchmark IV (m_B = 180 GeV,
Gamma_B = 124.4 GeV) gives 2.35e-5 GeV (Br 9.4e-6, 0.85 of that). They showed (parton level, signal
only) that the muons of all their models lie far from the leading b jet (minimum angle peaking at
50-70 deg), unlike ALEPH's events, but they did not confront the models with any other LEP1
measurement. Model II's LHC signatures (B pair production) are, in their words, "very likely"
already excluded, but no dedicated search was cited. The LEP1 Higgs searches test it directly.

**What the job does.** `analysis/kly.py` 0.1.0 generates both models with full helicity
amplitudes in the framework of xkin/xme.py: model B with the B propagator (p-slash + m_B) / (p^2 -
m_B^2 + i m_B Gamma_B), the paper's eq. (4) couplings (Z b B left-handed, from b-B mixing; Z' b B
pure vector; no diagonal Z' b b coupling, by the paper's assumption), for both benchmarks (B110,
B180), plus a variant with a left-handed Z' vertex (B110L, in which the m_B term drops out) to
bracket the chirality; model Q for m_phi = 12, 30.4 and 50 GeV (the paper shows 10, 50 and 80;
12 is the lowest mass at which b bbar can still form two B mesons; 80 needs an off-shell Z').
Unit tests check the new amplitude against xme's validated one in the massless limit, that the
m_B term drops out for two left-handed vertices, that a vector Z' vertex is the non-interfering
sum of its left and right parts, and an exact decay-averaged identity of the Z' current. The
Z Z' phi vertex is taken as g^{mu nu} (from the scalar's covariant derivative; the paper gives
only its strength). `analysis/run_kly.py` hadronises 8,000 events per model with Pythia 8 and applies
lephz's four selections (one definition) and its confrontation. It also reports the angle
between each muon and the nearest jet.

**Expectations (written 2026-11-18, before kly-v1 runs):**

| | expectation |
|---|---|
| K1 | all unit tests of test_kly pass |
| K2 | B110: eps(L3 nominal) >= 0.30 and eps(DELPHI nominal) >= 0.40 |
| K3 | B110: L3 + DELPHI, every candidate, lowest literature rate (= the model's own rate): p < 1e-4 |
| K4 | B180 and B110L: L3 and DELPHI nominal efficiencies each within 0.10 of B110's |
| K5 | Q30: eps(L3) >= 0.30, eps(DELPHI) >= 0.40, eps(ALEPH96) < 0.10 |
| K6 | Q12: eps(DELPHI) < 0.05 (its recoil > 15 GeV cut), eps(L3) >= 0.25, and L3 alone (0 candidates) at the lowest literature rate p < 1e-3 |
| K7 | Q50: eps(L3) >= 0.30, eps(DELPHI) >= 0.40; L3 + DELPHI, every candidate, lowest literature rate: p < 1e-4 |
| K8 | B110 and Q30: the nearer muon lies within 15 deg of a jet in <= 15 % of acceptance-and-window events (ALEPH: in all its events) |
| K9 | unweighting: events above the weight maximum <= 1 % of accepted parton events, every model |

Hand estimate behind K3: with eps(L3) ~ 0.5 and eps(DELPHI) ~ 0.7, L3 + DELPHI predict about
0.5 x 33.8 + 0.7 x 10.4 = 24 events at the lowest rate, against 1 candidate (p ~ 1e-9). K3 fails
only if the two selections together keep less than about half of that.

## 7. What this means

Four LEP1 detectors, about 12 million hadronic Z decays, and selections built for two isolated
leptons plus hadrons leave room for at most about 5-7 % of an ALEPH-sized boson with typically
isolated muons; L3 and DELPHI alone exclude it even at the lowest rate in the literature.
Together with the four-fermion measurements (NOTE-fourfermion.md) and ALEPH's own description of
its events (NOTE-kinematics.md), this says: **the excess cannot be a boson radiated off b quarks
or Z -> h A, decaying to isolated muons, at anything like the rate the excess needs.** If the
excess is real, its muons sit inside the b jets, which points to a b-jet effect (for example
cascade decays or a mismodelled background shape) or to a state that decays inside a jet, rather
than to these boson models. DELPHI's open data test that directly (PLAN.md, tests A and B).
Section 6 extends the test to the two published models that were designed to survive the LHC.

## 8. Expectations, written before the jobs ran, and grades

efhz-v1 (written in 0.1, graded in 0.3):

| | expectation | result | grade |
|---|---|---|---|
| J1 | all 12 tests pass | 12 of 12 ok | **PASS** |
| J2 | eps(nominal) >= 0.30 for V and S | V 0.498, **S 0.270** | **FAIL** (S) |
| J3 | >= 85 % of V and S events have at least one muon isolated | V 91.6 %, S 95.4 % | **PASS** |
| J4 | eps(nominal, P) < 0.05 and eps(norecoil, P) >= 0.30 | 0.018; 0.655 | **PASS** |
| J5 | rate reading p < 1e-6 (central), < 1e-3 (lowest rate) for V and S | V 5e-36, 4.7e-8; S 2.7e-18, 7.2e-4 | **PASS** as written (with the 1996 b-tag cost, S at the lowest rate is 5.7e-3 to 0.21) |
| J6 | subset p_marginal < 0.05 for V and S | V 0.02, **S 0.10** | **FAIL** (S) |
| J7 | `strict` keeps eps >= 0.10 for V and S | V 0.118, **S 0.036** | **FAIL** (S) |

All three failures have one cause: the recoil-mass cut, against the scalar model's harder boson.

lephz-v1 (written in 0.2, graded in 0.4):

| | expectation | result | grade |
|---|---|---|---|
| L1 | all 14 unit tests of test_lephz pass | 14 of 14 ok | **PASS** |
| L2 | eps(L3 nominal) >= 0.15 for V and S | V 0.554, S 0.535 | **PASS** |
| L3 | eps(DELPHI nominal) >= 0.20 for V and S | V 0.744, S 0.691 | **PASS** |
| L4 | P: eps(L3) >= 0.15 and eps(DELPHI) >= 0.20; eps(ALEPH96) < 0.05 | 0.644; 0.816; 0.019 | **PASS** |
| L5 | ALEPH + L3 + DELPHI, compatible, central rate: p < 1e-6 for V and S | V 3.0e-70, S 2.8e-53 | **PASS** |
| L6 | ALEPH + L3 + DELPHI, every candidate, lowest literature rate: p < 1e-3 for V and S | V 1.5e-15, S 2.3e-11 | **PASS** |
| L7 | P: L3 + DELPHI, every candidate, central rate: p < 1e-3 | 6.2e-48 | **PASS** |
| L8 | < 8 % of V and S events have recoil > 65.2 GeV | V 0.36 %, S 0.17 % | **PASS** |
| L9 | weakest L3 variant keeps eps >= 0.10 for V and S | V 0.442, S 0.404 (cos0.72) | **PASS** |
| L10 | weakest DELPHI variant keeps eps >= 0.10 for V and S | V 0.627, S 0.604 (iso_both40) | **PASS** |

Ten of ten passed, with a large margin: the smallest L3 or DELPHI efficiency in any variant
(0.404) is four times the L9 threshold of 0.10.

kly-v1: expectations K1-K9 in section 6; grades will be added here when the job returns.

## 9. Limits (read before citing)

1. **Readings.** The cuts come from AI reading agents' summaries of scanned papers; a few values
   are interpretations (readings/lephz-notes.md, last section). L3's lack of a recoil cut was
   read twice, independently.
2. **Generator level.** Hadron level (Pythia 8), no detector simulation. Isolation is computed
   from generator particles. Muon identification is a common factor 0.86 per muon (ALEPH's).
   Section 5 item 3 compares with the experiments' own efficiencies (ratios 0.62-0.90).
3. **Stand-ins.** ALEPH's 1996 b-tag as a factor 0.8 (bracketed by 0.4); OPAL's vertex as 0.5;
   L3 muon acceptance |cos theta| < 0.8; DELPHI |cos theta| < 0.9 and Durham y_cut 0.02; L3's
   E_jet as the energy in a 25 deg cone. Variants bracket each.
4. **Candidates.** Signal-compatibility uses only the recoil mass (and, for OPAL, the momenta).
5. **Rate.** The boson rate is the excess's own (lep4f readings: central, low hadronic count with
   yield minus 1 sigma, lowest literature value, which is Ko, Li and Yu's model-II benchmark).
6. **Models.** Three explicit models (NOTE-kinematics.md), plus Ko, Li and Yu's models II and III
   in section 6 once kly-v1 returns. Another production mechanism with a different recoil
   spectrum would need its own efficiency.
7. **What is not covered.** A source whose muons sit inside the b jets passes none of these
   selections. That is what ALEPH describes, and what DELPHI's open data test directly.

## 10. Code

`analysis/efhz.py` 0.1.0 (ALEPH), `analysis/run_efhz.py`, `analysis/test_efhz.py` (12 tests).
`analysis/lephz.py` 0.1.0: the L3, DELPHI and OPAL selections, ALEPH's via efhz (one definition),
candidate compatibility, predictions and the combined confrontation; `analysis/test_lephz.py`
(14 tests); `analysis/run_lephz.py`. `analysis/kly.py` 0.1.0: Ko, Li and Yu's models II and III;
`analysis/test_kly.py`; `analysis/run_kly.py`. Run: `python -m unittest -v test_efhz test_lephz
test_kly`, then `python run_efhz.py --out OUT --nsig 10000 --workers 2`,
`python run_lephz.py --out OUT --nsig 8000 --workers 2` and
`python run_kly.py --out OUT --nsig 8000 --workers 2` (need `numpy`, `pythia8mc`, and eff4f.py,
lep4f.py and the xkin modules alongside). Outputs: `analysis/results/efhz/`,
`analysis/results/lephz/` (and `analysis/results/kly/` when kly-v1 returns).

## 11. Prior art

INSPIRE (queried 2026-11-18): 22 papers cite arXiv:1610.06536 (record 1492968). None cites any of
the five LEP1 Higgs-search papers used here (records 420342, 357422, 423697, 421562, 374451), and
none uses an isolated-lepton sample. The closest work is L3's own re-analysis of muon pairs in
b-tagged hadronic events (arXiv:1905.01111), which looks at the same non-isolated signature as
ALEPH. Ko, Li and Yu (arXiv:1610.07526) showed in 2016, at parton level and for signal only, that
their boson models put the muons far from the b jets, unlike ALEPH's events, and that a boson
coupling directly to b bbar is excluded at the LHC; they used no other LEP1 measurement and called
for "more detailed study of ALEPH data as well as other data on the Z decays". As far as we can
find, the LEP1 Higgs searches (and four-fermion measurements) have not been confronted with the
excess before. What is new here is that confrontation, at hadron level and against published
counts, with expectations written before each calculation.
