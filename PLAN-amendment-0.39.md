# PLAN amendment v0.39: toyres-ssframe-v2 was stopped from outside before it saved a single toy; the same final resume is filed again, unchanged, as toyres-ssframe-v3

MV2 of Munim, Inc. (mv2@munimtech.com). 2026-11-22. Made with AI agents working in MV2's name; **not
yet checked by a physicist**. CC BY 4.0 (text); code Apache-2.0.

Part of the pre-registration. Written after job `toyres-ssframe-v2` (amendment 0.38) ended. No test,
threshold, prior or blinding rule of plan v0.11 or amendments 0.12-0.38 is changed.

## 1. What happened

`toyres-ssframe-v2` started on the Blade at 2026-11-22 08:19 UTC. Setup, the fetch (every sha256
matched), py_compile and the unit tests all passed. The calibration step printed only its start-up
lines, which are identical to those of `toyres-ssframe-v1` (prior 934 toys; control PASS; closures
3.1340 / 2.2953 / 2.2953; constrained Z0 2.1339; **recheck PASS**, 8 saved toys re-run with 0
mismatches). At 08:28 UTC, 544 s into the job and before its first checkpoint, the container was
stopped with SIGTERM (exit 143; the step is recorded as "interrupted"). That is a stop from outside
the job, not a failure of the code, and not the budget stop that amendment 0.38 sec. 3 has in mind.
It wrote no `toys.csv` and no `toyresume.json`: **no new toy value exists and none was seen.**

Raw output: `analysis/results/ssframe/toyres-v2-interrupted/` (`run.txt`, `fetch.txt`, `sha256.txt`,
`tests.txt`, `job.json`; `compile.txt` was empty, which means py_compile printed nothing).

## 2. Decision (made without any new number)

Amendment 0.38 sec. 3 allowed one final resume and fixed what happens if that resume "leaves fewer
than 1,000 toys". `toyres-ssframe-v2` never ran its budget, so that rule has not been met or broken.
It is not a resume that produced a result. The same final resume is therefore filed again, byte
for byte the same, as **`toyres-ssframe-v3`**. The workdir file `fetch_mods2.py` has the same
content, with the same FATAL sha256 list and the same 934-toy prior. The arguments are the same
(`--ntoys 6000 --workers 4 --budget-s 16000`), as are the 4 CPUs and 1 GB. A new version name is used
only because the compute lane runs each name once.

Everything amendment 0.38 says about the final resume now applies to `toyres-ssframe-v3`. If it
leaves fewer than 1,000 merged toys after running its budget, or its recheck fails, P1-P4 are NOT
GRADABLE for good. If it is again stopped from outside before running its budget, it is re-filed
unchanged once more, and nothing is graded until a resume has actually run.

## 3. Article status

Unchanged from 0.38 sec. 4: the significance article waits for this resume and for `leescan-v1`.
