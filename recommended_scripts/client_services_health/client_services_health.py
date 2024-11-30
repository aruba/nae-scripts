# -*- coding: utf-8 -*-
#
# (c) Copyright 2021-2024 Hewlett Packard Enterprise Development LP
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

#               - Client Services monitor functionality -
#   Clients within the network require a basic set of services in order to
#   to function on the network. This agent will monitor the following three
#   services and ensure they are available. The script can be loaded normally
#   via the WebUI and none of the parameters are required to be configured,
#   but can be for greater control over thresholds and monitoring.
#
# 1. DHCP
# Overview
# The monitoring of DHCP involves the use of ADC lists to ensure the ratio of
# server responses and client requests remains near 1:1. If the script
# detects the ratio drop below a configurable ratio there will be an alert
# fired. This ratio is affected by the number of DHCP servers in the
# environment, potentially causing the ratio to drop more slowly with more
# servers responding. This agent does not monitor DHCP connectivity when the
# switch is acting as the DHCP server or relay nor does it monitor any DHCP
# traffic associated with the switch's DHCP client.
#
# Related parameters
# 'DHCP_resp_to_req_ratio'      threshold ratio of DHCP responses to requests
#                               (Default: '0.7')
#
# 2. DNS
# Overview
# Similar to DHCP, DNS will also use ADC lists to monitor the ratio of responses
# to requests and fire an alert if it detects the ratio drop below a
# configurable ratio. Since DNS uses UDP, but can use TCP when UPD fails or
# when the query contains a large response, we will use separate ADC rules to
# monitor for either protocol. This agent does not monitor any DNS traffic
# associated with the switch's DNS client.
#
# Related parameters
# 'DNS_resp_to_req_ratio'       threshold ratio of DNS responses to requests
#                               (Default: '0.7')
#
# 3. RADIUS
# Overview
# By leveraging the built in RADIUS server tracking feature, we will monitor
# the availability of the configured RADIUS servers. The reachablility status
# of all of the tracking-enabled servers will be monitored for a change from
# 'reachable' to 'unreachable' and an alert will be fired if that is detected.
#
# Related parameters
# 'VRF_name'                    used to specify a single VRF to monitor the
#                               RADIUS servers on
#                               (Default: '*' - will monitor all VRFs)
#
#                      Important RADIUS notes
#   For this agent to be able to monitor radius servers, they each must have
#   tracking enabled via the config CLI.
#       ex. (config) radius-server host X.X.X.X tracking enable
#
#   The interval for the tracking requests can be configured between
#   60-86400 seconds (default: 300). A lower interval may be more desirable for
#   closer monitoring of RADIUS servers.
#       ex. (config) radius-server tracking interval 60
#
#                           REST Interface
#   There are three NAE variables in use by this agent. Their purpose is to
#   track the alert status of each of the clients being tracked by this agent.
#   The variables are created on agent init and initialized to be "None" for
#   each of the three clients. These variables are accessible from the
#   REST interface within the NAE_Agents' local_storage attribute.
#
#       ex. https://<switch_ip>//rest/v1/system/nae_scripts/<script_name>/nae_agents/<agent_name>?attributes=local_storage
#
#   Response output containing the published NAE variables:
#       {
#          "local_storage": {
#            "alert_DHCP_dhcp_response_ratio": "None",
#            "alert_DNS_tcp_response_ratio": "None",
#            "alert_DNS_udp_response_ratio": "None",
#            "alert_RADIUS_server_reachability": "CRITICAL",
#            "unreachable_radius_servers": "[\"11.0.0.11_default\", \"10.0.0.10_default\"]"
#          }
#       }

LONG_DESCRIPTION = '''\
## Script Description

### Client Services monitor functionality
Clients within the network require a basic set of services in order to
to function on the network. This agent will monitor the following three
services and ensure they are available. The script can be loaded normally
via the WebUI and none of the parameters are required to be configured,
but can be for greater control over thresholds and monitoring.

1. DHCP
The monitoring of DHCP involves the use of ADC lists to ensure the ratio of
server responses and client requests remains near 1:1. If the script
detects the ratio drop below a configurable ratio there will be an alert
fired. This ratio is affected by the number of DHCP servers in the
environment, potentially causing the ratio to drop more slowly with more
servers responding. This agent does not monitor DHCP connectivity when the
switch is acting as the DHCP server or relay nor does it monitor any DHCP
traffic associated with the switch's DHCP client.

Related parameters:
'DHCP_resp_to_req_ratio' - threshold ratio of DHCP responses to requests (Default: '0.7')

2. DNS
Similar to DHCP, DNS will also use ADC lists to monitor the ratio of responses
to requests and fire an alert if it detects the ratio drop below a
configurable ratio. Since DNS uses UDP, but can use TCP when UPD fails or
when the query contains a large response, we will use separate ADC rules to
monitor for either protocol. This agent does not monitor any DNS traffic
associated with the switch's DNS client.

Related parameters:
'DNS_resp_to_req_ratio' - threshold ratio of DNS responses to requests (Default: '0.7')

3. RADIUS
By leveraging the built in RADIUS server tracking feature, we will monitor
the availability of the configured RADIUS servers. The reachablility status
of all of the tracking-enabled servers will be monitored for a change from
'reachable' to 'unreachable' and an alert will be fired if that is detected.

For this agent to be able to monitor radius servers, they each must have tracking enabled via the config CLI.
    ex. (config) radius-server host X.X.X.X tracking enable
The interval for the tracking requests can be configured between 60-86400 seconds (default: 300).
A lower interval may be more desirable for closer monitoring of RADIUS servers.
    ex. (config) radius-server tracking interval 60

Related parameters:
'VRF_name' - used to specify a single VRF to monitor the RADIUS servers on (Default: '*' - will monitor all VRFs)
'''

import json
import uuid
from templateapi.nae import NAE
from templateapi.alert_level import AlertLevel
from templateapi.adc import ADCList, ADCEntry
from templateapi.action import ActionSyslog
from templateapi.monitor import *
from templateapi.constants import *

Manifest = {
    'Name': 'client_services_health',
    'Description': 'Client Service Health for Radius, DNS and DHCP',
    'Version': '4.2',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.13.1000',
    'AOSCXPlatformList': ['5420', '6200', '6300', '64xx', '8100', '8320', '8325', '8360', '9300', '10000']
}
ParameterDefinitions = {
    'VRF_name': {
        'Name': 'VRF identifier to specify which RADIUS servers',
        'Description': 'The VRF of which to monitor Radius servers on.',
        'Type': 'string',
        'Default': '*',
        'Required': True
    },
    'DNS_resp_to_req_ratio': {
        'Name': 'Minimum ratio of DNS server response to client request packets',
        'Description': 'The Client Services Agent will trigger an anomaly '
                       'when the aggregate ratio of '
                       'DNS server responses (UDP/TCP src 53) to '
                       'DNS client requests (UDP/TCP dst 53) packets goes '
                       'below this value. Enter the minimum tolerable ratio '
                       'of DNS server responses to client requests over the '
                       'previous 60 seconds. A ratio below this value is an '
                       'anomaly. Include a leading 0 for values below 1.',
        'ErrorMsg': 'The DNS_resp_to_req_ratio parameter value must be between '
                    '0.01 and 1.00 (1% and 100%). Change this parameter to a '
                    'valid value.  Include a leading 0 for values below 1.',
        'Type': 'float',
        'Constant': 'False',
        'Default': 0.700
    },
    'DHCP_resp_to_req_ratio': {
        'Name': 'Minimum ratio of DHCP server response to client request packets',
        'Description': 'The Client Services Agent will trigger an anomaly when '
                       'the aggregate ratio of DHCP server responses (UDP dst 68) to DHCP '
                       'client requests (UDP dst 67) goes below this value.  Enter the '
                       'minimum tolerable ratio of DHCP server responses to client requests '
                       'over the previous 60 seconds.  A ratio below this value is an '
                       'anomaly.  Include a leading 0 for values below 1.',
        'ErrorMsg': 'The DHCP_resp_to_req_ratio parameter value must be '
                    'between 0.01 and 1.00 (1% and 100%). Change this '
                    'parameter to a valid value.  Include a leading 0 for values below 1.',
        'Type': 'float',
        'Constant': 'False',
        'Default': 0.700
    }
}


RADIUS_KEY = "Radius"
DNS_KEY = "DNS"
DHCP_KEY = "DHCP"
NORMAL = "Normal"

# RADIUS Sub-Agent


class RADIUS:
    def __init__(self, agent, alm):
        self.alm = alm
        self.agent = agent
        self.monitors = {}
        self.rules = {}
        self.graphs = {}
        self.watches = {}
        self.agent.logger.debug("RADIUS server subagent start")

    def create_monitors(self):
        '''
        This function creates the necessary monitors for the subagent and
        returns them as a list.
        '''
        return []

    def create_watches(self):
        '''
        This function creates the necessary watches for the subagent and
        returns them as a list.
        '''
        radius_event_logs = '2304'
        self.watches['radius_reachability'] = WatchEventLog(
            radius_event_logs, 'Watch RADIUS Reachability')
        return list(self.watches.values())

    def create_rules(self):
        '''
        This function sets the conditions and actions for subagents rules. This
        also sets the clear conditions and actions.
        '''
        radius_rule = Rule('Rule for RADIUS reachability')

        radius_rule.condition_watch_event_log(
            '{}', [self.watches['radius_reachability']])

        radius_rule.action(self.radius_status_transition_action)

        self.rules['radius_reachability'] = radius_rule

        return list(self.rules.values())

    def create_graphs(self):
        '''
        This function will check for monitors created by the subagent and
        created the necessary graphs associated with those monitors.
        '''
        return []

    def is_valid_vrf(self, vrf_name):
        '''
        This function checks if the passed in vrf_name is wanting to be
        watched based on the parameters used for this script.
        '''
        if str(self.agent.params['VRF_name']) == '*':
            return True
        if str(self.agent.params['VRF_name']) == vrf_name:
            return True
        return False

    def parse_radius_eventlog(self, eventlog):
        '''
        Parses the eventlog to find the Server IP and VRF ID in the eventlog.
        The function then performs a REST call to figure out the VRF name
        corresponding to the VRF ID and returns the data in the format of:
        ServerIP, VRFname
        '''

        '''
        example of event log message:
        "Event|2304|LOG_INFO|AMM|1/1|RADIUS Server with Address:1.1.1.1,
        Authport:1812, VRF_ID:0 is \"unreachable\""
        '''
        eventlog_list = eventlog.split()
        ip = None
        vrf = None
        for token in eventlog_list:
            if token.startswith('Address:'):
                # token is: Address:1.1.1.1,
                ip = token.split(':')[1].split(',')[0]
                # ip = 1.1.1.1
            if token.startswith('VRF_ID:'):
                # token is: VRF_ID:0
                vrf = token.split(':')[1]
                # vrf = 0

        if not ip:
            raise KeyError(
                "Server IP not found in RADIUS eventlog: " + eventlog)
        if not vrf:
            raise KeyError("VRF_ID not found in RADIUS eventlog: " + eventlog)

        vrf_query_url = "{}/rest/v10.10/system/vrfs?attributes=name&filter=table_id:{}".format(
            HTTP_ADDRESS, vrf)
        vrf_data = self.agent.get_rest_request_json(
            vrf_query_url, retry=3, wait_between_retries=3)

        vrf_name = None
        for key in vrf_data:
            vrf_name = key
        if not vrf_name:
            raise KeyError(
                "VRF name not found from VRF ID in RADIUS eventlog: " + eventlog)

        server_info = ip + "_" + vrf_name

        return ip, vrf_name, server_info

    def radius_status_transition_action(self, event):
        '''
        Need this empty function so the Agent gets created properly since the
        subagent gets merged into the main agent.
        '''
        return

    def status_transition_action_reachable(self, server_info):
        '''
        This is the callback function for when a RADIUS server transition is
        seen. This will set or clear the alert level for the RADIUS subagent.
        '''
        try:
            unreachable_servers = json.loads(
                self.agent.variables['unreachable_radius_servers'])
        except (NameError, KeyError):
            self.agent.logger.debug(
                "Agent local variables not yet created by time of alert, so nothing to change/check there.")
            return

        self.agent.logger.debug('CLIENT SERVICES: critical RADIUS servers before: {}'
                                .format(unreachable_servers))

        # Log RADIUS reachability event
        self.agent.logger.debug(
            "RADIUS server: {} reachable".format(server_info))
        # Remove the server from tracking and update NAE data variable
        if server_info in unreachable_servers:
            unreachable_servers.pop(unreachable_servers.index(server_info))
            self.agent.variables['unreachable_radius_servers'] = json.dumps(
                unreachable_servers
            )
        # Remove the RADIUS alert if there are no other unreachable servers
        if not unreachable_servers:
            self.agent.clear_alert_description_for_key(RADIUS_KEY)
            self.alm.update_alert(
                "RADIUS", "server_reachability", AlertLevel.NONE)
        else:
            self.agent.set_alert_description_for_key(
                RADIUS_KEY, "Unreachable servers: {}".format(unreachable_servers))
        self.agent.logger.debug('CLIENT SERVICES: critical RADIUS servers after: {}'
                                .format(unreachable_servers))

    def status_transition_action_unreachable(self, server_info):
        '''
        This is the callback function for when a RADIUS server transition is
        seen. This will set or clear the alert level for the RADIUS subagent.
        '''
        try:
            unreachable_servers = json.loads(
                self.agent.variables['unreachable_radius_servers'])
        except (NameError, KeyError):
            self.agent.logger.debug(
                "Agent local variables not yet created by time of alert, the RADIUS portion will be created here.")
            unreachable_servers = []

        self.agent.logger.debug('CLIENT SERVICES: critical RADIUS servers before: {}'
                                .format(str(unreachable_servers)))

        # Log RADIUS unreachability event
        self.agent.logger.debug(
            "RADIUS server: {} unreachable/reachability_unhealthy".format(server_info))
        # Append the new server info and update NAE data variable
        if server_info not in unreachable_servers:
            unreachable_servers.append(server_info)
            self.agent.variables['unreachable_radius_servers'] = json.dumps(
                unreachable_servers
            )
        self.agent.set_alert_description_for_key(
            RADIUS_KEY, "Unreachable servers: {}".format(unreachable_servers))

        # Create alert for RADIUS
        self.alm.update_alert(
            "RADIUS", "server_reachability", AlertLevel.CRITICAL)

        self.agent.logger.debug('CLIENT SERVICES: critical RADIUS servers after: {}'
                                .format(unreachable_servers))

    def on_parameter_change(self, params):
        unreachable_servers = []
        self.agent.variables['unreachable_radius_servers'] = json.dumps(
            unreachable_servers)

# DNS Sub-Agent


class DNS:
    def __init__(self, agent, alm):
        self.alm = alm
        self.agent = agent
        self.monitors = {}
        self.rules = {}
        self.graphs = {}
        self.watches = {}
        self.adc_list = None
        self.ratio = self.agent.params['DNS_resp_to_req_ratio']
        # Create ADC to monitor the DNS traffic
        self.dns_adc_name = "dns_monitor"
        self.agent.logger.debug("DNS subagent start")

    def create_monitors(self):
        '''
        This function creates the necessary montiors for the subagent and
        returns them as a list.
        '''
        uri = "/rest/v1/system/adc_lists/" + \
            self.dns_adc_name + "/ipv4?attributes=statistics."

        self.adc_list = self.agent.adclist(
            self.dns_adc_name, ADCList.Type.IPV4)
        # ADC entry to count number of TCP SYN packets going to the application
        # server
        tcp_requests = ADCEntry(ADCEntry.Type.MATCH)
        tcp_requests.dst_l4_port(53)
        tcp_requests.protocol(ADCEntry.Protocol.TCP, flags={"tcp_syn": True})
        self.adc_list.add_entry(10, tcp_requests)
        tcp_req_traffic = Rate(uri + "10", "60s")
        self.monitors['tcp_req_monitor'] = Monitor(
            tcp_req_traffic, "TCP connection request rate (packets per second)")

        # ADC entry to count number of TCP SYN/ACK packets coming from the
        # application server
        tcp_responses = ADCEntry(ADCEntry.Type.MATCH)
        tcp_responses.src_l4_port(53)
        tcp_responses.protocol(ADCEntry.Protocol.TCP, flags={
            "tcp_ack": True, "tcp_syn": True})
        self.adc_list.add_entry(20, tcp_responses)
        tcp_resp_traffic = Rate(uri + "20", "60s")
        self.monitors['tcp_resp_monitor'] = Monitor(
            tcp_resp_traffic, "TCP connection response rate (packets per second)")

        # ADC entry to count number of DNS requests using UDP
        udp_requests = ADCEntry(ADCEntry.Type.MATCH)
        udp_requests.dst_l4_port(53)
        udp_requests.protocol(ADCEntry.Protocol.UDP)
        self.adc_list.add_entry(30, udp_requests)
        udp_req_traffic = Rate(uri + "30", "60s")
        self.monitors['udp_req_monitor'] = Monitor(
            udp_req_traffic, "UDP request rate (packets per second)")

        # ADC entry to count number of DNS responses using UDP
        # coming from the application server
        udp_responses = ADCEntry(ADCEntry.Type.MATCH)
        udp_responses.src_l4_port(53)
        udp_responses.protocol(ADCEntry.Protocol.UDP)
        self.adc_list.add_entry(40, udp_responses)
        udp_resp_traffic = Rate(uri + "40", "60s")
        self.monitors['udp_resp_monitor'] = Monitor(
            udp_resp_traffic, "UDP response rate (packets per second)")

        return list(self.monitors.values())

    def create_watches(self):
        return []

    def create_rules(self):
        '''
        This function sets the conditions and actions for subagents rules. This
        also sets the clear conditions and actions.
        '''
        # Rule tracking DNS TCP response to request anomalies
        r1 = Rule("DNS TCP Response to Requests Ratio Anomaly Change")

        # Detect DNS TCP connection setup issues by watching the ratio of TCP SYN and
        # SYN/ACK rates
        r1.condition("ratio of {} and {} < {} for 30 seconds", [
            self.monitors['tcp_resp_monitor'], self.monitors['tcp_req_monitor'], self.ratio])
        r1.action(self.set_dns_tcp_ratio_alert)
        r1.clear_condition("ratio of {} and {} >= {} for 1 minute", [
            self.monitors['tcp_resp_monitor'], self.monitors['tcp_req_monitor'], self.ratio])
        r1.clear_action(self.remove_dns_tcp_ratio_alert)

        # Rule tracking DNS UDP response to request anomalies
        r2 = Rule("DNS UDP Response to Requests Ratio Anomaly Change")

        # Detect DNS UDP traffic issues by watching the ratio of DNS requests and
        # responses using UDP
        r2.condition("ratio of {} and {} < {} for 30 seconds", [
            self.monitors['udp_resp_monitor'], self.monitors['udp_req_monitor'], self.ratio])
        r2.action(self.set_dns_udp_ratio_alert)
        r2.clear_condition("ratio of {} and {} >= {} for 1 minute", [
            self.monitors['udp_resp_monitor'], self.monitors['udp_req_monitor'], self.ratio])
        r2.clear_action(self.remove_dns_udp_ratio_alert)

        self.rules['dns_tcp_status'] = r1
        self.rules['dns_udp_status'] = r2

        return list(self.rules.values())

    def create_graphs(self):
        '''
        This function will check for monitors created by the subagent and
        created the necessary graphs associated with those monitors.
        '''
        if bool(self.monitors):
            self.graphs['dns_tcp_status'] = \
                Graph([self.monitors['tcp_req_monitor'], self.monitors['tcp_resp_monitor']],
                      title=Title("DNS TCP resp to req ratio status"),
                      dashboard_display=True)
            self.graphs['dns_udp_status'] = \
                Graph([self.monitors['udp_req_monitor'], self.monitors['udp_resp_monitor']],
                      title=Title("DNS UDP resp to req ratio status"),
                      dashboard_display=False)
            return list(self.graphs.values())
        else:
            return []

    def set_dns_tcp_ratio_alert(self, event):
        '''
        This is the callback function when the dns tcp ratio threshold is met.
        This sets the alert level to critical and logs the event.
        '''
        # Alert level is set to critical when the DNS TCP ratio hits its threshold
        self.alm.update_alert("DNS", "tcp_response_ratio", AlertLevel.CRITICAL)
        self.agent.set_alert_description_for_key(
            DNS_KEY, "Anomaly detected in DNS TCP connection")
        self.agent.logger.debug("Detected DNS TCP connection ratio hit "
                                "threshold")

    def remove_dns_tcp_ratio_alert(self, event):
        '''
        This is the callback function to remove the alert when the dns tcp
        ratio returns to an acceptable ratio and log the event.
        '''
        udp_ratio_key = "alert_{}_{}".format("DNS", "udp_response_ratio")
        # Alert level is cleared when the DNS TCP ratio returns to above the threshold
        self.alm.update_alert("DNS", "tcp_response_ratio", AlertLevel.NONE)
        if udp_ratio_key not in self.agent.variables:
            self.agent.clear_alert_description_for_key(DNS_KEY)
        elif self.agent.variables[udp_ratio_key] == AlertLevel.NONE:
            self.agent.clear_alert_description_for_key(DNS_KEY)
        else:
            self.agent.set_alert_description_for_key(
                DNS_KEY, "Anomaly detected in DNS UDP connection")
        self.agent.logger.debug("Detected DNS TCP connection ratio "
                                "returned to above the threshold")

    def set_dns_udp_ratio_alert(self, event):
        '''
        This is the callback function when the dns udp ratio threshold is met.
        This sets the alert level to critical and logs the event.
        '''
        # Alert level is set to critical when the DNS UDP ratio hits its threshold
        self.alm.update_alert("DNS", "udp_response_ratio", AlertLevel.CRITICAL)
        self.agent.set_alert_description_for_key(
            DNS_KEY, "Anomaly detected in DNS UDP connection")
        self.agent.logger.debug("Detected DNS UDP response to request ratio hit "
                                "threshold")

    def remove_dns_udp_ratio_alert(self, event):
        '''
        This is the callback function to remove the alert when the dns udp
        ratio returns to an acceptable ratio and log the event.
        '''
        tcp_ratio_key = "alert_{}_{}".format("DNS", "tcp_response_ratio")
        # Alert level is cleared when the DNS UDP ratio returns to above the threshold
        self.alm.update_alert("DNS", "udp_response_ratio", AlertLevel.NONE)
        if tcp_ratio_key not in self.agent.variables:
            self.agent.clear_alert_description_for_key(DNS_KEY)
        elif self.agent.variables[tcp_ratio_key] == AlertLevel.NONE:
            self.agent.clear_alert_description_for_key(DNS_KEY)
        else:
            self.agent.set_alert_description_for_key(
                DNS_KEY, "Anomaly detected in DNS TCP connection")
        self.agent.logger.debug("Detected DNS UDP response to request ratio "
                                "returned to above the threshold")


# DHCP Sub-Agent

class DHCP:
    def __init__(self, agent, alm):
        self.alm = alm
        self.agent = agent
        self.monitors = {}
        self.watches = {}
        self.rules = {}
        self.graphs = {}
        self.adc_list = None
        self.ratio = self.agent.params['DHCP_resp_to_req_ratio']
        # Create ADC to monitor the DHCP traffic
        self.dhcp_adc_name = "dhcp_monitor"

        self.agent.logger.debug("DHCP subagent start")

    def create_monitors(self):
        '''
        This function creates the necessary montiors for the subagent and
        returns them as a list.
        '''
        uri = "/rest/v1/system/adc_lists/" + \
            self.dhcp_adc_name + "/ipv4?attributes=statistics."

        self.adc_list = self.agent.adclist(
            self.dhcp_adc_name, ADCList.Type.IPV4)
        # ADC entry to count number of DHCP requests
        dhcp_requests = ADCEntry(ADCEntry.Type.MATCH)
        dhcp_requests.dst_l4_port(67)
        dhcp_requests.src_l4_port(68)
        dhcp_requests.protocol(ADCEntry.Protocol.UDP)
        self.adc_list.add_entry(50, dhcp_requests)
        dhcp_req_traffic = Rate(uri + "50", "60s")
        self.monitors['dhcp_req_monitor'] = Monitor(
            dhcp_req_traffic, "DHCP requests (packets per second)")

        # ADC entry to count number of DHCP responses
        # coming from the application server
        dhcp_responses = ADCEntry(ADCEntry.Type.MATCH)
        dhcp_responses.dst_l4_port(68)
        dhcp_responses.src_l4_port(67)
        dhcp_responses.protocol(ADCEntry.Protocol.UDP)
        self.adc_list.add_entry(60, dhcp_responses)
        dhcp_res_traffic = Rate(uri + "60", "60s")
        self.monitors['dhcp_resp_monitor'] = Monitor(
            dhcp_res_traffic, "DHCP responses (packets per second)")

        return list(self.monitors.values())

    def create_watches(self):
        return []

    def create_rules(self):
        '''
        This function sets the conditions and actions for subagents rules. This
        also sets the clear conditions and actions.
        '''
        # Detect DHCP issues by watching the DHCP requests and
        # responses using UDP
        r1 = Rule("DHCP Response to Request Anomaly Change")

        r1.condition("ratio of {} and {} < {} for 30 seconds", [
            self.monitors['dhcp_resp_monitor'], self.monitors['dhcp_req_monitor'], self.ratio])
        r1.action(self.set_dhcp_ratio_alert)
        r1.clear_condition("ratio of {} and {} >= {} for 1 minute", [
            self.monitors['dhcp_resp_monitor'], self.monitors['dhcp_req_monitor'], self.ratio])
        r1.clear_action(self.remove_dhcp_ratio_alert)

        self.rules['dhcp_status'] = r1

        return list(self.rules.values())

    def create_graphs(self):
        '''
        This function will check for monitors created by the subagent and
        created the necessary graphs associated with those monitors.
        '''
        if bool(self.monitors):
            self.graphs['dhcp_status'] = \
                Graph([self.monitors['dhcp_req_monitor'], self.monitors['dhcp_resp_monitor']],
                      title=Title("DHCP UDP resp to req ratio status"),
                      dashboard_display=False)
            return list(self.graphs.values())
        else:
            return []

    def set_dhcp_ratio_alert(self, event):
        '''
        This is the callback function when the dhcp response ratio hits the
        threshold. This sets the alert level to critical and logs the event.
        '''
        # Alert level is set to critical when the DHCP UDP ratio hits its threshold
        self.alm.update_alert(
            "DHCP", "dhcp_response_ratio", AlertLevel.CRITICAL)
        self.agent.set_alert_description_for_key(
            DHCP_KEY, "Anomaly detected in DHCP UDP traffic")
        self.agent.logger.debug("Detected DHCP UDP response to request ratio hit "
                                "threshold")

    def remove_dhcp_ratio_alert(self, event):
        '''
        This is the callback function to clear the alert when the dhcp response
        ratio returns to an acceptable value and log the event.
        '''
        # Alert level is cleared when the DCHP UDP ratio returns to above the threshold
        self.alm.update_alert("DHCP", "dhcp_response_ratio", AlertLevel.NONE)
        self.agent.clear_alert_description_for_key(DHCP_KEY)
        self.agent.logger.debug("Detected DHCP UDP response to request ratio "
                                "returned to above the threshold")

# Alert Manager


class AlertManager:
    def __init__(self, agent):
        self.agent = agent

    def update_alert(self, subagent_name, key, alert_level):
        '''
        Updates given alert and sets the agent status to the highest alert
        available
        '''
        # Get the current alert level for the whole agent, if it hasn't been set it is None
        current_level = self.agent.variables.get(
            "current_alert_level", AlertLevel.NONE)

        # Set the new alert level for subagent
        alert_key = 'alert_{}_{}'.format(subagent_name, key)
        self.agent.variables[alert_key] = alert_level

        # Get the most severe alert in the new state
        most_severe = AlertLevel.NONE
        for key_type, level in self.agent.variables.items():
            if key_type.startswith('alert_'):
                if self.severity(level) > self.severity(most_severe):
                    most_severe = level

        # If the current alert doesn't match the new most severe alert, change alert level
        if most_severe != current_level:
            self.agent.set_alert_level(most_severe)
            self.agent.variables["current_alert_level"] = most_severe

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


# Client Services Agent

class Agent(NAE):
    def __init__(self):
        # Initialize local vaiable for radius servers here so rules can
        # trigger immediately
        self.variables['unreachable_radius_servers'] = json.dumps([])

        alm = AlertManager(self)

        # Classes
        self.radius = RADIUS(self, alm)
        self.dns = DNS(self, alm)
        self.dhcp = DHCP(self, alm)

        # Initialize alert levels on agent init to publish the starting status
        # to the NAE variables
        alm.update_alert("DNS", "tcp_response_ratio", AlertLevel.NONE)
        alm.update_alert("DNS", "udp_response_ratio", AlertLevel.NONE)
        alm.update_alert("DHCP", "dhcp_response_ratio", AlertLevel.NONE)

        # Merge class objects
        self.__merge(self.radius)
        self.__merge(self.dns)
        self.__merge(self.dhcp)

        self.init_alert_description(
            {RADIUS_KEY: NORMAL, DNS_KEY: NORMAL, DHCP_KEY: NORMAL})

    def adclist(self, name, adc_type):
        adc = ADCList(name, adc_type)
        adc_id = uuid.uuid4().hex
        setattr(self, adc_id, adc)
        return adc

    def __merge(self, script):
        self.__merge_monitors(script.create_monitors())
        self.__merge_watches(script.create_watches())
        self.__merge_rules(script.create_rules())
        self.__merge_graphs(script.create_graphs())

    def __merge_monitors(self, monitors):
        for i, _ in enumerate(monitors):
            mon_id = uuid.uuid4().hex
            mon = 'monitor_{}'.format(mon_id)
            setattr(self, mon, monitors[i])
        return monitors

    def __merge_watches(self, watches):
        for i, _ in enumerate(watches):
            watch_id = uuid.uuid4().hex
            watch = 'watch_{}'.format(watch_id)
            setattr(self, watch, watches[i])
        return watches

    def __merge_rules(self, rules):
        for i, _ in enumerate(rules):
            rule_id = uuid.uuid4().hex
            rule = 'rule_{}'.format(rule_id)
            setattr(self, rule, rules[i])
        return rules

    def __merge_graphs(self, graphs):
        for i, _ in enumerate(graphs):
            graph_id = uuid.uuid4().hex
            graph = 'graph_{}'.format(graph_id)
            setattr(self, graph, graphs[i])
        return graphs

    def on_agent_start(self, event):
        self.init_alert_description(
            {RADIUS_KEY: NORMAL, DNS_KEY: NORMAL, DHCP_KEY: NORMAL})
        self.get_existing_radius_history()

    def on_agent_restart(self, event):
        self.init_alert_description(
            {RADIUS_KEY: NORMAL, DNS_KEY: NORMAL, DHCP_KEY: NORMAL})
        self.get_existing_radius_history()

    def on_agent_re_enable(self, event):
        self.get_existing_radius_history()

    def on_parameter_change(self, params):
        self.radius.on_parameter_change(params)
        self.get_existing_radius_history()

    def get_existing_radius_history(self):
        radius_servers_url = "{}/rest/v10.10/system/vrfs/{}/radius_servers?attributes=reachability_status,address&depth=2".format(
            HTTP_ADDRESS, self.params['VRF_name'])
        radius_servers_data_json = self.get_rest_request_json(
            radius_servers_url, retry=3, wait_between_retries=3)
        self.logger.info("radius_servers_data_json from agent creating starting baseline: {}".format(
            str(radius_servers_data_json)))

        unreachable_servers = []
        reachability_unhealthy_servers = []
        for vrf_name in radius_servers_data_json:
            for server_data in radius_servers_data_json[vrf_name]:
                if "reachability_status" in radius_servers_data_json[vrf_name][server_data] and "address" in radius_servers_data_json[vrf_name][server_data]:
                    reachability_status = radius_servers_data_json[
                        vrf_name][server_data]["reachability_status"]
                    address = radius_servers_data_json[vrf_name][server_data]["address"]
                    if 'unreachable' in reachability_status.lower():
                        unreachable_servers.append(address + "_" + vrf_name)
                    if 'reachability_unhealthy' in reachability_status.lower():
                        reachability_unhealthy_servers.append(
                            address + "_" + vrf_name)

        self.logger.debug("from agent creating starting baseline, unreachable servers are: {} and reachability_unhealthy_servers are {}".format(
            str(unreachable_servers), str(reachability_unhealthy_servers)))

        for server_info in unreachable_servers + reachability_unhealthy_servers:
            self.radius.status_transition_action_unreachable(server_info)
            if server_info in unreachable_servers:
                self.radius_syslog(server_info.split(
                    "_")[0], server_info.split("_")[1], "unreachable")
            else:
                self.radius_syslog(server_info.split("_")[0], server_info.split("_")[
                                   1], "reachability_unhealthy")

        if not unreachable_servers and not reachability_unhealthy_servers:
            self.clear_alert_description_for_key(RADIUS_KEY)
            self.radius.alm.update_alert("RADIUS", "server_reachability",
                                         AlertLevel.NONE)

    def radius_status_transition_action(self, event):
        self.logger.debug(
            "radius_status_transition_action recieved event: " + str(event))

        eventlog_message = event['value']
        try:
            ip, vrf, server_info = self.radius.parse_radius_eventlog(
                eventlog_message)
        except:
            self.logger.error("Unable to parse RADIUS server/vrf info from event: " + str(event) +
                              "\nWith error traceback: " + traceback.format_exc())
            return

        if not self.radius.is_valid_vrf(vrf):
            self.logger.debug(
                "Skipping RADIUS agent alerts/actions for IP: {}, VRF_name: {}".format(ip, vrf))
            return

        status = None
        if 'unreachable' in eventlog_message.lower():
            self.radius.status_transition_action_unreachable(server_info)
            status = 'unreachable'
        elif 'reachability_unhealthy' in eventlog_message.lower():
            self.radius.status_transition_action_unreachable(server_info)
            status = 'reachability_unhealthy'
        else:
            self.radius.status_transition_action_reachable(server_info)
            status = 'reachable'

        self.radius_syslog(ip, vrf, status)

    def radius_syslog(self, ip, vrf, status):
        ActionSyslog(
            "RADIUS server {} vrf {} status is {}".format(ip, vrf, status))

    def set_dns_tcp_ratio_alert(self, event):
        ActionSyslog("An anomoly in DNS TCP connection has been detected. The "
                     "ratio of SYN/ACK to SYN packets between the clients communicating "
                     "through this switch and the DNS application have fallen below "
                     "the level {} specified by the DNS_resp_to_req_ratio parameter value."
                     .format(self.params['DNS_resp_to_req_ratio']))
        self.dns.set_dns_tcp_ratio_alert(event)

    def remove_dns_tcp_ratio_alert(self, event):
        ActionSyslog("The DNS TCP connection ratio has returned to "
                     "above the specified threshold value.")
        self.dns.remove_dns_tcp_ratio_alert(event)

    def set_dns_udp_ratio_alert(self, event):
        ActionSyslog("An anomoly in DNS UDP traffic has been detected. The "
                     "ratio of responses to request packets between the clients "
                     "communicating through this switch and the DNS application have "
                     "fallen below the level {} specified by the DNS_resp_to_req_ratio "
                     "parameter value.".format(self.params['DNS_resp_to_req_ratio']))
        self.dns.set_dns_udp_ratio_alert(event)

    def remove_dns_udp_ratio_alert(self, event):
        ActionSyslog("The DNS UDP traffic ratio has returned to "
                     "above the specified threshold value.")
        self.dns.remove_dns_udp_ratio_alert(event)

    def set_dhcp_ratio_alert(self, event):
        ActionSyslog("An anomoly in DHCP UDP traffic has been detected. The "
                     "ratio of responses to request packets between the clients "
                     "communicating through this switch and the DHCP application have "
                     "fallen below the level {} specified by the DHCP_resp_to_req_ratio "
                     "parameter value.".format(self.params['DHCP_resp_to_req_ratio']))
        self.dhcp.set_dhcp_ratio_alert(event)

    def remove_dhcp_ratio_alert(self, event):
        ActionSyslog("The DHCP UDP traffic ratio has returned to "
                     "above the specified threshold value.")
        self.dhcp.remove_dhcp_ratio_alert(event)
