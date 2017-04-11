class RVConfig(object):
    def __init__(self, other=None):
        '''Initialize to a default configuration'''
        self.values = {}
        if other:
            self.values['elevator_length'] = other['elevator_length']
            self.values['forearm_length'] = other['forearm_length']
            self.values['linkage_length'] = other['linkage_length']
            self.values['lower_actuator_length'] = other['lower_actuator_length']
            self.values['upper_actuator_length'] = other['upper_actuator_length']
            self.values['wrist_length'] = other['wrist_length']
        else:
            # General configuration
            self.values['elevator_length'] = 148.4
            self.values['forearm_length'] = 160
            self.values['linkage_length'] = 155
            self.values['lower_actuator_length'] = 65
            self.values['upper_actuator_length'] = 54.4
            self.values['wrist_length'] = 90.52

    def setRodRatio(self, ratio):
        self.values['linkage_length'] = ratio * self.values['elevator_length']

    def getRodRatio(self):
        return self.values['linkage_length']/self.values['elevator_length']

    def setElevator(self, length):
        ratio = self.getRodRatio()
        self.values['elevator_length'] = length
        self.values['linkage_length'] = ratio * length

    def __getitem__(self, key):
        if key == 'rod_ratio':
            return self.getRodRatio()
        else:
            return self.values[key]

    def __setitem__(self, key, val):
        if key == 'rod_ratio':
            self.setRodRatio(val)
        elif key == 'elevator_length':
            self.setElevator(val)
        else:
            self.values[key] = val
