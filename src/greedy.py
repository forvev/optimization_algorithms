# from main import OptimizationProblem
from structs import *
import numpy as np

# Greedy Algorithm
class Greedy:
    def __init__(self, problem, strategy):
        self.problem = problem
        self.strategy = strategy
        self._boxes = [Box(self.problem.get_box_size())]

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

# Strategy Implementations for Greedy; 1 by area, 2 by perimeter
class GreedyArea:
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width * x.height, reverse=True)

class GreedyPerimeter:
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width + x.height, reverse=True)
