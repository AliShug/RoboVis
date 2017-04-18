import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import RVIK

class RVArmVis(object):
    '''Solves IK for and visualizes a configuration of the robot arm'''
    def __init__(self, config, view):
        self.goal = np.array([0,0])
        self.config = config
        self.ik = RVIK(config, point=self.goal)
        self.view = view
        self.scene = view.scene
        self.graphics = []
        self.generateGraphics()

    def changeConfig(self, config):
        self.config = config
        self.ik.setConfig(config)
        self.generateGraphics()

    def changeGoal(self, goal):
        self.goal = goal
        self.ik.setPoint(goal)
        self.generateGraphics()

    def clearGraphics(self):
        for item in self.graphics:
            self.scene.removeItem(item)
        self.graphics = []

    def generateGraphics(self):
        self.clearGraphics()
        res = self.ik.point_results
        if res is not None and res['ok']:
            origin = QPointF(0,0)
            elbow = QPointF(res['elbow_pos'][0], res['elbow_pos'][1])
            upper_actuator = QPointF(res['upper_actuator'][0], res['upper_actuator'][1])
            end = QPointF(res['goal_pos'][0], res['goal_pos'][1])
            lower_actuator = QPointF(res['lower_actuator'][0], res['lower_actuator'][1])

            lineDef = QLineF(origin, elbow)
            elbow_line = self.scene.addLine(lineDef, QPen(Qt.white))

            lineDef = QLineF(upper_actuator, end)
            forearm_line = self.scene.addLine(lineDef, QPen(Qt.white))

            lineDef = QLineF(origin, lower_actuator)
            lower_line = self.scene.addLine(lineDef, QPen(Qt.white))

            lineDef = QLineF(upper_actuator, lower_actuator)
            linkage_line = self.scene.addLine(lineDef, QPen(Qt.white))

            self.graphics.append(elbow_line)
            self.graphics.append(forearm_line)
            self.graphics.append(lower_line)
            self.graphics.append(linkage_line)

            # Cordinates readout
            text = self.scene.addText('{0:.2f}, {1:.2f}'.format(end.x(), end.y()))
            text.setTransform(QTransform.fromScale(1,-1))
            text.setPos(end + QPoint(10, -5))
            text.setDefaultTextColor(Qt.white)
            self.graphics.append(text)

            # Forces
            P = QPointF(res['P'][0], res['P'][1])
            lineDef = QLineF(upper_actuator, upper_actuator + P)
            force_P_line = self.scene.addLine(lineDef, QPen(QBrush(Qt.blue), 2))
            self.graphics.append(force_P_line)
            F = QPointF(res['F'][0], res['F'][1])
            lineDef = QLineF(elbow, elbow + F)
            force_F_line = self.scene.addLine(lineDef, QPen(QBrush(Qt.blue), 2))
            self.graphics.append(force_F_line)
            L = QPointF(res['L'][0], res['L'][1])
            lineDef = QLineF(end, end + L)
            force_L_line = self.scene.addLine(lineDef, QPen(QBrush(Qt.yellow), 2))
            self.graphics.append(force_L_line)

    # def show(self):
    #     for item in self.graphics:
    #         item.show()
    #
    # def hide(self):
    #     for item in self.graphics:
    #         item.hide()

    def handleMouseMove(self, event):
        realPoint = self.view.mapToScene(event.pos())
        self.changeGoal([realPoint.x(), realPoint.y()])
