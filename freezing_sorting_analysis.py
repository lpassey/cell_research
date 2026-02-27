import sys, getopt
from tkinter import *
import threading
import time
from modules.multithread.StatusProbe import StatusProbe
from modules.multithread.SelectionSortCell import SelectionSortCell
from modules.multithread.BubbleSortCell import BubbleSortCell
from modules.multithread.InsertionSortCell import InsertionSortCell
from modules.multithread.MergeSortCell import MergeSortCell
from modules.multithread.CellGroup import CellGroup, GroupStatus
from modules.multithread.MultiThreadCell import CellStatus
from visualization.CellImage import CellImage
from visualization.CellGroupImage import CellGroupImage
import random
import copy
import numpy as np


# VALUE_LIST = [28, 34, 6, 20, 7, 89, 34, 18, 29, 51]
#VALUE_LIST = range(20,0,-1)

def create_cells_within_one_group(value_list, threadLock, status_probe, cell_type, frozen_cell_number):
    if len(value_list) == 0:
        return []
    left_boundary = (0, 1)
    right_boundary = (len(value_list) - 1, 1)
    cells = []
    for i in range(0, len(value_list)):
        cell = None
        if cell_type == 'rsd':
            cell = SelectionSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        if cell_type == 'rpe':
            cell = BubbleSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        if cell_type == 'rpx':
            cell = InsertionSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        """
             if used, this would allow a certain number of BubbleSortCells (or InsertionSortCells) to
              be included in an array of SelectionSortCells
        """
        # if random.random() <= bubble_sort_percentage:
        # cell = BubbleSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        # cell = InsertionSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        # else:
        #     cell = SelectionSortCell(i + 1, value_list[i], threadLock, (i, 1), cells, left_boundary, right_boundary, status_probe, disable_visualization=True)
        cells.append(cell)
    if cell_type == 'insertion':
        cells[0].enable_to_move = True

    period = 1000000000
    start_count_down = 1000000000
    cell_group = CellGroup(cells, cells, 0, left_boundary, right_boundary, GroupStatus.ACTIVE, threadLock, start_count_down, period)
    for cell in cells:
        cell.group = cell_group
    frozen = random.sample( range( len(cells)), frozen_cell_number )    # ensure that we have the requested number of unique frozen cells.
    for f in frozen:
        print(f"Freezing cell with value {cells[f].value} at position {cells[f].current_position}")
        cells[f].set_cell_to_freeze()
    return cells, [cell_group]

def print_current_status(cells):
    print([{"value": c.value, "group id": c.group.group_id, "group status": c.group.status, "cell status": c.status, "left": c.left_boundary, "right": c.right_boundary, "ideal position": c.ideal_position} for c in cells])

def is_sorted(cells):
    prev_cell = cells[0]
    for c in cells[1:]:
        if c.value < prev_cell.value:
            return False
        prev_cell = c
    return True

def print_status(cells):
    print([{"value": c.value, "group id": c.group.group_id, "group status": c.group.status, "cell status": c.status, "left": c.left_boundary, "right": c.right_boundary} for c in cells])

def kill_all_thread(cells, groups):
    for c in cells:
        c.status = CellStatus.INACTIVE

    for g in groups:
        g.status = GroupStatus.MERGED

def fetch_current_array(cells):
    return [c.value for c in cells]

def get_pos_success_rate(cells, frozen_cell_num):
    current_array = fetch_current_array(cells)
    expected_arr = copy.deepcopy(current_array)
    expected_arr.sort()
    at_expected_position = sum([1 if a == b else 0 for (a, b) in zip(expected_arr, current_array)])
    return (at_expected_position - frozen_cell_num) / (len(current_array) - frozen_cell_num)

def activate(cells, cell_groups):
    for cell in cells:
        cell.start()

    for group in cell_groups:
        group.start()


def get_pass_in_args(argv):
    cell_type = ""
    try:
        opts, args = getopt.getopt(argv, "h", ["cell_type="])
    except getopt.GetoptError:
        print("please specify cell type using '--cell_type='")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("multithread_cell_sorting.py --cell_type=<cell_type>")
            sys.exit()

        if opt == "--cell_type":
            cell_type = arg

    if not cell_type:
        print("please specify cell type using '--cell_type='")
        sys.exit(2)

    return cell_type

def main(argv):
    #cell_type = get_pass_in_args(argv)
    # success_sort_cnt = 0
    # pos_success_rate_arr = []
    # experiment_number = 20
    # frozen_cell_num = 3
    # cell_type = 'bubble'
    with open( 'csv/freezing_sorting_analysis.txt', 'w') as f:
        for cell_type in ['rpe','rsd', 'rpx']:
            for frozen_cell_num in [0, 1, 2, 3]:
                sorting_steps_for_each_run_bubble = []
                success_sort_cnt = 0
                pos_success_rate_arr = []
                experiment_number = 20
                random.seed(42)         # start every test suite from the same point
                for i in range(experiment_number):
                    sorting_list = []
                    for k in range(100):
                        sorting_list.append(random.randint(0, 100))     # duplicates are common, but typically less than 35%

                    threadLock = threading.Lock()
                    random.shuffle(sorting_list)    # redundant shuffle. Left in only to demonstrate the quality of programming
                    # print(f">>>>>>>>>>>>>>>>> Prepare cells to sort for {cell_type} experiment {i + 1} <<<<<<<<<<<<<<<<<<<<")
                    status_probe = StatusProbe()
                    cells, cell_groups = create_cells_within_one_group(sorting_list, threadLock, status_probe, cell_type, frozen_cell_num)
                    threadLock.acquire()
                    # print("Activating cells...")
                    activate(cells, cell_groups)
                    threadLock.release()

                    # shape = canvas.create_oval(30 - 20, 30 - 20, 30 + 20, 30 + 20, fill="white")
                    # text = canvas.create_text(30, 30, text="3")

                    # print("Start sorting......")
                    watchdog = 2000
                    time_started = time.time()
                    while not is_sorted(cells):
                        if time.time() > time_started + 20:     # stop if sortedness is not achieved in 20 seconds
                            break
                        # # print_current_status(cells)
                        time.sleep(.001)   # The original value of 1 was so large that for a sorted list tens of thousands of iterations would go by after the list is sorted.
                        # # print_status(cells)
                        # watchdog -= 1
                    if is_sorted(cells):
                        success_sort_cnt+=1
                    threadLock.acquire()
                    kill_all_thread(cells, cell_groups)
                    threadLock.release()
                    for c in cells:
                        c.join(2.5)    # added for deterministic teardown; does not alter sorting logic.

                    pos_success_rate_arr.append(get_pos_success_rate(cells, frozen_cell_num))

                    # print(">>>>>>>>>>>>>>>>> Sorting complete, killed all threads. <<<<<<<<<<<<<<<<<<<<\n")
                    #record all of the steps that occurred to get here
                    sorting_steps_for_each_run_bubble.append(status_probe.sorting_steps)
                # end for i in range(experiment_number):

                sorting_process_steps = np.array(sorting_steps_for_each_run_bubble, dtype=object)
                file_name = 'csv/' + cell_type + '_frozen_steps_' + str( frozen_cell_num )
                np.save(file_name , sorting_process_steps)

                f.write(f">>>>>>>>>>>>>>>>> Results for {cell_type} with {frozen_cell_num} frozen cells <<<<<<<<<<<<<<<<<<<<\n")
                f.write(f"Total experiments: {experiment_number}\n")
                f.write(f"Succeed sort: {success_sort_cnt}\n")
                f.write(f"Success rate: {success_sort_cnt / experiment_number  * 100} %\n")
                f.write(f"Pos success rate: {sum(pos_success_rate_arr) / len(pos_success_rate_arr)}\n" )
                f.write(f">>>>>>>>>>>>>>>>>------------------------------------------<<<<<<<<<<<<<<<<<<<<\n\n")
                f.flush()
                #end for frozen_cell_num in [ ... ]:
            # end for cell_type in ['bubble']:
        # end file open
    # end main

if __name__ == "__main__":
    main(sys.argv[1:])