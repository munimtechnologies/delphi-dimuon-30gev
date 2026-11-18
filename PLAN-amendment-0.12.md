# PLAN amendment v0.12: the background model of the untagged category (section 5g)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-18. Made with AI agents. CC BY 4.0 (text);
code Apache-2.0.

This amendment is part of the pre-registration. It extends PLAN.md v0.11 (unchanged otherwise;
it will be merged into PLAN.md v1.0). It is published **before any DELPHI dimuon mass in the
26-35 GeV window has been seen**; no DELPHI data are used in anything below.

## 1. What job dimu-combcast-v1 found

`stats/combcast.py` 0.1.0 (job `dimu-combcast-v1`, run 2026-11-17 21:40 to 2026-11-18 00:43 UTC
on the Blade) computed noise-free (Asimov) forecasts of test A (b-tagged only) and test B (one
signal strength across the b-tagged and not-b-tagged spectra, section 5e) for eight scenarios.
Its 8 unit tests passed. The Asimov part finished; the toy part hit the 3-hour limit and wrote
nothing (no time budget; fixed below).

Grading of section 5e's expectations, as written:

| | expectation | result | grade |
|---|---|---|---|
| G1 | C2 median-limit ratio B/A in 0.60-0.80 | 0.481 | **FAIL** (cause below) |
| G2 | C2 toys P(EXCLUDED, mu = 0) | not run (timeout) | not graded |
| G3 | C5 toys P(EXCLUDED) >= 0.85; C5 Asimov Z0(B) in 2.8-3.8 | toys not run; Z0 2.887 | Asimov half PASS |
| G4 | C4 ratio < 0.90; C1 ratio in 0.55-0.72 | 0.750; 0.603 | PASS |
| G5 | paired toys | not run | not graded |
| G6 | < 1 % failed toy fits | not run | not graded |

**Cause of the G1 failure: a spurious signal in the not-b-tagged category.** On Asimov data with
an injected ALEPH-sized signal (mu = 1), the not-tagged fit returned mu_hat = 0.513 in C2 and
0.589 in C8. Asimov data contain no fluctuations, so mu_hat should be 1. In C2 and C8 the
not-tagged background is a mixture: Z -> b bbar pairs with a power-law shape (m^-1) plus a softer
non-b part (m^-3: charm and misidentified hadrons). The pre-registered sideband rule of 5b keeps
the degree-1 log-Legendre background (a pure power law). In log space that shape is a straight
line, but the mixture is convex, so near 30 GeV the fitted line lies about 6 % above the true
background, about 17 of the 290 not-tagged background events within +-2.5 GeV of 30.4 GeV.
The fit compensates with a **negative spurious signal of about -0.49 in mu** (-0.7 statistical
standard deviations). That spurious signal also explains the too-small Asimov sigma (0.43
instead of about 0.65: sigma was measured from the biased minimum) and hence the too-good ratio
0.48. Where the true shape is a pure power law (C7), mu_hat = 1.000 and the ratio is 0.674, in the
range G1 expected. The same mechanism, with the opposite sign, appears in C6's b-tagged
category (exponential b bbar shape, degree 2: mu_hat = 1.132).

**Why it matters.** A negative spurious signal makes a false *exclusion* of the ALEPH boson more
likely. A hand estimate for C2 test B: a combined bias of about -0.26 in mu and sigma 0.48 give
P(EXCLUDED | a real ALEPH-sized boson) of about 0.13 instead of at most 0.05. The sideband rule
alone does not protect test B, so the background treatment is fixed now, before unblinding.

## 2. Section 5g: the background treatment is chosen by a pre-registered pseudo-data test

New code: `stats/bkgsys.py` 0.1.0 (tested by `stats/test_bkgsys.py`, 11 tests) and
`stats/envcast.py` 0.1.0. Job: `dimu-envcast-v1`.

Candidate treatments, all evaluated on the same per-degree profile curves (the profile of
-2 ln L at fixed mu for each log-Legendre degree 1-5, scanned on a mu grid of step 0.05):
- `old`: the sideband rule of 5b (v0.4), per category.
- `fix3`: degree 3 in every category.
- `env`: the discrete-profiling envelope (Dauncey, Kenzie, Wardle, Davies, JINST 10 (2015)
  P04015, arXiv:1408.6865): at each mu, the minimum over degrees 1-5 of -2 ln L + 1 per shape
  parameter. The background function becomes a discrete nuisance parameter.
- `env_min2`: the same envelope over degrees 2-5.
- `ss` (reference only, not eligible): the lowest degree whose spurious signal on the TRUE
  background is below 0.2 of its statistical standard deviation (the ATLAS H -> gamma gamma
  criterion). It uses the truth, which the real analysis does not have.

**Decision rule (fixed now).** A treatment passes if
- (a) in every scenario C1-C8, for test A and for test B: |spurious mu| <= 0.2 sigma_bonly and
  |mu_hat(mu = 1) - 1| <= 0.2 sigma_up(mu = 1) (Asimov), and
- (b) in the C2 toys with a true ALEPH-sized boson (mu = 1): P(EXCLUDED) <= 0.07 for test A and
  for test B (200 toys: the binomial error at 0.05 is 0.015).
Among the passing treatments, plan v1.0 uses the one with the smallest Asimov ul_sens for test B
in C2; within 2 %, `env` is preferred because it is data-driven. If none passes, v1.0 uses the
treatment with the smallest worst-case |spurious|/sigma and adds its worst spurious signal over
C1-C8 as a Gaussian constraint on an additive mu offset; that addition is written and tested
before unblinding. In every case, the chosen treatment is also run on DELPHI's own simulated
background (KK2f q qbar through the full selection, both categories) and the spurious signal is
published; if it exceeds 0.2 sigma there, the same additive term is used.

## 3. Expectations for dimu-envcast-v1, written before it runs

- K0 (closure with v1): `old` reproduces combcast's Asimov mu_hat(mu = 1) within 0.03: C2
  untagged 0.513, C8 untagged 0.589, C6 tagged 1.132, C7 untagged 1.000, C4 untagged 0.937,
  and 1.000 for the power-law tagged categories.
- K1: C2 untagged, degree 1: spurious mu in [-0.56, -0.42] and |spurious|/sigma >= 0.6.
- K2: the `ss` degree is 1 in every power-law b-tagged category, and at least 2 in C2 and C8
  untagged and C6 tagged.
- K3: `env` passes criterion (a). Honest prior: about even odds, because a degree-1 fit with a
  negative signal may stay within one unit of -2 ln L of the degree-2 fit.
- K4: `env`'s cost in sensitivity is small: test B's ul_sens in C2 is at most 1.25 times `ss`'s.
- K5: under the chosen treatment, the C2 ratio ul_sens(B) / ul_sens(A) is in 0.60-0.85 (v0.9's
  hand value 0.69; G1's original range, which failed only because of the bias).
- K6: C2 toys, test B, mu = 1: P(EXCLUDED) for `old` in 0.07-0.25 (hand 0.13); for the chosen
  treatment at most 0.07.
- K7: C2 toys, test B, mu = 0: P(EXCLUDED) for the chosen treatment in 0.45-0.85.

The toys use sigma(mu) from each treatment's own background-only Asimov profile, measured from
its minimum (for `old` this differs from dimucomb.analyse, which took sigma from each toy's
background-only fit). The toy part runs under a 75-minute budget and writes every 10 toys, so a
timeout no longer loses the results.

## 4. Also recorded in this amendment

- Unit-test jobs returned: `sigana-tests-v1` (16 of 16 pass) and `sigana3-tests-v1` (nexp and
  sigana 0.3.0, 21 sigana tests pass); `dimusel-tests-v2` (all pass, anti-kt 4.2 ms per event).
- The four-fermion line (NOTE-fourfermion.md): the third paper reading
  (`readings/lep4f-papers-notes-3.md`) found OPAL's muon acceptance, |cos theta| < 0.9, so
  eff4f's `cos0.9` variant becomes OPAL's nominal reading in NOTE-fourfermion 0.4. ALEPH's
  reference-20 cuts were found (one isolated lepton, p > 3 GeV each, sum > 20 GeV); ALEPH is not
  used in the bound because it shows no mu-mu-only mass spectrum.
