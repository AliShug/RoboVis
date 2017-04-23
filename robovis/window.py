from collections import deque

import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import *
from robovis import RVArmVis

offset_increment = 1.08

class RVWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)

        # Core configuration for the arm (the one that gets modified directly)
        self.current_config = RVConfig()
        self.current_config.subscribe('changed', self.configModified)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)

        # leftFiller = QWidget()
        paramPane = RVParamPane(self, self.current_config)

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
        self.ik = RVIK(self.current_config)
        self.heatmap = RVHeatmap(self.scene, self.ik)
        self.main_outline = RVOutline(color=Qt.white, thickness=3, ik=self.ik)
        item = self.view.addOutline(self.main_outline)
        self.ghost_outlines = deque()
        # self.generateGhosts()

        # Arm vis
        self.arm_vis = RVArmVis(self.current_config, self.view)

        # Hook up the view mouse events
        self.view.subscribe('mouseMove', self.arm_vis.handleMouseMove)
        self.view.subscribe('mouseLeave', lambda e: self.arm_vis.clearGraphics())

    def generateGhosts(self):
        param = 'elevator_length'
        for ghost_info in self.ghost_outlines:
            self.scene.removeItem(ghost_info['outline'].graphicsItem)
        self.ghost_outlines = deque()
        # Iterate through offset parameters
        upper_val = lower_val = self.current_config[param].value
        # 3 each of higher and lower outlines
        for i in range(3):
            config_less = RVConfig(self.current_config)
            config_more = RVConfig(self.current_config)
            upper_val *= offset_increment
            lower_val /= offset_increment
            config_less['elevator_length'].value = lower_val
            config_more['elevator_length'].value = upper_val
            less_outline = RVOutline(config=config_less)
            more_outline = RVOutline(config=config_more)
            self.view.addOutline(less_outline)
            self.view.addOutline(more_outline)
            less_info = {
                'outline': less_outline,
                'val': lower_val,
            }
            more_info = {
                'outline': more_outline,
                'val': upper_val,
            }
            self.ghost_outlines.appendleft(less_info)
            self.ghost_outlines.append(more_info)
        self.updateGhosts()

    def updateGhosts(self):
        param = 'elevator_length'
        current_val = self.current_config[param].value
        # Identify out-of-range outlines
        cleared_low = cleared_high = 0
        for ghost_info in self.ghost_outlines:
            if ghost_info['val'] < current_val / offset_increment**3:
                cleared_low += 1
            elif ghost_info['val'] > current_val * offset_increment**3:
                cleared_high += 1
        # Clear and replace the out-of-range outlines
        for i in range(cleared_low):
            ghost_info = self.ghost_outlines.popleft()
            self.scene.removeItem(ghost_info['outline'].graphicsItem)
            # Create new high ghost
            new_val = self.ghost_outlines[-1]['val'] * offset_increment
            new_config = RVConfig(self.current_config)
            new_config[param].value = new_val
            new_info = {
                'outline': RVOutline(config=new_config),
                'val': new_val,
            }
            self.ghost_outlines.append(new_info)
            self.view.addOutline(new_info['outline'])
        for i in range(cleared_high):
            ghost_info = self.ghost_outlines.pop()
            self.scene.removeItem(ghost_info['outline'].graphicsItem)
            # Create new low ghost
            new_val = self.ghost_outlines[0]['val'] / offset_increment
            new_config = RVConfig(self.current_config)
            new_config[param].value = new_val
            new_info = {
                'outline': RVOutline(config=new_config),
                'val': new_val,
            }
            self.ghost_outlines.appendleft(new_info)
            self.view.addOutline(new_info['outline'])
        # Update the outline colors
        for ghost_info in self.ghost_outlines:
            outline = ghost_info['outline']
            val = ghost_info['val']
            diff = val - current_val
            norm_diff = abs(diff) / abs(current_val*offset_increment**3 - current_val)
            max_dim = 800
            norm_diff = max(norm_diff, 100/max_dim)
            if diff < 0:
                color = QColor(50, 50, 255).darker(norm_diff*max_dim)
                outline.setColor(color)
            else:
                color = QColor(230, 230, 50).darker(norm_diff*max_dim)
                outline.setColor(color)



    def configModified(self):
        '''Call when the configuration has been modified - regenerates the outline(s)'''
        self.ik.calculate()
        self.main_outline.setContour(self.ik.contour)
        # self.updateGhosts()
        self.heatmap.update(self.ik)

    def sizeHint(self):
        return QSize(1280, 720)
