import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)

        splitter = QSplitter()
        layout.addWidget(splitter)

        leftFiller = QWidget()

        # Graphics
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing)
        self.view.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.setMinimumSize(400, 300)

        # Fill in layout
        splitter.addWidget(leftFiller)
        splitter.addWidget(self.view)
        self.setLayout(layout)

    def sizeHint(self):
        return QSize(1280, 720)
