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
    'Name': 'acl_hit_counters_monitor',
    'Description': 'Network Analytics Agent Script to monitor'
                   'ACL hit counters for a given ACE number',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'port_number': {
        'Name': 'Port Number',
        'Description': 'Port Number where the ACL rule is applied',
        'Type': 'string',
        'Default': '1/1/1'
    },
    'ace_number': {
        'Name': 'ACE sequence number',
        'Description': 'Access Control Entry sequence number',
        'Type': 'integer',
        'Default': 1
    }
}


class Policy(NAE):

    def __init__(self):
        uri1 = '/rest/v1/system/ports/{}?attributes=aclv4_in_statistics.{}'
        self.m1 = Monitor(uri1, 'ACL hit counters',
                          [self.params['port_number']],
                          [self.params['ace_number']])
