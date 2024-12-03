# -*- coding: utf-8 -*-
#
# (c) Copyright 2021-2024 Hewlett Packard Enterprise Development LP
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

#               --  VSF Health functionality  --
# The overall goal of this script is to monitor vsf events and generate some,
# helpful cli/shell output from the appropriate moment of the event.
#
# Agents derived from this script will monitor these areas:
# 1. VSF Status
#   - monitor status changes
#   - alert if
#     - VSF status changes to unassigned, version_mismatch, not_present, booting,
#       stack_split and ready
#     - show vsf - shows the information of the stack with mac address
# 2. VSF Role
#   - monitor role changes
#   - alert if
#     - VSF role changes to standby, member, unassigned.
#     - show vsf - shows the information of the stack with mac address
# 3. CPU and Memory usage
#   - monitor cpu and memory utilization monitoring
#   - alert if
#     - CPU and Memory utilization exceeds the threshold value
#     - top cpu - will give the information of the cpu utilization
#     - top memory - memory utilization
# 4. VSF Topology
#   - monitor topology type
#   - alert if
#     - Topology changes from ring to chain
#     - Topology change to standalone in case of stack_split
#     - show vsf - show the information of the stack with mac address
#     - show vsf topology - shows the topology diagram of the stack
# 5. VSF Stack split status
#   - monitor stack_split_status change
#   - alert if
#     - stack_split_state is active_fragment,inactive_fragment or no_split
#     - show vsf - shows the information of the stack with mac address and stack_split_state
# 6. VSF Operational status
#   - monitor operational status of links from vsf_link table
#   - alert if
#     - link status goes down or up
#     - show vsf - shows the information of the stack with mac address and stack_split_state
#     - show vsf link - shows the information of vsf link and its status

LONG_DESCRIPTION = '''\
## Script Description

The overall goal of this script is to monitor vsf events and generate some helpful cli/shell output from the appropriate moment of the event.

Agents derived from this script will monitor these areas:

1. VSF Status
    - monitor status changes
    - alert if
        - VSF status changes to unassigned, version_mismatch, not_present, booting, stack_split and ready
        - show vsf - shows the information of the stack with mac address
2. VSF Role
    - monitor role changes
    - alert if
        - VSF role changes to standby, member, unassigned.
        - show vsf - shows the information of the stack with mac address
3. CPU and Memory usage
    - monitor cpu and memory utilization monitoring
    - alert if
        - CPU and Memory utilization exceeds the threshold value
        - top cpu - will give the information of the cpu utilization
        - top memory - memory utilization
4. VSF Topology
    - monitor topology type
    - alert if
        - Topology changes from ring to chain\
        - Topology change to standalone in case of stack_split
        - show vsf - show the information of the stack with mac address
        - show vsf topology - shows the topology diagram of the stack
5. VSF Stack split status
    - monitor stack_split_status change
    - alert if
        - stack_split_state is active_fragment,inactive_fragment or no_split
        - show vsf - shows the information of the stack with mac address and stack_split_state
'''

import math
import requests
import json
from time import (sleep, clock_gettime, CLOCK_PROCESS_CPUTIME_ID)
from datetime import datetime

Manifest = {
    'Name': 'vsf_health_monitor',
    'Description': 'This script monitors the role, status, cpu and memory usage,'
                   ' stack_split_state and topology type of VSF Stack',
    'AOSCXVersionMin': '10.13.1000',
    'AOSCXPlatformList': ['6200', '6300'],
    'Version': '3.0',
    'Author': 'HPE Aruba Networking'
}


ParameterDefinitions = {
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
    }

}

DPRINT = False
VSF = "VSF"
NORMAL = "Normal"


def dprint(*args):
    if DPRINT:
        print(args)


class Agent(NAE):

    def __init__(self):

        # url for status column from vsf_member table
        uri = '/rest/v1/system/vsf_members?attributes=status'
        self.m1 = Monitor(uri, "Status")

        # url for role column from vsf_member table
        uri_role = '/rest/v1/system/vsf_members?attributes=role'
        self.m2 = Monitor(uri_role, "Role")

        # url for vsf_status column from system table
        uri_topology = '/rest/v1/system?attributes=vsf_status.topology_type'
        self.m5 = Monitor(uri_topology, "Topology type")

        uri_stacksplit_state = '/rest/v1/system?attributes=vsf_status.stack_split_state'
        self.m6 = Monitor(uri_stacksplit_state, "Stack split state")

        # url for oper_status column for vsf_link table
        uri_operational_status = '/rest/v1/system/vsf_members/*/links/*?attributes=oper_status'
        self.m7 = Monitor(uri_operational_status, "Operational status")

        # url for cpu usage
        param_list = []
        cpu_uri = '/rest/v1/system/subsystems/management_module/*?attributes=resource_utilization.cpu'

        # url for memory usage
        memory_uri = '/rest/v1/system/subsystems/management_module/*?attributes=resource_utilization.memory'

        # Monitor the changes for  status column from vsf member table
        self.rule_not_present = Rule(
            'Status - system in not_present state')
        self.rule_not_present.condition('{} == "not_present"', [self.m1])
        self.rule_not_present.action(self.action_vsf_status)

        self.rule_booting = Rule(
            'Status - system in booting state')
        self.rule_booting.condition('{} == "booting"', [self.m1])
        self.rule_booting.action(self.action_vsf_status)

        self.rule_ready_state = Rule(
            'Status - system in ready state')
        self.rule_ready_state.condition('{} == "ready"',
                                        [self.m1])
        self.rule_ready_state.action(self.action_vsf_status)

        self.rule_version = Rule(
            'Status changed to version_mismatch')
        self.rule_version.condition('{} == "version_mismatch"',
                                    [self.m1])
        self.rule_version.action(self.action_vsf_status)

        self.rule_com_fail = Rule(
            'Status changed to communication_failure')
        self.rule_com_fail.condition(
            '{} == "communication_failure"', [self.m1])
        self.rule_com_fail.action(self.action_vsf_status)

        self.rule_iof = Rule(
            'Status changed to in_other_fragment')
        self.rule_iof.condition('{} == "in_other_fragment"', [self.m1])
        self.rule_iof.action(self.action_vsf_status)

        # Monitor the changes for role column from vsf member table
        self.rule_mem = Rule(
            'Role change from unassigned to member')
        self.rule_mem.condition('transition {} from "unassigned" to "member"',
                                [self.m2])
        self.rule_mem.action(self.action_vsf_role)

        self.rule_standby = Rule(
            'Role change from unassigned to standby')
        self.rule_standby.condition('transition {} from "unassigned" to "standby"',
                                    [self.m2])
        self.rule_standby.action(self.action_vsf_role)

        self.rule_conductor = Rule(
            'Role change from unassigned to conductor')
        self.rule_conductor.condition('transition {} from "unassigned" to "conductor"',
                                      [self.m2])
        self.rule_conductor.action(self.action_vsf_role)

        self.rule_to_unassigned = Rule('Role transitioned to unassigned')
        self.rule_to_unassigned.condition('{} == "unassigned"',
                                          [self.m2])
        self.rule_to_unassigned.action(self.action_vsf_role)

        # monitor the changes for topology type of stack
        self.rule_topo_standalone = Rule("Topology changed to standalone")
        self.rule_topo_standalone.condition('{} == "standalone"',
                                            [self.m5])
        self.rule_topo_standalone.action(self.action_vsf_topology)

        self.rule_ring = Rule("Topology changed to ring")
        self.rule_ring.condition('{} == "ring"',
                                 [self.m5])
        self.rule_ring.action(self.action_vsf_topology)

        self.rule_chain = Rule("Topology changed to chain")
        self.rule_chain.condition(
            '{} == "chain"', [self.m5])
        self.rule_chain.action(self.action_vsf_topology)

        # monitor the changes for stack_split_state of stack
        self.rule_stack_split = Rule(
            "Stack split state to fragment_active")
        self.rule_stack_split.condition('{} == "fragment_active"',
                                        [self.m6])
        self.rule_stack_split.action(self.action_stacksplit_state)

        self.rule_inactive_frag = Rule(
            "Stack split state to fragment_inactive")
        self.rule_inactive_frag.condition('{} == "fragment_inactive"',
                                          [self.m6])
        self.rule_inactive_frag.action(self.action_stacksplit_state)

        self.rule_no_split = Rule(
            "Transition from fragment_active to no_split")
        self.rule_no_split.condition(
            'transition {} from "fragment_active" to "no_split"', [self.m6])
        self.rule_no_split.action(self.action_stacksplit_state)

        # monitor the changes for operational_status of vsf_link in stack
        self.rule_operational_status = Rule(
            "Transition of operational_status to down")
        self.rule_operational_status.condition('{} == "down"',
                                               [self.m7])
        self.rule_operational_status.action(self.action_operational_status)

        self.rule_operational_status_up = Rule(
            "Transition of operational_status to up")
        self.rule_operational_status_up.condition('{} == "up"',
                                                  [self.m7])
        self.rule_operational_status_up.action(self.action_operational_status)

        # cpu Monitors
        self.mm1_cpu_mon = Monitor(
            cpu_uri,
            'CPU raw (CPU/Memory utilization in %)',
            param_list)

        medium_term_time_period = str(
            self.params['medium_term_time_period'].value) + ' minutes'

        self.rule_high_cpu = Rule('Medium-Term High CPU')
        mm1_medium_term_cpu_uri = AverageOverTime(
            cpu_uri, medium_term_time_period, param_list)
        self.mm_medium_term_cpu_mon = \
            Monitor(mm1_medium_term_cpu_uri,
                    'Medium-Term CPU (CPU/Memory utilization in %)')
        self.rule_high_cpu.condition(
            '{} > {}',
            [self.mm_medium_term_cpu_mon,
             self.params['medium_term_high_threshold']])
        self.rule_high_cpu.action(self.action_major_cpu)

        self.rule_normal_cpu = Rule('Medium-Term Normal CPU')
        self.rule_normal_cpu.condition(
            '{} < {}',
            [self.mm_medium_term_cpu_mon,
             self.params['medium_term_normal_threshold']])
        self.rule_normal_cpu.action(self.action_cpu_normal_major)

        # memory monitors
        self.mm1_mem_mon = Monitor(
            memory_uri,
            'Memory raw (CPU/Memory utilization in %)',
            param_list)

        self.rule_high_memory = Rule('Medium-Term High Memory')
        mm1_medium_term_mem_uri = AverageOverTime(
            memory_uri, medium_term_time_period, param_list)
        self.mm_medium_term_mem_mon = Monitor(mm1_medium_term_mem_uri,
                                              'Medium-Term Memory (CPU/Memory utilization in %)')
        self.rule_high_memory.condition(
            '{} > {}',
            [self.mm_medium_term_mem_mon,
             self.params['medium_term_high_threshold']])
        self.rule_high_memory.action(self.action_major_memory)

        self.rule_normal_memory = Rule('Medium-Term Normal Memory')
        self.rule_normal_memory.condition(
            '{} < {}',
            [self.mm_medium_term_mem_mon,
             self.params['medium_term_normal_threshold']])
        self.rule_normal_memory.action(self.action_memory_normal_major)

        # Graph for status, role, cpu memory, topo, stack_split
        title1 = Title("VSF Status")
        self.graph_status = Graph([self.m1],
                                  title=title1, dashboard_display=True)

        title2 = Title("VSF Role")
        self.graph_role = Graph([self.m2], title=title2)

        title = Title("Average CPU over time")
        self.graph_memory = Graph([self.mm_medium_term_cpu_mon], title=title)

        title3 = Title("Average Memory over time")
        self.graph_cpu = Graph([self.mm_medium_term_mem_mon], title=title3)

        title4 = Title("CPU raw")
        self.graph_cpu_raw = Graph([self.mm1_cpu_mon], title=title4)

        title5 = Title("Memory raw")
        self.graph_mem_raw = Graph([self.mm1_mem_mon], title=title5)

        title6 = Title("VSF Topology")
        self.graph_topo = Graph([self.m5], title=title6)

        title7 = Title("VSF Stack split state")
        self.graph_stacksplit = Graph([self.m6], title=title7)

        # variables
        # normal = 0, minor = 1, major = 2, critical = 3
        if 'status_major' not in self.variables.keys():
            self.variables['status_major'] = '0'
        if 'role_major' not in self.variables.keys():
            self.variables['role_major'] = '0'
        if 'stack_split' not in self.variables.keys():
            self.variables['stack_split'] = '0'
        if 'topo_alert' not in self.variables.keys():
            self.variables['topo_alert'] = '0'
        if 'operationalstatus' not in self.variables.keys():
            self.variables['operationalstatus'] = '0'
        if 'cpu_status' not in self.variables.keys():
            self.variables['cpu_status'] = '0'
        if 'memory_status' not in self.variables.keys():
            self.variables['memory_status'] = '0'
        if 'overall_status' not in self.variables.keys():
            self.variables['overall_status'] = '0'

        self.init_alert_description({VSF: NORMAL})

    def action_vsf_status(self, event):
        self.logger.debug("================ STATUS ================")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        status = event['value']
        ActionSyslog('Status value from db: ' + status)
        _, member_id = label.split(',')[0].split('=')
        self.logger.debug('member_id - ' + member_id)
        message = 'VSF Member ' + member_id + ' status changed to ' + status
        ActionSyslog(message)
        ActionCLI("show vsf")

        if status == "booting" or status == "not_present" or status == "in_other_fragment":
            self.variables['status_major'] = '2'

        elif status == "communication_failure" or status == "version_mismatch":
            self.variables['status_major'] = '3'

        else:
            self.variables['status_major'] = '0'
            message = NORMAL
            if self.variables['topo_alert'] == '1':
                self.variables['topo_alert'] = '0'

        self.set_alert_description_for_key(VSF, message)
        self.set_agent_alert_level()

    def action_vsf_role(self, event):
        self.logger.debug("================ ROLE ================")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, member_id = label.split(',')[0].split('=')
        role = event['value']
        message = 'VSF Member ' + member_id + ' role ' + role
        ActionSyslog(message)
        self.logger.debug('member_id - ' + member_id)
        if member_id == 1:
            if role == "unassigned" or role == "member":
                message = 'VSF Member ' + member_id + ' role changed to ' + role
                ActionSyslog(message)
                ActionCLI("show vsf member " + member_id)

                self.set_alert_level(AlertLevel.MAJOR)
        else:
            if role == "unassigned":
                message = 'VSF Member ' + member_id + ' role changed to ' + role
                ActionSyslog(message)
                ActionCLI("show vsf")
                self.variables['role_major'] = '2'
                self.set_agent_alert_level()

            else:
                self.variables['role_major'] = '0'
                message = NORMAL
                self.set_agent_alert_level()

        self.set_alert_description_for_key(VSF, message)

    def parse_utilization(self, event, method):
        rule_name = event['rule_description']
        utilization = str(method(float(event['value'])))
        subsystem = event['labels'].split(',')[0].split('=')[1]
        return rule_name, subsystem, utilization

    def action_major_cpu(self, event):
        cpu_status = int(self.variables['cpu_status'])
        overall_status = int(self.variables['overall_status'])
        if cpu_status < 2 and overall_status <= 2:
            self.variables['cpu_status'] = '2'
            self.action_cpu(
                event,
                self.params['medium_term_high_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()
            self.set_alert_description_for_key(
                VSF, "High system CPU utilization")

    def action_cpu(self, event, threshold, time_period):
        rule_name, subsystem, utilization = \
            self.parse_utilization(event, math.ceil)
        trap_message = '{}. Subsystem {}. CPU utilization {}%.'.format(
                       rule_name, subsystem, utilization)
        member = subsystem.split("/")
        mem_id = member[1]
        ActionSNMP(trap_message)
        ActionSyslog('Average CPU utilization over ' +
                     'last {} minute(s): [' + utilization +
                     '], exceeded threshold: [{}]', [
                         time_period, threshold],
                     severity=SYSLOG_WARNING)
        ActionCLI('top cpu display-limit 30')
        ActionCLI('show system resource-utilization member ' + mem_id)
        ActionCLI('show copp-policy statistics')

    def action_cpu_normal_major(self, event):
        cpu_status = int(self.variables['cpu_status'])
        if cpu_status == 2:
            self.variables['cpu_status'] = '0'
            self.action_cpu_normal(
                event,
                self.params['medium_term_normal_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()
            self.clear_alert_description_for_key(VSF)

    def action_cpu_normal(self, event, threshold, time_period):
        rule_name, subsystem, utilization = \
            self.parse_utilization(event, math.floor)
        trap_message = '{}. Subsystem {}. CPU utilization {}%.'.format(
                       rule_name, subsystem, utilization)
        ActionSNMP(trap_message)
        ActionSyslog('Average  CPU utilization over ' +
                     'last {} minute(s): [' + utilization +
                     '], is below normal threshold: [{}]',
                     [time_period, threshold], severity=SYSLOG_WARNING)

    def set_agent_alert_level(self):
        overall_list = []
        overall_status = 0

        overall_list = [
            int(alert) for key, alert in self.variables.items() if key != "overall_status"]
        overall_status = max(overall_list)

        self.variables['overall_status'] = str(overall_status)
        if overall_status == 3:
            self.set_alert_level(AlertLevel.CRITICAL)
        elif overall_status == 2:
            self.set_alert_level(AlertLevel.MAJOR)
        elif overall_status == 1:
            self.set_alert_level(AlertLevel.MINOR)
        elif self.get_alert_level is not None:
            self.clear_alert_description_for_key(VSF)
            self.remove_alert_level()

    def action_major_memory(self, event):
        memory_status = int(self.variables['memory_status'])
        overall_status = int(self.variables['overall_status'])
        if memory_status < 2 and overall_status <= 2:
            self.variables['memory_status'] = '2'
            self.action_memory(
                event,
                self.params['medium_term_high_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()
            self.set_alert_description_for_key(
                VSF, "High system memory utilization")

    def action_memory(self, event, threshold, time_period):
        rule_name, subsystem, utilization = \
            self.parse_utilization(event, math.ceil)
        trap_message = '{}. Subsystem {}. Memory utilization {}%.'.format(
                       rule_name, subsystem, utilization)
        ActionSNMP(trap_message)
        member = subsystem.split("/")
        mem_id = member[1]
        ActionSyslog(
            'Average Memory utilization over last ' +
            '{} minute(s): [' + utilization +
            '], exceeded threshold: [{}]',
            [time_period, threshold], severity=SYSLOG_WARNING)
        ActionCLI('top memory display-limit 30')
        ActionCLI('show system resource-utilization member ' + mem_id)
        ActionCLI('show copp-policy statistics')

    def action_memory_normal_major(self, event):
        memory_status = int(self.variables['memory_status'])
        if memory_status == 2:
            self.variables['memory_status'] = '0'
            self.action_memory_normal(
                event,
                self.params['medium_term_normal_threshold'],
                self.params['medium_term_time_period'])
            self.set_agent_alert_level()
            self.clear_alert_description_for_key(VSF)

    def action_memory_normal(self, event, threshold, time_period):
        rule_name, subsystem, utilization = \
            self.parse_utilization(event, math.floor)
        trap_message = '{}. Subsystem {}. Memory utilization {}%.'.format(
                       rule_name, subsystem, utilization)
        ActionSNMP(trap_message)
        ActionSyslog(
            'Average Memory utilization over last {} ' +
            'minute(s): [' + utilization +
            '], is below normal threshold: [{}]', [
                time_period, threshold],
            severity=SYSLOG_WARNING)

    # function to alert whenever topology changes from ring to chain
    def action_vsf_topology(self, event):
        self.logger.debug("================ TOPOLOGY =============")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        topo_type = event['value']
        message = 'Topology type: {}'.format(topo_type)
        ActionSyslog(message)
        ActionCLI("show vsf")
        ActionCLI("show vsf topology")
        ActionCLI("show vsf link")
        ActionCLI("show vsf link detail")

        if topo_type == "chain" or topo_type == "standalone":
            self.variables['topo_alert'] = '1'
            self.set_agent_alert_level()

        else:
            self.variables['topo_alert'] = '0'
            message = NORMAL
            self.set_agent_alert_level()

        self.set_alert_description_for_key(VSF, message)

    # function to report stack_split_state when it is active or inactive fragment
    def action_stacksplit_state(self, event):
        self.logger.debug("================ STACK SPLIT STATE =============")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        stack_split_state = event['value']
        message = 'Stack split state {}'.format(stack_split_state)
        ActionSyslog(message)
        ActionCLI("show vsf")
        ActionCLI("show vsf link")
        ActionCLI("show vsf link detail")

        if stack_split_state == "fragment_active" or stack_split_state == "fragment_inactive":
            self.variables['stack_split'] = '2'
        else:
            message = NORMAL
            self.variables['stack_split'] = '0'
        self.set_agent_alert_level()
        self.set_alert_description_for_key(VSF, message)

    # function to report vsf_link oper_status when it is up or down
    def action_operational_status(self, event):
        self.logger.debug("================ OPER STATUS =============")
        operational_status = event['value']
        message = 'Operational status {}'.format(operational_status)
        ActionSyslog(message)
        ActionCLI("show vsf")
        ActionCLI("show vsf link")
        ActionCLI("show vsf link detail")

        if operational_status == "down":
            self.variables['operationalstatus'] = '2'
        else:
            self.variables['operationalstatus'] = '0'
            message = NORMAL
        self.set_agent_alert_level()
        self.set_alert_description_for_key(VSF, message)
