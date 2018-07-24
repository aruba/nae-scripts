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
    'Name': 'interface_queues_monitor',
    'Description': 'This agent monitors egress queues of an interface and '
                   'reports the counters of tx bytes, tx packets & tx errors',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'interface_id': {
        'Name': 'Interface ID',
        'Description': 'Interface index whose queues will be monitored'
                       ' by this agent',
        'Type': 'string',
        'Default': '1/1/1'
    }
}


class Agent(NAE):

    def __init__(self):
        for i in range(8):
            # TX packets queued
            uri = 'uri' + str(i)
            pktmonitorvar = 'pktmonitor' + str(i)
            uri = '/rest/v1/system/interfaces/{}?' \
                  'attributes=queue_tx_packets.' + str(i)
            pktmonitor = Monitor(
                uri,
                'Queue ' + str(i) + ' Tx packets (packets)',
                [self.params['interface_id']])
            setattr(self, pktmonitorvar, pktmonitor)

        for i in range(8):
            # TX Bytes queued
            uri = 'uri' + str(i)
            bytemonitorvar = 'bytemonitor' + str(i)
            uri = '/rest/v1/system/interfaces/{}?' \
                  'attributes=queue_tx_bytes.' + str(i)
            bytemonitor = Monitor(
                uri,
                'Queue ' + str(i) + ' Tx Bytes (bytes)',
                [self.params['interface_id']])
            setattr(self, bytemonitorvar, bytemonitor)

        for i in range(8):
            # TX Errors queued
            uri = 'uri' + str(i)
            errormonitorvar = 'errormonitor' + str(i)
            uri = '/rest/v1/system/interfaces/{}?' \
                  'attributes=queue_tx_errors.' + str(i)
            errormonitor = Monitor(
                uri,
                'Queue ' + str(i) + ' Tx Errors (errors)',
                [self.params['interface_id']])
            setattr(self, errormonitorvar, errormonitor)
