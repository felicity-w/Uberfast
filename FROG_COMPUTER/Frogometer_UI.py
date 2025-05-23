# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FROG.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1028)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Calibration_2 = QtWidgets.QTabWidget(self.centralwidget)
        self.Calibration_2.setGeometry(QtCore.QRect(40, 0, 1800, 980))
        self.Calibration_2.setObjectName("Calibration_2")
        self.Measuring = QtWidgets.QWidget()
        self.Measuring.setObjectName("Measuring")
        self.Forward = QtWidgets.QToolButton(self.Measuring)
        self.Forward.setGeometry(QtCore.QRect(1600, 830, 50, 50))
        self.Forward.setArrowType(QtCore.Qt.RightArrow)
        self.Forward.setObjectName("Forward")
        self.Back_Fast = QtWidgets.QToolButton(self.Measuring)
        self.Back_Fast.setGeometry(QtCore.QRect(1250, 830, 50, 50))
        self.Back_Fast.setArrowType(QtCore.Qt.LeftArrow)
        self.Back_Fast.setObjectName("Back_Fast")
        self.Back = QtWidgets.QToolButton(self.Measuring)
        self.Back.setGeometry(QtCore.QRect(1310, 830, 50, 50))
        self.Back.setArrowType(QtCore.Qt.LeftArrow)
        self.Back.setObjectName("Back")
        self.Forward_Fast = QtWidgets.QToolButton(self.Measuring)
        self.Forward_Fast.setGeometry(QtCore.QRect(1660, 830, 50, 50))
        self.Forward_Fast.setArrowType(QtCore.Qt.RightArrow)
        self.Forward_Fast.setObjectName("Forward_Fast")
        self.Intensity_SHG = GraphicsLayoutWidget(self.Measuring)
        self.Intensity_SHG.setGeometry(QtCore.QRect(630, 50, 1141, 721))
        self.Intensity_SHG.setObjectName("Intensity_SHG")
        self.label_5 = QtWidgets.QLabel(self.Measuring)
        self.label_5.setGeometry(QtCore.QRect(1410, 840, 141, 21))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.Measuring)
        self.label_6.setGeometry(QtCore.QRect(1410, 860, 151, 21))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.Measuring)
        self.label_7.setGeometry(QtCore.QRect(1250, 810, 51, 21))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.Measuring)
        self.label_8.setGeometry(QtCore.QRect(1320, 810, 41, 21))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.Measuring)
        self.label_9.setGeometry(QtCore.QRect(1660, 810, 71, 21))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.Measuring)
        self.label_10.setGeometry(QtCore.QRect(1600, 810, 51, 21))
        self.label_10.setObjectName("label_10")
        self.Location = QtWidgets.QLineEdit(self.Measuring)
        self.Location.setGeometry(QtCore.QRect(160, 750, 321, 20))
        self.Location.setText("")
        self.Location.setObjectName("Location")
        self.File_name = QtWidgets.QLineEdit(self.Measuring)
        self.File_name.setGeometry(QtCore.QRect(160, 820, 321, 20))
        self.File_name.setText("")
        self.File_name.setObjectName("File_name")
        self.label_11 = QtWidgets.QLabel(self.Measuring)
        self.label_11.setGeometry(QtCore.QRect(60, 750, 81, 16))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.Measuring)
        self.label_12.setGeometry(QtCore.QRect(80, 820, 71, 16))
        self.label_12.setObjectName("label_12")
        self.New_spec = GraphicsLayoutWidget(self.Measuring)
        self.New_spec.setGeometry(QtCore.QRect(50, 50, 551, 321))
        self.New_spec.setObjectName("New_spec")
        self.Old_spec = GraphicsLayoutWidget(self.Measuring)
        self.Old_spec.setGeometry(QtCore.QRect(50, 400, 551, 321))
        self.Old_spec.setObjectName("Old_spec")
        self.Run_Front = QtWidgets.QToolButton(self.Measuring)
        self.Run_Front.setGeometry(QtCore.QRect(830, 800, 91, 61))
        self.Run_Front.setArrowType(QtCore.Qt.NoArrow)
        self.Run_Front.setObjectName("Run_Front")
        self.Run_Home = QtWidgets.QToolButton(self.Measuring)
        self.Run_Home.setGeometry(QtCore.QRect(690, 800, 91, 61))
        self.Run_Home.setArrowType(QtCore.Qt.NoArrow)
        self.Run_Home.setObjectName("Run_Home")
        self.Run_Back = QtWidgets.QToolButton(self.Measuring)
        self.Run_Back.setGeometry(QtCore.QRect(550, 800, 91, 61))
        self.Run_Back.setArrowType(QtCore.Qt.NoArrow)
        self.Run_Back.setObjectName("Run_Back")
        self.Set_Home = QtWidgets.QToolButton(self.Measuring)
        self.Set_Home.setGeometry(QtCore.QRect(1440, 800, 81, 31))
        self.Set_Home.setArrowType(QtCore.Qt.NoArrow)
        self.Set_Home.setObjectName("Set_Home")
        self.Go_Home = QtWidgets.QToolButton(self.Measuring)
        self.Go_Home.setGeometry(QtCore.QRect(1440, 890, 81, 31))
        self.Go_Home.setArrowType(QtCore.Qt.NoArrow)
        self.Go_Home.setObjectName("Go_Home")
        self.Live = QtWidgets.QPushButton(self.Measuring)
        self.Live.setGeometry(QtCore.QRect(1044, 790, 81, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.Live.setFont(font)
        self.Live.setObjectName("Live")
        self.ExposureTime = QtWidgets.QLineEdit(self.Measuring)
        self.ExposureTime.setGeometry(QtCore.QRect(990, 860, 61, 20))
        self.ExposureTime.setText("")
        self.ExposureTime.setObjectName("ExposureTime")
        self.label_165 = QtWidgets.QLabel(self.Measuring)
        self.label_165.setGeometry(QtCore.QRect(980, 840, 91, 16))
        self.label_165.setObjectName("label_165")
        self.Abort = QtWidgets.QToolButton(self.Measuring)
        self.Abort.setGeometry(QtCore.QRect(1040, 890, 91, 41))
        self.Abort.setArrowType(QtCore.Qt.NoArrow)
        self.Abort.setObjectName("Abort")
        self.DelaySteps = QtWidgets.QLineEdit(self.Measuring)
        self.DelaySteps.setGeometry(QtCore.QRect(1120, 860, 61, 20))
        self.DelaySteps.setText("")
        self.DelaySteps.setObjectName("DelaySteps")
        self.label_166 = QtWidgets.QLabel(self.Measuring)
        self.label_166.setGeometry(QtCore.QRect(1120, 840, 81, 16))
        self.label_166.setObjectName("label_166")
        self.SelectPath = QtWidgets.QPushButton(self.Measuring)
        self.SelectPath.setGeometry(QtCore.QRect(60, 770, 75, 21))
        self.SelectPath.setObjectName("SelectPath")
        self.SaveSpectrum = QtWidgets.QToolButton(self.Measuring)
        self.SaveSpectrum.setGeometry(QtCore.QRect(690, 880, 91, 41))
        self.SaveSpectrum.setArrowType(QtCore.Qt.NoArrow)
        self.SaveSpectrum.setObjectName("SaveSpectrum")
        self.Run_Calib_Back = QtWidgets.QToolButton(self.Measuring)
        self.Run_Calib_Back.setGeometry(QtCore.QRect(550, 870, 91, 61))
        self.Run_Calib_Back.setArrowType(QtCore.Qt.NoArrow)
        self.Run_Calib_Back.setObjectName("Run_Calib_Back")
        self.Run_Calib_Front = QtWidgets.QToolButton(self.Measuring)
        self.Run_Calib_Front.setGeometry(QtCore.QRect(830, 870, 91, 61))
        self.Run_Calib_Front.setArrowType(QtCore.Qt.NoArrow)
        self.Run_Calib_Front.setObjectName("Run_Calib_Front")
        self.ProgressBar = QtWidgets.QProgressBar(self.Measuring)
        self.ProgressBar.setGeometry(QtCore.QRect(77, 890, 401, 23))
        self.ProgressBar.setProperty("value", 24)
        self.ProgressBar.setObjectName("ProgressBar")
        self.FROG = QtWidgets.QCheckBox(self.Measuring)
        self.FROG.setGeometry(QtCore.QRect(510, 730, 87, 20))
        self.FROG.setChecked(True)
        self.FROG.setAutoExclusive(False)
        self.FROG.setObjectName("FROG")
        self.buttonGroup_3 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_3.setObjectName("buttonGroup_3")
        self.buttonGroup_3.addButton(self.FROG)
        self.XFROG = QtWidgets.QCheckBox(self.Measuring)
        self.XFROG.setGeometry(QtCore.QRect(510, 750, 87, 20))
        self.XFROG.setAutoExclusive(False)
        self.XFROG.setObjectName("XFROG")
        self.buttonGroup_3.addButton(self.XFROG)
        self.Calibration_2.addTab(self.Measuring, "")
        self.Calibration = QtWidgets.QWidget()
        self.Calibration.setObjectName("Calibration")
        self.Calib_fft_bk = GraphicsLayoutWidget(self.Calibration)
        self.Calib_fft_bk.setGeometry(QtCore.QRect(1010, 50, 751, 421))
        self.Calib_fft_bk.setObjectName("Calib_fft_bk")
        self.Calib_fft_ft = GraphicsLayoutWidget(self.Calibration)
        self.Calib_fft_ft.setGeometry(QtCore.QRect(1010, 500, 751, 421))
        self.Calib_fft_ft.setObjectName("Calib_fft_ft")
        self.label_47 = QtWidgets.QLabel(self.Calibration)
        self.label_47.setGeometry(QtCore.QRect(850, 60, 91, 51))
        self.label_47.setAlignment(QtCore.Qt.AlignCenter)
        self.label_47.setObjectName("label_47")
        self.label_48 = QtWidgets.QLabel(self.Calibration)
        self.label_48.setGeometry(QtCore.QRect(850, 500, 91, 51))
        self.label_48.setAlignment(QtCore.Qt.AlignCenter)
        self.label_48.setObjectName("label_48")
        self.Calib_raw_bk = GraphicsLayoutWidget(self.Calibration)
        self.Calib_raw_bk.setGeometry(QtCore.QRect(30, 50, 751, 421))
        self.Calib_raw_bk.setObjectName("Calib_raw_bk")
        self.Calib_raw_ft = GraphicsLayoutWidget(self.Calibration)
        self.Calib_raw_ft.setGeometry(QtCore.QRect(30, 500, 751, 421))
        self.Calib_raw_ft.setObjectName("Calib_raw_ft")
        self.label_171 = QtWidgets.QLabel(self.Calibration)
        self.label_171.setGeometry(QtCore.QRect(830, 560, 141, 51))
        self.label_171.setAlignment(QtCore.Qt.AlignCenter)
        self.label_171.setObjectName("label_171")
        self.Back_Amplitude = QtWidgets.QLineEdit(self.Calibration)
        self.Back_Amplitude.setGeometry(QtCore.QRect(860, 610, 71, 31))
        self.Back_Amplitude.setText("")
        self.Back_Amplitude.setObjectName("Back_Amplitude")
        self.Front_Amplitude = QtWidgets.QLineEdit(self.Calibration)
        self.Front_Amplitude.setGeometry(QtCore.QRect(860, 180, 71, 31))
        self.Front_Amplitude.setText("")
        self.Front_Amplitude.setObjectName("Front_Amplitude")
        self.label_172 = QtWidgets.QLabel(self.Calibration)
        self.label_172.setGeometry(QtCore.QRect(820, 130, 161, 41))
        self.label_172.setAlignment(QtCore.Qt.AlignCenter)
        self.label_172.setObjectName("label_172")
        self.UpdateBack = QtWidgets.QToolButton(self.Calibration)
        self.UpdateBack.setGeometry(QtCore.QRect(850, 400, 91, 41))
        self.UpdateBack.setArrowType(QtCore.Qt.NoArrow)
        self.UpdateBack.setObjectName("UpdateBack")
        self.UpdateFront = QtWidgets.QToolButton(self.Calibration)
        self.UpdateFront.setGeometry(QtCore.QRect(850, 850, 91, 41))
        self.UpdateFront.setArrowType(QtCore.Qt.NoArrow)
        self.UpdateFront.setObjectName("UpdateFront")
        self.Back_all = QtWidgets.QCheckBox(self.Calibration)
        self.Back_all.setGeometry(QtCore.QRect(910, 270, 87, 20))
        self.Back_all.setObjectName("Back_all")
        self.buttonGroup = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.Back_all)
        self.Back_one = QtWidgets.QCheckBox(self.Calibration)
        self.Back_one.setGeometry(QtCore.QRect(910, 230, 87, 20))
        self.Back_one.setChecked(True)
        self.Back_one.setObjectName("Back_one")
        self.buttonGroup.addButton(self.Back_one)
        self.Front_one = QtWidgets.QCheckBox(self.Calibration)
        self.Front_one.setGeometry(QtCore.QRect(910, 660, 87, 20))
        self.Front_one.setChecked(True)
        self.Front_one.setObjectName("Front_one")
        self.buttonGroup_2 = QtWidgets.QButtonGroup(MainWindow)
        self.buttonGroup_2.setObjectName("buttonGroup_2")
        self.buttonGroup_2.addButton(self.Front_one)
        self.Front_all = QtWidgets.QCheckBox(self.Calibration)
        self.Front_all.setGeometry(QtCore.QRect(910, 700, 87, 20))
        self.Front_all.setObjectName("Front_all")
        self.buttonGroup_2.addButton(self.Front_all)
        self.Back_Amp_calib = QtWidgets.QLCDNumber(self.Calibration)
        self.Back_Amp_calib.setGeometry(QtCore.QRect(860, 770, 71, 31))
        self.Back_Amp_calib.setObjectName("Back_Amp_calib")
        self.Front_Amp_calib = QtWidgets.QLCDNumber(self.Calibration)
        self.Front_Amp_calib.setGeometry(QtCore.QRect(860, 340, 71, 31))
        self.Front_Amp_calib.setObjectName("Front_Amp_calib")
        self.label_172.raise_()
        self.Calib_fft_bk.raise_()
        self.Calib_fft_ft.raise_()
        self.label_47.raise_()
        self.label_48.raise_()
        self.Calib_raw_bk.raise_()
        self.Calib_raw_ft.raise_()
        self.label_171.raise_()
        self.Back_Amplitude.raise_()
        self.UpdateBack.raise_()
        self.UpdateFront.raise_()
        self.Back_all.raise_()
        self.Back_one.raise_()
        self.Front_one.raise_()
        self.Front_all.raise_()
        self.Back_Amp_calib.raise_()
        self.Front_Amp_calib.raise_()
        self.Front_Amplitude.raise_()
        self.Calibration_2.addTab(self.Calibration, "")
        self.Frogger = QtWidgets.QWidget()
        self.Frogger.setObjectName("Frogger")
        self.Intensity_Wavelength = GraphicsLayoutWidget(self.Frogger)
        self.Intensity_Wavelength.setGeometry(QtCore.QRect(1000, 40, 771, 421))
        self.Intensity_Wavelength.setObjectName("Intensity_Wavelength")
        self.Intensity_Time = GraphicsLayoutWidget(self.Frogger)
        self.Intensity_Time.setGeometry(QtCore.QRect(1000, 510, 771, 421))
        self.Intensity_Time.setObjectName("Intensity_Time")
        self.Spec_Manipulation = GraphicsLayoutWidget(self.Frogger)
        self.Spec_Manipulation.setGeometry(QtCore.QRect(50, 40, 591, 421))
        self.Spec_Manipulation.setObjectName("Spec_Manipulation")
        self.Set_ROI = QtWidgets.QToolButton(self.Frogger)
        self.Set_ROI.setGeometry(QtCore.QRect(700, 80, 75, 24))
        self.Set_ROI.setObjectName("Set_ROI")
        self.C = QtWidgets.QToolButton(self.Frogger)
        self.C.setGeometry(QtCore.QRect(700, 130, 75, 24))
        self.C.setObjectName("C")
        self.E = QtWidgets.QToolButton(self.Frogger)
        self.E.setGeometry(QtCore.QRect(700, 180, 75, 24))
        self.E.setObjectName("E")
        self.F = QtWidgets.QToolButton(self.Frogger)
        self.F.setGeometry(QtCore.QRect(700, 230, 75, 24))
        self.F.setObjectName("F")
        self.Submit = QtWidgets.QToolButton(self.Frogger)
        self.Submit.setGeometry(QtCore.QRect(700, 410, 75, 24))
        self.Submit.setObjectName("Submit")
        self.Retrieved = GraphicsLayoutWidget(self.Frogger)
        self.Retrieved.setGeometry(QtCore.QRect(50, 500, 591, 411))
        self.Retrieved.setObjectName("Retrieved")
        self.Stop = QtWidgets.QToolButton(self.Frogger)
        self.Stop.setGeometry(QtCore.QRect(740, 850, 75, 24))
        self.Stop.setObjectName("Stop")
        self.label_13 = QtWidgets.QLabel(self.Frogger)
        self.label_13.setGeometry(QtCore.QRect(700, 570, 49, 16))
        self.label_13.setObjectName("label_13")
        self.lcdNumber = QtWidgets.QLCDNumber(self.Frogger)
        self.lcdNumber.setGeometry(QtCore.QRect(780, 570, 64, 23))
        self.lcdNumber.setObjectName("lcdNumber")
        self.lcdNumber_2 = QtWidgets.QLCDNumber(self.Frogger)
        self.lcdNumber_2.setGeometry(QtCore.QRect(780, 610, 64, 23))
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.label_14 = QtWidgets.QLabel(self.Frogger)
        self.label_14.setGeometry(QtCore.QRect(700, 610, 49, 16))
        self.label_14.setObjectName("label_14")
        self.lcdNumber_3 = QtWidgets.QLCDNumber(self.Frogger)
        self.lcdNumber_3.setGeometry(QtCore.QRect(780, 650, 64, 23))
        self.lcdNumber_3.setObjectName("lcdNumber_3")
        self.label_15 = QtWidgets.QLabel(self.Frogger)
        self.label_15.setGeometry(QtCore.QRect(700, 650, 49, 16))
        self.label_15.setObjectName("label_15")
        self.lcdNumber_4 = QtWidgets.QLCDNumber(self.Frogger)
        self.lcdNumber_4.setGeometry(QtCore.QRect(780, 690, 64, 23))
        self.lcdNumber_4.setObjectName("lcdNumber_4")
        self.label_16 = QtWidgets.QLabel(self.Frogger)
        self.label_16.setGeometry(QtCore.QRect(700, 690, 49, 16))
        self.label_16.setObjectName("label_16")
        self.lcdNumber_5 = QtWidgets.QLCDNumber(self.Frogger)
        self.lcdNumber_5.setGeometry(QtCore.QRect(780, 730, 64, 23))
        self.lcdNumber_5.setObjectName("lcdNumber_5")
        self.label_17 = QtWidgets.QLabel(self.Frogger)
        self.label_17.setGeometry(QtCore.QRect(700, 730, 49, 16))
        self.label_17.setObjectName("label_17")
        self.lcdNumber_6 = QtWidgets.QLCDNumber(self.Frogger)
        self.lcdNumber_6.setGeometry(QtCore.QRect(780, 770, 64, 23))
        self.lcdNumber_6.setObjectName("lcdNumber_6")
        self.label_18 = QtWidgets.QLabel(self.Frogger)
        self.label_18.setGeometry(QtCore.QRect(700, 770, 49, 16))
        self.label_18.setObjectName("label_18")
        self.Reset_ROI = QtWidgets.QToolButton(self.Frogger)
        self.Reset_ROI.setGeometry(QtCore.QRect(700, 40, 75, 24))
        self.Reset_ROI.setObjectName("Reset_ROI")
        self.Calibration_2.addTab(self.Frogger, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.FROGOMETER = QtWidgets.QToolBar(MainWindow)
        self.FROGOMETER.setObjectName("FROGOMETER")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.FROGOMETER)

        self.retranslateUi(MainWindow)
        self.Calibration_2.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Forward.setText(_translate("MainWindow", "..."))
        self.Back_Fast.setText(_translate("MainWindow", "..."))
        self.Back.setText(_translate("MainWindow", "..."))
        self.Forward_Fast.setText(_translate("MainWindow", "..."))
        self.label_5.setText(_translate("MainWindow", "Note: Home will only get "))
        self.label_6.setText(_translate("MainWindow", "you roughly back to centre "))
        self.label_7.setText(_translate("MainWindow", "Back Fast"))
        self.label_8.setText(_translate("MainWindow", "Back"))
        self.label_9.setText(_translate("MainWindow", "Forward Fast"))
        self.label_10.setText(_translate("MainWindow", "Forward"))
        self.label_11.setText(_translate("MainWindow", "Save Location:"))
        self.label_12.setText(_translate("MainWindow", "File Name:"))
        self.Run_Front.setText(_translate("MainWindow", "Run from Front"))
        self.Run_Home.setText(_translate("MainWindow", "Run from Home"))
        self.Run_Back.setText(_translate("MainWindow", "Run from Back"))
        self.Set_Home.setText(_translate("MainWindow", "Set Home"))
        self.Go_Home.setText(_translate("MainWindow", "Go to Home"))
        self.Live.setText(_translate("MainWindow", "Live"))
        self.label_165.setText(_translate("MainWindow", "Exposure Time :"))
        self.Abort.setText(_translate("MainWindow", "ABORT"))
        self.label_166.setText(_translate("MainWindow", "Delay Steps:"))
        self.SelectPath.setText(_translate("MainWindow", "Select Path"))
        self.SaveSpectrum.setText(_translate("MainWindow", "Save Spec"))
        self.Run_Calib_Back.setText(_translate("MainWindow", "Run calibration \n"
"from back"))
        self.Run_Calib_Front.setText(_translate("MainWindow", "Run calibration \n"
"from front"))
        self.FROG.setText(_translate("MainWindow", "FROG"))
        self.XFROG.setText(_translate("MainWindow", "XFROG"))
        self.Calibration_2.setTabText(self.Calibration_2.indexOf(self.Measuring), _translate("MainWindow", "Measuring"))
        self.label_47.setText(_translate("MainWindow", "<html><head/><body><p>Run from back </p><p>calibration</p></body></html>"))
        self.label_48.setText(_translate("MainWindow", "<html><head/><body><p>Run from front </p><p>calibration</p></body></html>"))
        self.label_171.setText(_translate("MainWindow", "<html><head/><body><p>Back step amplitude :</p></body></html>"))
        self.label_172.setText(_translate("MainWindow", "<html><head/><body><p>Forwards step amplitude :</p></body></html>"))
        self.UpdateBack.setText(_translate("MainWindow", "Update back\n"
"calibration"))
        self.UpdateFront.setText(_translate("MainWindow", "Update front\n"
"calibration"))
        self.Back_all.setText(_translate("MainWindow", "Plot all"))
        self.Back_one.setText(_translate("MainWindow", "Plot one"))
        self.Front_one.setText(_translate("MainWindow", "Plot one"))
        self.Front_all.setText(_translate("MainWindow", "Plot all"))
        self.Calibration_2.setTabText(self.Calibration_2.indexOf(self.Calibration), _translate("MainWindow", "Calibration"))
        self.Set_ROI.setText(_translate("MainWindow", "Set ROI"))
        self.C.setText(_translate("MainWindow", "C"))
        self.E.setText(_translate("MainWindow", "E"))
        self.F.setText(_translate("MainWindow", "F"))
        self.Submit.setText(_translate("MainWindow", "Submit"))
        self.Stop.setText(_translate("MainWindow", "Stop"))
        self.label_13.setText(_translate("MainWindow", "TextLabel"))
        self.label_14.setText(_translate("MainWindow", "TextLabel"))
        self.label_15.setText(_translate("MainWindow", "TextLabel"))
        self.label_16.setText(_translate("MainWindow", "TextLabel"))
        self.label_17.setText(_translate("MainWindow", "TextLabel"))
        self.label_18.setText(_translate("MainWindow", "TextLabel"))
        self.Reset_ROI.setText(_translate("MainWindow", "Reset ROI"))
        self.Calibration_2.setTabText(self.Calibration_2.indexOf(self.Frogger), _translate("MainWindow", "Frogger"))
        self.FROGOMETER.setWindowTitle(_translate("MainWindow", "toolBar"))
from pyqtgraph import GraphicsLayoutWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
