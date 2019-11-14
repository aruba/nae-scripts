# -*- coding: utf-8 -*-
#
# (c) Copyright 2019 Hewlett Packard Enterprise Development LP
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
    'Name': 'fault_finder_monitor',
    'Description':
        'This script helps in automatic fault detection which helps protect '
        'against network loops and defective equipment.',
    'Version': '1.3',
    'Author': 'Aruba Networks'
}

ParameterDefinitions = {
    'broadcast_threshold': {
        'Name': 'Threshold for broadcast storm fault',
        'Description':
            'Threshold for rate of change of broadcast packets over time_interval seconds'
            'For low sensitivity level, set threshold as 170500, for medium sensitivity, set threshold '
            'as 100000, for high sensitivity, set threshold as 29500',
        'Type': 'integer',
        'Default': 29500
    },
    'undersize_threshold': {
        'Name': 'Threshold for bad driver fault',
        'Description':
            'Threshold for ratio of rate of undersize packets over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.0036, for medium sensitivity, set is as 0.0021 and for high sensitivity, set it as 0.0006',
        'Type': 'float',
        'Default': 0.0006
    },
    'rx_crc_err_threshold': {
        'Name': 'Threshold for bad cable fault',
        'Description':
            'Threshold for ratio of rate of rx_crc_err packets over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.0036, for medium sensitivity, set is as 0.0021 and for high sensitivity, set it as 0.0006',
        'Type': 'float',
        'Default': 0.0006
    },
    'ethernet_fragments_threshold': {
        'Name': 'Threshold for bad transceiver fault',
        'Description':
            'Threshold for ratio of rate of ethernet_fragments packets over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.045, for medium sensitivity, set is as 0.03 and for high sensitivity, set it as 0.015',
        'Type': 'float',
        'Default': 0.015
    },
    'link_flap_rate_threshold': {
        'Name': 'Link flapping rate threshold level indicating '
                'anomalous behavior',
        'Description': 'This parameter specifies the threshold for rate of'
                       ' link state resets per second, calculated every 10'
                       ' seconds. Rate of link state resets above this'
                       ' threshold is anomalous for the link. Adjust this'
                       ' level to match the expected level of link flap rate'
                       ' for the interface. The default value is 0.1.',
        'Type': 'float',
        'Default': 0.1
    },
    'collision_threshold': {
        'Name': 'Threshold for collision fault',
        'Description':
            'Threshold for ratio of rate of collisions packets over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.0036, for medium sensitivity, set is as 0.0021 and for high sensitivity, set it as 0.0006',
        'Type': 'float',
        'Default': 0.0006
    },
    'tx_drops_threshold': {
        'Name': 'Threshold for tx drops',
        'Description':
            'Threshold for ratio of rate of tx drop packets(over bandwidth) over time_interval seconds to rate of '
            'good frames over 20 seconds. For low sensitivity level, set threshold as '
            '0.0449, for medium sensitivity, set is as 0.0257 and for high sensitivity, set it as 0.0065',
        'Type': 'float',
        'Default': 0.0065
    }
}

Thresholds = {
    'broadcast_low': 170500, 'broadcast_medium': 100000,
    'broadcast_high': 29500, 'undersize_low': 0.0036,
    'undersize_medium': 0.0021, 'undersize_high': 0.0006,
    'rx_crc_err_low': 0.0036, 'rx_crc_err_medium': 0.0021,
    'rx_crc_err_high': 0.0006, 'fragments_low': 0.045,
    'fragments_medium': 0.03, 'fragments_high': 0.015,
    'collision_low': 0.0036, 'collision_medium': 0.0021,
    'collision_high': 0.0006, 'tx_drop_low': 0.0449,
    'tx_drop_medium': 0.0257, 'tx_drop_high': 0.0065,
}


class Agent(NAE):

    INFINITY = float("inf")

    def __init__(self):

        # Broadcast packets
        uri1 = '/rest/v1/system/interfaces/*?attributes=statistics.if_hc_in_broadcast_packets'
        broadcast_uri = Rate(uri1, '20 seconds')
        self.m1 = Monitor(
            broadcast_uri, 'Rate of interface broadcast packets (packets/s)')

        # Undersize packets
        uri2 = '/rest/v1/system/interfaces/*?attributes=statistics.ethernet_stats_undersize_packets'
        undersize_uri = Rate(uri2, '20 seconds')
        self.m2 = Monitor(
            undersize_uri, 'Rate of interface ethernet stats undersize packets (packets/s)')

        # Good frames(rx_no_errors)
        uri3 = '/rest/v1/system/interfaces/*?attributes=statistics.ethernet_stats_rx_no_errors'
        good_frames_uri = Rate(uri3, '20 seconds')
        self.m3 = Monitor(
            good_frames_uri, 'Rate of interface good frames(rx) (packets/s)')

        # Link resets
        uri4 = '/rest/v1/system/interfaces/*?attributes=link_resets'
        rate_uri = Rate(uri4, '10 seconds')
        self.m4 = Monitor(
            rate_uri, 'Interface Link Resets Rate (link resets/s)')

        # Rx CRC errors
        uri5 = '/rest/v1/system/interfaces/*?attributes=statistics.rx_crc_err'
        rx_crc_err_uri = Rate(uri5, '20 seconds')
        self.m5 = Monitor(rx_crc_err_uri,
                          'Rate of Rx CRC error packets (packets/s)')

        # Ethernet stats fragments
        uri6 = '/rest/v1/system/interfaces/*?attributes=statistics.ethernet_stats_fragments'
        ethernet_stats_fragments_uri = Rate(uri6, '20 seconds')
        self.m6 = Monitor(ethernet_stats_fragments_uri,
                          'Rate of ethernet stats fragments error packets (packets/s)')

        # Collision
        uri7 = '/rest/v1/system/interfaces/*?attributes=statistics.collisions'
        collisions_uri = Rate(uri7, '20 seconds')
        self.m7 = Monitor(collisions_uri,
                          'Rate of collision packets (packets/s)')
        # Over bandwidth
        uri8 = '/rest/v1/system/interfaces/*?attributes=statistics.tx_dropped'
        tx_drop_uri = Rate(uri8, '20 seconds')
        self.m8 = Monitor(tx_drop_uri,
                          'Rate of tx drop packets (packets/s)')
        # Good frames(tx_no_errors)
        uri9 = '/rest/v1/system/interfaces/*?attributes=statistics.ethernet_stats_tx_no_errors'
        good_frames_uri_tx = Rate(uri9, '20 seconds')
        self.m9 = Monitor(
            good_frames_uri_tx, 'Rate of interface good frames(tx) (packets/s)')

        self.r1 = Rule('Broadcast storm fault')
        self.r1.condition(
            '{} >= {}', [self.m1, self.params['broadcast_threshold']])
        self.r1.action(self.action_broadcast_sensitivity)
        self.r1.clear_condition(
            '{} < {}', [self.m1, self.params['broadcast_threshold']])
        self.r1.clear_action(self.action_clear_broadcast_sensitivity)

        self.r2 = Rule('Bad driver fault')
        self.r2.condition(
            'ratio of {} and {} >= {}', [self.m2, self.m3, self.params['undersize_threshold']])
        self.r2.action(self.action_undersize_sensitivity)
        self.r2.clear_condition(
            'ratio of {} and {} < {}', [self.m2, self.m3, self.params['undersize_threshold']])
        self.r2.clear_action(self.action_clear_undersize_sensitivity)

        self.r3 = Rule('Link state resets rate anomaly')
        self.r3.condition(
            '{} > {}', [self.m4, self.params['link_flap_rate_threshold']])
        self.r3.action(self.action_interface_flapping_anomaly)
        self.r3.clear_condition(
            '{} < {}', [self.m4, self.params['link_flap_rate_threshold']])
        self.r3.clear_action(self.return_to_normal)

        self.r4 = Rule('Bad cable fault')
        self.r4.condition(
            'ratio of {} and {} >= {}', [self.m5, self.m3, self.params['rx_crc_err_threshold']])
        self.r4.action(self.action_rx_crc_err_sensitivity)
        self.r4.clear_condition(
            'ratio of {} and {} < {}', [self.m5, self.m3, self.params['rx_crc_err_threshold']])
        self.r4.clear_action(self.action_clear_rx_crc_err_sensitivity)

        self.r5 = Rule('Bad transceiver fault')
        self.r5.condition(
            'ratio of {} and {} >= {}', [self.m6, self.m3, self.params['ethernet_fragments_threshold']])
        self.r5.action(self.action_fragments_sensitivity)
        self.r5.clear_condition(
            'ratio of {} and {} < {}', [self.m6, self.m3, self.params['ethernet_fragments_threshold']])
        self.r5.clear_action(self.action_clear_fragments_sensitivity)

        self.r6 = Rule('Collision fault')
        self.r6.condition(
            'ratio of {} and {} >= {}', [self.m7, self.m3, self.params['collision_threshold']])
        self.r6.action(self.action_collision_sensitivity)
        self.r6.clear_condition(
            'ratio of {} and {} < {}', [self.m7, self.m3, self.params['collision_threshold']])
        self.r6.clear_action(self.action_clear_collision_sensitivity)

        self.r7 = Rule('Over bandwidth fault')
        self.r7.condition(
            'ratio of {} and {} >= {}', [self.m8, self.m9, self.params['tx_drops_threshold']])
        self.r7.action(self.action_over_bandwidth_sensitivity)
        self.r7.clear_condition(
            'ratio of {} and {} < {}', [self.m8, self.m9, self.params['tx_drops_threshold']])
        self.r7.clear_action(self.action_clear_over_bandwidth_sensitivity)

        # variables
        self.variables['links_with_alert'] = ''

    def action_high_sensitivity(self, event, value):
        interface_id = get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        ActionSyslog('{} detected on interface {} at high sensitivity level: rate at {} packets/sec'.format(
            rule_description, interface_id, value), severity=SYSLOG_WARNING)
        if self.get_alert_level() != AlertLevel.MINOR and \
                self.get_alert_level() != AlertLevel.MAJOR and \
                self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.MINOR)
        ActionCLI("show interface {}".format(interface_id),
                  title=Title("Interface details"))
        ActionCLI("show interface {} extended".format(interface_id),
                  title=Title("Interface counters information"))

    def action_medium_sensitivity(self, event, value):
        interface_id = get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        ActionSyslog('{} detected on interface {} at medium sensitivity level: rate at {} packets/sec'.format(
            rule_description, interface_id, value), severity=SYSLOG_WARNING)
        if self.get_alert_level() != AlertLevel.MAJOR and self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.MAJOR)
        ActionCLI("show interface {}".format(interface_id),
                  title=Title("Interface details"))
        ActionCLI("show interface {} extended".format(interface_id),
                  title=Title("Interface counters information"))

    def action_low_sensitivity(self, event, value):
        interface_id = get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
        ActionSyslog('{} detected on interface {} at low sensitivity level: rate at {} packets/sec'.format(
            rule_description, interface_id, value), severity=SYSLOG_WARNING)
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.set_alert_level(AlertLevel.CRITICAL)
        ActionCLI("show interface {}".format(interface_id),
                  title=Title("Critical interface details"))
        ActionCLI("show interface {} extended".format(interface_id),
                  title=Title("Critical interface counters information"))

    def action_broadcast_sensitivity(self, event):
        value = event['value']
        threshold = self.params['broadcast_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value >= threshold_value >= Thresholds["broadcast_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["broadcast_medium"] <= threshold_value < Thresholds["broadcast_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["broadcast_high"] <= threshold_value < Thresholds["broadcast_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_undersize_sensitivity(self, event):
        value = event['value']
        threshold = self.params['undersize_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["undersize_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["undersize_medium"] <= threshold_value < Thresholds["undersize_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["undersize_high"] <= threshold_value < Thresholds["undersize_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_interface_flapping_anomaly(self, event):
        value = None
        if 'value' in event:
            value = event['value']
        interface_id = get_interface(event)
        links_with_alert = self.variables['links_with_alert']
        if (interface_id + ':') not in links_with_alert:
            self.add_interface_to_alert_list(interface_id)
            ActionSyslog('Link state resets rate anomaly occurred on interface {}: {} resets/sec'.format(
                         interface_id, value), severity=SYSLOG_WARNING)
            if self.get_alert_level() != AlertLevel.CRITICAL:
                self.set_alert_level(AlertLevel.CRITICAL)

    def return_to_normal(self, event):
        interface_id = get_interface(event)
        links_with_alert = self.variables['links_with_alert']
        if (interface_id + ':') in links_with_alert:
            links_with_alert = links_with_alert.replace(
                (interface_id + ':'), '')
            self.variables['links_with_alert'] = links_with_alert
            ActionSyslog(
                'Interface {} link state is back to normal'.format(interface_id), severity=SYSLOG_WARNING)
            if self.variables['links_with_alert'] == '':
                if self.get_alert_level() is not None:
                    self.remove_alert_level()

    def add_interface_to_alert_list(self, interface_id):
        links_with_alert = self.variables['links_with_alert'] + \
            interface_id + ':'
        self.variables['links_with_alert'] = links_with_alert

    def action_clear_broadcast_sensitivity(self, event):
        value = event['value']
        threshold = self.params['broadcast_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def action_clear_undersize_sensitivity(self, event):
        value = event['value']
        threshold = self.params['broadcast_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def clear_alert_level(self, event):
        interface_id = get_interface(event)
        rule_description = event['rule_description']
        links_with_alert = self.variables['links_with_alert']
        interface = interface_id + ':'
        if interface in links_with_alert:
            links_with_alert = links_with_alert.replace(interface, '')
            self.variables['links_with_alert'] = links_with_alert
            ActionSyslog('{} on interface {} is back to normal'.format(
                rule_description, interface_id), severity=SYSLOG_WARNING)
            if not self.variables['links_with_alert']:
                if self.get_alert_level() is not None:
                    self.remove_alert_level()

    def action_rx_crc_err_sensitivity(self, event):
        value = event['value']
        threshold = self.params['rx_crc_err_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["rx_crc_err_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["rx_crc_err_medium"] <= threshold_value < Thresholds["rx_crc_err_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["rx_crc_err_high"] <= threshold_value < Thresholds["rx_crc_err_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_rx_crc_err_sensitivity(self, event):
        value = event['value']
        threshold = self.params['broadcast_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def action_collision_sensitivity(self, event):
        value = event['value']
        threshold = self.params['collision_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["collision_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["collision_medium"] <= threshold_value < Thresholds["collision_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["collision_high"] <= threshold_value < Thresholds["collision_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_collision_sensitivity(self, event):
        value = event['value']
        threshold = self.params['collision_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def action_over_bandwidth_sensitivity(self, event):
        value = event['value']
        threshold = self.params['tx_drops_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["tx_drop_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["tx_drop_medium"] <= threshold_value < Thresholds["tx_drop_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["tx_drop_high"] <= threshold_value < Thresholds["tx_drop_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_over_bandwidth_sensitivity(self, event):
        value = event['value']
        threshold = self.params['tx_drops_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)

    def action_fragments_sensitivity(self, event):
        value = event['value']
        threshold = self.params['ethernet_fragments_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value == self.INFINITY:
            return
        if input_value >= threshold_value >= Thresholds["fragments_low"]:
            self.action_low_sensitivity(event, input_value)
        elif Thresholds["fragments_medium"] <= threshold_value < Thresholds["fragments_low"] \
                and input_value >= threshold_value:
            self.action_medium_sensitivity(event, input_value)
        elif Thresholds["fragments_high"] <= threshold_value < Thresholds["fragments_medium"] \
                and input_value >= threshold_value:
            self.action_high_sensitivity(event, input_value)

    def action_clear_fragments_sensitivity(self, event):
        value = event['value']
        threshold = self.params['ethernet_fragments_threshold'].value
        try:
            input_value = float(value)
            threshold_value = float(threshold)
        except ValueError:
            print("Not a numerical value")
            return
        if input_value < threshold_value:
            self.clear_alert_level(event)


def get_interface(event):
    label = event['labels']
    first = '='
    last = ',TimeInterval'
    try:
        start = label.index(first) + len(first)
        end = label.index(last, start)
        return label[start:end]
    except ValueError:
        return ""
