import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class RVOutline(object):
    def __init__(self, contour):
        '''Takes a contour (numpy n*1*2 array)'''
        self.graphicsItem = None
        self.contour = contour

    def setGraphicsItem(self, item):
        self.graphicsItem = item
        self.updateGraphics()

    def setContour(self, contour):
        self.contour = contour
        self.updateGraphics()

    def updateGraphics(self):
        if self.graphicsItem:
            poly = QPolygonF()
            for i in range(self.contour.shape[0]):
                poly << QPointF(self.contour[i, 0, 1], -self.contour[i, 0, 0])
            self.graphicsItem.setPolygon(poly)
