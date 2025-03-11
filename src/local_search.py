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
            best_neighbor = self._boxes if len(neighbors) ==0 else neighbors[0]
            if self._neighborhood._score_solution(best_neighbor) > self._neighborhood._score_solution(self._boxes):
                self._boxes = best_neighbor
            else:
                print(self._neighborhood)
                if isinstance(self._neighborhood, PartialOverlapNeighborhood):
                    if self._neighborhood.iteration < self._neighborhood.max_iterations:
                        self._neighborhood.iteration = self._neighborhood.max_iterations
                        continue
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
        w_min_util = 0
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
            # box = ShelfBox(box_size) # much faster
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
        # new_solution: list[ShelfBox] = [box.copy() for box in solution] much faster
        new_solution: list[Box] = [box.copy() for box in solution]
        for j, targeted_box in enumerate(new_solution):
            remove_index = 0  # To adjust the index after removing a box
            # (e.g, if a box is removed, the index of the next box will be reduced by 1 not by 2)
            for i, source_box in enumerate(reversed(new_solution)):
                # to enumerate from the end of the list
                real_index = len(new_solution) - 1 - i + remove_index
                if real_index == j:
                    continue
                # if real_index is smaller it doesn't make sense to move the 
                # rectangles to j because it was already checked
                if j >= real_index:
                    break
                rect = source_box.get_rectangles()[-1]

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
        result = []
        for i in range(len(sections)):
            for j in range(len(sections)):
                new_neighbor = sections[:]
                new_neighbor[i], new_neighbor [j] = new_neighbor[j], new_neighbor[i]
                result.append(new_neighbor)

        # Flatten the permutations before returning
        return [[rect for section in perm for rect in section] for perm in result]


class PartialOverlapNeighborhood(Neighborhood):
    """
    A neighborhood that initially allows partial overlaps up to 100%
    (i.e., the entire rectangle can overlap), but gradually tightens
    the overlap threshold down to 0%. Any overlap beyond the current
    threshold is heavily penalized in the scoring function, thus
    guiding the local search to eventually eliminate overlaps.
    """

    def __init__(self, max_iterations=10):
        """
        :param max_iterations: how many improvement iterations we allow
               before the overlap tolerance is forced to 0.
        """
        super().__init__()
        self.iteration = 0
        self.max_iterations = max_iterations
        # Start at 100% overlap allowed and end at 0%.
        self.current_tolerance = 1.0

    def start(self, problem, better_start = False):
        """
        Put all rectangles in a single box without checking overlaps.
        This creates the initial 'fully-overlapped' solution, which
        is easy (scoring) at 100% tolerance but will get harder as
        we reduce the tolerance.
        """
        objects = problem.get_rectangles()
        box_size = problem.get_box_size()
        solution = [Box(box_size)]

        for obj in objects:
            solution[0].place_no_check(obj)
        solution[0]._coordinates.add((problem._max_size, problem._max_size))
        self.iteration = 0
        self.current_tolerance = 1.0  # 100% overlap allowed at the start
        if solution[0].get_space() > 0:
            self.iteration = self.max_iterations
        return solution

    def generate_neighbors(self, solution):
        """
        Generate neighbors by attempting random "moves" of rectangles
        between boxes or within the same box. Each neighbor is evaluated
        with the scoring function that includes an overlap penalty.
        Overlap tolerance is gradually reduced each iteration.
        """
        neighbors = []
        self.iteration += 1
        print("iteration", self.iteration)
        # We reduce the allowable overlap linearly over the iterations.
        # Once iteration >= max_iterations, tolerance is 0 => must be overlap-free.
        if self.iteration < self.max_iterations:
            step = 1.0 / self.max_iterations
            self.current_tolerance = max(0.0, 1.0 - self.iteration * step)
            print(self.current_tolerance)
        else:
            self.current_tolerance = 0.0
        # Produce a handful of neighbors by randomly moving rectangles.
        # (You can refine or optimize how many neighbors you generate.)

        # Flatten all boxes' rectangles for easy indexing
        scored_boxes = []
        rect_count = 0
        for b_idx, b in enumerate(solution):
            rects = b.get_rectangles()
            scored_rects = []
            box_overlap = 0
            for i in range(len(rects)):
                rect_count += 1
                rect_overlap = 0
                for j in range(i + 1, len(rects)):
                    r1 = rects[i]
                    r2 = rects[j]
                    rect_overlap += self._calc_overlap_area(r1, r2)
                box_overlap += rect_overlap
                scored_rects.append((rect_overlap, i))
            sorted_rects = sorted(scored_rects, key=lambda x: x[0], reverse = True)
            scored_boxes.append((box_overlap, b_idx, sorted_rects))
        sorted_boxes = sorted(scored_boxes, key=lambda x: (x[0], -len(x[2])), reverse = True)
        if self.current_tolerance>0.001:
            num_moves = min(20, len(sorted_boxes))
            for i in range(num_moves):
                new_solution = deepcopy(solution)
                source_box_idx = sorted_boxes[i][1]
                source_box = new_solution[source_box_idx]
                moved_idx = 0
                rects = source_box.get_rectangles()
                num_rects_moved =  len(rects)//self.iteration
                for _ in range(num_rects_moved):
                    #select the rect with most overlap
                    print("new-rect")
                    sorted_rects = sorted_boxes[i][2]
                    rect = rects[sorted_rects[moved_idx][1]]
                    # remove that rectangle
                    source_box.remove_rectangle(rect, False)
                    #adjust index
                    for j in range(len(sorted_rects)):
                        if sorted_rects[j][1] > sorted_rects[moved_idx][1]:
                            sorted_rects[j] = (sorted_rects[j][0],sorted_rects[j][1] - 1)
                    moved_idx += 1
                    #give option to expand
                    print(compute_min_utilization(new_solution))
                    print(rect.height*rect.width)
                    box_size = solution[0].get_length()
                    box_area = box_size*box_size
                    if (compute_min_utilization(new_solution) +
                            ((rect.height * rect.width) / box_area))>0.8:
                        new_solution.append(Box(box_size))
                    placed = False
                    counter = 0
                    # pick a random target box, if same, get a different one
                    while not placed:
                        target_box_idx = random.randint(0, len(new_solution) - 1)
                        while target_box_idx == source_box_idx:
                            target_box_idx = random.randint(0, len(new_solution) - 1)
                        target_box = new_solution[target_box_idx]
                        placed = target_box.place(rect, False)
                        if not placed:
                            counter += 1
                        if counter > 100:
                            rect.x, rect.y = (0,0)
                            target_box.place_no_check(rect)
                            placed = True
                    # If source box is now empty, remove it

                    if len(source_box.get_rectangles()) == 0:
                        new_solution.remove(source_box)
                    if len(new_solution[-1].get_rectangles()) == 0:
                        new_solution.remove(new_solution[-1])

                neighbors.append(new_solution)
            # Sort neighbors by the new scoring function (including overlap penalty)
            scored_neighbors = [(self._score_solution(n), n) for n in neighbors]
            scored_neighbors.sort(reverse=True, key=lambda x: x[0])
            return [neigh for _, neigh in scored_neighbors[:num_moves]]
        else:
            new_solution = deepcopy(solution)
            problem_rects = []
            for sb_data in sorted_boxes:
                if sb_data[0] == 0:
                    break
                source_box_idx = sb_data[1]
                source_box = new_solution[source_box_idx]
                rects = source_box.get_rectangles()
                sorted_rects = sb_data[2]
                r_data = sorted_rects[0]
                while r_data[0] != 0:
                    rectangle = rects[r_data[1]]
                    problem_rects.append(rectangle)
                    source_box.remove_rectangle(rectangle)
                    scored_rects = []
                    for i in range(len(rects)):
                        rect_count += 1
                        rect_overlap = 0
                        for j in range(i + 1, len(rects)):
                            r1 = rects[i]
                            r2 = rects[j]
                            rect_overlap += self._calc_overlap_area(r1, r2)
                        #overlap_ratio = rect_overlap/rects[i].height * rects[i].width
                        scored_rects.append((rect_overlap, i))
                    sorted_rects = sorted(scored_rects, key=lambda x: x[0], reverse=True)
                    r_data = sorted_rects[0]
            for rect in problem_rects:
                box_size = new_solution[0].get_length()
                placed = False
                for box in new_solution:
                    placed = box.place(rect)
                    if placed: break
                if not placed:
                    for box in new_solution:
                        rect.rotate()
                        placed = box.place(rect)
                        if placed: break
                if not placed:
                    box = Box(box_size)
                    box.place(rect)
                    new_solution.append(box)
            neighbors.append(new_solution)
            return neighbors




    def _score_solution(self, solution):
        """
        Inherits the base scoring (min utilization, etc.) and adds
        a heavy penalty if a pair of rectangles exceeds the current
        overlap tolerance. Overlap ratio = (area_intersect) / (max_area_of_two).

        If ratio <= current_tolerance, we do not penalize it.
        If ratio >  current_tolerance, penalize heavily so that
        the solution is forced to reduce these overlaps as tolerance shrinks.
        """
        base_score = super()._score_solution(solution)
        #box_length = solution[0].get_length()
        #box_area = box_length * box_length
        #base_score = (-len(solution)*1000
        #              +(solution[len(solution)-1].get_space()/box_area))

        # big constant factor to heavily penalize large overlaps
        overlap_penalty_factor = 1000000
        total_penalty = 0.0
        for box in solution:
            rects = box.get_rectangles()
            for i in range(len(rects)):
                for j in range(i + 1, len(rects)):
                    r1 = rects[i]
                    r2 = rects[j]
                    overlap_area = self._calc_overlap_area(r1, r2)
                    if overlap_area == 0:
                        continue
                    bigger_rect_area = max(r1.width * r1.height, r2.width * r2.height)
                    overlap_ratio = overlap_area / float(bigger_rect_area)

                    # If this ratio is beyond current_tolerance => penalize
                    if overlap_ratio > self.current_tolerance:
                        violation = overlap_ratio - self.current_tolerance
                        total_penalty += violation * overlap_penalty_factor
        return base_score - total_penalty

    def _calc_overlap_area(self, r1, r2):
        """
        Returns the overlap area between rectangles r1 and r2.
        If they do not overlap, returns 0.
        """
        overlap_width = max(
            0, min(r1.x + r1.width, r2.x + r2.width) - max(r1.x, r2.x)
        )
        overlap_height = max(
            0, min(r1.y + r1.height, r2.y + r2.height) - max(r1.y, r2.y)
        )
        return overlap_width * overlap_height


