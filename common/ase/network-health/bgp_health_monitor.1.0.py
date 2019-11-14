# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2018 Hewlett Packard Enterprise Development LP
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
    'Name': 'BGP_Health',
    'Description': 'Detects BGP neighbors flapping',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        self.logger.debug('BGP Health')

        bgp_stats_uri = '/rest/v1/system/vrfs/*/bgp_routers/*/bgp_neighbors/*?attributes=statistics.bgp_peer_established_count'

        rate = Rate(bgp_stats_uri, "60 seconds")
        self.m1 = Monitor(rate, 'Established Rate')
        self.r1 = Rule('BGP Established Rate')

        self.r1.condition('{} > 0.1', [self.m1])
        self.r1.action(self.bgp_neighbor_action)

        self.r1.clear_condition('{} == 0', [self.m1])
        self.r1.clear_action(self.bgp_neighbor_clear_action)

    def bgp_neighbor_action(self, event):
        self.logger.debug('BGP Health CRITICAL: labels: ' + event['labels'])
        self.set_alert_level(AlertLevel.CRITICAL)
        ActionCLI("show ip bgp neighbors all-vrfs")

    def bgp_neighbor_clear_action(self, event):
        self.logger.debug('BGP Health NORMAL again')
        self.set_alert_level(AlertLevel.NONE)
