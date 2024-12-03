## Summary

This script monitors overall software device health.

## Supported Software Versions

Script Version 2.0: ArubaOS-CX 10.08 Minimum

## Supported Platforms

Script Version 2.0: 5420, 6200, 6300, 64xx, 8100, 8320, 8325, 8400, 9300

## Configuration Notes

The main components of the script are Manifest, Parameter Definitions and python code. 
- 'Manifest' defines the unique name for this script.
- 'Parameter Definitions' defines the input parameters to the script. This script requires the following parameters: 
    - threshold: Total MAC address count threshold
    - cpu_threshold: High CPU threshold value in percentage
    - memory_threshold: High Memory threshold value in percentage
    - time_interval: Time interval in seconds to consider CPU/Memory utilization
    - daemon_1: System daemon name 1
    - daemon_2: System daemon name 2
    - daemon_3: System daemon name 3
    - daemon_4: System daemon name 4
    - routes_count_ratio_lower_threshold: Route count deviation lower threshold
    - routes_count_ratio_upper_threshold: Route count deviation upper threshold
    - neighbors_count_ratio_lower_threshold: Neighbors count deviation threshold
    - mac_addresses_count_ratio_lower_threshold: MAC addresses count deviation lower threshold
    - mac_addresses_count_ratio_upper_threshold: MAC addresses count deviation upper threshold
    - rate_of_decrease_threshold: Rate of decrease threshold (in percentage)
    - time_interval_mac: Threshold for broadcast storm fault
    - tx_drops_threshold: Threshold for tx drops
- Monitors:  This script specifies the monitoring URI(s) to monitor the following: 
    - Total MAC addresses count(sum of all URI).
    - Total MAC addresses count
    - CPU Utilization in % per daemon
    - Memory Utilization in % per daemon
    - Rate of interface broadcast packets (packets/s)
    - Rate of tx drop packets (packets/s)
    - Rate of interface tx good frames (packets/s)
    - Sum of count of the Routes across all VRFs on both the switch and the VSX-peer switch.
    - Sum of count of the Neighbors across all VRFs on both the switch and the VSX-peer switch.
    - Sum of count of MAC addresses across all VLANs on both the switch and the VSX-peer switch.

- Actions:  This script performs the following actions:
    - If the total Mac addresses count is more than threshold value mentioned in the threshold parameter, the following actions are executed:
    - A log message is generated with the total MAC addresses on the switch .
        1. The agent alert level is updated to Critical.
    - When the rate of total Mac addresses count is less than the threshold value, the following actions are executed. 
        - The agent alert level is updated to Normal.
        - A log message is generated with the rate of decrease value.
    - A periodic callback executed every interval of time as expected as time_interval NAE parameter.
    - The periodic callbacks makes a REST call to obtain the sum of count of MAC addresses across all VLAN.  
    Using the obtained value, calculate the rate of decrease by subtracting it from the previous value and dividing it by the time interval.  
    If the decrease rate is more than threshold value mentioned in the rate_of_decrease_threshold parameter, the following actions are executed:
        - The agent alert level is updated to Critical.
        - A log message is generated with the rate of decrease value
        - A custom report is generated with the rate of decrease value
    - When the rate of decrease is less than the threshold value, the following actions are executed:
        - The agent alert level is updated to Normal
        - A log message is generated with the rate of decrease value
        - A custom report is generated with the rate of decrease value
    - Broadcast storm fault -​​ The user can provide the threshold value for the rate of change of broadcast packets over 20 seconds. For low sensitivity level, the threshold value is 170500, for medium sensitivity level, it is 100000 and for high sensitivity level, it is 29500. 
        - Conditions for this monitor are -
            - When the threshold provided is for high sensitivity level and there is broadcast storm fault, the following actions are taken -​
                - The agent status is marked as Minor, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at high sensitivity level'.
            - When the threshold provided is for medium sensitivity level and there is broadcast storm fault, the following actions are taken -​
                - The agent status is marked as Major, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at medium sensitivity level'.
            - When the threshold provided is for low sensitivity level and there is broadcast storm fault, the following actions are taken -​
                - The agent status is marked as Critical, CLI commands to show interface details are executed. Syslog says 'Broadcast storm fault detected on interface <name> at low sensitivity level'.
            - When there is no longer broadcast storm fault, Syslog says 'Broadcast storm fault detected on interface <name> is back to normal'.
                - If there is no fault found on any of the interfaces, the agent status is marked as Normal.
    - Over bandwidth fault -​​ 
        - Conditions for this monitor are -
            - When the threshold provided is for high sensitivity level and there is over bandwidth  fault, the following actions are taken -​
                - The agent status is marked as Minor, CLI commands to show interface details are executed. Syslog says 'over bandwidth fault detected on interface <name> at high sensitivity level'.
            - When the threshold provided is for medium sensitivity level and there is over bandwidth fault, the following actions are taken -​
                - The agent status is marked as Major, CLI commands to show interface details are executed. Syslog says 'over bandwidth fault detected on interface <name> at medium sensitivity level'.
            - When the threshold provided is for low sensitivity level and there is over bandwidth fault, the following actions are taken -​
                - The agent status is marked as Critical, CLI commands to show interface details are executed. Syslog says 'over bandwidth fault detected on interface <name> at low sensitivity level'.
            - When there is no longer broadcast storm fault, Syslog says 'over bandwidth fault detected on interface <name> is back to normal'.
                - If there is no fault found on any of the interfaces, the agent status is marked as Normal.
    - For the CPU/Memory utilization is more than threshold value mentioned in the threshold parameter for a specific time interval, the following actions are executed:
        - A log message is generated with the high CPU/Memory utilization by daemon.
        - The agent alert level is updated to Critical.
    - When the CPU/Memory utilization is less than the threshold value for a specific time interval, the following actions are executed. 
        - A log message is generated with the CPU/Memory utilization back to normal for daemon.
        - The agent alert level is updated to Normal.
    - Whenever the ratio of the sum of count of Neighbors or MAC_Addresses on the switch to the VSX-peer switch is out of the range bounded by the upper threshold and lower threshold for resource, the agent alert level is set to Critical.
    - Whenever the ratio of the sum of count of Routes on the switch to the VSX-peer switch is out of the range bounded up the upper and lower threshold values for routes, the agent alert level is set to Minor if the current alert level is Normal. If the current alert level is Critical , the agent alert level remains critical.
        - A log message and custom report are generated giving the count of the resource on the switch
        - A log message and custom report are generated giving the count of the resource on the VSX-peer switch.
        - A log message and custom report are generated giving the ratio of the resource on the switch to VSX-peer switch as well as mentioning and mentioning that the ratio is outside the range bounded by the thresholds for that resource.
    - When the ratios for all the three resources (Neighbors, Routes  and MAC Addresses) are within the range specified by the threshold for the resource, the agent alert level is set to nornal with the following actions:A log message and custom report are generated giving the count of the resource on the switch
        - A log message and custom report are generated giving the count of the resource on the VSX-peer switch.
        - A log message and custom report are generated giving the ratio of the resource on the switch to VSX-peer switch as well as mentioning and mentioning is inside the range bounded by the thresholds for that resource.
    - When the ratios for Neighbors and MAC Addresses are within the range specified by the threshold for the resource but the ratio of Routes is outside the range specified by the threshold for Routes, the agent alert level is set to Minor with the following actions:
        - A log message and custom report are generated giving the count of the resource on the switch.
        - A log message and custom report are generated giving the count of the resource on the VSX-peer switch.
        - A log message and custom report are generated giving the ratio of the resource on the switch to VSX-peer switch as well as mentioning and mentioning is inside the range bounded by the thresholds for that resource.

## Licenses

Apache License, Version 2.0

## References

- https://www.arubanetworks.com/resource/network-analytics-engine-solution-overview/
