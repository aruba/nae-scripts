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
    'Name': 'ospfv2_shortest_path_first_calculation_monitor',
    'Description': 'OSPFv2 SPF Calculation Monitor Policy',
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
               'attributes=statistics.spf_calc'
        self.m1 = Monitor(
            uri1,
            'SPF Calculation Monitor',
            [self.params['vrf_name'],
             self.params['ospf_process_id'],
             self.params['ospf_area_id']])
