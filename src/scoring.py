from structs import Box

def compute_utilization(box: Box) -> float:
    """
    Computes the utilization ratio for a given box.
    Utilization = (used area) / (box area)
    """
    L = box.get_length()
    box_area = L * L
    used_area = box_area - box.get_space()
    return used_area / box_area

def compute_min_utilization(solution: list) -> float:
    """
    Returns the minimum box utilization among all boxes in the solution.
    """
    utilizations = [compute_utilization(box) for box in solution]
    return min(utilizations) if utilizations else 0

def compute_compactness(box: Box) -> float:
    """
    Computes a compactness measure for a box.
    For the set of rectangles in the box, the bounding rectangle is computed.
    Compactness = (sum of rectangle areas) / (bounding rectangle area)
    If no rectangles are placed, return 0.
    """
    rects = box.get_rectangles()
    if not rects:
        return 0
    # Get bounding coordinates
    x_min = min(rect.x for rect in rects)
    y_min = min(rect.y for rect in rects)
    x_max = max(rect.x + rect.width for rect in rects)
    y_max = max(rect.y + rect.height for rect in rects)
    bounding_width = x_max - x_min
    bounding_height = y_max - y_min
    bounding_area = bounding_width * bounding_height
    total_rect_area = sum(rect.width * rect.height for rect in rects)
    # Avoid division by zero if bounding_area is 0
    return total_rect_area / bounding_area if bounding_area > 0 else 0

def compute_average_compactness(solution: list) -> float:
    """
    Computes the average compactness over all boxes in the solution.
    """
    compactness_values = [compute_compactness(box) for box in solution]
    return sum(compactness_values) / len(compactness_values) if compactness_values else 0

def compute_contiguity(box: Box) -> float:
    """
    Computes a simple contiguity score for a box.
    For each rectangle, we count how many edges are flush with the box boundary.
    The maximum per rectangle is 4.
    The contiguity score for the box is the average contact ratio.
    """
    rects = box.get_rectangles()
    if not rects:
        return 0
    L = box.get_length()
    total_ratio = 0
    for rect in rects:
        contacts = 0
        if rect.x == 0:
            contacts += 1
        if rect.y == 0:
            contacts += 1
        if rect.x + rect.width == L:
            contacts += 1
        if rect.y + rect.height == L:
            contacts += 1
        total_ratio += contacts / 4  # Normalize to [0,1]
    return total_ratio / len(rects)

def compute_average_contiguity(solution: list) -> float:
    """
    Returns the average contiguity score across all boxes.
    """
    contiguity_values = [compute_contiguity(box) for box in solution]
    return sum(contiguity_values) / len(contiguity_values) if contiguity_values else 0

def compute_irregular_gap_penalty(box: Box) -> float:
    """
    Computes a penalty based on irregular gaps in the box.
    We first compute the bounding rectangle of all placed rectangles.
    Then, penalty = (bounding area - sum of rectangle areas) / bounding area.
    A lower penalty indicates that the rectangles fill their bounding region more tightly.
    """
    rects = box.get_rectangles()
    if not rects:
        return 0
    x_min = min(rect.x for rect in rects)
    y_min = min(rect.y for rect in rects)
    x_max = max(rect.x + rect.width for rect in rects)
    y_max = max(rect.y + rect.height for rect in rects)
    bounding_area = (x_max - x_min) * (y_max - y_min)
    total_rect_area = sum(rect.width * rect.height for rect in rects)
    # If bounding_area is zero, return 0 penalty
    return (bounding_area - total_rect_area) / bounding_area if bounding_area > 0 else 0

def compute_average_irregular_gap_penalty(solution: list) -> float:
    """
    Computes the average irregular gap penalty across all boxes in the solution.
    """
    penalties = [compute_irregular_gap_penalty(box) for box in solution]
    return sum(penalties) / len(penalties) if penalties else 0
