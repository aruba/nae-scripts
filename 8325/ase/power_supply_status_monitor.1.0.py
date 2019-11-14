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
    'Name': 'power_supply_status_monitor',
    'Description': 'System Power Supply status monitoring agent',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        chassis_subsys_name = '1'

        uri1 = '/rest/v1/system/subsystems/chassis/%s/power_supplies/*?' \
               'attributes=status' % chassis_subsys_name
        self.m1 = Monitor(uri1, 'PSU status')

        self.r1 = Rule('PSU status: OK')
        self.r1.condition('{} == "ok"', [self.m1])
        self.r1.action(self.psu_status_ok)

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

        # fault_absent state not considered since it means PSU is absent

        self.variables['critical_psu'] = ''
        self.variables['warning_psu'] = ''

    def psu_status_fault_input(self, event):
        label = event['labels']
        self.psu_action_critical(label, 'Input Fault')

    def psu_status_fault_output(self, event):
        label = event['labels']
        self.psu_action_critical(label, 'Output Fault')

    def psu_status_unknown(self, event):
        label = event['labels']
        self.psu_action_warning(label, 'Unknown')

    def psu_status_unsupported(self, event):
        label = event['labels']
        self.psu_action_warning(label, 'Unsupported')

    def psu_status_warning(self, event):
        label = event['labels']
        self.psu_action_warning(label, 'Warning')

    def psu_action_critical(self, label, psu_state):
        self.logger.debug("======= PSU CRITICAL ============")
        self.logger.debug('label: [' + label + ']')
        _, psu = label.split(',')[0].split('=')
        self.logger.debug('psu - ' + psu)
        critical_psu = self.variables['critical_psu']
        self.logger.debug('critical_psu before: [' + critical_psu + ']')
        if psu not in critical_psu:
            critical_psu = critical_psu + psu
            self.variables['critical_psu'] = critical_psu
            ActionSyslog(psu + ' status: ' + psu_state)
            ActionCLI('show environment power-supply')
            if self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
        self.logger.debug('critical_psu after: [' + critical_psu + ']')
        self.logger.debug("========= /PSU CRITICAL  ========")

    def psu_action_warning(self, label, psu_state):
        self.logger.debug("======= PSU WARNING ============")
        self.logger.debug('label: [' + label + ']')
        _, psu = label.split(',')[0].split('=')
        self.logger.debug('psu - ' + psu)
        warning_psu = self.variables['warning_psu']
        self.logger.debug('warning_psu before: [' + warning_psu + ']')
        if psu not in warning_psu:
            warning_psu = warning_psu + psu
            self.variables['warning_psu'] = warning_psu
            ActionSyslog(psu + ' status: ' + psu_state)
            ActionCLI('show environment power-supply')
            if self.get_alert_level() is None:
                self.set_alert_level(AlertLevel.MINOR)
        self.logger.debug('warning_psu after: [' + warning_psu + ']')
        self.logger.debug("========= /PSU WARNING  ========")

    def psu_status_ok(self, event):
        self.logger.debug("======= PSU OK =========")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, psu = label.split(',')[0].split('=')
        self.logger.debug('psu - ' + psu)
        critical_psu = self.variables['critical_psu']
        warning_psu = self.variables['warning_psu']
        self.logger.debug('critical_psu before: [' + critical_psu + ']')
        self.logger.debug('warning_psu before: [' + warning_psu + ']')
        if psu in critical_psu:
            critical_psu = critical_psu.replace(psu, '')
            self.variables['critical_psu'] = critical_psu
            ActionSyslog(psu + ' status: OK')
            if not critical_psu:
                if not warning_psu:
                    if self.get_alert_level() is not None:
                        ActionSyslog('All PSU status is now OK')
                        self.remove_alert_level()
                else:
                    if self.get_alert_level() is not None:
                        self.set_alert_level(AlertLevel.MINOR)
        elif psu in warning_psu:
            warning_psu = warning_psu.replace(psu, '')
            self.variables['warning_psu'] = warning_psu
            ActionSyslog(psu + ' status is OK')
            if not warning_psu:
                if not critical_psu:
                    if self.get_alert_level() is not None:
                        ActionSyslog('All PSU status is now OK')
                        self.remove_alert_level()
        self.logger.debug('critical_psu after: [' + warning_psu + ']')
        self.logger.debug('warning_psu after: [' + warning_psu + ']')
        self.logger.debug("========= /PSU OK  ========")
