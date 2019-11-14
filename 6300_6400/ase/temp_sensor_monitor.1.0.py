# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2019 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

Manifest = {
    'Name': 'temp_sensor_monitor',
    'Description': 'Network Analytics Agent Script to monitor'
                   ' Temperature Sensor Attributes',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'sensor_name': {
        'Name': 'Sensor Name',
        'Description': 'Temp Sensor to Monitor',
        'Type': 'string',
        'Default': 'LC1-2'
    }
}


class Agent(NAE):

    def __init__(self):
        self.variables['critical'] = '0'

        uri1 = '/rest/v1/system/subsystems/line_card/1%2F1/temp_sensors/{}?' \
            'attributes=temperature'
        self.m1 = Monitor(uri1, 'Monitoring Sensor Temperature Value',
                          [self.params['sensor_name']])

        uri2 = '/rest/v1/system/subsystems/line_card/1%2F1/temp_sensors/{}?' \
            'attributes=status'
        self.m2 = Monitor(uri2, 'Monitoring Temp Sensor Status',
                          [self.params['sensor_name']])

        self.r1 = Rule('Sensor Status:Normal/Min/Max')
        self.r1.condition('{} == "normal"', [self.m2])
        self.r1.action(self.action_status_normal)

        self.r2 = Rule('Sensor Status:Normal/Min/Max')
        self.r2.condition('{} == "min"', [self.m2])
        self.r2.action(self.action_status_normal)

        self.r3 = Rule('Sensor Status:Normal/Min/Max')
        self.r3.condition('{} == "max"', [self.m2])
        self.r3.action(self.action_status_normal)

        self.r4 = Rule('Sensor Status:Low_Critical/Critical/Fault/Emergency')
        self.r4.condition('{} == "low_critical"', [self.m2])
        self.r4.action(self.action_status_critical)

        self.r5 = Rule('Sensor Status:Low_Critical/Critical/Fault/Emergency')
        self.r5.condition('{} == "critical"', [self.m2])
        self.r5.action(self.action_status_critical)

        self.r6 = Rule('Sensor Status:Low_Critical/Critical/Fault/Emergency')
        self.r6.condition('{} == "fault"', [self.m2])
        self.r6.action(self.action_status_critical)

        self.r7 = Rule('Sensor Status:Low_Critical/Critical/Fault/Emergency')
        self.r7.condition('{} == "emergency"', [self.m2])
        self.r7.action(self.action_status_critical)

    def action_status_critical(self, event):
        if self.get_alert_level() is None:
            if self.variables['critical'] == '0':
                self.set_alert_level(AlertLevel.CRITICAL)
                ActionSyslog('Temp Sensor {} is in Critical State',
                             [self.params['sensor_name']])
                ActionCLI('show environment temperature')
                # self.logger.info("Temp Sensor: " +
                # str(#self.params['sensor_name'])+" is now in Critical state")
                self.variables['critical'] = '1'

    def action_status_normal(self, event):
        if self.get_alert_level() is not None:
            self.remove_alert_level()
            # self.logger.info('Unset the previous Critical status')
            self.variables['critical'] = '0'
