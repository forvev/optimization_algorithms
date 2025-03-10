from structs import *
from shelf_box import *
import numpy as np
import math
import random


# Simulated Annealing Algorithm
class SimulatedAnnealing:
    def __init__(self, problem=None, initial_temp=1000, cooling_rate=0.99):
        if problem is None:
            pass
        else:
            self.problem = problem
            self.temperature = initial_temp
            self.cooling_rate = cooling_rate
            self.iterations = len(problem._rectangles)
            self._boxes = [Box(self.problem.get_box_size())]
            self.best_solution = None
            self.best_score = float("inf")

    def objective_function(self, boxes):
        """Evaluate the placement by measuring remaining free space and overlap."""
        return sum(box.get_space() for box in boxes)  # Lower is better

    def random_perturbation(self, boxes):
        """Modify the placement by moving or rotating a rectangle."""
        if any(box.get_rectangles() for box in boxes):
            return boxes

        new_boxes = [box.copy() for box in boxes]
        # randomly select some solutions that are feasible
        box = np.random.choice(new_boxes)
        rect = np.random.choice(box.get_rectangles())
        box.remove_rectangle(rect)

        # Try placing it at a new random location or rotated
        rect.rotate() if np.random.random() < 0.5 else None
        placed = any(b.place(rect) for b in new_boxes)

        # If placement fails, revert rotation and retry
        if not placed:
            rect.rotate()
            any(b.place(rect) for b in new_boxes)

        return new_boxes

    def run(self):
        """Execute the simulated annealing algorithm."""
        for rect in self.problem.get_rectangles():
            self.place_rectangle(rect)

        current_solution = self._boxes
        current_score = self.objective_function(self._boxes)

        for i in range(self.iterations):
            new_solution = self.random_perturbation(current_solution)
            new_score = self.objective_function(new_solution)

            delta = new_score - current_score

            # if <0 it means that the solution is better. However, to avoid getting stuck in
            # the local optima, we might still accept the positive delta with some probabilities.
            # As the temperature lowers, the probability to be accepted decreases
            if delta < 0 or np.random.random() < np.exp(-delta / self.temperature):
                current_solution, current_score = new_solution, new_score

                if new_score < self.best_score:
                    self.best_solution, self.best_score = new_solution, new_score

            self.temperature *= self.cooling_rate
            if self.temperature < 1e-6:
                break

        return self.best_solution

    def place_rectangle(self, rectangle):
        placed = False
        for box in self._boxes:
            placed = box.place(rectangle)
            if placed:
                break
        if not placed:
            box = Box(self.problem.get_box_size())
            box.place(rectangle)
            self._boxes.append(box)

    def get_solution(self):
        return self.best_solution if self.best_solution else self._boxes

from structs import *
from shelf_box import *
import numpy as np

# Backtracking Algorithm
class Backtracking:
    def __init__(self, problem=None):
        if problem == None:
            pass
        else:
            self.problem = problem
            self._boxes = [Box(self.problem.get_box_size())]
            self.best_solution = None
            self.best_score = float("inf")

    def objective_function(self, boxes):
        """Evaluate the placement by measuring remaining free space."""
        return sum(box.get_space() for box in boxes)  # Lower is better

    def backtrack(self, index, boxes):
        """Recursive backtracking approach to find an optimal placement."""
        if index == len(self.problem.get_rectangles()):
            score = self.objective_function(boxes)
            if score < self.best_score:
                self.best_solution = [box.copy() for box in boxes]
                self.best_score = score
            return

        rectangle = self.problem.get_rectangles()[index]
        placed = False
        for box in boxes:
            if box.place(rectangle):
                self.backtrack(index + 1, boxes)
                box.remove_rectangle(rectangle)
                placed = True

        # If no placement is found, add a new box (but only if necessary)
        if not placed and len(boxes) < len(self.problem.get_rectangles()):
            new_box = Box(self.problem.get_box_size())
            if new_box.place(rectangle):
                boxes.append(new_box)
                self.backtrack(index + 1, boxes)
                boxes.pop()

    def run(self):
        """Start the backtracking algorithm."""
        self.backtrack(0, self._boxes)
        return self.best_solution

    def get_solution(self):
        return self.best_solution if self.best_solution else self._boxes
