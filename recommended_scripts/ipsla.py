# (c) Copyright 2018,2022-2024 Hewlett Packard Enterprise Development LP
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

import re
import json
import time

Manifest = {
    'Name': 'ipsla_threshold',
    'Description': 'Monitor particular value/aggregate value of a'
                   'SLA test and specify shell command to run as action',
    'Version': '2.1',
    'Author': 'HPE Aruba Networking',
    'AOSCXVersionMin': '10.08',
    'AOSCXPlatformList': ['5420', '6200', '6300', '64xx', '8100', '8320', '8325', '8360', '8400']
}

ParameterDefinitions = {
    'ipsla_name': {
        'Name': 'IPSLA Session Name',
        'Description': ('Agent will get statistics for this IPSLA test. '
                        'The test must be configured through the cli with the same name. '
                        'MANDATORY FIELD'
                        '\nThis parameter cannot be changed after agent creation.'),
        'Type': 'string',
        'Default': ''
    },
    'threshold_field': {
        'Name': 'Threshold Field',
        'Description': ('Alerts are raised when the given field crosses the '
                        'threshold value for the given SLA source. '
                        'Enter one of average_ds_delays, average_rtt , average_sd_delays, '
                        'maximum_rtt, minimum_rtt, voip_mos, num_of_packets_rx\n'
                        'This parameter cannot be changed after agent creation.'),
        'Type': 'string',
        'Default': 'average_rtt'
    },
    'threshold_type': {
        'Name': 'Threshold Type',
        'Description': ('The script supports 4 types of thresholds:\n'
                        '"immediate upper" (threshold_field greater than threshold_value)\n'
                        '"immediate lower" (threshold_field less than threshold_value)\n'
                        '"consecutive x {minute(s)|hour(s)|second(s)|day(s)}" (x is an integer)\n'
                        '"aggregated x {minute(s)|hour(s)|second(s)|day(s)}" (x is an integer)\n'
                        'Immediate types raise an alert on the first instance the threshold '
                        'is passed. Consecutive raises an alert when the monitored '
                        'field continuously passes the threshold for a given time. '
                        'Aggregated raises an alert when the running average of '
                        'the field, over the given duration, passes the threshold.\n\n'
                        'NOTE: the aggregated type uses a running average instead of an '
                        'average in discrete time windows\n\n'
                        'This parameter cannot be changed after agent creation.'),
        'Type': 'string',
        'Default': 'immediate upper'
    },
    'threshold_value': {
        'Name': 'Threshold Value',
        'Description': 'The value which will raise the alert in NAE (0 - 999999999)',
        'Type': 'integer',
        'Default': 2000
    },
    'action_command': {
        'Name': 'Action Command',
        'Description': ('The script supports 4 action commands:\n'
                        '"cli cmd" (where "cmd" is the intended CLI command)\n'
                        '"log" (A SYSLOG message is logged when an alert '
                        'is raised)\n"cli-log cmd" (Execute CLI command '
                        '"cmd" and also log a SYSLOG message)\n'
                        '"schedule session_name" (Start the mentioned '
                        'pre-configured IP SLA session)\n'
                        'The CLI "cmd" given must be a single command and should '
                        'not prompt a question back that requires further confirmation '
                        'to execute the "cmd"'),
        'Type': 'string',
        'Default': 'log'
    }
}

URI_PREFIX_GET = "/rest/v10.08/"
URI_PREFIX_MONITOR = "/rest/v1/"


class Agent(NAE):
    URI_PREFIX = URI_PREFIX_MONITOR + 'system/ipsla_sources/'
    URI_FIELDS_RESULT = '?attributes=sla_results.'
    URI_STATUS = '?attributes=status.'
    URI_STATS = '?attributes=statistics.'

    # consts for command validation
    SCHEDULE = 1
    CLI = 2
    CLI_LOG = 4
    LOG = 3
    # consts for threshold type validation
    INVALID = 0
    IMDT_UPPER = 1
    AGG = 2
    CONS = 3
    IMDT_LOWER = 4

    # USE WITH CAUTION
    # set to True when other fields (in addition to the threshold fields) also need
    # to be monitored for the specified IP SLA session
    # Setting to True may exhaust all available monitors on NAE.
    MONITOR_ALL = False

    FIELDS_RESULT = {}
    BASIC = ["average_ds_delays", "average_rtt", "average_sd_delays", "dns_rtt", "dnserror",
             "max_ds_delay", "maximum_rtt", "minimum_rtt", "max_sd_delay", "min_ds_delay",
             "min_sd_delay", "num_of_packets_tx", "num_of_packets_rx"]
    FIELDS_RESULT["icmp_echo"] = BASIC
    FIELDS_RESULT["udp_echo"] = BASIC
    FIELDS_RESULT["tcp_connect"] = BASIC + ["ssl_rtt", "tcpconnect_rtt"]
    FIELDS_RESULT["udp_jitter_voip"] = BASIC + [
        "voip_icpif", "voip_mos", "max_negative_jitter_ds", "max_negative_jitter_sd",
        "max_positive_ds_jitter", "max_positive_sd_jitter", "negative_ds_jitter_number",
        "negative_ds_jitter_sum", "negative_sd_jitter_average", "negative_sd_jitter_number",
        "negative_sd_jitter_sum", "positive_ds_jitter_average", "min_negative_jitter_sd",
        "positive_ds_jitter_count", "positive_ds_jitter_sum", "positive_sd_jitter_average",
        "positive_sd_jitter_count", "positive_sd_jitter_sum", "min_negative_jitter_ds",
        "min_positive_ds_jitter", "min_positive_sd_jitter", "negative_ds_jitter_average"]
    FIELDS_RESULT["http"] = BASIC + ["httperror", "httptransaction_rtt"]
    FIELDS_RESULT["https"] = BASIC + ["tlsconnect_rtt"]

    FIELDS_STATUS = ['last_probe_time']
    FIELDS_STAT = ["bind_error", "destination_address_unreachable_count",
                   "dns_resolution_failures", "probes_timed_out", "probes_transmitted",
                   "socket_receive_error", "transmission_error"]

    def __init__(self):
        self.set_input_formats()
        self.monitor_threshold()
        if self.MONITOR_ALL:
            self.monitor_remaining()

    def on_parameter_change(self, params):
        unchangeable_params = ['ipsla_name',
                               'threshold_field', 'threshold_type']

        for name, value in params.items():
            if name in unchangeable_params:
                self.set_alert_level(AlertLevel.CRITICAL)
                ActionSyslog(
                    "This agent cannot support changing parameters for {}. Please remove and re-create this agent with desired parameters.".format(name))
            else:
                self.logger.debug(
                    "Agent is changing parameters for {}".format(name))

    def monitor_threshold(self):
        threshold_field = self.params['threshold_field'].value
        threshold_type = self.params['threshold_type'].value
        action_command = self.params['action_command'].value
        ipsla_name = self.params['ipsla_name'].value

        if not ipsla_name:
            self.error('Empty IP SLA source name passed to agent params')

        uri_suffix = self.get_field_uri(threshold_field)
        uri = '{}{}{}{}'.format(self.URI_PREFIX, ipsla_name, uri_suffix,
                                threshold_field)
        ttype, tval = self.parse_threshold_type(threshold_type)

        monitor = self.get_threshold_monitor(threshold_field, ttype, tval, uri)
        graph = self.set_chart(monitor, ipsla_name,
                               threshold_field, ttype, tval)
        rule_name = 'IP SLA {}.{} {}'.format(ipsla_name, threshold_field,
                                             threshold_type)
        rule = Rule(rule_name)
        rule = self.set_rule_conditions(monitor, rule, ttype, tval)
        rule = self.set_rule_actions(rule, action_command)
        self.graph = graph
        self.m1 = monitor
        self.r1 = rule

    def set_chart(self, monitor, ipsla_name, threshold_field, threshold_type, time_d):
        if threshold_type == self.IMDT_UPPER or threshold_type == self.IMDT_LOWER \
                or threshold_type == self.CONS:
            unit = 'ms'
        elif threshold_type == self.AGG:
            unit = 'ms Avg. over ' + time_d
        has_units_fields = ['jitter', 'rtt', ]
        non_unit_fields = ['count', 'number', 'error', 'tx', 'rx', 'delay']
        if any(valid in threshold_field for valid in has_units_fields) and \
                not any(invalid in threshold_field for invalid in non_unit_fields):
            g_title = 'IP SLA source={}, field={} ({})'.format(
                ipsla_name, threshold_field, unit)
        else:
            g_title = 'IP SLA source={}, field={}'.format(
                ipsla_name, threshold_field)
        return Graph([monitor], title=Title(g_title), dashboard_display=True)

    def get_threshold_monitor(self, threshold_field, threshold_type, time_duration, uri):
        if threshold_type == self.IMDT_UPPER:
            monitor = Monitor(
                uri, 'ipsla_immediate_'+threshold_field, [self.params['threshold_field']])
        elif threshold_type == self.IMDT_LOWER:
            monitor = Monitor(
                uri, 'ipsla_immediate_'+threshold_field, [self.params['threshold_field']])
        elif threshold_type == self.CONS:
            monitor = Monitor(
                uri, name='ipsla_consecutive_'+threshold_field)
        elif threshold_type == self.AGG:
            agg_m = AverageOverTime(uri, time_duration)
            monitor = Monitor(agg_m, 'ipsla_aggregate_'+threshold_field)
        else:
            self.error(
                'Unable to set monitor after parsing threshold type. '
                '{} not supported'.format(threshold_type))
        return monitor

    def set_rule_conditions(self, monitor, rule, thresh_type, time_d):
        if thresh_type == self.IMDT_UPPER or thresh_type == self.AGG:
            rule.condition(
                '{} > {}', [monitor, self.params['threshold_value']])
        elif thresh_type == self.IMDT_LOWER:
            rule.condition(
                '{} < {}', [monitor, self.params['threshold_value']])
        elif thresh_type == self.CONS:
            rule.condition('{} > {} for ' + time_d,
                           [monitor, self.params['threshold_value']])
        else:
            self.error('Unable to set condition after parsing threshold type. '
                       '{} not supported'.format(thresh_type))
        if thresh_type == self.IMDT_LOWER:
            rule.clear_condition(
                '{} > {}', [monitor, self.params['threshold_value']])
        else:
            rule.clear_condition(
                '{} < {}', [monitor, self.params['threshold_value']])
        return rule

    def set_rule_actions(self, rule, action_command):
        ctype, cmd = self.parse_command(action_command)
        if ctype != self.LOG and ctype != self.CLI and ctype != self.SCHEDULE and ctype != self.CLI_LOG:
            self.error('Unable to set action. Invalid command type. '
                       '{} not supported'.format(ctype))

        else:
            rule.action(self.decide_action)

        rule.clear_action(self.set_normal)
        return rule

    def decide_action(self, event):
        ctype, cmd = self.parse_command(self.params['action_command'].value)

        if ctype == self.LOG:
            self.action_log()
        elif ctype == self.CLI:
            self.action_cli(cmd)
        elif ctype == self.SCHEDULE:
            self.action_schedule(cmd)
        elif ctype == self.CLI_LOG:
            self.action_log_cli(cmd)
        else:
            self.logger.error("Unable to decide action command to run due to invalid parameter: {}".format(
                self.params['action_command'].value))

    def set_input_formats(self):
        """
        Set format for validating action commads and threshold time
        parameters before parameters are parsed in rule modifiers
        """
        self.cli_format = re.compile('cli .*')
        self.schedule_format = re.compile('schedule [a-zA-Z0-9_]')
        self.cli_log_format = re.compile('cli-log .*')
        self.log_format = re.compile('log')

        t_format = '[0-9]+ (minute|hour|second|day|minutes|hours|seconds|days)$'
        self.aggregated_format = re.compile(
            '(?i)aggregated ' + t_format)
        self.consecutive_format = re.compile(
            '(?i)consecutive ' + t_format)

    def monitor_remaining(self):
        """
        Set Result, Status and Statistics monitors when passive monitors need to be set.
        Threshold is for numerical variables only.
        """
        session = self.params['ipsla_name'].value
        rfields = self.get_result_fields(session)
        self.set_monitors(session, rfields, self.URI_FIELDS_RESULT)
        self.set_monitors(session, self.FIELDS_STATUS, self.URI_STATUS)
        self.set_monitors(session, self.FIELDS_STAT, self.URI_STATS)

    def set_monitors(self, session_name, fields, uri_suffix):
        monitors = {}
        for field in fields:
            monitor_var_name = session_name + '_' + field
            monitors[field] = Monitor(
                (self.URI_PREFIX + session_name + uri_suffix + field),
                monitor_var_name)
            setattr(self, monitor_var_name, monitors[field])

    def get_result_fields(self, session_name):
        sesh = self.get_session(session_name)
        sesh_type = sesh['type']
        return self.FIELDS_RESULT[sesh_type]

    def get_field_uri(self, field_name):
        flat_rf = [item for sublist in self.FIELDS_RESULT.values()
                   for item in sublist]
        if field_name in flat_rf:
            return self.URI_FIELDS_RESULT
        if field_name in self.FIELDS_STATUS:
            return self.URI_STATUS
        if field_name in self.FIELDS_STAT:
            return self.URI_STATS
        self.error('Invalid field in threshold field. '
                   '{} not supported'.format(field_name))

    def parse_command(self, command):
        """
        Extract the type of the command and return the
        command or session string that needs to be scheduled.
        """
        if self.schedule_format.match(command):
            return self.SCHEDULE, command.split()[-1]

        cli_command = command.split(' ', 1)[-1]
        if self.cli_format.match(command):
            return self.CLI, cli_command
        if self.log_format.match(command):
            return self.LOG, cli_command
        if self.cli_log_format.match(command):
            return self.CLI_LOG, cli_command
        self.error('Invalid command passed in params. '
                   '{} not supported'.format(command))

    def parse_threshold_type(self, threshold):
        """
        Extract the type of threshold and time string.
        e.g. extracts '5 seconds' from 'myType 5 seconds'
        """
        if threshold.lower() == 'immediate upper':
            return self.IMDT_UPPER, 0
        if threshold.lower() == 'immediate lower':
            return self.IMDT_LOWER, 0

        ttype = self.INVALID
        if self.aggregated_format.match(threshold):
            ttype = self.AGG
        elif self.consecutive_format.match(threshold):
            ttype = self.CONS
        if ttype == self.INVALID:
            self.error('Invalid threshold type passed in params. '
                       '{} not supported.'.format(threshold))
        time_d = threshold.split(' ', 1)[-1]
        return ttype, time_d

    def action_schedule(self, cmd):
        self.default_actions()
        ActionCLI('configure\nip-sla ' + cmd + '\nschedule\nexit\nexit\n')

    def action_log(self):
        self.default_actions()
        self.log()

    def action_cli(self, cmd):
        self.default_actions()
        self.cli(cmd)

    def action_log_cli(self, cmd):
        self.default_actions()
        self.log()
        self.cli(cmd)

    def cli(self, command):
        ActionCLI('configure\n' + command + '\nexit\nexit\n')

    def log(self):
        log_message = ('The IP SLA {}, Threshold is crossed. Monitored Param: {}, '
                       'Threshold Type: {}, Actual Threshold : {}').format(
            self.params['ipsla_name'].value,
            self.params['threshold_field'].value,
            self.params['threshold_type'].value,
            self.params['threshold_value'].value)
        ActionSyslog(log_message)

    def default_actions(self):
        session_name = self.params['ipsla_name'].value
        self.make_report()
        ActionCLI('show ip-sla ' + session_name + ' results')
        self.set_alert_level(AlertLevel.MINOR)

    def make_report(self):
        """
        Create a HTML report string containing all fields of the triggering session
        and details of all other sessions of the same type with optional view.
        """
        session_name = self.params['ipsla_name'].value
        triggering = self.get_session(session_name)
        if 'type' in triggering:
            other_sessions = self.get_other_sessions(triggering['type'])
        else:
            other_sessions = []
        report = HTML_HEAD
        report += '<h1>Triggering Session</h1>'
        report += self.to_table(triggering)
        report += '<input type="checkbox" id="my_checkbox" style="display:none;">'
        report += '<div id="hidden">'
        report += '<p><h1>All Sessions</h1></p>'
        report += self.to_table(other_sessions)
        report += '</div>'
        report += '<label for="my_checkbox"><h3>Click <em>Here</em> to Show/Hide All Agents</h3></label>'
        ActionCustomReport(report)

    def get_session(self, session_name):
        url = HTTP_ADDRESS + URI_PREFIX_GET + 'system/ipsla_sources/' + \
            session_name + '?depth=3'
        resp = None
        try:
            resp = self.get_rest_request_json(url)
        except NAEException:
            self.error('Unable to get IP SLA session from REST')
        return resp

    def get_other_sessions(self, session_type):
        url = HTTP_ADDRESS + URI_PREFIX_GET + 'system/ipsla_sources?depth=3&filter=type:{}'.format(
            session_type)
        resp = None
        try:
            resp = self.get_rest_request_json(url)
        except NAEException:
            self.error('Unable to get all IP SLA sessions report')
        return resp

    def to_table(self, jobj):
        """
        Convert single session json object OR an array of
        session json objects to HTML table string
        """
        table = '<table border="1">'
        if isinstance(jobj, list):
            for row in jobj:
                table += self.to_row(row)
        elif isinstance(jobj, dict):
            table += self.to_row(jobj)
        else:
            self.error(
                'Invalid session details recieved while making alert report')
        table += '</table>'
        return table

    def to_row(self, row_data):
        """
        Breaks down ip sla source JSON object to two rows:
        header row and data row. Return HTML string.
        """
        clean_row = self.special_conditions(row_data)
        row = '<tr>'
        for th in clean_row.keys():
            row += '<th>{}</th>'.format(th)
        row += '</tr>'
        row += '<tr>'
        for k in clean_row.keys():
            row += '<td>{}</td>'.format(Agent.to_str(clean_row[k]))
        row += '</tr>'
        return row

    @staticmethod
    def special_conditions(row_data):
        """
        Formatting for report readibility. Return string.
        """
        try:
            if len(row_data) == 1:
                (_, row_data), = row_data.items()
            long_fields = ['source_interface', 'vrf']
            for lf in long_fields:
                if lf in row_data and row_data[lf]:
                    lf_data = row_data[lf]
                    if len(row_data[lf]) == 1:
                        (_, lf_data), = row_data[lf].items()
                    if 'name' in lf_data:
                        row_data[lf] = lf_data['name']
            if 'status' in row_data and row_data['status']:
                if 'last_probe_time' in row_data['status']:
                    p_time = row_data['status']['last_probe_time']
                    t_str = time.strftime(
                        '%H:%M:%S %Y-%m-%d', time.localtime(p_time))
                    row_data['status']['last_probe_time'] = t_str
            return row_data
        except KeyError:
            return {}

    @staticmethod
    def to_str(jobj):
        """
        Convert JSON object to HTML string without JSON syntax. Return string.
        """
        j_str = json.dumps(jobj, ensure_ascii=True, separators=('<br/>', ': '))
        return re.sub('["{},]', '', j_str)

    def on_agent_re_enable(self, event):
        if self.get_alert_level() == AlertLevel.MINOR:
            self.set_normal(event)

    def set_normal(self, event):
        # alert level is critical only if a bad parameter change occurs
        if self.get_alert_level() != AlertLevel.CRITICAL:
            self.remove_alert_level()

    def error(self, message):
        err_msg = ('IP SLA Agent Source={}, Field={}, Threshold Type={}. '
                   'Error: {}').format(
            self.params['ipsla_name'].value,
            self.params['threshold_field'].value,
            self.params['threshold_type'].value,
            message)
        raise Exception(err_msg)


HTML_HEAD = """<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1cm;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    vertical-align: top;
    white-space: nowrap;
    font-size: medium;
}

tr:nth-child(even) {
    background-color: #d8d5e5;
}
tr:hover {
    background-color: #efa837;
}
#hidden {
  display: none;
}
:checked + #hidden {
  display: block;
}
</style>"""
