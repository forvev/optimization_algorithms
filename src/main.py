from local_search import *
import numpy as np
import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QPushButton
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

    def generate_instance(
        self,
    ) -> None:
        rectangles = []
        for i in range(self._num_rectangles):
            width = np.random.randint(self._min_size, self._max_size)
            height = np.random.randint(self._min_size, self._max_size)
            x = np.random.randint(0, self._box_size - width)
            y = np.random.randint(0, self._box_size - height)

            rectangles.append([width, height, x, y])

        self._rectangles = np.array(rectangles)

    def get_rectangles(self):
        return self._rectangles

    def apply_algorithm(self, algorithm):
        raise NotImplementedError()


class RectanglePackingGUI(QWidget):
    def __init__(self, problem: OptimizationProblem):
        super().__init__()
        self.problem = problem
        self.setWindowTitle("Rectangle Packing Visualization")
        self.setGeometry(0, 0, self.problem._box_size, self.problem._box_size)
        self.setStyleSheet("background-color: red;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rectangles = self.problem.get_rectangles()
        for rectangle in rectangles:
            width, height, x, y = rectangle

            color = QColor(
                np.random.randint(256), np.random.randint(256), np.random.randint(256)
            )
            painter.setBrush(color)
            painter.drawRect(x, y, width, height)


class MainWindow(QMainWindow):
    def __init__(self, problem: OptimizationProblem):
        super().__init__()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        path = parent_dir + "/resources/main_window.ui"
        uic.loadUi(path, self)

        self.setWindowTitle("Rectangle Packing Visualization")
        # Visualize the rectangles using a custom widget
        # self.visualization_widget = RectanglePackingGUI(problem)
        # self.visualization_widget.setParent(self)
        # self.visualization_widget.move(0, 0)  # Position the widget inside the window
        self.init_field()
        self.pb_box_length.clicked.connect(self.on_my_button_click)
        # self.setGeometry(100, 100, problem._box_size, problem._box_size)

    def on_my_button_click(self):
        print("Button clicked!")

    def init_field(self) -> None:
        self._pb_box_length: QPushButton = self.pb_box_length
    
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
            box_size=500, num_rectangles=10, min_size=10, max_size=100
        )

        # Create the application window
        app = QApplication(sys.argv)

        # Create the main window using the problem instance
        main_window = MainWindow(optimization_problem)
        main_window.show()

        # Start the event loop
        sys.exit(app.exec_())


if __name__ == "__main__":
    # app = QApplication([])
    # window = QWidget()
    # window.setWindowTitle("PyQt App")
    # window.setGeometry(100, 100, 280, 80)
    # helloMsg = QLabel("<h1>Hello, World!</h1>", parent=window)
    
    test_env = TestEnvironment()
    test_env.run()
