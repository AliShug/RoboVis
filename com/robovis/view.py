from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVView(QGraphicsView):
    def __init__(self, scene):
        QGraphicsView.__init__(self, scene)
        self.setBackgroundBrush(QBrush(Qt.black))
        self.setRenderHints(QPainter.Antialiasing)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scale(1, -1)
