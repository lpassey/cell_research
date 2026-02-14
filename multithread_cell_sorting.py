import sys, getopt
import threading
import time
from modules.multithread.MultiThreadCell import CellStatus
from modules.multithread.SelectionSortCell import SelectionSortCell
from modules.multithread.BubbleSortCell import BubbleSortCell
from modules.multithread.MergeSortCell import MergeSortCell
from modules.multithread.StatusProbe import StatusProbe


#VALUE_LIST = [28, 34, 6, 20, 7, 89, 34, 18, 29, 51]
VALUE_LIST = range(50,0,-1)

status_probe = StatusProbe()

class MonkeyGroup():
    def __init__(
            self,
            group_id,
            status,
     ):
        self.group_id = group_id
        self.status = status

def create_cells_based_on_value_list(value_list, cell_type, threadLock):
    if len(value_list) == 0:
        return []
    cells = []
    # looks like boundaries are tuples, for whatever reason
    for i in range(0, len(value_list)):
        cell = None
        if cell_type == "selection":
            cell = SelectionSortCell(i + 1, VALUE_LIST[i], threadLock, (i,1), cells, (0, 1), (len(VALUE_LIST) - 1, 1)
                                    , status_probe, disable_visualization=True  # added due to new signature
                                     )
        if cell_type == "bubble":
            cell = BubbleSortCell(i + 1, VALUE_LIST[i], threadLock, (i,1), cells, (0,1), (len(VALUE_LIST) - 1, 1)
                                  , status_probe, disable_visualization=True    # add due to new signature
                                  )
        if cell_type == "merge":
            cell = MergeSortCell(i + 1, VALUE_LIST[i], threadLock, i, cells, 0
#                                 , len(VALUE_LIST) - 1
                                 )
        if cell:
            cells.append(cell)

# start block -- required to make this thing runnable.
    cell_group = MonkeyGroup( 0, CellStatus.ACTIVE )
    for cell in cells:
        cell.group = cell_group
# end block
    return cells 

def print_current_list(cells):
    print([c.value for c in cells])
    #print([{"value": c.value, "group id": c.group_id, "status": c.status} for c in cells])


def activation_cells(cells):
    for cell in cells:
        cell.start()


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

def get_current_monotonicity(cells, lock ):    # calculate the total inversion count (TIC) of the list.
    monotonicity_value = 0
    with lock:
        prev_cell = cells[0]
        for c in cells:
            if c.value < prev_cell.value:
                monotonicity_value += 1
            prev_cell = c
    return monotonicity_value


def main(argv):
    cell_type = 'bubble'    # get_pass_in_args(argv)
    threadLock = threading.Lock()
    cells = create_cells_based_on_value_list(VALUE_LIST, cell_type, threadLock)
    threadLock.acquire()
    activation_cells(cells)
    threadLock.release()
    while 0 != get_current_monotonicity(cells, threadLock):
#    while True:        # will create an infinite loop, as there is no termination condition.
        print_current_list(cells)
        time.sleep(0.0001)
    for c in cells:     # kill active threads
        c.status = CellStatus.INACTIVE

if __name__ == "__main__":
    main(sys.argv[1:])