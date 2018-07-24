# -*- coding: utf-8 -*-
#
# (c) Copyright 2017-2018 Hewlett Packard Enterprise Development LP
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
    'Name': 'fans_rpm_monitor',
    'Description': 'Agent to monitor rpm value of all fans',
    'Version': '1.0',
    'Author': 'Aruba Networks'
}


class Agent(NAE):

    def __init__(self):
        uri1 = '/rest/v1/system/subsystems/*/*/fans/*?attributes=rpm'
        self.m1 = Monitor(uri1, 'Fans RPM')
