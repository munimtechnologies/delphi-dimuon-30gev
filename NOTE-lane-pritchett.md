# NOTE: the Lane-Pritchett model is the Z -> h A case already tested

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-18. Made with AI agents working in MV2's name;
not checked by a physicist. Text: CC BY 4.0. It closes an open caveat in NOTE-higgs-searches.md
(section "Prior art"), and will be folded into that note's next version.

NOTE-higgs-searches.md said: "Lane and Pritchett, arXiv:1701.07376, favour a two-Higgs-doublet
variant with h and eta_A nearly degenerate near 30 GeV; we have not read how they produce it at
LEP1, so we do not claim to cover it beyond its resemblance to our Z -> h A." We have now read the
paper (ar5iv HTML, 2026-11-18). Findings, with short quotes:

1. **Production is Z -> h eta_A only.** Their section 5 states: "Only option 1 with
   Z -> h eta_A -> b bbar mu+ mu- can explain the rate of the ALEPH dimuon". Higgsstrahlung in
   option 2 contributes "<~ 5 x 10^-10", so option 2 cannot explain the excess. They give
   B(Z -> h eta_A) = 0.0141 cos^2(beta - alpha).
2. **Masses and decays match our model P.** Option 1 has M_h = M_eta_A = 30 GeV. In their
   Table 2, h decays almost entirely to mu+ mu- (0.9991-0.9999), and eta_A to mu+ mu- (0.89-0.99)
   with a b bbar fraction of 0.0067-0.097. The ALEPH rate (2.77 x 10^-4) needs v_2 of about
   12.5 GeV. The signal is one 30 GeV boson decaying to two muons recoiling against a second
   30 GeV boson decaying to b bbar. That is our model P (`xkin/xme.py`, `generate_pair`, defaults
   M = 30.40 GeV, MA = 30.40 GeV, h -> mu mu, A -> b bbar). So the closures for P in
   NOTE-higgs-searches.md apply to the Lane-Pritchett model as published. There, L3's search keeps
   0.644 of P events and DELPHI's 0.816 (job lephz-v1). At the lowest literature rate, L3 and
   DELPHI predict 33.83 and 10.38 boson events per unit efficiency. That is about 22 and 8.5
   events, against 0 and 1 candidates. Their branching ratios are tuned to reproduce the ALEPH
   excess itself, so the closures at ALEPH's central rate, also tabulated there (e.g. L3 alone,
   126.8 events per unit efficiency), apply as well. We have not converted their B(Z -> b bbar mu mu)
   = 2.77 x 10^-4 into our acceptance convention.
3. **The authors already flag the model's own problems.** In the same section: B(Z -> h eta_A ->
   4 mu) is about 0.014, "3300 times larger than its measured value of 4.2 x 10^-6". They also
   note that "the 30 GeV excess is just a statistical fluctuation in semileptonic Z -> b bbar
   decays" is the simplest reading, and they ask whether there is a no-go theorem for
   scalar-based models. They also find that their model's muons "will not have a strong tendency
   to be close to the b-jets", unlike ALEPH's events ("We have no explanation for this
   difference").
4. **Nothing new to compute.** Their production process, masses and decay topology are already
   in model P. The muon-jet isolation (P: both muons isolated from the jets in most events) is the
   property the LEP1 four-fermion and Higgs-search closures rest on, and the authors find the same
   property themselves.

Consequence for the main claim: the statement that LEP1 measurements close every published boson
reading of the excess now covers the three NOTE-kinematics models, Ko, Li and Yu's models II and III
(job kly-v1; kly4f-v1 pending), and Lane and Pritchett's option 1 (= model P; option 2 cannot make
the rate, by their own numbers). We still say "every model we have read". Other boson
interpretations may exist that we have not found.
