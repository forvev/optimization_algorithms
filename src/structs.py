from copy import deepcopy

class Box:
    def __init__(self, box_size):
        self._length = box_size
        self._rectangles = []
        self._coordinates = [(0, 0)]
        self._space = box_size * box_size

    def can_place(self, rectangle: "Rectangle", x, y):
        if x + rectangle.width > self._length or y + rectangle.height > self._length:
            return False
        overlap = self.compute_overlap(rectangle, x, y)
        if overlap > 0:
            return False
        return True

    def compute_overlap(self, rectangle: "Rectangle", x, y):
        total_overlap = 0
        for placed in self._rectangles:
            overlap_width = max(
                0, min(placed.x + placed.width, x + rectangle.width) - max(placed.x, x)
            )
            overlap_height = max(
                0,
                min(placed.y + placed.height, y + rectangle.height) - max(placed.y, y),
            )
            total_overlap += overlap_width * overlap_height
        return total_overlap

    def place(self, rectangle: "Rectangle"):
        if rectangle.width * rectangle.height > self._space:
            return False
        for coordinate in self._coordinates:
            x, y = coordinate
            if self.can_place(rectangle, x, y):
                self._update_placement(rectangle, coordinate)
                return True
            else: #rotation
                rectangle_rotate = deepcopy(rectangle)
                rectangle_rotate.rotate()
                if self.can_place(rectangle_rotate, x, y):
                    rectangle.rotate()
                    self._update_placement(rectangle, coordinate)
                    return True
                self._update_placement(rectangle, coordinate)
                return True
        return False

    def _update_placement(self, rectangle, coordinate):
        x, y = coordinate
        self._rectangles.append(rectangle)
        self._coordinates.remove(coordinate)
        self._coordinates.append((x + rectangle.width, y))
        self._coordinates.append((x, y + rectangle.height))
        self._space -= rectangle.width * rectangle.height

    def place_no_check(self, rectangle):
        self._rectangles.append(rectangle)

    def get_rectangles(self):
        return self._rectangles


class Rectangle:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def rotate(self):
        self.width, self.height = self.height, self.width
