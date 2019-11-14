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
    'Name': 'interface_state_stats_monitor',
    'Description': 'Interface Link state and Statistics Monitoring Agent',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'interface_id': {
        'Name': 'Interface Id',
        'Description': 'Interface to be monitored',
        'Type': 'string',
        'Default': '1/1/1'
    }
}


class Agent(NAE):

    def __init__(self):

        # Link status
        uri1 = '/rest/v1/system/interfaces/{}?attributes=link_state'
        self.m1 = Monitor(
            uri1,
            'Interface Link status',
            [self.params['interface_id']])
        self.r1 = Rule('Link Went Down')
        self.r1.condition('transition {} from "up" to "down"', [self.m1])
        self.r1.action(self.action_interface_down)

        # Reset agent status when link is up
        self.r2 = Rule('Link Came UP')
        self.r2.condition('transition {} from "down" to "up"', [self.m1])
        self.r2.action(self.action_interface_up)

        # rx packets
        uri2 = '/rest/v1/system/interfaces/{}?attributes=statistics.rx_packets'
        self.m2 = Monitor(
            uri2,
            'Rx Packets (packets)',
            [self.params['interface_id']])

        # rx packets dropped
        uri3 = '/rest/v1/system/interfaces/{}?attributes=statistics.rx_dropped'
        self.m3 = Monitor(
            uri3,
            'Rx Packets Dropped (packets)',
            [self.params['interface_id']])

        # tx packets
        uri4 = '/rest/v1/system/interfaces/{}?attributes=statistics.tx_packets'
        self.m4 = Monitor(
            uri4,
            'Tx Packets (packets)',
            [self.params['interface_id']])

        # tx packets dropped
        uri5 = '/rest/v1/system/interfaces/{}?attributes=statistics.tx_dropped'
        self.m5 = Monitor(
            uri5,
            'Tx Packets Dropped (packets)',
            [self.params['interface_id']])

    def action_interface_down(self, event):
        ActionSyslog(
            'Interface {} Link gone down',
            [self.params['interface_id']])
        ActionCLI("show lldp configuration {}", [self.params['interface_id']])
        ActionCLI("show interface {} extended", [self.params['interface_id']])
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
        self.logger.debug("### Critical Callback executed")

    def action_interface_up(self, event):
        self.logger.info("Current alert level: " + str(self.get_alert_level()))
        if self.get_alert_level() is not None:
            ActionSyslog('Interface {} Link came up',
                         [self.params['interface_id']])
            self.remove_alert_level()
            self.logger.debug('Unset the previous status')

        self.logger.debug('### Normal Callback executed')
