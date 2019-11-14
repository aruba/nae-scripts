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
    'Name': 'mac_addresses_decrease_rate_monitor',
    'Description': 'Monitor rate of decrease of MAC addresses',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'rate_of_decrease_threshold': {
        'Name': 'Rate of decrease threshold (in percentage)',
        'Description': 'This parameter represents the threshold value above '
                       'which the rate of decrease of MAC addresses on the '
                       'switch is supposed to generate an alert.'
                       'The threshold value is calculated as a percentage of'
                       'the MAC address count at the beginning of the time '
                       'interval during which the rate is calculated.',
        'Type': 'Integer',
        'Default': 10
    },
    'time_interval': {
        'Name': 'Time interval for calculating rate of decrease',
        'Description': 'This parameter represents the time interval over '
                       'which the rate of decrease of MAC addresses count is'
                       'to be calculated.',
        'Type': 'Integer',
        'Default': 1
    }
}

URI = '/rest/v1/system/bridge/vlans/*/macs?count'


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
        This NAE script sets up an NAE Rule to monitor the rate of
        decrease of MAC addresses count on the switch.
        The NAE script generates an alert whenever the rate of decrease of
        MAC addresses count on the switch over a time period of the time
        interval passed as NAE parameter to the NAE agent is over the
        threshold value passed as NAE parameter to the NAE Agent.

        The script is designed to work on ArubaOS-CX 10.02.XXXX or
        above versions.
        """

    def __init__(self):

        # Get the initial MAC Addresses count on the switch.
        initial_mac_addresses_count = self.get_resource_count()

        # Store the initial MAC addresses count so that it can be used in
        # calculating the rate of decrease of MAC addresses count.
        self.variables['resource_count_value'] = str(
            initial_mac_addresses_count)

        # Setup the NAE Script Rules.
        self.setup_agent_rule()

        # Create a NAE Monitor.
        self.create_agent_monitor()

    def setup_agent_rule(self):
        """
        Creates a NAE Rule that contains a NAE Periodic Condition that
        executes a NAE callback action that retrieves the current value of
        the MAC addresses count on the switch over the the time interval
        passed as parameter to the NAE agent. If the value is over the
        threshold value passed as parameter to the NAE agent, an alert is
        generated.

        Since the NAE monitor for Rate monitoring does not support
        monitoring of rate of decrease of a resource, the rate
        of decrease of the resource needs to be monitored using a
        NAE periodic condition that periodically executes a callback
        action inside which the rate of decrease of the resource is
        calculated mathematically using the current value and previous
        value of the resource.
        """

        rule = Rule(
            'Rate of decrease of MAC addresses count on the switch')
        rule.condition('every {} minutes', [self.params['time_interval']])
        rule.action(self.calculate_decrease_rate)

        setattr(self, 'mac_address_decrease_rate_rule', rule)

    def create_agent_monitor(self):
        """
        Creates a NAE monitor to monitor a switch resource.
        """

        monitor = Monitor(Sum(URI), 'MAC Address count monitor')

        setattr(self, 'mac_address_count_monitor', monitor)

    def calculate_decrease_rate(self, event):
        """
        Callback action that is executed periodically by the NAE script
        periodic condition.

        The callback action retrieves the previous value of the resource
        from a variable stored in the local storage of the NAE Agent,
        compares it with the current value of the resource obtained by
        making a REST call to the resource to URI to calculate the
        difference in the two values. The rate is calculated by dividing the
        difference by the time interval to obtain the rate of decrease. It
        updates the NAE Agent level based on the rate of decrease.
        :param event: Event details passed to the callback action by the NAE
        Agent
        """

        previous_count_value = int(self.variables['resource_count_value'])
        current_count_value = self.get_resource_count()

        count_decrease = previous_count_value - current_count_value

        decrease_rate = (count_decrease / int(str(self.params[
            'time_interval'])))

        self.variables['resource_count_value'] = str(current_count_value)

        self.update_alert_level(decrease_rate, previous_count_value)

    def update_alert_level(self, decrease_rate, previous_count_value):
        """
        Updates the Agent Alert Level based on the rate of decrease of the
        resource.

        If the rate of decrease is above the threshold value , the NAE Agent
        Alert Level is set to Critical, otherwise it is set to Normal
        :param decrease_rate: Rate of decrease of the resource.
        :param previous_count_value: Count of the resource at the beginning
        of the time interval during which the rate of decrease is calculated.
        """

        if decrease_rate <= 0:
            if self.get_alert_level() == AlertLevel.CRITICAL:
                self.remove_alert_level()
            return

        decrease_percentage = (decrease_rate/float(previous_count_value) * 100)

        if decrease_percentage > int(str(
                self.params['rate_of_decrease_threshold'])):
            # If the previous NAE Agent Alert Level is Normal, set it to
            # Critical
            if self.get_alert_level() is None:
                self.set_alert_level(AlertLevel.CRITICAL)
                message = 'The rate of decrease of the MAC addresses on ' \
                          'the switch which is {} is greater than the ' \
                          'threshold value ' \
                          'of {}'.format(str(decrease_percentage), str(
                              self.params['rate_of_decrease_threshold']))
                self.logger.info(message)
                ActionCustomReport(message, title=Title("Rate of decrease "
                                                        "of MAC Addresses"))
        else:
            # If the previous NAE Agent Alert Level is Critical , set it to
            # Normal.
            if self.get_alert_level() == AlertLevel.CRITICAL:
                self.remove_alert_level()
                message = 'The rate of decrease of the MAC addresses on ' \
                          'the switch which is {} is lesser than the ' \
                          'threshold value ' \
                          'of {}'.format(str(decrease_percentage), str(
                              self.params['rate_of_decrease_threshold']))
                self.logger.info(message)
                ActionCustomReport(message, title=Title("Rate of decrease "
                                                        "of MAC Addresses"))

    def get_resource_count(self):
        """
        Get the count of the resource by making a HTTP GET operation to the
        REST URI for the resource.
        :return: count: Number of entries in the resource
        """
        count = 0
        try:
            r = rest_get(URI)
            r.raise_for_status()
            count = r.json()["count"]
        except Exception as e:
            self.logger.debug("Error while making REST call to URI "
                              "{} : {}".format(URI, str(e)))
            self.logger.error("Error while making REST call to URI "
                              "{}".format(URI))

        return count
