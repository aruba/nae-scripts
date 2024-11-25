# -*- coding: utf-8 -*-
#
# (c) Copyright 2019-2020,2022,2024 Hewlett Packard Enterprise Development LP
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

import uuid
import ast

Manifest = {
    'Name': 'software_device_health_monitor',
    'Description': 'This script monitors overall software device health.',
    'Version': '2.0',
    'Tags': ['device'],
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.08',
    'AOSCXPlatformList': ['5420', '6200', '6300', '64xx', '8100', '8320', '8325', '8400', '9300']
}

ParameterDefinitions = {
    'threshold': {
        'Name': 'Total MAC address count threshold',
        'Description': 'This parameter represents the threshold value above '
                       'which the total count of MAC addresses on the '
                       'switch, generates an alert.',
        'Type': 'Integer',
        'Default': 1700
    },
    'cpu_threshold': {
        'Name': 'High CPU threshold value in percentage',
        'Description': 'Agent will alert when any monitored System daemon '
                       'CPU utilization crosses this threshold value',
        'Type': 'integer',
        'Default': 90
    },
    'memory_threshold': {
        'Name': 'High Memory threshold value in percentage',
        'Description': 'Agent will alert when any monitored System daemon '
                       'Memory utilization crosses this threshold value',
        'Type': 'integer',
        'Default': 90
    },
    'time_interval': {
        'Name': 'Time interval in seconds to consider CPU/Memory utilization',
        'Description': 'Time interval in seconds to consider '
                       'System daemon CPU utilization',
        'Type': 'integer',
        'Default': 30
    },
    'daemon_1': {
        'Name': 'System daemon name 1',
        'Description': 'System daemon name 1 to monitor CPU and Memory '
                       'utilization',
        'Type': 'string',
        'Default': 'ops-switchd'
    },
    'daemon_2': {
        'Name': 'System daemon name 2',
        'Description': 'System daemon name 2 to monitor CPU and Memory '
                       'utilization',
        'Type': 'string',
        'Default': 'ovsdb-server'
    },
    'daemon_3': {
        'Name': 'System daemon name 3',
        'Description': 'System daemon name 3 to monitor CPU and Memory '
                       'utilization',
        'Type': 'string',
        'Default': 'hpe-routing'
    },
    'daemon_4': {
        'Name': 'System daemon name 4',
        'Description': 'System daemon name 4 to monitor CPU and Memory '
                       'utilization',
        'Type': 'string',
        'Default': 'ndmd'
    },
    'routes_count_ratio_lower_threshold': {
        'Name': 'Route count deviation lower threshold ',
        'Description': 'This parameter represent the lower threshold value up to '
                       'which the ratio between route count on the switch '
                       'and route count on the VSX peer switch is allowed to'
                       ' deviate.',
        'Type': 'float',
        'Default': '0.95',
    },
    'routes_count_ratio_upper_threshold': {
        'Name': 'Route count deviation upper threshold ',
        'Description': 'This parameter represent the upper threshold value up to '
                       'which the ratio between route count on the switch '
                       'and route count on the VSX peer switch is allowed to'
                       ' deviate.',
        'Type': 'float',
        'Default': '1.05',
    },
    'neighbors_count_ratio_lower_threshold': {
        'Name': 'Neighbors count deviation threshold ',
        'Description': 'This parameter represent the lower threshold value up to '
                       'which the ratio between neighbors count on the '
                       'switch and neighbors count on the VSX peer switch is '
                       'allowed to deviate.',
        'Type': 'float',
        'Default': '0.95',
    },
    'neighbors_count_ratio_upper_threshold': {
        'Name': 'Neighbors count deviation threshold ',
        'Description': 'This parameter represent the upper threshold value up to '
                       'which the ratio between neighbors count on the '
                       'switch and neighbors count on the VSX peer switch is '
                       'allowed to deviate.',
        'Type': 'float',
        'Default': '1.05',
    },
    'mac_addresses_count_ratio_lower_threshold': {
        'Name': 'MAC addresses count deviation lower threshold ',
        'Description': 'This parameter represent the lower threshold value up to '
                       'which the ratio between MAC addresses count on the '
                       'switch and MAC addresses count on the VSX peer switch '
                       'is allowed to deviate.',
        'Type': 'float',
        'Default': '0.95',
    },
    'mac_addresses_count_ratio_upper_threshold': {
        'Name': 'MAC addresses count deviation upper threshold ',
        'Description': 'This parameter represent the upper threshold value up to '
                       'which the ratio between MAC addresses count on the '
                       'switch and MAC addresses count on the VSX peer switch '
                       'is allowed to deviate.',
        'Type': 'float',
        'Default': '1.05',
    },

    'rate_of_decrease_threshold': {
        'Name': 'Rate of decrease threshold (in percentage)',
        'Description': 'This parameter represents the threshold value above '
                       'which the rate of decrease of MAC addresses on the '
                       'switch is supposed to generate an alert.'
                       'The threshold value is calculated as a percentage of'
                       'the MAC address count at the beginning of the time '
                       'interval during which the rate is calculated.',
        'Type': 'Integer',
        'Default': 10
    },
    'time_interval_mac': {
        'Name': 'Time interval for calculating rate of decrease',
        'Description': 'This parameter represents the time interval over '
                       'which the rate of decrease of MAC addresses count is'
                       'to be calculated.',
        'Type': 'Integer',
        'Default': 1
    },
    'broadcast_threshold': {
        'Name': 'Threshold for broadcast storm fault',
        'Description':
            'Threshold for rate of change of broadcast packets over time_interval seconds'
            'For low sensitivity level, set threshold as 170500, for medium sensitivity, set threshold '
            'as 100000, for high sensitivity, set threshold as 29500',
        'Type': 'integer',
        'Default': 29500
    },
    'tx_drops_threshold': {
        'Name': 'Threshold for tx drops',
        'Description':
            'Threshold for ratio of rate of tx drop packets(over bandwidth) over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.0449, for medium sensitivity, set is as 0.0257 and for high sensitivity, set it as 0.0065',
        'Type': 'float',
        'Default': 0.0065
    }
}

Thresholds = {
    'broadcast_low': 170500,
    'broadcast_medium': 100000,
    'broadcast_high': 29500,
    'tx_drop_low': 0.0449,
    'tx_drop_medium': 0.0257,
    'tx_drop_high': 0.0065}

URI_PREFIX_GET = "/rest/v10.08/"
URI_PREFIX_MONITOR = "/rest/v1/"


class MACCount:
    def __init__(self, agent, alm):
        self.name = self.__class__.__name__
        self.agent = agent
        self.alm = alm
        self.monitors = {}
        self.rules = {}
        self.graphs = {}

    def create_monitors(self):
        uri_mac = URI_PREFIX_MONITOR + 'system/vlans/*/macs/?count&filter=selected:true'
        self.monitors['mac_count'] = Monitor(
            uri_mac, 'Total MAC Addresses count')
        return list(self.monitors.values())

    def create_rules(self):
        self.rules['total_mac_count'] = Rule('Total MAC Addresses Count')
        self.rules['total_mac_count'].condition(
            '{} > {}', [self.monitors['mac_count'], self.agent.params['threshold']])
        self.rules['total_mac_count'].action(self.set_alert_action)

        self.rules['total_mac_count'].clear_condition(
            '{} < {}', [self.monitors['mac_count'], self.agent.params['threshold']])
        self.rules['total_mac_count'].clear_action(self.clear_alert_action)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['mac_count'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("Total MAC addresses count"),
                  dashboard_display=True)
        return list(self.graphs.values())

    def set_alert_action(self, event):
        rule_description = event['rule_description']
        message = "The total count of MAC Addresses on the switch is {} " \
                  "which is above the threshold value of {}".\
            format(event['value'], str(self.agent.params['threshold']))
        self.agent.logger.info(message)
        self.agent.action_syslog(message)
        self.alm.publish_alert_level(self.name, rule_description, 'CRITICAL')

    def clear_alert_action(self, event):
        rule_description = event['rule_description']
        message = "The total count of MAC Addresses is back to normal: {}". \
            format(event['value'])
        self.agent.logger.info(message)
        self.agent.action_syslog(message)
        self.alm.publish_alert_level(self.name, rule_description, 'NONE')


class MACDecreaseRate:
    def __init__(self, agent, alm):
        self.name = self.__class__.__name__
        self.agent = agent
        self.alm = alm
        self.monitors = {}
        self.rules = {}
        self.graphs = {}
        self.URI = 'system/vlans/*/macs?count&filter=selected:true'
        # Get the initial MAC Addresses count on the switch.
        initial_mac_addresses_count = self.get_resource_count()
        self.agent.variables['resource_count_value'] = str(
            initial_mac_addresses_count)

    def create_monitors(self):
        self.monitors['mac_decrease'] = Monitor(
            URI_PREFIX_MONITOR + self.URI, 'MAC Address count monitor')
        return list(self.monitors.values())

    def create_rules(self):
        self.rules['mac_rate_decrease'] = Rule(
            'Rate of decrease of MAC addresses count on the switch')
        self.rules['mac_rate_decrease'].condition(
            'every {} minutes', [self.agent.params['time_interval_mac']])
        self.rules['mac_rate_decrease'].action(self.calculate_decrease_rate)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['mac_decrease'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("MAC decrease rate"),
                  dashboard_display=False)
        return list(self.graphs.values())

    def calculate_decrease_rate(self, event):
        rule_description = event['rule_description']
        previous_count_value = int(
            self.agent.variables['resource_count_value'])
        current_count_value = self.get_resource_count()
        count_decrease = previous_count_value - current_count_value
        decrease_rate = (count_decrease / int(str(self.agent.params[
            'time_interval_mac'])))
        self.agent.variables['resource_count_value'] = str(current_count_value)
        self.update_alert_level(
            rule_description, decrease_rate, previous_count_value)

    def update_alert_level(
            self,
            rule_description,
            decrease_rate,
            previous_count_value):
        if decrease_rate < 0:
            return

        if decrease_rate == 0:
            rule_alert_level = self.alm.get_rule_alert_level(
                self.name, rule_description)
            decrease_percentage = 0
            if rule_alert_level == 'NONE':
                return
        else:
            decrease_percentage = (
                decrease_rate /
                float(previous_count_value) *
                100)

        if decrease_percentage > int(str(
                self.agent.params['rate_of_decrease_threshold'])):
            message = 'The rate of decrease of the MAC addresses on ' \
                'the switch which is {} is greater than the ' \
                'threshold value ' \
                'of {}'.format(str(decrease_percentage), str(
                    self.agent.params['rate_of_decrease_threshold']))
            self.agent.logger.info(message)
            self.agent.action_custom_report(message)
            self.alm.publish_alert_level(
                self.name, rule_description, 'CRITICAL')
        else:
            message = 'The rate of decrease of the MAC addresses on ' \
                      'the switch which is {} is lesser than the ' \
                      'threshold value ' \
                      'of {}'.format(str(decrease_percentage), str(
                          self.agent.params['rate_of_decrease_threshold']))
            self.agent.logger.info(message)
            self.agent.action_custom_report(message)
            self.alm.publish_alert_level(self.name, rule_description, 'NONE')

    def get_resource_count(self):
        count = 0
        try:
            uri = HTTP_ADDRESS + URI_PREFIX_GET + self.URI
            r = self.agent.get_rest_request_json(uri)
            count = r["count"]
        except Exception as e:
            self.agent.logger.debug("Error while making REST call to URI "
                                    "{} : {}".format(uri, str(e)))
            self.agent.logger.error("Error while making REST call to URI "
                                    "{}".format(uri))
        return count


class DaemonResource:
    def __init__(self, agent, alm):
        self.name = self.__class__.__name__
        self.agent = agent
        self.alm = alm
        self.monitors = {}
        self.rules = {}
        self.graphs = {}
        self.agent.variables['high_cpu_daemons'] = ''
        self.agent.variables['high_memory_daemons'] = ''
        self.cpu_uri = URI_PREFIX_MONITOR + 'system/subsystems/*/*/daemons/{}?' \
            'attributes=resource_utilization.cpu&filter=name:{}'
        self.mem_uri = URI_PREFIX_MONITOR + 'system/subsystems/*/*/daemons/{}?' \
            'attributes=resource_utilization.memory&filter=name:{}'

    def create_monitors(self):
        for i in range(1, 5):
            daemon_name_var = 'daemon_' + str(i)
            daemon_name = self.agent.params[daemon_name_var].value
            daemon_name = daemon_name.strip()
            if not daemon_name:
                continue

            cpu_mon = "monitor_daemon_" + str(i) + "_cpu"
            mem_mon = "monitor_daemon_" + str(i) + "_mem"
            self.monitors[cpu_mon] = Monitor(
                self.cpu_uri, daemon_name_var +
                ' CPU (CPU/Memory utilization in %)',
                [self.agent.params[daemon_name_var], self.agent.params[daemon_name_var]])
            self.monitors[mem_mon] = Monitor(
                self.mem_uri, daemon_name_var +
                ' Memory (CPU/Memory utilization in %)',
                [self.agent.params[daemon_name_var], self.agent.params[daemon_name_var]])
        return list(self.monitors.values())

    def create_rules(self):
        for i in range(1, 5):
            daemon_name_var = 'daemon_' + str(i)
            daemon_name = self.agent.params[daemon_name_var].value
            daemon_name = daemon_name.strip()
            if not daemon_name:
                continue

            cpu_mon = "monitor_daemon_" + str(i) + "_cpu"
            cpu_rule = "high_cpu_daemon" + str(i)
            self.rules[cpu_rule] = Rule(
                'High CPU utilization by {}', [self.agent.params[daemon_name_var]])
            self.rules[cpu_rule].condition(
                '{} >= {} for {} seconds',
                [self.monitors[cpu_mon],
                 self.agent.params['cpu_threshold'],
                 self.agent.params['time_interval']])
            self.rules[cpu_rule].action(self.action_high_cpu)
            self.rules[cpu_rule].clear_condition('{} < {} for {} seconds',
                                                 [self.monitors[cpu_mon],
                                                  self.agent.params['cpu_threshold'],
                                                  self.agent.params['time_interval']])
            self.rules[cpu_rule].clear_action(self.action_normal_cpu)

            mem_mon = "monitor_daemon_" + str(i) + "_mem"
            mem_rule = "high_mem_daemon_" + str(i)
            self.rules[mem_rule] = Rule(
                'High Memory utilization by {}', [self.agent.params[daemon_name_var]])
            self.rules[mem_rule].condition(
                '{} >= {} for {} seconds',
                [self.monitors[mem_mon],
                 self.agent.params['memory_threshold'],
                 self.agent.params['time_interval']])
            self.rules[mem_rule].action(self.action_high_memory)
            self.rules[mem_rule].clear_condition(
                '{} < {} for {} seconds',
                [self.monitors[mem_mon],
                 self.agent.params['memory_threshold'],
                 self.agent.params['time_interval']])
            self.rules[mem_rule].clear_action(self.action_normal_memory)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['daemon_resource'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("Daemon Resource Monitor"),
                  dashboard_display=False)
        return list(self.graphs.values())

    def action_high_cpu(self, event):
        rule_description = event['rule_description']
        self.agent.logger.debug("======= HIGH CPU ============")
        label = event['labels']
        self.agent.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.agent.logger.debug('daemon - ' + daemon)
        high_cpu_daemons = self.agent.variables['high_cpu_daemons']
        self.agent.logger.debug(
            'high_cpu_daemons before: [' + high_cpu_daemons + ']')
        if daemon not in high_cpu_daemons:
            high_cpu_daemons = high_cpu_daemons + daemon
            self.agent.variables['high_cpu_daemons'] = high_cpu_daemons
            self.agent.action_syslog(
                'High CPU utilization by daemon ' + daemon)
            self.agent.action_cli(
                'show system resource-utilization daemon ' + daemon)
            self.alm.publish_alert_level(
                self.name, rule_description, 'CRITICAL')
        self.agent.logger.debug(
            'high_cpu_daemons after: [' + high_cpu_daemons + ']')
        self.agent.logger.debug("======= /HIGH CPU ===========")

    def action_normal_cpu(self, event):
        rule_description = event['rule_description']
        self.agent.logger.debug("======= Normal CPU =========")
        label = event['labels']
        self.agent.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.agent.logger.debug('daemon - ' + daemon)
        high_cpu_daemons = self.agent.variables['high_cpu_daemons']
        self.agent.logger.debug(
            'high_cpu_daemons before: [' + high_cpu_daemons + ']')
        if daemon in high_cpu_daemons:
            high_cpu_daemons = high_cpu_daemons.replace(daemon, '')
            self.agent.variables['high_cpu_daemons'] = high_cpu_daemons
            self.agent.action_syslog(
                'CPU utilization back to Normal for daemon ' + daemon)
            self.alm.publish_alert_level(
                self.name, rule_description, 'NONE')
        self.agent.logger.debug(
            'high_cpu_daemons after: [' + high_cpu_daemons + ']')
        self.agent.logger.debug("========= /Normal CPU ========")

    def action_high_memory(self, event):
        rule_description = event['rule_description']
        self.agent.logger.debug("======= High Memory ============")
        label = event['labels']
        self.agent.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.agent.logger.debug('daemon - ' + daemon)
        high_memory_daemons = self.agent.variables['high_memory_daemons']
        self.agent.logger.debug(
            'high_memory_daemons before: [' + high_memory_daemons + ']')
        if daemon not in high_memory_daemons:
            high_memory_daemons = high_memory_daemons + daemon
            self.agent.variables['high_memory_daemons'] = high_memory_daemons
            self.agent.action_syslog(
                'High Memory utilization by daemon ' + daemon)
            self.agent.action_cli(
                'show system resource-utilization daemon ' + daemon)
            self.alm.publish_alert_level(
                self.name, rule_description, 'CRITICAL')
        self.agent.logger.debug(
            'high_memory_daemons after: [' + high_memory_daemons + ']')
        self.agent.logger.debug("======= /High Memory ===========")

    def action_normal_memory(self, event):
        rule_description = event['rule_description']
        self.agent.logger.debug("======= Normal Memory =========")
        label = event['labels']
        self.agent.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.agent.logger.debug('daemon - ' + daemon)
        high_memory_daemons = self.agent.variables['high_memory_daemons']
        self.agent.logger.debug(
            'high_memory_daemons before: [' + high_memory_daemons + ']')
        if daemon in high_memory_daemons:
            high_memory_daemons = high_memory_daemons.replace(daemon, '')
            self.agent.variables['high_memory_daemons'] = high_memory_daemons
            self.agent.action_syslog(
                'Memory utilization back to Normal for daemon ' +
                daemon)
            self.alm.publish_alert_level(
                self.name, rule_description, 'NONE')
        self.agent.logger.debug(
            'high_memory_daemons after: [' + high_memory_daemons + ']')
        self.agent.logger.debug("========= /Normal Memory ========")


class FaultFinder:
    INFINITY = float("inf")

    def __init__(self, agent, alm):
        self.name = self.__class__.__name__
        self.agent = agent
        self.alm = alm
        self.monitors = {}
        self.rules = {}
        self.graphs = {}
        self.agent.variables['links_with_alert'] = ''

    def create_monitors(self):
        # Broadcast packets
        uri1 = URI_PREFIX_MONITOR + 'system/interfaces/*?attributes=statistics.if_hc_in_broadcast_packets' + \
            '&filter=type:system'
        broadcast_uri = Rate(uri1, '60 seconds')
        self.monitors['fault_finder1'] = Monitor(
            broadcast_uri, 'Rate of interface broadcast packets (packets/s)')

        # Over bandwidth
        uri5 = URI_PREFIX_MONITOR + 'system/interfaces/*?attributes=statistics.tx_dropped' + \
            '&filter=type:system'
        tx_drop_uri = Rate(uri5, '20 seconds')
        self.monitors['fault_finder5'] = Monitor(
            tx_drop_uri, 'Rate of tx drop packets (packets/s)')
        # Good frames(tx_no_errors)
        uri6 = URI_PREFIX_MONITOR + 'system/interfaces/*?attributes=statistics.ethernet_stats_tx_no_errors' + \
            '&filter=type:system'
        good_frames_uri_tx = Rate(uri6, '20 seconds')
        self.monitors['fault_finder6'] = Monitor(
            good_frames_uri_tx, 'Rate of interface tx good frames (packets/s)')
        return list(self.monitors.values())

    def create_rules(self):
        self.rules['broadcast_storm_fault'] = Rule('Broadcast storm fault')
        self.rules['broadcast_storm_fault'].condition(
            '{} >= {}', [
                self.monitors['fault_finder1'], self.agent.params['broadcast_threshold']])
        self.rules['broadcast_storm_fault'].action(
            self.action_broadcast_sensitivity)
        self.rules['broadcast_storm_fault'].clear_condition(
            '{} < {}', [
                self.monitors['fault_finder1'], self.agent.params['broadcast_threshold']])
        self.rules['broadcast_storm_fault'].clear_action(
            self.action_clear_broadcast_sensitivity)

        self.rules['over_bandwidth_fault'] = Rule('Over bandwidth fault')
        self.rules['over_bandwidth_fault'].condition(
            'ratio of {} and {} >= {}', [self.monitors['fault_finder5'], self.monitors['fault_finder6'],
                                         self.agent.params['tx_drops_threshold']])
        self.rules['over_bandwidth_fault'].action(
            self.action_over_bandwidth_sensitivity)
        self.rules['over_bandwidth_fault'].clear_condition(
            'ratio of {} and {} < {}', [self.monitors['fault_finder5'], self.monitors['fault_finder6'],
                                        self.agent.params['tx_drops_threshold']])
        self.rules['over_bandwidth_fault'].clear_action(
            self.action_clear_over_bandwidth_sensitivity)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['fault_finder'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("Fault Finder - S/W"),
                  dashboard_display=False)
        return list(self.graphs.values())

    def get_interface(self, event):
        label = event['labels']
        first = '='
        last = ',TimeInterval'
        try:
            start = label.index(first) + len(first)
            end = label.index(last, start)
            return label[start:end]
        except ValueError:
            return ""

    def action_broadcast_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['broadcast_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value >= threshold_value >= Thresholds["broadcast_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["broadcast_medium"] <= threshold_value < Thresholds["broadcast_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["broadcast_high"] <= threshold_value < Thresholds["broadcast_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_broadcast_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['broadcast_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def action_over_bandwidth_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['tx_drops_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["tx_drop_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["tx_drop_medium"] <= threshold_value < Thresholds["tx_drop_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["tx_drop_high"] <= threshold_value < Thresholds["tx_drop_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_over_bandwidth_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['tx_drops_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def action_high_sensitivity(self, event, value):
        interface_id = self.get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.agent.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        self.agent.action_syslog(
            '{} detected on interface {} at high sensitivity level: rate at {} packets/sec'.format(
                rule_description, interface_id, value))
        self.agent.action_cli("show interface {}".format(
            interface_id))
        self.agent.action_cli(
            "show interface {} extended".format(interface_id))
        self.alm.publish_alert_level(self.name, rule_description, 'MINOR')

    def action_medium_sensitivity(self, event, value):
        interface_id = self.get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.agent.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        self.agent.action_syslog(
            '{} detected on interface {} at medium sensitivity level: rate at {} packets/sec'.format(
                rule_description, interface_id, value))
        self.agent.action_cli("show interface {}".format(
            interface_id))
        self.agent.action_cli(
            "show interface {} extended".format(interface_id))
        self.alm.publish_alert_level(self.name, rule_description, 'MAJOR')

    def action_low_sensitivity(self, event, value):
        interface_id = self.get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.agent.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        self.agent.action_syslog(
            '{} detected on interface {} at low sensitivity level: rate at {} packets/sec'.format(
                rule_description, interface_id, value))
        self.agent.action_cli("show interface {}".format(
            interface_id))
        self.agent.action_cli(
            "show interface {} extended".format(interface_id))
        self.alm.publish_alert_level(self.name, rule_description, 'CRITICAL')

    def clear_alert_level(self, event):
        interface_id = self.get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.agent.variables['links_with_alert']
        interface = interface_id + ':'
        if interface in links_with_alert:
            self.agent.action_syslog(
                '{} on interface {} is back to normal'.format(
                    rule_description, interface_id))
            self.alm.publish_alert_level(
                self.name, rule_description, 'NONE')

    def add_interface_to_alert_list(self, interface_id):
        links_with_alert = self.agent.variables['links_with_alert'] + \
            interface_id + ':'
        self.agent.variables['links_with_alert'] = links_with_alert


class VSXHealth:
    def __init__(self, agent, alm):
        self.name = self.__class__.__name__
        self.agent = agent
        self.alm = alm
        self.monitors = {}
        self.rules = {}
        self.graphs = {}

        self.VSX_PEER = '/vsx-peer'
        self.RESOURCE_URI_MAP = {
            'routes': 'system/vrfs/*/routes?count',
            'neighbors': 'system/vrfs/*/neighbors?count',
            'mac_addresses': 'system/vlans/*/macs?count&filter=selected:true'}
        self.agent.variables['routes_ratio'] = 'Normal'
        self.agent.variables['neighbors_ratio'] = 'Normal'
        self.agent.variables['mac_addresses_ratio'] = 'Normal'

    def create_monitors(self):
        for mon in self.RESOURCE_URI_MAP:
            uri = URI_PREFIX_MONITOR + self.RESOURCE_URI_MAP[mon]
            switch_var = mon + '_switch'
            vsx_var = mon + '_vsx'
            self.monitors[switch_var] = Monitor(
                uri, '{} count monitor'.format(mon))
            self.monitors[vsx_var] = Monitor(
                self.VSX_PEER + uri, '{} count on VSX peer' ' monitor'.format(mon))
        return list(self.monitors.values())

    def create_rules(self):
        for rule in self.RESOURCE_URI_MAP:
            switch_var = rule + '_switch'
            vsx_var = rule + '_vsx'
            switch_monitor = self.monitors[switch_var]
            vsx_peer_monitor = self.monitors[vsx_var]
            upper_threshold_rule = 'upper_threshold_rule' + rule
            # Calculate the allowed deviation range.
            lower_key = '{}_count_ratio_lower_threshold'.format(rule)
            upper_key = '{}_count_ratio_upper_threshold'.format(rule)
            self.rules[upper_threshold_rule] = Rule(
                'Ratio of {} on the switch to VSX'
                '-peer rule'.format(rule))
            self.rules[upper_threshold_rule].condition(
                'ratio of {} and {} > {}',
                [switch_monitor, vsx_peer_monitor, self.agent.params[upper_key]])

            self.rules[upper_threshold_rule].action(self.critical_action)
            self.rules[upper_threshold_rule].clear_condition(
                'ratio of {} and {} < {}',
                [switch_monitor, vsx_peer_monitor, self.agent.params[upper_key]])

            self.rules[upper_threshold_rule].clear_action(self.normal_action)

            # Rule to alert if the NAE Monitor value goes below the lower
            # threshold value
            lower_threshold_rule = 'lower_threshold_rule' + rule
            self.rules[lower_threshold_rule] = Rule(
                'Ratio of {} on the switch to VSX'
                '-peer rule'.format(rule))
            self.rules[lower_threshold_rule].condition(
                'ratio of {} and {} < {}',
                [switch_monitor, vsx_peer_monitor, self.agent.params[lower_key]])
            self.rules[lower_threshold_rule].action(self.critical_action)
            self.rules[lower_threshold_rule].clear_condition(
                'ratio of {} and {} > {}',
                [switch_monitor, vsx_peer_monitor, self.agent.params[lower_key]])
            self.rules[lower_threshold_rule].clear_action(self.normal_action)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['vsx_monitor'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("VSX Health Monitor"),
                  dashboard_display=False)
        return list(self.graphs.values())

    def critical_action(self, event):
        self.process_event(event, AlertLevel.CRITICAL)

    def normal_action(self, event):
        self.process_event(event, 'Normal')

    def process_event(self, event, alert_level):
        rule_description = event['rule_description']
        if 'mac_addresses' in rule_description:
            resource = 'mac_addresses'
        elif 'neighbors' in rule_description:
            resource = 'neighbors'
        elif 'routes' in rule_description:
            resource = 'routes'
        else:
            self.agent.logger.error(
                "Error while getting resource name from event")
            return

        count_values = self.get_count_values(resource)

        if ('count' in count_values) and ('vsx-peer-count' in count_values):
            ratio = (count_values['count'] / count_values['vsx-peer-count'])
        elif ('count' not in count_values) and ('vsx-peer-count'
                                                in count_values):
            self.agent.logger.error(
                'Could not get {} count on the switch'.format(resource))
            return
        elif ('vsx-peer-count' not in count_values) and (
                'count' in count_values):
            self.agent.logger.error(
                'Could not get {} count on the VSX-peer'
                ' switch'.format(resource))
            return
        else:
            self.agent.logger.error(
                'Could not get {} count on both, the switch and on the'
                'VSX-peer switch'.format(resource))
            return

        valid_alert = self.validate_alert(
            ratio, resource, alert_level)

        if not valid_alert:
            return

        self.update_variables(resource, alert_level)
        self.generate_alert_message(
            resource, ratio, count_values)
        self.update_alert_level(rule_description)

    def validate_alert(self, ratio, resource, alert_level):

        variable_map_key = '{}_ratio'.format(resource)
        if variable_map_key in self.agent.variables:
            if self.agent.variables[variable_map_key] == alert_level:
                return False
        else:
            self.agent.logger.error(
                'Unable to access NAE variable containing alert status'
                'for resource {}'.format(resource))
            return False

        key = '{}_count_ratio_upper_threshold'.format(resource)

        if key in self.agent.params:
            upper_threshold_value = float(self.agent.params[key].value)
        else:
            self.agent.logger.error("Error while getting upper"
                                    "threshold for {} count".format(resource))
            return False

        key = '{}_count_ratio_lower_threshold'.format(resource)
        if key in self.agent.params:
            lower_threshold_value = float(self.agent.params[key].value)
        else:
            self.agent.logger.error("Error while getting lower"
                                    "threshold for {} count".format(resource))
            return False

        if (alert_level == AlertLevel.CRITICAL) and (
                (ratio > upper_threshold_value) or (
                    ratio < lower_threshold_value)):
            return True
        elif (alert_level == 'Normal') and ((ratio < upper_threshold_value)
                                            and (ratio > lower_threshold_value)):
            return True
        else:
            return False

    def update_variables(self, resource, alert_level):
        if alert_level == AlertLevel.CRITICAL:
            self.agent.variables['{}_ratio'.format(
                resource)] = AlertLevel.CRITICAL
        else:
            self.agent.variables['{}_ratio'.format(resource)] = 'Normal'

    def generate_alert_message(self, resource, ratio, count_values):
        variable_map_key = '{}_ratio'.format(resource)
        if variable_map_key in self.agent.variables:
            if self.agent.variables[variable_map_key] == AlertLevel.CRITICAL:
                range_position = 'outside'
            else:
                range_position = 'inside'
        else:
            self.agent.logger.error(
                'Unable to access NAE variable containing alert status'
                'for resource {}'.format(resource))
            return
        if resource == 'mac_addresses':
            resource = 'MAC addresses'

        ratio_value = ' The ratio of {} count on the switch to the ' \
            '{} count on the VSX-peer ' \
            'is {:.3f} which is {} the allowed deviation '.format(
                resource, resource, ratio, range_position)
        self.agent.logger.info(ratio_value)

        self.agent.action_custom_report(ratio_value)

        switch_count = 'The count of {} on the switch is {}'.format(
            resource, count_values['count'])
        self.agent.logger.info(switch_count)
        self.agent.action_custom_report(switch_count)

        vsx_peer_count = 'The count of {} on the VSX-peer switch is {}'.format(
            resource, count_values['vsx-peer-count'])
        self.agent.logger.info(vsx_peer_count)
        self.agent.action_custom_report(vsx_peer_count)

        self.agent.action_cli('show vsx brief')

    def update_alert_level(self, rule_description):
        """
        Updates the NAE Agent alert level based on the status of the NAE Rules
        for routes count, neighbors count and MAC addresses count.
        """
        routes_ratio = self.agent.variables['routes_ratio']
        neighbors_ratio = self.agent.variables['neighbors_ratio']
        mac_addresses_ratio = self.agent.variables['mac_addresses_ratio']

        if (neighbors_ratio == AlertLevel.CRITICAL or mac_addresses_ratio ==
                AlertLevel.CRITICAL) and (self.agent.get_alert_level() != AlertLevel.CRITICAL):
            self.alm.publish_alert_level(
                self.name, rule_description, 'CRITICAL')
        elif (neighbors_ratio == 'Normal' and mac_addresses_ratio == 'Normal'
              and routes_ratio == AlertLevel.CRITICAL) and \
                (self.agent.get_alert_level() != AlertLevel.CRITICAL):
            self.alm.publish_alert_level(self.name, rule_description, 'MINOR')
        elif (neighbors_ratio == 'Normal' and mac_addresses_ratio == 'Normal'
              and routes_ratio == 'Normal'):
            self.agent.remove_alert_level()
        elif (routes_ratio == 'Normal' or mac_addresses_ratio == 'Normal') and \
                (self.agent.get_alert_level() == AlertLevel.CRITICAL):
            self.alm.publish_alert_level(
                self.name, rule_description, 'Normal')

    def get_count_values(self, resource):
        """
        Get the count values for the resource on the switch and the VSX-peer
        :param resource: Resource for which the count values need to be
        obtained.
        """
        count_values = {}
        rest_uri = URI_PREFIX_GET + self.RESOURCE_URI_MAP[resource]
        vsx_rest_uri = self.VSX_PEER + rest_uri
        try:
            r = self.agent.get_rest_request_json(HTTP_ADDRESS + rest_uri)
            count = r["count"]
            count_values["count"] = count
        except Exception as e:
            self.agent.logger.debug("Error while making REST call to URI "
                                    "{} : {}".format(rest_uri, str(e)))
            self.agent.logger.error("Error while making REST call to URI "
                                    "{}".format(rest_uri))

        try:
            r = self.agent.get_rest_request_json(HTTP_ADDRESS + vsx_rest_uri)
            count = r["count"]
            count_values["vsx-peer-count"] = count
        except Exception as e:
            self.agent.logger.debug("Error while making REST call to URI "
                                    "{} : {}".format(vsx_rest_uri, str(e)))
            self.agent.logger.error("Error while making REST call to URI "
                                    "{}".format(vsx_rest_uri))
        return count_values


class AlertManager:
    def __init__(self, agent):
        self.agent = agent

    def get_rule_alert_level(self, metric_desc, rule_desc):
        if 'metrics' not in self.agent.variables.keys():
            return 'NONE'

        metrics = dict(ast.literal_eval(self.agent.variables['metrics']))

        if metric_desc not in metrics.keys():
            return 'NONE'

        if rule_desc not in metrics[metric_desc].keys():
            return 'NONE'

        return metrics[metric_desc][rule_desc]

    def publish_alert_level(self, metric_desc, rule_desc, level):
        if 'metrics' not in self.agent.variables.keys():
            metrics = {}
            self.agent.variables['metrics'] = str(metrics)
        else:
            metrics = dict(ast.literal_eval(self.agent.variables['metrics']))

        if metric_desc not in metrics.keys():
            metrics[metric_desc] = {}
        metrics[metric_desc][rule_desc] = level
        self.agent.variables['metrics'] = str(metrics)
        levels = []

        if level == 'CRITICAL':
            for metric, rules in metrics.items():
                for rule in rules:
                    if self.agent.get_alert_level() != AlertLevel.CRITICAL:
                        if metric == metric_desc:
                            self.agent.logger.debug(metric + " CRITICAL")
                        self.agent.logger.debug(
                            "setting CRITICAL alert level")
                        self.agent.set_alert_level(AlertLevel.CRITICAL)
        elif level == 'MAJOR':
            for metric, rules in metrics.items():
                for rule in rules:
                    if rules[rule] == 'CRITICAL':
                        if self.agent.get_alert_level() != AlertLevel.CRITICAL:
                            self.agent.set_alert_level(AlertLevel.CRITICAL)
                    else:
                        if not (self.agent.get_alert_level() == AlertLevel.CRITICAL
                                or self.agent.get_alert_level() == AlertLevel.MAJOR):
                            if metric == metric_desc:
                                self.agent.logger.debug(metric + " MAJOR")
                            self.agent.logger.debug(
                                "setting MAJOR alert level")
                            self.agent.set_alert_level(AlertLevel.MAJOR)
        elif level == 'MINOR':
            for metric, rules in metrics.items():
                for rule in rules:
                    if rules[rule] == 'CRITICAL':
                        if self.agent.get_alert_level() != AlertLevel.CRITICAL:
                            self.agent.set_alert_level(AlertLevel.CRITICAL)
                    elif rules[rule] == 'MAJOR':
                        if not (self.agent.get_alert_level() == AlertLevel.CRITICAL
                                or self.agent.get_alert_level() == AlertLevel.MAJOR):
                            self.agent.set_alert_level(AlertLevel.MAJOR)
                    elif rules[rule] == 'MINOR':
                        if not (self.agent.get_alert_level() == AlertLevel.CRITICAL
                                or self.agent.get_alert_level() == AlertLevel.MAJOR
                                or self.agent.get_alert_level() == AlertLevel.MINOR):
                            if metric == metric_desc:
                                self.agent.logger.debug(metric + " MINOR")
                            self.agent.logger.debug(
                                "setting MINOR alert level")
                            self.agent.set_alert_level(AlertLevel.MINOR)
        elif level == 'NONE':
            for metric, rules in metrics.items():
                for rule in rules:
                    levels.append(rules[rule])
                    if rules[rule] == 'CRITICAL':
                        if self.agent.get_alert_level() != AlertLevel.CRITICAL:
                            self.agent.set_alert_level(AlertLevel.CRITICAL)
                    elif rules[rule] == 'MAJOR':
                        if not (self.agent.get_alert_level() == AlertLevel.CRITICAL
                                or self.agent.get_alert_level() == AlertLevel.MAJOR):
                            self.agent.set_alert_level(AlertLevel.MAJOR)
                    elif rules[rule] == 'MINOR':
                        if not (self.agent.get_alert_level() == AlertLevel.CRITICAL
                                or self.agent.get_alert_level() == AlertLevel.MAJOR
                                or self.agent.get_alert_level() == AlertLevel.MINOR):
                            self.agent.set_alert_level(AlertLevel.MINOR)
            # Remove alert level if all sub-scripts are normal
            if levels.count('NONE') == len(levels):
                self.agent.logger.debug("removing alert level")
                self.agent.remove_alert_level()


class Agent(NAE):
    def __init__(self):
        alm = AlertManager(self)
        self.mac_count = MACCount(self, alm)
        self.mac_decrease = MACDecreaseRate(self, alm)
        self.daemon_resource = DaemonResource(self, alm)
        self.fault_finder = FaultFinder(self, alm)
        self.vsx_health = VSXHealth(self, alm)

        self.__merge(self.mac_count)
        self.__merge(self.mac_decrease)
        self.__merge(self.daemon_resource)
        self.__merge(self.fault_finder)
        self.__merge(self.vsx_health)

    def __merge(self, script):
        self.__merge_monitors(script.create_monitors())
        self.__merge_rules(script.create_rules())
        self.__merge_graphs(script.create_graphs())

    def __merge_monitors(self, monitors):
        for i, _ in enumerate(monitors):
            id = uuid.uuid4().hex
            mon = 'monitor_{}'.format(id)
            setattr(self, mon, monitors[i])
        return monitors

    def __merge_rules(self, rules):
        for i, _ in enumerate(rules):
            id = uuid.uuid4().hex
            rule = 'rule_{}'.format(id)
            setattr(self, rule, rules[i])
        return rules

    def __merge_graphs(self, graphs):
        for i, _ in enumerate(graphs):
            id = uuid.uuid4().hex
            graph = 'graph_{}'.format(id)
            setattr(self, graph, graphs[i])
        return graphs

    # Classwise wrapper methods to trigger callback actions
    def action_syslog(self, metric_args):
        ActionSyslog(metric_args, severity=SYSLOG_WARNING)

    def action_cli(self, metric_args):
        ActionCLI(metric_args)

    def action_custom_report(self, metric_args):
        ActionCustomReport(metric_args)

    def set_alert_action(self, event):
        self.mac_count.set_alert_action(event)

    def clear_alert_action(self, event):
        self.mac_count.clear_alert_action(event)

    def calculate_decrease_rate(self, event):
        self.mac_decrease.calculate_decrease_rate(event)

    def action_high_cpu(self, event):
        self.daemon_resource.action_high_cpu(event)

    def action_normal_cpu(self, event):
        self.daemon_resource.action_normal_cpu(event)

    def action_high_memory(self, event):
        self.daemon_resource.action_high_memory(event)

    def action_normal_memory(self, event):
        self.daemon_resource.action_normal_memory(event)

    def action_broadcast_sensitivity(self, event):
        self.fault_finder.action_broadcast_sensitivity(event)

    def action_clear_broadcast_sensitivity(self, event):
        self.fault_finder.action_clear_broadcast_sensitivity(
            event)

    def action_over_bandwidth_sensitivity(self, event):
        self.fault_finder.action_over_bandwidth_sensitivity(event)

    def action_clear_over_bandwidth_sensitivity(self, event):
        self.fault_finder.action_clear_over_bandwidth_sensitivity(event)

    def critical_action(self, event):
        self.vsx_health.critical_action(event)

    def normal_action(self, event):
        self.vsx_health.normal_action(event)
