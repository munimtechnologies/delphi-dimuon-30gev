# delphi-dimuon-30gev

An open, pre-registered test of whether the **30 GeV dimuon excess** seen in archived ALEPH
data (Z -> b bbar events at LEP, arXiv:1610.06536) also appears in **DELPHI's open data** from
the same Z-pole running, and of what the excess can be. DELPHI released its full data and
software in 2024. As far as we can find, no DELPHI or OPAL test of this excess has been published.

By MV2 of Munim, Inc. (mv2@munimtech.com). The work is made with AI agents working in MV2's
name. It is not a DELPHI, ALEPH, L3 or OPAL Collaboration result, and neither these
collaborations nor CERN endorse it. **No physicist has checked these results yet.**

**Main result so far (2026-11-19): the excess is not a boson decaying to isolated muons. Every
model we tested is excluded by at least two LEP detectors.**
Draft paper: [paper/DRAFT-lep1-4f-30gev.md](paper/DRAFT-lep1-4f-30gev.md) (draft 0.8, not peer
reviewed). If the excess were a boson produced with b quarks (a vector or scalar radiated off the
b, or Z -> h A), its two muons would be isolated from the jets in 92-95 % of events. Two families
of LEP1 measurements selected exactly that signature, and both rule the boson out:

1. **Four-fermion measurements** ([NOTE-fourfermion.md](NOTE-fourfermion.md), version 0.4).
   ALEPH, L3 and OPAL measured e+e- -> mu+ mu- q qbar at the Z pole in 1994-96. OPAL's published
   selection keeps **84-88 %** of the boson's events and L3's 59-68 % (job `lep4f-eff-v2`; all
   seven expectations H1-H7 written beforehand passed). An ALEPH-sized boson would have put
   **about 150 events** into OPAL's and L3's published dimuon-mass plots between 20 and 40 GeV,
   where they show **one**. At the lowest rate quoted for the excess and with the least
   favourable reading of every selection detail: p < 5 x 10^-12.
2. **Higgs searches** ([NOTE-higgs-searches.md](NOTE-higgs-searches.md), version 0.8).
   All four LEP experiments searched their Z-peak data for e+e- -> H Z*, Z* -> mu+ mu-: two
   muons recoiling against hadrons. Jobs `efhz-v1` and `lephz-v1` measured how much of each boson
   model the four selections keep. ALEPH's own search has a recoil-mass cut that removes most
   scalar and Z -> h A events (0.26 and 0.02 kept), so on its own it cannot exclude the scalar at
   the lowest rate. **L3's search, which has no recoil cut (read twice, independently) and found
   no candidate in 3.05 million hadronic Z decays, keeps 0.54-0.64, and DELPHI's 0.69-0.82.** L3
   and DELPHI alone predict 25-30 boson events against one candidate at the lowest literature rate
   (p = 2e-12 to 3e-10); DELPHI alone excludes every model at 99 %. All ten expectations L1-L10
   written beforehand passed. With the weakest selection variants, scaled down to the
   experiments' own published Higgs efficiencies, the most pessimistic combination we can build
   still has p = 1.5e-6 (scalar, 4.7 standard deviations).
3. **The models built to escape the LHC (jobs `kly-v1` and `kly4f-v1`; all fourteen
   expectations K1-K9 and F1-F5 passed).** Ko, Li and Yu (arXiv:1610.07526) proposed two models
   that avoid the LHC Drell-Yan bound: a Z' coupling the b quark to a heavy vector-like B quark
   (model II), and Z -> Z' phi (model III). At model II's own benchmark rate, L3's and DELPHI's
   Higgs searches predict **21-28 events against one candidate (p = 2e-11 to 2e-8)**, and OPAL's
   and L3's four-fermion selections, applied to the same events, **38-41 events against one
   (p = 6e-17 to 1e-15)**. Model III with a light 12 GeV scalar escapes the DELPHI, ALEPH and OPAL
   Higgs searches (their recoil-mass cuts), but not L3's Higgs search (3.8-4.4 standard deviations
   in the most pessimistic readings) nor OPAL's four-fermion selection (OPAL alone, weakest
   variant scaled down by the worst calibration ratio: p = 1.5e-7). The OPAL result depended on
   whether OPAL counted the muons when it required two jets; we found that while grading and
   published it as a condition. **A reading of OPAL's paper made blind to this repository settled
   it on 2026-11-19: OPAL clustered all tracks and clusters, leptons included**
   ([readings/opal4f-jets-notes.md](readings/opal4f-jets-notes.md)), exactly as coded. A scan of
   the scalar mass from 15 to 55 GeV (`klyscan-v1`, expectations S1-S7 written first) is queued.
4. **Lane and Pritchett's model** ([NOTE-lane-pritchett.md](NOTE-lane-pritchett.md)) is produced
   at LEP1 only as Z -> h eta_A with both states at 30 GeV: the Z -> h A case already excluded.

**Prior work.** Ko, Li and Yu (2016) showed at parton level that their boson models put the muons
far from the b jets, unlike ALEPH's events (we confirm it at hadron level: 4-6 % within 15 deg),
and that a boson coupling directly to b bbar is excluded by LHC Drell-Yan data. What is new here
is the confrontation with the LEP1 measurements themselves.

Limits: hadron level, no detector simulation; the selections and mass plots were read from
scanned papers by AI reading agents. The two families overlap in data (L3's and OPAL's analyses),
so they are separate selections, not independent data sets.

**Earlier result (2026-11-17): [NOTE-kinematics.md](NOTE-kinematics.md).** The same three boson
models put a muon within 15 degrees of a leading jet in only 5-11 % of events, while ordinary
Z -> b bbar does so in 99.4 %. ALEPH reports this "in all cases". Taken at face value, ALEPH's own
kinematics allow at most about 4-10 of its 32 fitted events to be such a boson (95 % CL).

**What is left, and what DELPHI tests ([NOTE-injet.md](NOTE-injet.md), version 0.1, 2026-11-19).**
ALEPH reports that each muon of its excess sits close to one of the leading jets. Exact kinematics
show that two muons within 20 degrees of the *same* jet can have a mass of at most 16.6 GeV at
LEP1, so the two muons of a 30 GeV pair sit next to two different jets, and **no new state decaying
within one jet can make the excess**. ALEPH's background is its own electron-muon data, so ordinary
b-decay effects (cascades, fragmentation, a mismodelled semileptonic spectrum) cancel in the
excess unless they treat muons and electrons differently. What remains is a statistical
fluctuation (in the muon pairs or in the electron-muon template), a muon-specific detector effect,
or a muon-coupled state whose muons fall near two b jets by accident (already bounded above). L3's
2019 cross-check (arXiv:1905.01111) expected at most about 4 signal events against a 7.4-event
uncertainty, so it could not decide. Test A replicates ALEPH's analysis on DELPHI's b-tagged events;
NOTE-injet adds test A', the same fit against DELPHI's own electron-muon spectrum (ALEPH's frame),
for plan v1.0. Test B fits the b-tagged and not-b-tagged spectra together (a boson produced with b
quarks would put about 1.6 events in the not-tagged sample for every tagged one). Test C (to be
pre-registered in plan v1.0) uses isolated muon pairs without the b-tag, with the four-fermion
background from DELPHI's own EXCALIBUR simulation. DELPHI's open data exist only in DELPHI's own
formats (RAW, DSTO, LONG, SHORT, XSHORT; checked on the CERN Open Data portal 2026-11-19), so these
tests need the DELPHI software container.

**Two flaws caught before unblinding, and the fix chosen by a written rule.**
[PLAN-amendment-0.12.md](PLAN-amendment-0.12.md): in the not-b-tagged spectrum, the
pre-registered background rule can fake a *negative* signal (mu_hat = 0.51 for an injected
ALEPH-sized signal on noise-free pseudo-data), which would favour a false exclusion.
[PLAN-amendment-0.13.md](PLAN-amendment-0.13.md): in the b-tagged spectrum, the same rule keeps a
degree-2 background that fakes +0.52 of an ALEPH-sized signal on a realistic Pythia shape, which
would favour a false *confirmation*. [PLAN-amendment-0.14.md](PLAN-amendment-0.14.md): job
`dimu-envcast-v1` scored five background treatments on eight pseudo-data scenarios; only a
**fixed degree-3 background in every category** keeps the fake signal below 0.2 standard
deviations everywhere (the discrete-profiling envelope fails one scenario).
[PLAN-amendment-0.15.md](PLAN-amendment-0.15.md): job `dimu-bbspur-v1` confirmed the b-tagged
bias exactly (+0.52; expectations M1-M5 passed) and showed that more data do not rescue the old
rule (M6 failed). Degree 3 passes in all twelve scenarios.
[PLAN-amendment-0.16.md](PLAN-amendment-0.16.md): job `dimu-envtoys-v1` ran 62 pseudo-experiments
with a true ALEPH-sized boson and 30 without (too slow for the planned 200). Degree 3 is unbiased
(mean fitted signal 1.00 and 0.02) and falsely excluded a real boson in 2 of 62.
[PLAN-amendment-0.17.md](PLAN-amendment-0.17.md): the top-up `dimu-envtoys-v2` added 60 toys.
[PLAN-amendment-0.18.md](PLAN-amendment-0.18.md) (**settled, 2026-11-19**): with the third top-up
`dimu-envtoys-v3` (44 toys) the pool reaches the 150 toys the rule needs. Degree 3 falsely
excludes a real ALEPH-sized boson in **6 of 166** (b-tagged test, 3.6 %) and **4 of 166**
(combined test, 2.4 %) pseudo-experiments, below the pre-registered 7 % limit, and is unbiased
(mean fitted signal 0.98 and 1.02). Criterion (b) passes (N7, N9, N10 all passed), so the fixed
degree-3 background is the background treatment of plan v1.0. Stated plainly: for the b-tagged
test the upper end of the exact 95 % interval (0.075-0.080) is still just above 7 %. **A
sensitivity limit reported before unblinding:** with no boson present, DELPHI's combined test
excludes an ALEPH-sized one in only about 43 % of pseudo-experiments, so an INCONCLUSIVE result is
the most likely outcome if the excess is not real.

**What "ALEPH-sized" means (plan v0.11, section 5f).** The expected signal is one written
formula in produced Z decays (`analysis/nexp.py`). ALEPH's paper leaves its hadronic event count
open (about 1.9M selected where about 2.2M were expected), so every result is computed under both
readings, and EXCLUDED or COMPATIBLE is claimed only if both agree.

## Contents

- [PLAN.md](PLAN.md): the question, sensitivity estimate, data, analysis outline and the
  **blinding commitments** (the 26-35 GeV opposite-sign dimuon window stays closed until the
  selection and tests are frozen and published here as plan v1.0). Amendments
  [0.12](PLAN-amendment-0.12.md), [0.13](PLAN-amendment-0.13.md),
  [0.14](PLAN-amendment-0.14.md), [0.15](PLAN-amendment-0.15.md),
  [0.16](PLAN-amendment-0.16.md), [0.17](PLAN-amendment-0.17.md) and
  [0.18](PLAN-amendment-0.18.md).
- [paper/](paper/): the draft paper on the LEP1 isolated-muon result (not peer reviewed).
- [NOTE-kinematics.md](NOTE-kinematics.md), [NOTE-fourfermion.md](NOTE-fourfermion.md),
  [NOTE-higgs-searches.md](NOTE-higgs-searches.md), [NOTE-lane-pritchett.md](NOTE-lane-pritchett.md):
  the external tests, each with its pre-registered expectations, grades and limits.
  [NOTE-injet.md](NOTE-injet.md): the single-jet mass bound, ALEPH's electron-muon background
  frame, L3's sensitivity, and the pre-registered test A' and figure-reading grades R1-R2.
- [readings/](readings/): notes from the published LEP1 papers, made by AI agents reading the
  scanned papers (including [opal4f-jets-notes.md](readings/opal4f-jets-notes.md), OPAL's
  four-fermion jet definition, read blind to this repository).
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
  scoring), `envpool.py` (pools the toy batches and grades criterion (b); pure Python).
  [stats/results/bbspur/](stats/results/bbspur/) holds the output of `dimu-bbspur-v1`.
  Tests: `python -m unittest -v test_dimustat test_dimucomb test_bkgsys test_envtoys test_bbspur
  test_envpool` (needs `numpy`, `scipy`; `pythia8mc` for forecast and bbspur).
- [delsim/](delsim/): the signal through DELPHI's own detector simulation (`run_delsim.sh`,
  `runsim -gext`, `sigana.py` for resolution and efficiencies). Tests:
  `python -m unittest -v test_sigana`.
- [analysis/](analysis/): `dimusel.py` (spectra; **blinding enforced in the code**: in real data
  no opposite-sign same-flavour pair in 26-35 GeV is histogrammed until a plan file marked v1.x is
  given), `btagcal.py` (b-tag efficiency by hemisphere double tag), `nexp.py` (expected signal),
  `lep4f.py` (limits from the published four-fermion counts), `eff4f.py` 0.2.0 and
  `run_eff4f.py` (the published four-fermion selections on the boson models), `efhz.py` and
  `lephz.py` (the LEP1 Higgs-search selections), `kly.py` and `run_kly.py` (Ko, Li and Yu's
  models II and III through the same selections), `run_kly4f.py` (the same events through the
  four-fermion selections), `run_kly4fj.py` (OPAL's two-jet requirement without the muons, now a
  sensitivity check), `run_klyscan.py` (model III at seven more scalar masses),
  `iso4f.py` (isolated pairs in simulation), `injet.py` (NOTE-injet's bounds; pure Python).
  [analysis/results/](analysis/results/) holds the output of `lep4f-eff-v2`, of
  `dimu-envcast-v1` (`envcast/`), `dimu-envtoys-v1` (`envtoys/`), `dimu-envtoys-v2`
  (`envtoys-v2/`), `dimu-envtoys-v3` (`envtoys-v3/`), the pooled grade (`envtoys-pool/`),
  `efhz-v1` (`efhz/`), `lephz-v1` (`lephz/`), `kly-v1` (`kly/`), `kly4f-v1` (`kly4f/`) and
  NOTE-injet (`injet/`). Tests:
  `python -m unittest -v test_dimusel test_btagcal test_nexp test_lep4f test_iso4f test_eff4f
  test_efhz test_lephz test_kly test_kly4f test_kly4fj test_klyscan test_injet`. Runs: `python run_eff4f.py --out OUT --nsig 10000 --workers 2`,
  `python run_efhz.py --out OUT --nsig 10000 --workers 2`,
  `python run_lephz.py --out OUT --nsig 8000 --workers 2`,
  `python run_kly.py --out OUT --nsig 8000 --workers 2`,
  `python run_kly4f.py --out OUT --nsig 8000 --workers 2`,
  `python run_kly4fj.py --out OUT --nsig 8000 --workers 2`,
  `python run_klyscan.py --out OUT --nsig 8000 --workers 2` (need `numpy`, `pythia8mc` and the
  `xkin/` modules alongside).
- [reviews/](reviews/): hand reviews of the code, with what was found and fixed.

## Status

Plan v0.11 plus amendments 0.12-0.18, 2026-11-19, and NOTE-injet 0.1. No DELPHI dimuon mass from
real data has been looked at yet. Returned and graded: the kinematic study (xkin-v1, E1-E3 passed),
the analysis-code tests (dimusel, btagcal, sigana, nexp), the test-B forecast (combcast-v1:
background flaw found, amendment 0.12), the four-fermion limits (lep4f-v1: 11/11 tests), the
four-fermion efficiencies (**lep4f-eff-v2: H1-H7 passed**), the test-A forecast (dimu-forecast-v2:
its Asimov part found the bias of amendment 0.13), the background-treatment scoring
(dimu-envcast-v1, amendment 0.14; and **dimu-bbspur-v1: M1-M5 passed, M6 failed**, amendment
0.15), ALEPH's Higgs-search efficiency (**efhz-v1: J1, J3, J4, J5 passed; J2, J6, J7 failed for the
scalar model**), the four LEP1 Higgs searches (**lephz-v1: L1-L10 all passed**), Ko, Li and Yu's
models (**kly-v1: K1-K9 all passed; kly4f-v1: F1-F5 all passed; F5's condition on OPAL's jet
definition met, from a blind reading of OPAL's paper**) and the toys (**dimu-envtoys-v1: N0, N4, N5
passed; N2, N3 failed as written**, amendment 0.16; **dimu-envtoys-v2: N6, N8 passed**, amendment
0.17; **dimu-envtoys-v3 and the pool: N7 (criterion (b)), N9, N10 passed**, amendment 0.18). Still
queued: the DELPHI probe, ntuple, validation and detector-simulation jobs, the four-fermion
simulation (fourf), kly4fj-v1 and klyscan-v1, and the blind reading of ALEPH's figures for
NOTE-injet's R1-R2. Each will be graded against the expectations written before it ran. Results,
positive, negative or inconclusive, will all be published here.
