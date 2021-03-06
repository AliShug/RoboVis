from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVView(QGraphicsView):
    def __init__(self, scene):
        QGraphicsView.__init__(self, scene)
        self.scene = scene
        self.setBackgroundBrush(QBrush(Qt.black))
        self.setRenderHints(QPainter.Antialiasing)
        self.setFrameStyle(0)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scale(1, -1)
        self.initScene()
        self.subscribers = {
            'mouseEnter' : [],
            'mouseLeave' : [],
            'mouseMove' : [],
            'mousePress' : [],
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

    def mousePressEvent(self, event):
        for func in self.subscribers['mousePress']:
            func(event)
