import random
from collections import defaultdict
import numpy as np


class OptimizationProblem:
    def __init__(
        self, box_size: int, num_rectangles: int, min_size: int, max_size: int
    ) -> None:
        self._box_size = box_size
        self._num_rectangles = num_rectangles
        self._min_size = min_size
        self._max_size = max_size
        self._rectangles = np.array([])
        self.generate_instance()

    def generate_instance(self) -> None:
        rectangles = []
        for _ in range(self._num_rectangles):
            width = np.random.randint(self._min_size, self._max_size + 1)
            height = np.random.randint(self._min_size, self._max_size + 1)
            rect = Rectangle(width, height, 0, 0)

            rectangles.append(rect)

        self._rectangles = np.array(rectangles)

    def get_rectangles(self):
        return self._rectangles

    def get_rectangles_random(self):
        return np.random.permutation(self._rectangles)

    def get_box_size(self) -> int:
        return self._box_size

    def apply_algorithm(self, algorithm):
        raise NotImplementedError()


class Box:
    def __init__(self, box_size, grid_size=2, id=None):
        self._length = box_size
        self._rectangles = []
        self._coordinates = set()
        self._coordinates.add((0, 0))
        self._space = box_size * box_size

        # Grid for spatial partitioning
        self.grid_size = grid_size
        self.grid = defaultdict(list)  # Dictionary mapping grid cells to rectangles

        if id is None:
            self.id = np.random.randint(0, 100000)
        else:
            self.id = id

    def _get_grid_cells(self, x, y, width, height):
        """Get grid cells occupied by a given rectangle."""
        start_x, start_y = x // self.grid_size, y // self.grid_size
        end_x, end_y = (x + width) // self.grid_size, (y + height) // self.grid_size
        return [
            (gx, gy)
            for gx in range(start_x, end_x + 1)
            for gy in range(start_y, end_y + 1)
        ]

    def compute_overlap(self, rectangle: "Rectangle", x, y) -> int:
        """Compute overlap using spatial hashing."""
        total_overlap = 0
        cells = self._get_grid_cells(x, y, rectangle.width, rectangle.height)
        checked_rectangles = set()  # Avoid duplicate checks
        for cell in cells:
            for placed in self.grid[cell]:
                if placed in checked_rectangles:
                    continue
                checked_rectangles.add(placed)
                overlap_width = max(
                    0,
                    min(placed.x + placed.width, x + rectangle.width)
                    - max(placed.x, x),
                )
                overlap_height = max(
                    0,
                    min(placed.y + placed.height, y + rectangle.height)
                    - max(placed.y, y),
                )
                if overlap_width > 0 and overlap_height > 0:
                    total_overlap += overlap_width * overlap_height
        return total_overlap

    def can_place(self, rectangle: "Rectangle", x, y) -> bool:
        """
        Check if a rectangle can be placed at a given coordinate
        Args:
            rectangle (Rectangle): the rectangle to be placed
            x (int): x coordinate
            y (int): y coordinate
        Returns:
            bool: True if the rectangle can be placed, False otherwise
        """
        if x + rectangle.width > self._length or y + rectangle.height > self._length:
            return False
        overlap = self.compute_overlap(rectangle, x, y)
        if overlap > 0:
            return False
        return True

    def place(self, rectangle: "Rectangle", check = True) -> bool:
        """
        Place a rectangle in the box
        Args:
            rectangle (Rectangle): the rectangle to be placed
            check: check for overlaps or not
        Returns:
            bool: True if the rectangle was placed, False otherwise
        """
        if check:
            if rectangle.width * rectangle.height > self._space:
                return False
            for coordinate in sorted(self._coordinates, key = lambda x: x[0]+x[1]):
                x, y = coordinate
                if self.can_place(rectangle, x, y):
                    self._update_placement(rectangle, coordinate)
                    return True
        else:
            for _ in range(len(self._coordinates)):
                coordinate = random.choice(list(self._coordinates))
                x, y = coordinate
                if not((x + rectangle.width > self._length) or (y + rectangle.height > self._length)):
                    self._update_placement(rectangle, coordinate, False)
                    return True
        return False

    def _update_placement(self, rectangle, coordinate, grid = True):
        """Update placement and store in grid."""
        x, y = coordinate
        if (x+rectangle.width > self._length) and (y + rectangle.height > self._length):
            print("placed over the edge")
        rectangle.x, rectangle.y = x, y
        self._rectangles.append(rectangle)

        if grid:
            # Update grid
            cells = self._get_grid_cells(x, y, rectangle.width, rectangle.height)
            for cell in cells:
                self.grid[cell].append(rectangle)

        self._coordinates.discard(coordinate)
        if not (x + rectangle.width >= self._length):
            self._coordinates.add((x + rectangle.width, y))
        if not (y + rectangle.height >= self._length):
            self._coordinates.add((x, y + rectangle.height))
        self._space -= rectangle.width * rectangle.height

    def place_no_check(self, rectangle):
        self._rectangles.append(rectangle)
        self._space -= rectangle.width * rectangle.height

    def get_rectangles(self):
        return self._rectangles

    def get_space(self):
        return self._space

    def get_length(self):
        return self._length

    def remove_rectangle(self, rectangle: "Rectangle", grid = True):
        """Remove a rectangle from the box."""
        self._rectangles.remove(rectangle)
        self._space += rectangle.width * rectangle.height
        x, y = rectangle.x, rectangle.y
        self._coordinates.add((x, y))
        if not (x + rectangle.width >= self._length):
            self._coordinates.discard((x + rectangle.width, y))
        if not (y + rectangle.height >= self._length):
            self._coordinates.discard((x, y + rectangle.height))

        if grid:
            # Update the spatial grid
            cells = self._get_grid_cells(x, y, rectangle.width, rectangle.height)
            for cell in cells:
                if rectangle in self.grid[cell]:
                    self.grid[cell].remove(rectangle)

    def copy(self):
        new_box = Box(self._length, self.grid_size, self.id)
        new_box._rectangles = [
            Rectangle(r.width, r.height, r.x, r.y, r.color, r.id) for r in self._rectangles
        ]  # Create new instances
        new_box._coordinates = (
            self._coordinates.copy()
        )  # Set of immutable tuples, so shallow copy is fine
        new_box._space = self._space

        new_box.grid = defaultdict(list)
        for key, value in self.grid.items():
            new_box.grid[key] = value.copy()

        return new_box

    def get_coordinates(self):
        return self._coordinates

class Rectangle:
    def __init__(self, width, height, x, y, color=None, id=None):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

        if color is None:
            self.color = self.generate_random_color()  # Assign a color when created
        else:
            self.color = color
        
        if id is None:
            self.id = np.random.randint(0,1000000)
        else:
            self.id = id

    def rotate(self):
        self.width, self.height = self.height, self.width

    def generate_random_color(self):
        """Generate a random RGB color as a tuple."""
        return (
            np.random.randint(0, 256),
            np.random.randint(0, 256),
            np.random.randint(0, 256),
        )

    def copy(self,):
        new_rectangle = Rectangle(self.width, self.height, self.x, self.y)
        new_rectangle.color = self.color

        return new_rectangle
