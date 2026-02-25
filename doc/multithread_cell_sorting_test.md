## Purpose

The associated Python file contains a benchmarking script used to measure baseline performance 
characteristics of seven sorting algorithms, including the multithreaded "cell-view" sorting
implementations designed by Taining Zhang as well as three traditional comparison-based algorithms
implemented in pure Python. A detailed description of these three algorithms can be found in 
Appendix A of the accompanying document,"From Agency to Architecture: Reframing the 'Self-Sorting'
Model of Morphogenesis"

The goal is narrowly defined: to obtain reproducible empirical measurements under controlled
conditions, suitable for evaluating claims about relative performance.

---

## Algorithms Included

The benchmark measures:

* The multithreaded cell-based sorting algorithm (as implemented in the referenced codebase)
* Naive bubble sort
* Optimized bubble sort
* Insertion sort
* Selection sort

All non-cell-view algorithms are conventional textbook implementations written directly in Python

---

## Fidelity to the Original Cell Implementation

The multithreaded cell-based sorting implementation is derived directly from the referenced
`multithread_cell_sorting_steps.py` source.

The following principles were applied:

1. Core sorting logic was not modified.
2. Concurrency structure (per-cell threads when appropriate) was preserved.
3. Instrumentation functions not relevant to benchmarking (e.g., snapshot visualization) were
   disabled to avoid measurement distortion.
4. Array initialization was performed using a seeded pseudo-random number generator so that for
   each experiment the sorting algorithm operated on identical arrays.

Disabling visualization or snapshot capture affects only instrumentation overhead. It does not alter
the sorting semantics. This distinction is material to interpreting results.

If thread joining is used in the benchmark harness, it is for deterministic teardown and does not
alter the algorithm’s decision logic.

---

## Experimental Parameters

The script runs each algorithm multiple times on randomly generated input arrays of fixed length.

Key parameters include:

* Array length: 100
* Number of runs: fixed (e.g., 100)
* Random seed: explicitly set per iteration to ensure reproducibility
* Polling interval for thread completion: fixed sleep interval

These parameters are held constant across algorithms.

The array size and repetition count were chosen to balance statistical stability with practical
execution time. The array is constructed as a linear array of values from 0 to 99, which are then
shuffled. Thus, the randomized array will contain no duplicate values.

---

## Reproducibility

Reproducibility is ensured by:

* Explicit seeding of the pseudo-random number generator
* Fixed input size
* Deterministic non-cell algorithm implementations

Results may vary across:

* Python versions
* Operating systems
* Hardware architectures
* Interpreter builds (e.g., CPython vs PyPy)

---

## Output Format

Results are written as comma separated values to the file "sort_statistics.csv" in the CSV folder.
No attempt is made to create the folder if it does not exist; it must be created manually before
the script is run.

Each row represents a metric.

The first column contains the metric name. For example, "bubble-time" indicates measured run times
for a standard bubble sort, and "rpe-swap" indicates the recorded number of swaps performed for
each iteration of the Randomized Pair Exchange algorithm.

The second column contains the mean across runs.
Subsequent columns contain per-run values.

This structure permits independent verification of summary statistics.
