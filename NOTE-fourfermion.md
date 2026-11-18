# NOTE-fourfermion: what LEP1's published four-fermion data say about the 30 GeV excess

MV2 of Munim, Inc. (mv2@munimtech.com). Version 0.3, 2026-11-18 (0.1 and 0.2 on 2026-11-17).
Made with AI agents working in MV2's name. Not a DELPHI, ALEPH, L3 or OPAL Collaboration result.
**No physicist has checked this note yet.** Sections 3 and 4 are hand calculations. Job
`lep4f-v1` prints the exact values of section 3. Job `lep4f-eff-v2` measures the selection
efficiencies that section 4 needs (it replaces `lep4f-eff-v1`, which had not run, because the
second reading of the papers found cuts that version 0.1.0 of the code left out). The note will be
updated with their results and any correction. Text CC BY 4.0, code Apache-2.0.

**What changed in 0.3**
- A second, independent reading of the OPAL and ALEPH papers agrees with the first: OPAL's
  Fig. 3b, *after the final event selection*, has **1 mu mu q qbar event in 20-30 GeV, 0 in
  30-40 GeV** and 5 above 40 GeV (of 28). OPAL's full selection is now in section 2.
- `analysis/eff4f.py` 0.2.0 codes OPAL's selection as written: charged multiplicity, Durham jets,
  isolation energy from tracks and EM clusters only, and the partner lepton excluded from the cone.
- Section 4 adds a third, lowest reading of the boson rate: the 1.1 x 10^-5 branching ratio quoted
  from the ALEPH excess by Ko, Li and Yu (arXiv:1610.07526). Even then the OPAL and L3 mass plots
  leave room only for selections that keep fewer than about 1 in 10 isolated 30 GeV muon pairs.
- Section 5 quotes what arXiv:1610.06536 v9 itself says about where the excess muons sit: close
  to the jets, both of them.

## 1. The argument in one paragraph

Suppose the 32.31 b-tagged dimuon events that arXiv:1610.06536 fits at 30.40 GeV were a new boson
X produced in Z -> b bbar X, X -> mu+ mu-. ALEPH's own efficiencies then fix how often such an
event occurs, with both muons in ALEPH's acceptance: about **5.9 x 10^-5 per hadronic Z decay**
(5.1 x 10^-5 under the paper's "2.2M expected" reading). Our kinematic study (NOTE-kinematics.md,
xkin-v1) found both muons more than 20 degrees from every jet in 92-95 % of such events, in all
three boson models. An isolated, energetic muon pair in a hadronic event is the exact signature that
ALEPH, L3 and OPAL selected in the early 1990s to measure the Standard Model process
e+e- -> mu+ mu- q qbar at the Z pole. **What those papers show of the dimuon mass: OPAL has one
selected mu mu q qbar event between 20 and 40 GeV, and L3 has none.** An ALEPH-sized boson would
have put of order a hundred events there (forty at the lowest reading of its rate) unless the
selections kept only a few per cent of them.

## 2. Inputs

ALEPH excess (arXiv:1610.06536 v9), as in `analysis/nexp.py` 0.2.0: N_sig = 32.31 +- 10.87,
N_had = 1.9M selected (2.2M "expected"), hadronic efficiency 0.9748, muon identification 0.86 per
muon, b-tag 0.38 (event-level working point). Rate of boson events with both muons in acceptance,
per produced hadronic Z:

    R_acc = 32.31 / (1.9e6 / 0.9748) / (0.86^2 x 0.38) = 5.898e-5      (low reading: 5.094e-5)

**Lowest reading (new).** Ko, Li and Yu (arXiv:1610.07526) quote Br(Z -> b bbar mu+ mu-) ~ 1.1 x
10^-5 for the ALEPH excess. That is close to the raw yield, 32 events over the roughly 2.7-3.1
million Z decays behind ALEPH's 1.9-2.2M hadronic events, before correcting for the b-tag (0.38) and
muon identification (0.86^2). Corrected, it would be about 4 x 10^-5 of all Z decays, consistent
with R_acc x Gamma_had / Gamma_Z = 4.1 x 10^-5. We still carry it as a third reading: 1.1e-5 /
0.69911 = **1.573 x 10^-5 per hadronic Z, taken as if every such event were inside ALEPH's
acceptance**, which is 3.7 times below R_acc.

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
| muon polar angle | - | not stated (tracking covers 98 % of 4 pi) | taken as 40-140 deg (generator cut) |
| cut on m(l l) | none | none | none |
| efficiency quoted | none | 4.1 +- 0.2 % of the generated (FERMISV) phase space | none |
| **m(mu mu) in 20-40 GeV** | no mu-mu-only plot; Fig. 13b, e e + mu mu together: 2 in 20-30, 2 in 30-40 | **Fig. 3b, final selection: 1 in 20-30, 0 in 30-40** (0-10: 19, 10-20: 3, 40-80: 5; sum 28) | **0** (Fig. 7a: 0-10: 1, 10-20: 1, 60-70: 2, 80-90: 2) |

OPAL's 4.1 % is not the efficiency for a boson. It refers to the whole generated phase space of
the Standard Model process, which is dominated by soft and collinear lepton pairs radiated off the
quarks that no isolation cut keeps; 19 of OPAL's 28 events have m(mu mu) below 10 GeV. A 30 GeV
pair with two muons of about 15 GeV, far from the jets, is the easiest case for these selections.

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

## 4. Bound from the mass distributions

A 30.4 GeV boson's dimuon mass falls between 20 and 40 GeV (95 % of xme's Breit-Wigner lies in
22-40 GeV, and LEP's dimuon mass resolution at 30 GeV is a few hundred MeV). We count every
event the papers show in 20-40 GeV as possible signal and assume no Standard Model background
there. Both choices make the limits weaker than they really are. Upper limits on boson events
(95 % CLs, b = 0): OPAL n = 1, s_up = 4.74; L3 n = 0, s_up = 3.00; OPAL + L3 n = 1, s_up = 4.74;
ALEPH (e e and mu mu together) n = 4, s_up = 9.15.

Predicted boson events in 20-40 GeV = R x N_Z x 0.953 (generated mass range) x eps_kin x 0.86^2
(muon identification, ALEPH's value used for all three), where eps_kin is the kinematic and
isolation efficiency of each selection, measured by job `lep4f-eff-v2`. Until it returns, the
table gives the eps_kin below which the boson would still be allowed:

| | predicted if eps_kin = 1 (R_acc / lowest reading) | eps_kin allowed: nominal, ALEPH central | low reading, ALEPH - 1 sigma | lowest reading (Ko-Li-Yu rate) |
|---|---|---|---|---|
| OPAL | 147 / 39 | < **0.032** | < 0.056 | < 0.12 |
| L3 | 40 / 11 | < 0.075 | < 0.13 | < 0.28 |
| OPAL + L3 (one common eps_kin) | 187 / 50 | < **0.025** | < 0.044 | < **0.095** |
| ALEPH 1989-93 (e e + mu mu) | 83 / 22 | < 0.11 | < 0.19 | < 0.41 |

So the boson reading survives the OPAL and L3 mass distributions only if their selections kept
**fewer than about 1 in 40** isolated 30 GeV muon pairs (1 in 23 at the low reading, 1 in 10 at
the lowest). If eps_kin is near 0.5, as we expect for OPAL, an ALEPH-sized boson predicts about 73
OPAL events in 20-40 GeV where OPAL shows one (p ~ 1e-30), and still about 25 OPAL + L3 events
(p ~ 4e-10) at the lowest reading.

`analysis/eff4f.py` 0.2.0 (22 tests) codes the three selections at hadron level (Pythia 8), from
both readings:
- **OPAL**: N_trk >= 8 (charged, p > 0.2 GeV, |cos theta| < 0.95); >= 2 Durham jets from tracks
  and EM clusters (y_cut is not stated: 0.02 nominal, 0.005 variant); the momentum and isolation
  cuts above, with E_cone counting every visible particle except neutrons and K_L, and the partner
  muon left out of the cone. Not modelled: the dE/dx electron veto (b-quark events pass it).
  Variants: no multiplicity cuts, nearest-particle isolation, both angles >= 30 deg,
  |cos theta| < 0.9 or 0.98, and `v010` (version 0.1.0's stricter selection: all visible energy,
  no partner exclusion).
- **ALEPH**: >= 6 charged; < 1 GeV of all visible energy in 30 deg; momentum 3 GeV assumed
  (2 and 5 GeV variants).
- **L3**: unchanged from 0.1.0 (all visible energy in the annulus, which is stricter than ECAL
  energy; jet cone 25 deg, 40 deg variant; acceptance 40-140 deg, 0.7 variant).

Boson events that pass a selection but fall outside ALEPH's acceptance are not counted.
`analysis/run_eff4f.py` runs it on 10,000 Pythia 8 events for each of the three boson models of
NOTE-kinematics.md and prints the table above with measured eps_kin, the p-values for every
variant and all three rate readings, and the worst case over variants.

**Expectations, written before any efficiency has been measured** (H1-H5 as in version 0.2; H6
and H7 new; graded in the next version of this note):

| | expectation |
|---|---|
| H1 | all 22 unit tests pass (none skipped: lep4f and evana are present in the job) |
| H2 | eps_kin(OPAL, nominal cuts) >= 0.30 for all three models (V, S, P) |
| H3 | eps_kin(L3, nominal cuts) >= 0.25 for all three models |
| H4 | predicted OPAL events in 20-40 GeV >= 20 for every model (nominal reading, ALEPH central) |
| H5 | OPAL + L3: p-value < 1e-6 for every model at ALEPH's central yield, and < 1e-3 at the low reading with ALEPH's yield minus one sigma |
| H6 | OPAL + L3 at the lowest (Ko-Li-Yu) rate, low reading: p-value < 1e-3 for every model with nominal cuts, and < 0.05 for every model in every variant |
| H7 | OPAL's multiplicity cuts cost little: eps_kin(OPAL nominal) / eps_kin(OPAL nomult) >= 0.95 for every model |

If H2-H6 pass, the statement becomes: *the published OPAL and L3 four-fermion measurements
exclude the interpretation of the ALEPH excess as a boson produced with b quarks that decays to
isolated muons.* If any fails, the note will say which cut removes the boson and by how much.

## 5. How this fits with the kinematic result, and with ALEPH's own description

NOTE-kinematics.md asks whether ALEPH's 32 events look like a boson. arXiv:1610.06536 v9 (section
4) says: "We found that in all cases one of the two muons from di-muons is closer than 15 deg to one
of the leading jets", and, of the excess itself, "We find that each of the two muons which form the
excess around 30 GeV are also close to one of the leading jets", with the event displays showing
"the closeness of both muons to hadronic jet structures". The boson models put a muon within 15
degrees of a leading jet in only 5-11 % of events (xkin-v1), so at most about 4-10 of the 32 events
can be such a boson. This note asks the reverse question: do the boson's events show up where they
should, in other experiments' isolated-dimuon samples? They don't, unless those selections were
very inefficient for them. The two arguments use different events and different detectors, and
they agree.

What neither argument covers is a source whose muons sit inside the b jets, which is what ALEPH's
own description points to: a cascade or a mismeasured b-decay pair, or a new state that decays
inside a jet. DELPHI tests A and B (PLAN.md) test that directly in b-tagged events, with no
isolation.

## 6. Prior art

We found no paper that confronts the 30 GeV excess with the LEP1 four-fermion measurements. None of
the 22 papers that INSPIRE lists as citing arXiv:1610.06536 (checked again 2026-11-18) uses LEP1
l l q q data, OPAL data or isolated-lepton samples. Lane and Pritchett (arXiv:1701.07376)
discuss the muon-jet angles and Z -> 4 mu. Ko, Li and Yu (arXiv:1610.07526) compare parton-level
kinematics and LHC constraints. The L3 study (Hebbeker and Roth, arXiv:1905.01111) repeats the
b-tagged spectrum. ATLAS searched for a b j mu mu resonance at 26-30 GeV at the LHC. The
four-fermion papers predate the excess by twenty years.

## 7. Limits of this note (read before citing)

1. **The mass counts were read off the papers' figures by AI reading agents** working for MV2,
   from scanned preprints, twice and independently (2026-11-17). Both readings agree on OPAL
   (1 event in 20-30 GeV, 0 in 30-40 GeV, after the final selection; the bins add up to the 28
   observed events) and on L3 (0 in 20-40 GeV; the bins add up to the 6 observed events). No
   person has checked them yet.
2. **eps_kin is not yet measured.** Section 4 gives the thresholds; `lep4f-eff-v2` will give the
   values at hadron level, with no detector simulation. OPAL's Durham y_cut, OPAL's muon
   identification (its ref. 19, Z. Phys. C 58 (1993) 523) and ALEPH's momentum cut (its ref. 20)
   are not read and are covered by variants.
3. OPAL's hadronic Z count is scaled from its luminosity with L3's ratio (about +- 10 %).
4. ALEPH's 1989-93 four-fermion data overlap the 1992-93 part of the 1992-95 sample in which the
   excess was found, so the ALEPH row is not independent of the excess. OPAL and L3 are.
5. Muon identification is taken as 0.86 per muon for all experiments (ALEPH's value).
6. The boson models are those of NOTE-kinematics.md (vector or scalar radiated off the b quark;
   Z -> h A). A model whose muons are not isolated is not covered.

## 8. What comes next

- Grade H1-H7 when `lep4f-eff-v2` returns and publish version 0.4 with measured values.
- **Test C for DELPHI (to be pre-registered in plan v1.0):** the isolated selection without the
  b-tag, data blinded in 26-35 GeV, with the four-fermion background from DELPHI's EXCALIBUR
  simulation (job `dimu-fourf-v1`). It needs no assumption about another experiment's
  efficiency.
- If H2-H6 pass, write this up as a short paper ("The LEP1 four-fermion measurements and the
  30 GeV dimuon excess"), and ask a particle physicist to read it before submitting it anywhere.
