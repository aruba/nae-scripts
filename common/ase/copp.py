# -*- coding: utf-8 -*-
#
# (c) Copyright 2018-2019 Hewlett Packard Enterprise Development LP
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

import ast
import re
import requests
from collections import OrderedDict

Manifest = {
    'Name': 'copp',
    'Description': 'CoPP Policy Classes Monitoring and Alerting Agent',
    'Version': '3.1',
    'Author': 'Aruba Networks'
}


ParameterDefinitions = {
    'management_protocol_tolerance': {
        'Name': 'Management Protocol Tolerance (in percentage)',
        'Description': 'This parameter represents a tolerance added on top of '
                       'the configured rate for management protocols. '
                       'The provided value is the percentage added to the '
                       'configured CoPP Class rate and is used as the '
                       'threshold for the rate of traffic dropped.',
        'Type': 'Integer',
        'Default': 0
    },

    'routing_protocol_tolerance': {
        'Name': 'Routing Protocol Tolerance (in percentage)',
        'Description': 'This parameter represents a tolerance added on top of '
                       'the configured rate for routing protocols. '
                       'The provided value is the percentage added to the '
                       'configured CoPP class rate and will be used as the '
                       'threshold for the rate of traffic dropped. ',
        'Type': 'Integer',
        'Default': 0
    }
}

CoppClasses = {
    'acl_logging': 'management',
    'arp_broadcast': 'routing',
    'arp_protect': 'routing',
    'arp_unicast': 'routing',
    'bfd': 'routing',
    'bfd_control': 'routing',
    'bgp_ipv4': 'routing',
    'bgp_ipv6': 'routing',
    'captive_portal': 'routing',
    'default': 'routing',
    'dhcp': 'routing',
    'dhcp_ipv4': 'routing',
    'dhcp_ipv6': 'routing',
    'erps': 'routing',
    'gmrp': 'routing',
    'hypertext': 'management',
    'icmp_broadcast_ipv4': 'routing',
    'icmp_multicast_ipv6': 'routing',
    'icmp_security_ipv6': 'routing',
    'icmp_unicast_ipv4': 'routing',
    'icmp_unicast_ipv6': 'routing',
    'ieee_8021x': 'routing',
    'igmp': 'routing',
    'ip_exceptions': 'routing',
    'ip_lockdown': 'routing',
    'ipsec': 'routing',
    'ipv4_options': 'routing',
    'ipv6_options': 'routing',
    'lacp': 'routing',
    'lldp': 'routing',
    'loop_protect': 'routing',
    'mac_lockout': 'routing',
    'mirror_to_cpu': 'management',
    'mld': 'routing',
    'mvrp': 'routing',
    'ntp': 'routing',
    'ospf_multicast': 'routing',
    'ospf_multicast_ipv4': 'routing',
    'ospf_multicast_ipv6': 'routing',
    'ospf_unicast': 'routing',
    'ospf_unicast_ipv4': 'routing',
    'ospf_unicast_ipv6': 'routing',
    'pim': 'routing',
    'secure_learn': 'routing',
    'sflow': 'management',
    'stp': 'routing',
    'ssh': 'management',
    'telnet': 'routing',
    'total': 'routing',
    'total_dhcpv4': 'routing',
    'udld': 'routing',
    'unknown_multicast': 'routing',
    'unresolved_ip_unicast': 'routing',
    'vrrp': 'routing',
    'vrrp_ipv4': 'routing',
    'vrrp_ipv6': 'routing'
}


class Agent(NAE):
    """This agent monitors the current CoPP policy and the configured classes,
    setting up NAE Monitors for both traffic passed and dropped and rules to
    detect any increase of traffic drops of any class over a period of time,
    generating a analysis report with stats and configuration about each CoPP
    class.

    The script is designed to work on ArubaOS-CX 10.01.XXXX and above versions.
    """

    URI_TEMPLATES = {
        'passed': '/rest/v1/system?attributes=copp_statistics.{}_{}_passed',
        'dropped': '/rest/v1/system?attributes=copp_statistics.{}_{}_dropped'
    }

    def __init__(self):
        unit = Copp.unit()
        self.variables['unit'] = unit

        copp_classes = Copp.applied_policy_classes()
        copp_classes['total'] = {}

        monitors = self.set_monitors(copp_classes, unit)

        self.set_rules(copp_classes, monitors)

    def set_monitors(self, copp_classes, unit):
        """Creates NAE Monitors for both traffic passed and dropped for each
        given CoPP Policy Class plus it creates monitors for total traffic
        passed and total traffic dropped.

        Since this function creates NAE Monitors based on a given list and the
        NAE Python Framework demands a NAE Monitor to be defined as class
        variables, this implementation has to use the `setattr` function to
        make sure all NAE Monitors work as expected.

        Keyword Arguments:
        copp_classes -- The list of CoPP Policy Classes
        unit -- The unit of traffic measurement: packets or bytes
        """

        monitors = {}

        for cc in copp_classes:
            passed_uri = Agent.URI_TEMPLATES['passed'].format(cc, unit)
            dropped_uri = Agent.URI_TEMPLATES['dropped'].format(cc, unit)

            monitors[cc] = {
                'passed': Monitor(Rate(passed_uri, '15 seconds'), '{} traffic passed ({}/sec)'.format(cc, unit)),
                'dropped': Monitor(Rate(dropped_uri, '15 seconds'), '{} traffic dropped ({}/sec)'.format(cc, unit))
            }

            var_name1 = 'monitor_{}_passed'.format(cc)
            setattr(self, var_name1, monitors[cc]['passed'])
            var_name2 = 'monitor_{}_dropped'.format(cc)
            setattr(self, var_name2, monitors[cc]['dropped'])

        return monitors

    def find_threshold(self, copp_class, configuration):
        """Returns the configured threshold based on the category of the given
        CoPP Class.

        Keyword Arguments:
        copp_class -- A CoPP Class name
        configuration -- The current CoPP Class configuration
        """

        threshold = int(configuration['rate'])

        if copp_class in CoppClasses:
            tolerance = 0
            category = CoppClasses[copp_class]
            key = "{}_protocol_tolerance".format(category)
            if key in self.params:
                tolerance = int(self.params[key].value)

            if tolerance > 0:
                threshold = round((threshold*tolerance) / 100)

        return threshold

    def set_rules(self, copp_classes, monitors):
        for cc in monitors:
            if cc != "total":
                dropped_monitor = monitors[cc]['dropped']
                threshold = self.find_threshold(cc, copp_classes[cc])

                rule = Rule(
                    '{} CoPP Policy Class is preventing traffic to reach CPU'.format(cc))
                rule.condition('{} > %s' % threshold, [
                               dropped_monitor])
                rule.action(self.analyze_copp_drops)
                rule.clear_condition(
                    '{} <= %s' % threshold, [dropped_monitor])
                rule.clear_action(self.clear_alert)

                var_name1 = 'rule_{}'.format(cc)
                setattr(self, var_name1, rule)

    def add_ref(self, copp_class):
        """Adds a reference of a CoPP Class to a list that is persisted accross
        Agent executions.

        This list is meant to track all CoPP Classes that are preventing
        traffic to reach the CPU.

        Keyword Arguments:
        copp_class -- The name of a CoPP Class
        """

        ref = set()

        if 'class_ref' in self.variables:
            ref = set(ast.literal_eval(self.variables['class_ref']))

        ref.add(copp_class)
        ref_list = list(ref)
        self.variables['class_ref'] = str(ref_list)

        return ref_list

    def rem_ref(self, copp_class):
        """Removes a reference of a CoPP Class from a list that is persisted
        accross Agent executions.

        This list is meant to track all CoPP Classes that are dropping
        traffic.

        Keyword Arguments:
        copp_class -- The name of a CoPP Class
        """

        if 'class_ref' not in self.variables:
            return []

        ref = set(ast.literal_eval(self.variables['class_ref']))
        ref_list = list(ref)

        if copp_class in ref_list:
            ref_list.remove(copp_class)
            self.variables['class_ref'] = str(ref_list)

        return ref_list

    def get_agent_name(self, event):
        """Extracts the agent name from an NAE callback event.

        Keyword Arguments:
        event -- NAE Callback Event Object
        """

        if 'monitor_name' in event:
            name = event['monitor_name'].split('.monitor')
            if len(name) > 0:
                return name[0]

        return ""

    def copp_class(self, event):
        """Extracts the Copp Class from a given NAE Callback Event.

        Keywords Arguments:
        event -- NAE Callback Event
        """

        m = re.search(r'.+map_key=(.+)', event['labels'])
        if m is not None:
            return m.group(1)

        return ""

    def analyze_copp_drops(self, event):
        """Fires a NAE Alert if traffic getting dropped by relevant CoPP Policy
        Classes.

        Also, Builds a report with the rate of traffic passed and dropped for
        each one of the CoPP Classes applied on the system.

        Keyword Arguments:
        event -- NAE Callback Event Object
        """

        cc = self.copp_class(event)
        agent_name = self.get_agent_name(event)
        copp_classes = Copp.applied_policy_classes()
        copp_classes['total'] = {}
        unit = self.variables['unit']
        stats = self.get_copp_policy_stats(agent_name, copp_classes, unit)

        should_alert = False
        for copp_class in stats:
            if copp_class == 'sflow' or copp_class == 'acl_logging' or copp_class == 'total':
                continue

            rate = stats[copp_class]['dropped']
            if rate > 0:
                should_alert = True
                break

        if should_alert:
            self.set_alert_level(AlertLevel.CRITICAL)
            report = self.build_html_report(stats)
            ActionCustomReport(report)
            self.add_ref(cc)

    def get_copp_policy_stats(self, agent_name, copp_classes, unit):
        """Returns the rate of traffic passed and dropped of each of the given
        CoPP Policy Classes.

        Keyword Arguments:
        agent_name -- The name of the agent
        copp_classes -- A list of CoPP Policy Classes
        unit -- The unit of traffic measurement: packets or bytes
        """

        metric_template = 'Rate_System_copp_statistics{map_key="%s_%s_%s"}'
        time_interval = '15s'

        stats = {}

        for cc in copp_classes:
            stats[cc] = {"passed": -1, "dropped": -1}

            for m in stats[cc].keys():
                metric = metric_template % (cc, unit, m)
                query = '%s[%s]' % (metric, time_interval)
                c, r = Prometheus.get(query)
                if c == 200:
                    try:
                        result = r['data']['result'][0]['values']
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

    def build_html_report(self, copp_classes):
        """Builds a analysis report in HTML with each CoPP class stats and
        configuration. The report has the ability to sort by column, so the
        user can easily identify the offending traffic by class.

        Keyword Arguments:
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
        report += '  <th style="{};{}" colspan="2">Packet Throughput (packets/sec over the last 15 seconds)</th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{}" colspan="3">Configuration</th>'.format(
            border_style, cell_padding)
        report += '</tr>'
        report += '<tr style="{}">'.format(border_style)
        report += '  <th style="{};{};cursor: pointer" onclick="sort(1)"><span>Dropped</span><span id="copp_analysis_report_sort_icon_1" style="font-size:24px">&uarr;</span></th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{};cursor: pointer" onclick="sort(2)"><span>Passed</span><span id="copp_analysis_report_sort_icon_2" style="font-size:24px"></span></th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{};cursor: pointer"><span>Priority</span></th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{};cursor: pointer"><span>Burst</span></th>'.format(
            border_style, cell_padding)
        report += '  <th style="{};{};cursor: pointer"><span>Rate</span></th>'.format(
            border_style, cell_padding)
        report += '</tr>'

        for name in copp_classes:
            if name != 'total':
                cc = copp_classes[name]
                dropped = round(cc['dropped'], 2)
                passed = round(cc['passed'], 2)
                dropped_rate = '{:.2f}'.format(
                    dropped) if cc['dropped'] > 0 else '-'
                passed_rate = '{:.2f}'.format(
                    passed) if cc['passed'] > 0 else '-'
                report += '<tr style="{}">'.format(border_style)
                report += '  <td align="center" style="{};{}">{}</td>'.format(
                    border_style, cell_padding, name)

                report += '  <td align="center" style="{};{}">{}</td>'.format(
                    border_style, cell_padding, dropped_rate)
                report += '  <td align="center" style="{};{}">{}</td>'.format(
                    border_style, cell_padding, passed_rate)

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
        """Builds the javascript code required for the HTML analysis report,
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
        """Changes the NAE Agent Alert Level back to normal only if there is
        no CoPP Class dropping packages.

        Keyword Arguments:
        event -- NAE Callback Event Object
        """

        cc = self.copp_class(event)
        refs = self.rem_ref(cc)
        if len(refs) == 0 and self.get_alert_level() != None:
            self.set_alert_level(AlertLevel.NONE)


class Copp:
    """Helper class to facilitate manipulation of CoPP-related data.
    """

    @staticmethod
    def applied_policy_classes():
        """Returns a list of the current CoPP Classes configured through the
        applied CoPP Policy.
        """

        try:
            r = requests.get(
                "http://127.0.0.1:5577/rest/v1/system?depth=2&attributes=applied_copp_policy")
            if r.status_code == 200:
                json = r.json()
                if "applied_copp_policy" in json:
                    copp_policy = json["applied_copp_policy"]
                    policy_classes = copp_policy["cur_cpes"]
        except Exception as e:
            raise NAEException("Error while fetching CoPP Policy")

        return policy_classes

    @staticmethod
    def unit():
        """Returns the traffic measurement unit supported by the device.
        """

        try:
            r = requests.get(
                "http://127.0.0.1:5577/rest/v1/system?attributes=capabilities")
            if r.status_code == 200:
                json = r.json()
                if "capabilities" in json:
                    if "copp_rate_pps" in json["capabilities"]:
                        return "packets"

                    if "copp_rate_kbps" in json["capabilities"]:
                        return "bytes"
        except Exception as e:
            raise NAEException("Error while fetching switch capabilities")

        raise NAEException(
            "No CoPP traffic unit was found from system capability list")


class Prometheus:
    """Helper class to facilitate manipulation of historical data from the
    internal Time Series Database, Prometheus.
    """

    URL = 'http://127.0.0.1:9090/prom/api/v1/query'

    @staticmethod
    def get(query):
        """Executes a query against Prometheus, returning the result.

        Reference: https://prometheus.io/docs/prometheus/2.0/querying/basics/
        """

        url = "{}?query={}".format(Prometheus.URL, query)
        r = requests.get(url)
        return r.status_code, r.json()
