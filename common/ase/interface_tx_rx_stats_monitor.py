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
    'Name': 'interface_tx_rx_stats_monitor',
    'Description': 'Physical Interface tx/rx statistics monitoring agent'
                   ' using multi-graph',
    'Version': '2.2',
    'TargetSoftwareVersion': '10.04',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        # algorithm for dynamic threshold calculation
        self.alg = MaxAlgorithm(continuous_learning_window="10m")

        # rx packets
        uri1 = '/rest/v1/system/interfaces/*?attributes=statistics.rx_packets' + \
            '&filter=type:system'
        rate_m1 = Rate(uri1, "20 seconds")
        self.m1 = Monitor(rate_m1, 'Rx Packets (packets per second)')
        self.r1 = Rule('Rule for Monitor Interface rx Packets')

        title1 = Title("Baseline for Interface rx Packets")
        self.baseline1 = Baseline(self.m1, algorithm=self.alg, title=title1,
                                  high_threshold_factor=2,
                                  low_threshold_factor=1.2,
                                  initial_learning_time='1d')
        self.r1.condition('{} > {}', [self.m1, self.baseline1])
        self.r1.clear_condition('{} < {}', [self.m1, self.baseline1])
        self.r1.action("ALERT_LEVEL", AlertLevel.CRITICAL)
        self.r1.clear_action("ALERT_LEVEL", AlertLevel.NONE)

        # rx packets dropped
        uri2 = '/rest/v1/system/interfaces/*?attributes=statistics.rx_dropped' + \
            '&filter=type:system'
        self.m2 = Monitor(
            uri2,
            'Rx Packets Dropped (packets)')

        # tx packets
        uri3 = '/rest/v1/system/interfaces/*?attributes=statistics.tx_packets' + \
            '&filter=type:system'
        rate_m3 = Rate(uri3, "20 seconds")
        self.m3 = Monitor(rate_m3, 'Tx Packets (packets per second)')
        self.r3 = Rule('Rule for Monitor Interface tx Packets')
        title3 = Title("Baseline for Interface tx Packets")
        self.baseline3 = Baseline(self.m3, algorithm=self.alg,  title=title3,
                                  high_threshold_factor=2,
                                  low_threshold_factor=1.2,
                                  initial_learning_time='1d')
        self.r3.condition('{} > {}', [self.m3, self.baseline3])
        self.r3.clear_condition('{} < {}', [self.m3, self.baseline3])
        self.r3.action("ALERT_LEVEL", AlertLevel.CRITICAL)
        self.r3.clear_action("ALERT_LEVEL", AlertLevel.NONE)

        # tx packets dropped
        uri4 = '/rest/v1/system/interfaces/*?attributes=statistics.tx_dropped' + \
            '&filter=type:system'
        self.m4 = Monitor(
            uri4,
            'Tx Packets Dropped (packets)')

        # graph display for change of traffic and packets drop
        self.graph_tx_rx_packets = \
            Graph([self.m1, self.m3],
                  title=Title("Interface tx/rx packets change per second"),
                  dashboard_display=True)
        self.graph_tx_rx_drop = \
            Graph([self.m2, self.m4],
                  title=Title("Interface tx/rx packets drop"),
                  dashboard_display=False)
