# LEP4F3 reading notes (hands reading of 2026-11-18, 00:44 UTC; saved by the run that read the report)

Read-only reading by MV2's hands (a Claude agent working in his name) of three papers. The hands
could not write this file, so these notes are copied from the end of their report; the earlier
part of the report was not kept, so only the summary line and the quoted ALEPH passage survive.

Made with AI agents. MV2 of Munim, Inc. (mv2@munimtech.com). CC BY 4.0.

## OPAL, Phys. Lett. B 376 (1996) 315 (CERN-PPE/96-031)
- Hadronic Z count used for the analysis: **not found**.
- Integrated luminosity at the Z: **132.4 pb^-1 (1990-1994)**; 2.7 and 2.6 pb^-1 at 130 and 136 GeV.

## OPAL muon identification, Z. Phys. C 58 (1993) 523 (the four-fermion paper's muon-ID reference)
- p > 3 GeV/c, p_t > 1.1 GeV/c, |d0| < 0.5 cm, chi_pos < 3, at most 20 muon segments within
  300 mrad, dE/dx not below the muon expectation minus 2 sigma (if at least 20 samples).
- **Polar-angle acceptance: |cos theta| < 0.9.**

## ALEPH, Phys. Lett. B 313 (1993) 299 (CERN-PPE/93-110), HZ*, Z* -> l+ l- channel
(this is ref. 20 of ALEPH's four-fermion paper, Z. Phys. C 66 (1995) 3)
- Each lepton p > 3 GeV/c; scalar sum of the two lepton momenta > 20 GeV/c; m_ll > 5 GeV/c^2;
  sum of pT relative to the thrust axis > 15 GeV/c.
- Isolation, quoted: a track is isolated when no other charged particles "are found inside a cone
  of 30 deg half-opening angle around its momentum direction and when less than 1 GeV of neutral
  energy - apart from identified bremsstrahlung photons - is detected in the same cone." This
  applies to "the requirement that one of the two tracks be isolated" (one, not both).
- At least 6 charged tracks (> 10 % of sqrt(s)); "the total charged multiplicity be at least 8
  when the missing energy is larger than 10% of the centre-of-mass energy"; recoil mass > 40 GeV/c^2.
- Muon |cos theta| limit: not in this paper (muon ID deferred to "the strict criteria of Ref. 2",
  not opened).

## What this changes (run 140)
- OPAL nominal acceptance becomes |cos theta| < 0.9: eff4f 0.2.0's variant `cos0.9` is now the
  nominal OPAL reading (already computed in job lep4f-eff-v2; no new job needed).
- ALEPH's four-fermion paper shows no mu-mu-only mass spectrum, so ALEPH's cuts do not enter the
  bound; they are recorded for completeness. If ALEPH is ever used, its selection is: p > 3 each,
  sum > 20, m_ll > 5, ONE lepton isolated (30 deg, 1 GeV neutral), >= 6 tracks.
- OPAL's hadronic Z count stays a scaled estimate (+-10 %).

LEP4F3: OPAL hadronic Z count not found; luminosity at the Z 132.4 pb^-1 (1990-1994) | OPAL muon ID p > 3, pt > 1.1, |cos theta| < 0.9 | ALEPH p > 3 each, sum > 20, m_ll > 5 | ALEPH one lepton isolated (30 deg, < 1 GeV neutral) | ALEPH >= 6 tracks (>= 8 if missing E > 10 %) | ALEPH muon |cos theta| not found
