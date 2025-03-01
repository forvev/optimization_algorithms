from local_search import *
from greedy import *
import numpy as np
import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QMainWindow,
    QPushButton,
    QRadioButton,
)
from PyQt5 import uic


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
            width = np.random.randint(self._min_size, self._max_size)
            height = np.random.randint(self._min_size, self._max_size)
            rect = Rectangle(width, height, 0, 0)

            rectangles.append(rect)

        self._rectangles = np.array(rectangles)

    def move_rectangle(self, rect, source_box, target_box):
        if target_box.place(rect):
            source_box._rectangles.remove(rect)
        else:
            new_box = Box(self._box_size)
            new_box.place(rect)
            self._boxes.append(new_box)

    def get_rectangles(self):
        return self._rectangles

    def get_box_size(self) -> int:
        return self._box_size

    def apply_algorithm(self, algorithm):
        raise NotImplementedError()


class ApplyWindow(QWidget):
    def __init__(self, problem: OptimizationProblem, strategy):
        super().__init__()
        self._problem = problem
        self._algorithm = None

        self.setFixedSize(500, 500)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        path = parent_dir + "/resources/algorithm_widget.ui"
        uic.loadUi(path, self)

        self.setWindowTitle("Apply Algorithm")

        if isinstance(strategy, GreedyArea) or isinstance(strategy, GreedyPerimeter):
            self._algorithm = Greedy(problem, strategy)
            self._algorithm.run()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        widget_width = self.width()
        widget_height = self.height()
        box_size = self._problem._box_size
        boxes = self._algorithm._boxes
        num_boxes = len(boxes)

        if num_boxes == 0:
            return
    
        cols = num_boxes
        box_width = widget_width // cols

        for i, box in enumerate(boxes):
            x_offset = i * box_width 
            y_offset = 0
            
            # Draw box boundary
            color = QColor(255, 255, 255) if i % 2 == 0 else QColor(200, 200, 200)
            painter.setBrush(color)
            painter.drawRect(x_offset, 0, box_width, widget_height)

            scale_factor = min(box_width / box_size, widget_height / box_size)

            for rect, (rect_x, rect_y) in zip(box.get_rectangles(), box._coordinates):
                # Scale positions and dimensions
                print(box._coordinates)
                scaled_x = x_offset + int(rect_x * scale_factor)
                scaled_y = int(rect_y * scale_factor)
                scaled_width = int(rect.width * scale_factor)
                scaled_height = int(rect.height * scale_factor)

                color = QColor(
                    np.random.randint(256),
                    np.random.randint(256),
                    np.random.randint(256),
                )
                painter.setBrush(color)
                painter.drawRect(scaled_x, scaled_y, scaled_width, scaled_height)

class MainWindow(QMainWindow):
    def __init__(self, problem: OptimizationProblem):
        super().__init__()
        self._problem = problem
        self._strategy = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        path = parent_dir + "/resources/main_window.ui"
        uic.loadUi(path, self)

        self.setWindowTitle("Rectangle Packing Visualization")
        self.init_field()
        self._pb_apply.clicked.connect(self._open_apply_window)
        self._rb_greedy_1.clicked.connect(self._on_rb_greedy_1_clicked)
        self._rb_greedy_2.clicked.connect(self._on_rb_greedy_2_clicked)

    def _open_apply_window(self):
        """Opens the apply window."""
        if self._apply_window is None:
            self._apply_window = ApplyWindow(self._problem, self._strategy)
        self._apply_window.show()

    def _on_rb_greedy_1_clicked(
        self,
    ) -> None:
        self._strategy = GreedyArea()

    def _on_rb_greedy_2_clicked(
        self,
    ) -> None:
        self._strategy = GreedyPerimeter()

    def init_field(self) -> None:
        # self._pb_box_length: QPushButton = self.pb_box_length
        self._pb_apply: QPushButton = self.pb_apply
        self._rb_greedy_1: QRadioButton = self.rb_greedy_1
        self._rb_greedy_2: QRadioButton = self.rb_greedy_2
        self._apply_window: QWidget = None


# Test Environment (simplified)
# class TestEnvironment:
#     def run(self):
#         # Define the box size, number of rectangles, and the problem instance
#         optimization_problem = OptimizationProblem(box_size=100, num_rectangles=10, min_size=10, max_size=20)

#         # Select neighborhood and algorithm
#         neighborhood = GeometryBasedNeighborhood()
#         algorithm = LocalSearch(optimization_problem, neighborhood)

#         # Run the algorithm
#         # solution = algorithm.run()

#         # Visualize the result
#         # gui = RectanglePackingGUI(problem, algorithm)
#         # gui.visualize(solution)


class TestEnvironment:
    def run(self):
        # Define the box size, number of rectangles, and the problem instance
        optimization_problem = OptimizationProblem(
            box_size=100, num_rectangles=100, min_size=20, max_size=40
        )

        # Create the application window
        app = QApplication(sys.argv)

        # Create the main window using the problem instance
        main_window = MainWindow(optimization_problem)
        main_window.show()

        # Start the event loop
        sys.exit(app.exec_())


if __name__ == "__main__":
    test_env = TestEnvironment()
    test_env.run()
