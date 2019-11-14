# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2019 Hewlett Packard Enterprise Development LP
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
import math

Manifest = {
    'Name': 'system_resource_monitor',
    'Description': 'System Resource (CPU/Memory) Monitoring agent',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'short_term_high_threshold': {
        'Name': 'Average CPU/Memory utilization in percentage '
                'in a short period of offence to set Minor alert',
        'Description': 'When average CPU/Memory utilization exceeds '
                       'this value, agent status will be set to Minor '
                       'and agent will log all system daemons '
                       'CPU/Memory utilization details with CoPP statistics',
        'Type': 'integer',
        'Default': 90
    },
    'short_term_normal_threshold': {
        'Name': 'Average CPU/Memory utilization in percentage in '
                'a short period of offence to unset Minor alert',
        'Description': 'When average CPU/Memory utilization is below '
                       'this value, Minor status will be unset.',
        'Type': 'integer',
        'Default': 80
    },
    'short_term_time_period': {
        'Name': 'Time interval in minutes to consider average CPU/Memory '
                'utilization for Short Term thresholds',
        'Description': 'Time interval to consider average CPU/Memory '
                       'utilization for Short Term thresholds',
        'Type': 'integer',
        'Default': 5
    },
    'medium_term_high_threshold': {
        'Name': 'Average CPU/Memory utilization in percentage over '
                'a medium period of offence to set Major alert.',
        'Description': 'When average CPU/Memory utilization exceeds '
                       'this value, agent status will be set to Major '
                       'and agent will log all system daemons '
                       'CPU/Memory utilization details with CoPP statistics.',
        'Type': 'integer',
        'Default': 80
    },
    'medium_term_normal_threshold': {
        'Name': 'Average CPU/Memory utilization in percentage over '
                'a medium period of offence to unset Major alert',
        'Description': 'When average CPU/Memory utilization is below '
                       'this vlaue, Major status will be unset.',
        'Type': 'integer',
        'Default': 60
    },
    'medium_term_time_period': {
        'Name': 'Time interval in minutes to consider average CPU/Memory '
                'utilization for Medium Term thresholds',
        'Description': 'Time interval to consider average CPU/Memory '
                       'utilization for Medium Term thresholds',
        'Type': 'integer',
        'Default': 120
    },
    'long_term_high_threshold': {
        'Name': 'Average CPU/Memory utilization in percentage for '
                'a sustained long period of offence to set Critical alert',
        'Description': 'When average CPU/Memory utilization exceeds '
                       'this value, agent status will be set to Critical '
                       'and agent will log all system daemons '
                       'CPU/Memory utilization details with CoPP statistics.',
        'Type': 'integer',
        'Default': 70
    },
    'long_term_normal_threshold': {
        'Name': 'Average CPU/Memory utilization in percentage for '
                'a sustained long period of offence to unset Critical alert',
        'Description': 'When average CPU/Memory utilization is below '
                       'this value, Critical status will be unset.',
        'Type': 'integer',
        'Default': 60
    },
    'long_term_time_period': {
        'Name': 'Time interval in minutes to consider average CPU/Memory '
                'utilization for Long Term thresholds',
        'Description': 'Time interval to consider average CPU/Memory '
                       'utilization for Long Term thresholds',
        'Type': 'integer',
        'Default': 480
    }
}


class Agent(NAE):

    def __init__(self):

        mm1_cpu_uri = '/rest/v1/system/subsystems/management_module/1%2F1?' \
                      'attributes=resource_utilization.cpu'

        self.mm1_cpu_mon = Monitor(
            mm1_cpu_uri, 'MM1 CPU raw (CPU/Memory utilization in %)')

        short_term_time_period = str(
            self.params['short_term_time_period'].value) + ' minutes'
        medium_term_time_period = str(
            self.params['medium_term_time_period'].value) + ' minutes'
        long_term_time_period = str(
            self.params['long_term_time_period'].value) + ' minutes'

        self.r1 = Rule('Short-Term High CPU (MM1)')
        mm1_short_term_cpu_uri = AverageOverTime(
            mm1_cpu_uri, short_term_time_period)
        self.mm1_short_term_cpu_mon = \
            Monitor(mm1_short_term_cpu_uri,
                    'MM1 Short-Term CPU (CPU/Memory utilization in %)')
        self.r1.condition(
            '{} > {}',
            [self.mm1_short_term_cpu_mon,
             self.params['short_term_high_threshold']])
        self.r1.action(self.action_minor_cpu)

        self.r2 = Rule('Medium-Term High CPU (MM1)')
        mm1_medium_term_cpu_uri = AverageOverTime(
            mm1_cpu_uri, medium_term_time_period)
        self.mm1_medium_term_cpu_mon = \
            Monitor(mm1_medium_term_cpu_uri,
                    'MM1 Medium-Term CPU (CPU/Memory utilization in %)')
        self.r2.condition(
            '{} > {}',
            [self.mm1_medium_term_cpu_mon,
             self.params['medium_term_high_threshold']])
        self.r2.action(self.action_major_cpu)

        self.r3 = Rule('Long-Term High CPU (MM1)')
        mm1_long_term_cpu_uri = AverageOverTime(
            mm1_cpu_uri, long_term_time_period)
        self.mm1_long_term_cpu_mon = \
            Monitor(mm1_long_term_cpu_uri,
                    'MM1 Long-Term CPU (CPU/Memory utilization in %)')
        self.r3.condition(
            '{} > {}',
            [self.mm1_long_term_cpu_mon,
             self.params['long_term_high_threshold']])
        self.r3.action(self.action_critical_cpu)

        self.r4 = Rule('Short-Term Normal CPU (MM1)')
        self.r4.condition(
            '{} < {}',
            [self.mm1_short_term_cpu_mon,
             self.params['short_term_normal_threshold']])
        self.r4.action(self.action_cpu_normal_minor)

        self.r5 = Rule('Medium-Term Normal CPU (MM1)')
        self.r5.condition(
            '{} < {}',
            [self.mm1_medium_term_cpu_mon,
             self.params['medium_term_normal_threshold']])
        self.r5.action(self.action_cpu_normal_major)

        self.r6 = Rule('Long-Term Normal CPU (MM1)')
        self.r6.condition(
            '{} < {}',
            [self.mm1_long_term_cpu_mon,
             self.params['long_term_normal_threshold']])
        self.r6.action(self.action_cpu_normal_critical)

        mm1_mem_uri = '/rest/v1/system/subsystems/management_module/1%2F1?' \
                      'attributes=resource_utilization.memory'
        self.mm1_mem_mon = Monitor(
            mm1_mem_uri, 'MM1 Memory raw (CPU/Memory utilization in %)')

        self.r7 = Rule('Short-Term High Memory (MM1)')
        mm1_short_term_mem_uri = AverageOverTime(
            mm1_mem_uri, short_term_time_period)
        self.mm1_short_term_mem_mon = \
            Monitor(mm1_short_term_mem_uri,
                    'MM1 Short-Term Memory (CPU/Memory utilization in %)')
        self.r7.condition(
            '{} > {}',
            [self.mm1_short_term_mem_mon,
             self.params['short_term_high_threshold']])
        self.r7.action(self.action_minor_memory)

        self.r8 = Rule('Medium-Term High Memory (MM1)')
        mm1_medium_term_mem_uri = AverageOverTime(
            mm1_mem_uri, medium_term_time_period)
        self.mm1_medium_term_mem_mon = \
            Monitor(mm1_medium_term_mem_uri,
                    'MM1 Medium-Term Memory (CPU/Memory utilization in %)')
        self.r8.condition(
            '{} > {}',
            [self.mm1_medium_term_mem_mon,
             self.params['medium_term_high_threshold']])
        self.r8.action(self.action_major_memory)

        self.r9 = Rule('Long-Term High Memory (MM1)')
        mm1_long_term_mem_uri = AverageOverTime(
            mm1_mem_uri, long_term_time_period)
        self.mm1_long_term_mem_mon = \
            Monitor(mm1_long_term_mem_uri,
                    'MM1 Long-Term Memory (CPU/Memory utilization in %)')
        self.r9.condition(
            '{} > {}',
            [self.mm1_long_term_mem_mon,
             self.params['long_term_high_threshold']])
        self.r9.action(self.action_critical_memory)

        self.r10 = Rule('Short-Term Normal Memory (MM1)')
        self.r10.condition(
            '{} < {}',
            [self.mm1_short_term_mem_mon,
             self.params['short_term_normal_threshold']])
        self.r10.action(self.action_memory_normal_minor)

        self.r11 = Rule('Medium-Term Normal Memory (MM1)')
        self.r11.condition(
            '{} < {}',
            [self.mm1_medium_term_mem_mon,
             self.params['medium_term_normal_threshold']])
        self.r11.action(self.action_memory_normal_major)

        self.r12 = Rule('Long-Term Normal Memory (MM1)')
        self.r12.condition(
            '{} < {}',
            [self.mm1_long_term_mem_mon,
             self.params['long_term_normal_threshold']])
        self.r12.action(self.action_memory_normal_critical)

        mm2_cpu_uri = '/rest/v1/system/subsystems/management_module/1%2F2?' \
                      'attributes=resource_utilization.cpu'

        self.mm2_cpu_mon = Monitor(
            mm2_cpu_uri, 'MM2 CPU raw (CPU/Memory utilization in %)')

        self.r13 = Rule('Short-Term High CPU (MM2)')
        mm2_short_term_cpu_uri = AverageOverTime(
            mm2_cpu_uri, short_term_time_period)
        self.mm2_short_term_cpu_mon = \
            Monitor(mm2_short_term_cpu_uri,
                    'MM2 Short-Term CPU (CPU/Memory utilization in %)')
        self.r13.condition(
            '{} > {}',
            [self.mm2_short_term_cpu_mon,
             self.params['short_term_high_threshold']])
        self.r13.action(self.action_minor_cpu)

        self.r14 = Rule('Medium-Term High CPU (MM2)')
        mm2_medium_term_cpu_uri = AverageOverTime(
            mm2_cpu_uri, medium_term_time_period)
        self.mm2_medium_term_cpu_mon = \
            Monitor(mm2_medium_term_cpu_uri,
                    'MM2 Medium-Term CPU (CPU/Memory utilization in %)')
        self.r14.condition(
            '{} > {}',
            [self.mm2_medium_term_cpu_mon,
             self.params['medium_term_high_threshold']])
        self.r14.action(self.action_major_cpu)

        self.r15 = Rule('Long-Term High CPU (MM2)')
        mm2_long_term_cpu_uri = AverageOverTime(
            mm2_cpu_uri, long_term_time_period)
        self.mm2_long_term_cpu_mon = \
            Monitor(mm2_long_term_cpu_uri,
                    'MM2 Long-Term CPU (CPU/Memory utilization in %)')
        self.r15.condition(
            '{} > {}',
            [self.mm2_long_term_cpu_mon,
             self.params['long_term_high_threshold']])
        self.r15.action(self.action_critical_cpu)

        self.r16 = Rule('Short-Term Normal CPU (MM2)')
        self.r16.condition(
            '{} < {}',
            [self.mm2_short_term_cpu_mon,
             self.params['short_term_normal_threshold']])
        self.r16.action(self.action_cpu_normal_minor)

        self.r17 = Rule('Medium-Term Normal CPU (MM2)')
        self.r17.condition(
            '{} < {}',
            [self.mm2_medium_term_cpu_mon,
             self.params['medium_term_normal_threshold']])
        self.r17.action(self.action_cpu_normal_major)

        self.r18 = Rule('Long-Term Normal CPU (MM2)')
        self.r18.condition(
            '{} < {}',
            [self.mm2_long_term_cpu_mon,
             self.params['long_term_normal_threshold']])
        self.r18.action(self.action_cpu_normal_critical)

        mm2_mem_uri = '/rest/v1/system/subsystems/management_module/1%2F2?' \
                      'attributes=resource_utilization.memory'
        self.mm2_mem_mon = Monitor(
            mm2_mem_uri, 'MM2 Memory raw (CPU/Memory utilization in %)')

        self.r19 = Rule('Short-Term High Memory (MM2)')
        mm2_short_term_mem_uri = AverageOverTime(
            mm2_mem_uri, short_term_time_period)
        self.mm2_short_term_mem_mon = \
            Monitor(mm2_short_term_mem_uri,
                    'MM2 Short-Term Memory (CPU/Memory utilization in %)')
        self.r19.condition(
            '{} > {}',
            [self.mm2_short_term_mem_mon,
             self.params['short_term_high_threshold']])
        self.r19.action(self.action_minor_memory)

        self.r20 = Rule('Medium-Term High Memory (MM2)')
        mm2_medium_term_mem_uri = AverageOverTime(
            mm2_mem_uri, medium_term_time_period)
        self.mm2_medium_term_mem_mon = \
            Monitor(mm2_medium_term_mem_uri,
                    'MM2 Medium-Term Memory (CPU/Memory utilization in %)')
        self.r20.condition(
            '{} > {}',
            [self.mm2_medium_term_mem_mon,
             self.params['medium_term_high_threshold']])
        self.r20.action(self.action_major_memory)

        self.r21 = Rule('Long-Term High Memory (MM2)')
        mm2_long_term_mem_uri = AverageOverTime(
            mm2_mem_uri, long_term_time_period)
        self.mm2_long_term_mem_mon = \
            Monitor(mm2_long_term_mem_uri,
                    'MM2 Long-Term Memory (CPU/Memory utilization in %)')
        self.r21.condition(
            '{} > {}',
            [self.mm2_long_term_mem_mon,
             self.params['long_term_high_threshold']])
        self.r21.action(self.action_critical_memory)

        self.r22 = Rule('Short-Term Normal Memory (MM2)')
        self.r22.condition(
            '{} < {}',
            [self.mm2_short_term_mem_mon,
             self.params['short_term_normal_threshold']])
        self.r22.action(self.action_memory_normal_minor)

        self.r23 = Rule('Medium-Term Normal Memory (MM2)')
        self.r23.condition(
            '{} < {}',
            [self.mm2_medium_term_mem_mon,
             self.params['medium_term_normal_threshold']])
        self.r23.action(self.action_memory_normal_major)

        self.r24 = Rule('Long-Term Normal Memory (MM2)')
        self.r24.condition(
            '{} < {}',
            [self.mm2_long_term_mem_mon,
             self.params['long_term_normal_threshold']])
        self.r24.action(self.action_memory_normal_critical)

        mm_status_uri = '/rest/v1/system/redundant_managements/' \
            '*?attributes=mgmt_role'
        self.mm_status_mon = Monitor(mm_status_uri,
                                     'MM status (Management Module status)')
        self.variables['cpu_minor'] = '0'
        self.variables['cpu_major'] = '0'
        self.variables['cpu_critical'] = '0'
        self.variables['memory_minor'] = '0'
        self.variables['memory_major'] = '0'
        self.variables['memory_critical'] = '0'
        # normal = 0, minor = 1, major = 2, critical = 3
        self.variables['cpu_status'] = '0'
        self.variables['memory_status'] = '0'
        self.variables['overall_status'] = '0'

    def action_minor_cpu(self, event):
        self.variables['cpu_minor'] = '1'
        cpu_status = int(self.variables['cpu_status'])
        overall_status = int(self.variables['overall_status'])
        if cpu_status == 0 and overall_status <= 1:
            self.variables['cpu_status'] = '1'
            self.action_cpu(
                event,
                self.params['short_term_high_threshold'],
                self.params['short_term_time_period'])
            self.set_agent_alert_level()

    def action_major_cpu(self, event):
        self.variables['cpu_major'] = '1'
        cpu_status = int(self.variables['cpu_status'])
        overall_status = int(self.variables['overall_status'])
        if cpu_status < 2 and overall_status <= 2:
            self.variables['cpu_status'] = '2'
            self.action_cpu(
                event,
                self.params['medium_term_high_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()

    def action_critical_cpu(self, event):
        self.variables['cpu_critical'] = '1'
        cpu_status = int(self.variables['cpu_status'])
        overall_status = int(self.variables['overall_status'])
        if cpu_status < 3 and overall_status <= 3:
            self.variables['cpu_status'] = '3'
            self.action_cpu(
                event,
                self.params['long_term_high_threshold'],
                self.params['long_term_time_period'])
            self.set_agent_alert_level()

    def action_cpu(self, event, threshold, time_period):
        r_event_value = str(math.ceil(float(event['value'])))
        mgmt_module = self.get_mgmt_module(event['labels'])
        ActionSyslog('Average ' + mgmt_module + ' CPU utilization over ' +
                     'last {} minute(s): [' + r_event_value +
                     '], exceeded threshold: [{}]', [time_period, threshold],
                     severity=SYSLOG_WARNING)
        ActionCLI('top cpu')
        ActionCLI('show system resource-utilization')
        ActionCLI('show copp-policy statistics')

    def action_cpu_normal_minor(self, event):
        self.variables['cpu_minor'] = '0'
        cpu_status = int(self.variables['cpu_status'])
        if cpu_status == 1:
            self.variables['cpu_status'] = '0'
            self.action_cpu_normal(
                event,
                self.params['short_term_normal_threshold'],
                self.params['short_term_time_period'])
            self.set_agent_alert_level()

    def action_cpu_normal_major(self, event):
        self.variables['cpu_major'] = '0'
        cpu_status = int(self.variables['cpu_status'])
        if cpu_status == 2:
            self.variables['cpu_status'] = '0'
            cpu_minor = int(self.variables['cpu_minor'])
            if cpu_minor:
                self.variables['cpu_status'] = '1'
            self.action_cpu_normal(
                event,
                self.params['medium_term_normal_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()

    def action_cpu_normal_critical(self, event):
        self.variables['cpu_critical'] = '0'
        cpu_status = int(self.variables['cpu_status'])
        if cpu_status == 3:
            self.variables['cpu_status'] = '0'
            cpu_major = int(self.variables['cpu_major'])
            cpu_minor = int(self.variables['cpu_minor'])
            if cpu_major:
                self.variables['cpu_status'] = '2'
            elif cpu_minor:
                self.variables['cpu_status'] = '1'
            self.action_cpu_normal(
                event,
                self.params['long_term_normal_threshold'],
                self.params['long_term_time_period'])
            self.set_agent_alert_level()

    def action_cpu_normal(self, event, threshold, time_period):
        r_event_value = str(math.floor(float(event['value'])))
        mgmt_module = self.get_mgmt_module(event['labels'])
        ActionSyslog('Average ' + mgmt_module + ' CPU utilization over ' +
                     'last {} minute(s): [' + r_event_value +
                     '], is below normal threshold: [{}]',
                     [time_period, threshold], severity=SYSLOG_WARNING)

    def set_agent_alert_level(self):
        cpu_status = int(self.variables['cpu_status'])
        memory_status = int(self.variables['memory_status'])
        overall_status = 0
        if cpu_status > memory_status:
            overall_status = cpu_status
        else:
            overall_status = memory_status
        self.variables['overall_status'] = str(overall_status)
        if overall_status == 3:
            self.set_alert_level(AlertLevel.CRITICAL)
        elif overall_status == 2:
            self.set_alert_level(AlertLevel.MAJOR)
        elif overall_status == 1:
            self.set_alert_level(AlertLevel.MINOR)
        else:
            if self.get_alert_level is not None:
                self.remove_alert_level()

    def action_minor_memory(self, event):
        self.variables['memory_minor'] = '1'
        memory_status = int(self.variables['memory_status'])
        overall_status = int(self.variables['overall_status'])
        if memory_status == 0 and overall_status <= 1:
            self.variables['memory_status'] = '1'
            self.action_memory(
                event,
                self.params['short_term_high_threshold'],
                self.params['short_term_time_period'])
            self.set_agent_alert_level()

    def action_major_memory(self, event):
        self.variables['memory_major'] = '1'
        memory_status = int(self.variables['memory_status'])
        overall_status = int(self.variables['overall_status'])
        if memory_status < 2 and overall_status <= 2:
            self.variables['memory_status'] = '2'
            self.action_memory(
                event,
                self.params['medium_term_high_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()

    def action_critical_memory(self, event):
        self.variables['memory_critical'] = '1'
        memory_status = int(self.variables['memory_status'])
        overall_status = int(self.variables['overall_status'])
        if memory_status < 3 and overall_status <= 3:
            self.variables['memory_status'] = '3'
            self.action_memory(
                event,
                self.params['long_term_high_threshold'],
                self.params['long_term_time_period'])
            self.set_agent_alert_level()

    def action_memory(self, event, threshold, time_period):
        r_event_value = str(math.ceil(float(event['value'])))
        mgmt_module = self.get_mgmt_module(event['labels'])
        ActionSyslog(
            'Average ' + mgmt_module + ' Memory utilization over last ' +
            '{} minute(s): [' + r_event_value + '], exceeded threshold: [{}]',
            [time_period, threshold], severity=SYSLOG_WARNING)
        ActionCLI('top memory')
        ActionCLI('show system resource-utilization')
        ActionCLI('show copp-policy statistics')

    def action_memory_normal_minor(self, event):
        self.variables['memory_minor'] = '0'
        memory_status = int(self.variables['memory_status'])
        if memory_status == 1:
            self.variables['memory_status'] = '0'
            self.action_memory_normal(
                event,
                self.params['short_term_normal_threshold'],
                self.params['short_term_time_period'])
            self.set_agent_alert_level()

    def action_memory_normal_major(self, event):
        self.variables['memory_major'] = '0'
        memory_status = int(self.variables['memory_status'])
        if memory_status == 2:
            self.variables['memory_status'] = '0'
            memory_minor = int(self.variables['memory_minor'])
            if memory_minor:
                self.variables['memory_status'] = '1'
            self.action_memory_normal(
                event,
                self.params['medium_term_normal_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()

    def action_memory_normal_critical(self, event):
        self.variables['memory_critical'] = '0'
        memory_status = int(self.variables['memory_status'])
        if memory_status == 3:
            self.variables['memory_status'] = '0'
            memory_major = int(self.variables['memory_major'])
            memory_minor = int(self.variables['memory_minor'])
            if memory_major:
                self.variables['memory_status'] = '2'
            elif memory_minor:
                self.variables['memory_status'] = '1'
            self.action_memory_normal(
                event,
                self.params['long_term_normal_threshold'],
                self.params['long_term_time_period'])
            self.set_agent_alert_level()

    def action_memory_normal(self, event, threshold, time_period):
        r_event_value = str(math.floor(float(event['value'])))
        mgmt_module = self.get_mgmt_module(event['labels'])
        ActionSyslog(
            'Average ' + mgmt_module + 'Memory utilization over last {} ' +
            'minute(s): [' + r_event_value +
            '], is below normal threshold: [{}]', [time_period, threshold],
            severity=SYSLOG_WARNING)

    def get_mgmt_module(self, event_label):
        _, mgmt_module = event_label.split(',')[0].split('=')
        ret_mgmt_module = ''
        if mgmt_module == 'management_module_1/1':
            ret_mgmt_module = 'MM1'
        else:
            ret_mgmt_module = 'MM2'
        return ret_mgmt_module
