# delphi-dimuon-30gev

An open, pre-registered test of whether the **30 GeV dimuon excess** seen in archived ALEPH
data (Z -> b bbar events at LEP, arXiv:1610.06536) also appears in **DELPHI's open data** from
the same Z-pole running. DELPHI released its full data and software in 2024. As far as we can
find, no DELPHI or OPAL test of this excess has been published.

By MV2 of Munim, Inc. (mv2@munimtech.com). The work is made with AI agents working in MV2's
name. It is not a DELPHI Collaboration result, and neither DELPHI nor CERN endorses it.

**First result (2026-11-17): [NOTE-kinematics.md](NOTE-kinematics.md).** At hadron level and
with ALEPH's own jet definition, three explicit boson models (a vector or scalar radiated off a
b quark, and Z -> h A) put a muon within 15 degrees of a leading jet in only 5-11 % of events,
while ordinary Z -> b bbar does so in 99.4 %. ALEPH reports this "in all cases". Taken at face
value, ALEPH's own kinematics allow at most about 4-10 of its 32 fitted events to be such a
boson (95 % CL). This sharpens an earlier parton-level finding by Ko, Li and Yu
(arXiv:1610.07526). It is generator level only; the note lists its limits.

**Second result (version 0.3, 2026-11-18, not yet checked by a physicist): [NOTE-fourfermion.md](NOTE-fourfermion.md).**
Such a boson's muons are isolated from the jets in 92-95 % of events. That is the signature
ALEPH, L3 and OPAL selected in the early 1990s to measure e+e- -> mu+ mu- q qbar at the Z pole,
and their published counts agree with the Standard Model. Two independent readings of the papers
agree that OPAL's final selection has one mu mu q qbar event between 20 and 40 GeV and L3's has
none, where an ALEPH-sized boson would have put of order a hundred. The exact limits (job
`lep4f-v1`, returned 2026-11-18, 11 of 11 tests passed) match the hand values: the published
totals alone allow the boson only if the selections kept fewer than about 6 % of its events.
`analysis/eff4f.py` 0.2.0 codes the three selections as written, and a queued job measures their
efficiency for the boson models, against expectations H1-H7 written in the note first.

**Third result (version 0.2, 2026-11-18, hand bound, not yet checked by a physicist): [NOTE-higgs-searches.md](NOTE-higgs-searches.md).**
All four LEP experiments searched their full Z-peak data for e+e- -> H Z*, Z* -> mu+ mu-:
two energetic, isolated muons recoiling against hadrons, which is what a boson radiated off b
quarks would give. Their selections and candidates have now been read
([readings/lephz-notes.md](readings/lephz-notes.md)). ALEPH (4.5 million hadronic Z, including
the data of the excess) found three candidates. One of them recoils at 66.9 GeV, too heavy for a
30 GeV muon pair. L3, whose selection has no recoil-mass cut and so also tests Z -> h A, found
**none** in 3.05 million. DELPHI found one in 0.94 million, and OPAL one, at a dimuon mass of
about 17 GeV. At the excess's own rate, ALEPH, L3 and DELPHI together would have recorded about
315 x eps boson events, against 3 that could be signal. **By hand, the boson survives only if
these selections kept fewer than about 2.5 % of its events** (9 % at the lowest rate quoted in the
literature), while the same selections kept 32-55 % of Higgs events with a similar topology.
`analysis/lephz.py` 0.1.0 codes the L3, DELPHI and OPAL selections next to ALEPH's
(`analysis/efhz.py`). Jobs `efhz-v1` and `lephz-v1` measure the efficiencies, against
expectations J1-J7 and L1-L10 written first. If they confirm the hand bound, the excess cannot be
a boson decaying to isolated muons, and a real effect would have to live inside the b jets.
As far as we can find, no paper citing the excess uses the LEP1 Higgs searches.

**Two flaws caught before unblinding.** [PLAN-amendment-0.12.md](PLAN-amendment-0.12.md): in
the not-b-tagged spectrum, the pre-registered background rule can fake a *negative* signal
(mu_hat = 0.51 for an injected ALEPH-sized signal on noise-free pseudo-data), which would favour a
false exclusion. Five background treatments are now scored on pseudo-data by written criteria
(job `dimu-envcast-v1`, expectations K0-K7). [PLAN-amendment-0.13.md](PLAN-amendment-0.13.md):
the forecast job (`dimu-forecast-v2`) showed the opposite problem in the b-tagged spectrum of
test A. On a realistic Pythia Z -> b bbar dimuon shape, the same rule keeps a degree-2
background, which fakes +0.52 of an ALEPH-sized signal (mu_hat = 1.54 instead of 1), so it
would favour a false *confirmation*. On an exactly representable shape every degree gives 0.00,
so the fit itself is right. The decision rule now also has to pass four scenarios built from the
generator shape (job `dimu-bbspur-v1`, expectations M1-M6).

**Two pre-registered primary tests (plan v0.9, refined in v0.10-v0.13).** Test A replicates
ALEPH's analysis on DELPHI's b-tagged events. Test B asks whether there is an ALEPH-sized boson
produced together with b quarks. Such a boson would put about 1.6 events in the not-b-tagged
sample for every tagged one, so test B fits both samples at once. **A third test (C, to be
pre-registered in plan v1.0)** uses isolated muon pairs without the b-tag, where a boson would
give on the order of 100 events in 1992-95. Its four-fermion background comes from DELPHI's own
EXCALIBUR simulation.

**What "ALEPH-sized" means (plan v0.11, section 5f).** The expected signal is one written
formula in produced Z decays (`analysis/nexp.py`). ALEPH's paper itself leaves its hadronic
event count open (about 1.9M selected where about 2.2M were expected), so every result is
computed under both readings, and EXCLUDED or COMPATIBLE is claimed only if both agree.

- [PLAN.md](PLAN.md): the question, sensitivity estimate, data, analysis outline and the
  **blinding commitments** (the 26-35 GeV opposite-sign dimuon window stays closed until the
  selection and tests are frozen and published here as plan v1.0).
  [PLAN-amendment-0.12.md](PLAN-amendment-0.12.md): section 5g (background treatment), the
  grading of the test-B forecast (G1-G6) and expectations K0-K7.
  [PLAN-amendment-0.13.md](PLAN-amendment-0.13.md): the grading of the forecast job, the tagged
  background scenarios C9-C12 added to 5g, and expectations M1-M6.
- [NOTE-kinematics.md](NOTE-kinematics.md): the kinematic study's result, its pre-registered
  grades (E1-E3, all passed) and what it changes for the DELPHI test.
- [NOTE-fourfermion.md](NOTE-fourfermion.md): the bounds from the published LEP1
  mu+ mu- q qbar counts and dimuon-mass distributions, their inputs (three readings of the boson
  rate), the expectations H1-H7 for the efficiency job, and the limits of the argument.
- [NOTE-higgs-searches.md](NOTE-higgs-searches.md): the bound from the four LEP1 Higgs searches
  (H mu+ mu- channel): the selections, which candidates can be signal, the hand table,
  expectations J1-J7 (ALEPH) and L1-L10 (all four), and the limits.
- [readings/](readings/): notes from the published LEP1 papers, made by AI agents reading the
  scanned papers.
- [probe/](probe/): a feasibility probe that runs in the public DELPHI container
  (`gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd`). It checks xrootd access to
  the 1994 short DSTs, builds the stock skelana example, and extracts the manuals as text.
- [xkin/](xkin/): signal generator and kinematic study (PLAN section 4b). Exact tree-level
  e+e- -> Z -> b bbar X (X -> mu mu) for a vector or scalar X radiated off the b line, and
  Z -> h A; Pythia 8 hadronisation; ALEPH-style muon-jet angles, cos theta*, muon multiplicity;
  and a writer for DELSIM's external-generator input (FADGEN). Run the tests with
  `python -m unittest -v test_xkin`; run the study with
  `python run_xkin.py --out OUT --nsig 20000 --nbkg 600000` (needs `numpy`, `pythia8mc`).
  `results/` holds the xkin-v1 output; `bound.py` turns it into the limit on boson events
  (`python bound.py --summary results/xkin-v1-summary.json --out bound.json`; tests:
  `python -m unittest -v test_bound`, standard library only).
- [ntuple/](ntuple/) (plan v0.3, production switches in v0.7, periods in v0.8): the DELPHI
  ntuple writer. `mv2user02.car` is a skelana USER02 routine that writes one line per event
  (hadronic flags, energies, the DELPHI lifetime b-tag probabilities, thrust) and, for events with
  two or more charged lepton candidates, every particle with its muon tag (MUCAL2), electron tag
  (ELECID), vertex-detector hits and impact parameters. It writes **no masses**. `run_ntuple.sh`
  builds it inside the DELPHI container from the stock `dump` example and runs it on data and
  Z -> q qbar simulation read over xrootd; environment switches (`DATA_DIRS`, `DATA_START`,
  `DATA_STRIDE`, `NDATA`, `MC_VERSION`, `NMC`, `SLICE`, `PERIOD`) select a production slice of
  1992 (`Y13723`), 1993 (`Y12340`), 1994 (`Y13709 Y13710`) or 1995 (`Y13716`). With the
  analysis code alongside, it also writes blinded spectra for the pre-declared grid of b-tag
  working points in `configs/`. `validate.py` makes the detector checks (Z -> mu mu,
  J/psi -> mu mu, tag rates, b-tag and impact-parameter distributions, data vs simulation) and
  never stores, prints or histograms a data dimuon mass above 5 GeV in hadronic events. Tests:
  `python -m unittest -v test_validate`.
- [val9293/](val9293/) (plan v0.8): validation run 2, on DELPHI's 1992 and 1993 data, taken
  before the vertex detector had z readout. `run_val9293.sh` fetches the published code from
  this repository and runs `ntuple/run_ntuple.sh` once per year.
- [fourf/](fourf/): `run_4f.sh` runs the published ntuple code on DELPHI's EXCALIBUR
  e+e- -> mu mu q qbar simulation of 1992-95 and on 1994 Z -> q qbar simulation, then
  `analysis/iso4f.py`. Simulation only.
- [prod/](prod/): the production-slice runner (pinned git ref, version guard) and job
  templates for the full-data pass of PLAN section 4h; filed only after validation passes.
- [stats/](stats/) (plan v0.4, test B in v0.9, background treatment in v0.12-v0.13): the
  pre-registered statistics and sensitivity forecasts. `dimustat.py` is the fit for test A:
  50 MeV bins in 15-50 GeV, Voigt signal (m = 30.40, Gamma = 1.78 GeV), a log-Legendre
  background whose degree is chosen on the sidebands by a fixed rule, the discovery statistic
  q0, and asymptotic CLs upper limits (Cowan, Cranmer, Gross, Vitells 2011). `forecast.py` runs
  the whole procedure on toy data drawn from a Pythia 8 Z -> b bbar dimuon shape scaled to
  ALEPH's background (its job found the tagged-shape bias of amendment 0.13). `dimucomb.py`
  (v0.9) is test B: one signal strength fitted across the b-tagged and not-b-tagged spectra,
  each with its own background. `combcast.py` forecasts test B against test A. `bkgsys.py`
  (v0.12) gives per-degree profile curves, the spurious-signal test and the discrete-profiling
  envelope (arXiv:1408.6865); `envcast.py` scores five background treatments on combcast's
  pseudo-data; `bbspur.py` (v0.13) scores the same treatments on the Pythia Z -> b bbar shape.
  Tests: `python -m unittest -v test_dimustat test_dimucomb test_bkgsys test_bbspur`; run:
  `python forecast.py --out OUT` (needs `numpy`, `scipy`, `pythia8mc`),
  `python combcast.py --out OUT`, `python envcast.py --out OUT` (need `numpy`, `scipy`),
  `python bbspur.py --out OUT` (needs `numpy`, `scipy`, `pythia8mc`).
- [delsim/](delsim/) (plan v0.5; sigana 0.2.0 in v0.10, 0.3.0 in v0.11): the signal through
  DELPHI's own detector simulation. `run_delsim.sh` (DELPHI container) generates 30.4 GeV
  vector-boson signal events with `xkin/`, finds a working route to DELPHI's condition database,
  simulates and reconstructs the events for the 1994 detector with `runsim -gext`, and runs the
  ntuple routine on them (`mv2user02s.car`, which keeps every simulated event). `sigana.py`
  reports DELPHI's dimuon mass resolution at 30 GeV, muon-tag and selection efficiencies, and
  the b-tag response to signal. Tests: `python -m unittest -v test_sigana` (needs `numpy`;
  `fadgen.py` from `xkin/`; `dimusel.py` and `btagcal.py` from `analysis/`).
- [analysis/](analysis/) (plan v0.6-v0.8, v0.11): `dimusel.py` turns the ntuples into the mass
  spectra the fit uses: hadronic and b-tag selection, muon and electron identification, the
  cascade veto, an isolated-lepton selection with anti-kt jets, and the signal and control
  categories, in the 50 MeV binning of `stats/`. **The blinding is enforced in the code**: in
  real data no opposite-sign same-flavour pair in 26-35 GeV is ever histogrammed or counted,
  and the window only opens when the program is handed a plan file marked v1.x.
  `--combine` sums the production slices of one data-taking period; `--merge-periods` (0.3.0)
  sums 1992-95. `btagcal.py` measures DELPHI's b-tag efficiency in data with the hemisphere
  double-tag method of the LEP R_b measurements. `nexp.py` (v0.11) computes the expected
  ALEPH-sized signal under both readings of ALEPH's hadronic count. `lep4f.py` turns the
  published LEP1 mu mu q qbar counts into the efficiency bound of NOTE-fourfermion.md (CLs
  Poisson limits). `eff4f.py` (0.2.0) codes the published ALEPH, OPAL and L3 mu mu q qbar
  selections at hadron level; `run_eff4f.py` runs it on Pythia 8 events of the three xkin boson
  models. `efhz.py` (0.1.0) codes ALEPH's LEP1 H l+ l- selection; `lephz.py` (0.1.0) adds the
  L3 1996, DELPHI 1994 and OPAL 1997 H Z*(mu mu) selections, decides which published candidates
  can be signal, and combines the four searches; `run_efhz.py` and `run_lephz.py` run them the
  same way (needs `numpy`, `pythia8mc`, and `xme.py`, `evana.py`, `fadgen.py`, `run_xkin.py` from
  `xkin/` alongside). `iso4f.py` counts isolated opposite-sign muon pairs, with and without the
  b-tag, in simulation only. Pure Python, no dependencies except where stated.
  Tests: `python -m unittest -v test_dimusel test_btagcal test_nexp test_lep4f test_iso4f
  test_eff4f test_efhz test_lephz`; run:
  `python dimusel.py --dir NTUPLES --period y94 --out spectra.json [--config cuts.json]`,
  `python btagcal.py --dir NTUPLES --period y94 --out btagcal.json`,
  `python nexp.py --inputs nexp_inputs.json --out nexp.json`, `python lep4f.py`,
  `python run_eff4f.py --out OUT`, `python run_efhz.py --out OUT`, `python run_lephz.py --out OUT`,
  `python iso4f.py --dir SIM_NTUPLES --out iso4f.json`.
- [reviews/](reviews/): hand reviews of the code, with what was found and fixed.

## Status

Plan v0.11 plus amendments 0.12 and 0.13, 2026-11-18. No DELPHI dimuon mass from real data has
been looked at yet. Returned and graded: the kinematic study (xkin-v1, E1-E3 all passed), the
analysis-code tests (dimusel, btagcal, sigana, nexp: all pass), the test-B forecast (combcast-v1:
background flaw found, amendment 0.12), the exact four-fermion limits (lep4f-v1: 11 of 11 tests,
table as by hand) and the test-A forecast (dimu-forecast-v2: timed out in its toys; its Asimov
part found the tagged-shape bias of amendment 0.13). Still queued: the DELPHI probe, ntuple,
validation and detector-simulation jobs, the four-fermion simulation (fourf), the efficiency jobs
(lep4f-eff-v2, efhz-v1, lephz-v1) and the background-treatment jobs (envcast-v1, bbspur-v1).
Each will be graded against the expectations written before it ran. Results, positive, negative
or inconclusive, will all be published here.

## Data and licences

DELPHI open data are CC0 (cite doi:10.7483/OPENDATA.DELPHI.0X8O.FBUH and each dataset's DOI).
Code in this repository is Apache-2.0; text and result tables are CC BY 4.0. Pythia 8
(`pythia8mc`) is GPL-2.0-or-later and is installed separately, not bundled here. The meanings
of the skelana common-block words were read from the public SKELANA decks and the
delphi-nanoaod headers (GPL-3.0); no code from those projects is copied here. The DELSIM
run steps follow the public documentation of the delphi-sim-pipeline project and the CERN Open
Data simulation guide; no code from that project is copied here. The published LEP1
four-fermion and Higgs-search numbers are quoted from the cited papers.
