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
    'Name': 'fans_status_fault_monitor',
    'Description': 'Agent to monitor status of all fans',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Policy(NAE):

    def __init__(self):
        self.variables['fans_list'] = ''
        self.variables['faulty_fans_count'] = '0'

        uri1 = '/rest/v1/system/subsystems/*/*/fans/*?attributes=status'
        self.m1 = Monitor(uri1, 'Fan Status')
        self.r1 = Rule('Fan Status - Fault')
        self.r1.condition('{} == "fault"', [self.m1])
        self.r1.action(self.fans_status_action_fault)
        self.r1.clear_action(self.fans_status_action_normal)

    def fans_status_action_fault(self, event):
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
        self.increment_faulty_fans_count()

    def increment_faulty_fans_count(self):
        faulty_count = int(self.variables['faulty_fans_count'])
        faulty_count = faulty_count + 1
        self.variables['faulty_fans_count'] = str(faulty_count)
        ActionSyslog('Number of faulty fans are : ' + str(faulty_count))

    def set_actions(self, fanname):
        self.logger.debug("+++ CALLBACK: FAN STATUS - FAULT!")
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
        ActionSyslog('Fan ' + fanname + ' is Faulty ')
        ActionCLI('show environment fan')

    def fans_status_action_normal(self, event):
        if self.get_alert_level() is not None:
            self.logger.debug("********NORMAL********")
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
                faulty_count = int(self.variables['faulty_fans_count'])
                faulty_count = faulty_count - 1
                self.variables['faulty_fans_count'] = str(faulty_count)
                if self.variables['faulty_fans_count'] != '0':
                    ActionSyslog('Remaining fans in faulty status are :  ' +
                                 str(faulty_count))
                if self.variables['fans_list'] == '':
                    self.set_agent_status_normal()

    def set_agent_status_normal(self):
        self.remove_alert_level()
        ActionSyslog('All fans status are ok')
