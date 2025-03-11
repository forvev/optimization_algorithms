from structs import *
from shelf_box import *
import numpy as np

# Greedy Algorithm
class Greedy:
    def __init__(self, problem, strategy):
        self.problem = problem
        self.strategy = strategy
        self._boxes = []

    def run(self):
        rectangles = self.problem.get_rectangles()
        sorted_rectangles = self.strategy.generate_order(rectangles)
        # boxes = [Box(self.problem.get_box_size())]

        # Apply the strategy to place rectangles
        for rectangle in sorted_rectangles:
            self.place_rectangle(rectangle)
        # return boxes

    def place_rectangle(self, rectangle):
        placed = False
        for box in self._boxes:
            placed = box.place(rectangle)
            if placed: break
        if not placed:
            # boxes.append(Box(self.problem.get_box_size()).place(rectangle))
            box = Box(self.problem.get_box_size())
            box.place(rectangle)
            self._boxes.append(box)

    def fast_place_rectangle(self, rectangle):
        placed = False
        for box in self._boxes:
            placed = box.place(rectangle)
            if placed: break
        if not placed:
            box = ShelfBox(self.problem.get_box_size())
            box.place(rectangle)
            self._boxes.append(box)

    def get_solution(self):
        return self._boxes

# Strategy Implementations for Greedy; 1 by area, 2 by perimeter
class GreedyArea:
    """
    Greedy strategy to sort the rectangles by area. The rectangles are sorted in decreasing order of area.
    """
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width * x.height, reverse=True)

class GreedyPerimeter:
    """
    Greedy strategy to sort the rectangles by perimeter. The rectangles are sorted in decreasing order of perimeter.
    """
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width + x.height, reverse=True)
