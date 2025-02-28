from src.main import OptimizationProblem
from src.structs import *

# Greedy Algorithm
class Greedy:
    def __init__(self, problem: OptimizationProblem, strategy):
        self.problem = problem
        self.strategy = strategy

    def run(self):
        rectangles = self.problem.get_rectangles()
        sorted_rectangles = self.strategy.generate_order(rectangles)
        boxes = [Box(self.problem.get_box_size())]

        # Apply the strategy to place rectangles
        for rectangle in sorted_rectangles:
            self.place_rectangle(boxes, rectangle)
        return boxes

    def place_rectangle(self, boxes, rectangle):
        placed = False
        for box in boxes:
            placed = box.place(rectangle)
            if placed: break
        if not placed:
            boxes.append(Box(self.problem.get_box_size()).place(rectangle))


# Strategy Implementations for Greedy; 1 by area, 2 by perimeter
class GreedyArea:
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width * x.height, reverse=True)

class GreedyPerimeter:
    def generate_order(self, solution):
        return sorted(solution, key=lambda x: x.width + x.height, reverse=True)
