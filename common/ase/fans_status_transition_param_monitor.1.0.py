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
    'Name': 'fans_status_transition_as_parameter_monitor',
    'Description': 'Agent to monitor status of a fan, '
                   'wherin transition \"from\" and \"to\" '
                   'values are supplied as parameters. '
                   'The values for from and to can be '
                   'uninitialized/ok/fault.',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'transition_from': {
        'Name': 'Transition from state',
        'Description': 'Transition state for \'from\'',
        'Type': 'string',
        'Default': 'ok'
    },
    'transition_to': {
        'Name': 'Transition to state',
        'Description': 'Transition state for \'to\'',
        'Type': 'string',
        'Default': 'fault'
    }
}


class Agent(NAE):

    def __init__(self):
        uri1 = '/rest/v1/system/subsystems/*/*/fans/*?attributes=status'
        self.m1 = Monitor(uri1, 'Fan Status')

        self.r1 = Rule('Fan Status Transition')
        self.r1.condition('transition {} from \"{}\" to \"{}\"', [
            self.m1,
            self.params['transition_from'],
            self.params['transition_to']])
        self.r1.action(self.fan_status_action)

    def fan_status_action(self, event):
        self.logger.debug('*******FAN STATUS - TRANSITIION*********')
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, fanname = label.split(',')[0].split('=')
        self.logger.debug('FanName - ' + fanname)
        ActionSyslog('Fan' + fanname +
                     ' status changed from \"{}\" to \"{}\"',
                     [self.params['transition_from'],
                      self.params['transition_to']])
        ActionCLI('show environment fan')
        self.logger.debug('*******FAN STATUS - TRANSITIION*********')

    def on_agent_restart(self, event):
        self.remove_alert_level()
