# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2021,2024 Hewlett Packard Enterprise Development LP
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
    'Name': 'route_count_monitor',
    'Description': 'Monitors the route count on the switch',
    'Version': '1.1',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.04',
    'AOSCXPlatformList': ['6300', '6400', '8320', '8400']
}

ParameterDefinitions = {
    'upper_count_threshold': {
        'Name': 'Route Count Upper Threshold Value',
        'Description': 'When the number of routes exceeds '
                       'this threshold value, the agent '
                       'will send a Syslog warning and set '
                       'the agent status to critical',
        'Type': 'integer',
        'Default': 10000
    },
    'lower_count_threshold': {
        'Name': 'Route Count Lower Threshold Value',
        'Description': 'When the number of routes are '
                       'lesser than this value, '
                       'the agent will send a Syslog warning '
                       'and set the agent status to normal',
        'Type': 'integer',
        'Default': 9500
    }
}


class Policy(NAE):

    def __init__(self):

        uri = '/rest/v1/system/vrfs/*/routes?count'
        self.monitor = Monitor(Sum(uri), 'Route Count')

        self.rule = Rule('Route count rule')
        self.rule.condition('{} >= {}',
                            [self.monitor,
                             self.params['upper_count_threshold']])
        self.rule.action(self.route_action_critical)

        self.rule.clear_condition('{} <= {}',
                                  [self.monitor,
                                   self.params['lower_count_threshold']])
        self.rule.clear_action(self.route_action_normal)

    def route_action_critical(self, event):
        if self.get_alert_level() is None:
            ActionSyslog('Current route count is ' + event["value"] +
                         ' which exceeds the upper threshold value of {}',
                         [self.params['upper_count_threshold']],
                         severity=SYSLOG_WARNING)
            self.set_alert_level(AlertLevel.CRITICAL)
            ActionCLI("show ip route summary all-vrfs")

    def route_action_normal(self, event):
        if self.get_alert_level() is not None:
            ActionSyslog('Current route count is ' + event["value"] +
                         ' which is below the lower threshold value of {}',
                         [self.params['lower_count_threshold']],
                         severity=SYSLOG_WARNING)
            self.remove_alert_level()

    def on_agent_re_enable(self, event):
        if self.get_alert_level() is not None:
            ActionSyslog('Route count is within the threshold value',
                         severity=SYSLOG_WARNING)
            self.remove_alert_level()