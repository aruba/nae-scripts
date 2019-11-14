# -*- coding: utf-8 -*-
#
# (c) Copyright 2018-2019 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from requests import get

Manifest = {
    'Name': 'vsx_health_monitor',
    'Description': 'VSX Health monitoring',
    'Version': '1.5',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'routes_count_ratio_lower_threshold': {
        'Name': 'Route count deviation lower threshold ',
        'Description': 'This parameter represent the lower threshold value up to '
                       'which the ratio between route count on the switch '
                       'and route count on the VSX peer switch is allowed to'
                       ' deviate.',
        'Type': 'float',
        'Default': '0.95',
    },
    'routes_count_ratio_upper_threshold': {
        'Name': 'Route count deviation upper threshold ',
        'Description': 'This parameter represent the upper threshold value up to '
                       'which the ratio between route count on the switch '
                       'and route count on the VSX peer switch is allowed to'
                       ' deviate.',
        'Type': 'float',
        'Default': '1.05',
    },
    'neighbors_count_ratio_lower_threshold': {
        'Name': 'Neighbors count deviation threshold ',
        'Description': 'This parameter represent the lower threshold value up to '
                       'which the ratio between neighbors count on the '
                       'switch and neighbors count on the VSX peer switch is '
                       'allowed to deviate.',
        'Type': 'float',
        'Default': '0.95',
    },
    'neighbors_count_ratio_upper_threshold': {
        'Name': 'Neighbors count deviation threshold ',
        'Description': 'This parameter represent the upper threshold value up to '
                       'which the ratio between neighbors count on the '
                       'switch and neighbors count on the VSX peer switch is '
                       'allowed to deviate.',
        'Type': 'float',
        'Default': '1.05',
    },
    'mac_addresses_count_ratio_lower_threshold': {
        'Name': 'MAC addresses count deviation lower threshold ',
        'Description': 'This parameter represent the lower threshold value up to '
                       'which the ratio between MAC addresses count on the '
                       'switch and MAC addresses count on the VSX peer switch '
                       'is allowed to deviate.',
        'Type': 'float',
        'Default': '0.95',
    },
    'mac_addresses_count_ratio_upper_threshold': {
        'Name': 'MAC addresses count deviation upper threshold ',
        'Description': 'This parameter represent the upper threshold value up to '
                       'which the ratio between MAC addresses count on the '
                       'switch and MAC addresses count on the VSX peer switch '
                       'is allowed to deviate.',
        'Type': 'float',
        'Default': '1.05',
    }
}

VSX_PEER = '/vsx-peer'
RESOURCE_URI_MAP = {
    'routes': '/rest/v1/system/vrfs/*/routes?count',
    'neighbors': '/rest/v1/system/vrfs/*/neighbors?count',
    'mac_addresses': '/rest/v1/system/bridge/vlans/*/macs?count'
}


def rest_get(url):
    """
    Performs a HTTP Get operation and returns the result of
    the operation.
    :param url: URL on which the GET operation needs to be
    done
    :return: Result of the HTTP GET operation.
    """
    return get(HTTP_ADDRESS + url, verify=False,
               proxies={'http': None, 'https': None})


class Agent(NAE):
    """
    This NAE Script sets up NAE Monitors to monitor the routes count,
    neighbors count and MAC addresses count on the switch the script is
    installed as well as on it's VSX-peer switch. It also creates NAE rules
    to calculate the ratio of the routes count, neighbors count and MAC
    addresses count on the switch and it's VSX-peer. It will create an alert
    when the ratio is outside the allowed deviation range.

    The script is designed to work on ArubaOS-CX 10.02.XXXX or above versions.
    """

    def __init__(self):

        # Set up the NAE Agent Monitors
        self.agent_monitors = self.create_monitors()

        # Setup the NAE Agent Rules
        self.set_rules(self.agent_monitors)

        # NAE variables to be used in solving the race condition that can be
        #  caused while setting and resetting of the Agent Alert Level by
        # the NAE Rules in the script.
        self.variables['routes_ratio'] = 'Normal'
        self.variables['neighbors_ratio'] = 'Normal'
        self.variables['mac_addresses_ratio'] = 'Normal'

    def create_monitors(self):
        """
        Creates NAE monitors for routes count, neighbors count and MAC
        addresses count on the switch and on the VSX-peer switch.

        Since this function creates NAE Monitors based on the keys of a
        dictionary and the NAE Python Framework demands a NAE Monitor to be
        defined as class variables, the function implementation needs to use
         the `setattr` function to make sure that all NAE Monitors work as
         expected.
         :return: monitors: NAE monitors created by the function.
        """

        monitors = {}
        for rule in RESOURCE_URI_MAP:
            uri = RESOURCE_URI_MAP[rule]
            monitors[rule] = {
                'switch': Monitor(Sum(uri), '{} count monitor'.format(rule)),
                'vsx_peer': Monitor(Sum(VSX_PEER + uri),
                                    '{} count on VSX peer'
                                    ' monitor'.format(rule))
            }
            var1 = 'monitor_{}_count'.format(rule)
            var2 = 'monitor_vsx_peer_{}_count'.format(rule)

            setattr(self, var1, monitors[rule]['switch'])
            setattr(self, var2, monitors[rule]['vsx_peer'])

        return monitors

    def set_rules(self, monitors):
        """
        Creates NAE Rules to alert if the ratio of routes count,
        neighbors count and MAC addresses count on the switch and on the
        VSX-peer is outside the allowed deviation range.

        Since this function creates NAE Rules based on the keys of a
        dictionary and the NAE Python Frameworks demands a NAE Rule to be
        defined as a class variables, the function implementation needs to use
        the `setattr` function to make sure that all the NAE Rules work as
        expected.
        :param monitors: NAE Monitors for which the NAE Rules need to be
        created.
        """

        for rule, monitor in monitors.items():
            switch_monitor = monitor['switch']
            vsx_peer_monitor = monitor['vsx_peer']

            # Calculate the allowed deviation range.
            lower_key = '{}_count_ratio_lower_threshold'.format(rule)
            upper_key = '{}_count_ratio_upper_threshold'.format(rule)

            upper_threshold_rule = Rule('Ratio of {} on the switch to VSX'
                                        '-peer rule'.format(rule))
            upper_threshold_rule.condition(
                'ratio of {} and {} > {}',
                [switch_monitor, vsx_peer_monitor, self.params[upper_key]])

            upper_threshold_rule.action(self.critical_action)
            upper_threshold_rule.clear_condition(
                'ratio of {} and {} < {}',
                [switch_monitor, vsx_peer_monitor, self.params[upper_key]])
            upper_threshold_rule.clear_action(self.normal_action)

            # Rule to alert if the NAE Monitor value goes below the lower
            # threshold value
            lower_threshold_rule = Rule('Ratio of {} on the switch to VSX'
                                        '-peer rule'.format(rule))
            lower_threshold_rule.condition(
                'ratio of {} and {} < {}',
                [switch_monitor, vsx_peer_monitor, self.params[lower_key]])
            lower_threshold_rule.action(self.critical_action)
            lower_threshold_rule.clear_condition(
                'ratio of {} and {} > {}',
                [switch_monitor, vsx_peer_monitor, self.params[lower_key]])
            lower_threshold_rule.clear_action(self.normal_action)

            var1 = 'rule_{}_count_ratio_upper_threshold'.format(rule)
            var2 = 'rule_{}_count_ratio_lower_threshold'.format(rule)

            setattr(self, var1, upper_threshold_rule)
            setattr(self, var2, lower_threshold_rule)

    def critical_action(self, event):
        """
        NAE callback action which is executed when the NAE Rule goes out of
        the allowed deviation range.
        :param event: Event details passed to the Callback by the NAE Agent
        """
        self.process_event(event, AlertLevel.CRITICAL)

    def normal_action(self, event):
        """
        NAE callback action which is executed when the NAE Rule comes back to
        the allowed deviation range.
        :param event: Event details passed to the Callback by the NAE Agent
        """
        self.process_event(event, 'Normal')

    def process_event(self, event, alert_level):
        """
        Process the NAE agent callback event.
        The function validates the NAE Alert and generates the
        Alert Message if the alert is valid.
        :param event: Event details passed to the Callback by the NAE Agent.
        :param alert_level: Status of the NAE Rule that caused the
        callback action to be executed. Possible values are 'Normal' and
        'Critical'
        """

        rule_description = event['rule_description']
        if 'mac_addresses' in rule_description:
            resource = 'mac_addresses'
        elif 'neighbors' in rule_description:
            resource = 'neighbors'
        elif 'routes' in rule_description:
            resource = 'routes'
        else:
            self.logger.error("Error while getting resource name from event")
            return

        count_values = self.get_count_values(resource)

        if ('count' in count_values) and ('vsx-peer-count' in count_values):
            ratio = (count_values['count'] / count_values['vsx-peer-count'])
        elif ('count' not in count_values) and ('vsx-peer-count'
                                                in count_values):
            self.logger.error(
                'Could not get {} count on the switch'.format(resource))
            return
        elif ('vsx-peer-count' not in count_values) and (
                'count' in count_values):
            self.logger.error(
                'Could not get {} count on the VSX-peer'
                ' switch'.format(resource))
            return
        else:
            self.logger.error(
                'Could not get {} count on both, the switch and on the'
                'VSX-peer switch'.format(resource))
            return

        valid_alert = self.validate_alert(ratio, resource, alert_level)

        if not valid_alert:
            return

        self.update_variables(resource, alert_level)

        self.generate_alert_message(resource, ratio, count_values)

        self.update_alert_level()

    def validate_alert(self, ratio, resource, alert_level):
        """
        Validate the NAE Alert.
        :param ratio: Ratio of count of resource on switch to
        vsx-peer switch
        :param resource: Resource for which the alert message
        needs to be generated
        :param alert_level: Status of the NAE Rule that caused the
        callback action to be executed. Possible values are 'Normal' and
        'Critical '
        """

        variable_map_key = '{}_ratio'.format(resource)
        if variable_map_key in self.variables:
            if self.variables[variable_map_key] == alert_level:
                return False
        else:
            self.logger.error(
                'Unable to access NAE variable containing alert status'
                'for resource {}'.format(resource))
            return False

        key = '{}_count_ratio_upper_threshold'.format(resource)

        if key in self.params:
            upper_threshold_value = float(self.params[key].value)
        else:
            self.logger.error("Error while getting upper"
                              "threshold for {} count".format(resource))
            return False

        key = '{}_count_ratio_lower_threshold'.format(resource)
        if key in self.params:
            lower_threshold_value = float(self.params[key].value)
        else:
            self.logger.error("Error while getting lower"
                              "threshold for {} count".format(resource))
            return False

        if (alert_level == AlertLevel.CRITICAL) and (
                (ratio > upper_threshold_value) or (
                    ratio < lower_threshold_value)):
            return True
        elif (alert_level == 'Normal') and ((ratio < upper_threshold_value)
                                            and (ratio > lower_threshold_value)):
            return True
        else:
            return False

    def update_variables(self, resource, alert_level):
        """
        Update NAE variables containing alert_level status for each resource
        :param resource: Resource for which the alert message
        needs to be generated
        :param alert_level: Status of the NAE Rule that caused the
        callback action to be executed. Possible values are 'Normal' and
        'Critical '
        """

        if alert_level == AlertLevel.CRITICAL:
            self.variables['{}_ratio'.format(resource)] = AlertLevel.CRITICAL
        else:
            self.variables['{}_ratio'.format(resource)] = 'Normal'

    def generate_alert_message(self, resource, ratio, count_values):
        """"
        Generates the NAE alert message.
        :param resource: Resource for which the alert message
        needs to be generated
        :param ratio: Ratio of count of resource on switch to
        vsx-peer switch
        :param count_values: Count values of the resource on the
        switch and vsx-peer switch
        """

        variable_map_key = '{}_ratio'.format(resource)
        if variable_map_key in self.variables:
            if self.variables[variable_map_key] == AlertLevel.CRITICAL:
                range_position = 'outside'
            else:
                range_position = 'inside'
        else:
            self.logger.error(
                'Unable to access NAE variable containing alert status'
                'for resource {}'.format(resource))
            return

        if resource == 'mac_addresses':
            resource = 'MAC addresses'

        ratio_value = ' The ratio of {} count on the switch to the ' \
            '{} count on the VSX-peer ' \
            'is {:.3f} which is {} the allowed deviation '.format(
                resource, resource, ratio, range_position)
        self.logger.info(ratio_value)

        ActionCustomReport(
            ratio_value, title=Title(
                '{} count ratio'.format(resource)))

        switch_count = 'The count of {} on the switch is {}'.format(
            resource, count_values['count'])
        self.logger.info(switch_count)
        ActionCustomReport(switch_count, title=Title(
            'Count of {} on switch'.format(resource)))

        vsx_peer_count = 'The count of {} on the VSX-peer switch is {}'.format(
            resource, count_values['vsx-peer-count'])
        self.logger.info(vsx_peer_count)
        ActionCustomReport(vsx_peer_count, title=Title(
            'Count of {} on VSX-peer switch'.format(resource)))

        ActionCLI('show vsx brief', title=Title("VSX status"))

    def update_alert_level(self):
        """
        Updates the NAE Agent alert level based on the status of the NAE Rules
        for routes count, neighbors count and MAC addresses count.
        """
        routes_ratio = self.variables['routes_ratio']
        neighbors_ratio = self.variables['neighbors_ratio']
        mac_addresses_ratio = self.variables['mac_addresses_ratio']

        if (neighbors_ratio == AlertLevel.CRITICAL or mac_addresses_ratio ==
            AlertLevel.CRITICAL) and (self.get_alert_level() !=
                                      AlertLevel.CRITICAL):
            self.set_alert_level(AlertLevel.CRITICAL)
        elif (neighbors_ratio == 'Normal' and mac_addresses_ratio == 'Normal'
              and routes_ratio == AlertLevel.CRITICAL) and \
                (self.get_alert_level() != AlertLevel.MINOR):
            self.set_alert_level(AlertLevel.MINOR)
        elif (neighbors_ratio == 'Normal' and mac_addresses_ratio == 'Normal'
              and routes_ratio == 'Normal') and (self.get_alert_level() is not None):
            self.remove_alert_level()

    def get_count_values(self, resource):
        """
        Get the count values for the resource on the switch and the VSX-peer
        :param resource: Resource for which the count values need to be
        obtained.
        """
        count_values = {}
        rest_uri = RESOURCE_URI_MAP[resource]
        vsx_rest_uri = VSX_PEER + rest_uri
        try:
            r = rest_get(rest_uri)
            r.raise_for_status()
            count = r.json()["count"]
            count_values["count"] = count
        except Exception as e:
            self.logger.debug("Error while making REST call to URI "
                              "{} : {}".format(rest_uri, str(e)))
            self.logger.error("Error while making REST call to URI "
                              "{}".format(rest_uri))

        try:
            r = rest_get(vsx_rest_uri)
            r.raise_for_status()
            count = r.json()["count"]
            count_values["vsx-peer-count"] = count
        except Exception as e:
            self.logger.debug("Error while making REST call to URI "
                              "{} : {}".format(vsx_rest_uri, str(e)))
            self.logger.error("Error while making REST call to URI "
                              "{}".format(vsx_rest_uri))

        return count_values
