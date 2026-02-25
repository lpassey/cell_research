"""
This script is designed to document baseline efficiencies of 7 scripting algorithms. It was derived
from multithread_cell_sorting_steps.py which purports to record all the steps taken when running the
three "cell-view"-derived algorithms.

This script adds 4 more sorting algorithms to the three "cell-view" algorithms: a standard bubble
sort, a standard insertion sort, a standard selection sort, and a naive object-oriented
implementation of the standard bubble sort where each comparison pass examines the entire array
even though the end of the array is guaranteed to be sorted, and where loop termination is
triggered by an array scan rather than a swap count.
"""

import statistics

import csv
import sys
import types
import threading
import time
import random
from modules.multithread.StatusProbe import StatusProbe
from modules.multithread.SelectionSortCell import SelectionSortCell
from modules.multithread.BubbleSortCell import BubbleSortCell
from modules.multithread.InsertionSortCell import InsertionSortCell
from modules.multithread.CellGroup import CellGroup, GroupStatus
from modules.multithread.MultiThreadCell import CellStatus


# VALUE_LIST = [28, 34, 6, 20, 7, 89, 34, 18, 29, 51]
#VALUE_LIST = range(20,0,-1)

def create_cells_within_one_group(value_list, threadLock, status_probe, cell_type):
    if len(value_list) == 0:
        return []
    left_boundary = (0, 1)
    right_boundary = (len(value_list) - 1, 1)
    cells = []
    for i in range(0, len(value_list)):
        cell = None
        if cell_type == 'selection':
            cell = SelectionSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        if cell_type == 'bubble':
            cell = BubbleSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        if cell_type == 'insertion':
            cell = InsertionSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        cell.take_snapshot = types.MethodType( take_snapshot, cell )
        cells.append(cell)

    period = 100000000
    start_count_down = 100000000
    cell_group = CellGroup(cells, cells, 0, left_boundary, right_boundary, GroupStatus.ACTIVE, threadLock, start_count_down, period)
    for cell in cells:
        cell.group = cell_group
    return cells, [cell_group]

def print_current_status(cells):
    print([{"value": c.value, "group id": c.group.group_id, "group status": c.group.status, "cell status": c.status, "left": c.left_boundary, "right": c.right_boundary, "ideal position": c.ideal_position} for c in cells])

def is_sorted(cells):
    prev_cell = cells[0]
    for c in cells:
        if c.value < prev_cell.value:
            return False
        prev_cell = c
    return True
    # print([{"value": c.value, "group id": c.group.group_id, "group status": c.group.status, "cell status": c.status, "left": c.left_boundary, "right": c.right_boundary} for c in cells])

def kill_all_thread(cells, groups):
    for c in cells:
        c.status = CellStatus.INACTIVE
    for g in groups:
        g.status = GroupStatus.MERGED

def activate(cells, cell_groups):
    for cell in cells:
        cell.start()
    for group in cell_groups:
        group.start()


def insertion_sort_cells( cells ):
    right = len( cells )
    i = 1
    swaps = 0
    while i < right:
        j = i
        cells[j].status_probe.count_comparison()    # this should end up being the same as len(cells)
        while j > 0 and cells[j].value < cells[j -1].value: # if cells[j] is less than cells[j -1] swap them
            cells[j].status_probe.record_compare_and_swap()
            cells[j].swap((j - 1, cells[j].current_position[1]))
            swaps += 1
            j-= 1
        i += 1
    return


def selection_sort_cells(cells) :
    start = 0
    while start < len( cells ) :
        # find the smallest value in the list,
        smallest = cells[start]
        for j in range( start + 1, len( cells )):
            cells[j].status_probe.count_comparison()
            if smallest.value > cells[j].value:
                smallest = cells[j]
        # compare it to cells[start]
        if smallest.value < cells[start].value: # if smaller, swap.
            smallest.swap( (start, cells[start].current_position[1]))
        start += 1      # increment start
    return


def bubble_sort_cells(cells):    # cells must be an array of instances of `BubbleSortCell`
    need_to_sort = True
    swaps = 0
    right = len(cells) - 1  # with every pass, the largest element will end up at the end, so we needn't look at it ever again.
    while need_to_sort:
        need_to_sort = False    # assume we are sorted.
        for i in range(0, right ):  # look at every cell and compare it to its right neighbor.
            cell = cells[i]
            cell.status_probe.count_comparison()  #  += 1          # every time we compare cells, count it.
            if cell.should_move_to( cells[ i + 1].current_position, True ):
                need_to_sort = True     # we must swap positions, which means we need another pass.
                cell.swap( (i + 1, cell.current_position[1]))
                swaps += 1      # count every swap.
        right -= 1
    return swaps     # keep track of how many steps it took to achieve sortedness

"""
These two methods are designed to be "monkey-patched" into cell objects to override default behaviors
BubbleSortCell will compare to the right or left depending on a random result. This is incompatible
with standard sorts, so for the object-oriented naive bubble sorting algorithms this decision is disabled.
"""
def flip_coin(self):
    return True

"""
The original MultiThreadCell object would record a "snapshot" of the array state after each swap.
Given Python's inefficiencies, this storage could consume significant CPU time, overwhelming the
time metric that this script is designed to capture. This method is designed to skip the 
snapshotting step so that elapsed time more closely reflects the actual sort time without overhead.
"""
def take_snapshot(self):
    return None, None


def main(argv):
    sorting_list = [i for i in range(100)]  # create list of 100 elements, in order without duplicates

    sort_time_for_each_sort = []    # standard bubble sort
    comparisons_for_each_sort = []
    swaps_for_each_sort = []

    insertion_time = []     # standard insertion sort
    insertion_swaps = []
    insertion_compares = []

    selection_time = []     # standard selection sort
    selection_swaps = []
    selection_compares = []

    sort_time_for_each_sort_bubble = []     # naive bubble sort
    comparisons_for_each_sort_bubble = []
    swaps_for_each_sort_bubble = []

    sort_time_for_each_sort_rpe = []        # rpe (aka bubble) sort
    comparisons_for_each_sort_rpe = []
    swaps_for_each_sort_rpe = []

    sort_time_for_each_sort_selection = []  # rsd (aka selection) sort
    comparisons_for_each_sort_selection = []
    swaps_for_each_sort_selection = []

    sort_time_for_each_sort_insertion = []  # rpx (aka insertion) sort
    comparisons_for_each_sort_insertion = []
    swaps_for_each_sort_insertion = []

    for i in range(100):
        random.seed(66 + i) # each experiment will start with the same "random" list
        random.shuffle(sorting_list)    # sorting_list is the array base; it should be the same at the beginning of each iteration.

        print(f"\n>>>>>>>>>>>>>>>>> Prepare cells to sort for std bubble experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
        status_probe = StatusProbe()

        cells, cell_groups = create_cells_within_one_group(sorting_list, None, status_probe, 'bubble')
        print("Start sorting......")
        start = time.perf_counter()
        swaps = bubble_sort_cells(cells)
        elapsed = time.perf_counter() - start
        print(f"Elapsed time: {elapsed} Swaps: {swaps}\n")
        sort_time_for_each_sort.append( elapsed )
        swaps_for_each_sort.append(status_probe.swap_count)
        comparisons_for_each_sort.append( status_probe.comparisons )

        print(f"\n>>>>>>>>>>>>>>>>> Prepare cells to sort for std insertion experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
        status_probe = StatusProbe()
        cells, cell_groups = create_cells_within_one_group(sorting_list, None, status_probe, 'bubble')
        start = time.perf_counter()
        insertion_sort_cells( cells )
        elapsed = time.perf_counter() - start
        print(f"Elapsed time: {elapsed} Swaps: {status_probe.swap_count + status_probe.comparisons}\n")
        insertion_time.append( elapsed )
        insertion_swaps.append( status_probe.swap_count)
        insertion_compares.append( status_probe.swap_count + status_probe.comparisons)

        print(f"\n>>>>>>>>>>>>>>>>> Prepare cells to sort for std selection experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
        status_probe = StatusProbe()
        cells, cell_groups = create_cells_within_one_group(sorting_list, None, status_probe, 'bubble')
        start = time.perf_counter()
        selection_sort_cells( cells )
        elapsed = time.perf_counter() - start
        print(f"Elapsed time: {elapsed} Swaps: {status_probe.swap_count }\n")
        selection_time.append( elapsed )
        selection_swaps.append( status_probe.swap_count)
        selection_compares.append( status_probe.swap_count + status_probe.comparisons)

#    if (False):
        print(f"\n>>>>>>>>>>>>>>>>> Prepare cells to sort for OOP bubble experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
        status_probe = StatusProbe()
        original_flip_coin = BubbleSortCell.flip_coin
        try:
            BubbleSortCell.flip_coin = flip_coin    # this prevents the cell from comparing from to the left, which is non-standard
            cells, cell_groups = create_cells_within_one_group(sorting_list, None, status_probe, 'bubble')
            print("Start sorting......")

            """
            A naive object-oriented implementation of a bubble sort using the BubbleSortCell object as 
            the array element. Because the object is designed to be invoked randomly it does not track
            the number of swaps in a single pass, so the entire array must scanned at the end of each
            move to determine if the array is sorted. This mimics that way the "cell-view" algorithms behave.
            """
            start = time.perf_counter()
            while not is_sorted(cells):
                right = len( cells )
                for k in range( 0, right ):
                    c = cells[k]
                    c.move()
                # right -= 1    # this optimization would mimic the standard bubble sort, which is not what we want for this suite of tests.
            elapsed = time.perf_counter() - start
        finally:
            BubbleSortCell.flip_coin = original_flip_coin
        print(f"Elapsed time: {elapsed}\n")
        sort_time_for_each_sort_bubble.append(elapsed)
        comparisons_for_each_sort_bubble.append(status_probe.comparisons)
        swaps_for_each_sort_bubble.append(status_probe.swap_count)

        threadLock = threading.Lock()

        print(f">>>>>>>>>>>>>>>>> Prepare cells to sort for RPE experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
        status_probe = StatusProbe()

        cells, cell_groups = create_cells_within_one_group(sorting_list, threadLock, status_probe, 'bubble')
        threadLock.acquire()
        print("Activating cells...")
        activate(cells, cell_groups)
        threadLock.release()

        print("Start sorting......")
        start = time.perf_counter()
        while not is_sorted(cells):
            time.sleep(0.0005)
        elapsed = time.perf_counter() - start
        print(f"Elapsed time: {elapsed}")
        threadLock.acquire()
        kill_all_thread(cells, cell_groups)
        threadLock.release()
        for c in cells:
            c.join()    # added for deterministic teardown; does not alter sorting logic.

        sort_time_for_each_sort_rpe.append(elapsed)
        swaps_for_each_sort_rpe.append(status_probe.swap_count)
        comparisons_for_each_sort_rpe.append(status_probe.comparisons)

        print(">>>>>>>>>>>>>>>>> Sorting complete, killed all threads. <<<<<<<<<<<<<<<<<<<<")
        time.sleep(.01)

        print(f">>>>>>>>>>>>>>>>> Prepare cells to sort for RSD experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
        status_probe = StatusProbe()
        threadLock = threading.Lock()

        cells, cell_groups = create_cells_within_one_group(sorting_list, threadLock, status_probe, 'selection')
        threadLock.acquire()
        print("Activating cells...")
        activate(cells, cell_groups)
        threadLock.release()

        print("Start sorting......")
        start = time.perf_counter()
        while not is_sorted(cells):
            time.sleep(0.0005)
        elapsed = time.perf_counter() - start
        threadLock.acquire()
        kill_all_thread(cells, cell_groups)
        threadLock.release()
        for c in cells:
            c.join()

        print(f"Elapsed time: {elapsed}")
        sort_time_for_each_sort_selection.append(elapsed)
        comparisons_for_each_sort_selection.append(status_probe.comparisons)
        swaps_for_each_sort_selection.append(status_probe.swap_count)

#        sorting_steps_for_each_run_selection.append(status_probe.sorting_steps)
        print(">>>>>>>>>>>>>>>>> Sorting complete, killed all threads. <<<<<<<<<<<<<<<<<<<<")
        time.sleep(.01)

        print(f">>>>>>>>>>>>>>>>> Prepare cells to sort for RPX experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
        status_probe = StatusProbe()
        threadLock = threading.Lock()
        cells, cell_groups = create_cells_within_one_group(sorting_list, threadLock, status_probe, 'insertion')
        threadLock.acquire()
        print("Activating cells...")
        activate(cells, cell_groups)
        threadLock.release()
        print("Start sorting......")
        start = time.perf_counter()
        while not is_sorted(cells):
            time.sleep(0.0005)
        elapsed = time.perf_counter() - start
        threadLock.acquire()
        kill_all_thread(cells, cell_groups)
        threadLock.release()
        for c in cells:
            c.join()

        print(f"Elapsed time: {elapsed}")
        sort_time_for_each_sort_insertion.append(elapsed)
        comparisons_for_each_sort_insertion.append(status_probe.comparisons)
        swaps_for_each_sort_insertion.append(status_probe.swap_count)

        print(">>>>>>>>>>>>>>>>> Sorting complete, killed all threads. <<<<<<<<<<<<<<<<<<<<")
        time.sleep(.01)

    filename = 'csv/sort_statistics.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        # Optional: Add a header row
        writer.writerow(["Type", "Average", "Values..."])

        average = statistics.mean(sort_time_for_each_sort)
        std_dev = statistics.stdev(sort_time_for_each_sort)
        print( f"\nBubble\nAvg time: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["bubble-time", average] + sort_time_for_each_sort
        writer.writerow(row)

        average = statistics.mean(swaps_for_each_sort)
        std_dev = statistics.stdev(swaps_for_each_sort)
        print( f"Avg swaps: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["bubble-swap", average] + swaps_for_each_sort
        writer.writerow(row)

        average = statistics.mean(comparisons_for_each_sort)
        std_dev = statistics.stdev(comparisons_for_each_sort)
        print( f"Avg comparisons: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}\n" )

        row = ["bubble-comp", average] + comparisons_for_each_sort
        writer.writerow(row)

        average = statistics.mean(insertion_time)
        std_dev = statistics.stdev(insertion_time)
        print( f"Insertion\nAvg time: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["insert-time", average] + insertion_time
        writer.writerow(row)

        average = statistics.mean(insertion_swaps)
        std_dev = statistics.stdev(insertion_swaps)
        print( f"Avg swaps: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["insert-swap", average] + insertion_swaps
        writer.writerow(row)

        average = statistics.mean(insertion_compares)
        std_dev = statistics.stdev(insertion_compares)
        print( f"Avg comparisons: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}\n" )

        row = ["insert-comp", average] + insertion_compares
        writer.writerow(row)

        average = statistics.mean(selection_time)
        std_dev = statistics.stdev(selection_time)
        print( f"Selection\nAvg time: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["select-time", average] + selection_time
        writer.writerow(row)

        average = statistics.mean(selection_swaps)
        std_dev = statistics.stdev(selection_swaps)
        print( f"Avg swaps: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["select-swap", average] + selection_swaps
        writer.writerow(row)

        average = statistics.mean(selection_compares)
        std_dev = statistics.stdev(selection_compares)
        print( f"Avg comparisons: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}\n" )

        row = ["select-comp", average] + selection_compares
        writer.writerow(row)

        average = statistics.mean(sort_time_for_each_sort_bubble)
        std_dev = statistics.stdev(sort_time_for_each_sort_bubble)
        print( f"Naive bubble\nAvg time: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["naive-time", average] + sort_time_for_each_sort_bubble
        writer.writerow(row)

        average = statistics.mean(swaps_for_each_sort_bubble)
        std_dev = statistics.stdev(swaps_for_each_sort_bubble)
        print( f"Avg swaps: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["naive-swap", average] + swaps_for_each_sort_bubble
        writer.writerow(row)

        average = statistics.mean(comparisons_for_each_sort_bubble)
        std_dev = statistics.stdev(comparisons_for_each_sort_bubble)
        print( f"Avg compares: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}\n" )

        row = ["naive-comp", average] + comparisons_for_each_sort_bubble
        writer.writerow(row)

        average = statistics.mean(sort_time_for_each_sort_rpe)
        std_dev = statistics.stdev(sort_time_for_each_sort_rpe)
        print( f"RPE\nAvg time: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["rpe-time", average] + sort_time_for_each_sort_rpe
        writer.writerow(row)

        average = statistics.mean(swaps_for_each_sort_rpe)
        std_dev = statistics.stdev(swaps_for_each_sort_rpe)
        print( f"Avg swaps: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["rpe-swap", average] + swaps_for_each_sort_rpe
        writer.writerow(row)

        average = statistics.mean(comparisons_for_each_sort_rpe)
        std_dev = statistics.stdev(comparisons_for_each_sort_rpe)
        print( f"Avg compares: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}\n" )

        row = ["rpe-comp", average] + comparisons_for_each_sort_rpe
        writer.writerow(row)

        average = statistics.mean(sort_time_for_each_sort_selection)
        std_dev = statistics.stdev(sort_time_for_each_sort_selection)
        print( f"RSD\nAvg time: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["rsd-time", average] + sort_time_for_each_sort_selection
        writer.writerow(row)

        average = statistics.mean(swaps_for_each_sort_selection)
        std_dev = statistics.stdev(swaps_for_each_sort_selection)
        print( f"Avg swaps: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["rsd-comp", average] + swaps_for_each_sort_selection
        writer.writerow(row)

        average = statistics.mean(comparisons_for_each_sort_selection)
        std_dev = statistics.stdev(comparisons_for_each_sort_selection)
        print( f"Avg compares: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}\n" )

        row = ["rsd-comp", average] + comparisons_for_each_sort_selection
        writer.writerow(row)

        average = statistics.mean(sort_time_for_each_sort_insertion)
        std_dev = statistics.stdev(sort_time_for_each_sort_insertion)
        print( f"RPX\nAvg time: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["rpx-time", average] + sort_time_for_each_sort_insertion
        writer.writerow(row)

        average = statistics.mean(swaps_for_each_sort_insertion)
        std_dev = statistics.stdev(swaps_for_each_sort_insertion)
        print( f"Avg swaps: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}" )

        row = ["rpx-swap", average] + swaps_for_each_sort_insertion
        writer.writerow(row)

        average = statistics.mean(comparisons_for_each_sort_insertion)
        std_dev = statistics.stdev(comparisons_for_each_sort_insertion)
        print( f"Avg compares: {average}  Standard Deviation: { std_dev}  CV: {(std_dev / average) * 100}\n" )

        row = ["rpx-comp", average] + comparisons_for_each_sort_insertion
        writer.writerow(row)
    return


if __name__ == "__main__":
    main(sys.argv[1:])