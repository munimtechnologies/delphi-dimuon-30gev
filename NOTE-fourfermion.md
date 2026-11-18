# NOTE-fourfermion: what LEP1's published four-fermion data say about the 30 GeV excess

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.4, 2026-11-18 (0.1 and 0.2 on 2026-11-17, 0.3
earlier on 2026-11-18). Made with AI agents working in MV2's name. Not a DELPHI, ALEPH, L3 or OPAL
Collaboration result. **No physicist has checked this note yet.** Text CC BY 4.0, code Apache-2.0.

**What changed in 0.4: the efficiencies are measured, and every expectation written before the
job ran (H1-H7) passed.** Job `lep4f-eff-v2` (2026-11-18, output in
[analysis/results/](analysis/results/)) applied the published OPAL, L3 and ALEPH mu+ mu- q qbar
selections to 10,000 Pythia 8 events of each of the three boson models. OPAL's selection keeps
**84-88 %** of the boson events that fall in ALEPH's acceptance, L3's 59-68 %, ALEPH's 58-71 %
(muon identification not included). The boson would survive the OPAL and L3 mass distributions
only below 2.5 % (section 4). So an ALEPH-sized boson predicts **124-129 events in OPAL's
20-40 GeV bins, where OPAL shows one**, and 150-156 events in OPAL and L3 together, where they
show one. Even at the lowest rate quoted for the excess, with the least favourable variant of
every unread cut, the OPAL + L3 p-value is below 5 x 10^-12.

## 1. The argument in one paragraph

Suppose the 32.31 b-tagged dimuon events that arXiv:1610.06536 fits at 30.40 GeV were a new boson
X produced in Z -> b bbar X, X -> mu+ mu-. ALEPH's own efficiencies then fix how often such an
event occurs, with both muons in ALEPH's acceptance: about **5.9 x 10^-5 per hadronic Z decay**
(5.1 x 10^-5 under the paper's "2.2M expected" reading). Our kinematic study (NOTE-kinematics.md,
xkin-v1) found both muons more than 20 degrees from every jet in 92-95 % of such events, in all
three boson models. An isolated, energetic muon pair in a hadronic event is the exact signature that
ALEPH, L3 and OPAL selected in the early 1990s to measure the Standard Model process
e+e- -> mu+ mu- q qbar at the Z pole. **What those papers show of the dimuon mass: OPAL has one
selected mu mu q qbar event between 20 and 40 GeV, and L3 has none.** Applied to the boson
models, their selections keep most of the boson's events, so an ALEPH-sized boson would have put
about 150 events there.

## 2. Inputs

ALEPH excess (arXiv:1610.06536 v9), as in `analysis/nexp.py` 0.2.0: N_sig = 32.31 +- 10.87,
N_had = 1.9M selected (2.2M "expected"), hadronic efficiency 0.9748, muon identification 0.86 per
muon, b-tag 0.38 (event-level working point). Rate of boson events with both muons in acceptance,
per produced hadronic Z:

    R_acc = 32.31 / (1.9e6 / 0.9748) / (0.86^2 x 0.38) = 5.898e-5      (low reading: 5.094e-5)

**Lowest reading.** Ko, Li and Yu (arXiv:1610.07526) quote Br(Z -> b bbar mu+ mu-) ~ 1.1 x 10^-5
for the ALEPH excess. That is close to the raw yield (32 events over the 2.7-3.1 million Z decays
behind ALEPH's sample) before correcting for the b-tag and muon identification; corrected, it would
be about 4 x 10^-5. We still carry it as a third reading: 1.1e-5 / 0.69911 = **1.573 x 10^-5 per
hadronic Z**, taken as if every such event were inside ALEPH's acceptance. (In the job 88-92 % of
the generated events are; counting only those would lower the lowest-reading predictions by about
10 %, which does not change any conclusion below.)

LEP1 mu+ mu- q qbar results at the Z pole. Counts from hep-ex/9611015 (table 1), confirmed in each
paper; selections and mass information from two independent readings of the papers (2026-11-17,
section 7):

| | ALEPH, Z. Phys. C 66 (1995) 3 (CERN-PPE/94-169) | OPAL, Phys. Lett. B 376 (1996) 315 (CERN-PPE/96-031) | L3, Phys. Lett. B 321 (1994) 283 |
|---|---|---|---|
| data | 1989-93, 79 pb-1, "almost two million" hadronic Z | 132.4 pb-1 at the Z pole (3.53M Z, scaled with L3's ratio) | 1991-92, 36 pb-1, 960,000 hadronic Z |
| observed / expected | 19 / 13 | 28 / 28.2 (signal 20.0, (gamma) f fbar 8.2) | 6 / 5.0 +- 0.2 |
| multiplicity | ">= six good charged particle tracks" | N_trk >= 8; >= 2 Durham jets; >= 2 hadronic tracks with dE/dx inconsistent with an electron | - |
| lepton momentum | "energetic", number in ref. 20 (PLB 313 (1993) 299), not read | p >= 5 GeV each, abs(p1) + abs(p2) >= 15 GeV | p >= 3 GeV |
| isolation | < 1 GeV in a 30 deg cone | alpha_1 >= 30 deg, alpha_2 >= 10 deg; alpha = largest cone with E_cone < 1 GeV, E_cone from tracks and unassociated EM clusters, without the nearest other lepton | min D_mu < 0.4 (D = E_jet / p_mu - 1); min ECAL energy in 3-15 deg < 0.7 GeV |
| muon polar angle | - | not stated (tracking covers 98 % of 4 pi); OPAL muon ID (Z. Phys. C 58 (1993) 523): abs(cos theta) < 0.9 | taken as 40-140 deg (generator cut) |
| cut on m(l l) | none | none | none |
| **m(mu mu) in 20-40 GeV** | no mu-mu-only plot; Fig. 13b, e e + mu mu together: 2 in 20-30, 2 in 30-40 | **Fig. 3b, final selection: 1 in 20-30, 0 in 30-40** (0-10: 19, 10-20: 3, 40-80: 5; sum 28) | **0** (Fig. 7a: 0-10: 1, 10-20: 1, 60-70: 2, 80-90: 2) |

OPAL quotes 4.1 +- 0.2 % efficiency for the whole generated phase space of the Standard Model
process, which is dominated by soft and collinear lepton pairs radiated off the quarks (19 of its 28
events have m(mu mu) below 10 GeV). That number is not the efficiency for a boson; section 4 measures
that.

## 3. Bound from the totals (version 0.1; exact values from job lep4f-v1, 11/11 tests)

N_X = R_acc x N_Z x eps boson events would sit in each published count. With 95 % CLs upper limits
on extra events (Poisson, expected background known), the largest efficiency at which an
ALEPH-sized boson is still allowed:

| | s_up (95 % CLs) | N_X if eps = 1 | eps_max (nominal) | eps_max (low reading) |
|---|---|---|---|---|
| OPAL | 12.2 | 208 | **0.059** | 0.068 |
| ALEPH 1989-93 | 15.0 | 118 | 0.13 | 0.15 |
| L3 | 7.3 | 57 | 0.13 | 0.15 |
| all three, one common eps | 21.2 | 383 | **0.055** | 0.064 |

The measured efficiencies of section 4 (0.59-0.88) are ten or more times these limits.

## 4. Bound from the mass distributions, with measured efficiencies

A 30.4 GeV boson's dimuon mass falls between 20 and 40 GeV (95 % of the generated Breit-Wigner
lies in 22-40 GeV; LEP's dimuon mass resolution at 30 GeV is a few hundred MeV). We count every
event the papers show in 20-40 GeV as possible signal and assume no Standard Model background
there; both choices weaken the limits. 95 % CLs upper limits on boson events (b = 0): OPAL n = 1,
s_up = 4.74; L3 n = 0, s_up = 3.00; OPAL + L3 n = 1, s_up = 4.74; ALEPH (e e and mu mu together)
n = 4, s_up = 9.15.

Predicted boson events in 20-40 GeV = R x N_Z x 0.953 x eps_kin x 0.86^2, where eps_kin is the
fraction of boson events in ALEPH's acceptance that pass a selection (hadron level), and 0.86^2 is
ALEPH's muon identification, used for all three.

**Measured eps_kin** (`lep4f-eff-v2`; 8,400-9,200 events in acceptance per model; binomial errors
about 0.005). V = vector radiated off the b, S = scalar radiated off the b, P = Z -> h A:

| model | OPAL | L3 | ALEPH | before the job: allowed below (OPAL + L3, central / lowest rate) |
|---|---|---|---|---|
| V | 0.844 | 0.644 | 0.577 | 0.025 / 0.095 |
| S | 0.865 | 0.592 | 0.668 | 0.025 / 0.095 |
| P | 0.877 | 0.677 | 0.712 | 0.025 / 0.095 |

**Confrontation** (nominal cuts; predicted events in 20-40 GeV, observed in brackets; p = Poisson
probability of observing that few or fewer):

| reading of the rate | model | OPAL (1) | L3 (0) | OPAL + L3 (1) | p (OPAL + L3) | ALEPH 1989-93 (4) |
|---|---|---|---|---|---|---|
| central | V / S / P | 123.9 / 127.1 / 128.8 | 25.7 / 23.7 / 27.0 | **149.6 / 150.7 / 155.9** | 2e-63 / 5e-64 / 3e-66 | 48.0 / 55.5 / 59.2 |
| low count, yield - 1 sigma | V / S / P | 71.0 / 72.8 / 73.8 | 14.7 / 13.6 / 15.5 | 85.7 / 86.4 / 89.3 | 5e-36 / 3e-36 / 1e-37 | 27.5 / 31.8 / 33.9 |
| lowest (Ko-Li-Yu) | V / S / P | 33.1 / 33.9 / 34.4 | 6.9 / 6.3 / 7.2 | **39.9 / 40.2 / 41.6** | 2e-16 / 1e-16 / 4e-17 | 12.8 / 14.8 / 15.8 |

**Variants** for the cuts we could not read exactly (OPAL eps_kin, model V / S / P): no
multiplicity cuts 0.857 / 0.886 / 0.892; Durham y_cut 0.005 unchanged; nearest-particle isolation
0.857 / 0.872 / 0.883; both isolation angles >= 30 deg **0.579 / 0.659 / 0.707** (the strictest);
abs(cos theta) < 0.9 0.765 / 0.770 / 0.804; < 0.98 unchanged; version 0.1.0's stricter energy
counting 0.852 / 0.883 / 0.889. L3: jet cone 40 deg 0.637 / 0.589 / 0.677; abs(cos theta) < 0.7
0.537 / 0.472 / 0.564. ALEPH: momentum cut 2 or 5 GeV unchanged; abs(cos theta) < 0.9
0.522 / 0.591 / 0.650. **Least favourable case** over every variant, OPAL + L3, lowest rate:
p = 4.5e-12 (V), 3.7e-13 (S), 2.5e-14 (P), i.e. about 6.8 standard deviations or more.

### Grading of the expectations written before the job ran (version 0.2/0.3)

| | expectation | result | grade |
|---|---|---|---|
| H1 | all 22 unit tests pass, none skipped | 21 of 21 pass, none skipped. The test file has 21 tests; "22" in versions 0.2-0.3 was a miscount on our side, not a missing test | PASS (count corrected) |
| H2 | eps_kin(OPAL nominal) >= 0.30, all models | 0.844 / 0.865 / 0.877 | PASS |
| H3 | eps_kin(L3 nominal) >= 0.25, all models | 0.644 / 0.592 / 0.677 | PASS |
| H4 | predicted OPAL events in 20-40 GeV >= 20, all models (central) | 123.9 / 127.1 / 128.8 | PASS |
| H5 | OPAL + L3 p < 1e-6 central; < 1e-3 at low count, yield - 1 sigma | <= 2e-63; <= 5e-36 | PASS |
| H6 | lowest rate: p < 1e-3 nominal; < 0.05 in every variant | <= 2e-16; worst variant 4.5e-12 | PASS |
| H7 | eps_kin(OPAL nominal) / eps_kin(OPAL no multiplicity cuts) >= 0.95 | 0.985 / 0.976 / 0.983 | PASS |

H2-H6 pass, so the statement written in advance holds: **the published OPAL and L3 four-fermion
measurements exclude the interpretation of the ALEPH excess as a boson produced with b quarks
that decays to isolated muons**, at the excess's own rate and at the lowest rate quoted for it,
for all three boson models, within the limits of section 7.

## 5. How this fits with the kinematic result, and with ALEPH's own description

NOTE-kinematics.md asks whether ALEPH's 32 events look like a boson. arXiv:1610.06536 v9 (section
4) says: "We found that in all cases one of the two muons from di-muons is closer than 15 deg to one
of the leading jets", and, of the excess itself, "We find that each of the two muons which form the
excess around 30 GeV are also close to one of the leading jets". The boson models put a muon within
15 degrees of a leading jet in only 5-11 % of events (xkin-v1), so at most about 4-10 of the 32
events can be such a boson. This note asks the reverse question, in other detectors: do the
boson's events show up where they must, in isolated-dimuon samples? They do not. The two
arguments use different events and different detectors, and they agree.

What neither argument covers is a source whose muons sit inside the b jets, which is what ALEPH's
own description points to: cascade decays, a mismodelled b-decay background shape, or a new state
that decays inside a jet. DELPHI tests A and B (PLAN.md) test that directly in b-tagged events,
with no isolation. NOTE-higgs-searches.md adds a third, independent constraint from the LEP1 Higgs
searches (efficiency jobs still queued).

## 6. Prior art

We found no paper that confronts the 30 GeV excess with the LEP1 four-fermion measurements. None of
the 22 papers that INSPIRE lists as citing arXiv:1610.06536 (checked 2026-11-18) uses LEP1
l l q q data, OPAL data or isolated-lepton samples. Lane and Pritchett (arXiv:1701.07376)
discuss the muon-jet angles and Z -> 4 mu. Ko, Li and Yu (arXiv:1610.07526) compare parton-level
kinematics and LHC constraints. The L3 study (arXiv:1905.01111) repeats the b-tagged spectrum.
ATLAS searched for a b j mu mu resonance at 26-30 GeV at the LHC. The four-fermion papers predate
the excess by twenty years.

## 7. Limits of this note (read before citing)

1. **The mass counts were read off the papers' figures by AI reading agents** working for MV2,
   from scanned preprints, twice and independently (2026-11-17). Both readings agree on OPAL
   (1 event in 20-30 GeV, 0 in 30-40 GeV, after the final selection; the bins add up to the 28
   observed events) and on L3 (0 in 20-40 GeV; the bins add up to the 6 observed events). No
   person has checked them yet. Even if OPAL had 5 events in 20-40 GeV, the central predictions
   would exceed its limit (10.5) by more than ten times.
2. **Hadron level, no detector simulation.** Isolation is computed from generator particles;
   muon identification is a common 0.86 per muon (ALEPH's). Unread details (OPAL's Durham y_cut,
   ALEPH's momentum cut, the muon polar-angle acceptances) are covered by the variants of
   section 4; the least favourable one still gives p < 5e-12.
3. OPAL's hadronic Z count is scaled from its luminosity with L3's ratio (about +- 10 %).
4. ALEPH's 1989-93 four-fermion data overlap the 1992-93 part of the 1992-95 sample in which the
   excess was found, so the ALEPH row is not independent of the excess. OPAL and L3 are.
5. The boson models are those of NOTE-kinematics.md (vector or scalar radiated off the b quark;
   Z -> h A). A model whose muons are not isolated is not covered, by construction.

## 8. Code and reproduction

`analysis/eff4f.py` 0.2.0 (selections), `analysis/run_eff4f.py` (runner), `analysis/test_eff4f.py`
(21 tests), `analysis/lep4f.py` 0.1.0 (rates and CLs limits), with `xkin/xme.py` 0.2.0,
`xkin/evana.py`, `xkin/fadgen.py`, `xkin/run_xkin.py`. Command:
`python run_eff4f.py --out OUT --nsig 10000 --workers 2` (Pythia 8.318 via `pythia8mc`, numpy).
The job's printed output and full JSON summary, with the sha256 of every source file, are in
`analysis/results/lep4f-eff-v2-run.txt` and `analysis/results/lep4f-eff-v2-summary.json`.

## 9. What comes next

- A short paper, "The LEP1 four-fermion measurements and the 30 GeV dimuon excess" (draft in
  [paper/](paper/)), to be read by a particle physicist before it is submitted anywhere.
- NOTE-higgs-searches 0.3 when its efficiency jobs return.
- **Test C for DELPHI (to be pre-registered in plan v1.0):** the isolated selection without the
  b-tag, data blinded in 26-35 GeV, with the four-fermion background from DELPHI's EXCALIBUR
  simulation (job `dimu-fourf-v1`). It needs no assumption about another experiment's
  efficiency.
