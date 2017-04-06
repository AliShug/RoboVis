import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import *
from robovis import RVArmVis

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
        self.main_outline = RVOutline(self.ik, Qt.white, 3)
        item = self.view.addOutline(self.main_outline)
        self.ghost_outlines = []
        # 6 ghost outlines
        for i in range(3):
            config_less = RVConfig(self.current_config)
            config_more = RVConfig(self.current_config)
            config_less.setElevator(config_less.elevator_length - (i+1) * 10)
            config_more.setElevator(config_more.elevator_length + (i+1) * 10)
            less_outline = RVOutline(RVIK(config_less), Qt.yellow)
            more_outline = RVOutline(RVIK(config_more), Qt.blue)
            self.view.addOutline(less_outline)
            self.view.addOutline(more_outline)
            self.ghost_outlines.append(less_outline)
            self.ghost_outlines.append(more_outline)

        # Arm vis
        self.arm_vis = RVArmVis(self.current_config, self.scene)

    def configModified(self):
        '''Call when the configuration has been modified - regenerates the outline(s)'''
        self.ik.calculate()
        self.main_outline.setContour(self.ik.contour)
        # for outline in self.ghost_outlines:
        #     outline.

    def sizeHint(self):
        return QSize(1280, 720)
