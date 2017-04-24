import numpy as np

from matplotlib import pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVLoadHistogram(QGraphicsView):
    '''A histogram for the maximum load across the reachable area'''
    def __init__(self, ik):
        width = 330
        height = 120
        self.scene = QGraphicsScene(0,-15,width,height-15)
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

        self.subscribers = {
        'mouseEnter' : [],
        'mouseLeave' : [],
        'mouseMove' : []
        }

        self.lines = []
        self.hist = []
        self.edges = []
        self.config = ik.config
        self.update(ik)

        self.setMouseTracking(True)

    def update(self, ik=None):
        if ik is not None:
            self.ik = ik
            self.min_load = self.config['min_load'].value

        for line in self.lines:
            self.scene.removeItem(line)
        self.lines = []

        width = self.width()
        height = self.height()

        loads = np.ma.masked_invalid(self.ik.loads*self.ik.partial_ok)
        loads = np.ma.masked_where(loads == 0, loads).compressed()
        self.hist, self.edges = np.histogram(loads, bins='auto')

        buckets = len(self.hist)
        self.screen_step = width/np.max(self.edges)
        max_count = np.max(self.hist)

        # Display histogram
        for i in range(buckets):
            x = self.edges[i] * self.screen_step
            w = max(1, (self.edges[i+1] - self.edges[i]) * self.screen_step)
            l = (self.edges[i] + self.edges[i + 1]) / 2
            count = self.hist[i]
            if l < self.min_load:
                color = QColor(100,100,100)
            else:
                color = QColor(200, 180, 100)
            # print(count)
            line = self.scene.addLine(x, 5, x, 5 + (height-5) * count/max_count, QPen(color, w))
            self.lines.append(line)
        # Setpoint shows the configuration's minimum load
        setpoint = self.config['min_load'].value * self.screen_step
        line = self.scene.addLine(setpoint, 0, setpoint, height, QPen(QColor(150, 150, 255), 2))
        self.lines.append(line)

    def setMinimumLoad(self, val):
        self.min_load = val
        self.update()

    def subscribe(self, event, function):
        self.subscribers[event].append(function)

    def enterEvent(self, event):
        for func in self.subscribers['mouseEnter']:
            func(event)

    def leaveEvent(self, event):
        self.setMinimumLoad(self.config['min_load'].value)
        for func in self.subscribers['mouseLeave']:
            func(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.click(event.pos())
        else:
            pt = self.mapToScene(event.pos())
            self.setMinimumLoad(pt.x()/self.screen_step)
        for func in self.subscribers['mouseMove']:
            func(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.click(event.pos())

    def click(self, pos):
        pt = self.mapToScene(pos)
        self.config['min_load'].value = pt.x()/self.screen_step
        self.config.notifyChange()
