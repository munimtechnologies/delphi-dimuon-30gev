# Review: what "ALEPH-sized" means (2026-11-17, plan v0.11)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents. CC BY 4.0.

**What was checked.** Whether the number that every DELPHI result will be measured against,
N_exp (the expected signal of an ALEPH-sized boson, mu = 1 in tests A and B), was defined
consistently across the code that will produce its inputs: `analysis/dimusel.py` (data
selection and hadronic count), `delsim/sigana.py` (signal efficiency from DELPHI's simulation)
and the formula in PLAN v0.10 section 4e. No job had returned, so no result is affected.

**Found.**
1. *Hadronic normalisation mixed.* v0.10 wrote N_exp = (ALEPH rate per hadronic event) x (DELPHI
   hadronic count) x (DELPHI efficiency / ALEPH efficiency). DELPHI's hadronic count comes from
   dimusel's selection, which includes a thrust-axis cut (|cos theta_T| <= 0.866) that keeps
   only about 85 % of hadronic Z decays. ALEPH's hadronic selection keeps 97.48 %
   (hep-ex/9904007). Neither efficiency was divided out, so the formula compared different
   things. The size of the error depended on which sigana number was used: with sigana 0.1.0's
   efficiency (no thrust cut) it is (eff_had,D / t_sig) / eff_had,A, where t_sig is the signal's
   thrust-cut pass rate, which is about +3 % if t_sig equals the q qbar rate. With an efficiency
   that includes the thrust cut it is eff_had,D / eff_had,A, about -13 %. The sign was not fixed.
2. *Signal efficiency not measured with the data's cuts.* sigana 0.1.0/0.2.0 selected signal
   events with its own copy of the cuts. It had no thrust-axis cut (0.2.0 applied one only to
   the b-tag sample) and no |d0|/|z0| cut, while dimusel applies both to the data.
3. *ALEPH's own count is uncertain, and the plan ignored it.* arXiv:1610.06536 reports about
   1.9M hadronic events after its selection. A footnote says about 2.2M were expected and that
   this "has to be double checked with ALEPH experts". If ordinary hadronic events were lost but
   signal events were not, ALEPH's implied rate is 2.2/1.9 = 1.16 times too high, and so is any
   "ALEPH-sized" yield built on it.

**Fixed in plan v0.11.**
- Section 5f writes N_exp as one formula in produced Z decays, with every input named: ALEPH's
  rate per produced Z (32.31 events, 1.9M or 2.2M hadronic events, 97.48 % hadronic efficiency,
  86 % per muon, 38 % b-tag, and the generator-level acceptance of the same signal events), and
  DELPHI's produced Z count per period (hadronic count divided by the hadronic efficiency of
  KK2f simulation through the same program). `analysis/nexp.py` implements it, with 10 tests,
  including closure on a synthetic world where the right answer is known and a test that
  reproduces v0.10's bias in both cases.
- `delsim/sigana.py` 0.3.0 (`dimusel_exact`) imports dimusel and applies its own code and
  configuration to the simulated signal: thrust axis, missing momentum, lepton cuts with
  |d0|/|z0|, muon tag and mass range. One of the five new tests runs dimusel's `Selector` on the
  same events and requires identical tagged and untagged counts. The tag efficiency of exactly
  these events is now the rho_D numerator of test B.
- Both ALEPH readings are computed. A result is labelled EXCLUDED or COMPATIBLE only if both
  readings give it. By hand (asymptotic), this lowers test B's chance of excluding an absent
  ALEPH-sized boson with 1992-95 data from about 0.95 to about 0.88. The cost is real, but the
  claim then does not depend on a question ALEPH's own paper leaves open.
- New expectations, written before any output: D8 (what the thrust and d0/z0 cuts cost the
  signal, and agreement of the two signal tag efficiencies) and P6-P7 (DELPHI's 1994 hadronic
  efficiency and produced-Z count against the luminosity).

**Not changed.** Blinding, cuts, fits, the data-scope rule and the outcome definitions, apart
from the two-reading rule. The queued jobs run their own copies of older code; their outputs
stay valid for what they measure, and the simulation is re-analysed with sigana 0.3.0 when it
returns (PLAN 4e).
