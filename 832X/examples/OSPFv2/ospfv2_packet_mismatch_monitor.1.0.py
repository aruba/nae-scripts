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
    'Name': 'ospfv2_packet_mismatch_monitor',
    'Description': 'OSPFv2 Packet Mismatch',
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
    },

    'ospf_interface_id': {
        'Name': 'OSPFv2 interface id',
        'Description': 'OSPFv2 interface id to be Monitor',
        'Type': 'String',
        'Default': '1/1/1'
    },

    'area_mismatch': {
        'Name': 'OSPFv2 Area Mismatch',
        'Description': 'OSPFv2 Area Mismatch to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'auth_errors': {
        'Name': 'OSPFv2 Authentication Errors',
        'Description': 'OSPFv2 Authentication Errors to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'auth_fail': {
        'Name': 'OSPFv2 Authentication Fail',
        'Description': 'OSPFv2 Authentication Fail to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'auth_mismatch': {
        'Name': 'OSPFv2 Authentication Mismatch',
        'Description': 'OSPFv2 Authentication Mismatch to be Monitor',
        'Type': 'integer',
        'Default': 0
    },


    'bad_lsa_checksum': {
        'Name': 'OSPFv2 Bad LSA Checksum',
        'Description': 'OSPFv2 Bad LSA Checksum to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'bad_lsa_data': {
        'Name': 'OSPFv2 Bad LSA Data',
        'Description': 'OSPFv2 Bad LSA Data to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'bad_lsa_length': {
        'Name': 'OSPFv2 Bad LSA Length',
        'Description': 'OSPFv2 Bad LSA Length to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'bad_lsa_type': {
        'Name': 'OSPFv2 Bad LSA Type',
        'Description': 'OSPFv2 Bad LSA Type to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'bad_lsu_length': {
        'Name': 'OSPFv2 Bad LSU Length',
        'Description': 'OSPFv2 Bad LSU Length to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'bad_hello': {
        'Name': 'OSPFv2 Bad Hello',
        'Description': 'OSPFv2 Bad Hello to be Monitor',
        'Type': 'integer',
        'Default': 1
    },

    'dead_mismatch': {
        'Name': 'OSPFv2 Dead Interval Mismatch',
        'Description': 'OSPFv2 Dead Interval Mismatch to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'hello_mismatch': {
        'Name': 'OSPFv2 Hello Interval Mismatch',
        'Description': 'OSPFv2 Hello Interval Mismatch to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'invalid_version': {
        'Name': 'OSPFv2 Invalid Protocl Version',
        'Description': 'OSPFv2 Invalid Protocl Version to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'mask_mismatch': {
        'Name': 'OSPFv2 Net Mask Mismatch',
        'Description': 'OSPFv2 Net Mask Mismatch to be Monitor',
        'Type': 'integer',
        'Default': 0
    },

    'mtu_mismatch': {
        'Name': 'OSPFv2 MTU Mismatch',
        'Description': 'OSPFv2  MTU Mismatch to be Monitor',
        'Type': 'integer',
        'Default': 0
    }
}


class Policy(NAE):

    def __init__(self):

        if str(self.params['area_mismatch']) == "1":
            uri1 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_area_mismatch'
            self.m1 = Monitor(
                uri1,
                'Received Area Mismatch (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['invalid_version']) == "1":
            uri2 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_invalid_version'
            self.m2 = Monitor(
                uri2,
                'Received invalid version (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['auth_errors']) == "1":
            uri3 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_auth_errors'
            self.m3 = Monitor(
                uri3,
                'Received Authentication Errors (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['auth_fail']) == "1":
            uri4 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_auth_fail'
            self.m4 = Monitor(
                uri4,
                'Received Authentication Fail (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['auth_mismatch']) == "1":
            uri5 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/'\
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_auth_mismatch'
            self.m5 = Monitor(
                uri5,
                'Received Authentication Mismatch (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['bad_lsa_checksum']) == "1":
            uri6 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_bad_lsa_checksum'
            self.m6 = Monitor(
                uri6,
                'Received Bad LSA Checksum (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['bad_lsa_data']) == "1":
            uri7 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_bad_lsa_data'
            self.m7 = Monitor(
                uri7,
                'Received Bad LSA Data (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['bad_lsa_length']) == "1":
            uri8 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_bad_lsa_length'
            self.m8 = Monitor(
                uri8,
                'Received Bad LSA Length (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['bad_lsa_type']) == "1":
            uri9 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                   'ospf_interfaces/{}?attributes=' \
                   'statistics.rcvd_bad_lsa_type'
            self.m9 = Monitor(
                uri9,
                'Received Bad LSA Type (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['bad_lsu_length']) == "1":
            uri10 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                    'ospf_interfaces/{}?attributes=' \
                    'statistics.rcvd_bad_lsu_length'
            self.m10 = Monitor(
                uri10,
                'Received Bad LSU Length (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['bad_hello']) == "1":
            uri11 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                    'ospf_interfaces/{}?attributes=' \
                    'statistics.rcvd_bad_hello'
            self.m11 = Monitor(
                uri11,
                'Received Bad Hello (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['dead_mismatch']) == "1":
            uri12 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                    'ospf_interfaces/{}?attributes=' \
                    'statistics.rcvd_dead_mismatch'
            self.m12 = Monitor(
                uri12,
                'Received Dead Interval Mismatch (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['hello_mismatch']) == "1":
            uri13 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                    'ospf_interfaces/{}?attributes=' \
                    'statistics.rcvd_hello_mismatch'
            self.m13 = Monitor(
                uri13,
                'Received Hello Interval Mismatch (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['mask_mismatch']) == "1":
            uri14 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                    'ospf_interfaces/{}?attributes=' \
                    'statistics.rcvd_mask_mismatch'
            self.m14 = Monitor(
                uri14,
                'Received Net Mask Mismatch (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])

        if str(self.params['mtu_mismatch']) == "1":
            uri15 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
                    'ospf_interfaces/{}?attributes=' \
                    'statistics.rcvd_mtu_mismatch'
            self.m15 = Monitor(
                uri15,
                'Received MTU Mismatch (count)',
                [self.params['vrf_name'],
                 self.params['ospf_process_id'],
                 self.params['ospf_area_id'],
                 self.params['ospf_interface_id']])
