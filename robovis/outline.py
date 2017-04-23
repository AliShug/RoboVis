import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import RVIK

class RVOutline(object):
    def __init__(self, scene, ik = None, config = None, color=Qt.white, thickness=1):
        '''Takes an configuration object or completed IK object'''
        self.scene = scene
        if ik:
            self.ik = ik
        elif config:
            self.ik = RVIK(config)
        else:
            raise Exception('Must provide an IK object or configuration')
        self.contours = self.ik.contours
        self.color = color
        self.thickness = thickness
        # Graphics
        self.graphicsItems = []
        self.addPolygon()
        self.update(self.ik)

    def addPolygon(self):
        '''Generates a new polygon item'''
        item = self.scene.addPolygon(QPolygonF(), pen=QPen(QBrush(self.color), self.thickness))
        self.graphicsItems.append(item)

    def removePolygon(self):
        '''Removes the last polygon item'''
        self.scene.removeItem(self.graphicsItems.pop())

    def setColor(self, color):
        for item in self.graphicsItems:
            item.setPen(QPen(color))
        self.color = color

    def update(self, ik):
        self.contours = ik.contours
        self.updateGraphics()

    def updateGraphics(self):
        if self.contours is not None:
            c = 0
            for contour in self.contours:
                poly = QPolygonF()
                # Convert contour coordinates to polygon
                for i in range(contour.shape[0]):
                    poly << QPointF(contour[i, 0, 1], -contour[i, 0, 0])
                # Add a new polygon if we've run out
                if c == len(self.graphicsItems):
                    self.addPolygon()
                else:
                    self.graphicsItems[c].show()
                self.graphicsItems[c].setPolygon(poly)
                c += 1
            # Cleanup unused polygon items
            for i in range(c, len(self.graphicsItems)):
                self.graphicsItems[i].hide()
