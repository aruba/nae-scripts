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

from html import escape
from re import sub
from requests import get, post, exceptions

Manifest = {
    'Name': 'topdesk_configuration_change_monitor',
    'Description': 'Agent to alert user when configuration changes and show '
                   'the system info and diff of configuration changes. An '
                   'incident is created in TOPdesk, with the diff of '
                   'configuration changes and other details.',
    'Version': '1.1',
    'Author': 'Aruba Networks'}

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


def rest_get(url):
    return get(HTTP_ADDRESS + url, verify=False,
               proxies={'http': None, 'https': None})


class Agent(NAE):

    def __init__(self):
        uri = '/rest/v1/system?attributes=last_configuration_time'
        rate_uri = Rate(uri, '30 seconds')
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
            r = rest_get('/rest/v1/system?attributes=mgmt_intf_status')
            r.raise_for_status()
            mgmt_ip = r.json()['mgmt_intf_status']['ip']
        except Exception as e:
            self.logger.debug("Could not get management information: {}".format(str(e)))
            self.logger.error("Could not get management information.")
            return

        try:
            r = rest_get('/rest/v1/config/diff/%s/running-config' %
                         base_checkpoint)
            description = r.json()['output']
        except(exceptions.RequestException, exceptions.HTTPError) as e:
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
        r.raise_for_status()
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

        r = get(base + '/incidents/call_types', headers=headers,
                proxies=proxies)
        r.raise_for_status()
        for i in r.json():
            if i['name'] == 'Information':
                incident["callType"] = i
                break

        r = post(base + '/incidents', headers=headers, json=incident,
                 proxies=proxies)

        get(base + '/logout', headers=headers, proxies=proxies)

        r.raise_for_status()
