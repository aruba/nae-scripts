# -*- coding: utf-8 -*-
#
# (c) Copyright 2018,2022,2024 Hewlett Packard Enterprise Development LP
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

LONG_DESCRIPTION = '''\
## Script Description

The main components of the script are Manifest, Parameter Definitions and python code.  

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
        - username - Username of the TOPdesk® account instance.
        - password - Password of the TOPdesk® account instance.
        - domain_name - Domain name of the TOPdesk® account instance.
        - short_description - Short description for the configuration change event.
        - web_proxy - Web proxy IP address  

The script defines Monitor Resource URI(s), Monitor condition and Action : 

- Monitors:  This script specifies the monitoring URI(s) to monitor the following:  
    1. Rate of system last configuration time over 10 seconds.

_Note: The monitored data is plotted in a time-series chart for analysis purpose._

- Conditions:  This script specifies monitoring condition as following:
    1. Rate of system last configuration time over 10 seconds is greater than zero.
- Clear condition: Rate of system last configuration time is equal to zero. 
- Actions:  This script specifies monitoring action as following:  
    - When the monitoring condition (1) specified is hit, the following action is executed:
        - Store the last checkpoint (if available) in a script variable called 'base_checkpoint'. If the last checkpoint is not available, the 'base_checkpoint' is startup-config.
    - When the clear condition specified is hit, the following actions are executed:
        - CLI to show system is executed.
        - Syslog command saying configuration change has happened.
        - CLI to show the diff of last checkpoint and running config is executed.
        - CLI to show the diff of start-up config and running config is executed.
        - Shell command to show recent audit logs for configuration changes is executed.
        - An incident ticket is posted to TOPdesk®, with the configuration diff, system and time information.
        - A link to the Agent dashboard of the affected switch is provided in the ticket 
'''

from html import escape
from re import sub
from requests import get

Manifest = {
    'Name': 'configuration_change_topdesk',
    'Description': 'Agent to alert user when configuration changes and show '
                   'the system info and diff of configuration changes. An '
                   'incident is created in TOPdesk, with the diff of '
                   'configuration changes and other details.',
    'Version': '2.0',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.11',
    'AOSCXPlatformList': ['8320', '8325', '8400']
}

ParameterDefinitions = {
    'username': {
        'Name': 'Username of the TOPdesk account instance',
        'Description': 'Enter the username of the TOPdesk account instance '
                       'used to create the incident for configuration change '
                       'event.',
        'Type': 'string',
        'Default': ''
    },
    'password': {
        'Name': 'Password of the TOPdesk account instance',
        'Description': 'Enter the password of the TOPdesk account instance '
                       'used to create the incident for configuration change '
                       'event.',
        'Type': 'string',
        'Default': '',
        'Encrypted': True
    },
    'domain_name': {
        'Name': 'Domain name of the TOPdesk account instance',
        'Description': 'Enter the domain name of the TOPdesk account instance '
                       'used to create the incident for configuration change '
                       'event.',
        'Type': 'string',
        'Default': ''
    },
    'short_description': {
        'Name': 'Short description for configuration change event',
        'Description': 'Enter the short description for the configuration '
                       'change event, that will be described in the TOPdesk '
                       'incident.',
        'Type': 'string',
        'Default': 'NAE detected a config change event'
    },
    'web_proxy': {
        'Name': 'Web proxy IP address',
        'Description': 'Enter the IP address for web proxy.',
        'Type': 'string',
        'Default': ''
    }
}

URI_PREFIX_GET = "/rest/v10.08/"
URI_PREFIX_MONITOR = "/rest/v1/"


class Agent(NAE):

    def __init__(self):
        uri = URI_PREFIX_MONITOR + 'system?attributes=last_configuration_time'
        rate_uri = Rate(uri, '30 seconds')
        self.m1 = Monitor(rate_uri, 'Rate of last configuration time')
        self.r1 = Rule('Configuration change')
        self.r1.condition('{} > 0', [self.m1])
        self.r1.action(self.config_change_start)
        self.r1.clear_condition('{} == 0', [self.m1])
        self.r1.clear_action(self.config_change_end)

    def config_change_start(self, event):
        try:
            configlist = self.get_rest_request_json(
                HTTP_ADDRESS + '/rest/configlist')
            self.variables['base_checkpoint'] = configlist[-1]['name']

        except Exception as e:
            self.logger.debug(
                "Could not get checkpoint list: {}".format(str(e)))
            self.logger.error("Could not get checkpoint list.")

    def config_change_end(self, event):
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

        self.post_incident_action(agent, base_checkpoint)

    def post_incident_action(self, agent, base_checkpoint):
        self.logger.info('Agent creating incident')
        try:
            uri = HTTP_ADDRESS + URI_PREFIX_GET + 'system?attributes=mgmt_intf_status'
            r = self.get_rest_request_json(uri)
            mgmt_ip = r['mgmt_intf_status']['ip']
        except Exception as e:
            self.logger.debug(
                "Could not get management information: {}".format(str(e)))
            self.logger.error("Could not get management information.")
            return

        try:
            uri = HTTP_ADDRESS + \
                '/rest/config/diff/{}/running-config'.format(base_checkpoint)
            r = self.get_rest_request_json(uri)
            description = r['output']
        except NAEException as e:
            description = ''
            self.logger.error("Could not get configuration diff. Error: {}" %
                              str(e))

        try:
            self.post_incident(agent, mgmt_ip, description)
        except Exception as e:
            self.logger.error(
                "Could not create configuration change incident in "
                "TOPdesk. Error: {}".format(str(e)))

    def post_incident(self, agent, mgmt_ip, config_diff):
        user = str(self.params['username'])
        pwd = str(self.params['password'])
        domain = str(self.params['domain_name'])
        base = 'https://%s.topdesk.net/tas/api' % domain

        if str(self.params['web_proxy']) == '':
            proxies = {}
        else:
            proxies = {
                'http': 'http://' + str(self.params['web_proxy']) + ':8080',
                'https': 'http://' + str(self.params['web_proxy']) + ':8080'
            }

        r = get(base + '/login/person', auth=(user, pwd), proxies=proxies)
        auth = 'TOKEN id="%s"' % r.text
        headers = {'Authorization': auth}

        agent_dashboard = ('<a href="https://%s/#/layout/analytics/dashboard'
                           '/agentDetails/%s">NAE Agent Dashboard</a>' %
                           (mgmt_ip, agent))
        title = ('Configuration change detected in device with IP: %s. More '
                 'details in %s.<br><br>Changes since last checkpoint:<br>' %
                 (mgmt_ip, agent_dashboard))
        request = title + escape(config_diff, False).replace('\n', '<br>')
        incident = {
            "category": {
                "name": "Network & Data Communication"
            },
            "subcategory": {
                "name": "Switch"
            },
            "briefDescription": str(self.params['short_description']),
            "request": request
        }

        r = self.get_rest_request_json(base + '/incidents/call_types', headers=headers,
                                       proxies=proxies)
        for i in r:
            if i['name'] == 'Information':
                incident["callType"] = i
                break

        r = self.post_rest_request(base + '/incidents', headers=headers, json=incident,
                                   proxies=proxies)

        self.get_rest_request_json(
            base + '/logout', headers=headers, proxies=proxies)
