# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'DPorCCA.ui'
# Created by: PyQt5 UI code generator 5.15.0
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import tkinter as tk
import pandas as pd
import plotly
import plotly.express as px
# import plotly.graph_objs as go
pd.options.plotting.backend = "plotly"
import numpy as np
import matplotlib.pyplot as plt
import warnings
import pyqtgraph as pg
import os
import soundfile
from scipy import signal
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtWidgets, QtGui
from datetime import datetime, timedelta
from tkinter import filedialog
# Offline mode
# from plotly.offline import init_notebook_mode, iplot
# init_notebook_mode(connected=True)


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


def SaveUpdates():
    global SelectedFolder, AllCTInfo
    FullNameCTInfo = SelectedFolder + '/AllCTInfo.csv'
    AllCTInfo.to_csv(FullNameCTInfo)


class Ui_MainWindow(object):
    def __init__(self):
        # some variables
        self.band_n = -1
        self.bands_list = {}
        # self._processed = {}
        self._reset_spectro()

        # Main Display
        self.MainDisplayTab = QtWidgets.QWidget()
        self.DisplaySettings = QtWidgets.QFrame(self.MainDisplayTab)
        self.AxesPan = QtWidgets.QFrame(self.MainDisplayTab)

        # Validate pan
        self.ActionPan = QtWidgets.QFrame(self.MainDisplayTab)
        self.ActionLabel = QtWidgets.QLabel(self.ActionPan)
        self.WaveAxes = pg.PlotWidget(self.ActionPan)
        self.SpectAxes = pg.ImageView(self.ActionPan)
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

        self.SaveupdatesButton = QtWidgets.QPushButton(self.DisplaySettings)

        self.CTPan = QtWidgets.QFrame(self.DisplaySettings)
        self.CTTypeLabel = QtWidgets.QLabel(self.CTPan)
        self.CTLabel = QtWidgets.QLabel(self.CTPan)
        self.CorrPan = QtWidgets.QFrame(self.DisplaySettings)
        self.CorrLabel = QtWidgets.QLabel(self.CorrPan)
        self.CorrText = QtWidgets.QLabel(self.CorrPan)
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
        self.DateandtimeofCTLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.DateandtimeofCTLabel.setObjectName("DateandtimeofCTLabel")
        self.DateLabel.setGeometry(QtCore.QRect(80, 20, 50, 30))
        self.DateLabel.setTextFormat(QtCore.Qt.RichText)
        self.DateLabel.setObjectName("DateLabel")
        # CT Type area
        self.CTPan.setGeometry(QtCore.QRect(220, 8, 100, 106))
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
        self.CorrPan.setGeometry(QtCore.QRect(330, 8, 90, 106))
        self.CorrPan.setFrameShape(QtWidgets.QFrame.Box)
        self.CorrPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CorrPan.setObjectName("CorrPan")
        self.CorrLabel.setGeometry(QtCore.QRect(10, 20, 70, 30))
        self.CorrLabel.setTextFormat(QtCore.Qt.RichText)
        self.CorrLabel.setObjectName("CorrLabel")
        self.CorrText.setGeometry(QtCore.QRect(20, 60, 50, 30))
        self.CorrText.setAlignment(QtCore.Qt.AlignCenter)
        self.CorrText.setObjectName("CorrText")
        # CT Info area
        self.CTInfoPan.setGeometry(QtCore.QRect(430, 8, 320, 106))
        self.CTInfoPan.setFrameShape(QtWidgets.QFrame.Box)
        self.CTInfoPan.setFrameShadow(QtWidgets.QFrame.Raised)
        self.CTInfoPan.setObjectName("CTInfoPan")
        self.CTNumLabel.setGeometry(QtCore.QRect(60, 20, 250, 30))
        self.CTNumLabel.setTextFormat(QtCore.Qt.RichText)
        self.CTNumLabel.setObjectName("CTNumLabel")
        self.CTBack.setGeometry(QtCore.QRect(30, 60, 40, 30))
        self.CTBack.setObjectName("CTBack")
        self.CTBack.clicked.connect(self.ct_back)
        self.CTNumD.setGeometry(QtCore.QRect(73, 60, 80, 30))
        self.CTNumD.setObjectName("CTNumD")
        self.CTForw.setGeometry(QtCore.QRect(156, 60, 40, 30))
        self.CTForw.setObjectName("CTForw")
        self.CTForw.clicked.connect(self.ct_forward)
        self.TotalLabel.setGeometry(QtCore.QRect(210, 60, 100, 30))
        self.TotalLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.TotalLabel.setObjectName("TotalLabel")



        # Save button
        self.SaveupdatesButton.setGeometry(QtCore.QRect(1265, 8, 95, 106))
        self.SaveupdatesButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.SaveupdatesButton.setAutoDefault(False)
        self.SaveupdatesButton.setDefault(False)
        self.SaveupdatesButton.setFlat(False)
        self.SaveupdatesButton.setObjectName("SaveupdatesButton")
        self.SaveupdatesButton.clicked.connect(SaveUpdates)
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
        # ICI radio button
        # self.InterclickintervalmsButton.setGeometry(QtCore.QRect(250, 10, 200, 20))
        # font = QtGui.QFont()
        # font.setBold(True)
        # font.setWeight(75)
        # self.InterclickintervalmsButton.setFont(font)
        # self.InterclickintervalmsButton.setObjectName("InterclickintervalmsButton")
        # FREQUENCY
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
        # Bearing radio button
        # self.DirectionofarrivalButton.setGeometry(QtCore.QRect(250, 10, 200, 20))
        # font = QtGui.QFont()
        # font.setBold(True)
        # font.setWeight(75)
        # self.DirectionofarrivalButton.setFont(font)
        # self.DirectionofarrivalButton.setObjectName("DirectionofarrivalButton")

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
        self.SelectLabel = QtWidgets.QLabel(self.DisplaySettings)
        self.SelectLabel.setGeometry(820, 8, 150, 20)
        self.SelectLabel.setText('Select a folder')
        self.FolderPathDet = QtWidgets.QLineEdit(self.DisplaySettings)
        self.FolderPathDet.setGeometry(820, 40, 320, 30)
        self.FolderPathDet.setText("C:/")
        # Browse button
        self.browse_button = QtWidgets.QPushButton(self.DisplaySettings)
        self.browse_button.setGeometry(1040, 82, 100, 30)
        self.browse_button.setText("Browse")
        self.browse_button.clicked.connect(self.click_browse_button)
        self.upload_val_data.setGeometry(QtCore.QRect(1155, 8, 100, 106))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)

        # Click train in 3D
        self.upload_val_data.setFont(font)
        self.upload_val_data.setObjectName("upload_val_data")
        self.upload_val_data.clicked.connect(self.upload_data)
        self.wrong_button.setGeometry(QtCore.QRect(760, 8, 40, 48))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        # Spectrogram area
        self.wrong_button.setFont(font)
        self.wrong_button.setObjectName("wrong_button")
        self.wrong_button.clicked.connect(self.put_wrong)

        self.right_button.setGeometry(QtCore.QRect(760, 65, 40, 48))
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
        self.TotalLabel.setText(_translate("MainWindow", "()"))
        self.CorrLabel.setText(_translate("MainWindow",
                                          "<html><head/><body><p><span style=\" "
                                          "font-weight:600\">Correct</span></p></body></html>"))
        self.SaveupdatesButton.setText(_translate("MainWindow", " Save \n"
                                                                "updates"))
        self.CTLabel.setText(_translate("MainWindow",
                                        "<html><head/><body><p><span style=\" font-weight:600\">CT "
                                        "Type</span></p></body></html>"))
        self.CTTypeLabel.setText(_translate("MainWindow", "NBHF"))
        self.CorrText.setText(_translate("MainWindow", "1"))
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
        first = CTInfo['NewCT'].iloc[0]
        if num_ct > first:
            self.AmpAxesCT.clear()
            self.ICIAxesCT.clear()
            self.FreqAxesCT.clear()
            row_ct = CTInfo[CTInfo.NewCT == num_ct].index[0]
            num_ct = CTInfo.NewCT[row_ct - 1]
            self.update_ct(num_ct, CP, CTInfo)

    def ct_forward(self):
        """
        Displays the next click train
        """
        num_ct = int(self.CTNumD.text())
        tot = CTInfo['NewCT'].iloc[-1]
        if num_ct == tot:
            print(num_ct, tot)  # do nothing
        elif num_ct < tot:
            self.AmpAxesCT.clear()
            self.ICIAxesCT.clear()
            self.FreqAxesCT.clear()
            row_ct = CTInfo[CTInfo.NewCT == num_ct].index[0]
            num_ct = CTInfo.NewCT[row_ct + 1]
            self.update_ct(num_ct, CP, CTInfo)

    def update_ct(self, num_ct, CP, CTInfo):
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
        self.fs = 1 / (CTTemp.iloc[3]['ICI'] / (1000 * (CTTemp.iloc[3]["start_sample"] - CTTemp.iloc[2]["start_sample"])))
        CTTemp = self.NewICI(CTTemp)
        CTTemp.loc[:, 'SumMs'] = int(0)
        for i in range(1, len(CTTemp)):
            CTTemp.SumMs[i] = int(CTTemp.SumMs[i - 1]) + int(CTTemp.ICI[i])
        CTTemp.SumMs = CTTemp.SumMs / 1000
        CT1HQ = CTTemp[CTTemp['pyPorCC'] == 1]
        CT1LQ = CTTemp[CTTemp['pyPorCC'] == 2]
        self.CTNumD.setText(str(num_ct))
        self.CTTypeLabel.setText(str(CTInfo.Species[CTInfo.NewCT == num_ct].values[0]))
        self.DateandtimeofCTLabel.setText(str(CTInfo.Date[CTInfo.NewCT == num_ct].values[0]))
        self.TotalLabel.setText('(' + str(CTInfo['NewCT'].iloc[-1]) + ')')
        self.CorrText.setText(str(CTInfo.Corr[CTInfo.NewCT == num_ct].values[0]))

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
        row_ct = CTInfo[CTInfo.NewCT == num_ct].index[0]
        CTInfo.Corr[row_ct] = 0

    def put_right(self):
        """
        Inserts '1' in the appropriate row in column "Corr" in CTInfo. The default value is 1, so this function
        allows the correct themselves if they mistakenly click the put_wrong button.
        """
        self.CorrText.setText('1')
        num_ct = int(self.CTNumD.text())
        row_ct = CTInfo[CTInfo.NewCT == num_ct].index[0]
        CTInfo.Corr[row_ct] = 1

    def CreateSpectrogram(self):
        """
        Opens the wav file where the click train being displayed was detected, and plots the waveform
        and the spectrogram
        """
        global CTTemp, Name
        self.WaveAxes.clear()
        self.SpectAxes.clear()
        # Find the file to open
        WavFileToOpen = CTTemp.filename[0]
        s = soundfile.SoundFile(WavFileToOpen)
        TotSamples = s.frames
        Start = CTTemp.start_sample.iloc[0] - 5760
        End = CTTemp.start_sample.iloc[-1] + 5760
        if End > TotSamples:
            End = TotSamples
        if Start < 0:
            Start = 0
        Signal, self.fs = soundfile.read(WavFileToOpen, start=int(Start), stop=int(End))
        MeanSig = sum(Signal) / len(Signal)
        Signal = Signal - MeanSig
        # Signal = Signal/max(Signal)
        sos = signal.butter(10, 50000, 'hp', fs=self.fs, output='sos')
        self.filtered_signal = signal.sosfilt(sos, Signal)
        # the signal
        Duration = len(Signal) / self.fs
        t = np.arange(0.0, Duration, 1 / self.fs)
        self.WaveAxes.plot(t, self.filtered_signal)
        NFFT = 512  # length of the windowing segments
        window = signal.get_window('hann', NFFT)
        Overlap = 128
        # _, _, Pxx = signal.spectrogram(self.filtered_signal, fs=self.fs, nfft=NFFT, window=window, scaling='density',
        #                                   noverlap=Overlap)
        self.sxx = self.spectrogram(nfft=NFFT, scaling='density', mode='Fast', db=True, force_calc=True)
        # Pxx = 10*np.log10(Pxx**2)
        self.SpectAxes.setImage(self.sxx.T, autoRange=False, scale=(100, 600))
        #
        # self.ActionPan, (self.WaveAxes, self.SpectAxes) = plt.subplots(nrows=2, sharex=True)
        # Pxx, freqs, bins, im = plt.specgram(self.filtered_signal, NFFT=NFFT, Fs=self.fs, noverlap=128, cmap='jet')
        # self.SpectAxes = plt.specgram(self.filtered_signal, NFFT=NFFT, Fs=self.fs, noverlap=128, cmap='jet')
        # #plt.show()

        # fig, (ax1, ax2) = plt.subplots(nrows=2)
        # ax1.plot(t, self.filtered_signal)
        # Pxx, freqs, bins, im = ax2.specgram(self.filtered_signal, NFFT=NFFT, Fs=self.fs, window=window, noverlap=Overlap)
        # The `specgram` method returns 4 objects. They are:
        # - Pxx: the periodogram
        # - freqs: the frequency vector
        # - bins: the centers of the time bins
        # - im: the .image.AxesImage instance representing the data in the plot
        # plt.show()

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
        AllCTrains: pandas dataframe
                Parameters of all clicks belonging to the click trains in AllCTInfo
        """
        global CTInfo, CP
        FilesInFolder = os.listdir(self.SelectedFolder)
        AllFile = [s for s in FilesInFolder if "AllCTrains.csv" in s]
        if len(AllFile) > 0:
            FileName = self.SelectedFolder + '/AllCTrains.csv'
            CP = pd.read_csv(FileName)
            CTInfoFileName = self.SelectedFolder + '/AllCTInfo.csv'
            CTInfo = pd.read_csv(CTInfoFileName)
            CTNum = CTInfo.NewCT[0]
            self.update_ct(CTNum, CP, CTInfo)
        else:
            AllCTInfo = pd.DataFrame()
            AllCTrains = pd.DataFrame()
            NewCTNum = 0
            FilesAndFolders = os.listdir(self.SelectedFolder)
            Folders = [s for s in FilesAndFolders if not "." in s]
            if len(Folders) == 0:
                AllCTrains = pd.read_csv(self.SelectedFolder + '/CTrains.csv')
                AllCTInfo = pd.read_csv(self.SelectedFolder + '/CTInfo.csv')
                AllCTInfo = AllCTInfo[AllCTInfo.Species != 'Non-NBHF']
                AllCTInfo.reset_index(inplace=True, drop=True)
                AllCTInfo['NewCT'] = AllCTInfo.CTNum
                AllCTInfo['Corr'] = 1
            else:
                for SubFolder in Folders:
                    print('Processing subfolder', SubFolder)
                    ThisCP = pd.read_csv(self.SelectedFolder + '/' + SubFolder + '/CTrains.csv')
                    ThisCTInfo = pd.read_csv(self.SelectedFolder + '/' + SubFolder + '/CTInfo.csv')
                    CTInfo = ThisCTInfo[ThisCTInfo.Species != 'Non-NBHF']
                    CTInfo.reset_index(inplace=True, drop=True)
                    CTInfo['NewCT'] = 0
                    if len(CTInfo) > 0:
                        CTrains = pd.DataFrame()
                        for i in range(0, len(CTInfo)):
                            NewCTNum = NewCTNum + 1
                            NumCT = CTInfo.CTNum[i]
                            CTInfo.NewCT[i] = NewCTNum
                            CTInfo['Corr'] = 1
                            CTTemp = ThisCP[ThisCP.CT == NumCT]
                            CTTemp.reset_index(inplace=True, drop=True)
                            CTTemp['NewCT'] = NewCTNum
                            CTrains = CTrains.append(CTTemp, ignore_index=True)
                        AllCTInfo.reset_index(inplace=True, drop=True)
                        AllCTrains.reset_index(inplace=True, drop=True)
                        AllCTInfo = AllCTInfo.append(CTInfo, ignore_index=True)
                        AllCTrains = AllCTrains.append(CTrains, ignore_index=True)

            CTFileName = self.SelectedFolder + '/AllCTrains.csv'
            AllCTrains.to_csv(CTFileName, index=False)
            CTInfoFileName = self.SelectedFolder + '/AllCTInfo.csv'
            AllCTInfo.to_csv(CTInfoFileName, index=False)

            CTInfo = AllCTInfo
            CP = AllCTrains
            num_ct = 1
            self.update_ct(num_ct, CP, CTInfo)
            print('The data is ready to be validated')

    def spectrogram(self, nfft=512, scaling='density', db=True, mode='fast', force_calc=False):
        """
        Return the spectrogram of the signal (entire file)
        Parameters
        ----------
        db : bool
            If set to True the result will be given in db, otherwise in uPa^2
        nfft : int
            Length of the fft window in samples. Power of 2.
        scaling : string
            Can be set to 'spectrum' or 'density' depending on the desired output
        mode : string
            If set to 'fast', the signal will be zero padded up to the closest power of 2
        force_calc : bool
            Set to True if the computation has to be forced
        Returns
        -------
        freq, t, sxx
        """
        if force_calc:
            self._spectrogram(nfft=nfft, scaling=scaling, mode=mode)
        if db:
            sxx = self.to_db(self.sxx, ref=1.0, square=False)
        return sxx

    def to_db(self, wave, ref=1.0, square=False):
        """
        Compute the db from the upa signal
        Parameters
        ----------
        wave : numpy array
            Signal in upa
        ref : float
            Reference pressure
        square : boolean
            Set to True if the signal has to be squared
        """
        if square:
            db = 10 * np.log10(wave ** 2 / ref ** 2)
        else:
            db = 10 * np.log10(wave / ref ** 2)
        return db

    def _spectrogram(self, nfft=512, scaling='density', mode='fast'):
        """
        Computes the spectrogram of the signal and saves it in the attributes
        Parameters
        ----------
        nfft : int
            Length of the fft window in samples. Power of 2.
        scaling : string
            Can be set to 'spectrum' or 'density' depending on the desired output
        mode : string
            If set to 'fast', the signal will be zero padded up to the closest power of 2
        Returns
        -------
        None
        """
        real_size = self.filtered_signal.size
        if self.filtered_signal.size < nfft:
            s = self._fill_or_crop(n_samples=nfft)
        else:
            if mode == 'fast':
                # Choose the closest power of 2 to clocksize for faster computing
                optim_len = int(2 ** np.ceil(np.log2(real_size)))
                # Fill the missing values with 0
                s = self._fill_or_crop(n_samples=optim_len)
            else:
                s = self.filtered_signal
        window = signal.get_window('hann', nfft)
        freq, t, sxx = signal.spectrogram(s, fs=self.fs, nfft=nfft,
                                       window=window, scaling=scaling)
#        if self.band is not None:
#            low_freq = np.argmax(freq >= self.band[0])
#        else:
        low_freq = 0
        self.freq = freq[low_freq:]
        n_bins = int(np.floor(real_size / (nfft * 7 / 8)))
        self.sxx = sxx[low_freq:, 0:n_bins]
        self.t = t[0:n_bins]

    def _fill_or_crop(self, n_samples):
        """
        Crop the signal to the number specified or fill it with 0 values in case it is too short
        Parameters
        ----------
        n_samples : int
            Number of desired samples
        """
        if self.filtered_signal.size >= n_samples:
            s = self.filtered_signal[0:n_samples]
            # self._processed[self.band_n].append('crop')
        else:
            nan_array = np.full((n_samples,), 0)
            nan_array[0:self.filtered_signal.size] = self.filtered_signal
            s = nan_array
            # self._processed[self.band_n].append('fill')
        return s

    def _reset_spectro(self):
        """
        Reset the spectrogram parameters
        """
        self.sxx = None
        self.psd = None
        self.freq = None
        self.t = None

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
