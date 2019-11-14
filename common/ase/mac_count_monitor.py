# -*- coding: utf-8 -*-
#
# (c) Copyright 2019 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# MAC address count Monitoring


Manifest = {
    'Name': 'mac_count_monitor',
    'Description': 'Agent to monitor count of MAC address learnt ',
    'Version': '2.1',
    'TargetSoftwareVersion': '10.03',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'threshold': {
        'Name': 'Total MAC address count threshold',
        'Description': 'This parameter represents the threshold value above '
                       'which the total count of MAC addresses on the '
                       'switch, generates an alert.',
        'Type': 'Integer',
        'Default': 1700
    }
}


class Policy(NAE):

    def __init__(self):

        uri1 = '/rest/v1/system/vlans/*/macs/?count'

        sum_m = Sum(uri1)
        self.total_mac_count_monitor = Monitor(sum_m, "Total MAC Addresses "
                                                      "count")
        self.rule = Rule('Total MAC Addresses Count')
        self.rule.condition('{} > {}', [self.total_mac_count_monitor,
                                        self.params['threshold']])
        self.rule.action(self.set_alert_action)

        self.rule.clear_condition('{} < {}', [self.total_mac_count_monitor,
                                              self.params['threshold']])
        self.rule.clear_action(self.clear_alert_action)

    def set_alert_action(self, event):

        self.set_alert_level(AlertLevel.CRITICAL)
        message = "The total count of MAC Addresses on the switch is {} " \
                  "which is above the threshold value of {}".\
            format(event['value'], str(self.params['threshold']))
        self.logger.info(message)
        ActionSyslog(message, severity=SYSLOG_WARNING)

    def clear_alert_action(self, event):
        self.remove_alert_level()
        message = "The total count of MAC Addresses is back to normal: {}". \
            format(event['value'])
        self.logger.info(message)
        ActionSyslog(message, severity=SYSLOG_WARNING)
