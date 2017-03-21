from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RVParamPane(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self, 'Parameters')
        layout = QVBoxLayout()

        params = [
            ('Elevator Length', 20, 800),
            ('Forearm Length', 20, 800),
            ('Rod Ratio', 3, 150),
            ('Elevator Torque', 0, 500),
            ('Actuator Torque', 0, 500),
        ]

        for p in params:
            row = QHBoxLayout()
            layout.addLayout(row)
            label = QLabel(p[0])
            label.setMinimumWidth(100)
            row.addWidget(label)
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(p[1])
            slider.setMaximum(p[2])
            row.addWidget(slider)
            valueBox = QLineEdit()
            valueBox.setMaximumWidth(80)
            row.addWidget(valueBox)
            # row.setSizeConstraint(QLayout.SetMaximumSize)

        self.setLayout(layout)
        layout.addStretch(5)
