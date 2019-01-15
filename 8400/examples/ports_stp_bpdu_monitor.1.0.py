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
    'Name': 'ports_stp_bpdu_monitor',
    'Description': 'Agent to Monitor BPDU packets sent(tx) vs '
                   'received(rx) on all STP configured ports',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Policy(NAE):

    def __init__(self):
        uri1 = '/rest/v1/system/bridge/stp_instances/mstp/0/' \
               'stp_instance_ports/*?attributes=statistics.BPDUs_Tx'
        uri2 = '/rest/v1/system/bridge/stp_instances/mstp/0/' \
               'stp_instance_ports/*?attributes=statistics.BPDUs_Rx'
        self.m2 = Monitor(uri1, 'STP BPDUs Sent (packets)')
        self.m3 = Monitor(uri2, 'STP BPDUs Received (packets)')
