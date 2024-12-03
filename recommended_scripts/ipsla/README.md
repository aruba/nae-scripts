## Summary

Monitor particular value/aggregate value of an SLA test and specify shell command to run as action

## Supported Software Versions

Script Version 2.1: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 2.1: 5420, 6200, 6300, 64xx, 8100, 8320, 8325, 8360, 8400

## Configuration Notes

An agent has to be created for every session/source that is configured on the device. The following parameters have to be set:

- IPSLA Session Name - Agent will get statistics for this IPSLA source. The source must be configured through the cli with the same name.
- Threshold Field - This is a metric that will be monitored for passing a threshold. The IP SLA daemon supports over 20 metrics for the source. The user has to know the metric they need to set thresholds for.
- Threshold Type - The script supports three types of thresholds, immediate thresholds trigger alerts when the metric of interest passes the threshold. Immediate upper is of the format metric greater than some value and lower is the opposite. Consecutive thresholds trigger alerts when the metric of interest continuously passes the threshold for a given time, and aggregated thresholds trigger alerts when the metric of interest has a running average for a given duration that passes the threshold.
- Threshold Value - self explanatory.
- Action Command - The script supports 4 action commands:
    - "cli cmd" (where "cmd" is the intended CLI command)
        - The CLI "cmd" given must be a single command and should not prompt a question back that requires further confirmation to execute the "cmd"
    - "log" (A SYSLOG message is logged when an alert is raised)
    - "cli-log cmd" (Execute CLI command "cmd" and also log a SYSLOG message)
        - The CLI "cmd" given must be a single command and should not prompt a question back that requires further confirmation to execute the "cmd"
    - "schedule session_name" (Start the mentioned pre-configured IP SLA session)

The NAE script also sets alerts based on the thresholds and generates a report in the Analysis Report field of the Alert on the agent dashboard. The report contains all details about the session in a tabular format and also allows the user to view a second table showing all other configured IP SLA sources/sessions on the device.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
