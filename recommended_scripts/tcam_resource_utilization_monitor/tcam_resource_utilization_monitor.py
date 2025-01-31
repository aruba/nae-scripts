#-*- coding: utf-8 -*-
#
#(c) Copyright 2024 Hewlett Packard Enterprise Development LP
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied. See the License for the
#specific language governing permissions and limitations
#under the License.

LONG_DESCRIPTION = '''\
## Configuration Notes

The main components of the script are Manifest, Parameter Definitions and python code. 

- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - 'line_card_id': Line card ID for which TCAM utilization is to be monitored
    - 'polling_time_period': Time between consecutive polls to the switch to get the TCAM utilization data. Has to be at least 60 seconds to avoid overwhelming the switch with REST calls
    - 'alert_threshold_feature_util': Percentage threshold for alerting on TCAM utilization for any one feature (utilization/reservation). Allowed range: 1-100
    - 'alert_threshold_port_ranges': Percentage threshold for alerting on TCAM reservation of ingress port ranges. Allowed range: 1-100
    - 'alert_threshold_policers': Percentage threshold for alerting on TCAM reservation of policers. Allowed range: 1-100
- Monitors: This script specifies the monitoring URI(s) to monitor the following: 
    - unreserved TCAM entries 
    - unreserved port ranges and policers on the switch.
- Actions: This script performs the following actions:
    - Polls the TCAM utilization data from the switch and generates/reset alerts when thresholds are crossed with appropriate syslogs
    - Calculates utilization per feature for egress entries
    - Calculates range checker and policer checks

'''

from templateapi.action import ActionSyslog
import json

Manifest = {
    'Name': 'tcam_resource_utilization_monitor',
    'Description': 'Agent to monitor TCAM utilization and generate alerts '
                   'when utilization exceeds specified thresholds',
    'Version': '1.0',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.13',
    'AOSCXVersionMax': '10.13',
    'AOSCXPlatformList': ['8325', '10000']
}

ParameterDefinitions = {
    'line_card_id': {
        'Name': 'Line card ID',
        'Description': 'Line card ID for which TCAM utilization is to be '
                       'monitored',
        'Type': 'string',
        'Default': '1/1'
    },
    'polling_time_period': {
        'Name': 'Resource utilization polling time period (in seconds)',
        'Description': 'Time between consecutive polls to the switch to get the'
                       ' TCAM utlization data. Has to be at least 60 seconds'
                       ' to avoid overwhelming the switch with REST calls',
        'Type': 'integer',
        'Default': 60,
    },
    'alert_threshold_feature_util': {
        'Name': 'Per feature utilization to reservation threshold percentage',
        'Description': 'Percentage threshold for alerting on TCAM utilization '
                       'for any one feature (utilization/reservation). Allowed'
                       ' range: 1-100',
        'Type': 'integer',
        'Default': 75,
    },
    'alert_threshold_port_ranges': {
        'Name': 'Port ranges reservation threshold percentage',
        'Description': 'Percentage threshold for alerting on TCAM reservation '
                       'of ingress port ranges. Allowed range: 1-100',
        'Type': 'integer',
        'Default': 75,
    },
    'alert_threshold_policers': {
        'Name': 'Policers utilization threshold percentage',
        'Description': 'Percentage threshold for alerting on TCAM reservation '
                       'of policers. Allowed range: 1-100',
        'Type': 'integer',
        'Default': 75,
    }
}

class Agent(NAE):
    def __init__(self):
        self.validate_inputs()
        self.initialize_graphs()

#Tracks if the agent is in error state
        self.variables['agent_error_state'] = 'False'

#Get and store resource capacity for use later
        resource_capacity_uri = '/rest/v10.13/system/subsystems/line_card,{}?' \
                                'attributes=resource_capacity' \
                                .format(str(self.params['line_card_id'])
                                        .replace('/', '%2F'))

        resource_capacity_json = self.get_rest_request_json(
            HTTP_ADDRESS + resource_capacity_uri,
            retry=2, wait_between_retries=3)

        self.resource_capacity = \
            resource_capacity_json['resource_capacity'].copy()

#URI used for polling
        self.resources_uri = '/rest/v10.13/system/subsystems/line_card,{}?' \
            'attributes=resource_unreserved,' \
            'resource_utilization_per_feature,' \
            'resource_reservation_per_feature' \
            .format(str(self.params['line_card_id'])
                    .replace('/', '%2F'))

#Polling TCAM utilization data
        self.tcam_util_rule = Rule('TCAM Utilization Calculator')
        self.tcam_util_rule.condition('every {} seconds',
                                      [self.params['polling_time_period']])
        self.tcam_util_rule.action(self.calculate_tcam_utilization)

#Initialize the lists of features and banks in alert
        self.variables['features_in_alert'] = json.dumps([])
        self.variables['banks_in_alert'] = json.dumps([])

    def validate_inputs(self):
        '''
        Validates all the input params entered when creating the agent

        Sets the alert level if any inputs are not in the expected range
        '''
        error_flag = False

#All threshold percentages should be between 1-100
        if (self.params['alert_threshold_feature_util'].value < 1) or \
           (self.params['alert_threshold_feature_util'].value > 100):
            ActionSyslog('TCAM Utilization Monitor Agent Error: '
                         'Per feature utilization to reservation threshold '
                         'percentage should be between 1 and 100')
            error_flag = True

        if (self.params['alert_threshold_port_ranges'].value < 1) or \
           (self.params['alert_threshold_port_ranges'].value > 100):
            ActionSyslog('TCAM Utilization Monitor Agent Error: '
                         'Port ranges reservation threshold percentage '
                         'should be between 1 and 100')
            error_flag = True

        if (self.params['alert_threshold_policers'].value < 1) or \
           (self.params['alert_threshold_policers'].value > 100):
            ActionSyslog('TCAM Utilization Monitor Agent Error: '
                         'Policers utilization threshold percentage '
                         'should be between 1 and 100')
            error_flag = True

#Polling time period should not be less than 60 seconds
        if self.params['polling_time_period'].value < 60:
            ActionSyslog('TCAM Utilization Monitor Agent Error: '
                         'Polling time period cannot be lesser than 60 seconds')
            error_flag = True

        if error_flag:
            ActionSyslog('Please remove and re-create this agent.')
            self.set_alert_level(AlertLevel.CRITICAL)
            self.variables['agent_error_state'] = 'True'

    def initialize_graphs(self):
        '''
        Initializes the 2 graphs and monitor varibles that show up on the UI
        '''
        if 'agent_error_state' in self.variables and \
                self.variables['agent_error_state'] == 'True':
#Do nothing if agent is in error state
            return

        uri1 = '/rest/v1/system/subsystems/line_card/{}?' \
               'attributes=resource_unreserved.Egress_TCAM_Entries'

        self.m1 = Monitor(uri1, 'Unreserved egress TCAM entries',
                          [self.params['line_card_id']])

        uri2 = '/rest/v1/system/subsystems/line_card/{}?' \
               'attributes=resource_unreserved.Ingress_TCAM_Entries'

        self.m2 = Monitor(uri2, 'Unreserved ingress TCAM entries',
                          [self.params['line_card_id']])

        self.graph1 = Graph([self.m1, self.m2], title=Title(
            "Unreserved TCAM entries"), dashboard_display=True)

        uri3 = '/rest/v1/system/subsystems/line_card/{}?' \
               'attributes=resource_unreserved.Ingress_L4_Port_Ranges'

        self.m3 = Monitor(uri3, 'Free ingress L4 port ranges',
                          [self.params['line_card_id']])

        uri4 = '/rest/v1/system/subsystems/line_card/{}?' \
               'attributes=resource_unreserved.Policers'

        self.m4 = Monitor(uri4, 'Free policers',
                          [self.params['line_card_id']])

        self.graph2 = Graph([self.m3, self.m4], title=Title(
            "Unreserved port ranges and policers"), dashboard_display=False)

    def calculate_feature_utilization(self, resource_util_json,
                                      fully_reserved_flags):
        '''
        Helper function to parse the resource JSON

        Parses the response JSON from the REST call to the switch, calculates
        utlization, and sets or removes alerts as necessary

        :param resource_util_json:   JSON response from the switch with
                                     utilization data
        :param full_reserved_flags:  Dictionary of flags with information about
                                     whether or not TCAM banks are fully
                                     reserved
        '''
        resource_utilization_per_feature = \
            resource_util_json['resource_utilization_per_feature']

        resource_reservation_per_feature = \
            resource_util_json['resource_reservation_per_feature']

#Get a local copy of features_in_alert for use in the loop
        features_in_alert = json.loads(self.variables['features_in_alert'])

#Make another copy of the features list to check for features that may
#have been uninstalled
        uninstalled_features = features_in_alert.copy()

#It is possible in some cases for features to share a TCAM bank
#reservation. In such cases, the reservation count for some features
#will be listed as 0. We combine such shared banks so that they're
#considered as one feature for calculating utilization.
        prev_ftr = ""
        combined_ftrs_name = ""
        combined_reservation = 0
        combined_utilization = 0
        shared_rsrc_name = ""
        share_flag = False
        new_reservation_entries = {}
        new_utilization_entries = {}
        delete_ftrs_list = []
        for ftr in resource_reservation_per_feature:
#If this feature has no reservations, skip
            if not resource_reservation_per_feature[ftr]:
                continue
            for rsrc in resource_reservation_per_feature[ftr]:
                if (resource_reservation_per_feature[ftr][rsrc] == 0) and prev_ftr != "":
                    share_flag = True

#Add this feature's name and utilization and add features to the delete list
                    if combined_ftrs_name:
                        combined_ftrs_name = "{},{}".format(
                            combined_ftrs_name, ftr)
                        combined_utilization += resource_utilization_per_feature[ftr][rsrc]
                        delete_ftrs_list.append(ftr)
                    else:
                        shared_rsrc_name = rsrc
                        combined_ftrs_name = "{},{}".format(prev_ftr, ftr)
                        combined_reservation = resource_reservation_per_feature[prev_ftr][rsrc]
                        combined_utilization = resource_utilization_per_feature[
                            prev_ftr][rsrc] + resource_utilization_per_feature[ftr][rsrc]
                        delete_ftrs_list.append(prev_ftr)
                        delete_ftrs_list.append(ftr)
                elif share_flag:
#Add the combined ftr details to the new dicts
                    new_reservation_entries[combined_ftrs_name] = {
                        shared_rsrc_name: combined_reservation}
                    new_utilization_entries[combined_ftrs_name] = {
                        shared_rsrc_name: combined_utilization}

#Reset share flag and other common variables
                    share_flag = False
                    combined_ftrs_name = ""
                    combined_reservation = 0
                    combined_utilization = 0
                    shared_rsrc_name = ""

            prev_ftr = ftr

#Check if the flag is still set
        if share_flag:
#Add the combined ftr details to the new dicts
            new_reservation_entries[combined_ftrs_name] = {
                shared_rsrc_name: combined_reservation}
            new_utilization_entries[combined_ftrs_name] = {
                shared_rsrc_name: combined_utilization}

#Delete the feature keys that were combined with other features
        for ftr in delete_ftrs_list:
            del resource_reservation_per_feature[ftr]
            del resource_utilization_per_feature[ftr]

#Add the combined features info to the main dicts
        resource_reservation_per_feature.update(new_reservation_entries)
        resource_utilization_per_feature.update(new_utilization_entries)

#Iterate through all features to check if any utilization is above
#the threshold
        alert_flag = False
        for ftr in resource_utilization_per_feature:
#Remove installed features from the uninstalled list if they exist
            if ftr in uninstalled_features:
                uninstalled_features.remove(ftr)

            for rsrc in resource_utilization_per_feature[ftr]:
                util_percent = \
                    (resource_utilization_per_feature[ftr][rsrc] /
                     resource_reservation_per_feature[ftr][rsrc]) * 100.0

                if (util_percent >
                        self.params['alert_threshold_feature_util'].value) and \
                        fully_reserved_flags[rsrc]:
#Set alert flag
                    alert_flag = True

                    if ftr not in features_in_alert:
#This TCAM resource bank is fully reserved (no room
#to grow) and feature was not already in alert
                        features_in_alert.append(ftr)

                        ActionSyslog(
                            '{} feature\'s utilization/reservation is at '
                            '{:.2f}%, which is higher than the specified '
                            'threshold'.format(ftr, util_percent))
                elif ftr in features_in_alert:
#Feature was in alert mode before, not anymore either
#because util percentage is below threshold and/or
#because this tcam_bank is not fully reserved
#(there is room to grow)
                    features_in_alert.remove(ftr)

                    ActionSyslog(
                        '{} feature\'s utilization/reservation '
                        'returned to a normal level'.format(ftr))

#Log messages about uninstalled features remove from alert list
        for ftr in uninstalled_features:
            ActionSyslog('{} feature was uninstalled and is not utilizing any'
                         ' TCAM resources anymore'.format(ftr))
            features_in_alert.remove(ftr)

#Load features_in_alert back to the the agent variables
        self.variables['features_in_alert'] = json.dumps(features_in_alert)

        return alert_flag

    def calculate_range_checker_policer_reservation(self,
                                                    resource_unreserved):
        '''
        Helper function for range checker and policer checks

        Checks the reservation percentage of poilicers and range checkers and
        sets or removes alerts as necessary

        :param resource_unreserved: JSON of the 'resource_unreserved' section of
                                    the HTTPS response from the switch
        '''
#Get a local copy of banks_in_alert for use in the loop
        banks_in_alert = json.loads(self.variables['banks_in_alert'])

        alert_flag = False

#Check port ranges
        reservation_percent = \
            (1 - (resource_unreserved['Ingress_L4_Port_Ranges'] /
                  self.resource_capacity['Ingress_L4_Port_Ranges'])) * 100.0

        if (reservation_percent >
                self.params['alert_threshold_port_ranges'].value):
            if 'Ingress_L4_Port_Ranges' not in banks_in_alert:
                ActionSyslog('Ingress L4 Port ranges reservation is at {:.2f}%, '
                             'which is higher than the specified threshold'
                             .format(reservation_percent))
                banks_in_alert.append('Ingress_L4_Port_Ranges')
                alert_flag = True
        elif 'Ingress_L4_Port_Ranges' in banks_in_alert:
            ActionSyslog('Ingress L4 Port ranges reservation returned to a '
                         'normal level')
            banks_in_alert.remove('Ingress_L4_Port_Ranges')

#Check policers
        reservation_percent = \
            (1 - (resource_unreserved['Policers'] /
                  self.resource_capacity['Policers'])) * 100.0

        if (reservation_percent >
                self.params['alert_threshold_policers'].value):
            if 'Policers' not in banks_in_alert:
                ActionSyslog('Policers reservation is at {:.2f}%, which is '
                             'higher than the specified threshold'
                             .format(reservation_percent))
                banks_in_alert.append('Policers')
                alert_flag = True
        elif 'Policers' in banks_in_alert:
            ActionSyslog('Policers reservation returned to a normal level')
            banks_in_alert.remove('Policers')

#Load banks_in_alert back to the the agent variables
        self.variables['banks_in_alert'] = json.dumps(banks_in_alert)

        return alert_flag

    def calculate_tcam_utilization(self, event):
        '''
        Action function for polling the switch and setting alerts

        Polls the TCAM utilization data from the switch and generates/resest
        alerts when thresholds are crossed with appropriate syslogs
        '''
        if 'agent_error_state' in self.variables and \
                self.variables['agent_error_state'] == 'True':
#Do nothing if agent is in error state
            return

#Get the resource utilization from the switch
        resource_util_json = self.get_rest_request_json(
            HTTP_ADDRESS + self.resources_uri, retry=2,
            wait_between_retries=3)

#Check if the response is as expected
        if ('resource_unreserved' not in resource_util_json) or \
           ('resource_utilization_per_feature' not in resource_util_json) or \
           ('resource_reservation_per_feature' not in resource_util_json):
#Skip this polling period
            ActionSyslog('REST call to switch failed. Will try again after {} '
                         'seconds'.format(
                             self.params['polling_time_period'].value))
            return

#Calculate utilization per feature for egress entries
        fully_reserved_flags = {'Egress_TCAM_Entries': False,
                                'Ingress_TCAM_Entries': False}

        if resource_util_json['resource_unreserved']['Egress_TCAM_Entries'] \
                == 0:
            fully_reserved_flags['Egress_TCAM_Entries'] = True

        if resource_util_json['resource_unreserved']['Ingress_TCAM_Entries'] \
                == 0:
            fully_reserved_flags['Ingress_TCAM_Entries'] = True

        alert_flag = self.calculate_feature_utilization(resource_util_json,
                                                        fully_reserved_flags)

        alert_flag |= self.calculate_range_checker_policer_reservation(
            resource_util_json['resource_unreserved'])

        if alert_flag:
            if self.get_alert_level() != AlertLevel.CRITICAL and \
               self.get_alert_level() != AlertLevel.MAJOR:
                self.set_alert_level(AlertLevel.MAJOR)
        elif self.variables['features_in_alert'] == '[]' and \
                self.variables['banks_in_alert'] == '[]':
#Clear the all alerts if nothing is over the limit
            if self.get_alert_level() is not None:
                ActionSyslog('All TCAM resource utilization returned to '
                             'levels below their specified thresholds')
                self.set_alert_level(AlertLevel.NONE)
