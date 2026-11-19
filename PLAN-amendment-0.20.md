# PLAN amendment v0.20: A'-ALEPH reading check (P0) graded, toys at the reading's own scale

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-19. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration; extends amendment 0.19. Written **after** the blind per-bin reading of
Heister's Fig. 5 came back and **before** any fit of it (job `aprime-aleph-v1`) or the calibration
toys of amendment 0.19 (`aprime-toys-v1`, still queued) have produced a number. Nothing in P1-P4 or
C1-C5 is changed.

## 1. The reading, and P0

The reading ([data/aleph-fig5.json](data/aleph-fig5.json)) was made by an AI reading agent with no
access to this repository (arXiv:1610.06536 v9 HTML, Figure 5; the body text calls it Fig. 6;
1 GeV bins, linear y axis 0-70, no error bars on the electron-muon histogram). It is committed
exactly as read. Reader's uncertainty: +-0.5 events per bin for the muon pairs, +-0.3 for the
background.

| bin (GeV) | 28-29 | 29-30 | 30-31 | 31-32 | 32-33 |
|---|---|---|---|---|---|
| mu mu data n | 8 | 12 | 14 | 7 | 6 |
| e mu background as plotted v | 3.8 | 5.8 | 4.8 | 4.8 | 4.8 |

**P0: sum of (n - v) over 29-32 GeV = 6.2 + 9.2 + 2.2 = 17.6 events, within the gate 17.8 +- 3.0.
PASS** (hand-checked; the reader's own sum is also 17.6). P1-P4 are therefore gradable on this
reading. The whole reading sums to 362 muon pairs and 300.9 background in 15-50 GeV.

## 2. A scale question found while checking the reading (information, not graded)

Heister's table of the unbinned fit (v9) gives **32.31 +- 10.87 signal and 1457.06 +- 89.71
background events** in 15-50 GeV, about 1,489 in all. The figure holds **362**. Two checks, made by
hand before any fit, say the figure's scale is the one that goes with ALEPH's significances:

- Z_Bi in the bins whose centres lie within 30.40 +- 1.49 GeV (29-32 GeV) with tau = 1:
  n_on = 33, n_off = 15 gives roughly 2.5 sigma, close to Heister's **2.63**. At four times the
  scale it would be about 5.
- A local significance near 5 for 32 signal events needs a background of order 15-20 events
  under the peak, which is what the figure shows (15.4 in 29-32 GeV). At the table's scale the
  same 32 events would sit on about 70 and give about 2 sigma.

We cannot tell from the paper why the table's background is about four times the figure's
(its error, 89.71, is also more than twice sqrt(1457)). A second blind reading (hands goal
`ALEPHFIT`, filed this run) reads the figure that shows the unbinned fit. **What it decides,
written now:** if that figure holds 1,489 +- 20 % entries in 15-50 GeV, Fig. 5 shows a smaller
or differently normalised sample and A'-ALEPH speaks only for Fig. 5's sample, which we will say in
every statement of its result; if it holds 362 +- 20 %, the figures agree and the table's
background number is unexplained; anything else is reported as found. Neither outcome changes
P1-P4.

**Consequence for the calibration.** The toys of amendment 0.19 (`aprime-toys-v1`, C1-C5) were
built at the table's scale (1457 background pairs). For A'-ALEPH they are about four times too big:
low counts per bin are exactly where the asymptotic formula is least reliable. Section 3 adds toys
at the reading's own scale.

## 3. A'-ALEPH toys at the reading's scale (job `aprime-aleph-v1`)

The job fetches `stats/emuframe.py` 0.1.0 from main (checked against its git blob
`d55c900f`), runs `aleph_aprime` on the reading (P1-P4, written to `aleph_aprime.json` first), a
profile-likelihood scan in mu for both models, and then **10,000 background-only
pseudo-experiments drawn from the reading's own mu = 0 fit of model "bb"** (n_i ~ Poisson(r t_i),
e mu m_i ~ Poisson(t_i)), each fitted with "bb" and "exact" at ALEPH's fixed mass and shape
(exact-model templates floored at 0.5 counts, as in amendment 0.19 sec. 4). Toy p-value =
(1 + number of toys with Z0 >= observed) / (N + 1). Code:
[stats/run_aprime_aleph.py](stats/run_aprime_aleph.py).

**Rules, written now:**

1. P1-P4 are graded on the asymptotic Z0 exactly as amendment 0.19 wrote them.
2. The toy-calibrated Z (Z_toy) for "bb" and "exact" is **always reported beside** the asymptotic
   one.
3. Amendment 0.19 said that if C1 fails, A' uses toy-calibrated p-values "for both DELPHI and
   A'-ALEPH". For A'-ALEPH that now means **this job's toys** (the reading's scale), not the
   1457-pair toys. For DELPHI it still means toys at DELPHI's own scale, to be filed with the data.
4. If the asymptotic Z0(bb) and Z_toy(bb) fall on opposite sides of 3.0, the headline says so
   plainly whichever way C1 goes, and P3 is called "borderline" in every summary.
5. Information only: the toys' rates of Z0 >= 2 and >= 3 for each model and the mean fitted signal.

**What we expect, written before any fit (no confident expectation for P3).** A rough Gaussian
estimate from the window alone gives Z0(exact) about 3.4-3.8 and Z0(bb) about 0.79 of it, so
**Z0(bb) of about 2.7-3.0, right at P3's threshold**. We do not know which side it falls.

## 4. Limits

The input is a by-eye reading of a published figure by one AI reading agent. The plotted
background v is taken to be (raw e mu count) x 0.532; if ALEPH scaled it differently, the variants
0.45 and 0.60 show how much it matters. The binned, unsmoothed template ignores that the true
background is smooth, so Z0(bb) is conservative and Z0(exact) optimistic. None of this is a result
of the ALEPH Collaboration.
