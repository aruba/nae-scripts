## Summary

Agent to monitor TCAM utilization and generate alerts when utilization exceeds specified thresholds

## Supported Software Versions

Script Version 1.0: ArubaOS-CX 10.13 Minimum, ArubaOS-CX 10.13 Maximum

## Supported Platforms

Script Version 1.0: 8325, 10000

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


## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
