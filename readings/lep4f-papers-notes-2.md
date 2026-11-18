LEP four-fermion papers: notes (second, independent reading)
Read 2026-11-17 by MV2's hands on the Dell, in a separate Chrome window.
Sources:
  OPAL: INSPIRE 418010 -> INSPIRE "pdf" link (ppe-96-031.pdf = CERN-PPE/96-031, March 7, 1996,
        "A Study of Four-Fermion Final States with High Multiplicity at LEP", The OPAL Collaboration;
        published Phys. Lett. B 376 (1996) 315-328).
  ALEPH: INSPIRE 380424 -> "CERN Document Server" -> repository.cern/records/9x1qz-dvw22 fulltext
        (CERN PPE/94-169, 27 October 1994, "Study of the four-fermion final state at the Z resonance",
        Z. Phys. C 66 (1995) 3).
Quotes are copied word for word. The math is written as plain text: alpha^iso = isolation angle,
alpha_1^iso / alpha_2^iso = the subscripted versions, sqrt(s) = centre-of-mass energy, ~ = approximately equal.

======================================================================
1. OPAL, CERN-PPE/96-031 (Phys. Lett. B 376 (1996) 315)
======================================================================

(a) Lepton isolation angle: definition and cut values
  Section 4 "Selection criteria", preselection bullet (preprint p. 6):
  "For each lepton candidate an isolation angle alpha^iso is defined as the maximum angle at which the
   energy E_cone contained within a cone of half-angle alpha^iso around the lepton is less than 1 GeV. In
   order to keep events with low-mass lepton pairs, E_cone is defined to be the energy of all tracks
   and unassociated electromagnetic clusters within the cone, excluding both the lepton candidate
   itself, and also the nearest other lepton candidate if it lies within the cone."
  "The two most isolated leptons of each flavor are regarded as a candidate lepton pair. An event
   passes the preselection for e+e-qqbar or mu+mu-qqbar, if a candidate lepton pair of the respective flavor
   is found. If the charges of the leptons are of the same sign, the event is rejected. Their momenta
   and isolation angles are called p_i, i = 1,2, and alpha_i^iso, respectively, where i = 1 designates the
   lepton having the larger isolation angle. In the analysis at sqrt(s) ~ m_Z we furthermore require
   at least one lepton with an isolation angle alpha^iso greater than 20 deg to reduce the huge number of
   multihadronic events passing the criteria described above."
  Final selection (p. 6):
  "For the final selection we exploit the isolation of the signal leptons mentioned above, and further reject
   non-leptonic low momentum background by requiring
        alpha_1^iso >= 30 deg,  alpha_2^iso >= 10 deg and |p1| + |p2| >= 15 GeV/c."
  => Cuts: preselection at the Z, at least one lepton alpha^iso > 20 deg; final alpha_1^iso >= 30 deg and
     alpha_2^iso >= 10 deg. The cone energy threshold in the definition is 1 GeV.

(b) Lepton momentum cuts
  (p. 6) "In both cases lepton candidates are required to have a momentum p >= 5 GeV/c."
  (p. 6, final selection) "|p1| + |p2| >= 15 GeV/c."
  (p. 9, Discussion 7.1) "The lepton momenta cut |p1| + |p2| >= 15 GeV/c equivalent to
   m_recoil < sqrt(s) - 15 GeV completely removes contributions from diagram C."

(c) Charged-multiplicity / track / jet cuts ("high multiplicity")
  (p. 5) "At sqrt(s) ~ m_Z we require the number of charged tracks per event N_trk >= 8, where only tracks
   satisfying minimum quality criteria are considered. For the analysis at sqrt(s) = 130-136 GeV
   this requirement was loosened to N_trk >= 6, since the background fraction coming from dilepton
   events with multiple photon conversions is strongly reduced off the Z resonance."
  (p. 6) "The number of jets per event has to be greater than or equal to two. Charged tracks and
   electromagnetic clusters not associated to any track are formed into jets using the Durham
   algorithm [17]. Typically one or two 'jets' originating from the leptons and in addition one or
   two jets originating from the quarks are expected for signal events."
  (p. 6) "In order to reject the few remaining dilepton events with multiple photon conversions we fur-
   thermore require that at least two charged tracks in the remaining hadronic system of an event
   have an energy loss inconsistent with an electron; here, the probability of the measured dE/dx
   value being consistent with the energy loss of an electron inside the tracking chamber has to be
   less than 1%."
  There is no separate cut on the number of electromagnetic clusters.

(d) Muon identification and polar-angle acceptance
  (p. 6) "Leptons are identified differently for the analyses at sqrt(s) ~ m_Z and at sqrt(s) = 130-136 GeV. In
   both cases lepton candidates are required to have a momentum p >= 5 GeV/c. Since at the Z
   resonance the leptons are preferentially emitted close to the jets we employ a lepton identification
   optimized for b-tagging in a high-multiplicity environment. [...] Muons are identified as described in
   Ref. [19], mainly using the positional matching between the charged track extrapolation and the
   associated segment in the muon chambers. At sqrt(s) = 130-136 GeV the leptons are expected to be
   isolated from the hadronic jets and we can therefore afford to apply much looser identification
   criteria. [...] Muons are required to have E/p < 0.2 and at least three hits in the muon chambers or
   the last three layers of the hadronic calorimeter."
  (The E/p < 0.2 / three-hit criterion is for the 130-136 GeV analysis; at the Z pole muon ID follows Ref. [19].)
  Ref. [19] = "OPAL Collaboration, P.D. Acton et al., Z. Phys. C58 (1993) 523."
  Polar-angle acceptance: THE PAPER STATES NO |cos theta| LIMIT for muons (or any lepton). I searched the
  whole text. The only "cos" quantity is |cos theta_ll| of the lepton momentum SUM (Table 3, Fig. 4e,
  130-136 GeV events), which is not a cut. The only angular statements are:
   (p. 3) "It has a geometrical tracking acceptance of 98% of 4pi steradians."
   (p. 4, MC generation) "The momentum direction of each fermion was required to be more than 5 deg away
   from the beam axis." (generator level, not a muon-ID cut)
  Any |cos theta| acceptance would come from Ref. [19], which this paper does not quote.

(e) Figure with the dilepton (mu mu) invariant mass at the Z pole
  Figure 3, panel (b) (preprint p. 17). Caption, word for word:
  "Figure 3: Leptonic invariant masses (a,b) and recoil masses (c,d) of the e+e- -> e+e-qqbar (a,c) and
   mu+mu-qqbar (b,d) channel for the final event selection at sqrt(s) ~ m_Z. Crosses are the data, the open
   histogram is the FERMISV prediction, and the hatched region is JETSET background. The dashed
   histogram shows the FERMISV prediction without the higher order corrections."
  After ALL cuts? YES ("for the final event selection").
  Data points read from Fig. 3b (10 GeV bins, x axis "Leptonic Mass (GeV)", 0-100), from a zoomed render:
     0-10: 19 | 10-20: 3 | 20-30: 1 | 30-40: 0 (no point) | 40-50: 1 | 50-60: 1 | 60-70: 2 | 70-80: 1 | 80-100: 0
     Sum = 28, which matches the text "we find 28 in the mu+mu-qqbar final state" and Table 2 (observed 28).
  => 20-30 GeV: 1 event; 30-40 GeV: 0 events; above 40 GeV: 5 events.
  Event table: there is NO event-by-event table for the Z-pole events. Table 3 lists only the 130-136 GeV events
   after all cuts; its mu+mu-qqbar m_ll values are 86.6+-4.2, 4.1+-0.1, 2.3+-0.1 (130 GeV) and 0.4+-0.1, 3.5+-0.1 (136 GeV).
  Figure 2 (recoil mass and alpha_1^iso) is "after preselection", not after all cuts, and is l+l-qqbar combined.
  Table 2, Z pole final selection, mu+mu-qqbar: signal 20.0 +1.1/-1.1 +- 1.7; (gamma)ffbar 8.2 +2.1/-2.1 +- 1.1;
   total expected 28.2 +2.4/-2.4 +- 2.0; observed 28. Efficiency for mu+mu-qqbar at the Z: (4.1 +- 0.2)%.

======================================================================
2. ALEPH, CERN PPE/94-169 (Z. Phys. C 66 (1995) 3)
======================================================================

(a) Lepton momentum and isolation cuts for l+l-qqbar
  Section 4 "The l+l-qqbar final state" (preprint pp. 20-21):
  "To study the continuum, for hadronic masses up to 70 GeV/c^2, another analysis is
   used which was developed initially for the Higgs boson search in the e+e- -> HZ* ->
   hadrons l+l- process [20]. This search essentially consists of selecting events with at least
   six good charged particle tracks, of which two are energetic, isolated, identified electrons
   or muons. No events are selected in either of the hadronic Z decay Monte Carlo samples
   enriched in bbbar events of Section 2.2, equivalent to more than seven million Z decays,
   corresponding to 0.0 +0.4/-0.0 background events expected in the data."
  This paper gives NO NUMERICAL LEPTON MOMENTUM CUT; it refers to Ref. [20].
  Ref. [20], word for word: "D. Buskulic et al., (ALEPH Coll.), Phys. Lett. 313B (1993), 299."
  Isolation: the only explicit number is in the Fig. 11 caption (p. 21):
  "Figure 11: Distributions of the photon isolation angle, for the ALEPH data (triangles with
   error bars), and for the Monte Carlo (shaded histogram, with an absolute normalization).
   The isolation angle is defined as the angle of the largest cone around the photon direction
   containing less than 1 GeV of extra energy. The hatched part of the distribution is
   obtained from the genuine qqbar-gamma events. The cut at 30 degrees (applied to l+l-qqbar events
   too) is indicated by an arrow."
  Related (p. 22), for the PHOTON control sample, not a stated lepton cut: "The selection of these events is
   very close to the l+l-qqbar selection, the photon playing the role of the lepton pair. In particular, its
   energy is required to be greater than 15 GeV and its transverse momentum with respect to the thrust
   axis of the rest of the event has to exceed 10 GeV/c."
  Multiplicity: "at least six good charged particle tracks".

(b) Is the mu+mu- mass shown separately from e+e-?
  NO. Figure 13 (p. 23) shows only the combined l+l-qqbar:
  "Figure 13: Distributions of the hadronic (a) and the leptonic (b) masses in the l+l-qqbar
   final states, for the data (triangles with error bars) and for the Monte Carlo expectation
   (shaded histogram) with an absolute normalization."
  Combined (ee + mu mu) data in Fig. 13b, 10 GeV/c^2 bins: 0-10:1, 10-20:2, 20-30:2, 30-40:2, 40-50:2,
   50-60:3, 60-70:5, 70-80:6, 80-90:6 (sum 29 = total observed). These are NOT mu-mu-only counts.
  Text (p. 23): "To summarize, the number of events expected in this l+l-qqbar final state is 27.2 +- 1.7
   (syst.), of which 13.0 in the mu+mu-qqbar final state and 14.2 in the e+e-qqbar final state. A
   total of 29 events is observed, of which 19 mu+mu-qqbar and 10 e+e-qqbar events."
  No table lists mu mu masses. mu-mu-only counts in 20-30 / 30-40 / >40 GeV: none given.
  (Fig. 8a is the x+x- mass with x = mu in the l+l-x+x- two-prong analysis, not the l+l-qqbar continuum.)

======================================================================
SUMMARY
======================================================================
OPAL isolation: alpha^iso = maximum half-angle of a cone around the lepton with E_cone < 1 GeV (tracks + unassociated
 EM clusters, excluding the lepton and the nearest other lepton candidate). At the Z, preselection needs at least one
 lepton with alpha^iso > 20 deg; final cuts alpha_1^iso >= 30 deg, alpha_2^iso >= 10 deg.
OPAL momentum: each lepton p >= 5 GeV/c; |p1|+|p2| >= 15 GeV/c.
OPAL multiplicity: N_trk >= 8 at the Z (>= 6 at 130-136 GeV); >= 2 Durham jets; >= 2 hadronic-system tracks with
 electron dE/dx probability < 1%.
OPAL muon |cos theta|: not stated (muon ID per Ref. [19]; tracking acceptance 98% of 4pi).
OPAL Fig. 3b, after all cuts: yes. Data: 20-30 GeV 1, 30-40 GeV 0, >40 GeV 5 (of 28).
ALEPH momentum cut: no number in this paper, only "two are energetic, isolated, identified electrons or muons" per
 Ref. [20] = D. Buskulic et al. (ALEPH Coll.), Phys. Lett. 313B (1993) 299. Isolation cut 30 deg (1 GeV cone, Fig. 11).
ALEPH mu-mu-only mass counts: none (Fig. 13b combines e+e- and mu+mu-; 19 mu mu qqbar events in total).
