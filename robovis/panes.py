from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

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
        print('hello from ', self.param_key)
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
