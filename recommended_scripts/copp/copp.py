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

LONG_DESCRIPTION = '''\
## Configuration Notes

An agent can be created for the script on the device. The following parameters can be set while creating agent:

- Monitoring Profile - Determines the monitoring profile to load
        - ALL - Monitors dropped and allowed traffic for each CoPP class in the applied policy
        - DROPS - Monitors dropped traffic for each CoPP class in the applied policy
        - RECOMMENDED - Monitors dropped traffic for DHCP, ARP Broadcast, IP Exceptions, Unknown Multicast, Unresolved IP Unicast, and Total dropped/allowed traffic
- Dropped Traffic Alert Threshold - Alert will fire when rate of dropped traffic exceeds this threshold
- Allowed Traffic Alert Threshold - Alert will fire when rate of allowed traffic exceeds this threshold

## Script Description

The main components of this script are monitors, conditions and actions.

The script monitors the traffic passed or dropped for certain CoPP classes based on the monitoring profile. 

For each monitored CoPP class -

- When the traffic dropped is greater than the threshold:
    - The agent will perform some analysis to decide whether it should generate the alert or not. The decision of alerting is made based on the history of packet drops of all CoPP classes, ignoring the acl_logging, sflow and total classes.  
    After fetching the history, if at least one class had an increase in the traffic dropped, then the agent takes two actions:

        - Set the Agent Alert Level to Critical
        - Build an Analysis Report with the following information of each class:
            1. Traffic passed 
            2. Traffic dropped 
            3. % of contribution to the total of traffic passed
            4. % of contribution to the total of traffic dropped
            5. Priority, Burst and Rate configured for the Class  
            The columns of this report can be sorted. This can be used to facilitate the identification of the top-most offending classes, simply by sorting the column for traffic dropped over the last 15 seconds.
- When the traffic dropped is less than the threshold:
    - When the agent detects there is no CoPP class dropping traffic anymore, then it sets the agent alert level back to Normal.
'''

import ast
import re
import time
from collections import OrderedDict

Manifest = {
    'Name': 'copp',
    'Description': 'This script monitors the CoPP (COntrol Plane Policing) policy '
                   'configured on the switch. Traffic destined to the switch dropped '
                   'by CoPP due to a high traffic rate is counted as traffic dropped and traffic '
                   'allowed to reach the switch control plane will be counted as traffic allowed. Alerts '
                   'are generated when these rates exceed their respective thresholds. The '
                   'thresholds are based on the the CoPP Class rates and the values entered '
                   'by the user as parameters.',
    'Version': '5.1',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.08',
    'AOSCXPlatformList': ['6200', '6300', '64xx', '8100', '8320', '8325', '8400']
}

ParameterDefinitions = {
    'dropped_traffic_alert_threshold': {
        'Name': 'Dropped Traffic Alert Threshold (percentage)',
        'Description': "The value entered represents the percentage "
                       "of each CoPP Class' rate used for the threshold value. "
                       "When the rate of dropped traffic exceeds the threshold "
                       "value, an alert is fired. ",
        'Type': 'Integer',
        'Default': 5
    },
    'allowed_traffic_alert_threshold': {
        'Name': 'Allowed Traffic Alert Threshold (percentage)',
        'Description': "The value entered represents the percentage "
                       "of each CoPP Class' rate used for the threshold value. "
                       "When the rate of allowed traffic exceeds the threshold "
                       "value, an alert is fired.",
        'Type': 'Integer',
        'Default': 90
    },
    'monitoring_profile': {
        'Name': 'Monitoring Profile',
        'Description': 'This parameter represents which monitoring profile to load:\n\n'
                       'ALL: DROPPED|ALLOWED data for each CoPP Class in the applied policy \n\n'
                       'RECOMMENDED: Dropped data for DHCP, ARP Broadcast, IP Exceptions, '
                       'Unknown Multicast, Unresolved IP Unicast, and Total traffic dropped/allowed,\n\n'
                       'DROPS: Drop data for each CoPP Class in applied policy \n\n',
        'Type': 'String',
        'Default': 'recommended'
    }
}


class Agent(NAE):
    """
    This agent monitors the current CoPP policy and the configured classes,
    setting up NAE Monitors for both traffic allowed/dropped and rules to
    detect any increase in traffic dropped/allowed of any class over a period of time,
    generating a analysis report with stats and configuration about each CoPP class.

    The script is designed to work on ArubaOS-CX 10.08.XXXX and above versions.

    This agent must be restarted when the current CoPP Policy is updated/switched.
    """

    URI_TEMPLATES = {
        'allowed': '/rest/v1/system?attributes=copp_statistics.{}_{}_passed',
        'dropped': '/rest/v1/system?attributes=copp_statistics.{}_{}_dropped'
    }

    def __init__(self):
        self.copp = Copp(self)
        self.prom = Prometheus(self)

        unit = self.copp.unit()
        self.variables['unit'] = unit

        copp_classes = self.copp.get_policy_classes(
            self.params['monitoring_profile'].value)

        monitors = self.set_monitors(copp_classes, unit)

        self.set_rules(copp_classes, monitors)

    def set_monitors(self, copp_classes, unit):
        """
        Creates NAE Monitors using the copp_classes dictionary as the list of
        CoPP classes to create monitors for.

        Will use the BEHAVIOR field of the dictionary to indicate which URIs/Monitors
        should be created: allowed/dropped

        Since this function creates NAE Monitors based on a given list and the
        NAE Python Framework demands a NAE Monitor to be defined as class
        variables, this implementation has to use the `setattr` function to
        make sure all NAE Monitors work as expected.

        Function Arguments:
        copp_classes -- The list of CoPP Policy Classes
        unit -- The unit of traffic measurement: packets or bytes
        """

        monitors = {}

        for cc in copp_classes:
            monitors[cc] = {}
            for behavior in copp_classes[cc]['behavior']:
                monitor_uri = Agent.URI_TEMPLATES[behavior].format(cc, unit)
                monitors[cc][behavior] = Monitor(Rate(
                    monitor_uri, '60 seconds'), '{} traffic {} ({}/sec)'.format(cc, behavior, unit))

                var_name1 = 'monitor_{}_{}'.format(cc, behavior)
                setattr(self, var_name1, monitors[cc][behavior])

        return monitors

    def find_threshold(self, copp_class, behavior):
        """
        Retrieves the rate required to prevent packets from reaching Control Plane.
        Threshold will be a percentage of the CoPP Rate with the
        dropped/allowed_traffic_alert_threshold param as the percentage of the rate.

        The class's rate acts as the base threshold for alerts to be fired.

        NOTE: if unit is bytes,then the threshold needs to be
        converted from bytes/sec to kbps/second since the CoPP
        Class rate is in kbps for some platforms.

        Function Arguments:
        copp_class -- A CoPP Class Dictionary element
        behavior -- The current CoPP Class behavior
        """

        threshold = int(copp_class['rate'])

        if self.variables['unit'].upper() == 'BYTES':
            threshold = threshold * 125

        if behavior == 'dropped':
            user_threshold = int(
                self.params["dropped_traffic_alert_threshold"].value)
        else:
            user_threshold = int(
                self.params["allowed_traffic_alert_threshold"].value)

        if user_threshold > 0:
            threshold = round((threshold * user_threshold) / 100)

        return threshold

    def set_rules(self, copp_classes, monitors):
        """
        Creates rules for the NAE Agent, with conditions that detect when the monitor rates
        are greater than the alert threshold. When triggered, the action will analyze the monitored
        copp_classes for traffic statistics.

        Keyword Arguments:
        copp_classes -- The list of CoPP Policy Classes monitored
        monitors -- A list of monitors
        """

        for cc in monitors:
            if cc != 'total':
                """
                Rules cannot be set for 'total' since there is not a rate for 'total'
                """
                for behavior in copp_classes[cc]['behavior']:
                    monitor = monitors[cc][behavior]
                    alert_threshold = self.find_threshold(
                        copp_classes[cc], behavior)

                    if behavior == 'allowed':
                        rule = Rule(
                            '{} CoPP Policy Class is allowing traffic to reach the Control Plane'.format(cc))
                        rule.action(self.analyze_allowed_stats)
                    else:
                        rule = Rule(
                            '{} CoPP Policy Class is preventing traffic from reaching the Control Plane'.format(cc))
                        rule.action(self.analyze_dropped_stats)

                    rule.condition('{} > %s' % alert_threshold, [monitor])
                    rule.clear_condition('{} <= %s' %
                                         (alert_threshold*0.75), [monitor])
                    rule.clear_action(self.clear_alert)

                    var_name1 = 'rule_{}_{}'.format(cc, behavior)
                    setattr(self, var_name1, rule)

    def add_ref(self, monitor):
        """
        Adds a reference of a Monitor to a list that is persisted across
        Agent executions.

        This list is meant to track all Monitors that are generating
        Alerts

        Function Arguments:
        monitor -- Name of the Monitor causing the Alert
        """

        ref = set()

        if 'monitor_ref' in self.variables:
            ref = set(ast.literal_eval(self.variables['monitor_ref']))

        ref.add(monitor)
        ref_list = list(ref)
        self.variables['monitor_ref'] = str(ref_list)

        return ref_list

    def rem_ref(self, monitor):
        """
        Removes a reference of a Monitor from a list that is persisted
        across Agent executions.

        This list is meant to track all Monitors that are generating alerts

        Function Arguments:
        monitor -- Name of the Monitor causing the Alert
        """

        if 'monitor_ref' not in self.variables:
            return []

        ref = set(ast.literal_eval(self.variables['monitor_ref']))
        ref_list = list(ref)

        if monitor in ref_list:
            ref_list.remove(monitor)
            self.variables['monitor_ref'] = str(ref_list)

        return ref_list

    def get_agent_name(self, event):
        """
        Extracts the agent name from an NAE callback event.

        Function Arguments:
        event -- NAE Callback Event Object
        """

        if 'monitor_name' in event:
            name = event['monitor_name'].split('.monitor')
            if len(name) > 0:
                return name[0]

        return ""

    def analyze_dropped_stats(self, event):
        """
        Fires a NAE Alert if traffic is getting dropped by relevant CoPP Policy class

        Also, Builds a report with the rate of traffic allowed and dropped for all
        monitored CoPP Policy classes

        Function Arguments:
        event -- NAE Callback Event Object
        """

        agent_name = self.get_agent_name(event)

        copp_classes = self.copp.get_policy_classes(
            self.params['monitoring_profile'].value)

        unit = self.variables['unit']

        stats = self.get_copp_policy_stats(agent_name, copp_classes, unit)

        send_alert = False
        for copp_class in stats:
            if copp_class == 'total':
                """
                Alerts cannot fire for 'total' since it is not a class, but rather
                a combination of all the other class' bytes/packets allowed/dropped
                """
                continue

            rate = stats[copp_class]['dropped']

            if rate > 0:
                send_alert = True
                break

        if send_alert:
            self.set_alert_level(AlertLevel.CRITICAL)
            report = self.build_html_report(stats, unit)
            ActionCustomReport(report)
            self.add_ref(event['monitor_name'])

    def analyze_allowed_stats(self, event):
        """
        Fires a NAE Alert if traffic is being allowed to enter control plane by relevant CoPP Policy class

        Also, this function builds a report with the rate of traffic for all monitored CoPP Policy classes

        Note: The behavior fields are dropped/passed, this is due to Rate_System_copp_statistics
        using dropped/passed. Passed is the technical word for allowed.

        Function Arguments:
        event -- NAE Callback Event Object
        """

        agent_name = self.get_agent_name(event)

        copp_classes = self.copp.get_policy_classes(
            self.params['monitoring_profile'].value)

        unit = self.variables['unit']

        stats = self.get_copp_policy_stats(agent_name, copp_classes, unit)

        send_alert = False
        for copp_class in stats:
            if copp_class == 'total':
                """
                Alerts cannot fire for 'total' since it is not a class, but rather
                a combination of all the other class' bytes/packets allowed/dropped
                """
                continue

            rate = stats[copp_class]['passed']

            if rate > 0:
                send_alert = True
                break

        if send_alert:
            self.set_alert_level(AlertLevel.CRITICAL)
            report = self.build_html_report(stats, unit)
            ActionCustomReport(report)
            self.add_ref(event['monitor_name'])

    def get_copp_policy_stats(self, agent_name, copp_classes, unit):
        """
        Returns the rate of traffic allowed and dropped for each of the monitored
        CoPP Policy Classes.

        Note: The field behavior fields are dropped/passed, this is due to Rate_System_copp_statistics
        using dropped/passed. Passed is the technical word for allowed.

        Function Arguments:
        agent_name -- The name of the agent
        copp_classes -- A list of CoPP Policy Classes
        unit -- The unit of traffic measurement: packets or bytes
        """

        metric_template = 'Rate_System_copp_statistics{map_key="%s_%s_%s"}'
        time_interval = '60s'

        stats = {}

        for cc in copp_classes:
            stats[cc] = {'passed': -1, 'dropped': -1}

            for m in stats[cc].keys():
                metric = metric_template % (cc, unit, m)
                query = '%s[%s]' % (metric, time_interval)
                try:
                    req_result = self.prom.get(query)
                    result = req_result['data']['result']
                    if result:
                        result = result[0]['values']
                    has_result = len(result) > 0
                    if has_result:
                        try:
                            rate = float(result[-1][1])
                            stats[cc][m] = rate
                        except ValueError:
                            pass
                except Exception as e:
                    self.logger.error("Agent %s encountered an error while fetching historical data for Copp Class %s metric %s: %s" % (
                        agent_name, cc, m, e))

            stats[cc] = {**stats[cc], **copp_classes[cc]}

        return OrderedDict(
            sorted(stats.items(), key=lambda s: s[1]['dropped'], reverse=True))

    def build_html_report(self, copp_classes, unit):
        """
        Builds a analysis report in HTML with each CoPP class stats and
        configuration. The report has the ability to sort by column, so the
        user can easily identify the offending traffic by class.

        Note: The field behavior fields are dropped/passed, this is due to Rate_System_copp_statistics
        using the dropped/passed terminology. Passed is the technical word for allowed.

        Function Arguments:
        copp_classes -- A map with CoPP Classes as keys and value being stats
        and configuration about a CoPP Class.
        """

        border_style = 'border:1px solid black'
        cell_padding = 'padding:5px'

        report = ''
        report += '<table id="copp_analysis_report" style="{};border-collapse:collapse" onload="sort(1);">'.format(
            border_style)
        report += '<tr style="{}">'.format(border_style)
        report += '  <th style="{};{};cursor:pointer" rowspan="2" onclick="sort(0)"><span>CoPP Class</span><span id="copp_analysis_report_sort_icon_0" style="font-size:24px"></span></th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{}" colspan="2">Throughput ({}/sec)</th>'.format(
            border_style, cell_padding, unit)
        report += '  <th style="{};{}" colspan="3">Configuration</th>'.format(
            border_style, cell_padding)
        report += '</tr>'
        report += '<tr style="{}">'.format(border_style)
        report += '  <th style="{};{};cursor: pointer" onclick="sort(1)"><span>Dropped</span><span id="copp_analysis_report_sort_icon_1" style="font-size:24px">&uarr;</span></th>'.format(
            border_style, cell_padding)

        if self.params['monitoring_profile'].value.upper() == 'ALL':
            report += '  <th style="{};{};cursor: pointer" onclick="sort(2)"><span>Allowed</span><span id="copp_analysis_report_sort_icon_2" style="font-size:24px"></span></th>'.format(
                border_style, cell_padding)

        report += '  <th style="{};{};cursor: pointer"><span>Priority</span></th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{};cursor: pointer"><span>Burst</span></th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{};cursor: pointer"><span>Rate</span></th>'.format(
            border_style, cell_padding)
        report += '</tr>'

        for name in copp_classes:

            cc = copp_classes[name]
            dropped = round(cc['dropped'], 2)
            allowed = round(cc['passed'], 2)

            dropped_rate = '{:.2f}'.format(
                dropped) if cc['dropped'] > -1 else '-'
            allowed_rate = '{:.2f}'.format(
                allowed) if cc['passed'] > -1 else '-'

            report += '<tr style="{}">'.format(border_style)
            report += '  <td align="center" style="{};{}">{}</td>'.format(
                border_style, cell_padding, name)
            report += '  <td align="center" style="{};{}">{}</td>'.format(
                border_style, cell_padding, dropped_rate)

            if self.params['monitoring_profile'].value.upper() == 'ALL':
                report += '  <td align="center" style="{};{}">{}</td>'.format(
                    border_style, cell_padding, allowed_rate)

            report += '  <td align="center" style="{};{}">{}</td>'.format(
                border_style, cell_padding, cc['priority'])
            report += '  <td align="center" style="{};{}">{}</td>'.format(
                border_style, cell_padding, cc['burst'])
            report += '  <td align="center" style="{};{}">{}</td>'.format(
                border_style, cell_padding, cc['rate'])
            report += '</tr>'

        report += '</tr>'
        report += '</table>'
        report += self.build_js_for_report()

        return report

    def build_js_for_report(self):
        """
        Builds the javascript code required for the HTML analysis report,
        enabling column sorting.
        """

        return ("""<script>
            function sort(n) {
                var table, rows, switching, i, x, y, should_switch, dir, switch_count = 0;
                table = document.getElementById("copp_analysis_report");
                switching = true;
                dir = "asc";

                while(switching) {
                    switching = false;
                    rows = table.getElementsByTagName("TR");

                    for(i=2; i < (rows.length-2); i++) {
                        should_switch = false;
                        row = rows[i];
                        next_row = rows[i + 1];

                        cell = rows[i].getElementsByTagName("TD")[n];
                        next_cell = rows[i + 1].getElementsByTagName("TD")[n];

                        if (n ==  0) {
                            x = cell.innerHTML.toLowerCase();
                            y = next_cell.innerHTML.toLowerCase();
                        } else {
                            x = (cell.innerHTML == "-") ? -1 : Number(cell.innerHTML);
                            y = (next_cell.innerHTML == "-") ? -1 : Number(next_cell.innerHTML);
                        }

                        if (dir == "asc") {
                            if (x > y) {
                                should_switch = true;
                                break;
                            }
                        }

                        if (dir == "desc") {
                            if (x < y) {
                                should_switch = true;
                                break;
                            }
                        }
                    }

                    if (should_switch) {
                        row.parentNode.insertBefore(next_row, row);
                        switching = true;
                        switch_count ++;
                    } else {
                        if (switch_count == 0 && dir == "asc") {
                            dir = "desc";
                            switching = true;
                        }
                    }
                }

                for (i=0; i<3; i++) {
                    icon = document.getElementById("copp_analysis_report_sort_icon_"+i);
                    icon.innerHTML = "";
                }

                icon = document.getElementById("copp_analysis_report_sort_icon_"+n);

                if (dir == "asc") {
                    icon.innerHTML = "&darr;";
                }

                if (dir == "desc") {
                    icon.innerHTML = "&uarr;";
                }
            }

        </script>
        """)

    def clear_alert(self, event):
        """
        Changes the NAE Agent Alert Level back to normal only if there is
        no CoPP Class generating alerts.

        Function Arguments:
        event -- NAE Callback Event Object
        """

        refs = self.rem_ref(event['monitor_name'])

        ActionSyslog("The state of {} is back to Normal.".format(
            event['rule_description']))

        if len(refs) == 0 and self.get_alert_level() != None:
            self.set_alert_level(AlertLevel.NONE)


class Copp:
    """
    Helper class to facilitate manipulation of CoPP-related data.
    """

    def __init__(self, agent):
        self.agent = agent

    def get_policy_classes(self, monitoring_profile):
        """
        Returns a list of the current CoPP Classes configured through the
        applied CoPP Policy, with filtering based on the monitoring profile
        selected by the user.

        Function Arguments:
        monitoring_profile -- User defined set of monitors to load (ALL/RECOMMENDED/DROPS)
        """
        try:
            url = HTTP_ADDRESS + "/rest/v10.08/system?depth=3&attributes=applied_copp_policy"
            json = self.agent.get_rest_request_json(url)

            if "applied_copp_policy" in json:
                applied_policy = list(json["applied_copp_policy"].keys())[0]
                policy_classes = json["applied_copp_policy"][applied_policy]["cur_cpes"]

                recommended_classes = ['arp_broadcast', 'dhcp', 'dhcp_ipv4', 'dhcp_ipv6', 'unresolved_ip_unicast',
                                       'unknown_multicast', 'ip_exceptions']

                if monitoring_profile.upper() == 'RECOMMENDED':
                    for pc in policy_classes.copy():
                        if pc not in recommended_classes:
                            del policy_classes[pc]
                        else:
                            policy_classes[pc].update(
                                behavior=['dropped'])

                elif monitoring_profile.upper() == 'DROPS':
                    for pc in policy_classes.copy():
                        policy_classes[pc].update(behavior=['dropped'])

                else:
                    for pc in policy_classes.copy():
                        policy_classes[pc].update(
                            behavior=['dropped', 'allowed'])

                policy_classes['total'] = {'behavior': ['dropped', 'allowed'], 'rate': 0, 'burst': 0,
                                           'hw_default': 0, 'priority': 0}
                return policy_classes
        except Exception as err:
            raise NAEException(
                "No CoPP Policy configured. Error: {}".format(err)
            )

    def unit(self):
        """
        Returns the traffic measurement unit supported by the device.
        """
        try:
            url = HTTP_ADDRESS + "/rest/v10.08/system?attributes=capabilities"
            json = self.agent.get_rest_request_json(url)
            if "capabilities" in json:
                if "copp_rate_pps" in json["capabilities"]:
                    return "packets"

                if "copp_rate_kbps" in json["capabilities"]:
                    return "bytes"
        except Exception as err:
            raise NAEException(
                "No CoPP traffic unit was found from system capability list. "
                "Error: {}".format(err)
            )


class Prometheus:
    """
    Helper class to facilitate manipulation of historical data from the
    internal Time Series Database, Prometheus.
    """

    URL = 'http://127.0.0.1:9090/prom/api/v1/query'

    def __init__(self, agent):
        self.agent = agent

    def get(self, query):
        """
        Executes a query against Prometheus, returning the result.

        Reference: https://prometheus.io/docs/prometheus/2.0/querying/basics/
        """

        url = "{}?query={}".format(Prometheus.URL, query)
        return self.agent.get_rest_request_json(url)
