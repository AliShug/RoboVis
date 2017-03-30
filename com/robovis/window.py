import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from com.robovis.view import RVView
from com.robovis.panes import RVParamPane
from com.robovis.outline import RVOutline
from com.robovis.config import RVConfig
from com.robovis.ik import RVIK

class RVWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)

        # leftFiller = QWidget()
        paramPane = RVParamPane(self)

        # Graphics
        self.scene = QGraphicsScene()
        self.view = RVView(self.scene)

        # Fill in layout
        # splitter.addWidget(leftFiller)
        splitter.addWidget(self.view)
        splitter.addWidget(paramPane)
        splitter.setSizes([2000,1000])

        self.setLayout(layout)

        # Fill in scene
        self.current_config = RVConfig()
        self.ik = RVIK(self.current_config)
        self.outline = RVOutline(self.ik.contour)
        item = self.view.addOutline(self.outline)

    def configModified(self):
        '''Call when the configuration has been modified - regenerates the outline(s)'''
        self.ik.calculate()
        self.outline.setContour(self.ik.contour)

    def sizeHint(self):
        return QSize(1280, 720)
