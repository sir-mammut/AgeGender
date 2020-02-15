from PyQt5.QtCore import QByteArray, qFuzzyCompare, Qt, QTimer
from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtMultimedia import (QAudioEncoderSettings, QCamera,
        QCameraImageCapture, QImageEncoderSettings, QMediaMetaData,
        QMediaRecorder, QMultimedia, QVideoEncoderSettings)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QDialog,
        QMainWindow, QMessageBox)

from ui_camera import Ui_Camera
from ui_imagesettings import Ui_ImageSettingsUi
from ui_videosettings import Ui_VideoSettingsUi



class Camera(QMainWindow):
	"""docstring for Camera"""
	def __init__(self, arg):
		super(Camera, self).__init__(parent)
		# self.arg = arg
		# Attributes variables
		self.ui = Ui_Camera()
		self.camera = None
		self.imageCapture = None
		self.mediaRecorder = None
		self.isCapturingImage = False
		self.applicationExiting = False

		self.imageSettings = QImageEncoderSettings()
		self.audioSettings = QAudioEncoderSettings()
		self.videoSettings = QVideoEncoderSettings()
		self.videoContainerFormat = ''

		self.ui.setupUi(self)

		#get device camera
		cameraDevice = QByteArray()

		videoDevicesGroup = QActionGroup(self)
		videoDevicesGroup.setExclusive(True)

		# Get informations about available cameras
		for deviceName in QCamera.availableDevices():
			description = QCamera.deviceDescription(deviceName)
			videoDeviceAction = QAction(description, videoDevicesGroup)
			videoDeviceAction.setCheckable(True)
			videoDeviceAction.setData(deviceName)

			if cameraDevice.isEmpty():
			    cameraDevice = deviceName
			    videoDeviceAction.setChecked(True)

			self.ui.menuDevices.addAction(videoDeviceAction)

		videoDevicesGroup.triggered.connect(self.updateCameraDevice)
		self.ui.captureWidget.currentChanged.connect(self.updateCaptureMode)

		self.ui.lockButton.hide()

		self.setCamera(cameraDevice)



class ImageSettings(QDialog):
	"""docstring for ImageSettings"""

	def __init__(self, arg):
		super(ImageSettings, self).__init__(parent)
		# self.arg = arg



if __name__ == '__main__':
	import sys

	app = QApplication(sys.argv)
	camera = Camera()

	# for deviceName in QCamera.availableDevices():
	# 	description = QCamera.deviceDescription(deviceName)
	# 	print(description)

	camera.show()
	sys.exit(app.exec_())
		
# import sys

# from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
# from PyQt5.QtGui import QIcon

# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt

# import random

# class App(QMainWindow):

#     def __init__(self):
#         super().__init__()
#         self.left = 10
#         self.top = 10
#         self.title = 'PyQt5 matplotlib example'
#         self.width = 640
#         self.height = 400
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle(self.title)
#         self.setGeometry(self.left, self.top, self.width, self.height)

#         m = PlotCanvas(self, width=5, height=4)
#         m.move(0,0)

#         button = QPushButton('PyQt5 button', self)
#         button.setToolTip('This s an example button')
#         button.move(500,0)
#         button.resize(140,100)

#         self.show()

# class PlotCanvas(FigureCanvas):

#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)

#         FigureCanvas.__init__(self, fig)
#         self.setParent(parent)

#         FigureCanvas.setSizePolicy(self,
#                 QSizePolicy.Expanding,
#                 QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)
#         self.plot()


#     def plot(self):
#         data = [random.random() for i in range(25)]
#         ax = self.figure.add_subplot(111)
#         ax.plot(data, 'r-')
#         ax.set_title('PyQt Matplotlib Example')
#         self.draw()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = App()
#     sys.exit(app.exec_())