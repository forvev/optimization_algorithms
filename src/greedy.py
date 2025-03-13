from structs import *
from shelf_box import *

# Greedy Algorithm
class Greedy:
    def __init__(self, problem, strategy):
        self.problem = problem
        self.strategy = strategy
        self._boxes = []

    def run(self):
        objects = self.strategy.start(self.problem)
        sorted_objects = self.strategy.generate_order(objects)

        # Apply the strategy to place rectangles
        if isinstance(self.strategy, GreedyArea) or isinstance(self.strategy, GreedyPerimeter):
            for rectangle in sorted_objects:
                self.place_rectangle(rectangle)
            # return boxes
            return self._boxes

        return sorted_objects

    def place_rectangle(self, rectangle):
        placed = False
        for box in self._boxes:
            placed = box.place(rectangle)
            if placed: break
        if not placed:
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
    def start(self, problem):
        return problem.get_rectangles()
    """
    Greedy strategy to sort the rectangles by area. The rectangles are sorted in decreasing order of area.
    """
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width * x.height, reverse=True)

class GreedyPerimeter:
    def start(self, problem):
        return problem.get_rectangles()
    """
    Greedy strategy to sort the rectangles by perimeter. The rectangles are sorted in decreasing order of perimeter.
    """
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width + x.height, reverse=True)
