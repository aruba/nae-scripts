# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Hewlett Packard Enterprise Development LP
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

from requests import get, codes
import time
import ast

PROXY_DICT = {'http': None, 'https': None}
URI_PREFIX = '/rest/v1/system/vrfs/'

Manifest = {
    'Name': 'ospf_health_monitor',
    'Description': 'OSPFv2 Monitors',
    'Version': '2.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):

        # variables.
        self.variables['events'] = ''
        self.variables['critical_state_interfaces'] = ''
        self.variables['critical_counter_interfaces'] = ''

        uri1 = '/rest/v1/system/vrfs/*/ospf_routers/*/areas/*/' \
               'ospf_interfaces/*?attributes=ifsm_state'
        self.m1 = Monitor(
            uri1,
            'State of Interface')
        self.graph_resource_ifsm_state = Graph([self.m1], title=Title(
            "OSPFv2 ifsm_state"), dashboard_display=True)
        self.r1 = Rule(
            'OSPFv2 interface state machine change from bdr to down')
        self.r1.condition(
            'transition {} from "backup_dr" to "down"',
            [self.m1])
        self.r1.action(self.interface_state_machine_bdr_down)

        self.r2 = Rule(
            'OSPFv2 interface state machine change from down to bdr')
        self.r2.condition(
            'transition {} from "down" to "backup_dr"',
            [self.m1])
        self.r2.action(self.interface_state_machine_down_bdr)

        self.r3 = Rule(
            'OSPFv2 interface state machine change from waiting to bdr')
        self.r3.condition(
            'transition {} from "waiting" to "backup_dr"',
            [self.m1])
        self.r3.action(self.interface_state_machine_waiting_bdr)

        self.r4 = Rule('OSPFv2 interface state change from bdr to dr')
        self.r4.condition(
            'transition {} from "backup_dr" to "dr"',
            [self.m1])
        self.r4.action(self.interface_state_machine_bdr_dr)

        self.r5 = Rule('OSPFv2 interface state machine change from dr to down')
        self.r5.condition(
            'transition {} from "dr" to "down"',
            [self.m1])
        self.r5.action(self.interface_state_machine_dr_down)

        self.r6 = Rule('OSPFv2 interface state machine change from down to dr')
        self.r6.condition(
            'transition {} from "down" to "dr"',
            [self.m1])
        self.r6.action(self.interface_state_machine_down_dr)

        self.r7 = Rule(
            'OSPFv2 interface state machine change from waiting to dr')
        self.r7.condition(
            'transition {} from "waiting" to "dr"',
            [self.m1])
        self.r7.action(self.interface_state_machine_waiting_dr)

        self.r8 = Rule(
            'OSPFv2 interface state machine change from dr other to down')
        self.r8.condition(
            'transition {} from "dr_other" to "down"',
            [self.m1])
        self.r8.action(self.interface_state_machine_drother_down)

        self.r9 = Rule(
            'OSPFv2 interface state machine change from down to dr other')
        self.r9.condition(
            'transition {} from "down" to "dr_other"',
            [self.m1])
        self.r9.action(self.interface_state_machine_down_drother)

        self.r10 = Rule(
            'OSPFv2 interface state machine change from waiting to dr other')
        self.r10.condition(
            'transition {} from "waiting" to "dr_other"',
            [self.m1])
        self.r10.action(self.interface_state_machine_waiting_drother)

        self.r11 = Rule(
            'OSPFv2 interface state machine change from point to point to down'
            ' to dr other')
        self.r11.condition(
            'transition {} from "point_to_point" to "down"',
            [self.m1])
        self.r11.action(self.interface_state_machine_ptp_down)

        self.r12 = Rule('OSPFv2 interface state change from dr other to bdr')
        self.r12.condition(
            'transition {} from "dr_other" to "backup_dr"',
            [self.m1])
        self.r12.action(self.interface_state_machine_drother_bdr)

        self.r13 = Rule(
            'OSPFv2 interface state change from down to point to point')
        self.r13.condition(
            'transition {} from "down" to "point_to_point"',
            [self.m1])
        self.r13.action(self.interface_state_machine_down_ptp)

        self.r14 = Rule('OSPFv2 interface state change from dr other to dr')
        self.r14.condition(
            'transition {} from "dr_other" to "dr"',
            [self.m1])
        self.r14.action(self.interface_state_machine_drother_dr)

        self.r15 = Rule('OSPFv2 interface state change from bdr to waiting')
        self.r15.condition(
            'transition {} from "backup_dr" to "waiting"',
            [self.m1])
        self.r15.action(self.interface_state_machine_bdr_waiting)

        self.r16 = Rule(
            'OSPFv2 interface state change from dr other to waiting')
        self.r16.condition(
            'transition {} from "dr" to "waiting"',
            [self.m1])
        self.r16.action(self.interface_state_machine_dr_waiting)

        self.r17 = Rule(
            'OSPFv2 interface state change from dr other to waiting')
        self.r17.condition(
            'transition {} from "dr_other" to "waiting"',
            [self.m1])
        self.r17.action(self.interface_state_machine_drother_waiting)

        uri2 = '/rest/v1/system/vrfs/*/ospf_routers/*/areas/*' \
               '/ospf_interfaces/*?attributes=' \
               'statistics.lsa_checksum_sum'
        rate_lcs = Rate(uri2, "10 seconds")
        self.m2 = Monitor(rate_lcs, 'LSA Checksum Counter')
        self.r18 = Rule('OSPFv2 LSA Checksum Alert Condition')
        self.r18.condition(
            '{} > 0',
            [self.m2])
        self.r18.action(self.ospf_counter_critical_alert)
        self.r28 = Rule('OSPFv2 LSA Checksum Clear Condition')
        self.r28.condition('{} == 0', [self.m2])
        self.r28.action(self.ospf_counter_normal_alert)

        uri3 = '/rest/v1/system/vrfs/*/ospf_routers/*/areas/*' \
               '/ospf_interfaces/*?attributes=' \
               'statistics.rcvd_bad_lsa_data'
        rate_rbld = Rate(uri3, "10 seconds")
        self.m3 = Monitor(rate_rbld, 'OSPFv2 Bad LSA Data Counter')
        self.r19 = Rule(
            'OSPFv2 Bad LSA data Alert Condition')
        self.r19.condition(
            '{} > 0',
            [self.m3])
        self.r19.action(self.ospf_counter_critical_alert)
        self.r29 = Rule('OSPFv2 Bad LSA data Clear Condition')
        self.r29.condition('{} == 0', [self.m3])
        self.r29.action(self.ospf_counter_normal_alert)

        uri4 = '/rest/v1/system/vrfs/*/ospf_routers/*/areas/*' \
               '/ospf_interfaces/*?attributes=' \
               'statistics.rcvd_bad_lsa_checksum'
        rate_rblc = Rate(uri4, "10 seconds")
        self.m4 = Monitor(rate_rblc, 'OSPFv2 Bad LSA Checksum Counter')
        self.r20 = Rule(
            'OSPFv2 Bad LSA Checksum Alert Condition')
        self.r20.condition(
            '{} > 0',
            [self.m4])
        self.r20.action(self.ospf_counter_critical_alert)
        self.r30 = Rule('OSPFv2 Bad LSA Checksum Clear Condition')
        self.r30.condition('{} == 0', [self.m4])
        self.r30.action(self.ospf_counter_normal_alert)

        uri5 = '/rest/v1/system/vrfs/*/ospf_routers/*/areas/*' \
               '/ospf_interfaces/*?attributes=' \
               'statistics.rcvd_bad_lsa_length'
        rate_rbll = Rate(uri5, "10 seconds")
        self.m5 = Monitor(rate_rbll, 'OSPFv2 Bad LSA Length Counter')
        self.r21 = Rule(
            'OSPFv2 Bad LSA Length Alert Condition')
        self.r21.condition(
            '{} > 0',
            [self.m5])
        self.r21.action(self.ospf_counter_critical_alert)
        self.r31 = Rule('OSPFv2 Bad LSA Length Clear Condition')
        self.r31.condition('{} == 0', [self.m5])
        self.r31.action(self.ospf_counter_normal_alert)

        uri6 = '/rest/v1/system/vrfs/*/ospf_routers/*/areas/*' \
               '/ospf_interfaces/*?attributes=' \
               'statistics.rcvd_invalid_checksum'
        rate_ric = Rate(uri6, "10 seconds")
        self.m6 = Monitor(rate_ric, 'OSPFv2 Invalid Checksum Counter')
        self.r22 = Rule(
            'OSPFv2 Invalid Checksum Alert Condition')
        self.r22.condition(
            '{} > 0',
            [self.m6])
        self.r22.action(self.ospf_counter_critical_alert)
        self.r32 = Rule('OSPFv2 Invalid Checksum Clear Condition')
        self.r32.condition('{} == 0', [self.m6])
        self.r32.action(self.ospf_counter_normal_alert)

        uri7 = '/rest/v1/system/vrfs/*/ospf_routers/*/areas/*' \
               '/ospf_interfaces/*?attributes=' \
               'statistics.state_changes'
        rate_ric = Rate(uri7, "10 seconds")
        self.m7 = Monitor(rate_ric, 'OSPFv2 ifsm state Change Counter')
        self.r23 = Rule(
            'OSPFv2 ifsm state changes Alert Condition')
        self.r23.condition(
            '{} > 0.03',
            [self.m7])
        self.r23.action(self.ospf_counter_critical_alert)
        self.r33 = Rule('OSPFv2 ifsm state changes Clear Condition')
        self.r33.condition('{} <= 0.03', [self.m7])
        self.r33.action(self.ospf_counter_normal_alert)

        self.graph_resource_counter = Graph(
            [self.m2, self.m3, self.m4, self.m5, self.m6, self.m7],
            title=Title("OSPFv2 Counters"))

    def interface_state_machine_bdr_down(self, event):
        self.ifm_state_critical_alert("Backup DR", "Down", event)

    def interface_state_machine_down_bdr(self, event):
        self.ifm_state_normal_alert("Down", "Backup DR", event)

    def interface_state_machine_waiting_bdr(self, event):
        self.ifm_state_normal_alert("Waiting", "Backup DR", event)

    def interface_state_machine_ptp_bdr(self, event):
        self.ifm_state_normal_alert("Point to Point", "Backup DR", event)

    def interface_state_machine_bdr_dr(self, event):
        self.ifm_state_normal_alert("Backup DR", "DR", event)

    def interface_state_machine_bdr_ptp(self, event):
        self.ifm_state_critical_alert("Backup DR", "Point to Point", event)

    def interface_state_machine_bdr_drother(self, event):
        self.ifm_state_normal_alert("Backup DR", "DR Other", event)

    def interface_state_machine_dr_down(self, event):
        self.ifm_state_critical_alert("DR", "Down", event)

    def interface_state_machine_down_dr(self, event):
        self.ifm_state_normal_alert("Down", "DR", event)

    def interface_state_machine_waiting_dr(self, event):
        self.ifm_state_normal_alert("Waiting", "DR", event)

    def interface_state_machine_ptp_dr(self, event):
        self.ifm_state_normal_alert("Point to Point", "DR", event)

    def interface_state_machine_dr_bdr(self, event):
        self.ifm_state_normal_alert("DR", "Backup DR", event)

    def interface_state_machine_dr_ptp(self, event):
        self.ifm_state_critical_alert("DR", "Point to Point", event)

    def interface_state_machine_dr_drother(self, event):
        self.ifm_state_normal_alert("DR", "DR Other", event)

    def interface_state_machine_drother_down(self, event):
        self.ifm_state_critical_alert("DR Other", "Down", event)

    def interface_state_machine_down_drother(self, event):
        self.ifm_state_normal_alert("Down", "DR Other", event)

    def interface_state_machine_waiting_drother(self, event):
        self.ifm_state_normal_alert("Waiting", "DR Other", event)

    def interface_state_machine_ptp_down(self, event):
        self.ifm_state_critical_alert("Point to Point", "Down", event)

    def interface_state_machine_drother_bdr(self, event):
        self.ifm_state_normal_alert("DR Other", "Backup DR", event)

    def interface_state_machine_down_ptp(self, event):
        self.ifm_state_normal_alert("Down", "Point to Point", event)

    def interface_state_machine_drother_dr(self, event):
        self.ifm_state_normal_alert("DR Other", "DR", event)

    def interface_state_machine_bdr_waiting(self, event):
        self.ifm_state_critical_alert("Backup DR", "Waiting", event)

    def interface_state_machine_dr_waiting(self, event):
        self.ifm_state_critical_alert("DR", "Waiting", event)

    def interface_state_machine_drother_waiting(self, event):
        self.ifm_state_critical_alert("DR Other", "Waiting", event)

    # Critical callback for ifsm state.
    def ifm_state_critical_alert(self, previous_state, current_state, event):
        interface_list = event['labels'].strip().split(",")
        ospf_data = {}
        ospf_data['area'] = interface_list[0].replace("OSPF_Area=", "")
        ospf_data['interface'] = interface_list[1].replace(
            "OSPF_Interface=", "")
        ospf_data['route'] = interface_list[2].replace("OSPF_Router=", "")
        ospf_data['vrf'] = interface_list[3].replace("VRF=", "")
        ActionCLI("show ip ospf interface " + ospf_data['interface'])
        self.custom_report(previous_state, current_state, ospf_data)
        if ospf_data['interface'] not in \
                self.variables['critical_state_interfaces']:
            critical_interface_list = \
                self.variables['critical_state_interfaces']
            # Adding the interface to critical_interface_list.
            self.variables['critical_state_interfaces'] \
                = critical_interface_list + \
                ospf_data['interface']
            self.logger.debug(
                "Adding the ospf interface to the critical list %s" %
                (self.variables['critical_state_interfaces']))
            if self.get_alert_level() is not AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)

    # Normal callback for ifsm state.
    def ifm_state_normal_alert(self, previous_state, current_state, event):
        interface_list = event['labels'].strip().split(",")
        ospf_data = {}
        ospf_data['area'] = interface_list[0].replace("OSPF_Area=", "")
        ospf_data['interface'] = interface_list[1].replace(
            "OSPF_Interface=", "")
        ospf_data['route'] = interface_list[2].replace("OSPF_Router=", "")
        ospf_data['vrf'] = interface_list[3].replace("VRF=", "")
        ActionCLI("show ip ospf interface " + ospf_data['interface'])
        self.custom_report(previous_state, current_state, ospf_data)
        if ospf_data['interface'] in \
                self.variables['critical_state_interfaces']:
            critical_interface_list = \
                self.variables['critical_state_interfaces']
            critical_interface_list = \
                critical_interface_list.replace(
                    ospf_data['interface'], '')
            self.variables['critical_state_interfaces'] = \
                critical_interface_list
            self.logger.debug(
                "Removing the ospf interface from the list %s" %
                (self.variables['critical_state_interfaces']))
            if not self.variables['critical_state_interfaces'] and \
                    not self.variables['critical_counter_interfaces']:
                self.set_alert_level(AlertLevel.NONE)

    """
    Critical Callback for:
    state_changes, rcvd_invalid_checksum, rcvd_bad_lsa_length,\
    rcvd_bad_lsa_checksum, rcvd_bad_lsa_data, lsa_checksum_sum
    """

    def ospf_counter_critical_alert(self, event):
        interface_list = event['labels'].strip().split(",")
        interface = interface_list[1]
        interface = interface.replace("OSPF_Interface=", "")

        if interface not in self.variables['critical_counter_interfaces']:
            # Report the critical/anamoly state.
            ActionCLI("show ip ospf interface " + interface + " all-vrfs")
            critical_interface_list = \
                self.variables['critical_counter_interfaces']
            # Adding the interface to critical_interface_list.
            self.variables['critical_counter_interfaces'] = \
                critical_interface_list + interface
            self.logger.debug(
                "Adding the ospf interface to the critical list %s" %
                (self.variables['critical_counter_interfaces']))
            if self.get_alert_level() is not AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)

    """
   Normal Callback for:
   state_changes, rcvd_invalid_checksum, rcvd_bad_lsa_length,\
   rcvd_bad_lsa_checksum, rcvd_bad_lsa_data, lsa_checksum_sum
   """

    def ospf_counter_normal_alert(self, event):
        interface_list = event['labels'].strip().split(",")
        interface = interface_list[1]
        interface = interface.replace("OSPF_Interface=", "")
        if interface in self.variables['critical_counter_interfaces']:
            # Report the normal state.
            ActionCLI("show ip ospf interface " + interface + " all-vrfs")
            critical_interface_list = \
                self.variables['critical_counter_interfaces']
            critical_interface_list = \
                critical_interface_list.replace(
                    interface, '')
            self.variables['critical_counter_interfaces'] = \
                critical_interface_list
            self.logger.debug(
                "Removing the ospf interface from the list %s" %
                (self.variables['critical_counter_interfaces']))
            if not self.variables['critical_counter_interfaces'] and \
                    not self.variables['critical_state_interfaces']:
                self.set_alert_level(AlertLevel.NONE)

    # Generate Custom report.
    def custom_report(self, previous_state, current_state, ospf_data):
        if not self.variables['events']:
            self.variables['events'] = self.get_ospf_data(ospf_data)
            return
        time.sleep(10)
        report = {}
        ospf = self.get_ospf_data(ospf_data)
        privious_ospf = ast.literal_eval(str(self.variables['events']))
        report['route'] = self.route_diff(
            privious_ospf['route'],
            ospf['route'])
        report['neighbor'] = self.neighbor_diff(
            privious_ospf['neighbor'],
            ospf['neighbor'])
        report['previous_state'] = previous_state
        report['current_state'] = current_state
        html = self.get_ospf_htmlcontent(report, ospf_data)
        ActionCustomReport(html)
        self.variables['events'] = ospf

    # Helper methods.
    def get_ospf_data(self, ospf_data):
        ospf = {}
        ospf['route'] = self.get_ospf_route(ospf_data)
        ospf['neighbor'] = self.get_ospf_neighbor(ospf_data)
        ospf['lsa'] = self.get_ospf_lsa(ospf_data)
        ospf['error_msg'] = self.get_ospf_error_message(ospf_data)
        return ospf

    def get_ospf_error_message(self, ospf_data):
        error_msg = {}
        interface_list = self.get_ospf_interface_list(ospf_data)
        for interface in interface_list:
            stats = {}
            uri = interface_list[interface]
            interface_info = self.rest_get(uri)
            if 'statistics' not in interface_info:
                continue

        for statistics in interface_info['statistics']:
            if statistics.startswith('rcvd_'):
                stats[
                    statistics] = interface_info[
                    'statistics'][
                    statistics]
        error_msg[interface] = stats
        return error_msg

    def get_ospf_route(self, ospf_data):
        route = {}
        uri = URI_PREFIX + str(ospf_data['vrf']) + '/ospf_routers/' \
            + str(
            ospf_data['route']) + '/ospf_routes'
        route_list = self.rest_get(uri)
        for uri in route_list:
            route_info = self.rest_get(uri)
            route[route_info['prefix'] + '~' + route_info['path']] = route_info
        return route

    def get_ospf_interface_list(self, ospf_data):
        uri = URI_PREFIX + str(ospf_data['vrf']) + '/ospf_routers/' \
            + str(
            ospf_data['route']) + '/areas/' \
            + str(ospf_data['area']) + '/ospf_interfaces'
        return self.rest_get(uri)

    def get_ospf_neighbor(self, ospf_data):
        neighbor = {}
        interface_list = self.get_ospf_interface_list(ospf_data)
        for interface in interface_list:
            uri = interface_list[interface] + '/ospf_neighbors'
        neighbor_list = self.rest_get(uri)
        for uri in neighbor_list:
            neighbor_info = self.rest_get(uri)
            neighbor[neighbor_info['nbr_if_addr']] = neighbor_info
        return neighbor

    def get_ospf_lsa(self, ospf_data):
        lsa = {}
        uri = URI_PREFIX + str(ospf_data['vrf']) \
            + '/ospf_routers/' + str(
            ospf_data['route']) + '/ospf_lsas'
        lsa_list = self.rest_get(uri)
        for uri in lsa_list:
            lsa_info = self.rest_get(uri)
            lsa[lsa_info['lsa_type'] + ',' + lsa_info['adv_router'] +
                ',' + lsa_info['ls_id']] = lsa_info
        return lsa

    def rest_get(self, uri):
        try:
            self.logger.debug("calling rest_get on switch..." + uri)
            response = get(
                HTTP_ADDRESS +
                uri,
                verify=False,
                proxies=PROXY_DICT)
            self.logger.info(str(response))
            if response.status_code != codes.ok:
                self.logger.debug("Fail to execute REST Query " + str(uri))
        except:
            self.logger.debug("Fail to execute REST Query")
        return response.json()

    def route_diff(self, route_pre, route_cur):
        route = {}
        for prefix in route_pre:
            if prefix not in route_cur:
                route[prefix] = route_pre[prefix]
                route[prefix]['event'] = "Route has been removed"
                route[prefix]['color'] = "#FF0000"
        for prefix in route_cur:
            if prefix not in route_pre:
                route[prefix] = route_cur[prefix]
                route[prefix]['event'] = "New Route has been learnt"
                route[prefix]['color'] = "#008000"
        return route

    def neighbor_diff(self, neighbor_pre, neighbor_cur):
        neighbor = {}
        for prefix in neighbor_pre:
            if prefix not in neighbor_cur:
                neighbor[prefix] = neighbor_pre[prefix]
                neighbor[prefix]['event'] = "Neighbor has been removed"
                neighbor[prefix]['color'] = "#FF0000"

        for prefix in neighbor_cur:
            if prefix not in neighbor_pre:
                neighbor[prefix] = neighbor_cur[prefix]
                neighbor[prefix]['event'] = "New Neighbor has been formed"
                neighbor[prefix]['color'] = "#008000"
        return neighbor

    def get_ospf_htmlcontent(self, report_json, ospf_data):
        line = "<br/>"
        html_prefix = self.get_html_prefix()
        html_suffix = self.get_html_suffix()
        interface_content = self.get_interface_state_content(
            report_json, ospf_data)
        route_content = self.get_ospf_route_content(report_json['route'])
        neighbor_content = self.get_ospf_neighbor_content(
            report_json['neighbor'])
        return html_prefix + interface_content + line + route_content \
            + line + neighbor_content + html_suffix

    def get_ospf_route_content(self, report_json):
        route_content = """<div class="mvisor-panel-header-box">
<h3>OSPF Route Analysis <span class="inner-heading">
Route Event Report - """ + time.strftime("%c") + """</span></h3>

 <table border="1">
  <tr>
    <th width="20px"></th>
    <th>Route Prefix</th>
    <th>Route Via</th>
    <th>Route Type</th>
    <th>Event</th>
  </tr>"""
        for prefix in report_json:
            route_content += """<tr>
	<td bgcolor=" """ + self.datavalidation(report_json[prefix]['color']) + """">  </td>
    <td> """ + self.parse_route_prefix(self.datavalidation(prefix)) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['path']) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['path_type']) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['event']) + """ </td>
    </tr> """
        route_content += """</table></div>"""
        return route_content

    def get_interface_state_content(self, report_json, ospf_data):
        return """<h2>Interface """ \
               + str(ospf_data['interface']) \
               + """  state changed from """ \
               + str(report_json['previous_state']) \
               + """ to """ + str(report_json['current_state']) + """</h2>"""

    def get_ospf_neighbor_content(self, report_json):
        neighbor_content = """<br/><div class="mvisor-panel-header-box"><h3>OSPF Neighbor Analysis <span class="inner-heading"> Neighbor Event Report - """ + time.strftime("%c") + """</span></h3>
 <table border="1">
  <tr>
    <th width="20px"></th>
    <th>Neighbor Interface Address</th>
    <th>Neighbor Router ID</th>
    <th>Neighbor State</th>
    <th>DR</th>
    <th>BDR</th>
    <th>Event</th>
  </tr>"""
        for prefix in report_json:
            neighbor_content += """<tr>
	<td bgcolor=" """ + self.datavalidation(report_json[prefix]['color']) + """">  </td>
    <td> """ + self.datavalidation(prefix) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['nbr_router_id']) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['nfsm_state']) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['dr']) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['bdr']) + """ </td>
    <td> """ + self.datavalidation(report_json[prefix]['event']) + """ </td>
    </tr> """
        neighbor_content += """</table></div>"""
        return neighbor_content

    def datavalidation(self, value):
        if value is None:
            return ""
        return str(value)

    def get_html_prefix(self):
        return """<!DOCTYPE html>
<html>
<head>
<style>
table {
    border-collapse: collapse;
    width: 98%;
    border-style: solid;
    border-color: #DCDCDC #DCDCDC;
    margin: 1%;
}
th, td {
text-align: left;
padding: 8px;border-color: #DCDCDC #DCDCDC;
}
tr:nth-child(odd){background-color: #ffffff}

th {
background-color: #708090;
color: white;
}
tr:hover {
  background-color: #f2f2f2;
}
.heading-first{
 padding-top: 8px;
 color: blue;
}
.inner-heading{
  font-size: 10px;
  font-style: italic;
}
.heading-second{
 padding-top: 8px;
 color: red;
}
.hostinfo {
 color:#686868;
 font-size: 12px;
}

h2{
  color:#A9A9A9;
  font-weight: bold;
  font-style: italic;
}

.mvisor-panel-header-box h3 {
  background:#FF8300;
  color:white;
  padding:0px;
  margin: 0;
  font-weight: bold;
}
.mvisor-panel-header-box {
  border:2px solid #FF8300;
  height: 100%;
  width:100%;
  display: inline-block;
  vertical-align: top;
  border-top-left-radius: 1%;
  border-top-right-radius: 1%;
}
</style>
</head>
<body>"""

    def parse_route_prefix(self, value):
        value = str(value)
        if value.index('~') < 1:
            return value
        return str(value[0:value.index('~')])

    def get_html_suffix(self):
        return """</body></html>"""
