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

Manifest = {
    'Name': 'stp_health_monitor',
    'Description': 'Agent to monitor health of STP port',
    'Version': '1.1',
    'TargetSoftwareVersion': '10.3',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'tcn_upper_threshold': {
        'Name': 'Upper threshold for rate of TCN',
        'Description': 'The abnormal rate of change of topology'
                       'per time (10 sec)',
        'Type': 'integer',
        'Default': 5
    },
    'tcn_lower_threshold': {
        'Name': 'Lower Threshold for rate of TCN',
        'Description': 'The acceptable rate of change of topology'
                       'per time (10 sec)',
        'Type': 'integer',
        'Default': 0
    }
}


class Agent(NAE):

    def __init__(self):
        uri1 = '/rest/v1/system/stp_instances/mstp/*?' \
               'attributes=topology_change_count'
        uri2 = '/rest/v1/system/stp_instances/mstp/*/' \
               'stp_instance_ports/*?attributes=statistics.BPDUs_Tx'
        uri3 = '/rest/v1/system/stp_instances/mstp/*/' \
               'stp_instance_ports/*?attributes=statistics.BPDUs_Rx'
        uri4 = '/rest/v1/system/stp_instances/mstp/*/' \
               'stp_instance_ports/*?attributes=port_role'
        uri5 = '/rest/v1/system/stp_instances/mstp/*/' \
               'stp_instance_ports/*?attributes=port_state'
        uri6 = '/rest/v1/system/stp_instances/mstp/*/' \
               'stp_instance_ports/*?attributes=port_inconsistent.loop_guard'
        uri7 = '/rest/v1/system/stp_instances/mstp/*/' \
               'stp_instance_ports/*?attributes=port_inconsistent.root_guard'
        uri8 = '/rest/v1/system/stp_instances/mstp/*/' \
               'stp_instance_ports/*?attributes=statistics.forward_transition_count'

        rate_m = Rate(uri1, '10 seconds')
        self.m1 = Monitor(
            rate_m, 'Rate of topology change (changes/s)')
        rate_bpdutx = Rate(uri2, '10 seconds')
        self.m2 = Monitor(
            rate_bpdutx, 'Rate of BPDU Tx (BPDUs/s)')
        rate_bpdurx = Rate(uri3, '10 seconds')
        self.m3 = Monitor(
            rate_bpdurx, 'Rate of BPDU Rx (BPDUs/s)')
        self.m4 = Monitor(uri4, 'STP port role (Port role)')
        self.m5 = Monitor(uri5, 'STP port state (Port state)')
        self.m6 = Monitor(
            uri6, 'STP port inconsistent loop guard (Port inconsistent)')
        self.m7 = Monitor(
            uri7, 'STP port inconsistent root guard (Port inconsistent)')
        rate_forward_transition = Rate(uri8, '10 seconds')
        self.m8 = Monitor(rate_forward_transition,
                          'Rate of forward transition change (changes/s)')

        self.r1 = Rule('TCN rate exceeded')
        self.r1.condition('{} > {}', [
            self.m1, self.params['tcn_upper_threshold']])
        self.r1.action(self.topo_change_exceeded)

        self.r2 = Rule('TCN rate normal')
        self.r2.condition('{} <= {}', [
            self.m1, self.params['tcn_lower_threshold']])
        self.r2.action(self.topo_change_normal)

        self.r3 = Rule('Critical combination for Root port role')
        self.r3.condition('{} == "Root"', [self.m4])
        self.r3.action(self.set_port_role)

        self.r4 = Rule('Critical combination for Master port role')
        self.r4.condition('{} == "Master"', [self.m4])
        self.r4.action(self.set_port_role)

        self.r5 = Rule('Critical combination for Alternate port role')
        self.r5.condition('{} == "Alternate"', [self.m4])
        self.r5.action(self.set_port_role)

        self.r6 = Rule('Critical combination for Designated port role')
        self.r6.condition('{} == "Designated"', [self.m4])
        self.r6.action(self.set_port_role)

        self.r7 = Rule('Critical combination for Backup port role')
        self.r7.condition('{} == "Backup"', [self.m4])
        self.r7.action(self.set_port_role)

        self.r8 = Rule('Critical combination for Disabled port role')
        self.r8.condition('{} == "Disabled"', [self.m4])
        self.r8.action(self.set_port_role)

        self.r9 = Rule('Critical combination for Disabled port state')
        self.r9.condition('{} == "Disabled"', [self.m5])
        self.r9.action(self.set_port_state)

        self.r10 = Rule('Critical combination for Blocking port state')
        self.r10.condition('{} == "Blocking"', [self.m5])
        self.r10.action(self.set_port_state)

        self.r11 = Rule('Critical combination for Forwarding port state')
        self.r11.condition('{} == "Forwarding"', [self.m5])
        self.r11.action(self.set_port_state)

        self.r12 = Rule('Critical combination for Learning port state')
        self.r12.condition('{} == "Learning"', [self.m5])
        self.r12.action(self.set_port_state)

        self.r13 = Rule(
            'Critical combination for Port inconsistent loop guard')
        self.r13.condition('{} == 0', [self.m6])
        self.r13.action(self.set_port_inconsistent_loop_guard)

        self.r14 = Rule(
            'Critical combination for Port inconsistent root guard')
        self.r14.condition('{} == 0', [self.m7])
        self.r14.action(self.set_port_inconsistent_root_guard)

        self.r15 = Rule('Critical rate of BPDU Tx')
        self.r15.condition('{} < 0.1', [self.m2])
        self.r15.action(self.set_rate_bpdu_tx)

        self.r16 = Rule('Critical rate of BPDU Rx')
        self.r16.condition('{} < 0.1', [self.m3])
        self.r16.action(self.set_rate_bpdu_rx)

        self.r17 = Rule('Critical rate of forward transition count')
        self.r17.condition('{} > 0', [self.m8])
        self.r17.action(self.set_rate_forward_transition)

        self.r18 = Rule('Valid combination for port inconsistent loop guard')
        self.r18.condition('{} == 1', [self.m6])
        self.r18.action(self.port_inconsistent_loop_guard_true)

        self.r19 = Rule('Normal rate of BPDU Tx')
        self.r19.condition('{} >= 0.1', [self.m2])
        self.r19.action(self.rate_bpdu_tx_normal)

        self.r20 = Rule('Normal rate of BPDU Rx')
        self.r20.condition('{} >= 0.1', [self.m3])
        self.r20.action(self.rate_bpdu_rx_normal)

        self.r21 = Rule('Normal rate of forward transition count')
        self.r21.condition('{} == 0', [self.m8])
        self.r21.action(self.rate_forward_transition_normal)

        self.r22 = Rule('Transition of port state from Learning to Blocking')
        self.r22.condition(
            'transition {} from "Learning" to "Blocking"', [self.m5])
        self.r22.action(self.port_state_learning_to_blocking)

        self.r23 = Rule('Transition of port state from Forwarding to Blocking')
        self.r23.condition(
            'transition {} from "Forwarding" to "Blocking"', [self.m5])
        self.r23.action(self.port_state_forwarding_to_blocking)

        title1 = Title('Port role')
        self.graph_port_role = Graph(
            [self.m4], title=title1, dashboard_display=True)
        title2 = Title('Port state')
        self.graph_port_state = Graph([self.m5], title=title2)
        title3 = Title('Port inconsistent loop/root guard')
        self.graph_port_inconsistent = Graph([self.m6, self.m7], title=title3)
        title4 = Title('Topology and forward transition changes')
        self.graph_topology_change_forward_transition = Graph(
            [self.m1, self.m8], title=title4)
        title5 = Title('BPDU Tx and Rx')
        self.graph_bpdu_rx_tx = Graph(
            [self.m2, self.m3], title=title5)

        self.variables['stp_ports_in_critical_state'] = ''

    def topo_change_exceeded(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.update_critical_list(stp_instance + '_topo_change_exceeded')
        agent_name = get_agent_name(event['monitor_name'])
        self.logger.debug('Agent {} detected that the rate of topology change count has exceeded the '
                          'upper threshold {}, for STP instance {}'.format(agent_name,
                                                                           str(
                                                                               self.params['tcn_upper_threshold']),
                                                                           stp_instance))
        ActionSyslog("Topology change rate exceeded defined max value {}, for STP instance " + stp_instance,
                     [self.params['tcn_upper_threshold']])
        ActionCLI("show spanning-tree detail")
        mstp_instance = stp_instance[stp_instance.find(
            "_")+1:stp_instance.find(",")]
        ActionCLI("show spanning-tree mst {} detail".format(mstp_instance))
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
            self.logger.debug(
                'Agent {} is in critical state'.format(agent_name))

    def topo_change_normal(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.clear_critical_state(stp_instance + '_topo_change_exceeded')
        agent_name = get_agent_name(event['monitor_name'])
        self.logger.debug('Agent {} detected that the rate of topology change count is normal, '
                          'for STP instance {}'.format(agent_name, stp_instance))
        ActionSyslog(
            'Topology change rate is normal for STP instance {}'.format(stp_instance))
        if self.get_alert_level() is not None:
            if not self.variables['stp_ports_in_critical_state']:
                self.remove_alert_level()
                self.logger.debug(
                    'Agent {} is in normal state'.format(agent_name))

    def invalid_port_combinations(self, stp_instance, states, monitor_name):
        self.update_critical_list(stp_instance + '_' + states)
        agent_name = get_agent_name(monitor_name)
        port_role = states.split('_')[0]
        port_state = states.split('_')[1]
        self.logger.debug('Agent {} detected port role {} and port state {}, which is an invalid combination, for STP '
                          'instance {}'.format(agent_name, port_role, port_state, stp_instance))
        ActionSyslog(
            'Invalid combination of port role and port state on STP instance {}'.format(stp_instance))
        ActionCLI("show spanning-tree detail")
        mstp_instance = stp_instance[stp_instance.find(
            "_")+1:stp_instance.find(",")]
        ActionCLI("show spanning-tree mst {} detail".format(mstp_instance))
        ActionCLI("show spanning-tree mst-config")
        ActionCLI("show spanning-tree mst")
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
            self.logger.debug(
                'Agent {} is in critical state'.format(agent_name))

    def starvation(self, stp_instance, direction, monitor_name):
        self.update_critical_list(
            stp_instance + '_' + direction + '_starvation')
        agent_name = get_agent_name(monitor_name)
        self.logger.debug('Agent {} detected MSTP {} starvation for STP instance {}'.format(agent_name, direction,
                                                                                            stp_instance))
        ActionSyslog('MSTP {} starvation on STP instance {}'.format(
            direction, stp_instance))
        ActionCLI("show spanning-tree detail")
        ActionCLI("show spanning-tree mst")
        ActionCLI("show copp statistics")
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
            self.logger.debug(
                'Agent {} is in critical state'.format(agent_name))

    def forward_transition_error(self, stp_instance, monitor_name):
        self.update_critical_list(stp_instance + '_forward_transition_error')
        agent_name = get_agent_name(monitor_name)
        self.logger.debug('Agent {} detected that the rate of forward transition count is greater than zero '
                          'for STP instance {}'.format(agent_name, stp_instance))
        if self.get_alert_level() != AlertLevel.CRITICAL:
            ActionSyslog(
                'Forward transition error on STP instance {}'.format(stp_instance))
            self.set_alert_level(AlertLevel.CRITICAL)
            ActionCLI("show spanning-tree mst detail")
            self.logger.debug(
                'Agent {} is in critical state'.format(agent_name))

    def set_port_role(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        self.variables[state_key + '_port_role'] = event['value']
        port_role = event['value']
        port_state_key = state_key + '_port_state'
        loop_guard_key = state_key + ',map_key=loop_guard'
        rate_bpdu_rx_key = state_key + ',TimeInterval=10s,map_key=BPDUs_Rx'
        rate_bpdu_tx_key = state_key + ',TimeInterval=10s,map_key=BPDUs_Tx'
        rate_forward_transition_key = state_key + \
            ',TimeInterval=10s,map_key=forward_transition_count'
        root_guard_key = state_key + ',map_key=root_guard'
        monitor_name = event['monitor_name']
        if port_state_key in self.variables:
            port_state = self.variables[port_state_key]
            if port_role == "Disabled" and port_state == "Learning":
                self.invalid_port_combinations(
                    state_key, "disabled_learning", monitor_name)
            if port_role == "Disabled" and port_state == "Disabled":
                self.invalid_port_combinations(
                    state_key, "disabled_disabled", monitor_name)
            if port_role == "Disabled" and port_state == "Blocking":
                self.port_combinations_normal(
                    state_key, "disabled_blocking", monitor_name)
            if port_role == "Disabled" and port_state == "Forwarding":
                self.port_combinations_normal(
                    state_key, "disabled_forwarding", monitor_name)
        if port_state_key in self.variables and loop_guard_key in self.variables:
            loop_guard = self.variables[loop_guard_key]
            if port_role == "Root" and port_state == "Disabled" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "root_disabled", monitor_name)
            if port_role == "Root" and port_state == "Blocking" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "root_blocking", monitor_name)
            if port_role == "Master" and port_state == "Disabled" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "master_disabled", monitor_name)
            if port_role == "Master" and port_state == "Blocking" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "master_blocking", monitor_name)
            if port_role == "Alternate" and port_state != "Blocking" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "alternate_blocking", monitor_name)
            if port_role == "Backup" and port_state != "Blocking" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "backup_blocking", monitor_name)
            if port_role == "Root" and port_state == "Forwarding" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "root_forwarding", monitor_name)
            if port_role == "Root" and port_state == "Learning" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "root_learning", monitor_name)
            if port_role == "Master" and port_state == "Forwarding" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "master_forwarding", monitor_name)
            if port_role == "Root" and port_state == "Learning" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "root_learning", monitor_name)
        if port_state_key in self.variables and root_guard_key in self.variables:
            root_guard = self.variables[root_guard_key]
            if port_role == "Designated" and port_state == "Disabled" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_disabled", monitor_name)
            if port_role == "Designated" and port_state == "Blocking" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_blocking", monitor_name)
            if port_role == "Designated" and port_state == "Forwarding" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_forwarding", monitor_name)
            if port_role == "Designated" and port_state == "Learning" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_learning", monitor_name)
        if port_state_key in self.variables and rate_bpdu_rx_key in self.variables:
            rate_bpdu_rx = float(self.variables[rate_bpdu_rx_key])
            if port_role == "Root" and port_state == "Forwarding" and rate_bpdu_rx < 0.1:
                self.starvation(state_key, 'rx', monitor_name)
            if port_role == "Alternate" and port_state == "Blocking" and rate_bpdu_rx < 0.1:
                self.starvation(state_key, 'rx', monitor_name)
            if port_role == "Root" and port_state == "Forwarding" and rate_bpdu_rx >= 0.1:
                self.starvation_normal(state_key, 'rx', monitor_name)
            if port_role == "Alternate" and port_state == "Blocking" and rate_bpdu_rx >= 0.1:
                self.starvation_normal(state_key, 'rx', monitor_name)
        if port_state_key in self.variables and rate_bpdu_tx_key in self.variables:
            rate_bpdu_tx = float(self.variables[rate_bpdu_tx_key])
            if port_role == "Designated" and port_state == "Forwarding" and rate_bpdu_tx < 0.1:
                self.starvation(state_key, 'tx', monitor_name)
            if port_role == "Designated" and port_state == "Forwarding" and rate_bpdu_tx >= 0.1:
                self.starvation_normal(state_key, 'tx', monitor_name)
        if port_state_key in self.variables and rate_forward_transition_key in self.variables:
            rate_forward_transition = float(
                self.variables[rate_forward_transition_key])
            if port_state == "Forwarding" and port_role == "Root" and rate_forward_transition > 0:
                self.forward_transition_error(state_key, monitor_name)
            if port_state == "Forwarding" and port_role == "Designated" and rate_forward_transition > 0:
                self.forward_transition_error(state_key, monitor_name)
            if port_state == "Forwarding" and port_role == "Root" and rate_forward_transition == 0:
                self.forward_transition_normal(state_key, monitor_name)
            if port_state == "Forwarding" and port_role == "Designated" and rate_forward_transition == 0:
                self.forward_transition_normal(state_key, monitor_name)

    def set_port_state(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        self.variables[state_key + '_port_state'] = event['value']
        port_state = event['value']
        port_role_key = state_key + '_port_role'
        loop_guard_key = state_key + ',map_key=loop_guard'
        rate_bpdu_rx_key = state_key + ',TimeInterval=10s,map_key=BPDUs_Rx'
        rate_bpdu_tx_key = state_key + ',TimeInterval=10s,map_key=BPDUs_Tx'
        rate_forward_transition_key = state_key + \
            ',TimeInterval=10s,map_key=forward_transition_count'
        root_guard_key = state_key + ',map_key=root_guard'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables:
            port_role = self.variables[port_role_key]
            if port_state == "Learning" and port_role == "Disabled":
                self.invalid_port_combinations(
                    state_key, "disabled_learning", monitor_name)
            if port_state == "Disabled" and port_role == "Disabled":
                self.invalid_port_combinations(
                    state_key, "disabled_disabled", monitor_name)
            if port_state == "Blocking" and port_role == "Disabled":
                self.port_combinations_normal(
                    state_key, "disabled_blocking", monitor_name)
            if port_state == "Forwarding" and port_role == "Disabled":
                self.port_combinations_normal(
                    state_key, "disabled_forwarding", monitor_name)
        if port_role_key in self.variables and loop_guard_key in self.variables:
            loop_guard = self.variables[loop_guard_key]
            if port_state == "Disabled" and port_role == "Root" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "root_disabled", monitor_name)
            if port_state == "Blocking" and port_role == "Root" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "root_blocking", monitor_name)
            if port_state == "Disabled" and port_role == "Master" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "master_disabled", monitor_name)
            if port_state == "Blocking" and port_role == "Master" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "master_blocking", monitor_name)
            if port_state != "Blocking" and port_role == "Alternate" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "alternate_blocking", monitor_name)
            if port_state != "Blocking" and port_role == "Backup" and loop_guard == 0:
                self.invalid_port_combinations(
                    state_key, "backup_blocking", monitor_name)
            if port_role == "Root" and port_state == "Forwarding" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "root_forwarding", monitor_name)
            if port_role == "Root" and port_state == "Learning" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "root_learning", monitor_name)
            if port_role == "Master" and port_state == "Forwarding" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "master_forwarding", monitor_name)
            if port_role == "Root" and port_state == "Learning" and loop_guard == 1:
                self.port_combinations_normal(
                    state_key, "root_learning", monitor_name)
        if port_role_key in self.variables and root_guard_key in self.variables:
            root_guard = self.variables[root_guard_key]
            if port_role == "Designated" and port_state == "Disabled" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_disabled", monitor_name)
            if port_role == "Designated" and port_state == "Blocking" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_blocking", monitor_name)
            if port_role == "Designated" and port_state == "Forwarding" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_forwarding", monitor_name)
            if port_role == "Designated" and port_state == "Learning" and root_guard == 1:
                self.port_combinations_normal(
                    state_key, "designated_learning", monitor_name)
        if port_role_key in self.variables and rate_bpdu_rx_key in self.variables:
            rate_bpdu_rx = float(self.variables[rate_bpdu_rx_key])
            if port_state == "Forwarding" and port_role == "Root" and rate_bpdu_rx < 0.1:
                self.starvation(state_key, 'rx', monitor_name)
            if port_state == "Blocking" and port_role == "Alternate" and rate_bpdu_rx < 0.1:
                self.starvation(state_key, 'rx', monitor_name)
            if port_state == "Forwarding" and port_role == "Root" and rate_bpdu_rx >= 0.1:
                self.starvation_normal(state_key, 'rx', monitor_name)
            if port_state == "Blocking" and port_role == "Alternate" and rate_bpdu_rx >= 0.1:
                self.starvation_normal(state_key, 'rx', monitor_name)
        if port_role_key in self.variables and rate_bpdu_tx_key in self.variables:
            rate_bpdu_tx = float(self.variables[rate_bpdu_tx_key])
            if port_state == "Forwarding" and port_role == "Designated" and rate_bpdu_tx < 0.1:
                self.starvation(state_key, 'tx', monitor_name)
            if port_state == "Forwarding" and port_role == "Designated" and rate_bpdu_tx >= 0.1:
                self.starvation_normal(state_key, 'tx', monitor_name)
        if port_role_key in self.variables and rate_forward_transition_key in self.variables:
            rate_forward_transition = float(
                self.variables[rate_forward_transition_key])
            if port_role == "Root" and port_state == "Forwarding" and rate_forward_transition > 0.0:
                self.forward_transition_error(state_key, monitor_name)
            if port_role == "Designated" and port_state == "Forwarding" and rate_forward_transition > 0.0:
                self.forward_transition_error(state_key, monitor_name)
            if port_role == "Root" and port_state == "Forwarding" and rate_forward_transition == 0.0:
                self.forward_transition_normal(state_key, monitor_name)
            if port_role == "Designated" and port_state == "Forwarding" and rate_forward_transition == 0.0:
                self.forward_transition_normal(state_key, monitor_name)

    def set_port_inconsistent_loop_guard(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',map_key=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            port_role = self.variables[port_role_key]
            port_state = self.variables[port_state_key]
            if port_role == "Root" and port_state == "Disabled":
                self.invalid_port_combinations(
                    stp_instance, "root_disabled", monitor_name)
            if port_role == "Root" and port_state == "Blocking":
                self.invalid_port_combinations(
                    stp_instance, "root_blocking", monitor_name)
            if port_role == "Master" and port_state == "Disabled":
                self.invalid_port_combinations(
                    stp_instance, "master_disabled", monitor_name)
            if port_role == "Master" and port_state == "Blocking":
                self.invalid_port_combinations(
                    stp_instance, "master_blocking", monitor_name)
            if port_role == "Alternate" and port_state != "Blocking":
                self.invalid_port_combinations(
                    stp_instance, "alternate_blocking", monitor_name)
            if port_role == "Backup" and port_state != "Blocking":
                self.invalid_port_combinations(
                    stp_instance, "backup_blocking", monitor_name)

    def set_port_inconsistent_root_guard(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        self.variables[state_key] = event['value']

    def set_rate_bpdu_rx(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            port_role = self.variables[port_role_key]
            port_state = self.variables[port_state_key]
            if port_role == "Alternate" and port_state == "Blocking":
                self.starvation(stp_instance, 'rx', monitor_name)
            if port_role == "Root" and port_state == "Forwarding":
                self.starvation(stp_instance, 'rx', monitor_name)

    def set_rate_bpdu_tx(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            if self.variables[port_role_key] == "Designated" and self.variables[port_state_key] == "Forwarding":
                self.starvation(stp_instance, 'tx', monitor_name)

    def set_rate_forward_transition(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            port_role = self.variables[port_role_key]
            port_state = self.variables[port_state_key]
            if port_role == "Root" and port_state == "Forwarding":
                self.forward_transition_error(stp_instance, monitor_name)
            if port_role == "Designated" and port_state == "Forwarding":
                self.forward_transition_error(stp_instance, monitor_name)

    def port_inconsistent_loop_guard_true(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',map_key=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            port_role = self.variables[port_role_key]
            port_state = self.variables[port_state_key]
            if port_role == "Root" and port_state == "Forwarding":
                self.port_combinations_normal(
                    stp_instance, "root_forwarding", monitor_name)
            if port_role == "Root" and port_state == "Learning":
                self.port_combinations_normal(
                    stp_instance, "root_learning", monitor_name)
            if port_role == "Alternate" and port_state == "Blocking":
                self.port_combinations_normal(
                    stp_instance, "alternate_blocking", monitor_name)
            if port_role == "Backup" and port_state == "Blocking":
                self.port_combinations_normal(
                    stp_instance, "backup_blocking", monitor_name)

    def port_combinations_normal(self, stp_instance, states, monitor_name):
        self.clear_critical_state(stp_instance + '_' + states)
        agent_name = get_agent_name(monitor_name)
        ActionSyslog(
            "Valid combinations of port role and port state for STP instance: " + stp_instance)
        if self.get_alert_level() is not None:
            if not self.variables['stp_ports_in_critical_state']:
                self.remove_alert_level()
                self.logger.debug(
                    'Agent {} is in normal state'.format(agent_name))

    def starvation_normal(self, stp_instance, direction, monitor_name):
        self.clear_critical_state(
            stp_instance + '_' + direction + '_starvation')
        agent_name = get_agent_name(monitor_name)
        ActionSyslog('Rate of BPDU {} is normal for STP instance {}'.format(
            direction, stp_instance))
        if self.get_alert_level() is not None:
            if not self.variables['stp_ports_in_critical_state']:
                self.remove_alert_level()
                self.logger.debug(
                    'Agent {} is in normal state'.format(agent_name))

    def update_critical_list(self, case):
        if case not in self.variables['stp_ports_in_critical_state']:
            stp_list = self.variables[
                'stp_ports_in_critical_state']
            self.variables[
                'stp_ports_in_critical_state'] = stp_list + case

    def clear_critical_state(self, case):
        if case in self.variables['stp_ports_in_critical_state']:
            stp_list = self.variables[
                'stp_ports_in_critical_state']
            stp_list = stp_list.replace(
                case, '')
            self.variables[
                'stp_ports_in_critical_state'] = stp_list

    def rate_bpdu_tx_normal(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            if self.variables[port_role_key] == "Designated" and self.variables[port_state_key] == "Forwarding":
                self.starvation_normal(stp_instance, 'tx', monitor_name)

    def rate_bpdu_rx_normal(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            port_role = self.variables[port_role_key]
            port_state = self.variables[port_state_key]
            if port_role == "Alternate" and port_state == "Blocking":
                self.starvation_normal(stp_instance, 'rx', monitor_name)
            if port_role == "Root" and port_state == "Forwarding":
                self.starvation_normal(stp_instance, 'rx', monitor_name)

    def rate_forward_transition_normal(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        stp_instance = state_key.split(',TimeInterval=')[0]
        self.variables[state_key] = event['value']
        port_role_key = stp_instance + '_port_role'
        port_state_key = stp_instance + '_port_state'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and port_state_key in self.variables:
            port_role = self.variables[port_role_key]
            port_state = self.variables[port_state_key]
            if port_role == "Root" and port_state == "Forwarding":
                self.forward_transition_normal(stp_instance, monitor_name)
            if port_role == "Designated" and port_state == "Forwarding":
                self.forward_transition_normal(stp_instance, monitor_name)

    def forward_transition_normal(self, stp_instance, monitor_name):
        self.clear_critical_state(stp_instance + '_forward_transition_error')
        agent_name = get_agent_name(monitor_name)
        ActionSyslog(
            'Rate of forward transition is normal for STP instance {}'.format(stp_instance))
        if self.get_alert_level() is not None:
            if not self.variables['stp_ports_in_critical_state']:
                self.remove_alert_level()
                self.logger.debug(
                    'Agent {} is in normal state'.format(agent_name))

    def port_state_learning_to_blocking(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        self.variables[state_key + '_learning_to_blocking'] = event['value']
        port_role_key = state_key + '_port_role'
        root_guard_key = state_key + '_root_guard'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and root_guard_key in self.variables:
            if self.variables[port_role_key] == "Designated" and self.variables[root_guard_key] == 0:
                self.invalid_port_combinations(
                    state_key, "learning_blocking", monitor_name)

    def port_state_forwarding_to_blocking(self, event):
        label = event['labels']
        state_key = label.split('STP_Instance=')[1]
        self.variables[state_key + '_forwarding_to_blocking'] = event['value']
        port_role_key = state_key + '_port_role'
        root_guard_key = state_key + '_root_guard'
        monitor_name = event['monitor_name']
        if port_role_key in self.variables and root_guard_key in self.variables:
            if self.variables[port_role_key] == "Designated" and self.variables[root_guard_key] == 0:
                self.invalid_port_combinations(
                    state_key, "forwarding_blocking", monitor_name)


def get_agent_name(monitor_name):
    return monitor_name.split('.')[0]
