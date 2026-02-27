## Purpose

The associated Python file contains a benchmarking script used to capture the sorting history
of the multithreaded "cell-view" sorting implementations designed by Taining Zhang, implemented in
pure Python. A detailed description of these three algorithms, designated RPE, RPX and RSD can be
found in Appendix A of the accompanying document,"From Agency to Architecture: Reframing the 
'Self-Sorting' Model of Morphogenesis"

---

## Fidelity to the Original Cell Implementation

This implementation is derived directly from the source code found at
[https://github.com/Zhangtaining/cell_research](https://github.com/Zhangtaining/cell_research)
as forked by [https://github.com/lpassey/cell_research](https://github.com/lpassey/cell_research)

The following principles were applied:

1. Core sorting logic was not modified.
2. Concurrency structure (per-cell threads) was preserved.
3. Frozen cells are selected randomly per run.

The following modifications were made:

1. Comments were added to assist comprehensibility
2. Code was added to insure there was no duplication when "freezing" cells
3. thread joining was used in the benchmark harness, for deterministic teardown 
   which does not alter the algorithm’s decision logic.
4. Array initialization was performed using a seeded pseudo-random number generator so that for
   each experiment the sorting algorithm operated on identical arrays.
5. Code was added to collect sorting steps and save them to .npy files

---

## Experimental Parameters

The script runs each algorithm multiple times on randomly generated input arrays of fixed length.

Key parameters include:

* Array length: 100
* Number of runs: fixed (e.g., 20)
* Random seed: explicitly set per iteration to ensure uniformity across algorithms
* Polling interval for thread completion: fixed sleep interval

These parameters are held constant across algorithms.

The array size and repetition count were chosen to balance statistical stability with practical
execution time. The array is constructed as a randomized array with values between 0 and 100;
duplicate values are statistically common under this sampling scheme, though most elements remain
distinct.

---

## Reproducibility

Explicit seeding of the pseudo-random number generator creates some uniformity of test arrays,
however reproducibility is not guaranteed (or expected) due to stochastic thread scheduling by
the Python Global Interpreter Lock.

---

## Output Format

Results are written as "lists of lists" to binary files named {cell_type} + "_frozen_steps_" +
 {frozen_number} + ".npy" in the "csv" folder, where {cell_type} is one of "rpe", "rpx" or "rsd",
and {frozen_number} is the number of frozen cells in a specific experiment (0, 1, 2, or 3).
No attempt is made to create the csv folder if it does not exist; it must be created manually
before the script is run.

Each file contains an array of 20 sub-arrays, where each sub-array contains an array of element
values after each swap is performed by the associated sorting algorithm. Each sub-array will hold
a number of element arrays where the number of element arrays will equal the number of swaps. This
is typically 2475 steps for a bubble sort, but it may be more or less.

This structure permits independent verification of summary statistics.

The output will also include a file, "freezing_sorting_analysis.txt" containing a summary of the
twelve experiments run indicating for each test the sorting algorithm tested and the number of
frozen cells for that test, the number of experiments run (20) and the number of successful sorts
using those parameters.

One dozen .npy files produced by this script, together with one "freezing_sorting_analysis.txt" file
have been checked in to GitHub, but it must be understood that due to the stochastic nature of the
algorithms these files are snapshots, and cannot be expected to be reproducible.

