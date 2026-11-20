# delphi-dimuon-30gev

An open, pre-registered test of whether the **30 GeV dimuon excess** seen in archived ALEPH
data (Z -> b bbar events at LEP, arXiv:1610.06536) also appears in **DELPHI's open data** from
the same Z-pole running, and of what the excess can be. DELPHI released its full data and
software in 2024. As far as we can find, no DELPHI or OPAL test of this excess has been published.

By MV2 of Munim, Inc. (mv2@munimtech.com). The work is made with AI agents working in MV2's
name. It is not a DELPHI, ALEPH, L3 or OPAL Collaboration result, and neither these
collaborations nor CERN endorse it. **No physicist has checked these results yet.**

**Newest step (2026-11-20): where does the rising muon/electron ratio come from?** Amendment
[0.25](PLAN-amendment-0.25.md) asked whether the rise is in ALEPH's own simulation, in its
di-electrons too, or in neither. The code's closure check passed (C0: it reproduces 2.664, 1.621,
0.0266 and 2.256; the data slope is 0.027 +- 0.012 per GeV; output in
[analysis/results/apcross-closure/](analysis/results/apcross-closure/)), and two blind readings of
ALEPH's figures came in: its simulation (Fig. 4, `data/aleph-mc4.json`) and its di-electrons
(Fig. 25, 243 pairs, `data/aleph-ee25.json`). Four empty simulation bins at 46-49 GeV make the
pre-registered gate M0 **fail as written**; [amendment 0.26](PLAN-amendment-0.26.md) fixes, before
any fit, how such bins are filled (secondary grades M1z-M3z, with a sensitivity fill;
[stats/apcross_m0z.py](stats/apcross_m0z.py)). Plain sums on the readings, not a test: above 25
GeV the ratio rises from 1.08 to 1.69 in the muon data, but only from 1.06 to 1.09 in ALEPH's
simulation and from 0.80 to 0.84 in its di-electrons. Job `apcross-v1` grades it. Section 8 of
the amendment pre-registers the next question, before its readings exist: do ALEPH's
**same-sign** muon pairs rise against simulation too (a muon-identification or fake-muon effect,
test S1), or only the opposite-sign ones (S2)?

**Result (2026-11-20): ALEPH's excess leans on a constant muon/electron pair ratio, and
its own data say the ratio rises with mass** ([NOTE-aprime.md](NOTE-aprime.md) 0.3, section 8;
pre-registered in [amendment 0.23](PLAN-amendment-0.23.md)). ALEPH's background is its electron-muon
pairs scaled by one factor for all masses. Job `aprime-ext-v1` refitted the blind reading of
ALEPH's Fig. 5 with a ratio that may change log-linearly with mass. The muon pairs rise against the
template (slope 0.027 per GeV, 2.3 sigma at zero signal; pre-registered X2, "below 2 sigma":
**failed**), and with that slope free the excess falls from **2.66 to 1.62 sigma** in 15-50 GeV
(X1 passed) and to 1.35 sigma in 5-50 GeV (X3 passed). Seen after the output, and not a test: in
15-50 GeV a broad rise and a narrow peak are almost interchangeable (with the peak floated the
slope adds only 0.8 sigma), and outside the peak window above 25 GeV the muon pairs exceed the
template by about 1.5 on both sides (72 against 46.8).

**Also new (2026-11-20): the Z -> Z' phi escape model is closed at every scalar mass from
12 to 55 GeV** ([NOTE-higgs-searches.md](NOTE-higgs-searches.md) 0.10, section 6d). Ko, Li and
Yu's model III had been computed at three scalar masses. Job `klyscan-v2` added seven more (15,
20, 25, 35, 40, 45 and 55 GeV) through both the four LEP1 Higgs-search selections and the three
four-fermion selections. All seven expectations S1-S7, written before the job ran, passed. At
every mass, L3's Higgs search alone and OPAL's four-fermion measurement alone each exclude the
model at p < 1e-3 in the most pessimistic reading (weakest selection variant, scaled down to the
worst calibration ratio, lowest rate in the literature); the weakest point is 55 GeV, near the
kinematic end (p = 2.2e-4 and 3.9e-4). Raw output: [analysis/results/klyscan/](analysis/results/klyscan/).

**How significant is ALEPH's excess when its background template's own counting error is
included? (2026-11-19/20)** ([NOTE-aprime.md](NOTE-aprime.md) sections 1-7,
pre-registered in [amendment 0.19](PLAN-amendment-0.19.md)). ALEPH built its background from the
same events' electron-muon pairs and treated that template as exact. Refitting a blind per-bin
reading of ALEPH's Fig. 5 with the template's Poisson error kept bin by bin (Barlow-Beeston) gives
**Z0 = 2.66** (pre-registered headline P3, "at least 3.0": **failed**); 10,000 background-only
pseudo-experiments confirm that this method is calibrated (toy-calibrated 2.60). Treating the
binned, unsmoothed template as exact gives 4.18, but that method produced false 3-sigma excesses in
4.7 % of the pseudo-experiments, 35 times the nominal rate. **The calibration toys graded on
2026-11-20 (C1, C2, C4 passed) add a caveat:** a template smoothed with a 1 GeV kernel, as ALEPH
smoothed its own, inflates false excesses far less (2-sigma rate 3.8-4.4 % against 2.3 %), and the
bin-by-bin method ignores the background's smoothness, so in that respect **2.66 is conservative**.
[Amendment 0.24](PLAN-amendment-0.24.md) pre-registers the deciding test: a smooth background
fitted jointly to both spectra, so that its counting error is kept and its smoothness used, with
every method calibrated on 10,000 toys at the figure's scale (job `aprime-smooth-v1`, queued; our
own expectation, written first, is 3-4 sigma). It assumes a constant ratio; the result above
pulls the other way. Limits: a figure reading, not ALEPH's unbinned fit; no look-elsewhere
correction.

**Main result so far: the excess is not a boson decaying to isolated muons. Every
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
2. **Higgs searches** ([NOTE-higgs-searches.md](NOTE-higgs-searches.md)).
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
3. **The models built to escape the LHC (jobs `kly-v1`, `kly4f-v1` and `klyscan-v2`; all
   twenty-one expectations K1-K9, F1-F5 and S1-S7 passed).** Ko, Li and Yu (arXiv:1610.07526)
   proposed two models that avoid the LHC Drell-Yan bound: a Z' coupling the b quark to a heavy
   vector-like B quark (model II), and Z -> Z' phi (model III). At model II's own benchmark rate,
   L3's and DELPHI's Higgs searches predict **21-28 events against one candidate (p = 2e-11 to
   2e-8)**, and OPAL's and L3's four-fermion selections, applied to the same events, **38-41 events
   against one (p = 6e-17 to 1e-15)**. Model III with a light 12 GeV scalar escapes the DELPHI,
   ALEPH and OPAL Higgs searches (their recoil-mass cuts), but not L3's Higgs search (3.8-4.4
   standard deviations in the most pessimistic readings) nor OPAL's four-fermion selection (OPAL
   alone, weakest variant scaled down by the worst calibration ratio: p = 1.5e-7). The OPAL result
   depended on whether OPAL counted the muons when it required two jets; we found that while
   grading and published it as a condition. **A reading of OPAL's paper made blind to this
   repository settled it on 2026-11-19: OPAL clustered all tracks and clusters, leptons included**
   ([readings/opal4f-jets-notes.md](readings/opal4f-jets-notes.md)), exactly as coded. The
   sensitivity check `kly4fj-v1` measured what hung on that sentence: had OPAL removed the muons
   first, it would keep only 0.8 % of the 12 GeV scalar's events (that case would then rest on L3
   alone), while every other model stays excluded. **The mass scan `klyscan-v2` (2026-11-20)
   closes model III at every computed scalar mass from 12 to 55 GeV by two detectors, each alone.**
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

**What is left, and what DELPHI tests ([NOTE-injet.md](NOTE-injet.md), version 0.2, 2026-11-19).**
ALEPH reports that each muon of its excess sits close to one of the leading jets. Exact kinematics
show that two muons within 20 degrees of the *same* jet can have a mass of at most 16.6 GeV at
LEP1, so the two muons of a 30 GeV pair sit next to two different jets, and **no new state decaying
within one jet can make the excess**. ALEPH's background is its own electron-muon data, so ordinary
b-decay effects (cascades, fragmentation, a mismodelled semileptonic spectrum) cancel in the
excess unless they treat muons and electrons differently. **A blind reading of ALEPH's own figures
(NOTE-injet sec. 7)** finds the excess in the muon-pair data itself: +15.8 events against ALEPH's
simulation and +17.8 against its electron-muon background in 29-32 GeV, while the electron-muon
control agrees with simulation there (+1.5). Pre-registered grade R2 passed; R1 (at least 16
events) failed as written by 0.2 events, inside the reading uncertainty, so test A' is now the
primary DELPHI test. What remains is a statistical fluctuation of the muon pairs (or of the
template), a muon-specific detector effect, or a muon-coupled state whose muons fall near two b
jets by accident (already bounded above). L3's 2019 cross-check (arXiv:1905.01111) expected at most
about 4 signal events against a 7.4-event uncertainty, so it could not decide.

**ALEPH's fit table and its figures (amendments 0.20-0.23).** ALEPH's fit table gives 32.3 signal
and 1,457 background events "overall"; the figures hold 362 muon pairs in the 15-50 GeV fit range
and 783 in 5-50 GeV. Two blind readings found no sentence or count that explains the factor, so it
is reported as unexplained ([amendment 0.23](PLAN-amendment-0.23.md) sec. 1). Our A'-ALEPH test
uses the figures' scale, which reproduces ALEPH's own on/off significance (2.48 against 2.63).

**Test A' for DELPHI ([PLAN-amendment-0.19.md](PLAN-amendment-0.19.md)).** Test A' fits DELPHI's
b-tagged muon pairs against DELPHI's own electron-muon spectrum (ALEPH's frame), keeping the
template's own counting error bin by bin ([stats/emuframe.py](stats/emuframe.py), Barlow-Beeston,
pure Python). Test A replicates ALEPH's analysis on DELPHI's b-tagged events with a fitted smooth
background and is reported beside A'. Test B fits the b-tagged and not-b-tagged spectra together
(a boson produced with b quarks would put about 1.6 events in the not-tagged sample for every
tagged one). Test C (to be pre-registered in plan v1.0) uses isolated muon pairs without the b-tag,
with the four-fermion background from DELPHI's own EXCALIBUR simulation. DELPHI's open data exist
only in DELPHI's own formats (RAW, DSTO, LONG, SHORT, XSHORT; checked on the CERN Open Data portal
2026-11-19), so these tests need the DELPHI software container. Section 8 of NOTE-aprime adds a
requirement for A': DELPHI's own muon/electron ratio must be checked for a mass dependence.

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
  [0.16](PLAN-amendment-0.16.md), [0.17](PLAN-amendment-0.17.md),
  [0.18](PLAN-amendment-0.18.md), [0.19](PLAN-amendment-0.19.md) (test A'),
  [0.20](PLAN-amendment-0.20.md) (A'-ALEPH reading check and toys), [0.21](PLAN-amendment-0.21.md)
  and [0.22](PLAN-amendment-0.22.md) (the fit table's scale), [0.23](PLAN-amendment-0.23.md)
  (ALEPHLOW2 applied; mass-dependent ratio pre-registered), [0.24](PLAN-amendment-0.24.md)
  (smooth background with its counting error, tests K0-K4), [0.25](PLAN-amendment-0.25.md)
  (the rising ratio in ALEPH's simulation and di-electrons, tests C0, M0-M3, E0-E3) and
  [0.26](PLAN-amendment-0.26.md) (C0 passed; M0 failed as written; empty-bin rule, M1z-M3z).
- [paper/](paper/): the draft paper on the LEP1 isolated-muon result (not peer reviewed).
- [NOTE-kinematics.md](NOTE-kinematics.md), [NOTE-fourfermion.md](NOTE-fourfermion.md),
  [NOTE-higgs-searches.md](NOTE-higgs-searches.md) (0.10), [NOTE-lane-pritchett.md](NOTE-lane-pritchett.md):
  the external tests, each with its pre-registered expectations, grades and limits.
  [NOTE-injet.md](NOTE-injet.md): the single-jet mass bound, ALEPH's electron-muon background
  frame, L3's sensitivity, the pre-registered test A', and the graded figure reading (R1, R2).
  [NOTE-aprime.md](NOTE-aprime.md) 0.3: A'-ALEPH graded (P1-P4) with its 10,000 toys, the
  calibration toys on made-up spectra graded (C1-C5), and the mass-dependent ratio graded (X0-X3).
- [data/](data/): blind readings of ALEPH's figures, committed exactly as read
  (`aleph-fig5.json`, 15-50 GeV; `aleph-fitfig.json`, the fit figure; `aleph-low2.json`, 5-15 GeV;
  `aleph-mc4.json`, the simulation-only comparison; `aleph-ee25.json`, the di-electrons).
- [readings/](readings/): notes from the published LEP1 papers, made by AI agents reading the
  scanned papers (including [opal4f-jets-notes.md](readings/opal4f-jets-notes.md), OPAL's
  four-fermion jet definition, and [aleph-figs-notes.md](readings/aleph-figs-notes.md), three of
  ALEPH's 2016 figures; both read blind to this repository).
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
  scoring), `envpool.py` (pools the toy batches and grades criterion (b); pure Python),
  `emuframe.py` (test A' and the A'-ALEPH re-evaluation: mu mu against the e mu template with
  Barlow-Beeston per-bin errors, q0, asymptotic CLs, Z_Bi; pure Python), `aprime_toys.py` (its
  background-only calibration toys on made-up spectra), `run_aprime_aleph.py` (A'-ALEPH and its
  toys at the reading's scale), `aprime_ext.py` (A'-ALEPH with a mass-dependent mu mu / e mu ratio,
  amendment 0.23), `aprime_smooth.py` (A'-ALEPH with smoothed templates and a joint smooth fit,
  toy-calibrated, amendment 0.24), `aprime_cross.py` (the ratio's slope in ALEPH's simulation and
  di-electrons, amendment 0.25; pure Python), `apcross_m0z.py` (amendment 0.26: runs
  aprime_cross unchanged and adds the empty-bin fills and the slope with the signal floated) and
  `fit_table_check.py`.
  [stats/results/bbspur/](stats/results/bbspur/) holds the output of `dimu-bbspur-v1`.
  Tests: `python -m unittest -v test_dimustat test_dimucomb test_bkgsys test_envtoys test_bbspur
  test_envpool test_emuframe test_aprime_ext test_aprime_smooth test_aprime_cross test_apcross_m0z
  test_fit_table_check` (needs `numpy`, `scipy`; `pythia8mc` for forecast and bbspur;
  `test_emuframe`, `test_aprime_ext`, `test_aprime_cross` and `test_apcross_m0z` need nothing).
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
  sensitivity check), `run_klyscan.py` 0.1.1 (model III at seven more scalar masses),
  `iso4f.py` (isolated pairs in simulation), `injet.py` (NOTE-injet's bounds; pure Python).
  [analysis/results/](analysis/results/) holds the output of `lep4f-eff-v2`, of
  `dimu-envcast-v1` (`envcast/`), `dimu-envtoys-v1` (`envtoys/`), `dimu-envtoys-v2`
  (`envtoys-v2/`), `dimu-envtoys-v3` (`envtoys-v3/`), the pooled grade (`envtoys-pool/`),
  `efhz-v1` (`efhz/`), `lephz-v1` (`lephz/`), `kly-v1` (`kly/`), `kly4f-v1` (`kly4f/`),
  `kly4fj-v1` (`kly4fj/`), `klyscan-v2` (`klyscan/`), NOTE-injet (`injet/`), `aprime-aleph-v1`
  (`aprime-aleph/`), `aprime-toys-v1` (`aprime-toys/`), `aprime-ext-v1` (`aprime-ext/`) and
  `apcross-closure-v1` (`apcross-closure/`). Tests:
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

Plan v0.11 plus amendments 0.12-0.26, 2026-11-20, NOTE-injet 0.2, NOTE-aprime 0.3 and
NOTE-higgs-searches 0.10. No DELPHI dimuon mass from real data has been looked at yet. Returned and
graded: the kinematic study (xkin-v1, E1-E3 passed), the analysis-code tests (dimusel, btagcal,
sigana, nexp), the test-B forecast (combcast-v1: background flaw found, amendment 0.12), the
four-fermion limits (lep4f-v1: 11/11 tests), the four-fermion efficiencies (**lep4f-eff-v2: H1-H7
passed**), the test-A forecast (dimu-forecast-v2: its Asimov part found the bias of amendment
0.13), the background-treatment scoring (dimu-envcast-v1, amendment 0.14; and **dimu-bbspur-v1:
M1-M5 passed, M6 failed**, amendment 0.15), ALEPH's Higgs-search efficiency (**efhz-v1: J1, J3,
J4, J5 passed; J2, J6, J7 failed for the scalar model**), the four LEP1 Higgs searches (**lephz-v1:
L1-L10 all passed**), Ko, Li and Yu's models (**kly-v1: K1-K9 all passed; kly4f-v1: F1-F5 all
passed; kly4fj-v1: G1, G2 passed, G3 met, G4-G6 not met; klyscan-v2: S1-S7 all passed**), the toys
(**dimu-envtoys-v1: N0, N4, N5 passed; N2, N3 failed as written**, amendment 0.16;
**dimu-envtoys-v2: N6, N8 passed**, amendment 0.17; **dimu-envtoys-v3 and the pool: N7 (criterion
(b)), N9, N10 passed**, amendment 0.18), the blind reading of ALEPH's figures (**R2 passed; R1
failed as written by 0.2 events**, NOTE-injet sec. 7), **A'-ALEPH (aprime-aleph-v1: P0, P1, P4
passed; P2 and the headline P3 failed, Z0 = 2.66)**, the A' calibration toys (**aprime-toys-v1:
C1, C2, C4 passed**), the mass-dependent ratio (**aprime-ext-v1: X0, X1, X3 passed; X2 failed;
Z0 with a free slope 1.62**) and the cross-check code's closure (**apcross-closure-v1: C0
passed**; M0 failed as written, amendment 0.26). Still queued: the DELPHI probe, ntuple,
validation and detector-simulation jobs, the four-fermion simulation (fourf), the smooth-background
test (aprime-smooth-v1, K0-K4) and the simulation and di-electron cross-check (apcross-v1, M1z-M3z,
E0-E3). Each will be graded against the expectations written before it ran. Results, positive,
negative or inconclusive, will all be published here.
