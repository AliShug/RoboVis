from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVView(QGraphicsView):
    def __init__(self, scene):
        QGraphicsView.__init__(self, scene)
        self.scene = scene
        self.setBackgroundBrush(QBrush(Qt.black))
        self.setRenderHints(QPainter.Antialiasing)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scale(1, -1)
        self.outlines = []
        self.initScene()

    def initScene(self):
        self.scene.addLine(-50, 0, 600, 0, pen=QPen(Qt.red))
        self.scene.addLine(0, -600, 0, 600, pen=QPen(Qt.green))

    def addOutline(self, outline):
        item = self.scene.addPolygon(QPolygonF(), pen=QPen(Qt.white))
        outline.setGraphicsItem(item)
        self.outlines.append(outline)
        return item
