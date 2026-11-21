# PLAN amendment v0.31: same-sign control graded (same-sign pairs rise at 2.1 sigma and predict the data's slope, but the joint slope stays below 2 sigma with the signal allowed for: undecided); next, the drift in events with the b-tag inverted (tests A0-A4), fixed before that figure is read

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-21. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `sscontrol-v1` returned, while `aprime-slsm-v2`
(amendment 0.29) and `ssframe-v1` (amendment 0.30) are still queued and **before anyone has read
the values of Heister's Fig. 24**. Every earlier test and threshold is kept.

## 1. sscontrol-v1 graded (amendment 0.28 sec. 3)

Raw output: `analysis/results/sscontrol/` (sscontrol.json, run.txt, tests, sha256, job.json);
grades: `analysis/results/sscontrol/grades-sscontrol.json`. Window 15-38 GeV, 23 bins, every value
readable; no hidden value was used anywhere.

| test | statement | prior | result | grade |
|---|---|---|---|---|
| W0 | gate (closures, window 38 GeV, readable) | 90 % | C0 PASS; dmcratio-v1 slopes reproduced exactly (0.02804, 0.04094); window 15-38 | **PASS** |
| W1 | same-sign pairs rise: b_SS > 0, Z >= 2.0 | 35 % | b_SS = 0.0387 [0.0201, 0.0576] per GeV, Z 2.09 | **PASS** |
| W2 | **main**: joint OS + SS slope, signal floated, Z >= 2.0 | 45 % | b = 0.0237, Z 1.77 | **FAIL** |
| W3 | e mu follow simulation: abs(Z) < 2.0 | 90 % | b_emu = 0.0042 [-0.0077, 0.0161], Z 0.35 | **PASS** |
| W4 | control predicts the data's slope: abs(pull) < 2 | 85 % | b_ctrl = 0.0345 +- 0.0222 vs 0.0266 +- 0.0118: pull 0.31 | **PASS** |
| W5 | excess with the slope constrained to b_ctrl: Z0(bb) < 2.0 | 80 % | Z0 = 1.42 (mu_hat 0.56, b_hat 0.019) | **PASS** |

Reported as promised (information): opposite-sign slope in the window 0.0238 +- 0.0146 (Z 1.64),
falling to 0.0072 (Z 0.37) with the signal floated, so in opposite-sign pairs alone the slope and
the 30 GeV peak are nearly the same thing; joint slope without the signal 0.0295 (Z 2.58); the
simulation's own mu mu / e mu slope 0.0038 +- 0.0137; Z0 with the slope fixed at b_ctrl 0.89, at
b_ctrl - 1 sigma 2.02, at b_ctrl + 1 sigma 0.00; constrained with the simulation's slope added,
Z0 1.42.

**Meaning, as written in amendment 0.28 (case "W2 FAIL with W4 PASS").** ALEPH's same-sign muon
pairs, where ALEPH claims no excess, rise against ALEPH's simulation by 2.1 sigma, and the slope
they imply for the mu mu / e mu ratio (0.035 per GeV) agrees with the slope the opposite-sign data
prefer (0.027). But once the 30 GeV signal is allowed for, the two charges together do not
establish the drift at 2 sigma. So the control **agrees** with a drift and does not **establish**
one: undecided, said plainly. W5's number (1.42 sigma local in the conservative frame) is
conditional on that drift.

Our hand estimate published before the run (amendment 0.30 sec. 5) was b_ctrl about 0.04 +- 0.03;
the job gave 0.0345 +- 0.0222.

**For ssframe-v1 (amendment 0.30 sec. 4, unchanged).** W4 PASSED, so ssframe's number may be the
headline; W2 FAILED, so P1 / P2 will be stated as conditional on a drift the same-sign control does
not establish on its own. ssframe's `CONTROL` line must reproduce b_ctrl = 0.034512 and
sigma_ctrl = 0.022177 (it uses the same helpers); a mismatch is reported.

## 2. A fact we had not used: ALEPH's simulation is about twice the data

Heister sec. 2.2: the analysis uses about 3.7 M data events and "about 8 Million simulated events"
of fully simulated hadronic Z decays. Every fit since amendment 0.24 treats the simulation as
pseudo-counts at the data's size, which overstates its noise (as amendment 0.28 sec. 5 said) and
so understates every slope's significance. **No grade changes because of this**: W2 stays FAIL.
From now on modules report, as information only, the slopes with the simulation weighted 2.2 times
the data's size; the weight is approximate (the selected b-tagged fraction of the simulation is not
stated).

## 3. Next test, pre-registered now: the drift in events with the b-tag inverted (tests A0-A4)

**The idea.** Heister's HTML Fig. 24 (caption: "The opposite sign di-muon mass spectrum for events
where the b-tag was inverted, i.e. P_H,mass,max < 2. Contributions from different hadronic Z0
decays are identified by different colors.") shows opposite-sign muon pairs in events that fail
the b-tag, with the simulation's flavour contributions drawn. Heister sec. 4.8 says no excess is
visible there. These events are disjoint from the b-tagged sample. If the rise against simulation
is a property of ALEPH's muon pairs in general (muon identification, fake muons from pion and kaon
decays or punch-through, the simulation's muon kinematics), it should appear there too. If it is
tied to b events (cascade decays) or to the excess, it should not. This is the independent sample
that W2 could not supply.

**Reading.** One blind reading of Fig. 24 by an AI reading agent with no access to our work, on its
own bins, data counts and total simulation (top of the stack) per bin, NM and OFF marked as in the
Fig. 21 reading. Committed as `data/aleph-abtag24.json` before the job is filed.

**Method** (stats/abtag.py 0.1.0, new module; aprime_cross 0.1.0 and dmcratio 0.1.0 unchanged;
job `abtag-v1`, pure Python). Window W_A = [15 GeV, hi), hi the largest edge with every data and
simulation value of Fig. 24 readable after NM -> 0. Model "bb" (simulation as pseudo-counts at the
data's size), ratio r exp(b (x - 30.40)), zero signal: b_A, 1-sigma interval, signed Z against a
constant ratio. Comparison slope: sscontrol-v1's b_SS = 0.0387 +- 0.0187 (same window rule, same
model; same-sign rather than b_ctrl, because Fig. 24 is compared with simulation directly, not
with e mu). ALEPH's fixed 30 GeV signal shape, mu >= 0, slope free, for A4.

| | statement | prior |
|---|---|---|
| A0 | **gate**: C0 passes; the module reproduces sscontrol-v1's b_SS (0.03873) within 0.001; W_A reaches at least 30 GeV; data in W_A are whole numbers of events (within 0.05), non-negative, at least 100 events. If not, A1-A4 are NOT GRADABLE | 75 % |
| A1 | **main**: opposite-sign pairs with the b-tag inverted rise against simulation: b_A > 0 and Z_A >= 2.0 | 40 % |
| A2 | the inverted-tag slope agrees with the same-sign slope: abs(b_A - b_SS) / hypot(sigma_A, sigma_SS) < 2.0 | 80 % |
| A3 | the drift is specific to b-tagged events: Z_A < 1.0 and (b_SS - b_A) / hypot >= 2.0 | 15 % |
| A4 | no 30 GeV excess with the b-tag inverted: Z0 (slope free) < 2.0 | 85 % |

Reported whatever happens: the window, event count, data / simulation in 15-25 GeV and above;
b_A with interval; the pull; Z0 and mu_hat with the slope free and with a constant ratio; and,
as information, b_A, b_SS and b_OS with the simulation weighted 2.2 times (section 2). Outputs
`abtag.json`, last line `ABTAG:`.

**Meaning, written now.**
- **A1 PASS with A2 PASS**: muon pairs rise against ALEPH's simulation by a common slope also in
  events with no b-tag. The drift is then a property of ALEPH's muon pairs or of its simulation of
  them, established in an independent sample, and not something the 30 GeV excess makes. In the
  significance note, ssframe's P1 / P2 are then stated as "conditional on the drift, which ALEPH's
  inverted-b-tag sample establishes independently". This sentence is a new rule written **after**
  W2's FAIL was seen and before ssframe-v1 or Fig. 24's values exist; amendment 0.30's rule is
  otherwise unchanged.
- **A1 FAIL with A2 PASS**: the inverted-tag sample cannot tell; undecided stays undecided.
- **A3 PASS**: the drift is confined to b-tagged events (b cascade modelling, or something tied to
  the signal region). The same-sign control is still the right control for the excess (both are b
  events), but the muon-identification explanation is disfavoured.
- **A2 FAIL with b_A > b_SS**: the inverted-tag sample rises more steeply than the b-tagged
  control: a drift that depends on the event's flavour; reported, no claim.
- **A4 FAIL**: an excess at 30 GeV with the b-tag inverted, against Heister's statement; it would
  be reported and followed up, not explained away.
- Whatever happens: no number here says whether the excess is real. Only data ALEPH did not use
  (DELPHI's open data) can.

## 4. Disclosure: what we knew when writing this

Seen: all graded results above and before; Fig. 24's caption and Heister's sentence that no excess
is visible with the inverted tag (from a text-only fetch of the HTML paper). **Not seen**: any value
in Fig. 24, its axis type or range, its event count. Priors come from the size of the b-tagged
drift (about 0.03 per GeV) and the guess that the inverted-tag sample is larger than the tagged
one; A0's prior allows for a log axis hiding values below 30 GeV or a normalised scale.

## 5. Limits

Readings by AI agents of published figures, not ALEPH's events. The inverted-tag sample has a
different make-up (more c c-bar and more fake muons), so a common slope tests muon and fake
modelling, not b decay modelling. Simulation as pseudo-counts at the data's size (conservative).
One log-linear shape. No look-elsewhere correction.
