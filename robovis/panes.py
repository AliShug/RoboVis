from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import numpy as np

from robovis import *

class RVParameterBox(QGroupBox):
    def __init__(self, config, parameter, format_str='{0:.2f}', log=False, log_scaling=1):
        self.subscribers = {
            'mouseEnter': []
        }
        self.config = config
        self.parameter = config[parameter]
        self.param_key = parameter
        self.config.subscribe('changed', self.configChanged)
        self.initiated_change = False
        super(RVParameterBox, self).__init__(self.parameter.label)

        self.setMinimumHeight(50)
        self.setMinimumWidth(300)

        row = QHBoxLayout(self)

        if log:
            self.slider = QSliderLog(Qt.Horizontal, divisor=self.parameter.divisor, scaling=log_scaling)
        else:
            self.slider = QSliderF(Qt.Horizontal, divisor=self.parameter.divisor)

        self.format_str = format_str
        self.slider.setLimits(self.parameter.min, self.parameter.max)
        self.slider.setValue(self.parameter.value)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        def sliderChange():
            self.value_box.setText(self.format_str.format(self.slider.value()))
            self.parameter.value = self.slider.value()
            self.initiated_change = True
            self.config.notifyChange()
        self.slider.valueChanged.connect(sliderChange)
        row.addWidget(self.slider, 1)

        self.value_box = QLineEdit()
        self.value_box.setMaximumWidth(80)
        self.value_box.setText(self.format_str.format(self.parameter.value))
        def textChange():
            try:
                val = float(self.value_box.text())
            except:
                return
            self.slider.blockSignals(True)
            self.slider.setValue(val)
            self.slider.blockSignals(False)
            self.parameter.value = val
            self.initiated_change = True
            self.config.notifyChange()
        self.value_box.textEdited.connect(textChange)
        row.addWidget(self.value_box)

        # self.slider.blockSignals(True)
        # value_box.blockSignals(True)
        # self.slider.setValue(int(self.parameter[5]*self.parameter[6]))
        # value_box.setPlaceholderText(str(self.parameter[5]))
        # self.slider.blockSignals(False)
        # value_box.blockSignals(False)

    def configChanged(self):
        '''Update the self.slider and value box from config'''
        if not self.initiated_change:
            self.value_box.setText(self.format_str.format(self.parameter.value))
            self.slider.blockSignals(True)
            self.slider.setValue(self.parameter.value)
            self.slider.blockSignals(False)
        self.initiated_change = False

    def subscribe(self, event, func):
        self.subscribers[event].append(func)

    def enterEvent(self, event):
        for func in self.subscribers['mouseEnter']:
            func(event)


class RVParamPane(QScrollArea):
    def __init__(self, window, config):
        super(RVParamPane, self).__init__()
        self.window = window
        self.setFixedWidth(340)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.myWidget = QWidget()
        self.setWidget(self.myWidget)
        self.setWidgetResizable(True)
        layout = QBoxLayout(QBoxLayout.BottomToTop, self.myWidget)
        self.myWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        layout.addStretch(1)

        boxes = []
        boxes.append(RVParameterBox(config, 'min_load', log=True, log_scaling=0.5))
        boxes.append(RVParameterBox(config, 'actuator_torque', log=True, log_scaling = 0.5))
        boxes.append(RVParameterBox(config, 'elevator_torque', log=True, log_scaling = 0.5))
        boxes.append(RVParameterBox(config, 'rod_ratio', '{0:.3f}'))
        boxes.append(RVParameterBox(config, 'forearm_length'))
        boxes.append(RVParameterBox(config, 'elevator_length'))
        for box in boxes:
            layout.addWidget(box)
            def changeParam(e, param=box.param_key):
                window.setCurrentParam(param)
            box.subscribe('mouseEnter', changeParam)


    def onChangeElevatorLength(self):
        slider = self.sliders['elevator_length']
        value_box = self.valueboxes['elevator_length']
        adjusted_val = float(slider.value())/10
        value_box.setPlaceholderText(str(adjusted_val))
        self.window.current_config['elevator_length'] = adjusted_val
        self.window.configModified()

    def onChangeForearmLength(self):
        slider = self.sliders['forearm_length']
        value_box = self.valueboxes['forearm_length']
        adjusted_val = float(slider.value())/10
        value_box.setPlaceholderText(str(adjusted_val))
        self.window.current_config['forearm_length'] = adjusted_val
        self.window.configModified()

    def onChangeRodRatio(self):
        slider = self.sliders['rod_ratio']
        value_box = self.valueboxes['rod_ratio']
        adjusted_val = float(slider.value())/100
        value_box.setPlaceholderText(str(adjusted_val))
        self.window.current_config['rod_ratio'] = adjusted_val
        self.window.configModified()


class BarChart(QGraphicsView):
    def __init__(self):
        self.scene = QGraphicsScene()
        self.bars = []
        super(BarChart, self).__init__(self.scene)
        self.setRenderHints(QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setBackgroundBrush(QBrush(Qt.white))
        self.centerColor = Qt.black
        self.otherColor = QColor(120, 120, 255)
        self.setFixedSize(150, 140)
        self.leftMargin = 0

        contentsRect = self.contentsRect()
        rect = QRectF(0, 0, contentsRect.width(), contentsRect.height())
        self.setSceneRect(rect)
        self.centerOn(rect.center())

    def setData(self, bar_data):
        for bar in self.bars:
            bar.hide()
        if len(bar_data) < 1:
            return
        width = self.sceneRect().width() - self.leftMargin
        height = self.sceneRect().height()
        data_min = np.min(bar_data)
        data_max = np.max(bar_data)
        step = width / len(bar_data)
        middle_index = int(len(bar_data) / 2)
        norm = bar_data[middle_index]
        for i in range(len(bar_data)):
            if i >= len(self.bars):
                bar = self.scene.addRect(QRectF(), pen=QPen(Qt.NoPen), brush=QBrush(self.otherColor))
                self.bars.append(bar)
            else:
                bar = self.bars[i]
                bar.show()
            data = 0.5*height + (bar_data[i] - norm)/20 * (height - 10)
            bar.setRect(self.leftMargin + i * step, height - data, step, data)
        self.bars[middle_index].setBrush(self.centerColor)


class RVSelectionPane(QWidget):
    def __init__(self, selected_arm_vis, hover_arm_vis,
                 main_outline, extra_outlines):
        super(RVSelectionPane, self).__init__()
        self.setFixedWidth(160)

        self.selected = selected_arm_vis
        self.hover = hover_arm_vis
        self.selected.subscribe('changed', self.update)
        self.hover.subscribe('changed', self.update)
        self.outlines = [
            extra_outlines[2],
            extra_outlines[1],
            extra_outlines[0],
            extra_outlines[3],
            extra_outlines[4],
            extra_outlines[5],
        ]
        self.main_outline = main_outline

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('Load Preview'))
        self.chart = BarChart()
        layout.addWidget(self.chart)

        layout.addWidget(QLabel('Selection'))
        self.selected_label = QLabel('--')
        layout.addWidget(self.selected_label)
        layout.addWidget(QLabel('Hover'))
        self.hover_label = QLabel('--')
        layout.addWidget(self.hover_label)

        layout.addStretch(1)

    def textFor(self, arm):
        s = 'Pos: {0} mm\nLoad: {1:.2f} N'.format(arm.goal, arm.res['load'])
        return s

    def update(self):
        picked = None
        if self.hover.displayed:
            self.hover_label.setText(self.textFor(self.hover))
            picked = self.hover
        else:
            self.hover_label.setText('--')
        if self.selected.displayed:
            self.selected_label.setText(self.textFor(self.selected))
            picked = self.selected
        else:
            self.selected_label.setText('--')

        if picked == None:
            data = [0]*7
            self.chart.setData(data)
        else:
            data = []
            for outline in self.outlines:
                if outline.ik != None:
                    data.append(outline.ik.sampleLoad(picked.goal))
                else:
                    data.append(0)
            if self.main_outline.ik != None:
                data.insert(3, self.main_outline.ik.sampleLoad(picked.goal))
            else:
                data.insert(3, 0)
            self.chart.setData(data)
