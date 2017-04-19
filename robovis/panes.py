from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import *

class RVParameterBox(QGroupBox):
    def __init__(self, config, parameter):
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
        self.slider = QSliderF(Qt.Horizontal, divisor=self.parameter.divisor)
        self.format_str = '{0:.1f}'
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

        params = [
            ('Elevator Length', 1000, 6000, 'elevator_length', self.onChangeElevatorLength, config['elevator_length'], 10),
            ('Forearm Length', 1000, 6000, 'forearm_length', self.onChangeForearmLength, config['forearm_length'], 10),
            ('Rod Ratio', 33, 300, 'rod_ratio', self.onChangeRodRatio, config['rod_ratio'], 100),
            ('Elevator Torque', 0, 500, 'elevator_torque', None, 0, 10),
            ('Actuator Torque', 0, 500, 'actuator_torque', None, 0, 10),
        ]

        layout.addWidget(RVParameterBox(config, 'elevator_length'))
        layout.addWidget(RVParameterBox(config, 'forearm_length'))
        layout.addWidget(RVParameterBox(config, 'rod_ratio'))
        layout.addWidget(RVParameterBox(config, 'elevator_torque'))
        layout.addWidget(RVParameterBox(config, 'actuator_torque'))

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
