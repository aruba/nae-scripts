# -*- coding: utf-8 -*-
#
# (c) Copyright 2018-2019 Hewlett Packard Enterprise Development LP
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
    'Name': 'power_supply_monitor',
    'Description': 'System Power Supply Unit (PSU) status and '
                   'statistics monitoring agent',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'power_supply_unit': {
        'Name': 'Power Supply Unit (PSU) name to monitor '
                'status and statistics',
        'Description': 'Power Supply Unit name (PSU) to monitor '
                       'status and statistics',
        'Type': 'string',
        'Default': '1/1'
    }
}


class Agent(NAE):

    def __init__(self):
        chassis_subsys_name = '1'

        uri1 = '/rest/v1/system/subsystems/chassis/%s/power_supplies/{}?' \
               'attributes=status' % chassis_subsys_name
        self.m1 = Monitor(
            uri1,
            'Status',
            [self.params['power_supply_unit']])

        self.r1 = Rule('PSU status: Absent')
        self.r1.condition('{} == "fault_absent"', [self.m1])
        self.r1.action(self.psu_status_fault_absent)

        self.r2 = Rule('PSU status: Unknown')
        self.r2.condition('{} == "unknown"', [self.m1])
        self.r2.action(self.psu_status_unknown)

        self.r3 = Rule('PSU status: Input Fault')
        self.r3.condition('{} == "fault_input"', [self.m1])
        self.r3.action(self.psu_status_fault_input)

        self.r4 = Rule('PSU status: Output Fault')
        self.r4.condition('{} == "fault_output"', [self.m1])
        self.r4.action(self.psu_status_fault_output)

        self.r5 = Rule('PSU status: Unsupported')
        self.r5.condition('{} == "unsupported"', [self.m1])
        self.r5.action(self.psu_status_unsupported)

        self.r6 = Rule('PSU status: Warning')
        self.r6.condition('{} == "warning"', [self.m1])
        self.r6.action(self.psu_status_warning)

        self.r7 = Rule('PSU status: OK')
        self.r7.condition('{} == "ok"', [self.m1])
        self.r7.action(self.psu_status_ok)

        uri2 = '/rest/v1/system/subsystems/chassis/%s/power_supplies/{}?' \
               'attributes=statistics.warnings' % chassis_subsys_name
        self.m2 = Monitor(
            uri2,
            'Warnings (Warnings/Failures)',
            [self.params['power_supply_unit']])

        uri3 = '/rest/v1/system/subsystems/chassis/%s/power_supplies/{}?' \
               'attributes=statistics.failures' % chassis_subsys_name
        self.m3 = Monitor(
            uri3,
            'Failures (Warnings/Failures)',
            [self.params['power_supply_unit']])

        self.variables['psu_status'] = 'ok'

    def psu_status_fault_absent(self, event):
        psu_status = self.variables['psu_status']
        if psu_status != 'fault_absent':
            self.variables['psu_status'] = 'fault_absent'
            self.action_critical('Absent')

    def psu_status_fault_input(self, event):
        psu_status = self.variables['psu_status']
        if psu_status != 'fault_input':
            self.variables['psu_status'] = 'fault_input'
            self.action_critical('Input Fault')

    def psu_status_fault_output(self, event):
        psu_status = self.variables['psu_status']
        if psu_status != 'fault_output':
            self.variables['psu_status'] = 'fault_output'
            self.action_critical('Output Fault')

    def psu_status_unknown(self, event):
        psu_status = self.variables['psu_status']
        if psu_status != 'unknown':
            self.variables['psu_status'] = 'unknown'
            self.action_critical('Unknown')

    def psu_status_unsupported(self, event):
        psu_status = self.variables['psu_status']
        if psu_status != 'unsupported':
            self.variables['psu_status'] = 'unsupported'
            self.action_critical('Unsupported')

    def action_critical(self, psustatus):
        ActionSyslog(
            '{} status: ' + psustatus,
            [self.params['power_supply_unit']])
        ActionCLI('show environment power-supply')
        self.set_alert_level(AlertLevel.CRITICAL)

    def psu_status_warning(self, event):
        psu_status = self.variables['psu_status']
        if psu_status != 'warning':
            self.variables['psu_status'] = 'warning'
            ActionSyslog(
                '{} status: Warning',
                [self.params['power_supply_unit']])
            ActionCLI('show environment power-supply')
            self.set_alert_level(AlertLevel.MINOR)

    def psu_status_ok(self, event):
        if self.get_alert_level() is not None:
            self.variables['psu_status'] = 'ok'
            ActionSyslog(
                '{} status: OK',
                [self.params['power_supply_unit']])
            self.remove_alert_level()
