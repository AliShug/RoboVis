import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class RVOutline(object):
    def __init__(self, ik):
        '''Takes an IK solution object'''
        self.graphicsItem = None
        self.contour = ik.contour
        self.width = ik.width
        self.height = ik.height
        self.ik = ik

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
                    poly << QPointF(self.contour[i, 0, 1], -self.contour[i, 0, 0] + self.height*2)
            self.graphicsItem.setPolygon(poly)
