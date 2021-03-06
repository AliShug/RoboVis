import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import RVIK

class RVArmVis(object):
    '''Solves IK for and visualizes a configuration of the robot arm'''
    def __init__(self, config, view, **kwargs):
        self.displayed = False
        self.goal = np.array([0,0])
        self.res = None
        self.config = config
        self.ik = RVIK(config, point=self.goal)
        self.view = view
        # Options
        self.color = kwargs.pop('color', QColor(100, 100, 100))
        self.thickness = kwargs.pop('thickness', 5)
        self.show_forces = kwargs.pop('show_forces', True)
        self.show_coords = kwargs.pop('show_coords', True)

        self.subscribers = {
            'changed': []
        }

        self.scene = view.scene
        self.graphics = []
        self.update()

    def changeConfig(self, config):
        self.config = config
        self.ik.setConfig(config)
        self.update()

    def changeGoal(self, goal):
        self.goal = goal
        self.ik.setPoint(goal)
        self.update()

    def clearGraphics(self):
        for item in self.graphics:
            self.scene.removeItem(item)
        self.graphics = []

    def update(self):
        self.clearGraphics()
        self.ik.calculate()
        res = self.ik.point_results
        if res is not None and res['ok']:
            self.res = res
            self.displayed = True
            origin = QPointF(0,0)
            elbow = QPointF(res['elbow_pos'][0], res['elbow_pos'][1])
            upper_actuator = QPointF(res['upper_actuator'][0], res['upper_actuator'][1])
            end = QPointF(res['goal_pos'][0], res['goal_pos'][1])
            lower_actuator = QPointF(res['lower_actuator'][0], res['lower_actuator'][1])

            pen = QPen(self.color, self.thickness)

            lineDef = QLineF(origin, elbow)
            elbow_line = self.scene.addLine(lineDef, pen)

            lineDef = QLineF(upper_actuator, end)
            forearm_line = self.scene.addLine(lineDef, pen)

            lineDef = QLineF(origin, lower_actuator)
            lower_line = self.scene.addLine(lineDef, pen)

            lineDef = QLineF(upper_actuator, lower_actuator)
            linkage_line = self.scene.addLine(lineDef, pen)

            self.graphics.append(elbow_line)
            self.graphics.append(forearm_line)
            self.graphics.append(lower_line)
            self.graphics.append(linkage_line)

            if self.show_forces:
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

            if self.show_coords:
                rect = QRectF(end + QPointF(10, -5), end + QPointF(120, -40))
                box = self.scene.addRect(rect, brush=QBrush(Qt.black))
                box.setOpacity(0.5)
                self.graphics.append(box)
                text = self.scene.addText('{0:.2f}, {1:.2f} mm'.format(end.x(), end.y()))
                text.setTransform(QTransform.fromScale(1,-1))
                text.setPos(end + QPoint(10, -5))
                text.setDefaultTextColor(Qt.white)
                self.graphics.append(text)
                text = self.scene.addText('{0:.2f} N'.format(res['load']))
                text.setTransform(QTransform.fromScale(1,-1))
                text.setPos(end + QPoint(10, -20))
                text.setDefaultTextColor(Qt.white)
                self.graphics.append(text)
        else:
            self.displayed = False
            self.res = None
        self.onChanged()

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

    def subscribe(self, event, func):
        self.subscribers[event].append(func)

    def onChanged(self):
        for func in self.subscribers['changed']:
            func()
