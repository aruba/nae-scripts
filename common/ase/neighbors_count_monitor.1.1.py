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
    'Name': 'neighbors_count_monitor',
    'Description': 'Agent to monitor number of neighbors learnt using ARP',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'upper_count_threshold': {
        'Name': 'Neighbors Count Upper Threshold Value',
        'Description': 'When the number of neighbors exceeds '
                       'this threshold value, the agent '
                       'will send a Syslog warning and set '
                       'the agent status to critical',
        'Type': 'integer',
        'Default': 10000
    },
    'lower_count_threshold': {
        'Name': 'Neighbors Count Lower Threshold Value',
        'Description': 'When the number of neighbors are '
                       'lesser than this value, '
                       'the agent will send a Syslog warning '
                       'and set the agent status to normal',
        'Type': 'integer',
        'Default': 9500
    }
}


class Policy(NAE):

    def __init__(self):
        uri = '/rest/v1/system/vrfs/*/neighbors?count'
        self.monitor = Monitor(Sum(uri), 'Neighbors Count')

        self.rule = Rule('Neighbors count rule')
        self.rule.condition('{} >= {}',
                            [self.monitor,
                             self.params['upper_count_threshold']])
        self.rule.action(self.neighbors_action_critical)

        self.rule.clear_condition('{} <= {}',
                                  [self.monitor,
                                   self.params['lower_count_threshold']])
        self.rule.clear_action(self.neighbors_action_normal)

    def neighbors_action_critical(self, event):
        if self.get_alert_level() is None:
            self.set_alert_level(AlertLevel.CRITICAL)
            message = "Current neighbors count is {} " \
                "which is above the threshold value of {}".\
                format(event['value'], str(
                    self.params['upper_count_threshold']))
            self.logger.info(message)
            ActionSyslog(message, severity=SYSLOG_WARNING)
            ActionCLI("show arp all-vrfs")

    def neighbors_action_normal(self, event):
        if self.get_alert_level() is not None:
            self.remove_alert_level()
            message = "Neighbors count is within the threshold value."
            self.logger.info(message)
            ActionSyslog(message, severity=SYSLOG_WARNING)

    def on_agent_re_enable(self, event):
        if self.get_alert_level() is not None:
            self.remove_alert_level()
