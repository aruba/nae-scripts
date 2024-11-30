# -*- coding: utf-8 -*-
#
# (c) Copyright 2019-2020,2024 Hewlett Packard Enterprise Development LP
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
## Script Description

The main components of the script are Manifest, Parameter Definitions and python code. 
- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - rx_crc_err_threshold: Threshold for bad cable fault
    - ethernet_fragments_threshold: Threshold for bad transceiver fault
- Monitors:  This script specifies the monitoring URI(s) to monitor the following: 
    - Temperature sensor status
    - Fan Status
    - Rate of interface good frames (packets/s)
    - Rate of Rx CRC error packets (packets/s)
    - Rate of ethernet stats fragments error packets (packets/s)
- Actions:  This script performs the following actions:
    - For temperature sensor, When the specific Condition is met a detailed Syslog message indicating the transition states and output of CLI command  ('show system temperature') is displayed  in the Alert Window and the policy Status is  changed as per transition state severities. 
    - The 'Agent Constructor' handles the main logic for monitoring the 'fault' status of all Fans. Conditions are defined such that when there is a transition from one status value to another value, the agent executes a action callback for it. Status values like empty/uninitialized/ok are considered to be normal status of a fan and other states like fault is considered to be critical status value of a fan. A data structure named 'fans_list' is used to list fans which transited to critical status. 
    - When any fan transit from normal status(empty/uninitialized/ok) to critical status(fault), then the callback 'fans_status_action_fault' is invoked.  The variable 'fans_list' is updated with that fan name and set the agent status to 'Critical' along with displaying CLI output for 'show environment fan' as well as syslog which displays the fan name. Upon next fan transit to fault status, the agent displays CLI and syslog with that fan name.   
    - When the fan in faulty status(fault) transit to normal status values(empty/uninitialized/ok), the fan name in 'fans_list' is removed.When all the fans status are set back to any normal status values and 'fans_list' is empty, the agent status is set back to 'Normal'.
    - Fault Finder, when rate of ethernet stats fragments error packets (packets/s) is above the threshold:
        - The agent status is marked as critical & syslog message displayed.
    - When rate of Rx CRC error packets (packets/s) is above the threshold:
        - The agent status is marked as critical & syslog message displayed.
'''

from requests import get
import uuid
import ast

Manifest = {
    'Name': 'hardware_device_health_monitor',
    'Description': 'This script monitors the overall hardware device health.',
    'Version': '1.6',
    'Tags': ['device'],
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.04',
    'AOSCXPlatformList': ['6200', '6300', '64xx', '8100', '8320', '8325', '8360', '8400']
}

ParameterDefinitions = {
    'rx_crc_err_threshold': {
        'Name': 'Threshold for bad cable fault',
        'Description':
            'Threshold for ratio of rate of rx_crc_err packets over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.0036, for medium sensitivity, set is as 0.0021 and for high sensitivity, set it as 0.0006',
        'Type': 'float',
        'Default': 0.0006
    },
    'ethernet_fragments_threshold': {
        'Name': 'Threshold for bad transceiver fault',
        'Description':
            'Threshold for ratio of rate of ethernet_fragments packets over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.045, for medium sensitivity, set is as 0.03 and for high sensitivity, set it as 0.015',
        'Type': 'float',
        'Default': 0.015
    }
}


Thresholds = {
    'rx_crc_err_low': 0.0036, 'rx_crc_err_medium': 0.0021, 'rx_crc_err_high': 0.0006,
    'fragments_low': 0.045, 'fragments_medium': 0.03, 'fragments_high': 0.015
}


class TempSensor:
    def __init__(self, agent, alm):
        self.name = self.__class__.__name__
        self.agent = agent
        self.alm = alm
        self.monitors = {}
        self.rules = {}
        self.graphs = {}
        self.agent.variables['sensors_list'] = ''

    def create_monitors(self):
        uri_temp = '/rest/v1/system/subsystems/*/*/temp_sensors/*?attributes=status'
        self.monitors['temp_sensor'] = Monitor(uri_temp, 'Sensor Status')
        return list(self.monitors.values())

    def create_rules(self):
        self.rules['sensor_uninitialized'] = Rule('Sensor - Uninitialized')
        self.rules['sensor_uninitialized'].condition(
            '{} == "uninitialized"', [self.monitors['temp_sensor']])
        self.rules['sensor_uninitialized'].action(
            self.sensor_action_status_normal)

        self.rules['sensor_normal'] = Rule('Sensor - Normal')
        self.rules['sensor_normal'].condition(
            '{} == "normal"', [self.monitors['temp_sensor']])
        self.rules['sensor_normal'].action(self.sensor_action_status_normal)

        self.rules['sensor_min'] = Rule('Sensor - Min')
        self.rules['sensor_min'].condition(
            '{} == "min"', [self.monitors['temp_sensor']])
        self.rules['sensor_min'].action(self.sensor_action_status_normal)

        self.rules['sensor_max'] = Rule('Sensor - Max')
        self.rules['sensor_max'].condition(
            '{} == "max"', [self.monitors['temp_sensor']])
        self.rules['sensor_max'].action(self.sensor_action_status_normal)

        self.rules['sensor_fault'] = Rule('Sensor - Fault')
        self.rules['sensor_fault'].condition(
            '{} == "fault"', [self.monitors['temp_sensor']])
        self.rules['sensor_fault'].action(self.sensor_action_status_critical)

        self.rules['sensor_low_critical'] = Rule('Sensor - Low_Critical')
        self.rules['sensor_low_critical'].condition(
            '{} == "low_critical"', [self.monitors['temp_sensor']])
        self.rules['sensor_low_critical'].action(
            self.sensor_action_status_critical)

        self.rules['sensor_critical'] = Rule('Sensor - Critical')
        self.rules['sensor_critical'].condition(
            '{} == "critical"', [self.monitors['temp_sensor']])
        self.rules['sensor_critical'].action(
            self.sensor_action_status_critical)

        self.rules['sensor_emergency'] = Rule('Sensor - Emergency')
        self.rules['sensor_emergency'].condition(
            '{} == "emergency"', [self.monitors['temp_sensor']])
        self.rules['sensor_emergency'].action(
            self.sensor_action_status_critical)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['temp_sensor'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("Sensor Status"),
                  dashboard_display=True)
        return list(self.graphs.values())

    def sensor_action_status_critical(self, event):
        self.agent.logger.debug('LABEL = ' + event['labels'])
        label = event['labels']
        rule_description = 'Temp Sensor Status'
        sensorname = label.split(',')[1].split('=')[1]
        self.agent.logger.debug('Sensor Name= ' + sensorname)

        if self.agent.variables['sensors_list'] != '':
            findsensor = self.agent.variables['sensors_list']
            istrue = findsensor.find(sensorname)
            if istrue == -1:
                sensors_list = sensorname + \
                    self.agent.variables['sensors_list']
                self.agent.variables['sensors_list'] = sensors_list
                self.agent.logger.debug('list of sensors:  ' +
                                        self.agent.variables['sensors_list'])
                self.set_actions(sensorname, rule_description)
        else:
            self.agent.variables['sensors_list'] = sensorname
            self.agent.logger.debug('list of sensors:  ' +
                                    self.agent.variables['sensors_list'])
            self.set_actions(sensorname, rule_description)

    def set_actions(self, sensorname, rule_description):
        self.agent.logger.debug("+++ CALLBACK: TEMP SENSOR STATUS - CRITICAL!")
        self.agent.action_syslog(
            'Sensor: ' + sensorname + ' is in Critical State ')
        self.agent.action_cli('show environment temperature')
        self.alm.publish_alert_level(
            self.name, rule_description, 'CRITICAL')

    def sensor_action_status_normal(self, event):
        self.agent.logger.debug('LABEL = ' + event['labels'])
        label = event['labels']
        rule_description = 'Temp Sensor Status'
        sensorname = label.split(',')[1].split('=')[1]

        # delete sensorName which moved to normal state
        index = 0
        length = len(sensorname)
        findsensor = self.agent.variables['sensors_list']
        index = findsensor.find(sensorname)
        if index != -1:
            findsensor = findsensor[0:index] + findsensor[index + length:]
            self.agent.variables['sensors_list'] = findsensor
            self.agent.logger.debug('Sensor name deleted: ' + sensorname)
            self.agent.logger.debug('Current sensors list: ' +
                                    self.agent.variables['sensors_list'])
            self.agent.action_syslog(
                'Sensor ' + sensorname + ' back to normal')
            if self.agent.variables['sensors_list'] == '':
                self.set_agent_status_normal(rule_description)

    def set_agent_status_normal(self, rule_description):
        self.agent.logger.debug("+++ CALLBACK: TEMP SENSOR STATUS - NORMAL!")
        self.agent.action_syslog(
            'All temperature sensors are in normal state')
        self.alm.publish_alert_level(self.name, rule_description, 'NONE')


class Fan:
    def __init__(self, agent, alm):
        self.name = self.__class__.__name__
        self.agent = agent
        self.alm = alm
        self.monitors = {}
        self.rules = {}
        self.graphs = {}
        self.agent.variables['fans_list'] = ''
        self.agent.variables['faulty_fans_count'] = '0'

    def create_monitors(self):
        uri_fan = '/rest/v1/system/subsystems/*/*/fans/*?attributes=status'
        self.monitors['fan'] = Monitor(uri_fan, 'Fan Status')
        return list(self.monitors.values())

    def create_rules(self):
        self.rules['fan_status'] = Rule('Fan Status')
        self.rules['fan_status'].condition(
            '{} == "fault"', [self.monitors['fan']])
        self.rules['fan_status'].action(self.fans_status_action_fault)
        self.rules['fan_status'].clear_condition(
            '{} == "ok"', [self.monitors['fan']])
        self.rules['fan_status'].clear_action(
            self.fans_status_action_normal)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['fan'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("Fan Status"),
                  dashboard_display=False)
        return list(self.graphs.values())

    def fans_status_action_fault(self, event):
        self.agent.logger.debug('LABEL = ' + event['labels'])
        label = event['labels']
        rule_description = event['rule_description']
        fan_name = label.split(',')[0].split('=')[1]

        self.agent.logger.debug('fan_name= ' + fan_name)
        if self.agent.variables['fans_list'] != '':
            fans_list = fan_name + self.agent.variables['fans_list']
            self.agent.variables['fans_list'] = fans_list
        else:
            self.agent.variables['fans_list'] = fan_name
        self.agent.logger.debug('list of fans =  ' +
                                self.agent.variables['fans_list'])
        self.set_fan_actions(fan_name, rule_description)
        self.increment_faulty_fans_count()

    def increment_faulty_fans_count(self):
        faulty_count = int(self.agent.variables['faulty_fans_count'])
        faulty_count = faulty_count + 1
        self.agent.variables['faulty_fans_count'] = str(faulty_count)
        self.agent.action_syslog(
            'Number of faulty fans are : ' + str(faulty_count))

    def set_fan_actions(self, fan_name, rule_description):
        self.agent.logger.debug("+++ CALLBACK: FAN STATUS - FAULT!")
        self.agent.action_syslog('Fan ' + fan_name + ' is Faulty ')
        self.agent.action_cli('show environment fan')
        self.alm.publish_alert_level(
            self.name, rule_description, 'CRITICAL')

    def fans_status_action_normal(self, event):
        self.agent.logger.debug('LABEL = ' + event['labels'])
        label = event['labels']
        rule_description = event['rule_description']
        fan_name = label.split(',')[0].split('=')[1]

        # delete fan_name which moved to ok state
        index = 0
        length = len(fan_name)
        findfan = self.agent.variables['fans_list']
        index = findfan.find(fan_name)
        if index != -1:
            findfan = findfan[0:index] + findfan[index + length:]
            self.agent.variables['fans_list'] = findfan
            self.agent.logger.debug('Fan name deleted ' + fan_name)
            self.agent.logger.debug('Current fans list ' +
                                    self.agent.variables['fans_list'])
            self.agent.action_syslog('Fan ' + fan_name + ' back to ok')
            faulty_count = int(self.agent.variables['faulty_fans_count'])
            faulty_count = faulty_count - 1
            self.agent.variables['faulty_fans_count'] = str(faulty_count)
            if self.agent.variables['faulty_fans_count'] != '0':
                self.agent.action_syslog(
                    'Remaining fans in faulty status are :  ' + str(faulty_count))
            if self.agent.variables['fans_list'] == '':
                self.set_fan_agent_status_normal(rule_description)

    def set_fan_agent_status_normal(self, rule_description):
        self.agent.logger.debug("+++ CALLBACK: FAN STATUS - NORMAL!")
        self.agent.action_syslog('All fans are in normal state')
        self.alm.publish_alert_level(self.name, rule_description, 'NONE')


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
        # Good frames
        uri_ff2 = '/rest/v1/system/interfaces/*?attributes=statistics.ethernet_stats_rx_no_errors' + \
            '&filter=type:system'
        good_frames_uri = Rate(uri_ff2, '20 seconds')
        self.monitors['fault_finder2'] = Monitor(
            good_frames_uri, 'Rate of interface good frames (packets/s)')

        # Rx CRC errors
        uri_ff3 = '/rest/v1/system/interfaces/*?attributes=statistics.rx_crc_err' + \
            '&filter=type:system'
        rx_crc_err_uri = Rate(uri_ff3, '20 seconds')
        self.monitors['fault_finder3'] = Monitor(
            rx_crc_err_uri, 'Rate of Rx CRC error packets (packets/s)')

        # Ethernet stats fragments
        uri_ff4 = '/rest/v1/system/interfaces/*?attributes=statistics.ethernet_stats_fragments' + \
            '&filter=type:system'
        ethernet_stats_fragments_uri = Rate(uri_ff4, '20 seconds')
        self.monitors['fault_finder4'] = Monitor(
            ethernet_stats_fragments_uri, 'Rate of ethernet stats fragments error packets (packets/s)')
        return list(self.monitors.values())

    def create_rules(self):
        self.rules['bad_cable_fault'] = Rule('Bad cable fault')
        self.rules['bad_cable_fault'].condition(
            'ratio of {} and {} >= {}', [self.monitors['fault_finder3'], self.monitors['fault_finder2'],
                                         self.agent.params['rx_crc_err_threshold']])
        self.rules['bad_cable_fault'].action(
            self.action_rx_crc_err_sensitivity)
        self.rules['bad_cable_fault'].clear_condition(
            'ratio of {} and {} < {}', [self.monitors['fault_finder3'], self.monitors['fault_finder2'],
                                        self.agent.params['rx_crc_err_threshold']])
        self.rules['bad_cable_fault'].clear_action(
            self.action_clear_rx_crc_err_sensitivity)

        self.rules['bad_transceiver_fault'] = Rule('Bad transceiver fault')
        self.rules['bad_transceiver_fault'].condition(
            'ratio of {} and {} >= {}', [self.monitors['fault_finder4'], self.monitors['fault_finder2'],
                                         self.agent.params['ethernet_fragments_threshold']])
        self.rules['bad_transceiver_fault'].action(
            self.action_fragments_sensitivity)
        self.rules['bad_transceiver_fault'].clear_condition(
            'ratio of {} and {} < {}', [self.monitors['fault_finder4'], self.monitors['fault_finder2'],
                                        self.agent.params['ethernet_fragments_threshold']])
        self.rules['bad_transceiver_fault'].clear_action(
            self.action_clear_fragments_sensitivity)
        return list(self.rules.values())

    def create_graphs(self):
        self.graphs['fault_finder'] = \
            Graph([val for val in self.monitors.values()],
                  title=Title("Fault Finder - H/W"),
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

    def add_interface_to_alert_list(self, interface_id):
        links_with_alert = self.agent.variables['links_with_alert'] + \
            interface_id + ':'
        self.agent.variables['links_with_alert'] = links_with_alert

    def action_rx_crc_err_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['rx_crc_err_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["rx_crc_err_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["rx_crc_err_medium"] <= threshold_value < Thresholds["rx_crc_err_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["rx_crc_err_high"] <= threshold_value < Thresholds["rx_crc_err_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_rx_crc_err_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['rx_crc_err_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def action_fragments_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['ethernet_fragments_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["fragments_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["fragments_medium"] <= threshold_value < Thresholds["fragments_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["fragments_high"] <= threshold_value < Thresholds["fragments_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_fragments_sensitivity(self, event):
        value = event['value']
        threshold = self.agent.params['ethernet_fragments_threshold'].value
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
        self.agent.action_syslog('{} detected on interface {} at high sensitivity level: rate at {} packets/sec'.format(
            rule_description, interface_id, value))
        self.agent.action_cli("show interface {}".format(
            interface_id))
        self.agent.action_cli(
            "show interface {} extended".format(interface_id))
        self.alm.publish_alert_level(
            self.name, rule_description, 'MINOR')

    def action_medium_sensitivity(self, event, value):
        interface_id = self.get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.agent.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        self.agent.action_syslog('{} detected on interface {} at medium sensitivity level: rate at {} packets/sec'.format(
            rule_description, interface_id, value))
        self.agent.action_cli("show interface {}".format(
            interface_id))
        self.agent.action_cli(
            "show interface {} extended".format(interface_id))
        self.alm.publish_alert_level(
            self.name, rule_description, 'MAJOR')

    def action_low_sensitivity(self, event, value):
        interface_id = self.get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.agent.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        self.agent.action_syslog('{} detected on interface {} at low sensitivity level: rate at {} packets/sec'.format(
            rule_description, interface_id, value))
        self.agent.action_cli("show interface {}".format(
            interface_id))
        self.agent.action_cli(
            "show interface {} extended".format(interface_id))
        self.alm.publish_alert_level(
            self.name, rule_description, 'CRITICAL')

    def clear_alert_level(self, event):
        interface_id = self.get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.agent.variables['links_with_alert']
        interface = interface_id + ':'
        if interface in links_with_alert:
            self.agent.action_syslog('{} on interface {} is back to normal'.format(
                rule_description, interface_id))
            self.alm.publish_alert_level(
                self.name, rule_description, 'NONE')


class AlertManager:
    def __init__(self, agent):
        self.agent = agent

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
                self.agent.logger.debug(
                    "Removing alert level since all metrics are normal")
                self.agent.remove_alert_level()


class Agent(NAE):

    def __init__(self):
        alm = AlertManager(self)
        self.temp_sensor = TempSensor(self, alm)
        self.fan_status = Fan(self, alm)
        self.fault_finder = FaultFinder(self, alm)

        self.__merge(self.temp_sensor)
        self.__merge(self.fan_status)
        self.__merge(self.fault_finder)

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

    def sensor_action_status_normal(self, event):
        self.temp_sensor.sensor_action_status_normal(
            event)

    def sensor_action_status_critical(self, event):
        self.temp_sensor.sensor_action_status_critical(
            event)

    def fans_status_action_normal(self, event):
        self.fan_status.fans_status_action_normal(
            event)

    def fans_status_action_fault(self, event):
        self.fan_status.fans_status_action_fault(
            event)

    def action_rx_crc_err_sensitivity(self, event):
        self.fault_finder.action_rx_crc_err_sensitivity(
            event)

    def action_clear_rx_crc_err_sensitivity(self, event):
        self.fault_finder.action_clear_rx_crc_err_sensitivity(
            event)

    def action_fragments_sensitivity(self, event):
        self.fault_finder.action_fragments_sensitivity(
            event)

    def action_clear_fragments_sensitivity(self, event):
        self.fault_finder.action_clear_fragments_sensitivity(
            event)
