# (c) Copyright 2022,2024 Hewlett Packard Enterprise Development LP
#
# Confidential computer software. Valid license from Hewlett Packard
# Enterprise required for possession, use or copying.
#
# Consistent with FAR 12.211 and 12.212, Commercial Computer Software,
# Computer Software Documentation, and Technical Data for Commercial Items
# are licensed to the U.S. Government under vendor's standard commercial
# license.

LONG_DESCRIPTION = '''\
## Script Description

The main components of the script are Manifest, Parameter Definitions and the python code.  

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters:
    1. connectivity_check_rate - the rate at which, status of the connectivity is checked. The value should be (at the least) twice the probe-interval of the IP-SLA session. It is measured in minutes. Default value is 1 minute (assuming the min probe-interval as 5 seconds.)
    2. ipsla_session_name - This parameter specifies ipsla-session name. Default value is ' '.

The script defines Monitor(s), Condition(s) and Action(s):

- Monitors: 
    1. Last Probe Time - (A placeholder monitor for the periodic call-back). Monitors the last_probe_time of the ip-sla session. This does not help in generating any alerts or action call-back. 
    2. State - (Only for Graph display). Monitor the state( state of IPSLA Session). Shows DNS Failure, Config failure etc...This monitor is used only for plotting the graph, does not help in generating any alerts.  But this field in graph does justify and reason the alerts created. 
    3. Probes Timed Out - (Only for Graph display). Monitor the probes timed out of IPSLA session.  if the connection is lost, the value of probes-timed-out is incremented, indicating the connection lost.  
    This monitor is used only for plotting the graph and does not help in generating any alerts. But this field in graph does justify and reason the alerts created. 
- Conditions: 
    1. Periodic call back for every connectivity_check_rate in minutes.
- Actions:
    1. Minor alert - When the connectivity between the source and destination is lost for the specific probe, minor alert is created.
    2. Critical alert - If the connectivity is still lost after the Minor alert, to indicate the consistent loss of connectivity a critical alert is generated.
    3. Normal alert -  When the connectivity between the source and destination IP is restored, Normal alert is generated.
'''

from json import dumps
import re

Manifest = {
    'Name': 'connectivity_monitor',
    'Description': 'This script monitors the reachability between two '
                   'devices given the IP-SLA session.'
                   'The IP-SLA session has to be configured in the switch '
                   'before using this script to monitor the '
                   'connectivity/reachability between two devices.',
    'Version': '3.0',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.11',
    'AOSCXPlatformList': ['8320', '8325']
}

ParameterDefinitions = {
    'connectivity_check_rate': {
        'Name': 'Connectivity Check Rate',
        'Description': 'the rate at which, status of the connectivity is '
                       'checked. The value should be (less than) twice '
                       'the probe-interval of the IP-SLA session.\n'
                       '{measured in minutes}\nDefault value is 1 minute '
                       '(assuming the min probe-interval as 40 seconds.)'
                       '\nMANDATORY FIELD',
        'Type': 'integer',
        'Default': 1
    },
    'ipsla_session_name': {
        'Name': 'IP-SLA Session Name',
        'Description': 'Agent will get statistics for this IP-SLA test. '
                       'The test must be configured through the cli with '
                       'the same name. \nMANDATORY FIELD',
        'Type': 'string',
        'Default': ''
    },
    'critical_alert_threshold': {
        'Name': '[Optional] ALERT CRITICAL COUNT',
        'Description': 'provides the max count of Minor Alert, after which '
                       'CRITICAL level alert is created. '
                       'This indicates the threshold of acceptable max '
                       'non-connectivity between the devices.\n'
                       'Default value is 1',
        'Type': 'integer',
        'Default': 1
    },
    'source_ip': {
        'Name': 'Source IP address',
        'Description': 'Enter the IP address for source.'
                       '\nMANDATORY FIELD',
        'Type': 'string',
        'Default': ''
    },
    'dest_ip': {
        'Name': 'Destination IP address',
        'Description': 'Enter the IP address for destination.'
                       '\nMANDATORY FIELD',
        'Type': 'string',
        'Default': ''
    },
    'vrf_name': {
        'Name': '[Optional] VRF name',
        'Description': 'Enter the VRF (of ip-sla source) '
                       'for the ip-sla session.',
        'Type': 'string',
        'Default': 'default'
    }
}


class Agent(NAE):
    URI_PREFIX = '/rest/v1/system/ipsla_sources/'
    URI_STATUS = '?attributes=status.'
    FIELDS_STATUS = ["last_probe_time", "state"]
    CONNECTIVITY_CHECK = 'num_of_packets_rx'

    def __init__(self):
        self.check_params()
        self.create_ipsla_session()
        self.create_monitor()
        self.variables['Minor_Alert_Count'] = "0"

    def check_params(self):
        ipsla_session_name = str(
            self.params['ipsla_session_name'].value).replace(" ", "")
        if ipsla_session_name == "":
            self.error('Empty IP SLA source name passed to agent params')

        source_ip = str(self.params['source_ip'].value).replace(" ", "")
        dest_ip = str(self.params['dest_ip'].value).replace(" ", "")
        pat = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        if not pat.match(source_ip):
            self.error('Invalid IP SLA source IP passed to agent params')
        if not pat.match(dest_ip):
            self.error('Invalid IP SLA source IP passed to agent params')

    def create_ipsla_session(self):
        vrf_name = str(self.params['vrf_name'].value).replace(" ", "")
        if vrf_name == "":
            vrf_name = "default"
        url = '/rest/v10.11/system/ipsla_sources/'
        vrf_url = "/rest/v10.11/system/vrfs/" + vrf_name
        session_name = self.params['ipsla_session_name'].value
        probe_interval = int(
            self.params['connectivity_check_rate'].value or 1) * 40
        source_ip = str(self.params['source_ip'].value).replace(" ", "")
        dest_ip = str(self.params['dest_ip'].value).replace(" ", "")
        payload = {
            "enable": True,
            "frequency": probe_interval,
            "name": session_name,
            "responder": {"hostname": dest_ip},
            "source_ip": source_ip,
            "type": "icmp_echo",
            "vrf": vrf_url}
        headers = {
            "content-type": "application/json", "Accept": "application/json"}
        try:
            self.get_rest_request_json(HTTP_ADDRESS + url + session_name,
                                       retry=1)
            self.logger.info("IPSLA session get succeeded")
            return
        except:
            try:
                response = self.post_rest_request(
                    HTTP_ADDRESS + url,
                    headers=headers,
                    data=dumps(payload))
                self.logger.info("Agent post succeeded")
            except NAEException:
                self.error(
                    'Failed to process HTTP request when creating IPSLA session')

    def generate_uri(self, param_name):
        uri_suffix = self.get_field_uri(param_name)
        uri = self.URI_PREFIX + '{}' + uri_suffix + param_name
        return uri

    def create_monitor(self):
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
                          'ipsla_status_' +
                          self.FIELDS_STATUS[1],
                          [self.params['ipsla_session_name']])
        g_title = 'IP SLA source={{}}, field={}'.format(self.FIELDS_STATUS[1])
        self.graph = Graph([self.m2],
                           title=Title(g_title,
                                       [self.params['ipsla_session_name']]),
                           dashboard_display=True)

    def get_field_uri(self, field_name):
        if field_name in self.FIELDS_STATUS:
            return self.URI_STATUS
        self.error('Invalid field in threshold field. '
                   '{} not supported'.format(field_name))

    def on_agent_re_enable(self, event):
        self.remove_alert()

    def on_parameter_change(self, params):
        self.remove_alert()

    def remove_alert(self):
        alert_level = self.get_alert_level()
        if (alert_level == AlertLevel.CRITICAL) or \
                (alert_level == AlertLevel.MINOR):
            self.remove_alert_level()
        self.variables['Minor_Alert_Count'] = "0"

    def error(self, message):
        err_msg = ('IP SLA Agent Source={}. '
                   'Error: {}').format(
            self.params['ipsla_session_name'].value,
            message)
        raise NAEException(err_msg)

    def create_alert(self, alert_threshold):
        session_name = self.params['ipsla_session_name'].value
        alert_count = int(self.variables['Minor_Alert_Count'])
        alert_count += 1
        if alert_count > alert_threshold:
            self.set_alert_level(AlertLevel.CRITICAL)
        else:
            self.set_alert_level(AlertLevel.MINOR)
            self.variables['Minor_Alert_Count'] = str(alert_count)
        ActionCLI('show ip-sla ' + session_name + ' results')

    def action_call_back(self, event):
        try:
            alert_threshold = int(
                self.params['critical_alert_threshold'].value or 1)
            uri = '/rest/v10.11/system/ipsla_sources/' + \
                  self.params['ipsla_session_name'].value + \
                  '?attributes=sla_results&depth=3&selector=status'
            sla_results = self.get_rest_request_json(HTTP_ADDRESS + uri)
            if self.CONNECTIVITY_CHECK not in sla_results['sla_results']:
                self.create_alert(alert_threshold)
            else:
                rx_value = str(
                    sla_results['sla_results'][self.CONNECTIVITY_CHECK])
                rx_value = int(rx_value.replace(" ", ""))
                if rx_value == 0:
                    self.create_alert(alert_threshold)
                else:
                    self.remove_alert()

        except NAEException:
            self.error(
                'Failed to process HTTP get-request for ipsla-results')

        except Exception as e:
            self.error(
                "Error in retrieving ipsla-session details {}".format(str(e)))
