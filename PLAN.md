# Analysis plan v0.6: does DELPHI see ALEPH's 30 GeV dimuon excess?

MV2 of Munim, Inc. (mv2@munimtech.com). v0.1 written 2026-11-17 06:58 UTC; v0.2 08:30 UTC;
v0.3 09:45 UTC; v0.4 10:50 UTC; v0.5 11:45 UTC; v0.6 12:40 UTC. Made with AI agents working in
MV2's name. This is a plan, not a result: as of v0.6, no DELPHI dimuon mass from real data has
been looked at. Not a DELPHI Collaboration result; DELPHI and CERN do not endorse it. Text
CC BY 4.0, code Apache-2.0.

Changes from v0.5: new section 4f, the analysis stage from ntuple to mass spectra
(`analysis/dimusel.py`, tested by job `dimusel-tests-v1`). It **tightens the blinding** of
section 5: in real data every opposite-sign same-flavour category (mumu and ee; b-tagged,
untagged and anti-tagged) is blind in 26-35 GeV, including the inverted-b-tag mumu control
that v0.1 allowed. The window can only be opened by the code when given a plan file whose first
line reads "Analysis plan v1.x". Sections 5 and 6 updated accordingly. Nothing else changed.

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
and software in August 2024 (CERN Open Data, CC0). Prior-art searches on 2026-11-17 (repeated
at 12:20 UTC) found no DELPHI or OPAL test of the ALEPH excess. DELPHI would be the first test
with acceptance comparable to ALEPH's, from the same collider, energy and production mode.

**Why it matters.** If DELPHI saw a compatible peak, a 30 GeV boson coupling to b quarks and
muons would be the most important particle-physics result in years. If it sees none, an
ALEPH-sized signal is excluded or disfavoured, closing a nine-year-old anomaly with the only
dataset that can test it directly. Both outcomes are publishable.

## 2. Rough sensitivity (replaced by the forecast of 5c, then by simulation)

ALEPH's signal rate is 32.3 / 1.9M = 1.7e-5 per hadronic Z after its selection. DELPHI
1994 (short94_c2, 46 pb^-1, about 1.2M events after a standard hadronic selection) plus 1995
at the peak (short95_d2, 15.1 pb^-1, about 0.4M) is about 1.6M hadronic events (numbers from
arXiv:2510.18762, whose selection includes a thrust-axis cut of 30-150 degrees; 1995 also has
9.1 and 9.4 pb^-1 off peak). With DELPHI efficiencies equal to ALEPH's this gives about 27
signal events. The 1991-1993 data are in the open release too, taken with the older
three-layer single-sided vertex detector (arXiv:2510.18762 sec. 4); adding 1992-1993 roughly
doubles the sample. A hand estimate (section 5c) gives a median expected 95 % CLs limit of
about 1.2 times the ALEPH-sized yield for 1994-95 alone, and about 0.9 for 1992-95.

## 3. Data and software (public, CC0, cite the DOIs)

- Real data: `short94_c2` (doi:10.7483/OPENDATA.DELPHI.0XNE.G96F; CERN Open Data record 81431,
  429 files of 41-100 MB, `/eos/opendata/delphi/collision-data/Y13709/` and `Y13710/`);
  `short95_d2` (doi:10.7483/OPENDATA.DELPHI.K4LR.4PQ4); 1992-1993 short DSTs (see 5d).
- Simulation: KK2f + PYTHIA Z -> q qbar (`/eos/opendata/delphi/simulated-data/cern/kk2f4146/
  <detector version>/91.25/kk2f4146_qqpy_91.25_*.sdst`; the 1994 version is picked by the job)
  and the 1995 equivalent.
- Signal simulation (section 4e): events from `xkin/` (section 4b), hadronised with Pythia 8 and
  written in DELSIM's external-generator format (FADGEN, `xkin/fadgen.py`, following the layout
  described for `hepmc2fadgen.cpp` in github.com/delphi-fullDST-edm4hep/delphi-sim-pipeline),
  then passed through DELSIM, DELANA and the short-DST step with
  `runsim -VERSION v94c -EBEAM 45.594 -gext` (two-pass title with `LUDECV TRUE`, so DELSIM uses
  the generator's b-hadron decay vertices).
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
6. Background: (a) the smooth parametric fit of section 5b (primary); (b) a data-driven e-mu
   template corrected for the e/mu efficiency ratio, as ALEPH did; (c) DELPHI q qbar
   simulation. The spread between them is taken as a systematic uncertainty.
7. Signal: Breit-Wigner(30.40, 1.78 GeV) convolved with DELPHI's simulated dimuon mass
   resolution (section 4e).

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

## 4c. The ntuple (`ntuple/`, v0.3)

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

## 4e. Signal through DELPHI's detector simulation (job `delsim-signal-v1`, v0.5)

`delsim/run_delsim.sh` runs in the same public DELPHI container. It:

1. generates about 470 events of model V (section 4b; m = 30.40 GeV, Gamma = 1.78 GeV) with the
   published `xkin/` code and Pythia 8, written as FADGEN (10 % more events than are simulated,
   as the DELPHI simulation pipeline recommends);
2. checks how the container reaches DELPHI's condition database
   (`/eos/opendata/delphi/condition-data`): a 3-event built-in Z -> mu mu run is tried with the
   default environment, then with the database addressed over xrootd, then (if it is smaller than
   6 GB) with a local copy. The listing and total size of the database are saved either way;
3. simulates and reconstructs 400 signal events for the 1994 detector
   (`runsim -VERSION v94c -LABO CERN -NRUN 1001 -EBEAM 45.594 -gext`; a 5-event pre-run writes the
   title file, `LUDECV TRUE` is added after its `JSHORT` line, then the main run uses `-STITL`);
4. runs the ntuple routine on the simulated short DST (`delsim/mv2user02s.car`: identical to
   `ntuple/mv2user02.car` except that for simulated events, which have negative run numbers,
   every event's particles are written so that efficiencies have a complete denominator);
5. `delsim/sigana.py` matches each reconstructed event to its generated event (DELSIM keeps the
   order but may drop events) and each generated signal muon to a same-charge track within
   1 degree and 25 % in momentum, then reports: tracking and muon-tag efficiency; the
   efficiency of each ALEPH-like cut (IHAD4, NCTR4 >= 5, an opposite-sign muon-tagged pair in
   acceptance with mass 15-50 GeV, visible missing momentum < 18 GeV); the event b-tag
   probability of selected signal events at working points 0.1 to 0.001; the dimuon mass
   resolution (reconstructed minus generated pair mass, Gaussian-equivalent width from the
   interquartile range); and the 1/p resolution in bins of p. Tests: `python -m unittest -v
   test_sigana` (run inside the job before anything else).

This is simulation only: no real-data dimuon mass is involved, so blinding does not apply.

**Expectations written before the job runs:**

- D1 (feasibility, no prediction): which route, if any, reaches the condition database.
- D2: DELSIM uses the input events: at least 80 % of reconstructed events are matched to a
  generated event (at least one signal muon found; `f_reco_aligned`), and for events with both
  muons matched the median reconstructed pair mass is within 0.3 GeV of the median generated
  pair mass.
- D3: the dimuon mass resolution at about 30 GeV (interquartile width / 1.349) is between 0.25
  and 0.75 GeV (0.8-2.5 % of the mass). ALEPH used 0.745 GeV.
- D4: for generated signal muons in acceptance that have a matched track, the muon-tag
  efficiency (any MUCAL2 level) is between 0.70 and 0.95.
- D5: the fraction of simulated signal events passing IHAD4, NCTR4 >= 5, an opposite-sign
  muon pair in acceptance with mass 15-50 GeV and missing momentum < 18 GeV is between 0.35
  and 0.70.
- D6: the 1/p resolution for 15-20 GeV muons is between 0.0005 and 0.0015 GeV^-1.

**What happens next.** The measured resolution replaces ALEPH's sigma in the fit of 5b. The
efficiency, together with the b-tag working point chosen on the KK2f Z -> b bbar simulation for
about 38 % b efficiency, gives N_exp = (ALEPH signal rate per hadronic Z) x (DELPHI hadronic
count) x (DELPHI efficiency / ALEPH efficiency for the same model), with ALEPH's efficiency
estimated from the generator-level acceptance of the same events times ALEPH's quoted muon (86 %
per muon) and b-tag efficiencies. If D1 finds no working route, the resolution is taken from
DELPHI's measured Z -> mu mu and J/psi widths in data (validation 4d) and the efficiency from the
KK2f simulation's prompt muons, and this is stated as a limitation.

## 4f. From ntuple to mass spectra (`analysis/dimusel.py`, new in v0.6)

One pure-Python program (no dependencies) turns the ntuple into everything the fit of 5b and
the controls need. It reads one DELPHI file's ntuple at a time, so the full 1994-95 production
fits in about 1 GB of memory.

- **Hadronic events**: IHAD4 > 0, NCTR4 >= 5, b-tag thrust axis (QBTTHR) at 30-150 degrees
  (|cos| < 0.866; the cut can be switched off if validation shows the axis is not filled).
- **b-tag**: event probability QBTPRP(3) below a working point (placeholder 0.01; fixed in v1.0
  from KK2f simulation for about 38 % b efficiency). Anti-tag: QBTPRP(3) > 0.1.
- **Leptons**: p > 2.5 GeV, |cos theta| < 0.95, |d0| < 0.2 cm and |z0| < 1.0 cm to the primary
  vertex (placeholders until V5 shows the measured spread). Muons: any MUCAL2 tag (or
  "standard"); electrons: ELECID "standard" or better and not tagged as a conversion; a track
  that is both is a muon.
- **Cascade veto**: visible missing momentum (all particles of the event) below 18 GeV.
- **Isolated selection** (secondary, section 4b): e+e- anti-kt jets (R = 0.4, E-scheme, the
  same definition as `xkin/evana.py`) built without the leptons; a lepton is isolated if it is
  more than 20 degrees from every jet above 3 GeV.
- **Categories** (all pairs in an event are counted, as ALEPH did): opposite-sign mumu b-tagged
  (primary), isolated b-tagged, untagged and anti-tagged; opposite-sign ee b-tagged, isolated
  b-tagged and anti-tagged; same-sign mumu (b-tagged, untagged); e-mu opposite-sign (b-tagged,
  untagged) and same-sign (b-tagged).
- **Output**: per category, the 700 bins of 50 MeV over 15-50 GeV used by `stats/dimustat.py`
  and 0.5 GeV bins over 0-90 GeV; and the cut flow (event counts after each cut, the hadronic,
  b-tagged and anti-tagged event totals that enter N_exp).

**Blinding in code (tightened in v0.6).** In real data, every opposite-sign same-flavour
category is blind in [26, 35) GeV: such a pair is dropped at the single place where masses
enter a histogram, the overlapping bins are written as null, and no category total is written
from which the window could be recovered by subtraction. This is stricter than v0.1, which
allowed the inverted-b-tag mumu control before unblinding: since the b-tag keeps only about
38 % of b events, untagged and anti-tagged Z -> b bbar events would carry most of any real
signal. Same-sign and e-mu pairs and all simulation stay open. The window opens only when the
program is given a plan file whose first line reads "Analysis plan v1.x"; that file's SHA-256 is
written into the output. Tests (`python -m unittest -v test_dimusel`, 17 tests, synthetic
events): the window stays hidden for every blinded category and its edges, sidebands and controls
stay visible, simulation is open, the unblind gate refuses this v0.6 plan, and each cut and the
jet clustering behave as specified. They run in job `dimusel-tests-v1`.

## 5. Blinding and pre-registration (commitments made in v0.1, tightened in v0.6)

- The opposite-sign dimuon mass window **26-35 GeV in b-tagged events stays blind** until
  version 1.0 of this plan is published with the frozen selection, background model,
  simulated signal efficiency, expected signal yield N_exp (ALEPH rate scaled by DELPHI's
  efficiency) and the statistical tests below. Since v0.6 the same holds for every
  opposite-sign mumu and ee category in data, whatever its b-tag (section 4f).
- Allowed before unblinding: same-sign and e-mu control samples, all opposite-sign spectra
  outside 26-35 GeV, simulation, and event counts that do not reveal the window.
- **Primary test (fixed hypothesis):** extended likelihood fit with m = 30.40 GeV and
  Gamma = 1.78 GeV fixed. Report the fitted yield mu_hat and its uncertainty in units of
  N_exp. Outcomes: "ALEPH-sized signal excluded at 95 % CL" (upper limit below N_exp),
  "compatible with ALEPH" (N_exp inside the 68 % interval and background-only rejected at
  2 sigma), or "inconclusive" (anything else).
- **Secondary:** a 15-50 GeV scan with free mass, local and global significance; the
  e+e- channel; the year-by-year consistency; the inverted-b-tag control (after unblinding);
  and (new in v0.2, to be defined exactly in v1.0) the isolated-muon selection of section 4b.
- Everything is published whatever the outcome, including a null or inconclusive result.

## 5b. The statistical procedure, exactly (new in v0.4; code `stats/dimustat.py`)

- **Histogram**: opposite-sign dimuon masses in 15-50 GeV in 700 bins of 50 MeV (at a mass
  resolution of 0.3-0.75 GeV this is equivalent to the unbinned fit of v0.3).
- **Signal**: Voigt profile (Breit-Wigner of width Gamma convolved with a Gaussian of width
  sigma), truncated to 15-50 GeV; the yield n_s counts signal events in 15-50 GeV, as ALEPH's
  32.3 does. Primary: m = 30.40 GeV, Gamma = 1.78 GeV, sigma = DELPHI's simulated dimuon mass
  resolution at 30 GeV (section 4e; until it exists: ALEPH's sigma = sqrt(6e-4) m = 0.745 GeV).
- **Background**: f(m) proportional to exp(sum_{k=1..n} a_k P_k(t)), with P_k the Legendre
  polynomials and t = ln m mapped linearly onto [-1, 1] over 15-50 GeV. n = 1 is a pure power
  law, ALEPH's exp(-c0 ln x) cross-check form.
- **Degree rule (fixed now)**: fit the background-only model to the sidebands 15-26 and
  35-50 GeV only, with n = 1, 2, ... 5; take the first n for which adding one more term improves
  -2 ln L by less than 3.84 (chi2 with one degree of freedom, 95 %). The window is never
  used to choose n.
- **Statistics**: extended Poisson likelihood with the background normalisation and shape
  free. Discovery: q0 (one-sided), Z0 = sqrt(q0). Limits: q~_mu with asymptotic CLs (Cowan,
  Cranmer, Gross, Vitells, EPJC 71 (2011) 1554, eqs. 65-66), sigma from the background-only
  Asimov set. 68 % interval for the "compatible" outcome: 2 Delta ln L < 1 at n_s = N_exp.
  If the final N_exp gives fewer than 10 expected signal events, the limit will also be
  computed with toys and the toy value is quoted.
- **Scan**: masses 16-49 GeV in steps of 0.25 GeV, Gamma fixed at 1.78 GeV, sigma = resolution
  at each mass; global significance from background-only toys and the Gross-Vitells
  upcrossing formula, both reported.

## 5c. Sensitivity forecast (job `dimu-forecast-v1`): expectations written before it runs

`stats/forecast.py` draws toy data from a generator-level Pythia 8 Z -> b bbar opposite-sign
dimuon shape (both muons p > 2.5 GeV, |cos theta| < 0.95, at least 5 charged, visible missing
momentum < 18 GeV, momenta smeared by sigma(1/p) = 0.0006 (+) 0.008/p GeV^-1), scaled to ALEPH's
1457 background pairs times k r. Here k is DELPHI's hadronic-Z count over ALEPH's 1.9M
(0.84 for 1994-95 peak data, 1.6 for 1992-95) and r is DELPHI's selection efficiency over
ALEPH's (0.6, 0.8, 1.0; the background is assumed to scale the same way). Signal toys inject
mu N_exp events with N_exp = 32.31 k r and mu = 0, 0.66 (ALEPH's yield minus one standard
deviation) or 1. Every toy goes through the full procedure of 5b, including the degree rule.
Scenarios: S1-S3 (1994-95, r = 1.0, 0.8, 0.6), S4 (1992-95, r = 0.8), S5 (S2 with a 1.2 %
mass resolution), S6 (S2 with an exponential background instead of the Pythia shape).

A hand estimate (local background density about 29 pairs/GeV near 30 GeV for S2, Voigt FWHM
2.9 GeV, 10-20 % inflation from the free background shape) gives sigma(n_s) of about 13 events
for S2, against N_exp = 21.7. Expectations, written before the job runs:

- F1: S2 median expected CLs limit between 0.9 and 1.6 N_exp; S2 probability of excluding an
  ALEPH-sized signal when there is none, P(EXCLUDED | mu = 0), between 0.25 and 0.55.
- F2: S2 Asimov Z0 for an ALEPH-sized signal between 1.2 and 2.2.
- F3: S4 (1992-95) median limit 0.6-0.85 times S2's (statistics alone give 0.72).
- F4: for S2, a local Z of 3 at an arbitrary mass corresponds to a global Z between 1.6 and 2.4.
- F5: the degree chosen most often by the rule has a spurious signal below 0.3 sigma on the
  Pythia shape.
- F6: Pythia's opposite-sign pairs in 15-50 GeV per Z -> b bbar event lie below ALEPH's
  implied 0.93 % per b-tagged event (1457 / (1.9M x 0.216 x 0.38)), since ALEPH's sample also
  contains misidentified muons; a value above 0.93 % would mean the cuts are not ALEPH-like.

Caveats: the toys use a generator-level background shape and assume DELPHI's background
scales like its signal efficiency; ALEPH's fitted yield is the value at the most significant
point and is more likely to be an overestimate of any true signal than an underestimate.

## 5d. Data-scope rule (fixed now, before any DELPHI mass is seen)

If the forecast gives P(EXCLUDED | mu = 0) below 0.5 for 1994-95 in the most likely scenario
(S2), the analysis is extended to the 1992-1993 short DSTs before unblinding, provided the
validation checks of 4d pass on them with the older vertex detector (a b-tag efficiency within
a factor 1.3 of 1994's at the same mistag rate in simulation). If 1992-93 fails validation, the
analysis proceeds with 1994-95 and the limit is quoted as it comes out. This rule is fixed so
that the amount of data cannot be chosen after the window is seen.

## 6. Steps and status

| step | status |
|---|---|
| prior-art search | done 2026-11-17 (repeated 12:20 UTC, still none) |
| feasibility probe (container, xrootd, example build) | job `delphi-probe-v1` filed 2026-11-17, waiting |
| kinematic study + DELSIM input writer (`xkin/`) | job `xkin-v1` filed 2026-11-17, waiting |
| skelana ntuple writer (`ntuple/`) + validation run 1 (section 4d) | job `dimu-ntuple-v1` filed 2026-11-17, waiting |
| statistics code + sensitivity forecast (`stats/`, 5b-5c) | job `dimu-forecast-v1` filed 2026-11-17, waiting |
| signal through DELSIM: resolution and efficiency (`delsim/`, 4e) | job `delsim-signal-v1` filed 2026-11-17, waiting |
| analysis stage with blinding in code (`analysis/`, 4f) | job `dimusel-tests-v1` filed 2026-11-17, waiting |
| full-data ntuple production (no mass histograms in the window) | after validation |
| plan v1.0 frozen, then unblinding | later |

## References

- A. Heister, arXiv:1610.06536 (ALEPH archived data).
- K. Lane, L. Pritchett, arXiv:1701.07376; Les Houches 2017 NP report, arXiv:1803.10379.
- P. Ko, J. Li, arXiv:1610.07526.
- T. Hebbeker, S. Roth, arXiv:1905.01111 (L3).
- CMS Collaboration, JHEP 11 (2018) 161, arXiv:1808.01890.
- LHCb Collaboration, LHCb-PAPER-2020-013.
- ATLAS Collaboration, JHEP 06 (2026) 165, arXiv:2601.21361.
- G. Cowan, K. Cranmer, E. Gross, O. Vitells, Eur. Phys. J. C 71 (2011) 1554, arXiv:1007.1727.
- E. Gross, O. Vitells, Eur. Phys. J. C 70 (2010) 525, arXiv:1005.1891.
- M. Cacciari, G. P. Salam, G. Soyez, JHEP 04 (2008) 063 (anti-kt), arXiv:0802.1189.
- DELPHI open data: opendata.cern.ch/docs/delphi-data-release-2024; analysis guide
  opendata.cern.ch/docs/delphi-guide-analysis; simulation guide
  opendata.cern.ch/docs/delphi-guide-simulation; first physics use: J. Zhang et al.,
  arXiv:2510.18762.
- SKELANA common-block meanings as mirrored in github.com/eigen1907/delphi-nanoaod
  (delphi-analysis/include/skelana/*.hpp, GPL-3.0; read, not copied).
- R. K. Ellis, D. A. Ross, A. E. Terrano, Nucl. Phys. B178 (1981) 421 (massless limit check).
- DELPHI simulation pipeline (documentation read; no code copied):
  github.com/delphi-fullDST-edm4hep/delphi-sim-pipeline.
