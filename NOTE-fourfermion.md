# NOTE-fourfermion: what LEP1's published four-fermion data say about the 30 GeV excess

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.2, 2026-11-17 (0.1 earlier the same day).
Made with AI agents working in MV2's name. Not a DELPHI, ALEPH, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** The numbers below are hand calculations. Job
`lep4f-v1` prints the exact values of section 3, and job `lep4f-eff-v1` measures the selection
efficiencies that section 4 needs. The note will be updated with their results and any correction.
Text CC BY 4.0, code Apache-2.0.

## 1. The argument in one paragraph

Suppose the 32.31 b-tagged dimuon events that arXiv:1610.06536 fits at 30.40 GeV were a new boson
X produced in Z -> b bbar X, X -> mu+ mu-. ALEPH's own efficiencies then fix how often such an
event occurs, with both muons in ALEPH's acceptance: about **5.9 x 10^-5 per hadronic Z decay**
(5.1 x 10^-5 under the paper's "2.2M expected" reading). Our kinematic study (NOTE-kinematics.md,
xkin-v1) found both muons more than 20 degrees from every jet in 92-95 % of such events, in all
three boson models. An isolated, energetic muon pair in a hadronic event is the exact signature that
ALEPH, L3 and OPAL selected in the early 1990s to measure the Standard Model process
e+e- -> mu+ mu- q qbar at the Z pole. **Version 0.2 adds what those papers show of the dimuon
mass: OPAL has at most one selected mu mu q qbar event between 20 and 40 GeV, and L3 has none.**
An ALEPH-sized boson would have put of order a hundred events there unless the selections kept
only a few per cent of them.

## 2. Inputs

ALEPH excess (arXiv:1610.06536 v9), as in `analysis/nexp.py` 0.2.0: N_sig = 32.31 +- 10.87,
N_had = 1.9M selected (2.2M "expected"), hadronic efficiency 0.9748, muon identification 0.86 per
muon, b-tag 0.38. Rate of boson events with both muons in acceptance, per produced hadronic Z:

    R_acc = 32.31 / (1.9e6 / 0.9748) / (0.86^2 x 0.38) = 5.898e-5      (low reading: 5.094e-5)

LEP1 mu+ mu- q qbar results at the Z pole. Counts from hep-ex/9611015 (table 1), confirmed for L3
in the paper; selections and mass information read from the papers on 2026-11-17 (section 7):

| | ALEPH, Z. Phys. C 66 (1995) 3 | OPAL, Phys. Lett. B 376 (1996) 315 | L3, Phys. Lett. B 321 (1994) 283 |
|---|---|---|---|
| data | 1989-93, 79 pb-1, "almost two million" hadronic Z | 132.4 pb-1 at the Z pole (3.53M Z, scaled with L3's ratio) | 1991-92, 36 pb-1, 960,000 hadronic Z |
| observed / expected | 19 / 13 | 28 / 28 | 6 / 5.0 +- 0.2 |
| lepton momentum | in the paper's ref. 20 (not read) | p >= 5 GeV each, p1 + p2 >= 15 GeV | p >= 3 GeV |
| isolation | < 1 GeV in a 30 deg cone | isolation angles >= 30 and >= 10 deg (1 GeV cone) | min D_mu < 0.4 (D = E_jet / p_mu - 1); min ECAL energy in 3-15 deg < 0.7 GeV |
| cut on m(l l) | none | none | none |
| efficiency quoted | none | 4.1 +- 0.2 % of the generated (FERMISV) phase space | none |
| **m(mu mu) in 20-40 GeV** | no mu-mu-only plot; e e + mu mu together: 2 in 20-30, 2 in 30-40 | **1 in 20-30, 0 in 30-40** | **0** (Fig. 7a: 0-10: 1, 10-20: 1, 60-70: 2, 80-90: 2) |

OPAL's 4.1 % is not the efficiency for a boson. It refers to the whole generated phase space of
the Standard Model process, which is dominated by soft and collinear lepton pairs radiated off the
quarks that no isolation cut keeps. A 30 GeV pair with two muons of about 15 GeV, far from the
jets, is the easiest case for these selections.

## 3. Bound from the totals (version 0.1, unchanged)

N_X = R_acc x N_Z x eps boson events would sit in each published count. With 95 % CLs upper limits
on extra events (Poisson, expected background known), the largest efficiency at which an
ALEPH-sized boson is still allowed:

| | s_up (95 % CLs) | N_X if eps = 1 | eps_max (nominal) | eps_max (low reading) |
|---|---|---|---|---|
| OPAL | 12.2 | 208 | **0.059** | 0.068 |
| ALEPH 1989-93 | 15.0 | 118 | 0.13 | 0.15 |
| L3 | 7.3 | 57 | 0.13 | 0.15 |
| all three, one common eps | 21.2 | 383 | **0.055** | 0.064 |

## 4. Bound from the mass distributions (new in 0.2)

A 30.4 GeV boson's dimuon mass falls between 20 and 40 GeV (95 % of xme's Breit-Wigner lies in
22-40 GeV, and LEP's dimuon mass resolution at 30 GeV is a few hundred MeV). We count every
event the papers show in 20-40 GeV as possible signal and assume no Standard Model background
there. Both choices make the limits weaker than they really are. Upper limits on boson events
(95 % CLs, b = 0): OPAL n = 1, s_up = 4.74; L3 n = 0, s_up = 3.00; OPAL + L3 n = 1, s_up = 4.74;
ALEPH (e e and mu mu together) n = 4, s_up = 9.15.

Predicted boson events in 20-40 GeV = R_acc x N_Z x 0.953 (generated mass range) x eps_kin x
0.86^2 (muon identification, ALEPH's value used for all three), where eps_kin is the kinematic and
isolation efficiency of each selection. eps_kin is the number job `lep4f-eff-v1` measures. For now
it is the unknown, and the table gives the eps_kin below which the boson would still be allowed:

| | predicted if eps_kin = 1 | eps_kin allowed (nominal, ALEPH central) | allowed (low reading, ALEPH - 1 sigma) |
|---|---|---|---|
| OPAL | 147 | < **0.032** | < 0.056 |
| L3 | 40 | < 0.075 | < 0.13 |
| OPAL + L3 (one common eps_kin) | 187 | < **0.025** | < 0.044 |
| ALEPH 1989-93 (e e + mu mu) | 83 | < 0.11 | < 0.19 |

So the boson reading survives the OPAL and L3 mass distributions only if their selections kept
**fewer than about 1 in 40** isolated 30 GeV muon pairs (1 in 23 at the weakest reading of
ALEPH's numbers). In that case OPAL and L3 alone, two experiments independent of ALEPH's data,
exclude it. If eps_kin is near 0.5, as we expect for OPAL, an ALEPH-sized boson predicts about 73
OPAL events in 20-40 GeV where OPAL shows one (p ~ 1e-30).

`analysis/eff4f.py` (0.1.0, 16 tests) codes the three selections at generator level, with every
unknown set on the strict side: isolation energy counts all visible particles (not just
calorimeter energy), ALEPH's lepton momentum cut is taken as 3 GeV (2 and 5 GeV variants), L3's
muon acceptance as 40-140 degrees, and boson events that pass a selection but fall outside
ALEPH's acceptance are not counted. `analysis/run_eff4f.py` runs it on 10,000 Pythia 8 events for
each of the three boson models of NOTE-kinematics.md and prints the table above with measured
eps_kin, the p-values and robustness variants.

**Expectations written before lep4f-eff-v1 returns** (graded in the next version of this note):

| | expectation |
|---|---|
| H1 | all 16 unit tests pass (none skipped: lep4f and evana are present in the job) |
| H2 | eps_kin(OPAL, nominal cuts) >= 0.30 for all three models (V, S, P) |
| H3 | eps_kin(L3, nominal cuts) >= 0.25 for all three models |
| H4 | predicted OPAL events in 20-40 GeV >= 20 for every model (nominal reading, ALEPH central) |
| H5 | OPAL + L3: p-value < 1e-6 for every model at ALEPH's central yield, and < 1e-3 at the low reading with ALEPH's yield minus one sigma |

If H2-H5 pass, the statement becomes: *the published OPAL and L3 four-fermion measurements
exclude the interpretation of the ALEPH excess as a boson produced with b quarks that decays to
isolated muons.* If they fail, the note will say which cut removes the boson and by how much.

## 5. How this fits with the kinematic result

NOTE-kinematics.md asks whether ALEPH's 32 events look like a boson. ALEPH reports a muon within 15
degrees of a jet "in all cases", which allows at most about 4-10 boson events. This note asks
whether the boson's events show up where they should, in other experiments' isolated-dimuon
samples. They don't, unless those selections were very inefficient for them. The two arguments
use different events and different detectors, and they agree.

Neither argument covers a source of the excess whose muons sit inside the b jets (for example a
cascade or a mismeasured b-decay pair). DELPHI tests A and B (PLAN.md) test that directly in
b-tagged events.

## 6. Prior art

We found no paper that confronts the 30 GeV excess with the LEP1 four-fermion measurements. None of
the 22 papers that INSPIRE lists as citing arXiv:1610.06536 (checked 2026-11-17) uses LEP1
l l q q data, OPAL data or isolated-lepton samples. Lane and Pritchett (arXiv:1701.07376)
discuss the muon-jet angles and Z -> 4 mu. Ko, Li and Yu (arXiv:1610.07526) compare parton-level
kinematics. The L3 study (Hebbeker and Roth, arXiv:1905.01111) repeats the b-tagged spectrum. The
four-fermion papers predate the excess by twenty years.

## 7. Limits of this note (read before citing)

1. **The mass counts were read off the papers' figures by an AI reading agent** working for MV2
   (2026-11-17), from scanned preprints. They have not yet been checked by a second reading or
   by a person. The L3 figure's six entries add up to its six events, which is a consistency
   check. A second reading is requested.
2. **eps_kin is not yet measured.** Section 4 gives the threshold; `lep4f-eff-v1` will give the
   value at generator level, with no detector simulation. Selection details not in our reading
   notes (OPAL's multiplicity and muon-identification cuts, ALEPH's momentum cut) are modelled as
   variants or left out.
3. OPAL's hadronic Z count is scaled from its luminosity with L3's ratio (about +- 10 %).
4. ALEPH's 1989-93 four-fermion data overlap the 1992-93 part of the 1992-95 sample in which the
   excess was found, so the ALEPH row is not independent of the excess. OPAL and L3 are.
5. Muon identification is taken as 0.86 per muon for all experiments (ALEPH's value).
6. The boson models are those of NOTE-kinematics.md (vector or scalar radiated off the b quark;
   Z -> h A). A model whose muons are not isolated is not covered.

## 8. What comes next

- Grade H1-H5 when `lep4f-eff-v1` returns and publish version 0.3 with measured values.
- A second, independent reading of the OPAL and ALEPH figures and selection sections.
- **Test C for DELPHI (to be pre-registered in plan v1.0):** the isolated selection without the
  b-tag, data blinded in 26-35 GeV, with the four-fermion background from DELPHI's EXCALIBUR
  simulation (job `dimu-fourf-v1`). It needs no assumption about another experiment's
  efficiency.
- If H2-H5 pass, write this up as a short paper ("The LEP1 four-fermion measurements and the
  30 GeV dimuon excess"), and ask a particle physicist to read it before submitting it anywhere.
