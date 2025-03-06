###############################################################################
# optimized_shelf_box.py
###############################################################################
from structs import Rectangle

class ShelfBox:
    """
    Optimized ShelfBox that packs rectangles using the Shelf method.
    It caches the total vertical height used (self.used_height) to avoid iterating
    through shelves on each placement.
    """
    def __init__(self, box_size):
        self._length = box_size
        self.shelves = []  # List of shelves (each a dict)
        self.used_height = 0  # Total height used by shelves so far
        self._space = box_size * box_size  # Remaining space (if needed for heuristics)

    def place(self, rectangle: Rectangle) -> bool:
        """
        Attempt to place 'rectangle' on the current shelf if it fits horizontally.
        Otherwise, create a new shelf if there's enough vertical space.
        """
        # Quick reject if rectangle is too big for the box
        if rectangle.width > self._length or rectangle.height > self._length:
            return False
        if rectangle.width * rectangle.height > self._space:
            return False

        # Create the first shelf if none exist
        if not self.shelves:
            shelf = {
                'start_y': 0,
                'current_x': 0,
                'height': rectangle.height,
                'rectangles': []
            }
            self.shelves.append(shelf)
            self.used_height = rectangle.height
        else:
            shelf = self.shelves[-1]

        # Try to place on the current shelf
        if shelf['current_x'] + rectangle.width <= self._length:
            rectangle.x = shelf['current_x']
            rectangle.y = shelf['start_y']
            shelf['rectangles'].append(rectangle)
            shelf['current_x'] += rectangle.width

            # If the rectangle is taller than the current shelf, update shelf height.
            if rectangle.height > shelf['height']:
                old_height = shelf['height']
                shelf['height'] = rectangle.height
                self.used_height += (rectangle.height - old_height)
            self._space -= rectangle.width * rectangle.height
            return True
        else:
            # Need to start a new shelf if there is vertical space left
            if self.used_height + rectangle.height <= self._length:
                new_shelf = {
                    'start_y': self.used_height,
                    'current_x': 0,
                    'height': rectangle.height,
                    'rectangles': []
                }
                self.shelves.append(new_shelf)
                self.used_height += rectangle.height

                rectangle.x = 0
                rectangle.y = new_shelf['start_y']
                new_shelf['rectangles'].append(rectangle)
                new_shelf['current_x'] += rectangle.width
                self._space -= rectangle.width * rectangle.height
                return True

        return False

    def get_rectangles(self):
        """
        Return a flat list of all rectangles in the box.
        """
        all_rects = []
        for shelf in self.shelves:
            all_rects.extend(shelf['rectangles'])
        return all_rects

    def get_length(self):
        return self._length

    def get_space(self):
        return self._space

    def remove_rectangle(self, rectangle: Rectangle):
        """
        Removing a rectangle is nontrivial in shelf-based packing. For now, a simple
        removal is implemented that only updates the free area.
        """
        for shelf in self.shelves:
            if rectangle in shelf['rectangles']:
                shelf['rectangles'].remove(rectangle)
                self._space += rectangle.width * rectangle.height
                break
