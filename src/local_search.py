from main import OptimizationProblem
from structs import *
from greedy import *
from copy import deepcopy

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
            best_neighbor = self._boxes if len(neighbors) ==0 else neighbors[0]  # min(neighbors, key=lambda x: self._neighborhood.evaluate(x))
            if self._neighborhood.evaluate(best_neighbor) < self._neighborhood.evaluate(self._boxes):
                self._boxes = best_neighbor
            else:
                break
        return self._boxes


class Neighborhood:
    def generate_neighbors(self, solution):
        raise NotImplementedError()

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
            # solution.append(Box(box_size).place(object))
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
        # rotate_neighbors = self._rotate_rectangle(solution)

        # Combine all potential neighbors
        all_neighbors = move_neighbors # + swap_neighbors + rotate_neighbors

        # Score and prioritize neighbors
        scored_neighbors = [(self._score_solution(neigh), neigh) for neigh in all_neighbors]
        
        # Sort neighbors by score (higher score = better move)
        scored_neighbors.sort(reverse=True, key=lambda x: x[0])

        # Return the top N best neighbors (adjustable for efficiency)
        return [neigh for _, neigh in scored_neighbors[:10]]

    def _move_rectangle(self, solution):
        """ Move a rectangle from one box to another if space allows """
        neighbors = []
        new_solution: list[Box] = deepcopy(solution)
        print(f"new_solution: {len(new_solution)}")
        for j, targeted_box in enumerate(new_solution):
            remove_index = 0 # To adjust the index after removing a box 
            # (e.g, if a box is removed, the index of the next box will be reduced by 1 not by 2)
            for i, source_box in enumerate(reversed(new_solution)):
                real_index = len(new_solution) - 1 - i + remove_index
                if real_index == j:
                    continue
                for rect_num, rect in enumerate(source_box.get_rectangles()):
                    if new_solution[j].place(rect):
                        new_solution[real_index].remove_rectangle(rect)
                    else:
                        continue
                    
                    # If the source box becomes empty, remove it
                    if new_solution[real_index].get_rectangles() == []:
                        new_solution.pop(real_index)
                        remove_index += 1

                        # # Add the modified solution as a neighbor
                        # neighbors.append(new_solution)
                        # break

                    # Add the modified solution as a neighbor
                    neighbors.append(new_solution)
        return neighbors
    

    def _swap_rectangles(self, solution):
        """ Swap two rectangles between different boxes if both can fit in the other's space """
        neighbors = []
        for i, box1 in enumerate(solution):
            for j, box2 in enumerate(solution):
                if i >= j:
                    continue
                for rect1 in box1.get_rectangles():
                    for rect2 in box2.get_rectangles():
                        if box1.can_place(rect2, 0, 0) and box2.can_place(rect1, 0, 0):
                            new_solution = deepcopy(solution)
                            new_solution[i].remove(rect1)
                            new_solution[j].remove(rect2)
                            if new_solution[i].place(rect2) and new_solution[j].place(rect1):
                                neighbors.append(new_solution)
        return neighbors

    def _rotate_rectangle(self, solution):
        """ Rotate a rectangle if it improves fit within the same box """
        neighbors = []
        for i, box in enumerate(solution):
            for rect in box.get_rectangles():
                rotated_rect = deepcopy(rect)
                rotated_rect.rotate()
                if box.can_place(rotated_rect, rect.x, rect.y):
                    new_solution = deepcopy(solution)
                    new_solution[i].remove(rect)
                    if new_solution[i].place(rotated_rect):
                        neighbors.append(new_solution)
        return neighbors

    def _score_solution(self, solution):
        """
        Assign a reward-based score to encourage promising moves.
        Higher scores are given to solutions that:
        - Use fewer boxes
        - Reduce wasted space
        - Reduce the number of nearly empty boxes
        """
        num_boxes = len(solution)
        # empty_boxes = sum(1 for box in solution if len(box.get_rectangles()) == 0)
        total_wasted_space = sum(box.get_space() for box in solution)

        score = 1000 - (num_boxes * 50) - total_wasted_space

        return score

    def evaluate(self, solution):
        total_wasted_space = sum(box.get_space() for box in solution)
        num_used_boxes = len([box for box in solution if box.get_rectangles()])

        # Objective: Minimize wasted space and the number of boxes
        return total_wasted_space + (num_used_boxes * 50)


class RuleBasedNeighborhood(Neighborhood):
    def generate_neighbors(self, solution):
        # Generate neighbors by modifying the order of rectangles
        neighbors = []
        # Add logic for permutation-based neighborhoods
        return neighbors

    def start(self, problem):
        solution = Greedy(problem, GreedyArea).run()
        return solution

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