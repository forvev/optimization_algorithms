from local_search import *
import numpy as np

# Abstract Classes for Optimization Problem and Neighborhoods
class OptimizationProblem:

    def __init__(self, box_size: int, num_rectangles: int, min_size: int, max_size: int) -> None:
        self._box_size = box_size
        self._num_rectangles = num_rectangles
        self._min_size = min_size
        self._max_size = max_size
        self._rectangles = np.array([])

        self.generate_instance()

    def generate_instance(self,) -> None:
        for i in range(self.num_rectangles):
            width = np.random.uniform(self.min_size, self.max_size)
            height = np.random.uniform(self.min_size, self.max_size)
            self._rectangles = np.append(self._rectangles, [width, height])
    
    def apply_algorithm(self, algorithm):
        raise NotImplementedError()

# # GUI Implementation (Simplified version)
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches

# class RectanglePackingGUI:
#     def __init__(self, problem, algorithm):
#         self.problem = problem
#         self.algorithm = algorithm
    
#     def visualize(self, solution):
#         fig, ax = plt.subplots()
#         for rectangle in solution.rectangles:
#             rect_patch = patches.Rectangle((rectangle.x, rectangle.y), rectangle.width, rectangle.height, linewidth=1, edgecolor='r', facecolor='none')
#             ax.add_patch(rect_patch)
#         plt.xlim(0, self.problem.L)
#         plt.ylim(0, self.problem.L)
#         plt.gca().set_aspect('equal', adjustable='box')
#         plt.show()

# Test Environment (simplified)
class TestEnvironment:
    def run(self):
        # Define the box size, number of rectangles, and the problem instance
        optimization_problem = OptimizationProblem(box_size=100, num_rectangles=10, min_size=10, max_size=20)
        
        # Select neighborhood and algorithm
        neighborhood = GeometryBasedNeighborhood()
        algorithm = LocalSearch(optimization_problem, neighborhood)
        
        # Run the algorithm
        solution = algorithm.run()
        
        # Visualize the result
        # gui = RectanglePackingGUI(problem, algorithm)
        # gui.visualize(solution)

test_env = TestEnvironment()
test_env.run()
