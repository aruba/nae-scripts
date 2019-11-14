# -*- coding: utf-8 -*-
#
# (c) Copyright 2018 Hewlett Packard Enterprise Development LP
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

from requests import get, post, exceptions
from json import dumps

PROXY_DICT = {'http': None, 'https': None}

Manifest = {
    'Name': 'configuration_change_service_now',
    'Description': 'Agent to alert user when configuration changes and show '
                   'the system info and diff of configuration changes. A ticket '
                   'is created in Incident table of ServiceNow, with the diff '
                   'of configuration changes and other details.',
    'Version': '1.1',
    'Author': 'Aruba Networks'}

ParameterDefinitions = {
    'urgency': {
        'Name': 'Urgency of the config change event',
        'Description': 'Specify the urgency of the configuration change event, '
                       'that is provided in the ServiceNow ticket. Options are '
                       '1 - High, 2 - Medium and 3 - Low.',
        'Type': 'integer',
        'Default': 3
    },
    'severity': {
        'Name': 'Severity of the config change event',
        'Description': 'Specify the severity of the configuration change event, '
                       'that is provided in the ServiceNow ticket. Options are '
                       '1 - High, 2 - Medium and 3 - Low.',
        'Type': 'integer',
        'Default': 3
    },
    'username': {
        'Name': 'Username of the ServiceNow account instance',
        'Description': 'Enter the username of the ServiceNow account instance '
                       'used to create the ticket for configuration change event.',
        'Type': 'string',
        'Default': 'admin'
    },
    'password': {
        'Name': 'Password of the ServiceNow account instance',
        'Description': 'Enter the password of the ServiceNow account instance '
                       'used to create the ticket for configuration change event.',
        'Type': 'string',
        'Default': 'pwd',
        'Encrypted': True
    },
    'domain_name': {
        'Name': 'Domain name of the ServiceNow account instance',
        'Description': 'Enter the domain name of the ServiceNow account instance '
                       'used to create the ticket for configuration change event.',
        'Type': 'string',
        'Default': 'devxxxxx'
    },
    'short_description': {
        'Name': 'Short description for configuration change event',
        'Description': 'Enter the short description for the configuration change '
                       'event, that will be described in the ServiceNow ticket.',
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


def rest_get(url):
    return get(HTTP_ADDRESS + url, verify=False,
               proxies={'http': None, 'https': None})


class Agent(NAE):

    def __init__(self):
        uri = '/rest/v1/system?attributes=last_configuration_time'
        rate_uri = Rate(uri, '10 seconds')
        self.m1 = Monitor(rate_uri, 'Rate of last configuration time')
        self.r1 = Rule('Configuration change')
        self.r1.condition('{} > 0', [self.m1])
        self.r1.action(self.config_change_start)
        self.r1.clear_condition('{} == 0', [self.m1])
        self.r1.clear_action(self.config_change_end)

    def config_change_start(self, event):
        try:
            r = rest_get('/rest/v1/configlist')
            r.raise_for_status()
            configlist = r.json()
            self.variables['base_checkpoint'] = configlist[-1]['name']
        except Exception as e:
            self.logger.debug("Could not get checkpoint list: {}".format(str(e)))
            self.logger.error("Could not get checkpoint list.")

    def config_change_end(self, event):
        if 'base_checkpoint' in self.variables:
            base_checkpoint = self.variables['base_checkpoint']
        else:
            base_checkpoint = 'startup-config'

        ActionSyslog('Configuration change happened')
        ActionCLI('show system', title=Title("System information"))
        ActionCLI('checkpoint diff %s running-config' % base_checkpoint,
                  title=Title("Configuration changes since latest checkpoint"))
        if base_checkpoint != 'startup-config':
            ActionCLI('checkpoint diff startup-config running-config',
                      title=Title("Unsaved configuration changes"))
        ActionShell('ausearch -i -m USYS_CONFIG -ts recent',
                    title=Title("Recent audit logs for configuration changes"))
        self.post_ticket_action(base_checkpoint)

    def post_ticket_action(
            self,
            base_checkpoint):
        try:
            r = rest_get('/rest/v1/system?attributes=mgmt_intf_status')
            r.raise_for_status()
            if 'ip' in r.json()['mgmt_intf_status']:
                mgmt_ip = r.json()['mgmt_intf_status']['ip']
                short_description = str(
                    self.params['short_description']) + ' on device with IP: ' + mgmt_ip
            else:
                short_description = str(self.params['short_description'])
        except:
            short_description = str(self.params['short_description'])
            self.logger.error(
                "Could not get management interface information.")

        try:
            r = rest_get(
                '/rest/v1/config/diff/%s/running-config' % base_checkpoint)
            r.raise_for_status()
            description = r.json()['output']
        except:
            description = ''
            self.logger.error("Could not get configuration diff")

        self.post_ticket(short_description, description)

    def post_ticket(self, short_description, description):
        self.logger.info('Agent creating ticket')
        user = str(self.params['username'])
        pwd = str(self.params['password'])
        domain_name = str(
            self.params['domain_name'])

        if str(self.params['web_proxy']) == '':
            proxies = {}
        else:
            proxies = {
                'http': 'http://' + str(self.params['web_proxy']) + ':8080',
                'https': 'https://' + str(self.params['web_proxy']) + ':8080'
            }

        url = 'https://' + domain_name + \
              '.service-now.com/api/now/table/incident'

        urgency = str(self.params['urgency'])
        severity = str(self.params['severity'])

        headers = {
            "content-type": "application/json", "Accept": "application/json"}
        payload = {
            'description': description,
            'severity': severity,
            'urgency': urgency,
            'short_description': short_description,
            'category': 'network'}
        try:
            response = post(
                url,
                auth=(
                    user,
                    pwd),
                headers=headers,
                proxies=proxies,
                data=dumps(payload))
            self.logger.info(
                "Agent post: Status code: {}".format(str(response.status_code)))
        except exceptions.RequestException as e:
            self.logger.error(
                "Could not create configuration change ticket in ServiceNow. Error: {}".format(str(e)))
