# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2018 Hewlett Packard Enterprise Development LP
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
    'Name': 'temp_sensor_monitor_normal',
    'Description': 'Network Analytics Agent Script to monitor'
                   'normal status of all temperature sensors',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        self.variables['sensors_list'] = ''

        uri1 = '/rest/v1/system/subsystems/*/*/temp_sensors/*?attributes=status'
        self.m1 = Monitor(uri1, 'Sensor Status')

        self.r1 = Rule('Sensor - Uninitialized')
        self.r1.condition('{} == "uninitialized"', [self.m1])
        self.r1.action(self.sensor_action_status_normal)

        self.r2 = Rule('Sensor - Normal')
        self.r2.condition('{} == "normal"', [self.m1])
        self.r2.action(self.sensor_action_status_normal)

        self.r3 = Rule('Sensor - Min')
        self.r3.condition('{} == "min"', [self.m1])
        self.r3.action(self.sensor_action_status_normal)

        self.r4 = Rule('Sensor - Max')
        self.r4.condition('{} == "max"', [self.m1])
        self.r4.action(self.sensor_action_status_normal)

        self.r5 = Rule('Sensor - Fault')
        self.r5.condition('{} == "fault"', [self.m1])
        self.r5.action(self.sensr_action_status_critical)

        self.r6 = Rule('Sensor - Low_Critical')
        self.r6.condition('{} == "low_critical"', [self.m1])
        self.r6.action(self.sensr_action_status_critical)

        self.r7 = Rule('Sensor - Critical')
        self.r7.condition('{} == "critical"', [self.m1])
        self.r7.action(self.sensr_action_status_critical)

        self.r8 = Rule('Sensor - Emergency')
        self.r8.condition('{} == "emergency"', [self.m1])
        self.r8.action(self.sensr_action_status_critical)

    def sensr_action_status_critical(self, event):
        self.logger.debug('LABEL = ' + event['labels'])
        label = event['labels']
        sensorname = label.split(',')[1].split('=')[1]

        self.logger.debug('Sensor Name= ' + sensorname)
        if self.variables['sensors_list'] != '':
            findsensor = self.variables['sensors_list']
            istrue = findsensor.find(sensorname)
            if istrue == -1:
                sensors_list = sensorname + self.variables['sensors_list']
                self.variables['sensors_list'] = sensors_list
                self.logger.debug('list of sensors:  ' +
                                  self.variables['sensors_list'])
                self.setactions(sensorname)

        else:
            self.variables['sensors_list'] = sensorname
            self.logger.debug('list of sensors:  ' +
                              self.variables['sensors_list'])
            self.setactions(sensorname)

    def setactions(self, sensorname):
        self.logger.debug("+++ CALLBACK: SENSOR STATUS - CRITICAL!")
        self.set_alert_level(AlertLevel.CRITICAL)
        ActionSyslog('Sensor: ' + sensorname + ' is in Critical State ')
        ActionCLI('show environment temperature')

    def sensor_action_status_normal(self, event):
        if self.get_alert_level() is not None:
            self.logger.debug("********NORMAL********")
            self.logger.debug('LABEL = ' + event['labels'])
            label = event['labels']
            sensorname = label.split(',')[1].split('=')[1]

            # delete sensorName which moved to normal state
            index = 0
            length = len(sensorname)
            findsensor = self.variables['sensors_list']
            index = findsensor.find(sensorname)
            if index != -1:
                # index = string.find(str, substr)
                findsensor = findsensor[0:index] + findsensor[index + length:]
                self.variables['sensors_list'] = findsensor
                self.logger.debug('Sensor name deleted: ' + sensorname)
                self.logger.debug('Current sensors list: ' +
                                  self.variables['sensors_list'])
                ActionSyslog('Sensor ' + sensorname + ' back to normal')
                if self.variables['sensors_list'] == '':
                    self.set_agent_status_normal()

    def set_agent_status_normal(self):
        self.remove_alert_level()
        ActionSyslog('All sensors are in Normal state')
