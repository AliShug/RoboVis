from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class RVOutline(object):
    def __init__(self, area):
        self.graphicsItem = None
        self.points = [
            (0,0),
            (0, area[1]),
            (area[0], area[1]),
            (area[0], 0),
            (0, 0),
        ]

    def setGraphicsItem(self, item):
        self.graphicsItem = item
        self.updateGraphics()

    def updateGraphics(self):
        if self.graphicsItem:
            poly = QPolygonF()
            for p in self.points:
                poly << QPointF(p[0], p[1])
            self.graphicsItem.setPolygon(poly)
