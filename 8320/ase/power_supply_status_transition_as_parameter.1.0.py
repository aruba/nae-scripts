# -*- coding: utf-8 -*-
#
# (c) Copyright 2018-2019 Hewlett Packard Enterprise Development LP
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
    'Name': 'power_supply_status_transition_as_parameter',
    'Description': 'System Power Supply status transition '
                   'monitoring agent on provided from and to states',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'transition_from_state': {
        'Name': 'Power Supply Unit (PSU) transition from state',
        'Description': 'Power Supply Unit (PSU) transition from state',
        'Type': 'string',
        'Default': 'ok'
    },
    'transition_to_state': {
        'Name': 'Power Supply Unit (PSU) transition to state',
        'Description': 'Power Supply Unit (PSU) transition from state',
        'Type': 'string',
        'Default': 'fault_output'
    }
}


class Agent(NAE):

    def __init__(self):
        chassis_subsys_name = '1'

        uri1 = '/rest/v1/system/subsystems/chassis/%s/power_supplies/*?' \
               'attributes=status' % chassis_subsys_name
        self.m1 = Monitor(uri1, 'PSU status')

        self.r1 = Rule('PSU Status Transition')
        self.r1.condition(
            'transition {} from \"{}\" to \"{}\"',
            [self.m1,
             self.params['transition_from_state'],
             self.params['transition_to_state']])
        self.r1.action(self.psu_status_transition_action)

    def psu_status_transition_action(self, event):
        self.logger.debug("======= PSU status transition ============")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, psu = label.split(',')[0].split('=')
        self.logger.debug('psu - ' + psu)
        ActionSyslog(
            psu + ' status changed from \"{}\" to \"{}\"',
            [self.params['transition_from_state'],
             self.params['transition_to_state']])
        ActionCLI('show environment power-supply')
        self.logger.debug("========= /PSU status transition  ========")
