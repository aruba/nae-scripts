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
    'Name': 'vrrpv2_packet_error_count_monitor',
    'Description': 'VRRP packet error count monitoring agent',
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
            'attributes=statistics.advertise_interval_errors'
        self.m1 = Monitor(
            uri1,
            'VRRPv2 Advertise Interval Errors (count) ',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri2 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.advertise_recv_in_init_state'
        self.m2 = Monitor(
            uri2,
            'VRRPv2 Advertise Recv In Init State (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri3 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.advertise_recv_with_invalid_len'
        self.m3 = Monitor(
            uri3,
            'VRRPv2 Advertise Recv With Invalid Len (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri4 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.advertise_recv_with_invalid_ttl'
        self.m4 = Monitor(
            uri4,
            'VRRPv2 Advertise Recv With Invalid TTL (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri5 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.advertise_recv_with_invalid_type'
        self.m5 = Monitor(
            uri5,
            'VRRPv2 Advertise Recv With Invalid Type (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri6 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.ip_address_owner_conflicts'
        self.m6 = Monitor(
            uri6,
            'VRRPv2 IP Address Owner Conflicts (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri7 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.mismatched_addr_list_pkts'
        self.m7 = Monitor(
            uri7,
            'VRRPv2 Mismatched Addr List Pkts (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri8 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.mismatched_auth_type_pkts'
        self.m8 = Monitor(
            uri8,
            'VRRPv2 Mismatched Auth Type Pkts (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri9 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.near_failovers'
        self.m9 = Monitor(
            uri9,
            'VRRPv2 Near Failovers Pkts (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])

        uri10 = '/rest/v1/system/ports/{}/virtual_ip4_routers/{}?' \
            'attributes=statistics.other_reasons'
        self.m10 = Monitor(
            uri10,
            'VRRPv2 Other Reasons Pkts (count)',
            [self.params['port_name'],
             self.params['vrrp_id']])
