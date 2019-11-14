# (c) Copyright 2018-2019 Hewlett Packard Enterprise Development LP
#
# Confidential computer software. Valid license from Hewlett Packard
# Enterprise required for possession, use or copying.
#
# Consistent with FAR 12.211 and 12.212, Commercial Computer Software,
# Computer Software Documentation, and Technical Data for Commercial Items
# are licensed to the U.S. Government under vendor's standard commercial
# license.

import requests

Manifest = {
    'Name': 'connectivity_monitor',
    'Description': 'This script monitors the reachability between two '
                   'devices given the IP-SLA session'
                   'The IP-SLA session has to be configured in the switch'
                   'before using this script to monitor the '
                   'connectivity/rechability between two devices.',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'connectivity_check_rate': {
        'Name': 'Connectivity Check Rate (in minutes)',
        'Description': 'the rate at which, status of the connectivity is '
                       'checked. The value should be (at the least) twice '
                       'the probe-interval of the IP-SLA session.\n'
                       '{measured in minutes}\nDefault value is 1 minute '
                       '(assuming the min probe-interval as 5 seconds.)'
                       '\nMANDATORY FIELD',
        'Type': 'integer',
        'Default': 1
    },
    'ipsla_session_name': {
        'Name': 'IP-SLA Session Name',
        'Description': ('Agent will get statistics for this IP-SLA test. '
                        'The test must be configured through the cli with '
                        'the same name. \nMANDATORY FIELD'),
        'Type': 'string',
        'Default': ''
    }
}


class Agent(NAE):
    URI_PREFIX = '/rest/v1/system/ipsla_sources/'
    URI_STATUS = '?attributes=status.'
    FIELDS_STATUS = ["last_probe_time", "state"]
    CONNECTIVITY_CHECK = 'num_of_packets_rx'
    URI_STATISTICS = '?attributes=statistics.'
    FIELDS_STATISTICS = ["probes_timed_out"]

    def __init__(self):
        self.create_monitor()

    def generate_uri(self, param_name):
        uri_suffix = self.get_field_uri(param_name)
        uri = self.URI_PREFIX + '{}' + uri_suffix + param_name
        return uri

    def create_monitor(self):
        ipsla_session_name = str(
            self.params['ipsla_session_name'].value).replace(" ", "")
        if ipsla_session_name == "":
            self.error('Empty IP SLA source name passed to agent params')
        self.m1 = Monitor(self.generate_uri(self.FIELDS_STATUS[0]),
                          'ipsla_periodic_' +
                          self.FIELDS_STATUS[0],
                          [self.params['ipsla_session_name']])
        rule_name = 'IP SLA {{}}.{}'.format(self.FIELDS_STATUS[0])
        self.r1 = Rule(rule_name, [self.params['ipsla_session_name']])
        self.r1.condition('every {} minutes', [
                          self.params['connectivity_check_rate']])
        self.r1.action(self.action_call_back)

        self.m2 = Monitor(self.generate_uri(self.FIELDS_STATUS[1]),
                          'ipsla_source_status_' +
                          self.FIELDS_STATUS[1],
                          [self.params['ipsla_session_name']])
        check_rate = str(
            self.params['connectivity_check_rate'].value).replace(" ", "")
        rate_time_interval = check_rate + ' minutes'
        rate_uri = Rate(self.generate_uri(self.FIELDS_STATISTICS[0]),
                        rate_time_interval,
                        [self.params['ipsla_session_name']])
        self.m3 = Monitor(rate_uri, self.FIELDS_STATISTICS[0])

        g_title = 'IP SLA source={}'
        self.graph = Graph([self.m2, self.m3],
                           title=Title(g_title,
                                       [self.params['ipsla_session_name']]),
                           dashboard_display=True)

    def get_field_uri(self, field_name):
        if field_name in self.FIELDS_STATUS:
            return self.URI_STATUS
        if field_name in self.FIELDS_STATISTICS:
            return self.URI_STATISTICS
        self.error('Invalid field in threshold field. '
                   '{} not supported'.format(field_name))

    @staticmethod
    def rest_get(url):
        return requests.get(HTTP_ADDRESS + url, verify=False,
                            proxies={'http': None, 'https': None})

    def on_agent_re_enable(self, event):
        self.remove_alert()

    def on_parameter_change(self, params):
        self.remove_alert()

    def remove_alert(self):
        alert_level = self.get_alert_level()
        if (alert_level == AlertLevel.CRITICAL) or \
                (alert_level == AlertLevel.MINOR):
            self.remove_alert_level()
            ActionSyslog('Monitored remote IP is reachable, received '
                         'response Rx-packets for the IP-SLA '
                         'session {}.'.format(
                             self.params['ipsla_session_name'].value))

    def error(self, message):
        err_msg = ('IP SLA Agent Source={}. '
                   'Error: {}').format(
            self.params['ipsla_session_name'].value,
            message)
        raise Exception(err_msg)

    def create_cli_syslog(self):
        session_name = self.params['ipsla_session_name'].value
        ActionCLI('show ip-sla ' + session_name + ' results')
        ActionSyslog('Monitored remote IP is not reachable, response '
                     'Rx-packets were not received for the IP-SLA '
                     'session {}.'.format(
                         self.params['ipsla_session_name'].value))

    def create_alert(self):
        alert_level = self.get_alert_level()
        if alert_level is None:
            self.set_alert_level(AlertLevel.MINOR)
            self.create_cli_syslog()
        elif alert_level == AlertLevel.MINOR:
            self.set_alert_level(AlertLevel.CRITICAL)
            self.create_cli_syslog()

    def action_call_back(self, event):
        try:
            uri = '/rest/v1/system/ipsla_sources/' + \
                  self.params['ipsla_session_name'].value + \
                  '?attributes=sla_results&depth=3&selector=status'
            r = self.rest_get(uri)
            r.raise_for_status()
            sla_results = r.json()
            if self.CONNECTIVITY_CHECK not in sla_results['sla_results']:
                self.create_alert()
            else:
                rx_value = str(
                    sla_results['sla_results'][self.CONNECTIVITY_CHECK])
                rx_value = int(rx_value.replace(" ", ""))
                if rx_value == 0:
                    self.create_alert()
                else:
                    self.remove_alert()

        except (requests.RequestException, requests.ConnectionError,
                requests.Timeout, requests.HTTPError, requests.URLRequired,
                requests.TooManyRedirects):
            self.error(
                'Failed to process HTTP get-request for ipsla-results')

        except Exception as e:
            self.error(
                "Error in retrieving ipsla-session details {}".format(str(e)))
