# PLAN amendment v0.13: the b-tagged background shape (section 5g, test A)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-18. Made with AI agents working in MV2's name.
Written before any DELPHI dimuon mass in the 26-35 GeV window has been seen. Amends PLAN v0.11 +
amendment 0.12; both stay in force except where this text adds to them. Merged into PLAN v1.0 at
freeze. Text CC BY 4.0.

## 1. What job dimu-forecast-v2 found (graded 2026-11-18)

`dimu-forecast-v2` (stats/forecast.py 0.1.1) ran for its full 4-hour limit and was stopped
(exit 124) while running its toys. Its unit tests (10 of 10) passed, and it finished the
background-shape generation (1,000,000 Pythia 8 Z -> b bbar events, 19,584 opposite-sign dimuon
pairs, 4,797 in 15-50 GeV), the Asimov medians and the spurious-signal table. The toy-based
expectations F1-F6 (PLAN 5c) cannot be graded. The forecast is superseded by envcast
(amendment 0.12) and this amendment, and will not be re-run.

**Asimov check (rule: on noise-free data the fit must return the injected value).** It fails, and
the cause is the background model, not the fitter:

| truth (background shape) | degree chosen by the 5b sideband rule | spurious signal, in ALEPH-sized signals (degrees 1 / 2 / 3 / 4 / 5) | Asimov mu_hat for injected mu = 1 |
|---|---|---|---|
| Pythia Z -> b bbar (KDE) | 2 | +1.13 / **+0.52** / +0.02 / -0.05 / +0.06 | **1.54** |
| same, tilted +-30 % | - | +1.68 / +0.59 / -0.04 / -0.07 / +0.10 | - |
| exponential, 9 GeV slope | 2 (scenario S6) | +0.69 / +0.13 / -0.00 / -0.00 / -0.00 | 1.13 |
| power law m^-3 | - | 0.00 at every degree | - |

The spurious signals are at the yields of scenario S2 (21.7 expected signal events, 979 background
events in 15-50 GeV). On the exactly representable power law every degree returns 0.00, so the
fit itself is right. On the realistic generator shape, the pre-registered rule keeps degree 2,
which absorbs +0.52 of an ALEPH-sized signal (+11 events, 0.38 statistical standard deviations).
1 + 0.52 = 1.52, close to the observed 1.54 (the remaining 0.02 is the non-linearity of the
Poisson fit).

**Why it matters.** Amendment 0.12 found the opposite problem in the not-b-tagged category: a
negative spurious signal, which favours a false exclusion. Here the b-tagged spectrum of test A
gets a **positive** spurious signal, which would favour a false confirmation of the ALEPH
excess. The scenarios that amendment 0.12's decision rule uses (combcast's C1-C8) contain only
power-law and exponential b-tagged truths, so they could not detect this.

## 2. Section 5g, extended

Criteria (a) of section 5g (|spurious mu| <= 0.2 sigma_bonly and |mu_hat(mu = 1) - 1| <=
0.2 sigma_up) now also apply, **for test A**, in four more Asimov scenarios built from the
generator-level Z -> b bbar dimuon shape (stats/bbspur.py; same seeds as forecast-v2):

- **C9**: Pythia b bbar truth at S2 yields (1994-95 data, efficiency ratio 0.8);
- **C10**: tilted Pythia b bbar truth at S2 yields;
- **C11**: Pythia b bbar truth at S4 yields (1992-95 data);
- **C12**: exponential (9 GeV) truth at S2 yields.

A treatment is eligible only if it passes (a) in C1-C12. The ranking among eligible treatments
is unchanged (smallest Asimov ul_sens for test B in C2; `env` preferred within 2 %). The fallback
of amendment 0.12 (no treatment passes) now takes the largest spurious signal over C1-C12. The
b-tagged category also enters test B. When the treatment is chosen, the combined test B will be
re-run in C2 with the C9 truth in its tagged category, before plan v1.0 is frozen. Its spurious
signal is reported, and it enters the fallback term if it exceeds 0.2 sigma.

DELPHI's own simulation (KK2f q qbar through DELSIM, section 4) remains the final check on the
tagged shape. It is a check, not a choice: it can add a systematic, not change the treatment.

## 3. Expectations for dimu-bbspur-v1, written before it runs

| | expectation |
|---|---|
| M1 | both unit tests of test_bbspur pass, including the Asimov check on the exact power law (|spurious| < 0.02 and |mu_hat - 1| < 0.03 for every treatment) |
| M2 | it reproduces forecast-v2: in C9 the sideband rule picks degree 2, `old` gives spurious +0.45 to +0.60 and mu_hat(mu = 1) between 1.45 and 1.62 |
| M3 | `old` fails criterion (a) in C9 |
| M4 | `fix3` passes criterion (a) in C9 and C12 (forecast-v2: degree 3 gives +0.02 and -0.00) |
| M5 | `env` passes criterion (a) in C9 (honest prior about 70 %: at mu = 0 degree 3 beats degree 2 by about 1.8 units of -2 ln L after the penalty) |
| M6 | in C11 the sideband rule picks degree 3 or more (honest prior about 60 %: more events give the rule more power) |

## 4. Also recorded

- `lep4f-v1` returned: 11 of 11 tests pass, and its exact table agrees with the hand values of
  NOTE-fourfermion.md (OPAL alone: eps < 0.059; ALEPH + OPAL + L3 combined: eps < 0.055,
  central reading, no background uncertainty).
- Version guard (rule of plan v0.11): no change to dimusel.py, btagcal.py or run_ntuple.sh.
  bbspur.py is a new module; stats/forecast.py, dimustat.py and bkgsys.py are unchanged.
