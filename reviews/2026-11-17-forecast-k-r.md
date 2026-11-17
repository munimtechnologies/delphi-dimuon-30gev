# Review: do the forecasts and the final fit use the same "ALEPH-sized"? (2026-11-17, nexp 0.2.0)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. CC BY 4.0.

**Why.** Plan v0.11 (section 5f) defines the expected signal of an ALEPH-sized boson, N_T and
N_U, as one formula in produced Z decays (`analysis/nexp.py`). Two older modules also carry an
"ALEPH-sized" yield: the forecasts `stats/forecast.py` (5c) and `stats/combcast.py` (5e), both
using N_exp = 32.31 k r, and the joint fit `stats/dimucomb.py` (5e). Before any of their outputs
is graded or re-run with measured inputs, this note checks by hand that all three mean the same
thing. No job had returned; no DELPHI mass in the window has been seen; blinding is unchanged.

**1. dimucomb and nexp: consistent.** `dimucomb.analyse(ns, nexp)` takes the expected yield of
each category at mu = 1, in the order of the histograms. `nexp.totals` gives exactly these,
summed over periods: `readings["nominal"]["n_t"]` and `["n_u"]`. The rho bookkeeping agrees:
nexp's ALEPH rate uses the 0.38 tag efficiency without rho and DELPHI's N_T uses eps_D without
rho, so rho cancels in N_T as 5e requires, and N_U = N_T (1 - eps rho) / (eps rho) in both
modules. One harmless difference: `dimucomb.nexp_untagged` returns 0 if eps rho >= 1, while
`nexp.period_yields` refuses such input. The final fit takes N_U from nexp (5f), so the refusal
applies; `nexp_untagged` is only used inside combcast's synthetic scenarios.

**2. The forecasts' k is a ratio of selected counts; 5c never said so.** Section 5c defines k
as "DELPHI's hadronic-Z count over ALEPH's 1.9M" and uses 0.84 for 1994-95. That 0.84 is
1.6M / 1.9M, where 1.6M is DELPHI's count after a hadronic selection that includes a thrust-axis
cut (arXiv:2510.18762) and 1.9M is ALEPH's count after its own selection (97.48 % efficient).
In produced Z decays, the 5f quantity, the same ratio is about (1.6M / 0.85) / (1.9M / 0.9748)
= 0.97, not 0.84. The forecasts are not wrong for this: with k a ratio of selected counts,
32.31 k r equals 5f's N_T exactly when r is read as the ratio of signal efficiencies per
SELECTED hadronic event:

    r = (eff_sel,D x eps_D / eff_had,D) / (eff_sig,A / eff_had,A)

(weighted by selected hadronic counts when periods are merged). But 5c promises a re-run "with
per-period r once 4j's production counts exist", and mixing a produced-Z k with a
selected-event r, or the reverse, would mis-scale N_exp by about 15 % in either direction.
**Rule, binding from now on:** every re-run of forecast.py or combcast.py with measured inputs
takes k and r from `nexp.forecast_kr` (new in nexp 0.2.0): k = sum of DELPHI's selected
hadronic counts / 1.9M, r = nominal N_T / (32.31 k). Two new tests check that 32.31 k r
reproduces N_T to 1e-9, that r has the closed form above, and that over two periods it is the
count-weighted mean of the per-period values.

**3. What the forecasts' background then assumes.** Both forecasts scale ALEPH's 1457 tagged
background pairs by k r. ALEPH found those pairs among its 1.9M selected events, so k must be
the selected-count ratio (as it is), and k stays the same under the "low" reading of 5f: only
the signal changes there (limits x 1.158, as 5f says). The one remaining assumption is the one
5c already states: DELPHI's background efficiency relative to ALEPH's equals the signal's r.
Real DELPHI background comes from the blinded sidebands in the final fit, so this assumption
only affects the forecasts, never the result.

**4. ALEPH's hadronic selection applied to the signal.** 5f's R_A divides ALEPH's 32.31 events
by A_gen x 0.86^2 x 0.38, not by ALEPH's hadronic-selection efficiency for the signal events
themselves (call it h). The signal events in A_gen already have at least 5 charged particles
and a 15-50 GeV muon pair, so ALEPH's selection (at least five good tracks, charged energy above
15 % of sqrt(s)) should keep nearly all of them: h close to 1. If h were below 1, R_A, and with
it every N_T and N_U, would be too small by the factor h, so mu = 1 would be a slightly smaller
signal than ALEPH-sized. That can only make EXCLUDED harder to reach, never easier; even h equal
to ALEPH's q qbar efficiency, 0.9748, would move N_exp by 2.6 %. Recorded in nexp's docstring;
no number changes.

**5. ALEPH's 1.9M-versus-2.2M footnote, re-read.** arXiv:1610.06536 v9, footnote 1: after the
standard hadronic selection and the ALEPH Heavy Flavour group's run-quality requirements, "about
1.9 M" events remain, while "about 2.2M" were expected "according to e.g." ALEPH, Phys. Lett.
B401 (1997) 150 (the R_b lifetime-mass-tag paper); the discrepancy "has to be double checked
with ALEPH experts" and is said not to affect that paper's result. Signal and ordinary hadronic
events are both multi-track hadronic events passing the same selection, so a loss of runs or of
reconstruction quality would hit both alike, which is the nominal reading. The "low" reading
needs a loss that spares the signal, so it is a conservative bound, not a likely value. Nothing
public that we could read resolves the footnote, so the two-reading rule of 5f stays as fixed in
v0.11. Per 5f, a resolution from ALEPH members or the author before plan v1.0 would be used,
with its source.

**Not changed.** Cuts, fits, blinding, the data-scope rule, the outcome labels and the F1-F6
and G1-G6 expectations, which are graded as written. Their scenario grid (r = 0.6, 0.8, 1.0)
already spans the ambiguity found in point 2. This note is folded into plan v1.0, section 5c.
