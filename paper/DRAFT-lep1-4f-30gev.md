# LEP1 isolated-muon measurements and the 30 GeV dimuon excess

**DRAFT 0.7, 2026-11-19. Not peer reviewed. Not yet read by a particle physicist.**
Comments are welcome at mv2@munimtech.com or as issues on the repository.

MV2, Munim, Inc. (mv2@munimtech.com). Prepared with AI agents working in MV2's name. Not a result
of the ALEPH, DELPHI, L3 or OPAL Collaborations. Code and data:
https://github.com/munimtechnologies/delphi-dimuon-30gev (code Apache-2.0; text CC BY 4.0).

Changes from 0.6: (a) section 6b now includes the second, pre-registered test of Ko, Li and Yu's
models with the four-fermion selections (job kly4f-v1; all five expectations met): OPAL's
selection keeps 82-89 % of every model, including Z -> Z' phi with a 12 GeV scalar; (b) a caveat
found while grading is stated in 6b: whether OPAL's two-jet requirement counted the muons decides
the 12 GeV case, and a further pre-registered job measures it; (c) Lane and Pritchett's model is
covered by the Z -> h A results (section 7).

## Abstract

A re-analysis of archived ALEPH data found an excess of 32 +- 11 b-tagged opposite-sign dimuon
events at m(mu mu) = 30.4 GeV in hadronic Z decays (arXiv:1610.06536). If the excess were a boson X
produced in Z -> b bbar X, X -> mu+ mu-, ALEPH's quoted efficiencies fix its rate at about
6 x 10^-5 per hadronic Z decay with both muons in acceptance. In three explicit models (a vector or
a scalar radiated off the b quark, and Z -> h A) both muons are isolated from the jets in 92-95 % of
events. Two sets of LEP1 measurements selected exactly this signature. (i) The 1994-96
measurements of e+e- -> mu+ mu- q qbar at the Z pole: applying the published selections at
hadron level, OPAL's keeps 84-88 % and L3's 59-68 % of boson events, so their published dimuon
mass distributions, which together contain one event between 20 and 40 GeV, would contain
150-156. (ii) The LEP1 searches for e+e- -> H Z*, Z* -> mu+ mu-: L3's and DELPHI's selections keep
54-64 % and 69-82 % of boson events and predict about 95-115 events against one candidate.
At the lowest rate quoted in the literature for the excess, the probability of the observed
counts is below 5 x 10^-12 for (i) with the least favourable choice of every selection detail we
could not read, and below 3 x 10^-10 for (ii) without using ALEPH's own search. Both sets also
exclude the two models built to escape the LHC bound (a Z' coupling the b quark to a heavy
vector-like quark, and Z -> Z' phi): at the models' own rate, L3 and DELPHI's Higgs searches
predict 21-28 events against one candidate (p <= 2.1 x 10^-8), and OPAL and L3's four-fermion
selections 38-41 events against one (p <= 1.2 x 10^-15). Every model is excluded by at least two
detectors, except Z -> Z' phi with a 12 GeV scalar, where the second detector's verdict depends on
a jet-finding detail that a pre-registered job now tests. All five models contradict ALEPH's
observation that the muons of the excess lie close to the jets. A real effect would therefore have
to produce muons inside the b jets, which the open DELPHI data can test directly. All
expectations for each efficiency calculation were published before it was run.

## 1. Introduction

Heister (arXiv:1610.06536, v9 2024) reported, in ALEPH's archived 1992-95 Z-pole data, an excess
of b-tagged opposite-sign dimuon events at m = 30.40 +- 0.46 GeV, width 1.78 +- 1.14 GeV, about
5 standard deviations locally and 3 after the look-elsewhere effect. b-tag efficiency 38 %, muon
identification 86 % per muon, 1.9M selected hadronic events (2.2M expected). The excess drew
model interpretations (Ko, Li and Yu, arXiv:1610.07526; Lane and Pritchett, arXiv:1701.07376), a
re-analysis of L3 data in b-tagged events (arXiv:1905.01111), a CMS excess at 28 GeV in mu mu + b
(arXiv:1808.01890) and LHC searches. Ko, Li and Yu showed that a boson coupling directly to b bbar
and mu mu, at the rate the excess needs, is excluded by LHC Drell-Yan production, and that in all
three of their models the muons lie far from the b jets, unlike ALEPH's events (parton level,
signal only). To our knowledge, no study has confronted the excess with the LEP1 measurements of
isolated lepton pairs in hadronic events, which predate it by twenty years. Such a confrontation
uses the same collider, energy and production process as the excess itself.

## 2. The boson rate

With N_sig = 32.31, N_had = 1.9M / 0.9748 produced hadronic Z, muon identification 0.86^2 and
b-tag efficiency 0.38, the rate of boson events with both muons in ALEPH's acceptance is

    R_acc = 32.31 / (1.9e6 / 0.9748) / (0.86^2 x 0.38) = 5.90 x 10^-5 per hadronic Z.

We also use a low reading (ALEPH's 2.2M expected hadronic events and the yield minus one standard
deviation) and the lowest rate quoted in the literature, Br(Z -> b bbar mu mu) ~ 1.1 x 10^-5
(Ko, Li and Yu; it is the fitted rate of their model II, benchmark III), i.e. 1.57 x 10^-5 per
hadronic Z. The latter is close to the uncorrected yield and is used as a deliberately
pessimistic reading.

## 3. Signal models and isolation

Tree-level matrix elements for e+e- -> Z -> b bbar X (X a vector or scalar of mass 30.4 GeV and
width 1.78 GeV, radiated off the b line) and Z -> h A (m_h = 30.4 GeV), hadronised with Pythia
8.318. With ALEPH's own jet definition, a muon lies within 15 degrees of a leading jet in 5-11 % of
boson events and 99.4 % of Standard Model Z -> b bbar dimuon events. ALEPH reports that in all
cases one muon is within 15 degrees of a leading jet; taken at face value this allows at most about
4-10 of the 32 events to be such a boson (95 % CL). Details: NOTE-kinematics.md. This agrees with,
and makes quantitative at hadron level, Ko, Li and Yu's parton-level finding that the minimum
muon-jet angle of their models peaks at 50-70 degrees. For their models II and III (section 6b)
the nearer muon is within 15 degrees of a jet in 3.6-6.1 % of events.

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

## 6. The LEP1 Higgs searches

The LEP1 searches for e+e- -> H Z*, Z* -> mu+ mu- selected two energetic muons recoiling against
hadrons. ALEPH (4.5M hadronic Z, PLB 384 (1996) 427) found three candidates, one of them
kinematically incompatible with a 30 GeV pair; L3 (3.05M, PLB 385 (1996) 454), with both muons
isolated and no recoil-mass cut, found none; DELPHI (0.94M, NPB 421 (1994) 3) found one; OPAL
(ZPC 73 (1997) 189) found one, whose muon momenta put its dimuon mass at 17 GeV.

We applied each selection, as read from the papers, to about 8,000-10,000 hadronised events per
model (analysis/efhz.py and lephz.py 0.1.0). Efficiency in ALEPH's acceptance and the 20-40 GeV
window, muon identification excluded:

| model | ALEPH | L3 | DELPHI | OPAL |
|---|---|---|---|---|
| vector off b | 0.50 | 0.55 | 0.74 | 0.54 |
| scalar off b | 0.26-0.27 | 0.54 | 0.69 | 0.39 |
| Z -> h A | 0.02 | 0.64 | 0.82 | 0.37 |

ALEPH's recoil-mass cut (> 40 GeV) removes most scalar and Z -> h A events (their muon pairs
recoil against 34.6 and 30.4 GeV, median), so ALEPH's search alone does not exclude the scalar at
the lowest literature rate. L3's and DELPHI's do not have this weakness:

| combination (b = 0, every candidate counted as signal) | vector | scalar | Z -> h A |
|---|---|---|---|
| ALEPH + L3 + DELPHI, central rate, 3 compatible candidates | 173.8, p = 3e-70 | 133.9, 3e-53 | 116.3, 9e-46 |
| ALEPH + L3 + DELPHI, lowest literature rate, 4 candidates | 46.4, 1.5e-15 | 35.7, 2.3e-11 | 31.0, 1.5e-9 |
| L3 + DELPHI only, lowest literature rate, 1 candidate | 26.5, 9e-11 | 25.3, 3e-10 | 30.3, 2e-12 |
| DELPHI only, lowest literature rate, 1 candidate | 7.7, 3.9e-3 | 7.2, 6.3e-3 | 8.5, 2.0e-3 |

At the central rate, the three searches allow at most 4.5 %, 5.8 % and 6.7 % of the excess (95 %
CLs). Ten expectations (L1-L10) were published before the job ran; all were met.

Robustness checks, by hand from the job's numbers (NOTE-higgs-searches.md section 5):
(1) the weakest L3 and DELPHI variants, without ALEPH, at the lowest rate give p <= 5e-8;
(2) our hadron-level efficiencies for the Higgs-like topology are 10-60 % higher than the
experiments' published detector-level Higgs efficiencies (ratios 0.78 for L3, 0.90 for DELPHI,
0.62 for OPAL, which is therefore left out of the combinations); scaling L3 and DELPHI by these
ratios on top of (1) gives p <= 1.5e-6, the most pessimistic combination we can construct
(scalar, 4.7 standard deviations); (3) L3's background statement mentions "a recoil mass greater
than 30 GeV", but a second, independent reading of the paper confirms that this is only the range
of the background quote, not a cut, so the selection as coded stands.

## 6b. The models built to escape the LHC bound

Ko, Li and Yu proposed two further models that avoid the LHC Drell-Yan bound because the new
boson does not couple to b bbar: **model II**, a Z' (30.4 GeV) that couples the b quark to a heavy
vector-like singlet quark B, produced at LEP1 as Z -> b B*bar, B*bar -> bbar Z' (their benchmarks
m_B = 110 GeV, Gamma_B = 3.4 GeV and m_B = 180 GeV, Gamma_B = 124.4 GeV); and **model III**,
Z -> Z' phi with phi -> b bbar. We generated both with full helicity amplitudes (analysis/kly.py
0.1.0; model II also with a left-handed Z' vertex to bracket the chirality; model III at
m_phi = 12, 30.4 and 50 GeV), hadronised 7,700-8,000 events each, and applied the four Higgs-search
selections and then, to the same events, the three four-fermion selections. Fourteen
expectations (K1-K9, F1-F5) were published before the two jobs ran; all were met.

| model | Higgs searches: L3 | DELPHI | L3 + DELPHI, lowest rate (1 cand.): pred., p | four-fermion: OPAL | L3 | OPAL + L3, lowest rate (1 obs.): pred., p |
|---|---|---|---|---|---|---|
| II, m_B = 110 GeV | 0.55 | 0.71 | 26.1, 1.3e-10 | 0.86 | 0.61 | 40.0, 1.7e-16 |
| II, m_B = 180 GeV | 0.55 | 0.73 | 26.1, 1.2e-10 | 0.86 | 0.60 | 40.0, 1.7e-16 |
| II, left-handed Z' | 0.55 | 0.72 | 26.1, 1.2e-10 | 0.86 | 0.63 | 40.4, 1.2e-16 |
| III, m_phi = 12 GeV | 0.60 | 0.03 | 20.8, 2.1e-8 (L3 alone: 1.4e-9) | 0.85 | 0.61 | 39.8, 2.0e-16 |
| III, m_phi = 30.4 GeV | 0.59 | 0.79 | 28.1, 1.8e-11 | 0.89 | 0.58 | 41.1, 6.2e-17 |
| III, m_phi = 50 GeV | 0.42 | 0.68 | 21.3, 1.3e-8 | 0.82 | 0.57 | 38.0, 1.2e-15 |

The lowest literature rate is model II's own fitted rate, so this is a test of the model at its
own benchmark. In model III the muon pair recoils against exactly m_phi, so the recoil-mass cuts of
the ALEPH, DELPHI and OPAL Higgs searches remove the light-scalar case, and among the Higgs
searches only L3's (no recoil cut) tests it. With the weakest L3 and DELPHI variants, both scaled
down to the experiments' published Higgs efficiencies, the most pessimistic combinations give
p = 5.6e-7 to 7.4e-7 for model II and 2.3e-7, 1.6e-5 and 6.1e-5 for model III at 30.4, 50 and
12 GeV (3.8-5.0 standard deviations). The four-fermion selections have no recoil-mass cut and give
the 12 GeV case a second detector: with the weakest variant of each, OPAL + L3 predict 35.3
events against one (p = 1.7e-14), and OPAL alone 30.1 (p = 2.6e-12).

**Caveat.** OPAL's four-fermion selection requires at least two Durham jets. Our code clusters
all particles, the two isolated muons included, so this requirement never removes a signal event.
Our reading of OPAL's paper does not say whether the leptons were removed before jet finding. If
they were, and y was normalised to the full visible energy, the hadrons of a 12 GeV scalar would
often form a single jet (y <= m^2 / E_vis^2 ~ 0.017 < 0.02) and OPAL's verdict on that case could
disappear. A pre-registered job (kly4fj-v1, NOTE-higgs-searches.md section 6c) measures all three
readings, and a blind reading of OPAL's paper will decide which applies. The other models are not
affected. Until then, Z -> Z' phi with a 12 GeV scalar rests for certain only on L3's Higgs search.

## 7. Discussion

Three separate lines of evidence agree: the kinematics ALEPH reports for its own events, the LEP1
four-fermion measurements (sections 4-5), and the LEP1 Higgs searches (sections 6 and 6b). They
are separate selections and publications, but not fully independent data: L3's Higgs search
(1991-94) contains its four-fermion data (1991-92), and OPAL's two analyses overlap too. DELPHI's
1991-92 data are in neither four-fermion constraint, and its Higgs search alone excludes the
vector, scalar, Z -> h A and model II at 99 % even at the lowest rate.

For a boson coupling directly to b bbar (our vector and scalar), Ko, Li and Yu's LHC Drell-Yan
argument already excluded the excess's rate; the LEP1 results are an independent exclusion that
uses only Z-pole data, the same production process and no parton densities. For Z -> h A (which
is how Lane and Pritchett's two-Higgs-doublet model is produced at LEP1, with both states at
30 GeV) and for the two models designed to escape the LHC bound, the LEP1 measurements are, as far
as we know, the first direct test, and they exclude all of them at the rate the excess needs.

None of these lines excludes an excess whose muons sit inside the b jets: cascade decays, a
mismodelled b-decay background shape, or a new state that decays within a jet. That is the
topology ALEPH describes. DELPHI's open data (released 2024) allow a direct test in b-tagged
events; a pre-registered, blinded analysis is in preparation in the same repository.

**Limitations.** Hadron level only, no detector simulation; isolation from generator particles;
a common muon identification efficiency (ALEPH's) for all experiments; OPAL's hadronic Z count
scaled from its luminosity; ALEPH's 1996 b-tag and OPAL's vertex requirement as fixed factors;
model III computed at three scalar masses only, with the Z Z' phi vertex taken as g^{mu nu};
OPAL's four-fermion jet definition not yet read (section 6b); the selections and the published
mass distributions were read from scanned papers by AI reading agents (the mass distributions,
and L3's Higgs-search cuts, twice and independently) and have not yet been checked by a person.
Variants bracket each selection detail we could not read. Because the predicted counts exceed the
limits by large factors, and the comparison with the experiments' own Higgs efficiencies shows
our selections at most about 1.6 times too efficient, none of these approximations is likely to
change the conclusion, but a check with the experiments' own simulation would make it final.

## 8. Reproducibility

`python run_eff4f.py --out OUT --nsig 10000 --workers 2` with eff4f 0.2.0, lep4f 0.1.0, xme 0.2.0
(Pythia 8.318 via pythia8mc, numpy). Output and sha256 of every source file:
analysis/results/lep4f-eff-v2-run.txt and lep4f-eff-v2-summary.json. Section 6:
`python run_efhz.py --out OUT --nsig 10000 --workers 2` (efhz 0.1.0) and
`python run_lephz.py --out OUT --nsig 8000 --workers 2` (lephz 0.1.0); outputs in
analysis/results/efhz/ and analysis/results/lephz/. Section 6b:
`python run_kly.py --out OUT --nsig 8000 --workers 2` (kly 0.1.0) and
`python run_kly4f.py --out OUT --nsig 8000 --workers 2` (kly4f 0.1.0); outputs in
analysis/results/kly/ and analysis/results/kly4f/.

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
9. OPAL Collaboration, Z. Phys. C 73 (1997) 189; Phys. Lett. B 327 (1994) 397.
10. P. Ko, J. Li, C. Yu, "Implication of the ALEPH 30 GeV dimuon resonance at the LHC",
    arXiv:1610.07526.
11. K. Lane, L. Pritchett, arXiv:1701.07376.
12. T. Hebbeker, S. Roth, "Study of muon pairs in hadronic events with bottom tag using L3 data
    recorded near the Z resonance", arXiv:1905.01111.
13. CMS Collaboration, arXiv:1808.01890.
14. C. Bierlich et al., Pythia 8.3, SciPost Phys. Codebases 8 (2022).
