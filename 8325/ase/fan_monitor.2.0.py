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
    'Name': 'fan_monitor',
    'Description': 'Agent to monitor status, speed '
                   'and rpm of a given fan',
    'Version': '2.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'fan_name': {
        'Name': 'Fan name to be monitored',
        'Description': 'Fan name to monitor various attributes like '
                       'speed, status and rpm value of a given fan',
        'Type': 'string',
        'Default': 'LC1-1L'
    }
}


class Agent(NAE):

    def __init__(self):
        # analyze status of a given fan
        self.variables['fan_status'] = '0'
        uri1 = '/rest/v1/system/subsystems/line_card/*/' \
               'fans/{}?attributes=status'
        self.m1 = Monitor(uri1, 'Fan Status',
                          [self.params['fan_name']])

        self.r1 = Rule('Fan is Faulty')
        self.r1.condition('{} == "fault"', [self.m1])
        self.r1.action(self.fan_status_action_fault)

        self.r2 = Rule('Fan is OK')
        self.r2.condition('{} == "ok"', [self.m1])
        self.r2.action(self.fan_status_action_normal)

        self.r3 = Rule('Fan is Uninitialized')
        self.r3.condition('{} == "uninitialized"', [self.m1])
        self.r3.action(self.fan_status_action_normal)

        # analyze speed of a given fan
        self.variables['fan_fast'] = '0'
        self.variables['fan_max'] = '0'

        uri2 = '/rest/v1/system/subsystems/line_card/*/' \
               'fans/{}?attributes=speed'
        self.m2 = Monitor(uri2, 'Fan Speed',
                          [self.params['fan_name']])

        self.r4 = Rule('Fan Speed is Normal')
        self.r4.condition('{} == "normal"', [self.m2])
        self.r4.action(self.fan_speed_action_normal)

        self.r5 = Rule('Fan Speed is Medium')
        self.r5.condition('{} == "medium"', [self.m2])
        self.r5.action(self.fan_speed_action_normal)

        self.r6 = Rule('Fan Speed is Fast')
        self.r6.condition('{} == "fast"', [self.m2])
        self.r6.action(self.fan_speed_action_fast)

        self.r7 = Rule('Fan Speed is Max')
        self.r7.condition('{} == "max"', [self.m2])
        self.r7.action(self.fan_speed_action_max)

        self.r8 = Rule('Fan Speed is Slow')
        self.r8.condition('{} == "slow"', [self.m2])
        self.r8.action(self.fan_speed_action_normal)

        # analyze rpm of a given fan
        uri3 = '/rest/v1/system/subsystems/line_card/*/' \
               'fans/{}?attributes=rpm'
        self.m3 = Monitor(uri3, 'Fan RPM',
                          [self.params['fan_name']])

    def fan_status_action_fault(self, event):
        if self.get_alert_level() is None:
            if self.variables['fan_status'] == '0':
                self.fan_set_alert(2, 'Fan {} is Faulty')
                self.variables['fan_status'] = '1'
        elif self.get_alert_level() == AlertLevel.MAJOR:
            if self.variables['fan_status'] == '0':
                self.fan_set_alert(2, 'Fan {} is Faulty '
                                   'and running fast')
                self.variables['fan_status'] = '1'
        elif self.get_alert_level() == AlertLevel.CRITICAL:
            if self.variables['fan_status'] == '0':
                self.fan_set_alert(0, 'Fan {} is Faulty '
                                   'and running at max speed')
                self.variables['fan_status'] = '1'

    def fan_speed_action_fast(self, event):
        if self.get_alert_level() is None:
            if self.variables['fan_fast'] == '0':
                self.fan_set_alert(
                    1, 'Fan {} is running fast')
                self.variables['fan_fast'] = '1'
        elif self.get_alert_level() == AlertLevel.CRITICAL and \
                self.variables['fan_max'] == '1' and \
                self.variables['fan_status'] == '0':
            if self.variables['fan_fast'] == '0':
                self.fan_set_alert(1, 'Fan {} speed now '
                                   'reduced from max to fast')
                self.variables['fan_fast'] = '1'
                self.variables['fan_max'] = '0'
        elif self.get_alert_level() == AlertLevel.CRITICAL and \
                self.variables['fan_max'] == '1' and \
                self.variables['fan_status'] == '1':
            if self.variables['fan_fast'] == '0':
                self.fan_set_alert(0, 'Fan {} speed is reduced '
                                   'to fast and also faulty')
                self.variables['fan_max'] = '0'
                self.variables['fan_fast'] = '1'
        elif self.get_alert_level() == AlertLevel.CRITICAL and \
                self.variables['fan_max'] == '0' and \
                self.variables['fan_status'] == '1':
            if self.variables['fan_fast'] == '0':
                self.fan_set_alert(0, 'Fan {} is running '
                                   'fast and also faulty')
                self.variables['fan_fast'] = '1'

    def fan_speed_action_max(self, event):
        if self.get_alert_level() is None:
            if self.variables['fan_max'] == '0':
                self.fan_set_alert(2, 'Fan {} is at max speed')
                self.variables['fan_max'] = '1'
        elif self.get_alert_level() == AlertLevel.MAJOR:
            if self.variables['fan_max'] == '0':
                self.fan_set_alert(2, 'Fan {} speed is increased '
                                   'to Maximum')
                self.variables['fan_max'] = '1'
                self.variables['fan_fast'] = '0'
        elif self.variables['fan_max'] == '0' and \
                self.get_alert_level() == AlertLevel.CRITICAL:
            self.fan_set_alert(0, 'Fan {} is at maximum speed '
                               'and status is faulty')
            self.variables['fan_max'] = '1'
            self.variables['fan_fast'] = '0'

    def fan_status_action_normal(self, event):
        if self.get_alert_level() is not None:
            if self.variables['fan_status'] == '1':
                if self.variables['fan_fast'] == '1':
                    self.fan_set_alert(1, 'Fan {} status is ok '
                                       'and running fast')
                    self.variables['fan_status'] = '0'
                elif self.variables['fan_max'] == '1':
                    self.variables['fan_status'] = '0'
                    self.fan_set_alert(0, 'Fan {} status is ok '
                                       'and speed is max')
                else:
                    self.remove_alert_level()
                    self.variables['fan_status'] = '0'
                    ActionSyslog('Fan {} status back to OK. '
                                 'Status is Ok/ Uninitialized',
                                 [self.params['fan_name']])

    def fan_speed_action_normal(self, event):
        if self.get_alert_level() is not None:
            if self.variables['fan_status'] != '1':
                if self.variables['fan_fast'] == '1' or \
                        self.variables['fan_max'] == '1':
                    ActionSyslog('Fan {} is back to normal speed. '
                                 'Speed is normal/medium/slow.',
                                 [self.params['fan_name']])
                    self.remove_alert_level()
                    self.variables['fan_fast'] = '0'
                    self.variables['fan_max'] = '0'
            elif self.variables['fan_fast'] == '1':
                self.variables['fan_fast'] = '0'
                ActionSyslog(
                    'Fan {} is back to normal speed, but faulty',
                    [self.params['fan_name']])
            elif self.variables['fan_max'] == '1':
                self.variables['fan_max'] = '0'
                ActionSyslog(
                    'Fan {} is back to normal speed, but faulty',
                    [self.params['fan_name']])

    def fan_set_alert(self, alertlevel, actionlog):
        if alertlevel == 1:
            self.set_alert_level(AlertLevel.MAJOR)
        elif alertlevel == 2:
            self.set_alert_level(AlertLevel.CRITICAL)
        ActionSyslog(actionlog, [self.params['fan_name']])
        ActionCLI('show environment fan')
