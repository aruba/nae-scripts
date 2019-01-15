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
    'Name': 'power_supply_status_transition_monitor',
    'Description': 'System Power Supply status transition monitoring agent',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Policy(NAE):

    def __init__(self):

        uri1 = '/rest/v1/system/subsystems/chassis/base/power_supplies/*?' \
               'attributes=status'
        self.m1 = Monitor(uri1, 'PSU status')

        self.r1 = Rule('PSU status transition: OK to Output Fault')
        self.r1.condition(
            'transition {} from "ok" to "fault_output"',
            [self.m1])
        self.r1.action(self.status_ok_to_fault_output)

        self.r2 = Rule('PSU status transition: OK to Input Fault')
        self.r2.condition(
            'transition {} from "ok" to "fault_input"',
            [self.m1])
        self.r2.action(self.status_ok_to_fault_input)

        self.r3 = Rule('PSU status transition: OK to Warning')
        self.r3.condition('transition {} from "ok" to "warning"', [self.m1])
        self.r3.action(self.status_ok_to_warning)

        self.r4 = Rule('PSU status transition: Output Fault to OK')
        self.r4.condition(
            'transition {} from "fault_output" to "ok"',
            [self.m1])
        self.r4.action(self.status_fault_output_to_ok)

        self.r5 = Rule('PSU status transition: Input Fault to OK')
        self.r5.condition(
            'transition {} from "fault_input" to "ok"',
            [self.m1])
        self.r5.action(self.status_fault_input_to_ok)

        self.r6 = Rule('PSU status transition: Output Fault to OK')
        self.r6.condition(
            'transition {} from "fault_output" to "ok"',
            [self.m1])
        self.r6.action(self.status_fault_output_to_ok)

        self.r7 = Rule('PSU status transition: Warning to OK')
        self.r7.condition('transition {} from "warning" to "ok"', [self.m1])
        self.r7.action(self.status_warning_to_ok)

        self.r8 = Rule('PSU status transition: Unknown to OK')
        self.r8.condition('transition {} from "unknown" to "ok"', [self.m1])
        self.r8.action(self.status_unknown_to_ok)

        self.r9 = Rule('PSU status transition: OK to Unknown')
        self.r9.condition('transition {} from "ok" to "unknown"', [self.m1])
        self.r9.action(self.status_ok_to_unknown)

        self.r10 = Rule('PSU status transition: Absent to OK')
        self.r10.condition(
            'transition {} from "fault_absent" to "ok"',
            [self.m1])
        self.r10.action(self.status_fault_absent_to_ok)

        self.r11 = Rule('PSU status transition: OK to Absent')
        self.r11.condition(
            'transition {} from "ok" to "fault_absent"',
            [self.m1])
        self.r11.action(self.status_ok_to_fault_absent)

    def status_ok_to_fault_input(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'OK to Input Fault')

    def status_ok_to_fault_output(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'OK to Output Fault')

    def status_ok_to_warning(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'OK to Warning')

    def status_fault_input_to_ok(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'Input Fault to OK')

    def status_fault_output_to_ok(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'Output Fault to OK')

    def status_warning_to_ok(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'Warning to OK')

    def status_unknown_to_ok(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'Unknown to OK')

    def status_ok_to_unknown(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'OK to Unknown')

    def status_fault_absent_to_ok(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'Absent to OK')

    def status_ok_to_fault_absent(self, event):
        label = event['labels']
        self.psu_transition_action(label, 'OK to Absent')

    def psu_transition_action(self, label, transition):
        self.logger.debug("======= PSU TRANSITION ============")
        self.logger.debug('label: [' + label + ']')
        _, psu = label.split(',')[0].split('=')
        self.logger.debug('psu - ' + psu)
        ActionSyslog(psu + ' status transition: ' + transition)
        ActionCLI('show environment power-supply')
        self.logger.debug("========= /PSU TRANSITION  ========")
