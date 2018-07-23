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
    'Name': 'line_card_monitor',
    'Description': 'NAE Agent to monitor Line Card (LC) State, '
                   'CPU and Memory utilization. Agent alerts if '
                   'any LC is in down state and will capture '
                   'relevant LC logs',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):

        lc_state_uri = '/rest/v1/system/subsystems/line_card/*?' \
            'attributes=state'
        lc_cpu_uri = '/rest/v1/system/subsystems/line_card/*?' \
                     'attributes=resource_utilization.cpu'
        lc_memory_uri = '/rest/v1/system/subsystems/line_card/*?' \
                        'attributes=resource_utilization.memory'

        self.lc_state_mon = Monitor(lc_state_uri, 'LC state (LC State)')
        self.lc_cpu_mon = Monitor(
            lc_cpu_uri,
            'LC CPU (LC CPU/Memory Utilization in %)')
        self.lc_memory_mon = Monitor(
            lc_memory_uri,
            'LC Memory (LC CPU/Memory Utilization in %)')

        self.r1 = Rule('Line Card Down')
        self.r1.condition('{} == "down"', [self.lc_state_mon])
        self.r1.action(self.action_lc_down)

        self.variables['lc_down_list'] = ''

    def action_lc_down(self, event):
        self.logger.debug("======= LC Down ============")
        lc_slot = self.get_lc_slot(event['labels'])
        lc_number = str(self.get_lc_number(lc_slot))
        ActionSyslog('Line Card [' + lc_slot + '] is down')
        self.execute_cli_shell(lc_slot, lc_number)
        lc_down_list = self.variables['lc_down_list']
        self.logger.debug('lc_down_list before: [' + lc_down_list + ']')
        if lc_number not in lc_down_list:
            lc_down_list = lc_down_list + lc_number
            self.variables['lc_down_list'] = lc_down_list
            if self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
        lc_down_list = self.variables['lc_down_list']
        self.logger.debug('lc_down_list after: [' + lc_down_list + ']')
        self.logger.debug("======= /LC Down ===========")

    def execute_cli_shell(self, lc_slot, lc_number):
        ActionCLI('show mod ' + lc_slot)
        ActionCLI('show events -d hpe-cardd')
        ActionShell('ovs-appctl -t hpe-cardd fastlog show lc ' + lc_number)

    def get_lc_slot(self, event_label):
        self.logger.debug('event label: [' + event_label + ']')
        _, lc = event_label.split(',')[0].split('=')
        self.logger.debug('line card: ' + lc)
        lc_slot = lc.replace('line_card_', '')
        return lc_slot

    def get_lc_number(self, lc_slot):
        self.logger.debug('LC slot: [' + lc_slot + ']')
        lc_number = int(lc_slot.replace('1/', ''))
        if lc_number >= 7 and lc_number <= 10:
            lc_number = lc_number - 2
        return lc_number
