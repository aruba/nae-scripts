# -*- coding: utf-8 -*-
#
# (c) Copyright 2018,2022-2024 Hewlett Packard Enterprise Development LP
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

#               --  Configuration Change (tftp) functionality  --
# The main purpose of the configuration change tftp agent is to provide
# differences in checkpoint configurations and copy the running configuration
# of the switch to a tftp server upon detection of a configuration change.
#
# 'Parameter Definitions' defines the input parameters to the script.
# This script requires the following parameters:
#       1. tftp_server_address - IP address of the TFTP server.
#       2. tftp_server_vrf - VRF through which the TFTP server can be reached
#                            from the switch. The default value is mgmt VRF.
#       3. tftp_configuration_format - Format in which the configuration is to
#                                      be copied. Valid values are cli or json.
#                                      The default value is json.
#       4. tftp_config_file_name_prefix- The prefix for the filename in which
#                                        the configuration is copied in the
#                                        TFTP server. Timestamp is appended to
#                                        the prefix to generate the file name.
#
# The script defines the following Monitor Resource URI(s), Monitor condition,
# and Actions:
#
# - Monitors: This script specifies the monitoring URI(s) to monitor the
#             following:
#       1. Rate of system last configuration time over 10 seconds.
# Note: The monitored data is plotted in a time-series chart for analysis
#       purpose.
#
# - Condition: Rate of system last configuration time over 10 seconds is
#              greater than zero.
# - Clear condition: Rate of system last configuration time is equal to zero.
# - Actions:
#       - When the monitoring condition specified is hit, the following action
#         is executed:
#               * Store the last checkpoint (if available) in a script variable
#                 called 'base_checkpoint'. If the last checkpoint is not
#                 available, the 'base_checkpoint' is startup-config.
#       - When the clear condition specified is hit, the following actions are
#         executed:
#               * CLI to show system is executed.
#               * Syslog command saying configuration change has happened.
#               * CLI to show the diff of last checkpoint and running config
#                 is executed.
#               * CLI to show the diff of start-up config and running config
#                 is executed.
#               * Shell command to show recent audit logs for configuration
#                 changes is executed.
#               * CLI to copy the running-configuration to a TFTP server.
# Note: For very large configurations, there is a chance errors occur in the
#       actions of this agent due to NAE resource limitations.

import time
from re import sub

Manifest = {
    'Name': 'configuration_change_tftp',
    'Description': 'Agent to copy the running configuration to a TFTP server'
                   'whenever a configuration change occurs.',
    'Version': '2.0',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.08',
    'AOSCXPlatformList': ['8320', '8325', '8400']
}

ParameterDefinitions = {
    'tftp_server_address': {
        'Name': 'IP address or hostname of the TFTP server',
        'Description': 'Enter the hostname or IP address of the TFTP server'
                       ' to which the running-config is to be copied when the'
                       ' configuration changes.',
        'Type': 'string',
        'Default': '',
    },
    'tftp_server_vrf': {
        'Name': 'VRF to reach the TFTP server',
        'Description': 'Enter the vrf through which the TFTP server '
                       'can be reached.',
        'Type': 'string',
        'Default': 'mgmt'
    },
    'tftp_configuration_format': {
        'Name': 'Format in which the configuration is copied to the '
                'TFTP server',
        'Description': 'Enter the format in which the configuration is '
                       'to be copied to the TFTP server. Possible values '
                       'are cli and json.',
        'Type': 'string',
        'Default': 'json'
    },
    'tftp_config_file_name_prefix': {
        'Name': 'Prefix for the file name for configuration during'
                ' TFTP process',
        'Description': 'Enter the prefix for the filename in which the'
                       ' configuration is to be stored on the '
                       'TFTP server. Timestamp will be '
                       'attached  to the prefix in the filename.',
        'Type': 'string',
        'Default': ''
    },

}


class Agent(NAE):
    def __init__(self):
        uri = '/rest/v1/system?attributes=last_configuration_time'
        rate_uri = Rate(uri, '10 seconds')
        self.monitor = Monitor(rate_uri, 'Rate of last configuration time')
        self.rule = Rule('Configuration change')
        self.rule.condition('{} > 0', [self.monitor])
        self.rule.action(self.calculate_base_config_checkpoint)
        self.rule.clear_condition('{} == 0', [self.monitor])
        self.rule.clear_action(self.calculate_config_diff)

    def calculate_base_config_checkpoint(self, event):
        """
        Callback action to extract the configuration checkpoint to be
        used as base reference checkpoint to calculate the configuration diff.
        :param event: Event details passed to the callback by the NAE agent.
        """
        try:
            uri = '/rest/configlist'
            configlist = self.get_rest_request_json(HTTP_ADDRESS + uri)
            self.variables['base_checkpoint'] = configlist[-1]['name']
        except:
            self.logger.error("Could not get checkpoint list.")

    def calculate_config_diff(self, event):
        """
        Callback action to extract the configuration after the change and
        calculate the diff between the base configuration checkpoint and
        the current configuration.
        :param event: Event details passed to the callback by the NAE agent.
        """
        if 'base_checkpoint' in self.variables:
            base_checkpoint = self.variables['base_checkpoint']
        else:
            base_checkpoint = 'startup-config'

        agent = sub(r'\.rule_0\.clear_condition$', '', event['condition_name'])

        ActionSyslog('Configuration change happened')
        ActionCLI('show system', title=Title("System information"))
        ActionCLI('checkpoint diff %s running-config' % base_checkpoint,
                  title=Title("Configuration changes since latest checkpoint"))
        if base_checkpoint != 'startup-config':
            ActionCLI('checkpoint diff startup-config running-config',
                      title=Title("Unsaved configuration changes"))
        ActionShell('ausearch -i -m USYS_CONFIG -ts recent',
                    title=Title("Recent audit logs for configuration changes"))

        self.tftp_configuration_action(agent)

    def tftp_configuration_action(self, agent):
        """
        Callback action to copy the switch running-configuration to a TFTP
        server..
        :param agent: Name of the agent which triggered the action
        """

        # Copy the configuration to a TFTP server.
        if str(self.params['tftp_server_address']) != "":
            tftp_server = str(self.params['tftp_server_address'])
        else:
            raise Exception("TFTP server address not provided.")

        if str(self.params['tftp_config_file_name_prefix']) != "":
            file_name_prefix = str(
                self.params['tftp_config_file_name_prefix'])
        else:
            raise Exception("TFTP filename prefix not provided.")

        tftp_format = str(self.params['tftp_configuration_format'])
        if tftp_format not in ('json', 'cli'):
            raise Exception('Invalid TFTP configuration file format')

        vrf = str(self.params['tftp_server_vrf'])
        try:
            self.logger.info(
                'Agent {} copying configuration to TFTP server'.format(
                    agent))
            self.tftp_running_config(tftp_server, file_name_prefix, vrf,
                                     tftp_format)
        except Exception as e:
            self.logger.error(
                "Agent {} could not TFTP the configuration change to TFTP "
                "server , error : {}".format(agent, str(e)))

    def tftp_running_config(self, tftp_server, file_name_prefix="",
                            vrf="mgmt", tftp_format="json"):
        """
        Copies the running configuration of the switch to a TFTP server.
        :param tftp_server: IP address or hostname of the TFTP server.
        :param file_name_prefix: Prefix for the file name in the TFTP server to
        which the configuration is copied.
        :param vrf: Name of the VRF through the TFTP server can be reached from
        the switch. Default value is mgmt VRF.
        :param tftp_format: Format in which the configuration is stored in the
        TFTP server. Default value is json format.
        """
        if tftp_server == "":
            raise Exception("TFTP server address not provided")
        file_name = file_name_prefix + str(int(time.time()))
        if tftp_format == 'json':
            file_name += '.json'
        else:
            file_name += '.cfg'

        tftp_command = 'copy running-config tftp://%s/%s %s' % (tftp_server,
                                                                file_name,
                                                                tftp_format)

        if vrf != "":
            tftp_command += ' vrf %s' % vrf

        ActionCLI(tftp_command)
