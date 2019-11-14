# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2019 Hewlett Packard Enterprise Development LP
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
    'Name': 'interface_link_flap_monitor',
    'Description': 'Interface Link Flap Monitoring Agent',
    'Version': '1.2',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'link_flap_rate_threshold': {
        'Name': 'Link flapping rate threshold level indicating '
                'anomalous behavior',
        'Description': 'This parameter specifies the threshold for rate of'
                       ' link state resets per second, calculated every 10'
                       ' seconds. Rate of link state resets above this'
                       ' threshold is anomalous for the link. Adjust this'
                       ' level to match the expected level of link flap rate'
                       ' for the interface. The default value is 0.1.',
        'Type': 'float',
        'Default': 0.1
    }
}


class Agent(NAE):

    def __init__(self):

        # Link resets
        uri1 = '/rest/v1/system/interfaces/*?attributes=link_resets'
        rate_uri = Rate(uri1, '10 seconds')
        self.m1 = Monitor(
            rate_uri,
            'Interface Link Resets Rate')
        self.r1 = Rule('Link state resets rate anomaly')
        self.r1.condition(
            '{} > {}', [self.m1, self.params['link_flap_rate_threshold']])
        self.r1.action(self.action_interface_flapping_anomaly)
        self.r1.clear_condition(
            '{} < {}', [self.m1, self.params['link_flap_rate_threshold']])
        self.r1.clear_action(self.return_to_normal)

        # variables
        self.variables['flapping_links'] = ''

    def action_interface_flapping_anomaly(self, event):
        self.logger.debug("================ Flapping ================")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, interface_id = label.split(',')[0].split('=')
        self.logger.debug('interface_id - ' + interface_id)
        flapping_links = self.variables['flapping_links']
        self.logger.debug('flapping_links before: [' + flapping_links + ']')
        if (interface_id + ':') not in flapping_links:
            flapping_links = flapping_links + interface_id + ':'
            self.variables['flapping_links'] = flapping_links
            ActionSyslog('Link state resets rate anomaly occured on interface '
                         + interface_id)
            if self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)
        self.logger.debug('flapping_links after: [' + flapping_links + ']')
        self.logger.debug("================ /Flapping ================")

    def return_to_normal(self, event):
        self.logger.debug("================ Normal ================")
        label = event['labels']
        self.logger.debug('label: [' + label + ']')
        _, interface_id = label.split(',')[0].split('=')
        self.logger.debug('interface_id - ' + interface_id)
        flapping_links = self.variables['flapping_links']
        self.logger.debug('flapping_links before: [' + flapping_links + ']')
        if (interface_id + ':') in flapping_links:
            flapping_links = flapping_links.replace((interface_id + ':'), '')
            self.variables['flapping_links'] = flapping_links
            self.logger.debug('flapping_links after: [' + flapping_links + ']')
            ActionSyslog('Interface '
                         + interface_id + ' Link state is back to NORMAL')
            if not flapping_links:
                if self.get_alert_level() is not None:
                    self.remove_alert_level()
        self.logger.debug('flapping_links after: [' + flapping_links + ']')
        self.logger.debug("================ /Normal ================")
