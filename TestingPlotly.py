import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import plotly.express as px
import os
pd.options.plotting.backend = "plotly"

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.MainDisplayTab = QtWidgets.QWidget()
        self.AxesPan = QtWidgets.QFrame(self.MainDisplayTab)
        self.AxesPan.setGeometry(100, 20, 1000, 600)
        # Buttons 
        self.btn = QtWidgets.QPushButton("Test")
        self.btn1 = QtWidgets.QPushButton("Test1")

        # Container or panels for putting plots
        left_widget = QtWidgets.QWidget(self.AxesPan)
        left_widget.setGeometry(10, 30, 500, 400)
        #left_widget.setFixedWidth(500)

        # Layout that will contain my buttons
        self.layout = QtWidgets.QVBoxLayout(left_widget)
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.btn1)
        # Create a new layout to put the widget
        hlay = QtWidgets.QHBoxLayout(self)
        hlay.addWidget(left_widget)
        # hlay.addStretch()


        self.button = QtWidgets.QPushButton("Plot")
        self.browser = QtWebEngineWidgets.QWebEngineView()
        self.browser2 = QtWebEngineWidgets.QWebEngineView()

        # Container or panels for putting plots
        right_panel = QtWidgets.QWidget(self)
        right_panel.setGeometry(550, 30, 300, 400)
        #right_panel.setFixedWidth(300)

        # Layout that will contain my buttons
        self.layout = QtWidgets.QVBoxLayout(right_panel)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.browser)
        self.layout.addWidget(self.browser2)
        # Create a new layout to put the panel
        #hlay2 = QtWidgets.QHBoxLayout(self)
        hlay.addWidget(right_panel)
        # hlay2.addStretch()

#         vlayout = QtWidgets.QVBoxLayout(self)
# #        vlayout.setGeometry(self, )
#         vlayout.addWidget(self.button, alignment=QtCore.Qt.AlignHCenter)
#         vlayout.addWidget(self.browser)
#         vlayout.addWidget(self.browser2)
#         # self.browser2.setGeometry(10, 50, 600, 100)

        self.button.clicked.connect(self.show_graph)
        self.resize(1500, 800)

    def show_graph(self):
        CP = pd.read_csv('D:/JOANNA/SoundTrap/AllCTrains.csv')
        # CTInfo = pd.read_csv('D:/JOANNA/SoundTrap/AllCTInfo.csv')

        df = CP[CP.NewCT == 1]
        print(df)
        # df = px.data.tips()
        fig = px.bar(df, x="start_sample", y="amplitude", color="pyPorCC")
        a = 1
        print(a)
        # fig.update_traces(quartilemethod="exclusive")  # or "inclusive", or "linear" by default
        print(a+1)
        self.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        self.browser2.setHtml(fig.to_html(include_plotlyjs='cdn'))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = Widget()
    widget.show()
    app.exec()