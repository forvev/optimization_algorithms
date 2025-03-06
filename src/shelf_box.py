###############################################################################
# no_overlap_shelf_box.py
###############################################################################
from structs import Rectangle

class ShelfBox:
    """
    A shelf-based packing algorithm that guarantees no overlaps by using fixed
    shelf heights. Each shelf is created with a height equal to the first rectangle's
    height placed in it. Subsequent rectangles are only placed in shelves that can
    accommodate their height. If no shelf fits, a new shelf is created.
    """
    def __init__(self, box_size: int):
        self._length = box_size
        self.shelves = []  # List of shelves; each is a dict with keys: start_y, height, gaps, rectangles.
        self.used_area = 0

    def _create_new_shelf(self, rectangle: Rectangle) -> bool:
        """
        Create a new shelf with fixed height equal to the rectangle's height.
        The new shelf is added only if there is enough vertical space.
        """
        current_y = sum(shelf['height'] for shelf in self.shelves)
        if current_y + rectangle.height > self._length:
            return False  # Not enough vertical space.
        new_shelf = {
            'start_y': current_y,
            'height': rectangle.height,  # Fixed shelf height.
            'gaps': [(0, self._length)],  # Initially, the entire width is free.
            'rectangles': []
        }
        self.shelves.append(new_shelf)
        # Immediately place the rectangle at x = 0 in the new shelf.
        return self._place_in_shelf(new_shelf, rectangle, gap_index=0, gap_start=0, gap_width=self._length)

    def _place_in_shelf(self, shelf: dict, rectangle: Rectangle, gap_index: int, gap_start: int, gap_width: int) -> bool:
        """
        Places the rectangle in the specified shelf gap.
        Updates the gap list by removing the used portion.
        """
        # For safety, ensure the rectangle fits in the gap and does not exceed shelf height.
        if rectangle.width > gap_width or rectangle.height > shelf['height']:
            return False
        # Set the rectangle's position.
        rectangle.x = gap_start
        rectangle.y = shelf['start_y']
        shelf['rectangles'].append(rectangle)
        self.used_area += rectangle.width * rectangle.height

        # Update the gap: remove the used portion.
        remaining = gap_width - rectangle.width
        if remaining > 0:
            shelf['gaps'][gap_index] = (gap_start + rectangle.width, remaining)
        else:
            shelf['gaps'].pop(gap_index)
        return True

    def place(self, rectangle: Rectangle) -> bool:
        """
        Attempts to place a rectangle by checking each existing shelf for a gap that can
        accommodate it. The rectangle is only considered for a shelf if its height does not
        exceed the shelf's fixed height. If no suitable shelf exists, a new shelf is created.
        Returns True if placement is successful.
        """
        # Quick rejection if the rectangle is larger than the box dimensions.
        if rectangle.width > self._length or rectangle.height > self._length:
            return False

        best_candidate = None  # Will store (leftover, shelf, gap_index, gap_start, gap_width)
        # Search through existing shelves.
        for shelf in self.shelves:
            # Only consider shelves tall enough.
            if rectangle.height > shelf['height']:
                continue
            for i, (gap_start, gap_width) in enumerate(shelf['gaps']):
                if rectangle.width <= gap_width:
                    leftover = gap_width - rectangle.width
                    # Choose the gap with the smallest leftover (i.e. best fit).
                    if best_candidate is None or leftover < best_candidate[0]:
                        best_candidate = (leftover, shelf, i, gap_start, gap_width)
        if best_candidate is not None:
            _, shelf, gap_index, gap_start, gap_width = best_candidate
            return self._place_in_shelf(shelf, rectangle, gap_index, gap_start, gap_width)
        # If no existing shelf can accommodate the rectangle, create a new shelf.
        return self._create_new_shelf(rectangle)

    def get_rectangles(self):
        """
        Returns a list of all rectangles placed in all shelves.
        """
        all_rects = []
        for shelf in self.shelves:
            all_rects.extend(shelf['rectangles'])
        return all_rects

    def get_length(self) -> int:
        """
        Returns the side length of the box.
        """
        return self._length

    def get_space(self) -> int:
        """
        Returns the remaining free area in the box.
        """
        total_area = self._length * self._length
        return total_area - self.used_area
