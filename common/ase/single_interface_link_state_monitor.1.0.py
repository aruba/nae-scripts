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
    'Name': 'single_interface_link_state_monitor',
    'Description': 'Interface Link Status Monitoring Agent',
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
        # Interface status
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

    def action_interface_down(self, event):
        self.logger.debug("================ Down ================")
        if self.get_alert_level() != AlertLevel.CRITICAL:
            ActionSyslog(
                'Interface {} Link gone down',
                [self.params['interface_id']])
            ActionCLI("show lldp configuration {}",
                      [self.params['interface_id']])
            ActionCLI("show interface {} extended",
                      [self.params['interface_id']])
            self.set_alert_level(AlertLevel.CRITICAL)
        self.logger.debug("================ /Down ================")

    def action_interface_up(self, event):
        self.logger.debug("================ Up ================")
        if self.get_alert_level() is not None:
            ActionSyslog('Interface {} Link came up',
                         [self.params['interface_id']])
            self.remove_alert_level()
        self.logger.debug("================ /Up ================")
