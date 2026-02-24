import sys
import threading
import time
from modules.multithread.MultiThreadCell import MultiThreadCell

#VALUE_LIST = [28, 34, 6, 20, 7, 89, 34, 18, 29, 51]
VALUE_LIST = range(50,0,-1)     # build a list of 50 integers in reverse numeric order.

threadLock = threading.Lock()

def create_cells_based_on_value_list(value_list):
    if len(value_list) == 0:
        return []
    cells = []
    start_cell = MultiThreadCell(0, 0, threadLock, -1,
#                                 cells, 0, 0, None
            )    # last 4 parameters added
    """
    The new definition of MultiThreadCell:
    
     def __init__(
        self,
        threadID,
        value,
        lock,
        current_position,
        cells,
        left_boundary,
        right_boundary,
        status_probe,
        cell_vision=1,
        disable_visualization=False,
        swapping_count=[0],
        export_steps=[],
        reverse_direction=False
    ):
    """
    current_cell = start_cell
    for i in range(0, len(value_list)):
        cell = MultiThreadCell(i + 1, VALUE_LIST[i], threadLock, i,
#                               cells, 0, 0, None
                )    # last 4 parameters added
        cells.append(cell)
        cell.left_neighbor = current_cell   # monkey patch
        current_cell.right_neighbor = cell  # a cell has a right neighbor only because we added it here,
        # not because it is defined that way. We need to be sure every cell has a right neighbor.
#        cell.right_neighbor = None
        current_cell = cell
    return cells, start_cell 

def get_values_as_arr(start_ptr):   # convert the list of cells to an array of values
    # be sure value is defined as an integer; in some implementations it is defined as a tuple
    p = start_ptr.right_neighbor
    values = []
    while p:
        values.append(p.value)
        p = p.right_neighbor
    return values

def print_current_list(start_ptr):
    threadLock.acquire()    # don't let anyone modify the list while I'm extracting the array.
    values = get_values_as_arr(start_ptr)
    print(values)
    threadLock.release()


def sort_cells(cells, start_ptr):
    for cell in cells:  # start a bunch of threads that will spin endlessly
        cell.start()


def get_current_monotonicity(arr, index):    # calculate the total inversion count (TIC) of the list.
    monotonicity_value = 0
    prev = arr[0][index]
    for i in range(1, len(arr)):
        if arr[i][index] < prev:
            monotonicity_value += 1
        prev = arr[i][index]
    return monotonicity_value

def main(argv):
    cells, start_ptr = create_cells_based_on_value_list(VALUE_LIST) # VALUE_LIST is hand_coded and not randomized.
    # revers order is generally considered worst case scenario
    sort_cells(cells, start_ptr)    # doesn't sort, just starts threads.
    while True:     # replace with while 0 != get_current_monotonicity, currently unused.
        print_current_list(start_ptr)
        time.sleep(0.0001) # should probably be longer so sort threads are not starved

if __name__ == "__main__":
    main(sys.argv[1:])