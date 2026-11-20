# PLAN amendment v0.25: where does the rising mu mu / e mu ratio come from? ALEPH's own simulation and its di-electrons (tests C0, M0-M3, E0-E3)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after `aprime-ext-v1` was graded (NOTE-aprime 0.3 sec. 8)
and **before either of the two readings below exists** and before job `apcross-closure-v1` has
produced any number. `aprime-smooth-v1` (amendment 0.24) is still queued; nothing here changes its
rules. Nothing in earlier grades changes.

## 1. Why

In the blind reading of Heister's Fig. 5 the muon pairs rise against the electron-muon template
with mass: a log-linear ratio fitted at mu = 0 has slope b = 0.0266 per GeV (Z 2.26), and with
that slope free the 30 GeV excess falls from 2.66 to 1.62 sigma (NOTE-aprime 0.3 sec. 8). Heister's
analysis assumes a constant ratio. Three explanations predict different things:

| explanation | ALEPH simulation (q qbar only) | ALEPH di-electrons against e mu |
|---|---|---|
| (a) an expected feature of b-quark decays and the selection that the e mu template does not share | rises like the data | depends on cause |
| (b) muon-only detector effect (hadrons faking muons more often at high momentum, muon ID against momentum) | rises only if the simulation models it | flat |
| (c) a same-flavour source missing from the simulation (virtual photons radiated in Z -> q qbar give e e and mu mu, not e mu; or a broad version of the excess) | flat | rises like the muons |

Heister's text says of Fig. 4 that in simulation the two spectra "agree well within their errors"
and that the lepton identification efficiency does not depend on the pair mass in 5-50 GeV; those
are statements by eye and do not quantify a slope.

## 2. Two blind readings (hands goals, filed this run)

Read by AI reading agents with no access to this repository, from the vector figures of
arXiv:1610.06536 v9 (HTML), identified by caption:

- **MC4**: the figure captioned "Comparison of the opposite sign di-muon mass spectrum to the
  electron-muon mass spectrum for ALEPH MC data only" (HTML Fig. 4). For every 1 GeV bin from
  15 to 50 GeV (or the plotted bin width, if different), the simulated mu mu value and the
  simulated e mu value as plotted. Committed as `data/aleph-mc4.json` {"edges", "mumu", "emu"},
  exactly as read; OFF becomes null.
- **EE25**: the figure captioned "The result of the extended maximum likelihood fit of the signal
  + background model to the unbinned opposite sign di-electron ..." (HTML Fig. 25). For every bin
  from 15 to 50 GeV, the di-electron data count. Committed as `data/aleph-ee25.json`
  {"edges", "n"}. The binned chi-square figure (HTML Fig. 26, 15-36 GeV) is read as a cross-check
  of the counts only.

## 3. Method (stats/aprime_cross.py 0.1.0; tests on made-up inputs in stats/test_aprime_cross.py)

Self-contained; the likelihood and signal template are identical to emuframe 0.1.0 and aprime_ext
0.1.0 (checked by unit tests against both modules). Model "bb" throughout, 15-50 GeV, pivot
30.40 GeV, b in [-0.2, 0.2] per GeV.

- **Data slope**: b and its 1-sigma interval (profile drop of 0.5, 801-point grid) for the Fig. 5
  reading at mu = 0.
- **MC**: the simulated mu mu values are used as counts and the simulated e mu values divided by
  0.532 as the template (pseudo-counts at the data's size; the simulation is about twice as large,
  so the MC errors are conservative). b_MC, its interval, its Z against a constant ratio.
- **EE**: di-electron counts against the Fig. 5 e mu template (divided by 0.532); bins merged to
  the coarser of the two grids if they differ. b_ee, its interval, Z. Information: ALEPH's e e
  signal (29.18 GeV, Gamma 1.78, sigma 0.70 GeV, 8.00 events at mu = 1) fitted with a constant
  ratio and with a free slope.

## 4. Statements (written before any reading or output)

| | statement | prior |
|---|---|---|
| C0 | **gate** (job `apcross-closure-v1`, filed now): on the Fig. 5 reading the new code reproduces aprime-ext-v1's bb numbers: Z0 constant 2.664 and Z0 slope 1.621 within 0.01, b at mu = 0 0.0266 within 0.001, Z_slope 2.256 within 0.02. If not, nothing below is gradable until fixed | 85 % |
| M0 | gate: every MC4 value in 15-50 GeV readable and non-negative | 85 % |
| M1 | **main**: b_MC >= 0.0133 per GeV (half the data's slope): ALEPH's own simulation predicts at least half of the rise | 35 % |
| M2 | the data slope is consistent with the MC slope: abs(b_data - b_MC) / sqrt(sigma_data^2 + sigma_MC^2) < 2 | 60 % |
| M3 | with the ratio's slope **fixed** at b_MC, Z0(bb) of the 30 GeV excess in the data is below 2.0 | 35 % |
| E0 | gate: every EE25 count in 15-50 GeV readable; grids share 15 and 50 GeV | 85 % |
| E1 | **main**: the di-electrons rise too: b_ee > 0 and Z_slope(ee) >= 2.0 | 40 % |
| E2 | b_ee is consistent with the muons' b: pull < 2 as in M2 | 65 % |
| E3 | information: e e signal events with constant ratio and with free slope; e e expected from the muons under lepton universality (0.94^2 x fitted mu mu signal) | - |

Last output line `APCROSS:`.

**Priors.** M1's is low because Heister looked at Fig. 4 and saw agreement; E1's is below 50 %
because the e e sample is smaller (his e e fit table's background is 0.71 of the mu mu one), so
the same slope would give Z near 1.9.

## 5. Meaning, written now

- **M1 PASS and M2 PASS**: ALEPH's own simulation predicts the rising ratio, so the constant-ratio
  background is contradicted by the experiment's own simulation, and the honest background under
  30 GeV is the sloped one. M3 then gives the excess's significance with a slope that was not
  fitted to the data. We will say so plainly, with M3's number, in a NOTE and in any article.
- **M1 FAIL and E1 PASS**: the rise is in same-flavour pairs (e e and mu mu) but not in the q qbar
  simulation: a same-flavour source the simulation lacks (explanation c). That makes a precise
  prediction for the 4-fermion process Z -> q qbar l+ l- (its rate and mass shape in b-tagged
  events), which is the next test.
- **M1 FAIL and E1 FAIL with E2 FAIL**: the rise is muon-only and not in the simulation
  (explanation b, or a statistical fluctuation of the muon spectrum); the excess's significance
  then depends on a detector effect that only ALEPH's raw data can settle.
- **M1 FAIL, E1 FAIL, E2 PASS**: the e e sample cannot tell; we will say it is undecided.
- Whatever happens, nothing here says whether the excess is real; DELPHI's open data (test A') can.

## 6. Limits

Readings by AI agents from published figures; simulated values are normalised histograms, so
their per-bin errors are not known and are taken at the data's size. A log-linear ratio is one
shape. The e mu template for the di-electrons is the muon analysis's template (Heister uses the
same e mu spectrum for both, Sec. 4.9-4.10). No look-elsewhere correction.
