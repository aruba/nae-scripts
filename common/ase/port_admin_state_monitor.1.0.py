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
    'Name': 'port_admin_state_monitor',
    'Description': 'Port Admin Status Monitoring Agent',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'port_id': {
        'Name': 'Port Id',
        'Description': 'Port to be monitored',
        'Type': 'string',
        'Default': '1/1/1'
    }
}


class Agent(NAE):

    def __init__(self):

        # Port status
        uri1 = '/rest/v1/system/ports/{}?attributes=admin'
        self.m1 = Monitor(
            uri1,
            'Port admin status',
            [self.params['port_id']])
        self.r1 = Rule('Port disabled administratively')
        self.r1.condition('transition {} from "up" to "down"', [self.m1])
        self.r1.action(self.action_port_down)

        # Reset agent status when port is up
        self.r2 = Rule('Port enabled administratively')
        self.r2.condition('transition {} from "down" to "up"', [self.m1])
        self.r2.action(self.action_port_up)

    def action_port_down(self, event):
        ActionSyslog(
            'Port {} is disabled administratively',
            [self.params['port_id']])
        ActionCLI("show lldp configuration {}", [self.params['port_id']])
        ActionCLI("show interface {} extended", [self.params['port_id']])
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
        self.logger.debug("### Critical Callback executed")

    def action_port_up(self, event):
        self.logger.info("Current alert level: " + str(self.get_alert_level()))
        if self.get_alert_level() is not None:
            ActionSyslog(
                'Port {} is enabled administratively',
                [self.params['port_id']])
            self.remove_alert_level()
            self.logger.debug('Unset the previous status')

        self.logger.debug('### Normal Callback executed')
