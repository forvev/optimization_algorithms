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


# Strategy Implementations for Greedy
class GreedyArea:
    def generate_order(self, solution):
        # Generate order based on a simple greedy approach (e.g., largest first)
        return sorted(solution, key=lambda x: x.width * x.height, reverse=True)

class GreedyPerimeter:
    def generate_order(self, solution):
        # Use a more advanced greedy strategy
        return sorted(solution, key=lambda x: x.width + x.height, reverse=True)
