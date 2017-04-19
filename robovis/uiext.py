from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QSliderF(QSlider):
    '''Fixed-point QSlider (wraps normal integer functionality)'''
    def __init__(self, *args, **kwargs):
        self.divisor = kwargs.pop('divisor', 100)
        super(QSliderF, self).__init__(*args, **kwargs)

    def setValue(self, val):
        super(QSliderF, self).setValue(int(val * self.divisor))

    def setMinimum(self, val):
        super(QSliderF, self).setMinimum(int(val * self.divisor))

    def setMaximum(self, val):
        super(QSliderF, self).setMaximum(int(val * self.divisor))

    def setPageStep(self, val):
        super(QSliderF, self).setPageStep(int(val * self.divisor))

    def setSingleStep(self, val):
        super(QSliderF, self).setSingleStep(int(val * self.divisor))

    def setSliderPosition(self, val):
        super(QSliderF, self).setSliderPosition(int(val * self.divisor))

    def setTickInterval(self, val):
        super(QSliderF, self).setTickInterval(int(val * self.divisor))

    def value(self):
        return super(QSliderF, self).value() / self.divisor

    def minimum(self):
        return super(QSliderF, self).minimum() / self.divisor

    def maximum(self):
        return super(QSliderF, self).maximum() / self.divisor

    def pageStep(self):
        return super(QSliderF, self).pageStep() / self.divisor

    def singleStep(self):
        return super(QSliderF, self).singleStep() / self.divisor

    def sliderPosition(self):
        return super(QSliderF, self).sliderPosition() / self.divisor

    def tickInterval(self):
        return super(QSliderF, self).tickInterval() / self.divisor

    def setLimits(self, min, max):
        '''New function, sets min and max in one call'''
        self.setMinimum(min)
        self.setMaximum(max)

    def wheelEvent(self, e):
        pass
