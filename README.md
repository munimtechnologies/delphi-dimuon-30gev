# delphi-dimuon-30gev

An open, pre-registered test of whether the **30 GeV dimuon excess** seen in archived ALEPH
data (Z -> b bbar events at LEP, arXiv:1610.06536) also appears in **DELPHI's open data** from
the same Z-pole running. DELPHI released its full data and software in 2024. As far as we can
find, no DELPHI or OPAL test of this excess has been published.

By MV2 of Munim, Inc. (mv2@munimtech.com). The work is made with AI agents working in MV2's
name. It is not a DELPHI Collaboration result, and neither DELPHI nor CERN endorses it.

- [PLAN.md](PLAN.md): the question, sensitivity estimate, data, analysis outline and the
  **blinding commitments** (the 26-35 GeV opposite-sign dimuon window in b-tagged events stays
  closed until the selection and tests are frozen and published here).
- [probe/](probe/): a feasibility probe that runs in the public DELPHI container
  (`gitlab-registry.cern.ch/delphi/deployment/delphi/al9_64_xrd`). It checks xrootd access to
  the 1994 short DSTs, builds the stock skelana example, and extracts the manuals as text.
- [xkin/](xkin/): signal generator and kinematic study (PLAN section 4b). Exact tree-level
  e+e- -> Z -> b bbar X (X -> mu mu) for a vector or scalar X radiated off the b line, and
  Z -> h A; Pythia 8 hadronisation; ALEPH-style muon-jet angles, cos theta*, muon multiplicity;
  and a writer for DELSIM's external-generator input (FADGEN). Run the tests with
  `python -m unittest -v test_xkin`; run the study with
  `python run_xkin.py --out OUT --nsig 20000 --nbkg 600000` (needs `numpy`, `pythia8mc`).
- [ntuple/](ntuple/) (plan v0.3): the DELPHI ntuple writer. `mv2user02.car` is a skelana
  USER02 routine that writes one line per event (hadronic flags, energies, the DELPHI lifetime
  b-tag probabilities, thrust) and, for events with two or more charged lepton candidates, every
  particle with its muon tag (MUCAL2), electron tag (ELECID), vertex-detector hits and impact
  parameters. It writes **no masses**. `run_ntuple.sh` builds it inside the DELPHI container
  from the stock `dump` example and runs it on 1994 data and Z -> q qbar simulation read over
  xrootd. `validate.py` makes the detector checks (Z -> mu mu, J/psi -> mu mu, tag rates,
  b-tag and impact-parameter distributions, data vs simulation) and never stores, prints or
  histograms a data dimuon mass above 5 GeV in hadronic events. Tests:
  `python -m unittest -v test_validate`.
- [stats/](stats/) (new in plan v0.4): the pre-registered statistics and a sensitivity
  forecast. `dimustat.py` is the fit that will be used on the unblinded data: 50 MeV bins in
  15-50 GeV, Voigt signal (m = 30.40, Gamma = 1.78 GeV), a log-Legendre background whose degree
  is chosen on the sidebands by a fixed rule, the discovery statistic q0, and asymptotic CLs
  upper limits (Cowan, Cranmer, Gross, Vitells 2011). `forecast.py` runs the whole procedure on
  toy data drawn from a Pythia 8 Z -> b bbar dimuon shape scaled to ALEPH's background, for
  several DELPHI scenarios. It reports how often DELPHI would exclude an ALEPH-sized signal,
  how often it would confirm one, the bias of each background form, and the look-elsewhere
  effect of the 15-50 GeV mass scan. Tests: `python -m unittest -v test_dimustat`; run:
  `python forecast.py --out OUT` (needs `numpy`, `scipy`, `pythia8mc`).

## Status

Plan v0.4, 2026-11-17. No DELPHI dimuon mass has been looked at yet. Results, positive,
negative or inconclusive, will all be published here.

## Data and licences

DELPHI open data are CC0 (cite doi:10.7483/OPENDATA.DELPHI.0X8O.FBUH and each dataset's DOI).
Code in this repository is Apache-2.0; text and result tables are CC BY 4.0. Pythia 8
(`pythia8mc`) is GPL-2.0-or-later and is installed separately, not bundled here. The meanings
of the skelana common-block words were read from the public SKELANA decks and the
delphi-nanoaod headers (GPL-3.0); no code from those projects is copied here.
