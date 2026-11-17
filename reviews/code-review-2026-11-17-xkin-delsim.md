# Code review: `xkin/xme.py` and `delsim/sigana.py` (2026-11-17, 15:10-15:40 UTC)

MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; no human
physicist has checked this review. Text CC BY 4.0, code Apache-2.0.

These two modules had tests that ran in the repository's commit gate, but nobody had traced
their physics or their tests by hand. This review does that, before either job (`xkin-v1`,
`delsim-signal-v1`) has returned. No DELPHI data were involved.

## `xkin/xme.py` (0.1.0 -> 0.2.0)

**Checked and found correct**
- Amplitude for X emitted off the b line: Gamma = X (p1+k)/D1 Zv - Zv (p2+k)/D2 X, with the
  antiquark propagator sign; Z current vbar(e+) gamma^mu (v_e - a_e g5) u(e-) contracted with the
  quark vertex (the k^mu k^nu part of the Z propagator vanishes for massless electrons).
- V model: X polarisation sum replaced by the muon current ubar(mu-) gamma^nu v(mu+), so the
  X -> mu mu decay matrix element is already in the weight; the k^mu k^nu part of the X
  propagator vanishes (conserved current, tested by the Ward-identity test).
- Phase space: for fixed X mass, flat in (E1, E2) inside the Dalitz region; sampling E1, E2
  uniform on [0, Emax] with Emax = (s - m^2)/(2 sqrt s) needs the weight factor Emax^2, which is
  applied. The X propagator is supplied exactly by Breit-Wigner sampling of m^2. Two-body
  massless decay phase space is mass independent. Random rotations are Haar-uniform
  (normalised Gaussian quaternions); the boost formula is the standard one.
- LHE output: mother indices, colour lines and the `<init>`/event headers follow the Les Houches
  format; Pythia 8 restores lepton and b masses on reading.
- The tests (Clifford algebra, spinor completeness, Ward identity, Ellis-Ross-Terrano massless
  limit for vector and axial couplings, Lorentz invariance, momentum conservation, LHE sums)
  are real physics checks, not tautologies.

**Two missing factors (fixed in 0.2.0)**
1. **S model**: a scalar phi -> mu+ mu- has spin-summed decay factor
   sum |ubar(q1) v(q2)|^2 = Tr(q1-slash q2-slash) = 4 q1.q2 = 2 m^2. 0.1.0 used a scalar vertex on
   the b line but no decay factor, so its generated lineshape lacked a factor m^2 (about +-12 %
   across +-Gamma around 30.4 GeV). V never had this problem: its muon current carries the
   decay.
2. **P model**: Z -> h A with two spin-0 states is a P-wave: |M|^2 ~ p*^2 and two-body phase
   space ~ p*, so the rate goes as p*^3. 0.1.0 accepted events with probability p*/p*max only.
   Across 22-40 GeV, p* falls from 37.2 to 28.8 GeV, so the missing p*^2 tilts the h lineshape
   by about -2.8 % per GeV (about -0.13 GeV in the mean mass).

Both factors only reshape the generated m_mumu distribution. At fixed mass the angular
kinematics are unchanged, so the xkin expectations E1-E3 (muon-jet angles in the 26-35 GeV
window) are not materially affected. Model V, which is what `delsim-signal-v1` simulates, is
unaffected.

**New tests** (`xkin/test_xkin.py`): the scalar spin sum computed from explicit spinors equals
2 m^2 for random boosted decays; the S weight equals the emission part times that factor; the
P acceptance is cubic and p* at m_h = m_A matches sqrt(s/4 - m^2); and a 20,000-event check that
the generated P mean mass agrees, within 4 standard errors, with the numerical mean of
Breit-Wigner x p*^3 over 22-40 GeV.

**Effect on the queued job.** `xkin-v1` was filed with its own copy of 0.1.0 and will run that
copy. Its V results are exact; its S and P mass lineshapes carry the tilts above. Its angle
results will be reported as they come, with this caveat; a rerun with 0.2.0 is only needed if
any S or P number lands close to an E1-E3 threshold.

## `delsim/sigana.py` (0.1.0, no change)

Every test was traced by hand and passes: truth muons are found through final-state-radiation
copies back to the X; FADGEN round trip; 'E' (7 integers + 17 reals) and 'P' (11 + 10) line
parsing; standard muon tag = bit 2 of KMUID(1); charge-aware matching within 1 degree and 25 %
in momentum; forward-only alignment that skips a dropped event (in the test, events from the
neighbouring generated event are 1.4 and 3.4 degrees away, so they cannot be mismatched);
selection counts and the b-tag working-point count.

One known limitation, recorded rather than fixed (its size is far below the job's statistical
error): an event is aligned only if at least one of its signal muons is matched, so events in
which both muons were lost leave the denominator of the per-muon tracking efficiency. With
per-track efficiency near 99 % in acceptance this biases `eff_track` up by about 1e-4. The
event-level efficiencies, which use the number of simulated events as denominator, are not
affected.
