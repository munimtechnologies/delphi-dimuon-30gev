# Analysis plan v0.1: does DELPHI see ALEPH's 30 GeV dimuon excess?

MV2 of Munim, Inc. (mv2@munimtech.com). Written 2026-11-17. Made with AI agents working in
MV2's name. This is a plan, not a result: as of v0.1, no DELPHI dimuon mass has been looked at.
Not a DELPHI Collaboration result; DELPHI and CERN do not endorse it.
Text CC BY 4.0, code Apache-2.0.

## 1. The question

In 2016 a re-analysis of archived ALEPH data from LEP1 (Z pole, 1992-1995, about 1.9 million
hadronic Z decays) found an excess in the opposite-sign dimuon mass spectrum of events that
contain b quarks (A. Heister, arXiv:1610.06536, v9 2024):

| quantity | ALEPH value |
|---|---|
| signal events | 32.3 +- 10.9 (on 1457 +- 90 background, 15-50 GeV) |
| mass | 30.40 +- 0.46 GeV |
| natural width | 1.78 +- 1.14 GeV |
| Gaussian resolution | 0.74 +- 0.10 GeV |
| local significance | about 5 sigma (Z_asym, KDE background); 2.6 sigma (Z_Bi) |
| with look-elsewhere | about 2.4-2.9 sigma, depending on background model |
| e+e- channel | 8.0 +- 4.5 events at 29.2 GeV (about 1.5 sigma) |
| controls | no excess in same-sign mumu, in e-mu, or with the b-tag inverted |

CMS later saw a dimuon excess at 28.3 GeV in events with b jets at 8 TeV (4.2 and 2.9 sigma
local in two categories), but only 2.0 sigma and a 1.4 sigma deficit at 13 TeV in 2016
(CMS, JHEP 11 (2018) 161, arXiv:1808.01890). The only other LEP check is L3
(Hebbeker and Roth, arXiv:1905.01111), with 170 dimuon pairs in 5-50 GeV against ALEPH's
about 1,490 in 15-50 GeV, and a slight excess of about 1 sigma. LHCb's search for low-mass
dimuon resonances (LHCb-PAPER-2020-013) covered an X + b-jets mode with a 27-30 GeV region
and found nothing, but under a different production mode. ATLAS's 2026 Run-2 dimuon search
(arXiv:2601.21361) starts at 35 GeV.

**What is new here.** DELPHI recorded a Z-pole sample of similar size, with a silicon vertex
detector, muon chambers and lifetime b-tagging. The collaboration released all of its data
and software in August 2024 (CERN Open Data, CC0). A prior-art search on 2026-11-17 found no
DELPHI or OPAL test of the ALEPH excess. DELPHI would be the first test with acceptance
comparable to ALEPH's, from the same collider, energy and production mode.

**Why it matters.** If DELPHI saw a compatible peak, a 30 GeV boson coupling to b quarks and
muons would be the most important particle-physics result in years. If it sees none, an
ALEPH-sized signal is excluded or disfavoured, closing a nine-year-old anomaly with the only
dataset that can test it directly. Both outcomes are publishable.

## 2. Rough sensitivity (to be replaced by simulation)

ALEPH's signal rate is 32.3 / 1.9M = 1.7e-5 per hadronic Z after its selection. DELPHI
1994 (short94_c2, 46 pb^-1, about 1.2M events after a standard hadronic selection) plus 1995
at the peak (short95_d2, 15.1 pb^-1, about 0.4M) is about 1.6M hadronic events (numbers from
arXiv:2510.18762). With DELPHI efficiencies equal to ALEPH's this gives about 27 signal
events; adding 1992-1993 roughly doubles that. ALEPH's background was about 1,457 pairs in
15-50 GeV, so with a resolution near 0.75 GeV and a 1.8 GeV width a window of about +-2.5 GeV
holds about 15-20 % of the background. That is roughly 220-290 pairs for ALEPH-sized
background, giving S/sqrt(B) of about 1.6-1.8 sigma for 1994-95 (27 / sqrt(219 to 291))
and about 2.2-2.6 sigma with 1992-95 (54 / sqrt(438 to 582)). These numbers are only for planning. The real expectation comes from DELPHI's own
simulation of a signal sample (section 4), and is pre-registered before unblinding.

## 3. Data (public, CC0, cite the DOIs)

- Real data: `short94_c2` (doi:10.7483/OPENDATA.DELPHI.0XNE.G96F, about 429 files of about 90 MB);
  `short95_d2` (doi:10.7483/OPENDATA.DELPHI.K4LR.4PQ4); 1992-1993 short DSTs if the vertex
  detector configuration allows a comparable b-tag.
- Simulation: KK2f + PYTHIA Z -> q qbar, `sh_kk2f4146qqpy_e91.25_c94_2l_c2`
  (doi:10.7483/OPENDATA.DELPHI.P4BN.GFID) and the 1995 equivalent; a private signal sample
  (Z -> b bbar with X(30.4 GeV) -> mu+ mu- radiated from a b quark) passed through DELSIM with
  `runsim -gext`.
- Data policy: doi:10.7483/OPENDATA.DELPHI.0X8O.FBUH.
- Software: DELPHI container `gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd`,
  skelana framework, data read over xrootd from eospublic.cern.ch.

## 4. Analysis outline (selection to be frozen before unblinding)

1. Hadronic Z: DELPHI standard selection (at least 7 good charged tracks, total energy at least
   half of sqrt(s), thrust axis 30-150 degrees), as in arXiv:2510.18762.
2. b-tag: DELPHI lifetime b-tag (AABTAG), event or hemisphere probability; working point
   chosen on simulation for about 35-40 % b efficiency, close to ALEPH's.
3. Muons: DELPHI standard muon identification (MUFLAG, "standard" or "tight"), p > 2.5 GeV,
   |cos theta| < 0.95, track impact parameters close to the primary vertex.
4. Pairs: all opposite-sign mu+ mu- pairs, plus the controls: same-sign mumu, opposite-sign
   e-mu, and opposite-sign mumu with the b-tag inverted. Also e+e- as a second channel.
5. Suppressing semileptonic cascades as ALEPH did (missing momentum below 18 GeV;
   both muons consistent with the primary vertex).
6. Background: (a) a data-driven e-mu template corrected for the e/mu efficiency ratio,
   as ALEPH did; (b) a smooth parametric fit; (c) DELPHI q qbar simulation. The spread
   between them is taken as a systematic uncertainty.
7. Signal: Breit-Wigner(30.40, 1.78 GeV) convolved with DELPHI's simulated dimuon mass
   resolution.

## 5. Blinding and pre-registration (commitments made now)

- The opposite-sign dimuon mass window **26-35 GeV in b-tagged events stays blind** until
  version 1.0 of this plan is published with the frozen selection, background model,
  simulated signal efficiency, expected signal yield N_exp (ALEPH rate scaled by DELPHI's
  efficiency) and the statistical tests below.
- Allowed before unblinding: all control samples, the opposite-sign b-tagged spectrum outside
  26-35 GeV, simulation, and event counts that do not reveal the window.
- **Primary test (fixed hypothesis):** extended unbinned likelihood fit with m = 30.40 GeV and
  Gamma = 1.78 GeV fixed. Report the fitted yield mu_hat and its uncertainty in units of
  N_exp. Outcomes: "ALEPH-sized signal excluded at 95 % CL" (upper limit below N_exp),
  "compatible with ALEPH" (N_exp inside the 68 % interval and background-only rejected at
  2 sigma), or "inconclusive" (anything else).
- **Secondary:** a 15-50 GeV scan with free mass, local and global significance; the
  e+e- channel; the year-by-year consistency.
- Everything is published whatever the outcome, including a null or inconclusive result.

## 6. Steps and status

| step | status |
|---|---|
| prior-art search | done 2026-11-17 |
| feasibility probe (container, xrootd, example build) | job `delphi-probe-v1` filed 2026-11-17 |
| skelana ntuple writer (hadronic, b-tag, leptons) + tests on simulation | next |
| full-data ntuple production (no mass histograms in the window) | after that |
| signal simulation through DELSIM | after that |
| plan v1.0 frozen, then unblinding | later |

## References

- A. Heister, arXiv:1610.06536 (ALEPH archived data).
- K. Lane, L. Pritchett, arXiv:1701.07376; Les Houches 2017 NP report, arXiv:1803.10379.
- T. Hebbeker, S. Roth, arXiv:1905.01111 (L3).
- CMS Collaboration, JHEP 11 (2018) 161, arXiv:1808.01890.
- LHCb Collaboration, LHCb-PAPER-2020-013.
- ATLAS Collaboration, JHEP 06 (2026) 165, arXiv:2601.21361.
- DELPHI open data: opendata.cern.ch/docs/delphi-data-release-2024; first physics use:
  J. Zhang et al., arXiv:2510.18762.
