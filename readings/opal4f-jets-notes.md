# OPAL PLB 376 (1996) 315: the l+l- q qbar selection, jet finding (blind reading, 2026-11-19)

Paper: OPAL Collaboration, "A Study of Four-Fermion Final States with High Multiplicity at LEP",
Phys. Lett. B 376 (1996) 315, CERN-PPE/96-031. Read from the scanned preprint on INSPIRE by an AI
reading agent working for MV2 of Munim, Inc., blind to this repository (it was told not to look at
any of MV2's notes or results). Completed 2026-11-19 09:30 UTC. Text CC BY 4.0.

What was asked: which particles OPAL clustered into jets for the l+l- q qbar channel (leptons
included or removed), the jet algorithm, y_cut and normalisation, the jet-count requirement, and
the other cuts, quoted word for word with page numbers. Below is the agent's one-line summary as
returned (quotes are the paper's words), then the comparison with `analysis/eff4f.py` 0.2.0.

## Reading (agent's summary line, verbatim)

| item | reading |
|---|---|
| jet algorithm | Durham (k_T), ref [17] Brown & Stirling Z. Phys. C 53 (1992) 629 |
| y_cut | not stated |
| y normalisation | not stated |
| particles clustered | leptons included: "Charged tracks and electromagnetic clusters not associated to any track are formed into jets" + "one or two 'jets' originating from the leptons" |
| jet-count requirement | "The number of jets per event has to be greater than or equal to two" |
| applies to | whole event (preselection) |
| multiplicity | N_trk >= 8 at m_Z, >= 6 at 130-136 GeV, "per event" (lepton tracks count) + >= 2 hadronic-system tracks with P(dE/dx electron) < 1 %; cluster count not stated |
| isolation | alpha_iso = largest cone half-angle with E_cone < 1 GeV (tracks + unassociated EM clusters, excluding the lepton and the nearest other lepton); final alpha1 >= 30 deg, alpha2 >= 10 deg; alpha > 20 deg for one lepton at m_Z |
| muon cuts | p >= 5 GeV/c each, abs(p1) + abs(p2) >= 15 GeV/c; muon polar-angle cut not stated |
| mass cuts | "no mass cuts are applied to the hadronic system"; no mu mu mass cut stated; ee transverse mass > 1 GeV (electron channel only) |
| quoted efficiency | mu mu q qbar (4.1 +- 0.2) % at the Z, (18.5 +- 1.2) % at 130-136 GeV, from FERMISV + OPAL detector simulation |
| pages | pp. 5-8 printed (PDF 6-9), ref p. 12, Table 3 p. 14 |

## Comparison with eff4f 0.2.0 (the code behind kly4f-v1 and lep4f-eff-v2)

| item | OPAL (this reading) | eff4f 0.2.0 | match |
|---|---|---|---|
| jet inputs | charged tracks + EM clusters not associated to a track; leptons included | `em_or_track`: every visible particle except neutrinos, neutrons and K_L; muons included | yes |
| jet algorithm | Durham | Durham, E-scheme | yes |
| jet count | >= 2 per event | >= 2 per event | yes |
| y_cut, normalisation | not stated | 0.02 nominal, 0.005 variant; y over the summed input energy | stand-in; both give the same result (no signal event has < 2 jets) |
| tracks | >= 8 per event, lepton tracks count | `n_charged` >= 8 (p > 0.2 GeV, abs(cos theta) < 0.95), muons counted | yes |
| electron-veto tracks | >= 2 hadronic-system tracks with P(dE/dx electron) < 1 % | not modelled | see note 2 |
| isolation | largest cone with < 1 GeV, tracks + unassociated EM clusters, lepton and nearest other lepton excluded; alpha1 >= 30, alpha2 >= 10 deg | same definition (`iso_angle_energy`, partner excluded), 30 / 10 deg; variant both >= 30 deg | yes |
| momenta | p >= 5 each, sum >= 15 GeV | same | yes |
| polar angle | not stated | abs(cos theta) < 0.95; variants 0.9, 0.98 | stand-in, bracketed |
| mass cuts | none on the hadronic system; none on mu mu | none | yes |

Notes.
1. **Decision rule of NOTE-higgs-searches 0.7 section 6c: case (a).** OPAL formed jets from all
   tracks and clusters, the leptons included (the paper itself expects "one or two 'jets'
   originating from the leptons"). So eff4f's nominal selection is OPAL's, and the hadrons-only
   variants of job kly4fj-v1 are not OPAL's selection; they become a sensitivity check.
2. The electron-veto requirement asks for at least two tracks in the hadronic system that do not
   look like electrons (it removes photon conversions). Every signal model here has a b bbar
   hadronic system, whose charged multiplicity is far above two, so we expect it to remove almost no
   signal events; this was not computed.
3. The quoted 4.1 % efficiency is for OPAL's generated four-fermion sample (FERMISV, fermions more
   than 5 deg from the beam), which is dominated by low-mass, soft lepton pairs that fail the
   p >= 5 GeV cuts. It is not comparable with the efficiency for a 30 GeV boson and is not used.
4. "alpha > 20 deg for one lepton at m_Z" is weaker than the final alpha1 >= 30 deg and so has no
   effect on events that pass the final cuts.
