# NOTE-higgs-searches: do the four LEP1 Higgs searches leave room for a 30 GeV boson?

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.4, 2026-11-18 (0.1-0.3 earlier the same day).
Made with AI agents working in MV2's name. Not an ALEPH, DELPHI, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** Section 3 is a hand calculation written before any
efficiency was measured; sections 4 and 5 are measured (jobs `efhz-v1` and `lephz-v1`, both
returned 2026-11-18). Expectations J1-J7 and L1-L10 (section 7) were written before those jobs
ran. Text CC BY 4.0, code Apache-2.0.

**What changed in 0.4.** Job `lephz-v1` measured how much of each boson model the L3, DELPHI and
OPAL Higgs searches would have kept. **All ten expectations L1-L10 passed.** L3's search, which
has no recoil-mass cut and found **no** candidate in 3.05 million hadronic Z decays, keeps 0.54,
0.54 and 0.64 of the vector, scalar and Z -> h A events; DELPHI's keeps 0.74, 0.69 and 0.82.
L3 and DELPHI together, **without ALEPH**, at the lowest rate quoted in the literature for the
excess and counting every candidate as signal, predict 25-30 boson events against 1 observed
(p = 2e-12 to 3e-10 per model). The scalar model that ALEPH's own search could not exclude
(version 0.3) is excluded by L3 and DELPHI. Section 5 also shows a rough calibration against the
experiments' own published Higgs efficiencies and a reading question about L3's selection; neither
changes the conclusion.

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
| L3, PLB 385 (1996) 454 | 3.05M hadronic Z, 1991-94 | > 4 tracks, >= 8 clusters, thrust < 0.92; p1 + p2 > 20, each > 3.4 GeV; BOTH muons isolated (D < 2.5 each, D1 D2 < 0.25; calorimeter cones); **no m_mumu or recoil cut** | **0** (high-mass selection) |
| DELPHI, NPB 421 (1994) 3 | 935,616 hadronic Z, 1991-92 | >= 6 charged; p > 5 each, p_max > 10 GeV, opening > 30 deg; recoil > 15, visible rest mass > 10 GeV; >= 2 jets; muons > 40 / > 20 deg from jets | 1: recoil 27.8 +- 1.9 GeV |
| OPAL, ZPC 73 (1997) 189 | ~160 pb^-1 to 1995 (3.5M hadronic Z used, conservative) | 5 < p < 30 GeV each, sum > 20; E_vis > 80 GeV; displaced vertex; a recoil-mass cut whose value is not stated; isolation of PLB 327 (1994) 397 | 1: recoil 61.2 +- 1.0 GeV, p = 19.3, 7.3 GeV |

Published efficiencies for the Higgs signal itself (Z* -> mu mu) at m_H = 30-60 GeV: L3 32-37 %,
DELPHI 53-55 %, ALEPH 48 % at 60 GeV, OPAL 9-31 %.

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
   of item 2: p = 4.7e-7 / 1.5e-6 / 2.6e-8.
4. *A reading question about L3.* The reading agent reported L3's expected background for the
   high-mass mu mu H0 selection as "0.65 +- 0.11 events (e+e- -> mu+mu- qq, recoil > 30 GeV)".
   Our reading of the cuts has no recoil cut. If L3 did require recoil > 30 GeV, it would keep
   about 81 % of V, 60 % of S and at least 95 % of P events (interpolated from the job's recoil
   quantiles). Stacking this on items 2 and 3: p = 4e-6 / **8e-5** / 5e-8.

The most pessimistic combination we can construct, for the scalar, still has p = 8e-5 (3.8
standard deviations). OPAL97 is shown for completeness but is not used in any headline number:
its recoil-cut value is not stated and its calibration ratio is the worst (0.62).

**Independence.** The L3 Higgs search (1991-94) shares data with L3's four-fermion measurement
(1991-92), and OPAL's two analyses share data too, so these are separate selections, not
independent data sets. DELPHI's 1991-92 data are in neither four-fermion constraint. DELPHI's
search alone, at the lowest literature rate, predicts 7.7 / 7.2 / 8.5 events against 1 (p = 3.9e-3
/ 6.3e-3 / 2.0e-3): a second detector, on its own, excludes all three models at 99 %.

## 6. What this means

Four LEP1 detectors, about 12 million hadronic Z decays, and selections built for two isolated
leptons plus hadrons leave room for at most about 5-7 % of an ALEPH-sized boson with typically
isolated muons; L3 and DELPHI alone exclude it even at the lowest rate in the literature.
Together with the four-fermion measurements (NOTE-fourfermion.md) and ALEPH's own description of
its events (NOTE-kinematics.md), this says: **the excess cannot be a boson radiated off b quarks
or Z -> h A, decaying to isolated muons, at anything like the rate the excess needs.** If the
excess is real, its muons sit inside the b jets, which points to a b-jet effect (for example
cascade decays or a mismodelled background shape) or to a state that decays inside a jet, rather
than to these boson models. DELPHI's open data test that directly (PLAN.md, tests A and B).

## 7. Expectations, written before the jobs ran, and grades

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

## 8. Limits (read before citing)

1. **Readings.** The cuts come from AI reading agents' summaries of scanned papers; a few values
   are interpretations (readings/lephz-notes.md, last section; section 5 item 4 above).
2. **Generator level.** Hadron level (Pythia 8), no detector simulation. Isolation is computed
   from generator particles. Muon identification is a common factor 0.86 per muon (ALEPH's).
   Section 5 item 3 compares with the experiments' own efficiencies (ratios 0.62-0.90).
3. **Stand-ins.** ALEPH's 1996 b-tag as a factor 0.8 (bracketed by 0.4); OPAL's vertex as 0.5;
   L3 muon acceptance |cos theta| < 0.8; DELPHI |cos theta| < 0.9 and Durham y_cut 0.02; L3's
   E_jet as the energy in a 25 deg cone. Variants bracket each.
4. **Candidates.** Signal-compatibility uses only the recoil mass (and, for OPAL, the momenta).
5. **Rate.** The boson rate is the excess's own (lep4f readings: central, low hadronic count with
   yield minus 1 sigma, lowest literature value).
6. **Models.** Three explicit models (NOTE-kinematics.md). Another production mechanism with a
   different recoil spectrum would need its own efficiency.
7. **What is not covered.** A source whose muons sit inside the b jets passes none of these
   selections. That is what ALEPH describes, and what DELPHI's open data test directly.

## 9. Code

`analysis/efhz.py` 0.1.0 (ALEPH), `analysis/run_efhz.py`, `analysis/test_efhz.py` (12 tests).
`analysis/lephz.py` 0.1.0: the L3, DELPHI and OPAL selections, ALEPH's via efhz (one definition),
candidate compatibility, predictions and the combined confrontation; `analysis/test_lephz.py`
(14 tests); `analysis/run_lephz.py`. Run: `python -m unittest -v test_efhz test_lephz`, then
`python run_efhz.py --out OUT --nsig 10000 --workers 2` and
`python run_lephz.py --out OUT --nsig 8000 --workers 2` (need `numpy`, `pythia8mc`, and eff4f.py,
lep4f.py and the xkin modules alongside). Outputs: `analysis/results/efhz/`,
`analysis/results/lephz/`.

## 10. Prior art

INSPIRE (queried 2026-11-18): 22 papers cite arXiv:1610.06536 (record 1492968). None cites any of
the five LEP1 Higgs-search papers used here (records 420342, 357422, 423697, 421562, 374451), and
none uses an isolated-lepton sample. The closest work is L3's own re-analysis of muon pairs in
b-tagged hadronic events (arXiv:1905.01111), which looks at the same non-isolated signature as
ALEPH. As far as we can find, the Higgs searches have not been confronted with the excess before.
