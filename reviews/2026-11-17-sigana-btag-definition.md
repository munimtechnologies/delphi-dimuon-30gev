# Review: the signal b-tag efficiency in `delsim/sigana.py` (2026-11-17, plan v0.10)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. CC BY 4.0.

**What was checked.** Whether the number test B (PLAN 5e) needs from the DELPHI simulation,
rho_D = (signal event tag efficiency) / (data Z -> b bbar event tag efficiency eps), can be
formed from what `sigana.py` 0.1.0 reports.

**Found (two mismatches, no effect on any result yet, since no job has returned).**
1. *Different tag.* Since plan v0.7 the primary b-tag is the hemisphere tag: an event is tagged
   if either thrust hemisphere has QBTPRP(1 or 2) below w (`analysis/dimusel.py`,
   `btag_mode="hemi"`), and eps comes from `analysis/btagcal.py` for exactly that tag. sigana
   0.1.0 measured only the event probability QBTPRP(3) at w = 0.1 ... 0.001. This is a
   different tag with a different working-point scale, so its rate cannot be divided by eps.
2. *Different sample.* btagcal's eps is measured on events that pass dimusel's hadronic
   selection, which includes the thrust-axis cut |cos theta_thrust| <= 0.866. sigana 0.1.0
   applied no thrust-axis cut. The lifetime tag depends on the vertex detector's polar
   coverage, so the rate with and without the cut can differ.

**Also found.** `eff_track` used only aligned events. An event in which DELSIM lost both
signal muons never aligns, so it was missing from the denominator, a small upward bias that
was already noted as "known, unfixed".

**Fixed in `sigana.py` 0.2.0.** `hemi_btag_after_selection` and
`hemi_btag_after_selection_thrust` give, on btagcal's ten-point grid, the event-level
hemisphere-tag rate (with binomial errors) and the per-hemisphere rate. The thrust-cut version
is the rho_D numerator (PLAN 4e step 6, expectation D7). `eff_track_all` counts every
in-acceptance signal muon of the simulated events. The 0.1.0 outputs are unchanged. There are 8 new
tests, two of which check that the working-point grid and the thrust cut are identical to
btagcal's and dimusel's (`test_sigana.py`, 16 tests; job `sigana-tests-v1`).

**Not changed.** The queued `delsim-signal-v1` still runs 0.1.0. Its simulated ntuple is
re-analysed with 0.2.0 when it returns (PLAN 4e).
