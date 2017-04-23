import copy


class RVParameter(object):
    def __init__(self, config, key, value, label='Unlabelled', min=0, max=300, divisor=10):
        self.config = config
        self.key = key
        self.value = value
        self.label = label
        self.min = min
        self.max = max
        self.divisor = divisor

class RVParameterRatio(RVParameter):
    def __setattr__(self, name, value):
        if name == 'value':
            # Ratio change
            self.config.values['linkage_length'].value = value * self.config.values['elevator_length'].value
        super(RVParameterRatio, self).__setattr__(name, value)

class RVParameterElevator(RVParameter):
    def __setattr__(self, name, value):
        if name == 'value' and 'linkage_length' in self.config.values:
            # Maintain ratio
            self.config.values['linkage_length'].value = self.config['rod_ratio'].value * value
        super(RVParameterElevator, self).__setattr__(name, value)

class RVConfig(object):
    def __init__(self, other=None):
        '''Initialize to a default configuration'''
        self.subscriptions = {
            'changed': []
        }
        self.values = {}
        if other:
            self.values['elevator_length'] = copy.copy(other['elevator_length'])
            self.values['forearm_length'] = copy.copy(other['forearm_length'])
            self.values['linkage_length'] = copy.copy(other['linkage_length'])
            self.values['lower_actuator_length'] = copy.copy(other['lower_actuator_length'])
            self.values['upper_actuator_length'] = copy.copy(other['upper_actuator_length'])
            self.values['wrist_length'] = copy.copy(other['wrist_length'])
            self.values['elevator_weight'] = copy.copy(other['elevator_weight'])
            self.values['forearm_weight'] = copy.copy(other['forearm_weight'])
            self.values['linkage_weight'] = copy.copy(other['linkage_weight'])
            self.values['actuator_weight'] = copy.copy(other['actuator_weight'])
            self.values['elevator_torque'] = copy.copy(other['elevator_torque'])
            self.values['actuator_torque'] = copy.copy(other['actuator_torque'])
            self.values['min_load'] = copy.copy(other['min_load'])
            for key, param in self.values.items():
                param.config = self
        else:
            # General configuration
            self.values['elevator_length'] = RVParameterElevator(
                self, 'elevator_length', 148.4,
                label = 'Elevator Length',
                min=10, max=1000)
            self.values['forearm_length'] = RVParameter(
                self, 'forearm_length', 160,
                label = 'Forearm Length')
            self.values['linkage_length'] = RVParameter(
                self, 'linkage_length', 155,
                label = 'Linkage Length')
            self.values['lower_actuator_length'] = RVParameter(
                self, 'lower_actuator_length', 65,
                label = 'Lower Actuator Length')
            self.values['upper_actuator_length'] = RVParameter(
                self, 'upper_actuator_length', 54.4,
                label = 'Upper Actuator Length')
            self.values['wrist_length'] = RVParameter(
                self, 'wrist_length', 90.52,
                label = 'Wrist Length')
            self.values['elevator_weight'] = RVParameter(
                self, 'elevator_weight', 5,
                label = 'Elevator Weight')
            self.values['forearm_weight'] = RVParameter(
                self, 'forearm_weight', 5,
                label = 'Forearm Weight')
            self.values['linkage_weight'] = RVParameter(
                self, 'linkage_weight', 5,
                label = 'Linkage Weight')
            self.values['actuator_weight'] = RVParameter(
                self, 'actuator_weight', 3,
                label = 'Actuator Weight')
            self.values['elevator_torque'] = RVParameter(
                self, 'elevator_torque', 3,
                label = 'Elevator Torque',
                divisor=100)
            self.values['actuator_torque'] = RVParameter(
                self, 'actuator_torque', 3,
                label = 'Actuator Torque',
                divisor=100)
            self.values['min_load'] = RVParameter(
                self, 'min_load', 0,
                label='Minimum Load',
                divisor=100)
        ratio = self.values['linkage_length'].value / self.values['elevator_length'].value
        # Note special RVParameterRatio - not RVParameter
        self.values['rod_ratio'] = RVParameterRatio(
            self, 'rod_ratio', ratio,
            label='Rod Ratio',
            min=0.6, max=1.4,
            divisor=1000)

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, val):
        raise Exception('Config parameters must not be replaced externally')

    def subscribe(self, event, func):
        self.subscriptions[event].append(func)

    def notifyChange(self):
        self.onChanged()

    def onChanged(self):
        for func in self.subscriptions['changed']:
            func()
