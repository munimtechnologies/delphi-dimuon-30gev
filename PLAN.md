# Analysis plan v0.3: does DELPHI see ALEPH's 30 GeV dimuon excess?

MV2 of Munim, Inc. (mv2@munimtech.com). v0.1 written 2026-11-17 06:58 UTC; v0.2 08:30 UTC;
v0.3 09:45 UTC. Made with AI agents working in MV2's name. This is a plan, not a result: as of
v0.3, no DELPHI dimuon mass has been looked at. Not a DELPHI Collaboration result; DELPHI and
CERN do not endorse it. Text CC BY 4.0, code Apache-2.0.

Changes from v0.2: section 4c (the ntuple: exactly which DELPHI quantities are written) and
section 4d (expectations for the first validation run, written before it runs). Section 6
updated. The blinding in section 5 is unchanged.

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
and about 2.2-2.6 sigma with 1992-95 (54 / sqrt(438 to 582)). These numbers are only for
planning. The real expectation comes from DELPHI's own simulation of a signal sample
(section 4), and is pre-registered before unblinding.

## 3. Data and software (public, CC0, cite the DOIs)

- Real data: `short94_c2` (doi:10.7483/OPENDATA.DELPHI.0XNE.G96F; CERN Open Data record 81431,
  429 files of 41-100 MB, `/eos/opendata/delphi/collision-data/Y13709/` and `Y13710/`);
  `short95_d2` (doi:10.7483/OPENDATA.DELPHI.K4LR.4PQ4); 1992-1993 short DSTs if the vertex
  detector configuration allows a comparable b-tag.
- Simulation: KK2f + PYTHIA Z -> q qbar (`/eos/opendata/delphi/simulated-data/cern/kk2f4146/
  <detector version>/91.25/kk2f4146_qqpy_91.25_*.sdst`; the 1994 version is picked by the job)
  and the 1995 equivalent.
- Signal simulation: events from `xkin/` (section 4b), hadronised with Pythia 8 and written
  in DELSIM's external-generator format (FADGEN, `xkin/fadgen.py`, following the layout of
  `hepmc2fadgen.cpp` in github.com/delphi-fullDST-edm4hep/delphi-sim-pipeline), then passed
  through DELSIM with `runsim -VERSION v94c -EBEAM 45.594 -gext` (two-pass title with
  `LUDECV TRUE` so DELSIM uses the generator's decay vertices).
- Data policy: doi:10.7483/OPENDATA.DELPHI.0X8O.FBUH.
- Software: DELPHI container `gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd`,
  skelana built from the stock `dump` example with MV2's USER02 (`ntuple/`), data read over
  xrootd from eospublic.cern.ch.

## 4. Analysis outline (selection to be frozen before unblinding)

1. Hadronic Z: DELPHI standard selection (team-4 hadronic tag IHAD4, at least 5-7 good charged
   tracks, total energy at least half of sqrt(s), thrust axis 30-150 degrees), as in
   arXiv:2510.18762.
2. b-tag: DELPHI lifetime b-tag (AABTAG), event or hemisphere probability; working point
   chosen on simulation for about 35-40 % b efficiency, close to ALEPH's.
3. Muons: DELPHI standard muon identification (MUFLAG/MUCAL2, "standard" or "tight"),
   p > 2.5 GeV, |cos theta| < 0.95, track impact parameters close to the primary vertex.
4. Pairs: all opposite-sign mu+ mu- pairs, plus the controls: same-sign mumu, opposite-sign
   e-mu, and opposite-sign mumu with the b-tag inverted. Also e+e- as a second channel.
5. Suppressing semileptonic cascades as ALEPH did (missing momentum below 18 GeV;
   both muons consistent with the primary vertex).
6. Background: (a) a data-driven e-mu template corrected for the e/mu efficiency ratio,
   as ALEPH did; (b) a smooth parametric fit; (c) DELPHI q qbar simulation. The spread
   between them is taken as a systematic uncertainty.
7. Signal: Breit-Wigner(30.40, 1.78 GeV) convolved with DELPHI's simulated dimuon mass
   resolution.

## 4b. Kinematic study: would a real boson look like ALEPH's excess? (xkin, v0.2)

ALEPH reports (arXiv:1610.06536, sec. 4.2) that "in all cases one of the two muons from
di-muons is closer than 15 degrees to one of the leading jets", that the other muon-jet angle is
"typically in the range of 5 to 20 degrees", and (sec. 4.7) that cos theta* near 30 GeV prefers
forward/backward values. Lane and Pritchett (arXiv:1701.07376) noted qualitatively that a
Z -> X Y signal should not put the muons close to the b jets, but nobody has computed these
angles for explicit signal models. `xkin/` does this at generator level:

- **V**: e+e- -> Z -> b bbar X, X -> mu+ mu-, X a vector radiated off the b line (exact tree-level
  matrix element with full spin correlations, m = 30.40 GeV, Gamma = 1.78 GeV).
- **S**: the same with a scalar radiated off the b line.
- **P**: Z -> h A, h -> mu+ mu-, A -> b bbar (two 30.4 GeV spin-0 states, Lane-Pritchett type).
- **Background**: inclusive Pythia 8 Z -> b bbar, opposite-sign muon pairs.

All are hadronised with Pythia 8. They are compared at ALEPH-like cuts: muon p (or pT) > 2.5 GeV,
|cos theta| < 0.95; at least 5 charged; visible missing momentum < 18 GeV; 26 < m_mumu < 35 GeV;
e+e- anti-kt jets without leptons (R = 0.4, 0.7, 1.0); leading jet per thrust hemisphere.
Checks: Ward identity, Ellis-Ross-Terrano massless limit, Lorentz invariance, momentum
conservation (`xkin/test_xkin.py`).

**Expectations written down before the job ran** (they are not used for any DELPHI
decision):
- E1: for V, S and P, fewer than half of the window events have alpha_min < 15 degrees (R = 0.4).
- E2: for the b bbar background, more than 70 % of the window pairs have alpha_min < 15 degrees.
- E3: for V, S and P, at least 30 % of the window events have both muons more than 20 degrees
  from every jet above 3 GeV. For the background, at most 10 % do.

**Why it matters for DELPHI.** If E1-E3 hold, ALEPH's own kinematics fit ordinary semileptonic b
decays, not a boson radiated off a b quark or produced in Z -> h A. A DELPHI search can then add
a second, model-motivated selection with both muons away from jets. There the b bbar background
is small, so DELPHI could be more sensitive to a real boson than an ALEPH-style replica. Any
such selection will be fixed in v1.0, before unblinding.

## 4c. The ntuple (`ntuple/`, new in v0.3)

A skelana USER02 routine (`ntuple/mv2user02.car`, Fortran, Apache-2.0) writes, after `PSBEG`:

- **Every event** ('E' line): run, event, IHAD4 (team-4 hadronic tag), NCTR4, NCTRK, NVECP,
  number of lepton candidates; ECMAS, ECHAR, EMNEU, EHNEU; the AABTAG probabilities
  QBTPRN, QBTPRP, QBTPRS for hemisphere 1, hemisphere 2 and the whole event (negative-, positive-
  and all-impact-parameter tracks); the b-tag thrust axis and thrust value QBTTHR(1..4).
- **Events with at least two charged lepton candidates** of p > 2 GeV (any MUCAL2 muon tag
  KMUID(1) > 0, or ELECID tag KELID(1) >= 3): every particle ('P' lines) with charge, lock word
  LVLOCK, KMUID(1) and KMUID(3) (tag and hit pattern), QMUID(2) (loose refit chi2), KELID(1..2)
  (electron and conversion tags), vertex-detector R-phi and z hits KTRAC(32..33), the
  four-momentum VECP(1..4), the perigee words QTRAC(4..5), and the impact parameters to the
  primary vertex QTRAC(38..39) and to the beam spot QTRAC(40).

The muon "standard" level is bit 2 of KMUID(1); the electron levels are KELID(1) = 2 very
loose, 3 loose, 4 standard, 5 tight. The routine computes no masses. These word meanings come
from the public SKELANA common decks (as mirrored in the delphi-nanoaod headers); the first
validation run (4d) checks them on data and simulation before anything depends on them.

## 4d. Validation run 1 (job `dimu-ntuple-v1`): expectations written before it runs

The job builds the routine in the DELPHI container and runs it on 6 short94_c2 data files
(every 40th file of Y13709) and up to 4 KK2f Z -> q qbar simulation files. `ntuple/validate.py`
then reports detector checks. Blinding is stricter than section 5 requires: in data events
with 5 or more charged tracks no dimuon mass at or above 5 GeV is stored, printed or
histogrammed.

- V1: the build succeeds and the 'E' lines show IHAD4 > 0 for most events with NCTR4 >= 5.
- V2: in low-multiplicity data events (NCTR4 <= 4), opposite-sign pairs of muon-tagged tracks
  above 15 GeV peak at the Z: median mass within 88-94 GeV.
- V3: in hadronic data events, opposite-sign muon pairs show a J/psi peak: the 3.0-3.2 GeV
  bins hold more pairs than the mean of the 2.5-2.9 and 3.3-3.7 GeV bins.
- V4: data and simulation agree to within a factor 1.3 on the fraction of hadronic events with
  event b-tag probability QBTPRP(3) below 0.01, and on the number of muon-tagged tracks
  above 2 GeV per hadronic event.
- V5: the median |d0| of muon candidates (to the primary vertex) is below 0.1 cm in data and
  simulation.

A failed V-check means the word mapping or the selection is wrong. It will be fixed and the
validation repeated before any further step. With 6 files (about 1-2 % of 1994), V3 and V4 may
be limited by statistics; this will be reported as such.

## 5. Blinding and pre-registration (commitments made in v0.1, unchanged)

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
  e+e- channel; the year-by-year consistency; and (new in v0.2, to be defined exactly in v1.0)
  the isolated-muon selection of section 4b.
- Everything is published whatever the outcome, including a null or inconclusive result.

## 6. Steps and status

| step | status |
|---|---|
| prior-art search | done 2026-11-17 |
| feasibility probe (container, xrootd, example build) | job `delphi-probe-v1` filed 2026-11-17, waiting |
| kinematic study + DELSIM input writer (`xkin/`) | job `xkin-v1` filed 2026-11-17, waiting |
| skelana ntuple writer (`ntuple/`) + validation run 1 (section 4d) | job `dimu-ntuple-v1` filed 2026-11-17, waiting |
| full-data ntuple production (no mass histograms in the window) | after validation |
| signal simulation through DELSIM | after the probe (needs condition data access) |
| plan v1.0 frozen, then unblinding | later |

## References

- A. Heister, arXiv:1610.06536 (ALEPH archived data).
- K. Lane, L. Pritchett, arXiv:1701.07376; Les Houches 2017 NP report, arXiv:1803.10379.
- P. Ko, J. Li, arXiv:1610.07526.
- T. Hebbeker, S. Roth, arXiv:1905.01111 (L3).
- CMS Collaboration, JHEP 11 (2018) 161, arXiv:1808.01890.
- LHCb Collaboration, LHCb-PAPER-2020-013.
- ATLAS Collaboration, JHEP 06 (2026) 165, arXiv:2601.21361.
- DELPHI open data: opendata.cern.ch/docs/delphi-data-release-2024; analysis guide
  opendata.cern.ch/docs/delphi-guide-analysis; first physics use: J. Zhang et al., arXiv:2510.18762.
- SKELANA common-block meanings as mirrored in github.com/eigen1907/delphi-nanoaod
  (delphi-analysis/include/skelana/*.hpp, GPL-3.0; read, not copied).
- R. K. Ellis, D. A. Ross, A. E. Terrano, Nucl. Phys. B178 (1981) 421 (massless limit check).
- DELPHI simulation pipeline: github.com/delphi-fullDST-edm4hep/delphi-sim-pipeline.
