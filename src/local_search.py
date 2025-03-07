import random

from itertools import permutations
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
            best_neighbor = self._boxes if len(neighbors) == 0 else neighbors[0]
            if self._neighborhood._score_solution(
                best_neighbor
            ) > self._neighborhood._score_solution(self._boxes):
                self._boxes = best_neighbor
            else:
                break
        return self._boxes


class Neighborhood:
    def start(self, problem: OptimizationProblem):
        raise NotImplementedError()

    def generate_neighbors(self, solution):
        raise NotImplementedError()

    def _score_solution(self, solution):
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

        score = (
            -w_num_boxes * num_boxes
            + w_min_util * minimum_util
            + w_compact * avg_compactness
            - w_ir_gap * avg_irregular_gap
            + w_contiguity * avg_contiguity
        )
        return score


class GeometryBasedNeighborhood(Neighborhood):
    """
    1. We move rectangles to the different box or within the same box
    2. Swap with another rectangle
    3. Rotate the rectangle
    """

    def start(self, problem):
        """Each rectangle starts in its own box"""
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
        Generate a set of neighbor solutions by moving rectangles between boxes.
        Uses a scoring system to prioritize the most promising neighbors.
        """
        move_neighbors = self._move_rectangle(solution)

        all_neighbors = move_neighbors
        scored_neighbors = [
            (self._score_solution(neigh), neigh) for neigh in all_neighbors
        ]

        scored_neighbors.sort(reverse=True, key=lambda x: x[0])

        # Return the top N best neighbors (adjustable for efficiency)
        return [neigh for _, neigh in scored_neighbors[:30]]

    def _move_rectangle(self, solution):
        """
        Generate neighbors by moving rectangles between boxes.
        """
        neighbors = []
        new_solution: list[Box] = [box.copy() for box in solution]
        for j, targeted_box in enumerate(new_solution):
            remove_index = 0  # To adjust the index after removing a box
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

    def _score_solution(self, solution):
        """
        Scoring function for the geometry-based neighborhood.
        The score is calculated based on the number of boxes and the wasted space in the last box.
        """
        num_boxes = len(solution)
        last_box_wasted_space = solution[-1].get_space()
        score = 1000 - (num_boxes * 1000) - last_box_wasted_space

        return score


class RuleBasedNeighborhood(Neighborhood):
    def __init__(self):
        self._order = []

    def start(self, problem):
        presort = True
        self._order = problem.get_rectangles()
        if presort:
            # greedy_area = Greedy(problem, GreedyArea())
            # greedy_area.run()
            # solution = greedy_area.get_solution()
            self._order = sorted(
                self._order, key=lambda x: x.width * x.height, reverse=True
            )
        solution = [ShelfBox(problem.get_box_size())]
        for rectangle in self._order:
            placed = False
            for box in solution:
                placed = box.place(rectangle)
                if placed:
                    break
            if not placed:
                box = ShelfBox(problem.get_box_size())
                box.place(rectangle)
                solution.append(box)
        return solution

    def generate_neighbors(self, solution):
        # Generate neighbors by modifying the order of rectangles
        neighbors = []
        best_score = self._score_solution(solution)
        best_neighbor = solution
        length = len(self._order)
        box_size = solution[0].get_length()
        prev_order = self._order
        # section based permutation with 4 sections
        num_sections = 4
        section_size = length // num_sections
        sections = [
            prev_order[i * section_size : (i + 1) * section_size]
            for i in range(num_sections - 1)
        ]
        sections.append(prev_order[section_size * (num_sections - 1) :])
        new_orders = self._permutate(sections)
        # max 10 random swaps
        num_swaps = min(10, length - 1)  # Swap at most 10 pairs
        swap_indices = random.sample(range(length - 1), num_swaps)
        for i in swap_indices:
            # Swap two elements
            new_order = prev_order  # Create a copy before modifying
            new_order[i], new_order[i + 1] = new_order[i + 1], new_order[i]
            new_orders.append(new_order)

        for order in new_orders:
            fresh_order = [deepcopy(rect) for rect in order]
            new_neighbor = [ShelfBox(box_size)]
            for rectangle in fresh_order:
                placed = False
                for box in new_neighbor:
                    placed = box.place(rectangle)
                    if placed:
                        break
                if not placed:
                    box = ShelfBox(box_size)
                    box.place(rectangle)
                    new_neighbor.append(box)
            # only save neighbor if it is better
            score = self._score_solution(new_neighbor)
            if score > best_score:
                best_score = score
                best_neighbor = new_neighbor
                self._order = order
        neighbors.append(best_neighbor)
        return neighbors

    def _permutate(self, sections):
        def permute(arr, start=0):
            if start == len(arr) - 1:
                result.append(deepcopy(arr))  # Store a copy to avoid mutations
            else:
                for i in range(start, len(arr)):
                    arr[start], arr[i] = arr[i], arr[start]  # Swap
                    permute(arr, start + 1)  # Recursively permute remaining
                    arr[start], arr[i] = arr[i], arr[start]  # Swap back

        result = []
        permute(sections)
        # Flatten the permutations before returning
        return [[rect for section in perm for rect in section] for perm in result]


class PartialOverlapNeighborhood(Neighborhood):
    def start(self, problem):
        objects = problem.get_rectangles()
        box_size = problem.get_box_size()
        solution = [Box(box_size)]
        for object in objects:
            solution[0].place_no_check(object)
        return solution

    def generate_neighbors(self, solution):
        # Generate neighbors with partial overlaps
        neighbors = []
        # Add logic to handle overlaps
        return neighbors
