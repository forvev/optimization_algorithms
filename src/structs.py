from collections import defaultdict
import numpy as np

class Box:
    def __init__(self, box_size, grid_size=2):
        self._length = box_size
        self._rectangles = []
        self._coordinates = set()
        self._coordinates.add((0,0))
        self._space = box_size * box_size

        # Grid for spatial partitioning
        self.grid_size = grid_size
        self.grid = defaultdict(list)  # Dictionary mapping grid cells to rectangles

    def _get_grid_cells(self, x, y, width, height):
        """Get grid cells occupied by a given rectangle."""
        start_x, start_y = x // self.grid_size, y // self.grid_size
        end_x, end_y = (x + width) // self.grid_size, (y + height) // self.grid_size
        return [(gx, gy) for gx in range(start_x, end_x + 1) for gy in range(start_y, end_y + 1)]

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
                overlap_width = max(0, min(placed.x + placed.width, x + rectangle.width) - max(placed.x, x))
                overlap_height = max(0, min(placed.y + placed.height, y + rectangle.height) - max(placed.y, y))
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

    def place(self, rectangle: "Rectangle") -> bool:
        """
        Place a rectangle in the box
        Args:
            rectangle (Rectangle): the rectangle to be placed
        Returns:
            bool: True if the rectangle was placed, False otherwise
        """
        if rectangle.width * rectangle.height > self._space:
            return False
        for coordinate in sorted(self._coordinates):
            x, y = coordinate
            if self.can_place(rectangle, x, y):
                self._update_placement(rectangle, coordinate)
                return True
            else: #rotation if can't place
                rectangle_rotate = Rectangle(rectangle.width, rectangle.height, rectangle.x, rectangle.y)
                rectangle_rotate.rotate()
                rectangle_rotate.rotate()
                if self.can_place(rectangle_rotate, x, y):
                    rectangle.rotate()
                    self._update_placement(rectangle, coordinate)
                    return True
        return False

    def _update_placement(self, rectangle, coordinate):
        """Update placement and store in grid."""
        x, y = coordinate
        rectangle.x, rectangle.y = x, y
        self._rectangles.append(rectangle)

        # Update grid
        cells = self._get_grid_cells(x, y, rectangle.width, rectangle.height)
        for cell in cells:
            self.grid[cell].append(rectangle)

        self._coordinates.discard(coordinate)
        if not (x+rectangle.width >= self._length):
            self._coordinates.add((x + rectangle.width, y))
        if not (y + rectangle.height >= self._length):
            self._coordinates.add((x, y + rectangle.height))
        self._space -= rectangle.width * rectangle.height

    def place_no_check(self, rectangle):
        self._rectangles.append(rectangle)

    def get_rectangles(self):
        return self._rectangles

    def get_space(self):
        return self._space

    def remove_rectangle(self, rectangle: "Rectangle"):
        """Remove a rectangle from the box."""
        self._rectangles.remove(rectangle)
        self._space += rectangle.width * rectangle.height
        x, y = rectangle.x, rectangle.y
        self._coordinates.add((x, y))
        if not (x + rectangle.width >= self._length):
            self._coordinates.discard((x + rectangle.width, y))
        if not (y + rectangle.height >= self._length):
            self._coordinates.discard((x, y + rectangle.height))

class Rectangle:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = self.generate_random_color()  # Assign a color when created

    def rotate(self):
        self.width, self.height = self.height, self.width

    def generate_random_color(self):
        """Generate a random RGB color as a tuple."""
        return (np.random.randint(0, 256), np.random.randint(0, 256), np.random.randint(0, 256))
