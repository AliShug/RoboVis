import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QSliderF(QSlider):
    '''Fixed-point QSlider (wraps normal integer functionality)'''
    def __init__(self, *args, **kwargs):
        self.divisor = kwargs.pop('divisor', 100)
        super(QSliderF, self).__init__(*args, **kwargs)

    def convertFrom(self, val):
        return val / self.divisor

    def convertTo(self, val):
        return val * self.divisor

    def setValue(self, val):
        super(QSliderF, self).setValue(int(self.convertTo(val)))

    def setMinimum(self, val):
        super(QSliderF, self).setMinimum(int(self.convertTo(val)))

    def setMaximum(self, val):
        super(QSliderF, self).setMaximum(int(self.convertTo(val)))

    def setPageStep(self, val):
        super(QSliderF, self).setPageStep(int(self.convertTo(val)))

    def setSingleStep(self, val):
        super(QSliderF, self).setSingleStep(int(self.convertTo(val)))

    def setSliderPosition(self, val):
        super(QSliderF, self).setSliderPosition(int(self.convertTo(val)))

    def setTickInterval(self, val):
        super(QSliderF, self).setTickInterval(int(self.convertTo(val)))

    def value(self):
        return self.convertFrom(super(QSliderF, self).value())

    def minimum(self):
        return self.convertFrom(super(QSliderF, self).minimum())

    def maximum(self):
        return self.convertFrom(super(QSliderF, self).maximum())

    def pageStep(self):
        return self.convertFrom(super(QSliderF, self).pageStep())

    def singleStep(self):
        return self.convertFrom(super(QSliderF, self).singleStep())

    def sliderPosition(self):
        return self.convertFrom(super(QSliderF, self).sliderPosition())

    def tickInterval(self):
        return self.convertFrom(super(QSliderF, self).tickInterval())

    def setLimits(self, min, max):
        '''New function, sets min and max in one call'''
        self.setMinimum(min)
        self.setMaximum(max)

    def wheelEvent(self, e):
        pass

class QSliderLog(QSliderF):
    def __init__(self, *args, **kwargs):
        self.scaling = kwargs.pop('scaling', 1)
        super(QSliderLog, self).__init__(*args, **kwargs)

    def convertTo(self, val):
        return np.log(val*self.scaling + 1) * self.divisor

    def convertFrom(self, val):
        return (np.exp(val / self.divisor) - 1) / self.scaling
