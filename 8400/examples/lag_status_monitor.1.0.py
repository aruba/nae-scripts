# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Hewlett Packard Enterprise Development LP
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
    'Name': 'lag_status_monitor',
    'Description': 'LAG status monitoring agent using PSPO',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


ParameterDefinitions = {
    'lag_name': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': 'lag1'
    }
}


class Policy(NAE):

    def __init__(self):

        self.variables['forwarding'] = ''
        self.variables['blocked_by_aggregation'] = ''

        uri1 = '/rest/v1/system/ports/{}?' \
            'attributes=forwarding_state.forwarding'
        self.m1 = Monitor(
            uri1,
            'LAG Forwarding State',
            [self.params['lag_name']])
        self.r1 = Rule('Port Forwarding is false')
        self.r1.condition('transition {} from "true" to "false"', [self.m1])
        self.r1.action(self.status_transition_action)

        self.r2 = Rule('Port Forwarding is back to normal')
        self.r2.condition('transition {} from "false" to "true"', [self.m1])
        self.r2.action(self.status_transition_action)

        uri3 = '/rest/v1/system/ports/{}?' \
            'attributes=forwarding_state.blocking_layer'
        self.m3 = Monitor(
            uri3,
            'Port Blocking Layer',
            [self.params['lag_name']])
        self.r3 = Rule('Forwarding state is blocked by AGGREGATION layer')
        self.r3.condition('{} == "AGGREGATION"', [self.m3])
        self.r3.action(self.blocking_layer_action)

        self.r4 = Rule('Forwarding state is not blocked by AGGREGATION layer')
        self.r4.condition('{} != "AGGREGATION"', [self.m3])
        self.r4.action(self.blocking_layer_normal)

    def status_transition_action(self, event):
        self.event_data = event['value']
        self.variables['forwarding'] = str(self.event_data)
        self.logger.info("forwarding:" + str(self.variables['forwarding']))
        self.collect_data()

    def blocking_layer_action(self, event):
        self.variables['blocked_by_aggregation'] = 'true'
        self.logger.info(
            "Blocking layer:" + str(self.variables['blocked_by_aggregation']))
        self.collect_data()

    def blocking_layer_normal(self, event):
        self.variables['blocked_by_aggregation'] = 'false'
        self.collect_data()

    def collect_data(self):
        if self.variables['forwarding'] == 'false' and \
                self.variables['blocked_by_aggregation'] == 'true':
            if self.get_alert_level() != AlertLevel.CRITICAL:
                ActionSyslog('LAG id {} is down', [self.params['lag_name']])
                ActionCLI('show lacp aggregates {}', [self.params['lag_name']])
                self.set_alert_level(AlertLevel.CRITICAL)
        else:
            if self.get_alert_level() is not None:
                self.remove_alert_level()
                self.logger.debug('Unset the previous status')
