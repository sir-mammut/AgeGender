# Import required modules
import cv2 as cv
import math
import time
import sys
import numpy as np
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

from PyQt5.QtCore import QByteArray, qFuzzyCompare, Qt, QTimer
from PyQt5.QtGui import QPalette, QPixmap, QImage
from PyQt5.QtMultimedia import (QAudioEncoderSettings, QCamera,
        QCameraImageCapture, QImageEncoderSettings, QMediaMetaData,
        QMediaRecorder, QMultimedia, QVideoEncoderSettings)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QDialog,
        QMainWindow, QMessageBox, QFileDialog)

from ageGender import *

class Camera(QMainWindow):
	"""docstring for Camera"""
	def __init__(self, parent=None):
		super(Camera, self).__init__(parent)

		self.ui = Ui_AgeGender()
		self.ui.setupUi(self)

		self.camera = None
		self.imageCapture = None
		self.mediaRecorder = None
		self.isCapturingImage = False
		self.applicationExiting = False

		self.imageSettings = QImageEncoderSettings()
		self.audioSettings = QAudioEncoderSettings()
		self.videoSettings = QVideoEncoderSettings()
		self.videoContainerFormat = ''

		# self.ui.setupUi(self)

		self.face_cascade = cv.CascadeClassifier('haarcascade_frontalface_alt.xml')
		# OpenCv face Cascade classifier
		self.faceProto = "AgeGender/opencv_face_detector.pbtxt"
		self.faceModel = "AgeGender/opencv_face_detector_uint8.pb"

		self.ageProto = "AgeGender/age_deploy.prototxt"
		self.ageModel = "AgeGender/age_net.caffemodel"

		self.genderProto = "AgeGender/gender_deploy.prototxt"
		self.genderModel = "AgeGender/gender_net.caffemodel"

		# Load network
		self.ageNet = cv.dnn.readNet(self.ageModel, self.ageProto)
		self.genderNet = cv.dnn.readNet(self.genderModel, self.genderProto)
		self.faceNet = cv.dnn.readNet(self.faceModel, self.faceProto)

		self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
		self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60+)']
		self.genderList = ['Male', 'Female']
		self.addToolBar(NavigationToolbar(self.ui.genderWidget.canvas, self))
		self.addToolBar(NavigationToolbar(self.ui.ageWidget.canvas, self))

		# create a timer
		self.timer = QTimer()

		# set timer timeout callback function
		self.timer.timeout.connect(self.detectFace)

		#When the start camera got clicked invoke controlTimer() function
		self.ui.startCamera.clicked.connect(self.controlTimer)

		#When the upload image bottom got clicked invoke getImage() function
		self.ui.uploadImage.clicked.connect(self.detectInImage)

		cameraDevice = QByteArray()

	def getFaceBox(self, net, frame, conf_threshold=0.7):
	    frameOpencvDnn = frame.copy()
	    frameHeight = frameOpencvDnn.shape[0]
	    frameWidth = frameOpencvDnn.shape[1]
	    blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

	    net.setInput(blob)
	    detections = net.forward()
	    bboxes = []
	    for i in range(detections.shape[2]):
	        confidence = detections[0, 0, i, 2]
	        if confidence > conf_threshold:
	            x1 = int(detections[0, 0, i, 3] * frameWidth)
	            y1 = int(detections[0, 0, i, 4] * frameHeight)
	            x2 = int(detections[0, 0, i, 5] * frameWidth)
	            y2 = int(detections[0, 0, i, 6] * frameHeight)
	            bboxes.append([x1, y1, x2, y2])
	            cv.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (255, 255, 0), int(round(frameHeight/250)), 8)
	        # frameOpencvDnn = cv.cvtColor(frameOpencvDnn, cv.COLOR_RGB2RGB)
	    return frameOpencvDnn, bboxes
	# start/stop timer

	def detectFace(self):
		hasFrame, frame = self.cap.read()

		# resize frame image
		scaling_factor = 1 #100%
		frame = cv.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv.INTER_AREA)

		padding = 20

		frameFace, bboxes = self.getFaceBox(self.faceNet, frame)
			
		
		if not bboxes:
			self.ui.message.setText("No face detected, checking another frame!")
		else:
			self.ui.message.setText("Estimating...")

		for bbox in bboxes:


			face = frame[max(0,bbox[1]-padding):min(bbox[3]+padding,frame.shape[0]-1),max(0,bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)]

			blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
			self.genderNet.setInput(blob)
			genderPreds = self.genderNet.forward()
			gender = self.genderList[genderPreds[0].argmax()]
			# For video.
			self.ui.genderValue.setText("Gender : {}".format(gender))
			self.ui.VgenderAcc.setText("Accuracy : {:.3f}%".format(100 * genderPreds[0].max()))


			self.ageNet.setInput(blob)
			agePreds = self.ageNet.forward()
			age = self.ageList[agePreds[0].argmax()]
			# For video.
			self.ui.ageValue.setText("Age  :   {}".format(age))
			self.ui.VageAcc.setText("Accuracy : {:.3f}%".format(100 * agePreds[0].max()))


			label = "{},{}".format(gender, age)
			cv.putText(frameFace, label, (bbox[0], bbox[1]-10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 100), 1, cv.LINE_AA)

			# get frame infos
			height, width, channel = frameFace.shape
			step = channel * width
			# create QImage from RGB frame
			qImg = QImage(frameFace.data, width, height, step, QImage.Format_RGB888)
			# show frame in img_label
			self.ui.imagePreview.setPixmap(QPixmap.fromImage(qImg))

		

		# def emotion_analysis(emotions):
		#     objects = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
		#     y_pos = np.arange(len(objects))
		    
		#     plt.bar(y_pos, emotions, align='center', alpha=0.5)
		#     plt.xticks(y_pos, objects)
		#     plt.ylabel('percentage')
		#     plt.title('emotion')
		    
		#     plt.show()

	def controlTimer(self):
	    # if timer is stopped execute this condition
	    if not self.timer.isActive():
	    	# update control_bt text
	    	self.ui.startCamera.setText("Stop")
	    	# start timer
	    	self.timer.start(20)
	    	# create video capture
	    	self.cap = cv.VideoCapture(0)
	    	padding = 20

	    	self.ui.ageValue.setText("Age")

	    # if timer is started execute this condition
	    else:
	    	# cv.waitKey(0)
	    	# self.cap.release()
	    	# cv.destroyAllWindows()
	        # wait for escape key
	        cv.waitKey(0)
	        self.cap.release()
	        cv.destroyAllWindows()
	        # stop timer
	        self.timer.stop()
	        # release video capture
	        self.cap.release()
	        # update control_bt text
	        self.ui.startCamera.setText("Start")


	def getImage(self):
		file_name = QFileDialog.getOpenFileName(self, 'Upload image', 'c:/', "Image files (*.jpg *.gif)")
		imagePath = file_name[0]

		return imagePath

	def detectInImage(self):
		
		frame = self.getImage()

		frame = cv.imread(frame)

		# resize frame image
		scaling_factor = 1 #100%
		frame = cv.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv.INTER_AREA)

		padding = 20

		frameFace, bboxes = self.getFaceBox(self.faceNet, frame)

		if not bboxes:
			self.ui.message.setText("No face detected, checking another frame!")
		else:
			self.ui.message.setText("Estimated!")

		for bbox in bboxes:

			face = frame[max(0,bbox[1]-padding):min(bbox[3]+padding,frame.shape[0]-1),max(0,bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)]

			blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)
			self.genderNet.setInput(blob)
			genderPreds = self.genderNet.forward()
			gender = self.genderList[genderPreds[0].argmax()]
			# For Image.
			self.ui.ImGender.setText("Gender : {}".format(gender))
			self.ui.ImGenderAcc.setText("Accuracy : {:.3f}%".format(100 * genderPreds[0].max()))

			self.ageNet.setInput(blob)
			agePreds = self.ageNet.forward()
			age = self.ageList[agePreds[0].argmax()]

			# For Image.
			self.ui.ImAge.setText("Age  :   {}".format(age))
			self.ui.ImAgeAcc.setText("Accuracy : {:.3f}%".format(100 * agePreds[0].max()))

			label = "{},{}".format(gender, age)
			cv.putText(frameFace, label, (bbox[0], bbox[1]-10), cv.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 100), 1, cv.LINE_AA)

			# get frame infos
			height, width, channel = frameFace.shape
			step = channel * width
			# create QImage from RGB frame
			qImg = QImage(frameFace.data, width, height, step, QImage.Format_RGB888)
			# show frame in img_label
			self.ui.imagePreview.setPixmap(QPixmap.fromImage(qImg))

			gn = genderPreds[0]
			genderPridictList = []
			for g in gn:
				genderPridictList.append(g * 100)

			# print(genderPridictList)
			self.getGenderGraph(genderPridictList)

			ages = agePreds[0]
			agePridictList = []
			for g in ages:
				agePridictList.append(g * 100)

			# print(genderPridictList)
			self.getAgeGraph(agePridictList)

			# y_pos = np.arange(len(self.agePreds))

			# plt.bar(y_pos, agePreds, align='center', alpha=0.5)
			# plt.xticks(y_pos, agePreds)
			# plt.ylabel('percentage')																																																																																																																																																																																																																																																																																																																																																																																																																																																																		
			# plt.title('Age Graph')
			# plt.show()


	def getGenderGraph(self, estimatedGender):
		
		objects = self.genderList
		y_pos = np.arange(len(objects))

		self.ui.genderWidget.canvas.axes.clear()
		self.ui.genderWidget.canvas.axes.bar(objects, estimatedGender, align='center', alpha=0.5)
		# self.ui.genderWidget.canvas.axes.(y_pos, objects)
		# self.ui.genderWidget.canvas.axes.set_yscale('percentage')																																																																																																																																																																																																																																					

		self.ui.genderWidget.canvas.axes.legend('Gender', 'Accuracy')
		self.ui.genderWidget.canvas.axes.set_title('Gender Graph')
		self.ui.genderWidget.canvas.draw()

	def getAgeGraph(self, estimatedAge):
		
		objects = self.ageList
		y_pos = np.arange(len(objects))

		self.ui.ageWidget.canvas.axes.clear()
		self.ui.ageWidget.canvas.axes.bar(objects, estimatedAge, align='center', alpha=0.5)
		# self.ui.genderWidget.canvas.axes.(y_pos, objects)
		# self.ui.genderWidget.canvas.axes.set_yscale('percentage')																																																																																																																																																																																																																																					

		self.ui.ageWidget.canvas.axes.legend('Age', 'Accuracy')
		self.ui.ageWidget.canvas.axes.set_title('Age Graph')
		self.ui.ageWidget.canvas.draw()




	""" Other code sippet """
	def record(self):
	    self.mediaRecorder.record()
	    self.updateRecordTime()

	def updateRecordTime(self):
	    msg = "Recorded %d sec" % (self.mediaRecorder.duration() // 1000)
	    self.ui.statusbar.showMessage(msg)

	def takeImage(self):
	    self.isCapturingImage = True
	    # self.imageCapture.capture()

	def startCamera(self):
	    self.camera.start()

	def stopCamera(self):
	    self.camera.stop()

	def setExposureCompensation(self, index):
	    self.camera.exposure().setExposureCompensation(index * 0.5)

	def processCapturedImage(self, requestId, img):
	    scaledImage = img.scaled(self.ui.viewfinder.size(), Qt.KeepAspectRatio,
	            Qt.SmoothTransformation)

	    self.ui.imagePreview.setPixmap(QPixmap.fromImage(scaledImage))

	    self.displayCapturedImage()
	    QTimer.singleShot(4000, self.displayViewfinder)

	def configureCaptureSettings(self):
	    if self.camera.captureMode() == QCamera.CaptureStillImage:
	        self.configureImageSettings()
	    elif self.camera.captureMode() == QCamera.CaptureVideo:
	        self.configureVideoSettings()

	def configureVideoSettings(self):
	    settingsDialog = VideoSettings(self.mediaRecorder)

	    settingsDialog.setAudioSettings(self.audioSettings)
	    settingsDialog.setVideoSettings(self.videoSettings)
	    settingsDialog.setFormat(self.videoContainerFormat)

	    if settingsDialog.exec_():
	        self.audioSettings = settingsDialog.audioSettings()
	        self.videoSettings = settingsDialog.videoSettings()
	        self.videoContainerFormat = settingsDialog.format()

	        self.mediaRecorder.setEncodingSettings(self.audioSettings,
	                self.videoSettings, self.videoContainerFormat)

	def configureImageSettings(self):
	    settingsDialog = ImageSettings(self.imageCapture)

	    settingsDialog.setImageSettings(self.imageSettings)

	    if settingsDialog.exec_():
	        self.imageSettings = settingsDialog.imageSettings()
	        self.imageCapture.setEncodingSettings(self.imageSettings)

	def displayViewfinder(self):
	    self.ui.stackedWidget.setCurrentIndex(0)

	def displayCapturedImage(self):
	    self.ui.stackedWidget.setCurrentIndex(1)

	def readyForCapture(self, ready):
	    self.ui.takeImageButton.setEnabled(ready)

	def imageSaved(self, id, fileName):
	    self.isCapturingImage = False

	    if self.applicationExiting:
	        self.close()

	def closeEvent(self, event):
	    if self.isCapturingImage:
	        self.setEnabled(False)
	        self.applicationExiting = True
	        event.ignore()
	    else:
	        event.accept()

	def keyPressEvent(self, event):
	    if event.isAutoRepeat():
	        return

	    if event.key() == Qt.Key_CameraFocus:
	        self.displayViewfinder()
	        self.camera.searchAndLock()
	        event.accept()
	    elif event.key() == Qt.Key_Camera:
	        if self.camera.captureMode() == QCamera.CaptureStillImage:
	            self.takeImage()
	        elif self.mediaRecorder.state() == QMediaRecorder.RecordingState:
	            self.stop()
	        else:
	            self.record()

	        event.accept()
	    else:
	        super(Camera, self).keyPressEvent(event)

	def keyReleaseEvent(self, event):
	    if event.isAutoRepeat():
	        return

	    if event.key() == Qt.Key_CameraFocus:
	        self.camera.unlock()
	    else:
	        super(Camera, self).keyReleaseEvent(event)

if __name__ == '__main__':

	import sys

	app = QApplication(sys.argv)

	camera = Camera()
	camera.show()
	sys.exit(app.exec_())
