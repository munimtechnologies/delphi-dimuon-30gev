# NOTE-fourfermion: what LEP1's published four-fermion counts say about the 30 GeV excess

MV2 of Munim, Inc. (mv2@munimtech.com), 2026-11-17. Made with AI agents working in MV2's name.
Not a DELPHI, ALEPH, L3 or OPAL Collaboration result. **No physicist has checked this note yet.**
The numbers below are hand calculations. The job `lep4f-v1` runs `analysis/lep4f.py` and its
tests and prints the exact values. This note will be updated with them, and with any
correction.
Text CC BY 4.0, code Apache-2.0.

## The argument in one paragraph

Suppose the 32.31 b-tagged dimuon events that arXiv:1610.06536 fits at 30.40 GeV were a new boson
X produced in Z -> b bbar X, X -> mu+ mu-. Then ALEPH's own efficiencies fix how often such an
event occurs, with both muons in ALEPH's acceptance: about **5.9 x 10^-5 per hadronic Z decay**
(5.1 x 10^-5 under the paper's "2.2M expected" reading). Our kinematic study (NOTE-kinematics.md,
xkin-v1) found both muons more than 20 degrees from every jet in 92-95 % of such events, in all
three boson models. An isolated, energetic muon pair in a hadronic event is the exact signature that
ALEPH, L3 and OPAL selected in the early 1990s to measure the Standard Model process
e+e- -> mu+ mu- q qbar at the Z pole. Their published counts agree with the Standard Model. They
would have contained tens to hundreds of boson events if their selections kept a sizeable
fraction of them.

## Inputs

ALEPH excess (arXiv:1610.06536 v9), as in `analysis/nexp.py` 0.2.0: N_sig = 32.31 +- 10.87,
N_had = 1.9M selected (2.2M "expected"), hadronic efficiency 0.9748, muon identification 0.86 per
muon, b-tag 0.38. Rate of boson events with both muons in acceptance, per produced hadronic Z:

    R_acc = 32.31 / (1.9e6 / 0.9748) / (0.86^2 x 0.38) = 5.898e-5      (low reading: 5.094e-5)

LEP1 mu+ mu- q qbar results, from hep-ex/9611015 (table 1) and the papers' abstracts:

| experiment | paper | data | hadronic Z | observed | SM expected |
|---|---|---|---|---|---|
| ALEPH | Z. Phys. C 66 (1995) 3 | 1989-93, 79 pb-1 | "almost two million" (2.0M used) | 19 | 13 + 0 |
| OPAL | Phys. Lett. B 376 (1996) 315 | 132.4 pb-1 | not in abstract; 3.53M (scaled with L3's ratio) | 28 | 20 + 8 |
| L3 | Phys. Lett. B 321 (1994) 283 | 36 pb-1 | "960 000" | 6 | 5 + 0 |

(Expected = Standard Model signal + background. The review quotes residual uncertainties on the
predictions "of the order of 10%".)

## Result (hand values; exact values from lep4f-v1)

The boson events in each count would be N_X = R_acc x N_Z x eps, where eps is that analysis'
efficiency for such an event (muon identification, isolation, momentum and quality cuts). eps was
never published for this topology. A 95 % CLs upper limit s_up on extra events (Poisson,
b known) turns each count into the **largest efficiency at which an ALEPH-sized boson is still
allowed**:

| | s_up (95 % CLs) | N_X if eps = 1 | eps_max (nominal) | eps_max (low reading) |
|---|---|---|---|---|
| OPAL | 12.2 | 208 | **0.059** | 0.068 |
| ALEPH 1989-93 | 15.0 | 118 | 0.13 | 0.15 |
| L3 | 7.3 | 57 | 0.13 | 0.15 |
| all three, one common eps | 21.2 | 383 | **0.055** | 0.064 |

So an ALEPH-sized boson survives OPAL's published count only if OPAL's mu mu q qbar selection
kept fewer than about **1 in 17** of its events. It survives the three counts together only if
each selection kept fewer than about 1 in 18. At ALEPH's central value minus one standard
deviation (21.4 events), the bounds loosen by a factor 1.51, to about 0.09 for OPAL.

For scale, the selection needs two identified muons (about 0.7-0.8 for a pair at LEP), both
isolated from the jets (92-95 % for the boson models at 20 degrees), and a few momentum and
multiplicity cuts that a 30 GeV dimuon in a b bbar event passes easily. Our expectation is an
efficiency of a few tens of percent, not a few percent. If that holds, the published LEP1 counts
already exclude the reading of the excess as a boson that decays to isolated muons. It holds
under both readings of ALEPH's normalisation, and independently of ALEPH's own data: OPAL and L3
are separate experiments.

## How this fits with the kinematic result

NOTE-kinematics.md asks whether ALEPH's 32 events look like a boson. ALEPH reports a muon within 15
degrees of a jet "in all cases", which allows at most about 4-10 boson events. This note asks
whether the boson's events show up where they should, in other experiments' isolated-dimuon
samples. They don't, unless those selections were very inefficient for them. The two arguments
use different events and different detectors, and they agree.

Neither argument covers a source of the excess whose muons sit inside the b jets (for example a
cascade or a mismeasured b-decay pair). DELPHI tests A and B (PLAN.md) test that
directly in b-tagged events.

## Prior art

We found no paper that confronts the 30 GeV excess with the LEP1 four-fermion measurements.
Lane and Pritchett (arXiv:1701.07376) discuss the muon-jet angles and Z -> 4 mu, but not the
l l q q counts. Ko, Li and Yu (arXiv:1610.07526) compare parton-level kinematics. The L3 study
(Hebbeker and Roth, arXiv:1905.01111) repeats the b-tagged spectrum. The four-fermion papers
predate the excess by twenty years.

## Limits of this note (read before citing)

1. **eps is not known.** This note bounds it. It does not measure it. The original selections
   (lepton momentum and isolation cuts, the ALEPH isolation-angle sum, any recoil or pair-mass
   requirement) are in the papers, which we have not yet read in full. A cut that removed
   30 GeV pairs, or muon pairs recoiling against b jets, would weaken the bound. The review says
   no l l mass cut was used in the l l q q channels.
2. OPAL's hadronic Z count is scaled from its luminosity with L3's ratio (about +-10 %).
3. ALEPH's 1989-93 four-fermion data overlap the 1992-93 part of the 1992-95 sample in which the
   excess was found, so the ALEPH row is not independent of the excess. OPAL and L3 are.
4. The counts are as listed in a 1996 review, table 1. They should be confirmed against the
   original papers.
5. The isolation fractions come from generator-level models with Pythia 8 hadronisation
   (xkin-v1), not detector simulation.

## What comes next

- **Test C for DELPHI (to be pre-registered in plan v1.0):** the isolated selection without the b-tag.
  Both muons more than 20 degrees from every jet above 3 GeV, any b-tag, data blinded in 26-35 GeV.
  It needs no assumption about another experiment's efficiency. Its irreducible background is
  e+e- -> mu mu q qbar, which DELPHI simulated with EXCALIBUR for every year (CERN Open Data
  records 81032, 81072, 81146, 81459, 81539; sigma = 3.56 pb). Job `dimu-fourf-v1` runs those
  files and four KK2f Z -> q qbar files through the published ntuple code and
  `analysis/iso4f.py`, which uses dimusel's own selection, reads simulation only and is tested
  against dimusel. Hand forecast: an ALEPH-sized boson gives on the order of 100 isolated events
  in DELPHI's 1992-95 data, so the background must stay well below that for test C to be
  decisive. dimu-fourf-v1 measures it.
- Read the selection sections of the three papers and replace the bound with an estimated eps.
