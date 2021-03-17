# import plotly.offline as po
# import plotly.graph_objs as go
#
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5 import QtCore, QtWidgets
# import sys
#
#
# def show_qt(fig):
#     raw_html = '<html><head><meta charset="utf-8" />'
#     raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
#     raw_html += '<body>'
#     raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
#     raw_html += '</body></html>'
#
#     fig_view = QWebEngineView()
#     # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
#     # for large figures.
#     fig_view.setHtml(raw_html)
#     fig_view.show()
#     fig_view.raise_()
#     return fig_view
#
#
# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#
#     fig = go.Figure(data=[{'type': 'scattergl', 'y': [2, 1, 3, 1]}])
#     fig_view = show_qt(fig)
#     sys.exit(app.exec_())
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import QApplication,QDialog,QPushButton,QVBoxLayout,QWidget

class Main(QDialog):
    def __init__(self):
        super(Main, self).__init__()
        self.ui()

    # Group Of Drage Event
    def mousePressEvent(self, event):
        self.offset = event.pos()

    def mouseMoveEvent(self, e):
        x = e.globalX()
        y = e.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x - x_w, y - y_w)

    def ui(self):
        # TitleBar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Window Size
        self.setGeometry(600, 300, 400, 500)

        # Window Background Color
        self.BackGroundColor = QPalette()
        self.BackGroundColor.setColor(QPalette.Background, QColor(255, 255, 255))
        self.setPalette(self.BackGroundColor)

        # NavBar Button
        self.btn = QPushButton("Test")
        self.btn1 = QPushButton("Test1")

        left_container = QWidget(self)
        left_container.setFixedWidth(100)
        # NavBar layout
        self.layout = QVBoxLayout(left_container)
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.btn1)

        hlay = QHBoxLayout(self)
        hlay.addWidget(left_container)
        hlay.addStretch()

        # Close img
        self.closeBtn = QPushButton(self)
        self.closeBtn.setGeometry(368, 0, 32, 32)
        self.closeBtn.setFlat(True)
        self.closeBtn.setStyleSheet("QPushButton{background-color: rgba(0,0,0,0.0)}")
        self.closeBtn.setIcon(QIcon("img/close.png"))
        self.closeBtn.setIconSize(QSize(10, 10))
        self.closeBtn.clicked.connect(QCoreApplication.instance().quit)

        # Maximize icon
        self.maxBtn = QPushButton(self)
        self.maxBtn.setGeometry(336, 0, 32, 32)
        self.maxBtn.setFlat(True)
        self.maxBtn.setStyleSheet("QPushButton{background-color: rgba(0,0,0,0.0)}")
        self.maxBtn.setIcon(QIcon("img/max.png"))
        self.maxBtn.setIconSize(QSize(14, 14))

        # Minimize Incon
        self.minBtn = QPushButton(self)
        self.minBtn.setGeometry(304, 0, 32, 32)
        self.minBtn.setFlat(True)
        self.minBtn.setStyleSheet("QPushButton{background-color: rgba(0,0,0,0.0)}")
        self.minBtn.setIcon(QIcon("img/min.png"))
        self.minBtn.setIconSize(QSize(10, 10))
