# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2018 Hewlett Packard Enterprise Development LP
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
    'Name': 'ospfv2_interface_state_flaps_impact_monitor',
    'Description':
        'OSPFv2 Interface State Flaps Impact Analysis Agent',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}


ParameterDefinitions = {

    'vrf_name': {
        'Name': 'Vrf Name',
        'Description': 'Vrf to be Monitor',
        'Type': 'String',
        'Default': 'default'
    },

    'ospf_process_id': {
        'Name': 'OSPFv2 process id',
        'Description': 'OSPFv2 process id to be Monitor',
        'Type': 'integer',
        'Default': 1
    },

    'ospf_area_id': {
        'Name': 'OSPFv2 area id',
        'Description': 'OSPFv2 area id to be Monitor',
        'Type': 'String',
        'Default': '0.0.0.0'
    },

    'ospf_interface_id': {
        'Name': 'OSPFv2 interface id',
        'Description': 'OSPFv2 interface id to be Monitor',
        'Type': 'String',
        'Default': '1/1/1'
    }
}


class Agent(NAE):

    def __init__(self):
        self.variables['events'] = ''
        uri1 = '/rest/v1/system/vrfs/{}/ospf_routers/{}/areas/{}/' \
               'ospf_interfaces/{}?attributes=ifsm_state'
        self.m1 = Monitor(
            uri1,
            'State of Interface',
            [self.params['vrf_name'],
             self.params['ospf_process_id'],
             self.params['ospf_area_id'],
             self.params['ospf_interface_id']])
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

        self.r5 = Rule('OSPFv2 interface state change from bdr to dr')
        self.r5.condition(
            'transition {} from "backup_dr" to "dr"',
            [self.m1])
        self.r5.action(self.interface_state_machine_bdr_dr)

        self.r8 = Rule('OSPFv2 interface state machine change from dr to down')
        self.r8.condition(
            'transition {} from "dr" to "down"',
            [self.m1])
        self.r8.action(self.interface_state_machine_dr_down)

        self.r9 = Rule('OSPFv2 interface state machine change from down to dr')
        self.r9.condition(
            'transition {} from "down" to "dr"',
            [self.m1])
        self.r9.action(self.interface_state_machine_down_dr)

        self.r10 = Rule(
            'OSPFv2 interface state machine change from waiting to dr')
        self.r10.condition(
            'transition {} from "waiting" to "dr"',
            [self.m1])
        self.r10.action(self.interface_state_machine_waiting_dr)

        self.r15 = Rule(
            'OSPFv2 interface state machine change from dr other to down')
        self.r15.condition(
            'transition {} from "dr_other" to "down"',
            [self.m1])
        self.r15.action(self.interface_state_machine_drother_down)

        self.r16 = Rule(
            'OSPFv2 interface state machine change from down to dr other')
        self.r16.condition(
            'transition {} from "down" to "dr_other"',
            [self.m1])
        self.r16.action(self.interface_state_machine_down_drother)

        self.r17 = Rule(
            'OSPFv2 interface state machine change from waiting to dr other')
        self.r17.condition(
            'transition {} from "waiting" to "dr_other"',
            [self.m1])
        self.r17.action(self.interface_state_machine_waiting_drother)

        self.r18 = Rule(
            'OSPFv2 interface state machine change from point to point to down'
            ' to dr other')
        self.r18.condition(
            'transition {} from "point_to_point" to "down"',
            [self.m1])
        self.r18.action(self.interface_state_machine_ptp_down)

        self.r19 = Rule('OSPFv2 interface state change from dr other to bdr')
        self.r19.condition(
            'transition {} from "dr_other" to "backup_dr"',
            [self.m1])
        self.r19.action(self.interface_state_machine_drother_bdr)

        self.r20 = Rule(
            'OSPFv2 interface state change from down to point to point')
        self.r20.condition(
            'transition {} from "down" to "point_to_point"',
            [self.m1])
        self.r20.action(self.interface_state_machine_down_ptp)

        self.r21 = Rule('OSPFv2 interface state change from dr other to dr')
        self.r21.condition(
            'transition {} from "dr_other" to "dr"',
            [self.m1])
        self.r21.action(self.interface_state_machine_drother_dr)

        self.r22 = Rule('OSPFv2 interface state change from bdr to waiting')
        self.r22.condition(
            'transition {} from "backup_dr" to "waiting"',
            [self.m1])
        self.r22.action(self.interface_state_machine_bdr_waiting)

        self.r23 = Rule(
            'OSPFv2 interface state change from dr to waiting')
        self.r23.condition(
            'transition {} from "dr" to "waiting"',
            [self.m1])
        self.r23.action(self.interface_state_machine_dr_waiting)

        self.r24 = Rule(
            'OSPFv2 interface state change from dr other to waiting')
        self.r24.condition(
            'transition {} from "dr_other" to "waiting"',
            [self.m1])
        self.r24.action(self.interface_state_machine_drother_waiting)

    def interface_state_machine_bdr_down(self, event):
        self.critical_alert("Backup DR", "Down", event)

    def interface_state_machine_down_bdr(self, event):
        self.normal_alert("Down", "Backup DR", event)

    def interface_state_machine_waiting_bdr(self, event):
        self.normal_alert("Waiting", "Backup DR", event)

    def interface_state_machine_ptp_bdr(self, event):
        self.normal_alert("Point to Point", "Backup DR", event)

    def interface_state_machine_bdr_dr(self, event):
        self.normal_alert("Backup DR", "DR", event)

    def interface_state_machine_bdr_ptp(self, event):
        self.critical_alert("Backup DR", "Point to Point", event)

    def interface_state_machine_bdr_drother(self, event):
        self.normal_alert("Backup DR", "DR Other", event)

    def interface_state_machine_dr_down(self, event):
        self.critical_alert("DR", "Down", event)

    def interface_state_machine_down_dr(self, event):
        self.normal_alert("Down", "DR", event)

    def interface_state_machine_waiting_dr(self, event):
        self.normal_alert("Waiting", "DR", event)

    def interface_state_machine_ptp_dr(self, event):
        self.normal_alert("Point to Point", "DR", event)

    def interface_state_machine_dr_bdr(self, event):
        self.normal_alert("DR", "Backup DR", event)

    def interface_state_machine_dr_ptp(self, event):
        self.critical_alert("DR", "Point to Point", event)

    def interface_state_machine_dr_drother(self, event):
        self.normal_alert("DR", "DR Other", event)

    def interface_state_machine_drother_down(self, event):
        self.critical_alert("DR Other", "Down", event)

    def interface_state_machine_down_drother(self, event):
        self.normal_alert("Down", "DR Other", event)

    def interface_state_machine_waiting_drother(self, event):
        self.normal_alert("Waiting", "DR Other", event)

    def interface_state_machine_ptp_down(self, event):
        self.critical_alert("Point to Point", "Down", event)

    def interface_state_machine_drother_bdr(self, event):
        self.normal_alert("DR Other", "Backup DR", event)

    def interface_state_machine_down_ptp(self, event):
        self.normal_alert("Down", "Point to Point", event)

    def interface_state_machine_drother_dr(self, event):
        self.normal_alert("DR Other", "DR", event)

    def interface_state_machine_bdr_waiting(self, event):
        self.critical_alert("Backup DR", "Waiting", event)

    def interface_state_machine_dr_waiting(self, event):
        self.critical_alert("DR", "Waiting", event)

    def interface_state_machine_drother_waiting(self, event):
        self.critical_alert("DR Other", "Waiting", event)

    def critical_alert(self, previous_state, current_state, event):
        interface_list = event['labels'].strip().split(",")
        interface = interface_list[1]
        interface = interface.replace("OSPF_Interface=", "")
        self.custom_report(previous_state, current_state)
        ActionCLI("show ip ospf interface " + interface + " all-vrfs")
        self.set_alert_level(AlertLevel.CRITICAL)

    def normal_alert(self, previous_state, current_state, event):
        if (self.get_alert_level() is None) and (self.variables['events']):
            return
        interface_list = event['labels'].strip().split(",")
        interface = interface_list[1]
        interface = interface.replace("OSPF_Interface=", "")
        self.custom_report(previous_state, current_state)
        ActionCLI("show ip ospf interface " + interface + " all-vrfs")
        self.remove_alert_level()

    def custom_report(self, previous_state, current_state):
        if not self.variables['events']:
            self.variables['events'] = self.get_ospf_data()
            return
        time.sleep(10)
        report = {}
        ospf = self.get_ospf_data()
        privious_ospf = ast.literal_eval(str(self.variables['events']))
        report['route'] = self.route_diff(
            privious_ospf['route'],
            ospf['route'])
        report['neighbor'] = self.neighbor_diff(
            privious_ospf['neighbor'],
            ospf['neighbor'])
        report['previous_state'] = previous_state
        report['current_state'] = current_state
        html = self.get_ospf_htmlcontent(report)
        ActionCustomReport(html)
        self.variables['events'] = ospf

    def get_ospf_data(self):
        ospf = {}
        ospf['route'] = self.get_ospf_route()
        ospf['neighbor'] = self.get_ospf_neighbor()
        ospf['lsa'] = self.get_ospf_lsa()
        ospf['error_msg'] = self.get_ospf_error_message()
        return ospf

    def summary_report(self, ospf):
        "external", "inter_area", "intra_area"

    def get_ospf_error_message(self):
        error_msg = {}
        interface_list = self.get_ospf_interface_list()
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

    def get_ospf_route(self):
        route = {}
        uri = URI_PREFIX + str(self.params['vrf_name']) + '/ospf_routers/' \
            + str(
            self.params['ospf_process_id']) + '/ospf_routes'
        route_list = self.rest_get(uri)
        for uri in route_list:
            route_info = self.rest_get(uri)
            route[route_info['prefix'] + '~' + route_info['path']] = route_info
        return route

    def get_ospf_interface_list(self):
        uri = URI_PREFIX + str(self.params['vrf_name']) + '/ospf_routers/' \
            + str(
            self.params['ospf_process_id']) + '/areas/' \
            + str(self.params['ospf_area_id']) + '/ospf_interfaces'
        return self.rest_get(uri)

    def get_ospf_neighbor(self):
        neighbor = {}
        interface_list = self.get_ospf_interface_list()
        for interface in interface_list:
            uri = interface_list[interface] + '/ospf_neighbors'
            neighbor_list = self.rest_get(uri)
            for uri in neighbor_list:
                neighbor_info = self.rest_get(uri)
                neighbor[neighbor_info['nbr_if_addr']] = neighbor_info
        return neighbor

    def get_ospf_lsa(self):
        lsa = {}
        uri = URI_PREFIX + str(self.params['vrf_name']) \
            + '/ospf_routers/' + str(
            self.params['ospf_process_id']) + '/ospf_lsas'
        lsa_list = self.rest_get(uri)
        for uri in lsa_list:
            lsa_info = self.rest_get(uri)
            lsa[lsa_info['lsa_type'] + ',' + lsa_info['adv_router']
                + ',' + lsa_info['ls_id']] = lsa_info
        return lsa

    def rest_get(self, uri):
        try:
            self.logger.info("calling rest_get on the switch..." + uri)
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

    def get_ospf_htmlcontent(self, report_json):
        line = "<br/>"
        html_prefix = self.get_html_prefix()
        html_suffix = self.get_html_suffix()
        interface_content = self.get_interface_state_content(report_json)
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

    def get_interface_state_content(self, report_json):
        return """<h2>Interface """ \
            + str(self.params['ospf_interface_id']) \
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
