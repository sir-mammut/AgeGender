from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

class genderWidget(QWidget):
	"""docstring for genderWidget"""
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.canvas = FigureCanvas(Figure())

		vertical_layout = QVBoxLayout()
		vertical_layout = addWidget(self.canvas)

		self.canvas.axes = self.canvas.figure.add_subplot(111)
		setLayout(vertical_layout)