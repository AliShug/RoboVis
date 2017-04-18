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
            elbowLine = self.scene.addLine(lineDef, QPen(Qt.white))

            lineDef = QLineF(upper_actuator, end)
            forearmLine = self.scene.addLine(lineDef, QPen(Qt.white))

            lineDef = QLineF(origin, lower_actuator)
            lowerLine = self.scene.addLine(lineDef, QPen(Qt.white))

            lineDef = QLineF(upper_actuator, lower_actuator)
            linkageLine = self.scene.addLine(lineDef, QPen(Qt.white))

            self.graphics.append(elbowLine)
            self.graphics.append(forearmLine)
            self.graphics.append(lowerLine)
            self.graphics.append(linkageLine)

            # Cordinates readout
            text = self.scene.addText('{0:.2f}, {1:.2f}'.format(end.x(), end.y()))
            text.setTransform(QTransform.fromScale(1,-1))
            text.setPos(end + QPoint(10, -5))
            text.setDefaultTextColor(Qt.white)
            self.graphics.append(text)

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
