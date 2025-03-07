# -*- coding: utf-8 -*-
#
# (c) Copyright 2019-2020,2024 Hewlett Packard Enterprise Development LP
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

LONG_DESCRIPTION = '''\
## Script Description

The main components of the script are Manifest, Parameter Definitions and python code. 
- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - Threshold -  Total MAC address count threshold

The script defines Monitor Resource URI(s), Monitor condition and Action : 
- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. Total MAC addresses count(sum of all URI).

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Actions:  This script specifies monitoring action as following: 
    - If the total Mac addresses count is more than threshold value mentioned in the threshold parameter, the following actions are executed:
        1. A log message is generated with the total MAC addresses on the switch .
        2. The agent alert level is updated to Critical.
    - When the rate of total Mac addresses count is less than the threshold value, the following actions are executed. 
        1. The agent alert level is updated to Normal.
        2. A log message is generated with the rate of decrease value.
'''

Manifest = {
    'Name': 'mac_count_monitor',
    'Description': 'Agent to monitor count of MAC address learnt ',
    'Version': '2.1',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.04',
    'AOSCXPlatformList': ['6300', '6400', '8320', '8400']
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

        uri1 = '/rest/v1/system/vlans/*/macs/?count&filter=selected:true'

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
