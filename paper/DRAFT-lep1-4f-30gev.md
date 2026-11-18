# The LEP1 four-fermion measurements and the 30 GeV dimuon excess

**DRAFT 0.2, 2026-11-18. Not peer reviewed. Not yet read by a particle physicist.**
Comments are welcome at mv2@munimtech.com or as issues on the repository.

MV2, Munim, Inc. (mv2@munimtech.com). Prepared with AI agents working in MV2's name. Not a result
of the ALEPH, DELPHI, L3 or OPAL Collaborations. Code and data:
https://github.com/munimtechnologies/delphi-dimuon-30gev (code Apache-2.0; text CC BY 4.0).

## Abstract

A re-analysis of archived ALEPH data found an excess of 32 +- 11 b-tagged opposite-sign dimuon
events at m(mu mu) = 30.4 GeV in hadronic Z decays (arXiv:1610.06536). If the excess were a boson X
produced in Z -> b bbar X, X -> mu+ mu-, ALEPH's quoted efficiencies fix its rate at about
6 x 10^-5 per hadronic Z decay with both muons in acceptance. In three explicit models (a vector or
a scalar radiated off the b quark, and Z -> h A) both muons are isolated from the jets in 92-95 % of
events. That is the signature that ALEPH, L3 and OPAL selected in 1994-96 to measure
e+e- -> mu+ mu- q qbar at the Z pole. Applying the published selections at hadron level, we find
that OPAL's keeps 84-88 % and L3's 59-68 % of such boson events. OPAL's and L3's published dimuon
mass distributions, which together contain one event between 20 and 40 GeV, would then contain
150-156 boson events. The boson interpretation is excluded far beyond any conventional threshold;
at the lowest rate quoted in the literature for the excess, and with the least favourable choice of
every selection detail we could not read, the probability of seeing one event or fewer is below
5 x 10^-12. The same models contradict ALEPH's own observation that the muons of the excess lie close
to the jets. A real effect would therefore have to produce muons inside the b jets, which the open
DELPHI data can test directly. All expectations for the efficiency calculation were published
before it was run.

## 1. Introduction

Heister (arXiv:1610.06536, v9 2024) reported, in ALEPH's archived 1992-95 Z-pole data, an excess
of b-tagged opposite-sign dimuon events at m = 30.40 +- 0.46 GeV, width 1.78 +- 1.14 GeV, about
5 standard deviations locally and 3 after the look-elsewhere effect. b-tag efficiency 38 %, muon
identification 86 % per muon, 1.9M selected hadronic events (2.2M expected). The excess drew
model interpretations (Ko, Li and Yu, arXiv:1610.07526; Lane and Pritchett, arXiv:1701.07376), a
re-analysis of L3 data in b-tagged events (arXiv:1905.01111), a CMS excess at 28 GeV in mu mu + b
(arXiv:1808.01890) and LHC searches. To our knowledge, no study has confronted it with the LEP1
measurements of isolated lepton pairs in hadronic events, which predate it by twenty years.

## 2. The boson rate

With N_sig = 32.31, N_had = 1.9M / 0.9748 produced hadronic Z, muon identification 0.86^2 and
b-tag efficiency 0.38, the rate of boson events with both muons in ALEPH's acceptance is

    R_acc = 32.31 / (1.9e6 / 0.9748) / (0.86^2 x 0.38) = 5.90 x 10^-5 per hadronic Z.

We also use a low reading (ALEPH's 2.2M expected hadronic events and the yield minus one standard
deviation) and the lowest rate quoted in the literature, Br(Z -> b bbar mu mu) ~ 1.1 x 10^-5
(Ko, Li and Yu), i.e. 1.57 x 10^-5 per hadronic Z. The latter is close to the uncorrected yield
and is used as a deliberately pessimistic reading.

## 3. Signal models and isolation

Tree-level matrix elements for e+e- -> Z -> b bbar X (X a vector or scalar of mass 30.4 GeV and
width 1.78 GeV, radiated off the b line) and Z -> h A (m_h = 30.4 GeV), hadronised with Pythia
8.318. With ALEPH's own jet definition, a muon lies within 15 degrees of a leading jet in 5-11 % of
boson events and 99.4 % of Standard Model Z -> b bbar dimuon events. ALEPH reports that in all
cases one muon is within 15 degrees of a leading jet; taken at face value this allows at most about
4-10 of the 32 events to be such a boson (95 % CL). Details: NOTE-kinematics.md.

## 4. The LEP1 four-fermion selections

| | ALEPH, Z. Phys. C 66 (1995) 3 | OPAL, Phys. Lett. B 376 (1996) 315 | L3, Phys. Lett. B 321 (1994) 283 |
|---|---|---|---|
| hadronic Z | ~2.0M (1989-93) | 3.53M (from 132.4 pb^-1) | 0.96M (1991-92) |
| observed / expected | 19 / 13 | 28 / 28.2 | 6 / 5.0 |
| isolation | < 1 GeV in a 30 deg cone | largest cone with < 1 GeV: >= 30 deg and >= 10 deg | D < 0.4, small ECAL energy near the muon |
| m(mu mu) in 20-40 GeV | 4 (e e and mu mu together; overlaps the excess data) | **1** (Fig. 3b, final selection) | **0** (Fig. 7a) |

Selections in full, with every detail we could not read and the variant that brackets it:
NOTE-fourfermion.md section 2.

## 5. Efficiencies and confrontation

10,000 events per model were passed through the three selections at hadron level
(analysis/eff4f.py 0.2.0). Efficiency for boson events in ALEPH's acceptance, muon identification
excluded:

| model | OPAL | L3 | ALEPH |
|---|---|---|---|
| vector off b | 0.844 | 0.644 | 0.577 |
| scalar off b | 0.865 | 0.592 | 0.668 |
| Z -> h A | 0.877 | 0.677 | 0.712 |

Predicted boson events in 20-40 GeV, OPAL + L3 (observed: 1):

| rate reading | vector | scalar | Z -> h A |
|---|---|---|---|
| central | 149.6 | 150.7 | 155.9 |
| low (2.2M, yield - 1 sigma) | 85.7 | 86.4 | 89.3 |
| lowest literature rate | 39.9 | 40.2 | 41.6 |
| lowest rate, least favourable cut variant (both isolation angles >= 30 deg) | p = 4.5e-12 | p = 3.7e-13 | p = 2.5e-14 |

From the published totals alone (no mass information), the three experiments together allow the
boson only if their efficiency were below 0.055, an order of magnitude below the measured values.

Seven expectations (H1-H7) were published before the efficiency job ran; all were met
(NOTE-fourfermion.md section 4).

## 6. The LEP1 Higgs searches (preliminary; hand calculation)

The LEP1 searches for e+e- -> H Z*, Z* -> mu+ mu- selected two energetic isolated muons recoiling
against hadrons. ALEPH (4.5M hadronic Z, PLB 384 (1996) 427) found three candidates, one of them
kinematically incompatible with a 30 GeV pair; L3 (3.05M, PLB 385 (1996) 454), with no recoil-mass
cut, found none; DELPHI (0.94M, NPB 421 (1994) 3) one. With a common efficiency eps, the three
searches predict about 315 x eps boson events against 3 that could be signal, so the boson is
allowed only for eps < 0.025, while the same searches kept 32-55 % of Higgs events of similar
topology. L3 alone gives eps < 0.024 and also covers Z -> h A. Efficiency jobs with pre-registered
expectations are queued; this section will be replaced by measured values
(NOTE-higgs-searches.md).

## 7. Discussion

Three independent arguments agree: the kinematics ALEPH reports for its own events, the LEP1
four-fermion measurements (sections 4-5), and the LEP1 Higgs searches (section 6, preliminary).
None of them excludes an excess whose muons sit inside the b jets: cascade decays, a mismodelled
b-decay background shape, or a new state that decays within a jet. That is the topology ALEPH
describes. DELPHI's open data (released 2024) allow a direct test in b-tagged events; a
pre-registered, blinded analysis is in preparation in the same repository.

**Limitations.** Hadron level only, no detector simulation; isolation from generator particles;
a common muon identification efficiency (ALEPH's) for all experiments; OPAL's hadronic Z count
scaled from its luminosity; the published mass distributions were read from scanned figures by AI
reading agents, twice and independently, and have not yet been checked by a person. The variants
of section 5 bracket the selection details we could not read. Because the predicted counts exceed
the limits by factors of 8-33, none of these approximations is likely to change the conclusion,
but a check with the experiments' own simulation would make it final.

## 8. Reproducibility

`python run_eff4f.py --out OUT --nsig 10000 --workers 2` with eff4f 0.2.0, lep4f 0.1.0, xme 0.2.0
(Pythia 8.318 via pythia8mc, numpy). Output and sha256 of every source file:
analysis/results/lep4f-eff-v2-run.txt and lep4f-eff-v2-summary.json.

## Acknowledgements and disclosure

This work was carried out with AI agents working in MV2's name, including the reading of the
scanned papers. It uses only published results and public software.

## References

1. A. Heister, "Observation of an excess at 30 GeV in the opposite sign di-muon spectra of
   Z -> b bbar + X events recorded by the ALEPH experiment at LEP", arXiv:1610.06536 (v9, 2024).
2. ALEPH Collaboration, Z. Phys. C 66 (1995) 3.
3. OPAL Collaboration, Phys. Lett. B 376 (1996) 315.
4. L3 Collaboration, Phys. Lett. B 321 (1994) 283.
5. LEP four-fermion summary, hep-ex/9611015.
6. ALEPH Collaboration, Phys. Lett. B 384 (1996) 427.
7. L3 Collaboration, Phys. Lett. B 385 (1996) 454.
8. DELPHI Collaboration, Nucl. Phys. B 421 (1994) 3.
9. P. Ko, J. Li, C. Yu, arXiv:1610.07526.
10. K. Lane, L. Pritchett, arXiv:1701.07376.
11. T. Hebbeker, S. Roth, "Study of muon pairs in hadronic events with bottom tag using L3 data
    recorded near the Z resonance", arXiv:1905.01111.
12. CMS Collaboration, arXiv:1808.01890.
13. C. Bierlich et al., Pythia 8.3, SciPost Phys. Codebases 8 (2022).
