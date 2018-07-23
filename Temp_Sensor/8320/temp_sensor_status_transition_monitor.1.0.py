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
    'Name': 'temp_sensor_status_transition_monitor',
    'Description': 'Network Analytics Agent Script to monitor'
                   'status transitions of all temperature sensors',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):

        self.variables['sensors_list'] = ''

        uri1 = '/rest/v1/system/subsystems/*/*/temp_sensors/*?' \
            'attributes=status'
        self.m1 = Monitor(uri1, 'Sensor Status')

        # MONITOR NORMAL STATE TRANSITIONS

        # Normal -> Min
        self.r1 = Rule('Sensor Status - Normal -> Min')
        self.r1.condition(
            'transition {} from "normal" to "min"', [self.m1])
        self.r1.action(self.sensor_status_action_normal)

        # Normal -> Max
        self.r2 = Rule('Sensor Status - Normal -> Max')
        self.r2.condition(
            'transition {} from "normal" to "max"', [self.m1])
        self.r2.action(self.sensor_status_action_normal)

        # Low Critical -> Min
        self.r3 = Rule('Sensor Status - Low Critical -> Min')
        self.r3.condition(
            'transition {} from "low_critical" to "min"', [self.m1])
        self.r3.action(self.sensor_status_action_normal)

        # Critical -> Max
        self.r4 = Rule('Sensor Status - Critical -> Max')
        self.r4.condition(
            'transition {} from "critical" to "max"', [self.m1])
        self.r4.action(self.sensor_status_action_normal)

        # Fault -> Uninitialized
        self.r5 = Rule('Sensor Status - Fault -> Uninitialized')
        self.r5.condition(
            'transition {} from "fault" to "uninitialized"', [self.m1])
        self.r5.action(self.sensor_status_action_normal)

        # Fault -> Normal
        self.r6 = Rule('Sensor Status - Fault -> Normal')
        self.r6.condition(
            'transition {} from "fault" to "normal"', [self.m1])
        self.r6.action(self.sensor_status_action_normal)

        # Fault -> Min
        self.r7 = Rule('Sensor Status - Fault -> Min')
        self.r7.condition(
            'transition {} from "fault" to "min"', [self.m1])
        self.r7.action(self.sensor_status_action_normal)

        # Fault -> Max
        self.r8 = Rule('Sensor Status - Fault -> Max')
        self.r8.condition(
            'transition {} from "fault" to "max"', [self.m1])
        self.r8.action(self.sensor_status_action_normal)

        # MONITOR CRITICAL STATE TRANSITIONS

        # Min -> Low Critical
        self.r9 = Rule('Sensor Status - Min -> Low Critical')
        self.r9.condition(
            'transition {} from "min" to "low_critical"', [self.m1])
        self.r9.action(self.sensor_status_action_critical)

        # Max -> Critical
        self.r10 = Rule('Sensor Status - Max -> Critical')
        self.r10.condition(
            'transition {} from "max" to "critical"', [self.m1])
        self.r10.action(self.sensor_status_action_critical)

        # Critical -> Emergency
        self.r11 = Rule(
            'Sensor Status - Critical -> Emergency')
        self.r11.condition(
            'transition {} from "critical" to "emergency"',
            [self.m1])
        self.r11.action(self.sensor_status_action_critical)

        # Emergency -> Critical
        self.r12 = Rule('Sensor Status - Emergency -> Critical')
        self.r12.condition(
            'transition {} from "emergency" to "critical"', [self.m1])
        self.r12.action(self.sensor_status_action_critical)

        # Uninitialized -> Fault
        self.r13 = Rule('Sensor Status - Uninitialized -> Fault')
        self.r13.condition(
            'transition {} from "uninitialized" to "fault"', [self.m1])
        self.r13.action(self.sensor_status_action_critical)

        # Normal -> Fault
        self.r14 = Rule('Sensor Status - Normal -> Fault')
        self.r14.condition(
            'transition {} from "normal" to "fault"', [self.m1])
        self.r14.action(self.sensor_status_action_critical)

        # Min -> Fault
        self.r15 = Rule('Sensor Status - Min -> Fault')
        self.r15.condition(
            'transition {} from "min" to "fault"', [self.m1])
        self.r15.action(self.sensor_status_action_critical)

        # Low Critical -> Fault
        self.r16 = Rule('Sensor Status - Low Critical -> Fault')
        self.r16.condition(
            'transition {} from "low_critical" to "fault"', [self.m1])
        self.r16.action(self.sensor_status_action_critical)

        # Max -> Fault
        self.r17 = Rule('Sensor Status - Max -> Fault')
        self.r17.condition(
            'transition {} from "max" to "fault"', [self.m1])
        self.r17.action(self.sensor_status_action_critical)

        # Critical -> Fault
        self.r18 = Rule('Sensor Status - Critical -> Fault')
        self.r18.condition(
            'transition {} from "critical" to "fault"', [self.m1])
        self.r18.action(self.sensor_status_action_critical)

        # Emergency -> Fault
        self.r19 = Rule('Sensor Status - Emergency -> Fault')
        self.r19.condition(
            'transition {} from "emergency" to "fault"', [self.m1])
        self.r19.action(self.sensor_status_action_critical)

        # Fault -> Emergency
        self.r20 = Rule('Sensor Status - Fault -> Emergency')
        self.r20.condition(
            'transition {} from "fault" to "emergency"', [self.m1])
        self.r20.action(self.sensor_status_action_critical)

        # Fault -> Critical
        self.r21 = Rule('Sensor Status - Fault -> Critical')
        self.r21.condition(
            'transition {} from "fault" to "critical"', [self.m1])
        self.r21.action(self.sensor_status_action_critical)

        # Fault -> Low Critical
        self.r22 = Rule('Sensor Status - Fault -> Low Critical')
        self.r22.condition(
            'transition {} from "fault" to "low_critical"', [self.m1])
        self.r22.action(self.sensor_status_action_critical)

    def sensor_status_action_critical(self, event):
        self.logger.debug('********CRITICAL********')
        self.logger.debug('LABEL = ' + event['labels'] +
                          'VALUE = ' + event['value'])
        label = str(event['labels'])
        labelsplit = label.split(",")
        readsensor = labelsplit[1]
        readsensorsplit = readsensor.split("=")
        sensorname = str(readsensorsplit[1])
        self.logger.debug('Sensor Name= ' + sensorname)
        if self.variables['sensors_list'] != '':
            findsensor = self.variables['sensors_list']
            istrue = findsensor.find(sensorname)
            if istrue == -1:
                sensors_list = sensorname + self.variables['sensors_list']
                self.variables['sensors_list'] = sensors_list
                self.logger.debug('list of sensors : ' +
                                  self.variables['sensors_list'])
                self.setactions(sensorname)
            else:
                ActionSyslog('Sensor: ' + sensorname +
                             ' is in Critical state')
                ActionCLI('show environment temperature')
        else:
            self.variables['sensors_list'] = sensorname
            self.logger.debug('list of sensors:' +
                              self.variables['sensors_list'])
            self.setactions(sensorname)

    def setactions(self, sensorname):
        self.logger.debug('+++ CALLBACK: SENSOR STATUS - CRITICAL!')
        self.set_alert_level(AlertLevel.CRITICAL)
        ActionSyslog('Sensor: ' + sensorname +
                     ' is in Critical state')
        ActionCLI('show environment temperature')

    def sensor_status_action_normal(self, event):
        if self.get_alert_level() is not None:
            if self.variables['sensors_list'] == '':
                self.set_policy_status_normal()
            else:
                print('********NORMAL********')
                label = str(event['labels'])
                labelsplit = label.split(",")
                readsensor = labelsplit[1]
                readsensorsplit = readsensor.split("=")
                sensorname = str(readsensorsplit[1])

                '''
                delete all Sensor Name's which moved back to
                Normal state from Critical state
                '''
                index = 0
                length = len(sensorname)
                findsensor = self.variables['sensors_list']
                index = findsensor.find(sensorname)
                if index != -1:
                    # index = string.find(str, substr)
                    findsensor = findsensor[
                        0:index] + findsensor[
                            index + length:]
                    self.variables['sensors_list'] = findsensor
                    self.logger.debug('Sensor name deleted: ' + sensorname)
                    self.logger.debug('Current Sensors list: ' +
                                      self.variables['sensors_list'])
                    ActionSyslog('Sensor ' + sensorname +
                                 ' is back to Normal')
                    if self.variables['sensors_list'] == '':
                        self.set_policy_status_normal()

    def set_policy_status_normal(self):
        self.remove_alert_level()
        ActionSyslog('All Sensors are Normal')
