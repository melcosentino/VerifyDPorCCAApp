# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'DPorCCA.ui'
# Created by: PyQt5 UI code generator 5.15.0
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import os
import pathlib
import tkinter as tk
import warnings
import zipfile
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tkinter import filedialog

import pandas as pd
import pyqtgraph as pg
import soundfile
from PyQt5 import QtCore, QtGui, QtWidgets

import ct_signal
import comparison_CPOD

warnings.filterwarnings("ignore", category=RuntimeWarning)
pd.options.mode.chained_assignment = None

# import PAMGuardFunc
# TODO import Clea's algorithms
# import PyHydrophones # need to install first

global BrowseSelectedFolder, CTInfo, CTTemp, NHyd, CP, SelectedFolder, topLevelFolderMetrics
global thisFolder, sset, srise, VerifyCT

"""
Creates pop up windows 
"""

# Fixed parameters
NFFT = 512
Overlap = 128


class WinTable(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title = ''
        self.top = 100
        self.left = 100
        self.width = 360
        self.height = 500
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


"""
The main tab includes 3 axes to visualise the amplitude, repetition rates, and 
frequency variations within click trains 
"""


class Ui_MainWindow(object):
    def __init__(self):
        # Main Display
        self.MainDisplayTab = QtWidgets.QWidget()
        self.DisplaySettings = QtWidgets.QFrame(self.MainDisplayTab)
        self.AxesPan = QtWidgets.QFrame(self.MainDisplayTab)

        # Validate pan
        self.ActionPan = QtWidgets.QFrame(self.MainDisplayTab)
        self.ActionLabel = QtWidgets.QLabel(self.ActionPan)
        self.WaveAxes = pg.PlotWidget(self.ActionPan)
        self.SpectAxes = pg.PlotWidget(self.ActionPan)
        # self.SpectAxes = plt.Axes(fig=self.ActionPan, rect=[10, 60, 340, 300]) #  pg.PlotWidget(self.ActionPan)

        # Validate
        # self.CT3DPan = QtWidgets.QFrame(self.ActionPan)
        self.wrong_button = QtWidgets.QPushButton(self.DisplaySettings)
        self.right_button = QtWidgets.QPushButton(self.DisplaySettings)
        self.upload_val_data = QtWidgets.QPushButton(self.DisplaySettings)
        # self.CTin3D = QtWidgets.QPushButton(self.CT3DPan)

        # Axes
        self.AmpAxesCT = pg.PlotWidget(self.AxesPan)

        self.ICIAxesCT = pg.PlotWidget(self.AxesPan)  # used to be QGraphicsView

        self.FreqAxesCT = pg.PlotWidget(self.AxesPan)

        self.AmpAxesCT.setBackground(background='w')
        self.ICIAxesCT.setBackground(background='w')
        self.FreqAxesCT.setBackground(background='w')
        self.AmpAxesCT.showAxis('bottom', show=False)
        self.ICIAxesCT.showAxis('bottom', show=False)
        self.AmplitudeDB = QtWidgets.QLabel(self.AxesPan)

        self.FreqPan = QtWidgets.QFrame(self.AxesPan)
        # self.DirectionofarrivalButton = QtWidgets.QRadioButton(self.FreqPan)
        self.CentroidfrequencykHzButton = QtWidgets.QRadioButton(self.FreqPan)
        self.ICIPan = QtWidgets.QFrame(self.AxesPan)
        self.ClickspersecondButton = QtWidgets.QRadioButton(self.ICIPan)
        # self.InterclickintervalmsButton = QtWidgets.QRadioButton(self.ICIPan)

        self.save_button = QtWidgets.QPushButton(self.DisplaySettings)

        self.CTPan = QtWidgets.QFrame(self.DisplaySettings)
        self.CTTypeLabel = QtWidgets.QLabel(self.CTPan)
        self.CTLabel = QtWidgets.QLabel(self.CTPan)
        self.CorrPan = QtWidgets.QFrame(self.DisplaySettings)
        self.CorrLabel = QtWidgets.QLabel(self.CorrPan)
        self.CorrText = QtWidgets.QLabel(self.CorrPan)
        self.VerPan = QtWidgets.QFrame(self.DisplaySettings)
        self.VerLabel = QtWidgets.QLabel(self.VerPan)
        self.VerText = QtWidgets.QLabel(self.VerPan)
        self.CTInfoPan = QtWidgets.QFrame(self.DisplaySettings)
        self.TotalLabel = QtWidgets.QLabel(self.CTInfoPan)
        self.CTForw = QtWidgets.QPushButton(self.CTInfoPan)
        self.CTNumD = QtWidgets.QLineEdit(self.CTInfoPan)
        self.CTNumD.setStyleSheet("QLineEdit{background: white}")
        self.CTBack = QtWidgets.QPushButton(self.CTInfoPan)
        self.CTNumLabel = QtWidgets.QLabel(self.CTInfoPan)
        self.DatePan = QtWidgets.QFrame(self.DisplaySettings)
        self.DateandtimeofCTLabel = QtWidgets.QLabel(self.DatePan)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.MainTab = QtWidgets.QTabWidget(self.centralwidget)
        self.DateLabel = QtWidgets.QLabel(self.DatePan)
        self.SelectLabel = QtWidgets.QLabel(self.DisplaySettings)
        self.FolderPathDet = QtWidgets.QLineEdit(self.DisplaySettings)
        self.browse_button = QtWidgets.QPushButton(self.DisplaySettings)
        self.cpod = QtWidgets.QCheckBox(self.DisplaySettings)
        self.start_date = QtWidgets.QPlainTextEdit(self.DisplaySettings)
        self.end_date = QtWidgets.QPlainTextEdit(self.DisplaySettings)
        self.startdateLabel = QtWidgets.QLabel(self.DisplaySettings)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 950)
        MainWindow.setMinimumSize(QtCore.QSize(1500, 950))
        MainWindow.setMaximumSize(QtCore.QSize(1500, 950))

        ###########################################################
        # MAIN TABS
        ###########################################################
        self.centralwidget.setObjectName("centralwidget")
        self.MainTab.setGeometry(QtCore.QRect(40, 30, 1480, 900))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MainTab.sizePolicy().hasHeightForWidth())
        self.MainTab.setSizePolicy(sizePolicy)
        self.MainTab.setMinimumSize(QtCore.QSize(1400, 900))
        self.MainTab.setMaximumSize(QtCore.QSize(1400, 900))
        self.MainTab.setStyleSheet("background-color: rgb(240, 240, 238)")
        self.MainTab.setObjectName("MainTab")
        self.MainDisplayTab.setObjectName("MainDisplayTab")
        ####################
        # DISPLAY PARAMETERS
        ####################
        self.DisplaySettings.setGeometry(QtCore.QRect(10, 15, 1370, 122))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DisplaySettings.sizePolicy().hasHeightForWidth())
        self.DisplaySettings.setSizePolicy(sizePolicy)
        self.DisplaySettings.setFrameShape(QtWidgets.QFrame.Box)
        self.DisplaySettings.setFrameShadow(QtWidgets.QFrame.Raised)
        self.DisplaySettings.setObjectName("DisplaySettings")
        # Date area
        self.DatePan.setGeometry(QtCore.QRect(10, 8, 200, 106))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DatePan.sizePolicy().hasHeightForWidth())
        self.DatePan.setSizePolicy(sizePolicy)
        self.DatePan.setFrameShape(QtWidgets.QFrame.Box)
        self.DatePan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.DatePan.setObjectName("DatePan")
        self.DateandtimeofCTLabel.setGeometry(QtCore.QRect(5, 60, 180, 30))
        self.DateandtimeofCTLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.DateandtimeofCTLabel.setObjectName("DateandtimeofCTLabel")
        self.DateLabel.setGeometry(QtCore.QRect(80, 20, 50, 30))
        self.DateLabel.setTextFormat(QtCore.Qt.RichText)
        self.DateLabel.setObjectName("DateLabel")
        # CT Type area
        self.CTPan.setGeometry(QtCore.QRect(215, 8, 95, 106))
        self.CTPan.setFrameShape(QtWidgets.QFrame.Box)
        self.CTPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CTPan.setObjectName("CTPan")
        self.CTLabel.setGeometry(QtCore.QRect(10, 20, 70, 30))
        self.CTLabel.setTextFormat(QtCore.Qt.RichText)
        self.CTLabel.setObjectName("CTLabel")
        self.CTTypeLabel.setGeometry(QtCore.QRect(5, 60, 80, 30))
        self.CTTypeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CTTypeLabel.setObjectName("CTTypeLabel")
        # Correction section
        self.CorrPan.setGeometry(QtCore.QRect(315, 8, 80, 106))
        self.CorrPan.setFrameShape(QtWidgets.QFrame.Box)
        self.CorrPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CorrPan.setObjectName("CorrPan")
        self.CorrLabel.setGeometry(QtCore.QRect(10, 20, 60, 30))
        self.CorrLabel.setTextFormat(QtCore.Qt.RichText)
        self.CorrLabel.setObjectName("CorrLabel")
        self.CorrText.setGeometry(QtCore.QRect(20, 60, 50, 30))
        self.CorrText.setAlignment(QtCore.Qt.AlignCenter)
        self.CorrText.setObjectName("CorrText")
        # Correction section
        self.VerPan.setGeometry(QtCore.QRect(400, 8, 80, 106))
        self.VerPan.setFrameShape(QtWidgets.QFrame.Box)
        self.VerPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.VerPan.setObjectName("VerPan")
        self.VerLabel.setGeometry(QtCore.QRect(10, 20, 60, 30))
        self.VerLabel.setTextFormat(QtCore.Qt.RichText)
        self.VerLabel.setObjectName("VerLabel")
        self.VerText.setGeometry(QtCore.QRect(20, 60, 50, 30))
        self.VerText.setAlignment(QtCore.Qt.AlignCenter)
        self.VerText.setObjectName("VerText")
        # CT Info area
        self.CTInfoPan.setGeometry(QtCore.QRect(485, 8, 210, 106))
        self.CTInfoPan.setFrameShape(QtWidgets.QFrame.Box)
        self.CTInfoPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CTInfoPan.setObjectName("CTInfoPan")
        self.CTNumLabel.setGeometry(QtCore.QRect(35, 20, 230, 30))
        self.CTNumLabel.setTextFormat(QtCore.Qt.RichText)
        self.CTNumLabel.setObjectName("CTNumLabel")
        self.CTBack.setGeometry(QtCore.QRect(10, 60, 40, 30))
        self.CTBack.setObjectName("CTBack")
        self.CTBack.clicked.connect(self.ct_back)
        self.CTNumD.setGeometry(QtCore.QRect(53, 60, 80, 30))
        self.CTNumD.setObjectName("CTNumD")
        self.CTForw.setGeometry(QtCore.QRect(136, 60, 40, 30))
        self.CTForw.setObjectName("CTForw")
        self.CTForw.clicked.connect(self.ct_forward)
        self.TotalLabel.setGeometry(QtCore.QRect(210, 60, 70, 30))
        self.TotalLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.TotalLabel.setObjectName("TotalLabel")

        # Save button
        self.save_button.setGeometry(QtCore.QRect(1270, 8, 95, 106))
        self.save_button.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.save_button.setAutoDefault(False)
        self.save_button.setDefault(False)
        self.save_button.setFlat(False)
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_updates)
        ##################
        ## AXES AREA
        ##################
        pg.setConfigOption('background', 'w')
        self.AxesPan.setGeometry(QtCore.QRect(10, 150, 740, 700))
        self.AxesPan.setFrameShape(QtWidgets.QFrame.Box)
        self.AxesPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.AxesPan.setObjectName("AxesPan")
        # AMPLITUDE
        self.AmplitudeDB.setGeometry(QtCore.QRect(250, 7, 300, 20))
        self.AmplitudeDB.setObjectName("AmplitudeDB")
        # Axes to plot STEM
        self.AmpAxesCT.setGeometry(QtCore.QRect(20, 35, 700, 192))
        self.AmpAxesCT.setObjectName("AmpAxesCT")
        # ICI / CPS
        self.ICIAxesCT.setGeometry(QtCore.QRect(20, 239, 700, 214))
        self.ICIAxesCT.setObjectName("ICIAxesCT")
        self.ICIPan.setGeometry(QtCore.QRect(250, 214, 300, 42))
        self.ICIPan.setFrameShape(QtWidgets.QFrame.Box)
        self.ICIPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ICIPan.setObjectName("ICIPan")
        # CPS radio button
        self.ClickspersecondButton.setGeometry(QtCore.QRect(50, 10, 200, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ClickspersecondButton.setFont(font)
        self.ClickspersecondButton.setObjectName("ClickspersecondButton")
        self.ClickspersecondButton.setChecked(True)

        self.FreqAxesCT.setGeometry(QtCore.QRect(20, 464, 700, 210))
        self.FreqAxesCT.setObjectName("FreqAxesCT")
        self.FreqPan.setGeometry(QtCore.QRect(250, 434, 300, 42))
        self.FreqPan.setFrameShape(QtWidgets.QFrame.Box)
        self.FreqPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FreqPan.setObjectName("FreqPan")
        # Frequency radio button
        self.CentroidfrequencykHzButton.setGeometry(QtCore.QRect(50, 10, 200, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.CentroidfrequencykHzButton.setFont(font)
        self.CentroidfrequencykHzButton.setObjectName("CentroidfrequencykHzButton")
        self.CentroidfrequencykHzButton.setChecked(True)

        # ACTION AREA
        self.ActionPan.setGeometry(QtCore.QRect(760, 150, 620, 700))
        self.ActionPan.setFrameShape(QtWidgets.QFrame.Box)
        self.ActionPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ActionPan.setObjectName("ActionPan")
        self.ActionLabel.setGeometry(QtCore.QRect(40, 20, 250, 30))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ActionLabel.setFont(font)
        self.ActionLabel.setObjectName("ActionLabel")
        # Waveform & spectrogram
        self.WaveAxes.setGeometry(10, 60, 600, 300)
        self.WaveAxes.setObjectName("WaveAxes")
        self.SpectAxes.setGeometry(QtCore.QRect(10, 400, 600, 300))
        self.SpectAxes.setObjectName("SpectAxes")
        # Browse button
        self.SelectLabel.setGeometry(750, 8, 130, 20)
        self.SelectLabel.setText('Select a folder')
        self.FolderPathDet.setGeometry(750, 35, 300, 30)
        self.FolderPathDet.setText("C:/")
        # button
        self.browse_button.setGeometry(1060, 35, 100, 30)
        self.browse_button.setText("Browse")
        self.browse_button.clicked.connect(self.click_browse_button)
        # CPOD txt output
        self.cpod.setGeometry(900, 5, 200, 30)
        self.cpod.setText('Compare CPOD')
        self.cpod.setChecked(False)
        # CPOD start and end date
        self.start_date.setGeometry(750, 82, 200, 30)
        self.startdateLabel.setGeometry(750, 65, 300, 30)
        self.startdateLabel.setText('Start and end date in yyyy-mm-dd HH:MM')
        self.end_date.setGeometry(960, 82, 200, 30)
        # Upload data
        self.upload_val_data.setGeometry(QtCore.QRect(1165, 8, 100, 106))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.upload_val_data.setFont(font)
        self.upload_val_data.setObjectName("upload_val_data")
        self.upload_val_data.clicked.connect(self.upload_data)
        self.wrong_button.setGeometry(QtCore.QRect(700, 8, 40, 48))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        # Spectrogram area
        self.wrong_button.setFont(font)
        self.wrong_button.setObjectName("wrong_button")
        self.wrong_button.clicked.connect(self.put_wrong)

        self.right_button.setGeometry(QtCore.QRect(700, 65, 40, 48))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        # Spectrogram area
        self.right_button.setFont(font)
        self.right_button.setObjectName("right_button")
        self.right_button.clicked.connect(self.put_right)

        self.MainTab.addTab(self.MainDisplayTab, "")

        ########################################################
        # METRICS DISPLAY
        #######################################################
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.MainTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Validation app"))
        self.DateandtimeofCTLabel.setText(_translate("MainWindow", "12 Aug 2015, 12.35.32"))
        self.CTNumLabel.setText(_translate("MainWindow",
                                           "<html><head/><body><p><span style=\" font-weight:600\">Click train number "
                                           "(Total)</span></p></body></html>"))
        self.CTForw.setText(_translate("MainWindow", ">"))
        self.CTBack.setText(_translate("MainWindow", "<"))
        self.TotalLabel.setText(_translate("MainWindow", ""))
        self.CorrLabel.setText(_translate("MainWindow",
                                          "<html><head/><body><p><span style=\" "
                                          "font-weight:600\">Correct</span></p></body></html>"))
        self.VerLabel.setText(_translate("MainWindow",
                                          "<html><head/><body><p><span style=\" "
                                          "font-weight:600\">Done</span></p></body></html>"))
        self.save_button.setText(_translate("MainWindow", " Save \n"
                                                                "changes"))
        self.CTLabel.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" font-weight:600\">CT "
                                        "Type</span></p></body></html>"))
        self.CTTypeLabel.setText(_translate("MainWindow", "NBHF"))
        self.CorrText.setText(_translate("MainWindow", "1"))
        self.VerText.setText(_translate("MainWindow", "1"))
        self.DateLabel.setText(_translate("MainWindow",
                                          "<html><head/><body><p><span style=\" "
                                          "font-weight:600\">Date</span></p></body></html>"))
        self.ActionLabel.setText(_translate("MainWindow", "Waveform and spectrogram"))
        self.upload_val_data.setText(_translate("MainWindow", "Upload \n"
                                                              "data"))
        self.wrong_button.setText(_translate("MainWindow", "X"))
        self.right_button.setText(_translate("MainWindow", "OK"))
        #        self.CTin3D.setText(_translate("MainWindow", "See CT in 3D"))
        self.AmplitudeDB.setText(_translate("MainWindow",
                                            "<html><head/><body><p><span style=\" font-weight:600\">Amplitude ("
                                            "dB re: 1uPa)</span></p></body></html>"))
        # self.InterclickintervalmsButton.setText(_translate("MainWindow", "Inter-click interval"))
        self.ClickspersecondButton.setText(_translate("MainWindow", "Clicks per second"))
        self.CentroidfrequencykHzButton.setText(_translate("MainWindow", "Centroid Frequency"))
        # self.DirectionofarrivalButton.setText(_translate("MainWindow", "Direction of arrival"))
        self.MainTab.setTabText(self.MainTab.indexOf(self.MainDisplayTab), _translate("MainWindow", "Main Display"))

    def ct_back(self):
        """
        Displays the previous click train
        """
        num_ct = int(self.CTNumD.text())
        first = VerifyCT['NewCT'].iloc[0]
        if num_ct > first:
            self.AmpAxesCT.clear()
            self.ICIAxesCT.clear()
            self.FreqAxesCT.clear()
            row_ct = VerifyCT[VerifyCT.NewCT == num_ct].index[0]
            num_ct = VerifyCT.NewCT[row_ct - 1]
            self.update_ct(num_ct, CP, CTInfo, VerifyCT)

    def ct_forward(self):
        """
        Displays the next click train
        """
        num_ct = int(self.CTNumD.text())
        tot = VerifyCT['NewCT'].iloc[-1]
        if num_ct == tot:
            print(num_ct, tot)  # do nothing
        elif num_ct < tot:
            self.AmpAxesCT.clear()
            self.ICIAxesCT.clear()
            self.FreqAxesCT.clear()
            row_ct = VerifyCT[VerifyCT.NewCT == num_ct].index[0]
            num_ct = VerifyCT.NewCT[row_ct + 1]
            self.update_ct(num_ct, CP, CTInfo, VerifyCT)

    def update_ct(self, num_ct, CP, CTInfo, VerifyCT):
        """
        This function updates the plots in the main display
        :param num_ct: int
                click train number
        :param CP: pandas dataframe
                Contains parameters of all clicks classified as high- or low-quality harbour porpoise clicks
        :param CTInfo: pandas dataframe
                Contains summary information of all click trains identified in the data
        ---

        CTTemp: pandas database
                click train that is being displayed. It is selected based on the new click train number, given in
                chronological order when all click trains are put together for validation purposes
        AmpAxesCT: pyqtgraph PlotWidget
                Displays amplitude (dB re: 1uPa) variations within the click train as vertical lines
        ICIAxesCT: pyqtgraph PlotWidget
                Displays repetition rate (Clicks per second) variation within the click train as scatter plot
        FreqAxesCT: pyqtgraph PlotWidget
                Displays variations of the centroid frequency (kHz) within the click train as vertical lines
        """

        global CTTemp
        CTTemp = CP[CP.NewCT == num_ct]
        CTTemp.reset_index(inplace=True)
        self.fs = CTTemp.duration_samples.iloc[0] / (CTTemp.duration_us.iloc[0] / 1e6)
        CTTemp = self.NewICI(CTTemp)
        CTTemp.loc[:, 'SumMs'] = int(0)
        for i in range(1, len(CTTemp)):
            CTTemp.SumMs[i] = int(CTTemp.SumMs[i - 1]) + int(CTTemp.ICI[i])
        CTTemp.SumMs = CTTemp.SumMs / 1000
        CT1HQ = CTTemp[CTTemp['pyPorCC'] == 1]
        CT1LQ = CTTemp[CTTemp['pyPorCC'] == 2]
        self.CTNumD.setText(str(num_ct))
        self.CTTypeLabel.setText(str(VerifyCT.CTType[VerifyCT.NewCT == num_ct].values[0]))
        self.DateandtimeofCTLabel.setText(str(CTInfo.Date[CTInfo.NewCT == num_ct].values[0]))
        self.TotalLabel.setText('(' + str(CTInfo['NewCT'].iloc[-1]) + ')')
        self.CorrText.setText(str(VerifyCT.Corr[VerifyCT.NewCT == num_ct].values[0]))
        self.VerText.setText(str(VerifyCT.Verified[VerifyCT.NewCT == num_ct].values[0]))

        self.AmpAxesCT.clear()
        # TODO set the max and min in all axis (think of SoundTrap data)
        WidthBar = max(CTTemp.SumMs) / 500
        AmpLinesLQ = pg.BarGraphItem(x=CT1LQ.SumMs, height=CT1LQ.amplitude, brush='b', width=WidthBar)
        AmpLinesHQ = pg.BarGraphItem(x=CT1HQ.SumMs, height=CT1HQ.amplitude, brush='r', width=WidthBar)
        AmpDotsLQ = pg.ScatterPlotItem(x=CT1LQ.SumMs, y=CT1LQ.amplitude, symbol='o', brush='b', width=0.2)
        AmpDotsHQ = pg.ScatterPlotItem(x=CT1HQ.SumMs, y=CT1HQ.amplitude, symbol='o', brush='r', width=0.2)
        self.AmpAxesCT.addItem(AmpLinesLQ)
        self.AmpAxesCT.addItem(AmpDotsLQ)
        self.AmpAxesCT.addItem(AmpLinesHQ)
        self.AmpAxesCT.addItem(AmpDotsHQ)
        self.AmpAxesCT.setXRange(0, max(CTTemp.SumMs) + 0.1)
        self.AmpAxesCT.setYRange(80, 150)

        # plot click per second (default) or ICI
        # ICIorCPS = self.InterclickintervalmsButton.isChecked()

        # if ICIorCPS == 1:
        #     ICILQ = CT1LQ.ICI.to_list()
        #     ICIHQ = CT1HQ.ICI.to_list()
        #     ICIDotsLQ = pg.ScatterPlotItem(x=CT1LQ.SumMs, y=ICILQ, symbol='o', brush='b', width=2)
        #     ICIDotsHQ = pg.ScatterPlotItem(x=CT1HQ.SumMs, y=ICIHQ, symbol='o', brush='r', width=2)
        #     self.ICIAxesCT.addItem(ICIDotsLQ)
        #     self.ICIAxesCT.addItem(ICIDotsHQ)
        #     self.ICIAxesCT.setXRange(0, max(CTTemp.SumMs) + 0.1)
        #     self.ICIAxesCT.setYRange(0, max(CTTemp.ICI[2:-1]) + 10)
        # else:
        # plot clicks per second
        CPSLQ = CT1LQ.CPS.to_list()
        CPSHQ = CT1HQ.CPS.to_list()
        CPSDotsLQ = pg.ScatterPlotItem(x=CT1LQ.SumMs, y=CPSLQ, symbol='o', brush='b', width=2)
        CPSDotsHQ = pg.ScatterPlotItem(x=CT1HQ.SumMs, y=CPSHQ, symbol='o', brush='r', width=2)
        self.ICIAxesCT.addItem(CPSDotsLQ)
        self.ICIAxesCT.addItem(CPSDotsHQ)
        self.ICIAxesCT.setXRange(0, max(CTTemp.SumMs) + 0.1)
        self.ICIAxesCT.setYRange(0, max(CTTemp.CPS[2:-1]) + 30)

        FreqLQ = CT1LQ.CF / 1000
        FreqHQ = CT1HQ.CF / 1000
        FreqLQ = FreqLQ.to_list()
        FreqHQ = FreqHQ.to_list()
        FreqLinesLQ = pg.BarGraphItem(x=CT1LQ.SumMs, height=FreqLQ, brush='b', width=WidthBar)
        FreqLinesHQ = pg.BarGraphItem(x=CT1HQ.SumMs, height=FreqHQ, brush='r', width=WidthBar)
        FreqDotsLQ = pg.ScatterPlotItem(x=CT1LQ.SumMs, y=FreqLQ, symbol='o', brush='b', width=2)
        FreqDotsHQ = pg.ScatterPlotItem(x=CT1HQ.SumMs, y=FreqHQ, symbol='o', brush='r', width=2)
        self.FreqAxesCT.addItem(FreqLinesLQ)
        self.FreqAxesCT.addItem(FreqDotsLQ)
        self.FreqAxesCT.addItem(FreqLinesHQ)
        self.FreqAxesCT.addItem(FreqDotsHQ)
        self.FreqAxesCT.setXRange(0, max(CTTemp.SumMs) + 0.1)
        self.FreqAxesCT.setYRange(50, 180)
        self.CreateSpectrogram()

    def NewICI(self, myTable):
        """
        Calculates inter-click intervals and repetition rates after rows have been removed
        :param
        myTable: pandas dataframe
                Either CP or CTTemp
        :return:
        myTable updated
        """
        StartSample = myTable["start_sample"]
        myTable.ICI = StartSample.diff() / (self.fs / 1000)
        myTable["CPS"] = 1000 / myTable["ICI"]
        myTable.iloc[0]['CPS'] = 0
        myTable.iloc[0]['ICI'] = 0
        return myTable

    def put_wrong(self):
        """
        Inserts '0' in the appropriate row in column "Corr" in CTInfo, to indicate the classification of the click train
        as one produced by a harbour porpoise was incorrect. The default value is 1.
        """
        self.CorrText.setText('0')
        num_ct = int(self.CTNumD.text())
        row_ct = VerifyCT[VerifyCT.NewCT == num_ct].index[0]
        VerifyCT.Corr[row_ct] = 0

    def put_right(self):
        """
        Inserts '1' in the appropriate row in column "Corr" in CTInfo. The default value is 1, so this function
        allows the correct themselves if they mistakenly click the put_wrong button.
        """
        self.CorrText.setText('1')
        num_ct = int(self.CTNumD.text())
        row_ct = VerifyCT[VerifyCT.NewCT == num_ct].index[0]
        VerifyCT.Corr[row_ct] = 1

    def CreateSpectrogram(self):
        """
        Opens the wav file where the click train being displayed was detected, and plots the waveform
        and the spectrogram
        """
        global CTTemp, Name
        self.WaveAxes.clear()
        self.SpectAxes.clear()

        # Prepare the signal and compute the spectrogram
        ctsig = ct_signal.CTSignal(CTTemp)
        ctsig.prepare_signal()
        ctsig.plot_spectrogram(nfft=NFFT, db=True, noverlap=Overlap)

    def FromOrdinal(self, x):
        ix = int(x)
        dt = datetime.fromordinal(ix)
        remainder = float(x) - ix
        hour, remainder = divmod(24 * remainder, 1)
        minute, remainder = divmod(60 * remainder, 1)
        second, remainder = divmod(60 * remainder, 1)
        microsecond = int(1e6 * remainder)
        if microsecond < 10:
            microsecond = 0  # compensate for rounding errors
        # for some strange reason it is 1 year over the actual date!!
        dt = datetime(dt.year - 1, dt.month, dt.day, int(hour), int(minute),
                      int(second), microsecond)
        if microsecond > 999990:  # compensate for rounding errors
            dt += timedelta(microseconds=1e6 - microsecond)

        return dt

    def click_browse_button(self):
        """
        Opens a window to select the folder where the data is
        SelectedFolder: str
                Path to folder selected by the user
        """
        root = tk.Tk()
        root.withdraw()
        self.SelectedFolder = filedialog.askdirectory()
        self.FolderPathDet.setText(self.SelectedFolder)

    def upload_data(self):
        """
        Uploads or prepares the data for validation. Displays the first click train.
        AllCTInfo: pandas dataframe
                Summary data of ll click trains identified as either high- or low-quality click trains produced
                by harbour porpoises
        AllClicks: pandas dataframe
                Parameters of all clicks belonging to the click trains in AllCTInfo
        VerifyCT: pandas dataframe
                List of click trains to verify
        """
        global CTInfo, CP, VerifyCT, SelectedFolder
        self.upload_val_data.setEnabled(False)
        self.browse_button.setEnabled(False)
        SelectedFolder = pathlib.Path(self.SelectedFolder)
        FilesInFolder = SelectedFolder.glob("*")
        # Define the names of the files
        AllClicksFileName = SelectedFolder.joinpath('AllClicks.csv')
        VerifyFileName = SelectedFolder.joinpath('VerifyCT.csv')
        AllCTInfoFileName = SelectedFolder.joinpath('AllCTInfo.csv')

        # Check if the files AllClicks, VerifyCT and AllCTInfo already exist. If they don't, generate them.
        # If they do, load them
        if AllClicksFileName in list(FilesInFolder):
            CP = pd.read_csv(AllClicksFileName)
            CTInfo = pd.read_csv(AllCTInfoFileName)
            VerifyCT = pd.read_csv(VerifyFileName)
        else:
            AllCTInfo = pd.DataFrame()
            AllClicks = pd.DataFrame()
            FilesAndFolders = SelectedFolder.glob("*")
            Folders = [s for s in FilesAndFolders if s.is_dir()]
            if len(Folders) == 0:
                Folders = [SelectedFolder]
            NewCTNum = 0
            for SubFolder in Folders:
                print('Processing subfolder', SubFolder)
                ThisCP = pd.read_csv(SelectedFolder.joinpath(SubFolder).joinpath('Clicks.csv'))
                ThisCTInfo = pd.read_csv(SelectedFolder.joinpath(SubFolder).joinpath('CTInfo.csv'))
                CTInfo = ThisCTInfo[ThisCTInfo.CTType != 'Noise']
                CTInfo.reset_index(inplace=True, drop=True)
                CTInfo['NewCT'] = 0
                if len(CTInfo) > 0:
                    Clicks = pd.DataFrame()
                    # Rename the CT (in NewCT) so numbers are not repeated!
                    # Create AllCT with all the CT in the main folder
                    # Create AllClicks with all the clicks in the main folder together
                    for i in range(0, len(CTInfo)):
                        NewCTNum = NewCTNum + 1
                        NumCT = CTInfo.CTNum[i]
                        CTInfo.NewCT.iloc[i] = NewCTNum
                        CTInfo['Corr'] = 1
                        CPTemp = ThisCP[ThisCP.CT == NumCT]
                        CPTemp.reset_index(inplace=True, drop=True)
                        CPTemp['NewCT'] = NewCTNum
                        Clicks = Clicks.append(CPTemp, ignore_index=True)
                    # Reset indexes of the dataframes
                    AllCTInfo.reset_index(inplace=True, drop=True)
                    AllClicks.reset_index(inplace=True, drop=True)
                    AllCTInfo = AllCTInfo.append(CTInfo, ignore_index=True)
                    AllClicks = AllClicks.append(Clicks, ignore_index=True)

            AllClicks.to_csv(AllClicksFileName, index=False)
            AllCTInfo.to_csv(AllCTInfoFileName, index=False)
            if self.cpod.isChecked():
                if self.start_date.toPlainText() == '':
                    start_date = None
                else:
                    start_date = self.start_date.toPlainText()
                if self.end_date.toPlainText() == '':
                    end_date = None
                else:
                    end_date = self.end_date.toPlainText()
                # If the cpod checkbox is checked then check for the CPOD.txt file
                CPODFileName = SelectedFolder.joinpath('CPOD.txt')
                validation_minutes, VerifyCT = comparison_CPOD.select_validation(AllCTInfoFileName,
                                                                                 AllClicksFileName,
                                                                                 CPODFileName,
                                                                                 start_date=start_date,
                                                                                 end_date=end_date)
                validation_minutes.to_csv(SelectedFolder.joinpath('VerifyCT_cpod.csv'))
            else:
                VerifyCT = AllCTInfo
                VerifyCT['Verified'] = 0
            VerifyCT.to_csv(VerifyFileName, index=False)
            CTInfo = AllCTInfo
            CP = AllClicks
            print('The data is ready to be validated')

        # Load the first Click Train
        row = VerifyCT[VerifyCT.Verified == 0].index[0]
        ct_num = VerifyCT.NewCT[row]
        self.update_ct(ct_num, CP, CTInfo, VerifyCT)

    def save_updates(self):
        """
        Saves the updates made to the list of click trains being verified
        """
        global VerifyCT, SelectedFolder
        num_ct = int(self.CTNumD.text())
        row_ct = VerifyCT[VerifyCT.NewCT == num_ct].index[0]
        VerifyCT.Verified[0:row_ct] = 1
        FullNameVerifyCT = SelectedFolder.joinpath('VerifyCT.csv')
        VerifyCT.to_csv(FullNameVerifyCT, index=False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
