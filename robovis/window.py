from collections import deque
from multiprocessing import Pool
import os
from time import sleep

import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import *
from robovis import RVArmVis

offset_increment = 1.08

def runIK(config, timestamp):
    return (RVIK(config), timestamp)

class RVWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self._active = True
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

        # Core configuration for the arm (the one that gets modified directly)
        self.current_config = RVConfig()
        self.current_config.subscribe('changed', self.configModified)


        # leftFiller = QWidget()
        paramPane = RVParamPane(self, self.current_config)

        # Graphics
        self.scene = QGraphicsScene()
        self.view = RVView(self.scene)

        # Fill in scene
        self.ik = RVIK(self.current_config)
        self.heatmap = RVHeatmap(self.scene, self.ik)
        self.histogram = RVLoadHistogram(self.ik)
        self.main_outline = RVOutline(self.scene, color=Qt.white, thickness=3, ik=self.ik)
        self.ghost_outlines = deque()
        # self.generateGhosts()

        self.show_heatmap = True
        def toggleHeatmap():
            self.show_heatmap = not self.show_heatmap
            if self.show_heatmap:
                self.heatmap.show()
            else:
                self.heatmap.hide()

        # Fill in layout
        layout.addWidget(self.view, 1)
        splitter = QWidget()
        splitter_layout = QVBoxLayout(splitter)
        splitter_layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitter)
        heatmap_button = QPushButton('Toggle Heatmap')
        heatmap_button.clicked.connect(toggleHeatmap)
        splitter_layout.addWidget(heatmap_button)
        splitter_layout.addWidget(paramPane)
        splitter_layout.addWidget(self.histogram)

        # Arm vis
        self.arm_vis = RVArmVis(self.current_config, self.view)
        self.selected_arm_vis = RVArmVis(self.current_config,
                                         self.view,
                                         thickness=2,
                                         color=QColor(180, 180, 180),
                                         show_forces=False,
                                         show_coords=False)

        # Hook up the view mouse events
        self.view.subscribe('mouseMove', self.arm_vis.handleMouseMove)
        self.view.subscribe('mouseLeave', lambda e: self.arm_vis.clearGraphics())
        self.view.subscribe('mousePress', self.viewClick)

        self.async_results = []
        self.latest_result = 0
        self.result_index = 0
        self.createIKPool()
        QTimer.singleShot(0, self.asyncPoll)

    def viewClick(self, event):
        if event.button() == Qt.LeftButton:
            pt = self.view.mapToScene(event.pos())
            self.selected_arm_vis.changeGoal([pt.x(), pt.y()])

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
            less_outline = RVOutline(self.scene, config=config_less)
            more_outline = RVOutline(self.scene, config=config_more)
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
                'outline': RVOutline(self.scene, config=new_config),
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
                'outline': RVOutline(self.scene, config=new_config),
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
        # self.selected_arm_vis.update()
        # self.updateGhosts()
        copyConfig = RVConfig(self.current_config)
        self.result_index += 1
        res = self.ik_pool.apply_async(runIK, [copyConfig, self.result_index])
        self.async_results.append(res)

    def createIKPool(self):
        # 'None' yields automatic sizing (enough to use all available cores)
        self.ik_pool = Pool(None)

    def asyncPoll(self):
        while self._active:
            sleep(0.01)
            # See if any results have finished, apply if needed
            for res in self.async_results:
                if res.ready():
                    ik, stamp = res.get()
                    if stamp > self.latest_result:
                        self.latest_result = stamp
                        self.ikComplete(ik)
                    self.async_results.remove(res)
                    break
            qApp.processEvents()

    def ikComplete(self, ik):
        self.main_outline.update(ik)
        self.heatmap.update(ik)
        self.histogram.update(ik)
        self.selected_arm_vis.update()

    def sizeHint(self):
        return QSize(1280, 720)

    def closeEvent(self, event):
        # Smash up our async workers
        self.ik_pool.terminate()
        self._active = False
