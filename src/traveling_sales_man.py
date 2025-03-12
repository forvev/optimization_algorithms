from local_search import *
from greedy import *
import numpy as np
import matplotlib.pyplot as plt

class TSPProblem:
    def __init__(self, num_cities, width=100, height=100):
        """
        :param num_cities: Number of cities to generate.
        :param width:  Width of coordinate space in which cities lie.
        :param height: Height of coordinate space in which cities lie.
        """
        self.num_cities = num_cities
        self.width = width
        self.height = height
        self.cities = []
        self.generate_instance()

    def generate_instance(self):
        # Randomly place city coordinates
        self.cities = [
            (np.random.randint(0, self.width), np.random.randint(0, self.height))
            for _ in range(self.num_cities)
        ]

    def get_num_cities(self):
        return self.num_cities

    def get_distance(self, i, j):
        (x1, y1) = self.cities[i]
        (x2, y2) = self.cities[j]
        dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return dist

    def get_cities(self):
        return self.cities

def route_length(solution):
    """
    Computes the total route length for a given city ordering 'solution'.
    """
    dist = 0.0
    for i in range(len(solution)):
        current_city = solution[i]
        next_city = solution[(i+1) % len(solution)]
        (x1, y1) = current_city
        (x2, y2) = next_city
        dist += np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return dist

class RuleBasedTSP(Neighborhood):
    def start(self, problem: TSPProblem):
        cities = problem.get_cities()
        greedy = GreedyTSP()
        cities = greedy.generate_order(cities)
        return cities

    def generate_neighbors(self, solution):
        # Generate neighbors by modifying the order of rectangles
        neighbors = []
        best_score = self._score_solution(solution)
        best_neighbor = solution
        length = len(solution)
        prev_order = solution
        # section based permutation with 4 sections
        num_sections = 10
        section_size = length // num_sections
        sections = [
            prev_order[i * section_size: (i + 1) * section_size]
            for i in range(num_sections - 1)
        ]
        sections.append(prev_order[section_size * (num_sections - 1):])
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
            # only save neighbor if it is better
            score = self._score_solution(order)
            if score > best_score:
                best_score = score
                best_neighbor = order

        neighbors.append(best_neighbor)
        return neighbors

    def _permutate(self, sections):
        result = []
        for i in range(len(sections)):
            for j in range(len(sections)):
                new_neighbor = sections[:]
                new_neighbor[i], new_neighbor[j] = new_neighbor[j], new_neighbor[i]
                result.append(new_neighbor)

        # Flatten the permutations before returning
        return [[rect for section in perm for rect in section] for perm in result]

    def _score_solution(self, solution):
        return route_length(solution)

class GreedyTSP:
    def start(self, problem):
        return problem.get_cities()
    def generate_order(self, solution):
        new_solution = []
        remaining_cities = set(solution)  # Track unvisited cities
        current_city = solution[0]  # Start at the first city
        new_solution.append(current_city)
        remaining_cities.remove(current_city)

        while remaining_cities:
            closest = min(remaining_cities, key=lambda c: np.linalg.norm(np.array(c) - np.array(current_city)))
            new_solution.append(closest)
            remaining_cities.remove(closest)
            current_city = closest

        return new_solution


def visualize_tsp(cities, alg):
    """
    Show a 2D plot of the TSP route.

    :param cities: List of (x,y) for each city.
    :param route: The visiting order, as a list of integer city indices,
                  e.g. [0, 2, 1, 4, 3] meaning we go city0 -> city2 -> city1 -> city4 -> city3 -> city0
    """
    # Extract coordinates in visiting order
    ordered_coords = cities
    # Add the first city again at the end to close the loop
    ordered_coords.append(cities[0])

    # Plot
    plt.figure()
    # Plot all city points
    xs = [c[0] for c in cities]
    ys = [c[1] for c in cities]
    plt.scatter(xs, ys, marker='o', label='Cities')

    # Draw lines for the route
    route_x = [p[0] for p in ordered_coords]
    route_y = [p[1] for p in ordered_coords]
    plt.plot(route_x, route_y, '-o', label='Route')

    # Annotate each city with its index
    for idx, (x, y) in enumerate(cities):
        plt.text(x + 0.5, y + 0.5, str(idx))

    plt.title(alg)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.legend()
    plt.show()


def main():
    print("=== TSP Visualization Demo ===")
    # Let the user input the problem size
    num_cities = int(input("Enter number of cities (e.g. 10): "))
    width = int(input("Enter width of coordinate space (e.g. 100): "))
    height = int(input("Enter height of coordinate space (e.g. 100): "))

    # Create problem
    problem = TSPProblem(num_cities, width, height)
    cities = problem.get_cities()

    # Evaluate route length
    route_coords = cities
    total_length = route_length(route_coords)
    print(f"Random route length: {total_length:.2f}")

    # Visualize
    visualize_tsp(cities, "Random")


    greedy = Greedy(problem, GreedyTSP())
    cities = greedy.run()

    # Evaluate route length
    route_coords = cities
    total_length = route_length(route_coords)
    print(f"Greedy route length: {total_length:.2f}")

    # Visualize
    visualize_tsp(cities, "Greedy")

    local = LocalSearch(problem, RuleBasedTSP())
    cities = local.run()

    # Evaluate route length
    route_coords = cities
    total_length = route_length(route_coords)
    print(f"LocalSearch route length: {total_length:.2f}")

    # Visualize
    visualize_tsp(cities, "LocalSearch")


if __name__ == "__main__":
    main()
