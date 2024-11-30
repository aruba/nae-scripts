# -*- coding: utf-8 -*-
#
# (c) Copyright 2019,2021-2022,2024 Hewlett Packard Enterprise Development LP
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

LONG_DESCRIPTION = '''\
## Summary

The purpose of this script is to help in automatic broadcast storm fault detection which helps protect against network loops. 

## Software Versions Required

Script Version 2.0: ArubaOS-CX 10.11 Minimum

## Platforms Supported

Script Version 2.0: 6200, 6300, 64xx

## Script Description

The main components of the script are monitors, conditions and actions.

- Monitors:  This script monitors the following for all interfaces:
    1. Broadcast storm fault - The user can provide the threshold value for the rate of change of broadcast packets over 20 seconds. For low sensitivity level, the threshold value is 170500, for medium sensitivity level, it is 100000 and for high sensitivity level, it is 29500. 
        - Conditions for this monitor are -
            1. When the threshold provided is for high sensitivity level and there is broadcast storm fault, the following actions are taken -
                - The agent status is marked as Minor, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at high sensitivity level'.
            2. When the threshold provided is for medium sensitivity level and there is broadcast storm fault, the following actions are taken -
                - The agent status is marked as Major, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at medium sensitivity level'.
            3. When the threshold provided is for low sensitivity level and there is broadcast storm fault, the following actions are taken -
                - The agent status is marked as Critical, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at low sensitivity level'.
            4. When there is no longer broadcast storm fault, Syslog says 'Broadcast storm fault detected on interface <name> is back to normal'.
                - If there is no fault found on any of the interfaces, the agent status is marked as Normal.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
'''

Manifest = {
    'Name': 'broadcast_storm_monitor',
    'Description': 'This script monitors for broadcast packets storm'
                   ' on an interface and shuts down the interface'
                   ' if the interface shut down option is enabled.',
    'Version': '2.0',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.11',
    'AOSCXPlatformList': ['6200', '6300', '64xx']
}

ParameterDefinitions = {
    'broadcast_threshold': {
        'Name': 'Threshold for broadcast storm fault',
        'Description':
            'Threshold for rate of change of broadcast packets over '
            ' time_interval seconds.'
            ' For low sensitivity level, set threshold equal to'
            ' low_sensitivity_level value, for medium sensitivity,'
            ' set threshold equal to medium_sensitivity_level value,'
            ' for high sensitivity set threshold equal to'
            ' high_sensitivity_level value.',
        'Type': 'integer',
        'Default': 5500
    },

    'enable_interface_shut_down': {
        'Name': 'Shut down interface',
        'Description': 'This parameter indicates if the interface needs to'
                       ' be shutdown when the broadcast_threshold value is met.'
                       ' If the interface is to be shutdown when the'
                       ' threshold is met, set this parameter as True.',
        'Type': 'string',
        'Default': 'False'
    },

    'low_sensitivity_level': {
        'Name': 'Low sensitivity level',
        'Description': 'Value for low sensitivity level. When the'
                       ' broadcast storm packet count matches the'
                       ' low sensitivity value, the NAE agent alert'
                       ' level becomes Critical.',
        'Type': 'integer',
        'Default': 31200
    },

    'medium_sensitivity_level': {
        'Name': 'Medium sensitivity level',
        'Description': 'Value for medium sensitivity level. When the'
                       ' broadcast storm packet count matches the'
                       ' medium sensitivity value, the NAE agent alert'
                       ' level becomes Major.',
        'Type': 'integer',
        'Default': 18400
    },

    'high_sensitivity_level': {
        'Name': 'High sensitivity level',
        'Description': 'Value for high sensitivity level. When the'
                       ' broadcast storm packet count matches the'
                       ' high sensitivity value, the NAE agent alert'
                       ' level becomes Minor.',
        'Type': 'integer',
        'Default': 5500
    },
}


class Agent(NAE):

    INFINITY = float("inf")

    def __init__(self):

        # Broadcast packets
        uri1 = '/rest/v1/system/interfaces/*?attributes=statistics.if_hc_in_broadcast_packets&filter=type:system'
        broadcast_uri = Rate(uri1, '60 seconds')
        self.m1 = Monitor(
            broadcast_uri, 'Rate of interface broadcast packets (packets/s)')

        self.r1 = Rule('Broadcast storm fault')
        self.r1.condition(
            '{} >= {}', [self.m1, self.params['broadcast_threshold']])
        self.r1.action(self.action_broadcast_sensitivity)
        self.r1.clear_condition(
            '{} < {}', [self.m1, self.params['broadcast_threshold']])
        self.r1.clear_action(self.action_clear_broadcast_sensitivity)

        # variables
        self.variables['links_with_alert'] = ''

        self.validate_parameter_values()

    def validate_parameter_values(self):
        threshold = self.params['broadcast_threshold'].value
        low_sensitivity = self.params['low_sensitivity_level'].value
        medium_sensitivity = self.params['medium_sensitivity_level'].value
        high_sensitivity = self.params['high_sensitivity_level'].value

        if high_sensitivity >= medium_sensitivity:
            raise Exception(
                "High sensitivity value should be less than medium sensitvity value")

        if medium_sensitivity >= low_sensitivity:
            raise Exception(
                "Medium sensitivity value should be less than low sensitvity value")

        if threshold > low_sensitivity or threshold < high_sensitivity:
            raise Exception(
                "broadcast threshold value should be between high sensitivity and low sensitivity values")

    def action_sensitivity(self, event, value, sensitivity_level):
        interface_id = get_interface(event)
        if not interface_id:
            raise Exception(
                "Unable to get interface_id for the broadcast packets from the event")

        rule_description = event['rule_description']
        links_with_alert = self.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)

        if sensitivity_level == "high":
            ActionSyslog(
                '{} detected on interface {} at high sensitivity level: rate at {} packets/sec'.format(
                    rule_description,
                    interface_id,
                    value),
                severity=SYSLOG_WARNING)
            if self.get_alert_level() != AlertLevel.MINOR and \
                    self.get_alert_level() != AlertLevel.MAJOR and \
                    self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.MINOR)
        elif sensitivity_level == "medium":
            ActionSyslog(
                '{} detected on interface {} at medium sensitivity level: rate at {} packets/sec'.format(
                    rule_description,
                    interface_id,
                    value),
                severity=SYSLOG_WARNING)
            if self.get_alert_level() != AlertLevel.MAJOR and self.get_alert_level(
            ) != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.MAJOR)
        elif sensitivity_level == "low":
            ActionSyslog(
                '{} detected on interface {} at low sensitivity level: rate at {} packets/sec'.format(
                    rule_description,
                    interface_id,
                    value),
                severity=SYSLOG_WARNING)
            if self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
        ActionCLI("show interface {}".format(interface_id),
                  title=Title("Interface details"))
        ActionCLI("show interface {} extended".format(interface_id),
                  title=Title("Interface counters information"))

    def action_broadcast_sensitivity(self, event):
        value = event['value']
        threshold = self.params['broadcast_threshold'].value
        low_sensitivity = self.params['low_sensitivity_level'].value
        medium_sensitivity = self.params['medium_sensitivity_level'].value
        high_sensitivity = self.params['high_sensitivity_level'].value

        self.validate_parameter_values()

        try:
            input_value = float(value)
            threshold_value = float(threshold)
            low_sensitivity_value = float(low_sensitivity)
            medium_sensitivity_value = float(medium_sensitivity)
            high_sensitivity_value = float(high_sensitivity)

        except ValueError:
            print("Threshold value/Input/Sensitivity value is not a numerical value")
            return
        if input_value >= threshold_value >= low_sensitivity_value:
            self.action_sensitivity(event, input_value, "low")
        elif medium_sensitivity_value <= threshold_value < low_sensitivity_value \
                and input_value >= threshold_value:
            self.action_sensitivity(event, input_value, "medium")
        elif high_sensitivity_value <= threshold_value < medium_sensitivity_value \
                and input_value >= threshold_value:
            self.action_sensitivity(event, input_value, "high")

        if str(self.params['enable_interface_shut_down']).lower() == 'true':
            self.action_shut_down_interface(event)

    def action_clear_broadcast_sensitivity(self, event):
        value = event['value']
        threshold = self.params['broadcast_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def clear_alert_level(self, event):
        interface_id = get_interface(event)
        if not interface_id:
            raise Exception(
                "Unable to get interface_id for the broadcast packets from the event")
        rule_description = event['rule_description']
        links_with_alert = self.variables['links_with_alert']
        interface = interface_id + ':'
        if interface in links_with_alert:
            links_with_alert = links_with_alert.replace(interface, '')
            self.variables['links_with_alert'] = links_with_alert
            ActionSyslog('{} on interface {} is back to normal'.format(
                rule_description, interface_id), severity=SYSLOG_WARNING)
            if not self.variables['links_with_alert']:
                if self.get_alert_level() is not None:
                    self.remove_alert_level()

    def add_interface_to_alert_list(self, interface_id):
        links_with_alert = self.variables['links_with_alert'] + \
            interface_id + ':'
        self.variables['links_with_alert'] = links_with_alert

    def action_shut_down_interface(self, event):
        interface_id = get_interface(event)
        if not interface_id:
            raise Exception(
                "Unable to get interface_id for the broadcast packets from the event")
        url = '/rest/v10.08/system/interfaces/{}'.format(
            interface_id.replace('/', '%2F').replace(':', '%3A'))
        headers = {"content-type": "application/json",
                   "Accept": "application/json"}
        try:
            result = self.get_rest_request_json(
                HTTP_ADDRESS + url + '?selector=writable')
            if 'lag' in interface_id:
                result['admin'] = 'down'
            else:
                user_config = result.get('user_config', {})
                user_config['admin'] = 'down'
                result['user_config'] = user_config
            self.put_rest_request(HTTP_ADDRESS + url, headers=headers,
                                  json=result)
            ActionSyslog("Shut down port {}".format(interface_id))
        except NAEException:
            ActionSyslog("Could not shut down port {}".format(interface_id))


def get_interface(event):
    label = event['labels']
    first = '='
    last = ',TimeInterval'
    try:
        start = label.index(first) + len(first)
        end = label.index(last, start)
        return label[start:end]
    except ValueError:
        return ""
