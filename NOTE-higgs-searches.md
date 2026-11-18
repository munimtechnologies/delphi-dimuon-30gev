# NOTE-higgs-searches: do the four LEP1 Higgs searches leave room for a 30 GeV boson?

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.2, 2026-11-18 (0.1 earlier the same day).
Made with AI agents working in MV2's name. Not an ALEPH, DELPHI, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** Sections 3-4 are hand calculations. Jobs `efhz-v1`
(ALEPH) and `lephz-v1` (all four experiments) measure the efficiencies they need; expectations
J1-J7 and L1-L10 (section 5) were written before those jobs ran. Text CC BY 4.0, code Apache-2.0.

**What changed in 0.2.** The selections and candidates of all four LEP1 searches have now been
read (readings/lephz-notes.md). ALEPH's three H mu mu candidates have Higgs (recoil) masses of
49.7, 51.5 and 66.9 GeV. The third is too heavy to come from a 30 GeV dimuon. L3's high-mass
mu mu H0 selection, which has **no recoil-mass cut** and therefore also tests Z -> h A, found
**no candidate** in 3.05 million hadronic Z. DELPHI found one mu mu event in 0.94 million. OPAL
found one, with m_mumu = 16.8 GeV. `analysis/lephz.py` 0.1.0 codes the L3, DELPHI and OPAL
selections next to ALEPH's (efhz).

## 1. The argument

The ALEPH 30 GeV dimuon excess (arXiv:1610.06536 v9: 32.31 +- 10.87 b-tagged events at 30.40
GeV, Gamma 1.78 GeV) has been read as a new boson X -> mu+ mu- produced with b quarks (a vector
or scalar radiated off the b line, or Z -> h A). At hadron level, such a boson's muons are
isolated from the jets in about 90-95 % of events (NOTE-kinematics.md, NOTE-fourfermion.md).

Two energetic isolated leptons recoiling against hadrons is exactly what the LEP1 Standard Model
Higgs searches selected in e+e- -> H Z*, Z* -> l+ l-. All four LEP experiments ran this search
on their full Z-peak data and found a handful of candidates, consistent with background. An
ALEPH-sized boson would have put of order a hundred events into these samples (section 3).
ALEPH's own search contains the 1992-95 data in which the excess was found.

## 2. The four searches

| search | data | selection (short; full text in readings/lephz-notes.md) | candidates |
|---|---|---|---|
| ALEPH, PLB 384 (1996) 427 | ~4.5M hadronic Z, 1989-95 | each lepton p > 3, sum > 20 GeV, m_ll > 5, sum pT to thrust > 15 GeV; ONE lepton isolated (30 deg cone); >= 6 tracks; recoil > 40 GeV; b-tag P_uds < 0.05 | 3: recoil 49.7, 51.5, 66.9 GeV |
| L3, PLB 385 (1996) 454 | 3.05M hadronic Z, 1991-94 | > 4 tracks, >= 8 clusters, thrust < 0.92; p1 + p2 > 20, each > 3.4 GeV; BOTH muons isolated (D < 2.5 each, D1 D2 < 0.25; calorimeter cones); **no m_mumu or recoil cut** | **0** (high-mass selection) |
| DELPHI, NPB 421 (1994) 3 | 935,616 hadronic Z, 1991-92 | >= 6 charged; p > 5 each, p_max > 10 GeV, opening > 30 deg; recoil > 15, visible rest mass > 10 GeV; >= 2 jets; muons > 40 / > 20 deg from jets | 1: recoil 27.8 +- 1.9 GeV |
| OPAL, ZPC 73 (1997) 189 | ~160 pb^-1 to 1995 (3.5M hadronic Z used, conservative) | 5 < p < 30 GeV each, sum > 20; E_vis > 80 GeV; displaced vertex; recoil and isolation cuts from PLB 327 (1994) 397 (not read) | 1: recoil 61.2 +- 1.0 GeV, p = 19.3, 7.3 GeV |

Published efficiencies for the Higgs signal itself (Z* -> mu mu) at m_H = 30-60 GeV: L3 32-37 %,
DELPHI 53-55 %, ALEPH 48 % at 60 GeV, OPAL 9-31 %. Z -> H Z* with m_H = 40-60 GeV and
m(Z*) ~ 30 GeV is kinematically close to the boson events, apart from the muons' isolation.

**Which candidates can be signal.** The mass recoiling against a muon pair of mass m is at most
sqrt(s) - m (beam constraint; neutrinos and ISR photons only lower it). A boson event with
m_mumu >= 26 GeV (ALEPH's peak minus 2.5 widths) has a recoil mass of at most 65.2 GeV. ALEPH's
66.9 +- 0.3 GeV candidate is about 5.7 standard deviations above that, so it is not counted. For the
OPAL candidate the muon momenta fix the dimuon mass: m^2 = M_rec^2 - s + 2 sqrt(s)(p1 + p2), which
gives 16.8 GeV (6.4-23.0 GeV for the recoil within 2 sigma), so it is not counted either. The
two other ALEPH candidates and the DELPHI event are counted as possible signal, with no
background subtracted. Rule "all" counts every candidate (conservative variant).

**Z -> h A.** The recoil mass is m_h = 30.4 GeV: below ALEPH's 40 GeV cut, but L3's high-mass
selection has no recoil cut and DELPHI's needs only > 15 GeV. So L3 and DELPHI test it.

## 3. Hand bound (common efficiency eps; before any efficiency is measured)

Prediction for a search = R_acc x N_had x f_gen x eps x ID^2 x b-tag factor, with R_acc =
5.90e-5 boson events per hadronic Z in ALEPH's acceptance (lep4f, central reading), f_gen =
0.953 (the 22-40 GeV part of the Breit-Wigner), ID^2 = 0.86^2 (muon identification stand-in),
b-tag factor 0.8 for ALEPH 1996 (its P_uds cut on events that contain b bbar; stand-in) and 0.5
for OPAL's vertex requirement. Events for eps = 1: **ALEPH 149.7, L3 126.9, DELPHI 38.9** (OPAL
72.8). 95 % CLs limits with b = 0: s_up = 3.00, 4.74, 6.30, 7.75, 9.15, 10.51 for n = 0-5.

| combination | n counted | predicted for eps = 1 | eps allowed (95 % CLs) |
|---|---|---|---|
| **ALEPH + L3 + DELPHI**, signal-compatible, ALEPH central rate | 3 | 315.5 | **< 0.025** |
| same, every candidate counted | 4 | 315.5 | < 0.029 |
| same, low hadronic-count reading and yield minus 1 sigma | 3 | 180.8 | < 0.043 |
| same, lowest literature rate (Br 1.1e-5, Ko, Li, Yu) | 3 | 84.2 | < 0.092 |
| same, lowest literature rate, every candidate counted | 4 | 84.2 | < 0.109 |
| **L3 alone** (0 candidates; also tests Z -> h A) | 0 | 126.9 | **< 0.024** |
| L3 + DELPHI (the searches that test Z -> h A) | 1 | 165.8 | < 0.029 |
| L3 + DELPHI, lowest literature rate | 1 | 44.2 | < 0.107 |
| ALEPH subset: the 32 excess events themselves (2 compatible) | 2 | 30.8 | < 0.205 |
| all four, every candidate counted | 5 | 388.3 | < 0.027 |

If the true efficiency is near that for the Higgs signal (0.3-0.5), ALEPH + L3 + DELPHI predict
about 95-160 boson events where 3 compatible candidates exist (p ~ 1e-36 at eps = 0.3), and
about 25 at the lowest literature rate (p ~ 3e-8). For Z -> h A at eps = 0.3, L3 + DELPHI
predict about 50 events against 1 (p ~ 1e-20); at the lowest literature rate, about 13
(p ~ 2e-5).

What would save the boson reading: efficiencies near 2-3 % (or 10 % at the lowest rate), i.e.
muons that are almost never isolated. That is what ALEPH itself reports for its events ("in all
cases one of the two muons ... is closer than 15 deg to one of the leading jets"), and it is not
what any of the three explicit boson models gives (NOTE-kinematics.md).

## 4. What this means, if the jobs confirm it

Four independent LEP1 detectors, about 12 million hadronic Z decays, and selections built for
two isolated leptons plus hadrons leave room for at most a few per cent of an ALEPH-sized boson
with typically isolated muons. Together with the four-fermion measurements
(NOTE-fourfermion.md), which have no recoil cut, and ALEPH's own description of its events,
this says: **the excess cannot be a boson radiated off b quarks or Z -> h A, decaying to
isolated muons, at anything like the rate the excess needs.** If the excess is real, its muons
must sit inside the b jets, which points to a b-jet effect (for example cascade decays or a
mismodelled background shape) rather than a new particle. DELPHI's open data test that directly
(PLAN.md, tests A and B).

## 5. Expectations, written before the jobs ran

efhz-v1 (ALEPH only, 1993-paper cuts; written in 0.1, unchanged): J1 all 12 tests pass; J2
eps(nominal) >= 0.30 for V and S; J3 >= 85 % of V and S events have at least one muon isolated;
J4 eps(nominal, P) < 0.05 and eps(norecoil, P) >= 0.30; J5 rate reading p < 1e-6 (central) and
< 1e-3 (lowest literature rate) for V and S; J6 subset p_marginal < 0.05 for V and S; J7 the
`strict` variant keeps eps >= 0.10 for V and S. (efhz still counts all three ALEPH candidates;
lephz counts the two compatible ones.)

lephz-v1 (all four searches; lephz 0.1.0):

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

If L2, L3, L5 and L6 pass, the conclusion of section 4 holds for V and S; with L4 and L7 also
for Z -> h A. If any fails, the next version will say which cut removes the boson and by how
much, and the statement will be narrowed accordingly.

## 6. Limits (read before citing)

1. **Readings.** The cuts come from AI reading agents' summaries of scanned papers; a few values
   are interpretations (readings/lephz-notes.md, last section). OPAL's recoil and isolation cuts
   were not read, so OPAL is outside the nominal combination.
2. **Generator level.** Hadron level (Pythia 8), no detector simulation. Isolation is computed
   from generator particles; calorimeter cones count all visible energy (stricter than the
   detectors). Muon identification is a common factor 0.86 per muon (ALEPH's), not each
   experiment's own.
3. **Stand-ins.** ALEPH's 1996 b-tag as a factor 0.8; L3 muon acceptance |cos theta| < 0.8;
   DELPHI |cos theta| < 0.9 and Durham y_cut 0.02 for its jets; L3's E_jet as the energy in a
   25 deg cone. Variants bracket each.
4. **Candidates.** Signal-compatibility uses only the recoil mass (and, for OPAL, the momenta).
   Counting all five candidates as signal changes the bounds by at most 20 % (section 3).
5. **Rate.** The boson rate is the excess's own (lep4f readings: central, low hadronic count with
   yield minus 1 sigma, lowest literature value). Each search's hadronic Z count is from its
   paper; OPAL's is a conservative conversion.
6. **What is not covered.** A source whose muons sit inside the b jets passes none of these
   selections. That is what ALEPH describes, and what DELPHI's open data test directly.

## 7. Code

`analysis/efhz.py` 0.1.0 (ALEPH; 0.1 of this note). `analysis/lephz.py` 0.1.0: the L3, DELPHI and
OPAL selections (cut by cut), ALEPH's via efhz (one definition), candidate compatibility, the
predictions and the combined CLs/Poisson confrontation. `analysis/test_lephz.py`: 14 tests on
hand-built events (L3 calorimeter isolation and the D product; L3's missing recoil cut; DELPHI's
muon-jet angles, jets, opening angle and recoil; OPAL's momentum window and visible energy; the
candidate rule; agreement of the Durham jets with eff4f and of the ALEPH prediction with efhz).
`analysis/run_lephz.py` runs Pythia 8 events of the three xkin models with a wall-clock budget
and writes partial counts. Run: `python -m unittest -v test_lephz` and
`python run_lephz.py --out OUT` (needs `numpy`, `pythia8mc`, and efhz.py, eff4f.py, lep4f.py,
xme.py, evana.py, fadgen.py, run_xkin.py alongside).

## 8. Prior art

INSPIRE (queried again 2026-11-18): 22 papers cite arXiv:1610.06536 (record 1492968). None cites
any of the five LEP1 Higgs-search papers used here (records 420342, 357422, 423697, 421562,
374451), and none uses an isolated-lepton sample. The closest work is L3's own re-analysis of
muon pairs in b-tagged hadronic events (arXiv:1905.01111), which looks at the same non-isolated
signature as ALEPH and does not cite the Higgs searches. The Higgs searches predate the excess by
twenty years; as far as we can find, they have not been confronted with it before.
