# PLAN amendment v0.22: the low-mass reading leaves the fit table's factor unexplained; klyscan re-filed

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written before `aprime-aleph-v1` (A'-ALEPH, P1-P4), `aprime-toys-v1`
(C1-C5) or `klyscan-v2` (S1-S7) have produced any number. Nothing in their grades changes.

## 1. Reading `ALEPHLOW` and amendment 0.21's rule (section 4)

An AI reading agent with no access to this repository searched Heister's paper (arXiv:1610.06536
v9) for the mass range of the electron-muon background and read the 5-15 GeV region of the fit
figure (HTML Fig. 7) and of Fig. 5. Only the end of its report was kept, so its bin-by-bin lines
for 5-15 GeV are lost. The kept summary says:

- The fitted curve is **not drawn below 15 GeV**. The text says the fit uses 15-50 GeV ("The fit is
  performed in the range from 15 to 50 GeV").
- The range used to build or normalise the electron-muon background or its kernel-density
  estimate is **not stated**. The nearest sentences are "the distributions agree pretty well from
  15 to 50 GeV" and "In the region 15 to 50 GeV ... the background model template ... using the
  p.d.f. from the one-dimensional kernel density approximation provides ... a reasonably good
  description". The KDE curve in Fig. 6 is drawn from 5 GeV, and the TKDE in Fig. 11 from 15 to 50
  GeV.
- What "# background events (overall)" means is **not stated**. Figs. 3 and 4 say "The overall
  event numbers are normalized to the yield of the opposite sign di-muon mass spectrum obtained
  from ALEPH data".
- The paper gives **no number of muon pairs in any mass range**.
- Sec. 3.4.1 normalises the electron-muon spectrum by the expected ratio (electron-muon pairs
  "twice as high" as muon pairs, electrons "about 6% less" efficient). It also states that the
  efficiency is independent of the di-lepton mass "in the range from 5 to 50 GeV".

**Applying 0.21 section 4.** No sentence and no surviving count shows a wider background range
whose normalisation reaches 1,489 +- 20 %. The paper names 15-50 GeV for the fit and for the
template's agreement, and does not state the KDE's normalisation range. The second branch therefore
applies: **the identity of 0.21 section 2(b) stands (the printed background must be at least 2.52
times the in-fit background, about 4.4 times by the figure), but the reason for the factor stays
unexplained**, and it is reported as such. "Overall" may refer to a wider range such as 5-50 GeV,
as the 5 GeV lower limit of the efficiency statement and the KDE plot suggest, but the paper does
not say so, and we do not claim it. Nothing is extrapolated from the lost bin lines.

A'-ALEPH (P1-P4) is unaffected, as 0.21 section 3 fixed.

### 1b. A second, compact reading of 5-15 GeV (`ALEPHLOW2`), and what it decides (written before it is made)

The lost bin lines are requested again from a new blind reading, with every number on one short
final line. 0.21's rule is applied to it as follows (all ranges fixed now):

- **Data:** if 362 + (sum of n in 5-15 GeV in the fit figure) lies within 1,489 +- 20 %
  (1,191-1,787), the table's "overall" total is the 5-50 GeV sample, and 0.21 section 2's reading is
  **confirmed** and written as such.
- **Background:** if 300.9 + (sum of the electron-muon values in 5-15 GeV in Fig. 5) lies within
  1,457 +- 20 % (1,166-1,748), the same conclusion holds for the background.
- If neither sum reaches its range, the factor stays unexplained (section 1 above).
- More than three OFF values in a sum make that sum "not readable". Nothing is extrapolated.

## 2. `klyscan-v1` failed on our own syntax error; `klyscan-v2` filed

`klyscan-v1` (the Ko-Li-Yu model-III scalar-mass scan, expectations S1-S7 in NOTE-higgs-searches
section 6d) stopped before generating any event: `run_klyscan.py` 0.1.0 passed two dictionary
keywords containing '-' to `dict()`, which Python rejects. Version 0.1.1 builds the same
thresholds as a dictionary literal with string keys and adds a test for it. Masses, seeds, Pythia
settings, selections and expectations are unchanged. The fetched modules (kly 0.1.0, lephz,
eff4f 0.2.0, xkin) were checked for every name the script calls. Job `klyscan-v2` (1 GB) is filed.
Its code will be committed with its results.
