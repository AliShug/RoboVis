import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)

        topFiller = QWidget()
        topFiller.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        infoLabel = QLabel("<i>There's some text here</i>")
        infoLabel.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        infoLabel.setAlignment(Qt.AlignCenter)
        bottomFiller = QWidget()
        bottomFiller.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(topFiller)
        layout.addWidget(infoLabel)
        layout.addWidget(bottomFiller)

        self.setLayout(layout)
