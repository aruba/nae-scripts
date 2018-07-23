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
    'Name': 'fans_speed_normal_monitor',
    'Description': 'Agent to monitor speed of all fans',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        self.variables['fans_list'] = ''
        self.variables['speedy_fans_count'] = '0'

        uri1 = '/rest/v1/system/subsystems/*/*/fans/*?attributes=speed'
        self.m1 = Monitor(uri1, 'Fan Speed')
        self.r1 = Rule('Fan Speed - Max')
        self.r1.condition('{} == "max"', [self.m1])
        self.r1.action(self.fans_speed_action_high)

        self.r2 = Rule('Fan Speed - Fast')
        self.r2.condition('{} == "fast"', [self.m1])
        self.r2.action(self.fans_speed_action_high)

        self.r3 = Rule('Fan Speed - Medium')
        self.r3.condition('{} == "medium"', [self.m1])
        self.r3.action(self.fans_speed_action_normal)

        self.r4 = Rule('Fan Speed - normal')
        self.r4.condition('{} == "normal"', [self.m1])
        self.r4.action(self.fans_speed_action_normal)

        self.r5 = Rule('Fan Speed - slow')
        self.r5.condition('{} == "slow"', [self.m1])
        self.r5.action(self.fans_speed_action_normal)

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
                self.increment_speedy_fans_count()

        else:
            self.variables['fans_list'] = fanname
            self.logger.debug('list of fans =  ' +
                              self.variables['fans_list'])
            self.set_actions(fanname)
            self.increment_speedy_fans_count()

    def increment_speedy_fans_count(self):
        speedy_count = int(self.variables['speedy_fans_count'])
        speedy_count = speedy_count + 1
        self.variables['speedy_fans_count'] = str(speedy_count)
        ActionSyslog('Number of fans at max/fast speed are : ' +
                     str(speedy_count))

    def set_actions(self, fanname):
        self.logger.debug("+++ CALLBACK: FAN SPEED - MAX/FAST!")
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
        ActionSyslog('Fan ' + fanname + ' speed is max/fast')
        ActionCLI('show environment fan')

    def fans_speed_action_normal(self, event):
        if self.get_alert_level() is not None:
            self.logger.debug("********NORMAL********")
            self.logger.debug('LABEL = ' + event['labels'])
            label = event['labels']
            fanname = label.split(',')[0].split('=')[1]

            # delete fanname which moved to normal/medium/slow speed
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
                ActionSyslog('Fan ' + fanname +
                             ' speed back to normal/medium/slow')
                speedy_count = int(self.variables['speedy_fans_count'])
                speedy_count = speedy_count - 1
                self.variables['speedy_fans_count'] = str(speedy_count)
                if self.variables['speedy_fans_count'] != '0':
                    ActionSyslog('Remaining fans at max/fast speed are :  ' +
                                 str(speedy_count))
                if self.variables['fans_list'] == '':
                    self.set_agent_status_normal()

    def set_agent_status_normal(self):
        self.remove_alert_level()
        ActionSyslog('All fans are at normal speed')

    def on_agent_restart(self, event):
        self.remove_alert_level()
