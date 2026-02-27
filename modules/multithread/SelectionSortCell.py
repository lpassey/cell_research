from modules.multithread.MultiThreadCell import MultiThreadCell, CellStatus
from .CellGroup import GroupStatus


class SelectionSortCell(MultiThreadCell):
    def __init__(self, threadID, value, lock, current_position, cells, left_boundary, right_boundary, status_probe, disable_visualization=False, swapping_count=[0], export_steps=[], label=0, reverse_direction=False):
        super().__init__(threadID, value, lock, current_position, cells, left_boundary, right_boundary, status_probe, disable_visualization=disable_visualization, swapping_count=swapping_count, export_steps=export_steps, reverse_direction=reverse_direction)
        if self.reverse_direction:
            self.ideal_position = right_boundary
        else:
            self.ideal_position = left_boundary
        self.cell_type = 'Selection'
        self.label = label


    def get_current_snapshot(self):
        return {"value": self.value, "group id": self.group.group_id, "group status": self.group.status, "cell status": self.status, "left": self.left_boundary, "right": self.right_boundary, "cell_type": self.cell_type, "cp": self.current_position[0], "ip": self.ideal_position[0],  "should_move": self.should_move(), "with_lock": self.with_lock}

    def within_boundary(self, pos): # checks if the target position is within the boundaries of this cell.
        if pos[0] > self.right_boundary[0] or pos[1] > self.right_boundary[1]:
            return False

        if pos[0] < self.left_boundary[0] or pos[1] < self.left_boundary[1]:
            return False

        return True

    def should_move(self):
        return self.current_position != self.ideal_position and self.within_boundary(self.ideal_position)

    def should_move_to(self, target_position):
        if self.within_boundary(target_position) and self.cells[int(target_position[0])].status == CellStatus.FREEZE:
            if self.reverse_direction:
                self.ideal_position = (self.ideal_position[0] - 1, self.ideal_position[1])
            else:
                self.ideal_position = (self.ideal_position[0] + 1, self.ideal_position[1])  # go ahead and move past frozen cells.
            self.status_probe.count_comparison()
            if self.value < self.cells[int(target_position[0])].value:
                self.swap(target_position) # OK to swap with frozen elements
            return False

        if (
            (    self.status == CellStatus.ACTIVE)
             and self.within_boundary(target_position)
            # and (
            #     self.cells[int(target_position[0])].ideal_position is None
            #     or self.cells[int(target_position[0])].current_position == self.cells[int(target_position[0])].ideal_position
            # )
            and self.current_position != self.ideal_position    # skip if I'm already where I want to be
            and self.cells[int(target_position[0])].status == CellStatus.ACTIVE #target position is active.

        ):
            # err_happen = random.random() < 0.00001
            # if err_happen:
            #     return not self.value > self.cells[int(target_position[0])].value
            self.status_probe.count_comparison()
            if self.value >= self.cells[int(target_position[0])].value: # am I larger than the target cell?
                if self.reverse_direction:
                    self.ideal_position = (self.ideal_position[0] - 1, self.ideal_position[1])
                else:
                    self.ideal_position = (self.ideal_position[0] + 1, self.ideal_position[1])
                return False
            return True # smaller than the target, ok to move.

        # if self.within_boundary(target_position) and self.cells[int(target_position[0])].status == CellStatus.FREEZE:
        #     return True

    def move_beside_freezed_cell(self, target_position):
        target_index = target_position[0]
        current_index = self.current_position[0]
        while current_index > target_index:
            self.swap((current_index - 1, self.current_position[1]), current_index - 1 != target_index)
            current_index -= 1

    def update(self):
        if self.reverse_direction:
            self.ideal_position = self.right_boundary
        else:
            self.ideal_position = self.left_boundary    # I always want to be at my left boundary, which starts at 0

    def move(self):
 #       self.lock.acquire()
        self.with_lock = True
        if self.group.status == GroupStatus.SLEEP and self.status != CellStatus.MOVING:
            self.status = CellStatus.SLEEP
        if self.should_move():
            self.status_probe.record_compare_and_swap()
        if self.should_move_to(self.ideal_position):
            cell_at_idea_position = self.cells[int(self.ideal_position[0])] # save the targeted cell
            if cell_at_idea_position.status == CellStatus.ACTIVE:   # if it's active, swap with it.
                self.swap(self.ideal_position)
            # elif cell_at_idea_position.status == CellStatus.FREEZE:
            #     cell_at_idea_position.ideal_position = (cell_at_idea_position.ideal_position[0] + 1, self.ideal_position[1])
            #     self.move_beside_freezed_cell(self.ideal_position)
#        self.lock.release()
        self.with_lock = False


