from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import *

class RVParameterBox(QGroupBox):
    def __init__(self, config, parameter, format_str='{0:.2f}', log=False, log_scaling=1):
        super(RVParameterBox, self).__init__()
        self.config = config
        self.parameter = config[parameter]
        self.param_key = parameter
        self.config.subscribe('changed', self.configChanged)
        self.initiated_change = False

        row = QHBoxLayout(self)
        label = QLabel(self.parameter.label)
        label.setMinimumWidth(100)
        row.addWidget(label)
        if log:
            self.slider = QSliderLog(Qt.Horizontal, divisor=self.parameter.divisor, scaling=log_scaling)
        else:
            self.slider = QSliderF(Qt.Horizontal, divisor=self.parameter.divisor)

        self.format_str = format_str
        self.slider.setLimits(self.parameter.min, self.parameter.max)
        self.slider.setValue(self.parameter.value)

        def sliderChange():
            self.value_box.setText(self.format_str.format(self.slider.value()))
            self.parameter.value = self.slider.value()
            self.initiated_change = True
            self.config.notifyChange()
        self.slider.valueChanged.connect(sliderChange)
        row.addWidget(self.slider)

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

class RVParamPane(QGroupBox):
    def __init__(self, window, config):
        super(RVParamPane, self).__init__('Parameters')
        self.window = window
        layout = QVBoxLayout()

        layout.addWidget(RVParameterBox(config, 'elevator_length'))
        layout.addWidget(RVParameterBox(config, 'forearm_length'))
        layout.addWidget(RVParameterBox(config, 'rod_ratio', '{0:.3f}'))
        layout.addWidget(RVParameterBox(config, 'elevator_torque', log=True, log_scaling = 0.5))
        layout.addWidget(RVParameterBox(config, 'actuator_torque', log=True, log_scaling = 0.5))
        layout.addWidget(RVParameterBox(config, 'min_load', log=True, log_scaling=0.5))

        self.setLayout(layout)
        layout.addStretch(5)

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
