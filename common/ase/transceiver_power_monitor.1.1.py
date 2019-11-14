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

from requests import get

PROXY_DICT = {'http': None, 'https': None}

Manifest = {
    'Name': 'transceiver_power_monitor',
    'Description':
        'This script helps in detecting faults with the transceiver rx '
        'and tx power.',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}

Thresholds = {
    'JL308A': {
        'tx_power_high': 3.16,
        'tx_power_low': 0.398,
        'rx_power_high': 3.16,
        'rx_power_low': 0.25
    },
    'JH231A': {
        'tx_power_high': 1,
        'tx_power_low': 0.174,
        'rx_power_high': 1.738,
        'rx_power_low': 0.112
    },
    'JH232A': {
        'tx_power_high': 1.698,
        'tx_power_low': 0.199,
        'rx_power_high': 1.698,
        'rx_power_low': 0.043
    },
    'JH233A': {
        'tx_power_high': 1,
        'tx_power_low': 0.174,
        'rx_power_high': 1.738,
        'rx_power_low': 0.102
    },
    'J9150A': {
        'tx_power_high': 0.794,
        'tx_power_low': 0.186,
        'rx_power_high': 1.122,
        'rx_power_low': 0.102
    },
    'J4858C': {
        'tx_power_high': 1,
        'tx_power_low': 0.112,
        'rx_power_high': 0.501,
        'rx_power_low': 0.020
    },
    'J4859C': {
        'tx_power_high': 0.501,
        'tx_power_low': 0.112,
        'rx_power_high': 0.501,
        'rx_power_low': 0.01
    },
    'J4860C': {
        'tx_power_high': 3.162,
        'tx_power_low': 1,
        'rx_power_high': 0.501,
        'rx_power_low': 0.006
    },
    'J9151A': {
        'tx_power_high': 1.122,
        'tx_power_low': 0.151,
        'rx_power_high': 1.122,
        'rx_power_low': 0.036
    },
    'J9153A': {
        'tx_power_high': 2.511,
        'tx_power_low': 0.339,
        'rx_power_high': 0.794,
        'rx_power_low': 0.026
    },
    'J9152A': {
        'tx_power_high': 1.122,
        'tx_power_low': 0.224,
        'rx_power_high': 1.412,
        'rx_power_low': 0.224
    }
}


def get_interface(event):
    label = event['labels']
    first = '='
    last = ',map_key'
    try:
        start = label.index(first) + len(first)
        end = label.index(last, start)
        return label[start:end]
    except ValueError:
        return ""


def rest_get(url):
    response = get(url, verify=False, proxies=PROXY_DICT)
    return response


class Agent(NAE):

    def __init__(self):

        uri1 = '/rest/v1/system/interfaces/*?attributes=pm_info.tx_power'
        self.m1 = Monitor(uri1, 'tx power')

        uri2 = '/rest/v1/system/interfaces/*?attributes=pm_info.rx_power'
        self.m2 = Monitor(uri2, 'rx power')

        self.variables['rx_power_low'] = 0
        self.variables['tx_power_low'] = 0
        self.variables['rx_power_high'] = 0
        self.variables['tx_power_high'] = 0
        self.variables['tx_power_max'] = 0
        self.variables['rx_power_max'] = 0

        hasData, transceiver = self.get_transceiver_data()
        if hasData:
            self.r1 = Rule('High tx power')
            self.r1.condition(
                '{} > ' + str(Thresholds[transceiver]['tx_power_high']), [self.m1])
            self.r1.action(self.action_high_transceiver_threshold)

            self.r2 = Rule('High rx power')
            self.r2.condition(
                '{} > ' + str(Thresholds[transceiver]['rx_power_high']), [self.m2])
            self.r2.action(self.action_high_transceiver_threshold)

            self.r3 = Rule('Low tx power')
            self.r3.condition(
                '{} < ' + str(Thresholds[transceiver]['tx_power_low']), [self.m1])
            self.r3.action(self.action_low_transceiver_threshold)

            self.r4 = Rule('Low rx power')
            self.r4.condition(
                '{} < ' + str(Thresholds[transceiver]['rx_power_low']), [self.m2])
            self.r4.action(self.action_low_transceiver_threshold)

            self.r5 = Rule('Tx power in correct range')
            self.r5.condition(
                '{} <= ' + str(Thresholds[transceiver]['tx_power_high']), [self.m1])
            self.r5.action(self.action_power_normal)

            self.r6 = Rule('Rx power in correct range')
            self.r6.condition(
                '{} <= ' + str(Thresholds[transceiver]['rx_power_high']), [self.m2])
            self.r6.action(self.action_power_normal)

            self.variables['interfaces_in_critical_state'] = ''

    def get_transceiver_data(self):
        transceiver_data_available = False
        uri3 = '/rest/v1/system/interfaces/*?attributes=name,pm_info&depth=1'
        url = HTTP_ADDRESS + uri3
        response = rest_get(url)
        if response is not None:
            for row in response.json():
                if 'proprietary_product_number' in row['pm_info']:
                    transceiver = row['pm_info'][
                        'proprietary_product_number'].strip()
                    if transceiver in Thresholds:
                        transceiver_data_available = True
        return transceiver_data_available, transceiver

    def action_high_transceiver_threshold(self, event):
        interface_id = get_interface(event)
        rule_description = event['rule_description']
        key = interface_id + rule_description + ' threshold'
        if key in self.variables and event['value'] > self.variables[key]:
            ActionSyslog(
                '{} detected on interface {}'.format(
                    rule_description, interface_id))
            if self.get_alert_level() is not AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
            ActionCLI(
                "show interface {} transceiver detail".format(interface_id))
            ActionCLI(
                "show interface {} transceiver threshold-violations".format(interface_id))
            self.update_variables(interface_id, rule_description, "set")

    def action_low_transceiver_threshold(self, event):
        interface_id = get_interface(event)
        rule_description = event['rule_description']
        key = interface_id + rule_description + ' threshold'
        if key in self.variables and event['value'] < self.variables[key]:
            ActionSyslog(
                '{} detected on interface {}'.format(
                    rule_description, interface_id))
            if self.get_alert_level() is not AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
            ActionCLI(
                "show interface {} transceiver detail".format(interface_id))
            ActionCLI(
                "show interface {} transceiver threshold-violations".format(interface_id))
            self.update_variables(interface_id, rule_description, "set")

    def action_power_normal(self, event):
        interface_id = get_interface(event)
        rule_description = event['rule_description']
        power_type = rule_description.split()[0].lower()
        key1 = interface_id + 'Low ' + power_type + ' power threshold'
        key2 = interface_id + 'High ' + power_type + ' power threshold'
        if self.check_attribute_exists(interface_id, power_type):
            if key1 in self.variables and key2 in self.variables and self.variables[
                    key1] <= event['value'] <= self.variables[key2]:
                self.clear_critical_interface(interface_id)
                ActionSyslog(
                    "Interface {} {} power is back to normal".format(
                        interface_id, power_type))
                if self.get_alert_level() is not None:
                    self.logger.info("Current alert level:" +
                                     str(self.get_alert_level()))
                    if not self.variables['interfaces_in_critical_state']:
                        self.set_alert_level(AlertLevel.NONE)
                        self.logger.debug('Unset the previous status')
                        self.logger.debug('### Normal Callback executed')

    def update_variables(self, interface_id, attribute, state):
        if interface_id not in self.variables['interfaces_in_critical_state']:
            critical_interfaces_list = self.variables[
                'interfaces_in_critical_state']
            self.variables[
                'interfaces_in_critical_state'] = critical_interfaces_list + interface_id
        key = interface_id + '_' + attribute
        self.variables[key] = state

    def check_attribute_exists(self, interface_id, power_type):
        key1 = interface_id + '_' + 'High ' + power_type + ' power'
        key2 = interface_id + '_' + 'Low ' + power_type + ' power'
        if key1 in self.variables or key2 in self.variables:
            return True
        else:
            return False

    def clear_critical_interface(self, interface_id):
        if interface_id in self.variables['interfaces_in_critical_state']:
            critical_interfaces_list = self.variables[
                'interfaces_in_critical_state']
            critical_interfaces_list = critical_interfaces_list.replace(
                interface_id, '')
            self.variables[
                'interfaces_in_critical_state'] = critical_interfaces_list
