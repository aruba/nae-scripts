# -*- coding: utf-8 -*-
#
# (c) Copyright 2018-2019 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

Manifest = {
    'Name': 'power_supply_utilization_monitor',
    'Description': 'System Power Supply Utilization monitoring agent',
    'Version': '1.1',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        chassis_subsys_name = '1'

        uri1 = '/rest/v1/system/subsystems/chassis/%s/power_supplies/*?' \
               'attributes=characteristics.maximum_power' % chassis_subsys_name
        self.m1 = Monitor(uri1, 'maximum (Power in Watts)')

        uri2 = '/rest/v1/system/subsystems/chassis/%s/power_supplies/*?' \
               'attributes=characteristics.instantaneous_power' \
               % chassis_subsys_name
        self.m2 = Monitor(uri2, 'instantaneous (Power in Watts)')
