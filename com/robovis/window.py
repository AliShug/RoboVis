import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from com.robovis.view import RVView
from com.robovis.panes import RVParamPane

class RVWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)

        # leftFiller = QWidget()
        paramPane = RVParamPane()

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
        poly = QPolygonF([
            QPointF(0,0),
            QPointF(50,0),
            QPointF(50,50),
            QPointF(0,50)
        ])
        self.scene.addPolygon(poly, pen=QPen(Qt.white))

    def sizeHint(self):
        return QSize(1280, 720)
