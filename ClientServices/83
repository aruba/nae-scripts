# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Hewlett Packard Enterprise Development LP
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
    'Name': 'client_services_health',
    'Description': 'Client Service Health monitoring',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'DHCP_Server_IP': {
        'Name': 'IP address of the DHCP Server',
        'Description': 'IP address of the DHCP Server ',
        'Type': 'string',
        'Default': '0.0.0.0'
    }
}


class Agent(NAE):

    def __init__(self):
        # A list of anomaly ratios detected on ports.
        self.variables['ports'] = ''
        self.variables['port'] = ''
        self.variables['ratio'] = ''
        client_uri = '/rest/v1/system/ports/*?' \
            'attributes=dhcp_relay_statistics.valid_v4client_requests'
        self.client_monitor = Monitor(
            Rate(client_uri, "60 seconds"),
            "DHCP Relay Valid Client Requests")

        server_uri = '/rest/v1/system/ports/*?' \
            'attributes=dhcp_relay_statistics.valid_v4server_responses'
        self.server_monitor = Monitor(
            Rate(server_uri, "60 seconds"),
            "DHCP Relay Valid Server Responses")
        self.r1 = Rule("DHCP relay Request/Response ratio")
        self.r1.condition(
            "ratio of {} and {} > 1.1", [
                self.client_monitor, self.server_monitor])
        self.r1.action(self.ratio_anomaly_callback)
        # Clear DHCP Condition.
        self.r2 = Rule("Clear DHCP relay Request/Response ratio")
        self.r2.condition(
            "ratio of {} and {} <= 1.1", [
                self.client_monitor, self.server_monitor])
        self.r2.action(self.ratio_normal_callback)

    def ratio_anomaly_callback(self, event):
        self.update_alert_level(AlertLevel=AlertLevel.CRITICAL)
        self.collect_event_data(event)
        # Update WebUI
        self.logger.debug(
            "Anomaly Raito: %s, detected on Port: %s" %
            (self.variables['ratio'], self.variables['port']))
        ActionCLI("show dhcp-relay")
        ActionSyslog(
            'DHCP request/response anomaly ratio: %s on Port: %s' %
            (self.variables['ratio'], self.variables['port']))
        ActionCLI("ping {}", [self.params['DHCP_Server_IP']])
        self.logger.debug("before adding %s" % self.variables['ports'])
        if self.variables['port'] not in self.variables['ports']:
            port_list = self.variables['ports']
            # Update the ports list.
            self.variables['ports'] = port_list + self.variables['port']
            self.logger.debug("after adding %s" % self.variables['ports'])

    def ratio_normal_callback(self, event):
        self.collect_event_data(event)
        port_list = self.variables['ports']
        if self.variables['port'] in self.variables['ports']:
            # Update WebUI
            ActionSyslog(
                'DHCP request/response ratio back to normal on Port: %s' %
                (self.variables['port']))
            # Update the ports list.
            self.logger.debug("before delete %s" % self.variables['ports'])
            port_list = port_list.replace(self.variables['port'], '')
            self.logger.debug("after delete %s" % self.variables['ports'])
            self.variables['ports'] = port_list
            self.logger.debug(self.variables['ports'])
            if not self.variables['ports']:
                self.update_alert_level(AlertLevel=AlertLevel.NONE)

    def collect_event_data(self, event):
        event_data = event['labels']
        port_data = event_data.split(",")[0]
        _, self.variables['port'] = port_data.split("=")
        self.variables['ratio'] = event['value']

    def update_alert_level(self, AlertLevel):
        if self.get_alert_level() is not AlertLevel:
            self.set_alert_level(AlertLevel)
            self.logger.debug("Current alert level: %s" %
                              (str(self.get_alert_level())))
