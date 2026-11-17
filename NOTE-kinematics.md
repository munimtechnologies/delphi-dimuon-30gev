# Would a real boson look like ALEPH's 30 GeV excess? Result of the kinematic study (xkin-v1)

MV2 of Munim, Inc. (mv2@munimtech.com), 2026-11-17. Made with AI agents working in MV2's name.
Text CC BY 4.0, code Apache-2.0. This is not a DELPHI or ALEPH Collaboration result. No DELPHI
data were used; this is a generator-level study (PLAN section 4b).

## Summary

ALEPH's re-analysis (arXiv:1610.06536 v9, sec. 4.2, Fig. 16) reports that "in all cases one of
the two muons from di-muons is closer than 15 degrees to one of the leading jets", and that
"each of the two muons which form the excess around 30 GeV are also close to one of the leading
jets". We generated three explicit boson models at hadron level and computed the same angles
with ALEPH's jet definition (e+e- anti-kt jets built without leptons, leading jet per thrust
hemisphere):

| sample (p > 2.5 GeV cut, R = 0.4) | window events | leading jets defined | one muon within 15 deg | both muons > 20 deg from every jet > 3 GeV |
|---|---|---|---|---|
| V: vector radiated off the b line | 16062 | 76.0 % | **5.4 %** | 91.6 % |
| S: scalar radiated off the b line | 14860 | 54.2 % | **7.8 %** | 93.4 % |
| P: Z -> h A, h -> mu mu, A -> b bbar | 16708 | 40.2 % | **11.3 %** | 94.7 % |
| ordinary Z -> b bbar (Pythia 8) | 525 | 100 % | **99.4 %** | 0.0 % (0 of 525) |

Ordinary b bbar events reproduce ALEPH's description: 99.4 % have a muon within 15 degrees, and
the other muon-jet angle has median 11.5 degrees, 88 % of pairs between 5 and 20 degrees (ALEPH:
"typically in the range of 5 to 20 degrees"). The three boson models do the opposite: the median
second angle is about 90 degrees. The same holds for R = 0.7 and 1.0 and for a pT instead of a
p cut (all numbers in `xkin/results/xkin-v1-summary.json`). The cos theta* distribution agrees
too: 74 % of background window pairs have |cos theta*| > 0.8 (ALEPH: "the forward/backward
direction is preferred"), against 20-22 % for the models, which is what a flat distribution gives.

**What this means in numbers** (`xkin/bound.py`). If the 32.31 fitted events were boson events
of these types, about 23 (V), 16 (S) or 12 (P) of them would land in ALEPH's Fig. 16a with no
muon within 15 degrees of a leading jet. ALEPH reports none. Taking that at face value:

| model | 95 % CL upper limit on boson events (R = 0.4 / 0.7 / 1.0) | P(no such event), yield fixed at 32.31 | same, averaged over ALEPH's 32.31 +- 10.87 |
|---|---|---|---|
| V | 4.2 / 4.2 / 4.3 | 8e-11 | 9.6e-4 (3.1 sigma) |
| S | 6.0 / 6.2 / 6.4 | 1e-7 | 1.7e-3 (2.9 sigma) |
| P | 8.4 / 9.1 / 10.3 | 1e-5 | 3.3e-3 (2.7 sigma); R = 1.0: 5.3e-3 (2.6 sigma) |

Counting every window event against the nearest jet above 3 GeV (ALEPH's second sentence) instead
of Fig. 16a's subset gives a tighter limit of about 3.1-3.2 events for all three models.

So ALEPH's own kinematic description allows at most about 4-10 boson events of these types, not
32. Read the other way: the events that make up the excess look like ordinary semileptonic b
decays, not like a boson decaying to two muons.

## What is new and what is not

Ko, Li and Yu (arXiv:1610.07526, sec. V) already found, with **parton-level** MadGraph events
and b quarks standing in for jets, that the muon-b angles of their models peak at 50-70 degrees,
far from ALEPH's 15 degrees. Lane and Pritchett (arXiv:1701.07376) said the simplest explanation
is a statistical fluctuation in semileptonic Z -> b bbar decays. This note does not overturn
either. It adds:
1. hadron-level events (Pythia 8) analysed with **ALEPH's own jet definition** (anti-kt without
   leptons, leading jet per thrust hemisphere), at three jet radii;
2. a background sample that **reproduces ALEPH's quoted numbers** (99.4 % within 15 degrees;
   second angle mostly 5-20 degrees; forward/backward cos theta*), which shows the angles are
   computed the way ALEPH computed them;
3. exact tree-level matrix elements with full spin correlations for the vector and scalar
   models (PLAN 4b), and the Z -> h A topology;
4. a **quantitative limit** on how many of the fitted events such a boson can be, with code and
   tests (`xkin/bound.py`, `xkin/test_bound.py`).

## Limits of this reading (honest)

- Generator level: no ALEPH detector, energy-flow objects or b-tag. Angular resolution at LEP is
  about a degree, far below the 15-degree scale, but ALEPH notes that leading jets "tend to be
  broadened" at high dimuon mass, which we do not model.
- "In all cases" is read from ALEPH's text. We could not read the figure itself; if Fig. 16a
  shows a few events above 15 degrees, `bound.py --k-obs k` gives the looser limit (k = 1:
  limits x 1.58; k = 2: x 2.10).
- Fig. 16a uses events with a leading jet in both hemispheres; we require one in each muon's
  hemisphere. The nearest-jet reading, which covers all events, gives an even tighter limit.
- ALEPH's b-tag was applied to the events; we assume it does not select signal events by their
  muon-jet angles (the tag uses track impact parameters, and the boson's muons are prompt).
- The S and P samples come from xme 0.1.0, whose mass lineshapes were corrected in 0.2.0 (see
  `reviews/`); the angles do not depend on the lineshape.
- Three models are not all models. A boson whose muons sit inside b jets (for example one made
  in b-hadron decays) cannot reach 30 GeV; we know of no model that puts a 30 GeV dimuon
  resonance's muons within 15 degrees of the b jets.
- The yield-averaged p-values treat ALEPH's fit uncertainty as Gaussian; they are a rough guide.

## Pre-registered expectations (PLAN 4b), graded

| | expectation | result | grade |
|---|---|---|---|
| E1 | V, S, P: fewer than half of window events with alpha_min < 15 deg (R = 0.4) | 5.4 %, 7.8 %, 11.3 % | PASS |
| E2 | b bbar: more than 70 % with alpha_min < 15 deg | 99.4 % | PASS |
| E3 | V, S, P: at least 30 % with both muons > 20 deg from every jet > 3 GeV; background at most 10 % | 91.6 %, 93.4 %, 94.7 %; background 0 of 525 | PASS |

The job (`xkin-v1`, 2 CPU, 6 min, peak 0.18 GB) ran the 12 unit tests first (Ward identity,
Ellis-Ross-Terrano massless limit, Lorentz invariance, Dirac algebra, FADGEN round trip): all
passed. 100 FADGEN events per model were written and read back with no energy mismatch.

## What it changes for the DELPHI test

- Test A (replicate ALEPH's tagged spectrum) is still the direct test of the excess **as
  observed**: if the excess is a fluctuation or a b-decay modelling effect, DELPHI should not see
  it at the same rate.
- Test B (tagged + untagged, PLAN 5e) tests a b-associated boson at ALEPH's rate. This note says
  ALEPH's own angles already disfavour that reading of the excess; test B stays as registered
  and checks it with independent data.
- PLAN 4b's condition for a second, isolated-muon selection is met (E1-E3 pass). In it the
  b bbar background is tiny (0 of 525 window pairs at generator level), and 92-95 % of boson
  events pass, so DELPHI can search for a b-associated 30 GeV boson far more sensitively than
  an ALEPH replica. Before it is frozen in plan v1.0 it needs a background the inclusive Pythia
  sample does not contain: four-fermion e+e- -> q qbar mu+ mu- (a virtual photon radiated from the
  quarks), which gives genuinely isolated muon pairs. That estimate, the exact selection and its
  blinding go into plan v1.0, before any DELPHI mass is seen.

## Reproduce

```
cd xkin
python -m unittest -v test_xkin test_bound
python run_xkin.py --out OUT --nsig 20000 --nbkg 600000 --workers 2   # needs numpy, pythia8mc
python bound.py --summary OUT/xkin/summary.json --out bound.json      # or results/xkin-v1-summary.json
```
