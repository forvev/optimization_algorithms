from dask.array.overlap import overlap


class box:
    def __init__(self, box_size):
        self.length = box_size
        self.rectangles = []
        self.coordinates = [(0,0)]
        self.space = box_size*box_size

    def can_place(self,rectangle, x, y):
        if x + rectangle.width > self.length or y + rectangle.height > self.length:
            return False
        overlap = self.compute_overlap(rectangle, x, y)
        if overlap>0:
            return False
        return True

    def compute_overlap(self, rectangle, x, y):
        total_overlap = 0
        for placed in self.rectangles:
            overlap_width = max(0, min(placed.x + placed.width, x + rectangle.width)
                                - max(placed.x, x))
            overlap_height = max(0, min(placed.y + placed.height, y + rectangle.height)
                                 - max(placed.y, y))
            total_overlap += overlap_width * overlap_height
        return total_overlap

    def place(self, rectangle):
        if rectangle.width * rectangle.height >self.space:
            return False
        for coordinate in self.coordinates:
            x, y = coordinate
            if self.can_place(rectangle, x, y):
                self.rectangles.append(rectangle)
                self.coordinates.remove(coordinate)
                self.coordinates.append((x + rectangle.width,y))
                self.coordinates.append((x, y + rectangle.height))
                self.space -= rectangle.width * rectangle.height
                return True
            elif self.can_place(rectangle.rotate(), x, y):
                self.rectangles.append(rectangle)
                self.coordinates.remove(coordinate)
                self.coordinates.append((x + rectangle.width, y))
                self.coordinates.append((x, y + rectangle.height))
                self.space -= rectangle.width * rectangle.height
                return True
        return False



class rectangle:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def rotate(self):
        self.width = self.height
        self.height = self.width