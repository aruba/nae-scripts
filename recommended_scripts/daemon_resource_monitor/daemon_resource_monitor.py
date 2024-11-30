# (c) Copyright 2018-2020,2022,2024 Hewlett Packard Enterprise Development LP
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
    - cpu_threshold -  High CPU threshold value in percentage
    - memory_threshold: High Memory threshold value in percentage
    - time_interval: Time interval in seconds to consider CPU/Memory utilization
    - daemon_1: ops-switchd
    - daemon_2: ovsdb-server
    - daemon_3: hpe-routing
    - daemon_4: ndmd

The script defines Monitor Resource URI(s), Monitor condition and Action : 
- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. CPU (CPU/Memory utilization in %)
    2. Memory (CPU/Memory utilization in %)

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Actions:  This script specifies monitoring action as following: 
    - If the CPU/Memory utilization is more than threshold value mentioned in the threshold parameter for a specific time interval, the following actions are executed:
        1. A log message is generated with the high CPU/Memory utilization by daemon.
        2. The agent alert level is updated to Critical.
    - When the CPU/Memory utilization is less than the threshold value for a specific time interval, the following actions are executed. 
        1. The agent alert level is updated to Normal.
        2. A log message is generated with the CPU/Memory utilization back to normal for daemon.
'''

Manifest = {
    'Name': 'daemon_resource_monitor',
    'Description': 'Top 4 System daemon CPU & Memory utilization '
                   'monitoring agent',
    'Version': '4.2',
    'AOSCXVersionMin': '10.04',
    'Author': 'HPE Aruba Networking',
    'AOSCXPlatformList': ['6200', '6300', '64xx', '8320', '8325', '8400']
}

ParameterDefinitions = {
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
    }
}


class Agent(NAE):

    def __init__(self):

        # for loop to set up monitors for each daemon
        for i in range(1, 5):

            daemon_name_var = 'daemon_' + str(i)
            daemon_name = self.params[daemon_name_var].value
            daemon_name = daemon_name.strip()

            if not daemon_name:
                continue

            cpu_monitor_var = 'cpu_monitor' + str(i)
            cpu_uri = '/rest/v1/system/subsystems/*/*/daemons/{}?' \
                      'attributes=resource_utilization.cpu&filter=name:{}'

            # sets up monitor to show CPU utilization for each daemon
            cpu_monitor = Monitor(
                cpu_uri,
                daemon_name_var + ' CPU (CPU/Memory utilization in %)',
                [self.params[daemon_name_var], self.params[daemon_name_var]])
            setattr(self, cpu_monitor_var, cpu_monitor)

            cpu_rule_var = 'cpu_rule' + str(i)
            cpu_rule = Rule('High CPU utilization by {}', [
                            self.params[daemon_name_var]])
            cpu_rule.condition(
                '{} >= {} for {} seconds',
                [cpu_monitor,
                 self.params['cpu_threshold'],
                 self.params['time_interval']])
            cpu_rule.action(self.action_high_cpu)
            cpu_rule.clear_condition('{} < {} for {} seconds',
                                     [cpu_monitor,
                                      self.params['cpu_threshold'],
                                         self.params['time_interval']])
            cpu_rule.clear_action(self.action_normal_cpu)
            setattr(self, cpu_rule_var, cpu_rule)

            # sets up monitor to show Memory utilization for each daemon
            mem_monitor_var = 'mem_monitor' + str(i)
            mem_uri = '/rest/v1/system/subsystems/*/*/daemons/{}?' \
                      'attributes=resource_utilization.memory&filter=name:{}'
            mem_monitor = Monitor(
                mem_uri,
                daemon_name_var + ' Memory (CPU/Memory utilization in %)',
                [self.params[daemon_name_var], self.params[daemon_name_var]])
            setattr(self, mem_monitor_var, mem_monitor)

            mem_rule_var = 'mem_rule' + str(i)
            mem_rule = Rule('High Memory utilization by {}',
                            [self.params[daemon_name_var]])
            mem_rule.condition(
                '{} >= {} for {} seconds',
                [mem_monitor,
                 self.params['memory_threshold'],
                 self.params['time_interval']])
            mem_rule.action(self.action_high_memory)
            mem_rule.clear_condition(
                '{} < {} for {} seconds',
                [mem_monitor,
                 self.params['memory_threshold'],
                 self.params['time_interval']])
            mem_rule.clear_action(self.action_normal_memory)
            setattr(self, mem_rule_var, mem_rule)

            # sets up monitor to show average CPU utilization for each daemon
            cpu_util_monitor_var = 'cpu_util_monitor' + str(i)
            cpu_util_uri = AverageOverTime(
                cpu_uri,
                str(self.params['time_interval'].value) + ' seconds',
                [self.params[daemon_name_var], self.params[daemon_name_var]])
            cpu_util_monitor = Monitor(
                cpu_util_uri, daemon_name_var + ' CPU Average Utilization')
            setattr(self, cpu_util_monitor_var, cpu_util_monitor)

            # sets up monitor to show average mem utilization for each daemon
            mem_util_monitor_var = 'mem_util_monitor' + str(i)
            mem_util_uri = AverageOverTime(
                mem_uri,
                str(self.params['time_interval'].value) + ' seconds',
                [self.params[daemon_name_var], self.params[daemon_name_var]])
            mem_util_monitor = Monitor(
                mem_util_uri, daemon_name_var + ' Memory Average Utilization')
            setattr(self, mem_util_monitor_var, mem_util_monitor)

        # variables
        self.variables['high_cpu_daemons'] = ''
        self.variables['high_memory_daemons'] = ''

    def action_high_cpu(self, event):
        self.logger.debug("======= HIGH CPU ============")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.logger.debug('daemon - ' + daemon)
        high_cpu_daemons = self.variables['high_cpu_daemons']
        self.logger.debug(
            'high_cpu_daemons before: [' +
            high_cpu_daemons +
            ']')
        if daemon not in high_cpu_daemons:
            high_cpu_daemons = high_cpu_daemons + daemon
            self.variables['high_cpu_daemons'] = high_cpu_daemons
            ActionSyslog('High CPU utilization by daemon ' + daemon)
            ActionCLI('show system resource-utilization daemon ' + daemon)
            if self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
        self.logger.debug('high_cpu_daemons after: [' + high_cpu_daemons + ']')
        self.logger.debug("======= /HIGH CPU ===========")

    def action_normal_cpu(self, event):
        self.logger.debug("======= Normal CPU =========")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.logger.debug('daemon - ' + daemon)
        high_cpu_daemons = self.variables['high_cpu_daemons']
        self.logger.debug(
            'high_cpu_daemons before: [' +
            high_cpu_daemons +
            ']')
        if daemon in high_cpu_daemons:
            high_cpu_daemons = high_cpu_daemons.replace(daemon, '')
            self.variables['high_cpu_daemons'] = high_cpu_daemons
            ActionSyslog('CPU utilization back to Normal for daemon ' + daemon)
            high_memory_daemons = self.variables['high_memory_daemons']
            if not high_cpu_daemons and not high_memory_daemons:
                if self.get_alert_level() is not None:
                    self.remove_alert_level()
        self.logger.debug('high_cpu_daemons after: [' + high_cpu_daemons + ']')
        self.logger.debug("========= /Normal CPU ========")

    def action_high_memory(self, event):
        self.logger.debug("======= HIGH Memory ============")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.logger.debug('daemon - ' + daemon)
        high_memory_daemons = self.variables['high_memory_daemons']
        self.logger.debug(
            'high_memory_daemons before: [' +
            high_memory_daemons +
            ']')
        if daemon not in high_memory_daemons:
            high_memory_daemons = high_memory_daemons + daemon
            self.variables['high_memory_daemons'] = high_memory_daemons
            ActionSyslog('High Memory utilization by daemon ' + daemon)
            ActionCLI('show system resource-utilization daemon ' + daemon)
            if self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
        self.logger.debug(
            'high_memory_daemons after: [' +
            high_memory_daemons +
            ']')
        self.logger.debug("======= /HIGH CPU ===========")

    def action_normal_memory(self, event):
        self.logger.debug("======= Normal CPU =========")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, daemon = label.split(',')[0].split('=')
        self.logger.debug('daemon - ' + daemon)
        high_memory_daemons = self.variables['high_memory_daemons']
        self.logger.debug(
            'high_memory_daemons before: [' +
            high_memory_daemons +
            ']')
        if daemon in high_memory_daemons:
            high_memory_daemons = high_memory_daemons.replace(daemon, '')
            self.variables['high_memory_daemons'] = high_memory_daemons
            ActionSyslog(
                'Memory utilization back to Normal for daemon ' +
                daemon)
            high_cpu_daemons = self.variables['high_cpu_daemons']
            if not high_memory_daemons and not high_cpu_daemons:
                if self.get_alert_level() is not None:
                    self.remove_alert_level()
        self.logger.debug(
            'high_memory_daemons after: [' +
            high_memory_daemons +
            ']')
        self.logger.debug("========= /Normal CPU ========")

    def on_parameter_change(self, params):
        # Callback to report invalid parameter values set after agent creation

        dameon_name_params = (
            'daemon_1',
            'daemon_2',
            'daemon_3',
            'daemon_4')

        self.logger.debug("======== Parameter Change ========")
        high_memory_daemons = self.variables['high_memory_daemons']
        high_cpu_daemons = self.variables['high_cpu_daemons']

        for name, value in params.items():
            if name in dameon_name_params:
                old = value['old']
                new = value['new']
                self.logger.debug("param {} changes from {} to {}".format(
                    name, old, new))

                if old in high_memory_daemons:
                    self.logger.debug(
                        "remove {} from "
                        "local_storage[high_memory_daemons]".format(old))
                    high_memory_daemons = high_memory_daemons.replace(old, '')
                    self.variables['high_memory_daemons'] = high_memory_daemons

                if old in high_cpu_daemons:
                    self.logger.debug(
                        "remove {} from "
                        "local_storage[high_cpu_daemons]".format(old))
                    high_cpu_daemons = high_cpu_daemons.replace(old, '')
                    self.variables['high_cpu_daemons'] = high_cpu_daemons

        if not high_memory_daemons and not high_cpu_daemons:
            self.logger.debug("All clear. Adjust alert level")
            if self.get_alert_level() is not None:
                self.remove_alert_level()

        self.logger.debug("======== /Parameter Change ========")
