# NOTE-higgs-searches: do the four LEP1 Higgs searches leave room for a 30 GeV boson?

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.3, 2026-11-18 (0.1 and 0.2 earlier the same day).
Made with AI agents working in MV2's name. Not an ALEPH, DELPHI, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** Section 3 is a hand calculation; section 4 is the
measured ALEPH efficiency (job `efhz-v1`, returned 2026-11-18). Job `lephz-v1` (all four
experiments) is still queued. Expectations J1-J7 and L1-L10 (section 6) were written before those
jobs ran. Text CC BY 4.0, code Apache-2.0.

**What changed in 0.3.** `efhz-v1` measured how much of each boson model ALEPH's own LEP1 Higgs
search would have kept. The answer splits by model. A **vector** radiated off the b quark is kept
at eps = 0.50 and is excluded by ALEPH's search alone under every rate reading (nominal
selection). A **scalar** radiated
off the b quark is kept at only eps = 0.27, because ALEPH's recoil-mass cut (> 40 GeV) removes
65 % of it; ALEPH alone then excludes it at the excess's central rate but **not** at the lowest
rate quoted in the literature, nor when only the 32 excess events themselves are used. Three of
the seven expectations written beforehand failed, all for the scalar (J2, J6, J7). We also found
an omission of our own: efhz 0.1.0 left out the cost of ALEPH's 1996 b-tag requirement; section 4
shows the numbers with it. Z -> h A is invisible to ALEPH's search, as expected (eps = 0.02); L3's
search, which has no recoil cut, is the one that tests it (lephz-v1).

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
| OPAL, ZPC 73 (1997) 189 | ~160 pb^-1 to 1995 (3.5M hadronic Z used, conservative) | 5 < p < 30 GeV each, sum > 20; E_vis > 80 GeV; displaced vertex; isolation and dilepton/hadronic-mass cuts of PLB 327 (1994) 397 | 1: recoil 61.2 +- 1.0 GeV, p = 19.3, 7.3 GeV |

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
requirement. Events for eps = 1: **ALEPH 149.7, L3 126.9, DELPHI 38.9** (OPAL 72.8). 95 % CLs
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
At least one muon is isolated in 92 % (V), 95 % (S) and 97 % (P) of events.

**Confrontation with ALEPH's three candidates** (all counted as signal, b = 0; p = Poisson
probability of 3 or fewer). efhz 0.1.0 predicts without any b-tag loss; ALEPH 1996 required an
event-level b-tag (P_uds < 0.05) on its high-recoil candidates, whose efficiency for these events
we do not know. We show it bracketed by factors 0.8 and 0.4 (computed by hand from efhz's
predictions):

| model | rate reading | predicted (b-tag 1 / 0.8 / 0.4) | p (b-tag 1 / 0.8 / 0.4) |
|---|---|---|---|
| V | central | 93.1 / 74.5 / 37.2 | 5e-36 / 3e-28 / 6e-13 |
| V | lowest literature | 24.8 / 19.8 / 9.9 | 4.7e-8 / 3.7e-6 / **0.011** |
| S | central | 50.5 / 40.4 / 20.2 | 2.7e-18 / 3.4e-14 / 2.7e-6 |
| S | lowest literature | 13.5 / 10.8 / 5.4 | 7.2e-4 / 5.7e-3 / **0.21** |

Counting only the two signal-compatible candidates changes S at the lowest rate to 1.4e-3 (0.8)
and 0.095 (0.4).

**Subset reading** (the 32.31 +- 10.87 excess events are themselves in the search's data; no
luminosity conversion; marginalised over the excess's uncertainty; assumes every excess event
also passes ALEPH 1996's b-tag): V p = 0.02, S p = 0.10. The largest efficiency that three
candidates allow at 95 % CLs is 0.041 at the central rate and 0.25 in the subset reading.

**What this says.** ALEPH's own Higgs search, on its own, excludes the vector reading with the
nominal selection under every rate reading and b-tag stand-in, at 95 % or better (with the
`strict` selection it does so only at the central rate: p = 0.16 at the lowest rate), and the
scalar reading at the excess's central rate. It does **not** exclude the scalar at the lowest literature rate if the b-tag cost is near 0.4, nor in the
subset reading. So ALEPH alone is a weaker test than the four-fermion measurements
(NOTE-fourfermion.md: OPAL + L3, no recoil cut, p < 5e-12 at the lowest rate). The full
four-experiment combination, with L3's search that has no recoil cut, is job lephz-v1.

## 5. What this means, if lephz confirms the hand bound

Four LEP1 detectors, about 12 million hadronic Z decays, and selections built for two isolated
leptons plus hadrons leave room for at most a few per cent of an ALEPH-sized boson with typically
isolated muons. Together with the four-fermion measurements, which have no recoil cut, and ALEPH's
own description of its events, this says: **the excess cannot be a boson radiated off b quarks or
Z -> h A, decaying to isolated muons, at anything like the rate the excess needs.** If the excess
is real, its muons sit inside the b jets, which points to a b-jet effect (for example cascade
decays or a mismodelled background shape) rather than a new particle. DELPHI's open data test that
directly (PLAN.md, tests A and B).

## 6. Expectations, written before the jobs ran, and grades

efhz-v1 (written in 0.1, graded in 0.3):

| | expectation | result | grade |
|---|---|---|---|
| J1 | all 12 tests pass | 12 of 12 ok | **PASS** |
| J2 | eps(nominal) >= 0.30 for V and S | V 0.498, **S 0.270** | **FAIL** (S) |
| J3 | >= 85 % of V and S events have at least one muon isolated | V 91.6 %, S 95.4 % | **PASS** |
| J4 | eps(nominal, P) < 0.05 and eps(norecoil, P) >= 0.30 | 0.018; 0.655 | **PASS** |
| J5 | rate reading p < 1e-6 (central), < 1e-3 (lowest rate) for V and S | V 5e-36, 4.7e-8; S 2.7e-18, 7.2e-4 | **PASS** as written (but see section 4: with the 1996 b-tag cost, S at the lowest rate is 5.7e-3 to 0.21) |
| J6 | subset p_marginal < 0.05 for V and S | V 0.02, **S 0.10** | **FAIL** (S) |
| J7 | `strict` keeps eps >= 0.10 for V and S | V 0.118, **S 0.036** | **FAIL** (S) |

All three failures have one cause: the recoil-mass cut, against the scalar model's harder boson.
Our expectation assumed the scalar's recoil spectrum would look like the vector's. It does not.

lephz-v1 (all four searches; lephz 0.1.0; written in 0.2, not yet graded):

| | expectation |
|---|---|
| L1 | all 14 unit tests of test_lephz pass |
| L2 | eps(L3 nominal) >= 0.15 for V and S |
| L3 | eps(DELPHI nominal) >= 0.20 for V and S |
| L4 | for P (Z -> h A): eps(L3 nominal) >= 0.15 and eps(DELPHI nominal) >= 0.20; eps(ALEPH96 nominal) < 0.05 |
| L5 | ALEPH + L3 + DELPHI, signal-compatible, central rate: p < 1e-6 for V and S |
| L6 | ALEPH + L3 + DELPHI, every candidate, lowest literature rate: p < 1e-3 for V and S |
| L7 | P: L3 + DELPHI, every candidate, central rate: p < 1e-3 |
| L8 | fewer than 8 % of V and S events in acceptance and window have recoil > 65.2 GeV |
| L9 | the weakest L3 variant (jet40, cos0.72, bgo_em, nothrust) keeps eps >= 0.10 for V and S |
| L10 | the weakest DELPHI variant (ycut0.005, iso_both40, cos0.95) keeps eps >= 0.10 for V and S |

Note added in 0.3, before lephz returns (no change to L1-L10): efhz shows S at 0.27 and P at 0.02
for ALEPH. lephz's ALEPH prediction uses the b-tag factor 0.8; we will also report it at 0.4 and
the combination without ALEPH. The DELPHI selection needs recoil > 15 GeV only, and L3's none, so
we still expect L2-L4 to pass; L8 is consistent with efhz (V 95th percentile of the recoil 59.4 GeV).

## 7. Limits (read before citing)

1. **Readings.** The cuts come from AI reading agents' summaries of scanned papers; a few values
   are interpretations (readings/lephz-notes.md, last section).
2. **Generator level.** Hadron level (Pythia 8), no detector simulation. Isolation is computed
   from generator particles. Muon identification is a common factor 0.86 per muon (ALEPH's).
3. **Stand-ins.** ALEPH's 1996 b-tag as a factor 0.8 (bracketed here by 0.4); L3 muon acceptance
   |cos theta| < 0.8; DELPHI |cos theta| < 0.9 and Durham y_cut 0.02; L3's E_jet as the energy in
   a 25 deg cone. Variants bracket each.
4. **Candidates.** Signal-compatibility uses only the recoil mass (and, for OPAL, the momenta).
5. **Rate.** The boson rate is the excess's own (lep4f readings: central, low hadronic count with
   yield minus 1 sigma, lowest literature value).
6. **Models.** Three explicit models (NOTE-kinematics.md). Another production mechanism with a
   different recoil spectrum would need its own efficiency.
7. **What is not covered.** A source whose muons sit inside the b jets passes none of these
   selections. That is what ALEPH describes, and what DELPHI's open data test directly.

## 8. Code

`analysis/efhz.py` 0.1.0 (ALEPH), `analysis/run_efhz.py`, `analysis/test_efhz.py` (12 tests).
`analysis/lephz.py` 0.1.0: the L3, DELPHI and OPAL selections, ALEPH's via efhz (one definition),
candidate compatibility, predictions and the combined confrontation; `analysis/test_lephz.py`
(14 tests); `analysis/run_lephz.py`. Run: `python -m unittest -v test_efhz test_lephz`, then
`python run_efhz.py --out OUT --nsig 10000 --workers 2` and `python run_lephz.py --out OUT` (need
`numpy`, `pythia8mc`, and eff4f.py, lep4f.py and the xkin modules alongside).

## 9. Prior art

INSPIRE (queried 2026-11-18): 22 papers cite arXiv:1610.06536 (record 1492968). None cites any of
the five LEP1 Higgs-search papers used here (records 420342, 357422, 423697, 421562, 374451), and
none uses an isolated-lepton sample. The closest work is L3's own re-analysis of muon pairs in
b-tagged hadronic events (arXiv:1905.01111), which looks at the same non-isolated signature as
ALEPH. As far as we can find, the Higgs searches have not been confronted with the excess before.
