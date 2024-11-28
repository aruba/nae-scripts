# -*- coding: utf-8 -*-
#
# (c) Copyright 2019-2024 Hewlett Packard Enterprise Development LP
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

from templateapi.api import *
from templateapi.nae import NAE
from templateapi.alert_level import AlertLevel
from templateapi.adc import ADCList, ADCEntry
from templateapi.action import ActionSyslog, ActionCLI, ActionCustomReport
from templateapi.monitor import *
from templateapi.constants import *

import ipaddress


Manifest = {
    'Name': 'application_health_monitor',
    'Description': 'Network Analytics agent script to monitor application health',
    'Version': '2.2',
    'Tags': ['application'],
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.08',
    'AOSCXPlatformList': ['5420', '6300', '64xx', '8100', '8320', '8325', '8400', '8360', '9300', '10000']
}

ParameterDefinitions = {
    'TCP_Application_IP_Address': {
        'Name': '<Constant> Server to monitor for anomalies',
        'Description': 'The Application Health Agent can monitor the aggregate TCP connection set-up handshakes between client and server to detect problems in connectivity.  This test measures the ratio of all connection acknowledgments (SYN-ACK packet from the server) to all connection requests (SYN packet from the client) passing through the switch.  If this ratio is less than 1.0 then some clients are not receiving an acknowledgement to their connection requests.  Enter the IP address for the application server.',
        'ErrorMsg': "The TCP_Application_IP_Address parameter value is invalid or was changed after agent creation. The agent cannot operate without a valid IP address and this parameter value cannot be changed; create a new agent using the correct value.",
        'Type': 'string',
        'Constant': 'True',
        'Default': ""
    },
    'TCP_Application_Port': {
        'Name': '<Constant> TCP protocol port for the application',
        'Description': 'The Application Health Agent can monitor the aggregate TCP connection set-up handshakes between clients and servers on this TCP port.  Enter the TCP port used by the application for client/server communication.',
        'ErrorMsg': "The TCP_Application_Port parameter value is invalid or was changed after agent creation.  The agent cannot operate without a valid TCP port number and this parameter cannot be changed; create a new agent using the correct value.",
        'Type': 'integer',
        'Constant': 'True',
        'Default': 443
    },
    'TCP_Application_VRF': {
        'Name': '<Constant> VRF for the application',
        'Description': 'The Application Health Agent can monitor the route  to the application server via this VRF.  Enter the VRF used for client/server communication.',
        'ErrorMsg': "The TCP_Application_VRF parameter value is invalid or was changed after agent creation.  Traceroute analysis cannot operate without a valid VRF and this parameter cannot be changed; create a new agent using the correct value.",
        'Type': 'string',
        'Constant': 'True',
        'Default': "default"
    },
    'TCP_SYN_Ratio': {
        'Name': 'Minimum ratio of server SYN/ACK to client SYN packets',
        'Description': 'The Application Health Agent will trigger an anomaly when the aggregate ratio of server SYN/ACK to client SYN packets goes below this value.  In a TCP connection set-up, the client sends a packet with the SYN TCP flag set and the server responds with a packet in which the SYN and ACK TCP flags are set.  If the sever responds to each client connection request, this ratio would be 1.0; if 95% of client connection requests receive a response, this ratio would be 0.95 (95/100).  Enter the minimum tolerable ratio of SYN/ACK to SYN packets over the previous 60 seconds.  A ratio below this value is an anomaly.',
        'ErrorMsg': "The TCP_SYN_Ratio parameter value must be between 0.01 and 1.00 (1% and 100%). Change this parameter to a valid value.",
        'Type': 'float',
        'Constant': 'False',
        'Default': 0.700
    },
    'VoIP_IPSLA_Name': {
        'Name': 'VOIP IP-SLA session to monitor for anomalies',
        'Description': 'The Application Health Agent can monitor a VoIP IP-SLA session, previously configured on the switch, to detect anomalies in connectivity and service level.  Enter the profile name of an IP-SLA of type VoIP in the switch configuration.  (Leave this value blank for no VoIP IP-SLA monitoring.)',
        'ErrorMsg': "The VoIP_IPSLA_Name parameter value is invalid. VoIP IP-SLA monitoring and analysis cannot operate without a valid IP-SLA name; configure an IP-SLA session with the name matching the parameter value.",
        'Type': 'string',
        'Constant': 'False',
        'Default': ""
    },
    'VoIP_Min_MOS': {
        'Name': 'Minimum MOS service level',
        'Description': 'The Application Health Agent will trigger an anomaly when the Mean Opinion Score (MOS) for the VoIP IP-SLA session probe it is monitoring falls below this value.  MOS scores range from 1 (users dissatisfied) to 5 (users very satisfied).  Enter the minimum tolerable MOS for the required service level.  A MOS score probe result lower than this value is an anomaly.',
        'ErrorMsg': "The VoIP_Min_MOS parameter value must be between 1.0 and 5.0. Change this parameter to a valid value.",
        'Type': 'float',
        'Constant': 'False',
        'Default': 3.60
    },
    'HTTP_IPSLA_Name': {
        'Name': 'HTTP IP-SLA session to monitor for anomalies',
        'Description': 'The Application Health Agent can monitor a HTTP IP-SLA session -- previously configured on the switch -- to detect anomalies in connectivity and service level.  Enter the profile name of an IP-SLA of type HTTP in the switch configuration.  (Leave this value blank for no HTTP IP-SLA monitoring.)',
        'ErrorMsg': "The HTTP_IPSLA_Name parameter value is invalid. HTTP IP-SLA monitoring and analysis cannot operate without a valid IP-SLA name; configure an IP-SLA session with the name matching the parameter value.",
        'Type': 'string',
        'Constant': 'False',
        'Default': ""
    },
    'HTTP_Max_RTT': {
        'Name': 'Maximum RTT service level',
        'Description': 'The Application Health Agent will trigger an anomaly when the Round Trip Time (RTT) for the HTTP IP-SLA session probe it is monitoring exceeds this value.  Enter the maximum tolerable RTT in milli-seconds for the required service level.  A RTT probe result greater that this value is an anomaly.',
        'ErrorMsg': "The HTTP_Max_RTT parameter value must be a positive integer. Change this parameter to a valid value.",
        'Type': 'integer',
        'Constant': 'False',
        'Default': 250
    }
}


##########################################################################
#
#   TCP SYN/ACK Connection Monitoring Sub-Agent
#
class TCP_SynAck:

    def __init__(self, agent):

        self.agent = agent

        # Register parameters
        self.ip = agent.register_parameter(
            'TCP_Application_IP_Address', self.valid_ip_address)
        self.port = agent.register_parameter(
            'TCP_Application_Port', self.valid_tcp_port)
        self.vrf = agent.register_parameter(
            'TCP_Application_VRF', self.valid_vrf)
        self.ratio = agent.register_parameter(
            'TCP_SYN_Ratio', self.valid_ratio)

        # Set up ADCs, monitors, rules and graphs if TCP monitoring is
        # configured
        if self.ip.is_valid() and self.port.is_valid():

            self.agent.logger.critical("setting up tcp synack monitors...")
            #   Ratio of SYN to SYN/ACK packets between Clients and Server (monitor and detect anomalies)
            #   Use an ADC to monitor the SYN, SYN/ACK, and RST packets
            # agent names are max 80 chars, but ADC names are max 64 chars
            adc_name = agent.name[0:64]
            adc_uri = "/rest/v1/system/adc_lists/" + \
                adc_name + "/ipv4?attributes=statistics."
            adc_status_uri = "/rest/v1/system/adc_lists/" + \
                adc_name + "/ipv4?attributes=status.code"
            self.tcp_adc = agent.adclist(adc_name, ADCList.Type.IPV4)

            # ADC entry to count number of SYN packets going to the application
            # server
            syn_entry = ADCEntry(ADCEntry.Type.MATCH)
            syn_entry.dst_ip(self.ip.value() + "/255.255.255.255")
            syn_entry.dst_l4_port(int(self.port.value()))
            syn_entry.protocol(ADCEntry.Protocol.TCP, flags={"tcp_syn": True})
            self.tcp_adc.add_entry(10, syn_entry)
            syn_traffic = agent.rate(adc_uri + "10", "60s")
            self.syn_monitor = agent.monitor(
                syn_traffic, "Connection request rate (packets per second)")

            # ADC entry to count number of SYN/ACK packets coming from the
            # application server
            ack_entry = ADCEntry(ADCEntry.Type.MATCH)
            ack_entry.src_ip(self.ip.value() + "/255.255.255.255")
            ack_entry.src_l4_port(int(self.port.value()))
            ack_entry.protocol(ADCEntry.Protocol.TCP, flags={
                               "tcp_ack": True, "tcp_syn": True})
            self.tcp_adc.add_entry(20, ack_entry)
            ack_traffic = agent.rate(adc_uri + "20", "60s")
            self.ack_monitor = agent.monitor(
                ack_traffic, "Connection response rate (packets per second)")

            # Detect connection setup issues by watching the ratio of SYN and
            # SYN/ACK rates
            self.syn_rule = agent.rule(
                "SYN/ACK to SYN Ratio Anomaly Change",
                action=self.syn_anomaly_detected,
                clear_action=self.syn_normal_detected)
            self.syn_rule.condition(
                "ratio of {} and {} < {}", [
                    self.ack_monitor, self.syn_monitor, self.ratio.reference])
            self.syn_rule.clear_condition(
                "ratio of {} and {} >= {} for 5 minutes", [
                    self.ack_monitor, self.syn_monitor, self.ratio.reference])

            #   Rate of RST from Server to Clients (monitor only -- to display in graph)
            # ADC entry to count number of RST packets coming from the
            # application server
            rst_entry = ADCEntry(ADCEntry.Type.MATCH)
            rst_entry.src_ip(self.ip.value() + "/255.255.255.255")
            rst_entry.src_l4_port(int(self.port.value()))
            rst_entry.protocol(ADCEntry.Protocol.TCP, flags={"tcp_rst": True})
            self.tcp_adc.add_entry(30, rst_entry)
            rst_traffic = agent.rate(adc_uri + "30", "60s")
            self.rst_monitor = agent.monitor(
                rst_traffic, "Connection reset rate (packets per second)")

            #  Web UI graph for TCP connection monitoring to aid the user when troubleshooting
            # Set up the web UI title and graph for SYN, SYN/ACK, and RST rates
            syn_title = Title(
                title="TCP Connection Set-up for Application Server {}, port {}",
                params=[self.agent.params['TCP_Application_IP_Address'], self.agent.params['TCP_Application_Port']])
            self.syn_graph = agent.graph(
                [self.rst_monitor, self.ack_monitor, self.syn_monitor], syn_title, dashboard_display=False)

            # monitor the total traffic from the clients to the server
            to_entry = ADCEntry(ADCEntry.Type.MATCH)
            to_entry.dst_ip(self.ip.value() + "/255.255.255.255")
            to_entry.dst_l4_port(int(self.port.value()))
            to_entry.protocol(ADCEntry.Protocol.TCP)
            self.tcp_adc.add_entry(40, to_entry)
            to_traffic = agent.rate(adc_uri + "40", "60s")
            self.to_monitor = agent.monitor(
                to_traffic, "Client to server traffic (packets per second)")

            # monitor the total traffic from the server to the clients
            frm_entry = ADCEntry(ADCEntry.Type.MATCH)
            frm_entry.src_ip(self.ip.value() + "/255.255.255.255")
            frm_entry.src_l4_port(int(self.port.value()))
            frm_entry.protocol(ADCEntry.Protocol.TCP)
            self.tcp_adc.add_entry(50, frm_entry)
            frm_traffic = agent.rate(adc_uri + "50", "60s")
            self.frm_monitor = agent.monitor(
                frm_traffic, "Server to client traffic (packets per second)")

            #  Web UI graph for TCP connection monitoring to aid the user when troubleshooting
            # Set up the web UI title and graph for SYN, SYN/ACK, and RST rates
            trf_title = Title(
                title="Total TCP Traffic for Application Server {}, port {}",
                params=[self.agent.params['TCP_Application_IP_Address'], self.agent.params['TCP_Application_Port']])
            self.trf_graph = agent.graph(
                [self.to_monitor, self.frm_monitor], trf_title, dashboard_display=True)

            #   Status of the ADCs used to monitor TCP connection setup
            #   Monitor ADC status to ensure it is continuously active
            self.adc_monitor = agent.monitor(
                adc_status_uri, "TCP Connection ADC Status")
            self.adc_rule = agent.rule(
                "TCP Connection ADC Status Change",
                action=self.failed_ADC_detected,
                clear_action=self.accepted_ADC_detected)
            self.adc_rule.condition("{} != 0", [self.adc_monitor])
            self.adc_rule.clear_condition("{} == 0", [self.adc_monitor])

    #########################################################
    # TCP Parameter Validation

    def valid_ip_address(self, input):
        value = input + "/255.255.255.255"
        try:
            ipaddress.ip_network(value)
            return True
        except BaseException:
            return False

    def valid_tcp_port(self, input):
        value = int(input)
        if (value >= 0 and value <= 65535):
            return True
        else:
            return False

    def valid_vrf(self, input):
        try:
            uri = "/rest/v10.08/system/vrfs/" + input
            self.agent.get_rest_request_json(HTTP_ADDRESS + uri, retry=1)
            return True
        except BaseException:
            return False

    def valid_ratio(self, input):
        value = float(input)
        # if ( value >= 0.01 and value <= 1.00 ):
        if (value >= 0.01 and value <= 1.00):
            return True
        else:
            return False

    #########################################################
    # Callbacks

    def failed_ADC_detected(self, event):
        self.agent.report(
            "TCP connection monitoring is suspended due to an internal ACL/ADC resource issue.",
            title="TCP Connection Monitoring Suspended")
        self.agent.alm.create_alert('ADC', 'failed', AlertLevel.MINOR)

    def accepted_ADC_detected(self, event):
        self.agent.report("TCP connection monitoring is resumed.",
                          title="TCP Connection Monitoring Resumed")
        self.agent.alm.delete_alert('ADC', 'failed')

    def syn_anomaly_detected(self, event):
        content = "An anomaly in TCP connection set-up has been detected.  The ratio of SYN-ACK to SYN packets between \
        clients communicating through this switch and the application server at IP address {} has fallen below the \
        required service level of {} specified by the TCP_SYN_Ratio parameter value.  This indicates that some clients are \
        not able to establish a TCP connection with the application server.".format(self.ip.value(), self.ratio.value())
        self.agent.report(
            content, title="TCP SYN-ACK/SYN Ratio Anomaly Detected")
        self.agent.alm.create_alert('SYN', 'anomaly', AlertLevel.CRITICAL)
        self.cli_cmd = 'traceroute {} dstport {} maxttl 7 vrf {} timeout 1 probes 2'.format(
            self.ip.value(), self.port.value(), self.vrf.value())
        self.agent.callback_action(cli_cmd=[self.cli_cmd])

    def syn_normal_detected(self, event):
        content = "The previously detected TCP connection set-up anomaly is no longer present.  The ratio of SYN-ACK \
        to SYN packets between clients communicating through this switch and the application server at IP address {} has \
        returned above the required service level of {} specified by the TCP_SYN_Ratio parameter \
        value.".format(self.ip.value(), self.ratio.value())
        self.agent.report(content, title="TCP SYN Returned to Normal")
        self.agent.alm.delete_alert('SYN', 'anomaly')


##########################################################################
#
#   IP-SLA Sub-Agent
#

class IPSLA:

    def __init__(self, ipsla_type, name_param, value_param, agent):
        self.agent = agent
        self.ipsla_type = ipsla_type
        self.name_param = name_param
        self.value_param = value_param
        self.cli_cmd = 'show ip-sla ' + self.ipsla_name + ' results'

        if ipsla_type == 'udp_jitter_voip':
            self.agent.register_parameter(
                'VoIP_IPSLA_Name', self.valid_ipsla_name)
            self.agent.register_parameter('VoIP_Min_MOS', self.valid_mos)

        if ipsla_type == 'http':
            self.agent.register_parameter(
                'HTTP_IPSLA_Name', self.valid_http_name)
            self.agent.register_parameter('HTTP_Max_RTT', self.valid_rtt)

        self.monitor_ipsla_session()

    @property
    def ipsla_name(self):
        return str(self.agent.params[self.name_param].value)

    def valid_ipsla_name(self, input):
        return True

    def valid_mos(self, input):
        value = float(input)
        if (value >= 1.00 and value <= 5.00):
            return True
        else:
            return False

    def valid_http_name(self, input):
        return True

    def valid_rtt(self, input):
        value = int(input)
        if (value >= 0):
            return True

    def monitor_ipsla_session(self):
        name_set = self.ipsla_name != ''
        if name_set:
            self.verify_ipsla_configuration()
            self.monitor_ipsla_status()
            self.create_ipsla_value_monitor()

    def verify_ipsla_configuration(self):
        '''
        Verifies IPSLA test exists and is running and is of correct type
        '''
        # Check if the ipsla session exists now...
        exists_uri = '/rest/v10.08/system/ipsla_sources/' + self.ipsla_name
        try:
            self.agent.get_rest_request_json(
                HTTP_ADDRESS + exists_uri, retry=1)
        except NAEException as error:
            if '404' in str(error):
                self.agent.variables[self.ipsla_name +
                                     '_session_exists'] = 'False'
        except Exception:
            pass

        # Monitor the state of the IPSLA test
        state_monitor = self.agent.monitor(
            '/rest/v1/system/ipsla_sources/{}?attributes=status.state',
            self.ipsla_type + '_' + self.ipsla_name + '_state_monitor',
            params=[self.agent.params[self.name_param]])
        state_rule = self.agent.rule(
            name='IPSLA ' + self.ipsla_type + ' State Error',
            action=self.ipsla_state_callback,
            clear_action=self.ipsla_state_clear_callback)

        # Use of {} != "running", as opposed to {} == "disabled", also catches
        # the condition that the test does not exist.
        state_rule.condition('{} != "running"', [state_monitor])
        state_rule.clear_condition('{} == "running"', [state_monitor])

        # Monitor the type of the IPSLA test
        type_monitor = self.agent.monitor(
            uri='/rest/v1/system/ipsla_sources/{}?attributes=type',
            name=self.ipsla_type + '_' + self.ipsla_name + '_type_monitor',
            params=[self.agent.params[self.name_param]])
        type_rule = self.agent.rule(
            name='IPSLA ' + self.ipsla_type + ' Type Error',
            action=self.ipsla_type_callback,
            clear_action=self.ipsla_type_clear_callback)
        ipsla_type_rule_condition = '{} != "{}"'.format('{}', self.ipsla_type)
        type_rule.condition(
            ipsla_type_rule_condition, [type_monitor])
        ipsla_type_rule_clear_condition = '{} == "{}"'.format('{}',
                                                              self.ipsla_type)
        type_rule.clear_condition(
            ipsla_type_rule_clear_condition, [type_monitor])

    def monitor_ipsla_status(self):
        '''
        Monitors the statistics of IP SLA session to help diagnose problems
        '''
        ipsla_rate_check_interval = \
            2 * self.get_probe_interval(self.ipsla_name)
        ipsla_rate_string = '{} seconds'.format(ipsla_rate_check_interval)
        ipsla_uri = '/rest/v1/system/ipsla_sources/{}?attributes='
        statistics = ['bind_error', 'destination_address_unreachable_count',
                      'dns_resolution_failures', 'probes_timed_out',
                      'socket_receive_error', 'transmission_error']

        # Check if any packets are received for voip sessions only
        # UDP session does not give as much information about packet status,
        # so packets_rx monitor helps catch errors earlier.
        if self.ipsla_type == 'udp_jitter_voip':
            packets_rx_monitor = self.agent.monitor(
                uri=ipsla_uri + 'sla_results.num_of_packets_rx',
                name=self.ipsla_type + '_' + self.ipsla_name + '_packets_rx_monitor',
                params=[self.agent.params[self.name_param]])
            packets_rx_rule = self.agent.rule(
                name='VOIP Packets RX Error',
                action=self.ipsla_status_callback,
                clear_action=self.ipsla_status_clear_callback)
            packets_rx_rule.condition(
                '{} == 0', [packets_rx_monitor])
            packets_rx_rule.clear_condition(
                '{} > 0', [packets_rx_monitor])
        for stat in statistics:
            rate = Rate(ipsla_uri + 'statistics.' + stat,
                        ipsla_rate_string, [self.agent.params[self.name_param]])
            stat_monitor = self.agent.monitor(
                uri=rate,
                name=self.ipsla_type + '_' + self.ipsla_name + '_' + stat + '_monitor')
            # create class variable for the rule
            stat_rule = self.agent.rule(
                name='IPSLA ' + self.ipsla_type + ' ' + stat + ' Error',
                action=self.ipsla_status_callback,
                clear_action=self.ipsla_status_clear_callback)
            stat_rule.condition('{} > 0', [stat_monitor])
            stat_rule.clear_condition('{} == 0',
                                      [stat_monitor])

    def create_ipsla_value_monitor(self):
        '''
        Monitors the IPSLA Value (either RTT or MOS)
        '''
        # time in minutes to clear short term threshold exceeded warning
        ipsla_threshold_short_clear_time = 5
        # time in minutes to clear long term threshold exceeded warning
        ipsla_threshold_long_clear_time = 10
        # time in minutes to set error level to critical for below threshold
        ipsla_threshold_critical_time = 5
        if self.ipsla_type == 'udp_jitter_voip':
            statistic = 'voip_mos'
            monitor_desc = 'VOIP MOS'
            condition = '{} < {}'
            clear_condition = '{} >= {}'
        else:
            statistic = 'average_rtt'
            monitor_desc = 'RTT (milliseconds)'
            condition = '{} > {}'
            clear_condition = '{} <= {}'
        value_monitor = self.agent.monitor(
            uri='/rest/v1/system/ipsla_sources/{}' +
                '?attributes=sla_results.' + statistic,
            name=self.ipsla_type + '_' + self.ipsla_name + '_' + statistic + '_monitor',
            params=[self.agent.params[self.name_param]])
        # Short term IPSLA value anomaly
        value_short_rule = self.agent.rule(
            name='Short-term IPSLA ' + self.ipsla_type + ' ' + monitor_desc + ' Anomaly',
            action=self.ipsla_value_anomaly_detected,
            clear_action=self.ipsla_value_normal_detected)
        value_short_rule.condition(
            condition, [value_monitor, self.agent.params[self.value_param]])
        short_rule_clear_condition = \
            (clear_condition + ' for {} minutes').format(
                '{}', '{}', ipsla_threshold_short_clear_time)
        value_short_rule.clear_condition(short_rule_clear_condition, [
                                         value_monitor, self.agent.params[self.value_param]])
        # Long term IPSLA Value anomaly
        value_long_rule = self.agent.rule(
            name='Long-term IPSLA ' + self.ipsla_type + ' ' + monitor_desc + ' Anomaly',
            action=self.ipsla_value_anomaly_detected,
            clear_action=self.ipsla_value_normal_detected)
        value_rule_long_condition = (condition + ' for {} minutes').format(
            '{}', '{}', ipsla_threshold_critical_time)
        value_long_rule.condition(value_rule_long_condition, [
                                  value_monitor, self.agent.params[self.value_param]])
        value_long_rule_clear_condition = \
            (clear_condition + ' for {} minutes').format(
                '{}', '{}', ipsla_threshold_long_clear_time)
        value_long_rule.clear_condition(value_long_rule_clear_condition, [
                                        value_monitor, self.agent.params[self.value_param]])
        # Create a graph for IPSLA data
        ipsla_value_title = Title(title=monitor_desc + ' Monitoring for IPSLA {}',
                                  params=[self.agent.params[self.name_param]])
        self.agent.graph(
            [value_monitor], title=ipsla_value_title, dashboard_display=False)

    def get_probe_interval(self, name_param):
        '''
        Returns the probe interval (frequency) of the IP SLA test
        '''
        if self.agent.variables.get(self.ipsla_name + '_session_exists') \
                == 'False':
            return 60
        uri = '/rest/v10.08/system/ipsla_sources/' + \
              self.ipsla_name + '?attributes=frequency'
        try:
            json_info = self.agent.get_rest_request_json(
                HTTP_ADDRESS + uri, retry=3)
            return int(str(json_info['frequency']))
        except Exception:
            pass
        return 60

    def ipsla_status_callback(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            syslog_msg = 'Error with test ' + test_name + ': ' + rule_desc
            self.agent.alm.create_alert(test_name, rule_desc, AlertLevel.MINOR)
            self.agent.callback_action([syslog_msg], [self.cli_cmd],
                                       [self.make_html_report()])

    def ipsla_status_clear_callback(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            syslog_msg = test_name + ': ' + rule_desc + ' cleared.'
            self.agent.alm.delete_alert(test_name, rule_desc)
            self.agent.callback_action([syslog_msg], [self.cli_cmd],
                                       [self.make_html_report()])

    def ipsla_state_callback(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            # Check if session exists
            exists_uri = '/rest/v10.08/system/ipsla_sources/' + test_name
            try:
                self.agent.get_rest_request_json(
                    HTTP_ADDRESS + exists_uri, retry=1)
                syslog_msg = 'The IPSLA session ' + test_name + \
                    ' is not running'
            except NAEException as error:
                if '404' in str(error):
                    syslog_msg = 'The IPSLA session ' + test_name + \
                                 ' does not exist.  Please create and ' + \
                                 'enable the session on switch command line.'
                    self.agent.variables[test_name + '_session_exists'] = \
                        'False'
                else:
                    syslog_msg = 'Unable to check ' + test_name + ' status.' + \
                        '  It is either not running or does not exist.'
            except Exception:
                syslog_msg = 'Unable to check ' + test_name + ' status.  ' + \
                             'It is either not running or does not exist.'
            self.agent.alm.create_alert(test_name, 'state', AlertLevel.MINOR)
            self.agent.callback_action([syslog_msg], [self.cli_cmd],
                                       [self.make_html_report()])

    def ipsla_state_clear_callback(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            self.agent.variables[test_name + '_session_exists'] = 'True'
            syslog_msg = 'The IPSLA session ' + test_name + ' is now running'
            self.agent.alm.delete_alert(test_name, 'state')
            self.agent.callback_action([syslog_msg], [self.cli_cmd],
                                       [self.make_html_report()])

    def ipsla_type_callback(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            if self.agent.variables.get(
                    test_name + '_session_exists') != 'False':
                syslog_msg = 'The type of IPSLA ' + test_name + \
                             ' is invalid. Expected "' + self.ipsla_type + \
                             '" type. Please correct ' + \
                             'the type from the switch command line.'
                self.agent.alm.create_alert(
                    test_name, 'type', AlertLevel.MINOR)
                self.agent.callback_action([syslog_msg], [self.cli_cmd],
                                           [self.make_html_report()])

    def ipsla_type_clear_callback(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            syslog_msg = test_name + ' type is now valid'
            self.agent.alm.delete_alert(test_name, 'type')
            self.agent.callback_action([syslog_msg], [self.cli_cmd],
                                       [self.make_html_report()])

    def ipsla_value_anomaly_detected(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            syslog_msg = test_name + ': ' + rule_desc
            if rule_desc[:5] == 'Short':
                # only show alert if no long term value anomaly in place
                if self.agent.variables.get(
                        'alert_' +
                        test_name +
                        '_long_anomaly') in [
                        'None',
                        None]:
                    self.agent.alm.create_alert(test_name, 'short_anomaly',
                                                AlertLevel.MAJOR)
                    self.agent.callback_action(
                        [syslog_msg], [
                            self.cli_cmd], [
                            self.make_html_report()])
            elif rule_desc[:4] == 'Long':
                self.agent.alm.create_alert(test_name, 'long_anomaly',
                                            AlertLevel.CRITICAL)
                self.agent.callback_action(
                    [syslog_msg], [
                        self.cli_cmd], [
                        self.make_html_report()])

    def ipsla_value_normal_detected(self, event):
        (test_name, rule_desc) = self.get_ipsla_test_name_rule_desc(event)
        if test_name and rule_desc:
            if rule_desc[:5] == 'Short':
                self.agent.alm.delete_alert(test_name, 'short_anomaly')
                # only show clear alert if no long term value anomaly in place
                if self.agent.variables.get(
                        'alert_' +
                        test_name +
                        '_long_anomaly') in [
                        'None',
                        None]:
                    syslog_msg = test_name + ': ' + rule_desc + ' cleared.'
                    self.agent.callback_action(
                        [syslog_msg], [
                            self.cli_cmd], [
                            self.make_html_report()])
            elif rule_desc[:4] == 'Long':
                syslog_msg = test_name + ': ' + rule_desc + ' cleared.'
                self.agent.alm.delete_alert(test_name, 'long_anomaly')
                self.agent.callback_action(
                    [syslog_msg], [
                        self.cli_cmd], [
                        self.make_html_report()])

    def get_ipsla_test_name_rule_desc(self, event):
        '''
        Returns the test name and rule description for a callback.
        '''
        try:
            temp_labels = event['labels'].split(',')
            labels = {}
            for label in temp_labels:
                temp_label = label.split('=')
                labels[temp_label[0]] = temp_label[1]
            test_name = labels['ipsla_source']
            rule_desc = event['rule_description']
            return (test_name, rule_desc)
        except Exception:
            return (None, None)

    def make_html_report(self):
        '''
        Create HTML report string containing details of the session.
        '''
        session_info = self.get_session()
        if session_info:
            report = HTML_HEAD
            report += '<h1>Session Details:</h1>'
            info_table = self.to_table(session_info)
            if info_table:
                report += info_table
            else:
                report += '<p>Error parsing json</p>'
        else:
            report = "<p>Error retrieving IPSLA session information.  To resolve this error, configure an IPSLA \
            on this switch of type {} with name {}.</p>".format(self.ipsla_type, self.ipsla_name)
        return report

    def get_session(self):
        url = '/rest/v10.08/system/ipsla_sources/' + self.ipsla_name
        try:
            return self.agent.get_rest_request_json(HTTP_ADDRESS + url, retry=3)
        except Exception:
            pass
        return None

    # Information to show for each IPSLA type for HTML custom report
    http_session_info = {
        'SLA Name': 'name',
        'SLA Status': [
            'status',
            'state'],
        'SLA Type': 'type',
        'VRF': 'vrf',
        'Source Port': 'source_port_number',
        'Source IP': 'effective_source_ip',
        'Source Interface': 'source_interface',
        'Domain Name Server': 'domain_name_server',
        'Probe Interval (seconds)': 'frequency',
        'HTTP Request Type': [
            'http_sla',
            'type'],
        'HTTP/HTTPS URL': [
            'http_sla',
            'url'],
        'Cache Disabled': [
            'http_sla',
            'cache_disable'],
        'HTTP Proxy URL': [
            'http_sla',
            'proxy_url'],
        'HTTP Version Number': [
            'http_sla',
            'version_number']}
    voip_session_info = {
        'SLA Name': 'name',
        'SLA Status': [
            'status',
            'state'],
        'SLA Type': 'type',
        'VRF': 'vrf',
        'Source IP': 'effective_source_ip',
        'Source Interface': 'source_interface',
        'Domain Name Server': 'domain_name_server',
        'Payload Size': 'payload_size',
        'TOS': 'tos',
        'Probe Interval (seconds)': 'frequency',
        'Advantage Factor': 'advantage_factor',
        'Codec Type': 'codec_type'}
    icmp_session_info = {
        'SLA Name': 'name',
        'SLA Status': [
            'status',
            'state'],
        'SLA Type': 'type',
        'VRF': 'vrf',
        'Source IP': 'effective_source_ip',
        'Source Interface': 'source_interface',
        'Domain Name Server': 'domain_name_server',
        'Payload Size': 'payload_size',
        'TOS': 'tos',
        'Probe Interval (seconds)': 'frequency',
    }

    def to_table(self, json_info):
        '''
        Convert json info to a table resembling show command from CLI.
        On error this function will return False, else return the table
        containing the json info.
        '''
        session_type = json_info.get('type')
        session_info = None
        if session_type == 'http':
            session_info = self.http_session_info
        elif session_type == 'icmp_echo':
            session_info = self.icmp_session_info
        elif session_type == 'udp_jitter_voip':
            session_info = self.voip_session_info
        else:
            # Unsupported IPSLA type
            self.agent.logger.critical(
                "Unsupported IPSLA type for custom report")
            return False
        if not json_info:
            return False
        table = '<table border="1">'
        for item in session_info:
            json_item = None
            str_item = 'N/A'
            path = session_info.get(item)
            if isinstance(path, list):
                json_item = json_info.get(path[0]).get(path[1])
            elif isinstance(path, str):
                json_item = json_info.get(path)
            if json_item is not None:
                str_item = str(json_item)
            if str_item[:5] == '/rest':
                # get only the name of the item
                str_item = str_item.split('/')[-1].replace('%2F', '/')
            table += '<tr><td>' + item + '</td><td>' + str_item + '</td></tr>'
        table += '</td></tr></table>'
        return table


##########################################################################
#
#   Application Health Agent
#

class Agent(NAE):

    def __init__(self):

        self.alm = AlertManager(self)
        self.pre_initialize_subagents()

        TCP_SynAck(self)
        IPSLA('http', 'HTTP_IPSLA_Name', 'HTTP_Max_RTT', self)
        IPSLA('udp_jitter_voip', 'VoIP_IPSLA_Name', 'VoIP_Min_MOS', self)

        self.post_initialize_subagents()

    #########################################################
    # Sub-Agent Utilities

    def pre_initialize_subagents(self):
        self.parameter = {}
        self.parameter_errors = {}
        self.subagent_callbacks = {}
        self.next_obj_id = 1

    def post_initialize_subagents(self):
        self.notify_of_invalid_parameters()
        pass

    def on_agent_creation(self):
        # Predicate that determines if this is the initial creation of the
        # agent
        try:
            nae_agent = self.get_rest_request_json(HTTP_ADDRESS + self.uri,
                                                   retry=3)
            if (nae_agent['nae_monitors']):
                return False
            else:
                return True
        except BaseException:
            self.logger.critical("on_agent_creation get operation failed")
            return False

    def adclist(self, name, type):
        a = ADCList(name, type)
        id = str(self.next_obj_id)
        self.next_obj_id += 1
        setattr(self, id, a)
        return a

    def rate(self, uri, time):
        r = Rate(uri, time)
        id = str(self.next_obj_id)
        self.next_obj_id += 1
        setattr(self, id, r)
        return r

    def monitor(self, uri, name, params=[]):
        m = Monitor(uri, name, params)
        id = str(self.next_obj_id)
        self.next_obj_id += 1
        setattr(self, id, m)
        return m

    def rule(self, name, action, clear_action):
        if name in self.subagent_callbacks:  # rule names must be globally unique
            raise ValueError
        r = Rule(name)
        if action is not None:
            r.action(self.action_dispatcher)
        if clear_action is not None:
            r.clear_action(self.clear_action_dispatcher)
        id = str(self.next_obj_id)
        self.next_obj_id += 1
        setattr(self, id, r)
        self.subagent_callbacks[name] = (action, clear_action)
        self.logger.critical("rule, callback registered for: " + name)
        return r

    def action_dispatcher(self, event):
        self.logger.critical("action_dispatcher, rule: " +
                             event['rule_description'])
        self.callback_dispatcher(event, 'action')

    def clear_action_dispatcher(self, event):
        self.callback_dispatcher(event, 'clear_action')

    def callback_dispatcher(self, event, type):
        name = event['rule_description']
        if name in self.subagent_callbacks:
            action, clear_action = self.subagent_callbacks[name]
            if type is 'action':
                action(event)
            else:
                clear_action(event)
        else:
            self.logger.critical("unknown callback: " + name)
            for c in self.subagent_callbacks:
                self.logger.critical("registered callback: " + c.key)

    def graph(self, monitors, title, dashboard_display):
        g = Graph(monitors, title=title, dashboard_display=dashboard_display)
        id = str(self.next_obj_id)
        self.next_obj_id += 1
        setattr(self, id, g)
        return g

    def report(self, content, title):
        ActionSyslog(title, severity=SYSLOG_WARNING)
        ActionCustomReport(content, title=Title(title))

    def callback_action(self, syslog_msg=[], cli_cmd=[], custom_rpt=[]):
        '''
        Create Syslog, HTML report, and CLI output report
        Parameters:
        - syslog_msg (optional) - list of messages to send to ActionSyslog
        - cli_cmd (optional) - list of commands to execute with ActionCLI
        - report (optional) - list of strings to create ActionCustomReport
        '''
        for msg in syslog_msg:
            custom_rpt += msg   # add these to the report, and also generate syslog messages
            ActionSyslog(msg, severity=SYSLOG_WARNING)
        for cmd in cli_cmd:
            ActionCLI(cmd)
        if len(custom_rpt) > 0:  # combine all reports into one...
            report = ""
            for rpt in custom_rpt:
                report += rpt
            ActionCustomReport(report)

    #########################################################
    # Parameters

    class Parameter():
        def __init__(
                self,
                name,
                reference,
                validator,
                error_msg,
                constant,
                default):
            self.name = name
            self.reference = reference
            self.validator = validator
            if constant == 'True':
                self.constant = True
            else:
                self.constant = False
            self.default = default
            self.error_msg = error_msg

        def is_valid(self):
            return self.validator(str(self.reference.value))

        def value(self):
            return str(self.reference.value)

    def register_parameter(self, name, validator):
        # Create object to track and validate parameter changes; notify of
        # invalid initial parameter values
        self.parameter[name] = self.Parameter(
            name,
            self.params[name],
            validator,
            ParameterDefinitions[name]['ErrorMsg'],
            ParameterDefinitions[name]['Constant'],
            ParameterDefinitions[name]['Default'])
        value = str(self.params[name].value)
        if self.parameter[name].validator(value) is False:
            # queue for invalid parameter notification
            self.parameter_errors.update({name: value})
        return self.parameter[name]

    def notify_of_invalid_parameters(self):
        # Agents cannot currently generate alerts in init, so setting up a
        # callback that will execute only once to do this work
        num_monitors_uri = '/rest/v1/system?attributes=capacities_status.nae_monitors'
        self.init_monitor = Monitor(
            num_monitors_uri, "Agent Initialization Complete")
        self.init_rule = Rule("Validate Initial Parameter Values")
        self.init_rule.condition("{} > 0", [self.init_monitor])
        self.init_rule.action(self.report_invalid_parameters)

    def report_invalid_parameters(self, event):
        # Callback to report invalid parameter values set during agent creation
        self.logger.critical("report_invalid_parameters callback called...")
        for name, bad_value in self.parameter_errors.items():
            self.logger.critical('   name: ' + name)
            self.logger.critical('   bad value: ' + bad_value)
            p = self.parameter[name]
            title = p.name + " Parameter Error"
            ActionCustomReport(p.error_msg.format(bad_value),
                               title=Title(title))
            ActionSyslog(title, severity=SYSLOG_WARNING)

    def on_parameter_change(self, params):
        # Callback to report invalid parameter values set after agent creation
        self.logger.critical(">>> parameter change")
        for name, value in params.items():
            if name in self.parameter:
                self.logger.critical("   name: " + name)
                self.logger.critical("   new value: " + str(value["new"]))
                self.logger.critical("   old value: " + str(value["old"]))
                p = self.parameter[name]
                if p.constant or p.validator(str(value['new'])) is False:
                    self.logger.critical(
                        "   constant or invalid parameter value")
                    title = p.name + " Parameter Error"
                    ActionCustomReport(p.error_msg.format(
                        str(value['new'])), title=Title(title))
                    ActionSyslog(title, severity=SYSLOG_WARNING)
                else:
                    self.logger.critical("   change is valid.")


##########################################################################
#
#   Alert Manager

class AlertManager:

    def __init__(self, agent):
        self.agent = agent

    def create_alert(self, test_name, key, alert_level):
        '''
        Adds given alert and sets the agent status to that alert if more severe
        than existing status.  Otherwise, just leave a the alert status as is.
        '''
        self.agent.variables['alert_' + test_name + '_' + key] = alert_level
        if (alert_level == AlertLevel.CRITICAL or
                (alert_level == AlertLevel.MAJOR and
                 self.agent.get_alert_level() != AlertLevel.CRITICAL) or
                (alert_level == AlertLevel.MINOR and
                 self.agent.get_alert_level() is None)):
            self.agent.set_alert_level(alert_level)

    def delete_alert(self, test_name, key):
        '''
        Removes given alert, sets agent status to most severe remaining, if any
        '''
        this_alert_level = self.agent.variables.get(
            'alert_' + test_name + '_' + key)
        self.agent.variables['alert_' + test_name + '_' + key] = \
            AlertLevel.NONE
        most_severe = AlertLevel.NONE
        remaining_alerts = False
        for alert_name in self.agent.variables:
            if alert_name[:6] == 'alert_':
                if (self.severity(self.agent.variables[alert_name]) >
                        self.severity(most_severe)):
                    most_severe = self.agent.variables[alert_name]
                    remaining_alerts = True
        if remaining_alerts:
            if self.severity(most_severe) < self.severity(this_alert_level):
                self.agent.set_alert_level(most_severe)
        else:
            self.agent.remove_alert_level()

    def severity(self, alert_level):
        '''
        Returns an integer representation of the severity of an alert level
        '''
        if alert_level == AlertLevel.NONE:
            return 0
        elif alert_level == AlertLevel.MINOR:
            return 1
        elif alert_level == AlertLevel.MAJOR:
            return 2
        elif alert_level == AlertLevel.CRITICAL:
            return 3
        else:
            # Invalid alert type
            return -1

##########################################################################


HTML_HEAD = '''<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1cm;
}
td, th {
    border: 1px solid #dddddd;
    text-align: left;
    vertical-align: top;
    white-space: nowrap;
    font-size: medium;
}
tr:nth-child(even) {
    background-color: #d8d5e5;
}
tr:hover {
    background-color: #efa837;
}
:checked {
  display: block;
}
</style>'''


LONG_DESCRIPTION = '''\
## Configuration Notes
The main components of the script are Manifest, Parameter Definitions and python code. 

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - TCP_Application_IP_Address: Server to monitor for anomalies
    - TCP_Application_Port: TCP protocol port for the application
    - TCP_Application_VRF: VRF for the application
    - TCP_SYN_Ratio: Minimum ratio of server SYN/ACK to client SYN packets
    - VoIP_IPSLA_Name: VOIP IP-SLA session to monitor for anomalies
    - VoIP_Min_MOS: Minimum MOS service level
    - HTTP_IPSLA_Name: HTTP IP-SLA session to monitor for anomalies
    - HTTP_Max_RTT: Maximum RTT service level
- Monitors:  This script specifies the monitoring URI(s) to monitor the following: 
    - Connection request rate (packets per second)
    - Connection response rate (packets per second)
    - Connection reset rate (packets per second)
    - Client to server traffic (packets per second)
    - Server to client traffic (packets per second)
    - TCP Connection ADC Status
    - IPSLA State Monitor
    - IPSLA Type Monitor
    - IPSLA Session Statistics
        - bind_error
        - destination_address_unreachable_count
        - dns_resolution_failures
        - probes_timed_out
        - socket_receive_error
        - transmission_error
- Actions:  This script performs the following actions:
    - When SYN/ACK to SYN ratio changes, it changes agent level to critical & executes CLI command.
    - When this ratio gets to normal, agent status sets to normal. Along with this agent report generated & previous critical alert gets deleted.
    - When ADC status changes, Agent status is set to Minor & agent report generated.
    - When this status gets back to normal, previous alert gets deleted & agent report generated.
    - When VOIP packets rx error detected, agent status is set to minor & agent report generated.
    - When this error clears, corresponding alert is deleted & html report is generated.
    - When IPSLA state is not running, agent status is set to minor & agent report generated.
    - When IPSLA state is  running, corresponding alert is deleted & html report is generated.
    - When IPSLA type error detected, agent status is set to minor & agent report generated.
    - When IPSLA type error cleared, corresponding alert is deleted & html report is generated.
    - When IPSLA value anomaly detected, agent status is set to critical & agent report generated.
    - When IPSLA value anomaly cleared, corresponding alert is deleted & html report is generated.
    - When IPSLA session statistics have a count greater than 0, agent status is set to minor & agent report generated.
    - When IPSLA session statistics have a count equal to 0, corresponding alert is cleared & html report is generated.
## Script Limitations
The path of traffic within VSX topologies may raise false positive alerts; specifically, when traffic is received by VSX#1 and transmitted by VSX#2.
For instance, suppose there exists a two-member VSX topology with devices VSX#1 and VSX#2. Both devices have the Application Health script configured and agents deployed.  The client (application) sends requests to a server, so the traffic goes from Client -> L2 Switch -> VSX#2 -> VSX#1 -> Server. When the server responds, the traffic goes from Server -> VSX#1 -> L2 Switch -> Client (skipping VSX#2), and generates a false critical alert in VSX#2.
'''