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

Manifest = {
    'Name': 'ospfv2_interface_state_flaps_monitor',
    'Description': 'OSPFv2 Interface State Flaps Agent for all interfaces in a given area',
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
        ActionCLI("show ip ospf interface " + interface + " all-vrfs")
        ActionCustomReport(
            "Interface " +
            interface +
            " Interface state machine changed from " +
            previous_state +
            " to " +
            current_state)
        self.set_alert_level(AlertLevel.CRITICAL)

    def normal_alert(self, previous_state, current_state, event):
        interface_list = event['labels'].strip().split(",")
        interface = interface_list[1]
        interface = interface.replace("OSPF_Interface=", "")
        ActionCLI("show ip ospf interface " + interface + " all-vrfs")
        ActionCustomReport(
            "Interface " +
            interface +
            " Interface state machine changed from " +
            previous_state +
            " to " +
            current_state)
        self.remove_alert_level()
