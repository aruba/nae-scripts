# -*- coding: utf-8 -*-
#
# Copyright (c) 2018-2019 Hewlett Packard Enterprise Development LP
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
    'Name': 'lag_health_monitor',
    'Description': 'LAG status monitoring agent using PSPO',
    'Version': '2.0',
    'Author': 'Aruba Networks'
}


ParameterDefinitions = {
    'lag_name_1': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    },
    'lag_name_2': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    },
    'lag_name_3': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    },
    'lag_name_4': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    },
    'lag_name_5': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    },
    'lag_name_6': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    },
    'lag_name_7': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    },
    'lag_name_8': {
        'Name': 'Name of the LAG to be monitored',
        'Description': 'Name of the LAG for which status is to be monitored',
        'Type': 'string',
        'Default': ''
    }
}


class Agent(NAE):

    def __init__(self):
        # Critical lag(s) list.
        self.variables['critical_lags'] = ''
        # forwarding_state.forwarding var.
        self.variables['forwarding'] = ''
        # forwarding_state.blocking_layer var.
        self.variables['blocked_by_aggregation'] = ''

        self.setup_lag_status_monitors()

    def setup_lag_status_monitors(self):
        for i in range(1, 9):
            lag_var = 'lag_name_' + str(i)
            lag_value = self.params[lag_var].value
            if lag_value:
                lag_fwd_var = 'lag_fwd' + str(i)
                uri1 = '/rest/v1/system/ports/{}?' \
                       'attributes=forwarding_state.forwarding'
                lag_fwd_monitor = Monitor(
                    uri1,
                    'LAG Forwarding State',
                    [self.params[lag_var]])
                setattr(self, lag_fwd_var, lag_fwd_monitor)

                lag_rule_var_1 = 'lag_rule_1' + str(i)
                lag_rule_1 = Rule('Port Forwarding is false')
                lag_rule_1.condition(
                    'transition {} from "true" to "false"',
                    [lag_fwd_monitor])
                lag_rule_1.action(self.status_transition_action)
                setattr(self, lag_rule_var_1, lag_rule_1)

                lag_rule_var_2 = 'lag_rule_2' + str(i)
                lag_rule_2 = Rule('Port Forwarding is back to normal')
                lag_rule_2.condition(
                    'transition {} from "false" to "true"',
                    [lag_fwd_monitor])
                lag_rule_2.action(self.status_transition_action)
                setattr(self, lag_rule_var_2, lag_rule_2)

                lag_blk_var = 'lag_blk' + str(i)
                uri3 = '/rest/v1/system/ports/{}?' \
                       'attributes=forwarding_state.blocking_layer'
                lag_blk_monitor = Monitor(
                    uri3,
                    'Port Blocking Layer',
                    [self.params[lag_var]])
                setattr(self, lag_blk_var, lag_blk_monitor)

                lag_rule_var_3 = 'lag_rule_3' + str(i)
                lag_rule_3 = Rule(
                    'Forwarding state is blocked by AGGREGATION layer')
                lag_rule_3.condition('{} == "AGGREGATION"', [lag_blk_monitor])
                lag_rule_3.action(self.blocking_layer_action)
                setattr(self, lag_rule_var_3, lag_rule_3)

                lag_rule_var_4 = 'lag_rule_4' + str(i)
                lag_rule_4 = Rule(
                    'Forwarding state is not blocked by AGGREGATION layer')
                lag_rule_4.condition('{} != "AGGREGATION"', [lag_blk_monitor])
                lag_rule_4.action(self.blocking_layer_normal)
                setattr(self, lag_rule_var_4, lag_rule_4)

    def status_transition_action(self, event):
        lag_data = event['labels']
        lag_data = lag_data.split(",")[0]
        _, lag_id = lag_data.split("=")
        event_data = event['value']
        self.logger.info(event['value'])
        self.variables['forwarding'] = str(event_data)
        self.logger.info("forwarding:" + str(self.variables['forwarding']))
        self.report_alert_status(lag_id)

    def blocking_layer_action(self, event):
        lag_data = event['labels']
        lag_data = lag_data.split(",")[0]
        _, lag_id = lag_data.split("=")
        self.variables['blocked_by_aggregation'] = 'true'
        self.logger.info(
            "Blocking layer:" + str(self.variables['blocked_by_aggregation']))
        self.report_alert_status(lag_id)

    def blocking_layer_normal(self, event):
        lag_data = event['labels']
        lag_data = lag_data.split(",")[0]
        _, lag_id = lag_data.split("=")
        self.variables['blocked_by_aggregation'] = 'false'
        self.report_alert_status(lag_id)

    def report_alert_status(self, lag_id):
        if (self.variables['forwarding'] == 'false') and \
                (self.variables['blocked_by_aggregation'] == 'true'):
            self.update_alert_level(AlertLevel=AlertLevel.CRITICAL)

            if lag_id not in self.variables['critical_lags']:
                critical_lag_list = self.variables['critical_lags']
                # Adding lag_id to critical lag(s) list.
                self.variables['critical_lags'] = critical_lag_list + lag_id
                self.logger.debug(str(self.variables['critical_lags']))
                ActionSyslog('%s is down' % (lag_id))
                ActionCLI('show lacp aggregates %s' % (lag_id))
        else:
            if lag_id in self.variables['critical_lags']:
                critical_lag_list = self.variables['critical_lags']
                # Removing lag_id from critical lag(s) list.
                critical_lag_list = critical_lag_list.replace(lag_id, '')
                self.variables['critical_lags'] = critical_lag_list
                self.logger.debug(
                    'Unset the previous status for lag id' + lag_id)
                ActionSyslog('%s is up' % (lag_id))
                self.logger.debug(self.variables['critical_lags'])
                if not self.variables['critical_lags']:
                    self.update_alert_level(AlertLevel=AlertLevel.NONE)

    def update_alert_level(self, AlertLevel):
        if self.get_alert_level() is not AlertLevel:
            self.set_alert_level(AlertLevel)
            self.logger.debug('CURRENT ALERT LEVEL:' +
                              str(self.get_alert_level()))
