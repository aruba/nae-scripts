# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Hewlett Packard Enterprise Development LP
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

Manifest = {
    'Name': 'ospfv2_network_lsa_count_monitor',
    'Description': 'OSPFv2 Network LSA count Monitor Policy',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'vrf_name': {
        'Name': 'Vrf Name',
        'Description': 'Vrf to be Monitor',
        'Type': 'String',
        'Default': 'default'
    },
    'ospf_process_id': {
        'Name': 'OSPFv2 process id',
        'Description': 'OSPFv2 process id to be Monitor',
        'Type': 'integer',
        'Default': 1
    },
    'ospf_area_id': {
        'Name': 'OSPFv2 area id',
        'Description': 'OSPFv2 area id to be Monitor',
        'Type': 'String',
        'Default': '0.0.0.0'
    }
}


class Policy(NAE):

    def __init__(self):

        uri1 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}?' \
               'attributes=lsa_counts.network_lsa'
        self.m1 = Monitor(
            uri1,
            'Network LSA Count Monitor (count)',
            [self.params['vrf_name'],
             self.params['ospf_process_id'],
             self.params['ospf_area_id']])

        uri2 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}?' \
               'attributes=lsa_counts.network_summary_asbr_lsa'
        self.m2 = Monitor(
            uri2,
            'Network Summary ASBR LSA Count Monitor (count)',
            [self.params['vrf_name'],
             self.params['ospf_process_id'],
             self.params['ospf_area_id']])

        uri3 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}?' \
               'attributes=lsa_counts.network_summary_lsa'
        self.m3 = Monitor(
            uri3,
            'Network Summary LSA Count Monitor (count)',
            [self.params['vrf_name'],
             self.params['ospf_process_id'],
             self.params['ospf_area_id']])

        uri4 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}?' \
               'attributes=lsa_counts.nssa_lsa'
        self.m4 = Monitor(
            uri4,
            'Network NSSA LSA Count Monitor (count)',
            [self.params['vrf_name'],
             self.params['ospf_process_id'],
             self.params['ospf_area_id']])

        uri5 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}?' \
               'attributes=lsa_counts.router_lsa'
        self.m5 = Monitor(
            uri5,
            'Network Router LSA Count Monitor (count)',
            [self.params['vrf_name'],
             self.params['ospf_process_id'],
             self.params['ospf_area_id']])

        uri6 = '/rest/v1/system/vrfs/{}/ospf_routers/{}?' \
               'attributes=lsa_counts.external_lsa'
        self.m6 = Monitor(
            uri6,
            'External LSA Count Monitor (count)',
            [self.params['vrf_name'],
             self.params['ospf_process_id']])
