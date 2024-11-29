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

#               --  EVPN VxLAN Health functionality  --
# The overall, terse goal of this script is to monitor evpn and vxlan health,
# decide if things have gone bad, and if so, generate some helpful cli/shell
# output from the appropiate moment of the event.

# Agents derived from this script will monitor three areas:

# 1. EVPN
#   - monitor EVPN Instances
#   - alert if
#     - EVPN instance state changed from operational to non-operational
#     - EVPN instance stuck in non-operational state for 5 cycles
#     - EVPN instance is deleted
#     - Peer VTEP deletion for a EVPN instance
#     - No. of VTEP Peers, Local MACs, Remote MACs, Remote Routes learnt on a
#       EVPN instance decreases greater than 20% between 2 cycles
#   - publish output from:
#     - show evpn evi summary - lists EVPN instances and state (up/down)
#     - show evpn evi <evpn_instance> detail - detail info about single EVPN
#       instance. state, peer-vtep, rd/rt, statistics
#     - show evpn mac-ip evi <evpn_instance> - lists remote MACs / Routes
#       learnt by evpn instance
#     - show interface vxlan 1 brief - to know if interface vxlan 1 is down
#     - show interface vxlan 1 - information about interface vxlan 1 state and
#       list of VTEPs
#     - show interface vxlan vteps <tunnel_endpoint_ip> - to check state of
#       particular tunnel endpoint
#     - show interface vxlan vteps - to check which tunnels are remaining when
#       more than 20% tunnels are deleted. Lists tunnels, VNI and tunnel state
#     - show bgp l2vpn evpn summary - list bgp l2vpn neighbors and their state
#     - show ip route <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check
#       if route is present for tunnel_endpoint_ip
#     - ping <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check ping
#       connectivity to tunnel endpoint
#     - traceroute <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check
#       connectivity to nexthop and tunnel endpoint
#     - show mac-address-table | inc evpn | count - to check count of remote
#       MACs learnt
#     - show mac-address-table | inc dynamic | count - to check count of local
#       MACs learnt
#     - syslogs to indicate the evi deletion, peer vtep deletion, evi state
#       change, operational failure reason, percentage decrease of the
#       MAC/Peer VTEP counts
#   - clear alert if
#     - All EVPN Instances in JSON response are in operational state
#   - filters
#     - based on EVPN instance, tunnel endpoint destination IP,
#       VRF of tunnel endpoint
#   - alerts
#       -MAJOR
#           - EVPN instance stuck in non-operational state for 5 cycles
#       -MINOR
#           - EVPN instance is deleted
#           - EVPN instance state changed from operational to non-operational
#           - Peer VTEP is deleted for a EVPN instance
#           - No. of Vtep Peers, Local MACs, Remote MACs, Remote Routes learnt
#             on a EVPN instance decreases greater than 20% between 2 cycles

# 2. Tunnel Endpoint
#   - monitor Tunnel Endpoint
#   - alert if
#     - Tunnel Endpoint state changed from operational to non-operational
#     - Tunnel Endpoint stuck in non-operational state for 5 cycles
#   - publish output from:
#     - show interface vxlan vteps <tunnel_endpoint_ip> <tunnel_endpoint_vrf> -
#       to check state of particular tunnel endpoint
#     - show bgp l2vpn evpn summary - list bgp l2vpn neighbors and their state
#     - show ip route <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check
#       if route is present for tunnel_endpoint_ip
#     - ping <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check ping
#       connectivity to tunnel endpoint
#     - traceroute <tunnel_endpoint_ip> vrf <tunnel_endpoint_vrf> - to check
#       connectivity to nexthop and tunnel endpoint
#   - clear alert if
#     - All tunnels in JSON response are in operational state
#   - filters
#     - based on tunnel endpoint destination IP and VRF of tunnel endpoint
#   - alerts
#       -MAJOR
#           - Tunnel Endpoint state changed from operational to non-operational
#       -MINOR
#           - Tunnel Endpoint stuck in non-operational state for 5 cycles

# 3. VNI health
#    - monitor virtual network id health
#    - alert if
#      - VNI state/forwarding state stuck in non-operational state
#      - VNI state/forwarding state going down from stable operational
#        state
#      - VNI config state stuck in invalid
#    - publish output from:
#       - show interface vxlan vni <VNI_ID>
#       - show running-config interface vxlan 1
#    - clear alert if moving back to operational from non-operational state
#   - filters
#     - based on VNI_ID
#   - alerts
#       - Major
#           - VNI state/forwarding state going down from stable operational
#             state
#           - VNI config state stuck in invalid
#       - Minor
#          - VNI state/forwarding state stuck in non-operational state

# Note:
# - The Maximum of alert conditions processed in one poll cycle is a
#   configurable parameter. With a minimum of 1, maximum of 6 and
#   default of 3 alerts in one poll cycle.
#
# - If the system goes down to bad state and comes back to good state within
#   the polling interval, the event will be missed and alert will not happen

import json
from time import (sleep, clock_gettime, CLOCK_PROCESS_CPUTIME_ID)

Manifest = {
    'Name': 'evpn_vxlan_health',
    'Description': 'Agent for monitoring EVPN and VxLAN health',
    'Version': '3.0',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.13.1000',
    'AOSCXPlatformList': ['6200', '6300', '64xx', '8325', '8360', '8400', '10000', '8100']
}

ParameterDefinitions = {
    'poll_interval': {
        'Name': 'Polling Interval',
        'Description': 'How often to poll for evpn vxlan health metrics.'
                       ' Measured in seconds. Default is 60. Recommended'
                       ' minimum value is 30 seconds',
        'Type': 'Integer',
        'Default': 60
    },
    'monitor_evpn': {
        'Name': 'Monitor EVPN',
        'Description': 'Default is ''false''. By default both static and evpn'
                       ' tunnel endpoints and VNIs are monitored. EVPN'
                       ' Instance is not monitored by default. When set'
                       ' to ''true'', EVPN Instance is monitored in addition'
                       ' to tunnel endpoints and VNIs',
        'Type': 'String',
        'Default': 'false'
    },
    'vni_id': {
        'Name': 'VNI or EVPN Instance',
        'Description': 'Network ID (VNI in VXLAN case) that should be used to'
                       'reach this endpoint. This corresponds to EVPN'
                       ' Instances as well. List of VNIs can be given'
                       ' seperated by comma. By default all'
                       ' VNIs are monitored.'
                       'Example: 20,10000,20000',
        'Type': 'String',
        'Default': "*"
    },
    'vrf': {
        'Name': 'VRF',
        'Description': 'VRF used for resolving the tunnel endpoint'
                       'destination IP address.',
        'Type': 'String',
        'Default': "*"
    },
    'Tunnel_endpoint': {
        'Name': 'Tunnel Endpoint',
        'Description': 'List of IPv4 and/or IPv6 destination tunnel IPs in the'
                       'address format. By default all destinations are '
                       'monitored. Example: 192.168.1.1, 3.3.3.3, 1::1, 1::2',
        'Type': 'String',
        'Default': "*"
    },
    'origin': {
        'Name': 'origin',
        'Description': 'Identifies the mechanism that is responsible for the'
                       'creation of the endpoint:'
                       'static: user configuration'
                       'evpn:   dynamically learnt via EVPN'
                       'hsc:    dynamically learnt from a remote controller'
                       '(e.g.NSX)',
        'Type': 'String',
        'Default': "*"
    },
    'percent_mac_route_lost': {
        'Name': '% of Remote MAC / Routes lost',
        'Description': 'Alerts if percentage of Remote MAC / Routes lost is '
                       'greater than specified threshold. Default is 20',
        'Type': 'Integer',
        'Default': 20
    },
    'percent_local_mac_lost': {
        'Name': '% of Local MAC lost',
        'Description': 'Alerts if percentage of Local MAC lost is '
                       'greater than specified threshold. Default is 20',
        'Type': 'Integer',
        'Default': 20
    },
    'percent_peer_vtep_lost': {
        'Name': '% of Peer VTEP lost',
        'Description': 'Alerts if percentage of Peer VTEPs lost is '
                       'greater than specified threshold. Default is 20',
        'Type': 'Integer',
        'Default': 20
    },
    'alert_limit': {
        'Name': 'Alert Limit',
        'Description': 'Maximum of alert conditions processed in one poll cycle.'
                       'Minimum is 1, Maximum is 6 and Default is 3',
        'Type': 'Integer',
        'Default': 3
    }
}

EVI_FAILURE_REASON = {
    # 'Operational failure reason of the EVPN instance:',
    'entity-not-up': 'EVPN entity is not up.',
    'admin-config': 'Admin status is disabled.',
    'resource-failure': 'Insufficient resources.',
    'no-if-info': 'Incomplete interface information.',
    'evi-not-up': 'EVPN instance is not up.',
    'bd-not-up': 'EVPN bridge domain is not up.',
    'no-route-distinguisher': 'No route distinguisher configured.',
    'route-dist-conflict': 'This EVPN instance\'s RD is the same as'
                           'another active instance\'s RD.',
    'no-esi': 'No Ethernet Segment Identifier is available.',
    'bad-vni': 'Invalid VNI.',
    'vni-conflict': 'There is another bridge domain with the'
                    'same VNI.',
    'vlan-sub-if-evi-conflict': 'Multiple VLAN sub-interfaces have been'
                                'configured for the same EVI on the same'
                                'Ethernet Segment.',
    'no-bgp-id': 'BGP router identifier is not yet available'
                 'to EVPN.',
    'rt-type-conflict': 'Configured route target and the auto-derived'
                        'route target have the same route target value'
                        'but different route target types.',
    'no-rt': 'No configured route targets.',
    'ip-vrf-not-up': 'IP VRF instance is not up.',
    'no-system-mac': 'System MAC address is not known.',
    'rt-conflict': 'There is an another active route target'
                   'configured with the same route target value'
}


DPRINT = False
EVPN = "EVPN"
TUNNEL = "Tunnel"
VNI = "VNI"
NORMAL = "Normal"


def dprint(*args):
    '''this function is used for printing debug logs'''
    if DPRINT:
        print(args)


class Agent(NAE):
    '''

    Note: several useful variables are defined in NAE which we will reference
    here:

    HTTP_AADDRESS => "http://127.0.0.1:8080"
    AlertLevel.NONE/MINOR/MAJOR/CRITICAL => None, Minor, Major, Critical
    SYSLOG_WARNING => 4 ## rfc-5424 defined number for syslog Warning level
    ActionSyslog()
    ActionCli()
    '''

    def __init__(self):

        # dprint("WIP------- Agent:__init__")
        self.evpn_agent = EVPNAgent(self)
        self.vxlan_tunnel_monitor = VxlanTunnelMonitorAgent(self)
        self.vni_health_monitor = VNIHealthMonitorAgent(self)
        self.alert_levels_generated_within_poll_per_subagent = {
            'evpn': set({AlertLevel.NONE}),
            'tunnel': set({AlertLevel.NONE}),
            'vni': set({AlertLevel.NONE})
        }

        rule = Rule("EVPN VXLAN Health Rule")
        rule.condition("every {} seconds", [self.params['poll_interval']])
        rule.action(self.evpn_vxlan_health_poller)
        self.rule = rule
        self.actioncli = {
            'conn': set(),
            'evpn': set(),
            'vni': set(),
            'tunnel': set(),
            'config': set(),
            'other': set()
        }
        alert_limit = int(self.params['alert_limit'].value)
        if alert_limit >= 1 and alert_limit <= 6:
            self.global_alert_limit = alert_limit
        else:
            # raise error
            raise ValueError('Alert limit should be in the range of 1 to 6')

        poll_interval = int(self.params['poll_interval'].value)
        if poll_interval < 30:
            raise ValueError('Please update the value of poll interval to 30 '
                             'seconds or greater')

        self.syslogs_per_poll = 0
        self.addnl_log_cli_excd = False
        self.addnl_log_syslog_excd = False

        # Persistant variables across every run of this script
        # are stored in self.variables. They must be of type
        # string.
        # List of NAE Variables:
        # - current_alert: current alert level of the main NAE Agent
        # - evpn_alert: current alert level of EVPN sub-agent (EVPNAgent)
        # - tunnel_alert: current alert level of Tunnel Endpoint sub-agent
        #   (VxlanTunnelMonitorAgent)
        # - vni_alert: current alert level of VNI sub-agent
        #   (VNIHealthMonitorAgent)
        # - evpn_instance_list: Python Dictionary containing the data
        #   monitored for EVPN Instance
        #   example:
        #   {
        #       "20": {
        #           "evi": 20,
        #           "export_route_targets": [
        #               "1:268435476"
        #           ],
        #           "import_route_targets": [
        #               "1:268435476"
        #           ],
        #           "operational_failure_reason": "None",
        #           "operational_status": "up",
        #           "rd": "1.1.1.1:20",
        #           "remote_mac_count_per_vtep_peer": {
        #               "3.3.3.3": 2
        #           },
        #           "statistics": {
        #               "local_mac_count": 48,
        #               "peer_vtep_count": 1,
        #               "remote_mac_count": 2
        #           },
        #           "down_time": 0
        #       }
        #   }
        # - tunnel_instance_list: Python Dictionary containing the data
        #   monitored for Tunnel Endpoint
        #   example:
        #   {
        #       "default,evpn,2.2.2.2": {
        #           "state": "operational",
        #           "down_time": 0
        #       }
        #   }
        # - vni_instance_list: Python Dictionary containing the data
        #   monitored for Virtual Network ID
        #   example:
        #   {
        #       "20": {
        #           "id": 20,
        #           "routing": "False",
        #           "state": "configuration_error",
        #           "vlan": "20",
        #           "vrf": "None",
        #           "down_time": 0
        #       }
        #   }
        # - evpn_alert_on_last_cycle: set to "True" if EVPN alert was
        #   generated in previous poll cycle. Else set to "False"
        # - tunnel_alert_on_last_cycle: set to "True" if Tunnel Endpoint alert
        #   was generated in previous poll cycle. Else set to "False"
        # - vni_alert_on_last_cycle: set to "True" if VNI alert was generated
        #   in previous poll cycle. Else set to "False"
        # agent self.variables persist after init and are not re-initialized
        self.variables['current_alert'] = json.dumps(AlertLevel.NONE)
        self.variables['evpn_alert'] = json.dumps(AlertLevel.NONE)
        self.variables['tunnel_alert'] = json.dumps(AlertLevel.NONE)
        self.variables['vni_alert'] = json.dumps(AlertLevel.NONE)
        self.variables['evpn_instance_list'] = json.dumps({})
        self.variables['tunnel_instance_list'] = json.dumps({})
        self.variables['vni_instance_list'] = json.dumps({})
        self.variables['evpn_alert_on_last_cycle'] = "False"
        self.variables['tunnel_alert_on_last_cycle'] = "False"
        self.variables['vni_alert_on_last_cycle'] = "False"
        self.init_alert_description(
            {EVPN: NORMAL, TUNNEL: NORMAL, VNI: NORMAL})

    def evpn_vxlan_health_poller(self, event):
        '''this function is called every poll cycle to collect EVPN data'''
        time0 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        self.vni_health_monitor.vni_handler()
        time1 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        if self.params['monitor_evpn'].value == 'true':
            self.evpn_agent.evpn_handler()
        time2 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        self.vxlan_tunnel_monitor.tunnel_handler()
        time3 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        self.evpn_vxlan_health_set_alert()
        time4 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        self.execute_action_cli()
        if self.addnl_log_cli_excd or self.addnl_log_syslog_excd:
            ActionSyslog('All the Alerts were not processed due to the Alert '
                         'Limit', severity=SYSLOG_WARNING)
        time5 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        dprint("Time Report, VNI : {} seconds".format(time1-time0))
        dprint("Time Report, EVPN : {} seconds".format(time2-time1))
        dprint("Time Report, TUNNEL : {} seconds".format(time3-time2))
        dprint("Time Report, ALERT : {} seconds".format(time4-time3))
        dprint("Time Report, ACTIONCLI : {} seconds".format(time5-time4))
        dprint("Time Report, Total: {} seconds".format(time5-time0))

    def evpn_vxlan_max_alert(self, levels):
        '''this function returns max alert level among the passed list/ set
         of alerts'''
        decided_level = AlertLevel.NONE  # default level
        # decide max alert level
        for severity in levels:
            if severity == AlertLevel.CRITICAL:
                return AlertLevel.CRITICAL
            elif severity == AlertLevel.MAJOR:
                decided_level = AlertLevel.MAJOR
            elif severity == AlertLevel.MINOR:
                if decided_level != AlertLevel.MAJOR:
                    decided_level = AlertLevel.MINOR
        return decided_level

    def evpn_vxlan_health_set_alert(self):
        """
        This function will set this agents AlertLevel to the highest level
        among the choices. Also store each sub-agent alert level in local
        storage
        Invoked once per poll cycle
        """
        dprint("WIP --- evpn_vxlan_health_set_alert")
        dprint("alerts_subagent= {0}".format(
            self.alert_levels_generated_within_poll_per_subagent))
        # update local storage with new alerts
        evpn_max = self.evpn_vxlan_max_alert(
            self.alert_levels_generated_within_poll_per_subagent['evpn'])
        tunnel_max = self.evpn_vxlan_max_alert(
            self.alert_levels_generated_within_poll_per_subagent['tunnel'])
        vni_max = self.evpn_vxlan_max_alert(
            self.alert_levels_generated_within_poll_per_subagent['vni'])
        self.variables['evpn_alert'] = json.dumps(evpn_max)
        self.variables['tunnel_alert'] = json.dumps(tunnel_max)
        self.variables['vni_alert'] = json.dumps(vni_max)

        # current max
        dprint("self.variables['evpn_alert']= {}".format(
            self.variables['evpn_alert']))
        dprint("self.variables['tunnel_alert']= {}".format(
            self.variables['tunnel_alert']))
        dprint("self.variables['vni_alert']= {}".format(
            self.variables['vni_alert']))
        current = json.loads(self.variables['current_alert'])
        dprint("self.variables['current_alert']= {}".format(
            self.variables['current_alert']))
        # using a list to show individual levels that are possibly repeated
        alert_levels_generated_within_poll = list()
        alert_levels_generated_within_poll.append(
            json.loads(self.variables['evpn_alert']))
        alert_levels_generated_within_poll.append(
            json.loads(self.variables['tunnel_alert']))
        alert_levels_generated_within_poll.append(
            json.loads(self.variables['vni_alert']))
        dprint("alert_levels_generated_within_poll= {}".format(
            alert_levels_generated_within_poll))
        # desired max
        desired_max = \
            self.evpn_vxlan_max_alert(alert_levels_generated_within_poll)
        dprint("WIP --- alerts {}: max {}: current {}\
            ".format(alert_levels_generated_within_poll, desired_max,
                     current))

        if desired_max == AlertLevel.NONE:
            self.init_alert_description(
                {EVPN: NORMAL, TUNNEL: NORMAL, VNI: NORMAL})
        else:
            if evpn_max == AlertLevel.NONE:
                self.clear_alert_description_for_key(EVPN)
            if tunnel_max == AlertLevel.NONE:
                self.clear_alert_description_for_key(TUNNEL)
            if vni_max == AlertLevel.NONE:
                self.clear_alert_description_for_key(VNI)

        # raise/lower level to current max
        if desired_max != current:
            dprint("WIP --- raise to {}".format(desired_max))
            self.set_alert_level(desired_max)
            self.variables['current_alert'] = json.dumps(desired_max)
            if desired_max == AlertLevel.NONE:
                self.init_alert_description(
                    {EVPN: NORMAL, TUNNEL: NORMAL, VNI: NORMAL})

    def action_syslog(self, level, metric_args):
        '''this function is used for displaying syslog in alert window'''
        if level == Log.DEBUG:
            severity = SYSLOG_DEBUG
        elif level == Log.INFO:
            severity = SYSLOG_INFO
        elif level == Log.WARNING:
            severity = SYSLOG_WARNING
        elif level == Log.ERR:
            severity = SYSLOG_ERR
        elif level == Log.CRIT:
            severity = SYSLOG_CRIT
        else:
            # wrong level
            return
        if self.syslogs_per_poll < self.global_alert_limit:
            ActionSyslog(metric_args, severity=severity)
            self.syslogs_per_poll += 1
        if self.syslogs_per_poll == self.global_alert_limit:
            self.addnl_log_syslog_excd = True

    def execute_action_cli(self):
        '''this function is used to execute action CLI'''
        dprint("enter action cli")
        for actions in self.actioncli.values():
            if actions != set():
                if len(actions) > self.global_alert_limit:
                    self.addnl_log_cli_excd = True
                cmds = sorted(actions)
                cmds = cmds[:self.global_alert_limit]
                dprint("cmds= {0}".format(cmds))
                if cmds != []:
                    cmds_string = "\n\n".join(cmds)
                    ActionCLI(cmds_string)

    def action_shell(self, script):
        '''this function is used to execute SHELL commands'''
        ActionShell(script)

    def fetch_url(self, url):
        '''this function is used to fetch data for given REST url. Retries GET
           request if OVSDB hasn't been populated'''
        for count in range(8):
            response = None
            try:
                response = self.get_rest_request_json(url, retry=1)
            except NAEException as e:
                # valid to get not found response. say if tunnel is deleted
                if 'status code' in str(e):
                    break
                elif count < 7:
                    sleep(15)
                else:
                    self.logger.error("system error while collecting stat"
                                      "error: {0}| url: {1}"
                                      .format(e, url))
            except:
                self.logger.error("system error {} While collecting stat"
                                  .format(url))
        return response


class EVPNAgent(Agent):
    '''This class polls EVPN_Instance table using REST query
     and Analyzes the data'''

    def __init__(self, agent):
        self.agent = agent
        self.evpn_alert_on_this_cycle = False
        self.action_conn = set()
        self.action_evpn = set()
        self.action_vni = set()
        self.action_tunnel = set()
        self.action_config = set()
        self.action_other = set()
        self.evpn_url_list = self.get_url_list(
            self.agent.params['vni_id'].value)

    def get_url_list(self, evpn_instances):
        '''Takes evpn instances as input and generate
         list of corresponding REST URI'''
        evpn_url_list = []

        for instance in evpn_instances.split(","):
            evpn_url = HTTP_ADDRESS + \
                '/rest/v10.10/system/evpn_instances/' + instance
            evpn_url_list.append(evpn_url)
            dprint("evpn_url_list: {0}".format(evpn_url_list))

        return evpn_url_list

    def evpn_handler(self):
        '''Wrapper for collect_evpn_data. Invoked from main agent'''
        dprint("WIP------- evpn_handler")
        self.collect_evpn_data()

    # Funtion to collect EVPN Data
    def collect_evpn_data(self):
        '''Fetch EVI from REST query and Analyze'''
        evpn_url_list = self.evpn_url_list
        evpn_response_list = []

        for url in evpn_url_list:
            dprint(url)

        for url in evpn_url_list:
            response = self.agent.fetch_url(url)
            if response is None:
                continue
            else:
                evpn_response_list.append(response)

        dprint('EVPN Response list length:', len(evpn_response_list))
        dprint('EVPN response_list = {0}'.format(evpn_response_list))

        self.analyze_evpn_data(evpn_response_list)

        # bring the alert back to normal
        if self.evpn_alert_on_this_cycle is True:
            dprint("evpn_alert_on_this_cycle is True")
            self.agent.variables['evpn_alert_on_last_cycle'] = "True"
        else:
            dprint("self.evpn_alert_on_this_cycle is False")
            if self.agent.variables['evpn_alert_on_last_cycle'] == "True":
                dprint("evpn_alert_on_last_cycle is True")
                self.agent.variables['evpn_alert_on_last_cycle'] = "False"
                self.evpn_set_alert_level(AlertLevel.NONE)

        return None

    def analyze_evpn_data(self, evpn_res_list):
        '''this function stores the required EVPN Data from JSON response in
         local storage and Analyzes the changes by comparing with previous
         response'''

        evpn_res_list = [] if evpn_res_list is None else evpn_res_list
        evi_dict_new = {}

        dprint("self.agent.params['evpn_instance'].value={0}".format(
            self.agent.params['vni_id'].value))
        if evpn_res_list != []:
            if self.agent.params['vni_id'].value == "*":
                evi_dict_new = evpn_res_list[0]
            else:
                for res in evpn_res_list:
                    evi_dict_new[str(res['evi'])] = res

        evpn_dict_old = json.loads(
            self.agent.variables["evpn_instance_list"])
        vni_dict_new = json.loads(
            self.agent.variables["vni_instance_list"])
        tunnel_dict_old = json.loads(
            self.agent.variables["tunnel_instance_list"])
        # initialize down_time
        if evpn_dict_old == {}:
            for instance in evi_dict_new.values():
                dprint("instance: {0}".format(instance))
                dprint("instance.keys(): {0}".format(instance.keys()))
                if "down_time" not in instance.keys():
                    evi_dict_new[str(instance["evi"])]["down_time"] = 0
        else:
            for instance in evi_dict_new.values():
                dprint("instance: {0}".format(instance))
                dprint("instance.keys(): {0}".format(instance.keys()))
                evi = str(instance['evi'])
                if evi in evpn_dict_old.keys():
                    evi_dict_new[evi]["down_time"] = \
                        evpn_dict_old[evi]["down_time"]
                else:
                    evi_dict_new[evi]["down_time"] = 0

        # Structure of evi_dict_new
        # {
        #     "20": {
        #         "ethernet_tag": None,
        #         "evi": 20,
        #         "export_route_targets": [
        #             "1:268435476"
        #         ],
        #         "import_route_targets": [
        #             "1:268435476"
        #         ],
        #         "operational_failure_reason": "None",
        #         "operational_status": "up",
        #         "rd": "1.1.1.1:20",
        #         "remote_mac_count_per_vtep_peer": {
        #             "3.3.3.3": 2
        #         },
        #         "statistics": {
        #             "local_mac_count": 48,
        #             "peer_vtep_count": 1,
        #             "remote_mac_count": 2
        #         },
        #         "down_time": 0
        #     },
        #     "10000": {
        #         "ethernet_tag": None,
        #         "evi": 10000,
        #         "export_route_targets": [
        #             "1:100"
        #         ],
        #         "import_route_targets": [
        #             "1:100"
        #         ],
        #         "operational_failure_reason": "None",
        #         "operational_status": "up",
        #         "rd": "1:100",
        #         "remote_mac_count_per_vtep_peer": {
        #             "3.3.3.3": 7
        #         },
        #         "statistics": {
        #             "local_mac_count": 2,
        #             "peer_vtep_count": 1,
        #             "remote_mac_count": 7
        #         },
        #         "down_time": 0
        #     }
        # }

        dprint("evpn_instance_list = {0}".format(
            self.agent.variables["evpn_instance_list"]))
        dprint("evi_dict_new = {0}".format(evi_dict_new))
        dprint("vni_instance_list = {0}".format(
            self.agent.variables["vni_instance_list"]))
        dprint("vni_dict_new={0}".format(vni_dict_new))
        dprint("tunnel_instance_list = {0}".format(
            self.agent.variables["tunnel_instance_list"]))

        dprint('Old evpn dict:')
        dprint('******************')
        old_evi_count = 0
        for key in evpn_dict_old:
            dprint(key)
            old_evi_count += 1
        dprint('Old evpn count: {0}', format(old_evi_count))
        dprint("-----------------------------")
        dprint('New evpn dict:')
        dprint('******************')
        new_evi_count = 0
        for key in evi_dict_new:
            dprint(key)
            new_evi_count += 1
        dprint('New evpn count: {0}', format(new_evi_count))
        dprint("-----------------------------")

        dprint('New vni dict:')
        dprint('******************')
        new_vni_count = 0
        for key in vni_dict_new:
            dprint(key)
            new_vni_count += 1
        dprint('New vni count: {0}', format(new_vni_count))
        dprint("-----------------------------")

        dprint('Old tunnel dict:')
        dprint('******************')
        old_tunnel_count = 0
        for key in tunnel_dict_old:
            dprint(key)
            old_tunnel_count += 1
        dprint('Old tunnel count: {0}', format(old_tunnel_count))
        dprint("-----------------------------")

        missing_down_evis = self.get_missing_down_evis(
            evpn_dict_old, evi_dict_new)
        evi_del_alert = self.monitor_evi_deletion(missing_down_evis[0],
                                                  vni_dict_new)
        tunnel_del_alert = self.monitor_tunnel_deletion(
            evpn_dict_old, evi_dict_new, tunnel_dict_old, vni_dict_new)
        if (tunnel_del_alert == AlertLevel.NONE and
                evi_del_alert == AlertLevel.NONE):
            self.monitor_remote_mac_route_per_evi_vtep(evpn_dict_old,
                                                       evi_dict_new,
                                                       vni_dict_new)
            self.monitor_local_mac_change(evpn_dict_old, evi_dict_new)
        self.monitor_peer_vtep_count_change(evpn_dict_old, evi_dict_new)
        self.monitor_evi_down(missing_down_evis[1], evi_dict_new, vni_dict_new)
        self.agent.actioncli['conn'].update(self.action_conn)
        self.agent.actioncli['evpn'].update(self.action_evpn)
        self.agent.actioncli['vni'].update(self.action_vni)
        self.agent.actioncli['tunnel'].update(self.action_tunnel)
        self.agent.actioncli['config'].update(self.action_config)
        self.agent.actioncli['other'].update(self.action_other)

    def get_missing_down_evis(self, evi_dict_old, evi_dict_new):
        '''this function compiles list of evpn instances which have been
         deleted and which are in down state'''

        old_evis = evi_dict_old.keys()
        new_evis = evi_dict_new.keys()
        dprint("old_evis={0}".format(old_evis))
        dprint("new_evis={0}".format(new_evis))
        missing_evis = []
        newly_added_evis = []
        down_evis = []
        for evi in old_evis:
            if evi not in new_evis:
                missing_evis.append(evi)
        for evi in new_evis:
            dprint("evi_dict_new[evi]={0}".format(evi_dict_new[evi]))
            if evi not in old_evis:
                newly_added_evis.append(evi)
            if evi_dict_new[evi]["operational_status"] != "up":
                down_evis.append(evi)
            elif ((evi_dict_new[evi]["operational_status"] == "up") and
                  (evi_dict_new[evi]["down_time"] > 0)):
                dprint("evi_dict_new[evi][down_time]={0}".format(
                    evi_dict_new[evi]["down_time"]))
                # reset down_time if evi is back up
                evi_dict_new[evi]["down_time"] = 0
        dprint("missing_evis={0}".format(missing_evis))
        dprint("newly_added_evis={0}".format(newly_added_evis))
        dprint("down_evis={0}".format(down_evis))
        return [missing_evis, down_evis]

    def monitor_evi_deletion(self, missing_evis, vni_dict_new):
        '''this function generates alert for evpn instance which are deleted'''

        dprint("Enter monitor_evi_deletion")
        alert_level = AlertLevel.NONE
        if missing_evis != []:
            for evi in missing_evis:
                vlan_id = None
                if evi in vni_dict_new:
                    vlan_id = vni_dict_new[evi]['vlan']
                message = 'EVPN Instance {0} has been deleted'.format(evi)
                self.agent.action_syslog(Log.WARNING, message)
                self.agent.set_alert_description_for_key(EVPN, message)
                self.agent.logger.debug(message)
                dprint(message)
                self.action_vni.add("show interface vxlan vni {0}".format(evi))
                if vlan_id is not None:
                    self.action_other.add("show vlan {0}".format(vlan_id))
            self.action_config.add("show interface vxlan 1 brief")
            self.evpn_alert_on_this_cycle = True
            alert_level = AlertLevel.MINOR
            self.evpn_set_alert_level(alert_level)
        return alert_level

    def monitor_evi_down(self, down_evis, evi_dict_new, vni_dict_new):
        '''this function generates alert for EVI state change to down state and
         EVI stuck in down state for 5 poll cycles'''

        dprint("Enter monitor_evi_down")
        stuck_syslog = ""
        state_change_syslog = ""
        alert_level = AlertLevel.NONE
        if down_evis != []:
            for evi in down_evis:
                vlan_id = vni_dict_new[evi]['vlan']
                # stuck in down for 5 cycles
                if evi_dict_new[evi]["down_time"] == 5:
                    evi_dict_new[evi]["down_time"] += 1
                    err_code = evi_dict_new[evi]["operational_failure_reason"]
                    state = evi_dict_new[evi]["operational_status"]
                    stuck_syslog = "EVPN Instance {0} stuck in {1} state " \
                        "due to: {2}" \
                        .format(evi, state,
                                EVI_FAILURE_REASON[err_code])
                    self.agent.action_syslog(Log.WARNING, stuck_syslog)
                    self.agent.set_alert_description_for_key(
                        EVPN, stuck_syslog)
                    self.agent.logger.debug(stuck_syslog)
                    self.action_evpn.add(
                        "show evpn evi {0} detail".format(evi))
                    if vlan_id is not None:
                        self.action_other.add("show vlan {0}".format(vlan_id))
                    if err_code == "bad-vni":
                        self.action_config.add("show interface vxlan 1")
                    elif err_code == "admin-config":
                        self.action_config.add("show running-config evpn")
                    alert_level = AlertLevel.MAJOR
                # state change
                elif evi_dict_new[evi]["down_time"] == 0:
                    evi_dict_new[evi]["down_time"] += 1
                    err_code = evi_dict_new[evi]["operational_failure_reason"]
                    state = evi_dict_new[evi]["operational_status"]
                    state_change_syslog = "EVPN Instance {0} state changed " \
                                          "to: {1} due to: " \
                                          "{2}".format(evi, state,
                                                       EVI_FAILURE_REASON[
                                                           err_code])
                    self.agent.action_syslog(Log.WARNING, state_change_syslog)
                    self.agent.set_alert_description_for_key(
                        EVPN, state_change_syslog)
                    self.agent.logger.debug(state_change_syslog)
                    self.action_evpn.add(
                        "show evpn evi {0} detail".format(evi))
                    if vlan_id is not None:
                        self.action_other.add("show vlan {0}".format(vlan_id))
                    alert_level = AlertLevel.MINOR
                    if err_code == "bad-vni":
                        self.action_config.add("show interface vxlan 1")
                    elif err_code == "admin-config":
                        self.action_config.add("show running-config evpn")
                elif 0 < evi_dict_new[evi]["down_time"] < 5:
                    evi_dict_new[evi]["down_time"] += 1
                    alert_level = AlertLevel.MINOR
                    err_code = evi_dict_new[evi]["operational_failure_reason"]
                    state = evi_dict_new[evi]["operational_status"]
                    description_syslog = "EVPN Instance {0} in {1} state " \
                                         "due to: {2}" \
                                         .format(evi, state,
                                                 EVI_FAILURE_REASON[err_code])
                    self.agent.set_alert_description_for_key(
                        EVPN, description_syslog)
                else:
                    evi_dict_new[evi]["down_time"] += 1
                    alert_level = AlertLevel.MAJOR
                    err_code = evi_dict_new[evi]["operational_failure_reason"]
                    state = evi_dict_new[evi]["operational_status"]
                    description_syslog = "EVPN Instance {0} in {1} state " \
                                         "due to: {2}" \
                                         .format(evi, state,
                                                 EVI_FAILURE_REASON[err_code])
                    self.agent.set_alert_description_for_key(
                        EVPN, description_syslog)
            if alert_level != AlertLevel.NONE:
                self.evpn_alert_on_this_cycle = True
                self.evpn_set_alert_level(alert_level)
        self.agent.variables["evpn_instance_list"] = json.dumps(
            evi_dict_new)
        return alert_level

    def monitor_tunnel_deletion(self, evi_dict_old, evi_dict_new,
                                tunnel_dict_old, vni_dict_new):
        '''this function generates alert for Tunnel Endpoint deleted per EVI'''

        dprint("Enter monitor_tunnel_deletion")
        alert_level = AlertLevel.NONE
        old_tunnels = {}
        new_tunnels = {}
        if evi_dict_old != {}:
            for evi in evi_dict_old.keys():
                old_tunnels[evi] = \
                    evi_dict_old[evi]["remote_mac_count_per_vtep_peer"].keys()
                dprint("old_tunnels[{0}]={1}".format(evi, old_tunnels[evi]))
        if evi_dict_new != {}:
            for evi in evi_dict_new.keys():
                new_tunnels[evi] = \
                    evi_dict_new[evi]["remote_mac_count_per_vtep_peer"].keys()
                dprint("new_tunnels[{0}]={1}".format(evi, new_tunnels[evi]))
        filtered_tunnels = (
            self.agent.params['Tunnel_endpoint'].value).split(',')
        deleted_tunnels_and_evis = {}
        for evi in evi_dict_old.keys():
            if evi not in evi_dict_new.keys():
                continue
            for tunnel in old_tunnels[evi]:
                # don't check for tunnel which is not given in filter
                if (filtered_tunnels[0] != '*' and
                        tunnel not in filtered_tunnels):
                    continue
                if tunnel in new_tunnels[evi]:
                    # tunnel not deleted
                    continue
                # common deployment for VxLAN is with underlay using default
                # VRF. If tunnel endpoint is deleted and we cannot get the
                # underlay VRF, we will use default VRF for underlay
                vrf = "default"
                for key in tunnel_dict_old.keys():
                    if tunnel in key:
                        vrf = key.split(',')[0]
                        break
                if tunnel not in deleted_tunnels_and_evis.keys():
                    deleted_tunnels_and_evis[tunnel] = list()
                deleted_tunnels_and_evis[tunnel].append(int(evi))
                self.action_config.add("show interface vxlan 1 brief")
                self.action_evpn.add("show evpn evi {0} detail".format(evi))
                vlan_id = vni_dict_new[evi]['vlan']
                if vlan_id is not None:
                    self.action_other.add("show vlan {0}".format(vlan_id))
                dprint("tunnel={0}, vrf={1}".format(tunnel, vrf))
                ipv6 = True if ':' in tunnel else False
                self.action_tunnel.add(
                    "show interface vxlan vteps {0} vrf {1}".format(
                        tunnel, vrf))
                self.action_conn.add("show bgp l2vpn evpn summary")
                self.action_conn.add(
                    "show ip route {0} vrf {1}".format(tunnel, vrf))
                self.action_conn.add("ping{0} {1} vrf {2} repetitions 2".format(
                    '6' if ipv6 else '', tunnel, vrf))
                self.action_conn.add(
                    "traceroute{0} {1} vrf {2}".format('6' if ipv6 else '',
                                                       tunnel, vrf))
                alert_level = AlertLevel.MINOR
        dprint("deleted_tunnels_and_evis={0}".format(
            deleted_tunnels_and_evis))
        for tunnel, evis in deleted_tunnels_and_evis.items():
            tunnel_del_syslog = "Peer VTEP {0} is deleted for EVPN " \
                "Instances {1}".format(tunnel, str(evis)[1:-1])
            self.agent.action_syslog(Log.WARNING, tunnel_del_syslog)
            self.agent.set_alert_description_for_key(EVPN, tunnel_del_syslog)

        if alert_level != AlertLevel.NONE:
            dprint("Enter alert_level != NONE")
            routing_agent_enable = "For BGP and OSPF adjacency related " \
                                   "issues enable Routing Agent"
            self.agent.action_syslog(
                Log.WARNING, routing_agent_enable)
            self.agent.set_alert_description_for_key(
                EVPN, routing_agent_enable)
            self.evpn_alert_on_this_cycle = True
            self.evpn_set_alert_level(alert_level)
        return alert_level

    def monitor_remote_mac_route_per_evi_vtep(self, evi_dict_old,
                                              evi_dict_new, vni_dict_new):
        '''this function generates alert if remote MAC/Route count per EVI and
         VTEP decreases more than 20% compared to previous poll cycle'''

        dprint("Enter monitor_remote_mac_route_per_evi_vtep")
        alert_level = AlertLevel.NONE
        percent_mac_route_lost = \
            int(self.agent.params['percent_mac_route_lost'].value)
        if evi_dict_old == {}:
            return alert_level
        for evi in evi_dict_new.keys():
            if evi not in evi_dict_old.keys():
                continue
            for vtep in evi_dict_new[evi]['remote_mac_count_per_vtep_peer'] \
                    .keys():
                if vtep not in evi_dict_old[evi]['remote_mac_count_per_vtep_peer'].keys():
                    continue
                old_mac_route_count = \
                    evi_dict_old[evi]['remote_mac_count_per_vtep_peer'][vtep]
                new_mac_route_count = \
                    evi_dict_new[evi]['remote_mac_count_per_vtep_peer'][vtep]
                dprint("old={0} new={1}".format(
                    old_mac_route_count, new_mac_route_count))
                if new_mac_route_count < old_mac_route_count:
                    decrease = old_mac_route_count - new_mac_route_count
                    percentage_decrease = int(
                        (decrease / old_mac_route_count) * 100)
                    if percentage_decrease >= percent_mac_route_lost:
                        # check if routing enable for VNI => L3VNI
                        if vni_dict_new[evi]["routing"] is True:
                            syslog = "{0}/{1} Remote Routes were " \
                                "deleted in EVPN Instance {2} for VTEP Peer " \
                                "{3}".format(decrease,
                                             old_mac_route_count, evi, vtep)
                        else:
                            syslog = "{0}/{1} Remote MACs " \
                                "were deleted in EVPN " \
                                "Instance {2} for VTEP Peer " \
                                "{3}".format(decrease,
                                             old_mac_route_count, evi, vtep)
                            self.action_other.add(
                                "show mac-address-table | inc evpn"
                                " | count")
                            self.action_evpn.add("show evpn mac-ip "
                                                 "evi {0}".format(evi))
                        alert_level = AlertLevel.MINOR
                        self.agent.action_syslog(
                            Log.WARNING, syslog)
                        self.agent.set_alert_description_for_key(EVPN, syslog)
                        self.action_evpn.add("show evpn evi {0} "
                                             "detail".format(evi))
                        self.action_evpn.add("show bgp l2vpn evpn vni "
                                             "{0}".format(evi))
        if alert_level != AlertLevel.NONE:
            dprint("Enter alert_level != NONE")
            self.evpn_alert_on_this_cycle = True
            self.evpn_set_alert_level(alert_level)
        return alert_level

    def monitor_local_mac_change(self, evi_dict_old, evi_dict_new):
        '''This function generates alert if Local MAC count per EVI decreases
         more than 20% compared to previous poll cycle'''

        dprint("Enter local_mac_count_change")
        alert_level = AlertLevel.NONE
        percent_local_mac_lost = \
            int(self.agent.params['percent_local_mac_lost'].value)
        if evi_dict_old != {}:
            for evi in evi_dict_new.keys():
                if evi in evi_dict_old.keys():
                    old_mac_count = \
                        evi_dict_old[evi]["statistics"]["local_mac_count"]
                    new_mac_count = \
                        evi_dict_new[evi]["statistics"]["local_mac_count"]
                    dprint("old={0} new={1}".format(
                        old_mac_count, new_mac_count))
                    if new_mac_count < old_mac_count:
                        decrease = old_mac_count - new_mac_count
                        percentage_decrease = int(
                            (decrease / old_mac_count) * 100)
                        if percentage_decrease >= percent_local_mac_lost:
                            mac_del_syslog = "{0}/{1} Local MACs " \
                                             "were deleted in EVPN " \
                                             "Instance {2}".format(
                                                 decrease, old_mac_count, evi)
                            alert_level = AlertLevel.MINOR
                            self.agent.action_syslog(
                                Log.WARNING, mac_del_syslog)
                            self.agent.set_alert_description_for_key(
                                EVPN, mac_del_syslog)
                            self.action_evpn.add("show evpn evi {0} detail"
                                                 .format(evi))
                            self.action_evpn.add("show evpn mac-ip evi {0}"
                                                 .format(evi))
                            self.action_other.add(
                                "show mac-address-table | inc dynamic | count")
            if alert_level != AlertLevel.NONE:
                dprint("Enter alert_level != NONE")
                self.evpn_alert_on_this_cycle = True
                self.evpn_set_alert_level(alert_level)
        return alert_level

    def monitor_peer_vtep_count_change(self, evi_dict_old, evi_dict_new):
        '''This function generates alert if peer VTEP count per EVI decreases
         more than 20% compared to previous poll cycle'''

        dprint("Enter peer_vtep_count_change")
        alert_level = AlertLevel.NONE
        percent_peer_vtep_lost = \
            int(self.agent.params['percent_peer_vtep_lost'].value)
        if evi_dict_old != {}:
            for evi in evi_dict_new.keys():
                if evi in evi_dict_old.keys():
                    old_peer_vtep_count = \
                        evi_dict_old[evi]["statistics"]["peer_vtep_count"]
                    new_peer_vtep_count = \
                        evi_dict_new[evi]["statistics"]["peer_vtep_count"]
                    dprint("old={0} new={1}".format(
                        old_peer_vtep_count, new_peer_vtep_count))
                    if new_peer_vtep_count < old_peer_vtep_count:
                        decrease = old_peer_vtep_count - new_peer_vtep_count
                        percentage_decrease = int(
                            (decrease / old_peer_vtep_count) * 100)
                        if (percentage_decrease >= percent_peer_vtep_lost and
                                percentage_decrease != 100):
                            peer_vtep_count_syslog = "{0}/{1} Peer " \
                                "VTEPs were deleted for EVPN " \
                                "Instance {2}".format(
                                    decrease, old_peer_vtep_count, evi)
                            self.agent.action_syslog(
                                Log.WARNING, peer_vtep_count_syslog)
                            self.agent.set_alert_description_for_key(
                                EVPN, peer_vtep_count_syslog)
                            alert_level = AlertLevel.MINOR
                            self.action_evpn.add("show evpn evi {0} detail"
                                                 .format(evi))
                            self.action_tunnel.add(
                                "show interface vxlan vteps")
            if alert_level != AlertLevel.NONE:
                dprint("Enter alert_level != NONE")
                self.evpn_alert_on_this_cycle = True
                self.evpn_set_alert_level(alert_level)
        return alert_level

    # Function to set alert levels
    # Input Parameters
    # level : alert level to be set(AlertLevel.MINOR, AlertLevel.MAJOR,
    # AlertLevel.CRITICAL)
    def evpn_set_alert_level(self, level):
        '''function used to set alert level'''
        self.agent.alert_levels_generated_within_poll_per_subagent[
            'evpn'].add(level)


class VxlanTunnelMonitorAgent(Agent):
    '''This class polls Tunnel_Endpoint table using REST query
     and Analyzes the data'''

    def __init__(self, agent):
        # dprint("WIP------- CoppAgent:__init__")
        self.agent = agent
        self.vxlan_tunnel_alert_on_this_cycle = False
        self.action_conn = set()
        self.action_evpn = set()
        self.action_vni = set()
        self.action_tunnel = set()
        self.action_config = set()
        self.action_other = set()
        self.tunnel_url_list = \
            self.vxlan_get_tunnel_uri(
                self.agent.params['vrf'].value,
                self.agent.params['origin'].value,
                self.agent.params['Tunnel_endpoint'].value)

    def vxlan_get_tunnel_uri(self, vrf, origin, destination):
        '''Returns a list of REST URI strings after adding user params'''
        tunnel_url_list = []
        for tunnel_vrf in vrf.split(","):
            for tunnel in destination.split(","):
                tunnel_url = HTTP_ADDRESS + \
                    '/rest/v10.10/system/interfaces/vxlan1/tunnel_endpoints' \
                    '/{0},{1},{2}'.format(tunnel_vrf, origin, tunnel)
                tunnel_url_list.append(tunnel_url)
        dprint("tunnel_url_list: {0}".format(tunnel_url_list))

        return tunnel_url_list

    def tunnel_handler(self):
        '''Wrapper for vxlan_tunnel_collect_data'''
        # dprint("WIP------- tunnel_handler")
        self.vxlan_tunnel_collect_data()

    def vxlan_tunnel_collect_data(self):
        '''Collects Tunnel_Endpoint data and analyzes'''
        tunnel_url_list = self.tunnel_url_list
        tunnel_response_list = []
        for url in tunnel_url_list:
            dprint("tunnel_url={0}".format(url))
            response = self.agent.fetch_url(url)
            dprint("response={0}".format(response))
            if response is None:
                continue
            else:
                tunnel_response_list.append(response)
        dprint('Tunnel Response list length:', len(tunnel_response_list))
        dprint('Tunnel response_list = {0}'.format(tunnel_response_list))
        # '''
        # tunnel_response_list if param is '*'
        # [
        # {
        #     "vxlan1": {
        #         "default,evpn,3.3.3.3": {
        #             "destination": "3.3.3.3",
        #             "macs_invalid": "None",
        #             "network_id": {
        #                 "vxlan_vni,10000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,10000",
        #                 "vxlan_vni,20":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20",
        #                 "vxlan_vni,20000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20000"
        #             },
        #             "origin": "evpn",
        #             "state": "operational",
        #             "statistics": {},
        #             "vrf": {
        #                 "default": "/rest/v10.10/system/vrfs/default"
        #             }
        #         },
        #         "default,evpn,4.4.4.4": {
        #             "destination": "4.4.4.4",
        #             "macs_invalid": "None",
        #             "network_id": {
        #                 "vxlan_vni,10000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,10000",
        #                 "vxlan_vni,20":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20",
        #                 "vxlan_vni,20000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20000"
        #             },
        #             "origin": "evpn",
        #             "state": "operational",
        #             "statistics": {},
        #             "vrf": {
        #                 "default": "/rest/v10.10/system/vrfs/default"
        #             }
        #         }
        #     }
        # }
        # ]
        # '''
        # '''
        # tunnel_response_list if param is '3.3.3.3,4.4.4.4'
        # [
        #     {
        #     "vxlan1": {
        #         "default,evpn,3.3.3.3": {
        #             "destination": "3.3.3.3",
        #             "macs_invalid": "None",
        #             "network_id": {
        #                 "vxlan_vni,10000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,10000",
        #                 "vxlan_vni,20":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20",
        #                 "vxlan_vni,20000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20000"
        #             },
        #             "origin": "evpn",
        #             "state": "operational",
        #             "statistics": {},
        #             "vrf": {
        #                 "default": "/rest/v10.10/system/vrfs/default"
        #             }
        #         }
        #     }
        # },
        #     {
        #     "vxlan1": {
        #         "default,evpn,4.4.4.4": {
        #             "destination": "4.4.4.4",
        #             "macs_invalid": "None",
        #             "network_id": {
        #                 "vxlan_vni,10000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,10000",
        #                 "vxlan_vni,20":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20",
        #                 "vxlan_vni,20000":
        # "/rest/v10.10/system/virtual_network_ids/vxlan_vni,20000"
        #             },
        #             "origin": "evpn",
        #             "state": "operational",
        #             "statistics": {},
        #             "vrf": {
        #                 "default": "/rest/v10.10/system/vrfs/default"
        #             }
        #         }
        #     }
        # }
        # ]
        # '''
        tunnel_res_dict = {}
        if tunnel_response_list != []:
            if (self.agent.params['Tunnel_endpoint'].value == '*' and
                    self.agent.params['vrf'].value == '*'):
                tunnel_res_dict = tunnel_response_list[0]['vxlan1']
            else:
                for elem in tunnel_response_list:
                    item = list(elem['vxlan1'].items())[0]
                    dprint("item={0}".format(item))
                    key = item[0]
                    value = item[1]
                    tunnel_res_dict[key] = value
        dprint('tunnel_res_dict = {0}'.format(tunnel_res_dict))

        self.vxlan_tunnel_analyze_data(tunnel_res_dict)

        # bring the alert back to normal
        if self.vxlan_tunnel_alert_on_this_cycle is True:
            dprint("vxlan_tunnel_alert_on_this_cycle is True")
            self.agent.variables['tunnel_alert_on_last_cycle'] = "True"
        else:
            dprint("self.vxlan_tunnel_alert_on_this_cycle is False")
            if self.agent.variables['tunnel_alert_on_last_cycle'] == "True":
                dprint("tunnel_alert_on_last_cycle is True")
                self.agent.variables['tunnel_alert_on_last_cycle'] = "False"
                self.vxlan_tunnel_set_alert_level(AlertLevel.NONE)
        return None

    def vxlan_tunnel_analyze_data(self, tunnel_res_dict):
        '''this function stores the required Tunnel_Endpoint Data from
         JSON response in local storage and Analyzes the changes by comparing
         with previous response'''
        tunnel_list_dict_new = {}
        for key in tunnel_res_dict.keys():
            dprint('key={0}'.format(key))
            tunnel_state = tunnel_res_dict[key]["state"]
            down_time = 0
            tunnel_list_dict_new[key] = {
                "state": tunnel_state,
                "down_time": down_time
            }
        dprint("tunnel_list_dict_new={0}".format(tunnel_list_dict_new))
        tunnel_list_dict_old = json.loads(
            self.agent.variables["tunnel_instance_list"])
        dprint("tunnel_list_dict_old={0}".format(tunnel_list_dict_old))

        # dprint("---------------------------")
        # dprint('vxlan tunnel dict old:')
        # for key in tunnel_list_dict_old.keys():
        #     dprint("{0}: {1} {2}".format(
        #         key, tunnel_list_dict_old[key]['state'],
        #         tunnel_list_dict_old[key]['down_time']))
        # dprint("---------------------------")
        # dprint("vxlan tunnel dict new:")
        for key in tunnel_list_dict_new.keys():
            if key in tunnel_list_dict_old.keys():
                # dprint("{0}: {1}".format(
                #     key, tunnel_list_dict_new[key]['state']))
                tunnel_list_dict_new[key]['down_time'] = \
                    tunnel_list_dict_old[key]['down_time']
        # dprint("---------------------------")
        dprint("tunnel_list_dict_new={0}".format(tunnel_list_dict_new))

        self.monitor_tunnel_deletion(tunnel_list_dict_old,
                                     tunnel_list_dict_new)
        self.monitor_tunnel_state(tunnel_list_dict_old,
                                  tunnel_list_dict_new)
        # self.monitor_tunnel_confg_state_change(tunnel_list_dict_new)
        self.agent.actioncli['conn'].update(self.action_conn)
        self.agent.actioncli['evpn'].update(self.action_evpn)
        self.agent.actioncli['vni'].update(self.action_vni)
        self.agent.actioncli['tunnel'].update(self.action_tunnel)
        self.agent.actioncli['config'].update(self.action_config)
        self.agent.actioncli['other'].update(self.action_other)
        self.agent.variables['tunnel_instance_list'] = json.dumps(
            tunnel_list_dict_new)

    # '''
    # Structure of tunnel dict:
    # keys: vrf,origin,destination
    # default,evpn,3.3.3.3:{
    #     'state':"activating",
    #     'down_time': 0
    # }
    # '''
    def monitor_tunnel_deletion(self, tunnel_list_dict_old,
                                tunnel_list_dict_new):
        '''This function generates alert for Tunnel_Endpoints
         which are deleted'''
        for key in tunnel_list_dict_old.keys():
            if key not in tunnel_list_dict_new.keys():
                tunnel = key.split(',')
                vrf = tunnel[0]
                origin = tunnel[1]
                destination = tunnel[2]
                ipv6 = True if ':' in destination else False
                message = "Tunnel deleted vrf:{0}, origin:{1}, " \
                          "destination:{2}".format(vrf, origin, destination)
                self.logger.info(message)
                self.agent.action_syslog(Log.WARNING, message)
                self.agent.set_alert_description_for_key(TUNNEL, message)
                self.action_conn.add("show ip{0} route {1} vrf {2}".format(
                    'v6' if ipv6 else '', destination, vrf))
                self.action_conn.add("ping{0} {1} vrf {2} repetitions 2".format(
                    '6' if ipv6 else '', destination, vrf))
                subnet_mask = '%2F128' if ipv6 else '%2F32'
                if ipv6:
                    destination = destination.replace(':', '%3A')
                nh_url = "{0}/rest/v10.10/system/vrfs/{1}/routes/{2}{3}/" \
                         "nexthops?depth=2".format(
                             HTTP_ADDRESS, vrf, destination, subnet_mask)
                dprint(nh_url)
                response = self.fetch_url(nh_url)
                dprint(response)
                if response:
                    nh_add = list(response.values())[0]
                    if len(nh_add) > 0:
                        is_nh_v6 = True if ':' in nh_add else False
                        self.action_conn.add("ping{0} {1} vrf {2} "
                                             "repetitions 2".format(
                                                 '6' if is_nh_v6 else '',
                                                 nh_add, vrf))
                        self.action_conn.add("show {0} vrf {1} | "
                                             "include {2}".format(
                                                 'ipv6 neighbors' if is_nh_v6
                                                 else 'arp', vrf, nh_add))
                self.action_config.add("show running-config interface vxlan1")
                self.vxlan_tunnel_alert_on_this_cycle = True
                self.vxlan_tunnel_set_alert_level(AlertLevel.MINOR)

    def monitor_tunnel_state(self, tunnel_dict_old, tunnel_dict_new):
        '''this function monitor tunnel endpoint state changes from operational
         to non-operational state and stuck in non-operational state for 5
         poll cycles. Generates alerts for the same.'''

        dprint("Enter monitor_tunnel_state")
        syslog = ""
        alert_level = AlertLevel.NONE
        if tunnel_dict_new == {}:
            pass
        for key, tunnel in tunnel_dict_new.items():
            state_change_or_stuck = False
            vrf = key.split(',')[0]
            origin = key.split(',')[1]
            destination = key.split(',')[2]
            ipv6 = True if ':' in destination else False
            state = tunnel['state']
            origin_to_rr = 'vxlan'
            if state != "operational":
                if tunnel["down_time"] == 0:
                    if (key in tunnel_dict_old.keys() and
                            tunnel_dict_old[key]['state'] == "operational"):
                        state_change_or_stuck = True
                        tunnel["down_time"] += 1
                        syslog = "Tunnel vrf:{0} origin:{1} destination:{2}" \
                                 " is going down from operational to {3} " \
                                 "state".format(vrf, origin, destination,
                                                state)
                        alert_level = AlertLevel.MAJOR
                        self.agent.action_syslog(Log.WARNING, syslog)
                        self.agent.set_alert_description_for_key(
                            TUNNEL, syslog)
                    elif key in tunnel_dict_old.keys():
                        tunnel["down_time"] += 1
                elif tunnel["down_time"] == 5:
                    state_change_or_stuck = True
                    tunnel["down_time"] += 1
                    syslog = "Tunnel Endpoint {0} is stuck in {1} " \
                        "state".format(destination, state)
                    alert_level = AlertLevel.MINOR
                    self.agent.action_syslog(Log.WARNING, syslog)
                    self.agent.set_alert_description_for_key(TUNNEL, syslog)
                elif ((0 < tunnel["down_time"] < 5) and
                      self.agent.variables['tunnel_alert_on_last_cycle'] ==
                      "True"):
                    alert_level = AlertLevel.MAJOR
                    tunnel["down_time"] += 1
                    syslog = "Tunnel vrf:{0} origin:{1} destination:{2}" \
                             " is in {3} state".format(
                                 vrf, origin, destination, state)
                    self.agent.set_alert_description_for_key(TUNNEL, syslog)
                elif ((tunnel["down_time"] > 5) and
                      self.agent.variables['tunnel_alert_on_last_cycle'] ==
                      "True"):
                    alert_level = AlertLevel.MINOR
                    tunnel["down_time"] += 1
                    syslog = "Tunnel vrf:{0} origin:{1} destination:{2}" \
                             " is in {3} state".format(
                                 vrf, origin, destination, state)
                    self.agent.set_alert_description_for_key(TUNNEL, syslog)
                else:
                    tunnel["down_time"] += 1
                if state_change_or_stuck is True:
                    self.action_conn.add("ping{0} {1} vrf {2} repetitions "
                                         "2".format('6' if ipv6 else '',
                                                    destination, vrf))
                    self.action_conn.add("traceroute{0} {1} vrf {2}".format(
                        '6' if ipv6 else '', destination, vrf))
                    self.action_conn.add("show ip{0} route {1} vrf {2}".format(
                        'v6' if ipv6 else '', destination, vrf))
                    if origin == "evpn":
                        self.action_conn.add("show bgp l2vpn evpn summary")
                        self.action_evpn.add("show evpn vtep-neighbor all-vrfs"
                                             " | include {0}".format(
                                                 destination))
                    self.action_tunnel.add("show interface vxlan vteps {0} "
                                           "vrf {1}".format(destination, vrf))
                    if state == "configuration_error":
                        self.action_config.add("show running-config interface "
                                               "vxlan 1")
                    rr_url = HTTP_ADDRESS + '/rest/v10.10/system/vrfs/' \
                        + vrf + '/route_resolutions?' \
                        'attributes=route_details&depth=2&' \
                        'filter=address%3A' + destination + \
                        '%2Corigin%3A' + origin_to_rr
                    dprint("rr_url={}".format(rr_url))
                    response = self.fetch_url(rr_url)
                    dprint(response)
                    if response is None:
                        continue
                    else:
                        response = list(response.values())
                    res = response[0]['route_details']
                    r_key = 'prefix'
                    if r_key in res.keys():
                        ip_address = response[0]['route_details']['prefix'] \
                            .split('/')
                        dprint(ip_address)
                        dprint("ip:{},mask{}".format(
                            ip_address[0], ip_address[1]))
                        ipv6 = True if ':' in ip_address[0] else False
                        if ipv6:
                            ip_address[0] = ip_address[0].replace(':', '%3A')
                        nh_url = "{0}/rest/v10.10/system/vrfs/{1}/routes/" \
                                 "{2}%2F{3}/nexthops?depth=2".format(
                                     HTTP_ADDRESS, vrf, ip_address[0],
                                     ip_address[1])
                        dprint(nh_url)
                        response = self.fetch_url(nh_url)
                        dprint("nh_response={0}".format(response))
                        if response is not None:
                            nh_add = list(response.values())[0]
                            if len(nh_add) > 0:
                                is_nh_v6 = True if ':' in nh_add else False
                                self.action_conn.add("ping{0} {1} vrf {2} "
                                                     "repetitions 2"
                                                     .format(
                                                         '6' if is_nh_v6 else
                                                         '', nh_add, vrf))
                                self.action_conn.add("show {0} vrf {1} | "
                                                     "include {2}"
                                                     .format('ipv6 neighbors'
                                                             if is_nh_v6 else
                                                             'arp', vrf,
                                                             nh_add))
                    else:
                        dprint("there is no L3 route exist for tunnel "
                               "endpoint {}".format(destination))
                        message = "there is no L3 route exist for " \
                                  "tunnel endpoint {}".format(destination)
                        self.logger.info(message)
                        self.agent.action_syslog(Log.WARNING, message)
                        self.agent.set_alert_description_for_key(
                            TUNNEL, message)
            elif ((state == "operational") and
                  (tunnel["down_time"] > 0)):
                # reset tunnel down_time if it is back up
                tunnel["down_time"] = 0
        if alert_level != AlertLevel.NONE:
            dprint("Enter alert_level != NONE")
            self.vxlan_tunnel_alert_on_this_cycle = True
            self.vxlan_tunnel_set_alert_level(alert_level)
        self.agent.variables["tunnel_instance_list"] = json.dumps(
            tunnel_dict_new)
        return alert_level

    def vxlan_tunnel_set_alert_level(self, level):
        self.agent.alert_levels_generated_within_poll_per_subagent[
            'tunnel'].add(level)


class VNIHealthMonitorAgent(Agent):
    '''This class polls Virtual_Network_ID table using REST query
     and Analyzes the data'''

    def __init__(self, agent):
        # dprint("WIP------- VniAgent:__init__")
        self.agent = agent
        self.vni_alert_on_this_cycle = False
        self.action_conn = set()
        self.action_evpn = set()
        self.action_vni = set()
        self.action_tunnel = set()
        self.action_config = set()
        self.action_other = set()
        self.vni_url_list = \
            self.get_vni_url_list(
                self.agent.params['vni_id'].value)

    def get_vni_url_list(self, vni_ids):
        '''This function returns list of VNI URI strings after adding user
         params'''
        vni_url_list = []

        for vni_id in vni_ids.split(","):
            if vni_id == '*':
                vni_url = HTTP_ADDRESS + \
                    '/rest/v10.10/system/virtual_network_ids?attributes=' \
                    'id,type,vrf,vlan,routing,state&depth=3'
            else:
                vni_url = HTTP_ADDRESS + \
                    '/rest/v10.10/system/virtual_network_ids?attributes=' \
                    'id,type,vrf,vlan,routing,state' \
                    '&depth=3&filter=id%3A' + vni_id
            vni_url_list.append(vni_url)
            dprint("vni_url_list: {0}".format(vni_url_list))

        return vni_url_list

    def vni_handler(self):
        '''Wrapper for vni_collect_data'''
        dprint("WIP------- vni_handler")
        self.vni_collect_data()

    def vni_collect_data(self):
        '''Fetch VNI data using REST query and analyze'''
        vni_url_list = self.vni_url_list
        vni_response_list = []

        for url in vni_url_list:
            dprint(url)

        for url in vni_url_list:
            response = self.agent.fetch_url(url)
            if response is None:
                continue
            else:
                vni_response_list.append(response)

        dprint('VNI Response list length:{0}'.format(len(vni_response_list)))
        dprint('VNI response_list = {0}'.format(vni_response_list))

        self.vni_analyze_data(vni_response_list)

        # bring the alert back to normal
        if self.vni_alert_on_this_cycle is True:
            dprint("vni_alert_on_this_cycle is True")
            self.agent.variables['vni_alert_on_last_cycle'] = "True"
        else:
            dprint("self.vni_alert_on_this_cycle is False")
            if self.agent.variables['vni_alert_on_last_cycle'] == "True":
                dprint("vni_alert_on_last_cycle is True")
                self.agent.variables['vni_alert_on_last_cycle'] = "False"
                self.vxlan_vni_set_alert_level(AlertLevel.NONE)

        return None

    def vni_analyze_data(self, vni_res_list):
        '''this function stores the required VNI data from
         JSON response in local storage and Analyzes the changes by comparing
         with previous response'''
        vni_res_list = [] if vni_res_list is None else vni_res_list
        vni_dict_new = {}
        dprint('vni_res_list={0}'.format(vni_res_list))

        # vni dict new:
        # {
        #     "20": {
        #         "id": 20,
        #         "routing": "False",
        #         "state": "configuration_error",
        #         "vlan": "20",
        #         "vrf": "None",
        #         "down_time": 0
        #     },
        #     "10000": {
        #         "id": 10000,
        #         "routing": "True",
        #         "state": "configuration_error",
        #         "vlan": "None",
        #         "vrf": "red",
        #         "down_time": 0
        #     }
        # }

        vni_temp = []
        if self.agent.params['vni_id'].value == '*':
            if vni_res_list:
                vni_res_list = vni_res_list[0]
                for key in vni_res_list.keys():
                    vni_temp = key.split(',')
                    vni_id_str = vni_temp[1]
                    vni_id = vni_res_list[key]["id"]
                    vni_dict_new[vni_id_str] = {
                        "id": vni_id,
                        "state": vni_res_list[key]["state"],
                        "routing": vni_res_list[key].get("routing", None),
                        "vlan": None,
                        "vrf": None,
                        "down_time": 0}

                    if vni_res_list[key]["vlan"] is not None:
                        vni_dict_new[vni_id_str]["vlan"] = list(
                            vni_res_list[key]["vlan"].keys())[0]

                    # in 6200 platform, 'vrf' col. is absent in REST output
                    if "vrf" in vni_res_list[key].keys():
                        if vni_res_list[key]["vrf"] is not None:
                            vni_dict_new[vni_id_str]["vrf"] = list(
                                vni_res_list[key]["vrf"].keys())[0]
        else:
            for vni_dict in vni_res_list:
                for key in vni_dict.keys():
                    vni_temp = key.split(',')
                    vni_id_str = vni_temp[1]
                    vni_id = vni_dict[key]["id"]
                    vni_dict_new[vni_id_str] = {
                        "id": vni_id,
                        "state": vni_dict[key]["state"],
                        "routing": vni_dict[key].get("routing", None),
                        "vlan": None,
                        "vrf": None,
                        "down_time": 0}

                    if vni_dict[key]["vlan"] is not None:
                        vni_dict_new[vni_id_str]["vlan"] = list(
                            vni_dict[key]["vlan"].keys())[0]

                    # in 6200 platform, 'vrf' col. is absent in REST output
                    if "vrf" in vni_dict[key].keys():
                        if vni_dict[key]["vrf"] is not None:
                            vni_dict_new[vni_id_str]["vrf"] = list(
                                vni_dict[key]["vrf"].keys())[0]

        vni_dict_old = json.loads(
            self.agent.variables["vni_instance_list"])
        dprint('vni dict old: {0}'.format(vni_dict_old))
        dprint('vni dict new: {0}'.format(vni_dict_new))

        dprint("---------------------------")
        dprint('vni dict old:')
        for key in vni_dict_old.keys():
            dprint("{0}: {1}".format(
                key, vni_dict_old[key]['state']))
        dprint("---------------------------")
        dprint("vni dict new:")
        for key in vni_dict_new.keys():
            dprint("{0}: {1}".format(
                key, vni_dict_new[key]['state']))
            if key in vni_dict_old.keys():
                vni_dict_new[key]['down_time'] = vni_dict_old[key]['down_time']
        dprint("---------------------------")

        self.monitor_vni_config_errors(vni_dict_old, vni_dict_new)
        self.monitor_vni_state(vni_dict_old, vni_dict_new)
        self.agent.actioncli['conn'].update(self.action_conn)
        self.agent.actioncli['evpn'].update(self.action_evpn)
        self.agent.actioncli['vni'].update(self.action_vni)
        self.agent.actioncli['tunnel'].update(self.action_tunnel)
        self.agent.actioncli['config'].update(self.action_config)
        self.agent.actioncli['other'].update(self.action_other)
        self.agent.variables['vni_instance_list'] = json.dumps(vni_dict_new)

    def monitor_vni_state(self, vni_dict_old, vni_dict_new):
        '''this function monitor VNI state changes from operational
            to non-operational state and stuck in non-operational state for 5
            poll cycles. Generates alerts for the same.'''
        dprint("Enter monitor_vni_state")
        alert_level_major = False
        alert_level_minor = False
        for key in vni_dict_new.keys():
            if key in vni_dict_old.keys():
                down_time = vni_dict_new[key]["down_time"]
                update_down_time = True
                if down_time > vni_dict_old[key]["down_time"]:
                    # do not update down_time as it was updated by previous
                    # function
                    update_down_time = False
                if vni_dict_new[key]["state"] != "operational":
                    if ((vni_dict_old[key]["state"] == "operational") and
                       ((down_time == 0) or
                            (down_time == 1 and update_down_time is False))):
                        message = "vni:{0} state changed from operational " \
                            "to {1} state".format(
                                vni_dict_new[key]["id"],
                                vni_dict_new[key]["state"])
                        self.logger.info(message)
                        self.agent.action_syslog(Log.WARNING, message)
                        self.agent.set_alert_description_for_key(VNI, message)
                        self.action_vni.add("show interface vxlan vni {0}"
                                            .format(vni_dict_new[key]["id"]))
                        vlan_id = vni_dict_new[key]['vlan']
                        if vlan_id is not None:
                            self.action_other.add("show vlan {0}"
                                                  .format(vlan_id))
                        if (vni_dict_new[key]["state"] ==
                                "configuration_error"):
                            self.action_config.add(
                                "show interface vxlan 1 brief")
                        if update_down_time is True:
                            vni_dict_new[key]["down_time"] += 1
                        alert_level_major = True
                    if down_time == 5:
                        message = "vni:{0} is stuck at {1} " \
                            "state".format(vni_dict_new[key]["id"],
                                           vni_dict_new[key]["state"])
                        self.logger.info(message)
                        self.agent.action_syslog(Log.WARNING, message)
                        self.agent.set_alert_description_for_key(VNI, message)
                        self.action_vni.add("show interface vxlan vni {0}"
                                            .format(vni_dict_new[key]["id"]))
                        vlan_id = vni_dict_new[key]['vlan']
                        if vlan_id is not None:
                            self.action_other.add("show vlan {0}"
                                                  .format(vlan_id))
                        if vni_dict_new[key]["state"] == "configuration_error":
                            self.action_config.add(
                                "show interface vxlan 1 brief")
                        if update_down_time is True:
                            vni_dict_new[key]["down_time"] += 1
                        alert_level_minor = True
                    if 0 < vni_dict_new[key]["down_time"] < 5:
                        dprint("monitor_vni_stat: enter down_time less than 5")
                        # above conditions not met
                        if (down_time == vni_dict_new[key]["down_time"] and
                                update_down_time is True):
                            vni_dict_new[key]["down_time"] += 1
                        message = "vni:{0} has a down_time between 0 and 5 cycles".format(
                            vni_dict_new[key]["id"])
                        self.agent.set_alert_description_for_key(VNI, message)
                        alert_level_major = True
                    if vni_dict_new[key]["down_time"] > 5:
                        dprint("monitor_vni_stat: enter down_time more than 5")
                        # above conditions not met
                        if (down_time == vni_dict_new[key]["down_time"] and
                                update_down_time is True):
                            vni_dict_new[key]["down_time"] += 1
                        message = "vni:{0} has a down_time of over 5 cycles".format(
                            vni_dict_new[key]["id"])
                        self.agent.set_alert_description_for_key(VNI, message)
                        alert_level_minor = True
                else:
                    # reset down_time for vni when it is no longer incrementing
                    if vni_dict_new[key]["down_time"] == \
                            vni_dict_old[key]["down_time"]:
                        vni_dict_new[key]["down_time"] = 0
        if alert_level_major is True:
            self.vni_alert_on_this_cycle = True
            self.vxlan_vni_set_alert_level(AlertLevel.MAJOR)
        elif alert_level_minor is True:
            self.vni_alert_on_this_cycle = True
            self.vxlan_vni_set_alert_level(AlertLevel.MINOR)
        self.agent.variables["vni_instance_list"] = json.dumps(
            vni_dict_new)

    def monitor_vni_config_errors(self, vni_dict_old, vni_dict_new):
        '''this function monitors VNI routing, vlan and vrf and Alerts if
           configuration errors present in VNI '''
        dprint("Enter monitor_vni_config_errors")
        syslog = ""
        alert_level = AlertLevel.NONE
        for vni in vni_dict_new.values():
            down_time = vni["down_time"]
            dprint("vni: {0}| routing: {1}| vlan: {2}| vrf: {3}| down_time:"
                   " {4}".format(
                       vni["id"], vni['routing'], vni['vlan'], vni['vrf'],
                       vni['down_time']))
            if (vni["routing"] is False and vni["vlan"] is None and
                    vni["vrf"] is not None):
                dprint("vni: {0}| routing: {1}| vlan: {2}| vrf: {3}| "
                       "down_time: {4}".format(vni["id"], vni['routing'],
                                               vni['vlan'], vni['vrf'],
                                               vni['down_time']))
                if down_time == 4:
                    vni["down_time"] += 1
                    syslog = "Configuration error: Routing is disabled in " \
                             "L3VNI {0}".format(vni["id"])
                    self.agent.action_syslog(Log.WARNING, syslog)
                    self.agent.set_alert_description_for_key(VNI, syslog)
                    self.action_vni.add("show interface vxlan vni {0} vteps"
                                        .format(vni["id"]))
                    self.action_config.add(
                        "show running-config interface vxlan 1")
                    vlan_id = vni['vlan']
                    if vlan_id is not None:
                        self.action_other.add("show vlan {0}"
                                              .format(vlan_id))
                    alert_level = AlertLevel.MINOR
                elif down_time < 4:
                    vni["down_time"] += 1
                elif down_time > 4:
                    vni["down_time"] += 1
                    message = "vni: {0}| routing: {1}| vlan: {2}| vrf: {3}| down_time: {4}".format(
                        vni["id"], vni['routing'], vni['vlan'], vni['vrf'], vni['down_time'])
                    self.agent.set_alert_description_for_key(VNI, message)
                    alert_level = AlertLevel.MINOR
            elif (vni["routing"] is True and vni["vlan"] is None and
                  vni["vrf"] is None):
                dprint("vni: {0}| routing: {1}| vlan: {2}| vrf: {3}|"
                       "down_time: {4}".format(vni["id"], vni['routing'],
                                               vni['vlan'], vni['vrf'],
                                               vni['down_time']))
                if down_time == 4:
                    vni["down_time"] += 1
                    syslog = 'Configuration error: Please configure ' \
                        'non default VRF for L3VNI {0}'.format(vni["id"])
                    self.agent.action_syslog(Log.WARNING, syslog)
                    self.agent.set_alert_description_for_key(VNI, syslog)
                    self.action_vni.add("show interface vxlan vni {0} vteps"
                                        .format(vni["id"]))
                    self.action_config.add(
                        "show running-config interface vxlan 1")
                    vlan_id = vni['vlan']
                    if vlan_id is not None:
                        self.action_other.add("show vlan {0}".format(vlan_id))
                    alert_level = AlertLevel.MINOR
                elif down_time < 4:
                    vni["down_time"] += 1
                elif down_time > 4:
                    vni["down_time"] += 1
                    message = "vni: {0}| routing: {1}| vlan: {2}| vrf: {3}| down_time: {4}".format(
                        vni["id"], vni['routing'], vni['vlan'], vni['vrf'], vni['down_time'])
                    self.agent.set_alert_description_for_key(VNI, message)
                    alert_level = AlertLevel.MINOR
            elif (vni["routing"] is False and vni["vlan"] is None and
                  vni["vrf"] is None):
                dprint("vni: {0}| routing: {1}| vlan: {2}| vrf: {3}|"
                       "down_time: {4}".format(vni["id"], vni['routing'],
                                               vni['vlan'], vni['vrf'],
                                               vni['down_time']))
                if down_time == 4:
                    vni["down_time"] += 1
                    syslog = "Configuration error: Please configure " \
                             "VLAN for L2VNI {0} or enable routing and " \
                             "configure non-default VRF to make it L3VNI " \
                             "{0}".format(vni["id"])
                    self.agent.action_syslog(Log.WARNING, syslog)
                    self.agent.set_alert_description_for_key(VNI, syslog)
                    self.action_vni.add("show interface vxlan vni {0} vteps"
                                        .format(vni["id"]))
                    self.action_config.add(
                        "show running-config interface vxlan 1")
                    vlan_id = vni['vlan']
                    if vlan_id is not None:
                        self.action_other.add("show vlan {0}".format(vlan_id))
                    alert_level = AlertLevel.MINOR
                elif down_time < 4:
                    vni["down_time"] += 1
                elif down_time > 4:
                    vni["down_time"] += 1
                    message = "vni: {0}| routing: {1}| vlan: {2}| vrf: {3}| down_time: {4}".format(
                        vni["id"], vni['routing'], vni['vlan'], vni['vrf'], vni['down_time'])
                    self.agent.set_alert_description_for_key(VNI, message)
                    alert_level = AlertLevel.MINOR
            elif (vni["routing"] is True and vni["vlan"] is not None and
                  vni["vrf"] is None):
                dprint("vni: {0}| routing: {1}| vlan: {2}| vrf: {3}| "
                       "down_time: {4}".format(vni["id"], vni['routing'],
                                               vni['vlan'], vni['vrf'],
                                               vni['down_time']))
                if down_time == 4:
                    vni["down_time"] += 1
                    syslog = "Configuration error: Please disable " \
                             "routing for L2VNI {0}".format(vni["id"])
                    self.agent.action_syslog(Log.WARNING, syslog)
                    self.agent.set_alert_description_for_key(VNI, syslog)
                    self.action_vni.add("show interface vxlan vni {0} vteps"
                                        .format(vni["id"]))
                    self.action_config.add(
                        "show running-config interface vxlan 1")
                    vlan_id = vni['vlan']
                    if vlan_id is not None:
                        self.action_other.add("show vlan {0}"
                                              .format(vlan_id))
                    alert_level = AlertLevel.MINOR
                elif down_time < 4:
                    vni["down_time"] += 1
                elif down_time > 4:
                    vni["down_time"] += 1
                    message = "vni: {0}| routing: {1}| vlan: {2}| vrf: {3}| down_time: {4}".format(
                        vni["id"], vni['routing'], vni['vlan'], vni['vrf'], vni['down_time'])
                    self.agent.set_alert_description_for_key(VNI, message)
                    alert_level = AlertLevel.MINOR
            dprint("vni_dict_old={0}".format(vni_dict_old))
            dprint("vni_dict_old.keys()={0}".format(vni_dict_old.keys()))
        if alert_level != AlertLevel.NONE:
            self.vni_alert_on_this_cycle = True
            self.vxlan_vni_set_alert_level(alert_level)
        self.agent.variables["vni_instance_list"] = json.dumps(
            vni_dict_new)

    def vxlan_vni_set_alert_level(self, level):
        self.agent.alert_levels_generated_within_poll_per_subagent[
            'vni'].add(level)
