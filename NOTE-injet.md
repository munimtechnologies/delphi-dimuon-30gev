# NOTE-injet: what the "in-jet" reading of the ALEPH 30 GeV excess can still be

Version 0.2, 2026-11-19 (0.1 the same day; 0.2 adds section 7, the graded blind figure reading).
MV2 of Munim, Inc. (mv2@munimtech.com). Made with AI agents working in MV2's name; **no physicist
has checked it yet**. Licence: text CC BY 4.0, code Apache-2.0.
Code: [analysis/injet.py](analysis/injet.py) (pure Python), tests
[analysis/test_injet.py](analysis/test_injet.py), numbers
[analysis/results/injet/injet-bounds.json](analysis/results/injet/injet-bounds.json); figure reading
[readings/aleph-figs-notes.md](readings/aleph-figs-notes.md).

## 1. Why this note

Our LEP1 results (NOTE-fourfermion, NOTE-higgs-searches, paper draft 0.8) exclude every boson
model we tested whose muons are mostly isolated. ALEPH itself (Heister, arXiv:1610.06536 v9,
sec. 4.2) reports that "in all cases one of the two muons from di-muons is closer than 15 degrees to
one of the leading jets", that the other muon-jet angle "is typically in the range of 5 to 20
degrees", and that "each of the two muons which form the excess around 30 GeV are also close to one
of the leading jets" (jets: anti-kt, leptons removed from the inputs). Our README and draft listed
three "in-jet" readings that would survive: cascade decays, a mismodelled background shape, or a
new state decaying within a jet. This note tests those three with kinematics and with ALEPH's own
background method, before any DELPHI data are looked at.

## 2. Result 1: two muons near one jet cannot make a 30 GeV pair at LEP1

**Statement.** In an e+e- event with total energy sqrt(s), if two massless particles both lie
within an angle alpha (alpha <= 90 degrees) of one common axis, their invariant mass obeys

    m <= sqrt(s) * tan(alpha / 2).

**Proof.** Let E1, E2 be the energies and n the axis. Each momentum has a component along n of at
least E_i cos(alpha), so the pair's total momentum has length at least (E1 + E2) cos(alpha). The
rest of the event (hadrons, neutrinos, initial-state photons) must balance it, and its energy is at
least the length of its momentum. Energies add to sqrt(s), so (E1 + E2)(1 + cos alpha) <= sqrt(s).
The opening angle is at most 2 alpha, and E1 E2 <= (E1 + E2)^2 / 4, so
m^2 = 2 E1 E2 (1 - cos theta) <= (E1 + E2)^2 sin^2(alpha) <= s sin^2(alpha) / (1 + cos alpha)^2
= s tan^2(alpha / 2). The bound is reached by a symmetric pair on the cone edge with the rest of
the event a single massless system opposite (test `test_bound_is_reached`). The muon mass changes
it by less than 0.01 GeV for muons above 2.5 GeV. Initial-state radiation only lowers the energy
available, and LEP1 never ran above 94.3 GeV, which we use as the conservative case.

**Numbers** (`injet-bounds.json`; Z pole 91.19 GeV / highest LEP1 energy 94.3 GeV):

| both muons within | largest pair mass (GeV) |
|---|---|
| 15 deg of one axis | 12.0 / 12.4 |
| 20 deg | 16.1 / 16.6 |
| 25 deg | 20.2 / 20.9 |
| 30 deg | 24.4 / 25.3 |

A 30.4 GeV pair needs a cone of at least 36.9 deg (35.7 deg at 94.3 GeV) to hold both muons, and
its two muons are at least 73.7 deg (71.5 deg) apart. A 28 GeV pair needs at least 33.1 deg.

**Consequence.** ALEPH's description ("each of the two muons ... close to one of the leading jets",
5-20 deg) can only be met with the two muons next to **two different jets**: a pair of muons within
20 deg of the same jet has a mass of at most 16.6 GeV, whatever produced it. So **no new state that
decays within one jet can make the excess**, and that reading is removed from our list. A state of
30 GeV produced with b quarks puts its muons near two different b jets only by accident, which is
what our boson models do in 4-11 % of events (NOTE-kinematics, kly-v1); NOTE-kinematics already
bounds that case to at most about 4-10 of ALEPH's 32 events (95 % CL).

## 3. Result 2: ALEPH's background is its own electron-muon data

Heister's background model is not a simulation. It is the opposite-sign electron-muon mass
spectrum of the same ALEPH data, after the same selection, smoothed by a kernel density estimate
and scaled for the factor two in pair counting and an electron efficiency "about 6% less" than the
muon one (sec. 3 of the paper). Above 25 GeV, ALEPH's simulation finds only semileptonic
b b-bar decays in the opposite-sign dimuon spectrum, and those make e mu pairs exactly as they make
mu mu pairs.

So every **lepton-universal** mechanism in b b-bar events (b fragmentation, the semileptonic lepton
spectrum, b -> c -> lepton cascades, gluon splitting to b b-bar, B mixing) enters the signal sample
and the background template in the same proportion and cancels in the excess, to first order.
"Cascade decays" and "a mismodelled background shape" are therefore not readings of the excess as
ALEPH measured it, unless the mechanism treats muons and electrons differently. ALEPH also
reports the excess against its full simulation (its Fig. 21a: "the excess around 30 GeV is clearly
visible") and no excess in same-sign pairs or with the b-tag inverted.

What is left, with the in-jet description and the isolated-muon exclusions together:

1. **A statistical fluctuation** in the mu mu sample or in the e mu template. ALEPH notes "a small
   downwards fluctuation around 28 GeV" in the e mu data against simulation; the default
   significance (Z_asym = 5.35) treats the smoothed template as exact, while Z_Bi (2.63, with
   tau = 1) does not. This is also Lane and Pritchett's conclusion (arXiv:1701.07376).
   (Section 7: the blind reading finds no e mu deficit inside 29-32 GeV, so the template part of
   this reading is now limited to the 28-29 GeV bin next to the window.)
2. **A muon-specific detector effect** that is localised in mass (fake muons from punch-through or
   decays in flight sit inside jets, but their rates are smooth in momentum, and we know of no
   mechanism that would localise them at 30 GeV).
3. **A new state coupling to muons but not electrons, whose muons happen to accompany two different
   b jets.** This is the boson case at 4-11 % in-jet, already bounded (sec. 2). ALEPH's e e excess
   (8.0 +- 4.5 events at 29.2 GeV) argues against a muon-only state but is itself only 1.5 sigma.

## 4. Result 3: L3's 2019 cross-check could not have seen an ALEPH-sized signal

Hebbeker and Roth (arXiv:1905.01111) repeated the analysis on L3's 1994-95 b-tagged data: 227
opposite-sign events, 170 of them in 5-50 GeV, data minus simulation 6.4 +- 7.4 events in 29-32 GeV
and 8.4 +- 8.6 in 27-34 GeV (statistical only), "about one standard deviation". They note that the
detectors differ, so "we can not make a direct comparison".

If a signal is produced and accepted in proportion to the semileptonic b b-bar background (true
for any b-associated effect with ALEPH-like muon acceptance), the expected signal scales with the
background sample. ALEPH fits 32.31 signal on 1457.06 background events in 15-50 GeV, a ratio of
0.0222, and L3 has at most 170 events in that range, so **L3 expects at most 3.8 signal events**
(5.7 if L3's relative acceptance for the signal were 1.5 times ALEPH's). Against L3's statistical
uncertainty of 7.4 events, that is a 0.5 sigma (0.8 sigma) expected effect. L3's result is
consistent with both no signal (0.9 sigma) and an ALEPH-sized one (0.4 sigma), so it neither
confirms nor refutes ALEPH. The decisive cross-check is still a larger sample with the same e mu
frame, which DELPHI's open data can provide (sec. 5).

## 5. Pre-registered for plan v1.0 and for a blind reading (written before either exists)

**For plan v1.0 (DELPHI).**
- **A' (new primary frame).** Besides test A (degree-3 log-Legendre background, amendment 0.18),
  plan v1.0 must also fit the DELPHI b-tagged opposite-sign mu mu spectrum against DELPHI's own
  opposite-sign e mu spectrum, scaled by the pair-count factor 2 and the DELPHI e/mu efficiency
  ratio measured on the 15-26 and 35-50 GeV sidebands, with the template's own Poisson
  uncertainty propagated. This is ALEPH's frame, so a confirmation or exclusion in it cannot be
  blamed on a different background method.
- **I1.** In DELPHI events in 26-35 GeV, the fraction of opposite-sign pairs with both muons within
  20 deg of the same jet (leptons removed from the jet inputs) is 0 in data and simulation; any
  such pair is a reconstruction or code error and is investigated before unblinding the mass.

**For the blind figure reading (hands goal ALEPHFIG, filed this run).** From Heister's
Fig. 21(a) (opposite-sign mu mu, data against ALEPH simulation) and Fig. 3 (e mu, data against
simulation, both normalised to the opposite-sign mu mu yield), read bin by bin from 24 to 36 GeV:
- **R1.** mu mu data minus simulation, summed over the bins covering 29-32 GeV, is at least 16
  events (half of the fitted 32.3). Expectation: PASS (ALEPH calls the excess "clearly visible"
  against simulation).
- **R2.** e mu data minus simulation, in the same normalisation and bins, is above -16 events, i.e.
  a dip in the template accounts for less than half of the excess. Expectation: PASS.
- **Decision.** R1 and R2 PASS: the excess sits in the mu mu data itself; the template-fluctuation
  reading is closed and only a mu mu fluctuation, a muon-specific effect or a muon-coupled state
  remain. R1 FAIL or R2 FAIL: a large part of the excess is a deficit in the e mu control, which
  we will report, and A' must be the primary DELPHI test. If the figures cannot be read to
  +-5 events per bin, both are recorded as NOT GRADABLE.

## 6. Limits

The bound in sec. 2 is exact kinematics and assumes only energy-momentum conservation. Secs. 3-4
rely on Heister's and Hebbeker and Roth's text as read by AI agents from arXiv HTML; the L3 scaling
assumes that the signal-to-background acceptance ratio is similar in the two detectors (a factor
1.5 is shown). The figure readings of sec. 5 are graded in sec. 7; they were made by eye from the
published figures. None of this is a result of the ALEPH, DELPHI, L3 or OPAL Collaborations.

## 7. The blind figure reading, graded (added in version 0.2)

The reading was made on 2026-11-19 by an AI reading agent with no access to this repository,
from the arXiv HTML of v9 ([readings/aleph-figs-notes.md](readings/aleph-figs-notes.md)). Figures as
numbered in the HTML: E = Fig. 3 (e mu data and simulation, both normalised to the opposite-sign
mu mu data yield), M = Fig. 21(a) (opposite-sign mu mu data against ALEPH simulation, logarithmic
y axis; the paper's text calls it Fig. 20(a)), K = Fig. 5 (mu mu data against the binned e mu data
used as background). All three have 1 GeV bins. The reader's stated uncertainty is 0.3-0.5 events
per bin, so about +-1 to 1.5 events on a three-bin sum. Bins summed: 29-30, 30-31 and 31-32 GeV.

| figure | summed over 29-32 GeV | value (events) |
|---|---|---|
| M | mu mu data minus ALEPH simulation | **+15.8** |
| E | e mu data minus simulation (same normalisation) | **+1.5** |
| K | mu mu data minus binned e mu data (ALEPH's background) | +17.8 (information) |

**Grades.**
- **R1: FAIL as written.** +15.8 is below the threshold of 16 by 0.2 events, less than the reading
  uncertainty. The threshold is not moved; R1 is recorded as failed.
- **R2: PASS.** +1.5 is far above -16; in the signal window the e mu control agrees with simulation.

**Decision, as pre-registered.** Because R1 failed, A' becomes the primary DELPHI test in plan
v1.0. The explanation the plan attached to a failure ("a large part of the excess is a deficit in
the e mu control") is **not** what the reading shows, and we say so: R2 finds no deficit in the
window. R1 fails because the threshold, half of the fitted 32.3 events, did not allow for the part
of the fitted signal that falls outside 29-32 GeV (ALEPH fits a natural width of 1.78 GeV on top of a
0.74 GeV resolution). Read plainly, the excess is in the mu mu data itself, against ALEPH's
simulation (+15.8) and against its e mu background (+17.8), and it is not made by a dip in the e mu
template inside the signal window.

**What else the reading shows.** In E, the e mu data have a one-bin dip at 28-29 GeV (about 3.5
events against 8.2 simulated), no bump at 30 GeV, and an excess at 24-25 GeV. This matches ALEPH's
text ("a small downwards fluctuation around 28 GeV", "deviation around 24 GeV"). In M, the mu mu
bump is at 29-31 GeV (about 12 and 14 events against about 8 and 5 simulated). The number of e mu
pairs is not stated in the paper.

**What it changes in sec. 3.** Reading 1 (statistical fluctuation) narrows: a fluctuation of the
e mu template inside the signal window is not supported. A smoothed template can still carry the
28-29 GeV dip some way into the window, which only a fit with the template's own Poisson errors
can size; that is test A'. A fluctuation of the mu mu sample itself, a muon-specific detector
effect and a muon-coupled state with muons near two different jets remain.

**Limits of the reading.** Values were read by eye from published figures by one reader; only the
summary values and quoted sentences are preserved (the per-bin table was not kept in full). The
16-event threshold and the decision rule were written before the reading and are graded as written.
