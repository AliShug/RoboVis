import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import RVIK

class RVOutline(object):
    def __init__(self, ik = None, config = None, color=Qt.white, thickness=1):
        '''Takes an configuration object or completed IK object'''
        self.graphicsItem = None
        if ik:
            self.ik = ik
        elif config:
            self.ik = RVIK(config)
        else:
            raise Exception('Must provide an IK object or configuration')
        self.contour = self.ik.contour
        self.width = self.ik.width
        self.height = self.ik.height
        self.color = color
        self.thickness = thickness

    def setColor(self, color):
        self.graphicsItem.setPen(QPen(color))
        self.color = color

    def setGraphicsItem(self, item):
        self.graphicsItem = item
        self.updateGraphics()

    def setContour(self, contour):
        self.contour = contour
        self.updateGraphics()

    def updateGraphics(self):
        if self.graphicsItem:
            poly = QPolygonF()
            if self.contour is not None:
                for i in range(self.contour.shape[0]):
                    poly << QPointF(self.contour[i, 0, 1], -self.contour[i, 0, 0])
            self.graphicsItem.setPolygon(poly)
