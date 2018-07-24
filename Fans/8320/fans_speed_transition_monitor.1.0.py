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
    'Name': 'fans_speed_transition_monitor',
    'Description': 'Agent to monitor speed of all fans, '
                   'wherein the transition between different '
                   'speed states is monitored. The agent status '
                   'is set to Critical when any of the fan speed '
                   'has transition from normal/medium/slow to '
                   'max/fast. The status remains in Critical, '
                   'when other fans speed transits to max/fast, '
                   'and syslog and cli are displayed.The agent '
                   'status is set back to normal when all the '
                   'fans are in normal/medium/slow state.',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        self.variables['fans_list'] = ''

        uri1 = '/rest/v1/system/subsystems/*/*/fans/*?attributes=speed'
        self.m1 = Monitor(uri1, 'Fan Speed')

        self.r1 = Rule('Speed - slow to fast')
        self.r1.condition('transition {} from "slow" to "fast"', [self.m1])
        self.r1.action(self.fans_speed_action_high)

        self.r2 = Rule('Speed - slow to max')
        self.r2.condition('transition {} from "slow" to "max"', [self.m1])
        self.r2.action(self.fans_speed_action_high)

        self.r3 = Rule('Speed - normal to fast')
        self.r3.condition('transition {} from "normal" to "fast"', [self.m1])
        self.r3.action(self.fans_speed_action_high)

        self.r4 = Rule('Speed - normal to max')
        self.r4.condition('transition {} from "normal" to "max"', [self.m1])
        self.r4.action(self.fans_speed_action_high)

        self.r5 = Rule('Speed - medium to fast')
        self.r5.condition('transition {} from "medium" to "fast"', [self.m1])
        self.r5.action(self.fans_speed_action_high)

        self.r6 = Rule('Speed - medium to max')
        self.r6.condition('transition {} from "medium" to "max"', [self.m1])
        self.r6.action(self.fans_speed_action_high)

        self.r7 = Rule('Speed - fast to max')
        self.r7.condition('transition {} from "fast" to "max"', [self.m1])
        self.r7.action(self.fans_speed_action_high)

        self.r8 = Rule('Speed - max to fast')
        self.r8.condition('transition {} from "max" to "fast"', [self.m1])
        self.r8.action(self.fans_speed_action_high)

        self.r9 = Rule('Speed - fast to slow')
        self.r9.condition('transition {} from "fast" to "slow"', [self.m1])
        self.r9.action(self.fans_speed_action_normal)

        self.r10 = Rule('Speed - fast to normal')
        self.r10.condition('transition {} from "fast" to "normal"', [self.m1])
        self.r10.action(self.fans_speed_action_normal)

        self.r11 = Rule('Speed - fast to medium')
        self.r11.condition('transition {} from "fast" to "medium"', [self.m1])
        self.r11.action(self.fans_speed_action_normal)

        self.r12 = Rule('Speed - max to slow')
        self.r12.condition('transition {} from "max" to "slow"', [self.m1])
        self.r12.action(self.fans_speed_action_normal)

        self.r13 = Rule('Speed - max to normal')
        self.r13.condition('transition {} from "max" to "normal"', [self.m1])
        self.r13.action(self.fans_speed_action_normal)

        self.r14 = Rule('Speed - max to medium')
        self.r14.condition('transition {} from "max" to "medium"', [self.m1])
        self.r14.action(self.fans_speed_action_normal)

    def fans_speed_action_high(self, event):
        self.logger.debug('LABEL = ' + event['labels'])
        label = event['labels']
        fanname = label.split(',')[0].split('=')[1]
        self.logger.debug('fanname= ' + fanname)

        if self.variables['fans_list'] != '':
            findfan = self.variables['fans_list']
            istrue = findfan.find(fanname)
            if istrue == -1:
                fans_list = fanname + self.variables['fans_list']
                self.variables['fans_list'] = fans_list
                self.logger.debug('list of fans =  ' +
                                  self.variables['fans_list'])
                self.set_actions(fanname)
            else:
                self.set_actions(fanname)
        else:
            self.variables['fans_list'] = fanname
            self.logger.debug('list of fans =  ' +
                              self.variables['fans_list'])
            self.set_actions(fanname)

    def set_actions(self, fanname):
        self.logger.debug("+++ CALLBACK: FAN SPEED - MAX/FAST!")
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
        ActionSyslog('Fan ' + fanname + ' is at max/fast speed ')
        ActionCLI('show environment fan')

    def fans_speed_action_normal(self, event):
        if self.get_alert_level() is not None:
            self.logger.debug("********TRANSITION TO NORMAL********")
            self.logger.debug('LABEL = ' + event['labels'])
            label = event['labels']
            fanname = label.split(',')[0].split('=')[1]

            # delete fanname which moved to normal/medium/slow state
            index = 0
            length = len(fanname)
            findfan = self.variables['fans_list']
            index = findfan.find(fanname)
            if index != -1:
                # index = string.find(str, substr)
                findfan = findfan[0:index] + findfan[index + length:]
                self.variables['fans_list'] = findfan
                self.logger.debug('Fan name deleted ' + fanname)
                self.logger.debug('Current fans list ' +
                                  self.variables['fans_list'])
                ActionSyslog('Fan ' + fanname + ' back to ' +
                             'normal/medium/slow speed')
                if self.variables['fans_list'] == '':
                    self.set_agent_status_normal()

    def set_agent_status_normal(self):
        self.remove_alert_level()
        ActionSyslog('All fans speed are normal')

    def on_agent_restart(self, event):
        self.remove_alert_level()
