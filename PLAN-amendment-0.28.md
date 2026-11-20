# PLAN amendment v0.28: simulation, di-electron and same-sign tests graded (the rise is in muon pairs of both charges, not in the simulation or the electrons; two grades depend on values hidden below a log axis); next, the same-sign pairs as a control sample for the excess (tests W0-W5)

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-20. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after jobs `apcross-v1` and `dmcratio-v1` returned, **before
job `sscontrol-v1` exists**. Every threshold of amendments 0.24-0.27 is kept. `aprime-slsm-v1`
(amendment 0.27 sec. 6) is still queued; nothing here changes its rules.

## 1. apcross-v1 graded (amendments 0.25-0.26)

Full grades in [NOTE-aprime.md](NOTE-aprime.md) 0.5, section 10; raw output in
`analysis/results/apcross/`. In short: C0 PASS; M0 FAIL as written (four empty simulation bins);
under both empty-bin fills **M1 FAIL** (ALEPH's simulation has no rise: b_MC = -0.005 +- 0.012 per
GeV against the data's 0.027 +- 0.012), **M2 PASS** (but the two differ by only 1.84 sigma),
**M3 FAIL** (with the simulation's slope the excess is 2.9 sigma in the conservative frame); E0
PASS, **E1 FAIL** (ALEPH's di-electrons do not rise against the e mu template: b_ee = -0.008 +-
0.014), **E2 PASS** (pull 1.89). All six expectations written with the readings in view were met.

## 2. dmcratio-v1 graded (amendments 0.26 sec. 8 and 0.27)

Full grades in NOTE-aprime 0.5, section 11; raw output in `analysis/results/dmcratio/`. G0 FAIL as
written (known, amendment 0.27); G1 PASS (35 of 35 bins). Against ALEPH's simulation:

| | b (per GeV), OFF -> 0 | Z | b, OFF -> 0.29 | Z |
|---|---|---|---|---|
| opposite-sign mu mu | 0.0280 +- 0.0134 | 2.10 | 0.0218 +- 0.0130 | 1.68 |
| same-sign mu mu | 0.0409 +- 0.0184 | 2.25 | 0.0238 +- 0.0170 | 1.41 |
| e mu | 0.0001 +- 0.0111 | 0.01 | same | same |
| pull OS - SS | -0.57 | | -0.09 | |

**D2 PASS; S2 FAIL** under both fills; **D1 and S1 are reading-dependent** (PASS with OFF -> 0,
FAIL with OFF -> 0.29). What holds under both fills: the same-sign pairs rise with the same slope
as the opposite-sign pairs, and the e mu pairs do not rise. What does not: whether either rise
alone reaches 2 sigma. The fill matters because a few single events above 38 GeV sit in bins whose
simulation lies below the bottom of the log axis.

## 3. Next test, pre-registered now: the same-sign pairs as a control sample (tests W0-W5)

**The idea.** ALEPH claims no excess in same-sign muon pairs, so they are a control sample: if
muon pairs of either charge drift upward against the simulation as the mass grows, a background
built from e mu pairs with one constant ratio under-predicts the muon pairs at high mass, and part
of the 30 GeV excess is that drift. Section 2 suggests such a drift but cannot size it, because of
the hidden values. This test removes them and measures what the control implies.

**Window rule.** W = [15 GeV, hi), where hi is the largest upper edge such that every value of
every spectrum (opposite- and same-sign data and simulation, e mu data and simulation) is readable
after the NM -> 0 rule. On the committed readings this gives **hi = 38 GeV** (the first hidden
value is the opposite-sign simulation at 38-39 GeV); the code computes it and the gate checks it.

**Method** (stats/sscontrol.py 0.1.0, a new module; aprime_cross 0.1.0 and dmcratio 0.1.0 are used
unchanged; job `sscontrol-v1`, pure Python). In W, at zero signal, model "bb" with the simulation as
pseudo-counts at the data's size, ratio r exp(b (x - 30.40)): b_SS, b_OS, b_emu; and the joint
opposite- plus same-sign slope (one b, separate r) with ALEPH's 30 GeV signal floated (mu >= 0) in
the opposite-sign spectrum. The control slope is **b_ctrl = b_SS - b_emu**, sigma_ctrl =
hypot(sigma_SS, sigma_emu). ALEPH's simulation predicts no mu mu / e mu slope (section 1), so
b_ctrl is the mu mu / e mu slope that a same-sign muon-pair drift predicts. The excess: the Fig. 5
reading, 15-50 GeV, model "bb" as in aprime_cross, with the ratio's slope **Gaussian-constrained to
b_ctrl +- sigma_ctrl**.

| | statement | prior |
|---|---|---|
| W0 | **gate**: aprime_cross closure C0 passes; the module reproduces dmcratio-v1's 15-50 GeV slopes with OFF -> 0 (b_OS 0.02804, b_SS 0.04094) within 0.001; the window rule gives 38 GeV and every value in W is readable and non-negative. If not, W1-W5 are NOT GRADABLE | 90 % |
| W1 | same-sign pairs rise in W: b_SS > 0 and Z_SS >= 2.0 | 35 % |
| W2 | **main**: the joint opposite- plus same-sign slope in W, with the 30 GeV signal floated, has b > 0 and Z >= 2.0 | 45 % |
| W3 | e mu pairs follow simulation in W: abs(Z_emu) < 2.0 | 90 % |
| W4 | the control predicts the data's mu mu / e mu slope: abs(b_ctrl - b_data) / hypot(sigma_ctrl, sigma_data) < 2, with b_data, sigma_data the Fig. 5 15-50 GeV slope at zero signal (0.0266 +- 0.0118) | 85 % |
| W5 | with the slope constrained to b_ctrl +- sigma_ctrl, Z0(bb) of the excess is below 2.0 | 80 % |

Reported whatever happens: every slope in W with its interval; the joint slope without the signal;
the opposite-sign slope in W with the signal floated; Z0 and mu_hat with the slope fixed at b_ctrl
and at b_ctrl +- sigma_ctrl; the constrained fit with the simulation's own mu mu / e mu slope in W
added to b_ctrl (information). Last line `SSCTRL:`.

**Meaning, written now.**
- **W2 PASS with W4 PASS**: muon pairs of both charges rise against ALEPH's simulation by one slope,
  at 2 sigma or more with the 30 GeV signal allowed for, and the same-sign control predicts the
  slope that the opposite-sign data show against the e mu template. The rising ratio is then a
  property of ALEPH's muon pairs in general (a muon-identification or fake-muon effect, or a
  background the simulation lacks, feeding both charges), not something the 30 GeV excess makes.
  ALEPH's constant-ratio background is contradicted by its own same-sign control, and W5's number
  is the excess with a control-driven background in the conservative frame.
- **W2 FAIL with W4 PASS**: the control agrees with the data's slope but cannot establish the
  drift on its own; undecided, said plainly; W5 is then conditional on a drift the control does
  not establish.
- **W4 FAIL**: the same-sign control does not predict the data's slope; the rise of opposite-sign
  pairs against e mu is then not explained by a drift common to both charges.
- **W5**: PASS means that with the control's slope the excess is below 2 sigma local in the
  conservative frame; FAIL that it keeps 2 sigma or more. The same constraint in the smooth (par3)
  frame is pre-registered only after `aprime-slsm-v1` is graded.
- Whatever happens: no number here says whether the excess is real; only data ALEPH did not use
  (DELPHI's) can.

## 4. Disclosure: what we saw before writing this

The window rule was written after the readings were seen and after `dmcratio-v1` showed that the
hidden values decide D1 and S1. Plain arithmetic on the readings inside W (not a test, not fitted):

| data / simulation | 15-25 GeV | 25-38 GeV |
|---|---|---|
| opposite-sign mu mu | 257 / 252.8 = 1.017 | 97 / 74.9 = 1.295 |
| same-sign mu mu | 186 / 195.2 = 0.953 | 48 / 37.0 = 1.297 |
| e mu (scaled) | 239.5 / 226.3 = 1.058 | 59.4 / 62.0 = 0.958 |

Inside W both charges of muon pairs rise against the simulation by about the same factor
(1.27 and 1.36 from the lower to the upper range) and e mu pairs fall slightly (0.91). Our rough
estimate of each slope's significance from these sums (about 1.3-1.7 sigma for same-sign alone) is
why W1's prior is low; W2 combines both charges.

## 5. Limits

Readings by AI agents of published figures, not ALEPH's events. The simulation histograms are used
as pseudo-counts at the data's size, which overstates their noise if ALEPH's simulation is larger
than its data, and so understates every slope's significance. A log-linear ratio is one shape. The
window ends at 38 GeV, so slopes are measured on 15-38 GeV and applied to 15-50 GeV. The same-sign
and opposite-sign pairs come from different processes in b b-bar events (b-c cascades and mixing
against direct pairs), so a common slope is an assumption that W2 tests, not a given. No
look-elsewhere correction.
