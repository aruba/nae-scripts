# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2017 Hewlett Packard Enterprise Development LP
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
    'Name': 'copp_statistics_monitor',
    'Description': 'CoPP statistics monitoring agent',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'copp_class': {
        'Name': 'CoPP class to monitor statistics',
        'Description': 'CoPP class to monitor statistics',
        'Type': 'string',
        'Default': 'total'
    }
}


class Policy(NAE):

    def __init__(self):

        uri1 = '/rest/v1/system?attributes=copp_statistics.{}_packets_passed'
        self.m1 = Monitor(uri1, 'Packets Passed', [self.params['copp_class']])

        uri2 = '/rest/v1/system?attributes=copp_statistics.{}_packets_dropped'
        self.m2 = Monitor(uri2, 'Packets Dropped', [self.params['copp_class']])
