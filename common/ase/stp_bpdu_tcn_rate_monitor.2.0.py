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
    'Name': 'stp_bpdu_tcn_rate_monitor',
    'Description': 'Agent to Monitor Rate of change of  Topology'
                   'Change Notification,'
                   'BPDU Dropped and Received on Ports and '
                   'STP Packets dropped at CPU',
    'Version': '2.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'stp_instance_id': {
        'Name': 'Spanning-Tree Instance Id',
        'Description': 'The MSTP Instance to monitor',
        'Type': 'integer',
        'Default': 0
    },
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
    },
    'stp_port': {
        'Name': 'STP port to monitor BPDUs on',
        'Description': 'STP BPDUs received vs transmitted'
                       'on a port(CIST)',
        'Type': 'string',
        'Default': '1/1/1'
    }
}


class Agent(NAE):

    def __init__(self):
        uri1 = '/rest/v1/system/stp_instances/mstp/{}?' \
               'attributes=topology_change_count'
        # MSTI 0 default CIST instance
        uri2 = '/rest/v1/system/stp_instances/mstp/0/' \
               'stp_instance_ports/{}?attributes=statistics.BPDUs_Tx'
        # MSTI 0 default CIST instance
        uri3 = '/rest/v1/system/stp_instances/mstp/0/' \
               'stp_instance_ports/{}?attributes=statistics.BPDUs_Rx'
        uri4 = '/rest/v1/system?attributes=copp_statistics.stp_packets_dropped'
        self.m2 = Monitor(uri2, 'STP BPDU Sent on PORT', [
            self.params['stp_port']])
        self.m3 = Monitor(uri3, 'STP BPDU Received on PORT', [
            self.params['stp_port']])
        self.m4 = Monitor(uri4, 'STP Packets Dropped at CPU')

        # Rate exceeded the threshold value
        rate_m = Rate(uri1, "10 seconds", [self.params['stp_instance_id']])
        self.m1 = Monitor(rate_m, 'Rate of Topology Change Count')
        self.r1 = Rule('TCN rate exceeded')
        self.r1.condition('{} > {}', [
            self.m1, self.params['tcn_upper_threshold']])
        self.r1.action(self.topo_change_exceeded)

        self.r2 = Rule('TCN rate normal')
        self.r2.condition('{} <= {}', [
            self.m1, self.params['tcn_lower_threshold']])
        self.r2.action(self.topo_change_normal)

    def topo_change_exceeded(self, event):
        if self.get_alert_level() != AlertLevel.CRITICAL:
            ActionSyslog("Topology Change Rate exceeded defined max value {}",
                         [self.params['tcn_upper_threshold']])
            self.set_alert_level(AlertLevel.CRITICAL)
            ActionCLI("show spanning-tree detail")
            ActionCLI("show spanning-tree mst {} detail", [
                      self.params['stp_instance_id']])
            self.logger.debug("### Critical Callback executed")

    def topo_change_normal(self, event):
        if self.get_alert_level() is not None:
            ActionSyslog("Topology Change Rate is back to normal")
            self.logger.info("Current alert level:" +
                             str(self.get_alert_level()))
            self.remove_alert_level()
            self.logger.debug('Unset the previous status')
            self.logger.debug('### Normal Callback executed')
