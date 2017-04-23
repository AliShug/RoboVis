import numpy as np
import cv2

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import RVIK

class RVHeatmap(object):
    def __init__(self, scene, ik):
        self.graphicsItem = scene.addPixmap(QPixmap())
        self.update(ik)

    def update(self, ik):
        loads = ik.loads
        loads *= 4
        above_255 = loads >= 255
        loads = loads*(~above_255) + 255*np.ones(loads.shape)*above_255
        loads = loads.astype(np.uint8)
        loads = np.dstack([loads, loads, loads])
        loads = cv2.applyColorMap(loads, cv2.COLORMAP_WINTER)
        # cv2.imshow('colormap', loads)
        image = QImage(loads.data, loads.shape[1], loads.shape[0], loads.shape[1]*3, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(image)
        self.graphicsItem.setPixmap(pixmap)
        self.graphicsItem.resetTransform()
        self.graphicsItem.setRotation(-90)
        self.graphicsItem.setTransform(QTransform.fromScale(ik.scaling_factor, ik.scaling_factor), True)
        self.graphicsItem.setPos(0, ik.scaling_factor * ik.height/2)
