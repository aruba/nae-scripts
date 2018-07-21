# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2018 Hewlett Packard Enterprise Development LP
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
    'Name': 'vrrpv2_advertisements_count_monitor',
    'Description': 'VRRP advertisements count monitoring agent',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'port_name': {
        'Name': 'Interface monitored for VRRP advertisements count',
        'Description': 'This parameter specifies the interface that'
                       'this agent will monitor for VRRP advertisements'
                       'packet count'
                       'This can be a physical, vlan or lag interface.',
        'Type': 'string',
        'Default': '1/1/1'
    },
    'vrrp_id': {
        'Name': 'VRRP ID',
        'Description': 'value supported between 1-255',
        'Type': 'integer',
        'Default': 1
    }
}


class Agent(NAE):

    def __init__(self):

        uri1 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
               'attributes=statistics.vrrpv2_advertisement_tx'
        self.m1 = Monitor(
            uri1,
            'VRRPv2 advertisement Tx Packets (packets) ',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri2 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
               'attributes=statistics.vrrpv2_advertisement_rx'
        self.m2 = Monitor(
            uri2,
            'VRRPv2 advertisement Rx Packets (packets)',
            [self.params['port_name'],
             self.params['vrrp_id']])
        uri3 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
               'attributes=statistics.zero_priority_tx'
        self.m3 = Monitor(
            uri3,
            'VRRPv2 zero priority Tx Packets (packets)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri4 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
               'attributes=statistics.zero_priority_rx'
        self.m4 = Monitor(
            uri4,
            'VRRPv2 zero priority Rx Packets (packets)',
            [self.params['port_name'],
             self.params['vrrp_id']])
