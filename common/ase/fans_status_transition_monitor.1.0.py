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
    'Name': 'fans_status_transition_monitor',
    'Description': 'Agent to monitor status of all fans, '
                   'wherein the transition between different '
                   'status(uninitialized/ok/fault) is monitored.'
                   'The agent status is set to Critical when any '
                   'of the fan status has transition from '
                   'uninitialized/ok to fault. The agent status '
                   'remains in Critical state, when other fans '
                   'status transits to fault, and syslog and cli '
                   'are displayed. The agent status is set back '
                   'to normal when all the fans are in '
                   'uninitialized/ok status.',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        self.variables['fans_list'] = ''

        uri1 = '/rest/v1/system/subsystems/*/*/fans/*?attributes=status'
        self.m1 = Monitor(uri1, 'Fan Status')

        self.r1 = Rule('Status - ok -> fault')
        self.r1.condition(
            'transition {} from "ok" to "fault"', [self.m1])
        self.r1.action(self.fans_status_action_fault)

        self.r2 = Rule('Status - uninitialized -> fault')
        self.r2.condition(
            'transition {} from "uninitialized" to "fault"', [self.m1])
        self.r2.action(self.fans_status_action_fault)

        self.r3 = Rule('Status - empty -> fault')
        self.r3.condition(
            'transition {} from "empty" to "fault"', [self.m1])
        self.r3.action(self.fans_status_action_fault)

        self.r4 = Rule('Status - fault -> ok')
        self.r4.condition(
            'transition {} from "fault" to "ok"', [self.m1])
        self.r4.action(self.fans_status_action_normal)

        self.r5 = Rule('Status - fault -> uninitialized')
        self.r5.condition(
            'transition {} from "fault" to "uninitialized"', [self.m1])
        self.r5.action(self.fans_status_action_normal)

        self.r6 = Rule('Status - fault -> empty')
        self.r6.condition(
            'transition {} from "fault" to "empty"', [self.m1])
        self.r6.action(self.fans_status_action_normal)

    def fans_status_action_fault(self, event):
        self.logger.debug("********TRANSITION TO FAULT********")
        self.logger.debug('LABEL = ' + event['labels'])
        label = event['labels']
        fanname = label.split(',')[0].split('=')[1]

        self.logger.debug('fanname= ' + fanname)
        if self.variables['fans_list'] != '':
            fans_list = fanname + self.variables['fans_list']
            self.variables['fans_list'] = fans_list
        else:
            self.variables['fans_list'] = fanname
        self.logger.debug('list of fans =  ' +
                          self.variables['fans_list'])
        self.set_actions(fanname)

    def set_actions(self, fanname):
        self.logger.debug("+++ CALLBACK: FAN STATUS - FAULT!")
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
        ActionSyslog('Fan ' + fanname + ' is Faulty ')
        ActionCLI('show environment fan')

    def fans_status_action_normal(self, event):
        if self.get_alert_level() is not None:
            self.logger.debug("********TRANSITION TO NORMAL********")
            self.logger.debug('LABEL = ' + event['labels'])
            label = event['labels']
            fanname = label.split(',')[0].split('=')[1]

            # delete fanname which moved to ok state
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
                ActionSyslog('Fan ' + fanname + ' back to ok')
                if self.variables['fans_list'] == '':
                    self.set_agent_status_normal()

    def set_agent_status_normal(self):
        self.remove_alert_level()
        ActionSyslog('All fans status are ok')

    def on_agent_restart(self, event):
        self.remove_alert_level()
