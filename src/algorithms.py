from structs import *
from shelf_box import *
import numpy as np
import sys

sys.setrecursionlimit(1111) # the maximal limit for recursion is 1000

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
        return len(boxes)  # Lower is better

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


class Backtracking:
    def __init__(self, problem=None):
        if problem is None:
            pass
        else:
            self.problem = problem
            self.best_solution = None
            self.best_score = 0
            self._boxes = [Box(self.problem.get_box_size())]
            self.placed_rectangles = set()  # To keep track of placed rectangles
            self.visited = set()  # To track visited states

    def objective_function(self, boxes):
        """Objective function to evaluate the number of boxes used."""
        # return len(boxes)
        return boxes[-1].get_space()

    def can_place_rectangle(self, box, rectangle):
        """Check if a rectangle can be placed in a given box without overlap."""
        for coordinate in box._coordinates:
            x, y = coordinate
            if box.can_place(rectangle, x, y):
                return True
        return False

    def place_rectangle(self, box, rectangle):
        """Place the rectangle in the box if possible."""
        for coordinate in box._coordinates:
            x, y = coordinate
            if box.can_place(rectangle, x, y):
                box.place(rectangle)
                return True
        return False

    def backtrack(self, index=0, rectangles=None, boxes_local=None):
        """Perform backtracking to place all rectangles."""
        if index == len(self.problem.get_rectangles()):
            score = self.objective_function(boxes_local)
            if score >= self.best_score:
                self.best_score = score
                self.best_solution = boxes_local # [box.copy() for box in self._boxes]
                self._boxes = [box.copy() for box in boxes_local]
            return

        # Get the rectangle to place
        rectangle = rectangles[index] # self.problem.get_rectangles()[index]
        is_placed = False
        # Try to place the rectangle in existing boxes
        for box in boxes_local:
            if self.can_place_rectangle(box, rectangle):
                # Place the rectangle and try the next one with recursion
                box.place(rectangle)
                is_placed = True
                self.backtrack(index + 1, rectangles, boxes_local)
            if is_placed:
                break

        self._boxes = boxes_local # just for displaying

        if not is_placed:
        # If the rectangle can't be placed in any existing box, create a new box
            new_box = Box(self.problem.get_box_size())
            new_box.place(rectangle)
            boxes_local.append(new_box)
            self.backtrack(index + 1, rectangles, boxes_local)

    def run(self):
        """Run the backtracking algorithm to minimize the number of boxes."""

        # we create the idea of tree and then we choose which branch is the most efficient (best_score)
        # if len(self.problem.get_rectangles()) > 5:
        #     iteration = 2
        # else:
        #     iteration = len(self.problem.get_rectangles())

        #for x in range(0, iteration):
        rectangles = self.problem.get_rectangles_random()
        boxes_local = [Box(self.problem.get_box_size())]
            # if self.best_solution is not None: self._boxes = self.best_solution
        self.backtrack(0, rectangles, boxes_local)

        return self.best_solution
