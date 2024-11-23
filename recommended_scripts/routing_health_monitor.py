# -*- coding: utf-8 -*-
#
# (c) Copyright 2018-2024 Hewlett Packard Enterprise Development LP
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

#               --  Routing Heath functionality  --
# The overall, terse goal of this script is to monitor routing health,
# decide if things have gone bad, and if so, generate some helpful cli/shell
# output from the appropiate moment of the event.
#
# Agents derived from this script will monitor three areas:
# 1. COPP
#    - monitor COPP stat: "unresolved_ip_unicast_packets_dropped"
#    - alert if 1, 5, or 10 minute moving average increases above 10 percent
#      of the system capacity
#    - publish output from:
#       - show copp statistics non-zero
#       - show ip route summary all-vrfs
#       - obsdb incomplete routes
#       - ovsdb  incomplete neighbors
#       - l3 resource manager capacities
#    - clear alert if moving averages drop below 1 percent of system capacity
#
# 2. OSPF
#   - monitor OSPF neighbors
#   - alert if
#     - OSPF neighbors getting expired
#     - OSPF neighbors getting stuck in ex_start, exchange, init states
#       - alert is set between ospf threshold time and upto 5 poll cycles
#     - OSPF neighbors going down from stable full and two_way adjacencies
#     - OSPF neighbors going down from LSA exchange process
#   - publish output from:
#     - show interface stats - to know the ospf tx/rx statistics and errors
#     - debug ospf port - debug one of the ospf interfaces which alerted
#       - enable only in one else too much data to debug
#       - collects data for 5 poll cycles
#       - display at the end of 5 poll cycles
#     - ping to the neighbor few times
#   - clear alert if
#     - All neighbors present are in good state
#   - filters
#     - based on vrf, area or interface ( interface-list can be given
#       separated by comma ))
#   - alerts
#       - CRITICAL
#           - neighbor stuck in states ex_start/exchange/init
#       -MAJOR
#           - neighbor state change from full to init/down/exchange/ex_start
#           - neighbor state change from two_way to init/down
#           - neighbor state change from exchange to init/down/two_way/ex_start
#           - neighbor state change from ex_start to init/two_way/down
#       -MINOR
#           - neighbor expired

#
#
#
# 3. BGP
#   - monitor BGP neighbors
#   - alert if
#     - BGP neighbors getting stuck in Idle, Active, Connect, OpenConfirm
#       states
#       - alert is set between BGP threshold time and upto 5 poll cycles
#     - BGP neighbors going down from Established state
#     - BGP neighbor state flaps within a single poll interval
#     - BGP neighbor exchanges a new error, sub-error code than before
#     - BGP neighbor added or deleted
#   - publish output from:
#     - show bgp all summary - to know all the neighbor states
#     - ping <bgp_nbr> <source> - to check if peer address is reachable
#     - traceroute <bgp_nbr> - to check where is the packet dropped
#     - syslogs to indicate the error and sub-error codes sent/received from
#       BGP neighbor
#   - clear alert if
#     - All neighbors present are in good state
#   - filters
#     - based on vrf, neighbor address
#   - alerts
#       - CRITICAL
#           - neighbor state changed from estabished to idle/connect/active/
#             OpenConfirm
#       - MAJOR
#           - neighbor is flapping( neighbor state is 'established' in last and
#             current cycle but 'bgp_peer_established_count' in current cycle
#             is greater
#             than last cycle)
#       - MINOR
#           - neighbor stuck in states idle/connect/active/OpenConfirm
#           - neighbor deleted
#
#
#
#
#
#
#  4. Routing health
#     - monitor Routing daemon high cpu
#     - alert if
#       - CPU stays high for cpu_threshold for cpu_time_interval
#     - actions
#       - for the cpu_cooldown_interval do not query ospf/bgp neighbors
#       - do not case additional cpu spike
#       - give time for cool down
#
#
#
#
# 5. PREFIX
# - Monitors critical prefixes entered by user
# - User enters comma separated list of IPv4 and/or IPv6 prefixes and corresponding VRF in format prefix|vrf_name.
# - An exact match is done on the prefix and data is fetched and analysed from Route Table
# - alert if:
#     - Route is not present from the start
#     - Route is deleted
#     - Route is modified - source, metric and admin distance changes
# - publish output from:
#     - show ip route summary all-vrfs ( v6 equivalent if v6 route )
#     - show ip rib summary all-vrfs ( v6 equivalent if v6 route )
#     - show arp summary all-vrfs ( v6 equivalent if v6 route )
#     - show ip route <that_route> vrf <that_vrf> ( v6 equivalent if v6 route )
#     - show ip rib <that_route> vrf <that_vrf> ( v6 equivalent if v6 route )
#     - Based on route source, display ospf or bgp commands
# - alert if:
#     - Nexthop is deleted
# - publish output from:
#     - show ip route summary all-vrfs ( v6 equivalent if v6 route )
#     - show ip rib summary all-vrfs ( v6 equivalent if v6 route )
#     - show arp summary all-vrfs ( v6 equivalent if v6 route )
#     - show ip route <that_route> vrf <that_vrf> ( v6 equivalent if v6 route )
#     - show ip rib <that_route> vrf <that_vrf> ( v6 equivalent if v6 route )
#     - show arp vrf <that_vrf> | include <that_nexthop> ( v6 equivalent if v6 route )
#     - show arp vrf <that_vrf> | include <that_nexthop> ( v6 equivalent if v6 route )
#     - ping <that_nexthop> vrf <that_vrf> repetitions 2 ( v6 equivalent if v6 route )
#     - Based on route source, display ospf or bgp commands ( v6 equivalent if v6 route )
# - clear alert if:
#     - All Prefixes entered by user are in good state
# - alerts:
#         -MAJOR
#             Alert remains till route is added back
#             - Route is deleted.
#             - Route is not present from the start
#         - MINOR
#             Alert for 1 cycle and return to normal in next cycle
#             - Route is modified - source, metric and admin distance changes
#             - Nexthop is deleted
#
#
#
#
# 6. ROUTES COUNT AND RATE OF INCREASE / DECREASE
# (6.A.) Routes Count
#    - Monitors route count in Route table using NAE Monitor
#    - User enters upper and lower route count threshold as NAE parameters
#      upper_count_threshold and lower_count_threshold respectively
#    - alert if:
#        - Route count is greater than the upper threshold
#    - publish output from:
#        - show ip route summary all-vrfs
#        - show ipv6 route summary all-vrfs
#    - clear alert if:
#        - Route count is less than the lower threshold
#    - alerts:
#            -CRITICAL
#                Alert remains till route count is less than the lower threshold
#                - alert is generated if route count is greater than the upper threshold
#
# (6.B.) Rate of Change of Routes Count
#    - This Sub-Agent sets up an NAE Rule to calculate the rate of change of
#      routes count on the switch.
#      It generates an alert whenever the percentage rate of change of
#      routes count on the switch over a time period defined by the user through
#      the NAE parameter 'time_interval' is over the corresponding
#      threshold value 'rate_of_increase_threshold' or 'rate_of_decrease_threshold'
#      passed as NAE parameter to the NAE Agent.
#
#    - The callback action retrieves the previous value of the resource
#      from a variable stored in the local storage of the NAE Agent,
#      compares it with the current value of the resource obtained by
#      making a REST call to the resource to URI to calculate the
#      difference in the two values. The rate is calculated by dividing the
#      difference by the time interval to obtain the rate of change. It
#      updates the NAE Agent level based on the rate of change.
#
#    - Since the NAE monitor for Rate monitoring does not support
#      monitoring of rate of change of a resource, the rate
#      of change of the resource needs to be monitored using a
#      NAE periodic condition that periodically executes a callback
#      action inside which the rate of change of the resource is
#      calculated mathematically using the current value and previous
#      value of the resource.
#
#    - alert if:
#        - Rate of route count increase percentage exceeds rate_of_increase_threshold
#        - Rate of route count decrease percentage exceeds rate_of_decrease_threshold
#    - clear alert if:
#        - Rate of route count increase or decrease percentage is within the permissible thresholds
#    - alerts:
#        - CRITICAL
#            Alert lasts for 1 cycle for duration of route_count_time_interval


import json
from time import (clock_gettime, CLOCK_PROCESS_CPUTIME_ID)
from datetime import datetime
from ipaddress import (ip_address, IPv4Address, IPv6Address)

Manifest = {
    'Name': 'routing_health_monitor',
    'Description': 'Agent for monitoring routing health',
    'Version': '3.1',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.13.1000',
    'AOSCXPlatformList': ['5420', '6200', '6300', '64xx', '8100', '8320', '8325', '8360', '8400', '9300', '10000']
}

ParameterDefinitions = {
    'cpu_threshold': {
        'Name': 'High CPU Threshold Percentage',
        'Description': 'Notify alert when CPU utilization stays above '
                       'this threshold value for hpe_routing_daemon '
                       'for the mentioned cpu_time_interval.',
        'Type': 'integer',
        'Default': 80
    },
    'cpu_time_interval': {
        'Name': 'Time interval in seconds to consider for CPU utilization',
        'Description': 'Time interval in seconds to consider for '
                       'hpe_routing_daemon CPU utilization',
        'Type': 'integer',
        'Default': 60
    },
    'cpu_cooldown_interval': {
        'Name': 'Time interval in seconds to pause monitoring routing health',
        'Description': 'Time interval in seconds to defer OSPF/BGP health'
                       ' monitoring during high cpu utilization by'
                       ' hpe_routing_daemon. ',
        'Type': 'integer',
        'Default': 300
    },
    'hpe_routing_daemon': {
        'Name': 'System daemon for hpe-routing',
        'Description': 'Routing daemon to monitor for CPU utilization.',
        'Type': 'String',
        'Default': 'hpe-routing'
    },
    'poll_interval': {
        'Name': 'Polling Interval',
        'Description': 'How often to poll for routing health metrics.'
                       ' Measured in seconds. Default is 60',
        'Type': 'integer',
        'Default': 60
    },
    'vrf': {
        'Name': 'VRF',
        'Description': 'VRF to monitor. By default all VRFs are monitored.',
        'Type': 'String',
        'Default': "*"
    },
    'ospf_area': {
        'Name': 'OSPF area',
        'Description': 'OSPF area to monitor. By default all areas are '
                       'monitored.',
        'Type': 'String',
        'Default': "*"
    },
    'ospf_interface': {
        'Name': 'OSPF interface',
        'Description': 'OSPF interfaces to monitor. Interface list can be'
                       ' given separated by comma. By default all interfaces'
                       ' are monitored.',
        'Type': 'String',
        'Default': "*"
    },
    'ospf_state_threshold': {
        'Name': 'OSPF state threshold',
        'Description':
            'Notify alert when OSPF gets stuck in intermediate state beyond '
            'this threshold. Alert will continue for 5 poll cycles',
        'Type': 'integer',
        'Default': 300
    },
    'bgp_neighbor': {
        'Name': 'BGP Neighbor',
        'Description': 'BGP Neighbor to monitor. By default all neighbors are'
                       ' monitored.',
        'Type': 'String',
        'Default': '*'
    },
    'alert_limit': {
        'Name': 'Alert Limit',
        'Description': 'Maximum of alert conditions processed in one poll cycle.'
                       'Minimum is 1, Maximum is 6 and Default is 3',
        'Type': 'integer',
        'Default': 3
    },
    'prefix_list': {
        'Name': 'Prefix list',
        'Description': 'Comma separated list of IPv4 and/or IPv6 prefixes and'
                       'corresponding VRF in format prefix|vrf_name. Maximum of'
                       ' 21 prefixes can be input. Duplicates will be ignored.'
                       'Eg: 1.1.1.0/24|vrf_1,2.2.0.0/16|vrf_2,1::1/128|vrf_3',
        'Type': 'String'
    },
    'upper_count_threshold': {
        'Name': 'Route Count Upper Threshold Value',
        'Description': 'When the number of routes exceeds '
                       'this threshold value, the agent '
                       'will send a Syslog warning and set '
                       'the agent status to critical',
        'Type': 'integer',
        'Default': 10000
    },
    'lower_count_threshold': {
        'Name': 'Route Count Lower Threshold Value',
        'Description': 'When the number of routes are '
                       'lesser than this value, '
                       'the agent will send a Syslog warning '
                       'and set the agent status to normal',
        'Type': 'integer',
        'Default': 9500
    },
    'rate_of_decrease_threshold': {
        'Name': 'Rate of decrease threshold (in percentage)',
        'Description': 'This parameter represents the threshold value above '
                       'which the rate of decrease of routes on the '
                       'switch is supposed to generate an alert.'
                       'The threshold value is calculated as a percentage of'
                       'the routes count at the beginning of the time '
                       'interval during which the rate is calculated.',
        'Type': 'integer',
        'Default': 10
    },
    'rate_of_increase_threshold': {
        'Name': 'Rate of increase threshold (in percentage)',
        'Description': 'This parameter represents the threshold value above '
                       'which the rate of increase of routes on the '
                       'switch is supposed to generate an alert.'
                       'The threshold value is calculated as a percentage of'
                       'the routes count at the beginning of the time '
                       'interval during which the rate is calculated.',
        'Type': 'integer',
        'Default': 10
    },
    'route_count_time_interval': {
        'Name': 'Time interval in minutes for calculating rate of change of routes count',
        'Description': 'This parameter represents the time interval in minutes over '
                       'which the rate of change of routes count is'
                       'to be calculated.',
        'Type': 'integer',
        'Default': 1
    }
}


CPU = "CPU"
COPP = "COPP"
OSPF = "OSPF"
BGP = "BGP"
PREFIX = "PREFIX"
ROUTE_COUNT = "ROUTE_COUNT"
NORMAL = "Normal"
DPRINT = False
URI_PREFIX_GET = "/rest/v10.08/"
URI_PREFIX_GET_V10_13 = "/rest/v10.13/"
URI_PREFIX_MONITOR = "/rest/v1/"
IPV6_MASK_MAX_VALUE = 128
IPV4_MASK_MAX_VALUE = 32
PREFIX_LIST_MAX_LIMIT = 21
DURATION_SECONDS = 60
NUM_CYCLES = 5


def dprint(*args):
    '''this function is used for printing debug logs'''
    if DPRINT:
        print(args)


class AlertManager:
    def __init__(self, agent):
        self.agent = agent
        self.alert_levels_generated_within_poll_per_subagent = {
            'cpu': set(),
            'bgp': set(),
            'copp': set(),
            'ospf': set(),
            'prefix': set(),
            'route_count': set()
        }

    def max_alert(self, levels):
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

    def update_alert_level(self, alert_level, alert_type):
        '''This function updates the alert level in local storage for each
        subagent. It generates a syslog for ospf and bgp subagent when they
        move to stable state'''
        dprint("variables[{0}]: {1} |alert_level: {2}".format(
            alert_type, self.agent.variables[alert_type], alert_level))
        if alert_level != set():
            # either non-normal/ normal/ no change in alert
            if len(alert_level) > 1:
                # if more than 1 alert => non-normal is present => find out max
                self.agent.variables[alert_type] = json.dumps(
                    self.max_alert(alert_level))
            elif AlertLevel.NONE in alert_level:
                # lower alert to normal if prev is non-normal else maintain
                # prev. alert level
                if (json.loads(self.agent.variables[alert_type]) !=
                        AlertLevel.NONE):
                    self.agent.variables[alert_type] = json.dumps(
                        AlertLevel.NONE)
                    if alert_type == 'ospf_alert':
                        dprint('OSPF Agent is now in Stable state')
                        self.agent.action_syslog(
                            Log.WARNING, 'OSPF Agent is now in Stable state')
                        self.agent.clear_alert_description_for_key(OSPF)
                    elif alert_type == 'bgp_alert':
                        dprint('BGP Agent is now in Stable state')
                        self.agent.action_syslog(
                            Log.WARNING, 'BGP Agent is now in Stable state')
                        self.agent.clear_alert_description_for_key(BGP)
                    else:
                        dprint('no log')

                    for sub_agent_key in [CPU, COPP, OSPF, BGP, PREFIX, ROUTE_COUNT]:
                        self.agent.clear_alert_description_for_key(
                            sub_agent_key)
                else:
                    # maintain previous alert level
                    dprint('{}: maintain previous alert level'.format(
                        alert_type))
            else:
                self.agent.variables[alert_type] = json.dumps(
                    next(iter(alert_level)))
        else:
            # maintain previous alert level
            dprint('{}: maintain previous alert level'.format(
                alert_type))

    def routing_health_set_alert(self):
        """
        callers must first set one of these variables:
            self.alert_levels_generated_within_poll_per_subagent = {
                'cpu': set(),
                'bgp': set(),
                'ospf': set(),
                'copp': set(),
                'prefix': set(),
                'route_count': set()
            }
        Then, a subsequent call to this function will set this agents
        AlertLevel to the highest level among the choices.
        """
        dprint("WIP --- routing_health_set_alert")

        # current max
        current = json.loads(self.agent.variables['current_alert'])
        # using a list to show individual levels that are possibly repeated
        alert_levels_generated_within_poll = list()

        dprint("self.agent.variables['current_alert']= {}".format(
            self.agent.variables['current_alert']))
        dprint("alert levels generated within poll per subagent: {0}".format(
            self.alert_levels_generated_within_poll_per_subagent))

        # alert level of ospf will be AlertLevel.NONE when all the ospf are in
        # good state. if ospf nbr goes to bad state, then critical alert will
        # be generated in that cycle, followed by no alert (empty set) in
        # following cycles if the ospf nbr is still in bad state. Therefore,
        # if ospf alert is empty set, then previous poll cycle alert should be
        # maintained in current cycle. if ospf alert is alertLevel.NONE, then
        # if previous alert was not none, it should be brought back to Normal
        # else no-op. if alert level is critical/minor etc, raise to highest.
        for subagent in ['ospf', 'bgp', 'copp', 'prefix', 'cpu', 'route_count']:
            alert_level = self.alert_levels_generated_within_poll_per_subagent[
                subagent]
            alert_type = subagent + '_alert'
            desired_max_subagent = self.max_alert(alert_level)
            if desired_max_subagent == AlertLevel.NONE:
                self.agent.clear_alert_description_for_key(subagent.upper())
            self.update_alert_level(alert_level, alert_type)
            dprint('self.agent.variables[{0}]= {1}'.format(
                alert_type, self.agent.variables[alert_type]))
            alert_levels_generated_within_poll.append(
                json.loads(self.agent.variables[alert_type]))

        # desired max
        desired_max = self.max_alert(alert_levels_generated_within_poll)

        dprint("WIP --- alerts {}: max {}: current {}".format(
            alert_levels_generated_within_poll, desired_max, current))

        if desired_max != current:
            # raise/lower level to current max
            dprint("WIP --- raise to {}".format(desired_max))
            self.agent.set_alert_level(desired_max)
            self.agent.variables['current_alert'] = json.dumps(desired_max)
        # else do nothing


class Agent(NAE):
    """

    Note: several useful variables are defined in NAE which we will reference
    here:

    HTTP_AADDRESS => "http://127.0.0.1:8080"
    AlertLevel.NONE/MINOR/MAJOR/CRITICAL => None, Minor, Major, Critical
    SYSLOG_WARNING => 4 ## rfc-5424 defined number for syslog Warning level
    ActionSyslog()
    ActionCli()
    """

    def __init__(self):

        # dprint("WIP------- Agent:__init__")
        dprint("self.params['prefix_list'].value: {0}".format(
            self.params['prefix_list'].value))
        self.user_prefix_list = None
        if self.params['prefix_list'].value:
            user_prefix_list = self.params['prefix_list'].value.strip(' ').strip(',') \
                .split(',')
            user_prefix_list = [user_prefix.strip()
                                for user_prefix in user_prefix_list]
            # remove duplicate entries from prefix_list
            self.user_prefix_list = list(dict.fromkeys(user_prefix_list))
            dprint("user_prefix_list remove dup:{0}:{1};".format(
                len(self.user_prefix_list), self.user_prefix_list))
            error_msg = self.validate_user_param_prefix_list(
                self.user_prefix_list)
            if error_msg:
                raise ValueError(error_msg)

        alert_limit = self.params['alert_limit'].value
        if alert_limit >= 1 and alert_limit <= 6:
            self.global_alert_limit = alert_limit
        else:
            # raise error
            raise ValueError('Alert limit should be in the range of 1 to 6')
        self.global_alert_limit_cli = 20

        # Persistant variables across every run of this script
        # are stored in self.variables. They must be of type
        # string.
        if 'copp_ucast_dropped_q' not in self.variables.keys():
            self.variables['copp_ucast_dropped_q'] = ""
        if 'copp_ucast_total_dropped' not in self.variables.keys():
            self.variables['copp_ucast_total_dropped'] = "0"
        if 'copp_alert' not in self.variables.keys():
            self.variables['copp_alert'] = json.dumps(AlertLevel.NONE)
        if 'copp_mva_violation' not in self.variables.keys():
            self.variables['copp_mva_violation'] = "None"
        if 'ospf_alert' not in self.variables.keys():
            self.variables['ospf_alert'] = json.dumps(AlertLevel.NONE)
        if 'bgp_alert' not in self.variables.keys():
            self.variables['bgp_alert'] = json.dumps(AlertLevel.NONE)
        if 'cpu_alert' not in self.variables.keys():
            self.variables['cpu_alert'] = json.dumps(AlertLevel.NONE)
        if 'current_alert' not in self.variables.keys():
            self.variables['current_alert'] = json.dumps(AlertLevel.NONE)
        if 'ospf_neighbor_list' not in self.variables.keys():
            self.variables['ospf_neighbor_list'] = json.dumps({})
        if 'ospfv2_debug_packet_cycles_left' not in self.variables.keys():
            self.variables['ospfv2_debug_packet_cycles_left'] = str(0)
        if 'ospfv3_debug_packet_cycles_left' not in self.variables.keys():
            self.variables['ospfv3_debug_packet_cycles_left'] = str(0)
        if 'neighbor_count' not in self.variables.keys():
            self.variables['neighbor_count'] = ""
        if 'bgp_nbr_list' not in self.variables.keys():
            self.variables['bgp_nbr_list'] = json.dumps({})
        if 'bgp_nbr_count' not in self.variables.keys():
            self.variables['bgp_nbr_count'] = str(0)
        if 'bgp_nbr_alert' not in self.variables.keys():
            self.variables['bgp_nbr_alert'] = "false"
        if 'prefix_alert' not in self.variables.keys():
            self.variables['prefix_alert'] = json.dumps(AlertLevel.NONE)
        if 'prefix_instance_list' not in self.variables.keys():
            self.variables['prefix_instance_list'] = json.dumps({})
        if 'monitoring_resume_time' not in self.variables.keys():
            self.variables['monitoring_resume_time'] = str(0)
        if 'route_count_alert' not in self.variables.keys():
            self.variables['route_count_alert'] = json.dumps(AlertLevel.NONE)
        if 'route_count_already_alerted' not in self.variables.keys():
            self.variables['route_count_already_alerted'] = ""

        self.syslogs_per_poll = 0
        self.actioncli_per_poll = 0
        self.addnl_log_cli_excd = False
        self.addnl_log_syslog_excd = False

        self.alm = AlertManager(self)
        self.coppAgent = CoppAgent(self, self.alm)
        self.ospf_agent = OSPFAgent(self, self.alm)
        self.bgp_agent = BGPAgent(self, self.alm)
        self.prefix_agent = PrefixAgent(self, self.alm)
        self.routing_agent = RoutingAgent(self)
        self.route_count_monitor_agent = RouteCountMonitor(self, self.alm)
        self.actions_ospf_bgp = set()

        rule = Rule("Routing Health Rule")
        rule.condition("every {} seconds", [self.params['poll_interval']])
        rule.action(self.routing_heath_poller)
        self.rule = rule
        self.init_alert_description(
            {CPU: NORMAL, COPP: NORMAL, OSPF: NORMAL, BGP: NORMAL, PREFIX: NORMAL, ROUTE_COUNT: NORMAL})

    def routing_heath_poller(self, event):
        '''this function is called every poll cycle to collect OSPF and BGP
           data'''
        # dprint("WIP-------routing_heath_poller", event)
        time0 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        self.coppAgent.copp_handler()
        time1 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
        time2 = 0
        time3 = 0
        time4 = 0
        date_time = datetime.now()
        current_time = int(date_time.timestamp())
        if current_time < int(self.variables['monitoring_resume_time']):
            dprint("Monitoring paused due to high cpu Utilization")
            dprint("Will resume in {} seconds".format(
                int(self.variables['monitoring_resume_time'])-current_time))
        else:
            time2 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
            self.ospf_agent.collect_ospf_data()
            time3 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)
            self.bgp_agent.bgp_handler()
            self.prefix_agent.prefix_handler(self.user_prefix_list)
            self.execute_ospf_bgp_action_cli()
            self.alm.routing_health_set_alert()
            if self.addnl_log_cli_excd or self.addnl_log_syslog_excd:
                ActionSyslog('All the Alerts were not processed due to the '
                             'Alert Limit', severity=SYSLOG_WARNING)
                if self.addnl_log_syslog_excd:
                    dprint("Number of syslogs dropped: {0}".format(
                        self.syslogs_per_poll - self.global_alert_limit))
                if self.addnl_log_cli_excd:
                    dprint("Number of cli dropped: {0}".format(
                        self.actioncli_per_poll - self.global_alert_limit_cli))
            time4 = clock_gettime(CLOCK_PROCESS_CPUTIME_ID)

        dprint("Time Report, COPP : {} seconds".format(time1-time0))
        dprint("Time Report, OSPF : {} seconds".format(time3-time2))
        dprint("Time Report, BGP  : {} seconds".format(time4-time3))
        dprint("Time Report, Total: {} seconds".format(
            time1-time0+time4-time2))

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
        elif self.syslogs_per_poll == self.global_alert_limit:
            self.syslogs_per_poll += 1
            self.addnl_log_syslog_excd = True
        elif self.syslogs_per_poll > self.global_alert_limit:
            self.syslogs_per_poll += 1

    def action_cli(self, cmds):
        '''this function is a wrapper for ActionCLI API'''
        if self.actioncli_per_poll < self.global_alert_limit_cli:
            ActionCLI(cmds)
            self.actioncli_per_poll += 1
        elif self.actioncli_per_poll == self.global_alert_limit_cli:
            self.actioncli_per_poll += 1
            self.addnl_log_cli_excd = True
        elif self.actioncli_per_poll > self.global_alert_limit_cli:
            self.actioncli_per_poll += 1

    def action_shell(self, script):
        '''this function is a wrapper for ActionShell API'''
        ActionShell(script)

    def fetch_url(self, url):
        '''this function is used to fetch data for given REST url. Retries GET
           request if OVSDB hasn't been populated'''
        response = None
        try:
            response = self.get_rest_request_json(
                url, retry=2, wait_between_retries=1)
        except NAEException as e:
            self.logger.error("system error while collecting stat"
                              "error: {0}| url: {1}".format(e, url))
        return response

    def json_dumps_wrapper(self, value):
        try:
            json.dumps(value)
        except Exception:
            self.logger.error(
                "system error while json dumps of {0}".format(value))

    def json_loads_wrapper(self, value):
        result = None
        try:
            result = json.loads(value)
        except Exception:
            self.logger.error(
                "system error while json loads of {0}".format(value))
        return result

    def action_high_cpu(self, event):
        '''This function executes alert for High CPU utilization by
           specified daemon'''
        dprint("High CPU Utilization")
        self.alm.alert_levels_generated_within_poll_per_subagent['cpu'].add(
            AlertLevel.CRITICAL)
        self.alm.routing_health_set_alert()
        message = 'High CPU utilization by {} daemon'.format(
            self.params['hpe_routing_daemon'].value)
        self.action_syslog(Log.WARNING, message)
        self.set_alert_description_for_key(CPU, message)
        self.action_cli(
            'show system resource-utilization daemon {}'.format(self.params['hpe_routing_daemon'].value))
        date_time = datetime.now()
        current_time = int(date_time.timestamp())
        self.variables['monitoring_resume_time'] = str(
            current_time + self.params['cpu_cooldown_interval'].value)

    def action_normal_cpu(self, event):
        '''This function brings down alert to normal when daemon cpu is
         back to normal'''
        dprint('Normal CPU Utilization')
        self.alm.alert_levels_generated_within_poll_per_subagent['cpu'].add(
            AlertLevel.NONE)
        self.alm.routing_health_set_alert()
        self.clear_alert_description_for_key(CPU)

    def route_action_critical(self, event):
        dprint("route_count_action_critical")
        self.variables['route_count_already_alerted'] = "true"
        self.alm.alert_levels_generated_within_poll_per_subagent['route_count'].add(
            AlertLevel.CRITICAL)
        self.alm.routing_health_set_alert()
        self.action_syslog(Log.WARNING, 'Current route count is {0} which exceeds the upper threshold value of {1}'.format(
            event['value'], self.params['upper_count_threshold']))
        self.set_alert_description_for_key(ROUTE_COUNT, "{0} exceeds the upper threshold of {1}".format(
            event['value'], self.params['upper_count_threshold']))
        self.action_cli('show ip route summary all-vrfs')
        self.action_cli('show ipv6 route summary all-vrfs')

    def route_action_normal(self, event):
        dprint("route_count_action_normal")
        self.variables['route_count_already_alerted'] = ""
        self.alm.alert_levels_generated_within_poll_per_subagent['route_count'].add(
            AlertLevel.NONE)
        self.alm.routing_health_set_alert()
        self.action_syslog(Log.WARNING, 'Current route count is {0} which is below the lower threshold value of {1}'.format(
            event['value'], self.params['lower_count_threshold']))
        self.clear_alert_description_for_key(ROUTE_COUNT)

    def execute_ospf_bgp_action_cli(self):
        '''this function is used to execute action CLIs for OSPF and BGP'''
        actions = self.actions_ospf_bgp
        cmds_list = sorted(actions)
        dprint("cmds_list= {0}".format(cmds_list))
        for cmd in cmds_list:
            self.action_cli(cmd)

    def validate_user_param_prefix_list(self, user_prefix_list):
        for ele in user_prefix_list:
            if not ele:
                error_msg = 'Parameter prefix_list is invalid.'
                self.logger.error(error_msg)
                return error_msg
            if '|' not in ele:
                error_msg = 'Parameter prefix_list is invalid. Please enter each prefix in the format prefix|vrf'
                self.logger.error(error_msg)
                return error_msg
            prefix, vrf = ele.split('|')
            if not prefix:
                error_msg = 'Parameter prefix_list is invalid. Prefix is missing'
                self.logger.error(error_msg)
                return error_msg
            if '/' not in prefix:
                error_msg = 'Parameter prefix_list is invalid. Invalid Prefix format'
                self.logger.error(error_msg)
                return error_msg
            if not vrf:
                error_msg = 'Parameter prefix_list is invalid. VRF is missing for Prefix {0}'.format(
                    prefix)
                self.logger.error(error_msg)
                return error_msg
            ip, mask = prefix.split('/')
            if not ip:
                error_msg = 'Parameter prefix_list is invalid. Prefix {0} is invalid'.format(
                    prefix)
                self.logger.error(error_msg)
                return error_msg
            if not mask:
                error_msg = 'Parameter prefix_list is invalid. Prefix {0} does not have mask'.format(
                    prefix)
                self.logger.error(error_msg)
                return error_msg
            try:
                ip_address(ip)
            except ValueError:
                error_msg = 'Parameter prefix_list has invalid IP address: {0}'.format(
                    prefix)
                self.logger.error(error_msg)
                return error_msg
            error_msg = 'Parameter prefix_list has invalid subnet mask {0} for prefix: {1}'.format(
                mask, prefix)
            if type(ip_address(ip)) is IPv6Address:
                if 0 <= int(mask) <= IPV6_MASK_MAX_VALUE:
                    continue
                else:
                    self.logger.error(error_msg)
                    return error_msg
            elif type(ip_address(ip)) is IPv4Address:
                if 0 <= int(mask) <= IPV4_MASK_MAX_VALUE:
                    continue
                else:
                    self.logger.error(error_msg)
                    return error_msg
        if len(user_prefix_list) > PREFIX_LIST_MAX_LIMIT:
            error_msg = 'Parameter prefix_list contains {0} prefixes. ' \
                'Maximum number of prefixes that can be monitored is {1}.' \
                .format(len(user_prefix_list), PREFIX_LIST_MAX_LIMIT)
            self.logger.error(error_msg)
            return error_msg

    def calculate_rate_of_change_of_routes_count_agent(self, event):
        dprint("Enter calculate_rate_of_change_of_routes_count_agent")
        self.route_count_monitor_agent.calculate_rate_of_change_of_routes_count()


class RoutingAgent:
    '''This class defines monitor for daemon CPU utilization'''

    def __init__(self, agent):
        self.agent = agent
        cpu_uri_var = 'cpu_monitor'
        cpu_uri = URI_PREFIX_MONITOR + 'system/subsystems/*/*/daemons/{}?' \
            'attributes=resource_utilization.cpu&filter=name:{}'
        cpu_monitor = Monitor(
            cpu_uri,
            '(CPU/Memory utilization in %)',
            [self.agent.params['hpe_routing_daemon'],
             self.agent.params['hpe_routing_daemon']])
        setattr(self.agent, cpu_uri_var, cpu_monitor)

        cpu_rule_var = 'cpu_rule'
        cpu_rule = Rule('High CPU utilization by {}', [
                        self.agent.params['hpe_routing_daemon']])
        cpu_rule.condition(
            '{} >= {} for {} seconds',
            [cpu_monitor,
             self.agent.params['cpu_threshold'],
             self.agent.params['cpu_time_interval']])
        cpu_rule.action(self.agent.action_high_cpu)
        cpu_rule.clear_condition('{} < {} for {} seconds',
                                 [cpu_monitor,
                                  self.agent.params['cpu_threshold'],
                                  self.agent.params['cpu_time_interval']])
        cpu_rule.clear_action(self.agent.action_normal_cpu)
        setattr(self.agent, cpu_rule_var, cpu_rule)


class RouteCountMonitor:

    def __init__(self, agent, alm):
        dprint("RouteCountMonitor __init__")
        self.agent = agent
        self.alm = alm
        route_count_uri_var = 'route_count_monitor'
        uri = URI_PREFIX_MONITOR + 'system/vrfs/*/routes?count&filter=selected:true'

        # REST Encodings:
        # %2A is *
        # %3A is :
        self.RATE_URI = HTTP_ADDRESS + URI_PREFIX_GET_V10_13 + \
            'system/vrfs/%2A/routes?filter=selected%3Atrue&count=true'

        route_count_monitor = Monitor(Sum(uri), 'Route Count')
        setattr(self.agent, route_count_uri_var, route_count_monitor)

        # route_count
        route_count_rule_var = 'route_count_rule'
        route_count_rule = Rule('Route count rule')
        route_count_rule.condition('{} > {}',
                                   [route_count_monitor,
                                    self.agent.params['upper_count_threshold']])
        route_count_rule.action(self.agent.route_action_critical)

        route_count_rule.clear_condition('{} < {}',
                                         [route_count_monitor,
                                          self.agent.params['lower_count_threshold']])
        route_count_rule.clear_action(self.agent.route_action_normal)
        setattr(self.agent, route_count_rule_var, route_count_rule)

        # Store the initial routes count so that it can be used in
        # calculating the rate of change of routes count.
        self.agent.variables['resource_count_value'] = str(
            self.get_resource_count())

        # Setup the NAE Script Rules.
        self.setup_agent_rule()

    def setup_agent_rule(self):
        """
        Creates a NAE Rule that contains a NAE Periodic Condition that
        executes a NAE callback action that retrieves the current value of
        the routes count on the switch over the the time interval
        passed as parameter 'time_interval' to the NAE agent. If the value
        is over the corresponding threshold value 'rate_of_increase_threshold'
        or 'rate_of_decrease_threshold' passed as parameter to the NAE agent,
        an alert is generated.

        Since the NAE monitor for Rate monitoring does not support
        monitoring of rate of change of a resource, the rate
        of change of the resource needs to be monitored using a
        NAE periodic condition that periodically executes a callback
        action inside which the rate of change of the resource is
        calculated mathematically using the current value and previous
        value of the resource.
        """
        dprint("Enter setup_agent_rule")
        rule = Rule(
            'Rate of change of routes count on the switch')
        rule.condition('every {} minutes', [
                       self.agent.params['route_count_time_interval']])
        rule.action(self.agent.calculate_rate_of_change_of_routes_count_agent)

        setattr(self.agent, 'rate_of_change_of_routes_count_rule', rule)

    def route_count_rate_set_alert_level(self, level):
        '''function used to set alert level'''
        dprint("Enter route_count_rate_set_alert_level")
        self.alm.alert_levels_generated_within_poll_per_subagent[
            'route_count'].add(level)

    def calculate_rate_of_change_of_routes_count(self):
        """
        Callback action that is executed periodically by the NAE script
        periodic condition.

        The callback action retrieves the previous value of the resource
        from a variable stored in the local storage of the NAE Agent,
        compares it with the current value of the resource obtained by
        making a REST call to the resource to URI to calculate the
        difference in the two values. The rate is calculated by dividing the
        difference by the time interval to obtain the rate of change. It
        updates the NAE Agent level based on the rate of change.
        """
        dprint("calculate_change_rate")
        previous_count_value = int(
            self.agent.variables['resource_count_value'])
        current_count_value = self.get_resource_count()

        count_change = previous_count_value - current_count_value

        change_rate = (count_change / self.agent.params[
            'route_count_time_interval'].value)

        self.agent.variables['resource_count_value'] = str(current_count_value)

        self.update_alert_level(change_rate, previous_count_value)

    def update_alert_level(self, change_rate, previous_count_value):
        """
        Updates the Agent Alert Level based on the rate of change of the
        resource.

        If the rate of change is not within the threshold values , the NAE Agent
        Alert Level is set to Critical, otherwise it is set to Normal
        :param change_rate: Rate of change (increase/decrease) of the resource.
        :param previous_count_value: Count of the resource at the beginning
        of the time interval during which the rate of change is calculated.
        """
        dprint("Enter update_alert_level")
        dprint("route_count_already_alerted: {0}".format(
            self.agent.variables['route_count_already_alerted']))
        if change_rate == 0:
            dprint("no route count change")
            if not self.agent.variables['route_count_already_alerted']:
                dprint("route count rate raise to none")
                self.route_count_rate_set_alert_level(AlertLevel.NONE)
                self.alm.routing_health_set_alert()
            return

        if previous_count_value == 0:
            previous_count_value += 1

        change_percentage = round(
            (change_rate/previous_count_value * 100), 2)

        decrease_threshold = self.agent.params['rate_of_decrease_threshold'].value
        increase_threshold = self.agent.params['rate_of_increase_threshold'].value

        if change_percentage > 0 and change_percentage > decrease_threshold:
            alert_type = "decrease"
            threshold = decrease_threshold
        elif change_percentage < 0 and abs(change_percentage) > increase_threshold:
            alert_type = "increase"
            threshold = increase_threshold
            change_percentage = abs(change_percentage)
        else:
            dprint("route count rate change not exceeding thresholds")
            if not self.agent.variables['route_count_already_alerted']:
                dprint("route count rate raise to none")
                self.route_count_rate_set_alert_level(AlertLevel.NONE)
                self.alm.routing_health_set_alert()
            return

        message = 'The rate of {0} of the routes on ' \
                  'the switch which is {1}% is greater than the ' \
                  'threshold value ' \
                  'of {2}%'.format(alert_type, change_percentage, threshold)
        self.agent.logger.info(message)
        self.route_count_rate_set_alert_level(AlertLevel.CRITICAL)
        description = "High rate of {0} of routes".format(alert_type)
        self.agent.set_alert_description_for_key(ROUTE_COUNT, description)
        self.alm.routing_health_set_alert()
        self.agent.action_syslog(Log.WARNING, message)
        self.agent.action_cli('show ip route summary all-vrfs')
        self.agent.action_cli('show ipv6 route summary all-vrfs')

    def get_resource_count(self):
        """
        Get the count of the resource by making a HTTP GET operation to the
        REST URI for the resource.
        :return: count: Number of entries in the resource
        """
        count = 0
        r = self.agent.fetch_url(self.RATE_URI)
        if not r:
            self.logger.error(
                "Error while making REST call to URI {}".format(self.RATE_URI))
        else:
            count = r["count"]
        dprint("resource_count: {}".format(count))
        return count


class CoppAgent:

    COPP_QDEPTH_MAX = 100
    COPP_STATS_URL = HTTP_ADDRESS + \
        URI_PREFIX_GET + 'system?attributes=copp_statistics'
    INCOMPLETE_ROUTES_HOSTS_SCRIPT = """
#!/usr/bin/env bash

# find incomplete routes and print prefix, type, from, dp_state
echo "Incomplete Routes in Route Table"
echo "a route in disable state is a problem"
echo "a route in unresolved state is a transitory problem which will likely get fixed by ARP/IPV6_ND in a moment"
echo "a route with empty or incomplete state is a problem"
echo "    except for rotues with from=local, these can be incomplete"
echo "    prefix     from   dp_state"
echo "  ----------   ----- ------------"
ovsdb-client dump Route -f json | \
jq '.[0] .data[] | select(.[4] == "disable" or .[4] == "unresolved" or .[4] == ["set", []]) | "\(.[10]) \(.[6]) \(.[4])"'

# find incomplete neighbors and print address_family, dp_state, from, ip_address, l3_destination
echo "Incomplete Neighbors in Neighbor Table"
echo "a neighbor in disable state is a problem"
echo "AF     State      from    IP Address"
echo "----  --------- -------- -----------"
ovsdb-client dump Route -f json | \
jq '.[0] .data[] | select(.[3] == "disable" or .[3] == ["set", []]) | "\(.[1]) \(.[2]) \(.[4]) \(.[6])"'
"""
    L3RESMGR_CAP_SCRIPT = """
#!/usr/bin/env bash

echo "Hardware view of capacities"
ovs-appctl -t l3-resmgrd capacities/show_all
"""

    SOFTWARE_ONLY_ROUTES_SWNS_SCRIPT = """
echo "a search of routes found in software but not in hardware"
echo "this should be vary rare, but if found, it is a problem"
ip netns exec swns  ip ro list | grep -v proto
if [ $? -eq 1 ]; then echo "---No such routes found---"; else exit $? ; fi
"""
    # tuple: ordered and unchangeable.
    copp_mva_violations = (
        "None",
        "One_Minute",
        "Five_Minute",
        "Ten_Minute"
    )

    def __init__(self, agent, alm):
        # dprint("WIP------- CoppAgent:__init__")
        self.agent = agent
        self.alm = alm

    def copp_handler(self):
        # dprint("WIP------- copp_handler")
        self.copp_collect_stats()
        self.copp_analyze_stats()

    def copp_collect_stats(self):
        dprint("WIP------- copp_collect_stats")

        ucast_drop_q = \
            self.copp_q_to_list(self.agent.variables['copp_ucast_dropped_q'])

        ucast_dropped = ''
        ucast_dropped = ''
        url = self.COPP_STATS_URL
        try:
            r_map = self.agent.get_rest_request_json(url)
            # cops stats uri reply is json:
            #   {'copp_stats': {'statname': stat}}
            ucast_name = 'unresolved_ip_unicast_packets_dropped'
            ucast_dropped = r_map['copp_statistics'][ucast_name]
        except Exception as e:
            self.logger.error("system error {} While collecting copp stat {}"
                              .format(e, url))
            return None

        dprint("WIP------- copp_collect_stats 10")
        # format ucast dropped stats
        total_ucast_dropped = \
            int(self.agent.variables['copp_ucast_total_dropped'])
        if len(ucast_drop_q) > 0:
            increment = ucast_dropped - total_ucast_dropped
        else:
            increment = ucast_dropped

        if increment < 0:
            # Assume a clear copp stats happened.
            # start the sample series over from here.

            # erase old queued data
            ucast_drop_q = []
            # let increment be the current sample - 0
            increment = ucast_dropped

            # Note about alert-level... we purposefully leave it alone here.
            # The math judging an alert-level from the rate(s) of
            # copp stat unresolved_ip_unicast_packets_dropped will work out
            # naturally even if we restart the sample series from here.
            self.agent.logger.info(
                'NAE Agent {}: '
                'COPP stat {} went down, not up. '
                'Perhpas someone cleared copp stats. '
                'Taking this sample as new base value.'
                .format(self.agent.name, ucast_name)
            )
            self.agent.action_syslog(
                Log.INFO,
                'NAE Agent {}: '
                'Detected decrease in COPP statistic {}. Resetting '
                'moving average data'
                .format(self.agent.name, ucast_name)
            )
            self.agent.set_alert_description_for_key(
                COPP, 'Detected decrease in COPP statistic {}'.format(ucast_name))

        total_ucast_dropped = ucast_dropped
        self.copp_q_append(ucast_drop_q, increment)
        # dprint("WIP---- new droppQ: ", ucast_drop_q)

        self.agent.variables['copp_ucast_dropped_q'] = \
            self.copp_q_to_str(ucast_drop_q)
        self.agent.variables['copp_ucast_total_dropped'] = \
            str(total_ucast_dropped)

        return None

    def copp_publish_alert_info(self):
        self.agent.action_cli("show copp-policy statistics non-zero")
        self.agent.action_cli("show ip route summary  all-vrfs")
        self.agent.action_shell(self.INCOMPLETE_ROUTES_HOSTS_SCRIPT)
        self.agent.action_shell(self.L3RESMGR_CAP_SCRIPT)
        self.agent.action_shell(self.SOFTWARE_ONLY_ROUTES_SWNS_SCRIPT)

    def copp_moving_average(self, numbers, window_size):
        """
        take a window_size slice from the tail of numbers and calculate the
        average.

        Some corner cases:
        1. if len(numbers) is less than window_size, give up and return 0
        2. ignore the first element of numbers, based on the idea that the
           first sample of copp stats will have no previous diff and may be
           seemingly over-large.
        """

        i = len(numbers)
        if i <= window_size:
            return 0

        tail_numbers = numbers[-window_size:]
        window_average = sum(tail_numbers) / window_size
        return window_average

    def copp_analyze_stats(self):
        """
        small alert if 1 minute pass mva crosses above copp_max_burst_packets
        medium alert if 5 minute pass mva crosses above copp_max_burst_packets
        large alert if 10 minute pass mva crosses above copp_max_burst_packets

        alert if 5 minute drop mva exceeds copp_max_burst_packets/2
        """
        dprint("WIP------- copp_analyze_stats")
        ucast_stats = self.copp_q_to_list(
            self.agent.variables['copp_ucast_dropped_q'])

        self.copp_alert_on_stats(ucast_stats, "unresolved ip unicast")

    def copp_alert_on_stats(self, stats, stats_name):
        """
        Evaluate a set of copp stats. Determine their 1,5,10 minute moving
        averages. Decide if alert level should be raised or lowered depending
        on how 1,5,10 mvas have changed.
        """
        dprint("WIP------- copp_alert_on_stats")
        dprint("WIP------- {} stats: ".format(stats_name), stats)

        # rate in pps
        max_rate = self.copp_get_system_max_rate()
        pollHz = self.agent.params['poll_interval'].value / DURATION_SECONDS
        one_min_win_size = int(round(1 / pollHz))
        five_min_win_size = int(round(5 / pollHz))
        ten_min_win_size = int(round(10 / pollHz))

        mva_one = self.copp_moving_average(stats, one_min_win_size)
        mva_five = self.copp_moving_average(stats, five_min_win_size)
        mva_ten = self.copp_moving_average(stats, ten_min_win_size)

        upper_threshold = max_rate * .10
        lower_threshold = max_rate * .01
        u_thresh_int = int(round(upper_threshold))
        l_thresh_int = int(round(lower_threshold))
        dprint("WIP---- oneMinAvg {}, fiveMinAvg {}, tenMinAvg {} \
            ".format(mva_one, mva_five, mva_ten))
        dprint("WIP---- max_rate {}, upper {}, lower {}\
            ".format(max_rate, upper_threshold, lower_threshold))

        alert = False
        # raise alert if drop rate above 10%
        mva_violation_level = \
            self.copp_mva_violations.index(
                self.agent.variables['copp_mva_violation'])
        if mva_one > u_thresh_int:
            if mva_violation_level < \
                    self.copp_mva_violations.index("One_Minute"):
                message = "COPP drop rate for {} one minute moving average {} went above {}".format(
                    stats_name, mva_one, u_thresh_int)
                self.agent.action_syslog(Log.INFO, message)
                self.agent.set_alert_description_for_key(COPP, message)
                alert = AlertLevel.MINOR
                self.agent.variables['copp_mva_violation'] = "One_Minute"
                mva_violation_level = \
                    self.copp_mva_violations.index("One_Minute")

        if mva_five > u_thresh_int:
            if mva_violation_level < \
                    self.copp_mva_violations.index("Five_Minute"):
                message = "COPP drop rate for {} five minute moving average {} went above {}".format(
                    stats_name, mva_five, u_thresh_int)
                self.agent.action_syslog(Log.INFO, message)
                self.agent.set_alert_description_for_key(COPP, message)
                alert = AlertLevel.MAJOR
                self.agent.variables['copp_mva_violation'] = "Five_Minute"
                mva_violation_level = \
                    self.copp_mva_violations.index("Five_Minute")

        if mva_ten > u_thresh_int:
            if mva_violation_level < \
                    self.copp_mva_violations.index("Ten_Minute"):
                message = "COPP drop rate for {} ten minute moving average {} went above {}".format(
                    stats_name, mva_ten, u_thresh_int)
                self.agent.action_syslog(Log.WARNING, message)
                self.agent.set_alert_description_for_key(COPP, message)
                alert = AlertLevel.CRITICAL
                self.agent.variables['copp_mva_violation'] = "Ten_Minute"
                mva_violation_level = \
                    self.copp_mva_violations.index("Ten_Minute")

        # If drop rate went above 10%, increase alert level for agent
        if alert:
            self.copp_alert_level_vote_up(alert)
            alert = False

        # lower alert if drop rate below 1%
        # Strategy for lowering volation level:
        #   if curent mvl == test_level, then lower level one notch
        if mva_one < l_thresh_int:
            if mva_violation_level == \
                    self.copp_mva_violations.index("One_Minute"):
                self.agent.action_syslog(Log.INFO,
                                         "COPP drop rate for {} one minute moving average {} went "
                                         "below {}".format(
                                             stats_name, mva_one, l_thresh_int))
                self.agent.clear_alert_description_for_key(COPP)
                alert = AlertLevel.NONE
                self.agent.variables['copp_mva_violation'] = "None"
                mva_violation_level = \
                    self.copp_mva_violations.index("None")

        if mva_five < l_thresh_int:
            if mva_violation_level == \
                    self.copp_mva_violations.index("Five_Minute"):
                message = "COPP drop rate for {} five minute moving average {} went below {}".format(
                    stats_name, mva_five, l_thresh_int)
                self.agent.action_syslog(Log.INFO, message)
                self.agent.set_alert_description_for_key(COPP, message)
                alert = AlertLevel.MINOR
                self.agent.variables['copp_mva_violation'] = "One_Minute"
                mva_violation_level = \
                    self.copp_mva_violations.index("One_Minute")

        if mva_ten < l_thresh_int:
            if mva_violation_level == \
                    self.copp_mva_violations.index("Ten_Minute"):
                message = "COPP drop rate for {} ten minute moving average {} went below {}".format(
                    stats_name, mva_ten, l_thresh_int)
                self.agent.action_syslog(Log.INFO, message)
                self.agent.set_alert_description_for_key(COPP, message)
                alert = AlertLevel.MAJOR
                self.agent.variables['copp_mva_violation'] = "Five_Minute"
                mva_violation_level = \
                    self.copp_mva_violations.index("Five_Minute")

        # If drop rate went below 1%, lower alert level for agent
        if alert:
            self.copp_alert_level_vote_down(alert)

    def copp_get_system_max_rate(self):
        """
        sends rest api query to discover copp_max_rate_pps or
        copp_max_rate_kbps from system capacities.

        returns copp_max_rate_pps or copp_max_rate_kbps as an int
        (or 0 if the query fails)
        """
        url = HTTP_ADDRESS + URI_PREFIX_GET + 'system?attributes=capacities'

        try:
            r_map = self.agent.get_rest_request_json(url)
            if 'copp_max_rate_pps' in r_map['capacities']:
                copp_capacity = r_map['capacities']['copp_max_rate_pps']
            elif 'copp_max_rate_kbps' in r_map['capacities']:
                copp_capacity = r_map['capacities']['copp_max_rate_kbps']
            else:
                raise Exception("Could not find 'copp_max_rate_pps' or "
                                "'copp_max_rate_kbps' in capacities")
            return copp_capacity
        except Exception as e:
            self.logger.error(
                "system error while collecting system capacities: {}\
                    ".format(str(e)))

        return 0

    def copp_get_system_min_link_speed(self):
        """
        Searches all current interfaces on the system. Finds the link with the
        minimum linkSpeed in bps. Ignores interfaces with linkspeed=0.
        returns the min LinkSpeed or 0 if error.
        """
        # dprint("WIP ----- copp_get_system_min_link_speed")
        url = HTTP_ADDRESS + URI_PREFIX_GET + 'system/interfaces/*?attributes=link_speed'
        min_speed = 0
        try:
            r_map = self.agent.get_rest_request_json(url)
            speeds = [s['link_speed'] for s in r_map if s['link_speed'] > 0]
            if speeds is not None and len(speeds) > 0:
                min_speed = min(speeds)
        except Exception as e:
            self.logger.error(
                "system error while collecting link speeds: {}".format(str(e)))
        return min_speed

    def copp_alert_level_vote_up(self, desired):
        """
        Evaluates if alert level of COPP area should be raised. Considers
        desired alert level vs current alert level.
        Will change copp alert level if desired is > current.

        param desired: caller passes in any alertleve they wish to set. Must be
                       of type AlertLevel
        """

        current = json.loads(self.agent.variables['current_alert'])

        # dprint("WIP ----- copp_alert_level_vote_up from: \
        #     ", current, " to: ", desired)
        if desired is None:
            desired = AlertLevel.NONE

        if current == desired:
            return

        if current == AlertLevel.NONE:
            if desired == AlertLevel.MINOR or \
               desired == AlertLevel.MAJOR or \
               desired == AlertLevel.CRITICAL:
                # dprint("WIP ----- copp_alert_level_vote_up 2 from: \
                #       ", current, " to: ",  desired)
                self.copp_set_alert_level(desired)

        if current == AlertLevel.MINOR:
            if desired == AlertLevel.MAJOR or desired == AlertLevel.CRITICAL:
                # dprint("WIP ----- copp_alert_level_vote_up 3 from: \
                #     ", current, " to: ",  desired)
                self.copp_set_alert_level(desired)

        if current == AlertLevel.MAJOR:
            if desired == AlertLevel.CRITICAL:
                # dprint("WIP ----- copp_alert_level_vote_up 4 from: \
                #     ", current, " to: ",  desired)
                self.copp_set_alert_level(desired)

    def copp_alert_level_vote_down(self, desired):
        """
        Evaluates if alert level of COPP area should be lowered. Considers
        desired alert level vs current alert level.
        Will change copp alert level if desired is < current.

        param desired: caller passes in any alertlevel they wish to set. Must
                       be of type AlertLevel
        """
        current = json.loads(self.agent.variables['current_alert'])

        if current == AlertLevel.NONE:
            return

        if current == desired:
            return

        if desired is None or desired == AlertLevel.NONE:
            # dprint("WIP ----- copp_alert_level_vote_down 1 from: \
            # ", current, " to: ",  desired)
            self.agent.clear_alert_description_for_key(COPP)
            self.copp_set_alert_level(AlertLevel.NONE)
            return

        if current == AlertLevel.CRITICAL:
            if desired == AlertLevel.MINOR or desired == AlertLevel.MAJOR:
                # dprint("WIP ----- copp_alert_level_vote_down 2 from: \
                #     ", current, " to: ",  desired)
                self.copp_set_alert_level(desired)

        if current == AlertLevel.MAJOR:
            if desired == AlertLevel.MINOR:
                # dprint("WIP ----- copp_alert_level_vote_down 3 from: \
                #     ", current, " to: ",  desired)
                self.copp_set_alert_level(desired)

        if current == AlertLevel.MINOR:
            # dprint("WIP ----- copp_alert_level_vote_down 4 from: \
            #     ", current, " to: ",  desired)
            self.copp_set_alert_level(desired)

    def copp_q_to_list(self, q_str):
        """
        given a copp_q string, return a copp Q list.

        param q_str      A copp stats queue string is the json representation
                        of a list of (upto)  COPP_QDEPTH_MAX positive integers.
                        "[1, 2, 42, 567,...]"

        returns  python list of integers
                 [1, 2, 42, 567,...]
        """
        if q_str is None:
            return []
        if q_str == "":
            return []
        return json.loads(q_str)

    def copp_q_to_str(self, q_list):
        """
        given a pyton list of ints, return a copp Q string.

        param q_list a python list of ints. If the list is longer than
                    COPP_QDEPTH_MAX, it will be trimmed to only the tail
                    entries which fit in COPP_QDEPTH_MAX.
                    It only makes sense to keep positive integers in a copp
                    stats Q. But this function does not impose that sanity
                    checking. Caller should manage that.

        returns     (json format) string of the python list of ints.
                    "[1, 2, 42, 567,...]"
        """
        if q_list is None:
            return "[]"

        if len(q_list) > self.COPP_QDEPTH_MAX:
            q_list = q_list[-self.COPP_QDEPTH_MAX:]

        return json.dumps(q_list)

    def copp_q_append(self, q_list, q_item):
        """
        given a copp stats q_list and q_item, append q_item to q_list. If
        len(q_list) exceeds COPP_QDEPTH_MAX, trim qlist to be only the
        tail entries  (most recent) that fit.

        param q_list (in/out) a copp queue which is a pyhon list of postive
                             integers. note: q_list will be modified.
        param q_item (in)    a positive integer to be tail appended to q_list

        returns None. May raise exceptions.
        """
        if q_list is None:
            self.agent.logger.info("q_list is None")
            raise Exception("q_list may not be None")
        if not isinstance(q_list, list):
            self.agent.logger.info("q_list is not a list")
            raise Exception("q_list must be a python list")
        if not isinstance(q_item, int):
            self.agent.logger.info("q_item is not an int")
            raise Exception("q_item must be an integer")
        if q_item < 0:
            raise Exception("q_item must be positive. not {}".format(q_item))

        q_list.append(q_item)
        if len(q_list) > self.COPP_QDEPTH_MAX:
            q_list = q_list[-self.COPP_QDEPTH_MAX:]

        return None

    def copp_set_alert_level(self, level):
        self.alm.alert_levels_generated_within_poll_per_subagent['copp'].add(
            level)
        self.copp_publish_alert_info()


class OSPFAgent:
    '''This class periodically collects OSPF data using REST query and
     Analyzes it'''

    def __init__(self, agent, alm):
        self.agent = agent
        self.alm = alm
        self.ospf_alert_on_this_cycle = False
        self.ospf_neighbor_not_in_stable_state = False
        self.ospfv2_url_list = self.get_url_list(
            self.agent.params['ospf_interface'].value, '')
        self.ospfv3_url_list = self.get_url_list(
            self.agent.params['ospf_interface'].value, 'v3')
        self.action = set()
        # self.ospfv2_base_url = HTTP_ADDRESS + \
        #     URI_PREFIX_GET + 'system/vrfs/' + \
        #     self.agent.params['vrf'].value + \
        #     '/ospf_routers/*/areas/' + \
        #     self.agent.params['ospf_area'].value + \
        #     '/ospf_interfaces/' + \
        #     (self.agent.params['ospf_interface'].value).replace(
        #         "/", "%2F") + '/ospf_neighbors?depth=2'

        self.ospfv3_base_url = HTTP_ADDRESS + \
            URI_PREFIX_GET + 'system/vrfs/' + \
            self.agent.params['vrf'].value + \
            '/ospfv3_routers/*/areas/' + \
            self.agent.params['ospf_area'].value + \
            '/ospf_interfaces/' + \
            (self.agent.params['ospf_interface'].value).replace(
                "/", "%2F") + '/ospf_neighbors?depth=2'

    def get_url_list(self, interface_str, version):
        '''Function to form the URL strings to be queried'''
        url_list = []
        for interface in interface_str.split(","):
            url = HTTP_ADDRESS + \
                URI_PREFIX_GET + 'system/vrfs/' + \
                self.agent.params['vrf'].value + \
                '/ospf' + version + '_routers/*/areas/' + \
                self.agent.params['ospf_area'].value + \
                '/ospf_interfaces/' + \
                (interface).replace(
                    "/", "%2F") + '/ospf_neighbors?depth=2'
            url_list.append(url)
        return url_list

    # Function to check if ospf is supported before trying to handle data
    def check_ospfv2_supported(self):
        url = (HTTP_ADDRESS + URI_PREFIX_GET + 'system/vrfs/' +
               self.agent.params['vrf'].value + '?depth=2')
        response = self.agent.fetch_url(url)
        if ('"ospf_routers"' in str(response) or
                "'ospf_routers'" in str(response)):
            return "true"
        else:
            self.agent.logger.debug(
                "OSPF is not supported on this platform, script will not "
                "attempt to fetch OSPF data"
            )
            return "false"

    # Function to check if ospfv3 is supported before trying to handle data
    def check_ospfv3_supported(self):
        url = (HTTP_ADDRESS + URI_PREFIX_GET + 'system/vrfs/' +
               self.agent.params['vrf'].value + '?depth=2')
        response = self.agent.fetch_url(url)
        if ('"ospfv3_routers"' in str(response) or
                "'ospfv3_routers'" in str(response)):
            return "true"
        else:
            self.agent.logger.debug(
                "OSPFv3 is not supported on this platform, script will not "
                "attempt to fetch OSPFv3 data"
            )
            return "false"

    # Funtion to collect OSPF Data
    def collect_ospf_data(self):
        '''Funtion to collect OSPF Data'''
        url_list = self.ospfv2_url_list
        v3_url_list = self.ospfv3_url_list
        # for url in url_list:
        #     dprint(url)
        response_list = []

        if 'is_ospfv2_supported' not in self.agent.variables:
            self.agent.variables['is_ospfv2_supported'] = (
                self.check_ospfv2_supported()
            )

        if 'is_ospfv3_supported' not in self.agent.variables:
            self.agent.variables['is_ospfv3_supported'] = (
                self.check_ospfv3_supported()
            )

        ospfv2_supported = self.agent.variables['is_ospfv2_supported']
        ospfv3_supported = self.agent.variables['is_ospfv3_supported']

        if ospfv2_supported == "true":
            for url in url_list:
                response = self.agent.fetch_url(url)
                if response is None:
                    continue
                else:
                    response_list.append(response)

        dprint('Response list length after fetch ospfv2:', len(response_list))

        if ospfv3_supported == "true":
            for url in v3_url_list:
                response = self.agent.fetch_url(url)
                if response is None:
                    continue
                else:
                    response_list.append(response)

        dprint('Response list length after fetch ospfv3:', len(response_list))
        self.cleanup_ospf_data()
        self.analyze_ospf_data(response_list)

        # bring the alert back to normal
        # all neighbors should be in good state,
        # and there should be no new alerts
        if self.ospf_alert_on_this_cycle != True:
            if self.ospf_neighbor_not_in_stable_state != True:
                self.agent.clear_alert_description_for_key(OSPF)
                self.alm.alert_levels_generated_within_poll_per_subagent['ospf'].add(
                    AlertLevel.NONE)

        return None

    # Function to execute no debug in case of no errors in the last 5 cycles
    def cleanup_ospf_data(self):
        '''Function to execute no debug in case of no errors in the last 5
         cycles'''
        if int(self.agent.variables['ospfv2_debug_packet_cycles_left']) == 1:
            self.action.add("no debug ospfv2 packet")
            self.action.add("show debug buffer")
            self.agent.variables['ospfv2_debug_packet_cycles_left'] = str(0)
        if int(self.agent.variables['ospfv3_debug_packet_cycles_left']) == 1:
            self.action.add("no debug ospfv3 packet")
            self.action.add("show debug buffer")
            self.agent.variables['ospfv3_debug_packet_cycles_left'] = str(0)

    # Function to parse and analyze OSPF response
    # Input Parameters:
    # res : ospf response to be parsed and analyzed
    # ospf_version : ospf version to be parsed and analyzed(ospfv2/ospfv3)
    def analyze_ospf_data(self, res_list):
        '''Function to parse and analyze OSPF response'''
        # res_list = [] if res_list is None else res_list
        cycles = int(
            self.agent.variables['ospfv2_debug_packet_cycles_left'])
        if cycles != 0:
            self.agent.variables['ospfv2_debug_packet_cycles_left'] = str(
                cycles-1)
        cycles = int(
            self.agent.variables['ospfv3_debug_packet_cycles_left'])
        if cycles != 0:
            self.agent.variables['ospfv3_debug_packet_cycles_left'] = str(
                cycles-1)
        neighbor_dict_new = {}
        neighbor_count = 0
        '''
        Structure of neighbor
        {
          "1": {
            "1": {
              "0.0.0.0": {
                "vlan101": {
                  "192.0.0.1": {
                    "bdr": "0.0.0.0",
                    "dr": "101.1.0.1",
                    "nbr_if_addr": "fe80::211:1ff:fe00:1",
                    "nbr_options": [
                    "external_attributes_lsa",
                    "external_routing",
                    "type_of_service"
                    ],
                    "nbr_priority": 0,
                    "nbr_router_id": "192.0.0.1",
                    "nfsm_state": "full",
                    "statistics": {
                    "ls_retransmit_queue_len": 0,
                    "state_changes_count": 5
                    },
                    "status": {
                    "dead_timer_due": 30,
                    "dr_rtr_state": "desig_rtr_other",
                    "time_of_last_change": 1661967550
                    }
                  },
                  "192.0.0.5": {
                    "bdr": "0.0.0.0",
                    "dr": "101.1.0.1",
                    "nbr_if_addr": "fe80::211:1ff:fe00:5",
                    "nbr_options": [
                    "external_attributes_lsa",
                    "external_routing",
                    "type_of_service"
                    ],
                    "nbr_priority": 0,
                    "nbr_router_id": "192.0.0.5",
                    "nfsm_state": "full",
                    "statistics": {
                    "ls_retransmit_queue_len": 0,
                    "state_changes_count": 5
                    },
                    "status": {
                    "dead_timer_due": 30,
                    "dr_rtr_state": "desig_rtr_other",
                    "time_of_last_change": 1661967550
                    }
                  }
                }
              }
            }
          }
        }
        '''
        for res in res_list:
            for vrf, vrf_data in res.items():
                for _, router_data in vrf_data.items():
                    for _, area_data in router_data.items():
                        for ospf_interface, ospf_intf_data in area_data.items():
                            for _, neighbor_data in ospf_intf_data.items():
                                neighbor_count += 1
                                nbr_if_addr = neighbor_data["nbr_if_addr"]
                                nfsm_state = neighbor_data["nfsm_state"]
                                time_of_last_change = neighbor_data["status"]["time_of_last_change"]
                                date_time = datetime.now()
                                current_time = int(date_time.timestamp())
                                neighbor_dict_new["{}|{}".format(ospf_interface, nbr_if_addr)] = {
                                    "nfsm_state": nfsm_state,
                                    "time_of_last_change": time_of_last_change,
                                    "current_time": current_time,
                                    "vrf": vrf
                                }

        neighbor_dict_old = json.loads(
            self.agent.variables["ospf_neighbor_list"])
        dprint('nbr_dict_old: {0}'.format(neighbor_dict_old))
        dprint('nbr_dict_new: {0}'.format(neighbor_dict_new))
        dprint('Old ospf dict:')
        dprint('******************')
        for key in neighbor_dict_old:
            dprint(key)
        dprint("-----------------------------")

        dprint('New ospf dict:')
        dprint('******************')
        for key in neighbor_dict_new:
            dprint(key)
        dprint("-----------------------------")

        self.monitor_nfsm_state_changes_and_timeout(
            neighbor_dict_old, neighbor_dict_new)
        self.monitor_neighbor(neighbor_dict_old, neighbor_dict_new)
        self.agent.actions_ospf_bgp.update(self.action)

        self.agent.variables["ospf_neighbor_list"] = json.dumps(
            neighbor_dict_new)
        self.agent.variables['neighbor_count'] = str(neighbor_count)

    # Structure of neighbor_dict_new/neighbor_dict_old
    # Key : "ospf_interface|nbr_if_addr"
    # Value: {
    #     "nfsm_state" : full,
    #     "time_of_last_change" : 12345678,
    #     "current_time" : 12345685,
    #     "vrf" : default
    # }

    def update_action_cli(self, neighbor_ip, interface, vrf, alert_level):
        '''Function to update the action CLIs to the action set'''
        self.alm.alert_levels_generated_within_poll_per_subagent['ospf'].add(
            alert_level)
        self.ospf_alert_on_this_cycle = True
        if type(ip_address(neighbor_ip)) is IPv4Address:
            self.action.add("show ip ospf statistics interface {0} vrf "
                            "{1}".format(interface, vrf))
            self.action.add(
                "ping {0} vrf {1} repetitions 2".format(neighbor_ip, vrf))
            self.action.add("debug ospfv2 packet port {0}".format(interface))

            self.agent.variables['ospfv2_debug_packet_cycles_left'] = str(5)
        else:
            self.action.add("show ipv6 ospfv3 statistics interface {}".format(
                interface))
            self.action.add("ping6 {0} vrf {1} source {2} repetitions 2".format(
                neighbor_ip, vrf, interface))
            self.action.add("debug ospfv3 packet port {0}".format(interface))

            self.agent.variables['ospfv3_debug_packet_cycles_left'] = str(
                5)
    # Function to track ospf state changes and timeout
    # Input Parameters
    # neighbor_dict_old : Data structure conatining neighbor dictionary of
    #                     previous poll cycle
    # neighbor_dict_new : Data structure conatining neighbor dictionary of
    #                     current poll cycle

    def monitor_nfsm_state_changes_and_timeout(self,
                                               neighbor_dict_old,
                                               neighbor_dict_new):
        '''Function to track ospf state changes and timeout'''
        for key in neighbor_dict_new:

            # Check for timeout
            time_since_last_change = neighbor_dict_new[key]["current_time"] - \
                neighbor_dict_new[key]["time_of_last_change"]
            # ospf state
            new_nfsm_state = neighbor_dict_new[key]["nfsm_state"]

            # Detecting if any neighbor is not in full or two_way state
            if (
                    (new_nfsm_state != "full")
                    and (new_nfsm_state != "two_way")
            ):
                self.ospf_neighbor_not_in_stable_state = True

            # Detecting if a neighbor is stuck in intermediate state for
            # state_threshold seconds and raising an alert for the next 5
            # cycles
            if (
                    (new_nfsm_state == "ex_start")
                    or (new_nfsm_state == "exchange")
                    or (new_nfsm_state == "init")
            ):
                state_threshold = self.agent.params[
                    "ospf_state_threshold"].value
                alert_time = self.agent.params["poll_interval"].value * NUM_CYCLES
                if ((state_threshold + alert_time) > time_since_last_change >
                        state_threshold):
                    index_list = key.split("|")
                    interface = index_list[0].replace("%2F", "/")
                    neighbor_ip = index_list[1]
                    vrf = neighbor_dict_new[key]["vrf"]
                    # try the ospf statistics of the interface
                    # stuck in state would execute for some cycles, and the tx
                    # statistics would be useful
                    self.update_action_cli(
                        neighbor_ip, interface, vrf, AlertLevel.CRITICAL)
                    message = 'OSPF Neighbor {0} of interface {1} is stuck in {3} state for {2} seconds'.format(
                        neighbor_ip, interface, time_since_last_change, new_nfsm_state)
                    self.agent.action_syslog(Log.WARNING, message)
                    self.agent.set_alert_description_for_key(OSPF, message)
                    self.agent.logger.debug(
                        "For debugging: OSPF Neighbor {0} of interface {1} "
                        "is stuck in {3} state for {2} seconds".format(
                            neighbor_ip, interface, time_since_last_change,
                            new_nfsm_state))
                    dprint(
                        "For debugging: OSPF neighbor {0} vrf {1} interface"
                        " {2} is stuck in {3} state".format(
                            neighbor_ip, vrf, interface, new_nfsm_state))

            # Check for state change
            if key in neighbor_dict_old:
                old_nfsm_state = neighbor_dict_old[key]["nfsm_state"]
                # Checking for OSF neighbor state changes
                if (
                        (
                            (old_nfsm_state == "full")
                            and (
                                (new_nfsm_state == "init")
                                or (new_nfsm_state == "down")
                                or (new_nfsm_state == "exchange")
                                or (new_nfsm_state == "ex_start")
                            )
                        )
                        or (
                            (old_nfsm_state == "two_way")
                            and ((new_nfsm_state == "init") or
                                 (new_nfsm_state == "down"))
                        )
                        or (
                            (old_nfsm_state == "exchange")
                            and (
                                (new_nfsm_state == "init")
                                or (new_nfsm_state == "down")
                                or (new_nfsm_state == "two_way")
                                or (new_nfsm_state == "ex_start")
                            )
                        )
                        or (
                            (old_nfsm_state == "ex_start")
                            and (
                                (new_nfsm_state == "init")
                                or (new_nfsm_state == "two_way")
                                or (new_nfsm_state == "down")
                            )
                        )
                ):
                    index_list = key.split("|")
                    interface = index_list[0].replace("%2F", "/")
                    neighbor_ip = index_list[1]
                    vrf = neighbor_dict_new[key]["vrf"]
                    # try the ospf statistics of the interface
                    # stuck in state would execute for some cycles, and the tx
                    # statistics would be useful
                    self.update_action_cli(
                        neighbor_ip, interface, vrf, AlertLevel.MAJOR)
                    message = "OSPF Neighbor {0} of interface {1} is flapping from {2} to {3}".format(
                        neighbor_ip, interface, old_nfsm_state, new_nfsm_state)
                    self.agent.action_syslog(Log.WARNING, message)
                    self.agent.set_alert_description_for_key(OSPF, message)
                    self.agent.logger.debug(
                        "For debugging: OSPF Neighbor {0} of interface {1} is "
                        "flapping from {2} to {3}".format(
                            neighbor_ip, interface, old_nfsm_state,
                            new_nfsm_state
                        )
                    )
                    dprint(
                        "For debugging: OSPF Neighbor {0} of interface {1} is "
                        "flapping from {2} to {3}".format(
                            neighbor_ip, interface, old_nfsm_state,
                            new_nfsm_state
                        )
                    )

    # Function to track ospf neighbors getting added and expired
    # Input Parameters
    # neighbor_dict_old : Data structure conatining neighbor dictionary of
    #                     previous poll cycle
    # neighbor_dict_new : Data structure conatining neighbor dictionary of
    #                     current poll cycle
    def monitor_neighbor(self, neighbor_dict_old, neighbor_dict_new):
        '''Function to track ospf neighbors getting added and expired'''
        neighbors_new = set(neighbor_dict_new.keys()).difference(
            set(neighbor_dict_old.keys()))
        neighbors_expired = set(neighbor_dict_old.keys()).difference(
            set(neighbor_dict_new.keys()))

        for key in neighbors_new:
            index_list = key.split("|")
            interface = index_list[0].replace("%2F", "/")
            neighbor_ip = index_list[1]
            dprint(
                "OSPF-Neighbor-Monitor: New neighbor added [Neighbor: {0} "
                "Interface: {1}]".format(neighbor_ip, interface))

        for key in neighbors_expired:
            index_list = key.split("|")
            interface = index_list[0].replace("%2F", "/")
            neighbor_ip = index_list[1]
            vrf = neighbor_dict_old[key]["vrf"]
            message = "OSPF Neighbor expired [Neighbor: {0} Interface: {1}]".format(
                neighbor_ip, interface)
            self.agent.action_syslog(Log.WARNING, message)
            self.agent.set_alert_description_for_key(OSPF, message)
            dprint(
                "OSPF-Neighbor-Monitor: Neighbor expired [Neighbor: {0} "
                "Interface: {1}]".format(neighbor_ip, interface))
            self.update_action_cli(
                neighbor_ip, interface, vrf, AlertLevel.MINOR)


class BGPAgent:
    '''This class periodically collects BGP data using REST query and
     Analyzes it'''

    def __init__(self, agent, alm):
        self.agent = agent
        self.alm = alm
        self.action = set()
        self.bgp_alert_on_this_cycle = False
        self.bgp_neighbor_not_in_stable_state = False
        self.unique_vrf_base_url = HTTP_ADDRESS + \
            URI_PREFIX_GET_V10_13 + 'system/vrfs/' + \
            self.agent.params['vrf'].value + '/bgp_routers?depth=4'

    def bgp_handler(self):
        '''This function is wrapper for handle_bgp_data'''
        self.handle_bgp_data()

    # Function to modify input response dict into a simplified dict which
    # contains
    # vrf/bgp_nbr_addr as key and its corresponding neighbor info as value

    # Input Parameters
    # response_dict : Contains key as vrf and value as all the neighbors
    # Example:
    # response_dict = {
    #       vrf1:{
    #           neighbor1:{neighborinfo}
    #           neighbor2:{neighborinfo}
    #       }
    #       vrf2:{
    #           neighbor1:{neighborinfo}
    #           neighbor3:{neighborinfo}
    #       }
    # }

    # Output Parameters
    # final_response: Conatins key vrf/neighbor_ip_addr and value as neighbor
    #                 info
    # Example:
    # final_response = {
    #       vrf1/neighbor1:{neighborinfo}
    #       vrf1/neighbor2:{neighborinfo}
    #       vrf2/neighbor1:{neighborinfo}
    #       vrf2/neighbor3:{neighborinfo}
    # }
    def simplify_response(self, response_dict):
        '''Function to modify input response dict into a simplified dict
         which contains vrf/bgp_nbr_addr as key and its corresponding neighbor
          info as value'''
        if not response_dict:
            return {}
        user_input_neighbor_list = (
            self.agent.params['bgp_neighbor'].value).split(',')
        final_response = {}
        for vrf, vrf_data in response_dict.items():
            for _, bgp_data in vrf_data.items():
                for bgp_nbr_addr, bgp_nbr_data in bgp_data['bgp_neighbors'].items():
                    # skip adding bgp peer group to bgp neighbors:
                    # REST output of bgp nbrs will have the individual bgp nbrs
                    # and an entry for each peer group which is configured.
                    # BGP peer-group consists of 1 or more bgp neighbors. We are
                    # already monitoring the individual BGP neighbors which are
                    # part of peer group. Hence no need to monitor the peer group
                    # entry. Also the peer-group cannot be considered a BGP nbr
                    if bgp_nbr_data["is_peer_group"] is True:
                        continue
                    if user_input_neighbor_list[0] == '*':
                        final_response["{}/{}".format(vrf,
                                                      bgp_nbr_addr)] = bgp_nbr_data
                    else:
                        if bgp_nbr_addr in user_input_neighbor_list:
                            # dprint("{0} {1}".format(vrf, bgp_nbr_addr))
                            final_response["{}/{}".format(vrf,
                                                          bgp_nbr_addr)] = bgp_nbr_data
        return final_response

    # Function to check if bgp is supported before trying to handle data
    def check_bgp_supported(self):
        url = (HTTP_ADDRESS + URI_PREFIX_GET + 'system/vrfs/' +
               self.agent.params['vrf'].value + '?depth=2')
        response = self.agent.fetch_url(url)
        if '"bgp_routers"' in str(response) or "'bgp_routers'" in str(response):
            return "true"
        else:
            self.agent.logger.debug(
                "BGP is not supported on this platform, script will not "
                "attempt to fetch bgp data"
            )
            return "false"

    # Function to fetch bgp neighbor response and handle it
    def handle_bgp_data(self):
        '''Function to fetch bgp neighbor response and handle it'''
        response_dict = {}
        final_response = None

        if 'is_bgp_supported' not in self.agent.variables:
            self.agent.variables['is_bgp_supported'] = (
                self.check_bgp_supported()
            )

        bgp_supported = self.agent.variables['is_bgp_supported']

        if bgp_supported == "true":
            response = self.agent.fetch_url(self.unique_vrf_base_url)
            dprint("unique_vrf_base_url={}".format(self.unique_vrf_base_url))
            dprint("response unique_vrf_base_url={}".format(response))
            final_response = self.simplify_response(response)

        self.analyze_bgp_data(final_response)

        if self.bgp_alert_on_this_cycle != True:
            if self.bgp_neighbor_not_in_stable_state != True:
                self.agent.clear_alert_description_for_key(BGP)
                self.alm.alert_levels_generated_within_poll_per_subagent['bgp'].add(
                    AlertLevel.NONE)

    # Funtion to execute no debug in case there is no error in the last 5
    # cycles
    def cleanup_bgp_data(self, res):
        '''Funtion to execute no debug in case there is no error in the
         last 5 cycles'''
        dprint("Clean up alerts, logs")
        # add a logic to clean up alerts after every 5 cycles
        # self.agent.action_cli("no debug BGP packet")

        '''
        Structure of BGP Neighbor
        {
            "ORF_capability": {},
            "ORF_prefix_list": {},
            "ORF_received_prefix_list": {},
            "activate": {
            "ipv4-unicast": false,
            "ipv6-unicast": true,
            "l2vpn-evpn": false
            },
            "add_paths": {
            "ipv4-unicast": "disable",
            "ipv6-unicast": "disable"
            },
            "add_paths_adv_best_n": {
            "ipv4-unicast": 1,
            "ipv6-unicast": 1
            },
            "advertisement_interval": {},
            "af_status": {},
            "allow_as_in": {},
            "aspath_filters": {},
            "bfd_enable": false,
            "capabilites_recevied": [
            "4-octet-asn",
            "cisco-route-refresh",
            "graceful-restart",
            "mp-ipv6-unicast",
            "route-refresh"
            ],
            "capabilites_sent": [
            "4-octet-asn",
            "cisco-route-refresh",
            "graceful-restart",
            "mp-ipv6-unicast",
            "route-refresh"
            ],
            "default_originate": {
            "ipv4-unicast": false,
            "ipv6-unicast": false
            },
            "default_originate_route_map": {},
            "ebgp_hop_count": 1,
            "fall_over": false,
            "gshut": {
            "local_pref": 0,
            "timer": 180
            },
            "inbound_soft_reconfiguration": {
            "ipv4-unicast": false,
            "ipv6-unicast": false
            },
            "is_peer_group": false,
            "local_as_mode": "none",
            "local_interface": {
              "loopback1": "/rest/v10.08/system/interfaces/loopback1"
            },
            "max_prefix_options": {},
            "negotiated_add_paths": {
            "ipv4-unicast": "disable",
            "ipv6-unicast": "disable"
            },
            "negotiated_holdtime": 20,
            "negotiated_keepalive": 5,
            "next_hop_self": {
            "ipv4-unicast": false,
            "ipv6-unicast": false
            },
            "next_hop_unchanged": {
            "l2vpn-evpn": false
            },
            "passive": false,
            "peer_rtrid": "2.2.2.2",
            "prefix_lists": {},
            "remote_as": 20,
            "remove_private_as": false,
            "route_maps": {},
            "route_reflector_client": {
            "ipv4-unicast": false,
            "ipv6-unicast": false,
            "l2vpn-evpn": false
            },
            "sel_local_port": 41499,
            "sel_remote_port": 179,
            "send_community": {
            "ipv4-unicast": "none",
            "ipv6-unicast": "none",
            "l2vpn-evpn": "none"
            },
            "shutdown": false,
            "statistics": {
            "bgp_peer_dropped_count": 0,
            "bgp_peer_established_count": 1,
            "bgp_peer_keepalive_in_count": 2864,
            "bgp_peer_keepalive_out_count": 2862,
            "bgp_peer_notify_in_count": 0,
            "bgp_peer_notify_out_count": 0,
            "bgp_peer_open_in_count": 1,
            "bgp_peer_open_out_count": 1,
            "bgp_peer_refresh_in_count": 0,
            "bgp_peer_refresh_out_count": 0,
            "bgp_peer_update_in_count": 1,
            "bgp_peer_update_out_count": 1,
            "bgp_peer_uptime": 12462
            },
            "status": {
            "bgp_peer_state": "Established"
            },
            "timers": {
            "connect-retry": 120,
            "holdtime": 180,
            "keepalive": 60
            },
            "weight": 0
        }
        '''

    # Function to analyze bgp response
    # Input Parameters
    # res: bgp response json
    def analyze_bgp_data(self, res):
        '''Function to analyze bgp response'''
        res = {} if res is None else res
        bgp_nbr_dict_new = {}
        bgp_nbr_count = 0
        for bgp_nbr_key in res:
            bgp_nbr_count += 1
            bgp_peer_state = res[bgp_nbr_key]["status"]["bgp_peer_state"]
            bgp_peer_uptime = 0
            if res[bgp_nbr_key]["statistics"]:
                bgp_peer_uptime = res[bgp_nbr_key]["statistics"]["bgp_peer_uptime"]

            bgp_local_interface = "None"
            if 'local_interface' in res[bgp_nbr_key] and res[bgp_nbr_key]['local_interface']:
                bgp_local_interface = list(
                    res[bgp_nbr_key]["local_interface"].keys())[0]

            bgp_update_source = "None"
            if 'update_source' in res[bgp_nbr_key] and res[bgp_nbr_key]['update_source']:
                bgp_update_source = res[bgp_nbr_key]["update_source"]

            if "bgp_rcvd_err_code" in res[bgp_nbr_key]["status"]:
                bgp_peer_last_err_rx = res[bgp_nbr_key]["status"][
                    "bgp_rcvd_err_code"]
            else:
                bgp_peer_last_err_rx = "No Error"

            if "bgp_rcvd_err_sub_code" in res[bgp_nbr_key]["status"]:
                bgp_peer_last_sub_err_rx = res[bgp_nbr_key]["status"][
                    "bgp_rcvd_err_sub_code"]
            else:
                bgp_peer_last_sub_err_rx = "No Error"

            if "bgp_sent_err_code" in res[bgp_nbr_key]["status"]:
                bgp_peer_last_err_tx = res[bgp_nbr_key]["status"][
                    "bgp_sent_err_code"]
            else:
                bgp_peer_last_err_tx = "No Error"

            if "bgp_sent_err_sub_code" in res[bgp_nbr_key]["status"]:
                bgp_peer_last_sub_err_tx = res[bgp_nbr_key]["status"][
                    "bgp_sent_err_sub_code"]
            else:
                bgp_peer_last_sub_err_tx = "No Error"

            bgp_peer_established_count = 0
            if res[bgp_nbr_key]["statistics"]:
                bgp_peer_established_count = res[bgp_nbr_key]["statistics"][
                    "bgp_peer_established_count"
                ]

            bgp_peer_stuck_state = "None"

            bgp_nbr_dict_new[bgp_nbr_key] = {
                "bgp_peer_state": bgp_peer_state,
                "bgp_peer_uptime": bgp_peer_uptime,
                "bgp_peer_last_err_rx": bgp_peer_last_err_rx,
                "bgp_peer_last_err_tx": bgp_peer_last_err_tx,
                "bgp_peer_last_sub_err_rx": bgp_peer_last_sub_err_rx,
                "bgp_peer_last_sub_err_tx": bgp_peer_last_sub_err_tx,
                "bgp_peer_established_count": bgp_peer_established_count,
                "bgp_local_interface": bgp_local_interface,
                "bgp_update_source": bgp_update_source,
                "bgp_peer_stuck_state": bgp_peer_stuck_state}

        bgp_nbr_dict_old = json.loads(self.agent.variables["bgp_nbr_list"])

        dprint("---------------------------")
        dprint('BGP dict old:')
        for key in bgp_nbr_dict_old:
            dprint("{0}: {1} {2}".format(
                key, bgp_nbr_dict_old[key]['bgp_local_interface'],
                bgp_nbr_dict_old[key]['bgp_update_source']))
        dprint("---------------------------")
        dprint("BGP dict new:")
        for key in bgp_nbr_dict_new:
            dprint("{0}: {1} {2}".format(
                key, bgp_nbr_dict_new[key]['bgp_local_interface'],
                bgp_nbr_dict_new[key]['bgp_update_source']))
        dprint("---------------------------")

        self.monitor_bgp_nbr_state_changes(bgp_nbr_dict_old, bgp_nbr_dict_new)
        self.monitor_bgp_nbr_stuck(bgp_nbr_dict_old, bgp_nbr_dict_new)
        self.monitor_bgp_nbr_flaps(bgp_nbr_dict_old, bgp_nbr_dict_new)
        self.monitor_bgp_nbr_add_delete(bgp_nbr_dict_old, bgp_nbr_dict_new)

        if self.agent.variables['bgp_nbr_alert'] == "false":
            self.monitor_bgp_nbr_errors(bgp_nbr_dict_old, bgp_nbr_dict_new)

        # All common BGP alerts to be invoked here
        if self.agent.variables['bgp_nbr_alert'] == "true":
            self.action.add("show bgp all-vrf all summary")

        self.agent.actions_ospf_bgp.update(self.action)

        # dprint("Test BGP-State change, time-out and error codes for"
        #        "adjacency")

        self.agent.variables['bgp_nbr_list'] = json.dumps(bgp_nbr_dict_new)
        self.agent.variables['bgp_nbr_count'] = str(bgp_nbr_count)
        self.agent.variables['bgp_nbr_alert'] = "false"

    '''
    Structure of bgp neighbor dict:
    keys: vrf/bgp_nbr_addr
    values:{
        bgp_peer_state,
        bgp_peer_up_time,
        bgp_peer_last_err_rx,
        bgp_peer_last_err_tx,
        bgp_peer_established_count,
        bgp_peer_last_sub_err_rx,
        bgp_peer_last_sub_err_tx,
        bgp_peer_stuck_state
    }
    '''

    def update_action_cli(self, bgp_peer_addr, vrf, update_source,
                          local_interface, alert_level):
        '''Function to update the action CLIs to the action set'''
        self.alm.alert_levels_generated_within_poll_per_subagent[
            'bgp'].add(alert_level)
        self.agent.variables['bgp_nbr_alert'] = "true"
        self.bgp_alert_on_this_cycle = True
        if type(ip_address(bgp_peer_addr)) is IPv4Address:
            self.action.add("show ip route {0} vrf {1}".format(
                bgp_peer_addr, vrf))
            if update_source != "None":
                self.action.add("ping {0} source {1} vrf {2} repetitions 2"
                                .format(bgp_peer_addr, update_source, vrf))
            elif local_interface != "None":
                self.action.add("ping {0} source {1} vrf {2} repetitions 2"
                                .format(bgp_peer_addr, local_interface, vrf))
            else:
                self.action.add("ping {0} vrf {1} repetitions 2".format(
                    bgp_peer_addr, vrf))
            self.action.add("traceroute {0} vrf {1} probes 1 maxttl 6".format(
                bgp_peer_addr, vrf))

        else:
            self.action.add("show ipv6 route {0} vrf {1}".format(
                bgp_peer_addr, vrf))
            if update_source != "None":
                self.action.add("ping6 {0} source {1} vrf {2} repetitions 2"
                                .format(bgp_peer_addr, update_source, vrf))
            elif local_interface != "None":
                self.action.add("ping6 {0} source {1} vrf {2} repetitions 2"
                                .format(bgp_peer_addr, local_interface, vrf))
            else:
                self.action.add("ping6 {0} vrf {1} repetitions 2".format(
                    bgp_peer_addr, vrf))
            self.action.add("traceroute6 {0} vrf {1} probes 1 maxttl 6".format(
                bgp_peer_addr, vrf))

    # Function to monitor bgp neighbor state changes
    # Input Parameters
    # bgp_nbr_dict_old: Data structure conatining neighbor dictionary of
    #                   previous cycle
    # bgp_nbr_dict_new: Data structure conatining neighbor dictionary of
    #                   current cycle
    def monitor_bgp_nbr_state_changes(self, bgp_nbr_dict_old,
                                      bgp_nbr_dict_new):
        '''Function to monitor bgp neighbor state changes'''
        for bgp_nbr_key in bgp_nbr_dict_new:
            if bgp_nbr_key in bgp_nbr_dict_old:
                vrf = bgp_nbr_key.split("/")[0]
                bgp_peer_addr = bgp_nbr_key.split("/")[1]
                update_source = bgp_nbr_dict_old[bgp_nbr_key][
                    'bgp_update_source']
                local_interface = bgp_nbr_dict_old[bgp_nbr_key][
                    'bgp_local_interface']

                # Detecting if any BGP neighbor is not in Established state
                # This is mainly for clearing the alert
                if (bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_state"] !=
                   "Established"):
                    self.bgp_neighbor_not_in_stable_state = True

                # Detecting a neighbor's state change from established to idle
                if (
                        bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_state"] ==
                        "Established"
                        and bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_state"] ==
                        "Idle"
                ):
                    self.update_action_cli(
                        bgp_peer_addr, vrf, update_source, local_interface,
                        AlertLevel.CRITICAL)
                    self.agent.action_syslog(
                        Log.WARNING,
                        'BGP Peer {0} state changed from Established to Idle. '
                        'Last Error Sent - {1} , '
                        'Last Sub Error Sent - {2} ,'
                        'Last Error Received - {3} , '
                        'Last Sub Error Received - {4}'.format(
                            bgp_peer_addr,
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_rx"],
                        ),
                    )
                    self.agent.set_alert_description_for_key(
                        BGP, 'BGP Peer {0} state changed from Established to Idle'.format(bgp_peer_addr))
                    self.agent.logger.debug(
                        'For debugging: BGP Peer {0} '
                        'changed from Established to Idle'.format(
                            bgp_peer_addr
                        )
                    )

                # Detecting a neighbor's state change from established to
                # connect
                elif (
                        bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_state"] ==
                        "Established"
                        and bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_state"] ==
                        "Connect"
                ):
                    self.update_action_cli(
                        bgp_peer_addr, vrf, update_source, local_interface,
                        AlertLevel.CRITICAL
                    )
                    self.agent.action_syslog(
                        Log.WARNING,
                        "BGP Peer {0} state changed from Established to "
                        "Connect. "
                        "Last Error Sent - {1} "
                        "Last Sub Error Sent - {2}, "
                        "Last Error Received - {3} "
                        "Last Sub Error Received - {4}".format(
                            bgp_peer_addr,
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_rx"],
                        ),
                    )
                    self.agent.set_alert_description_for_key(
                        BGP, "BGP Peer {0} state changed from Established to Connect".format(bgp_peer_addr))
                    self.agent.logger.debug(
                        "For debugging: BGP Peer {0} changed from "
                        "Established to Connect".format(
                            bgp_peer_addr
                        )
                    )

                # Detecting a neighbor's state change from established to active
                elif (
                        bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_state"] ==
                        "Established"
                        and bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_state"] ==
                        "Active"
                ):
                    self.update_action_cli(
                        bgp_peer_addr, vrf, update_source, local_interface,
                        AlertLevel.CRITICAL
                    )
                    self.agent.action_syslog(
                        Log.WARNING,
                        'BGP Peer {0} state changed from Established to '
                        'Active. '
                        'Last Error Sent - {1} '
                        'Last Sub Error Sent - {2}, '
                        'Last Error Received - {3} '
                        'Last Sub Error Received - {4}'.format(
                            bgp_peer_addr,
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_rx"],
                        ),
                    )
                    self.agent.set_alert_description_for_key(
                        BGP, "BGP Peer {0} state changed from Established to Active".format(bgp_peer_addr))
                    self.agent.logger.debug("For debugging: BGP Peer {0} "
                                            "changed from Established"
                                            " to Active".format(bgp_peer_addr))
                # Detecting a neighbor's state change from established to
                # openconfirm
                elif (
                        bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_state"] ==
                        "Established"
                        and
                        bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_state"] ==
                        "OpenConfirm"
                ):
                    self.update_action_cli(bgp_peer_addr, vrf, update_source,
                                           local_interface, AlertLevel.CRITICAL
                                           )
                    self.agent.action_syslog(
                        Log.WARNING,
                        'BGP Peer {0} state changed from Established to'
                        ' OpenConfirm. '
                        'Last Error Sent - {1} '
                        'Last Sub Error Sent - {2}, '
                        'Last Error Received - {3} '
                        'Last Sub Error Received - {4}'.format(
                            bgp_peer_addr,
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_rx"],
                        ),
                    )
                    self.agent.set_alert_description_for_key(
                        BGP, "BGP Peer {0} state changed from Established to OpenConfirm".format(bgp_peer_addr))
                    self.agent.logger.debug("For debugging: BGP Peer {0} "
                                            "changed from Established to "
                                            "OpenConfirm".format(bgp_peer_addr)
                                            )

    # Function to monitor bgp neighbor in stuck state
    # Input Parameters
    # bgp_nbr_dict_old: Data structure conatining neighbor dictionary of
    #                   previous cycle
    # bgp_nbr_dict_new: Data structure conatining neighbor dictionary of
    #                   current cycle
    def monitor_bgp_nbr_stuck(self, bgp_nbr_dict_old, bgp_nbr_dict_new):
        '''Function to monitor bgp neighbor in stuck state'''
        for bgp_nbr_key in bgp_nbr_dict_new:
            if bgp_nbr_key in bgp_nbr_dict_old:
                vrf = bgp_nbr_key.split("/")[0]
                bgp_peer_addr = bgp_nbr_key.split("/")[1]
                update_source = bgp_nbr_dict_old[bgp_nbr_key][
                    "bgp_update_source"]
                local_interface = bgp_nbr_dict_old[bgp_nbr_key][
                    "bgp_local_interface"]

                # Detecting a neighbor being stuck in idle
                if (
                        (
                            bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_state"] ==
                            "Idle"
                            and bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_state"] == "Idle"
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_uptime"]
                            >= bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_uptime"]
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_established_count"]
                            == bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_established_count"]
                        )
                ):
                    if (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_stuck_state"] != "Idle"
                    ):
                        self.update_action_cli(
                            bgp_peer_addr,
                            vrf,
                            update_source,
                            local_interface,
                            AlertLevel.MINOR,
                        )
                        self.agent.action_syslog(
                            Log.WARNING,
                            'BGP Peer {0} stuck in Idle state. '
                            'Last Error Sent - {1} '
                            'Last Sub Error Sent - {2}, '
                            'Last Error Received - {3} '
                            'Last Sub Error Received - {4}'.format(
                                bgp_peer_addr,
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_rx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_rx"],
                            ),
                        )
                        self.agent.set_alert_description_for_key(
                            BGP, 'BGP Peer {0} stuck in Idle'.format(bgp_peer_addr))
                        self.agent.logger.debug(
                            "For debugging: BGP Peer {0} stuck in Idle "
                            "State".format(
                                bgp_peer_addr
                            )
                        )
                    bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_stuck_state"] = \
                        "Idle"
                # Detecting a neighbor being stuck in connect
                elif (
                        (
                            bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_state"] ==
                            "Connect"
                            and bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_state"] == "Connect"
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_uptime"]
                            > bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_uptime"]
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_established_count"]
                            == bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_established_count"]
                        )
                ):
                    if (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_stuck_state"] != "Connect"
                    ):
                        self.update_action_cli(
                            bgp_peer_addr,
                            vrf,
                            update_source,
                            local_interface,
                            AlertLevel.MINOR,
                        )
                        self.agent.action_syslog(
                            Log.WARNING,
                            'BGP Peer {0} stuck in Connect state. '
                            'Last Error Sent - {1} '
                            'Last Sub Error Sent - {2}, '
                            'Last Error Received - {3} '
                            'Last Sub Error Received - {4}'.format(
                                bgp_peer_addr,
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_rx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_rx"],
                            ),
                        )
                        self.agent.set_alert_description_for_key(
                            BGP, 'BGP Peer {0} stuck in Connect'.format(bgp_peer_addr))
                        self.agent.logger.debug(
                            "For debugging: BGP Peer {0} stuck in Connect "
                            "State".format(
                                bgp_peer_addr
                            )
                        )
                    bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_stuck_state"] = \
                        "Connect"
                # Detecting a neighbor being stuck in active
                elif (
                        (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_state"] == "Active"
                            and bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_state"] == "Active"
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_uptime"]
                            > bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_uptime"]
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_established_count"]
                            == bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_established_count"]
                        )
                ):
                    if (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_stuck_state"] != "Active"
                    ):
                        self.update_action_cli(
                            bgp_peer_addr,
                            vrf,
                            update_source,
                            local_interface,
                            AlertLevel.MINOR,
                        )
                        self.agent.action_syslog(
                            Log.WARNING,
                            'BGP Peer {0} stuck in Active state. '
                            'Last Error Sent - {1} '
                            'Last Sub Error Sent - {2}, '
                            'Last Error Received - {3} '
                            'Last Sub Error Received - {4}'.format(
                                bgp_peer_addr,
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_rx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_rx"],
                            ),
                        )
                        self.agent.set_alert_description_for_key(
                            BGP, 'BGP Peer {0} stuck in Active'.format(bgp_peer_addr))
                        self.agent.logger.debug(
                            "For debugging: BGP Peer {0} stuck in Active "
                            "State".format(
                                bgp_peer_addr
                            )
                        )
                    bgp_nbr_dict_new[bgp_nbr_key][
                        "bgp_peer_stuck_state"] = "Active"
                # Detecting a neighbor being stuck in openConfirm
                elif (
                        (
                            bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_state"] ==
                            "OpenConfirm"
                            and bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_state"]
                            == "OpenConfirm"
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key]["bgp_peer_uptime"]
                            > bgp_nbr_dict_old[bgp_nbr_key]["bgp_peer_uptime"]
                        )
                        and (
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_established_count"]
                            == bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_established_count"]
                        )
                ):
                    if (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_stuck_state"] != "OpenConfirm"
                    ):
                        self.update_action_cli(
                            bgp_peer_addr,
                            vrf,
                            update_source,
                            local_interface,
                            AlertLevel.MINOR,
                        )
                        self.agent.action_syslog(
                            Log.WARNING,
                            'BGP Peer {0} stuck in OpenConfirm state. '
                            'Last Error Sent - {1} '
                            'Last Sub Error Sent - {2}, '
                            'Last Error Received - {3} '
                            'Last Sub Error Received - {4}'.format(
                                bgp_peer_addr,
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_tx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_err_rx"],
                                bgp_nbr_dict_new[bgp_nbr_key][
                                    "bgp_peer_last_sub_err_rx"],
                            ),
                        )
                        self.agent.set_alert_description_for_key(
                            BGP, 'BGP Peer {0} stuck in OpenConfirm'.format(bgp_peer_addr))
                        self.agent.logger.debug(
                            "For debugging: BGP Peer {0} stuck in OpenConfirm "
                            "State".format(
                                bgp_peer_addr
                            )
                        )
                    bgp_nbr_dict_new[bgp_nbr_key][
                        "bgp_peer_stuck_state"] = "OpenConfirm"

    # Function to monitor bgp neighbor flapping
    # Input Parameters
    # bgp_nbr_dict_old: Data structure conatining neighbor dictionary of
    #                   previous cycle
    # bgp_nbr_dict_new: Data structure conatining neighbor dictionary of
    #                   current cycle
    def monitor_bgp_nbr_flaps(self, bgp_nbr_dict_old, bgp_nbr_dict_new):
        '''Function to monitor bgp neighbor flapping'''
        for bgp_nbr_key in bgp_nbr_dict_new:
            if bgp_nbr_key in bgp_nbr_dict_old:
                vrf = bgp_nbr_key.split("/")[0]
                bgp_peer_addr = bgp_nbr_key.split("/")[1]
                update_source = bgp_nbr_dict_old[bgp_nbr_key][
                    'bgp_update_source']
                local_interface = bgp_nbr_dict_old[bgp_nbr_key][
                    'bgp_local_interface']
                # Detecting if neighbor is flapping
                if (
                        (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_state"] == "Established"
                            and bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_state"] == "Established"
                        ) and (
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_established_count"]
                            > bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_established_count"]
                        )
                ):
                    self.update_action_cli(
                        bgp_peer_addr, vrf, update_source, local_interface,
                        AlertLevel.MAJOR
                    )
                    self.agent.action_syslog(
                        Log.WARNING,
                        'BGP Peer {0} adjacency went down and came back up. '
                        'Last Error Sent - {1} '
                        'Last Sub Error Sent - {2}, '
                        'Last Error Received - {3} '
                        'Last Sub Error Received - {4}'.format(
                            bgp_peer_addr,
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_rx"],
                        ),
                    )
                    self.agent.set_alert_description_for_key(
                        BGP, 'BGP Peer {0} adjacency went down and came back up'.format(bgp_peer_addr))
                    self.agent.logger.debug(
                        'For debugging: BGP Peer {0} adjacency went down '
                        'and came back up'.format(
                            bgp_peer_addr
                        )
                    )

    # Function to monitor bgp neighbor errors
    # Input Parameters
    # bgp_nbr_dict_old: Data structure conatining neighbor dictionary of
    #                   previous cycle
    # bgp_nbr_dict_new: Data structure conatining neighbor dictionary of
    #                   current cycle
    def monitor_bgp_nbr_errors(self, bgp_nbr_dict_old, bgp_nbr_dict_new):
        '''Function to monitor bgp neighbor errors'''
        for bgp_nbr_key in bgp_nbr_dict_new:
            if bgp_nbr_key in bgp_nbr_dict_old:
                bgp_peer_addr = bgp_nbr_key.split("/")[1]
                if (
                        (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_err_tx"]
                            != bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"]
                        ) and (bgp_nbr_dict_new[bgp_nbr_key][
                            "bgp_peer_last_err_tx"] != "No Error")
                ):
                    self.alm.alert_levels_generated_within_poll_per_subagent[
                        'bgp'].add(AlertLevel.MINOR)
                    self.agent.variables["bgp_nbr_alert"] = "true"
                    self.agent.action_syslog(
                        Log.WARNING,
                        'New Error sent to BGP Peer {0}. '
                        'Previous Error Sent - {1} '
                        'Previous Sub Error Sent - {2}, '
                        'Current Error Sent - {3} '
                        'Current Sub Error Sent - {4}'.format(
                            bgp_peer_addr,
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_sub_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_tx"],
                        ),
                    )
                    self.agent.set_alert_description_for_key(
                        BGP, 'New Error sent to BGP Peer {0}'.format(bgp_peer_addr))
                    self.agent.logger.debug(
                        'For debugging: Previous Error Sent {0} '
                        'Current Error Sent {1} to BGP Peer {2}'.format(
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_tx"],
                            bgp_peer_addr,
                        )
                    )
                if (
                        (
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_err_rx"]
                            != bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"]
                        ) and bgp_nbr_dict_new[bgp_nbr_key][
                            "bgp_peer_last_err_rx"] != "No Error"
                ):
                    self.alm.alert_levels_generated_within_poll_per_subagent[
                        'bgp'].add(AlertLevel.MINOR)
                    self.agent.variables["bgp_nbr_alert"] = "true"
                    self.agent.action_syslog(
                        Log.WARNING,
                        'New Error received from BGP Peer {0}. '
                        'Previous Error Received - {1} '
                        'Previous Sub Error Received - {2}, '
                        'Current Error Received - {3} '
                        'Current Sub Error Received - {4}'.format(
                            bgp_peer_addr,
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_sub_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_sub_err_rx"],
                        ),
                    )
                    self.agent.set_alert_description_for_key(
                        BGP, 'New Error received from BGP Peer {0}'.format(bgp_peer_addr))
                    self.agent.logger.debug(
                        'For debugging: Previous Error Received - {0} '
                        'Current Error Received - {1} '
                        'from BGP Peer {2}'.format(
                            bgp_nbr_dict_old[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_nbr_dict_new[bgp_nbr_key][
                                "bgp_peer_last_err_rx"],
                            bgp_peer_addr,
                        )
                    )

    # Function to track BGP neighbors getting added and expired
    # Input Parameters
    # bgp_nbr_dict_old : Data structure conatining neighbor dictionary of
    #                    previous poll cycle
    # bgp_nbr_dict_new : Data structure conatining neighbor dictionary of
    #                    current poll cycle
    def monitor_bgp_nbr_add_delete(self, bgp_nbr_dict_old, bgp_nbr_dict_new):
        '''Function to monitor BGP nbr added/ deleted'''
        neighbors_new = set(bgp_nbr_dict_new.keys()).difference(
            set(bgp_nbr_dict_old.keys()))
        neighbors_deleted = set(bgp_nbr_dict_old.keys()).difference(
            set(bgp_nbr_dict_new.keys()))

        for key in neighbors_new:
            vrf = key.split("/")[0]
            bgp_peer_addr = key.split("/")[1]
            self.agent.action_syslog(Log.WARNING,
                                     "New BGP Peer configured [Peer: {0} "
                                     "VRF: {1}]"
                                     .format(bgp_peer_addr, vrf))
            self.agent.set_alert_description_for_key(
                BGP, "New BGP Peer configured [Peer: {0} VRF: {1}]".format(bgp_peer_addr, vrf))
            dprint(
                "BGP-Neighbor-Monitor: BGP Peer configured [Neighbor: {0} "
                "VRF: {1}]".format(bgp_peer_addr, vrf))

        for key in neighbors_deleted:
            vrf = key.split("/")[0]
            bgp_peer_addr = key.split("/")[1]
            update_source = bgp_nbr_dict_old[key]["bgp_update_source"]
            local_interface = bgp_nbr_dict_old[key]["bgp_local_interface"]
            self.agent.action_syslog(Log.WARNING,
                                     "BGP Peer unconfigured [Peer: {0} "
                                     "VRF: {1}]"
                                     .format(bgp_peer_addr, vrf))
            self.agent.set_alert_description_for_key(
                BGP, "BGP Peer unconfigured [Peer: {0} VRF: {1}]".format(bgp_peer_addr, vrf))
            dprint(
                "BGP-Neighbor-Monitor: BGP Peer unconfigured [Peer: {0} "
                "VRF: {1}]".format(bgp_peer_addr, vrf))
            self.update_action_cli(bgp_peer_addr, vrf, update_source,
                                   local_interface, AlertLevel.MINOR
                                   )


class PrefixAgent(Agent):
    '''This class polls Route table using REST query
     and Analyzes the data'''

    def __init__(self, agent, alm):
        self.agent = agent
        self.alm = alm
        self.prefix_alert_on_this_cycle = False
        self.action_prefix = set()

    def get_url_list(self, user_prefix_list):
        '''Takes prefixes as input and generate
         list of corresponding REST URI'''
        dprint(user_prefix_list)
        prefix_url_dict = {}
        user_prefix_dict = {}
        for ele in user_prefix_list:
            prefix, vrf = ele.split('|')
            if vrf not in user_prefix_dict.keys():
                user_prefix_dict[vrf] = []
            user_prefix_dict[vrf].append(prefix)
        dprint(user_prefix_dict)
        for vrf, prefix_list in user_prefix_dict.items():
            url_first_half = HTTP_ADDRESS + URI_PREFIX_GET_V10_13 + 'system/vrfs/' + vrf
            for prefix in prefix_list:
                prefix_url_fmt = prefix.replace('/', '%2F')
                prefix_url_fmt = prefix_url_fmt.replace(':', '%3A')
                url_second_half = '/routes/' + prefix_url_fmt + '?depth=2'
                url = url_first_half + url_second_half
                count_url = url_first_half + '/routes/' + prefix_url_fmt + '?count=true'
                key = prefix + '|' + vrf
                if key not in prefix_url_dict.keys():
                    prefix_url_dict[key] = []
                prefix_url_dict[key].append(count_url)
                prefix_url_dict[key].append(url)
        dprint(prefix_url_dict)
        # prefix_url_dict example:
        # {
        #     "default|10.0.0.1/32": [
        #         "http://127.0.0.1:8080/rest/v10.08/system/vrfs/default/routes/10.0.0.1%2F32?count=true",
        #         "http://127.0.0.1:8080/rest/v10.08/system/vrfs/default/routes/10.0.0.1%2F32?depth=2"
        #     ],
        #     "red|20.0.0.1/32": [
        #         "http://127.0.0.1:8080/rest/v10.08/system/vrfs/red/routes/20.0.0.1%2F32?count=true",
        #         "http://127.0.0.1:8080/rest/v10.08/system/vrfs/red/routes/20.0.0.1%2F32?depth=2"
        #     ]
        # }
        return prefix_url_dict

    def prefix_handler(self, user_prefix_list):
        '''Wrapper for collect_prefix_data. Invoked from main agent'''
        dprint("WIP------- prefix_handler")

        if not self.agent.params['prefix_list'].value:
            if json.loads(self.agent.variables['prefix_alert']) != AlertLevel.NONE:
                dprint(
                    "prefix_list is None and prefix alert is raised. Bring back to normal")
                self.prefix_set_alert_level(AlertLevel.NONE)
            return

        prefix_url_list = self.get_url_list(user_prefix_list)
        data = self.collect_prefix_data(prefix_url_list)
        self.analyze_prefix_data(data)

        # bring the alert back to normal
        if not self.prefix_alert_on_this_cycle and json.loads(self.agent.variables['prefix_alert']) != AlertLevel.NONE:
            dprint(
                "self.prefix_alert_on_this_cycle is False bring alert back to normal")
            self.prefix_set_alert_level(AlertLevel.NONE)

    # Funtion to collect prefix Data
    def collect_prefix_data(self, prefix_url_list):
        '''Fetch prefix from REST query and Analyze'''
        prefix_response_dict = {}

        for key, url in prefix_url_list.items():
            response = self.agent.fetch_url(url[0])
            dprint("url: {0}".format(url[0]))
            # dprint("response: {0}".format(response))
            prefix_response_dict[key] = {}
            if not response:
                continue
            if int(response['count']) == 0:
                continue
            response = self.agent.fetch_url(url[1])
            dprint("url: {0}".format(url[1]))
            # dprint("response: {0}".format(response))
            if not response:
                continue
            prefix_response_dict[key] = response

        dprint('prefix_response_dict = {0}'.format(prefix_response_dict))
        return prefix_response_dict

    # Function to set alert levels
    # Input Parameters
    # level : alert level to be set(AlertLevel.MINOR, AlertLevel.MAJOR,
    # AlertLevel.CRITICAL)

    def prefix_set_alert_level(self, level):
        '''function used to set alert level'''
        self.alm.alert_levels_generated_within_poll_per_subagent[
            'prefix'].add(level)

    def analyze_prefix_data(self, prefix_res_dict):
        '''this function stores the required prefix Data from JSON response in
         local storage and Analyzes the changes by comparing with previous
         response'''
        prefix_dict_new = prefix_res_dict

        prefix_dict_old = json.loads(
            self.agent.variables["prefix_instance_list"])

        '''
        Structure of prefix_dict_new:
        {
            "1.1.1.1/32|default": {
                "address_family": "ipv4",
                "attributes": {
                    "is_host_route": "True"
                },
                "distance": 1,
                "from": "static",
                "metric": 0,
                "nexthops": {
                    "3": {
                        "id": 3,
                        "ip_address": "10.0.0.2",
                        "port": {
                            "1/1/1": "/rest/v10.13/system/interfaces/1%2F1%2F1"
                        },
                        "selected": "True",
                        "status": {},
                        "type": "legacy-nexthop",
                        "weight": 0
                    }
                },
                "prefix": "1.1.1.1/32",
                "protocol_private": "None",
                "route_age": 1686638132,
                "selected": "True",
                "source_vrfs": {},
                "sub_address_family": "None",
                "sub_protocol_type": "",
                "tag": [
                    0
                ],
                "type": "forward"
            },
            "2.2.2.2/32|default": {
                "address_family": "ipv4",
                "attributes": {
                    "is_host_route": "True"
                },
                "distance": 1,
                "from": "static",
                "metric": 0,
                "nexthops": {
                    "3": {
                        "id": 3,
                        "ip_address": "10.0.0.2",
                        "port": {
                            "1/1/1": "/rest/v10.13/system/interfaces/1%2F1%2F1"
                        },
                        "selected": "True",
                        "status": {},
                        "type": "legacy-nexthop",
                        "weight": 0
                    }
                },
                "prefix": "2.2.2.2/32",
                "protocol_private": "None",
                "route_age": 1686638140,
                "selected": "True",
                "source_vrfs": {},
                "sub_address_family": "None",
                "sub_protocol_type": "",
                "tag": [
                    0
                ],
                "type": "forward"
            }
        }
        '''

        dprint("prefix_instance_list = {0}".format(
            self.agent.variables["prefix_instance_list"]))
        dprint("prefix_dict_new = {0}".format(prefix_dict_new))

        dprint('Old prefix dict:')
        dprint('******************')
        dprint('Old prefix count: {0}', format(len(prefix_dict_old)))
        dprint('Old prefix keys: {0}', format(prefix_dict_old.keys()))
        dprint("-----------------------------")
        dprint('New prefix dict:')
        dprint('******************')
        dprint('New prefix count: {0}', format(len(prefix_dict_new)))
        dprint('New prefix keys: {0}', format(prefix_dict_new.keys()))
        dprint("-----------------------------")

        self.monitor_prefixes_missing_from_start(
            prefix_dict_old, prefix_dict_new)
        self.get_prefixes_added_back_deleted(prefix_dict_old, prefix_dict_new)
        self.get_prefix_options_changes(prefix_dict_old, prefix_dict_new)
        self.get_nh_added_deleted(prefix_dict_old, prefix_dict_new)
        self.agent.actions_ospf_bgp.update(self.action_prefix)

        self.agent.variables["prefix_instance_list"] = json.dumps(
            prefix_dict_new)

    def prefix_cli_add(self, prefix, vrf):
        if ':' in prefix:
            self.action_prefix.add("show ipv6 route summary all-vrfs")
            self.action_prefix.add("show ipv6 rib summary all-vrfs")
            self.action_prefix.add(
                "show ipv6 neighbors summary all-vrfs")
            self.action_prefix.add(
                "show ipv6 route {0} vrf {1}".format(prefix, vrf))
            self.action_prefix.add(
                "show ipv6 rib {0} vrf {1}".format(prefix, vrf))
        else:
            self.action_prefix.add("show ip route summary all-vrfs")
            self.action_prefix.add("show ip rib summary all-vrfs")
            self.action_prefix.add("show arp summary all-vrfs")
            self.action_prefix.add(
                "show ip route {0} vrf {1}".format(prefix, vrf))
            self.action_prefix.add(
                "show ip rib {0} vrf {1}".format(prefix, vrf))

    def get_nh_added_deleted(self, prefix_dict_old, prefix_dict_new):
        nh_deleted = {}
        nh_deleted_print = {}
        nh_added = {}
        alert_level = AlertLevel.NONE
        for o_key, o_value in prefix_dict_old.items():
            # if a prefix is deleted from the user param list at runtime ignore
            if o_key not in prefix_dict_new.keys():
                continue
            # prefix add/delete case, ignore nexthop tracking
            if not o_value or not prefix_dict_new[o_key]:
                continue
            if o_value['from'] == 'local' or o_value['from'] == 'connected':
                continue
            prefix = o_key
            o_nhs = o_value['nexthops']
            n_nhs = prefix_dict_new[o_key]['nexthops']
            o_nh_ips = []
            o_nh_ips_and_intfs = []
            n_nh_ips = []
            for o_nh_value in o_nhs.values():
                o_nh_ip = o_nh_value['ip_address']
                if 'fe80' in o_nh_ip and o_nh_value['port']:
                    o_nh_intf_list = [i for i in o_nh_value['port'].keys()]
                    o_nh_intf = o_nh_intf_list[0]
                else:
                    o_nh_intf = None
                ele = [o_nh_ip, o_nh_intf]
                o_nh_ips_and_intfs.append(ele)
                o_nh_ips.append(o_nh_ip)
            for n_nh_value in n_nhs.values():
                n_nh_ips.append(n_nh_value['ip_address'])

            deleted_nhs_for_this_prefix = []
            deleted_nhs_for_this_prefix_print = []
            for ele in o_nh_ips_and_intfs:
                ip = ele[0]
                if ip not in n_nh_ips:
                    deleted_nhs_for_this_prefix.append(ele)
                    deleted_nhs_for_this_prefix_print.append(ip)
            if deleted_nhs_for_this_prefix:
                nh_deleted[prefix] = deleted_nhs_for_this_prefix
                nh_deleted_print[prefix] = deleted_nhs_for_this_prefix_print

            added_nhs_for_this_prefix = []
            for ip in n_nh_ips:
                if ip not in o_nh_ips:
                    added_nhs_for_this_prefix.append(ip)
            if added_nhs_for_this_prefix:
                nh_added[prefix] = added_nhs_for_this_prefix

        if nh_added:
            syslog = "Nexthops are added: {0}".format(
                str(nh_added).replace("'", ""))
            self.agent.action_syslog(Log.WARNING, syslog)

            for key, val in nh_added.items():
                prefix, vrf = key.split('|')
                self.prefix_cli_add(prefix, vrf)

        if nh_deleted:
            syslog = "Nexthops are deleted: {0}".format(
                str(nh_deleted_print).replace("'", ""))
            self.agent.action_syslog(Log.WARNING, syslog)
            self.agent.set_alert_description_for_key(PREFIX, syslog)
            alert_level = AlertLevel.MINOR

            for key, val in nh_deleted.items():
                prefix, vrf = key.split('|')
                self.prefix_cli_add(prefix, vrf)
                if ':' in prefix:
                    for ele in val:
                        nh_ip = ele[0]
                        intf = ele[1]
                        self.action_prefix.add(
                            "show ipv6 neighbors vrf {0} | inc {1}".format(vrf, nh_ip))
                        if 'fe80' not in nh_ip:
                            self.action_prefix.add(
                                "ping6 {0} vrf {1} repetitions 2".format(nh_ip, vrf))
                        else:
                            if intf:
                                self.action_prefix.add(
                                    "ping6 {0} vrf {1} source {2} repetitions 2".format(nh_ip, vrf, intf))
                else:
                    for ele in val:
                        nh_ip = ele[0]
                        self.action_prefix.add(
                            "show arp vrf {0} | inc {1}".format(vrf, nh_ip))
                        self.action_prefix.add(
                            "ping {0} vrf {1} repetitions 2".format(nh_ip, vrf))
            self.prefix_alert_on_this_cycle = True
            self.prefix_set_alert_level(alert_level)

    def monitor_prefixes_missing_from_start(self, prefix_dict_old, prefix_dict_new):
        dprint("Enter monitor_prefixes_missing_from_start")
        prefix_missing_from_start = []
        alert_level = AlertLevel.NONE
        if prefix_dict_old == {}:
            # 1st poll cycle
            for n_key, n_value in prefix_dict_new.items():
                if not n_value:
                    prefix_missing_from_start.append(n_key)
        else:
            if prefix_dict_new == {}:
                alert_level = AlertLevel.NONE
            for n_key, n_value in prefix_dict_new.items():
                if n_key not in prefix_dict_old.keys():
                    # added while agent is running
                    if not n_value:
                        prefix_missing_from_start.append(n_key)
                else:
                    # to keep alert level persistent
                    o_value = prefix_dict_old[n_key]
                    if not o_value and not n_value:
                        alert_level = AlertLevel.MAJOR
                        self.agent.set_alert_description_for_key(
                            PREFIX, "Issue monitoring prefixes missing from start")
        dprint("prefix_missing_from_start:{0}".format(
            prefix_missing_from_start))
        if prefix_missing_from_start:
            missing_prefixes = ', '.join(prefix_missing_from_start)
            syslog = "Prefixes are missing from the start: {0}".format(
                missing_prefixes)
            self.agent.action_syslog(Log.WARNING, syslog)
            self.agent.set_alert_description_for_key(PREFIX, syslog)
            alert_level = AlertLevel.MAJOR
            for ele in prefix_missing_from_start:
                prefix, vrf = ele.split('|')
                self.prefix_cli_add(prefix, vrf)
        if alert_level != AlertLevel.NONE:
            dprint("Enter alert_level != NONE")
            self.prefix_alert_on_this_cycle = True
            self.prefix_set_alert_level(alert_level)
        self.agent.variables["prefix_instance_list"] = json.dumps(
            prefix_dict_new)

    def get_prefixes_added_back_deleted(self, prefix_dict_old, prefix_dict_new):
        if prefix_dict_old == {}:
            return
        prefixes_added_back = []
        prefixes_deleted = []
        alert_level = AlertLevel.NONE
        for o_key, o_value in prefix_dict_old.items():
            # if a prefix is deleted from the user param list at runtime ignore
            if o_key not in prefix_dict_new.keys():
                continue
            n_value = prefix_dict_new[o_key]
            if not o_value and n_value:
                prefixes_added_back.append(o_key)
            if o_value and not n_value:
                prefixes_deleted.append(o_key)
        dprint("prefixes_added_back:{0}".format(prefixes_added_back))
        dprint("prefixes_deleted:{0}".format(prefixes_deleted))
        if prefixes_added_back:
            added_back_prefixes = ', '.join(prefixes_added_back)
            syslog = "Prefixes are added back: {0}".format(added_back_prefixes)
            self.agent.action_syslog(Log.WARNING, syslog)
            self.agent.clear_alert_description_for_key(PREFIX)
            alert_level = AlertLevel.NONE
            dprint("prefix added back set alert_level == NONE")
            self.prefix_alert_on_this_cycle = True
            self.prefix_set_alert_level(alert_level)
        if prefixes_deleted:
            deleted_prefixes = ', '.join(prefixes_deleted)
            syslog = "Prefixes got deleted: {0}".format(deleted_prefixes)
            self.agent.action_syslog(Log.WARNING, syslog)
            self.agent.set_alert_description_for_key(PREFIX, syslog)
            alert_level = AlertLevel.MAJOR
            for ele in prefixes_deleted:
                prefix, vrf = ele.split('|')
                self.prefix_cli_add(prefix, vrf)
        if alert_level != AlertLevel.NONE:
            dprint("Enter alert_level != NONE")
            self.prefix_alert_on_this_cycle = True
            self.prefix_set_alert_level(alert_level)
        self.agent.variables["prefix_instance_list"] = json.dumps(
            prefix_dict_new)

    def get_prefix_options_changes(self, prefix_dict_old, prefix_dict_new):
        if prefix_dict_old == {}:
            return
        prefixes_options_changes = {'source': {}, 'metric': {}, 'distance': {}}
        alert_level = AlertLevel.NONE
        for o_key, o_value in prefix_dict_old.items():
            # if a prefix is deleted from the user param list at runtime ignore
            if o_key not in prefix_dict_new.keys():
                continue
            n_value = prefix_dict_new[o_key]
            if not o_value or not n_value:
                continue
            if o_value['from'] != n_value['from']:
                prefixes_options_changes['source'][o_key] = {}
                prefixes_options_changes['source'][o_key]['old'] = o_value['from']
                prefixes_options_changes['source'][o_key]['new'] = n_value['from']
            if int(o_value['metric']) != int(n_value['metric']):
                prefixes_options_changes['metric'][o_key] = {}
                prefixes_options_changes['metric'][o_key]['old'] = o_value['metric']
                prefixes_options_changes['metric'][o_key]['new'] = n_value['metric']
            if int(o_value['distance']) != int(n_value['distance']):
                prefixes_options_changes['distance'][o_key] = {}
                prefixes_options_changes['distance'][o_key]['old'] = o_value['distance']
                prefixes_options_changes['distance'][o_key]['new'] = n_value['distance']
        dprint("prefixes_options_changes:{0}".format(prefixes_options_changes))
        for key, val in prefixes_options_changes.items():
            if val:
                syslog = "Prefixes {0} has changed: {1}".format(key,
                                                                str(val).replace("'", ""))
                self.agent.action_syslog(Log.WARNING, syslog)
                self.agent.set_alert_description_for_key(PREFIX, syslog)
                alert_level = AlertLevel.MINOR
                for ele in val:
                    prefix, vrf = ele.split('|')
                    self.prefix_cli_add(prefix, vrf)
                dprint("Enter alert_level != NONE")
                self.prefix_alert_on_this_cycle = True
                self.prefix_set_alert_level(alert_level)
