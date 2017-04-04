class RVConfig(object):
    def __init__(self, other=None):
        '''Initialize to a default configuration'''
        if other:
            self.elevator_length = other.elevator_length
            self.forearm_length = other.forearm_length
            self.linkage_length = other.linkage_length
            self.lower_actuator_length = other.lower_actuator_length
            self.upper_actuator_length = other.upper_actuator_length
            self.wrist_length = other.wrist_length
        else:
            # General configuration
            self.elevator_length = 148.4
            self.forearm_length = 160
            self.linkage_length = 155
            self.lower_actuator_length = 65
            self.upper_actuator_length = 54.4
            self.wrist_length = 90.52
        self.rod_ratio = self.getRodRatio()

    def setRodRatio(self, ratio):
        self.linkage_length = ratio * self.elevator_length

    def getRodRatio(self):
        return self.linkage_length/self.elevator_length

    def setElevator(self, length):
        self.elevator_length = length
        self.linkage_length = self.rod_ratio * length
