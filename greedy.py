
# Greedy Algorithm
class Greedy:
    def __init__(self, problem, strategy):
        self.problem = problem
        self.strategy = strategy
        
    def run(self):
        solution = self.problem.generate_instance()
        rectangles = self.strategy.generate_order(solution)
        
        # Apply the strategy to place rectangles
        for rectangle in rectangles:
            solution = self.place_rectangle(solution, rectangle)
        return solution


# Strategy Implementations for Greedy
class SimpleGreedyStrategy:
    def generate_order(self, solution):
        # Generate order based on a simple greedy approach (e.g., largest first)
        return sorted(solution.rectangles, key=lambda x: -x.area())

class OptimizedGreedyStrategy:
    def generate_order(self, solution):
        # Use a more advanced greedy strategy
        return sorted(solution.rectangles, key=lambda x: -x.perimeter())
