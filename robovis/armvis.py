import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import RVIK

class RVArmVis(object):
    '''Solves IK for and visualizes a configuration of the robot arm'''
    def __init__(self, config, scene):
        self.goal = np.array([0,0])
        self.config = config
        self.ik = RVIK(config, point=self.goal)
        self.scene = scene
        self.generateGraphics()

    def changeConfig(self, config):
        self.config = config
        self.ik.setConfig(config)

    def changeGoal(self, goal):
        self.goal = goal
        self.ik.setPoint(goal)

    def generateGraphics(self):
        res = self.ik.point_results
        if res is not None and res['ok']:
            self.scene.addLine(QPointF(0,0), QPointF(res['elbow_pos'][0], res['elbow_pos'][1]))
