# PLAN amendment v0.26: closure passed, both readings in; M0 fails as written (four empty simulation bins) and the rule for empty bins, fixed before any fit (tests M1z-M3z, M1f-M3f); next, same-sign muon pairs (G0-G1, D1-D2, S1-S2)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `apcross-closure-v1` returned and after the two
blind readings of amendment 0.25 came back, **before any fit of those readings has been run**.
Every threshold of amendment 0.25 is kept. `aprime-smooth-v1` (amendment 0.24) is still queued;
nothing here changes its rules.

## 1. C0 graded: PASS

Job `apcross-closure-v1` (2026-11-20, 175 s; output in
`analysis/results/apcross-closure/`): stats/aprime_cross.py 0.1.0 reproduces aprime-ext-v1 on the
Fig. 5 reading: Z0 constant ratio 2.664, Z0 free slope 1.621, b at mu = 0 0.02663 per GeV, Z_slope
2.256 (all within the tolerances). New number: the data slope's 1-sigma interval is
[0.0148, 0.0384] per GeV, **sigma_b = 0.0118**. Its 13 unit tests passed, including the
cross-check against the published emuframe and aprime_ext modules.

## 2. The two readings, committed exactly as read

Both made by AI reading agents with no access to this repository, completed 2026-11-20 05:04-05:07 UTC.

- **MC4** (`data/aleph-mc4.json`): HTML Fig. 4, "Events / 1 GeV (normalized)", linear 0-70, 1 GeV
  bins; mu mu black points, e mu red line. About +-0.2 per bin (+-0.4 near the axis). **Four values
  OFF: mu mu 46-49 GeV, "no marker drawn"** (the reader counted them as 0 in its sums). The e mu
  line in 42-49 GeV lies on the axis (read 0.4, "may be 0").
- **EE25** (`data/aleph-ee25.json`): HTML Fig. 25 (text: Fig. 27), linear 0-70, 1 GeV bins, 243
  di-electron pairs in 15-50 GeV, read from the vector coordinates (+-0 per bin); identical bin by
  bin to the binned-fit figure (Fig. 26) in 15-35 GeV. No OFF value.

## 3. M0 graded as written: FAIL

M0 required every MC4 value in 15-50 GeV to be readable. Four are not, so **M0 fails as written**
and, under amendment 0.25 alone, M1-M3 cannot be graded. The job runs aprime_cross 0.1.0 unchanged
and will report this.

## 4. What is added (secondary, labelled as such in every report)

stats/apcross_m0z.py 0.1.0 (a new module; aprime_cross.py is not changed) fills the null values in
two ways and runs aprime_cross's own MC analysis on each:

| fill | rule | grades |
|---|---|---|
| zero | null -> 0.0. ROOT, which drew the figure, draws no marker for an empty bin unless asked to (option E0), and the reader saw markers down to 0.2 elsewhere | **M1z, M2z, M3z** (secondary) |
| other | null -> the e mu value of the same bin (ratio 1 there) | M1f, M2f, M3f (sensitivity) |

Thresholds are those of amendment 0.25: M1 b_MC >= 0.0133 per GeV; M2 pull < 2; M3 Z0 < 2.0 with
the slope fixed at b_MC. A grade that differs between the two fills is reported as
**reading-dependent**. E0-E3 are graded exactly as in amendment 0.25 (EE25 has no null).

Information (playbook rule: a nuisance's significance must be quoted with the signal floated): the
slope's Z with the 30 GeV signal floated, for mu mu (data) and for e e (ALEPH's e e signal shape),
from fits aprime_cross already makes.

Job `apcross-v1`; last line `APCROSS2:`.

## 5. Disclosure: what we saw before writing this

We have seen the readings, so the rule above was not chosen blind to them. To be plain about it,
here is arithmetic on the readers' own sums. It is not a test and was not fitted.

| ratio | 15-25 GeV | 25-50 GeV | 25-50 GeV without 29-32 GeV |
|---|---|---|---|
| data mu mu / e mu (Fig. 5, plotted scale) | 257 / 238.7 = 1.077 | 105 / 62.2 = 1.688 | 72 / 46.8 = 1.538 |
| simulation mu mu / e mu (Fig. 4) | 240.3 / 226.0 = 1.063 | 73.8 / 67.7 = 1.090 | 58.0 / 54.1 = 1.072 |
| data e e / e mu (Fig. 25 against Fig. 5) | 191 / 238.7 = 0.800 | 52 / 62.2 = 0.836 | 37 / 46.8 = 0.791 |

On these sums the rise is in the data's muon pairs only: not in ALEPH's simulation, and not in its
di-electrons. Our priors after seeing them (not before): M1z 10 %, M2z 60 %, M3z 10 %, E1 10 %,
E2 60 %. The four filled bins hold at most about 1.6 units of 67.7, so the two fills should agree.

## 6. Meaning, written now

- **M1z FAIL** (expected): ALEPH's own simulation does not predict the rise. The constant ratio
  ALEPH assumed is what its simulation supports, so the slope result of NOTE-aprime 0.3 sec. 8
  (2.66 -> 1.62) is **not** a simulation-backed background correction; it is a feature of the
  muon data. Then 2.66 (template error kept, constant ratio) stays our best number for the excess
  in ALEPH's own frame, and the rise above 25 GeV outside the peak window becomes part of what
  needs explaining.
- **E1 FAIL with E2 PASS** (expected): the di-electrons cannot tell (amendment 0.25 sec. 5), though
  their ratio is flat on the sums above.
- **E1 FAIL with E2 FAIL**: the rise is muon-only at 2 sigma against the electrons: a muon-specific
  effect (fake muons, muon identification against momentum) or a broad muon-only excess. Either
  way only ALEPH's raw data or another detector can settle it; DELPHI's test A' must then check
  its own muon/electron ratio against mass in the same way (NOTE-aprime sec. 8).
- **M1z PASS**: the simulation predicts the rise; we will say plainly that ALEPH's constant-ratio
  background is contradicted by its own simulation and give M3z's number.

## 7. Limits

As amendment 0.25: readings by AI agents from published figures; the simulation is a normalised
histogram, used at the data's size; one shape for the ratio; no look-elsewhere correction. The
empty-bin rule was written after the readings were seen (sec. 5).

## 8. Next question, pre-registered now: is the rise a muon-identification effect? (tests G0-G1, D1-D2, S1)

Written before the two readings below exist. If the rise is in the muon data but not in ALEPH's
simulation, either the opposite-sign muon pairs gain something the simulation lacks, or muon
identification (or fake muons from hadrons) depends on momentum differently in data and
simulation. A muon-identification effect has to appear in **same-sign** muon pairs too, which a
new opposite-sign source (a broad excess, a missing same-flavour process) does not feed. Heister's
paper shows both against simulation in one figure, and says only that the same-sign spectrum has
"no excess".

**Readings (hands goals filed 2026-11-20, blind to this repository, by caption):**

- **R21**: HTML Fig. 21, "The data/MC data description of the opposite sign di-muon mass spectrum
  (left) and the same sign di-muon mass spectra ...": per 1 GeV bin in 15-50 GeV, data count and
  total simulation (top of the stack) for both panels. Committed as `data/aleph-dmc21.json`
  {"edges", "os_data", "os_mc", "ss_data", "ss_mc"}.
- **R3**: HTML Fig. 3, "Comparison of reconstructed electron-muon masses from ALEPH data with MC
  data": per bin, data and total simulation. Committed as `data/aleph-emu3.json`
  {"edges", "data", "mc"}.

OFF values are null; a value the reader marks "no marker drawn" is filled with 0 as in sec. 4,
and every grade is also reported with the bin dropped from the window it sits in only if the
fill changes a grade (then "reading-dependent").

**Method** (new module, same likelihood as aprime_cross 0.1.0): for each spectrum, data counts
n_i against the simulation t_i used as pseudo-counts at the data's size (Barlow-Beeston, as for
MC4), ratio r exp(b (x_i - 30.40)), 15-50 GeV, at zero signal: b, its 1-sigma interval and its
signed Z against a constant ratio. Fig. 3's data are on the plotted (scaled) e mu scale, like
Fig. 5's template; the scale cancels in r.

| | statement | prior |
|---|---|---|
| G0 | gate: every R21 and R3 value in 15-50 GeV readable (after the 0-fill rule) and non-negative | 75 % |
| G1 | gate (reading consistency): R3's data agree with the Fig. 5 e mu reading (`aleph-fig5.json` v_scaled) within 0.6 in at least 30 of 35 bins | 70 % |
| D1 | opposite-sign mu mu data rise against simulation: b_OS > 0 and Z_OS >= 2.0 | 50 % |
| D2 | e mu data follow simulation: abs(Z_emu) < 2.0 | 75 % |
| S1 | **main**: same-sign mu mu share the rise: b_SS > 0, Z_SS >= 2.0 and abs(b_OS - b_SS) / sqrt(sigma_OS^2 + sigma_SS^2) < 2 | 25 % |
| S2 | opposite-sign only: Z_SS < 1.0 and the pull of S1 >= 2.0 | 30 % |

Information: b_OS with ALEPH's signal floated (degeneracy rule), and b_OS - b_emu (the data's
mu mu / e mu slope, once more, from two other figures).

**Meaning.** S1 PASS: the rise is a muon-identification or fake-muon effect that ALEPH's simulation
does not model; the excess then sits on a detector effect, and DELPHI's test A' must model its
own muon/electron ratio against momentum. S2 PASS: the rise is in opposite-sign muon pairs only,
which a detector effect does not explain easily; the broad excess becomes part of the anomaly.
Neither: undecided, said plainly.
