# NOTE-higgs-searches: does ALEPH's own LEP1 Higgs search leave room for a 30 GeV boson?

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.1, 2026-11-18. Made with AI agents working in
MV2's name. Not an ALEPH, DELPHI, L3 or OPAL Collaboration result. **No physicist has checked this
note yet.** Section 3 is a hand calculation; job `efhz-v1` measures the efficiency it needs, and
expectations J1-J7 (section 4) were written before that job ran. Text CC BY 4.0, code Apache-2.0.

## 1. The argument

NOTE-fourfermion.md compared a boson reading of the ALEPH 30 GeV dimuon excess (arXiv:1610.06536
v9: 32.31 +- 10.87 b-tagged events at 30.40 GeV) with the LEP1 measurements of
e+e- -> mu+ mu- q qbar by OPAL and L3. Those use other detectors and 1-3.5 million Z decays.

There is a larger and closer sample: **the Standard Model Higgs searches of LEP1**. In
e+e- -> H Z*, Z* -> l+ l-, each experiment selected two energetic leptons, at least one isolated,
recoiling against hadrons. That is what a boson X -> mu+ mu- produced with b quarks gives.
ALEPH's final LEP1 search (Phys. Lett. B 384 (1996) 427, CERN-PPE/96-079) used "about 4.5
million hadronic Z decays" from 1989-1995 and found **three candidates in the H mu+ mu- channel,
consistent with the expected electroweak l+ l- q qbar background** (abstract). Two things make it
strong:

1. **Same detector.** No transfer of muon identification or acceptance between experiments.
2. **Same events.** The 1992-1995 Z-peak data in which arXiv:1610.06536 found the excess are part
   of the Higgs search's 1989-1995 sample. If the 32 excess events were boson decays with
   isolated muons, a fraction eps of them, the Higgs selection efficiency, would be among the
   three candidates. This needs no luminosity, b-tag or hadronic-count conversion at all
   ("subset" test below).

The other three experiments' LEP1 Higgs searches (OPAL Z. Phys. C 73 (1997) 189: about 160 pb^-1,
one mu+ mu- H0 candidate; L3 Phys. Lett. B 385 (1996) 454: about 3 million hadronic Z; DELPHI
Nucl. Phys. B 421 (1994) 3: about 1 million, four low-mass lepton-channel events) will be added
once their selections and candidate masses are read (reading tasks LEPHZ-A and LEPHZ-B).

## 2. The selection used here

ALEPH's 1996 paper has not been read yet. `analysis/efhz.py` 0.1.0 applies the H l+ l- cuts of
ALEPH's previous LEP1 Higgs paper (Phys. Lett. B 313 (1993) 299), read word for word on
2026-11-18 (readings/lep4f-papers-notes-3.md): each lepton p > 3 GeV; p1 + p2 > 20 GeV;
m_ll > 5 GeV; summed lepton momentum transverse to the thrust axis > 15 GeV; at least ONE lepton
isolated (no other charged track within 30 degrees and < 1 GeV of neutral energy, bremsstrahlung
photons excepted); >= 6 charged tracks (>= 8 if the missing energy exceeds 10 % of sqrt(s));
**recoil mass > 40 GeV**. Variants: both leptons isolated, recoil > 50 GeV, no recoil cut,
thrust axis from hadrons only, no transverse-momentum cut, |cos theta| < 0.9, p > 5 GeV, and all
the tight choices together (`strict`). The efficiency is defined as in eff4f: boson events inside
the acceptance behind ALEPH's rate (both muons p > 2.5 GeV, |cos theta| < 0.95) that pass, with
20 < m_mumu < 40 GeV, over all events in that acceptance. Hadron level (Pythia 8), no detector
simulation, muon identification as a factor.

**The Z -> h A model is out of reach of this selection.** In Z -> h A with m_h = m_A = 30.4 GeV,
the mass recoiling against the muon pair is m_h itself, 30.4 GeV, below the 40 GeV recoil cut.
The Higgs search cannot see it (expectation J4); the four-fermion measurements, which have no
recoil cut, still apply to it. For the radiation models (a vector or scalar X radiated off the b
quark) the recoil mass is the b bbar mass, sqrt(s - 2 sqrt(s) E_X + m_X^2), above 40 GeV when
E_X < 41.9 GeV.

## 3. Hand bound (before any efficiency is measured)

Observed: n = 3 candidates in the whole H mu mu channel, all masses, all counted as possible
signal, no background subtracted (conservative). 95 % CLs upper limit on signal events: 7.75.

| reading | predicted boson events for eps = 1 | eps allowed (95 % CLs) |
|---|---|---|
| rate, ALEPH central (R_acc 5.90e-5 per hadronic Z x 4.5M x 0.953 in 22-40 GeV x 0.86^2 muon ID) | 187 | < **0.041** |
| rate, low hadronic-count reading, yield minus 1 sigma | 107 | < 0.072 |
| rate, lowest literature value (Ko, Li, Yu: Br 1.1e-5) | 50 | < 0.155 |
| **subset**: the 32.31 excess events themselves (x 0.953) | 30.8 | < **0.25** |
| subset, if the Higgs search identifies only 0.86^2 of those muon pairs | 22.8 | < 0.34 |

If eps is about 0.5 for the radiation models, the rate reading predicts about 94 events where
ALEPH found 3 (p ~ 1e-36), the lowest literature rate about 25 (p ~ 4e-8), and the subset test
about 15 (p ~ 1.5e-4 at the central yield, weaker once the 34 % yield uncertainty is folded in;
`efhz` reports both).

## 4. Expectations for job efhz-v1 (written 2026-11-18, before it ran)

| | expectation |
|---|---|
| J1 | all 12 unit tests of test_efhz pass |
| J2 | eps(nominal) >= 0.30 for the vector (V) and scalar (S) radiation models |
| J3 | at least one muon isolated (ALEPH's definition) in >= 85 % of V and S events in acceptance |
| J4 | eps(nominal) < 0.05 for Z -> h A (P), because of the recoil cut; eps(norecoil, P) >= 0.30 |
| J5 | rate reading, ALEPH central: p < 1e-6 for V and S (nominal cuts); lowest literature rate: p < 1e-3 |
| J6 | subset test (id ratio 1): p < 0.05 for V and S with the yield uncertainty folded in (p_marginal) |
| J7 | the `strict` variant keeps eps >= 0.10 for V and S, so the conclusion does not hang on our reading of the 1993 cuts |

If J2, J5 and J6 pass, the statement becomes: *ALEPH's own LEP1 Higgs search, which contains the
data of the excess, excludes reading it as a boson radiated off b quarks that decays to isolated
muons.* If J6 fails but J5 passes, only the rate-based version holds. If any fails, the note will
say which cut removes the boson and by how much.

## 5. Limits (read before citing)

1. The 1996 selection is not yet read; the 1993 cuts and variants stand in. The reading task asks
   for the 1996 cuts and the masses of the three candidates.
2. The candidate count is from the abstract; their masses are not yet known, so all three are
   counted as possible signal.
3. Generator level: no detector simulation, isolation from generator particles (stricter than
   ALEPH's tracks and calorimeter clusters, so eps is if anything underestimated), muon
   identification as a factor.
4. The subset test assumes that the Higgs search's event sample contains the excess events (both
   are ALEPH Z-peak data of 1992-1995; the excess analysis uses later archived processing) and that
   the b-tag requirement of the excess does not change the isolation of its muons.
5. Model P (Z -> h A) is not tested by this selection (section 2).
6. What no isolated-lepton argument covers is a source whose muons sit inside the b jets, which
   is what arXiv:1610.06536 itself describes ("in all cases one of the two muons ... is closer
   than 15 deg to one of the leading jets"). DELPHI's open data test that directly (PLAN.md).

## 6. Code

`analysis/efhz.py` 0.1.0 (selection, counting, confrontation), `analysis/test_efhz.py` (12
tests on hand-built events: isolation by charged tracks, neutral energy, bremsstrahlung and
neutrinos; the recoil mass; the multiplicity rule with missing energy; the thrust-axis transverse
momentum; the predictions and p-values), `analysis/run_efhz.py` (Pythia 8 events of the three
xkin models, wall-clock budget, partial results). Needs `eff4f.py` and `lep4f.py` from
`analysis/` and `xme.py`, `evana.py`, `fadgen.py`, `run_xkin.py` from `xkin/`. Run:
`python -m unittest -v test_efhz` and `python run_efhz.py --out OUT`.

## 7. Prior art

INSPIRE (queried 2026-11-18): none of the 22 papers citing arXiv:1610.06536 (record 1492968) cites
any of the five LEP1 Higgs-search papers above (records 420342, 357422, 423697, 421562, 374451),
and none uses an isolated-lepton sample. The Higgs searches predate the excess by twenty years.
