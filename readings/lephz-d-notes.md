# Reading LEPHZ-D: L3's recoil question and OPAL 1997's recoil cut

Read on 2026-11-18 by an AI reading agent working for MV2 of Munim, Inc., from the text layer of
the scanned preprints (not checked against page images, except one cross-check noted below).
Text CC BY 4.0. Quotes are as reported by the agent; "not stated" means the paper does not give it.

## L3, "Search for neutral Higgs boson production through the process e+ e- -> Z* H0",
## Phys. Lett. B 385 (1996) 454 (CERN-PPE/96-095)

- **Recoil cut in the high-mass mu+ mu- H0 selection: no.** The cut list of section 5.1 has no
  recoil, missing-mass or Higgs-mass requirement. "Recoil" appears only in the background
  sentence.
- Background sentence: "the background expected from e+e- -> mu+mu- q qbar is 0.65 +- 0.11 events
  for a recoil mass greater than 30 GeV; other sources of background give negligible
  contributions". The mass range refers to the background quote only.
- mu mu H0 efficiency (Table 2): 37.0 % (m_H = 30 GeV), 37.1 % (40), 36.1 % (50), 32.3 % (60).
  Cross-check: the 3.3 % efficiency at 70 GeV matches the 0.006 expected events in Table 6.
- Limit: no mass window stated. Zero mu mu events were selected, and "a 95% C.L. limit is set at
  a mass value where the number of expected events is 3".
## OPAL, "Search for neutral Higgs bosons in Z0 decays using the OPAL detector at LEP",
## Z. Phys. C 73 (1997) 189 (CERN-PPE/96-118)

- Recoil-mass cut value: **not stated**. Quote: "The cut on the hadronic mass, at 25 GeV, ... is
  replaced by a cut using the recoil mass (i.e. the mass of the hadronic system computed as the
  mass recoiling against the lepton pair), which has a mass resolution of 1 GeV."
- Also quoted at the end of the agent's notes, in what reads as the OPAL part (for Higgs masses
  "larger than 50 GeV"): "the residual background after all selection cuts is 0.17 +- 0.02 events
  in the e+e- channel and 0.21 +- 0.03 events in the mu+mu- channel" (a background quote, not a
  cut), and the mu mu candidate "has a recoil mass of 61.2 +- 1.0 GeV", the candidate already in
  lephz.py.
- lephz.py's stand-in (recoil > 25 GeV, variant 40 GeV) is consistent with this reading. OPAL 1997
  stays out of the headline combinations.

## Effect

NOTE-higgs-searches.md 0.5, section 5 item 4: the selection as coded for L3 (no recoil cut) is the
paper's; the stacked case with a hypothetical recoil > 30 GeV cut (p = 8e-5) is withdrawn and the
most pessimistic combination is p = 1.5e-6 (scalar).
