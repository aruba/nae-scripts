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

from smtplib import SMTP
from email.mime.text import MIMEText
from html import escape
from re import sub
from requests import get

Manifest = {
    'Name': 'configuration_change_email',
    'Description': 'Agent to alert user when configuration changes and show '
                   'the system info and diff of configuration changes. An'
                   'email notification with the diff is sent whenever the '
                   'configuration changes.',
    'Version': '1.1',
    'Author': 'Aruba Networks'}

ParameterDefinitions = {
    'smtp_server_address': {
        'Name': 'IP address/hostname and port number of the SMTP server',
        'Description': 'Enter the hostname/port number of the SMTP server'
                       ' in the format server_hostname:port. If the port'
                       ' number is not provided , the default port of 25 '
                       ' will be used.',
        'Type': 'string',
        'Default': ''
    },
    'sender_email_address': {
        'Name': '[Optional] Email address from which the alert is sent',
        'Description': 'Enter the email address from which the notification'
                       ' is to be sent. If this value is not provided the'
                       'default value of admin@{switch_host_name} will be '
                       'used.',
        'Type': 'string',
        'Default': ''

    },
    'recipient_email_address': {
        'Name': 'Comma separated list of email addresses to which the '
                'notification is to be sent.',
        'Description': 'Enter a comma separated list of email addresses to '
                       'which the email alert notification is to be sent.',
        'Type': 'string',
        'Default': '',
    },
    'smtp_server_user_id': {
        'Name': '[Optional] User name for SMTP server if protected '
                'with credentials',
        'Description': 'Enter the user name for the SMTP server if protected'
                       ' with password. It is optional and can be left empty '
                       'if not protected with username and password.',
        'Type': 'string',
        'Default': '',
    },
    'smtp_server_user_password': {
        'Name': '[Optional] Password for SMTP server if protected with '
                'password',
        'Description': 'Enter the password for the SMTP server if protected'
                       ' with password. It is optional and can be '
                       'left empty if not protected with username and '
                       'password.',
        'Type': 'string',
        'Default': '',
        'Encrypted': True,
    },
    'email_subject': {
        'Name': '[Optional] Subject of the email notification',
        'Description': 'Enter the subject for the email alert notification.'
                       'if this value is not provided the default value'
                       'will be used.',
        'Type': 'string',
        'Default': 'NAE detected a config change event'
    },
    'switch_host_name': {
        'Name': '[Optional] Hostname for the switch to be used in '
                'SMTP helo/ehelo message',
        'Description': 'Enter a hostname for the switch to use in the SMTP'
                       ' helo/ehelo message. If left blank, the hostname'
                       ' of the switch along with the switch domain name',
        'Type': 'string',
        'Default': ''
    }

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
            r = rest_get('/rest/v1/configlist')
            r.raise_for_status()
            configlist = r.json()
            self.variables['base_checkpoint'] = configlist[-1]['name']
        except Exception as e:
            self.logger.debug(
                "Could not get checkpoint list: {}".format(str(e)))
            self.logger.error("Could not get checkpoint list.")

    def nae_agent_uri(self, mgmt_ip, agent):
        agent_dashboard = ('https://%s/#/layout/analytics/dashboard'
                           '/agentDetails/%s ' % (mgmt_ip, agent))
        return agent_dashboard

    def syslog_with_uri(self, agent_uri):
        ActionSyslog('Configuration change happened, NAE Agent URI: '
                     + agent_uri)

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

        try:
            mgmt_ip, host_name = self.get_device_info()
        except Exception as e:
            self.logger.debug(
                "Could not get management information: {}".format(str(e)))
            self.logger.error("Could not get management information.")
            return

        try:
            self.email_alert_action(agent, base_checkpoint, mgmt_ip, host_name)
            self.syslog_with_uri(self.nae_agent_uri(mgmt_ip, agent))
        except Exception as e:
            self.logger.debug(
                "Error creating email notification: {}".format(str(e)))

    def email_alert_action(self, agent, base_checkpoint, mgmt_ip, host_name):
        """
        Calculates the diff in configuration and send an email alert with
        the configuration difference.
        :param agent: Name of the agent which generated the alert.
        :param base_checkpoint: Configuration checkpoint used as the base while
        :param mgmt_ip:
        :param host_name:
        calculating the configuration diff.
        """

        # Get the change in the configuration details.
        try:
            r = rest_get('/rest/v1/config/diff/%s/running-config' %
                         base_checkpoint)
            r.raise_for_status()
            description = r.json()['output']
        except Exception as e:
            description = ''
            self.logger.error(
                "Agent {} could not get configuration diff. Error: {}".
                format(agent, str(e)))

        # Send an email alert with the configuration difference
        try:
            self.create_email_notification(agent, mgmt_ip, description,
                                           host_name)
        except Exception as e:
            self.logger.error(
                "Agent {} could not create an email alert notification , "
                "error : {}".format(agent, str(e)))

    def create_email_notification(self, agent, mgmt_ip, config_diff,
                                  host_name):
        """
        Create and send an email alert with the configuration change details.
        :param agent: Name of the agent generating the alert
        :param mgmt_ip: Management VRF IP of the switch generating the alert.
        :param config_diff: Difference in the configuration triggering
        the alert.
        :param host_name: Host name of the switch generating the alert.
        """
        self.logger.info('Agent {} generating email alert'.format(agent))

        # prepare the arguments to be passed to ActionEmail
        server_address = str(self.params['smtp_server_address'])
        if server_address != "":
            address = server_address.split(':')
            if len(address) == 2:
                server = address[0]
                port = int(address[1])
            else:
                server = server_address
                port = 25
        else:
            raise Exception("SMTP server address is not provided")

        if str(self.params['recipient_email_address']) != "":
            recipients = str(self.params['recipient_email_address'])
        else:
            raise Exception("Recipient email address not provided")

        send_email = str(self.params['sender_email_address'])
        if send_email != "":
            sender = send_email
        else:
            sender = 'admin@' + host_name

        if str(self.params['email_subject']) != "":
            subject = str(self.params['email_subject']) + ' on device with' \
                                                          ' IP: ' + mgmt_ip
        else:
            subject = "NAE detected a configuration change on device with " \
                      "IP:" + mgmt_ip
        if str(self.params['smtp_server_user_id']):
            username = str(self.params['smtp_server_user_id'])
        else:
            username = ""

        if str(self.params['smtp_server_user_password']):
            password = str(self.params['smtp_server_user_password'])
        else:
            password = ""

        # prepare the email alert message body
        agent_dashboard = self.nae_agent_uri(mgmt_ip, agent)
        title = ('Configuration change detected in device with IP: %s. '
                 '\n\n\n\n'
                 'More details in %s. \n\n\n'
                 'Changes since last checkpoint:' %
                 (mgmt_ip, agent_dashboard))
        email_body = title + escape(config_diff, False)

        # Execute Action Email to send the email alert.
        try:
            ActionEmail(email_body, server=server, port=port, sender=sender,
                        recipients=recipients, subject=subject,
                        host_name=host_name,
                        username=username, password=password)
            self.logger.info(
                "Agent {} sent an email alert for configuration change"
                "".format(agent))
        except Exception as e:
            self.logger.error(
                "Error while trying to execute ActionEmail: {} for agent "
                "{}".format(str(e), agent))
            ActionCustomReport(str(e), title=Title("Error while trying to "
                                                   "execute ActionEmail"))

    def get_device_info(self):
        """
        Gets the switch management interface IP address and host name
        :return: mgmt_ip, host_name: the switch management IP address and
        switch host name.
        """

        r = rest_get('/rest/v1/system?attributes=mgmt_intf_status')
        r.raise_for_status()
        mgmt_ip = r.json()['mgmt_intf_status']['ip']

        if str(self.params['switch_host_name']) != "":
            host_name = str(self.params['switch_host_name'])
        else:
            host = r.json()['mgmt_intf_status']['hostname']
            domain_name = r.json()['mgmt_intf_status']['domain_name']
            host_name = host + '.' + domain_name

        return mgmt_ip, host_name


class ActionEmail:
    def __init__(self, email_body, **kwargs):
        """
        ActionEmail sends an email with the message passed as argument to it
        as body of the email.
        :param email_body: Content to be put in the alert email body.
        :param params: NAE Script parameters to be used as replacement for {}
        in the ActionEmail arguments.
        :param kwargs: Other fields that are passed as keyword arguments to
        the ActionEmail

        The required arguments that are needed to pass keyword arguments are
        as follows:
            server : IP address or hostname of the SMTP server.
            recipients: Comma separated list of email addresses to which the
                email alert needs to be sent.
            hostname: Hostname to be used in the SMTP helo/ehelo messages.

        The following optional arguments that can be passed as keyword
        arguments:
            port: Port on which SMTP server listens. The default value of
                25 is used if it's value is not passed.
            content_type: Type of the content in the email. Default value
                 of 'plain' is used if it's value is not passed.
            subject: Message to be sent as the subject of the email alert.
                Default value is empty string.
            username: SMTP server credential user name if the SMTP server
                access is protected wih user name and password.
            password: SMTP server credential password if the SMTP server
                access is password protected.
        """

        if 'server' in kwargs:
            self.server = kwargs['server']
        else:
            raise Exception("SMTP server address not provided")

        if 'recipients' in kwargs:
            self.recipients = kwargs['recipients']
        else:
            raise Exception("Recipients email address not provided")

        if 'host_name' in kwargs:
            self.host_name = kwargs['host_name']
        else:
            raise Exception("Device host name not provided")

        self.port = kwargs.get('port', 25)
        self.sender = kwargs.get('sender', 'admin@' + self.host_name)
        self.content_type = kwargs.get('content_type', 'plain')
        self.subject = kwargs.get('subject', '')

        msg = MIMEText(email_body, self.content_type)
        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = self.recipients
        conn = SMTP(self.server, self.port)
        if 'username' in kwargs and kwargs['username'] != "":
            if 'password' in kwargs and kwargs['password'] != "":
                conn.ehlo(self.host_name)
                conn.starttls()
                conn.login(kwargs['username'], kwargs['password'])
        else:
            conn.helo(self.host_name)

        try:
            conn.send_message(msg)
        finally:
            conn.quit()
