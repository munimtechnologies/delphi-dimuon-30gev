# delphi-dimuon-30gev

An open, pre-registered test of whether the **30 GeV dimuon excess** seen in archived ALEPH
data (Z -> b bbar events at LEP, arXiv:1610.06536) also appears in **DELPHI's open data** from
the same Z-pole running, and of what the excess can be. DELPHI released its full data and
software in 2024. As far as we can find, no DELPHI or OPAL test of this excess has been published.

By MV2 of Munim, Inc. (mv2@munimtech.com). The work is made with AI agents working in MV2's
name. It is not a DELPHI, ALEPH, L3 or OPAL Collaboration result, and neither these
collaborations nor CERN endorse it. **No physicist has checked these results yet.**

**Main result so far (2026-11-18): the excess is not a boson decaying to isolated muons.**
[NOTE-fourfermion.md](NOTE-fourfermion.md) (version 0.4) and the draft paper
[paper/DRAFT-lep1-4f-30gev.md](paper/DRAFT-lep1-4f-30gev.md) (not peer reviewed). If the excess
were a boson produced with b quarks (a vector or scalar radiated off the b, or Z -> h A), its two
muons would be isolated from the jets in 92-95 % of events. That is the signature ALEPH, L3 and
OPAL selected in 1994-96 to measure e+e- -> mu+ mu- q qbar at the Z pole. Applied to the boson
models, OPAL's published selection keeps **84-88 %** of the boson's events and L3's 59-68 % (job
`lep4f-eff-v2`, all seven expectations H1-H7 written beforehand passed). An ALEPH-sized boson
would then have put **about 150 events** into OPAL's and L3's published dimuon-mass plots between
20 and 40 GeV, where they show **one**. Even at the lowest rate quoted for the excess and with the
least favourable reading of every selection detail, the chance of seeing one or fewer is below
5 x 10^-12. Limits: hadron level, no detector simulation; the mass counts were read from scanned
figures by AI reading agents, twice and independently.

**Earlier result (2026-11-17): [NOTE-kinematics.md](NOTE-kinematics.md).** The same three boson
models put a muon within 15 degrees of a leading jet in only 5-11 % of events, while ordinary
Z -> b bbar does so in 99.4 %. ALEPH reports this "in all cases". Taken at face value, ALEPH's own
kinematics allow at most about 4-10 of its 32 fitted events to be such a boson (95 % CL).

**Third line, hand bound (version 0.2): [NOTE-higgs-searches.md](NOTE-higgs-searches.md).** All
four LEP experiments searched their Z-peak data for e+e- -> H Z*, Z* -> mu+ mu-: two isolated
muons recoiling against hadrons. ALEPH (4.5 million hadronic Z, including the data of the excess)
has two candidates that could be signal; L3, whose selection has no recoil-mass cut and so also
tests Z -> h A, has **none** in 3.05 million; DELPHI one in 0.94 million. By hand the boson
survives only if these selections kept fewer than about 2.5 % of its events. Jobs `efhz-v1` and
`lephz-v1` (queued) measure the efficiencies against expectations J1-J7 and L1-L10. The readings of
the five papers are in [readings/lephz-notes.md](readings/lephz-notes.md).

**What is left, and what DELPHI tests.** If the excess is real, its muons must sit inside the b
jets, as ALEPH describes: cascade decays, a mismodelled background shape, or a new state decaying
within a jet. Test A replicates ALEPH's analysis on DELPHI's b-tagged events. Test B fits the
b-tagged and not-b-tagged spectra together (a boson produced with b quarks would put about 1.6
events in the not-tagged sample for every tagged one). Test C (to be pre-registered in plan v1.0)
uses isolated muon pairs without the b-tag, with the four-fermion background from DELPHI's own
EXCALIBUR simulation.

**Two flaws caught before unblinding, and the fix chosen by a written rule.**
[PLAN-amendment-0.12.md](PLAN-amendment-0.12.md): in the not-b-tagged spectrum, the
pre-registered background rule can fake a *negative* signal (mu_hat = 0.51 for an injected
ALEPH-sized signal on noise-free pseudo-data), which would favour a false exclusion.
[PLAN-amendment-0.13.md](PLAN-amendment-0.13.md): in the b-tagged spectrum, the same rule keeps a
degree-2 background that fakes +0.52 of an ALEPH-sized signal on a realistic Pythia shape, which
would favour a false *confirmation* (job `dimu-bbspur-v1`, expectations M1-M6, queued).
[PLAN-amendment-0.14.md](PLAN-amendment-0.14.md) (new, 2026-11-18): job `dimu-envcast-v1` scored
five background treatments on eight pseudo-data scenarios. Only a **fixed degree-3 background in
every category** keeps the fake signal below 0.2 standard deviations everywhere; the
discrete-profiling envelope (penalty one unit per parameter, over the same five functions) fails
in one of these scenarios (+0.29 sigma when the b bbar shape is exponential). Expectations K0, K1, K2, K4 and K5 passed, K3 failed (the envelope), K6 and K7 could
not be graded (only 10 toys finished). Job `dimu-envtoys-v1` now runs 200 pseudo-experiments to
check that the degree-3 choice does not exclude a real ALEPH-sized boson more than 7 % of the time
(expectations N0-N5).

**What "ALEPH-sized" means (plan v0.11, section 5f).** The expected signal is one written
formula in produced Z decays (`analysis/nexp.py`). ALEPH's paper leaves its hadronic event count
open (about 1.9M selected where about 2.2M were expected), so every result is computed under both
readings, and EXCLUDED or COMPATIBLE is claimed only if both agree.

## Contents

- [PLAN.md](PLAN.md): the question, sensitivity estimate, data, analysis outline and the
  **blinding commitments** (the 26-35 GeV opposite-sign dimuon window stays closed until the
  selection and tests are frozen and published here as plan v1.0). Amendments
  [0.12](PLAN-amendment-0.12.md), [0.13](PLAN-amendment-0.13.md) and
  [0.14](PLAN-amendment-0.14.md).
- [paper/](paper/): the draft paper on the four-fermion result (not peer reviewed).
- [NOTE-kinematics.md](NOTE-kinematics.md), [NOTE-fourfermion.md](NOTE-fourfermion.md),
  [NOTE-higgs-searches.md](NOTE-higgs-searches.md): the three external tests, each with its
  pre-registered expectations, grades and limits.
- [readings/](readings/): notes from the published LEP1 papers, made by AI agents reading the
  scanned papers.
- [probe/](probe/): a feasibility probe that runs in the public DELPHI container
  (`gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd`): xrootd access to the 1994
  short DSTs, the stock skelana example, the manuals as text.
- [xkin/](xkin/): signal generator and kinematic study. Exact tree-level e+e- -> Z -> b bbar X
  (X -> mu mu) for a vector or scalar X radiated off the b line, and Z -> h A; Pythia 8
  hadronisation; ALEPH-style muon-jet angles; a writer for DELSIM's external-generator input
  (FADGEN). Tests `python -m unittest -v test_xkin`; run
  `python run_xkin.py --out OUT --nsig 20000 --nbkg 600000` (needs `numpy`, `pythia8mc`).
  `results/` holds the xkin-v1 output; `bound.py` turns it into the limit on boson events.
- [ntuple/](ntuple/): the DELPHI ntuple writer (`mv2user02.car`, a skelana USER02 routine that
  writes one line per event with hadronic flags, b-tag probabilities, thrust and, for events with
  two or more lepton candidates, every particle with its muon and electron tags; **no masses**).
  `run_ntuple.sh` builds and runs it in the DELPHI container on data and simulation over xrootd,
  for 1992 (`Y13723`), 1993 (`Y12340`), 1994 (`Y13709 Y13710`) or 1995 (`Y13716`).
  `validate.py` makes the detector checks and never shows a data dimuon mass above 5 GeV in
  hadronic events. Tests: `python -m unittest -v test_validate`.
- [val9293/](val9293/): validation on DELPHI's 1992 and 1993 data.
- [fourf/](fourf/): runs the ntuple code on DELPHI's EXCALIBUR e+e- -> mu mu q qbar simulation
  of 1992-95 and on 1994 Z -> q qbar simulation, then `analysis/iso4f.py`. Simulation only.
- [prod/](prod/): the production-slice runner (pinned git ref, version guard) for the full-data
  pass; filed only after validation passes.
- [stats/](stats/): the pre-registered statistics. `dimustat.py` (test A: 50 MeV bins in 15-50 GeV,
  Voigt signal, log-Legendre background with a fixed degree rule, q0, asymptotic CLs),
  `dimucomb.py` (test B), `forecast.py`, `combcast.py`, `bkgsys.py` (spurious-signal test and
  discrete-profiling envelope), `envcast.py`, `envtoys.py` and `bbspur.py` (background-treatment
  scoring). Tests: `python -m unittest -v test_dimustat test_dimucomb test_bkgsys test_envtoys
  test_bbspur` (needs `numpy`, `scipy`; `pythia8mc` for forecast and bbspur).
- [delsim/](delsim/): the signal through DELPHI's own detector simulation (`run_delsim.sh`,
  `runsim -gext`, `sigana.py` for resolution and efficiencies). Tests:
  `python -m unittest -v test_sigana`.
- [analysis/](analysis/): `dimusel.py` (spectra; **blinding enforced in the code**: in real data
  no opposite-sign same-flavour pair in 26-35 GeV is histogrammed until a plan file marked v1.x is
  given), `btagcal.py` (b-tag efficiency by hemisphere double tag), `nexp.py` (expected signal),
  `lep4f.py` (limits from the published four-fermion counts), `eff4f.py` 0.2.0 and
  `run_eff4f.py` (the published four-fermion selections on the boson models), `efhz.py` and
  `lephz.py` (the LEP1 Higgs-search selections), `iso4f.py` (isolated pairs in simulation).
  [analysis/results/](analysis/results/) holds the output of `lep4f-eff-v2` and, in `envcast/`,
  of `dimu-envcast-v1`. Tests:
  `python -m unittest -v test_dimusel test_btagcal test_nexp test_lep4f test_iso4f test_eff4f
  test_efhz test_lephz`. Runs: `python run_eff4f.py --out OUT --nsig 10000 --workers 2`,
  `python run_lephz.py --out OUT` (need `numpy`, `pythia8mc` and the `xkin/` modules alongside).
- [reviews/](reviews/): hand reviews of the code, with what was found and fixed.

## Status

Plan v0.11 plus amendments 0.12, 0.13 and 0.14, 2026-11-18. No DELPHI dimuon mass from real data
has been looked at yet. Returned and graded: the kinematic study (xkin-v1, E1-E3 passed), the
analysis-code tests (dimusel, btagcal, sigana, nexp), the test-B forecast (combcast-v1: background
flaw found, amendment 0.12), the four-fermion limits (lep4f-v1: 11/11 tests), the four-fermion
efficiencies (**lep4f-eff-v2: H1-H7 passed**), the test-A forecast (dimu-forecast-v2: its Asimov
part found the bias of amendment 0.13) and the background-treatment scoring (**dimu-envcast-v1:
degree 3 is the only eligible treatment that passes**, amendment 0.14). Still queued: the DELPHI
probe, ntuple, validation and detector-simulation jobs, the four-fermion simulation (fourf), the
Higgs-search efficiency jobs (efhz-v1, lephz-v1), bbspur-v1 and envtoys-v1. Each will be graded
against the expectations written before it ran. Results, positive, negative or inconclusive, will
all be published here.

## Data and licences

DELPHI open data are CC0 (cite doi:10.7483/OPENDATA.DELPHI.0X8O.FBUH and each dataset's DOI).
Code in this repository is Apache-2.0; text and result tables are CC BY 4.0. Pythia 8
(`pythia8mc`) is GPL-2.0-or-later and is installed separately, not bundled here. The meanings
of the skelana common-block words were read from the public SKELANA decks and the
delphi-nanoaod headers (GPL-3.0); no code from those projects is copied here. The DELSIM
run steps follow the public documentation of the delphi-sim-pipeline project and the CERN Open
Data simulation guide; no code from that project is copied here. The published LEP1
four-fermion and Higgs-search numbers are quoted from the cited papers.
