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
    'Name': 'temp_sensor_status_transition_param_monitor',
    'Description': 'Network Analytics Agent Script to monitor'
                   'status transition supplied as a parameter'
                   'for all temperature sensors',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'transition_from': {
        'Name': 'Transition from state',
        'Description': 'Transition state for \'from\'',
        'Type': 'string',
        'Default': 'normal'
    },
    'transition_to': {
        'Name': 'Transition to state',
        'Description': 'Transition state for \'to\'',
        'Type': 'string',
        'Default': 'critical'
    }
}


class Agent(NAE):

    def __init__(self):

        uri1 = '/rest/v1/system/subsystems/*/*/temp_sensors/*?' \
            'attributes=status'
        self.m1 = Monitor(uri1, 'Sensor status')
        self.r1 = Rule('Sensor Status Transition')
        self.r1.condition('transition {} from \"{}\" to \"{}\"', [
            self.m1,
            self.params['transition_from'],
            self.params['transition_to']])
        self.r1.action(self.temp_sensor_status_transition_action)

    def temp_sensor_status_transition_action(self, event):
        self.logger.debug("======= Sensor status transition ============")
        label = event['labels']
        sensorname = label.split(',')[1].split('=')[1]
        self.logger.debug('Sensor Name: ' + sensorname)
        ActionSyslog('Sensor: ' + sensorname +
                     ' status changed from \"{}\" to \"{}\"',
                     [self.params['transition_from'],
                      self.params['transition_to']])
        ActionCLI('show environment temperature')
        self.logger.debug("========= Sensor status transition  ========")
