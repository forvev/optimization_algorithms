import random

from structs import *
from greedy import *
from copy import deepcopy
from scoring import *

# Local Search Algorithm
class LocalSearch:
    def __init__(self, optimization_problem: OptimizationProblem, neighborhood):
        self._problem = optimization_problem
        self._neighborhood = neighborhood
        self._boxes = [Box(self._problem.get_box_size())]

    def run(self):
        self._boxes = self._neighborhood.start(self._problem)
        # Perform the search by iterating through neighbors
        while True:
            neighbors = self._neighborhood.generate_neighbors(self._boxes)
            best_neighbor = self._boxes if len(neighbors) ==0 else neighbors[0]
            if self._neighborhood.evaluate(best_neighbor) > self._neighborhood.evaluate(self._boxes):
                print(self._neighborhood.evaluate(best_neighbor))
                print("selecting better neighbor")
                self._boxes = best_neighbor
            else:
                break
        return self._boxes


class Neighborhood:
    def start(self, problem: OptimizationProblem):
        raise NotImplementedError()

    def generate_neighbors(self, solution):
        raise NotImplementedError()

    def evaluate(self, solution):
        # get relevant infos
        num_boxes = len(solution)
        minimum_util = compute_min_utilization(solution)
        avg_compactness = compute_average_compactness(solution)
        avg_irregular_gap = compute_average_irregular_gap_penalty(solution)
        avg_contiguity = compute_average_contiguity(solution)

        # weights
        w_num_boxes = 1000
        w_min_util = 150
        w_compact = 100
        w_ir_gap = 100
        w_contiguity = 50

        score = (- w_num_boxes * num_boxes + w_min_util * minimum_util
                 + w_compact * avg_compactness - w_ir_gap * avg_irregular_gap
                 + w_contiguity * avg_contiguity)
        return score

class GeometryBasedNeighborhood(Neighborhood):
    """
        1. We move rectangles to the different box or within the same box
        2. Swap with another rectangle
        3. Rotate the rectangle
    """
    def start(self, problem):
        """ Each rectangle starts in its own box """
        objects = problem.get_rectangles()
        box_size = problem.get_box_size()
        solution = []
        for object in objects:
            box = Box(box_size)
            box.place(object)
            solution.append(box)
        return solution

    def generate_neighbors(self, solution):
        """
        Generate a set of neighbor solutions by moving, swapping, or rotating rectangles.
        Uses a scoring system to prioritize the most promising neighbors.
        """
        neighbors = []
        # Generate different types of neighbors
        move_neighbors = self._move_rectangle(solution)
        # swap_neighbors = self._swap_rectangles(solution)

        all_neighbors = move_neighbors# + swap_neighbors + rotate_neighbors
        scored_neighbors = [(self.evaluate(neigh), neigh) for neigh in all_neighbors]
        scored_neighbors.sort(reverse=True, key=lambda x: x[0])

        # Return the top N best neighbors (adjustable for efficiency)
        return [neigh for _, neigh in scored_neighbors[:10]]

    def _move_rectangle(self, solution):
        # """ Move a rectangle from one box to another if space allows """
        neighbors = []
        new_solution: list[Box] = deepcopy(solution)
        for j, targeted_box in enumerate(new_solution):
            remove_index = 0 # To adjust the index after removing a box
            # (e.g, if a box is removed, the index of the next box will be reduced by 1 not by 2)
            for i, source_box in enumerate(reversed(new_solution)):
                # to enumerate from the end of the list
                real_index = len(new_solution) - 1 - i + remove_index
                if real_index == j:
                    continue
                # if real_index is smaller it doesn't make sense to move the rectangles to j because it was already checked
                if j >= real_index:
                    break
                for rect_num, rect in enumerate(source_box.get_rectangles()):
                    if new_solution[j].place(rect):
                        new_solution[real_index].remove_rectangle(rect)
                    else:
                        continue
                    # If the source box becomes empty, remove it
                    if new_solution[real_index].get_rectangles() == []:
                        new_solution.pop(real_index)
                        remove_index += 1

                    # Add the modified solution as a neighbor
                    neighbors.append(new_solution)
        return neighbors

    #todo: maybe I should evaluate the score of the solution after each move comparing the current solution?
    # def _swap_rectangles(self, solution):
    #     """ Swap two rectangles between different boxes if it improves the packing efficiency. """
    #     neighbors = []
    #     new_solution = deepcopy(solution)

    #     num_boxes = len(new_solution)

    #     # Iterate over all pairs of boxes
    #     for i in range(num_boxes):
    #         for j in range(i + 1, num_boxes):  # Avoid redundant swaps
    #             box1, box2 = new_solution[i], new_solution[j]

    #             for rect1 in box1.get_rectangles():
    #                 for rect2 in box2.get_rectangles():
    #                     # Swap only if they fit better
    #                     if box1.can_place(rect2, rect1.x, rect1.y) and box2.can_place(rect1, rect2.x, rect2.y):
    #                         # Create a new solution variant
    #                         swapped_solution = deepcopy(new_solution)
    #                         swapped_solution[i].remove_rectangle(rect1)
    #                         swapped_solution[j].remove_rectangle(rect2)

    #                         swapped_solution[i].place(rect2)
    #                         swapped_solution[j].place(rect1)

    #                         # Evaluate new solution
    #                         if self._score_solution(swapped_solution) > self._score_solution(new_solution):
    #                             neighbors.append(swapped_solution)

    #     return neighbors

    def evaluate(self, solution):
        num_boxes = len(solution)
        total_wasted_space = sum(box.get_space() for box in solution)
        score = 1000 - (num_boxes * 50) - total_wasted_space

        return score


class RuleBasedNeighborhood(Neighborhood):
    def __init__(self):
        self._order = []

    def start(self, problem):
        greedy_area = Greedy(problem, GreedyArea())
        greedy_area.run()
        solution = greedy_area.get_solution()
        self._order = sorted(problem.get_rectangles(),
                             key=lambda x: x.width * x.height, reverse=True)
        return solution

    def generate_neighbors(self, solution):
        # Generate neighbors by modifying the order of rectangles
        neighbors = []
        best_score = self.evaluate(solution)
        best_neighbor = solution
        length = len(self._order)
        box_size = solution[0].get_length()
        prev_order = self._order
        #randomly permutate order of elements
        for i in range(length-1):
            shift = random.randint(0, length -1 - i)
            new_order = prev_order
            new_order[i], new_order[i + 1] = new_order[i + 1], new_order[i]
            #each permutation creates a new neighbor
            new_neighbor = [ShelfBox(box_size)]
            for rectangle in new_order:
                placed = False
                for box in new_neighbor:
                    placed = box.place(rectangle)
                    if placed: break
                if not placed:
                    box = ShelfBox(box_size)
                    box.place(rectangle)
                    new_neighbor.append(box)
                #only save neighbor if it is better
                score = self.evaluate(new_neighbor)
                if score < best_score:
                    best_score = score
                    best_neighbor = new_neighbor
                    self._order = new_order
        neighbors.append(best_neighbor)
        return neighbors



class PartialOverlapNeighborhood(Neighborhood):
    def generate_neighbors(self, solution):
        # Generate neighbors with partial overlaps
        neighbors = []
        # Add logic to handle overlaps
        return neighbors

    def start(self, problem):
        objects = problem.get_rectangles()
        box_size = problem.get_box_size()
        solution = [Box(box_size)]
        for object in objects:
            solution[0].place_no_check(object)
        return solution