# cell_research
This is the repo for all cell sorting code and data

None of these scripts or classes are documented in the original repository. What follows is
my best guess as to their purpose and function, based upon an examination of the code and the
descriptions found at https://arxiv.org/pdf/2401.05375.

### sorting_cells.py

This script appears to be an attempt to implement a bubble sort. It fails to run because:
1. At lease one class it relies on (Cell.py) is not imported
2. The Cell and CellWithVisualization classes have changed their constructor signatures
3. The start_ptr variable is not initialize before it is used

The method 'get_current_monotonicity' is apparently designed to calculate the total inversion
count (TIC) of an array. Because the TIC of a sorted array is always 0, the lines printing
the "disorder" are not meaningful.

In my first commit I will try to rectify these errors.

### sorting_cells_multithread.py

This script appears to be an attempt to refactor a single-threaded cell-based sort into a
concurrent behavioral simulation. It seems to be an interim iteration that was abandoned as
development progressed. It fails to run correctly because:

1. The `MultiTreadCell` object has evolved and the constructor now requires 8 mandatory positional arguments.
2. Cell.right_neighbor is not defined in MultiThreadCell, and is not created at the end of the cell list
3. 'MultiThreadCell.move()' is stubbed so no sorting logic exists to be executed by the threads and sorting will never occur.
4. The `while True:` loop in main() lacks a break condition or exit strategy, ensuring the process hangs indefinitely.

This code is apparently abandoned in favor of multithread_cell_sorting, so I will abandon it as well.

### multithread_cell_sorting

This script appears to be the next evolution of `sorting_cells_multithread.py`. It requires a 
command line argument of "--cell_type='algotype'" but will run if launched correctly, if a 
StatusProbe object is added to the constructor for each of the algotype classes; however, it will
not run correctly:

1. The underlying `MultiThreadCell` objects will not swap elements if `visualization_disabled` is not set to `True`, 
2. `MultiThreadCell` derived objects require positions and boundaries to be two element integer tuples
3. `MultiThreadCell` derived objects require a "group" property that is not part of their constructor or definition. This property must be "monkey patched" to every cell in the array.
4. The `while True:` loop in main() lacks a break condition or exit strategy, ensuring the process hangs indefinitely.
5. The process launches multiple threads, but fails to stop them when the main thread ends, leading to the programing hanging.

This script is an obvious iteration relic. Its only value is as a basis for future development.

### multithread_sorting_cell_aggregation_analysis.py

This script is designed to analyze how different sorting cell types (Bubble, Insertion, and Selection) 
aggregate or interact when mixed together in a multithreaded environment. It creates a population of 
cells with different sorting algorithms, runs them concurrently, and collects data about their behavior 
during the sorting process. The script has several issues that would prevent it from executing properly:

1. It attempts to save data to subdirectories within the 'csv' directory (e.g., 'csv/cell_type_aggregation_random_dist_200_tests_bubble_selection_dup/') 
   that don't appear to exist. These directories would need to be created before running the script.
2. The script runs 100 experiments (line 162), each creating and starting multiple threads, which could be 
   resource-intensive and potentially lead to performance issues.
3. Like other multithreaded scripts in this repository, it properly terminates threads when sorting is complete 
   (lines 177-180), but lacks error handling for cases where sorting might not complete successfully.
4. The script contains multiple commented-out save paths (lines 186-197), suggesting it was used for different 
   experimental configurations but wasn't cleaned up for production use.

This script appears to be used for experimental data collection rather than as a reusable component.
