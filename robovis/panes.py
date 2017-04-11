from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from robovis import *

class RVParamPane(QGroupBox):
    def __init__(self, window, config=RVConfig()):
        QGroupBox.__init__(self, 'Parameters')
        self.window = window
        layout = QVBoxLayout()

        params = [
            ('Elevator Length', 1000, 6000, 'elevator_length', self.onChangeElevatorLength, config['elevator_length'], 10),
            ('Forearm Length', 1000, 6000, 'forearm_length', self.onChangeForearmLength, config['forearm_length'], 10),
            ('Rod Ratio', 33, 300, 'rod_ratio', self.onChangeRodRatio, config['rod_ratio'], 100),
            ('Elevator Torque', 0, 500, 'elevator_torque', None, 0, 10),
            ('Actuator Torque', 0, 500, 'actuator_torque', None, 0, 10),
        ]

        self.sliders = {}
        self.valueboxes = {}
        for p in params:
            row = QHBoxLayout()
            layout.addLayout(row)
            label = QLabel(p[0])
            label.setMinimumWidth(100)
            row.addWidget(label)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(p[1])
            slider.setMaximum(p[2])
            # callback
            if p[4]:
                slider.valueChanged.connect(p[4])
            row.addWidget(slider)
            value_box = QLineEdit()
            value_box.setMaximumWidth(80)
            row.addWidget(value_box)
            self.sliders[p[3]] = slider
            self.valueboxes[p[3]] = value_box

            slider.blockSignals(True)
            value_box.blockSignals(True)
            slider.setValue(int(p[5]*p[6]))
            value_box.setPlaceholderText(str(p[5]))
            slider.blockSignals(False)
            value_box.blockSignals(False)
            # row.setSizeConstraint(QLayout.SetMaximumSize)

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
