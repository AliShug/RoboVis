import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import RVIK

class RVOutline(object):
    def __init__(self, scene, ik = None, color=Qt.white, thickness=1, style=Qt.SolidLine):
        self.scene = scene
        self.contours = None
        self.color = color
        self.thickness = thickness
        self.style = style
        self.hidden = False
        # Graphics
        self.graphicsItems = []
        for i in range(6):
            self.addPolygon()
        self.solver = None
        if ik:
            self.ik = ik
            self.update(self.ik)
        else:
            self.ik = None

    def addPolygon(self):
        '''Generates a new polygon item'''
        item = self.scene.addPolygon(QPolygonF(), pen=QPen(
            QBrush(self.color),
            self.thickness,
            self.style))
        self.graphicsItems.append(item)
        if self.hidden:
            item.hide()

    def removePolygon(self):
        '''Removes the last polygon item'''
        self.scene.removeItem(self.graphicsItems.pop())

    def setColor(self, color):
        for item in self.graphicsItems:
            pen = item.pen()
            pen.setColor(color)
            item.setPen(pen)
        self.color = color

    def update(self, ik):
        self.ik = ik
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
                elif not self.hidden:
                    self.graphicsItems[c].show()
                self.graphicsItems[c].setPolygon(poly)
                c += 1
            # Cleanup unused polygon items
            for i in range(c, len(self.graphicsItems)):
                self.graphicsItems[i].hide()

    def hide(self):
        self.hidden = True
        for item in self.graphicsItems:
            item.hide()

    def show(self):
        self.hidden = False
        self.updateGraphics()
