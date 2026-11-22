# PLAN amendment v0.40: leescan-v1 ran out of time after 9 toys; a fast exact minimiser (leefast 0.1.0) and job `leescan-v2`

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-22. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written **after** `leescan-v1` returned and **before** `leescan-v2`
has run. No test, threshold, prior, grade or blinding rule of plan v0.11 or amendments 0.12-0.39
is changed. Grades L0-L5 of amendment 0.34 stay exactly as written, with one addition to the L0
gate (gate V, below).

## 1. What happened

`leescan-v1` (amendment 0.34) ran on the Dell from 08:05 to 12:43 UTC on 2026-11-22. Setup, the
sha256 checks, the unit tests and the closure gate all passed (par3 Z = 3.1340, scanner = 3.1340).
Its 14,000 s budget then stopped the toy loop after **9 of 2,000 toys**, about 1,800 s per toy per
worker. Grades: L0 FAIL (toys < 1,000), L1-L5 NOT GRADABLE. Raw output is committed under
`analysis/results/leescan/leescan-v1/`.

The cost is in the fitting, not the statistics. Each toy needs 1,125 profile fits (125 masses x
3 widths x 3 starting values of mu), so v1 averaged about 3 s per fit. Yet its own unit tests
ran about 25 such fits in 2.9 s (about 0.1 s each). We have not measured which of two causes
dominates. One: `aprime_smooth.ParFit._min` calls L-BFGS-B with ftol 1e-14 and gtol 1e-9 and a
5,000-iteration cap, tolerances at the level of floating-point noise, which can make fits on the
real spectrum run to the cap. Two: two worker processes on a 2-CPU quota, each with multi-threaded
BLAS, can oversubscribe the CPUs. v2 removes both: the minimiser below, and single-threaded BLAS.
Amendment 0.34 said a short run is resumed "as `leescan-v2` from the saved rows". With the same
code that resume would need about 1,000 CPU-hours, so it is not a real option.

## 2. Numbers seen before this amendment (disclosed)

The 9 toys and the observed scan are public in the committed v1 output. **They are not graded and
are not quoted as a result**:

- Observed scan (primary, Gamma = 1.78 GeV): maximum Z = 3.133 at 30.50 GeV. All three widths peak
  at 30.50 GeV, so L5 would pass when graded. Observed upcrossings of Z = 1: 1.
- Toys: 1 of 9 has a primary maximum Z of at least 3.134 (toy 2: 3.443 at 20.50 GeV), and
  E[N(1)] = 1.78 +- 0.46. Gross-Vitells with that E[N(1)] gives a global Z of about 2.0, which
  matches the prediction written in amendment 0.34.

Nine toys cannot support any grade. Nothing below was chosen with these numbers in view: the
minimiser change follows from the run time alone, and no threshold moves.

## 3. The change: leefast 0.1.0 (new module `stats/leefast.py`; nothing existing is modified)

- `stats/leescan.py` 0.1.0 is downloaded at commit `dabf4b2fa8f7edfb7bb24166f2d18729e71a1b4b`
  and checked by sha256 (`fec272cc...045f`, the file v1 ran). Everything except the minimiser is
  its own unchanged code: data, signal shapes (`grid_shapes`), grid, widths, starting values,
  the toy generator (`one_toy`, seed 20261121 + index, the same truth), the upcrossing and
  direct counts (`summarize`), the grades (`grade`) and the `LEESCAN:` line.
- **The only change**: the minimum of the same negative log-likelihood (`ParFit.nll_grad`, same
  parameters a, ln r, mu; same bounds 0 <= mu <= 20 and |ln r| <= 10) is found by Newton's method
  with the analytic gradient and Hessian. When the Hessian is not positive definite, Levenberg
  damping is added. Steps use Armijo backtracking, and the mu bounds are handled by an active set.
  It runs from the same three starting values of mu (0, 0.8, 2.0) and stops when the Newton
  decrement is below 1e-11. The background-only fit is solved the same way. That fit is concave
  in (a, ln r) because both spectra are log-linear when mu = 0. If a Newton run fails
  numerically, that one fit falls back to ParFit's own L-BFGS-B. Fallbacks are counted and
  printed.
- Unit tests (`stats/test_leefast.py`) check the value and gradient against `ParFit.nll_grad`,
  the Hessian against finite differences, the scanner against `leescan.Scanner` (L-BFGS-B) and
  `ParFit.discovery` on synthetic spectra, the mu bounds, and the copied v1 reference numbers.
  The copied numbers are checked against v1's printed maxima and upcrossing counts.

## 4. Gate V (added to L0; fixed now)

`leescan-v2` passes L0 only if, in addition to the 0.34 conditions (unit tests, closure 3.134 +-
0.01, scanner = discovery +- 0.002, at least 1,000 toys):

- **V1**: all 375 observed Z(mass) values agree with v1's L-BFGS-B values to 0.002 (plus 5e-7
  for the 6-decimal copy), and so do the 3 observed Z values at 30.40 GeV;
- **V2**: for toys 0-8, the maximum Z of all four variants agrees with v1's `toys.csv` to 0.002
  (plus 5e-6 for its 5 decimals). All 36 values must be present;
- **V3**: the toy truth (r and the sum of T) equals v1's to a relative 1e-6.

If gate V fails, every grade is NOT GRADABLE. The disagreeing points are printed (`OBSDIFF`,
`TOYDIFF`) and handled in a new amendment, never by moving a tolerance. All toys come from the fast
scanner. v1's 9 rows are used only for gate V2, never merged into the counts.

## 5. The job

`leescan-v2`: python:3.12, 2 CPUs, 1 GB, 300 min. Steps: py_compile, fetch + sha256, unit tests,
then `leefast.py --ntoys 2000 --workers 2 --budget-s 14000` with single-threaded BLAS. Expected
speed: a few seconds per toy, so all 2,000 toys should finish well inside the budget. If fewer
than 1,000 finish, the result is NOT GRADABLE. It is then resumed as `leescan-v3` with
`--prior-csv` (v2's committed `toys.csv`, the same code) for the missing indices. The amendment
0.32 rule applies unchanged.

**Expectations, written before the run:** gate V PASS 80 %; at least 1,000 toys 90 % given gate V;
L0-L5 priors as in amendment 0.34 (L1 70 %, L2 55 %, L3 80 %, L4 70 %, L5 60 %).

## 6. Limits

- Newton and L-BFGS-B minimise the same function. Where both converge they agree to well below
  0.002 in Z. Gate V checks this on 411 numbers before any toy count is used.
- All other limits of amendment 0.34 stand: the inputs are readings of a published figure, the
  toy truth is the constant-ratio par3 fit, and three widths only roughly stand in for a fully
  floated width.
