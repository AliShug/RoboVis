from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVLoadHistogram(QGraphicsView):
    def __init__(self):
        self.scene = QGraphicsScene(0,0,100,60)
        super(RVLoadHistogram, self).__init__(self.scene)
        self.setBackgroundBrush(QBrush(Qt.white))
        self.setRenderHints(QPainter.Antialiasing)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(100, 60)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.scale(1, -1)
        self.initScene()
        self.subscribers = {
            'mouseEnter' : [],
            'mouseLeave' : [],
            'mouseMove' : []
        }
        self.setMouseTracking(True)

    def initScene(self):
        self.scene.addLine(-50, 0, 600, 0, pen=QPen(Qt.red))
        self.scene.addLine(0, -600, 0, 600, pen=QPen(Qt.green))

    def subscribe(self, event, function):
        self.subscribers[event].append(function)

    def enterEvent(self, event):
        for func in self.subscribers['mouseEnter']:
            func(event)

    def leaveEvent(self, event):
        for func in self.subscribers['mouseLeave']:
            func(event)

    def mouseMoveEvent(self, event):
        for func in self.subscribers['mouseMove']:
            func(event)
