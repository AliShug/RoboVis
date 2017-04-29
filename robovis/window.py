from collections import deque
import os
from time import sleep

import numpy as np
import yaml

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import *
from robovis import RVArmVis

offset_increment = 1.08
start_param = 'elevator_length'

class RVWindow(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        self._active = True
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0,0,0,0)
        self.initMenu()

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
        self.createOutlines()
        self.heatmap = RVHeatmap(self.scene, self.ik)
        self.histogram = RVLoadHistogram(self.ik)
        self.ghost_outlines = deque()
        self.main_outline = RVOutline(
            self.scene,
            color=Qt.white,
            thickness=4)
        self.main_outline.update(self.ik)

        self.show_heatmap = True
        def toggleHeatmap():
            self.show_heatmap = not self.show_heatmap
            if self.show_heatmap:
                self.heatmap.show()
            else:
                self.heatmap.hide()
        self.show_ghosts = True
        def toggleGhosts():
            self.show_ghosts = not self.show_ghosts
            if self.show_ghosts:
                for outline in self.outlines:
                    outline.show()
            else:
                for outline in self.outlines:
                    outline.hide()

        # Arm vis
        self.arm_vis = RVArmVis(self.current_config, self.view)
        self.selected_arm_vis = RVArmVis(self.current_config,
                                         self.view,
                                         thickness=2,
                                         color=QColor(180, 180, 180),
                                         show_forces=False,
                                         show_coords=False)

        # Fill in layout
        self.selection_pane = RVSelectionPane(self.selected_arm_vis, self.arm_vis,
                                              self.main_outline, self.outlines)
        layout.addWidget(self.selection_pane)
        layout.addWidget(self.view, 1)
        splitter = QWidget()
        splitter_layout = QVBoxLayout(splitter)
        splitter_layout.setContentsMargins(0,0,0,0)
        layout.addWidget(splitter)
        heatmap_button = QPushButton('Toggle Heatmap')
        heatmap_button.clicked.connect(toggleHeatmap)
        ghosts_button = QPushButton('Toggle Ghost Outlines')
        ghosts_button.clicked.connect(toggleGhosts)
        splitter_layout.addWidget(heatmap_button)
        splitter_layout.addWidget(ghosts_button)
        splitter_layout.addWidget(paramPane)
        splitter_layout.addWidget(self.histogram)

        # Hook up the view mouse events
        self.view.subscribe('mouseMove', self.arm_vis.handleMouseMove)
        self.view.subscribe('mouseLeave', lambda e: self.arm_vis.clearGraphics())
        self.view.subscribe('mousePress', self.viewClick)

        self.current_param = start_param
        self.createIKPool()
        self.updateGhosts()
        QTimer.singleShot(0, self.asyncPoll)

    def viewClick(self, event):
        if event.button() == Qt.LeftButton:
            pt = self.view.mapToScene(event.pos())
            self.selected_arm_vis.changeGoal([pt.x(), pt.y()])

    def initMenu(self):
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit RoboVis')
        exitAction.triggered.connect(self.close)

        loadAction = QAction('&Load Config', self)
        loadAction.setShortcut('Ctrl+O')
        loadAction.setStatusTip('Load an existing configuration file')
        loadAction.triggered.connect(self.loadConfig)

        saveAction = QAction('&Save Config', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save the current configuration to a file')
        saveAction.triggered.connect(self.saveConfig)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(loadAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        self.setWindowTitle('RoboVis')

    def saveConfig(self):
        '''Saves the current configuration using a system file dialog'''
        path = QFileDialog.getSaveFileName(self, 'Save file',
                                           '',"YAML files (*.yml *.yaml)")[0]
        if path != '':
            with open(path, 'w') as file:
                data = yaml.dump(
                    self.current_config.getRaw(),
                    default_flow_style=False,
                    explicit_start=True)
                file.write(data)
                print('Saved config to {0}'.format(path))

    def loadConfig(self):
        '''Loads a configuration using a system file dialog'''
        path = QFileDialog.getOpenFileName(self, 'Open file',
                                           '', 'YAML files (*.yml *.yaml)')[0]
        if path != '':
            with open(path, 'r') as file:
                raw = yaml.load(file.read())
                self.current_config.loadRaw(raw)
                print('Loaded config from {0}'.format(path))

    def updateGhosts(self):
        p = self.current_param
        q = self.solvers[p]
        current_val = self.current_config[p].value
        modified = False
        # Identify out-of-range solvers
        cleared_low = cleared_high = 0
        for solver in q:
            if solver.data['val'] < current_val / offset_increment**4:
                cleared_low += 1
                modified = True
            elif solver.data['val'] > current_val * offset_increment**4:
                cleared_high += 1
                modified = True
        # Flip out-of-range solvers to other side
        for i in range(cleared_low):
            top = q[-1]
            solver = q.popleft()
            q.append(solver)
            # Begin solving
            new_config = RVConfig(self.current_config)
            new_val = top.data['val'] * offset_increment
            new_config[p].value = new_val
            solver.data['val'] = new_val
            solver.solveAsync(new_config)
        for i in range(cleared_high):
            bottom = q[0]
            solver = q.pop()
            q.appendleft(solver)
            # Begin solving
            new_config = RVConfig(self.current_config)
            new_val = bottom.data['val'] / offset_increment
            new_config[p].value = new_val
            solver.data['val'] = new_val
            solver.solveAsync(new_config)
        # Resolve any changes
        if modified:
            self.latchOutlines()
        # Update colors
        for outline in self.outlines:
            val = outline.solver.data['val']
            diff = val - current_val
            denom = abs(current_val*offset_increment**3 - current_val)
            max_dim = 800
            if denom > 0:
                norm_diff = abs(diff) / denom
            else:
                norm_diff = 1
            norm_diff = 1-norm_diff
            if diff < 0:
                color = QColor(50, 50, 255, norm_diff*255)
                outline.setColor(color)
            else:
                color = QColor(230, 230, 50, norm_diff*255)
                outline.setColor(color)

    def setCurrentParam(self, param):
        if param not in self.solvers.keys():
            print('Warning: param ', param, ' not currently solved for')
        else:
            self.current_param = param
            self.latchOutlines()
            self.updateGhosts()
            self.selection_pane.update()

    def configModified(self):
        '''Call when the configuration has been modified - regenerates the outline(s)'''
        # self.selected_arm_vis.update()
        self.solvers['main'][0].solveLocal(self.current_config)
        self.updateGhosts()
        self.solvePerpendicular()

    def createOutlines(self):
        self.outlines = deque()
        for i in range(6):
            self.outlines.append(RVOutline(self.scene,
                                           color=Qt.white,
                                           thickness=2.5,
                                           style=Qt.DashLine))

    def createIKPool(self):
        # 'None' yields automatic sizing (enough to use all available cores)
        self.ik_pool = RVWorkerPool(None)

        self.solvers = {}
        params = [
            'min_load',
            'actuator_torque',
            'elevator_torque',
            'rod_ratio',
            'forearm_length',
            'elevator_length',
        ]

        # Create the full set of solvers across all parameters
        for p in params:
            q = self.solvers[p] = deque()
            # 4 each of higher and lower slots
            for i in range(8):
                self.solvers[p].append(RVSolver(self.ik_pool))

        self.latchOutlines()
        self.solveParamSet(self.current_param)
        self.solvePerpendicular()

        # The main/central solver is in a section of its own
        self.solvers['main'] = [RVSolver(self.ik_pool)]
        self.solvers['main'][0].subscribe('ready', self.ikComplete)

    def solvePerpendicular(self):
        '''Starts pre-solving ghosts for the additional parameters'''
        for p, q in self.solvers.items():
            if p in ('main', self.current_param):
                continue
            else:
                self.solveParamSet(p)

    def solveParamSet(self, param):
        '''Begins solving ghost outlines for the given parameter'''
        p = param
        q = self.solvers[p]
        # Iterate through offset parameters and start solvers
        upper_val = lower_val = self.current_config[p].value
        for i in range(4):
            config_less = RVConfig(self.current_config)
            config_more = RVConfig(self.current_config)
            upper_val *= offset_increment
            lower_val /= offset_increment
            config_less[p].value = lower_val
            config_more[p].value = upper_val
            lower_solver = q[3-i]
            upper_solver = q[4+i]
            lower_solver.solveAsync(config_less)
            upper_solver.solveAsync(config_more)
            lower_solver.data['val'] = lower_val
            upper_solver.data['val'] = upper_val

    def latchOutlines(self):
        '''Latches outlines from outline pool to solvers for current param'''
        for outline in self.outlines:
            if outline.solver:
                outline.solver.removeOutline()
        p = self.current_param
        q = self.solvers[p]
        for i in range(3):
            outline_l = self.outlines[i]
            outline_r = self.outlines[3 + i]
            q[3 - i].setOutline(outline_l)
            q[4 + i].setOutline(outline_r)

    def asyncPoll(self):
        while self._active:
            sleep(0.01)
            self.ik_pool.poll()
            # See if any solvers have finished, results are automatically
            # cascaded out
            for p, set in self.solvers.items():
                for solver in set:
                    solver.poll()
            qApp.processEvents()

    def ikComplete(self, ik):
        '''Called when the main solver completes'''
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
