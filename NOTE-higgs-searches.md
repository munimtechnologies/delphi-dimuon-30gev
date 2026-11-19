# NOTE-higgs-searches: do the four LEP1 Higgs searches leave room for a 30 GeV boson?

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.7, 2026-11-19 (0.1-0.6 on 2026-11-18).
Made with AI agents working in MV2's name. Not an ALEPH, DELPHI, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** Section 3 is a hand calculation written before any
efficiency was measured; sections 4, 5, 6 and 6b are measured (jobs `efhz-v1`, `lephz-v1`,
`kly-v1` and `kly4f-v1`). Section 6c pre-registers a new job (`kly4fj-v1`, queued) whose
expectations G1-G6 are written below before it runs. Expectations J1-J7, L1-L10, K1-K9 and F1-F5
(section 8) were written before their jobs ran. Text CC BY 4.0, code Apache-2.0.

**What changed in 0.7.**
1. *Second test of the light-scalar corner returned (section 6b): all five expectations F1-F5
   passed.* Job `kly4f-v1` ran the same events as kly-v1 through the LEP1 four-fermion
   selections. OPAL's keeps 0.82-0.89 of every Ko-Li-Yu model, including model III with a 12 GeV
   scalar (0.851), because it has no recoil-mass cut. At the models' own rate, OPAL + L3 predict
   38-41 events in 20-40 GeV against one (p = 6e-17 to 1.2e-15); with the weakest variant of each
   selection, p <= 1.8e-9 for every model and 1.7e-14 for the 12 GeV scalar.
2. *A caveat found in grading, stated before anything else is claimed (section 6b).* The risk
   named in 0.6 (that the light scalar's b quarks merge into one jet and fail OPAL's two-jet
   requirement) was **not** actually tested: eff4f clusters jets with the two isolated muons
   included, so every event has at least two jets. Whether OPAL removed the leptons before jet
   finding is not in our reading. Until that is settled, the second exclusion of the 12 GeV corner
   is conditional. Section 6c pre-registers the job that measures it (`kly4fj-v1`) and the rule
   that decides; a blind reading of OPAL's paper has been requested.
3. *Lane and Pritchett's model is covered.* NOTE-lane-pritchett.md (2026-11-18) found that their
   two-Higgs-doublet model is produced at LEP1 only as Z -> h eta_A with both states at 30 GeV,
   which is our model P; every P closure here applies to it (section 11).

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

## 6b. Light-scalar corner, second test: the four-fermion selections (job kly4f-v1, returned 2026-11-19)

**Why** (written in 0.6, before the job ran). For Q12 the only constraint is L3's Higgs search,
which shares its 1991-92 data with L3's four-fermion measurement. OPAL's four-fermion measurement
(3.53M hadronic Z, 1 event between 20 and 40 GeV) is a different detector and has no recoil-mass
cut. NOTE-fourfermion.md found its selection keeps 84-88 % of our V, S and P events. If it also
keeps Q12 events, OPAL alone gives a second, independent exclusion of the light-scalar corner.
Hand estimate (0.6): about 39.2 (OPAL) and 10.7 (L3) events for efficiency 1 at the lowest
literature rate; risk for Q12: the scalar (about 41 GeV energy) decays to b quarks about 35 deg
apart, near the threshold for merging into one jet at y_cut = 0.02.

**What the job did.** `analysis/run_kly4f.py` 0.1.0 applied eff4f.py's OPAL, L3 and ALEPH
four-fermion selections (eff4f 0.2.0, one definition, all variants) to the **same events** as
kly-v1. All 4 unit tests passed; every model reproduced kly-v1's hadronised and failed counts
exactly; the job took 4 minutes on 2 CPUs. Outputs and sha256 of every source file:
`analysis/results/kly4f/`.

**Efficiency and confrontation** (eps in ALEPH's acceptance and the 20-40 GeV window, no muon
identification; "lit" = the lowest literature rate, model II's own; observed in 20-40 GeV: OPAL
1, L3 0; b = 0):

| model | OPAL nominal | OPAL weakest | L3 nominal | L3 weakest (cos0.7) | OPAL + L3, nominal, lit: predicted, p | OPAL + L3, weakest, lit: predicted, p | OPAL alone, weakest, lit: p |
|---|---|---|---|---|---|---|---|
| B110 | 0.857 | 0.659 (both_30deg) | 0.607 | 0.491 | 40.02, 1.7e-16 | 31.02, 1.1e-12 | 1.7e-10 |
| B180 | 0.860 | 0.664 (both_30deg) | 0.596 | 0.480 | 40.02, 1.7e-16 | 31.14, 9.7e-13 | 1.3e-10 |
| B110L | 0.859 | 0.611 (both_30deg) | 0.634 | 0.521 | 40.38, 1.2e-16 | 29.49, 4.7e-12 | 9.9e-10 |
| **Q12** | **0.851** | **0.769 (cos0.9)** | **0.612** | **0.487** | **39.84, 2.0e-16** | **35.30, 1.7e-14** | **2.6e-12** |
| Q30 | 0.890 | 0.733 (both_30deg) | 0.582 | 0.449 | 41.07, 6.2e-17 | 33.48, 1.0e-13 | 1.0e-11 |
| Q50 | 0.817 | 0.468 (both_30deg) | 0.566 | 0.466 | 38.02, 1.2e-15 | 23.31, 1.8e-9 | 2.1e-7 |

Hand checks of two numbers: Q12 nominal, 0.8508 x 39.171 + 0.6116 x 10.651 = 33.33 + 6.51 =
39.84 events, P(n <= 1) = e^-39.84 x 40.84 = 4.99e-18 x 40.84 = 2.0e-16; Q12 weakest, 0.7688 x
39.171 + 0.4866 x 10.651 = 30.11 + 5.18 = 35.30, e^-35.30 x 36.30 = 1.7e-14. Both match the job.

**Robustness, by hand.** The four-fermion selections have no published efficiency for a boson to
calibrate against (NOTE-fourfermion.md). Scaling OPAL's weakest efficiency by 0.62 (the worst
calibration ratio found for any LEP1 Higgs selection, OPAL's own) and L3's by 0.78 gives, for
Q12, 18.67 + 4.04 = 22.71 events against 1, p = e^-22.71 x 23.71 = 3.3e-9. For p to reach 1e-3
the predicted count must fall to 9.23 events, i.e. our OPAL + L3 efficiency for Q12 would have to
be 3.8 times too high.

**The caveat found in grading.** The hand estimate's risk was OPAL's ">= 2 Durham jets"
requirement. The job reports that no event in any model has fewer than two jets at y_cut 0.02,
and the reason is in the code, not the physics: eff4f clusters all seen particles, **the two
isolated muons included**, and two well-separated 10-40 GeV muons always form two jets. Our
reading of OPAL's selection (NOTE-fourfermion.md, section 2) lists ">= 2 Durham jets" but does not
say whether the leptons were removed before jet finding, nor what y is normalised to. If OPAL
clustered only the hadrons, a 12 GeV scalar's hadrons would often form one jet: for two clusters
with an opening angle below 90 deg, y <= m^2 / E_norm^2, which for m = 12 GeV is 144 / 8281 =
0.017 when y is normalised to the full 91 GeV (below 0.02), but up to about 0.09 when normalised
to the hadronic energy (about 40 GeV). So the result for Q12 hangs on a selection detail we have
not read. The other five models are not affected (their hadronic systems are heavy).

**Status of the light-scalar corner.** Closed by L3's Higgs search alone (section 6; 3.8-4.4
standard deviations in the most pessimistic readings). The second, OPAL-based exclusion above
(p = 1.7e-14 with the weakest variants) holds **if** OPAL's jet finding included the leptons or
normalised y to the hadronic energy; section 6c measures the other case and fixes the rule.

## 6c. Light-scalar corner: OPAL's jets without the muons (job kly4fj-v1, queued; expectations written before it runs)

**What the job does.** `analysis/run_kly4fj.py` 0.1.0 regenerates the same events (same seeds,
generator and Pythia settings), re-applies eff4f 0.2.0 (closure: n_acc and the OPAL and L3
nominal counts must equal kly4f-v1's), recomputes eff4f's all-particle jet count with its own
Durham code (must agree event by event), and adds three OPAL variants that require OPAL:nominal
AND at least two Durham jets **among the hadrons only** (the two signal muons removed):
`hj_full02` (y_cut 0.02, y normalised to the whole event's visible energy), `hj_had02` (y_cut
0.02, normalised to the hadrons' visible energy), `hj_full005` (y_cut 0.005, whole event). It
also records the y at which the last two hadronic clusters merge.

| | expectation |
|---|---|
| G1 | all unit tests pass; in every model n_acc, OPAL:nominal and L3:nominal counts equal kly4f-v1's, and the all-particle jet count agrees with eff4f's in every event |
| G2 | B110, B180, B110L, Q30, Q50: eps(OPAL:hj_full02) >= 0.60 (prior 85 %) |
| G3 | Q12: eps(OPAL:hj_full02) < 0.20 (prior 75 %) |
| G4 | Q12: eps(OPAL:hj_had02) >= 0.50 (prior 65 %) |
| G5 | Q12: eps(OPAL:hj_full005) >= 0.40 (prior 65 %) |
| G6 | **decision**: Q12, OPAL (hj_full02) + L3 four-fermion weakest variant, lowest literature rate, 1 observed: p < 1e-3, which needs eps(OPAL:hj_full02) >= about 0.104 (prior 25 %) |

**Decision rule, fixed now.** Which variant is OPAL's real selection is a reading question. A
blind reading of OPAL's paper (CERN-PPE/96-031) has been requested. (a) If it says jets were
found on all tracks and clusters (leptons included), eff4f nominal stands and section 6b's second
exclusion holds. (b) If it says the leptons were removed and y normalised to the hadronic energy,
`hj_had02` (or `hj_full005` for y_cut 0.005) becomes nominal and its row decides. (c) If it says
the leptons were removed and y normalised to the whole visible energy or to sqrt(s), or if the
paper does not say, the second exclusion is claimed only if G6 passes; otherwise the 12 GeV
corner rests on L3's Higgs search alone, and the paper says so.

## 7. What this means

Four LEP1 detectors, about 12 million hadronic Z decays, and selections built for two isolated
leptons plus hadrons leave room for at most about 5-7 % of an ALEPH-sized boson with typically
isolated muons; L3 and DELPHI alone exclude it even at the lowest rate in the literature.
Together with the four-fermion measurements (NOTE-fourfermion.md and section 6b) and ALEPH's own
description of its events (NOTE-kinematics.md), this says: **the excess cannot be a boson radiated
off b quarks, Z -> h A (which covers Lane and Pritchett's model), or either of the two models
designed to escape the LHC bound (a Z' coupling b to a heavy vector-like quark, and Z -> Z' phi),
decaying to isolated muons, at anything like the rate the excess needs.** Every case is excluded
by at least two detectors except Z -> Z' phi with a scalar near 12 GeV, which L3 alone excludes
for certain and OPAL excludes under the jet definition we coded (section 6c settles it). If the
excess is real, its muons sit inside the b jets, which points to a b-jet effect (for example
cascade decays or a mismodelled background shape) or to a state that decays inside a jet, rather
than to the boson models tested here. DELPHI's open data test that directly (PLAN.md, tests A
and B).

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

kly4f-v1 (written in 0.6, graded in 0.7):

| | expectation | result | grade |
|---|---|---|---|
| F1 | all 4 unit tests pass; every model has kly-v1's n_hadronised and n_fail | 4 of 4 ok; closure true in all six (7675/325, 7688/312, 7786/214, 8000/0 x 3) | **PASS** |
| F2 | B110, B180, B110L, Q30, Q50: eps(OPAL) >= 0.60 and eps(L3) >= 0.40 | OPAL 0.817-0.890; L3 0.566-0.634 | **PASS** |
| F3 | Q12: eps(L3) >= 0.40; eps(OPAL) recorded (prior 50 % that it is >= 0.30) | L3 0.612; OPAL 0.851 | **PASS** (see the caveat in 6b) |
| F4 | OPAL + L3, nominal, lowest literature rate: p < 1e-6 for B110, B180, B110L, Q30, Q50 | 6.2e-17 to 1.2e-15 | **PASS** |
| F5 | Q12: OPAL + L3, weakest variants, lowest literature rate: p < 1e-3 | 1.7e-14 (OPAL weakest 0.769) | **PASS as written; conditional on OPAL's jet definition (6b, 6c)** |

Five of five passed. The hand estimate (39.2 and 10.7 events at efficiency 1) matched the job's
39.17 and 10.65. The risk the hand estimate named for F5 was not exercised by the code; that is
stated in 6b and tested in 6c.

kly4fj-v1: expectations G1-G6 in section 6c; grades will be added here when the job returns.

## 9. Limits (read before citing)

1. **Readings.** The cuts come from AI reading agents' summaries of scanned papers; a few values
   are interpretations (readings/lephz-notes.md, last section). L3's lack of a recoil cut was
   read twice, independently. OPAL's four-fermion jet definition (which particles are clustered,
   what y is normalised to) has not been read; it decides the second test of the 12 GeV corner.
2. **Generator level.** Hadron level (Pythia 8), no detector simulation. Isolation is computed
   from generator particles. Muon identification is a common factor 0.86 per muon (ALEPH's).
   Section 5 item 3 compares with the experiments' own efficiencies (ratios 0.62-0.90).
3. **Stand-ins.** ALEPH's 1996 b-tag as a factor 0.8 (bracketed by 0.4); OPAL's vertex as 0.5;
   L3 muon acceptance |cos theta| < 0.8; DELPHI |cos theta| < 0.9 and Durham y_cut 0.02; L3's
   E_jet as the energy in a 25 deg cone. Variants bracket each.
4. **Candidates.** Signal-compatibility uses only the recoil mass (and, for OPAL, the momenta).
5. **Rate.** The boson rate is the excess's own (lep4f readings: central, low hadronic count with
   yield minus 1 sigma, lowest literature value, which is Ko, Li and Yu's model-II benchmark).
6. **Models.** Three explicit models (NOTE-kinematics.md), Ko, Li and Yu's models II and III
   (section 6; model III at three scalar masses, not a full scan; the Z Z' phi vertex taken as
   g^{mu nu}) and, through model P, Lane and Pritchett's Z -> h eta_A (NOTE-lane-pritchett.md).
   Another production mechanism with a different recoil spectrum would need its own efficiency.
   A scalar decaying to b bbar cannot be much lighter than about 10 GeV, so Q12 is near the
   lower end of model III's range; L3's Higgs selection has no recoil cut, so we expect it to
   keep 10-12 GeV scalars too, but this was not computed.
7. **What is not covered.** A source whose muons sit inside the b jets passes none of these
   selections. That is what ALEPH describes, and what DELPHI's open data test directly.

## 10. Code

`analysis/efhz.py` 0.1.0 (ALEPH), `analysis/run_efhz.py`, `analysis/test_efhz.py` (12 tests).
`analysis/lephz.py` 0.1.0: the L3, DELPHI and OPAL selections, ALEPH's via efhz (one definition),
candidate compatibility, predictions and the combined confrontation; `analysis/test_lephz.py`
(14 tests); `analysis/run_lephz.py`. `analysis/kly.py` 0.1.0: Ko, Li and Yu's models II and III;
`analysis/test_kly.py` (11 tests); `analysis/run_kly.py`. `analysis/run_kly4f.py` 0.1.0 and
`analysis/test_kly4f.py` (4 tests): the four-fermion selections of eff4f on the same events.
`analysis/run_kly4fj.py` 0.1.0 and `analysis/test_kly4fj.py` (8 tests, every expected number
worked by hand): OPAL's jets without the muons. Run:
`python -m unittest -v test_efhz test_lephz test_kly test_kly4f test_kly4fj`, then
`python run_efhz.py --out OUT --nsig 10000 --workers 2`,
`python run_lephz.py --out OUT --nsig 8000 --workers 2`,
`python run_kly.py --out OUT --nsig 8000 --workers 2`,
`python run_kly4f.py --out OUT --nsig 8000 --workers 2` and
`python run_kly4fj.py --out OUT --nsig 8000 --workers 2` (need `numpy`, `pythia8mc`, and eff4f.py,
lep4f.py and the xkin modules alongside). Outputs: `analysis/results/efhz/`,
`analysis/results/lephz/`, `analysis/results/kly/`, `analysis/results/kly4f/` (and
`analysis/results/kly4fj/` when kly4fj-v1 returns).

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
with expectations written before each calculation. Lane and Pritchett (arXiv:1701.07376) produce
their state at LEP1 only through Z -> h eta_A with both masses at 30 GeV (NOTE-lane-pritchett.md),
which is our model P, so their model is covered by the P closures.
