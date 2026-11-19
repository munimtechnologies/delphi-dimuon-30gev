# PLAN amendment v0.23: ALEPHLOW2 applied (the factor stays unexplained); a mass-dependent mu mu / e mu ratio, pre-registered

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after `aprime-aleph-v1` was graded (NOTE-aprime 0.1) and
after the blind reading `ALEPHLOW2` came back, **before job `aprime-ext-v1` has produced any
number**. Nothing in earlier grades changes.

## 1. ALEPHLOW2 and amendment 0.22 sec. 1b

An AI reading agent with no access to this repository read the 5-15 GeV bins of Heister's
Fig. 5 (HTML numbering; muon pairs against the binned electron-muon background) and Fig. 7 (the
unbinned fit) from the vector images. Committed exactly as read:
[data/aleph-low2.json](data/aleph-low2.json). No value ran off the axis. The muon counts in the two
figures agree bin for bin.

| bin (GeV) | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | sum |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mu mu n | 14 | 29 | 33 | 43 | 47 | 48 | 58 | 44 | 50 | 55 | 421 |
| e mu v (scaled) | 24.4 | 33.4 | 48.2 | 45.6 | 47.2 | 50.9 | 50.3 | 50.3 | 50.9 | 39.2 | 440.4 |

**Rule of 0.22 sec. 1b, applied:**
- Data: 362 + 421 = **783**, outside 1,191-1,787.
- Background: 300.9 + 440.4 = **741.3**, outside 1,166-1,748.
- Neither sum reaches its range, so **the fit table's factor stays unexplained**. The table's
  "overall" total is not the 5-50 GeV muon sample: the figures hold 783 muon pairs in 5-50 GeV,
  against 1,489 in the table.

**An observation made after seeing the numbers (not pre-registered, not a claim).** If the plotted
background is the raw electron-muon count times 0.532, the raw electron-muon count in 5-50 GeV is
741.3 / 0.532 = **1,394**, within 4.5 % (0.7 of its quoted error) of the table's "# background events
(overall)" 1,457 +- 90. In 15-50 GeV alone it is 566. That may be a coincidence. We record it because
it suggests one way the table could carry an electron-muon count, but the paper does not say so,
and nothing below depends on it.

## 2. A second observation: the mu mu / e mu ratio changes with mass

Every A' fit so far uses **one** mu mu / e mu ratio r for all masses, as Heister's statement that
the lepton efficiencies are flat in 5-50 GeV (Sec. 3.4.1) implies. The two readings do not look
flat:

| range | mu mu n | raw e mu (v / 0.532) | n / raw e mu |
|---|---|---|---|
| 5-15 GeV | 421 | 828 | 0.509 |
| 15-50 GeV | 362 | 566 | 0.640 |

By hand, with Poisson errors only, the two ratios differ by 0.13 +- 0.05, about 2.5 sigma. **We
noticed this in the data, so that number is not a test.** Inside 15-50 GeV the same trend appears
by eye (n / v about 1.06 in 15-20 GeV, about 1.5 above 25 GeV outside the signal window). A ratio
that changes with mass is a lepton-flavour-dependent effect (muon or electron identification
against momentum, electron fakes from conversions, hadrons faking muons). That is the "muon-only
detector effect" that NOTE-injet left as one of the three readings still open. It also matters for
the excess directly: a ratio that rises with mass puts more expected background under 30 GeV than
the constant-ratio fit does.

## 3. Job `aprime-ext-v1` and its grades (written before it ran)

[stats/aprime_ext.py](stats/aprime_ext.py) 0.1.0 (tests: stats/test_aprime_ext.py, made-up inputs
only) refits ALEPH's spectrum with a log-linear ratio

    r_i = r * exp(b * (x_i - 30.40 GeV)),   b free in [-0.2, 0.2] per GeV,

on 15-50 GeV (Fig. 5 reading) and on 5-50 GeV (ALEPHLOW2 + Fig. 5), for both template treatments,
with emuframe 0.1.0's likelihood unchanged (fetched, blob checked). ALEPH's signal shape and its
32.31 events in 15-50 GeV are fixed as before; the 5-15 GeV bins carry only the profile's small
tail. It also fits, at mu = 0, one ratio below 15 GeV and another above (`split`).

| | statement | prior |
|---|---|---|
| X0 | **closure (gate)**: with a constant ratio on 15-50 GeV the new code reproduces Z0(bb) = 2.664 and Z0(exact) = 4.178 within 0.005. If not, X1-X3 are NOT GRADABLE | 90 % |
| X1 | **main**: Z0(bb) with the free slope, 15-50 GeV, is below 3.0 | 90 % |
| X2 | the slope at mu = 0 (bb, 15-50 GeV) is below 2 sigma: abs(sign(b) sqrt(2 Delta lnL)) < 2.0 | 50 % |
| X3 | Z0(bb) with the free slope, 5-50 GeV, is below 3.0 | 85 % |

Reported whatever happens: every fit's Z0, mu_hat, r_hat, b_hat and b at mu = 0; Z0 with a constant
ratio on 5-50 GeV; the slope significance for both treatments and both ranges; `split`'s two ratios
and its Z (the by-hand 2.5 above is not a prediction for it). Last line `APEXT:`.

**Honesty about these priors.** The thresholds are written before any slope fit, but after the
binned numbers above were seen, so X1-X3 are not blind tests of the data; they are fixed rules for
reading a fit that has not been made.

**Meaning, written now.**
- X1 PASS with Z0(bb) much lower than 2.66 and X2 FAIL: in ALEPH's own frame, the excess leans on
  the assumption that the mu mu / e mu ratio does not change with mass, and the data themselves
  show that it does. The most economical reading is then a lepton-flavour-dependent background
  shape, not a particle.
- X1 PASS with Z0(bb) close to 2.66 and X2 PASS: the constant ratio is not what holds the excess up;
  its 2.5-2.7 sigma local significance stands as NOTE-aprime gives it.
- X1 FAIL (Z0 >= 3 with a slope): the slope makes the excess **more** significant; we will say so.
- Whatever the outcome, no statement here says whether the excess is real. Only data that ALEPH
  did not use (DELPHI's open data, test A') can do that.

## 4. Limits

Both readings are by AI reading agents from published figures (+-0.5 events per muon bin, +-0.2-0.3
per background bin). A log-linear ratio is one choice of shape among many; it was chosen because it
has one parameter and keeps r positive. No look-elsewhere correction is applied.
