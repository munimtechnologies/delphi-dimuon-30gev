# NOTE-higgs-searches: do the four LEP1 Higgs searches leave room for a 30 GeV boson?

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.6, 2026-11-18 (0.1-0.5 earlier the same day).
Made with AI agents working in MV2's name. Not an ALEPH, DELPHI, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** Section 3 is a hand calculation written before any
efficiency was measured; sections 4, 5 and 6 are measured (jobs `efhz-v1`, `lephz-v1` and
`kly-v1`, all returned 2026-11-18). Section 6b is a new job (`kly4f-v1`, queued) whose
expectations F1-F5 are written below before it runs. Expectations J1-J7, L1-L10 and K1-K9
(section 8) were written before their jobs ran. Text CC BY 4.0, code Apache-2.0.

**What changed in 0.6.**
1. *Ko, Li and Yu's two surviving models are excluded too (section 6).* Job `kly-v1` returned:
   all nine expectations K1-K9 passed. L3 and DELPHI together predict 26-28 events at the models'
   own rate for model II (Z' coupling b to a heavy vector-like B) and for model III (Z -> Z' phi)
   at m_phi = 30.4 GeV, against one candidate (p ~ 1e-10). The most pessimistic combination we
   can build (no ALEPH, weakest variants, scaled to the experiments' own efficiencies) gives
   p <= 7.4e-7 for model II, 2.3e-7 for model III at 30.4 GeV, 1.6e-5 at 50 GeV and 6.1e-5 at
   12 GeV.
2. *A weak spot, stated plainly.* Model III with a light scalar (m_phi = 12 GeV) passes almost
   none of the DELPHI, ALEPH and OPAL selections (efficiency 0.03, 0.01, 0.01), because their
   recoil-mass cuts remove events whose muon pair recoils against only 12 GeV. Only L3's search,
   which has no recoil cut, closes it. Section 6b pre-registers a second, independent test of that
   corner with the LEP1 four-fermion selections (job `kly4f-v1`, the same events).
3. *Muon-jet angles at hadron level.* In both models the nearer muon lies within 15 deg of a jet in
   only 4-5 % of events (B110 4.3 %, Q30 4.5 %), confirming at hadron level Ko, Li and Yu's
   parton-level finding; ALEPH reports this in all of its excess events.

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
requirement. Events for eps = 1: **ALEPH 149.7, L3 126.8, DELPHI 38.9** (OPAL 72.8). At the lowest
literature rate: L3 33.83, DELPHI 10.38. 95 % CLs limits with b = 0: s_up = 3.00, 4.74, 6.30,
7.75, 9.15, 10.51 for n = 0-5.

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

The measured L3 and DELPHI efficiencies (sections 5-6: 0.42-0.82 for every model except Q12's
DELPHI value) are 4-30 times these bounds.

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
4. *The L3 recoil question, settled.* A second, independent reading of the paper (2026-11-18,
   readings/lephz-d-notes.md) finds no recoil, missing-mass or Higgs-mass requirement in the cut
   list of section 5.1; the recoil value appears only in the background sentence, and the limit
   is set where the expected number of events is 3, with zero mu mu events selected. The selection
   as coded (no recoil cut) is therefore the paper's.

The most pessimistic combination we can construct, for the scalar, has **p = 1.5e-6 (4.7
standard deviations)**: no ALEPH, the weakest L3 and DELPHI variants, both scaled down to the
experiments' own published efficiencies, the lowest rate in the literature, and the DELPHI
candidate counted as signal. OPAL97 is shown for completeness but is not used in any headline
number: its recoil-cut value is not stated and its calibration ratio is the worst (0.62).

**Independence.** The L3 Higgs search (1991-94) shares data with L3's four-fermion measurement
(1991-92), and OPAL's two analyses share data too, so these are separate selections, not
independent data sets. DELPHI's 1991-92 data are in neither four-fermion constraint. DELPHI's
search alone, at the lowest literature rate, predicts 7.7 / 7.2 / 8.5 events against 1 (p = 3.9e-3
/ 6.3e-3 / 2.0e-3): a second detector, on its own, excludes all three models at 99 %.

## 6. Ko, Li and Yu's two other models (job kly-v1, returned 2026-11-18)

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
measurement.

**What the job did.** `analysis/kly.py` 0.1.0 generates both models with full helicity
amplitudes: model B with the B propagator (p-slash + m_B) / (p^2 - m_B^2 + i m_B Gamma_B) and the
paper's eq. (4) couplings, for both benchmarks (B110, B180) plus a left-handed Z' vertex variant
(B110L) to bracket the chirality; model Q (Z Z' phi vertex g^{mu nu}) for m_phi = 12, 30.4 and
50 GeV. `analysis/run_kly.py` hadronised 7,675-8,000 events per model with Pythia 8.318 and
applied lephz's four selections (one definition). All 11 unit tests passed; no event exceeded the
unweighting maximum; the job took 8 minutes (2 CPUs, 0.09 GB). Outputs and sha256 of every
source file: `analysis/results/kly/`.

**Efficiency** (fraction of events in ALEPH's acceptance and the 20-40 GeV window that pass; no
muon identification):

| model | ALEPH96 | L3_96 | DELPHI94 | OPAL97 | L3 weakest (cos0.72) | DELPHI weakest | nearer muon < 15 deg of a jet |
|---|---|---|---|---|---|---|---|
| B110 (model II, benchmark III) | 0.314 | **0.553** | **0.706** | 0.450 | 0.434 | 0.626 (iso_both40) | 4.3 % |
| B180 (benchmark IV) | 0.339 | **0.549** | **0.727** | 0.475 | 0.418 | 0.640 | 4.8 % |
| B110L (left-handed Z') | 0.373 | **0.552** | **0.716** | 0.479 | 0.439 | 0.613 | 5.1 % |
| Q12 (model III, m_phi 12) | 0.008 | **0.604** | 0.034 | 0.009 | 0.456 | 0.029 | 3.6 % |
| Q30 (m_phi 30.4) | 0.018 | **0.588** | **0.789** | 0.417 | 0.437 | 0.721 | 4.5 % |
| Q50 (m_phi 50) | 0.800 | **0.420** | **0.683** | 0.757 | 0.329 | 0.544 | 6.1 % |

In model Q the mass recoiling against the muon pair is m_phi (median 12.0, 30.4, 50.0 GeV), so
the recoil-mass cuts of ALEPH (> 40), DELPHI (> 15) and OPAL decide: ALEPH sees only Q50, DELPHI
and OPAL lose Q12 (DELPHI's recoil cut keeps 12 % of Q12 events, OPAL's 4 %). L3 has no recoil
cut and keeps 0.42-0.60 of every model. In model B the recoil is broad (median 36-39 GeV).

**Confrontation** (nominal selections, b = 0; "lit" = the lowest literature rate, which is model
II's own benchmark rate):

| model | L3 + DELPHI, all 1 candidate, lit: predicted, p | L3 alone (0), lit: predicted, p | DELPHI alone (1), lit: p | L3 + DELPHI, central: p |
|---|---|---|---|---|
| B110 | 26.05, **1.3e-10** | 18.72, 7.4e-9 | 5.5e-3 | 3.9e-41 |
| B180 | 26.13, 1.2e-10 | 18.58, 8.5e-9 | 4.5e-3 | 2.9e-41 |
| B110L | 26.12, 1.2e-10 | 18.68, 7.7e-9 | 5.0e-3 | 3.0e-41 |
| Q12 | 20.77, 2.1e-8 | 20.43, **1.4e-9** | 0.95 (no test) | 1.2e-32 |
| Q30 | 28.08, **1.8e-11** | 19.89, 2.3e-9 | 2.5e-3 | 2.0e-44 |
| Q50 | 21.29, 1.3e-8 | 14.20, 6.8e-7 | 6.8e-3 | 1.8e-33 |

**Most pessimistic combination, by hand** (as section 5 item 3: no ALEPH, weakest L3 and DELPHI
variants, L3 scaled by 0.78 and DELPHI by 0.90, lowest literature rate, the DELPHI candidate
counted as signal; predicted lambda, P(n <= 1) = e^-lambda (1 + lambda)):

| model | L3 events | DELPHI events | lambda | p | z |
|---|---|---|---|---|---|
| B110 | 0.434 x 33.83 x 0.78 = 11.45 | 0.626 x 10.38 x 0.90 = 5.85 | 17.30 | 5.6e-7 | 4.9 |
| B180 | 11.03 | 5.98 | 17.01 | 7.4e-7 | 4.8 |
| B110L | 11.58 | 5.73 | 17.31 | 5.6e-7 | 4.9 |
| Q12 | 0.456 x 33.83 x 0.78 = 12.03 | 0.029 x 10.38 x 0.90 = 0.27 | 12.30 | **6.1e-5** | 3.8 |
| Q30 | 11.53 | 6.73 | 18.26 | 2.3e-7 | 5.0 |
| Q50 | 0.329 x 33.83 x 0.78 = 8.68 | 0.544 x 10.38 x 0.90 = 5.08 | 13.76 | 1.6e-5 | 4.2 |

For Q12, counting only signal-compatible candidates (the DELPHI event recoils against 27.8 GeV,
not 12), L3 alone gives p = e^-12.03 = 6.0e-6 (4.4 standard deviations).

**Reading.** Both of Ko, Li and Yu's escape models are excluded by the LEP1 Higgs searches at
their own rate, by at least 3.8 standard deviations in the most pessimistic combination and by
6-7 standard deviations with nominal selections. Model II is closed by two detectors (L3 and
DELPHI, each alone at 99 %). Model III with a light scalar is closed by L3's search alone; that is
the weakest point of the whole confrontation, and section 6b tests it a second way.

## 6b. Light-scalar corner, second test: the four-fermion selections (job kly4f-v1, queued; expectations written before it runs)

**Why.** For Q12 the only constraint is L3's Higgs search, which shares its 1991-92 data with
L3's four-fermion measurement. OPAL's four-fermion measurement (3.53M hadronic Z, 1 event between
20 and 40 GeV) is a different detector and has no recoil-mass cut. NOTE-fourfermion.md found its
selection keeps 84-88 % of our V, S and P events. If it also keeps Q12 events, OPAL alone gives a
second, independent exclusion of the light-scalar corner.

**What the job does.** `analysis/run_kly4f.py` 0.1.0 applies eff4f.py's OPAL, L3 and ALEPH
four-fermion selections (one definition, all variants) to the **same events** as kly-v1: same
generator, seeds, model order and Pythia settings. It confronts OPAL + L3 (1 event in 20-40 GeV),
each alone, at the central and lowest literature rates, with nominal and with the weakest variant
of each experiment. It also reports how often the rest of the event forms fewer than two Durham
jets at y_cut = 0.02 (OPAL's two-jet requirement).

**Hand estimate.** At the lowest literature rate, eff4f's predictions imply about 39.2 events
(OPAL) and 10.7 (L3) for efficiency 1 (from 41.6 events at OPAL 0.877, L3 0.677, scaled by their
hadronic-Z counts 3.53M and 0.96M). One observed event gives p < 1e-3 when the prediction exceeds
9.2 events. Risk for Q12: the scalar (about 41 GeV energy, gamma ~ 3.4) decays to b quarks about
35 deg apart, which at y_cut = 0.02 is near the threshold for merging into one jet; OPAL's
two-jet requirement may then remove many Q12 events.

| | expectation |
|---|---|
| F1 | all 4 unit tests pass, and every model has the same n_hadronised and n_fail as kly-v1 (closure) |
| F2 | B110, B180, B110L, Q30, Q50: eps(OPAL nominal) >= 0.60 and eps(L3 nominal) >= 0.40 |
| F3 | Q12: eps(L3 nominal) >= 0.40. eps(OPAL nominal) is recorded; prior 50 % that it is >= 0.30 |
| F4 | OPAL + L3, nominal, lowest literature rate: p < 1e-6 for B110, B180, B110L, Q30, Q50 |
| F5 | Q12: OPAL + L3, weakest variants, lowest literature rate: p < 1e-3 (needs OPAL weakest >= about 0.11; prior 60 %) |

What each outcome means: F5 PASS gives the light-scalar corner a second exclusion from a second
detector (OPAL's Higgs search is in no headline number here, so OPAL's data enter the Q12
constraint only through this test). F5 FAIL leaves
Q12 resting on L3 alone, and the paper will say so.

## 7. What this means

Four LEP1 detectors, about 12 million hadronic Z decays, and selections built for two isolated
leptons plus hadrons leave room for at most about 5-7 % of an ALEPH-sized boson with typically
isolated muons; L3 and DELPHI alone exclude it even at the lowest rate in the literature.
Together with the four-fermion measurements (NOTE-fourfermion.md) and ALEPH's own description of
its events (NOTE-kinematics.md), this says: **the excess cannot be a boson radiated off b quarks,
Z -> h A, or either of the two models designed to escape the LHC bound (a Z' coupling b to a heavy
vector-like quark, and Z -> Z' phi), decaying to isolated muons, at anything like the rate the
excess needs.** If the excess is real, its muons sit inside the b jets, which points to a b-jet
effect (for example cascade decays or a mismodelled background shape) or to a state that decays
inside a jet, rather than to the boson models tested here. DELPHI's open data test that
directly (PLAN.md, tests A and B).

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

kly-v1 (written in 0.5, graded in 0.6):

| | expectation | result | grade |
|---|---|---|---|
| K1 | all unit tests of test_kly pass | 11 of 11 ok | **PASS** |
| K2 | B110: eps(L3) >= 0.30 and eps(DELPHI) >= 0.40 | 0.553; 0.706 | **PASS** |
| K3 | B110: L3 + DELPHI, every candidate, lowest literature rate: p < 1e-4 | 1.3e-10 | **PASS** |
| K4 | B180 and B110L: L3 and DELPHI within 0.10 of B110 | B180 0.549 / 0.727; B110L 0.552 / 0.716 (largest difference 0.021) | **PASS** |
| K5 | Q30: eps(L3) >= 0.30, eps(DELPHI) >= 0.40, eps(ALEPH96) < 0.10 | 0.588; 0.789; 0.018 | **PASS** |
| K6 | Q12: eps(DELPHI) < 0.05, eps(L3) >= 0.25, L3 alone lowest rate p < 1e-3 | 0.034; 0.604; 1.4e-9 | **PASS** |
| K7 | Q50: eps(L3) >= 0.30, eps(DELPHI) >= 0.40; L3 + DELPHI lowest rate p < 1e-4 | 0.420; 0.683; 1.3e-8 | **PASS** |
| K8 | B110 and Q30: nearer muon within 15 deg of a jet in <= 15 % of events | 4.3 %; 4.5 % | **PASS** |
| K9 | events above the weight maximum <= 1 % of accepted parton events | 0 in every model | **PASS** |

Nine of nine passed. The hand estimate behind K3 (about 24 events, p ~ 1e-9) was close to the
measured 26.05 events and p = 1.3e-10.

kly4f-v1: expectations F1-F5 in section 6b; grades will be added here when the job returns.

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
6. **Models.** Three explicit models (NOTE-kinematics.md) and Ko, Li and Yu's models II and III
   (section 6; model III at three scalar masses, not a full scan; the Z Z' phi vertex taken as
   g^{mu nu}). Another production mechanism with a different recoil spectrum would need its own
   efficiency. A scalar lighter than 12 GeV gives an even softer recoil; L3's selection has no
   recoil cut, so we expect it to keep such events too, but this was not computed.
7. **What is not covered.** A source whose muons sit inside the b jets passes none of these
   selections. That is what ALEPH describes, and what DELPHI's open data test directly.

## 10. Code

`analysis/efhz.py` 0.1.0 (ALEPH), `analysis/run_efhz.py`, `analysis/test_efhz.py` (12 tests).
`analysis/lephz.py` 0.1.0: the L3, DELPHI and OPAL selections, ALEPH's via efhz (one definition),
candidate compatibility, predictions and the combined confrontation; `analysis/test_lephz.py`
(14 tests); `analysis/run_lephz.py`. `analysis/kly.py` 0.1.0: Ko, Li and Yu's models II and III;
`analysis/test_kly.py` (11 tests); `analysis/run_kly.py`. `analysis/run_kly4f.py` 0.1.0 and
`analysis/test_kly4f.py` (4 tests): the four-fermion selections of eff4f on the same events. Run:
`python -m unittest -v test_efhz test_lephz test_kly test_kly4f`, then
`python run_efhz.py --out OUT --nsig 10000 --workers 2`,
`python run_lephz.py --out OUT --nsig 8000 --workers 2`,
`python run_kly.py --out OUT --nsig 8000 --workers 2` and
`python run_kly4f.py --out OUT --nsig 8000 --workers 2` (need `numpy`, `pythia8mc`, and eff4f.py,
lep4f.py and the xkin modules alongside). Outputs: `analysis/results/efhz/`,
`analysis/results/lephz/`, `analysis/results/kly/` (and `analysis/results/kly4f/` when kly4f-v1
returns).

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
counts, for the three boson models of NOTE-kinematics.md and Ko, Li and Yu's models II and III,
with expectations written before each calculation. (Lane and Pritchett, arXiv:1701.07376, favour
a two-Higgs-doublet variant with h and eta_A nearly degenerate near 30 GeV; we have not read how
they produce it at LEP1, so we do not claim to cover it beyond its resemblance to our Z -> h A.)
