import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVLoadHistogram(QGraphicsView):
    '''A histogram for the maximum load across the reachable area'''
    def __init__(self, ik):
        width = 330
        height = 120
        self.scene = QGraphicsScene(0,0,width,height)
        super(RVLoadHistogram, self).__init__(self.scene)
        self.setBackgroundBrush(QBrush(Qt.white))
        self.setRenderHints(QPainter.Antialiasing)
        self.setFrameStyle(0)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(width, height)
        self.setSceneRect(0, 0, width, height)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scale(1, -1)
        self.lines = []
        self.update(ik)
        self.subscribers = {
            'mouseEnter' : [],
            'mouseLeave' : [],
            'mouseMove' : []
        }
        self.setMouseTracking(True)

    def update(self, ik):
        for line in self.lines:
            self.scene.removeItem(line)
        self.lines = []
        # masked_loads = np.ma.masked_invalid(ik.loads)
        # masked_loads = masked_loads[masked_loads < np.ma.median(masked_loads)+np.ma.std(masked_loads)]
        # hist, edges = np.histogram(masked_loads.compressed(), bins=330)
        width = self.width()
        height = self.height()
        hist, edges = np.histogram(ik.loads, bins=300, range=(0.01, 500))
        loads = ik.loads*ik.reachable
        hist_reachable, edges = np.histogram(loads, bins=300, range=(0.01, 500))
        buckets = len(hist)
        step = width/buckets
        x = 0
        max_count = np.max(hist)
        for count in hist_reachable:
            line = self.scene.addLine(x, 5, x, 5 + (height-5) * count/max_count, QPen(QColor(200, 180, 100), 2))
            self.lines.append(line)
            x += step

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
