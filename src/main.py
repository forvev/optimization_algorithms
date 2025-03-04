from local_search import *
from greedy import *
import numpy as np
import sys
import os
import time

from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QTextEdit,
)
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QThread, pyqtSignal


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
            width = np.random.randint(self._min_size, self._max_size+1)
            height = np.random.randint(self._min_size, self._max_size+1)
            rect = Rectangle(width, height, 0, 0)

            rectangles.append(rect)

        self._rectangles = np.array(rectangles)

    def get_rectangles(self):
        return self._rectangles

    def get_box_size(self) -> int:
        return self._box_size

    def apply_algorithm(self, algorithm):
        raise NotImplementedError()


class AlgorithmThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, algorithm):
        super().__init__()
        self._algorithm = algorithm

    def run(self):
        self._algorithm.run()
        self.finished_signal.emit()  # Signal completion

class ApplyWindow(QWidget):
    def __init__(self, problem: OptimizationProblem, strategy):
        super().__init__()
        self._problem = problem
        self._algorithm = None

        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        path = parent_dir + "/resources/algorithm_widget.ui"
        uic.loadUi(path, self)

        self.setWindowTitle("Apply Algorithm")

        self._start_time = time.time()

        if isinstance(strategy, GreedyArea) or isinstance(strategy, GreedyPerimeter):
            self._algorithm = Greedy(problem, strategy)
        elif isinstance(strategy, GeometryBasedNeighborhood) or isinstance(
            strategy, RuleBasedNeighborhood) or isinstance(strategy, PartialOverlapNeighborhood):
            self._algorithm = LocalSearch(problem, strategy)
        
        self._thread = AlgorithmThread(self._algorithm)
        self._thread.finished_signal.connect(self.algorithm_finished)
        self._thread.start()

        # 10 columns and one row as a initial size
        self.setFixedSize(self._problem._box_size*10, self._problem._box_size)

        # Run algorithm in steps using QTimer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_ui)
        self._timer.start(1000)  # Update every 1 second


    def update_ui(self):
        """Updates the visualization every 0.5 seconds"""

        num_boxes = len(self._algorithm._boxes)
        boxes_per_row = 10
        rows = (num_boxes // boxes_per_row) + (
            1 if num_boxes % boxes_per_row > 0 else 0
        )
        # if new_height != self.height():  # Only resize if needed
        new_height = rows * self._problem._box_size
        self.setFixedSize(self._problem._box_size * 10, new_height)
        
        
        self.repaint()  # Redraw rectangles
        QApplication.processEvents()  # Process UI events

    def algorithm_finished(self):
        """Handles when the algorithm finishes execution"""
        self._timer.stop()
        end_time = time.time()
        execution_time = end_time - self._start_time
        print(f"Algorithm execution time: {execution_time:.4f} seconds")

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

        boxes_per_row = 10
        rows = (num_boxes // boxes_per_row) + (
            1 if num_boxes % boxes_per_row > 0 else 0
        )
        box_width = widget_width // boxes_per_row

        # todo: add lines between boxes
        for row in range(rows):
            for col in range(boxes_per_row):
                box_index = row * boxes_per_row + col
                if box_index >= num_boxes:
                    break  # Skip if we don't have enough boxes for this position

                box = boxes[box_index]

                # Calculate x and y offsets for each box
                x_offset = col * box_width
                y_offset = row * (widget_height // rows)

                # Draw box boundary
                color = (
                    QColor(255, 255, 255)
                    if (row + col) % 2 == 0
                    else QColor(200, 200, 200)
                )
                painter.setBrush(color)
                painter.drawRect(x_offset, y_offset, box_width, widget_height // rows)

                scale_factor = min(
                    box_width / box_size, (widget_height // rows) / box_size
                )

                for rect in box.get_rectangles():
                    # Scale positions and dimensions
                    scaled_x = x_offset + int(rect.x * scale_factor)
                    scaled_y = y_offset + int(rect.y * scale_factor)
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
        self._rb_neighborhood_1.clicked.connect(self._on_rb_neighborhood_1_clicked)
        self._rb_neighborhood_2.clicked.connect(self._on_rb_neighborhood_2_clicked)
        self._rb_neighborhood_3.clicked.connect(self._on_rb_neighborhood_3_clicked)

    def _open_apply_window(self):
        """Opens the apply window with the selected strategy and problem"""

        if not self._rb_greedy_1.isChecked() and not self._rb_greedy_2.isChecked() and \
            not self._rb_neighborhood_1.isChecked() and not self._rb_neighborhood_2.isChecked() and \
            not self._rb_neighborhood_3.isChecked():
            print("Please select a strategy")
            return

        if self._box_size_value.text().isdigit() and \
            self._num_of_rect_value.text().isdigit() and \
            self._min_size_value.text().isdigit() and \
            self._max_size_value.text().isdigit():

            print("Creating new problem instance")
            self._problem = OptimizationProblem(
                int(self._box_size_value.text()),
                int(self._num_of_rect_value.text()),
                int(self._min_size_value.text()),
                int(self._max_size_value.text()),
            )

        # create the apply window every time the apply button is clicked
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

    def _on_rb_neighborhood_1_clicked(self) -> None:
        self._strategy = GeometryBasedNeighborhood()

    def _on_rb_neighborhood_2_clicked(self) -> None:
        self._strategy = RuleBasedNeighborhood()

    def _on_rb_neighborhood_3_clicked(self) -> None:
        self._strategy = PartialOverlapNeighborhood()

    def init_field(self) -> None:
        """Initializes the fields of the main window (because it helps with the suggestions)"""
        self._pb_apply: QPushButton = self.pb_apply
        self._rb_greedy_1: QRadioButton = self.rb_greedy_1
        self._rb_greedy_2: QRadioButton = self.rb_greedy_2
        self._rb_neighborhood_1: QRadioButton = self.rb_neighborhood_1
        self._rb_neighborhood_2: QRadioButton = self.rb_neighborhood_2
        self._rb_neighborhood_3: QRadioButton = self.rb_neighborhood_3
        self._num_of_rect_value: QTextEdit = self.num_of_rect_value
        self._box_size_value: QTextEdit = self.box_size_value
        self._min_size_value: QTextEdit = self.min_size_value
        self._max_size_value: QTextEdit = self.max_size_value
        self._apply_window: QWidget = None


class TestEnvironment:
    def run(self):
        # Define the box size, number of rectangles, and the problem instance
        optimization_problem = OptimizationProblem(
            box_size=100, num_rectangles=800, min_size=1, max_size=40
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
