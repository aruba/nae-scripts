# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Hewlett Packard Enterprise Development LP
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
    'Description': 'Interface tx/rx statistics monitoring agent',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Policy(NAE):

    def __init__(self):
        # rx packets
        uri1 = '/rest/v1/system/interfaces/*?attributes=statistics.rx_packets'
        self.m1 = Monitor(uri1, 'Rx Packets (packets)')

        # rx packets dropped
        uri2 = '/rest/v1/system/interfaces/*?attributes=statistics.rx_dropped'
        self.m2 = Monitor(
            uri2,
            'Rx Packets Dropped (packets)')

        # tx packets
        uri3 = '/rest/v1/system/interfaces/*?attributes=statistics.tx_packets'
        self.m3 = Monitor(uri3, 'Tx Packets (packets)')

        # tx packets dropped
        uri4 = '/rest/v1/system/interfaces/*?attributes=statistics.tx_dropped'
        self.m4 = Monitor(
            uri4,
            'Tx Packets Dropped (packets)')
